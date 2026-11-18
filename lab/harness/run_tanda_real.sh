#!/usr/bin/env bash
# Tanda real (perfil final, 10 repeticiones) por bloques en orden de prioridad, con commit y push de
# data/raw tras cada bloque (sin capturas). Si se corta, se relanza igual: --resume salta lo ya hecho.
# Uso: PROFILE=lab/config/profile_<plataforma>.env lab/harness/run_tanda_real.sh
set -uo pipefail
source "$(dirname "$0")/../setup/lib.sh"
cd "$REPO"
export MATRIX_NOTE="tanda=real"
block(){ # nombre escenarios ataques
  echo "##### bloque $1  $(date -u +%T)"
  "$REPO/lab/harness/run_matrix.sh" --run-profile final --reps 10 --seed 2027 --scenarios "$2" --attacks "$3" --resume
  python3 -I lab/analysis/summarize_runs.py --platform "$PLATFORM" --profile final >/dev/null
  git add data/raw data/processed data/captures/manifest.csv
  git commit -q -m "Tanda real ($PLATFORM): bloque $1" && git push -q 2>&1 | tail -1
  [ -e "$LAB_RUN/ABORT" ] && { echo "ABORT: tanda detenida"; exit 3; }
}
block "1 E1/E3 syn+modbus" "E1 E3" "syn modbus"
block "2 E1/E3 udp"        "E1 E3" "udp"
block "3 E1/E3 icmp"       "E1 E3" "icmp"
block "4 E2 todos"         "E2"    "syn modbus udp icmp"
block "5 E0"               "E0"    "none"
echo "##### tanda terminada $(date -u +%T)"
