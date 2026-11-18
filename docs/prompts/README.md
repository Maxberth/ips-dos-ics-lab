# Prompts del laboratorio ICITS'27 (IPS contra DoS en redes de control industrial)

> **Documento histórico:** estos prompts se usaron para construir el laboratorio y su plan inicial difiere del resultado final: no se usó Kali (el atacante es Debian 13 con `hping3` y un script de Python), no se usó pfSense (el firewall es nftables), Snort no se evaluó y las mediciones salieron de `laptop-dev`. El estado real está en `docs/lab/00_diario.md`.

Serie de prompts **secuenciales** para pegar en Claude Code, uno a la vez, dentro del repo `ips-dos-ics-lab` (carpeta `articulo/`, junto a `paper/`). Los prompts montan y ejecutan el laboratorio; no los he ejecutado, solo están redactados. Cada uno termina con una verificación y no debe pasarse al siguiente si algo queda en "NO CUMPLE".

## Arquitectura acordada (una sola máquina, todo virtual, 100 % libre)
- Host: CachyOS (Arch), Ryzen 5 5600X 6c/12t, 24 GB RAM, NVMe. Sin NIC nuevas.
- KVM/libvirt + **Open vSwitch** `ovs-ot` sin puertos físicos, 3 VLAN estilo Purdue: 10 (IT/atacante), 20 (DMZ/SCADA), 30 (PLC).
- Kali (hping3, scapy) → firewall (pfSense CE, o nftables como alternativa) → **IPS en línea, enrutado** (Suricata, NFQUEUE, reglas `drop`; Snort 3 como comparación) → OpenPLC con proceso simulado. SCADA/cliente pymodbus en VLAN 20.
- Medición **fuera de banda** en el host (mirror/taps de OVS, tcpdump) como segunda fuente.
- Presupuesto: VMs ≈ 8–9 GiB con tope duro (`machine.slice`), reserva del host ≥ 6 GiB, un núcleo físico para el host, guardián de RAM/swap/temperatura con PAUSE y ABORT.

## Escenarios
| Id | Condición | Para qué |
|---|---|---|
| E0 | Base, sin ataque | Referencia y sobrecoste del IPS |
| E1 | Solo firewall/VLAN (IPS solo enrutando) | La condición "sin IPS" del paper; separa firewall de Suricata |
| E2 | Suricata en línea, `alert` | Muestra que alert no previene |
| E3 | Suricata en línea, `drop` | Prevención real |
| E4 | Snort 3 en línea, `drop` (opcional) | Comparación |
Ataques en cada uno: SYN flood al 502, UDP flood, ICMP flood y Modbus flood. 10 repeticiones, orden aleatorio con semilla, media, DE e IC 95 %.

## Índice y prioridad
Leyenda: **I** = imprescindible, **R** = recomendado, **O** = opcional.

| Prompt | Contenido | Prio. | Observaciones que cubre |
|---|---|---|---|
| [P01](P01_repo_y_reglas.md) | Confirmar ruta del repo, estructura `docs/lab/`, `CLAUDE.md` con reglas permanentes | I | base de trazabilidad |
| [P02](P02_estado_hardware.md) | Estado del hardware (solo lectura): RAM, temperatura, KVM, IOMMU, reinicios previos | I | 11, 24 |
| [P03](P03_dependencias.md) | Dependencias presentes y faltantes, plan de instalación (sin instalar) | I | 3, 11 |
| [P04](P04_guardarrailes_ram_temp.md) | Límites cgroups/systemd, oomd, guardián de RAM/swap/temperatura, pruebas seguras | I | 11, 24 |
| [P05](P05_instalacion_paquetes.md) | Instalación de paquetes por grupos con verificación | I | 1, 3, 11 |
| [P06](P06_red_ovs_vlan.md) | OVS, VLAN 10/20/30, mirror, aislamiento | I | 4, 10, 11 |
| [P07](P07_vms_base.md) | VMs con límites duros, cloud-init, snapshots | I | 11, 24 |
| [P08](P08_firewall.md) | Firewall (pfSense o nftables), política E1 | I | 4, 10 |
| [P09](P09_ips_en_linea.md) | Suricata inline NFQUEUE, reglas alert/drop, prueba de descarte real | I | 1, 8, 20 |
| [P10](P10_plc_scada_trafico_legitimo.md) | OpenPLC, SCADA pymodbus, definiciones de métricas | I | 6, 7, 8, 22, 24 |
| [P11](P11_arnes_de_medicion.md) | Arnés de corridas, CSV crudos con metadatos, validación | I | 5, 6, 11, 22 |
| [P12](P12_piloto_y_auditoria_cadena.md) | Piloto y auditoría cruzada (puerta de calidad) | I | 1, 5, 6, 8, 20 |
| [P13](P13_E0_linea_base.md) | E0 base ×10 | I | 5, 6, 7, 11 |
| [P14](P14_E1_solo_firewall_vlan.md) | E1 solo firewall/VLAN, 4 ataques ×10 | I | 2, 5, 6, 10, 22 |
| [P15](P15_E2_suricata_alert.md) | E2 Suricata `alert` ×10 | R | 1, 8, 10, 20 |
| [P16](P16_E3_suricata_drop.md) | E3 Suricata `drop`, 4 ataques ×10 | I | 1, 2, 5, 6, 8, 20 |
| [P17](P17_E4_snort_opcional.md) | E4 Snort 3 inline | O | 3 |
| [P18](P18_switch_ovs_contadores.md) | Aislamiento VLAN y contadores del switch | R | 4, 25 |
| [P19](P19_series_temporales.md) | Series temporales medidas (reemplazan figura conceptual) | R | 19 |
| [P20](P20_estadistica_y_graficos.md) | Scripts de estadística, tablas LaTeX y gráficos | I | 5, 16, 18, 19, 21, 23 |
| [P21](P21_insumos_articulo.md) | Insumos redactados para el paper (tabla de configuración, métricas, reglas, limitaciones) | I | 4, 6–9, 11, 12, 24, 25 |
| [P22](P22_auditoria_final_y_mapeo.md) | Auditoría final y mapa observación → evidencia → sección | I | 0–26 |
| [CLOUD](CLOUD_variante_EC2.md) | Variante para servidor EC2/KVM/contenedores y diferencias de comandos | O | 11, 24 |

