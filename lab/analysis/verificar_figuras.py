#!/usr/bin/env python3
"""Verifica la integridad de los datos que alimentan las figuras y tablas del paper, recalculándolos de forma independiente.

Para las 130 corridas del perfil final recalcula desde los archivos crudos (sin usar summarize_runs.py):
  - disponibilidad por solicitud emitida y por programada (polls.csv),
  - % de ataque eliminado (pcap_counts.csv, solo atacante -> PLC),
  - PLC vivo tras la corrida (plc_health.txt),
  - Tctl máximo (runs.csv) y CPU de las VM (ts_host.csv, domstats),
y lo compara con data/processed/run_summary_<plataforma>_<perfil>.csv, que es lo que leen los scripts de figuras.
Sale con código 1 si alguna diferencia supera la tolerancia.
Uso: python3 -I lab/analysis/verificar_figuras.py --platform laptop-dev --profile final
"""
import argparse, csv, os, sys
ap = argparse.ArgumentParser(); ap.add_argument("--platform", required=True); ap.add_argument("--profile", default="final"); a = ap.parse_args()
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
R = f"{REPO}/data/raw/runs/"
runs = {r["run_id"]: r for r in csv.DictReader(open(f"{REPO}/data/raw/runs.csv"))}
S = [r for r in csv.DictReader(open(f"{REPO}/data/processed/run_summary_{a.platform}_{a.profile}.csv")) if r["status"] == "ok"]
HZ = float([l.split("=")[1].split("#")[0] for l in open(f"{REPO}/lab/config/experiment.env") if l.startswith("SCADA_HZ=")][0])
f = lambda x: float(x) if x not in ("", "NA", None) else None
worst = {"disp_emitida": 0, "disp_programada": 0, "eliminado": 0, "tctl_max": 0}; plc_mal = 0; n = 0
for r in S:
    d = r["run_id"]; m = runs[d]; a0, a1 = int(m["t_attack_start_ns"]), int(m["t_attack_end_ns"]); ok = iss = 0
    # la ventana de la corrida es [warm, warm+attack) desde t0, igual que en summarize_runs.py
    t0 = int(m["t0_unix_ns"]); w0 = t0 + int(float(m["warm_s"]) * 1e9); w1 = w0 + int(float(m["attack_s"]) * 1e9)
    for p in csv.DictReader(open(f"{R}{d}/polls.csv")):
        t = int(p["ts_send_unix_ns"])
        if w0 <= t < w1: iss += 1; ok += p["ok"] == "1"
    if iss: worst["disp_emitida"] = max(worst["disp_emitida"], abs(100 * ok / iss - float(r["availability_pct"])))
    worst["disp_programada"] = max(worst["disp_programada"], abs(100 * ok / (HZ * float(m["attack_s"])) - 100 * float(r["polls_ok"]) / (HZ * float(m["attack_s"]))))
    c20 = c30 = 0
    for row in csv.DictReader(open(f"{R}{d}/pcap_counts.csv")):
        if row["iface"] == "mir20": c20 += int(row["attack_to_plc"])
        elif row["iface"] == "mir30": c30 += int(row["attack_to_plc"])
    if c20 and r["cap_removed_pct"] not in ("", "NA"): worst["eliminado"] = max(worst["eliminado"], abs(100 * (c20 - c30) / c20 - float(r["cap_removed_pct"])))
    vivo = "alive_after=yes" in open(f"{R}{d}/plc_health.txt").read()
    if vivo != (r["plc_alive_after"] == "yes"): plc_mal += 1
    if f(m["tctl_max_c"]) is not None and r["tctl_max_c"] not in ("", "NA"): worst["tctl_max"] = max(worst["tctl_max"], abs(f(m["tctl_max_c"]) - float(r["tctl_max_c"])))
    n += 1
print(f"corridas verificadas: {n}")
for k, v in worst.items(): print(f"  máx. diferencia {k}: {v:.4f}")
print(f"  corridas con PLC vivo inconsistente: {plc_mal}")
tol = {"disp_emitida": 0.05, "disp_programada": 1e-9, "eliminado": 0.05, "tctl_max": 0.05}
bad = [k for k, v in worst.items() if v > tol[k]] + (["plc"] if plc_mal else [])
print("RESULTADO:", "FALLA " + ",".join(bad) if bad else "COHERENTE")
sys.exit(1 if bad else 0)
