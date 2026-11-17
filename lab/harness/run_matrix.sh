#!/usr/bin/env bash
# Ejecuta una matriz de corridas en orden aleatorio reproducible (semilla), obedeciendo al guardián.
# Uso: PROFILE=... lab/harness/run_matrix.sh --run-profile piloto --reps 1 \
#        [--scenarios "E0 E1 E2 E3"] [--attacks "syn udp icmp modbus"] [--seed 2027]
set -uo pipefail
source "$(dirname "$0")/../setup/lib.sh"
RP=piloto; REPS=1; SCENS="E0 E1 E2 E3"; ATTACKS="syn udp icmp modbus"; SEED=2027
while [ $# -gt 0 ]; do case $1 in
  --run-profile) RP=$2; shift 2;; --reps) REPS=$2; shift 2;; --scenarios) SCENS=$2; shift 2;;
  --attacks) ATTACKS=$2; shift 2;; --seed) SEED=$2; shift 2;; *) echo "arg $1"; exit 1;; esac; done
PLAN=$(python3 -I - "$SEED" "$REPS" "$SCENS" "$ATTACKS" <<'EOF'
import random, sys
seed, reps, scens, attacks = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3].split(), sys.argv[4].split()
runs = []
for r in range(1, reps + 1):
    for s in scens:
        for a in (["none"] if s == "E0" else attacks):
            runs.append((s, a, r))
random.Random(seed).shuffle(runs)
for s, a, r in runs: print(s, a, r)
EOF
)
N=$(echo "$PLAN" | wc -l)
echo "matriz: $N corridas, perfil=$RP, semilla=$SEED"
i=0
while read -r s a r; do
  i=$((i+1))
  [ -e "$LAB_RUN/ABORT" ] && { echo "ABORT del guardián: se detiene la matriz"; exit 3; }
  echo "=== [$i/$N] $s $a rep $r  $(date -u +%T)"
  t0=$(date +%s)
  "$REPO/lab/harness/run_once.sh" --scenario "$s" --attack "$a" --run-profile "$RP" --rep "$r" --notes "matrix seed=$SEED $i/$N"
  echo "    duración real: $(( $(date +%s) - t0 )) s"
done <<< "$PLAN"