Las observaciones solo de texto, plantilla o bibliografía (0, 9, 12–15, 17, 18, 23, 26 y parte de 7, 21) **no las resuelve el laboratorio**; P21 y P22 entregan los insumos y el mapa de qué editar.

## Cómo usarlos
1. Abre Claude Code en tu PC, pega el bloque "PROMPT" de un archivo y espera a que termine. Revisa el veredicto CUMPLE/NO CUMPLE antes del siguiente.
2. P01 crea `CLAUDE.md` con las reglas permanentes (no inventar datos, dudar, segunda fuente, límites de recursos), así que los prompts siguientes son más cortos y heredan las reglas.
3. Toda la documentación queda en `docs/lab/*.md` (hardware, versiones, limitaciones, decisiones, problemas, logros, resultados auditados), y los datos crudos en `data/raw/*.csv`, que son tu fuente para el artículo.
4. Los prompts piden tu confirmación antes de cualquier `sudo` y en las decisiones que cambian el estudio.

## Tiempo y recorte de alcance (entrega 18 de nov)
Estimación de máquina con perfil `final` (ataque de 60 s, 10 repeticiones, ≈ 90 s por corrida con calentamiento y enfriamiento, más esperas térmicas): E0 ≈ 0,5 h, E1 ≈ 1,5 h, E3 ≈ 1,5 h, E2 ≈ 1,5 h, E4 ≈ 1,5 h, series ≈ 0,5 h. **Total ≈ 5–8 h de corridas**, aparte del montaje y la depuración (P05–P12), que es el cuello de botella real (1–2 días en el documento de requisitos). Se miden de verdad en P12. Si no alcanza, recorta en este orden, y declara cada recorte en el paper:
1. Imprescindible mínimo: P01–P12, P13, P14 y P16 con `syn` y `modbus`; P20, P21 y P22.
2. Después: añadir `udp` (obs. 2), luego `icmp`.
3. Después: P15 (E2), P18, P19.
4. Último: P17 (Snort). Si no se hace, quita Snort de la comparación (obs. 3, opción B).
5. Si no se logra la prevención real en P09, el texto debe rebajar la afirmación a detección/alerta (obs. 1, 20): decisión tuya.

La duración del ataque (60 s) difiere de los 5 min del paper: es una desviación que debe declararse o corregirse en la tabla de escenarios.

## Cuidado con la PC (ya a 74 °C)
Los floods con `--flood` saturan CPU. El guardián (P04) pausa a 85 °C y aborta a 90 °C, y el arnés enfría entre corridas. Antes de empezar, revisa ventiladores y polvo; en P02 se medirá la temperatura en reposo. Si no baja de ~70 °C, considera la variante cloud.

## Supuestos que debes confirmar
- El nombre real del repo (P01 lo pregunta).
- pfSense: requiere descarga manual de la ISO; P08 pide elegir entre pfSense y nftables.
- IPs del laboratorio: PLC en 192.168.30.10 (el paper usa 192.168.1.10), SCADA en VLAN 20; el texto del paper deberá actualizarse (P21).
