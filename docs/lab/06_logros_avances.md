# Logros y avances

Qué quedó verificado y con qué evidencia.

## laptop-dev, 2026-11-17
- **P01–P11:** laboratorio completo montado y verificado (`check_chain.sh` 23/23). Descarte real demostrado: drop 0/5 ecos al PLC, alert 5/5, eve.json con `blocked`, fail-closed.
- **P12:** piloto de 4 escenarios × 4 ataques con auditoría cruzada (`auditoria_piloto_laptop-dev.md`).
  - El firewall, la captura antes y después del IPS, Suricata y NFQUEUE cuadran.
  - Se identificaron y separaron tres mecanismos de "prevención" que no son reglas: el desbordamiento de cola NFQUEUE (A11, A14), la política de excepciones del parser Modbus (A16) y `stream.drop-invalid` (A17).
  - El Modbus flood tumba OpenPLC de forma reproducible sin prevención (A15, A18).
- **Arnés robusto:** límites de memoria para todo el post-proceso (A10), salud del PLC en cada corrida, `--resume` de la matriz y validación automática.

## laptop-dev, 2026-11-17 a 2026-11-18: tanda real y análisis
- **Tanda real:** 130 corridas finales (E0, E1, E2 y E3 × SYN, UDP, ICMP y Modbus, 10 repeticiones), todas `status=ok`, en 5 bloques con commit por bloque; 6 h 29 min de ejecución (`09_analisis_tanda_real_laptop-dev.md`).
- **Defecto del control térmico (A20):** el arnés buscaba el CSV del guardián por la fecha UTC y no lo encontraba pasada la medianoche; corregido, con 7 corridas con campos térmicos vacíos que se declaran (L7).
- **Segunda fuente:** conservación de paquetes entre nftables, NFQUEUE y Suricata verificada en las 80 corridas E2/E3 (A21) y recálculo independiente de las métricas de las 130 corridas (`verificar_figuras.py`, resultado COHERENTE).
- **Calibraciones con registro completo de alertas:** UDP genera una alerta por flujo (A22) y la regla Modbus descarta paquetes del SCADA al final del ataque (A23).
- **Métrica de disponibilidad:** el cliente es de lazo cerrado; se reporta por solicitud emitida y por solicitud programada (A24).
- **Artículo:** tablas y figuras generadas por script (`tablas_paper.py`, `figuras_paper.py`, `figuras_arquitectura.py`) y seguimiento de los comentarios de los revisores (`10_seguimiento_revisores.md`).

