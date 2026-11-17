# P15 · Escenario E2: Suricata en línea solo con alertas (`alert`), todos los ataques × 10

**Prioridad: RECOMENDADO (muestra por qué el `alert` del paper no era prevención)** · Tiempo de máquina estimado: ≈ 1–1,5 h (valida con el piloto de P12)
**Observaciones que cubre:** 1 (la regla alert no previene), 20, 8 (detección), 10, 5

---

## PROMPT (copiar desde aquí)

Repo y rama confirmados (`pwd`, `git branch --show-current`); guardián activo y en OK; P12 aprobado por mí. Respeta `CLAUDE.md`: nada de datos inventados, dudar, segunda fuente, documentar.

### Objetivo
Demostrar con datos que Suricata en modo `alert` detecta pero no mitiga (contraste directo con E3). Si el tiempo apremia, ejecútalo solo con `syn` y `modbus` y declara el recorte.

### Qué ejecutar
- `E2` × {syn, udp, icmp, modbus} × 10 repeticiones, mismas semillas/orden y mismos parámetros que E1.
- Registra por corrida: alertas por SID, paquetes de ataque contados antes y después del IPS (deben ser ≈ iguales), carga de CPU de Suricata y paquetes perdidos en NFQUEUE.

### Criterios de aceptación
- (antes − después) ≈ 0 para el tráfico de ataque. Si no, el modo alert está descartando: anomalía.
- Tasa de detección por la definición de `definiciones_metricas.md` (por paquete y por ráfaga), con n y DE.
- Compara con E1: ¿Suricata en alert degrada o no el rendimiento respecto a E1 (sobrecoste de inspección)?

### Reglas comunes de ejecución de este prompt
- Lanza el arnés dentro de `tmux` y con `limited-run.sh`; vigila `lab/guard/lab-status.sh` cada 10 corridas. Si el guardián llega a PAUSE/ABORT, deja que el arnés pare, informa y espera.
- Tras **cada corrida** ejecuta `validate_run.py`. Una corrida FAIL o aborted se repite; las repeticiones, fallos y su causa quedan en `runs.csv` (no se borran).
- Tras la 1.ª, la 5.ª y la 10.ª repetición, mira los números: ¿tienen sentido físico y son consistentes con el piloto? Si no, **para y audita** (`05_problemas_anomalias.md`).
- Al terminar: segunda fuente sobre el conjunto (suma de paquetes de ataque antes/después del IPS frente a contadores de Suricata, por corrida; diferencia relativa mediana y máxima), resumen provisional de media y DE (solo exploratorio; las tablas finales salen de P20), entradas en `00_diario.md`, `06_logros_avances.md`, `05_problemas_anomalias.md`, `07_resultados_auditados.md` y commit (los CSV de `data/raw/` se versionan; las capturas no).
- Si algo no se pudo ejecutar, di **exactamente** qué falta y qué debe declararse como limitación; no lo sustituyas.

## FIN DEL PROMPT
