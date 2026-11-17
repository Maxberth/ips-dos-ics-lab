#!/usr/bin/env bash
# Configura una VM ya creada (create_vm.sh) según su rol. Idempotente. Se ejecuta desde el host por SSH.
# Uso: PROFILE=lab/config/profile_<plataforma>.env lab/setup/provision_vm.sh lab-fw
set -euo pipefail
source "$(dirname "$0")/lib.sh"
VM="${1:?vm}"; ROLE=$(vm_field "$VM" 2)
IP=$(mgmt_ip "$VM")
for i in $(seq 120); do lab_ssh "$VM" true 2>/dev/null && break; sleep 2; done
echo "== $VM ($ROLE): esperando a cloud-init"
lab_ssh "$VM" "cloud-init status --wait >/dev/null 2>&1; cloud-init status --long | head -3; test -f /var/lib/cloud/lab-ready"

# Común: directorio de scripts y sin offloads en las interfaces de datos (capturas y Suricata ven paquetes reales).
lab_ssh "$VM" "sudo install -d -o lab -g lab /opt/lab"
lab_scp "$REPO/lab/harness/scada_poller.py" "$REPO/lab/harness/modbus_flood.py" "lab@$IP:/opt/lab/"
lab_ssh "$VM" "sudo tee /etc/systemd/system/lab-offload.service >/dev/null" <<'EOF'
[Unit]
Description=IPS lab: desactiva offloads en interfaces de datos
After=network-online.target
Wants=network-online.target
[Service]
Type=oneshot
ExecStart=/bin/sh -c 'for i in v10 v20 v30; do [ -e /sys/class/net/$i ] && ethtool -K $i gro off lro off tso off gso off tx off rx off 2>/dev/null; done; true'
RemainAfterExit=yes
[Install]
WantedBy=multi-user.target
EOF
lab_ssh "$VM" "sudo systemctl daemon-reload && sudo systemctl enable --now lab-offload.service >/dev/null 2>&1 || true"

case $ROLE in
  FW)
    lab_scp "$REPO/lab/config/fw/nftables-e1.conf" "lab@$IP:/tmp/"
    lab_ssh "$VM" "echo net.ipv4.ip_forward=1 | sudo tee /etc/sysctl.d/90-lab.conf >/dev/null && sudo sysctl -q --system \
      && sudo install -m 0755 /tmp/nftables-e1.conf /etc/nftables.conf && sudo systemctl enable --now nftables >/dev/null 2>&1 \
      && sudo nft -f /etc/nftables.conf && echo fw ok"
    ;;
  IPS)
    lab_scp "$REPO/lab/config/ips/nftables-router.conf" "$REPO/lab/setup/make_suricata_yaml.py" "lab@$IP:/tmp/"
    lab_ssh "$VM" "echo net.ipv4.ip_forward=1 | sudo tee /etc/sysctl.d/90-lab.conf >/dev/null && sudo sysctl -q --system \
      && sudo install -m 0755 /tmp/nftables-router.conf /etc/nftables.conf && sudo systemctl enable --now nftables >/dev/null 2>&1 \
      && sudo nft -f /etc/nftables.conf \
      && sudo systemctl disable --now suricata >/dev/null 2>&1; sudo python3 -I /tmp/make_suricata_yaml.py /etc/suricata/suricata.yaml /etc/suricata/suricata-lab.yaml \
      && sudo touch /etc/suricata/rules/lab.rules && echo ips ok"
    lab_ssh "$VM" "cat /etc/suricata/suricata-lab.yaml" > "$REPO/lab/config/ips/suricata-lab.yaml"
    lab_ssh "$VM" "cat /etc/suricata/suricata.yaml" > "$CACHE/suricata-default-$VM.yaml"
    echo "router" > "$LAB_RUN/ips_mode"
    ;;
  PLC)
    lab_scp "$REPO/lab/config/plc/tank_sim.st" "$REPO/lab/setup/plc_install_openplc.sh" "lab@$IP:/tmp/"
    echo "OpenPLC se instala aparte: lab_ssh lab-plc 'bash /tmp/plc_install_openplc.sh' (compila; tarda)."
    ;;
  SCADA|ATTACKER) : ;;
esac
lab_ssh "$VM" "uname -r; . /etc/os-release; echo \$PRETTY_NAME; ip -br addr | grep -v '^lo'; ip route"
