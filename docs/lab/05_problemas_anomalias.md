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

## A15. El Modbus/TCP flood sin IPS (E1) tumbó el runtime de OpenPLC; 9 corridas posteriores midieron un PLC caído
- **Corrida:** `20261117T191113Z_laptop-dev_E1_modbus_piloto_r1`. El atacante abrió 8 conexiones Modbus y escribió unos 9,5 M de solicitudes en 30 s. El SCADA tuvo respuesta hasta la solicitud 352. A partir de la 353 (≈ 35 s desde t0, al terminar el ataque) recibió `ConnectionRefused`.
- **Estado del PLC:** el proceso `core/openplc` quedó zombi (`<defunct>`), sin rastro en dmesg. `openplc.service` seguía `active` porque systemd vigila el script `start_openplc.sh`, no el runtime.
- **Impacto:** las 9 corridas siguientes de la matriz piloto (E3 icmp, E1 icmp, E3 udp, E2 modbus, E2 udp, E2 syn, E3 modbus, E2 icmp y E1 syn, de 19:12 a 19:24 UTC) midieron un PLC caído: disponibilidad 0 % y casi todo `ConnectionRefused`. Quedan en `data/raw` con `status=failed` y la explicación en `notes`. **No son mediciones de esos escenarios.**
- **Es también un hallazgo:** sin IPS, un Modbus flood de una sola fuente tumba el runtime de OpenPLC (commit b5d41356). Hay que comprobar si se repite (E1 modbus ×10) y si el IPS lo evita (E3 modbus).
- **Corrección del arnés:** antes de cada corrida, `run_once.sh` comprueba el PLC con 1 s de sondeo (≥ 8/10 respuestas). Si no responde, reinicia OpenPLC y lo anota. Al final de la corrida vuelve a comprobarlo y guarda `alive_after=yes|no` en `plc_health.txt`. "PLC caído tras la corrida" pasa a ser un resultado del escenario.
- **Lección:** el validador debe tratar como FALLO una disponibilidad del 0 % con `ConnectionRefused` desde el inicio, no como un resultado.

## A16. En modo alert (E2), Suricata descartó el Modbus flood por su política de excepciones, no por una regla
- **Corridas:** `20261117T192925Z_…_E2_modbus` y `20261117T193310Z_…_E3_modbus`. El atacante solo escribió unas 18 500 solicitudes (617/s) frente a ~9,5 M en E1. Suricata: `applayer_error` 7 (uno por conexión), `flow_drop` 222, `rules` 0, `alert` 0. El SCADA no se vio afectado (450/450).
- **Causa:** el parser Modbus de Suricata 7 tiene un límite de solicitudes sin respuesta (`request-flood`, 500 por defecto) que marca error de protocolo. Con `exception-policy: auto` (por defecto), en modo IPS ese error descarta el flujo, incluso si las reglas están en `alert`. La regla 1000004 (rev 1) dependía de `app-layer-protocol:modbus` y no llegó a evaluarse.
- **Hallazgo para el paper:** Suricata con su configuración por defecto frena un Modbus flood de una sola fuente sin ninguna regla, por la validación del parser. Es distinto de "detección por reglas" y debe reportarse aparte.
- **Corrección del diseño (D19):** `exception-policy: ignore`, para que en E2 solo se alerte y en E3 decidan solo las reglas. Regla 1000004 rev 2: cuenta segmentos TCP con datos al 502 por origen (`dsize:>0`), sin depender del parser. Las corridas E2/E3 anteriores quedan con la nota "configuración previa a D19".

## A17. En modo alert (E2), el motor TCP de Suricata descartó 2,7 M SYN como "inválidos" (corregida en D19)
- **Corrida:** `20261117T194312Z_laptop-dev_E2_syn_piloto_r1` (ya con `exception-policy: ignore`). `ips.blocked` = 2 715 625, todo en `drop_reason.stream_error`. Captura: 5 165 262 paquetes de ataque antes del IPS y 172 142 después (97 % eliminado en modo "alert").
- **Causa:** en modo IPS, `stream.drop-invalid` (activo por defecto) descarta paquetes TCP que el motor TCP considera inválidos. Con hping3 los puertos de origen se reutilizan y el kernel del atacante envía RST, así que muchos SYN quedan como inválidos. Es independiente de las reglas y de la política de excepciones.
- **Hallazgo para el paper:** con la configuración por defecto, Suricata en línea frena buena parte de un SYN flood de una sola fuente por la validación de estado TCP, sin reglas. Hay que separarlo de la detección por reglas.
- **Corrección:** `stream.drop-invalid: no` (ampliación de D19). Las corridas E2/E3 de 19:38–19:48 UTC quedan con la nota "configuración intermedia".

