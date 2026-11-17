# P19 · Series temporales medidas durante el ataque (sustituyen la figura conceptual)

**Prioridad: RECOMENDADO** · Tiempo de máquina estimado: ≈ 30–45 min (valida con el piloto de P12)
**Observaciones que cubre:** 19 (PerformanceCurve es conceptual, no medida), 5, 6

---

## PROMPT (copiar desde aquí)

Repo y rama confirmados (`pwd`, `git branch --show-current`); guardián activo y en OK; P12 aprobado por mí. Respeta `CLAUDE.md`: nada de datos inventados, dudar, segunda fuente, documentar.

### Objetivo
Obtener curvas **medidas** de RTT, disponibilidad por segundo, pps y CPU a lo largo de una corrida (calentamiento, ataque, recuperación), para reemplazar la figura conceptual del paper.

### Qué ejecutar
- Corrida larga de `syn` (y `modbus` si hay tiempo) con calentamiento 30 s, ataque 120 s, recuperación 60 s en E1 y en E3, **3 repeticiones** cada una; el arnés ya registra los CSV a 1 s y las solicitudes Modbus a 10 Hz; ajusta el perfil `serie` en `experiment.yaml`.
- Marca en los datos los instantes exactos de inicio y fin de ataque (columnas `phase`).

### Aceptación
Series continuas sin huecos injustificados, instantes de transición visibles, mismas definiciones de métricas que P13–P16. Si la señal es ruidosa, no la suavices en crudo; el suavizado va solo en la figura y se declara.

### Reglas comunes de ejecución de este prompt
- Lanza el arnés dentro de `tmux` y con `limited-run.sh`; vigila `lab/guard/lab-status.sh` cada 10 corridas. Si el guardián llega a PAUSE/ABORT, deja que el arnés pare, informa y espera.
- Tras **cada corrida** ejecuta `validate_run.py`. Una corrida FAIL o aborted se repite; las repeticiones, fallos y su causa quedan en `runs.csv` (no se borran).
- Tras la 1.ª, la 5.ª y la 10.ª repetición, mira los números: ¿tienen sentido físico y son consistentes con el piloto? Si no, **para y audita** (`05_problemas_anomalias.md`).
- Al terminar: segunda fuente sobre el conjunto (suma de paquetes de ataque antes/después del IPS frente a contadores de Suricata, por corrida; diferencia relativa mediana y máxima), resumen provisional de media y DE (solo exploratorio; las tablas finales salen de P20), entradas en `00_diario.md`, `06_logros_avances.md`, `05_problemas_anomalias.md`, `07_resultados_auditados.md` y commit (los CSV de `data/raw/` se versionan; las capturas no).
- Si algo no se pudo ejecutar, di **exactamente** qué falta y qué debe declararse como limitación; no lo sustituyas.

## FIN DEL PROMPT
