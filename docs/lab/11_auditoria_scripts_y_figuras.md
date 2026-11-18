# Auditoría de los scripts de análisis y de las figuras (2026-11-18, UTC)

**Alcance real:** revisé línea por línea `analisis_final.py`, `stats_tables.py`, `calibracion_alertas.py`, `verificar_conservacion_nfq.py`, `muestras_guard_por_corrida.py` y los scripts nuevos de figuras; y las partes de `summarize_runs.py`, `pcap_count.py`, `scada_poller.py`, `run_once.sh` e `ips_mode.sh` que determinan lo que se grafica. **No auditué a fondo** `host_sampler.py`, `modbus_flood.py`, `validate_run.py` ni `audit_pilot.py`.
**Revisión visual:** abrí y miré cada PNG generado (10 en inglés y los diagramas en español) y corregí lo que vi. No se subió nada a un servicio externo: la revisión la hice con la herramienta de lectura de imágenes de esta sesión.

## Hallazgos y qué se hizo

| # | Hallazgo | Gravedad | Acción |
|---|---|---|---|
| 1 | **Ancho de las figuras:** las anteriores se hacían a 8 in con letra de 9 pt; al insertarlas en LNCS (4,8 in de texto) quedaban a ~5 pt. | Alta | `estilo_figuras.py`: 4,8 in, letra de 6,5–8 pt, PNG 300 dpi y PDF vectorial. |
| 2 | **Idioma:** etiquetas en español en un paper en inglés (los revisores señalaron terminología inconsistente). | Alta | `--lang en|es`; el paper usa `figures/paper/` (inglés). |
| 3 | **Leyendas fuera del lienzo o sobre los datos:** la primera versión recortaba las leyendas y la anterior las ponía encima de los puntos (E2 icmp). | Alta | Leyenda en una fila arriba, fuera de los ejes (`loc="outside upper center"`). |
| 4 | **Texto desbordado en los diagramas** (nombres de VM, `c_fwd_v20_v30`, etiquetas de los espejos) y etiqueta "accept" montada en un cuadro. | Alta | Rediseñé la geometría, reduje el texto por caja y revisé las versiones en inglés y español. |
| 5 | **Título cortado** (figura de respuestas/programadas) y títulos largos dentro de la imagen. | Media | Títulos fuera de la imagen (van en el caption de LaTeX); el título de panel es corto. |
| 6 | **Rótulo "(b)" montado sobre la etiqueta del eje.** | Media | Etiquetas de eje más cortas y panel como título izquierdo. |
| 7 | **Colores:** una paleta no apta para daltonismo y sin marcadores. | Media | Paleta Okabe-Ito y un marcador distinto por escenario (circulo, triángulo, rombo). Barras con parche en vez de marcador. |
| 8 | **Dos conjuntos de figuras** (`stats_tables.py` y `analisis_final.py`) con estilos distintos. | Media | `analisis_final.py` solo escribe la tabla; `stats_tables.py` solo dibuja con `--figures` (figuras antiguas); todas las del paper salen de `figuras_paper.py` y `figuras_arquitectura.py`. Eliminé las `laptop-dev_final_*` antiguas. |
| 9 | **`docs/arquitectura.md` desactualizado:** Ryzen 5 5600X con 24 GB, pfSense y Snort E4, que no son lo medido. | Alta | Corregido a `laptop-dev` (Ryzen 5 6600H, 14,8 GiB), nftables y E4 no ejecutado. |
| 10 | **Disponibilidad por solicitud emitida** (`summarize_runs.py`): sobreestima el servicio al saturarse (A24). | Alta | Documentado; las figuras muestran las dos métricas. No se cambió la definición oficial. |
| 11 | **`sat_pct` de `stats_tables.py` mezcla ambos sentidos** (A21). | Media | Documentado; no se usa en las figuras. **No debe citarse para E2 syn/icmp.** |
| 12 | **CPU de las VM puede superar 100 %** (incluye hilos de QEMU). | Media | Etiqueta del eje con la definición y nota en el análisis; proponer esa frase en el caption. |
| 13 | **`python3 -I` no importa módulos del mismo directorio** (error de importación en el script nuevo). | Baja | `sys.path` explícito. |
| 14 | **Datos de las figuras de arquitectura:** vCPU, RAM, duraciones y reglas se escribían a mano. | Media | Se leen de `lab/config/` (perfil, `experiment.env`, `nftables-nfq.conf`) para que no se desincronicen. |

## Pendiente y limitaciones
- Las capturas de pantalla del paper actual (`paper/figures/*.png`, de la primera versión) **no se regeneraron**: son capturas de herramientas, y no las revisé una por una. La matriz `10_seguimiento_revisores.md` registra el reemplazo como en curso.
- La serie `r3_availability_timeseries` distingue los escenarios solo por color (no por tipo de línea); en blanco y negro E2 y E3 son difíciles de distinguir.
- `r7_thermal` y `r6_vm_cpu` son material suplementario; el paper puede prescindir de ellas.
- Texto sugerido para el caption de `r1_availability`: "(a) replies divided by requests actually issued; (b) replies divided by the 600 requests scheduled (10 Hz × 60 s). The closed-loop poller issues fewer requests when replies are missing."
