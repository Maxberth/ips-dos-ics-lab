# Logros y avances

Qué quedó verificado y con qué evidencia.

## laptop-dev, 2026-11-17
- **P01–P11:** laboratorio completo montado y verificado (`check_chain.sh` 23/23). Descarte real demostrado: drop 0/5 ecos al PLC, alert 5/5, eve.json con `blocked`, fail-closed.
- **P12:** piloto de 4 escenarios × 4 ataques con auditoría cruzada (`auditoria_piloto_laptop-dev.md`).
  - El firewall, la captura antes y después del IPS, Suricata y NFQUEUE cuadran.
  - Se identificaron y separaron tres mecanismos de "prevención" que no son reglas: el desbordamiento de cola NFQUEUE (A11, A14), la política de excepciones del parser Modbus (A16) y `stream.drop-invalid` (A17).
  - El Modbus flood tumba OpenPLC de forma reproducible sin prevención (A15, A18).
- **Arnés robusto:** límites de memoria para todo el post-proceso (A10), salud del PLC en cada corrida, `--resume` de la matriz y validación automática.
