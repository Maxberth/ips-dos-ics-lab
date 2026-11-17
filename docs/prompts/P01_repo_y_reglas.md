# P01 · Confirmar el repo, crear la estructura de documentación y las reglas permanentes

**Prioridad: IMPRESCINDIBLE** · Pegar en Claude Code · Tiempo estimado: 10–15 min
**Observaciones que sustenta:** todas (base de trazabilidad). No instala nada.

---

## PROMPT (copiar desde aquí)

Vas a ayudarme a montar y ejecutar un laboratorio para un artículo científico (ICITS'27: IPS contra DoS en redes de control industrial). Todo el trabajo y toda la documentación viven dentro del repositorio Git del artículo. En este primer paso NO instales nada y NO toques configuración del sistema.

### 1. Confirmar la ruta del repo (obligatorio antes de escribir nada)
La carpeta madre es `/home/maxberth/code/articulo/` y tiene dos partes: `paper/` (proyecto LaTeX, fuera de Git) y `ips-dos-ics-lab/` (repo Git, **privado** en GitHub, cuenta `Maxberth`). Verifica: `git -C /home/maxberth/code/articulo/ips-dos-ics-lab rev-parse --show-toplevel`, `git remote -v`, rama actual y `git status --short`. Muéstramelo y **pídeme confirmación de que esa es la ruta correcta**. Si no existe o difiere, busca candidatos con `find ~ -maxdepth 4 -name main.tex 2>/dev/null` y pregunta. No uses `patriac-platform`: es otro proyecto. Tras mi confirmación, trabaja siempre ahí y cambia a la rama `lab/ips-icits27` (no empujes sin que yo lo pida). El LaTeX está en `../paper/` y **no se edita en estos prompts**.

#
```
lab/            # scripts y configuraciones del laboratorio (versionado)
  guard/  setup/  harness/  analysis/  config/
data/raw/       # CSV crudos, uno por corrida o por tipo (versionado)
data/captures/  # pcap/logs voluminosos (en .gitignore; se versiona solo manifest.csv con sha256, tamaño y ruta)
data/processed/ # tablas derivadas
figures/  tables/
docs/lab/       # toda la documentación en .md
  00_diario.md             # bitácora cronológica, solo se añade al final (UTC y hora local)
  01_hardware.md           # CPU, RAM, disco, temperatura, red, IOMMU, topología de núcleos
  02_software_versiones.md # tabla: componente | versión exacta | cómo se instaló | fecha
  03_limitaciones.md       # cada limitación, con su impacto sobre la validez del estudio
  04_decisiones.md         # una entrada por decisión: contexto, alternativas, elección, motivo
  05_problemas_anomalias.md# todo lo raro, aunque se resuelva: síntoma, hipótesis, evidencia, resolución
  06_logros_avances.md     # qué quedó verificado y con qué evidencia
  07_resultados_auditados.md
  08_mapa_observaciones.md # observación del revisor -> evidencia -> sección del paper
  logs/                    # salida literal de comandos importantes (un archivo por paso)
```
Añade a `.gitignore`: `data/captures/*` (excepto `manifest.csv`), `*.qcow2`, `*.iso`, `*.img`, `__pycache__/`.

### 3. Escribir `CLAUDE.md` en la raíz del repo con estas reglas permanentes (se aplican a todos los prompts posteriores)
- Idioma: responde y documenta en español; el código y los nombres de archivo en inglés o español sin tildes.
- **Prohibido inventar, estimar o rellenar datos.** Un valor en un CSV solo puede salir de una medición real hecha por un script del repo. Si una medición falla, se registra el fallo (`status=failed`) y no se sustituye. Los ejemplos de prueba de los scripts van marcados `SYNTHETIC` y nunca se guardan en `data/raw/` ni se usan en figuras del paper.
- **Dudar siempre.** Cada resultado importante requiere una segunda fuente independiente (p. ej. contadores de Suricata frente a conteo de paquetes en captura). Si no coinciden, es una anomalía: se registra en `05_problemas_anomalias.md` y no se avanza hasta explicarla o declararla.
- **Verificar antes de avanzar.** Cada paso termina con una comprobación objetiva con salida guardada en `docs/lab/logs/`. Si falla, te detienes y reportas; no sigues al paso siguiente.
- **Recursos:** la PC no debe llegar al 100 % de RAM ni a temperaturas peligrosas. Obedece los límites de `lab/guard/` (se crean en P04). Nunca lances VMs ni ataques fuera de `systemd-run`/slice con límites una vez que existan. Si `MemAvailable` < 4 GiB, swap en uso creciente o temperatura ≥ 85 °C: detén lo que estés haciendo y avísame.
- **Aislamiento:** el laboratorio no se conecta a `enp2s0`, `wlan0` ni `tailscale0`. Ningún ataque sale del host. No uses `--rand-source` ni apuntes a IP fuera de 192.168.10/20/30.0/24.
- `sudo`: pídeme confirmación antes de cualquier comando que modifique el sistema (instalar, servicios, sysctl, red). Muestra el comando antes. Nunca `rm -rf` fuera de `lab/` y `data/` del repo.
- Documentación: al terminar cada prompt, actualiza `00_diario.md` (qué hiciste, qué verificaste, qué falló) y los archivos que correspondan. Haz un commit local por paso verificado, con mensaje descriptivo.
- Cada artefacto lleva metadatos: fecha UTC, commit del repo, versiones relevantes.
- Mantén un mapa vivo de qué observaciones de los revisores (numeradas 0–26 en `observaciones_icits27.md`) cubre cada paso; el archivo está en `docs/observaciones_icits27.md`.

### 4. Verificación y cierre
- Muestra `tree -L 3` (o `find`) de lo creado y `git status`.
- Escribe la primera entrada de `00_diario.md` (fecha, ruta del repo confirmada, rama) y haz el commit local.
- Responde con: ruta confirmada, rama, y la lista de archivos creados. No avances a otros pasos.

## FIN DEL PROMPT
