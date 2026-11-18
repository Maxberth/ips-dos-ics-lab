# Limitaciones

Cada limitación con su impacto sobre la validez del estudio.

## L1. Laboratorio virtual en una sola máquina
Todo corre en una sola máquina física: VMs con QEMU/KVM y un switch Open vSwitch. El "PLC" es OpenPLC en una VM y su CPU no es la de un PLC físico. El switch es virtual: mide segmentación y aislamiento VLAN, no el hardware de un switch industrial. Debe declararse en el paper (obs. 4, 24, 25).

## L2. Desviaciones de software respecto al paper
| Paper | Laboratorio | Motivo |
|---|---|---|
| Kali Linux (atacante) | Debian 13 con `hping3` y `scapy` | Misma herramienta, una sola imagen base (D8) |
| pfSense 2.8.0-1 | nftables en Debian 13 | 100 % libre y reproducible por script (D3) |
| Ubuntu Server (Suricata, OpenPLC, SCADA) | Debian 13 | Una sola imagen base (D8) |
| HMI/SCADA gráfico | Cliente `pymodbus` a 10 Hz | Medición por solicitud y RAM (D4) |
| PLC en 192.168.1.10 | PLC en 192.168.30.10 (VLAN 30) | Topología Purdue de P06; la LAN de casa del host es 192.168.1.0/24 |

## L3. Una sola plataforma física: laptop-dev
Desde el 2026-11-18 la única plataforma del estudio es `laptop-dev` (Ryzen 5 6600H, 14,8 GiB), una laptop, y no se usarán pc-miguel ni pc-alem. Los números del paper salen de sus datos. Límites que deben declararse: una sola máquina y una sola réplica de plataforma (sin comprobar si los resultados se repiten en otro hardware); sus VMs tienen menos RAM (perfil `laptop-dev`); una laptop puede bajar la frecuencia por temperatura (en la tanda real no hubo throttling, A19 y figura `r7_thermal`); el RTT y la disponibilidad dependen de ese hardware y no se extrapolan a un PLC físico (L1). Las corridas piloto y reducidas anteriores a la tanda real son de calibración y no entran en tablas ni figuras del paper.

## L4. Límites de RAM y temperatura condicionan las corridas
El guardián pausa (PAUSE) o aborta (ABORT) según la RAM disponible, la presión de memoria, el swap, la temperatura y, en laptop-dev, si el cargador está conectado. Puede alargar las corridas (enfriamiento entre repeticiones) y obliga a perfiles de corrida más cortos si el equipo no aguanta el perfil `final`.

## L5. Un solo atacante con IP fija
El atacante usa una sola IP (sin `--rand-source`), así que las reglas con `track by_src` funcionan. Un DDoS distribuido con muchas IPs de origen queda fuera del alcance del estudio.

## L6. Open vSwitch arrastra DPDK
En CachyOS, el paquete `openvswitch` instala `dpdk` (unos 577 MiB) como dependencia. El laboratorio no usa DPDK: OVS corre en el kernel (datapath `system`). Solo ocupa disco.

## L7. Siete corridas de laptop-dev con arranque frío y campos térmicos vacíos (A20)
Siete corridas finales (E3 ICMP r3, r5, r6, r7, r8, r9 y E1 ICMP r4) perdieron `tctl_start_c`, `tctl_end_c` y/o `guard_states` en `runs.csv` por el fallo de fechas descrito en A20. Seis de ellas esperaron ~20 min antes de empezar, así que arrancaron con la laptop más fría (38–53 °C) que las demás corridas del perfil `final` (54–63 °C). Sus mediciones son completas y válidas. Esos campos quedan vacíos (no se estiman). Como referencia se dejan muestras reales del guardián en `data/processed/runs_guard_muestras_laptop-dev_final.csv` y el Tctl por segundo en `ts_host.csv`. Comparadas con las demás ICMP, E1 no mostró diferencia; en E3 hay una disponibilidad del SCADA algo menor (74 % frente a 82 %), con rangos solapados y sin separar el efecto del arranque frío del tiempo transcurrido, por lo que no se concluye nada y se declara. No se repitieron.

## L8. La regla Modbus (rev 3) produce falsos positivos sobre el SCADA y no impide la caída del PLC (A23, D22)
En modo `drop`, la regla 1000004 (umbral de 20 segmentos con datos por segundo y por origen) descartó paquetes legítimos del SCADA en las 4 corridas de calibración con `eve.json` completo (133–162 paquetes TCP SCADA→PLC:502 por corrida, en 24–30 flujos de reconexión), a partir de los ~29 s de un ataque de 30 s, es decir al final y en el enfriamiento. Por eso, en E3, la disponibilidad no vuelve al 100 % justo después del ataque (~92 %). No se ha demostrado que explique la pérdida durante el ataque. Además, el flood Modbus sigue tumbando OpenPLC al terminar (E3: 6/10; E1 y E2: 10/10). Los resultados de E3 incluyen ese efecto: son algo pesimistas para el IPS en la recuperación. La regla no se recalibró (D22) para mantener una sola versión de reglas en las 130 corridas; los falsos positivos de la tanda no se pueden cuantificar porque `eve.json` solo guardó estadísticas.

