#!/usr/bin/env python3
"""Verifica la conservación de paquetes en las colas NFQUEUE por corrida (A21), solo con datos crudos.

Todo paquete que entra a la cola (ambos sentidos: v20->v30 y v30->v20 pasan por `queue num 0-1`) termina en una de tres
partes. Identidad que se comprueba:
    c_fwd_v20_v30 + c_fwd_v30_v20  (contadores nftables, delta de la corrida)
  = nfq_queue_dropped              (nfq_{pre,post}.txt, suma de colas)
  + ips.blocked + ips.accepted     (suricata_stats.jsonl, delta de la corrida; valor acumulado de la última línea menos
                                    el de la primera, porque eve.json se vacía al iniciar cada corrida)
Salida: data/processed/conservacion_nfq_<plataforma>_<perfil>.csv y un resumen por celda (mín–máx del cociente).
Uso: python3 -I lab/analysis/verificar_conservacion_nfq.py --platform laptop-dev --profile final
"""
import argparse, csv, json, os, collections
ap = argparse.ArgumentParser(); ap.add_argument("--platform", required=True); ap.add_argument("--profile", default="final"); a = ap.parse_args()
R = "data/raw/runs/"
def ctr(d, w, n):
    for x in json.load(open(f"{R}{d}/ips_counters_{w}.json"))["nftables"]:
        c = x.get("counter")
        if c and c["name"] == n: return c["packets"]
def nfq(p):
    return sum(int(l.split()[5]) for l in open(p) if l.split())
def suri(d):
    L = [json.loads(l)["ips"] for l in open(f"{R}{d}/suricata_stats.jsonl") if l.strip()]
    return L[-1]["blocked"] - L[0]["blocked"], L[-1]["accepted"] - L[0]["accepted"]
runs = [r for r in csv.DictReader(open("data/raw/runs.csv")) if r["platform"] == a.platform and r["run_profile"] == a.profile and r["status"] == "ok" and r["scenario"] in ("E2", "E3")]
out = f"data/processed/conservacion_nfq_{a.platform}_{a.profile}.csv"; cel = collections.defaultdict(list)
with open(out, "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["run_id", "scenario", "attack", "nft_fwd_v20_v30", "nft_fwd_v30_v20", "entran_cola", "nfq_queue_dropped", "suri_blocked", "suri_accepted", "salen_cola", "cociente_salen_entran"])
    for r in runs:
        d = r["run_id"]
        try:
            f1 = ctr(d, "post", "c_fwd_v20_v30") - ctr(d, "pre", "c_fwd_v20_v30"); f2 = ctr(d, "post", "c_fwd_v30_v20") - ctr(d, "pre", "c_fwd_v30_v20")
            dr = nfq(f"{R}{d}/nfq_post.txt") - nfq(f"{R}{d}/nfq_pre.txt"); b, ac = suri(d)
        except Exception as e:
            print("sin datos:", d, e); continue
        q = (f1 + f2) or 1; ratio = (dr + b + ac) / q
        w.writerow([d, r["scenario"], r["attack"], f1, f2, f1 + f2, dr, b, ac, dr + b + ac, round(ratio, 4)]); cel[(r["scenario"], r["attack"])].append(ratio)
for k, v in sorted(cel.items()): print(k, f"n={len(v)} cociente {min(v):.4f}–{max(v):.4f}")
print("->", out)
