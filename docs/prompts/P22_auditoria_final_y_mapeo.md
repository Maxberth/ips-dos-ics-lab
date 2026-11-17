# P22 · Auditoría final y mapa de observaciones → evidencia → secciones del paper

**Prioridad: IMPRESCINDIBLE** · Tiempo: 45–60 min
**Observaciones:** todas (0–26).

---

## PROMPT (copiar desde aquí)

Repo y rama confirmados. Respeta `CLAUDE.md`. Eres ahora un **revisor escéptico** de tu propio trabajo. Hazlo con datos reales; no cierres ningún punto sin evidencia verificable.

### Parte A. Auditoría de los datos y del laboratorio
1. **Integridad:** `manifest.csv` (sha256) coincide con los archivos; `runs.csv` sin duplicados de `run_id`; todas las corridas del plan existen o su ausencia está explicada; versiones y hashes de reglas/config consistentes por escenario (si cambió una regla a mitad de una serie, esas corridas no se mezclan).
2. **Segunda fuente:** recalcula, para todas las corridas de E3 (y E4 si existe), la diferencia entre paquetes descartados vistos en captura y los de Suricata; informa mediana y máximo; lista corridas fuera de tolerancia y su explicación.
3. **Anomalías:** revisa `05_problemas_anomalias.md`: cada anomalía con estado (resuelta con evidencia / abierta / declarada como limitación). Ninguna abierta puede sustentar una afirmación del paper.
4. **Duda activa:** responde por escrito: (a) ¿qué resultado me sorprendió y lo verifiqué? (b) ¿hay algún efecto atribuible al generador de ataque, a la temperatura o a la CPU compartida en lugar de al IPS? (c) ¿qué parte del efecto es de Suricata y qué parte del firewall/VLAN (E1 vs E3)? (d) ¿qué afirmaciones del paper actual **no** están respaldadas por los datos (p. ej. las cifras de las tablas originales 61.5 %→98.3 % etc. frente a las nuevas)? Dilo sin suavizar.
5. **Reproducibilidad:** `make analysis` regenera todas las tablas y figuras desde cero y los números coinciden con `07_resultados_auditados.md`.
6. **Seguridad de la PC y del repo:** no hay secretos en el historial (`git log -p | grep -i -E 'password|secret|BEGIN .*PRIVATE'` o herramienta equivalente), y el laboratorio quedó aislado (OVS sin NIC físicas).

### Parte B. Mapa de trazabilidad (`docs/lab/08_mapa_observaciones.md`)
Tabla con una fila por observación **0–26**, con columnas: `# | resumen | ¿lo cubre el laboratorio? (sí / parcial / no, es de texto) | evidencia (CSV, figura, tabla, log) | sección(es) del paper a editar | afirmación permitida | pendiente | estado`. Reglas:
- Obs. de laboratorio (1, 2, 3, 4, 5, 6, 8, 10, 11, 19, 20, 22, 24): estado según evidencia real; si el experimento no se hizo, indica la acción honesta (retirar del texto / declarar limitación) tal como propone la matriz.
- Obs. solo de texto/plantilla/referencias (0, 7, 9, 12–18, 21, 23, 25, 26): marca "no lo cubre el laboratorio", pero enlaza los **insumos** que sí produjo (definiciones, tablas LaTeX, etiquetas de figura sin espacios, pp vs %).
- Para cada sección del paper (Abstract, §3 Método, §4.3 IPS, §4.4 Escenarios, §5 Resultados, §6 Conclusiones, limitaciones) lista qué tabla/figura/archivo la alimenta y qué frases hay que cambiar.

### Parte C. Informe de cierre (`docs/lab/informe_final.md`)
Resumen para mí: qué se logró, qué no, con números reales y su evidencia; recorte de alcance aplicado; las 5 decisiones que debo tomar antes del 18 de noviembre (título, afirmación de prevención, Snort sí/no, UDP sí/no, material suplementario); riesgos restantes. Diario final, commit y `git log --oneline` de la rama. No empujes a remoto sin mi confirmación.

## FIN DEL PROMPT
