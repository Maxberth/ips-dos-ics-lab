#!/usr/bin/env bash
# Crea UNA VM del laboratorio desde la imagen base Debian 13 y cloud-init. Sin sudo (grupo libvirt).
# Uso: PROFILE=lab/config/profile_<plataforma>.env lab/setup/create_vm.sh lab-ips [--install-nic]
#   --install-nic   añade una NIC en la red NAT lab-install para que cloud-init instale paquetes.
#                   Se quita después con lab/setup/detach_install_nic.sh.
set -euo pipefail
source "$(dirname "$0")/lib.sh"
VM="${1:?nombre de VM (ver lab/setup/lab_vms.tsv)}"; INSTALL_NIC="${2:-}"
ROLE=$(vm_field "$VM" 2); [ -n "$ROLE" ] || { echo "VM desconocida: $VM"; exit 1; }
NICS=$(vm_field "$VM" 3); ROUTES=$(vm_field "$VM" 4); PKGS=$(vm_field "$VM" 5)
eval "MEM=\$VM_${ROLE}_MEM VCPUS=\$VM_${ROLE}_VCPUS PIN=\"\$VM_${ROLE}_PIN\""
MEM=${MEM_OVERRIDE:-$MEM}   # p. ej. más RAM temporal para compilar OpenPLC
guard_ok || { echo "Guardián no está en OK/WARN: $(cat "$LAB_RUN/STATE" 2>/dev/null)"; exit 2; }
V dominfo "$VM" >/dev/null 2>&1 && { echo "$VM ya existe"; exit 0; }

[ -f "$SSH_KEY" ] || ssh-keygen -q -t ed25519 -N '' -C "ips-lab" -f "$SSH_KEY"
[ -f "$IMG_DIR/$BASE_IMG_NAME" ] || cp "$CACHE/$BASE_IMG_NAME" "$IMG_DIR/$BASE_IMG_NAME"
chmod 0644 "$IMG_DIR/$BASE_IMG_NAME" 2>/dev/null || true   # libvirt cambia el dueño al usarla

SEED="$CACHE/seed/$VM"; mkdir -p "$SEED"
MGMT=$(mgmt_ip "$VM")
# --- user-data ---
{
  echo "#cloud-config"
  echo "hostname: ${VM#lab-}"
  echo "fqdn: ${VM#lab-}.lab"
  echo "users:"
  echo "  - name: lab"
  echo "    sudo: ALL=(ALL) NOPASSWD:ALL"
  echo "    shell: /bin/bash"
  echo "    lock_passwd: true"
  echo "    ssh_authorized_keys: [\"$(cat "$SSH_KEY.pub")\"]"
  echo "ssh_pwauth: false"
  echo "timezone: UTC"
  if [ "$INSTALL_NIC" = --install-nic ]; then
    echo "package_update: true"
    echo "packages: [$(echo "$PKGS" | sed 's/ /, /g')]"
  fi
  echo "runcmd:"
  # Sin tareas de fondo que contaminen las mediciones.
  echo "  - [systemctl, disable, --now, apt-daily.timer, apt-daily-upgrade.timer, man-db.timer, e2scrub_all.timer, fstrim.timer]"
  echo "  - [sh, -c, 'echo done > /var/lib/cloud/lab-ready']"
} > "$SEED/user-data"
# --- network-config (v2) ---
{
  echo "version: 2"
  echo "ethernets:"
  IFS=, read -ra nl <<<"$NICS"
  for n in "${nl[@]}"; do
    vlan=${n%%:*}; cidr=${n#*:}; ip=${cidr%/*}; name=$([ "$vlan" = 99 ] && echo mgmt || echo "v$vlan")
    echo "  $name:"
    echo "    match: {macaddress: \"$(mac_for "$vlan" "$ip")\"}"
    echo "    set-name: $name"
    echo "    addresses: [$cidr]"
    if [ "$vlan" != 99 ]; then
      r=$(echo "$ROUTES" | tr ',' '\n' | while IFS='>' read -r dst gw; do
            [ -n "$dst" ] || continue
            gnet=$(echo "$gw" | cut -d. -f1-3); inet=$(echo "$ip" | cut -d. -f1-3)
            if [ "$gnet" = "$inet" ]; then printf '{to: %s, via: %s}, ' "$dst" "$gw"; fi; done; true)
      if [ -n "$r" ]; then echo "    routes: [${r%, }]"; fi
    fi
  done
  if [ "$INSTALL_NIC" = --install-nic ]; then
    echo "  nat:"
    echo "    match: {macaddress: \"$(mac_for 0 "$MGMT")\"}"
    echo "    set-name: nat"
    echo "    dhcp4: true"
    echo "    nameservers: {addresses: [192.168.250.1]}"
  fi
} > "$SEED/network-config"
printf 'instance-id: %s-%s\nlocal-hostname: %s\n' "$VM" "$(date +%s)" "${VM#lab-}" > "$SEED/meta-data"
cloud-localds -N "$SEED/network-config" "$IMG_DIR/$VM-seed.iso" "$SEED/user-data" "$SEED/meta-data"
mkdir -p "$REPO/lab/setup/cloud-init/$VM"
# Copia versionada sin la clave pública concreta.
sed 's/ssh_authorized_keys: .*/ssh_authorized_keys: ["<clave pública de ~\/.ssh\/ips-lab_ed25519.pub>"]/' "$SEED/user-data" > "$REPO/lab/setup/cloud-init/$VM/user-data"
cp "$SEED/network-config" "$REPO/lab/setup/cloud-init/$VM/network-config"

qemu-img create -q -f qcow2 -F qcow2 -b "$IMG_DIR/$BASE_IMG_NAME" "$IMG_DIR/$VM.qcow2" "${VM_DISK_GB}G"

NETARGS=()
IFS=, read -ra nl <<<"$NICS"
for n in "${nl[@]}"; do vlan=${n%%:*}; ip=${n#*:}; ip=${ip%/*}
  NETARGS+=(--network "network=ovs-ot,portgroup=vlan$vlan,model=virtio,mac=$(mac_for "$vlan" "$ip")"); done
if [ "$INSTALL_NIC" = --install-nic ]; then NETARGS+=(--network "network=lab-install,model=virtio,mac=$(mac_for 0 "$MGMT")"); fi

i=0; PINARGS=""; for c in $PIN; do PINARGS+="vcpupin$i.vcpu=$i,vcpupin$i.cpuset=$c,"; i=$((i+1)); done
HARD_KIB=$(( (MEM + 384) * 1024 ))

VI --name "$VM" --memory "$MEM" --vcpus "$VCPUS" \
  --cputune "${PINARGS}emulatorpin.cpuset=$EMULATOR_CPUS" \
  --memtune "hard_limit=$HARD_KIB" --memballoon none \
  --cpu host-passthrough --osinfo debian13 \
  --import --disk "path=$IMG_DIR/$VM.qcow2,bus=virtio" --disk "path=$IMG_DIR/$VM-seed.iso,device=cdrom" \
  "${NETARGS[@]}" --graphics none --video vga --console pty,target_type=serial --noautoconsole \
  --metadata "description=ips-dos-ics-lab $PLATFORM role=$ROLE"
V dumpxml "$VM" > "$REPO/lab/setup/libvirt/$VM.xml"
echo "creada $VM (mem=${MEM}MiB vcpus=$VCPUS pin=$PIN mgmt=$MGMT)"
