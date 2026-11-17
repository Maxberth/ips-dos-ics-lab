#!/usr/bin/env bash
# Ejecuta UNA corrida del experimento y deja todo en crudo. Sin sudo en el host.
#
# Uso: PROFILE=lab/config/profile_<plataforma>.env lab/harness/run_once.sh \
#        --scenario E1 --attack syn --run-profile piloto --rep 1 [--notes "texto"]
#   scenario : E0 (sin ataque, IPS router) | E1 (IPS router) | E2 (Suricata alert) | E3 (Suricata drop)
#   attack   : none | syn | udp | icmp | modbus
#   run-profile (lab/config/experiment.env): piloto | reduced | final
#
# Salidas (data/raw/):
#   runs.csv                         una fila por corrida (metadatos, versiones, hashes, estado)
#   runs/<run_id>/                   todo lo crudo de la corrida:
#     polls.csv          cada solicitud Modbus del SCADA (scada_poller.py)
#     ts_host.csv        1 Hz desde el host: domstats de las VMs, puertos espejo, RAM, Tctl
#     attack.txt         salida del generador (hping3 / modbus_flood.py) y contadores de v10 del atacante
#     fw_counters_{pre,post}.json, ips_counters_{pre,post}.json   contadores nftables
#     suricata_stats.jsonl, suricata_alerts_by_sid.txt            Suricata (eve.json, ventana de la corrida)
#     plc_pidstat.txt    CPU del proceso PLC dentro de la VM
#     capture_stats.txt  estadísticas de dumpcap (capturados/descartados)
#     pcap_counts_mir20.txt / _mir30.txt   conteos por segundo de la captura (tshark io,stat)
#   La captura .pcapng va a data/captures/ (fuera de Git) y su sha256 a data/captures/manifest.csv.
set -uo pipefail
source "$(dirname "$0")/../setup/lib.sh"
source "$REPO/lab/config/experiment.env"

SCEN=""; ATTACK=none; RP=""; REP=1; NOTES=""
while [ $# -gt 0 ]; do case $1 in
  --scenario) SCEN=$2; shift 2;; --attack) ATTACK=$2; shift 2;; --run-profile) RP=$2; shift 2;;
  --rep) REP=$2; shift 2;; --notes) NOTES=$2; shift 2;; *) echo "arg desconocido $1"; exit 1;; esac; done
RP=${RP:-$RUN_PROFILE_DEFAULT}
eval "WARM=\$${RP}_WARM ATT=\$${RP}_ATTACK COOL=\$${RP}_COOL"
[ "$SCEN" = E0 ] && ATTACK=none
case $SCEN in E0|E1) MODE=router;; E2) MODE=alert;; E3) MODE=drop;; *) echo "escenario?"; exit 1;; esac
TOTAL=$((WARM + ATT + COOL))
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)_${PLATFORM}_${SCEN}_${ATTACK}_${RP}_r${REP}"
OUT="$REPO/data/raw/runs/$RUN_ID"; mkdir -p "$OUT" "$REPO/data/captures"
CAP="$CACHE/captures/$RUN_ID.pcapng"; mkdir -p "$CACHE/captures"
STATUS=ok; FAIL=""
fail(){ STATUS=failed; FAIL="${FAIL:+$FAIL; }$*"; echo "FALLO: $*"; }
log(){ echo "[$(date -u +%T)] $*"; }
PLC=192.168.30.10

# --- 0. Salud: guardián y enfriamiento ---
for i in $(seq 600); do
  st=$(cut -d' ' -f1 "$LAB_RUN/STATE" 2>/dev/null)
  t=$(awk -F, 'END{print int($7)}' "$REPO/data/raw/guard/guard_${PLATFORM}_$(date -u +%Y%m%d).csv" 2>/dev/null)
  { [ "$st" = OK ] || [ "$st" = WARN ]; } && [ "${t:-99}" -le "$COOLDOWN_TARGET_TCTL" ] && break
  [ "$st" = ABORT ] && { echo "Guardián en ABORT"; exit 3; }
  [ $((i % 15)) = 1 ] && log "esperando guardián/enfriamiento: estado=$st Tctl=$t"
  sleep 2
done
T_START_TCTL=$t

# --- 1. Modo del IPS ---
CUR=$(cat "$LAB_RUN/ips_mode" 2>/dev/null)
if [ "$CUR" != "$MODE" ]; then "$REPO/lab/harness/ips_mode.sh" "$MODE" > "$OUT/ips_mode.txt" 2>&1 || fail "ips_mode $MODE"; fi
for vm in lab-attacker lab-fw lab-ips lab-plc lab-scada; do lab_ssh "$vm" true 2>/dev/null || fail "sin SSH a $vm"; done

