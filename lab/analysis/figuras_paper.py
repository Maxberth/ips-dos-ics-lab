#!/usr/bin/env python3
"""Figuras de resultados del paper, generadas SOLO desde los datos del repositorio, al ancho de LNCS (4,8 in).

Fuentes: data/raw/runs.csv, data/raw/runs/<id>/{polls.csv,ts_host.csv}, data/processed/run_summary_<plat>_<perfil>.csv
Salida: figures/paper/<nombre>.png (300 dpi) y .pdf (vector). Texto de las figuras en inglés por defecto (el paper está en
inglés; --lang es para la versión en español). Una figura = un archivo = un mensaje; las leyendas van fuera de los datos.
Uso: python3 -I lab/analysis/figuras_paper.py --platform laptop-dev --profile final [--lang en|es]
"""
import argparse, csv, math, os, sys, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # con -I el directorio del script no entra solo
from collections import defaultdict
import estilo_figuras as E
import matplotlib.pyplot as plt

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ap = argparse.ArgumentParser(); ap.add_argument("--platform", required=True); ap.add_argument("--profile", default="final"); ap.add_argument("--lang", default="en")
A = ap.parse_args(); P = f"{A.platform}_{A.profile}"; DEST = f"{REPO}/figures/paper" + ("" if A.lang == "en" else "_es")
E.aplicar()
T = {"en": dict(E1="E1 Router only (no IPS)", E2="E2 Suricata alert", E3="E3 Suricata drop", E0="E0 No attack",
                syn="TCP SYN", udp="UDP", icmp="ICMP", modbus="Modbus/TCP",
                av_iss="Valid replies / issued (%)", av_sch="Valid replies / scheduled (%)",
                rtt="p95 round-trip time (ms)", t="Time from attack start (s)", resp="Valid replies (%)",
                rem="Attack packets removed (%)", plcdown="Runs with PLC down\nafter the attack (of 10)",
                cpu_ips="lab-ips VM", cpu_plc="lab-plc VM", cpu_y="vCPU time / (vCPUs x wall time) (%)", base="E0 mean", attack="attack window",
                tmax="Peak Tctl (°C)", mhz="Mean CPU clock\nduring attack (MHz)", run="Run (chronological order)"),
     "es": dict(E1="E1 Solo router (sin IPS)", E2="E2 Suricata alert", E3="E3 Suricata drop", E0="E0 Sin ataque",
                syn="TCP SYN", udp="UDP", icmp="ICMP", modbus="Modbus/TCP",
                av_iss="Resp. válidas / emitidas (%)", av_sch="Resp. válidas / programadas (%)",
                rtt="RTT p95 (ms)", t="Tiempo desde el inicio del ataque (s)", resp="Respuestas válidas (%)",
                rem="Paquetes de ataque eliminados (%)", plcdown="Corridas con PLC caído\ntras el ataque (de 10)",
                cpu_ips="VM lab-ips", cpu_plc="VM lab-plc", cpu_y="tiempo de vCPU / (vCPUs x tiempo) (%)", base="Media E0", attack="ventana de ataque",
                tmax="Tctl máx. (°C)", mhz="Frecuencia media de CPU\ndurante el ataque (MHz)", run="Corrida (orden cronológico)")}[A.lang]
AT = ["syn", "udp", "icmp", "modbus"]; SC = ["E1", "E2", "E3"]
runs = {r["run_id"]: r for r in csv.DictReader(open(f"{REPO}/data/raw/runs.csv"))}
S = [r for r in csv.DictReader(open(f"{REPO}/data/processed/run_summary_{P}.csv")) if r["status"] == "ok"]
HZ = float([l.split("=")[1].split("#")[0] for l in open(f"{REPO}/lab/config/experiment.env") if l.startswith("SCADA_HZ=")][0])
f = lambda r, k: float(r[k]) if r.get(k, "") not in ("", "NA", None) else None
for r in S:
    att = float(runs[r["run_id"]]["attack_s"])
    r["resp_sch"] = 100 * float(r["polls_ok"]) / (HZ * att)
by = defaultdict(list)
for r in S: by[(r["scenario"], r["attack"])].append(r)
vals = lambda s, a, k: [x for x in (f(r, k) for r in by.get((s, a), [])) if x is not None]
def ci95(v):
    from scipy import stats
    return stats.t.ppf(.975, len(v) - 1) * st.stdev(v) / math.sqrt(len(v)) if len(v) > 1 else 0

