# Funciones comunes de los scripts del laboratorio (se cargan con `source`).
# Requiere: PROFILE con la ruta del perfil de plataforma.
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# shellcheck disable=SC1090
source "${PROFILE:?define PROFILE=lab/config/profile_<plataforma>.env}"
IMG_DIR=/var/lib/libvirt/images/ips-lab
CACHE="$HOME/.cache/ips-lab"
BASE_IMG_NAME=debian-13-genericcloud-amd64.qcow2
SSH_KEY="$HOME/.ssh/ips-lab_ed25519"
LAB_RUN="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/ips-lab"
URI=qemu:///system

# Ejecuta con el grupo indicado aunque la sesión gráfica aún no lo tenga (usermod reciente sin
# volver a iniciar sesión). CachyOS no trae `sg`; se usa `newgrp` (setuid) leyendo el comando por stdin.
in_group(){ local g=$1; shift; if id -nG | tr ' ' '\n' | grep -qx "$g"; then "$@"; else printf '%q ' "$@" | newgrp "$g"; fi; }
# libvirt autoriza por polkit según la pertenencia al grupo en /etc/group, así que no hace falta newgrp.
V(){ virsh -c "$URI" "$@"; }
VI(){ virt-install --connect "$URI" "$@"; }

# IP de gestión de una VM (columna nics del inventario, VLAN 99).
vm_field(){ awk -F'\t' -v n="$1" -v c="$2" '$1==n{print $c}' "$REPO/lab/setup/lab_vms.tsv"; }
mgmt_ip(){ vm_field "$1" 3 | tr ',' '\n' | awk -F'[:/]' '$1==99{print $2}'; }
lab_ssh(){ local vm=$1; shift; ssh -i "$SSH_KEY" -o BatchMode=yes -o StrictHostKeyChecking=accept-new \
  -o UserKnownHostsFile="$CACHE/known_hosts" -o ConnectTimeout=5 "lab@$(mgmt_ip "$vm")" "$@"; }
lab_scp(){ scp -q -i "$SSH_KEY" -o BatchMode=yes -o StrictHostKeyChecking=accept-new \
  -o UserKnownHostsFile="$CACHE/known_hosts" "$@"; }
# MAC determinista: 52:54:00:00:<vlan>:<último octeto en hex>
mac_for(){ printf '52:54:00:00:%02d:%02x' "$1" "${2##*.}"; }
guard_ok(){ local s; s=$(cat "$LAB_RUN/STATE" 2>/dev/null | cut -d' ' -f1); [ "$s" = OK ] || [ "$s" = WARN ]; }
