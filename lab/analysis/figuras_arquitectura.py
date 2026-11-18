#!/usr/bin/env python3
"""Diagramas de arquitectura y diseño experimental del paper (matplotlib, vectorial), al ancho de LNCS (4,8 in).

Los datos que aparecen (VLAN, subredes, hosts, reglas de nftables, repeticiones, duración de las fases) se leen de
lab/config (profile_<plataforma>.env, experiment.env, nftables-nfq.conf) para que no se desincronicen del laboratorio.
Salida: figures/paper/a0_logical_topology, a1_topology, a2_ips_datapath, a3_experiment_design (.png 300 dpi y .pdf).
Uso: python3 -I lab/analysis/figuras_arquitectura.py --platform laptop-dev [--lang en|es]
"""
import argparse, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import estilo_figuras as E
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ap = argparse.ArgumentParser(); ap.add_argument("--platform", required=True); ap.add_argument("--lang", default="en"); A = ap.parse_args()
DEST = f"{REPO}/figures/paper" + ("" if A.lang == "en" else "_es")
E.aplicar(); plt.rcParams["axes.grid"] = False
prof = open(f"{REPO}/lab/config/profile_{A.platform}.env").read(); exp = open(f"{REPO}/lab/config/experiment.env").read()
def vm(n):
    mem = int(re.search(rf"VM_{n}_MEM=(\d+)", prof).group(1)); cpu = int(re.search(rf"VM_{n}_VCPUS=(\d+)", prof).group(1))
    return f"{cpu} vCPU\n{mem / 1024:g} GiB"
warm, att, cool = (int(re.search(rf"final_{k}=(\d+)", exp).group(1)) for k in ("WARM", "ATTACK", "COOL"))
hz = int(re.search(r"SCADA_HZ=(\d+)", exp).group(1))
nft = open(f"{REPO}/lab/config/ips/nftables-nfq.conf").read(); q = re.search(r"queue num (\d+-\d+)", nft).group(1)
EN = A.lang == "en"

def box(ax, x, y, w, h, txt, fc="#ffffff", ec="#333", fs=6.5, bold=False, lw=.7, ls="-"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.005,rounding_size=0.012", fc=fc, ec=ec, lw=lw, ls=ls))
    ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=fs, fontweight="bold" if bold else "normal", linespacing=1.2)
def arrow(ax, p, q, txt=None, c="#222", style="-|>", lw=.9, ls="-", off=(0, .02), fs=6):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=7, lw=lw, color=c, ls=ls, shrinkA=0, shrinkB=0))
    if txt: ax.text((p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], txt, ha="center", va="bottom", fontsize=fs, color=c)
def lienzo(h):
    fig, ax = plt.subplots(figsize=(E.W, h)); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off"); return fig, ax

# ---------- A0: topología lógica propuesta (mismo formato que la Fig. 1 original: flujo vertical de cajas grises) ----------
fig, ax = plt.subplots(figsize=(3.6, 3.4)); ax.set_xlim(0, 1); ax.set_ylim(-.04, 1.04); ax.axis("off")
G = "#f2f2f2"
nodos = [(.87, "Corporate / IT network\n(VLAN 10, attacker)" if EN else "Red corporativa / TI\n(VLAN 10, atacante)"),
         (.58, "Industrial DMZ\nSCADA/HMI (VLAN 20)" if EN else "DMZ industrial\nSCADA/HMI (VLAN 20)"),
         (.29, "PLC network (VLAN 30)\nOpenPLC, Modbus/TCP" if EN else "Red del PLC (VLAN 30)\nOpenPLC, Modbus/TCP"),
         (.00, "Simulated industrial\nprocess" if EN else "Proceso industrial\nsimulado")]
for y, t in nodos: box(ax, .04, y, .56, .13, t, fc=G, ec="#555", fs=7)
for (y1, _), (y2, _), lab in zip(nodos[:-1], nodos[1:], ("Firewall (nftables)" if EN else "Firewall (nftables)", "Inline IPS (Suricata, NFQUEUE)" if EN else "IPS en línea (Suricata, NFQUEUE)", "Modbus/TCP :502" if EN else "Modbus/TCP :502")):
    arrow(ax, (.32, y1), (.32, y2 + .13), c="#333", lw=.9); ax.text(.35, (y1 + y2 + .13) / 2, lab, fontsize=6.3, va="center", ha="left", color="#333")
ax.add_patch(Rectangle((.905, .03), .04, .94, fc="#dbe8f4", ec="#8fb0d1", lw=.6))
ax.text(.99, .50, "Virtual industrial switch (Open vSwitch, 802.1Q VLANs)" if EN else "Switch industrial virtual (Open vSwitch, VLAN 802.1Q)", rotation=90, fontsize=6.3, va="center", ha="center", color="#33597d")
E.guardar(fig, DEST, "a0_logical_topology")

