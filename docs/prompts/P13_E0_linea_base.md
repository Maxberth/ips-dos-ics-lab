# P13 · Escenario E0: línea base (sin ataque), 10 repeticiones

**Prioridad: IMPRESCINDIBLE** · Tiempo de máquina estimado: ≈ 30–40 min (valida con el piloto de P12)
**Observaciones que cubre:** 5 (repeticiones, media, DE, IC), 6 (datos crudos), 7 (RTT), 11 (parámetros)

---

## PROMPT (copiar desde aquí)

Repo y rama confirmados (`pwd`, `git branch --show-current`); guardián activo y en OK; P12 aprobado por mí. Respeta `CLAUDE.md`: nada de datos inventados, dudar, segunda fuente, documentar.

### Objetivo
Medir la operación normal con los tres modos de ruta, para tener la referencia de latencia, disponibilidad, rendimiento y CPU contra la que se comparan los ataques.

### Qué ejecutar
- `E0` con IPS en modo router, en modo NFQ-alert y en modo NFQ-drop (reglas cargadas, **sin ataque**): 10 repeticiones cada uno, perfil `final` (se puede reducir a 60 s de medición por corrida).
- Además, **iperf3** TCP 30 s entre `scada` y `plc` (o el servicio de prueba apropiado) en cada modo, 10 repeticiones, para el rendimiento máximo de la ruta (bytes·8/(tiempo·10⁶), sin ×100) y el coste del IPS en línea sin ataque (latencia añadida por Suricata).

### Criterios de aceptación
- Disponibilidad de las solicitudes Modbus legítimas ≈ 100 % en las 30 corridas; cualquier excepción se audita.
- RTT con y sin NFQ: diferencia medida y registrada (es el sobrecoste del IPS).
- Variabilidad entre repeticiones (DE) creíble (no 0).

### Reglas comunes de ejecución de este prompt
- Lanza el arnés dentro de `tmux` y con `limited-run.sh`; vigila `lab/guard/lab-status.sh` cada 10 corridas. Si el guardián llega a PAUSE/ABORT, deja que el arnés pare, informa y espera.
- Tras **cada corrida** ejecuta `validate_run.py`. Una corrida FAIL o aborted se repite; las repeticiones, fallos y su causa quedan en `runs.csv` (no se borran).
- Tras la 1.ª, la 5.ª y la 10.ª repetición, mira los números: ¿tienen sentido físico y son consistentes con el piloto? Si no, **para y audita** (`05_problemas_anomalias.md`).
- Al terminar: segunda fuente sobre el conjunto (suma de paquetes de ataque antes/después del IPS frente a contadores de Suricata, por corrida; diferencia relativa mediana y máxima), resumen provisional de media y DE (solo exploratorio; las tablas finales salen de P20), entradas en `00_diario.md`, `06_logros_avances.md`, `05_problemas_anomalias.md`, `07_resultados_auditados.md` y commit (los CSV de `data/raw/` se versionan; las capturas no).
- Si algo no se pudo ejecutar, di **exactamente** qué falta y qué debe declararse como limitación; no lo sustituyas.

## FIN DEL PROMPT