# --- 2. Contadores previos ---
lab_ssh lab-fw "sudo nft -j list counters" > "$OUT/fw_counters_pre.json" 2>/dev/null || fail "contadores fw"
lab_ssh lab-ips "sudo nft -j list counters" > "$OUT/ips_counters_pre.json" 2>/dev/null || fail "contadores ips"
lab_ssh lab-attacker "ip -s -j link show v10" > "$OUT/attacker_v10_pre.json" 2>/dev/null
EVE_LINES0=$(lab_ssh lab-ips "sudo sh -c 'wc -l < /var/log/suricata/eve.json' 2>/dev/null || echo 0")

# --- 3. Arranque de mediciones ---
T0_NS=$(date +%s%N)
in_group wireshark dumpcap -q -i mir20 -i mir30 -s 128 -B 64 -a duration:$((TOTAL + 2)) -w "$CAP" \
  > "$OUT/capture_stats.txt" 2>&1 &
CAP_PID=$!
in_group libvirt python3 -I "$REPO/lab/harness/host_sampler.py" --seconds "$((TOTAL + 2))" --out "$OUT/ts_host.csv" &
HS_PID=$!
lab_ssh lab-scada "nohup python3 -I /opt/lab/scada_poller.py --plc $PLC --hz $SCADA_HZ --seconds $TOTAL --out /tmp/polls.csv > /tmp/poller.log 2>&1 &" || fail "poller"
lab_ssh lab-plc "nohup sh -c 'pidstat -h -u -r -p \$(pgrep -d, -f \"$PLC_PROCESS_PATTERN\" || echo 1) 1 $TOTAL' > /tmp/pidstat.txt 2>&1 &"
log "$RUN_ID: calentamiento ${WARM}s"
sleep "$WARM"

# --- 4. Ataque ---
case $ATTACK in
  syn)    ACMD="sudo timeout -s INT ${ATT} hping3 -S -p 502 --flood $PLC";;
  udp)    ACMD="sudo timeout -s INT ${ATT} hping3 --udp -p 502 --flood $PLC";;
  icmp)   ACMD="sudo timeout -s INT ${ATT} hping3 --icmp --flood $PLC";;
  modbus) ACMD="python3 -I /opt/lab/modbus_flood.py --plc $PLC --conns $MODBUS_CONNS --seconds $ATT --out /tmp/modbus_flood.json";;
  none)   ACMD="sleep $ATT";;
esac
T_ATT0_NS=$(date +%s%N)
log "ataque $ATTACK ${ATT}s: $ACMD"
lab_ssh lab-attacker "$ACMD" > "$OUT/attack.txt" 2>&1; ARC=$?
T_ATT1_NS=$(date +%s%N)
[ "$ATTACK" != none ] && [ $ARC -ne 0 ] && [ $ARC -ne 124 ] && [ $ARC -ne 130 ] && echo "rc=$ARC" >> "$OUT/attack.txt"
log "enfriamiento ${COOL}s"
sleep "$COOL"; sleep 2
wait $CAP_PID $HS_PID 2>/dev/null

# --- 5. Recogida ---
lab_ssh lab-attacker "ip -s -j link show v10" > "$OUT/attacker_v10_post.json" 2>/dev/null
[ "$ATTACK" = modbus ] && lab_ssh lab-attacker "cat /tmp/modbus_flood.json" >> "$OUT/attack.txt"
lab_ssh lab-fw "sudo nft -j list counters" > "$OUT/fw_counters_post.json" 2>/dev/null || fail "contadores fw post"
lab_ssh lab-ips "sudo nft -j list counters" > "$OUT/ips_counters_post.json" 2>/dev/null || fail "contadores ips post"
for i in $(seq 10); do lab_ssh lab-scada "pgrep -f scada_poller.py >/dev/null" || break; sleep 1; done
lab_ssh lab-scada "cat /tmp/polls.csv" > "$OUT/polls.csv" 2>/dev/null || fail "polls.csv"
lab_ssh lab-scada "cat /tmp/poller.log" > "$OUT/poller.log" 2>/dev/null
lab_ssh lab-plc "cat /tmp/pidstat.txt" > "$OUT/plc_pidstat.txt" 2>/dev/null
if [ "$MODE" != router ]; then
  lab_ssh lab-ips "sudo tail -n +$((EVE_LINES0 + 1)) /var/log/suricata/eve.json | jq -c 'select(.event_type==\"stats\") | {timestamp, uptime:.stats.uptime, decoder_pkts:.stats.decoder.pkts, ips:.stats.ips, nfq:.stats.capture, alert:.stats.detect.alert, flow_memcap:.stats.flow.memcap, tcp_syn:.stats.tcp.syn}'" \
    > "$OUT/suricata_stats.jsonl" 2>/dev/null || fail "suricata stats"
  lab_ssh lab-ips "sudo tail -n +$((EVE_LINES0 + 1)) /var/log/suricata/eve.json | jq -r 'select(.event_type==\"alert\") | \"\(.alert.signature_id) \(.alert.action)\"' | sort | uniq -c" \
    > "$OUT/suricata_alerts_by_sid.txt" 2>/dev/null
  lab_ssh lab-ips "systemctl is-active suricata-lab" > "$OUT/suricata_state_post.txt" 2>&1
