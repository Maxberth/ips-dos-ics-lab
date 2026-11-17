# P12 · Piloto corto y primera auditoría: ¿la cadena de medición es creíble?

**Prioridad: IMPRESCINDIBLE** · Tiempo: 45–75 min (incluye enfriamiento)
**Observaciones:** 1, 20 (evidencia de bloqueo), 6, 8, 5. **Puerta de calidad antes de las 40+ corridas.**

---

## PROMPT (copiar desde aquí)

Repo y rama confirmados; guardián activo; arnés de P11 listo. Respeta `CLAUDE.md`. Este paso decide si la medición es defendible: **desconfía de tus propios resultados**.

### 1. Piloto (perfil `piloto`, una repetición de cada combinación)
Corre `E0`, `E1`, `E2`, `E3` × {`syn`, `udp`, `icmp`, `modbus`}. Entre corridas, el arnés enfría y comprueba salud. Si el guardián sube a PAUSE/ABORT, detente y reporta. Si algún ataque tumba la VM o la cadena, documéntalo (puede ser un hallazgo, no un error: anótalo en `06_logros_avances.md` y en anomalías).

### 2. Auditoría cruzada (cada punto con evidencia numérica; guarda en `docs/lab/auditoria_piloto.md`)
1. **Segunda fuente de bloqueo (clave para obs. 1 y 20):** en `E3`, compara (a) paquetes de ataque contados en la captura **antes** del IPS (VLAN 20), (b) paquetes de ataque contados **después** (VLAN 30), (c) `ips.drop`/`nfq` y alertas `drop` de Suricata, (d) contadores del puerto OVS del PLC. Esperado: (a) − (b) ≈ (c). Informa la diferencia relativa; si > 5 %, es una anomalía a explicar (pérdida de captura, drops de NFQUEUE por saturación, paquetes en vuelo).
2. **E2 (alert) no debe descartar:** (a) ≈ (b); si no, el modo alert está bloqueando por error.
3. **E1:** sin reglas de IPS, (a) ≈ (b); las diferencias vienen de la saturación de la ruta, no de reglas.
4. **Tráfico legítimo:** cuántas solicitudes Modbus válidas se perdieron, y si alguna coincide con un `drop` de Suricata (falso positivo). Una regla que bloquea el SCADA invalida el escenario.
5. **El ataque realmente ocurrió:** pps efectivos de Kali (host y VM), no solo "el comando se ejecutó". Compara con el rendimiento máximo esperado del bridge virtual.
6. **El generador no contamina:** CPU de `kali` y de los hilos del host durante el ataque; temperatura máxima; ¿el `scada_poller` pierde datos por falta de CPU en su propia VM y no por el ataque? (comprueba CPU de `scada`).
7. **Causalidad:** cada variable (latencia, disponibilidad, pérdida) tiene una explicación mecánica plausible (p. ej. SYN flood ⇒ cola SYN/backlog del PLC ⇒ timeouts) y no es artefacto (reloj, buffers de captura, offloading).
8. **Valores imposibles o sospechosos** (disponibilidad > 100 %, RTT negativo, pérdidas exactamente 0 o 100 % en todas las corridas, desviación 0): sospecha un fallo de medición.
9. Resultados **inesperados** (p. ej. sin diferencia E1 vs E3): no los "arregles"; investiga si falla la regla, el umbral o la cadena, o si el hallazgo es genuino, y decide conmigo.

### 3. Entregables
- `docs/lab/auditoria_piloto.md` con tabla: control | resultado | veredicto (OK / ANOMALÍA / INCIERTO) | evidencia (ruta del CSV/log).
- Ajustes necesarios a reglas/umbrales/arnés (con su justificación en `04_decisiones.md` y re-ejecución del piloto afectado).
- Estimación **medida** del tiempo por corrida y del tiempo total del plan final (480 min estimados en el documento de requisitos → valor real): dime si cabe antes del 18 de noviembre y propón el recorte de alcance necesario (ver README).
- Diario, anomalías, commit.

### Puerta de calidad
Solo pasa a las corridas finales si: (1) el punto 1 coincide dentro de la tolerancia o la discrepancia está explicada, (2) no hay falsos positivos sobre el SCADA, (3) el guardián no pasó de WARN de forma sostenida. De lo contrario, dime qué corregir. **Espera mi OK para P13.**

## FIN DEL PROMPT
