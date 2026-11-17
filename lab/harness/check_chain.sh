#!/usr/bin/env bash
# Verificaciones de la cadena antes de medir (P06, P08, P09, P10). Cada prueba: CUMPLE / NO CUMPLE.
# Salida en docs/lab/logs/P09_check_chain_<plataforma>.txt. Sin sudo en el host.
# Uso: PROFILE=... lab/harness/check_chain.sh
set -uo pipefail
source "$(dirname "$0")/../setup/lib.sh"
LOG="$REPO/docs/lab/logs/P09_check_chain_${PLATFORM}.txt"
exec > >(tee "$LOG") 2>&1
NOK=0
check(){ local name=$1; shift; if "$@" >/tmp/ips-lab-check.out 2>&1; then echo "CUMPLE    $name"; else echo "NO CUMPLE $name"; sed 's/^/          /' /tmp/ips-lab-check.out | tail -5; NOK=$((NOK+1)); fi; }
ncheck(){ local name=$1; shift; if "$@" >/tmp/ips-lab-check.out 2>&1; then echo "NO CUMPLE $name (debía fallar)"; NOK=$((NOK+1)); else echo "CUMPLE    $name"; fi; }
echo "# check_chain $(date -u +%FT%TZ) plataforma=$PLATFORM repo=$(git -C "$REPO" rev-parse --short HEAD)"

echo "## P06 red y aislamiento"
check "ovs-ot sin puertos físicos (enp2s0/wlan0/tailscale0)" sh -c "! ip -o link show master ovs-system | grep -qE 'enp|wlan|tailscale|eth'"
check "el host no tiene IP en VLAN 10/20/30" sh -c "! ip -4 -br addr | grep -qE '192\.168\.(10|20|30)\.'"
ssh_all(){ for v in lab-attacker lab-fw lab-ips lab-plc lab-scada; do lab_ssh "$v" true || return 1; done; }
check "SSH de gestión a las 5 VMs" ssh_all
ncheck "aislamiento: atacante (VLAN 10) no llega a SCADA por capa 2 (ARP directo)" lab_ssh lab-attacker "sudo arping -c 2 -w 3 -I v10 192.168.20.20"
ncheck "aislamiento: SCADA (VLAN 20) no llega al PLC por capa 2" lab_ssh lab-scada "sudo arping -c 2 -w 3 -I v20 192.168.30.10"
check  "misma VLAN: SCADA ve al IPS (192.168.20.2)" lab_ssh lab-scada "ping -c 2 -W 2 192.168.20.2"
ncheck "VMs sin ruta por defecto (sin Internet)" lab_ssh lab-attacker "ping -c 1 -W 2 1.1.1.1"
ncheck "atacante no alcanza la gestión de otra VM (VLAN 99)" lab_ssh lab-attacker "ping -c 1 -W 2 192.168.99.13"
ncheck "atacante no alcanza la gestión vía firewall (VLAN 10 -> 99)" lab_ssh lab-attacker "ping -c 1 -W 2 -I v10 192.168.99.13"

echo "## P08/P09 ruta con el IPS en modo router"
"$REPO/lab/harness/ips_mode.sh" router >/dev/null
check "atacante -> fw (192.168.10.1)" lab_ssh lab-attacker "ping -c 2 -W 2 192.168.10.1"
check "atacante -> PLC a través de fw e ips" lab_ssh lab-attacker "ping -c 3 -W 2 192.168.30.10"
check "SCADA -> PLC a través del ips" lab_ssh lab-scada "ping -c 3 -W 2 192.168.30.10"
check "SCADA lee Modbus del PLC (10 lecturas)" lab_ssh lab-scada "python3 -I /opt/lab/scada_poller.py --seconds 1 --out /tmp/chk.csv && awk -F, 'NR>1&&\$5==1{n++}END{exit !(n==10)}' /tmp/chk.csv"
lab_ssh lab-attacker "ping -c 3 -W 2 192.168.30.10" | tail -1 | sed 's/^/          RTT ping atacante->PLC (router): /'

echo "## P09 NFQUEUE y prueba de drop real (ping 1 pps x 5 desde SCADA)"
count_plc_icmp(){ lab_ssh lab-plc "sudo timeout 9 tcpdump -ni v30 -c 100 'icmp[icmptype]==icmp-echo and src 192.168.20.20' 2>/dev/null | wc -l" & sleep 2; lab_ssh lab-scada "ping -c 5 -i 1 -W 1 192.168.30.10 >/dev/null 2>&1; true"; wait; }
"$REPO/lab/harness/ips_mode.sh" test-alert > /tmp/ips-lab-mode.out 2>&1 || { cat /tmp/ips-lab-mode.out; }
check "suricata -T valida config y reglas (test-alert)" grep -q 'ips_mode=test-alert suricata=active' /tmp/ips-lab-mode.out
n_alert=$(count_plc_icmp | tail -1)
echo "          ecos que llegan al PLC con regla alert: $n_alert de 5"
check "alert: llegan los 5 ecos al PLC" test "$n_alert" = 5
"$REPO/lab/harness/ips_mode.sh" test-drop > /tmp/ips-lab-mode.out 2>&1 || cat /tmp/ips-lab-mode.out
n_drop=$(count_plc_icmp | tail -1)
echo "          ecos que llegan al PLC con regla drop: $n_drop de 5"
check "drop: no llega ningún eco al PLC" test "$n_drop" = 0
check "eve.json registra el bloqueo (sid 1000099, action blocked)" lab_ssh lab-ips "sudo jq -r 'select(.event_type==\"alert\" and .alert.signature_id==1000099) | .alert.action' /var/log/suricata/eve.json | grep -q blocked"
check "SCADA sigue leyendo Modbus con Suricata en línea" lab_ssh lab-scada "python3 -I /opt/lab/scada_poller.py --seconds 1 --out /tmp/chk.csv && awk -F, 'NR>1&&\$5==1{n++}END{exit !(n==10)}' /tmp/chk.csv"
lab_ssh lab-ips "sudo systemctl stop suricata-lab"
ncheck "fail-closed: sin Suricata la cola corta el tráfico" lab_ssh lab-scada "ping -c 2 -W 2 192.168.30.10"
"$REPO/lab/harness/ips_mode.sh" router >/dev/null
check "tras volver a modo router el tráfico se restaura" lab_ssh lab-scada "ping -c 2 -W 2 192.168.30.10"

echo "## Resultado: $NOK pruebas en NO CUMPLE"
exit $NOK