fi

# --- 6. Conteos de la captura (segunda fuente) ---
ATT_SRC=192.168.10.100; SCADA=192.168.20.20
for ifc in mir20 mir30; do
  in_group wireshark tshark -r "$CAP" -q -z "io,stat,1,COUNT(frame)frame,\
COUNT(frame)frame.interface_name==\"$ifc\" && ip.src==$ATT_SRC && ip.dst==$PLC,\
COUNT(frame)frame.interface_name==\"$ifc\" && ip.src==$SCADA && ip.dst==$PLC && tcp.dstport==502,\
COUNT(frame)frame.interface_name==\"$ifc\" && ip.src==$PLC && ip.dst==$SCADA" \
    > "$OUT/pcap_counts_$ifc.txt" 2>&1 || fail "tshark $ifc"
done
CAP_SHA=$(sha256sum "$CAP" | cut -d' ' -f1); CAP_SIZE=$(stat -c %s "$CAP")
[ -s "$REPO/data/captures/manifest.csv" ] || echo "run_id,file,sha256,bytes,kept" > "$REPO/data/captures/manifest.csv"
KEEP=yes; [ "$CAP_SIZE" -gt $((CAPTURE_KEEP_MAX_MB * 1024 * 1024)) ] && KEEP=no
echo "$RUN_ID,$(basename "$CAP"),$CAP_SHA,$CAP_SIZE,$KEEP" >> "$REPO/data/captures/manifest.csv"
[ $KEEP = no ] && rm -f "$CAP"

# --- 7. Metadatos y fila de runs.csv ---
T_END_TCTL=$(awk -F, 'END{print $7}' "$REPO/data/raw/guard/guard_${PLATFORM}_$(date -u +%Y%m%d).csv" 2>/dev/null)
GMAX=$(awk -F, -v t0="$(date -u -d @$((T0_NS/1000000000)) +%FT%T)" '$1>=t0{print $10}' "$REPO/data/raw/guard/guard_${PLATFORM}_$(date -u +%Y%m%d).csv" 2>/dev/null | sort -u | paste -sd'|')
TMAX=$(awk -F, '$2=="host" && $4=="tctl_c"{if($5>m)m=$5}END{print m}' "$OUT/ts_host.csv")
RULES_SHA=$( [ "$MODE" != router ] && sha256sum "$CACHE/active.rules" | cut -c1-16 || echo -)
YAML_SHA=$(sha256sum "$REPO/lab/config/ips/suricata-lab.yaml" 2>/dev/null | cut -c1-16)
[ -s "$OUT/polls.csv" ] || fail "polls vacío"
validate=$(python3 -I "$REPO/lab/harness/validate_run.py" "$OUT" --attack "$ATTACK" --mode "$MODE" 2>&1 | tail -1)
H="$REPO/data/raw/runs.csv"
[ -s "$H" ] || echo "run_id,platform,scenario,attack,ips_mode,run_profile,rep,warm_s,attack_s,cool_s,t0_unix_ns,t_attack_start_ns,t_attack_end_ns,tctl_start_c,tctl_max_c,tctl_end_c,guard_states,status,validate,repo_commit,repo_dirty,rules_sha16,suricata_yaml_sha16,capture_sha256,notes" > "$H"
DIRTY=$(git -C "$REPO" status --porcelain -- lab | wc -l)
echo "$RUN_ID,$PLATFORM,$SCEN,$ATTACK,$MODE,$RP,$REP,$WARM,$ATT,$COOL,$T0_NS,$T_ATT0_NS,$T_ATT1_NS,$T_START_TCTL,$TMAX,$T_END_TCTL,${GMAX:-NA},$STATUS,\"$validate\",$(git -C "$REPO" rev-parse --short HEAD),$DIRTY,$RULES_SHA,$YAML_SHA,$CAP_SHA,\"${FAIL:+$FAIL; }$NOTES\"" >> "$H"
log "fin $RUN_ID status=$STATUS validate=$validate"
