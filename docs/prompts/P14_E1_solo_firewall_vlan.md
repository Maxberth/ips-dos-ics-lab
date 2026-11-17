# P14 · Escenario E1: solo firewall/VLAN (sin IPS), todos los ataques × 10

**Prioridad: IMPRESCINDIBLE** · Tiempo de máquina estimado: ≈ 1–1,5 h (60 s de ataque) (valida con el piloto de P12)
**Observaciones que cubre:** 10 (separar efecto firewall/VLAN de Suricata), 2 (UDP), 5, 6, 11, 22

---

## PROMPT (copiar desde aquí)

Repo y rama confirmados (`pwd`, `git branch --show-current`); guardián activo y en OK; P12 aprobado por mí. Respeta `CLAUDE.md`: nada de datos inventados, dudar, segunda fuente, documentar.

### Objetivo
Esta es la condición "sin IPS" del paper: firewall y segmentación activos, IPS solo enrutando (modo router). Sirve de contraste directo con E2/E3 y responde a la pregunta de atribución del revisor.

### Qué ejecutar
- `E1` × {syn, udp, icmp, modbus} × 10 repeticiones, perfil `final`, orden aleatorio con semilla (arnés P11).
- Registra además contadores de reglas del firewall (cuántos paquetes pasaron) y los del puerto OVS del PLC.

### Criterios de aceptación
- Los cuatro ataques ocurren realmente (pps efectivos ≈ constantes entre repeticiones; documenta la variabilidad).
- Se observa o **no se observa** degradación del servicio Modbus; si no hay degradación en algún ataque, documenta por qué (puede ser un hallazgo, p. ej. un PLC simulado robusto a UDP). No ajustes tasas para forzar un resultado; si cambias tasas, es un nuevo perfil documentado con justificación técnica previa a ver el resultado.
- Tabla exploratoria: por ataque, disponibilidad, RTT p50/p95, pérdida, CPU del PLC (guest y host), con n, media y DE.

### Reglas comunes de ejecución de este prompt
- Lanza el arnés dentro de `tmux` y con `limited-run.sh`; vigila `lab/guard/lab-status.sh` cada 10 corridas. Si el guardián llega a PAUSE/ABORT, deja que el arnés pare, informa y espera.
- Tras **cada corrida** ejecuta `validate_run.py`. Una corrida FAIL o aborted se repite; las repeticiones, fallos y su causa quedan en `runs.csv` (no se borran).
- Tras la 1.ª, la 5.ª y la 10.ª repetición, mira los números: ¿tienen sentido físico y son consistentes con el piloto? Si no, **para y audita** (`05_problemas_anomalias.md`).
- Al terminar: segunda fuente sobre el conjunto (suma de paquetes de ataque antes/después del IPS frente a contadores de Suricata, por corrida; diferencia relativa mediana y máxima), resumen provisional de media y DE (solo exploratorio; las tablas finales salen de P20), entradas en `00_diario.md`, `06_logros_avances.md`, `05_problemas_anomalias.md`, `07_resultados_auditados.md` y commit (los CSV de `data/raw/` se versionan; las capturas no).
- Si algo no se pudo ejecutar, di **exactamente** qué falta y qué debe declararse como limitación; no lo sustituyas.

## FIN DEL PROMPT
