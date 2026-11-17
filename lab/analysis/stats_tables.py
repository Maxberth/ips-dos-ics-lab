#!/usr/bin/env python3
"""Estadística por escenario y ataque (P20), a partir de data/processed/run_summary_<plataforma>_<perfil>.csv.

Por cada (escenario, ataque): n, media, DE e IC 95 % (t de Student, n-1 gl) de disponibilidad, RTT mediana,
RTT p95, pps del atacante, % de ataque eliminado y % de descarte por saturación. Solo corridas status=ok
y validate distinto de FAIL. Una plataforma por archivo: nunca se mezclan.
Salidas:
  data/processed/stats_<plataforma>_<perfil>.csv
  tables/stats_<plataforma>_<perfil>.tex       (tabla LaTeX lista para revisar; plataforma en el caption)
  figures/<plataforma>_<perfil>_availability.png y _rtt_p95.png
Uso: stats_tables.py --platform laptop-dev --profile reduced
"""
import argparse, csv, math, os, sys
from collections import defaultdict

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
METRICS = [("availability_pct", "Disponibilidad (%)"), ("rtt_median_ms", "RTT mediana (ms)"),
           ("rtt_p95_ms", "RTT p95 (ms)"), ("attacker_pps", "Ataque (pps)"),
           ("removed_pct", "Ataque eliminado (%)"), ("sat_pct", "Eliminado por saturación (%)")]

def tcrit(n):
    from scipy import stats
    return stats.t.ppf(0.975, n - 1) if n > 1 else float("nan")

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--platform", required=True); ap.add_argument("--profile", required=True)
    a = ap.parse_args()
    src = f"{REPO}/data/processed/run_summary_{a.platform}_{a.profile}.csv"
    runs = [r for r in csv.DictReader(open(src)) if r["status"] == "ok"]
    vr = {r["run_id"]: r["validate"] for r in csv.DictReader(open(f"{REPO}/data/raw/runs.csv"))}
    runs = [r for r in runs if not vr.get(r["run_id"], "").startswith("FAIL")]
    groups = defaultdict(list)
    for r in runs:
        A, B, D, C = (float(r[k]) if r.get(k) not in (None, "") else None for k in
                      ("cap_attack_vlan20", "cap_attack_vlan30", "nfq_queue_dropped", "suri_ips_blocked"))
        r["removed_pct"] = 100 * (A - B) / A if A else ""
        r["sat_pct"] = 100 * D / (D + C) if (D is not None and C is not None and (D + C) > 0) else ""
        groups[(r["scenario"], r["attack"])].append(r)
    rows = []
    for (s, at), rs in sorted(groups.items()):
        out = {"platform": a.platform, "profile": a.profile, "scenario": s, "attack": at, "n": len(rs)}
        for k, _ in METRICS:
            xs = [float(r[k]) for r in rs if r.get(k) not in (None, "")]
            n = len(xs)
            if not n: continue
            m = sum(xs) / n
            sd = math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1)) if n > 1 else float("nan")
            h = tcrit(n) * sd / math.sqrt(n) if n > 1 else float("nan")
            out.update({f"{k}_mean": round(m, 3), f"{k}_sd": round(sd, 3), f"{k}_ci95": round(h, 3), f"{k}_n": n})
        alive = [r["plc_alive_after"] for r in rs if r.get("plc_alive_after") in ("yes", "no")]
        out["plc_down_after"] = f"{alive.count('no')}/{len(alive)}" if alive else ""
        rows.append(out)
    os.makedirs(f"{REPO}/data/processed", exist_ok=True)
    p = f"{REPO}/data/processed/stats_{a.platform}_{a.profile}.csv"
    cols = []
    for r in rows:
        for k in r:
            if k not in cols: cols.append(k)
    with open(p, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n"); w.writeheader(); w.writerows(rows)
    # Tabla LaTeX
    os.makedirs(f"{REPO}/tables", exist_ok=True)
    fmt = lambda r, k: (f"{r[k + '_mean']:.1f} $\\pm$ {r[k + '_ci95']:.1f}" if (k + "_mean") in r and not math.isnan(r[k + "_ci95"])
                        else (f"{r[k + '_mean']:.1f}" if (k + "_mean") in r else "--"))
    L = ["% Generado por lab/analysis/stats_tables.py. NO EDITAR A MANO.",
         f"% Plataforma: {a.platform}. Perfil: {a.profile}. Media $\\pm$ semiamplitud IC 95 \\% (t de Student).",
         "\\begin{table}[htbp]", "\\centering",
         f"\\caption{{Resultados por escenario y ataque ({a.platform}, perfil {a.profile}). Media $\\pm$ IC 95\\,\\%.}}",
         f"\\label{{tab:stats-{a.platform}-{a.profile}}}", "\\scriptsize",
         "\\begin{tabular}{l l r r r r r r}", "\\toprule",
         "Esc. & Ataque & $n$ & Disp. (\\%) & RTT p95 (ms) & Elim. (\\%) & Saturación (\\%) & PLC caído \\\\", "\\midrule"]
    for r in rows:
        L.append(f"{r['scenario']} & {r['attack']} & {r['n']} & {fmt(r, 'availability_pct')} & {fmt(r, 'rtt_p95_ms')} & "
                 f"{fmt(r, 'removed_pct')} & {fmt(r, 'sat_pct')} & {r.get('plc_down_after') or '--'} \\\\")
    L += ["\\bottomrule", "\\end{tabular}", "\\end{table}"]
    open(f"{REPO}/tables/stats_{a.platform}_{a.profile}.tex", "w").write("\n".join(L) + "\n")
    # Figuras
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    os.makedirs(f"{REPO}/figures", exist_ok=True)
    for k, lab in (("availability_pct", "Disponibilidad del SCADA (%)"), ("rtt_p95_ms", "RTT p95 (ms)")):
        rr = [r for r in rows if k + "_mean" in r]
        names = [f"{r['scenario']}\n{r['attack']}" for r in rr]
        ys = [r[k + "_mean"] for r in rr]
        es = [0 if math.isnan(r[k + "_ci95"]) else r[k + "_ci95"] for r in rr]
        fig, ax = plt.subplots(figsize=(max(4, 0.7 * len(rr) + 1), 3.2))
        ax.bar(range(len(rr)), ys, yerr=es, capsize=3, color="#4C78A8")
        ax.set_xticks(range(len(rr))); ax.set_xticklabels(names, fontsize=7)
        ax.set_ylabel(lab); ax.set_title(f"{a.platform}, perfil {a.profile} (media ± IC 95 %)", fontsize=8)
        ax.grid(axis="y", alpha=.3); fig.tight_layout()
        fig.savefig(f"{REPO}/figures/{a.platform}_{a.profile}_{k}.png", dpi=200); plt.close(fig)
    print(p)
    return 0

if __name__ == "__main__":
    sys.exit(main())
