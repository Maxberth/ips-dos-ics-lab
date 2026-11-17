#!/usr/bin/env bash
# Vuelca las versiones relevantes del host y de cada VM a data/raw/versions/<plataforma>_<fecha>.txt.
# Uso: PROFILE=... lab/setup/versions_snapshot.sh
set -uo pipefail
source "$(dirname "$0")/lib.sh"
mkdir -p "$REPO/data/raw/versions"
OUT="$REPO/data/raw/versions/${PLATFORM}_$(date -u +%Y%m%dT%H%M%SZ).txt"
{
  echo "# versiones  $(date -u +%FT%TZ)  plataforma=$PLATFORM  repo=$(git -C "$REPO" rev-parse --short HEAD)"
  echo "## host"; uname -r
  pacman -Q qemu-base qemu-system-x86 libvirt virt-install openvswitch edk2-ovmf wireshark-cli tcpdump python python-numpy python-scipy python-pandas python-matplotlib systemd linux-cachyos 2>&1
  echo "base_image_sha512=$(sha512sum "$IMG_DIR/$BASE_IMG_NAME" 2>/dev/null | cut -d' ' -f1)"
  for vm in $(V list --name | grep '^lab-'); do
    echo "## $vm"
    lab_ssh "$vm" ". /etc/os-release; echo \$PRETTY_NAME; uname -r; dpkg-query -W -f='\${Package} \${Version}\n' suricata nftables hping3 python3-scapy python3-pymodbus python3 tcpdump iperf3 sysstat 2>/dev/null; cat /opt/lab/openplc_commit.txt 2>/dev/null; command -v suricata >/dev/null && suricata --build-info | grep -iE '^This is|NFQueue support|NFQ' ; true"
  done
} > "$OUT" 2>&1
echo "$OUT"
