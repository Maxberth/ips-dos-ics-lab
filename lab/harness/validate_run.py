#!/usr/bin/env python3
"""Audita una corrida cruda (data/raw/runs/<run_id>/) y devuelve OK / WARN / FAIL con motivos.

No calcula resultados para el paper: solo comprueba que los datos crudos son completos y plausibles.
La última línea de salida es "VEREDICTO motivo1|motivo2" (run_once.sh la guarda en runs.csv).
Uso: validate_run.py <dir_corrida> --attack syn --mode drop
"""
import argparse, csv, json, os, re, sys

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir"); ap.add_argument("--attack", default="none"); ap.add_argument("--mode", default="router")
    a = ap.parse_args()
    d = a.run_dir; fails, warns, info = [], [], []

    # 1. Sondeo SCADA
    p = os.path.join(d, "polls.csv")
    rows = list(csv.DictReader(open(p))) if os.path.exists(p) and os.path.getsize(p) else []
    if not rows:
        fails.append("polls.csv vacío")
    else:
        seq = [int(r["seq"]) for r in rows]
        if seq != list(range(len(seq))):
            fails.append("seq no consecutivo")
        mono = [int(r["ts_send_mono_ns"]) for r in rows]
        if any(b < a_ for a_, b in zip(mono, mono[1:])):
            fails.append("ts_send no monótono")
        gaps = [(b - a_) / 1e6 for a_, b in zip(mono, mono[1:])]
        late = sum(1 for g in gaps if g > 250)
        if late:
            warns.append(f"{late} huecos >250ms en el envío del poller")
        okn = sum(int(r["ok"]) for r in rows)
        rtts = [float(r["rtt_ms"]) for r in rows if r["ok"] == "1"]
        if any(x < 0 for x in rtts):
            fails.append("RTT negativo")
        if any(r["ok"] == "1" and not r["rtt_ms"] for r in rows):
            fails.append("ok sin RTT")
        info.append(f"polls={len(rows)} ok={okn}")
        if a.attack == "none" and okn < len(rows):
            warns.append(f"{len(rows) - okn} solicitudes fallidas sin ataque")

    # 2. Muestreo del host
    h = os.path.join(d, "ts_host.csv")
    if not os.path.exists(h) or os.path.getsize(h) < 100:
        fails.append("ts_host.csv vacío")
    else:
        ts = sorted({r["ts_unix_ns"] for r in csv.DictReader(open(h))})
        info.append(f"host_samples={len(ts)}")

    # 3. Captura
    c = os.path.join(d, "capture_stats.txt")
    if os.path.exists(c):
        txt = open(c).read()
        m = re.findall(r"Packets dropped[^:]*:\s*(\d+)", txt) or re.findall(r"dropped[^\d]*(\d+)", txt)
        drops = sum(int(x) for x in m)
        if drops:
            warns.append(f"captura descartó {drops} paquetes")
    else:
        warns.append("sin capture_stats.txt")

    # 4. El ataque ocurrió (contador tx de v10 del atacante)
    if a.attack != "none":
        try:
            pre = json.load(open(os.path.join(d, "attacker_v10_pre.json")))[0]["stats64"]["tx"]["packets"]
            post = json.load(open(os.path.join(d, "attacker_v10_post.json")))[0]["stats64"]["tx"]["packets"]
            info.append(f"attacker_tx_pkts={post - pre}")
            if post - pre < 1000:
                fails.append("el atacante casi no transmitió")
        except Exception as e:
            fails.append(f"contadores del atacante ilegibles ({type(e).__name__})")

    # 5. Suricata
    if a.mode != "router":
        s = os.path.join(d, "suricata_stats.jsonl")
        if not os.path.exists(s) or os.path.getsize(s) == 0:
            fails.append("sin estadísticas de Suricata")
        st = os.path.join(d, "suricata_state_post.txt")
        if os.path.exists(st) and "active" != open(st).read().strip():
            fails.append("Suricata no estaba activo al final")

    verdict = "FAIL" if fails else ("WARN" if warns else "OK")
    print(" ".join(info))
    print(f"{verdict} " + "|".join(fails + warns))
    return 0

if __name__ == "__main__":
    sys.exit(main())
