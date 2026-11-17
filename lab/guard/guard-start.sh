#!/usr/bin/env bash
# Arranca el guardián como servicio de usuario transitorio (sin sudo). Idempotente.
# Uso: lab/guard/guard-start.sh lab/config/profile_<plataforma>.env
set -euo pipefail
PROFILE="$(realpath "${1:?uso: guard-start.sh <perfil.env>}")"
DIR="$(cd "$(dirname "$0")" && pwd)"
if systemctl --user is-active -q ips-lab-guard; then echo "guardián ya activo"; exit 0; fi
systemctl --user reset-failed ips-lab-guard 2>/dev/null || true
systemd-run --user --unit=ips-lab-guard --description="IPS lab guard" \
  -p CPUWeight=1000 -p MemoryMax=64M -p OOMScoreAdjust=-500 \
  "$DIR/guard.sh" "$PROFILE"
sleep 3; systemctl --user is-active ips-lab-guard
