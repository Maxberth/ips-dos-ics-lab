# figures

- `figures/paper/` (inglés) y `figures/paper_es/` (español): **figuras del paper**, generadas solo por script, al ancho de LNCS (4,8 in), en PNG (300 dpi) y PDF vectorial.
  - Resultados (`lab/analysis/figuras_paper.py --platform laptop-dev --profile final`): `r1_availability`, `r2_rtt_p95`, `r3_availability_timeseries`, `r4_attack_removed`, `r5_plc_down`, `r6_vm_cpu`, `r7_thermal`.
  - Arquitectura y diseño (`lab/analysis/figuras_arquitectura.py --platform laptop-dev`): `a0_logical_topology` (flujo vertical, mismo formato que la Fig. 1 original), `a1_topology`, `a2_ips_datapath`, `a3_experiment_design`.
- Tablas LaTeX del paper: `tables/paper/` (`lab/analysis/tablas_paper.py`): resultados, pruebas estadísticas y VM.
- `laptop-dev_piloto_*` y `laptop-dev_reduced_*`: figuras antiguas de la calibración (`stats_tables.py --figures`), no van al paper.
