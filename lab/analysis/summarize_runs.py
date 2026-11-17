#!/usr/bin/env python3
"""Resumen por corrida a partir de los datos crudos (data/raw/runs/<run_id>/). No modifica data/raw.

Para cada corrida calcula, en la VENTANA DE ATAQUE (warm .. warm+attack segundos desde t0):
  - SCADA: solicitudes, respondidas, disponibilidad (%), RTT mediana/media/p95/p99 (ms), timeouts
  - Ataque: paquetes transmitidos por el atacante (kernel, v10) y pps efectivos
  - Captura (segunda fuente): paquetes de ataque antes (mir20, VLAN 20) y después (mir30, VLAN 30) del IPS,
    y la diferencia (a)-(b); descartes de dumpcap
  - Suricata: delta de ips.blocked, ips.accepted, detect.alert, decoder.pkts en la corrida
  - Firewall: deltas de los contadores nftables
  - Temperatura máxima del host
Salida: data/processed/run_summary_<plataforma>.csv  (una plataforma por archivo: no se mezclan)
Uso: summarize_runs.py --platform laptop-dev [--profile piloto]
"""
import argparse, csv, json, os, re, statistics, sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def pct(xs, q):
    if not xs: return ""
    xs = sorted(xs); k = (len(xs) - 1) * q; f = int(k); c = min(f + 1, len(xs) - 1)
    return round(xs[f] + (xs[c] - xs[f]) * (k - f), 3)

