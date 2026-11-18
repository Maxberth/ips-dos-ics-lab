# Definiciones de métricas

Sirven para corregir el §3.4 del paper (observaciones 6, 7 y 8). Todas se calculan con `lab/analysis/summarize_runs.py` a partir de los datos crudos de `data/raw/runs/<run_id>/`, solo en la **ventana de ataque**: de `warm` a `warm + attack` segundos desde el inicio de la corrida (`t0`).

## Tráfico

- **Tráfico legítimo:** solicitudes Modbus/TCP "Read Holding Registers" (función 3, registros 0–3) de lab-scada (192.168.20.20) a lab-plc (192.168.30.10:502), a 10 Hz. Lo genera `lab/harness/scada_poller.py`, que registra cada solicitud.
- **Tráfico malicioso:** todo paquete IPv4 de lab-attacker (192.168.10.100) hacia el PLC (192.168.30.10).
  - `syn`: `hping3 -S -p 502 --flood 192.168.30.10`
  - `udp`: `hping3 --udp -p 502 --flood 192.168.30.10`
  - `icmp`: `hping3 --icmp --flood 192.168.30.10`
  - `modbus`: `modbus_flood.py --plc 192.168.30.10 --conns 8 --seconds <ataque>`. Son solicitudes Modbus válidas (función 3) enviadas sin esperar respuesta, por 8 conexiones TCP.

## Métricas

| Métrica | Definición | Fuente | Segunda fuente |
|---|---|---|---|
| **Disponibilidad** (principal) | % de solicitudes legítimas con respuesta Modbus válida (mismo transaction id, sin excepción) en ≤ 500 ms, dentro de la ventana de ataque | `polls.csv` | Respuestas Modbus contadas en la captura después del IPS (`pcap_counts.csv`, `plc_resp_payload`, VLAN 30) |
| **Pérdida de paquetes legítimos** | 1 − respondidas / enviadas (%) | `polls.csv` | Solicitudes en la VLAN 20 frente a la VLAN 30 en la captura |
| **Latencia** | RTT en ms entre el envío de la solicitud y la llegada completa de la respuesta, medido con el reloj monotónico de lab-scada. **Es RTT, no latencia de una vía**, y no necesita sincronizar relojes. Se reportan mediana, media, p95 y p99 | `polls.csv` | — (el ping solo se usa en las verificaciones) |
| **Rendimiento (throughput)** | bytes × 8 / (tiempo × 10⁶) en Mbps, **sin el ×100** del paper | contadores de interfaz (`ts_host.csv`, domstats) | captura |
| **Paquetes de ataque eliminados por el IPS** | (a) − (b): paquetes de ataque en la VLAN 20 (antes del IPS) menos en la VLAN 30 (después) | `pcap_counts.csv` | (c) `ips.blocked` de Suricata + (d) `queue_dropped` de NFQUEUE, frente al contador del firewall |
| **Descartes por regla** | `ips.blocked` (Suricata, `drop_reason.rules`) | `suricata_stats.jsonl` | captura |
| **Descartes por saturación** | `queue_dropped` de `/proc/net/netfilter/nfnetlink_queue`: paquetes que el kernel descartó porque la cola de Suricata estaba llena. No son detección | `nfq_pre.txt` y `nfq_post.txt` | captura y firewall |
| **Tasa de detección** (principal, por paquete) | alertas de la regla del escenario / paquetes de ataque **entregados a Suricata** (`detect.alert` / `decoder.pkts`). Se reporta junto a la fracción del ataque que llegó a Suricata | `suricata_stats.jsonl` | captura |
| **Paquetes de ataque efectivos** | `tx_packets` del kernel en la interfaz v10 de lab-attacker durante la corrida (incluye los RST que su kernel envía a los SYN-ACK) / segundos de ataque | `attacker_v10_{pre,post}.json` | hping3 (`attack.txt`) y el firewall (`c_v10_plc_*`) |
| **CPU del PLC** | CPU del proceso `openplc` dentro de lab-plc (`pidstat` 1 s). **Es CPU de una VM, no de un PLC físico** (obs. 24) | `plc_pidstat.txt` | `cpu.time` de la VM vista desde el host (`ts_host.csv`, domstats) |

## Notas

- El poller tiene una sola solicitud en vuelo, como un SCADA real: si una respuesta tarda (hasta 500 ms), la siguiente se retrasa. Por eso, bajo ataque hay menos de 10 solicitudes por segundo. Los huecos > 250 ms quedan en el veredicto de `validate_run.py`. La disponibilidad se calcula sobre las solicitudes realmente enviadas.
- La primera solicitud de cada corrida incluye la conexión TCP y la resolución ARP. No entra en la ventana de ataque, porque cae en el calentamiento.
- Sin pruebas estadísticas no se usa la palabra "significativo" (obs. 23). Con 10 repeticiones se reportan media ± DE e IC 95 % (t de Student, n−1 gl).

## Complemento (A24): respuestas válidas respecto a las solicitudes programadas
El poller es de lazo cerrado y deja de emitir solicitudes mientras espera respuestas (timeout 0,5 s), así que en celdas saturadas emite menos de las 600 programadas (10 Hz × 60 s). Además de la disponibilidad (respondidas / emitidas), se reporta **respondidas válidas / programadas** (`polls_ok` / 600) y el número de solicitudes emitidas (`polls_attack_window`). Ambas salen de `polls.csv` (`lab/analysis/analisis_final.py`, columnas `resp_vs_programadas_pct` y `polls_emitidas_pct`).

