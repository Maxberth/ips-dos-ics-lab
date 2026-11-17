#!/usr/bin/env bash
# Quita de todas las VMs la NIC de la red NAT lab-install (en vivo y en la configuración)
# y apaga esa red. Después comprueba que ninguna VM tiene ruta por defecto.
set -euo pipefail
source "$(dirname "$0")/lib.sh"
for vm in $(V list --all --name | grep '^lab-'); do
  mac=$(V domiflist "$vm" | awk '$3=="lab-install"{print $5}')
  [ -n "$mac" ] || continue
  flags="--config"; [ "$(V domstate "$vm")" = running ] && flags="--live --config"
  V detach-interface "$vm" network --mac "$mac" $flags && echo "$vm: NIC NAT $mac quitada"
done
V net-info lab-install 2>/dev/null | grep -q 'Active:.*yes' && V net-destroy lab-install
for vm in $(V list --name | grep '^lab-'); do
  r=$(lab_ssh "$vm" "ip route show default" 2>/dev/null || echo "?")
  echo "$vm ruta por defecto: ${r:-ninguna}"
done
