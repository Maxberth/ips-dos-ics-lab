#!/usr/bin/env bash
# Estado de un vistazo: RAM, swap, temperatura, guardián y VMs del laboratorio. Sin sudo.
LAB_RUN="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/ips-lab"
echo "== $(date -u +%FT%TZ)"
free -m | sed -n '1,3p'
awk '/^some/{print "PSI memoria:", $2}' /proc/pressure/memory
sensors 2>/dev/null | grep -E 'Tctl|Composite' | sed 's/  */ /g'
echo "AC: $(cat /sys/class/power_supply/A*/online 2>/dev/null)"
echo "Guardián: $(systemctl --user is-active ips-lab-guard)  estado: $(cat "$LAB_RUN/STATE" 2>/dev/null || echo -)"
for f in PAUSE ABORT; do [ -e "$LAB_RUN/$f" ] && echo "  $f: $(cat "$LAB_RUN/$f")"; done
echo "VMs:"; sg libvirt -c 'virsh -c qemu:///system list --all' 2>/dev/null | grep -E 'lab-|Name' || echo "  (libvirt no accesible)"
ps -C qemu-system-x86_64 -o pid=,rss=,args= 2>/dev/null | awk '{n=$0; sub(/.*guest=/,"",n); sub(/,.*/,"",n); printf "  pid %s rss %d MiB %s\n",$1,$2/1024,n}'
systemctl show machine.slice -p MemoryCurrent -p MemoryHigh -p MemoryMax 2>/dev/null