def nft(path):
    try:
        d = json.load(open(path))
        return {c["counter"]["name"]: c["counter"]["packets"] for c in d["nftables"] if "counter" in c}
    except Exception:
        return {}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--platform", required=True); ap.add_argument("--profile")
    a = ap.parse_args()
    runs = [r for r in csv.DictReader(open(f"{REPO}/data/raw/runs.csv")) if r["platform"] == a.platform
            and (not a.profile or r["run_profile"] == a.profile)]
    out = []
    for r in runs:
        d = f"{REPO}/data/raw/runs/{r['run_id']}"
        if not os.path.isdir(d): continue
        warm, att = int(r["warm_s"]), int(r["attack_s"])
        polls = list(csv.DictReader(open(f"{d}/polls.csv"))) if os.path.exists(f"{d}/polls.csv") else []
        t0 = int(r["t0_unix_ns"]) if r["t0_unix_ns"] else (int(polls[0]["ts_send_unix_ns"]) if polls else 0)
        win = [p for p in polls if warm <= (int(p["ts_send_unix_ns"]) - t0) / 1e9 < warm + att]
        base = [p for p in polls if (int(p["ts_send_unix_ns"]) - t0) / 1e9 < warm]
        ok = [p for p in win if p["ok"] == "1"]
        rtt = [float(p["rtt_ms"]) for p in ok]
        rtt_base = [float(p["rtt_ms"]) for p in base if p["ok"] == "1"][1:]  # la 1ª incluye ARP/conexión
        s = {"run_id": r["run_id"], "platform": r["platform"], "scenario": r["scenario"], "attack": r["attack"],
             "ips_mode": r["ips_mode"], "run_profile": r["run_profile"], "rep": r["rep"], "status": r["status"],
             "polls_attack_window": len(win), "polls_ok": len(ok),
             "availability_pct": round(100 * len(ok) / len(win), 2) if win else "",
             "timeouts": sum(1 for p in win if p["error"] == "timeout"),
             "rtt_median_ms": pct(rtt, .5), "rtt_mean_ms": round(statistics.mean(rtt), 3) if rtt else "",
             "rtt_p95_ms": pct(rtt, .95), "rtt_p99_ms": pct(rtt, .99),
             "rtt_baseline_median_ms": pct(rtt_base, .5)}
        try:
            pre = json.load(open(f"{d}/attacker_v10_pre.json"))[0]["stats64"]["tx"]["packets"]
            post = json.load(open(f"{d}/attacker_v10_post.json"))[0]["stats64"]["tx"]["packets"]
            s["attacker_tx_pkts"] = post - pre; s["attacker_pps"] = round((post - pre) / att) if r["attack"] != "none" else 0
        except Exception:
            s["attacker_tx_pkts"] = s["attacker_pps"] = ""
        pc = f"{d}/pcap_counts.csv"
        if os.path.exists(pc):
            tot = {"mir20": 0, "mir30": 0}
            for row in csv.DictReader(open(pc)):
                if row["iface"] in tot: tot[row["iface"]] += int(row["attack_to_plc"])
            s["cap_attack_vlan20"] = tot["mir20"]; s["cap_attack_vlan30"] = tot["mir30"]
            s["cap_attack_removed"] = tot["mir20"] - tot["mir30"]
            s["cap_removed_pct"] = round(100 * (tot["mir20"] - tot["mir30"]) / tot["mir20"], 2) if tot["mir20"] else ""
        cs = f"{d}/capture_stats.txt"
        if os.path.exists(cs):
            m = re.findall(r"received/dropped on interface '([^']+)': (\d+)/(\d+)", open(cs).read())
            s["cap_dropped"] = sum(int(x[2]) for x in m)
            s["cap_drop_pct"] = round(100 * s["cap_dropped"] / max(1, sum(int(x[1]) + int(x[2]) for x in m)), 2)
        st = f"{d}/suricata_stats.jsonl"
        if os.path.exists(st) and os.path.getsize(st):
            L = [json.loads(x) for x in open(st) if x.strip()]
            def g(o, *k):
                for kk in k: o = (o or {}).get(kk) if isinstance(o, dict) else None
                return o or 0
            first, last = L[0], L[-1]
            for name, path in (("ips_blocked", ("ips", "blocked")), ("ips_accepted", ("ips", "accepted"))):
                s[f"suri_{name}"] = g(last, *path) - g(first, *path)
            s["suri_alerts"] = (last.get("alert") or 0) - (first.get("alert") or 0)
            s["suri_decoder_pkts"] = (last.get("decoder_pkts") or 0) - (first.get("decoder_pkts") or 0)
            s["suri_stats_lines"] = len(L)
        def nfq(path):
            # /proc/net/netfilter/nfnetlink_queue: queue pid waiting copy_mode copy_range queue_dropped user_dropped id_seq 1
            try:
                return {l.split()[0]: (int(l.split()[5]), int(l.split()[6])) for l in open(path) if l.split() and l.split()[0].isdigit()}
            except OSError:
                return None
        q0, q1 = nfq(f"{d}/nfq_pre.txt"), nfq(f"{d}/nfq_post.txt")
        if q0 is not None and q1 is not None:
            s["nfq_queue_dropped"] = sum(v[0] - q0.get(k, (0, 0))[0] for k, v in q1.items())
            s["nfq_user_dropped"] = sum(v[1] - q0.get(k, (0, 0))[1] for k, v in q1.items())
        f0, f1 = nft(f"{d}/fw_counters_pre.json"), nft(f"{d}/fw_counters_post.json")
        for k in ("c_v10_plc_tcp502", "c_v10_plc_udp", "c_v10_plc_icmp", "c_fwd_est", "c_fwd_drop"):
            if k in f1: s["fw_" + k[2:]] = f1[k] - f0.get(k, 0)
        s["tctl_max_c"] = r["tctl_max_c"]
        ph = f"{d}/plc_health.txt"
        if os.path.exists(ph):
            txt = open(ph).read()
            s["plc_alive_after"] = "yes" if "alive_after=yes" in txt else ("no" if "alive_after=no" in txt else "")
        out.append(s)
    os.makedirs(f"{REPO}/data/processed", exist_ok=True)
    path = f"{REPO}/data/processed/run_summary_{a.platform}{'_' + a.profile if a.profile else ''}.csv"
    cols = []
    for s in out:
        for k in s:
            if k not in cols: cols.append(k)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(out)
    print(path, len(out), "corridas")
    return 0

if __name__ == "__main__":
    sys.exit(main())
