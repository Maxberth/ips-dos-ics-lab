#!/usr/bin/env python3
"""Análisis y figuras de la tanda real (perfil final) de una plataforma, leyendo SOLO de los datos del repositorio.

Fuentes (nada está escrito a mano en este script):
  data/raw/runs.csv                         metadatos y estado de cada corrida
  data/raw/runs/<run_id>/polls.csv          cada solicitud Modbus del SCADA (serie por segundo)
  data/processed/run_summary_<plat>_<perfil>.csv   métricas por corrida (lab/analysis/summarize_runs.py, desde lo crudo)
  data/processed/runs_guard_muestras_*.csv     campos térmicos reconstruidos (A20), solo para marcar corridas
Salidas:
  figures/<plat>_<perfil>_a1_disponibilidad.png      disponibilidad por escenario y ataque (cada punto = una corrida)
  figures/<plat>_<perfil>_a2_rtt_p95.png             RTT p95 (escala log)
  figures/<plat>_<perfil>_a3_disponibilidad_en_el_tiempo.png   disponibilidad por segundo respecto al inicio del ataque
  figures/<plat>_<perfil>_a4_eliminacion_ips.png     % del ataque eliminado y parte por saturación
  figures/<plat>_<perfil>_a5_termica.png             Tctl y frecuencia de CPU por corrida (¿throttling?)
  figures/<plat>_<perfil>_a6_a20_e3_icmp.png         corridas afectadas por A20 frente a las de referencia (E3 ICMP)
  data/processed/analisis_<plat>_<perfil>.csv        tabla agregada (n, media, DE, IC95, mín, máx)
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
MET = ["availability_pct", "rtt_median_ms", "rtt_p95_ms", "attacker_pps", "cap_removed_pct", "tctl_max_c", "cpu_mhz_attack"]
with open(f"{REPO}/data/processed/analisis_{P}.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["scenario", "attack", "metric", "n", "mean", "sd", "ci95", "min", "median", "max", "plc_alive_after_no"])
    for (s, a), rs in sorted(by.items()):
        down = sum(1 for r in rs if r["plc_alive_after"] != "yes")
        for m in MET:
            g = agg([f(r, m) for r in rs])
            if g["n"]: w.writerow([s, a, m, g["n"], *(round(g[k], 3) for k in ("mean", "sd", "ci95", "min", "median", "max")), down])

# ---- a1 y a2: puntos por corrida + media ----
def strip(metric, ylabel, fname, log=False, title=""):
    fig, ax = plt.subplots(figsize=(8, 4.2)); xs = {}
    for i, a in enumerate(AT):
        for j, s in enumerate(["E1", "E2", "E3"]):
            x = i + (j - 1) * .26; vals = [f(r, metric) for r in by.get((s, a), [])]; vals = [v for v in vals if v is not None]
            if not vals: continue
            ax.scatter([x + (k - len(vals) / 2) * .012 for k in range(len(vals))], vals, s=14, color=COL[s], alpha=.55, lw=0, label=NOM[s] if i == 0 else None)
            ax.hlines(st.mean(vals), x - .11, x + .11, color=COL[s], lw=2)
    e0 = [f(r, metric) for r in by.get(("E0", "none"), [])]; e0 = [v for v in e0 if v is not None]
    if e0: ax.axhline(st.mean(e0), color=COL["E0"], ls="--", lw=1, label="E0 sin ataque (media)")
    ax.set_xticks(range(len(AT))); ax.set_xticklabels(AT); ax.set_ylabel(ylabel)
    if log: ax.set_yscale("log")
    ax.set_title(title, loc="left", fontsize=10); ax.legend(frameon=False, fontsize=8, ncol=4, loc="upper center", bbox_to_anchor=(.5, -.1))
    fig.tight_layout(); fig.savefig(f"{FIG}/{A.platform}_{A.profile}_{fname}.png"); plt.close(fig)
strip("availability_pct", "Disponibilidad del SCADA durante el ataque (%)", "a1_disponibilidad", title=f"Disponibilidad por escenario y ataque ({A.platform}, perfil {A.profile}; punto = corrida, línea = media)")
strip("rtt_p95_ms", "RTT p95 (ms, escala log)", "a2_rtt_p95", log=True, title="Latencia (RTT p95) del tráfico legítimo durante el ataque")

# ---- a3: disponibilidad por segundo respecto al inicio del ataque (de polls.csv) ----
fig, axs = plt.subplots(1, 4, figsize=(12, 3.2), sharey=True)
for ax, a in zip(axs, AT):
    for s in ["E1", "E2", "E3"]:
        acc = defaultdict(lambda: [0, 0])
        for r in by.get((s, a), []):
            m = runs[r["run_id"]]; t0 = int(m["t_attack_start_ns"]); t1 = int(m["t_attack_end_ns"])
            for p in csv.DictReader(open(f"{REPO}/data/raw/runs/{r['run_id']}/polls.csv")):
                b = (int(p["ts_send_unix_ns"]) - t0) // 10**9
                if -10 <= b <= 70: acc[b][0] += p["ok"] == "1"; acc[b][1] += 1
        xs = sorted(acc); ax.plot(xs, [100 * acc[x][0] / acc[x][1] for x in xs], color=COL[s], lw=1.3, label=NOM[s])
    ax.axvspan(0, 60, color="#000", alpha=.05); ax.set_title(a); ax.set_xlabel("s desde el inicio del ataque")
axs[0].set_ylabel("solicitudes con respuesta (%)"); axs[0].legend(frameon=False, fontsize=7, loc="lower left")
fig.suptitle("Disponibilidad por segundo (media de las corridas; banda = ventana de ataque)", x=.01, ha="left", fontsize=10)
fig.tight_layout(); fig.savefig(f"{FIG}/{A.platform}_{A.profile}_a3_disponibilidad_en_el_tiempo.png"); plt.close(fig)

# ---- a4: % eliminado y saturación (E2/E3) ----
fig, ax = plt.subplots(figsize=(8, 3.4)); w = .26
for j, s in enumerate(["E1", "E2", "E3"]):
    ys = []
    for a in AT:
        v = [f(r, "cap_removed_pct") for r in by.get((s, a), [])]; v = [x for x in v if x is not None]; ys.append(st.mean(v) if v else 0)
    ax.bar([i + (j - 1) * w for i in range(len(AT))], ys, w, color=COL[s], label=NOM[s])
ax.set_xticks(range(len(AT))); ax.set_xticklabels(AT); ax.set_ylabel("ataque eliminado (%)"); ax.set_ylim(0, 105)
ax.set_title("Paquetes de ataque eliminados por el IPS (captura, solo atacante→PLC; la saturación de la cola mezcla sentidos, ver A21)", loc="left", fontsize=9)
ax.legend(frameon=False, fontsize=8); fig.tight_layout(); fig.savefig(f"{FIG}/{A.platform}_{A.profile}_a4_eliminacion_ips.png"); plt.close(fig)

# ---- a5: térmica por corrida, en orden cronológico ----
fig, (a1, a2) = plt.subplots(2, 1, figsize=(9, 4.6), sharex=True)
ordered = sorted(S, key=lambda r: r["run_id"])
for i, r in enumerate(ordered):
    c = COL[r["scenario"]]; mk = "x" if r["run_id"] in FRIA else "o"
    if f(r, "tctl_max_c") is not None: a1.scatter(i, f(r, "tctl_max_c"), color=c, s=12, marker=mk)
    if f(r, "cpu_mhz_attack") is not None: a2.scatter(i, f(r, "cpu_mhz_attack"), color=c, s=12, marker=mk)
a1.axhline(88, color="k", ls=":", lw=1); a1.text(0, 88.5, "umbral PAUSE 88 °C", fontsize=7); a1.set_ylabel("Tctl máx. (°C)")
a2.set_ylabel("MHz medios en el ataque"); a2.set_xlabel("corrida (orden cronológico); × = arranque frío por A20")
a1.set_title("Temperatura y frecuencia de CPU de la laptop durante la tanda (color = escenario)", loc="left", fontsize=10)
fig.tight_layout(); fig.savefig(f"{FIG}/{A.platform}_{A.profile}_a5_termica.png"); plt.close(fig)

# ---- a6: E3 ICMP, afectadas por A20 frente a referencia ----
fig, axs = plt.subplots(1, 2, figsize=(8, 3.2))
for ax, (m, lab) in zip(axs, [("availability_pct", "disponibilidad (%)"), ("rtt_median_ms", "RTT mediana (ms)")]):
    for k, (nm, sel) in enumerate([("referencia", lambda r: r["run_id"] not in FRIA), ("afectadas A20", lambda r: r["run_id"] in FRIA)]):
        v = [f(r, m) for r in by.get(("E3", "icmp"), []) if sel(r)]; v = [x for x in v if x is not None]
        ax.scatter([k + (i - len(v) / 2) * .03 for i in range(len(v))], v, color=COL["E3"], s=18, alpha=.7)
        if v: ax.hlines(st.mean(v), k - .15, k + .15, color="k", lw=2)
    ax.set_xticks([0, 1]); ax.set_xticklabels(["referencia", "arranque frío (A20)"]); ax.set_ylabel(lab)
fig.suptitle("E3 ICMP: arranque frío (A20) frente al resto (n pequeño; los rangos se solapan)", x=.01, ha="left", fontsize=10)
fig.tight_layout(); fig.savefig(f"{FIG}/{A.platform}_{A.profile}_a6_a20_e3_icmp.png"); plt.close(fig)

print("corridas ok:", len(S), "| afectadas A20 en el resumen:", len([r for r in S if r["run_id"] in AFF]))
for (s, a), rs in sorted(by.items()):
    g = agg([f(r, "availability_pct") for r in rs]); print(f"{s} {a:6s} n={g['n']:2d} disp={g['mean']:6.2f}±{g['ci95']:.2f} [{g['min']:.1f}-{g['max']:.1f}]")