def leyenda(fig, ncol=3, y=None, patches=False, e0=False):
    if patches: h = [plt.Rectangle((0, 0), 1, 1, fc=E.COL[s], label=T[s]) for s in SC]
    else: h = [plt.Line2D([], [], marker=E.MARK[s], color=E.COL[s], ls="", ms=4.5, label=T[s]) for s in SC]
    if e0: h.append(plt.Line2D([], [], color=E.COL["E0"], ls="--", lw=.8, label=T["base"]))
    fig.legend(handles=h, loc="outside upper center", ncol=ncol if not e0 else 4, frameon=False, columnspacing=1.0, handletextpad=.3)

def puntos(ax, metrica, ylabel, ylog=False, e0=True):
    for i, a in enumerate(AT):
        for j, s in enumerate(SC):
            v = vals(s, a, metrica); x0 = i + (j - 1) * .27
            ax.scatter([x0 + (k - (len(v) - 1) / 2) * .018 for k in range(len(v))], v, s=7, color=E.COL[s], marker=E.MARK[s], alpha=.6, lw=0)
            ax.hlines(st.mean(v), x0 - .11, x0 + .11, color="k", lw=1.0, zorder=5)
    if e0:
        v0 = vals("E0", "none", metrica)
        if v0: ax.axhline(st.mean(v0), color=E.COL["E0"], ls="--", lw=.7)
    ax.set_xticks(range(len(AT))); ax.set_xticklabels([T[a] for a in AT]); ax.set_ylabel(ylabel); ax.set_xlim(-.55, len(AT) - .45)
    if ylog: ax.set_yscale("log")

# R1: disponibilidad (a) por solicitud emitida y (b) respecto a lo programado
fig, (a1, a2) = plt.subplots(2, 1, figsize=(E.W, 3.7), sharex=True, constrained_layout=True)
puntos(a1, "availability_pct", T["av_iss"]); puntos(a2, "resp_sch", T["av_sch"])
for ax, l in ((a1, "(a)"), (a2, "(b)")): ax.set_title(l, loc="left", fontweight="bold", fontsize=8, pad=2)
for ax in (a1, a2): ax.set_ylim(-4, 106)
leyenda(fig, e0=True); E.guardar(fig, DEST, "r1_availability")

# R2: RTT p95 (escala log)
fig, ax = plt.subplots(figsize=(E.W, 2.7), constrained_layout=True)
puntos(ax, "rtt_p95_ms", T["rtt"], ylog=True); leyenda(fig, e0=True); E.guardar(fig, DEST, "r2_rtt_p95")

# R3: serie por segundo (de polls.csv), 2x2
fig, axs = plt.subplots(2, 2, figsize=(E.W, 3.1), sharex=True, sharey=True, constrained_layout=True)
for ax, a in zip(axs.flat, AT):
    for s in SC:
        acc = defaultdict(lambda: [0, 0])
        for r in by.get((s, a), []):
            m = runs[r["run_id"]]; t0 = int(m["t_attack_start_ns"])
            for p in csv.DictReader(open(f"{REPO}/data/raw/runs/{r['run_id']}/polls.csv")):
                b = (int(p["ts_send_unix_ns"]) - t0) // 10**9
                if -10 <= b <= 70: acc[b][0] += p["ok"] == "1"; acc[b][1] += 1
        xs = sorted(acc); ax.plot(xs, [100 * acc[x][0] / acc[x][1] for x in xs], color=E.COL[s], lw=.9, label=T[s])
    ax.axvspan(0, 60, color="k", alpha=.05, lw=0); ax.set_title(T[a], loc="left", pad=2); ax.set_ylim(-4, 106)
for ax in axs[1]: ax.set_xlabel(T["t"])
for ax in axs[:, 0]: ax.set_ylabel(T["resp"])
leyenda(fig); E.guardar(fig, DEST, "r3_availability_timeseries")

# R4: ataque eliminado (captura: solo atacante -> PLC), media e IC95
fig, ax = plt.subplots(figsize=(E.W, 2.2), constrained_layout=True); w = .26
for j, s in enumerate(SC):
    ys, es = [], []
    for a in AT:
        v = vals(s, a, "cap_removed_pct"); ys.append(st.mean(v) if v else 0); es.append(ci95(v) if v else 0)
    ax.bar([i + (j - 1) * w for i in range(4)], ys, w, yerr=es, color=E.COL[s], error_kw=dict(lw=.6, capsize=1.5), label=T[s])
