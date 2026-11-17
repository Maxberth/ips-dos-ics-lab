#!/usr/bin/env bash
# Ejecuta un comando del host dentro de un scope con límites (sin sudo).
# Uso: limited-run.sh <MemoryMax> <CPUWeight> -- comando args...
set -euo pipefail
MEM="${1:?MemoryMax}"; W="${2:?CPUWeight}"; shift 2; [ "${1:-}" = -- ] && shift
exec systemd-run --user --scope --quiet -p MemoryMax="$MEM" -p MemorySwapMax=0 -p CPUWeight="$W" "$@"
