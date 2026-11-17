# ips-dos-ics-lab

Laboratorio reproducible y documentación del artículo **ICITS'27**: *Implementation of an Intrusion Prevention System for Mitigating DoS Attacks in Industrial Control Networks*. Repositorio **privado** por ahora.

El objetivo de este repo es dejar todo documentado: resultados, cómo recrearlos, arquitectura, hardware, scripts y datos crudos. El texto del paper (LaTeX, plantilla Springer LNCS) vive en otro repositorio privado: [`Maxberth/ips-dos-ics-paper`](https://github.com/Maxberth/ips-dos-ics-paper) (en el equipo, `../paper/`). Las figuras y tablas de `figures/` y `tables/` se copian allí cuando entran al artículo, y su `observaciones/registro_cambios.md` dice qué observaciones están resueltas.

## Estructura
```
docs/
  observaciones_icits27.md          # matriz de observaciones de los revisores (0–26)
  requisitos_laboratorio_desde_cero.md
  arquitectura.md                   # diagrama y escenarios
  prompts/                          # serie P01–P22 para Claude Code (empezar por prompts/README.md)
  lab/                              # bitácora viva: hardware, versiones, limitaciones, decisiones, anomalías, logros, resultados
lab/        # scripts y configuraciones (guardián, red, harness, análisis)
data/       # raw/ (CSV crudos), processed/, captures/ (no versionado, solo manifest)
figures/ tables/
```

## Cómo se usa
1. Abrir Claude Code en esta carpeta y seguir `docs/prompts/README.md`, un prompt a la vez.
2. Cada prompt documenta en `docs/lab/` y guarda datos crudos reales en `data/raw/`. No se inventan datos.
3. Los CSV, scripts y reglas permiten regenerar tablas y figuras.

## Estado
Prompts redactados; el laboratorio aún no está montado. Ver `docs/lab/00_diario.md`.
