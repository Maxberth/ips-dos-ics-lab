#!/usr/bin/env python3
"""Resume las corridas de calibración C2/C3 (eve.json completo de alertas y drops) a partir de lo crudo (A22/A23).

Por corrida: alertas y drops por sid, origen y acción; cuántos paquetes/eventos tocan al SCADA legítimo (192.168.20.20);
disponibilidad del SCADA en la ventana de ataque (polls.csv). Solo lee data/raw; escribe
data/processed/calibracion_alertas_<plataforma>.csv. No mezcla con las corridas de la tanda (escenarios E*).
Uso: python3 -I lab/analysis/calibracion_alertas.py --platform laptop-dev
"""
import argparse, collections, csv, gzip, json, os
ap = argparse.ArgumentParser(); ap.add_argument("--platform", required=True); a = ap.parse_args()
R = "data/raw/runs/"; SCADA = "192.168.20.20"; PLC = "192.168.30.10"
runs = [r for r in csv.DictReader(open("data/raw/runs.csv")) if r["platform"] == a.platform and r["scenario"] in ("C2", "C3") and r["status"] == "ok"]
out = f"data/processed/calibracion_alertas_{a.platform}.csv"
with open(out, "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["run_id", "modo", "ataque", "disponibilidad_pct", "alertas_total", "alertas_sid1000004_total", "alertas_sid1000004_desde_scada", "acciones_desde_scada", "eventos_drop_total", "eventos_drop_desde_scada", "pkts_ataque_flujos_distintos"])
    for r in runs:
        d = r["run_id"]; f = f"{R}{d}/eve_alerts.jsonl.gz"
        if not os.path.exists(f): continue
        E = [json.loads(l) for l in gzip.open(f, "rt") if l.strip()]
        al = [e for e in E if e.get("event_type", "alert") == "alert"]; dr = [e for e in E if e.get("event_type") == "drop"]
        m = [e for e in al if e["sid"] == 1000004]; ms = [e for e in m if e["src_ip"] == SCADA]
        ds = [e for e in dr if SCADA in (e["src_ip"], e["dest_ip"])]
        a0, a1 = int(r["t_attack_start_ns"]), int(r["t_attack_end_ns"]); n = ok = 0
        for p in csv.DictReader(open(f"{R}{d}/polls.csv")):
            if a0 <= int(p["ts_send_unix_ns"]) <= a1: n += 1; ok += p["ok"] == "1"
        acc = collections.Counter(e["action"] for e in ms)
        w.writerow([d, r["ips_mode"], r["attack"], round(100 * ok / n, 2) if n else "", len(al), len(m), len(ms), ";".join(f"{k}={v}" for k, v in sorted(acc.items())), len(dr), len(ds), len({e["flow_id"] for e in al})])
print(open(out).read())
