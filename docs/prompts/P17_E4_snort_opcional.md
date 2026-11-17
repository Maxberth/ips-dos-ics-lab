# P17 · Escenario E4: Snort 3 en línea (comparación), ataques × 10

**Prioridad: OPCIONAL (si no hay tiempo: retirar Snort de la comparación y dejarlo como alternativa en la discusión)** · Tiempo de máquina estimado: ≈ 1,5–2 h incluida la instalación (valida con el piloto de P12)
**Observaciones que cubre:** 3 (Snort mencionado sin experimento), 5, 6

---

## PROMPT (copiar desde aquí)

Repo y rama confirmados (`pwd`, `git branch --show-current`); guardián activo y en OK; P12 aprobado por mí. Respeta `CLAUDE.md`: nada de datos inventados, dudar, segunda fuente, documentar.

### Objetivo
Comparar Suricata y Snort 3 con la misma ruta, las mismas reglas equivalentes y los mismos ataques. Primero decide conmigo si merece la pena dado el tiempo restante: estima las horas y recomienda.

### Pasos
1. En `ips` (nunca simultáneo con Suricata): instala Snort 3 con DAQ `nfq`, con la misma cola NFQUEUE (`queue num 0`). Registra versión y origen. Traduce las reglas `drop` de E3 a la sintaxis de Snort 3 (`lab/config/ips/snort/`), con umbrales equivalentes (`detection_filter`/`rate_filter`) y documenta cualquier diferencia semántica (no son idénticas).
2. Verificación equivalente a P09 (drop de un ping controlado, fail-closed, `snort -T`).
3. Mini-piloto (1 repetición × 4 ataques) y auditoría como en P12 antes de lanzar las 10 repeticiones.
4. `E4` × {syn, udp, icmp, modbus} × 10, mismas semillas y parámetros.

### Criterios de aceptación
Mismos que P16 (evidencia de bloqueo por dos fuentes, falsos positivos/negativos, CPU del IPS), más una tabla comparativa Suricata vs Snort con n, media y DE. **No afirmes que uno es mejor sin IC que lo respalde**; con n = 10 y solapamiento de IC, declara "sin diferencia detectable".

### Reglas comunes de ejecución de este prompt
- Lanza el arnés dentro de `tmux` y con `limited-run.sh`; vigila `lab/guard/lab-status.sh` cada 10 corridas. Si el guardián llega a PAUSE/ABORT, deja que el arnés pare, informa y espera.
- Tras **cada corrida** ejecuta `validate_run.py`. Una corrida FAIL o aborted se repite; las repeticiones, fallos y su causa quedan en `runs.csv` (no se borran).
- Tras la 1.ª, la 5.ª y la 10.ª repetición, mira los números: ¿tienen sentido físico y son consistentes con el piloto? Si no, **para y audita** (`05_problemas_anomalias.md`).
- Al terminar: segunda fuente sobre el conjunto (suma de paquetes de ataque antes/después del IPS frente a contadores de Suricata, por corrida; diferencia relativa mediana y máxima), resumen provisional de media y DE (solo exploratorio; las tablas finales salen de P20), entradas en `00_diario.md`, `06_logros_avances.md`, `05_problemas_anomalias.md`, `07_resultados_auditados.md` y commit (los CSV de `data/raw/` se versionan; las capturas no).
- Si algo no se pudo ejecutar, di **exactamente** qué falta y qué debe declararse como limitación; no lo sustituyas.

## FIN DEL PROMPT
