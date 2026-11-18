#!/usr/bin/env bash
# Pone lab-ips en un modo reproducible. La ruta e interfaces no cambian entre modos (obs. 10).
#   router  : nftables sin cola, Suricata detenido                  (E0, E1)
#   alert   : NFQUEUE 0 + Suricata con lab.rules en "alert"          (E2)
#   drop    : NFQUEUE 0 + Suricata con lab.rules en "drop"           (E3)
#   test-alert / test-drop : igual, pero con test.rules (prueba de P09)
#   calib-drop : como drop (lab.rules) pero con eve.json completo de alertas y drops, solo calibraciones (A23)
#   calib-alert : como alert (lab.rules) pero con eve.json completo de alertas, solo para calibraciones (A22); no entra en la tanda
# Uso: PROFILE=... lab/harness/ips_mode.sh <modo>
set -euo pipefail
source "$(dirname "$0")/../setup/lib.sh"
MODE="${1:?router|alert|drop|test-alert|test-drop|calib-alert|calib-drop}"
CFG="$REPO/lab/config/ips"
case $MODE in
  router) ACTION=""; SET="";;
  alert|drop) ACTION=$MODE; SET=lab;;
  test-alert) ACTION=alert; SET=test;;
  test-drop) ACTION=drop; SET=test;;
  calib-alert) ACTION=alert; SET=lab;;
  calib-drop) ACTION=drop; SET=lab;;
  *) echo "modo desconocido"; exit 1;;
esac
# Corridas (alert/drop): eve solo con stats; pruebas (test-*): eve con alert y drop (D17).
case $MODE in test-*|calib-*) YAML=suricata-lab.yaml;; *) YAML=suricata-lab-measure.yaml;; esac
lab_scp "$CFG/nftables-router.conf" "$CFG/nftables-nfq.conf" "lab@$(mgmt_ip lab-ips):/tmp/"
lab_scp "$CFG/$YAML" "lab@$(mgmt_ip lab-ips):/tmp/suricata-lab.yaml"
if [ -n "$SET" ]; then
  sed "s/^ACTION /$ACTION /" "$CFG/rules/$SET.rules.in" > "$CACHE/active.rules"
  lab_scp "$CACHE/active.rules" "lab@$(mgmt_ip lab-ips):/tmp/lab.rules"
fi
lab_ssh lab-ips "MODE=$MODE SET='$SET' bash -s" <<'EOS'
set -euo pipefail
sudo install -m 0644 /tmp/suricata-lab.yaml /etc/suricata/suricata-lab.yaml
if [ "$MODE" = router ]; then
  sudo systemctl stop suricata-lab 2>/dev/null || true
  sudo nft -f /tmp/nftables-router.conf
else
  sudo install -m 0644 /tmp/lab.rules /etc/suricata/rules/lab.rules
  sudo suricata -T -c /etc/suricata/suricata-lab.yaml -S /etc/suricata/rules/lab.rules -q 0 >/tmp/suricata-T.txt 2>&1 \
    || { cat /tmp/suricata-T.txt; exit 3; }
  sudo systemctl stop suricata-lab 2>/dev/null || true
  sudo systemctl reset-failed suricata-lab 2>/dev/null || true
  # Suricata primero, la cola después: así no hay ventana en que la cola exista sin lector.
  LOG=/var/log/suricata/suricata.log; n0=$(sudo sh -c "wc -l < $LOG" 2>/dev/null || echo 0)
  sudo systemd-run --unit=suricata-lab --property=Restart=no \
    /usr/bin/suricata -c /etc/suricata/suricata-lab.yaml -S /etc/suricata/rules/lab.rules -q 0 -q 1 --pidfile /run/suricata-lab.pid
  ok=0; for i in $(seq 90); do sudo tail -n +$((n0+1)) $LOG 2>/dev/null | grep -q 'Engine started' && { ok=1; break; }; sleep 1; done
  [ $ok = 1 ] || { echo "Suricata no arrancó en 90 s"; sudo tail -20 $LOG; exit 4; }
  sudo nft -f /tmp/nftables-nfq.conf
fi
echo "ips_mode=$MODE suricata=$(systemctl is-active suricata-lab 2>/dev/null || true) rules_sha256=$( [ -f /etc/suricata/rules/lab.rules ] && sha256sum /etc/suricata/rules/lab.rules | cut -c1-16 )"
EOS
echo "$MODE" > "$LAB_RUN/ips_mode"
