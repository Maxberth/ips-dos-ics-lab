# P10 · OpenPLC con proceso simulado, SCADA/HMI y tráfico legítimo

**Prioridad: IMPRESCINDIBLE** · Tiempo: 60–90 min
**Observaciones:** 6 (definir tráfico legítimo vs malicioso), 7 (RTT), 8, 11, 22 (comando exacto Modbus), 24 (CPU medida en VM).

---

## PROMPT (copiar desde aquí)

Repo y rama confirmados; guardián activo; VMs `plc`, `scada` listas; rutas de P09 funcionando. Respeta `CLAUDE.md`.

### 1. OpenPLC con un proceso simulado
1. En `plc`, instala OpenPLC Runtime (repositorio oficial, **fija el commit/tag** y regístralo; revisa el script de instalación antes de ejecutarlo). Servidor Modbus/TCP en el puerto 502, escuchando solo en `192.168.30.10`.
2. Carga un programa ST/Ladder versionado en `lab/config/plc/` que simule un proceso sencillo y determinista (p. ej. un tanque con nivel que sube/baja, bomba y alarma, ciclo de 100 ms) con registros de lectura/escritura conocidos. Documenta el mapa de registros (`lab/config/plc/registers.md`).
3. Verifica con `mbpoll` o `pymodbus` desde `scada`: lectura de registros esperados y escritura de un coil con retorno correcto.

### 2. SCADA/HMI y generador de tráfico legítimo
1. Cliente principal para medir: script `lab/harness/scada_poller.py` (`pymodbus`) en `scada`: consulta N registros cada 100 ms (10 Hz), con timeout de 500 ms, y registra **cada solicitud** en CSV: `ts_send_ns, ts_recv_ns, ok, rtt_ms, exception, tx_id`. RTT = tiempo entre envío y recepción de la respuesta Modbus (obs. 7: es RTT, no una vía).
2. HMI visual opcional: FUXA o ScadaBR **solo si cabe en RAM** (si no, queda como opcional y se declara que la HMI se sustituyó por un cliente pymodbus; D4). Si se instala, no debe correr durante las mediciones salvo decisión documentada.
3. **Definición escrita** en `docs/lab/definiciones_metricas.md` (se usará para corregir §3.4 del paper, obs. 6/7/8):
   - Tráfico legítimo = solicitudes Modbus/TCP de `scada` a `plc:502` a 10 Hz.
   - Tráfico malicioso = paquetes del atacante (192.168.10.100) hacia el objetivo del escenario.
   - Disponibilidad = % de solicitudes legítimas respondidas correctamente en la ventana de ataque (y también, aparte, % de segundos con ≥ 1 respuesta; indica cuál es la definición principal).
   - Pérdida de paquetes (legítimos) = 1 − respuestas/solicitudes; pérdida del enlace medida en captura como segunda fuente.
   - Latencia = RTT en ms (mediana, media, p95, p99 por corrida).
   - Rendimiento (throughput) = bytes·8 / (tiempo·10⁶) en Mbps, sobre el tráfico legítimo y el total observado en el puerto (sin ×100).
   - Tasa de detección = eventos `alert`/`drop` con el SID del escenario ÷ paquetes de ataque enviados (por paquete), y por separado sesiones/ráfagas detectadas; indica cuál se reportará (obs. 8).
   - CPU de OpenPLC: medida **dentro de la VM** (`pidstat -p`) y desde el host (`virsh domstats --cpu-total` o cgroup) como segunda fuente; en el paper se declara que es CPU de una VM, no de PLC físico (obs. 24).

### 3. Verificación (CUMPLE/NO CUMPLE con evidencia)
- Desde `scada`, 60 s de sondeo con IPS en modo router y luego en modo NFQ (alert, sin ataque): disponibilidad 100 % esperada; si no, **investiga antes de seguir** (offloading, tiempos, reloj de las VMs). Anota la RTT base (media, DE).
- Sincronización de relojes: las marcas de tiempo salen de **hosts distintos**; comprueba `chrony`/`timedatectl` y mide el desfase entre VMs y host (objetivo < 5 ms o documenta cómo lo corriges, p. ej. usando RTT en un mismo reloj, que no necesita sincronización).
- El poller a 10 Hz no deja huecos por su propio funcionamiento (prueba 60 s sin ataque con CPU del `scada` baja).
- Snapshots `clean-plc-ready` y `clean-scada-ready`; versiones, comandos exactos usados, diario, anomalías, commit.

## FIN DEL PROMPT
