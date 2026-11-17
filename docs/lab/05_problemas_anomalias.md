# Problemas y anomalías

Todo lo raro, aunque se resuelva: síntoma, hipótesis, evidencia y resolución.

## A1. Prueba de scope con `bytearray` no reservó memoria real (resuelta)
- **Síntoma:** un scope con `MemoryMax=256M` que crea `bytearray(600 MiB)` terminó con exit 0.
- **Causa:** `bytearray(n)` usa páginas a cero que el kernel no asigna hasta escribirlas.
- **Resolución:** la prueba escribe los datos (`b'\x01'*600MiB`) y el scope muere con exit 137. Evidencia: `docs/lab/logs/P04_pruebas_guardian.txt`.

## A2. Las simulaciones del guardián escribieron en `data/raw/` (resuelta)
- **Síntoma:** filas con umbrales simulados en `data/raw/guard/guard_laptop-dev_*.csv`.
- **Resolución:** se borró el archivo y `guard.sh` acepta `GUARD_CSV` para que las simulaciones escriban fuera de `data/raw`.

## A3. `docker network ls` arrancó dockerd por socket durante P02
- Ver `docs/lab/contenedores_apagados.md`. `root_setup.sh` lo detiene.

## A4. Las VMs entraban en bucle de reinicio justo después de GRUB (resuelta)
- **Síntoma:** la consola serie de lab-fw mostraba solo `Booting 'Debian GNU/Linux'` en bucle (unas 2 veces por segundo). El disco nunca se escribió (196 KiB).
- **Descartado, con prueba:** `hard_limit`, `cputune`, el modelo de CPU (host-passthrough, host-model EPYC-Milan) y la RAM (512 MiB arranca en QEMU directo).
- **Causa:** sin tarjeta de vídeo. `virt-install --graphics none` no crea dispositivo de vídeo, y el kernel cloud de Debian 13 (6.12.117) se reinicia al arrancar sin él. Reproducido con QEMU directo: `-vga none` provoca 40 reinicios en 15 s; con VGA arranca hasta `login:`.
- **Resolución:** `create_vm.sh` añade `--video vga`. No afecta a las mediciones.

## A5. El firewall del host (ufw) bloquea el DHCP de la red NAT de libvirt (evitada)
- **Síntoma:** la NIC `nat` de lab-fw no obtuvo IPv4 y cloud-init no pudo instalar paquetes.
- **Causa:** `ufw` está activo en laptop-dev y descarta el tráfico entrante desde `virbr-labi` (DHCP, DNS y reenvío).
- **Resolución sin tocar el firewall del usuario:** las VMs instalan paquetes a través de la conexión SSH del host: un proxy SOCKS inverso (`ssh -R 1080`) para apt, y para OpenPLC un proxy HTTP local (`lab/setup/http_proxy.py`, solo en 127.0.0.1) que llega por `ssh -R 3128`. Ver D12. La red NAT `lab-install` deja de ser necesaria.

## A6. `sg` no existe en CachyOS (resuelta)
- **Síntoma:** `sudo: sg: command not found` en el paso 8 de `root_setup.sh`.
- **Resolución:** libvirt autoriza por polkit según `/etc/group`, así que `virsh` funciona sin reiniciar la sesión. Para `dumpcap` (grupo wireshark) se usa `newgrp`, que sí existe (setuid). Ver D13.

## A7. Mirror de CachyOS con 404 para rdma-core (sin efecto)
- pacman no pudo bajar `rdma-core-65.0-1.1` de dos mirrors (404), pero lo instaló desde otro. `pacman -Q rdma-core` = 65.0-1.1 y `pacman -Qk` no muestra archivos faltantes. Evidencia: `docs/lab/logs/P05_verificacion_host_laptop-dev.txt`.

## A8. cloud-init queda en `status: error` en lab-fw
- Ocurrió porque cloud-init intentó instalar paquetes sin red (A5). La VM funciona y los paquetes se instalaron después por el proxy. Las VMs creadas después ya no piden paquetes a cloud-init.

