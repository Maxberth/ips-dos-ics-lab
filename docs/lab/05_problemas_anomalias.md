# Problemas y anomalías

Todo lo raro, aunque se resuelva: síntoma, hipótesis, evidencia y resolución.

## A1. Prueba de scope con `bytearray` no reservó memoria real (resuelta)
- **Síntoma:** un scope con `MemoryMax=256M` que crea `bytearray(600 MiB)` terminó con exit 0.
- **Causa:** `bytearray(n)` usa páginas a cero que el kernel no asigna hasta escribirlas.
- **Resolución:** la prueba escribe los datos (`b'\x01'*600MiB`) y el scope muere con exit 137. Evidencia: `docs/lab/logs/P04_pruebas_guardian.txt`.

## A2. Las simulaciones del guardián escribieron en `data/raw/` (resuelta)
- **Síntoma:** filas con umbrales simulados en `data/raw/guard/guard_laptop-dev_*.csv`.
- **Resolución:** se borró el archivo y `guard.sh` acepta `GUARD_CSV` para que las simulaciones escriban fuera de `data/raw`.

## A3. `docker network ls` arrancó dockerd por socket durante P02
- Ver `docs/lab/contenedores_apagados.md`. `root_setup.sh` lo detiene.
