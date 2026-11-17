#!/usr/bin/env python3
"""Auditoría cruzada del piloto (P12) a partir de data/processed/run_summary_<plataforma>[_perfil].csv.
Escribe docs/lab/auditoria_piloto_<plataforma>.md con una tabla control | resultado | veredicto | evidencia.
No inventa valores: si falta un dato, el veredicto es INCIERTO.
Uso: audit_pilot.py --platform laptop-dev --profile piloto
"""
import argparse, csv, os, sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def f(x):
    try: return float(x)
    except (TypeError, ValueError): return None

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--platform", required=True); ap.add_argument("--profile", default="piloto")
    ap.add_argument("--tol", type=float, default=5.0)
    a = ap.parse_args()
    src = f"{REPO}/data/processed/run_summary_{a.platform}_{a.profile}.csv"
    runs = list(csv.DictReader(open(src)))
    L = [f"# Auditoría del piloto ({a.platform}, perfil {a.profile})", "",
         f"Generado por `lab/analysis/audit_pilot.py` a partir de `{os.path.relpath(src, REPO)}`. "
         "Datos de calibración: no se usan en el paper.", "",
         "Leyenda: (a) ataque capturado en la VLAN 20 (antes del IPS), (b) en la VLAN 30 (después), "
         "(c) `ips.blocked` de Suricata, (d) `queue_dropped` de NFQUEUE.", "",
         "| Corrida | Control | Resultado | Veredicto |", "|---|---|---|---|"]
    def row(r, c, res, v): L.append(f"| `{r['run_id'][:16]}` {r['scenario']} {r['attack']} | {c} | {res} | {v} |")
    for r in runs:
        A, B, C, D = (f(r.get(k)) for k in ("cap_attack_vlan20", "cap_attack_vlan30", "suri_ips_blocked", "nfq_queue_dropped"))
        av, pps, cdrop = f(r.get("availability_pct")), f(r.get("attacker_pps")), f(r.get("cap_drop_pct"))
        # 5. El ataque ocurrió
        if r["attack"] != "none":
            row(r, "el ataque ocurrió (pps del kernel del atacante)", f"{pps:.0f} pps" if pps is not None else "sin dato",
                "OK" if pps and pps > 1000 else ("ANOMALÍA" if pps is not None else "INCIERTO"))
        # 1-3. Segunda fuente
        if r["attack"] != "none" and A:
            removed = A - (B or 0)
            if r["ips_mode"] == "drop":
                if C is not None and D is not None:
                    diff = 100 * abs(removed - (C + D)) / A
                    row(r, "(a)−(b) ≈ (c)+(d)", f"(a)−(b)={removed:.0f}; (c)+(d)={C + D:.0f} (regla {C:.0f}, cola {D:.0f}); dif {diff:.2f} % de (a)",
                        "OK" if diff <= a.tol else "ANOMALÍA")
                    row(r, "parte eliminada por regla frente a saturación", f"regla {100 * C / max(1, C + D):.1f} %, cola llena {100 * D / max(1, C + D):.1f} %",
                        "OK" if D == 0 else "ANOMALÍA (saturación del IPS)")
                else:
                    row(r, "(a)−(b) ≈ (c)+(d)", "faltan contadores de Suricata o de NFQUEUE", "INCIERTO")
            else:
                pct = 100 * removed / A
                extra = f"; cola llena {D:.0f}" if D else ""
                row(r, f"{r['scenario']} ({r['ips_mode']}): (a) ≈ (b)", f"(a)={A:.0f} (b)={B:.0f} eliminado {pct:.2f} %{extra}",
                    "OK" if abs(pct) <= a.tol else ("ANOMALÍA (saturación del IPS)" if D else "ANOMALÍA"))
        # captura fiable
        if cdrop is not None:
            row(r, "captura sin pérdidas relevantes (dumpcap)", f"{cdrop:.2f} % descartado", "OK" if cdrop <= 1 else ("ADVERTENCIA" if cdrop <= 5 else "ANOMALÍA"))
        # 4. tráfico legítimo
        if av is not None:
            res = f"disponibilidad {av:.2f} %, timeouts {r.get('timeouts')}, RTT mediana {r.get('rtt_median_ms')} ms, p95 {r.get('rtt_p95_ms')} ms"
            v = "OK" if r["attack"] != "none" or av == 100 else "ANOMALÍA (pérdidas sin ataque)"
            row(r, "tráfico legítimo (SCADA)", res, v)
        # 8. valores imposibles
        bad = [k for k in ("availability_pct",) if f(r.get(k)) is not None and not 0 <= f(r.get(k)) <= 100]
        if f(r.get("rtt_median_ms")) is not None and f(r.get("rtt_median_ms")) < 0: bad.append("rtt<0")
        row(r, "valores imposibles", ", ".join(bad) or "ninguno", "ANOMALÍA" if bad else "OK")
        # 6. temperatura
        t = f(r.get("tctl_max_c"))
        row(r, "temperatura máxima del host", f"{t:.1f} °C" if t is not None else "sin dato", "OK" if t is not None and t < 88 else "INCIERTO")
    out = f"{REPO}/docs/lab/auditoria_piloto_{a.platform}.md"
    open(out, "w").write("\n".join(L) + "\n")
    print(out)
    return 0

if __name__ == "__main__":
    sys.exit(main())
