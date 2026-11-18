#!/usr/bin/env python3
"""Reconstruye tctl_start_c, tctl_end_c y guard_states de las corridas cuyos campos quedaron vacíos (A20).

NO modifica data/raw/runs.csv. Escribe data/processed/runs_guard_reconstruido_<plataforma>_<perfil>.csv,
marcado como reconstruido, con la fuente (CSV del guardián, 1 muestra cada ~2 s).

Método: run_once.sh toma tctl_start_c del guardián justo antes de preparar la corrida y tctl_end_c al final
(después del enfriamiento). Esos instantes no se guardaron, así que se calibran con las corridas del mismo
perfil que sí tienen el valor: se busca el desfase (en segundos) respecto a t0 / fin del ataque que minimiza
el error absoluto medio, y se aplica a las corridas vacías. Se informa el error de la calibración.
Uso: python3 -I lab/analysis/reconstruir_campos_guard.py --platform laptop-dev --profile final
"""
import argparse, csv, glob, bisect, statistics as st
from datetime import datetime, timezone

ap = argparse.ArgumentParser(); ap.add_argument('--platform', required=True); ap.add_argument('--profile', default='final')
a = ap.parse_args()

def ts(s):  # '2026-11-18T02:28:29.194Z' -> segundos unix
    return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc).timestamp()

G = []  # (t, tctl, estado)
for f in sorted(glob.glob(f'data/raw/guard/guard_{a.platform}_*.csv')):
    for r in csv.reader(open(f)):
        if r and r[0] != 'ts_utc':
            try: G.append((ts(r[0]), float(r[6]), r[9]))
            except ValueError: pass
G.sort(); T = [g[0] for g in G]

def at(t):  # última muestra con instante <= t
    i = bisect.bisect_right(T, t) - 1
    return G[i] if i >= 0 else None

rows = [r for r in csv.DictReader(open('data/raw/runs.csv')) if r['platform'] == a.platform and r['run_profile'] == a.profile and r['status'] == 'ok']
ok = [r for r in rows if r['tctl_start_c'] and r['tctl_end_c']]
faltan = lambda r: not r['tctl_start_c'] or not r['tctl_end_c'] or r['guard_states'] in ('', 'NA')
bad = [r for r in rows if faltan(r)]

def calib(get_ref, field, rng):
    best = None
    for off in rng:
        e = []
        for r in ok:
            g = at(get_ref(r) + off)
            if g: e.append(abs(g[1] - float(r[field])))
        m = st.mean(e)
        if best is None or m < best[1]: best = (off, m, st.median(e), max(e), len(e))
    return best

t0 = lambda r: int(r['t0_unix_ns']) / 1e9
tend = lambda r: int(r['t_attack_end_ns']) / 1e9 + float(r['cool_s'])
c_s = calib(t0, 'tctl_start_c', range(-150, 1))
c_e = calib(tend, 'tctl_end_c', range(0, 91))
print(f'calibración con {len(ok)} corridas: inicio desfase {c_s[0]} s (MAE {c_s[1]:.2f} °C, mediana {c_s[2]:.2f}, máx {c_s[3]:.1f}); '
      f'fin desfase {c_e[0]} s (MAE {c_e[1]:.2f} °C, mediana {c_e[2]:.2f}, máx {c_e[3]:.1f})')

out = f'data/processed/runs_guard_reconstruido_{a.platform}_{a.profile}.csv'
with open(out, 'w', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(['run_id', 'tctl_start_c_rec', 'tctl_end_c_rec', 'guard_states_rec', 'tctl_max_guard_c', 'origen', 'desfase_inicio_s', 'desfase_fin_s', 'mae_calib_inicio_c', 'mae_calib_fin_c', 'nota'])
    for r in bad:
        gs, ge = at(t0(r) + c_s[0]), at(tend(r) + c_e[0])
        ini, fin = t0(r), tend(r) + c_e[0]
        win = [g for g in G if ini <= g[0] <= fin]
        states = '|'.join(sorted({g[2] for g in win})) or 'NA'
        # Solo se rellena lo que falta; lo medido por el arnés no se repite aquí.
        w.writerow([r['run_id'], '' if r['tctl_start_c'] else gs[1], '' if r['tctl_end_c'] else ge[1],
                    '' if r['guard_states'] not in ('', 'NA') else states, max(g[1] for g in win), 'reconstruido', c_s[0], c_e[0], f'{c_s[1]:.2f}', f'{c_e[1]:.2f}', 'A20: campos vacíos en runs.csv; reconstruido del CSV del guardián'])
print(f'{len(bad)} corridas reconstruidas -> {out}')
