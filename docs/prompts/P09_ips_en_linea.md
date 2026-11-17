# P09 · IPS en línea (Suricata con NFQUEUE) enrutando VLAN 20 ↔ VLAN 30

**Prioridad: IMPRESCINDIBLE** · Tiempo: 60–90 min (es el paso más delicado)
**Observaciones:** 1 (prevención real: `drop`, NFQUEUE), 20, 8 (qué cuenta como detección), 7, 11.

---

## PROMPT (copiar desde aquí)

Repo y rama confirmados; guardián activo; VM `ips` creada (P07) con eth1 en VLAN 20 (`192.168.20.2`) y eth2 en VLAN 30 (`192.168.30.1`). Respeta `CLAUDE.md`. **Dudar es obligatorio en este paso:** una regla `drop` no demuestra nada hasta que se vea que los paquetes dejan de llegar al PLC.

### Parte 1: ruta del IPS sin Suricata (modo "solo router", que será el modo E1)
1. En `ips`: `net.ipv4.ip_forward=1`, rutas hacia 192.168.10.0/24 vía `192.168.20.1`. En `plc` y `scada` las rutas correspondientes.
2. Verifica con `ping`/`traceroute` que `scada → plc` y `kali → plc` (a través de `fw` e `ips`) funcionan con el IPS solo reenviando. Registra el RTT base.

### Parte 2: NFQUEUE (modo en línea)
1. En `ips`, instala Suricata (misma versión que el host, mejor la de los repos de Ubuntu o el PPA oficial; anota versión y origen) con soporte NFQueue.
2. Crea un archivo nftables **versionado** (`lab/config/ips/nftables-nfq.conf`) con una cadena `forward` que mande a la cola 0 el tráfico enrutado entre eth1 y eth2: `queue num 0`. **Decisión explícita sobre `bypass`:** sin `bypass`, si Suricata cae el tráfico se corta (fail-closed, más fiel a un IPS pero puede cortar el laboratorio); con `bypass` se deja pasar (fail-open) y falsea una medición de "bloqueo". Usa **sin bypass** para las pruebas y documéntalo en `04_decisiones.md`.
3. Define dos conmutadores reproducibles: `ips_mode_router.sh` (sin regla de cola) e `ips_mode_nfq.sh` (con cola y Suricata en `-q 0`). El resto de la ruta debe ser idéntico en ambos modos, para atribuir diferencias solo al IPS (obs. 10).
4. Configuración de Suricata en `lab/config/ips/suricata.yaml` (copia del activo, diff frente al original): modo `nfq` con `mode: accept` (los verdictos `drop` de las reglas descartan), `HOME_NET` = `192.168.20.0/24,192.168.30.0/24`, `eve.json` con `stats` cada 1 s, `stats.log` habilitado, salida `alert` y `drop` en eve, afinación de `nfq` (`fail-open: no`, `batchcount`, `max-pending-packets` documentados), hilos `workers` y afinidad a los vCPU de `ips`. Anota todos los parámetros de rendimiento: irán a la tabla del paper (obs. 11).
5. Reglas en `lab/config/ips/rules/lab.rules` (copia al `ips`, y dile a Suricata que las cargue, solo estas más `emerging` si lo decides y documentas). Para el SID 1000001 en adelante, **dos variantes de cada una**, activables por archivo: `alert` (E2) y `drop` (E3):
   - SYN flood hacia 502: **no uses `threshold` con `drop` sin comprobar**; en Suricata una acción `drop` con `threshold` puede comportarse distinto a un `detection_filter`. Lee la documentación de **tu versión instalada** (`man suricata`, docs oficiales) y prueba empíricamente cuál descarta realmente tras superar el umbral. Registra la regla final y la prueba. Ejemplo de partida (a validar): `drop tcp any any -> 192.168.30.10 502 (msg:"LAB SYN flood to Modbus"; flags:S; detection_filter:track by_src, count 100, seconds 1; sid:1000001; rev:1;)`.
   - UDP flood hacia el PLC y hacia SCADA; ICMP flood hacia el PLC; Modbus/TCP flood (solicitudes Modbus por sesión excesivas, o `app-layer-protocol:modbus` con `detection_filter`). 
   - **Tráfico legítimo no debe caer**: SCADA consulta a 10 Hz; define umbrales por encima de eso (p. ej. conteos por segundo ≫ 10) y compruébalo.
   - Limitación documentada: el atacante usa una sola IP (sin `--rand-source`), así que `track by_src` funciona; un DDoS distribuido queda fuera de alcance (`03_limitaciones.md`).
6. Registra el **hash** de `lab.rules` y de `suricata.yaml` en cada corrida (metadato).

### Verificación (CUMPLE/NO CUMPLE con evidencia en `docs/lab/logs/P09_*.txt`)
1. `suricata -T -c … -S …` valida config y reglas sin errores.
2. Modo router: `scada → plc` ok (ping). Modo NFQ con Suricata corriendo: `scada → plc` ok (el tráfico pasa por la cola: contadores `nft list ruleset` aumentan; `suricata` `nfq` en `stats.log` muestra paquetes aceptados).
3. **Prueba de drop controlada, con tráfico mínimo (no flood):** regla `drop` de prueba sobre un ping de 1 paquete/s desde `scada` con `-c 5`; con la regla en `alert` los 5 llegan; con `drop` **ninguno llega al PLC** (`tcpdump` en `plc` sin eco entrante y en `ips` sí). `eve.json` contiene `event_type":"alert"` con `"action":"blocked"` / `drop` solo en el modo drop.
4. Fail-closed comprobado: si Suricata se detiene, el tráfico se corta (esperado) y se restaura al reiniciar.
5. Documenta en `05_problemas_anomalias.md` cualquier discrepancia (p. ej. alertas sin drops reales, offload de checksum `ethtool -K … tx off rx off` en virtio, MTU, etc.).
6. Guarda un snapshot `clean-ips-suricata`. Registra versiones, diario y commit.

No avances a P10 si el paso 3 no demuestra descarte real de paquetes.

## FIN DEL PROMPT
