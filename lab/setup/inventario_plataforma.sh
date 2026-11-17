#!/usr/bin/env bash
# Inventario SOLO LECTURA de una plataforma del laboratorio (P02). No instala ni cambia nada. Sin sudo.
# Uso: lab/setup/inventario_plataforma.sh pc-miguel   -> docs/lab/logs/pc-miguel_P02_*.txt (tarda ~45 s)
PLATAFORMA="${1:?uso: $0 <nombre-plataforma>  (ej. laptop, pc-miguel)}"
D="$(cd "$(dirname "$0")/../.." && pwd)/docs/lab/logs"
mkdir -p "$D"
P="$D/${PLATAFORMA}_P02"
run(){ echo "\$ $*"; eval "$@" 2>&1; echo; }
hdr(){ echo "# $1"; echo "# Fecha: $(date -Is)  Host: $(hostname)  (solo lectura, sin sudo)"; echo; }

{ hdr "01 Sistema"
run hostname
run cat /etc/os-release
run uname -a
run "pacman -Q linux-cachyos linux-cachyos-headers linux linux-lts 2>/dev/null"
run "ls /boot"
run cat /proc/cmdline
run "hostnamectl"
} > "${P}_01_sistema.txt"

{ hdr "02 CPU"
run lscpu
run lscpu -e
run "cat /sys/devices/system/cpu/cpu*/topology/thread_siblings_list | sort -u"
run "cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_driver"
run "cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"
run "cat /sys/devices/system/cpu/cpu0/cpufreq/energy_performance_preference"
run "cat /sys/devices/system/cpu/amd_pstate/status"
run "grep -m1 -o -w -E 'svm|vmx' /proc/cpuinfo"
} > "${P}_02_cpu.txt"

{ hdr "03 Memoria"
run free -h
run cat /proc/meminfo
run swapon --show
run zramctl
run cat /proc/sys/vm/swappiness
run "systemctl is-active systemd-oomd earlyoom"
run cat /proc/pressure/memory
run "ps -eo pid,user,rss,comm --sort=-rss | head -16"
run "ps -eo rss,comm --sort=-rss | awk 'NR>1{a[\$2]+=\$1}END{for(k in a)printf \"%8.0f MiB  %s\n\",a[k]/1024,k}' | sort -rn | head -15"
} > "${P}_03_memoria.txt"

{ hdr "04 Temperatura y energía"
for i in 1 2 3; do echo "## Lectura $i ($(date +%T))"; run sensors; [ $i -lt 3 ] && sleep 20; done
run "cat /proc/loadavg"
run "upower -d"
run "powerprofilesctl"
run "cat /sys/firmware/acpi/platform_profile /sys/firmware/acpi/platform_profile_choices"
run "for f in /sys/class/power_supply/*; do echo \$f; cat \$f/type \$f/online \$f/status \$f/capacity 2>/dev/null; done"
} > "${P}_04_temperatura_energia.txt"

{ hdr "05 KVM"
run ls -l /dev/kvm
run "lsmod | grep -E '^kvm'"
run cat /sys/module/kvm_amd/parameters/nested
run ls /sys/class/iommu
run "ls /sys/kernel/iommu_groups | wc -l"
run systemd-detect-virt
run id
} > "${P}_05_kvm.txt"

{ hdr "06 Disco"
run lsblk -f
run "lsblk -d -o NAME,SIZE,ROTA,TRAN,MODEL"
run df -h
run "df -BG --output=avail / | tail -1"
} > "${P}_06_disco.txt"

{ hdr "07 Red"
run ip -br link
run ip -br addr
run ip route
run "ip -br addr | grep -E '192\.168\.(10|20|30)\.' || echo 'Ninguna interfaz en 192.168.10/20/30.0/24'"
run "ip route | grep -E '192\.168\.(10|20|30)\.' || echo 'Ninguna ruta a 192.168.10/20/30.0/24'"
run "systemctl is-active docker docker.socket tailscaled libvirtd ovs-vswitchd NetworkManager"
if systemctl is-active -q docker; then run "docker network inspect -f '{{.Name}} {{range .IPAM.Config}}{{.Subnet}} {{end}}' \$(docker network ls -q)"; else echo 'dockerd inactivo: no se consulta para no activarlo por socket'; echo; fi
run "lspci | grep -iE 'ethernet|network'"
} > "${P}_07_red.txt"

{ hdr "08 Paquetes"
for p in qemu-base qemu-full libvirt virt-install openvswitch suricata snort hping python-scapy iperf3 tcpdump wireshark-cli nftables iptables-nft python-pymodbus dnsmasq edk2-ovmf paru yay latexmk texlive-binextra; do
  if pacman -Q $p >/dev/null 2>&1; then echo "INSTALADO  $(pacman -Q $p)"
  else r=$(pacman -Si $p 2>/dev/null | awk -F': ' '/^Repository/{r=$2}/^Version/{v=$2}END{if(r)print r" "v}'); echo "FALTA      $p  -> ${r:-no está en los repos oficiales (AUR u otra fuente)}"; fi
done
echo
run "paru -Si suricata snort python-pymodbus 2>&1 | grep -E '^(Repository|Name|Version|Out-of-date|Votes)'"
} > "${P}_08_paquetes.txt"

{ hdr "09 GPU y CachyOS"
run "lspci -k | grep -A3 -E 'VGA|3D|Display'"
run "pacman -Q | grep -iE '^(nvidia|mesa |vulkan-radeon|cachyos-settings|cachyos-hooks|cachyos-kernel-manager|linux-cachyos)'"
run "cat /etc/lsb-release"
run "grep -E '^\[cachyos' /etc/pacman.conf"
} > "${P}_09_gpu_cachyos.txt"

{ hdr "10 Estabilidad"
run "journalctl --list-boots --no-pager | tail -5"
run "journalctl -b -1 -p warning --no-pager | grep -iE 'oom|out of memory|thermal|critical temp|throttl|mce|hardware error' | tail -30 || true"
run "journalctl -b 0 -p warning --no-pager | grep -iE 'oom|out of memory|thermal|critical temp|throttl|mce|hardware error' | tail -30 || true"
run uptime
} > "${P}_10_estabilidad.txt"
echo DONE; ls -la "$D"
