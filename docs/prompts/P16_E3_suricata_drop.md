# P16 · Escenario E3: Suricata en línea con `drop` (prevención real), todos los ataques × 10

**Prioridad: IMPRESCINDIBLE** · Tiempo de máquina estimado: ≈ 1–1,5 h (valida con el piloto de P12)
**Observaciones que cubre:** 1 (reglas drop y evidencia en eve.json), 20 (automatic blocking demostrado), 2 (UDP), 5, 6, 8, 10, 22

---

## PROMPT (copiar desde aquí)

Repo y rama confirmados (`pwd`, `git branch --show-current`); guardián activo y en OK; P12 aprobado por mí. Respeta `CLAUDE.md`: nada de datos inventados, dudar, segunda fuente, documentar.

### Objetivo
Es el experimento central del paper: prevención real. Cada corrida debe dejar evidencia **independiente** del bloqueo.

### Qué ejecutar
- `E3` × {syn, udp, icmp, modbus} × 10 repeticiones, mismas semillas/orden y parámetros que E1/E2.
- Guarda por corrida: extracto de `eve.json` con eventos `drop` (recuento por SID y las primeras N líneas literales, para citar en el paper la salida de bloqueo), `stats` de `nfq`/`ips`, capturas antes/después del IPS, y tiempo hasta el primer `drop` (latencia de reacción del umbral).

### Criterios de aceptación (con duda activa)
1. Evidencia de bloqueo por **dos fuentes**: (antes − después) en captura ≈ `drop` de Suricata (tolerancia ≤ 5 %, o anomalía explicada).
2. **Falsos positivos:** solicitudes SCADA legítimas descartadas por reglas drop = lo más cercano a 0; cualquier caso se registra con su causa. Informa el número exacto.
3. **Falsos negativos:** paquetes de ataque que llegaron al PLC (después del IPS) y por qué (primeros paquetes hasta superar umbral, paquetes en vuelo).
4. Efecto sobre el PLC: ¿la disponibilidad/latencia mejora frente a E1? Reporta el resultado **tal cual salga**, incluso si es peor o no cambia; entonces investiga (cuello de botella del propio IPS en NFQUEUE, pérdida de paquetes en la cola, CPU) antes de interpretar.
5. Registro de CPU y colas de Suricata: ¿el IPS se satura (cuello de botella en pps)? Es hallazgo y limitación.
6. Captura el contenido de las reglas, versión y hashes en `runs.csv` (ya lo hace el arnés) y copia las reglas a `docs/lab/reglas_finales.md` para el paper (§4.3).

### Reglas comunes de ejecución de este prompt
- Lanza el arnés dentro de `tmux` y con `limited-run.sh`; vigila `lab/guard/lab-status.sh` cada 10 corridas. Si el guardián llega a PAUSE/ABORT, deja que el arnés pare, informa y espera.
- Tras **cada corrida** ejecuta `validate_run.py`. Una corrida FAIL o aborted se repite; las repeticiones, fallos y su causa quedan en `runs.csv` (no se borran).
- Tras la 1.ª, la 5.ª y la 10.ª repetición, mira los números: ¿tienen sentido físico y son consistentes con el piloto? Si no, **para y audita** (`05_problemas_anomalias.md`).
- Al terminar: segunda fuente sobre el conjunto (suma de paquetes de ataque antes/después del IPS frente a contadores de Suricata, por corrida; diferencia relativa mediana y máxima), resumen provisional de media y DE (solo exploratorio; las tablas finales salen de P20), entradas en `00_diario.md`, `06_logros_avances.md`, `05_problemas_anomalias.md`, `07_resultados_auditados.md` y commit (los CSV de `data/raw/` se versionan; las capturas no).
- Si algo no se pudo ejecutar, di **exactamente** qué falta y qué debe declararse como limitación; no lo sustituyas.

## FIN DEL PROMPT