## A9. Primera versión de check_chain contaba líneas en vez de paquetes (resuelta)
- **Síntoma:** "ecos que llegan al PLC" dio 6/5 con alert y 1/5 con drop.
- **Evidencia:** con la captura completa en lab-plc, el modo drop mostró `0 packets captured`, y eve.json registró los 5 ecos con `action: blocked`.
- **Causa:** `wc -l` contaba también una línea que no era un paquete. Ahora se cuentan solo las líneas `ICMP echo request`. Con la corrección: alert 5/5 y drop 0/5.
- El chequeo de OVS confundía `link/ether` con una interfaz `eth`; ahora mira solo el nombre de la interfaz.

## A10. El post-proceso de la captura agotó la RAM del host y systemd-oomd mató la app de Claude (resuelta; error del arnés)
- **Cuándo:** 2026-11-17, corrida `20261117T184920Z_laptop-dev_E1_syn_piloto_r1` (E1, SYN flood, perfil piloto, 30 s).
- **Qué estaba corriendo:** el ataque terminó bien (hping3: 4 038 649 SYN en 30 s, unos 134 kpps; captura de 1,49 GB con 15 919 545 tramas). Después, `run_once.sh` contaba la captura con `tshark -z io,stat`, sin límite de memoria y dentro del scope de la app de Claude.
- **Síntoma:** desde las 18:50:29 UTC, MemAvailable bajó, el swap creció hasta +6,7 GiB y el PSI llegó a 22 %. El guardián pasó a ABORT a las 18:51:07 (swap +3257 MiB) y destruyó las 5 VMs, pero tshark no estaba bajo su control. A las 18:52:52, `systemd-oomd` mató el scope `app-com.anthropic.Claude-*` (11,1 GiB de swap): se cortó la sesión de trabajo unos 55 minutos. La sesión gráfica del usuario y el resto de aplicaciones siguieron vivas.
- **Causa:** tshark conserva estado por cada trama. Con 16 M de tramas no cabe en la RAM de laptop-dev. El post-proceso no estaba en un scope con `MemoryMax`, y el guardián solo controlaba las VMs.
- **Correcciones:**
  1. `lab/harness/pcap_count.py`: lee la pcapng en streaming (bloque a bloque, memoria constante) y separa por interfaz. Validado contra la corrida E0: 450 solicitudes y 450 respuestas por VLAN, igual que el sondeo SCADA, y totales iguales a dumpcap (1361/1362).
  2. Captura, muestreo del host y conteo corren en scopes `ips-lab-job-*` con `MemoryMax` y sin swap (`limited-run.sh`). Si se pasan, solo muere ese scope.
  3. En ABORT, el guardián también detiene los scopes `ips-lab-job-*`.
  4. Captura con snaplen 64 y buffer de 256 MiB. En esta corrida dumpcap descartó 4,5 % en mir20 y 1,6 % en mir30. Quedan declarados en `capture_stats.txt` y en la validación.
- **Qué se rehízo:** el conteo de la captura de esa corrida con `pcap_count.py` dentro de un scope de 1 GiB. Los demás datos crudos de la corrida (sondeo SCADA, contadores, hping3, muestreo del host) ya estaban guardados y no se tocaron. Su fila en `runs.csv` se escribe a mano con `status=partial` y la explicación.

## A11. Con una sola cola NFQUEUE, el IPS se satura y descarta tráfico legítimo (hallazgo; corrección en D18)
- **Corrida:** `20261117T190317Z_laptop-dev_E3_syn_piloto_r1` (E3 drop, SYN flood, piloto 30 s, 1 cola NFQUEUE).
- **Cuadre de fuentes (el ataque se contabiliza entero):**
  - firewall `c_v10_plc_tcp502`: 4 467 006 SYN nuevos aceptados;
  - captura VLAN 20 (antes del IPS): 4 455 209 (dumpcap descartó 0,27 %);
  - Suricata `decoder.pkts`: 1 752 919, de ellos `ips.blocked` 1 747 408 (`drop_reason.rules` 1 732 555, `stream_error` 14 853);
  - kernel `/proc/net/netfilter/nfnetlink_queue`, cola 0: `queue_dropped` 2 714 095.
  - 1 752 920 (entregados a Suricata) + 2 714 095 (desbordamiento) = 4 467 015, frente a 4 467 006 del firewall: diferencia de 9 paquetes.
  - Captura VLAN 30 (después del IPS): 3 072 paquetes de ataque.
