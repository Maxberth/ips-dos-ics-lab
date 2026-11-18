#!/usr/bin/env python3
"""Diagramas de arquitectura y diseño experimental del paper (matplotlib, vectorial), al ancho de LNCS (4,8 in).

Los datos que aparecen (VLAN, subredes, hosts, reglas de nftables, repeticiones, duración de las fases) se leen de
lab/config (profile_<plataforma>.env, experiment.env, nftables-nfq.conf) para que no se desincronicen del laboratorio.
Salida: figures/paper/a1_topology, a2_ips_datapath, a3_experiment_design (.png 300 dpi y .pdf).
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

# ---------- A1: topología ----------
fig, ax = lienzo(3.0)
ax.add_patch(Rectangle((.005, .30), .99, .69, fc="#f7f7f7", ec="#777", lw=.7, ls="--"))
ax.text(.015, .96, "Host: KVM/libvirt + Open vSwitch (ovs-ot, " + ("no physical ports)" if EN else "sin puertos físicos)"), fontsize=6.3, va="center", fontweight="bold")
bands = [(.015, .22, "VLAN 10 · IT", "192.168.10.0/24"), (.365, .255, "VLAN 20 · DMZ/SCADA", "192.168.20.0/24"), (.75, .235, "VLAN 30 · " + ("Plant" if EN else "Planta"), "192.168.30.0/24")]
for x, w, t, n in bands:
    ax.add_patch(Rectangle((x, .33), w, .58, fc="#eaf1f8", ec="#9db7d1", lw=.6)); ax.text(x + w / 2, .875, t, ha="center", fontsize=6, fontweight="bold"); ax.text(x + w / 2, .83, n, ha="center", fontsize=5.8, color="#444")
box(ax, .03, .46, .19, .27, ("Attacker\nhping3, Scapy\n" if EN else "Atacante\nhping3, Scapy\n") + vm("ATTACKER").replace("\n", ", "), fc="#fbe3d6", fs=5.8)
box(ax, .25, .46, .10, .27, "Firewall\nnftables\n" + vm("FW"), fs=5.8)
box(ax, .627, .46, .115, .27, "IPS\nSuricata\nNFQUEUE\n" + vm("IPS"), fc="#fff2cc", fs=5.3)
box(ax, .385, .36, .215, .17, "SCADA\npymodbus %d Hz\n" % hz + vm("SCADA").replace("\n", ", "), fs=5.8)
box(ax, .765, .46, .205, .27, "OpenPLC\nModbus/TCP\n" + vm("PLC").replace("\n", ", "), fc="#dcefdc", fs=5.8)
arrow(ax, (.22, .595), (.25, .595)); arrow(ax, (.35, .66), (.627, .66)); arrow(ax, (.742, .595), (.765, .595))
arrow(ax, (.60, .445), (.627, .50), c="#555", lw=.7)
box(ax, .015, .075, .30, .15, "dumpcap +\ncounters of nftables,\nNFQUEUE and Suricata" if EN else "dumpcap +\ncontadores de nftables,\nNFQUEUE y Suricata", fc="#eeeeee", fs=5.8)
box(ax, .345, .075, .30, .15, "mir20: mirror of VLAN 20\n(before the IPS)" if EN else "mir20: espejo de\nla VLAN 20\n(antes del IPS)", fc="#eeeeee", fs=5.8)
box(ax, .675, .075, .31, .15, "mir30: mirror of VLAN 30\n(after the IPS)" if EN else "mir30: espejo de\nla VLAN 30\n(después del IPS)", fc="#eeeeee", fs=5.8)
arrow(ax, (.49, .33), (.49, .225), c="#777", ls=":", lw=.7, style="-"); arrow(ax, (.83, .33), (.83, .225), c="#777", ls=":", lw=.7, style="-")
ax.text(.5, .03, "Out-of-band measurement on the host: no packet passes through it" if EN else "Medición fuera de banda en el host: ningún paquete pasa por ella", ha="center", fontsize=5.8, color="#444")
E.guardar(fig, DEST, "a1_topology")

# ---------- A2: ruta de datos del IPS ----------
fig, ax = lienzo(3.0); ax.set_xlim(-.02, 1.02)
ax.add_patch(Rectangle((.135, .07), .74, .86, fc="#fffdf2", ec="#b8a64a", lw=.7, ls="--")); ax.text(.145, .90, "lab-ips (Debian 13)", fontsize=6, fontweight="bold", va="center")
yT, yB, h = .60, .16, .20
box(ax, .005, yT, .10, h, "v20\nVLAN 20", fc="#eaf1f8", fs=5.3); box(ax, .895, yT, .10, h, "v30\nVLAN 30", fc="#dcefdc", fs=5.3)
box(ax, .15, yT, .21, h, ("nftables forward\ncounter\nc_fwd_v20_v30\nqueue num %s" if EN else "nftables forward\ncontador\nc_fwd_v20_v30\nqueue num %s") % q, fs=5.5)
box(ax, .41, yT, .19, h, "NFQUEUE %s\nqueue_dropped\n(queue full)" % q if EN else "NFQUEUE %s\nqueue_dropped\n(cola llena)" % q, fc="#f3e5f5", fs=5.5)
box(ax, .65, yT, .21, h, "Suricata\nrules + verdict\naccept / drop" if EN else "Suricata\nreglas + veredicto\naccept / drop", fc="#fff2cc", fs=5.5)
arrow(ax, (.105, yT + h / 2), (.15, yT + h / 2)); arrow(ax, (.36, yT + h / 2), (.41, yT + h / 2)); arrow(ax, (.60, yT + h / 2), (.65, yT + h / 2)); arrow(ax, (.86, yT + h / 2), (.895, yT + h / 2), c="#2e7d32")
ax.text(.945, yT - .045, "accept", fontsize=5.5, color="#2e7d32", ha="center")
arrow(ax, (.755, yT), (.755, .50), c="#c62828"); ax.text(.755, .44, ("drop: ips.blocked\n(rule match)" if EN else "drop: ips.blocked\n(coincide regla)"), fontsize=5.5, color="#c62828", ha="center", va="center")
box(ax, .005, yB, .10, h, "v30\nVLAN 30", fc="#dcefdc", fs=5.3); box(ax, .895, yB, .10, h, "v20\nVLAN 20", fc="#eaf1f8", fs=5.3)
box(ax, .15, yB, .21, h, ("nftables forward\ncounter\nc_fwd_v30_v20\nqueue num %s" if EN else "nftables forward\ncontador\nc_fwd_v30_v20\nqueue num %s") % q, fs=5.5)
box(ax, .41, yB, .45, h, ("same NFQUEUE %s and Suricata\n(replies of the PLC, A21)" if EN else "mismas NFQUEUE %s y Suricata\n(respuestas del PLC, A21)") % q, fc="#f3e5f5", fs=5.5, ls="--")
arrow(ax, (.105, yB + h / 2), (.15, yB + h / 2)); arrow(ax, (.36, yB + h / 2), (.41, yB + h / 2)); arrow(ax, (.86, yB + h / 2), (.895, yB + h / 2))
ax.text(.5, .025, "E1: router mode, no queue · E2: action alert (rules only log) · E3: action drop" if EN else "E1: modo router, sin cola · E2: acción alert (las reglas solo registran) · E3: acción drop", ha="center", fontsize=5.8, color="#333")
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