## A18. Diagnóstico de la caída de OpenPLC (continuación de A15)
- **Reproducible y dependiente del volumen** (`docs/lab/logs/P12_diagnostico_openplc_laptop-dev.txt`, IPS en modo router):
  - 1 conexión a 50 solicitudes/s, 5 s (256 solicitudes): sobrevive.
  - 8 conexiones a 50/s, 5 s: sobrevive.
  - 1 conexión a 10/s: sobrevive.
  - 1 conexión sin límite, 2 s (536 736 solicitudes escritas): **el runtime termina**.
- **Patrón:** en las corridas, el SCADA deja de obtener respuesta justo al terminar el ataque, cuando el atacante cierra sus conexiones con respuestas pendientes. El proceso `core/openplc` queda zombi. `/proc/<pid>/stat` da `exit_code=0` (ninguna señal registrada) y no hay rastro en dmesg. `openplc.service` sigue `active` porque vigila `start_openplc.sh`.
- **Hipótesis descartada:** un SIGPIPE al escribir en un socket cerrado dejaría la señal 13 en el código de salida, y no aparece. **No se determinó la causa en el código de OpenPLC**; no se afirma ninguna.
- **En E3 (drop) también cayó una vez tras el ataque** (`20261117T195929Z`), aunque el SCADA tuvo 100 % de disponibilidad durante el ataque. La regla 1000004 deja pasar los primeros 100 segmentos/s por origen (`detection_filter`), y cada segmento del flood lleva 32 solicitudes, así que llegan hasta ~3 200 solicitudes/s. Ajustar el umbral, o medir por solicitudes en lugar de segmentos, es una decisión pendiente para pc-miguel; se registra el resultado tal cual.
- **Consecuencia para el diseño:** "el PLC sigue vivo tras la corrida" (`alive_after` en `plc_health.txt`) es un resultado del escenario y el arnés lo registra. El reinicio previo garantiza que cada corrida empiece con el PLC sano.

## A19. Calibración térmica de la tanda real en laptop-dev: sin throttling
- **Bloque:** E0 ×1 y E1/E3 × syn/modbus × 2, perfil `final` (21:26–21:46 UTC).
- **Temperatura:** Tctl máximo de 81,1 °C (PAUSE a 88 °C) y medio de hasta 68,5 °C durante las corridas con flood. El arnés esperó 5 veces a que la temperatura bajara de 65 °C antes de una corrida.
- **Frecuencia:** media de 4 125–4 217 MHz durante el ataque, frente a 3 000–3 430 MHz en el calentamiento. En reposo la CPU baja de frecuencia por sí sola, así que la frecuencia sube con la carga y no hay throttling. No hacen falta optimizaciones térmicas.
- **Duración:** 114–166 s por corrida.
- **Captura:** en E1 syn, dumpcap descartó 8–13 % (≈ 177 kpps). Esos conteos son una cota inferior; el contador del firewall y el kernel del atacante no dependen de la captura.

