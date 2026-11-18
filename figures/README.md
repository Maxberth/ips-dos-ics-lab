# figures

- `figures/paper/` (inglés) y `figures/paper_es/` (español): **figuras del paper**, generadas solo por script y al ancho de LNCS (4,8 in), en PNG (300 dpi) y PDF vectorial.
  - Resultados (`lab/analysis/figuras_paper.py --platform laptop-dev --profile final`): `r1_availability`, `r2_rtt_p95`, `r3_availability_timeseries`, `r4_attack_removed`, `r5_plc_down`, `r6_vm_cpu`, `r7_thermal` (material suplementario).
  - Arquitectura y diseño (`lab/analysis/figuras_arquitectura.py --platform laptop-dev`): `a1_topology`, `a2_ips_datapath`, `a3_experiment_design`.
- `laptop-dev_piloto_*` y `laptop-dev_reduced_*`: figuras antiguas de la calibración (`stats_tables.py --figures`), no van al paper.

Las figuras `laptop-dev_final_*` anteriores se eliminaron: las sustituyen las de `figures/paper/`.
