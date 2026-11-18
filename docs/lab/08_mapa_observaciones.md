# Mapa de observaciones

> **Documento histórico:** mapa inicial de observaciones por paso del plan. Sus estados de «medir en pc-miguel» quedaron superados; el estado vigente de cada observación está en `10_seguimiento_revisores.md`.

Observación del revisor (0–26, ver `docs/observaciones_icits27.md`) → evidencia → sección del paper.

| Obs. | Evidencia en este repo | Paso | Estado |
|---|---|---|---|
| 1, 20 | Descarte real: `check_chain.sh` (drop 0/5); cuadre (a)−(b) ≈ (c)+(d) en `auditoria_piloto_laptop-dev.md` | P09, P12 | Calibrado en laptop-dev; medir en pc-miguel |
| 2 | UDP flood medido en E1/E2/E3 (piloto) | P12 | Calibrado; medir ×10 en pc-miguel |
| 4, 25 | Switch virtual OVS, aislamiento VLAN y de gestión verificados | P06, P07 | Hecho (laptop-dev); repetir en pc-miguel |
| 5 | Arnés con repeticiones, semilla y validación; variabilidad observada (88–93 %) | P11, P12 | Pendiente: ×10 en pc-miguel |
| 6, 7, 8 | `definiciones_metricas.md` (RTT, disponibilidad, throughput sin ×100, detección por paquete entregado) | P10 | Hecho |
| 10 | E1 (solo firewall) frente a E3; además separa reglas, saturación (A11) y mecanismos por defecto (A16, A17) | P12 | Calibrado |
| 11 | Tabla de VMs (`P07_verificacion_vms_*.txt`), versiones (`data/raw/versions/`), parámetros de Suricata | P05, P07 | laptop-dev hecho; pc-miguel pendiente |
| 22 | Comandos exactos de cada ataque (`definiciones_metricas.md`, `attack.txt`) | P11 | Hecho |
| 24 | CPU del PLC dentro de la VM (`plc_pidstat.txt`) y desde el host | P11 | Hecho |
