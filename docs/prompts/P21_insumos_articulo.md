# P21 · Consolidar la documentación como insumo del artículo

**Prioridad: IMPRESCINDIBLE** · Tiempo: 30–45 min
**Observaciones:** 11 (tabla de configuración), 24 (limitaciones), 12 (pasado vs futuro), 6, 9 (contribución FOSS), 4, 25.

---

## PROMPT (copiar desde aquí)

Repo y rama confirmados. Respeta `CLAUDE.md`. **No modifiques el `main.tex` del paper todavía**: solo redacta insumos en `docs/lab/paper_inputs/`, en inglés académico (el paper es en inglés) con una versión breve en español para mi revisión. Todo debe salir de la documentación y de los datos reales; marca con `[PENDIENTE]` lo que no tenga evidencia.

Genera estos archivos:
1. `tabla_configuracion.md` y `.tex`: VMs (SO, vCPU, RAM, disco, núcleos fijados), host (CPU, RAM, kernel), versiones de Suricata, Snort, OpenPLC (commit), Open vSwitch, libvirt/QEMU, firewall, hping3, Scapy, pymodbus, tasa de ataque (pps efectivos observados), duración, repeticiones, herramientas de medición (obs. 11).
2. `metodologia_pasado.md`: descripción del montaje y del procedimiento **en pasado** tal como se ejecutó realmente (no como se planeó), con las desviaciones (duración 60 s vs 5 min, SCADA en VLAN 20, IPs reales, firewall A/B, Snort sí/no) (obs. 12).
3. `limitaciones.md`: lista final depurada desde `03_limitaciones.md` (PLC simulado y CPU en VM, switch virtual, un solo host, atacante de una sola IP, n = 10, floods acotados, posible contaminación de CPU entre VMs, temperatura) (obs. 24).
4. `definiciones_metricas_paper.md`: texto corregido de §3.4 (throughput sin ×100, RTT, detección, disponibilidad, tráfico legítimo vs malicioso) (obs. 6, 7, 8).
5. `reglas_suricata_paper.md`: las reglas `drop` finales, el modo NFQUEUE y un extracto literal de `eve.json` con eventos de bloqueo (obs. 1, 20).
6. `contribucion_foss.md`: borrador del párrafo de contribución: laboratorio reproducible 100 % FOSS (KVM, OVS, Suricata, OpenPLC, nftables), qué se mide, qué no se afirma; y una lista de 3–4 trabajos para la tabla comparativa **solo con referencias que yo valide** (no inventes citas; marca `[VERIFICAR DOI]`) (obs. 9).
7. `propuesta_titulo_abstract.md`: título/abstract alineados con lo medido (obs. 4, 25), con las afirmaciones respaldadas por IC y sin "significativo" sin prueba (obs. 23). Propón, yo decido.
8. `reproducibilidad.md`: cómo repetir el laboratorio (comandos, versiones, hashes) y qué se publicará como material suplementario (CSV de `data/raw/`, scripts, reglas). Sin secretos.

Cada archivo cita al final las rutas de evidencia (CSV, logs, figuras). Diario y commit.

## FIN DEL PROMPT
