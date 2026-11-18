#!/usr/bin/env python3
"""Tablas LaTeX del paper y pruebas estadísticas, generadas SOLO desde los datos del repositorio.

Fuentes: data/raw/runs.csv, data/processed/run_summary_<plat>_<perfil>.csv, lab/config/*.
Salidas (en tables/paper/): t_results.tex, t_tests.tex, t_config.tex, rules_drop.txt, y data/processed/pruebas_<plat>_<perfil>.csv
Pruebas: Mann-Whitney U bilateral (sin supuesto de normalidad; n=10 por grupo) sobre respuestas válidas/solicitudes programadas
y RTT p95, con corrección de Holm sobre todas las comparaciones de la métrica; tamaño del efecto: delta de Cliff.
PLC caído: prueba exacta de Fisher. Los IC al 95 % son t de Student (n-1 gl).
Uso: python3 -I lab/analysis/tablas_paper.py --platform laptop-dev --profile final
"""
import argparse, csv, itertools, math, os, re, statistics as st
from collections import defaultdict
from scipy import stats

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ap = argparse.ArgumentParser(); ap.add_argument("--platform", required=True); ap.add_argument("--profile", default="final"); A = ap.parse_args()
P = f"{A.platform}_{A.profile}"; OUT = f"{REPO}/tables/paper"; os.makedirs(OUT, exist_ok=True)
runs = {r["run_id"]: r for r in csv.DictReader(open(f"{REPO}/data/raw/runs.csv"))}
S = [r for r in csv.DictReader(open(f"{REPO}/data/processed/run_summary_{P}.csv")) if r["status"] == "ok"]
exp = open(f"{REPO}/lab/config/experiment.env").read(); HZ = float(re.search(r"SCADA_HZ=(\d+)", exp).group(1))
f = lambda r, k: float(r[k]) if r.get(k, "") not in ("", "NA", None) else None
for r in S: r["resp_sch"] = 100 * float(r["polls_ok"]) / (HZ * float(runs[r["run_id"]]["attack_s"]))
by = defaultdict(list)
for r in S: by[(r["scenario"], r["attack"])].append(r)
V = lambda s, a, k: [x for x in (f(r, k) for r in by.get((s, a), [])) if x is not None]
def mci(v):
    if not v: return None
    m = st.mean(v); c = stats.t.ppf(.975, len(v) - 1) * st.stdev(v) / math.sqrt(len(v)) if len(v) > 1 else 0
    return m, c
def fmt(v, d=1):
    x = mci(v)
    if x is None: return "--"
    if abs(x[0]) < 10 ** -d / 2: x = (0.0, x[1])
    return f"{x[0]:.{d}f} $\\pm$ {x[1]:.{d}f}" if x[1] >= 10 ** -d / 2 else f"{x[0]:.{d}f}"
AT = [("syn", "TCP SYN"), ("udp", "UDP"), ("icmp", "ICMP"), ("modbus", "Modbus")]; SC = [("E1", "E1"), ("E2", "E2"), ("E3", "E3")]
# ---- t_results ----
L = ["\\begin{tabular}{llrrrrr}", "\\toprule", "Attack & Scen. & Replies/ & Replies/ & RTT p95 & Removed & PLC\\\\", " & & issued (\\%) & sched. (\\%) & (ms) & (\\%) & down\\\\", "\\midrule"]
v0 = V("E0", "none", "availability_pct"); L.append(f"None & E0 & {fmt(v0)} & {fmt(V('E0','none','resp_sch'))} & {fmt(V('E0','none','rtt_p95_ms'),2)} & -- & {sum(r['plc_alive_after']!='yes' for r in by[('E0','none')])}/10\\\\")
for a, an in AT:
    L.append("\\midrule")
    for s, sn in SC:
        down = sum(r["plc_alive_after"] != "yes" for r in by[(s, a)])
        rem = fmt(V(s, a, "cap_removed_pct")) if s != "E1" else fmt(V(s, a, "cap_removed_pct"))
        L.append(f"{an if s == 'E1' else ''} & {sn} & {fmt(V(s,a,'availability_pct'))} & {fmt(V(s,a,'resp_sch'))} & {fmt(V(s,a,'rtt_p95_ms'),0 if mci(V(s,a,'rtt_p95_ms'))[0] > 50 else 1)} & {rem} & {down}/10\\\\")
