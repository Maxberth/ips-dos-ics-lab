#!/usr/bin/env python3
"""Muestras REALES del guardián alrededor de las corridas con campos térmicos vacíos en runs.csv (A20).

No estima ni rellena nada: no escribe en runs.csv ni inventa tctl_start_c/tctl_end_c. Para cada corrida a la que le
falta algún campo (tctl_start_c, tctl_end_c, guard_states) copia, tal como está en el CSV del guardián
(data/raw/guard/guard_<plataforma>_*.csv), la muestra medida en instantes definidos por t0 y fin de enfriamiento,
con su marca de tiempo, y los estados vistos en la ventana. Son mediciones distintas de los campos ausentes (el
arnés los tomó en otro instante), por eso llevan otro nombre y no sustituyen a los campos de runs.csv.
Salida: data/processed/runs_guard_muestras_<plataforma>_<perfil>.csv
Uso: python3 -I lab/analysis/muestras_guard_por_corrida.py --platform laptop-dev --profile final
"""
import argparse, csv, glob, bisect
from datetime import datetime, timezone
ap = argparse.ArgumentParser(); ap.add_argument('--platform', required=True); ap.add_argument('--profile', default='final'); a = ap.parse_args()
iso = lambda t: datetime.fromtimestamp(t, timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
ts = lambda s: datetime.strptime(s, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc).timestamp()
G = []
for f in sorted(glob.glob(f'data/raw/guard/guard_{a.platform}_*.csv')):
    for r in csv.reader(open(f)):
        if r and r[0] != 'ts_utc':
            try: G.append((ts(r[0]), float(r[6]), r[9]))
            except ValueError: pass
G.sort(); T = [g[0] for g in G]
at = lambda t: G[max(bisect.bisect_right(T, t) - 1, 0)]
rows = [r for r in csv.DictReader(open('data/raw/runs.csv')) if r['platform'] == a.platform and r['run_profile'] == a.profile and r['status'] == 'ok']
falta = lambda r: not r['tctl_start_c'] or not r['tctl_end_c'] or r['guard_states'] in ('', 'NA')
out = f'data/processed/runs_guard_muestras_{a.platform}_{a.profile}.csv'; n = 0
with open(out, 'w', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(['run_id', 'campos_vacios_en_runs_csv', 'guard_tctl_en_t0_c', 'guard_t_en_t0_utc', 'guard_tctl_fin_enfriamiento_c', 'guard_t_fin_enfriamiento_utc', 'guard_estados_ventana', 'guard_tctl_max_ventana_c', 'fuente'])
    for r in rows:
        if not falta(r): continue
        t0 = int(r['t0_unix_ns']) / 1e9; t1 = int(r['t_attack_end_ns']) / 1e9 + float(r['cool_s'])
        g0, g1 = at(t0), at(t1); win = [g for g in G if t0 <= g[0] <= t1]
        vac = '|'.join(k for k, v in (('tctl_start_c', r['tctl_start_c']), ('tctl_end_c', r['tctl_end_c']), ('guard_states', r['guard_states'] if r['guard_states'] != 'NA' else '')) if not v)
        w.writerow([r['run_id'], vac, g0[1], iso(g0[0]), g1[1], iso(g1[0]), '|'.join(sorted({g[2] for g in win})) or 'NA', max(g[1] for g in win), 'data/raw/guard/guard_%s_*.csv (medido)' % a.platform]); n += 1
print(f'{n} corridas con muestras reales del guardián -> {out}')
