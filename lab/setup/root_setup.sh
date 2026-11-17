#!/usr/bin/env bash
# Configuración de root del laboratorio. Es el ÚNICO paso con sudo; lo ejecuta el usuario.
# Idempotente: se puede volver a correr (por ejemplo después de reiniciar, para recrear mgmt99).
#
# Uso (desde la raíz del repo):
#   sudo bash lab/setup/root_setup.sh lab/config/profile_<plataforma>.env
#
# Qué hace:
#   1. Instala los paquetes del host con `pacman -S --needed` (sin -Sy ni -Syu).
#   2. Añade al usuario del laboratorio a los grupos libvirt, kvm y wireshark.
#   3. Detiene Docker (servicio y socket) sin deshabilitarlo.
#   4. Activa libvirtd y Open vSwitch.
#   5. Crea el directorio de imágenes de las VMs, propiedad del usuario.
#   6. Pone límites a machine.slice (RAM, swap y CPU de todas las VMs).
#   7. Crea el switch ovs-ot SIN puertos físicos, el puerto de gestión del host (VLAN 99)
#      y dos espejos (VLAN 20 -> mir20, VLAN 30 -> mir30) para capturar fuera de banda.
# No toca enp2s0, wlan0, tailscale0 ni las redes de Docker.
set -euo pipefail

PROFILE="${1:?uso: sudo bash lab/setup/root_setup.sh lab/config/profile_<plataforma>.env}"
[ "$(id -u)" -eq 0 ] || { echo "Ejecutar con sudo"; exit 1; }
# shellcheck disable=SC1090
source "$PROFILE"
id "$LAB_USER" >/dev/null || { echo "LAB_USER=$LAB_USER no existe; edita $PROFILE"; exit 1; }
echo "== root_setup  $(date -u +%FT%TZ)  plataforma=$PLATFORM  usuario=$LAB_USER"

step(){ echo; echo "== $*"; }
show(){ echo "+ $*"; "$@"; }

step "1. Paquetes del host"
PKGS=(qemu-base libvirt virt-install edk2-ovmf dnsmasq openvswitch libisoburn cloud-image-utils
      tcpdump wireshark-cli iperf3 python-scipy python-pandas sysstat stress-ng)
show pacman -S --needed --noconfirm "${PKGS[@]}"

step "2. Grupos del usuario"
for g in libvirt kvm wireshark; do getent group "$g" >/dev/null || show groupadd -r "$g"; done
show usermod -aG libvirt,kvm,wireshark "$LAB_USER"
id "$LAB_USER"

step "3. Docker detenido (no deshabilitado)"
if systemctl list-unit-files docker.service >/dev/null 2>&1; then
  echo "Contenedores en ejecución antes de detener:"; docker ps --format '{{.Names}} {{.Image}}' 2>/dev/null || true
  show systemctl stop docker.socket docker.service || true
  echo "docker: $(systemctl is-active docker.service || true)  socket: $(systemctl is-active docker.socket || true)"
  echo "Para reactivarlo: sudo systemctl start docker.socket docker.service"
fi

step "4. libvirtd y Open vSwitch"
show systemctl enable --now libvirtd.service
show systemctl enable --now ovsdb-server.service ovs-vswitchd.service
systemctl is-active libvirtd ovsdb-server ovs-vswitchd

step "5. Directorio de imágenes"
IMG_DIR=/var/lib/libvirt/images/ips-lab
show install -d -o "$LAB_USER" -g libvirt -m 2775 "$IMG_DIR"
ls -ld "$IMG_DIR"

step "6. Límites de machine.slice"
show systemctl set-property machine.slice \
  MemoryHigh="$MACHINE_MEMORY_HIGH" MemoryMax="$MACHINE_MEMORY_MAX" \
  MemorySwapMax="$MACHINE_SWAP_MAX" AllowedCPUs="$VM_ALLOWED_CPUS"
systemctl show machine.slice -p MemoryHigh -p MemoryMax -p MemorySwapMax -p AllowedCPUs

step "7. Switch ovs-ot, gestión y espejos"
show ovs-vsctl --may-exist add-br ovs-ot
show ovs-vsctl --may-exist add-port ovs-ot mgmt99 tag=99 -- set interface mgmt99 type=internal
show ovs-vsctl --may-exist add-port ovs-ot mir20 -- set interface mir20 type=internal
show ovs-vsctl --may-exist add-port ovs-ot mir30 -- set interface mir30 type=internal
show ip link set ovs-ot up
show ip link set mgmt99 up
show ip link set mir20 up
show ip link set mir30 up
ip -4 addr show dev mgmt99 | grep -q '192.168.99.1/24' || show ip addr add 192.168.99.1/24 dev mgmt99
# Sin IPv6 en los puertos de captura, para que el host no inyecte tráfico propio en ellos.
for i in mir20 mir30; do show sysctl -q -w "net.ipv6.conf.$i.disable_ipv6=1"; done
# Espejos: todo lo que viaja en la VLAN 20 (antes del IPS) y en la VLAN 30 (después del IPS).
show ovs-vsctl -- --if-exists clear bridge ovs-ot mirrors
for v in 20 30; do
  ovs-vsctl -- --id=@out get port "mir$v" \
            -- --id=@m create mirror name="m$v" select-all=true select-vlan="$v" output-port=@out \
            -- add bridge ovs-ot mirrors @m >/dev/null
done
echo "Puertos de ovs-ot: $(ovs-vsctl list-ports ovs-ot | tr '\n' ' ')"
for p in enp2s0 wlan0 tailscale0; do
  if ovs-vsctl list-ports ovs-ot | grep -qx "$p"; then echo "ERROR: $p está en ovs-ot"; exit 1; fi
done
ovs-vsctl --columns=name,select_vlan,output_port list mirror
echo "net.ipv4.ip_forward=$(sysctl -n net.ipv4.ip_forward) (no se cambia)"

step "8. Comprobación como $LAB_USER (con los grupos nuevos vía sg)"
sudo -u "$LAB_USER" sg libvirt -c 'virsh -c qemu:///system list --all' && echo "libvirt OK sin sudo"
sudo -u "$LAB_USER" sg wireshark -c 'dumpcap -D' | grep -E 'mir20|mir30|mgmt99' && echo "dumpcap OK sin sudo"
virt-host-validate qemu || true
echo; echo "== root_setup terminado $(date -u +%FT%TZ)"
