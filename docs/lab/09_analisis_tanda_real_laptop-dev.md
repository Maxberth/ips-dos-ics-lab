# Análisis de la tanda real (laptop-dev, perfil `final`)

- **Fecha:** 2026-11-18 (UTC). **Plataforma:** `laptop-dev` (Ryzen 5 6600H, 14,8 GiB). **Datos:** 130 corridas `status=ok` del 2026-11-17 21:26 al 2026-11-18 04:15 UTC (10 por celda: E1 y E3 × syn, udp, icmp, modbus; E2 × los mismos cuatro; E0 sin ataque).
- **Alcance (L3):** son datos de **calibración**. No se mezclan con `pc-miguel` ni van a tablas o figuras del paper.
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

## 4. Segunda fuente y anomalía abierta (A21)

El cociente entre los descartes que ve Suricata/NFQUEUE y los paquetes que desaparecen entre la VLAN 20 y la 30 en la captura es 1,00 en E3 y en E2 udp, pero **1,29–1,39 en E2 syn e icmp (A21, sin explicar)**. Hasta resolverla, el "% de ataque eliminado" y la parte por saturación de esas dos celdas (figura `a4_eliminacion_ips.png`) no deben citarse como resultado. La disponibilidad y el RTT no dependen de esos contadores.

## 5. Qué falta
1. Explicar A21 comparando captura, nftables y NFQUEUE corrida por corrida.
2. Tasa de detección por regla (`detect.alert` / paquetes entregados a Suricata) en E2/E3, aún sin analizar aquí.
3. Decidir si se añaden corridas E3 ICMP adicionales (reps 11+) para cerrar la duda de A20.
4. Repetir el análisis con `pc-miguel`; los números del paper salen solo de esa plataforma.
5. Revisar `07_resultados_auditados.md` con estos resultados y los WARN.
