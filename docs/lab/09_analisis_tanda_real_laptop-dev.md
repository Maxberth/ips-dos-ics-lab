# Análisis de la tanda real (laptop-dev, perfil `final`)

- **Fecha:** 2026-11-18 (UTC). **Plataforma:** `laptop-dev` (Ryzen 5 6600H, 14,8 GiB). **Datos:** 130 corridas `status=ok` del 2026-11-17 21:26 al 2026-11-18 04:15 UTC (10 por celda: E1 y E3 × syn, udp, icmp, modbus; E2 × los mismos cuatro; E0 sin ataque).
- **Alcance (L3):** `laptop-dev` es la única plataforma del estudio (decisión del 2026-11-18). Estas 130 corridas del perfil `final` son la base de los resultados del paper, con los límites de L1 y L3. Las corridas piloto y reducidas no entran.
- **Reproducible:** todo sale de `data/raw/` y `data/processed/run_summary_laptop-dev_final.csv` con `python3 -I lab/analysis/analisis_final.py --platform laptop-dev --profile final` (tabla agregada en `data/processed/analisis_laptop-dev_final.csv`) y `lab/analysis/stats_tables.py`. Ningún número de este texto está fuera de esos archivos.
- **Definiciones:** `docs/lab/definiciones_metricas.md`. Disponibilidad = % de solicitudes Modbus del SCADA (10 Hz) con respuesta válida en ≤ 500 ms durante los 60 s de ataque.

## 1. Resultados principales

| Escenario | Ataque | Disponibilidad media % [mín–máx] | RTT mediana ms | RTT p95 ms | PLC caído tras la corrida |
|---|---|---|---|---|---|
| E0 | ninguno | 100 [100–100] | 0,78 | 0,9 | 0/10 |
| E1 (IPS router) | syn | 99,2 [98,7–99,8] | 19,6 | 259,8 | 0/10 |
| | udp | 100 [100–100] | 0,69 | 4,3 | 0/10 |
| | icmp | 100 [99,8–100] | 10,5 | 21,0 | 0/10 |
| | modbus | 100 [100–100] | 1,79 | 2,0 | **10/10** |
| E2 (Suricata alert) | syn | **3,4 [1,7–5,8]** | 245,4 | 358,8 | 0/10 |
| | udp | 66,7 [30,0–85,2] | 32,3 | 248,6 | 0/10 |
| | icmp | 49,1 [2,5–82,9] | 139,7 | 203,1 | 0/10 |
| | modbus | 99,7 [99,7–99,8] | 0,53 | 0,9 | **10/10** |
| E3 (Suricata drop) | syn | 75,8 [63,9–83,3] | 9,75 | 310,4 | 0/10 |
| | udp | 73,3 [62,2–82,7] | 9,64 | 345,6 | 0/10 |
| | icmp | 77,3 [59,0–86,1] | 5,43 | 391,2 | 0/10 |
| | modbus | 100 [100–100] | 0,86 | 1,1 | **6/10** |

Figuras: `figures/laptop-dev_final_a1_disponibilidad.png`, `a2_rtt_p95.png`, `a3_disponibilidad_en_el_tiempo.png`.

## 2. Lectura de los resultados (sin generalizar más allá de esta plataforma)

1. **E0 es la línea base limpia:** 100 % y RTT de 0,78 ms.
2. **E1 (IPS en modo router, sin Suricata) aguanta casi todo:** solo el SYN flood le cuesta algo (99,2 %, RTT p95 de 260 ms).
3. **E2 es el peor caso para syn, udp e icmp**, con disponibilidad de 3,4 %, 66,7 % y 49,1 %. El ancho de las celdas es grande (udp 30–85 %, icmp 2,5–83 %), así que la media sola es engañosa. Con Suricata en línea la ruta pasa por NFQUEUE, que se satura (ver §4).
4. **E3 mejora a E2 pero no restaura el servicio:** ~73–77 % en los tres floods, con RTT p95 de 310–390 ms. Las reglas eliminan ~100 % del ataque (según la captura), aunque durante los 60 s el SCADA sigue perdiendo cerca de una cuarta parte de las solicitudes. Los dos flujos comparten la cola de Suricata.
5. **Modbus flood:** no reduce la disponibilidad durante el ataque (≈100 % en las tres), pero **el runtime de OpenPLC termina al acabar el ataque** (A15/A18): 10/10 en E1, 10/10 en E2 y 6/10 en E3. En E3 el atacante apenas transmite (46 pps de media) porque la regla corta el flujo; aun así el PLC cayó en 6 de 10. Figura `a3` (panel modbus): la disponibilidad cae a 0 justo tras el segundo 60.
6. **RTT en E2 icmp/udp** (figura `a2`): los puntos de RTT bajo corresponden a corridas casi sin respuestas, así que el RTT solo describe las pocas que llegaron.

## 3. Térmica y calidad de la medición

