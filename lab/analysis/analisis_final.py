#!/usr/bin/env python3
"""Análisis y figuras de la tanda real (perfil final) de una plataforma, leyendo SOLO de los datos del repositorio.

Fuentes (nada está escrito a mano en este script):
  data/raw/runs.csv                         metadatos y estado de cada corrida
  data/raw/runs/<run_id>/polls.csv          cada solicitud Modbus del SCADA (serie por segundo)
  data/processed/run_summary_<plat>_<perfil>.csv   métricas por corrida (lab/analysis/summarize_runs.py, desde lo crudo)
  data/processed/runs_guard_muestras_*.csv     campos térmicos reconstruidos (A20), solo para marcar corridas
Salida: data/processed/analisis_<plat>_<perfil>.csv (n, media, DE, IC95, mín, mediana, máx por escenario, ataque y métrica).
Las figuras se generan en lab/analysis/figuras_paper.py y figuras_arquitectura.py (figures/paper/).
Uso: python3 -I lab/analysis/analisis_final.py --platform laptop-dev --profile final
"""
import argparse, csv, glob, math, os, statistics as st
from collections import defaultdict
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ap = argparse.ArgumentParser(); ap.add_argument("--platform", required=True); ap.add_argument("--profile", default="final")
A = ap.parse_args(); P = f"{A.platform}_{A.profile}"
FIG = f"{REPO}/figures"; os.makedirs(FIG, exist_ok=True)
SC = ["E0", "E1", "E2", "E3"]; AT = ["syn", "udp", "icmp", "modbus"]
COL = {"E0": "#6b6b6b", "E1": "#1f77b4", "E2": "#d98a00", "E3": "#c0392b"}
NOM = {"E0": "E0 sin ataque", "E1": "E1 IPS router", "E2": "E2 Suricata alert", "E3": "E3 Suricata drop"}
plt.rcParams.update({"figure.dpi": 130, "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.alpha": .25, "font.size": 9})

runs = {r["run_id"]: r for r in csv.DictReader(open(f"{REPO}/data/raw/runs.csv"))}
S = [r for r in csv.DictReader(open(f"{REPO}/data/processed/run_summary_{P}.csv")) if r["status"] == "ok"]
f = lambda r, k: float(r[k]) if r.get(k, "") not in ("", "NA") else None
tc = {}
for p in glob.glob(f"{REPO}/data/processed/runs_guard_muestras_{P}.csv"):
    for r in csv.DictReader(open(p)): tc[r["run_id"]] = r
AFF = set(tc)  # corridas con algún campo térmico vacío por A20
FRIA = {k for k, v in tc.items() if "tctl_start_c" in v["campos_vacios_en_runs_csv"]}  # esperaron ~20 min: arranque frío
HZ = float([l.split("=")[1].split("#")[0] for l in open(f"{REPO}/lab/config/experiment.env") if l.startswith("SCADA_HZ=")][0])
for r in S:  # respuestas válidas respecto a las solicitudes PROGRAMADAS (HZ x segundos de ataque), no solo las emitidas (A24)
    r["resp_vs_programadas_pct"] = 100 * float(r["polls_ok"]) / (HZ * float(runs[r["run_id"]]["attack_s"]))
    r["polls_emitidas_pct"] = 100 * float(r["polls_attack_window"]) / (HZ * float(runs[r["run_id"]]["attack_s"]))
by = defaultdict(list)
for r in S: by[(r["scenario"], r["attack"])].append(r)

def tcrit(n):
    from scipy import stats
    return stats.t.ppf(0.975, n - 1) if n > 1 else float("nan")
def agg(v):
    v = [x for x in v if x is not None]; n = len(v)
    if not n: return dict(n=0)
    m = st.mean(v); sd = st.stdev(v) if n > 1 else 0.0
    return dict(n=n, mean=m, sd=sd, ci95=tcrit(n) * sd / math.sqrt(n) if n > 1 else float("nan"), min=min(v), max=max(v), median=st.median(v))

# ---- tabla agregada ----
MET = ["availability_pct", "rtt_median_ms", "rtt_p95_ms", "attacker_pps", "cap_removed_pct", "tctl_max_c", "cpu_mhz_attack", "suri_alerts", "suri_decoder_pkts", "resp_vs_programadas_pct", "polls_emitidas_pct"]
with open(f"{REPO}/data/processed/analisis_{P}.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["scenario", "attack", "metric", "n", "mean", "sd", "ci95", "min", "median", "max", "plc_alive_after_no"])
    for (s, a), rs in sorted(by.items()):
        down = sum(1 for r in rs if r["plc_alive_after"] != "yes")
        for m in MET:
            g = agg([f(r, m) for r in rs])
            if g["n"]: w.writerow([s, a, m, g["n"], *(round(g[k], 3) for k in ("mean", "sd", "ci95", "min", "median", "max")), down])

print("corridas ok:", len(S), "| afectadas A20 en el resumen:", len([r for r in S if r["run_id"] in AFF]))
for (s, a), rs in sorted(by.items()):
    g = agg([f(r, "availability_pct") for r in rs]); print(f"{s} {a:6s} n={g['n']:2d} disp={g['mean']:6.2f}±{g['ci95']:.2f} [{g['min']:.1f}-{g['max']:.1f}]")
