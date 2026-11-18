# Resultados auditados

Solo resultados con segunda fuente concordante. Cada tabla indica su plataforma; no se mezclan plataformas. Plataforma de todos los resultados: `laptop-dev`, perfil `final` (130 corridas).

| Resultado | Segunda fuente | Evidencia |
|---|---|---|
| Disponibilidad por solicitud emitida y programada | Recálculo independiente desde `polls.csv` (diferencia máxima 0,005 puntos) | `docs/lab/logs/figuras_integridad_laptop-dev.txt` |
| Ataque eliminado antes de la red del PLC | Captura en dos espejos frente a contadores de nftables, NFQUEUE y Suricata (cociente 1,0000–1,0001 en las 80 corridas E2/E3) | `data/processed/conservacion_nfq_laptop-dev_final.csv`, A21 |
| PLC caído tras la corrida | Archivo `plc_health.txt` de cada corrida frente al resumen | `verificar_figuras.py` (0 inconsistencias) |
| Temperatura máxima y frecuencia | Muestras por segundo del guardián y de `ts_host.csv` | `data/raw/guard/`, A19 |
| Alertas UDP por flujo | Registro completo de alertas en una corrida de calibración | A22, `data/raw/runs/*C2_udp_piloto_r1/` |

Análisis completo en [`09_analisis_tanda_real_laptop-dev.md`](09_analisis_tanda_real_laptop-dev.md). Los resultados no auditados o sin segunda fuente (por ejemplo, los falsos positivos de la regla Modbus fuera de las 4 corridas de calibración) se declaran como tales en `03_limitaciones.md`.