L += ["\\bottomrule", "\\end{tabular}"]; open(f"{OUT}/t_results.tex", "w").write("\n".join(L) + "\n")
# ---- pruebas ----
def cliff(x, y):
    g = sum(1 for a in x for b in y if a > b); l = sum(1 for a in x for b in y if a < b); return (g - l) / (len(x) * len(y))
pairs = [("E1", "E2"), ("E1", "E3"), ("E2", "E3")]; rows = []
for met, nm in (("resp_sch", "replies_per_scheduled"), ("rtt_p95_ms", "rtt_p95_ms")):
    tests = []
    for a, _ in AT:
        for s1, s2 in pairs:
            x, y = V(s1, a, met), V(s2, a, met)
            if len(x) < 2 or len(y) < 2: continue
            p = stats.mannwhitneyu(x, y, alternative="two-sided").pvalue; tests.append([nm, a, s1, s2, len(x), len(y), st.median(x), st.median(y), cliff(x, y), p])
    order = sorted(range(len(tests)), key=lambda i: tests[i][-1]); m = len(tests); run = 0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (m - rank) * tests[i][-1])); tests[i].append(run)
    rows += tests
with open(f"{REPO}/data/processed/pruebas_{P}.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["metric", "attack", "scenario_a", "scenario_b", "n_a", "n_b", "median_a", "median_b", "cliffs_delta_a_vs_b", "p_mannwhitney", "p_holm"]); [w.writerow(r[:8] + [round(r[8], 3), f"{r[9]:.3g}", f"{r[10]:.3g}"]) for r in rows]
def star(p): return "***" if p < .001 else "**" if p < .01 else "*" if p < .05 else "ns"
T = ["\\begin{tabular}{lccc}", "\\toprule", "Attack & E1 vs E2 & E1 vs E3 & E2 vs E3\\\\", "\\midrule"]
for a, an in AT:
    cells = []
    for s1, s2 in pairs:
        r = next(x for x in rows if x[0] == "replies_per_scheduled" and x[1] == a and x[2] == s1 and x[3] == s2)
        cells.append(f"{r[8]:+.2f} ({star(r[10])})")
    T.append(f"{an} & " + " & ".join(cells) + "\\\\")
fa = {}
for s1, s2 in pairs:
    x = [r["plc_alive_after"] != "yes" for r in by[(s1, "modbus")]]; y = [r["plc_alive_after"] != "yes" for r in by[(s2, "modbus")]]
    tab = [[sum(x), len(x) - sum(x)], [sum(y), len(y) - sum(y)]]; fa[(s1, s2)] = stats.fisher_exact(tab)[1]
T += ["\\midrule", "PLC down (Modbus), $p$ & " + " & ".join(f"{fa[p]:.3f}" for p in pairs) + "\\\\", "\\bottomrule", "\\end{tabular}"]
open(f"{OUT}/t_tests.tex", "w").write("\n".join(T) + "\n")
# ---- configuración ----
prof = open(f"{REPO}/lab/config/profile_{A.platform}.env").read()
def vm(n): return int(re.search(rf"VM_{n}_VCPUS=(\d+)", prof).group(1)), int(re.search(rf"VM_{n}_MEM=(\d+)", prof).group(1))
C = ["\\begin{tabular}{lllrr}", "\\toprule", "VM & Role / software & VLAN & vCPU & RAM (GiB)\\\\", "\\midrule"]
for n, role, vl in (("ATTACKER", "Attacker: hping3, Python flood script", "10"), ("FW", "Firewall/router: nftables", "10/20"), ("SCADA", "SCADA client (Python, 10 Hz)", "20"), ("IPS", "Inline IPS: Suricata 7.0.10, NFQUEUE", "20/30"), ("PLC", "PLC: OpenPLC runtime (Modbus/TCP)", "30")):
    c, m = vm(n); C.append(f"{n.lower()} & {role} & {vl} & {c} & {m / 1024:g}\\\\")
C += ["\\bottomrule", "\\end{tabular}"]; open(f"{OUT}/t_config.tex", "w").write("\n".join(C) + "\n")
# ---- reglas reales (modo drop) ----
rules = [l.replace("ACTION ", "drop ") for l in open(f"{REPO}/lab/config/ips/rules/lab.rules.in") if l.startswith("ACTION ")]
open(f"{OUT}/rules_drop.txt", "w").write("".join(rules))
print("tablas en", OUT, sorted(os.listdir(OUT)))
for r in rows:
    if r[0] == "replies_per_scheduled": print(r[1], r[2], r[3], f"delta={r[8]:+.2f} p_holm={r[10]:.3g}")
print({k: round(v, 4) for k, v in fa.items()})
