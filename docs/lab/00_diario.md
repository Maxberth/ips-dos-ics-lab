# Diario del laboratorio (solo se añade al final)

- 2026-11-17: se crea el repositorio con la documentación inicial, la arquitectura y la serie de prompts P01–P22. Aún no se ha ejecutado ningún paso del laboratorio.
- 2026-11-17 17:45 UTC (laptop-dev): P01 hecho (CLAUDE.md, docs/lab/01–08, perfiles `laptop-dev` y `pc-miguel`). No había contenedores Docker en ejecución (`docs/lab/contenedores_apagados.md`). `sudo` pide contraseña: se preparó `lab/setup/root_setup.sh` para que el usuario lo ejecute una vez.
- 2026-11-17 17:48 UTC (laptop-dev): P04 parcial. Guardián (`lab/guard/`) escrito y probado con umbrales simulados: WARN, PAUSE (RAM, PSI, temperatura), ABORT fijado y `lab-stop.sh --clear` funcionan; un scope con MemoryMax=256M que escribe 600 MiB muere solo (exit 137) sin afectar al escritorio. Primer intento de esa prueba no detectó nada porque `bytearray` no toca las páginas (corregido). Las simulaciones escribían en `data/raw/guard/`: se borraron y ahora usan `GUARD_CSV` temporal. Guardián activo como `ips-lab-guard` (servicio de usuario). Pendiente: límites de `machine.slice` (lo aplica `root_setup.sh`) y prueba térmica con `stress-ng`.
- 2026-11-17 17:47 UTC (laptop-dev): descargada la imagen Debian 13 genericcloud (344 MB) y verificada con SHA512SUMS. Decisiones D1–D5 y D8–D10, limitaciones L1–L4.
- 2026-11-17 18:47 UTC (laptop-dev): P05 a P10 verificados.
  - **P05:** host instalado (`docs/lab/logs/P05_*`).
  - **P06:** red `ovs-ot`.
  - **P07:** 5 VMs Debian 13 con límites duros y pinning (`P07_verificacion_vms_laptop-dev.txt`).
  - **P08:** firewall nftables E1.
  - **P09:** Suricata 7.0.10 en NFQUEUE fail-closed, con descarte real: drop 0/5 ecos al PLC, alert 5/5.
  - **P10:** OpenPLC (commit b5d41356) en RUN con `tank_sim.st` y SCADA leyendo Modbus.
  - `check_chain.sh`: 23 pruebas en CUMPLE (`docs/lab/logs/P09_check_chain_laptop-dev.txt`).
  - Problemas resueltos: arranque sin VGA (A4), ufw (A5, proxy por SSH), `sg` (A6), conteo de la prueba (A9).
- 2026-11-17 18:49–19:00 UTC (laptop-dev): **interrupción de unos 55 min.** Durante la primera corrida con ataque (E1 SYN piloto) el post-proceso con tshark agotó la RAM del host. El guardián destruyó las VMs (ABORT 18:51:07) y systemd-oomd mató la app de Claude (18:52:52), lo que cortó la sesión. Detalle y correcciones en A10. Se rehízo solo el conteo de la captura (con `pcap_count.py` en un scope de 1 GiB); la corrida queda como `partial` en `runs.csv`. Se borró el ABORT, se reiniciaron el guardián y las VMs, y se repitió `check_chain.sh`.
