# P18 · Switch virtual: aislamiento VLAN y contadores por puerto durante el ataque

**Prioridad: RECOMENDADO (barato; cubre el título del paper)** · Tiempo de máquina estimado: ≈ 30 min (valida con el piloto de P12)
**Observaciones que cubre:** 4 (título habla de switches industriales pero no se evalúan), 10, 25

---

## PROMPT (copiar desde aquí)

Repo y rama confirmados (`pwd`, `git branch --show-current`); guardián activo y en OK; P12 aprobado por mí. Respeta `CLAUDE.md`: nada de datos inventados, dudar, segunda fuente, documentar.

### Objetivo
Aportar evidencia del papel del switch virtual (segmentación 802.1Q y contadores por puerto), y dejar explícito en el paper que es un switch virtual, no hardware industrial.

### Qué ejecutar
1. Prueba de aislamiento entre VLAN con el ataque activo (`syn` de 30 s, perfil piloto): el flood de Kali no aparece como tráfico en puertos de otra VLAN (p. ej. el puerto de `scada` en VLAN 20 no ve paquetes de ataque dirigidos al PLC ni broadcast de la VLAN 10); evidencia con `ovs-ofctl dump-ports` antes/después y captura en un puerto de otra VLAN.
2. Contadores por puerto (rx/tx paquetes, bytes, drops, errores) cada 1 s durante una corrida de E1 y de E3 por ataque, ya capturados por el arnés (`ts_1s`): extrae y resume cuántos paquetes llegan al puerto del PLC con y sin IPS.
3. Un experimento de **contención** opcional: limita el puerto del atacante con QoS/policing de OVS (`ingress_policing_rate`) y mide el efecto sobre el PLC (¿es una mitigación complementaria del switch?). Solo si hay tiempo; sería una variante E5 documentada.

### Aceptación y documentación
Tabla de contadores y veredicto sobre el aislamiento. Redacta en `docs/lab/propuesta_texto_obs4.md` la frase de limitación y la propuesta de título/abstract alineados con lo medido (decisión mía: lo apruebo yo antes de tocar el paper).

### Reglas comunes de ejecución de este prompt
- Lanza el arnés dentro de `tmux` y con `limited-run.sh`; vigila `lab/guard/lab-status.sh` cada 10 corridas. Si el guardián llega a PAUSE/ABORT, deja que el arnés pare, informa y espera.
- Tras **cada corrida** ejecuta `validate_run.py`. Una corrida FAIL o aborted se repite; las repeticiones, fallos y su causa quedan en `runs.csv` (no se borran).
- Tras la 1.ª, la 5.ª y la 10.ª repetición, mira los números: ¿tienen sentido físico y son consistentes con el piloto? Si no, **para y audita** (`05_problemas_anomalias.md`).
- Al terminar: segunda fuente sobre el conjunto (suma de paquetes de ataque antes/después del IPS frente a contadores de Suricata, por corrida; diferencia relativa mediana y máxima), resumen provisional de media y DE (solo exploratorio; las tablas finales salen de P20), entradas en `00_diario.md`, `06_logros_avances.md`, `05_problemas_anomalias.md`, `07_resultados_auditados.md` y commit (los CSV de `data/raw/` se versionan; las capturas no).
- Si algo no se pudo ejecutar, di **exactamente** qué falta y qué debe declararse como limitación; no lo sustituyas.

## FIN DEL PROMPT
