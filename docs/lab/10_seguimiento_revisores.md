# Seguimiento de los comentarios de los revisores (lado laboratorio)

**Fecha:** 2026-11-18 (UTC). **Plataforma de los datos:** `laptop-dev` (única plataforma del estudio, 130 corridas `final`).
Complementa `docs/observaciones_icits27.md` (matriz 0–26, misma numeración) y el `observaciones/registro_cambios.md` del repositorio del paper (qué se cambió en el manuscrito y en qué commit). Aquí se registra **qué evidencia tiene el laboratorio** y **qué falta en el manuscrito**. Los comentarios de los tres revisores coinciden con esas observaciones (plantilla, regla `alert`, UDP ausente, Snort, estadística, reproducibilidad, métricas, alcance del switch, novedad, atribución a Suricata frente a firewall/VLAN, y redacción y referencias).

**Fecha límite de subida:** 18 de noviembre.

Estados: **Hecho**, **Laboratorio hecho; manuscrito pendiente** (hay datos y script, falta escribirlo en el paper), **Parcial**, **Pendiente de decisión**.

| # | Comentario | Evidencia en el laboratorio | Qué falta en el manuscrito | Estado |
|---|---|---|---|---|
| 0 | Plantilla ACM → LNCS | — | Hecho en el manuscrito (`e8ccd5b`) | Hecho |
| 1, 20 | La regla usa `alert`; no hay evidencia de bloqueo ('automatic blocking enabled') | E3 en modo `drop` con 130 corridas del perfil final: contadores de `ips.blocked` y paquetes eliminados según captura (E3 syn/udp/icmp ≈ 99,7–100 %); reglas en `lab/config/ips/rules/lab.rules.in`; inline con NFQUEUE (`queue num 0-1`, D18); conservación de paquetes verificada en 80 corridas (A21, `conservacion_nfq_laptop-dev_final.csv`). Limitación: falsos positivos de la regla Modbus (A23, L8). | Reescribir §4.3 con reglas `drop` y mostrar el mecanismo inline; ajustar la tabla 'Automatic Blocking' a lo medido; citar L8. | Laboratorio hecho; manuscrito pendiente |
| 2 | UDP en la metodología y no en los resultados | UDP medido en E1, E2 y E3 (10 corridas por celda). Resultados: `09_analisis_tanda_real_laptop-dev.md`, figuras `r1`, `r2`, `r3` (`figures/paper/`). Detección UDP por flujo, no por paquete (A22). | Añadir el escenario UDP a §4.4 y §5. | Laboratorio hecho; manuscrito pendiente |
| 3 | Snort mencionado sin experimento | No se ejecutó Snort. No hay corridas ni plan de laboratorio para Snort. | Quitar Snort de la comparación y dejarlo como alternativa en la discusión (opción B de la matriz original), o justificar la exclusión. | Pendiente de decisión (recomendado: opción B, solo texto) |
| 4, 25 | Título y abstract hablan de switches industriales; solo se evalúa el PLC | Switch virtual Open vSwitch con VLAN 802.1Q: segmentación y aislamiento verificados (P06–P07). No hay medición de hardware de switch industrial (L1). | Alinear título y abstract con lo medido, o declarar el alcance: switch virtual, no hardware industrial. | Pendiente de decisión del equipo |
| 5, 23 | Sin repeticiones, desviación estándar ni IC; 'significativo' sin prueba | 10 repeticiones por celda, media, DE e IC 95 % (`stats_laptop-dev_final.csv`, `tables/stats_laptop-dev_final.tex`, `analisis_laptop-dev_final.csv`). **No hay pruebas de hipótesis** entre escenarios; los IC y los rangos solapados son lo que respalda las comparaciones. | Reportar media ± IC 95 % y n; sustituir 'significativo' por 'notable' salvo que se añada una prueba (Mann-Whitney) calculada por script. | Laboratorio parcial (IC hechos, pruebas no); manuscrito pendiente |
| 6 | Datos crudos y separación del tráfico legítimo y malicioso | Datos crudos en `data/raw/` (`runs.csv`, `runs/<id>/polls.csv`, `pcap_counts.csv`, contadores); definición de tráfico legítimo (Modbus SCADA→PLC) y malicioso (atacante→PLC) en `definiciones_metricas.md`; `pcap_count.py` separa por origen y destino. | Citar el repositorio como material suplementario y resumir la definición; decidir si el repositorio se hace público. | Laboratorio hecho; manuscrito pendiente |
| 7 | Fórmula de throughput incorrecta; RTT frente a latencia de una vía | Definiciones corregidas en `definiciones_metricas.md` (Mbps = bytes·8 / (tiempo·10⁶), sin ×100; RTT con reloj monotónico). **El throughput no está calculado en los resúmenes de la tanda.** | Corregir las fórmulas del §3.4; añadir throughput solo si se calcula con un script desde los contadores o la captura. | Parcial: definición lista, resultado de throughput pendiente |
| 8 | Tasa de detección ambigua | Definición por paquete entregado a Suricata en `definiciones_metricas.md`. Detección por corrida 80/80; por paquete solo comparable en E3 syn e icmp; UDP por flujo (A22); `decoder.pkts` mezcla sentidos (A21). | Redefinir en §3.4 y reportar detección por corrida y por flujo para UDP. | Laboratorio parcial; manuscrito pendiente |
| 9 | Novedad poco clara | Aportes demostrables con datos: laboratorio virtual reproducible (arnés, semilla, hashes); hallazgos sobre Suricata por defecto (A16, A17), saturación de NFQUEUE (A11, A21), métrica de disponibilidad por solicitud programada (A24), falsos positivos de reglas por umbral (A23). | Párrafo de contribución explícita y comparación con trabajos previos. | Pendiente (texto) |
| 10 | No se separa el efecto de Suricata del de firewall y VLAN | E1 es el caso 'firewall nftables + VLAN, sin IPS'; E2 = Suricata solo alerta; E3 = Suricata `drop`; E0 = sin ataque. Resultados comparados en el análisis (09). | Presentar E1, E2 y E3 como el desglose pedido. | Laboratorio hecho; manuscrito pendiente |
| 11 | Falta detalle experimental | Hardware (`docs/lab/plataformas/laptop-dev.md`, `01_hardware.md`), versiones (`02_software_versiones.md`, `data/raw/versions/`), RAM/vCPU de cada VM, tasas de ataque (`attacker_pps` en el análisis), repeticiones (10), perfil (warm 15 s, ataque 60 s, enfriamiento 15 s), configuración de Suricata (`lab/config/ips/`). | Tabla de configuración y de parámetros en §3. | Laboratorio hecho; manuscrito pendiente |
| 12, 13 | Futuro en el método; redacción y terminología | — | Pasar §3–§4 a pasado; corrector. En `main.tex` aún hay 'will follow' y 'will be executed' en `03_method.tex`. | Pendiente (texto); parte mecánica de obs. 13 hecha (`ef40585`) |
| 14 | Referencias duplicadas | — | Parcial en el manuscrito (`Raman2021ML` fusionada); quedan decisiones sobre `Yu2019IDS`/`sayegh2019ids`. | Parcial |
| 15, 16, 17, 18, 26 | Yung/Yu, etiquetas duplicadas, caption equivocado, números de figura a mano, restos de plantilla | — | Hechos en el manuscrito (`7dd39ba`, `f8ef56c`, `1b38940`, `5b7e58c`, `44942fd`). | Hecho |
| 19 | Figura 'PerformanceCurve' conceptual | Serie temporal medida por segundo, de `polls.csv` (figura `r3_availability_timeseries`). | Sustituir la figura conceptual por `a3` y borrar la curva normalizada. | Laboratorio hecho; manuscrito pendiente |
| 21 | % frente a pp | — | Usar pp para disponibilidad y detección en las tablas. | Pendiente (texto/tablas) |
| 22 | Comandos de Scapy y Modbus sin detallar | Comandos exactos en `definiciones_metricas.md` y `attack.txt` de cada corrida; `modbus_flood.py` (8 conexiones TCP, solicitudes válidas); tasas en pps. | Incluir comandos y tasas en §4.4. | Laboratorio hecho; manuscrito pendiente |
| 24 | Limitaciones de la virtualización | L1, L3, L4, L7 y L8 en `03_limitaciones.md`. | Resumir en §6. | Laboratorio hecho; manuscrito pendiente |
| N1 | A24: disponibilidad por solicitud emitida frente a programada | `09`, figura `r1_availability` (a y b), `definiciones_metricas.md`. | Reportar ambas métricas y el número de solicitudes emitidas. | Pendiente (texto) |
| N2 | A23/L8/D22: falsos positivos de la regla Modbus y caída del PLC tras el flood Modbus | `05_problemas_anomalias.md`, `03_limitaciones.md`, `04_decisiones.md`. | Declarar como limitación en la sección de E3. | Declarado en el laboratorio; manuscrito pendiente |
| N3 | A20: arranque frío en 7 corridas y campos térmicos vacíos | L7, `runs_guard_muestras_laptop-dev_final.csv`. | Nota en limitaciones. | Declarado en el laboratorio; manuscrito pendiente |
| N4 | A22: alertas UDP por flujo | `05`, `09`. | Explicar la detección UDP por flujo. | Declarado en el laboratorio; manuscrito pendiente |
| N5 | Legibilidad de las figuras (comentario de los revisores) | Figuras regeneradas por script al ancho de LNCS y revisadas (ver `11_auditoria_scripts_y_figuras.md`). | Sustituir las capturas actuales por las figuras generadas. | En curso |

## Resumen
- **Hecho:** 0, 15–18, 26.
- **Laboratorio hecho, manuscrito pendiente:** 1, 2, 6, 10, 11, 19, 20, 22, 24 y los hallazgos nuevos N1–N4.
- **Parcial:** 5, 7, 8, 14, 23.
- **Pendiente de decisión del equipo:** 3 (Snort) y 4/25 (título y alcance del switch).
- **Solo texto:** 9, 12, 13, 21.

## Cómo se mantiene
Al cerrar un punto en el manuscrito, cambiar su estado aquí y en `registro_cambios.md` (con el hash del commit). Cualquier número del paper debe salir de `data/processed/analisis_laptop-dev_final.csv` y de los scripts de `lab/analysis/`.