## A20. El control de temperatura previo a cada corrida buscaba el CSV del guardián por la fecha UTC del día (corregida; afecta a 7 corridas)
- **Síntoma:** desde las 00:00 UTC del 2026-11-18 (19:00 hora local) cada corrida tardó ~22 min en vez de ~2,5 min, y `tctl_start_c`, `tctl_end_c` y `guard_states` quedaron vacíos en `runs.csv`.
- **Causa:** el guardián fija el nombre de su CSV al arrancar (`guard_<plataforma>_<fecha UTC de inicio>.csv`) y no rota a medianoche. `run_once.sh` deducía el archivo con la fecha de *ahora*, así que desde las 00:00 UTC buscaba `..._20261118.csv`, que no existe. La temperatura leída salía vacía (equivale a 99 °C) y el control esperaba el máximo de 600 × 2 s = 20 min antes de seguir. El guardián siguió activo y en `OK` todo el tiempo.
- **Efecto en los datos:** el control de temperatura no dejó pasar ninguna corrida caliente (al contrario, esperó de más), así que las corridas empezaron con la laptop fría (38–44 °C en reposo). Las mediciones de la corrida (polls, `ts_host.csv`, capturas, contadores) no se ven afectadas, y `ts_host.csv` conserva el Tctl por segundo. Se pierden solo los campos `tctl_start_c`, `tctl_end_c` y `guard_states` en `runs.csv` de las corridas afectadas, que se pueden reconstruir con `ts_host.csv` y con el CSV del guardián. Corridas afectadas: `20261117T235851Z_…_E3_icmp_final_r5` (solo `tctl_end_c` y `guard_states`: empezó antes de medianoche UTC y terminó después), `20261118T000055Z_…_E3_icmp_final_r3`, `…002300Z…_r6`, `…004508Z…_r7`, `…010715Z…_r9`, `…012921Z…_r8` y `…015128Z…_E1_icmp_final_r4`. La fila `20261117T184920Z_…_E1_syn_piloto_r1` tiene `tctl_start_c` vacío por otro motivo (piloto previo).
- **Corrección:** `run_once.sh` usa ahora `guard_csv()`: toma el CSV más reciente de la plataforma y solo si se está escribiendo (modificado hace menos de 30 s). Si el guardián no escribe, el resultado vacío mantiene el control esperando, como antes; el umbral (`COOLDOWN_TARGET_TCTL=65`), el estado `OK/WARN` exigido y el tope de espera no se tocaron. Se aplicó con reemplazo atómico del archivo, sin interrumpir la corrida en curso, y rige desde la siguiente corrida. El guardián no se tocó ni se reinició.
- **Tratamiento de los datos (sin estimar ni rellenar):** `runs.csv` no se modifica y los campos vacíos se quedan vacíos. `lab/analysis/muestras_guard_por_corrida.py` copia, para las 7 corridas afectadas, muestras *reales* del CSV del guardián (Tctl en `t0`, Tctl al final del enfriamiento con su marca de tiempo, estados y Tctl máximo de la ventana) a `data/processed/runs_guard_muestras_laptop-dev_final.csv`. No son los campos ausentes (el arnés los leía en otros instantes: `tctl_end_c` se toma tras el procesado y suele ser mayor) y no se presentan como tales. El Tctl por segundo de cada corrida sigue en `ts_host.csv`. Un primer intento de reconstruir los campos con un desfase calibrado se descartó por ser una estimación (regla de `CLAUDE.md`).
- **Pendiente (no urgente):** `guard.sh` sigue sin rotar su CSV a medianoche; es inocuo con la corrección, pero el archivo diario puede abarcar más de un día.

## A21. En E2 con syn e icmp, los descartes por saturación (NFQUEUE) superan en 29–39 % a los paquetes que la captura ve desaparecer (SIN EXPLICAR)
- **Observación (tanda real, laptop-dev, perfil `final`, 10 corridas por celda):** cociente `(suri_ips_blocked + nfq_queue_dropped) / cap_attack_removed`. E3 (syn, udp, icmp, modbus) y E2 udp: 1,00 en todas las corridas. **E2 syn: 1,29–1,33. E2 icmp: 1,33–1,39.** Ejemplo, E2 syn: la captura ve 6,95 M de paquetes de ataque eliminados entre la VLAN 20 y la VLAN 30; `nfq_queue_dropped` marca 9,18 M y `suri_ips_blocked` 0 (modo alert).
- **Qué se descartó:** el descarte de la captura (`cap_drop_pct`) es como máximo 2,2 % en E2, muy por debajo de la diferencia. No se ha comprobado si el contador NFQUEUE incluye paquetes que no son de ataque ni si hay doble conteo entre las dos colas (D18).
- **Estado:** **no se explica y no se afirma ninguna causa.** Según `CLAUDE.md`, el % de "ataque eliminado" y la parte por saturación de E2 syn/icmp no deben citarse como resultado hasta resolverla. La disponibilidad, el RTT y las demás métricas no dependen de estos dos contadores.
- **Siguiente paso propuesto:** comparar las tres fuentes (captura VLAN 20/30, contadores nftables y NFQUEUE) corrida por corrida en E2 syn/icmp y revisar cómo `summarize_runs.py` suma las dos colas.
