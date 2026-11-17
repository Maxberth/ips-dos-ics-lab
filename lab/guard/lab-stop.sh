#!/usr/bin/env bash
# Parada limpia del laboratorio, segura en cualquier momento. Sin sudo.
#   lab-stop.sh            apaga VMs (shutdown, destroy a los 30 s) y detiene el guardián
#   lab-stop.sh --clear    además borra los indicadores PAUSE/ABORT
LAB_RUN="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/ips-lab"
V="virsh -c qemu:///system"
vms=$($V list --name 2>/dev/null | grep '^lab-' || true)
for d in $vms; do $V shutdown $d >/dev/null 2>&1; done
for i in $(seq 30); do [ -z "$($V list --name 2>/dev/null | grep '^lab-')" ] && break; sleep 1; done
for d in $($V list --name 2>/dev/null | grep '^lab-'); do $V destroy $d >/dev/null 2>&1; done
systemctl --user stop ips-lab-guard 2>/dev/null || true
[ "${1:-}" = --clear ] && rm -f "$LAB_RUN/PAUSE" "$LAB_RUN/ABORT" "$LAB_RUN/STATE"
echo "lab-stop: VMs apagadas: ${vms:-ninguna}; guardián detenido"
