#!/usr/bin/env bash
# Guardián de RAM, swap, presión de memoria, temperatura y energía. Corre SIN sudo.
# Lee los umbrales del perfil de plataforma y escribe un CSV cada GUARD_INTERVAL_S segundos.
#
# Estados: OK -> WARN -> PAUSE -> ABORT
#   PAUSE crea  $LAB_RUN/PAUSE  (el arnés detiene el ataque y espera)
#   ABORT crea  $LAB_RUN/ABORT  y destruye las VMs del laboratorio (prefijo lab-). Queda fijado
#         hasta borrarlo a mano (lab/guard/lab-stop.sh --clear).
# Histéresis: PAUSE por temperatura solo se levanta cuando Tctl < GUARD_RESUME_TCTL.
#
# Uso:  lab/guard/guard.sh lab/config/profile_<plataforma>.env [--once]
#   Normalmente se lanza con lab/guard/guard-start.sh (servicio de usuario transitorio).
set -uo pipefail
PROFILE="${1:?uso: guard.sh <perfil.env> [--once]}"; ONCE="${2:-}"
# shellcheck disable=SC1090
source "$PROFILE"
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
LAB_RUN="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/ips-lab"
mkdir -p "$LAB_RUN" "$REPO/data/raw/guard"
# Las simulaciones de prueba ponen GUARD_CSV fuera de data/raw (no son datos del laboratorio).
CSV="${GUARD_CSV:-$REPO/data/raw/guard/guard_${PLATFORM}_$(date -u +%Y%m%d).csv}"
[ -s "$CSV" ] || echo "ts_utc,platform,mem_avail_mib,swap_used_mib,swap_growth_mib,psi_mem_some_avg10,tctl_c,load1,ac_online,state,reason" > "$CSV"

find_tctl(){ for h in /sys/class/hwmon/hwmon*; do
  [ "$(cat "$h/name" 2>/dev/null)" = k10temp ] || [ "$(cat "$h/name" 2>/dev/null)" = coretemp ] || continue
  for l in "$h"/temp*_label; do
    case "$(cat "$l")" in Tctl|Tdie|"Package id 0") echo "${l%_label}_input"; return;; esac
  done; done; }
TCTL_FILE="$(find_tctl)"
AC_FILE="$(for f in /sys/class/power_supply/*; do [ "$(cat "$f/type" 2>/dev/null)" = Mains ] && echo "$f/online"; done | head -1)"

swap_used(){ awk '/SwapTotal/{t=$2}/SwapFree/{f=$2}END{print int((t-f)/1024)}' /proc/meminfo; }
SWAP0="$(swap_used)"
PAUSE_TEMP_LATCH=0

destroy_lab_vms(){
  local c="virsh -c qemu:///system"
  for d in $(sg libvirt -c "$c list --name" 2>/dev/null | grep '^lab-'); do sg libvirt -c "$c destroy $d" >/dev/null 2>&1; done
}

while :; do
  mem=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
  sw=$(swap_used); growth=$(( sw - SWAP0 ))
  psi=$(awk '/^some/{split($2,a,"=");print a[2]}' /proc/pressure/memory)
  t=$( [ -n "$TCTL_FILE" ] && awk '{printf "%.1f",$1/1000}' "$TCTL_FILE" || echo NA)
  load=$(cut -d' ' -f1 /proc/loadavg)
  ac=$( [ -n "$AC_FILE" ] && cat "$AC_FILE" || echo NA)
  ti=${t%.*}; [ "$t" = NA ] && ti=0
  state=OK; reason=""

  if [ "$mem" -lt "$GUARD_ABORT_MEM_MIB" ]; then state=ABORT; reason="mem<${GUARD_ABORT_MEM_MIB}"
  elif [ "$ti" -ge "$GUARD_ABORT_TCTL" ]; then state=ABORT; reason="tctl>=${GUARD_ABORT_TCTL}"
  elif [ "$growth" -gt "$GUARD_ABORT_SWAP_GROWTH_MIB" ]; then state=ABORT; reason="swap+${growth}MiB"
  elif [ "$mem" -lt "$GUARD_PAUSE_MEM_MIB" ]; then state=PAUSE; reason="mem<${GUARD_PAUSE_MEM_MIB}"
  elif [ "$ti" -ge "$GUARD_PAUSE_TCTL" ]; then state=PAUSE; reason="tctl>=${GUARD_PAUSE_TCTL}"; PAUSE_TEMP_LATCH=1
  elif [ "$PAUSE_TEMP_LATCH" = 1 ] && [ "$ti" -ge "$GUARD_RESUME_TCTL" ]; then state=PAUSE; reason="enfriando>=${GUARD_RESUME_TCTL}"
  elif awk -v p="$psi" -v l="$GUARD_PAUSE_PSI" 'BEGIN{exit !(p>l)}'; then state=PAUSE; reason="psi>${GUARD_PAUSE_PSI}"
  elif [ "${GUARD_REQUIRE_AC:-0}" = 1 ] && [ "$ac" = 0 ]; then state=PAUSE; reason="bateria"
  elif [ "$mem" -lt "$GUARD_WARN_MEM_MIB" ]; then state=WARN; reason="mem<${GUARD_WARN_MEM_MIB}"
  elif [ "$ti" -ge "$GUARD_WARN_TCTL" ]; then state=WARN; reason="tctl>=${GUARD_WARN_TCTL}"
  elif [ "$growth" -gt 256 ]; then state=WARN; reason="swap+${growth}MiB"
  fi
  [ "$state" != PAUSE ] && [ "$ti" -lt "$GUARD_RESUME_TCTL" ] && PAUSE_TEMP_LATCH=0
  [ -e "$LAB_RUN/ABORT" ] && { state=ABORT; reason="${reason:-fijado}"; }

  case $state in
    ABORT) [ -e "$LAB_RUN/ABORT" ] || { echo "$(date -u +%FT%TZ) $reason" > "$LAB_RUN/ABORT"; destroy_lab_vms; }
           touch "$LAB_RUN/PAUSE";;
    PAUSE) [ -e "$LAB_RUN/PAUSE" ] || echo "$(date -u +%FT%TZ) $reason" > "$LAB_RUN/PAUSE";;
    *)     rm -f "$LAB_RUN/PAUSE";;
  esac
  echo "$state $reason" > "$LAB_RUN/STATE"
  echo "$(date -u +%FT%T.%3NZ),$PLATFORM,$mem,$sw,$growth,$psi,$t,$load,$ac,$state,$reason" >> "$CSV"
  [ "$ONCE" = --once ] && { echo "$state $reason mem=$mem tctl=$t psi=$psi ac=$ac"; exit 0; }
  sleep "$GUARD_INTERVAL_S"
done