# ---------- A1: banco de pruebas y puntos de medición ----------
fig, ax = lienzo(3.1)
bw, bh, xs, y0 = .18, .30, [.01, .275, .54, .805], .44
cajas = [("Attacker" if EN else "Atacante", "hping3,\nPython", "VLAN 10", "#fbe3d6"), ("Firewall", "nftables", "VLAN 10/20", "#ffffff"), ("IPS inline", "Suricata,\nNFQUEUE", "VLAN 20/30", "#fff2cc"), ("OpenPLC", "Modbus/TCP\n:502", "VLAN 30", "#dcefdc")]
for x, (n, sw, vl_, c) in zip(xs, cajas):
    ax.add_patch(FancyBboxPatch((x, y0), bw, bh, boxstyle="round,pad=0.005,rounding_size=0.012", fc=c, ec="#333", lw=.7))
    ax.text(x + bw / 2, y0 + bh - .06, n, ha="center", va="center", fontsize=6.8, fontweight="bold"); ax.text(x + bw / 2, y0 + bh / 2 - .005, sw, ha="center", va="center", fontsize=5.8, linespacing=1.2); ax.text(x + bw / 2, y0 + .045, vl_, ha="center", va="center", fontsize=5.8, color="#444")
for x in xs[:-1]: arrow(ax, (x + bw, y0 + bh / 2), (x + bw + .085, y0 + bh / 2))
box(ax, .28, .86, .26, .12, "SCADA (VLAN 20)\nPython client, %d Hz" % hz, fs=5.8)
arrow(ax, (.54, .90), (.62, y0 + bh), c="#555", lw=.8)
ax.add_patch(FancyBboxPatch((.01, .30), .98, .08, boxstyle="round,pad=0.003,rounding_size=0.01", fc="#dbe8f4", ec="#8fb0d1", lw=.6))
ax.text(.5, .34, "Open vSwitch ovs-ot: VLAN 10/20/30, no physical ports" if EN else "Open vSwitch ovs-ot: VLAN 10/20/30, sin puertos físicos", ha="center", va="center", fontsize=6)
for x in xs: arrow(ax, (x + bw / 2, y0), (x + bw / 2, .38), c="#8fb0d1", lw=.7, style="-")
box(ax, .01, .06, .30, .16, "mir20: mirror of\nVLAN 20\n(before the IPS)" if EN else "mir20: espejo de\nla VLAN 20\n(antes del IPS)", fc="#eeeeee", fs=5.8)
box(ax, .69, .06, .30, .16, "mir30: mirror of\nVLAN 30\n(after the IPS)" if EN else "mir30: espejo de\nla VLAN 30\n(después del IPS)", fc="#eeeeee", fs=5.8)
box(ax, .385, .06, .23, .16, "dumpcap +\ncounters" if EN else "dumpcap +\ncontadores", fc="#eeeeee", fs=5.8)
arrow(ax, (.16, .30), (.16, .22), c="#777", ls=":", lw=.8, style="-"); arrow(ax, (.84, .30), (.84, .22), c="#777", ls=":", lw=.8, style="-")
arrow(ax, (.31, .14), (.385, .14), c="#555", lw=.8); arrow(ax, (.69, .14), (.615, .14), c="#555", lw=.8)
ax.text(.5, .015, "Out-of-band measurement on the host: no packet passes through it" if EN else "Medición fuera de banda en el host: ningún paquete pasa por ella", ha="center", fontsize=5.8, color="#444")
E.guardar(fig, DEST, "a1_topology")

