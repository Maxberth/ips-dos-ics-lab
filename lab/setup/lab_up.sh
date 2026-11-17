#!/usr/bin/env bash
# Monta el laboratorio completo desde cero (sin sudo). Idempotente: lo ya hecho se salta.
# Requiere: root_setup.sh ejecutado, imagen base en ~/.cache/ips-lab, guardián activo.
# Uso: PROFILE=lab/config/profile_<plataforma>.env lab/setup/lab_up.sh [--skip-openplc]
set -euo pipefail
source "$(dirname "$0")/lib.sh"
source "$REPO/lab/config/experiment.env"
LOG="$REPO/docs/lab/logs/P07_lab_up_${PLATFORM}.txt"
exec > >(tee -a "$LOG") 2>&1
echo "== lab_up $(date -u +%FT%TZ) plataforma=$PLATFORM"
guard_ok || { echo "guardián no está en OK"; exit 2; }

# Redes libvirt
for n in ovs-ot lab-install; do
  V net-info "$n" >/dev/null 2>&1 || V net-define "$REPO/lab/setup/libvirt/net-$n.xml"
  V net-autostart "$n" --disable >/dev/null 2>&1 || true
  [ "$(V net-info "$n" | awk '/Active:/{print $2}')" = yes ] || V net-start "$n"
done

# VMs, una por una, comprobando el guardián entre cada una (P07).
VMS="lab-fw lab-ips lab-plc lab-scada lab-attacker"
for vm in $VMS; do
  if ! V dominfo "$vm" >/dev/null 2>&1; then
    guard_ok || { echo "guardián en $(cat "$LAB_RUN/STATE")"; exit 2; }
    if [ "$vm" = lab-plc ]; then
      # Compilar OpenPLC necesita más RAM: se crea con 1536 MiB y luego se baja al valor del perfil.
      MEM_OVERRIDE=1536 "$REPO/lab/setup/create_vm.sh" "$vm"
    else
      "$REPO/lab/setup/create_vm.sh" "$vm"
    fi
  fi
  [ "$(V domstate "$vm")" = running ] || V start "$vm"
  "$REPO/lab/setup/provision_vm.sh" "$vm"
  "$REPO/lab/guard/lab-status.sh" | sed -n '1,4p'
done

if [ "${1:-}" != --skip-openplc ] && ! lab_ssh lab-plc "ss -ltn | grep -q ':502 '"; then
  echo "== OpenPLC (compila, ~15-20 min)"
  python3 -I "$REPO/lab/setup/http_proxy.py" 3128 2> "$REPO/docs/lab/logs/P10_openplc_proxy_${PLATFORM}.txt" &
  PROXY_PID=$!; sleep 1
  ssh -i "$SSH_KEY" -o BatchMode=yes -o UserKnownHostsFile="$CACHE/known_hosts" -o ExitOnForwardFailure=yes \
    -R 127.0.0.1:3128:127.0.0.1:3128 "lab@$(mgmt_ip lab-plc)" \
    "LAB_PROXY=http://127.0.0.1:3128 OPENPLC_COMMIT='${OPENPLC_COMMIT:-}' bash /tmp/plc_install_openplc.sh" \
    || { kill $PROXY_PID; echo "OpenPLC falló: ver /opt/lab/openplc_install.log en lab-plc"; exit 1; }
  kill $PROXY_PID
fi
# PLC a la RAM del perfil
cur=$(V dominfo lab-plc | awk '/Max memory/{print $3}')
if [ "$cur" -ne $((VM_PLC_MEM * 1024)) ]; then
  V shutdown lab-plc; for i in $(seq 60); do [ "$(V domstate lab-plc)" = "shut off" ] && break; sleep 1; done
  V setmaxmem lab-plc "$((VM_PLC_MEM * 1024))" --config
  V setmem lab-plc "$((VM_PLC_MEM * 1024))" --config
  V memtune lab-plc --hard-limit "$(( (VM_PLC_MEM + 384) * 1024 ))" --config
  V start lab-plc; for i in $(seq 90); do lab_ssh lab-plc "ss -ltn | grep -q ':502 '" 2>/dev/null && break; sleep 2; done
  V dumpxml lab-plc > "$REPO/lab/setup/libvirt/lab-plc.xml"
fi

# Quitar la NIC NAT: sin ruta a Internet durante las mediciones.
"$REPO/lab/setup/detach_install_nic.sh"
echo "== lab_up terminado $(date -u +%FT%TZ)"
