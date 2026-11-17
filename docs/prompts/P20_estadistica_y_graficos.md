# P20 · Estadística, tablas y gráficos reproducibles desde los CSV

**Prioridad: IMPRESCINDIBLE** · Tiempo: 45–60 min (puede empezar con datos parciales y rehacerse)
**Observaciones:** 5 (media, DE, IC 95 %), 21 (pp vs %), 23 (quitar "significativo" si no hay prueba), 19, 18, 6.

---

## PROMPT (copiar desde aquí)

Repo y rama confirmados. Respeta `CLAUDE.md`. Escribe en `lab/analysis/` scripts de Python (`python -I` no hace falta aquí, pero no ejecutes nada desde `data/`) que lean **solo** `data/raw/` y generen todo en `data/processed/`, `tables/` y `figures/`. Nada se escribe a mano: cada número del paper debe poder regenerarse con `make analysis` (o `lab/analysis/run_all.sh`).

### 1. Carga y control de calidad (`load.py`, `qc.py`)
- Une `runs.csv` con los CSV por corrida; considera solo `status=ok` y validación OK/WARN (las WARN se listan). Informa cuántas corridas hay por escenario/ataque y cuántas se excluyeron y por qué (tabla `tables/exclusiones.csv`; no se excluye nada en silencio).
- Cada gráfico/tabla imprime en su pie el `n` real, la fecha de generación y el commit.

### 2. Métricas por corrida (`metrics.py`), según `docs/lab/definiciones_metricas.md`
Pérdida, disponibilidad, RTT (media, mediana, p95, p99), throughput (Mbps, sin ×100), CPU del PLC (guest y host), CPU del IPS, tasa de detección (por paquete y por ráfaga), paquetes de ataque antes/después del IPS, falsos positivos, pps efectivos. Cada valor con su archivo y ventana de origen.

### 3. Estadística (`stats.py`)
- Por escenario y ataque: n, media, DE muestral (n−1), IC 95 % con t de Student (`scipy.stats.t`). Si n < 10, indica el n real.
- Comparaciones E1 vs E2, E1 vs E3, E3 vs E4: diferencia de medias con IC (Welch). Prueba no paramétrica (Mann-Whitney) como comprobación. Tamaño del efecto. **No uses la palabra "significativo" sin prueba y sin informar el valor p y el IC** (obs. 23). Con n = 10, avisa de la baja potencia.
- Mejora relativa: reducción relativa en **%** para latencia/pérdida/CPU, y diferencia en **puntos porcentuales (pp)** para disponibilidad y detección (obs. 21), con IC por remuestreo (bootstrap, semilla fija) o por propagación.
- Normalidad y varianza: Shapiro-Wilk por grupo y registro en el informe; si se viola, destacar el no paramétrico.

### 4. Tablas (`tables.py`)
CSV y **LaTeX** listos (`tables/*.tex`) en el formato de las tablas del paper (mismas filas: Packet Loss, Latency, Availability, Detection Rate, CPU, Throughput), con columnas Sin IPS (E1) | Alert (E2) | Drop (E3) | Snort (E4) y notación `media ± DE [IC 95 %]`, más una tabla de configuración experimental (obs. 11) a partir de `runs.csv` y `01_hardware.md`.

### 5. Gráficos (`figures.py`, matplotlib)
Consulta la skill `dataviz` si está disponible para elegir colores accesibles (daltónicos), tipografía legible en columna LNCS (ancho ≈ 12 cm) y exporta **PDF vectorial y PNG 300 dpi**. Figuras mínimas:
1. Barras con barras de error (IC 95 %) por escenario y ataque: disponibilidad, RTT, pérdida, throughput, CPU.
2. Caja o puntos individuales (las 10 repeticiones visibles) para RTT y disponibilidad.
3. Series temporales medidas (P19): RTT y disponibilidad por segundo con las fases sombreadas.
4. Paquetes de ataque antes vs después del IPS (evidencia de bloqueo) y `drop` de Suricata, por ataque.
5. Contadores por puerto OVS (P18).
6. Diagrama de dispersión de verificación (segunda fuente): paquetes descartados según captura vs según Suricata, una nube de 10×4 puntos con la recta y = x.
Cada figura con título claro, ejes con unidades, **etiquetas de archivo sin espacios** (`fig_syn_availability.pdf`, para LaTeX; obs. 16) y un `figures/README.md` que liste figura → script → CSV de origen → observación cubierta.

### 6. Verificación (dudar de los scripts)
- Prueba con un conjunto **sintético** claramente marcado (`tests/synthetic/`, nunca en `data/raw/`) con medias/DE conocidas: el script debe devolverlas exactamente (test unitario `pytest`). Esos datos no se mezclan con los reales ni salen en ninguna figura del paper.
- Recalcula a mano (en un cuaderno aparte) una media, una DE y un IC de una celda de tabla y compáralos con la tabla generada; registra el resultado.
- Comprueba que cada número de las tablas aparece trazado a ≥ 1 corrida real.
- Diario, `07_resultados_auditados.md` (con las tablas finales y su estado), commit.

## FIN DEL PROMPT