- Tctl máximo de 81,4 °C (umbral PAUSE 88 °C). La frecuencia de CPU sube con la carga: ~3,3 GHz en el calentamiento y ~4,1–4,2 GHz durante el ataque. **No hay throttling** (figura `a5_termica.png`; coherente con A19).
- Todas las corridas finales tienen `status=ok`, pero la mayoría trae WARN: descarte de la captura (dumpcap) y huecos >250 ms en el poller. **El descarte llega a 13,8 % en E1 syn y 9,5 % en E1 icmp**, por lo que `% eliminado` en E1 (≈2 %) refleja el descarte de la captura y no un efecto del IPS (en router no elimina nada). En E2/E3 el descarte máximo es 2,2 %.
- **A20 (arranque frío en 6 corridas, y 1 más con campos vacíos):** ver `05_problemas_anomalias.md` y L7. La comparación con el resto no mostró diferencia en E1; en E3 ICMP la disponibilidad fue algo menor (n pequeño, rangos solapados; figura `a6`). No se concluye nada y no se repitieron.

## 4. Segunda fuente y anomalía A21 (explicada)

El cociente entre los descartes de Suricata/NFQUEUE y los paquetes que desaparecen entre la VLAN 20 y la 30 en la captura era 1,00 en E3 y E2 udp y 1,29–1,39 en E2 syn e icmp. **La causa es el sentido del tráfico:** las colas reciben también las respuestas del PLC y la captura solo cuenta atacante→PLC. Comprobación independiente en las 80 corridas E2/E3: entradas a la cola (`c_fwd_v20_v30 + c_fwd_v30_v20`) = `queue_dropped + blocked + accepted`, con cociente 1,0000–1,0001 (`data/processed/conservacion_nfq_laptop-dev_final.csv`). Los tres conjuntos de contadores son coherentes.

Consecuencias: el "% de ataque eliminado" válido es el de la captura (figura `a4_eliminacion_ips.png`). La parte "por saturación" (`sat_pct`) solo es utilizable en E3 syn/udp/icmp (sentido inverso casi nulo); en E2 syn/icmp mezcla ambos sentidos y no se cita. Detalle en A21.

## 5. Detección por regla (E2 y E3)

Reglas en `lab/config/ips/rules/lab.rules.in` (`detection_filter` por origen: syn 100/s, udp 100/s, icmp 50/s, modbus 20/s). Datos: `suri_alerts` y `suri_decoder_pkts` por corrida, deltas de `suricata_stats.jsonl` (`data/processed/analisis_laptop-dev_final.csv`).

| Escenario | Ataque | Corridas con ≥1 alerta | Alertas (media) | Paquetes de Suricata (media) | alertas / paquetes |
|---|---|---|---|---|---|
| E2 | syn | 10/10 | 3,37 M | 4,52 M | 74,6 % |
| E2 | udp | 10/10 | 65 480 | 4,85 M | 1,35 % |
| E2 | icmp | 10/10 | 3,73 M | 5,16 M | 72,3 % |
| E2 | modbus | 10/10 | 163 110 | 0,67 M | 24,3 % |
| E3 | syn | 10/10 | 5,89 M | 5,90 M | 99,8 % |
| E3 | udp | 10/10 | 65 464 | 5,68 M | 1,15 % |
| E3 | icmp | 10/10 | 5,87 M | 5,88 M | 99,9 % |
| E3 | modbus | 10/10 | 860 | 0,01 M | 11,1 % |

- **Detección a nivel de corrida:** las reglas alertan en las 80 corridas E2/E3, sin falsos negativos por corrida.
- **Límites de la tasa por paquete:** `decoder.pkts` incluye también el sentido inverso (respuestas del PLC, ver A21) y el tráfico del SCADA, así que `alertas/paquetes` en E2 syn/icmp (≈73 %) no es una tasa de detección del ataque; en E3, donde casi no hay respuestas, sí se acerca a 100 % para syn e icmp.
- **UDP es distinto (A22, explicada con una corrida de calibración):** el número de alertas es casi constante (~65,5 k, rango 65 302–65 638) aunque a Suricata lleguen 4,9–5,7 M de paquetes porque **se genera una alerta por flujo UDP (por puerto de origen distinto)** y no una por paquete (en la calibración: 64 982 alertas UDP, 64 982 puertos de origen distintos, todas en los primeros ~5 s). Por eso para UDP se reporta detección por corrida (10/10) y por flujo, no por paquete. No se explica por qué Suricata no vuelve a alertar en un flujo ya visto.
- **Posible falso positivo (A23, abierta):** en esa misma calibración la regla Modbus alertó 216 veces contra tráfico legítimo del SCADA al final del ataque. Una sola corrida, sin cuantificar en la tanda.
- **Qué no se puede medir con estos datos:** `eve.json` solo guarda estadísticas cada segundo, no cada alerta, así que no hay tiempo hasta la primera alerta ni falsos positivos por paquete del tráfico legítimo.

## 6. Qué falta
1. Decidir si se añade un contador de descartes por sentido (hoy no separable) para citar la saturación en E2.
2. Investigar A23 (alertas de la regla Modbus sobre el SCADA) con una calibración en modo `drop`, por si afecta la disponibilidad de E3.
3. (Descartado) No se repiten ni se añaden corridas por A20.
5. Revisar `07_resultados_auditados.md` con estos resultados y los WARN.
