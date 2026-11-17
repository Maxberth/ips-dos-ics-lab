# P11 · Arnés de medición: ejecutar una corrida completa y guardar datos crudos con metadatos

**Prioridad: IMPRESCINDIBLE** · Tiempo: 60–90 min
**Observaciones:** 5 (repeticiones), 6 (datos crudos), 11 (parámetros), 22 (comandos exactos), 2, 3, 10. Es el núcleo del rigor de los datos.

---

## PROMPT (copiar desde aquí)

Repo y rama confirmados; guardián activo; cadena probada en P09 y P10. Respeta `CLAUDE.md`: **cero datos inventados**. Escribe el arnés en `lab/harness/` (Python + shell), versionado, que ejecute **una corrida** y varias repeticiones, y deje todo en crudo.

### 1. Parámetros (archivo `lab/config/experiment.yaml`)
Perfiles: `piloto` (calentamiento 5 s, ataque 30 s, enfriamiento 10 s) y `final` (calentamiento 15 s, **ataque 60 s**, enfriamiento 15 s; la tabla actual del paper dice 5 min: documenta la desviación y su justificación en `03_limitaciones.md`; permite `--attack-seconds 300` si hay tiempo). Escenarios: `E0` base (sin ataque), `E1` solo firewall/VLAN (IPS en modo router), `E2` Suricata alert, `E3` Suricata drop, `E4` Snort drop (opcional). Ataques:
- `syn`: `hping3 -S -p 502 --flood 192.168.30.10` (sin `--rand-source`)
- `udp`: `hping3 --udp -p 502 --flood 192.168.30.10` (y variante hacia SCADA si lo decides)
- `icmp`: `hping3 --icmp --flood 192.168.30.10` (el paper usó `ping -f`; elige y documenta; si usas `ping -f`, hazlo con el mismo sistema)
- `modbus`: script Scapy/pymodbus con solicitudes Modbus válidas a tasa fija, comando exacto guardado (obs. 22).
**Tasa:** `--flood` envía al máximo y depende de la CPU: **mide los pps efectivos reales** (contadores del puerto OVS y de `ip -s link` en Kali) en cada corrida y guárdalos; si lo prefieres, usa tasas fijas (`-i u100`) además del flood, y declara ambas variantes. Todo con `limited-run.sh`.

### 2. Secuencia por corrida (cada paso con registro de tiempo UTC en ns)
1. Comprobar guardián en OK, temperatura < 70 °C (si no, esperar), y salud de la cadena (poller sin ataque 10 s con disponibilidad 100 %).
2. Preparar el escenario (conmutar modo IPS, cargar reglas del escenario, reiniciar contadores y rotar logs), anotando **hash** de reglas/config y versiones (`versions_snapshot.sh`).
3. Iniciar capturas **fuera de banda** en el host: `tcpdump` en el mirror/taps de VLAN 20 (antes del IPS) y VLAN 30 (después), con filtro por puerto/protocolo, `-s 96`, ring buffer; registra la pérdida de captura (`tcpdump` "dropped by kernel").
4. Iniciar poller SCADA, medición de CPU (guest y host), lectura de contadores OVS/nft/firewall y de Suricata (`eve.json` stats/`stats.log`) cada 1 s.
5. Calentamiento → ataque (se detiene también si aparece `/run/lab/PAUSE` o `ABORT`; esa corrida queda `status=aborted` y se repite, no se descarta en silencio) → enfriamiento.
6. Detener, **copiar** logs y capturas a `data/captures/<run_id>/`, calcular sha256 y añadirlos a `data/captures/manifest.csv`.
7. Esperar recuperación (PLC responde, temperatura baja) antes de la siguiente corrida; registrar el tiempo de espera.

### 3. Orden y repeticiones
`run_matrix.py`: para cada repetición 1..10, recorre los ataques en **orden aleatorio con semilla registrada** (evita sesgo por deriva térmica); un `run_id` único por corrida (`E3_syn_r07_20261117T2214Z`). Reanuda sin repetir lo ya hecho con estado `ok`.

### 4. Datos crudos (CSV, todos con `run_id`; nada de datos de ejemplo en `data/raw/`)
- `data/raw/runs.csv`: una fila por corrida: `run_id, status, scenario, attack, repetition, profile, attack_seconds, warmup_s, cooldown_s, start_utc, end_utc, seed, attack_cmd, target_ip, pps_sent_effective, host_temp_start_c, host_temp_max_c, guard_state_max, repo_commit, suricata_version, rules_sha256, suricata_yaml_sha256, ovs_version, kernel_host, kernel_ips, openplc_commit, notes`.
- `data/raw/scada_polls/<run_id>.csv` (cada solicitud Modbus), `data/raw/ts_1s/<run_id>.csv` (por segundo: pps y bytes por puerto OVS, nft/firewall counters, `suricata` `kernel_packets`, `nfq` accepted/dropped, `detect.alert`, `ips.drop`/`ips.accepted`, CPU guest y host del PLC y del IPS, temperatura, memoria libre).
- `data/raw/pcap_counts/<run_id>.csv`: conteos desde la captura (antes y después del IPS, por protocolo/ventana de 1 s), generados por `tshark`/`tcpdump`+script.
- `data/captures/manifest.csv`.
Todos los scripts guardan **salida cruda sin procesar**; cualquier cálculo va a `data/processed/` desde `lab/analysis/`.

### 5. Verificación del arnés (sin gastar horas)
- Corrida `E1` `syn` perfil `piloto` ×1 y corrida `E0` ×1: los CSV existen, tienen las columnas esperadas, sin celdas vacías inexplicables, `runs.csv` completo con versiones y hashes.
- Prueba de **fallo controlado**: lanza una corrida con la VM `plc` apagada; debe quedar `status=failed` con la causa en `notes`, sin números inventados.
- Escribe `lab/harness/validate_run.py` que audite cada corrida (columnas, conteos, `ts` monótonos, huecos del poller, desfase de relojes, captura sin pérdidas, métricas dentro de rangos físicos) y devuelva OK/WARN/FAIL; se ejecuta tras cada corrida y se registra en `runs.csv`.
- Documenta cómo reproducir una corrida desde cero en `docs/lab/reproducir.md`. Diario, decisiones, commit.

## FIN DEL PROMPT