- **Interpretación:** solo el 39 % de lo eliminado lo descartó una regla. El 61 % lo descartó el kernel porque la cola se llenó: Suricata, con un hilo de recepción, procesó unos 58 kpps frente a unos 149 kpps de ataque. Ese desbordamiento es indiscriminado: también se perdieron solicitudes Modbus legítimas (49 solicitudes en la VLAN 20 frente a 22 en la VLAN 30). La disponibilidad del SCADA bajó al 64,9 % (54 timeouts), peor que en E1 sin IPS (99,7 %, RTT p95 249 ms).
- **No se debe presentar como "bloqueo del IPS" sin separar** `rules` de `queue_dropped`. El arnés ahora guarda `nfq_pre.txt` y `nfq_post.txt` y el resumen reporta `nfq_queue_dropped`.
- **Error de cálculo propio detectado:** un primer cálculo rápido de disponibilidad con awk dio 0/299 en la ventana de ataque porque mezclaba columnas. El cálculo correcto (`summarize_runs.py`) da 298/299 para E1. No se usó ningún valor del cálculo erróneo.

## A12. `runs.csv` con saltos de línea dentro de un campo (resuelta)
- `host_sampler.py` escribía CSV con `\r\n`. awk arrastraba el `\r` al campo `tctl_max_c` y partía la fila.
- Todos los escritores CSV usan ahora `lineterminator="\n"`, y `run_once.sh` quita los `\r`. Se reparó `runs.csv` sin cambiar ningún valor medido; solo se quitaron los `\r`. En la fila E0 se reescribió `validate` con el validador corregido (A10), lo que queda anotado en `notes`.

## A13. `queue num 0-1 fanout` no repartió la carga (resuelta)
- **Corrida:** `20261117T190614Z_laptop-dev_E3_syn_piloto_r1`. La cola 0 recibió 3 558 paquetes y la cola 1, 2 856 466, de los que desbordaron 1 612 465.
- **Causa:** en nftables, `fanout` elige la cola según la CPU que procesa el paquete. Todo el flood entra por la misma vCPU. Sin `fanout`, el reparto es por hash de flujo, y hping3 cambia el puerto de origen en cada paquete.
- **Aun así:** con 2 hilos, Suricata procesó 2,86 M paquetes (antes 1,75 M) y la disponibilidad del SCADA pasó del 64,9 % al 93,3 %.

## A14. El balanceo de NFQUEUE no reparte un flood de una sola IP (limitación; se mantiene D18)
- **Corrida:** `20261117T190746Z_laptop-dev_E3_syn_piloto_r1`, con `queue num 0-1` sin fanout. La cola 0 recibió 0 paquetes y la cola 1, 2 872 742 (1 626 338 desbordados).
- **Causa:** el balanceo de NFQUEUE calcula el hash con las direcciones IP de origen y destino, no con los puertos. Un atacante con una sola IP (L5) cae siempre en la misma cola.
- **Consecuencia:** con un solo origen, el techo del IPS es una cola: Suricata procesó unos 95 kpps (2,87 M en 30 s) frente a unos 150 kpps de ataque en laptop-dev. El exceso lo descarta el kernel sin distinguir el tráfico legítimo.
- **Variabilidad:** dos corridas casi iguales (D18) dieron 93,3 % y 88,5 % de disponibilidad del SCADA. Hacen falta repeticiones (perfil final ×10) para dar intervalos.
- Se mantienen las 2 colas: no perjudican y ayudan con orígenes distintos. Para el paper: declarar el techo de rendimiento del IPS virtual y reportar `queue_dropped` aparte de los descartes por regla. En pc-miguel hay que medir el techo propio.