# ---------- A2: ruta de datos del IPS ----------
fig, ax = lienzo(2.7); ax.set_xlim(-.02, 1.02)
ax.add_patch(Rectangle((.125, .07), .755, .86, fc="#fffdf2", ec="#b8a64a", lw=.7, ls="--")); ax.text(.14, .895, "lab-ips (Debian 13)", fontsize=6.3, fontweight="bold", va="center")
yT, yB, h = .56, .14, .20; vw = .085; xN, wN, xQ, wQ, xS, wS = .165, .17, .385, .17, .605, .18; xo = .905
box(ax, .005, yT, vw, h, "v20", fc="#eaf1f8", fs=6); box(ax, xo, yT, vw, h, "v30", fc="#dcefdc", fs=6)
box(ax, xN, yT, wN, h, "nftables\nforward\nc_fwd_v20_v30\nqueue num %s" % q if EN else "nftables\nforward\nc_fwd_v20_v30\nqueue num %s" % q, fs=5.6)
box(ax, xQ, yT, wQ, h, "NFQUEUE\n%s\nqueue_dropped" % q, fc="#f3e5f5", fs=5.3)
box(ax, xS, yT, wS, h, "Suricata\nrules +\nverdict" if EN else "Suricata\nreglas +\nveredicto", fc="#fff2cc", fs=5.6)
cy = yT + h / 2
arrow(ax, (.005 + vw, cy), (xN, cy)); arrow(ax, (xN + wN, cy), (xQ, cy)); arrow(ax, (xQ + wQ, cy), (xS, cy)); arrow(ax, (xS + wS, cy), (xo, cy), c="#2e7d32")
ax.text((xS + wS + xo) / 2, cy + .045, "accept", fontsize=5.5, color="#2e7d32", ha="center")
arrow(ax, (xS + wS / 2, yT), (xS + wS / 2, .50), c="#c62828"); ax.text(xS + wS / 2, .445, "drop\n(ips.blocked)" if EN else "drop\n(ips.blocked)", fontsize=5.5, color="#c62828", ha="center", va="center")
box(ax, .005, yB, vw, h, "v30", fc="#dcefdc", fs=6); box(ax, xo, yB, vw, h, "v20", fc="#eaf1f8", fs=6)
box(ax, xN, yB, wN, h, "nftables\nforward\nc_fwd_v30_v20\nqueue num %s" % q, fs=5.6)
box(ax, xQ, yB, xS + wS - xQ, h, ("same NFQUEUE and Suricata\n(PLC replies)" if EN else "mismas NFQUEUE y Suricata\n(respuestas del PLC)"), fc="#f3e5f5", fs=5.6, ls="--")
cb = yB + h / 2
arrow(ax, (.005 + vw, cb), (xN, cb)); arrow(ax, (xN + wN, cb), (xQ, cb)); arrow(ax, (xS + wS, cb), (xo, cb))
ax.text(.5, .02, "E1: router mode, no queue · E2: action alert · E3: action drop" if EN else "E1: modo router, sin cola · E2: acción alert · E3: acción drop", ha="center", fontsize=5.8, color="#333")
E.guardar(fig, DEST, "a2_ips_datapath")

# ---------- A3: diseño experimental ----------
fig, (axT, axM) = plt.subplots(2, 1, figsize=(E.W, 3.1), gridspec_kw=dict(height_ratios=[.8, 1.35]), constrained_layout=True)
for a_ in (axT, axM): a_.axis("off")
tot = warm + att + cool; axT.set_xlim(0, tot); axT.set_ylim(0, 1)
for x0, w, c, t in ((0, warm, "#eaf1f8", "warm-up\n%d s" % warm if EN else "calentamiento\n%d s" % warm), (warm, att, "#f9d9cf", "attack\n%d s" % att if EN else "ataque\n%d s" % att), (warm + att, cool, "#dcefdc", "cool-down\n%d s" % cool if EN else "enfriamiento\n%d s" % cool)):
    axT.add_patch(Rectangle((x0, .30), w, .45, fc=c, ec="#555", lw=.6)); axT.text(x0 + w / 2, .525, t, ha="center", va="center", fontsize=6.5)
axT.annotate("", xy=(tot, .15), xytext=(0, .15), arrowprops=dict(arrowstyle="-|>", lw=.8, color="#222")); axT.text(tot / 2, .02, ("SCADA polls Modbus at %d Hz during the whole run; availability is measured in the attack window" if EN else "El SCADA consulta Modbus a %d Hz durante toda la corrida; la disponibilidad se mide en la ventana de ataque") % hz, ha="center", fontsize=6)
axT.text(0, .88, "t = 0" if EN else "t = 0", fontsize=6); axT.text(tot, .88, "%d s" % tot, fontsize=6, ha="right")
axM.set_xlim(0, 1); axM.set_ylim(0, 1)
cols = ["TCP SYN", "UDP", "ICMP", "Modbus/TCP"]; rows = [("E0", "No attack" if EN else "Sin ataque", None), ("E1", "Router only (no IPS)" if EN else "Solo router (sin IPS)", True), ("E2", "Suricata alert", True), ("E3", "Suricata drop", True)]
x0, cw, rh = .33, .165, .17
for j, c in enumerate(cols): axM.text(x0 + (j + .5) * cw, .94, c, ha="center", fontsize=6.5, fontweight="bold")
for i, (s, name, flag) in enumerate(rows):
    y = .72 - i * (rh + .035); axM.text(.0, y + rh / 2, f"{s}  {name}", va="center", fontsize=6.5)
    if s == "E0": axM.add_patch(Rectangle((x0, y), 4 * cw - .01, rh, fc="#eeeeee", ec="#555", lw=.6)); axM.text(x0 + 2 * cw, y + rh / 2, "10 runs, baseline" if EN else "10 corridas, línea base", ha="center", va="center", fontsize=6.5)
    else:
        for j in range(4): axM.add_patch(Rectangle((x0 + j * cw, y), cw - .01, rh, fc=E.COL[s], ec="#333", lw=.5, alpha=.35)); axM.text(x0 + (j + .5) * cw, y + rh / 2, "10 runs" if EN else "10 corridas", ha="center", va="center", fontsize=6.5)
E.guardar(fig, DEST, "a3_experiment_design")
print("diagramas en", DEST)