ax.set_xticks(range(4)); ax.set_xticklabels([T[a] for a in AT]); ax.set_ylabel(T["rem"]); ax.set_ylim(0, 108)
leyenda(fig, patches=True); E.guardar(fig, DEST, "r4_attack_removed")

# R5: PLC caído tras el ataque
fig, ax = plt.subplots(figsize=(E.W, 2.2), constrained_layout=True)
for j, s in enumerate(SC):
    ys = [sum(r["plc_alive_after"] != "yes" for r in by.get((s, a), [])) for a in AT]
    b = ax.bar([i + (j - 1) * w for i in range(4)], ys, w, color=E.COL[s])
    for x, y in zip([i + (j - 1) * w for i in range(4)], ys): ax.text(x, y + .25, str(y), ha="center", fontsize=6)
ax.set_xticks(range(4)); ax.set_xticklabels([T[a] for a in AT]); ax.set_ylabel(T["plcdown"]); ax.set_ylim(0, 12.5)
leyenda(fig, patches=True); E.guardar(fig, DEST, "r5_plc_down")

# R6: CPU de las VMs durante el ataque (domstats cpu.time de ts_host.csv)
prof = open(f"{REPO}/lab/config/profile_{A.platform}.env").read()
vcpus = lambda n: float(prof.split(n + "_VCPUS=")[1].split(";")[0].split()[0])
VC = {"lab-ips": vcpus("VM_IPS"), "lab-plc": vcpus("VM_PLC")}
def cpu(rid, vm):
    m = runs[rid]; a0, a1 = int(m["t_attack_start_ns"]), int(m["t_attack_end_ns"]); pts = []
    for row in csv.DictReader(open(f"{REPO}/data/raw/runs/{rid}/ts_host.csv")):
        if row["source"] == "domstats" and row["entity"] == vm and row["key"] == "cpu.time" and a0 <= int(row["ts_unix_ns"]) <= a1:
            pts.append((int(row["ts_unix_ns"]), float(row["value"])))
    if len(pts) < 2: return None
    return 100 * (pts[-1][1] - pts[0][1]) / ((pts[-1][0] - pts[0][0]) * VC[vm])
fig, axs = plt.subplots(1, 2, figsize=(E.W, 2.3), sharey=True, constrained_layout=True)
for ax, vm, lab in zip(axs, ("lab-ips", "lab-plc"), (T["cpu_ips"], T["cpu_plc"])):
    for j, s in enumerate(["E1", "E2", "E3"]):
        ys = []
        for a in AT:
            v = [x for x in (cpu(r["run_id"], vm) for r in by.get((s, a), [])) if x is not None]; ys.append(st.mean(v) if v else 0)
        ax.bar([i + (j - 1) * w for i in range(4)], ys, w, color=E.COL[s])
    ax.set_xticks(range(4)); ax.set_xticklabels([T[a] for a in AT], rotation=30, ha="right"); ax.set_title(lab, pad=2)
axs[0].set_ylabel(T["cpu_y"]); leyenda(fig, patches=True); E.guardar(fig, DEST, "r6_vm_cpu")

# R7 (material suplementario): temperatura y frecuencia por corrida
fig, (t1, t2) = plt.subplots(2, 1, figsize=(E.W, 3.2), sharex=True, constrained_layout=True)
for i, r in enumerate(sorted(S, key=lambda r: r["run_id"])):
    for ax, k in ((t1, "tctl_max_c"), (t2, "cpu_mhz_attack")):
        v = f(r, k)
        if v is not None: ax.scatter(i, v, s=5, color=E.COL[r["scenario"]], marker=E.MARK[r["scenario"]], lw=0)
t1.set_ylabel(T["tmax"]); t2.set_ylabel(T["mhz"]); t2.set_xlabel(T["run"])
h = [plt.Line2D([], [], marker=E.MARK[s], color=E.COL[s], ls="", ms=4, label=T[s]) for s in ("E0", "E1", "E2", "E3")]
fig.legend(handles=h, loc="outside upper center", ncol=4, frameon=False, columnspacing=1, handletextpad=.3)
E.guardar(fig, DEST, "r7_thermal")
print("figuras en", DEST, sorted(os.listdir(DEST)))
