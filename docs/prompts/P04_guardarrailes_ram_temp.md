# P04 · Guardarraíles de RAM, CPU y temperatura (antes de crear cualquier VM)

**Prioridad: IMPRESCINDIBLE** · Tiempo: 30–40 min
**Observaciones:** 11 (reproducibilidad: límites de recursos por VM), 24 (limitación de virtualización). Protege la PC de reinicios por OOM o calor.

---

## PROMPT (copiar desde aquí)

Repo y rama confirmados (`pwd`, `git branch --show-current`). Respeta `CLAUDE.md`. Todavía no hay VMs ni ataques. Quiero que **la PC nunca llegue al 100 % de RAM ni se reinicie**, y que si algo se descontrola el laboratorio se detenga antes que el escritorio. Esto es configuración mínima de systemd/cgroups y scripts; no instala paquetes grandes (si falta uno pequeño como `lm_sensors`, `stress-ng` o `sysstat`, muéstrame el comando y espera mi OK).

Antes de cada comando que use `sudo`, muéstramelo y espera confirmación. Guarda las salidas en `docs/lab/logs/P04_*.txt`.

### 1. Diseño de límites (propón y justifica en `04_decisiones.md`; yo apruebo)
Con los datos de `01_hardware.md` (24 GiB de RAM, Ryzen 5 5600X de 12 hilos):
- **Reserva del host:** ≥ 6 GiB de RAM libre/caché siempre para CachyOS y el escritorio. Un hilo-par (un núcleo físico) reservado al host y a la captura.
- **`machine.slice`** (donde libvirt/QEMU ponen las VMs): `MemoryHigh` ≈ 11 GiB, `MemoryMax` ≈ 12 GiB, `MemorySwapMax` bajo o 0 para que las VMs nunca empujen el host a swap, `AllowedCPUs` = hilos de los núcleos NO reservados, y `CPUQuota` si hace falta.
- **Límite duro por VM** en el XML de libvirt (`<memtune><hard_limit>` y `<memory>` = `<currentMemory>`, sin balloon dinámico ni sobreasignación) y `<cputune><vcpupin>` para fijar vCPUs. Cada VM suma su límite, y la suma debe ser menor que `MemoryHigh`.
- **Todo lo que no sea VM** (hping3, tcpdump, scripts de análisis) se lanza con `systemd-run --user --scope -p MemoryMax=… -p CPUWeight=…` mediante un envoltorio `lab/guard/limited-run.sh`.
- **Swap/zram:** revisa lo hallado en P02; si el swap es pequeño o no existe, propón (sin aplicar aún) un zram acotado. Documenta `vm.swappiness` y `vm.min_free_kbytes` sugeridos.
- **OOM:** revisa `systemd-oomd`/`earlyoom`. Propón que, ante presión de memoria, se maten **primero las VMs del laboratorio** (`ManagedOOMPreference` / `oom_score_adj` alto para los procesos QEMU del laboratorio, y bajo para el escritorio). No debe matar mi sesión gráfica.

### 2. Guardián (`lab/guard/guard.sh`) como servicio de usuario o `systemd-run`
Cada 2 s lee: `MemAvailable`, `SwapFree`, presión de memoria (`/proc/pressure/memory`, `some avg10`), temperatura Tctl (`k10temp` en `/sys/class/hwmon`), carga. Escribe `data/raw/guard_log.csv` (timestamp UTC, mem_avail_mib, swap_used_mib, psi_mem_avg10, tctl_c, load1, estado). Umbrales por defecto, en un archivo `lab/config/guard.env`:

| Estado | Condición | Acción |
|---|---|---|
| OK | MemAvailable ≥ 6 GiB y Tctl < 80 °C | nada |
| WARN | MemAvailable < 5 GiB, o Tctl ≥ 80 °C, o swap en aumento | avisa por consola/`notify-send` |
| PAUSE | MemAvailable < 4 GiB, o Tctl ≥ 85 °C, o PSI memory some avg10 > 20 | crea `/run/lab/PAUSE`; el arnés de pruebas debe detener el ataque y esperar |
| ABORT | MemAvailable < 2,5 GiB, o Tctl ≥ 90 °C, o swap > 1 GiB | crea `/run/lab/ABORT`, detiene generadores y hace `virsh destroy` de las VMs del laboratorio |

Importante: mi CPU ya llega a 74 °C en reposo; calcula una **línea base de temperatura** y propón histéresis (volver a OK solo tras enfriar a < 70 °C). Documenta que la temperatura limita la duración y la cadencia de las corridas (se necesitará enfriamiento entre corridas).

### 3. Scripts auxiliares
- `lab/guard/lab-status.sh`: muestra de un vistazo RAM, swap, temperatura, VMs activas (`virsh list`), PIDs de QEMU y su RSS, estado del guardián.
- `lab/guard/lab-stop.sh`: apaga limpiamente (`virsh shutdown`, luego `destroy` tras 30 s), desmonta redes del laboratorio y para el guardián. Debe poder ejecutarse en cualquier momento sin dañar nada.
- `lab/guard/limited-run.sh`: envoltorio con `systemd-run`.

### 4. Pruebas del guardián (sin arriesgar la PC)
**No agotes la RAM de verdad.** Prueba con umbrales artificialmente altos (p. ej. `PAUSE` si MemAvailable < tu-valor-actual-menos-500MB) y un consumo controlado y pequeño dentro de un scope con `MemoryMax=1G` (con `stress-ng --vm 1 --vm-bytes 800M --timeout 20s`). Comprueba: (a) el guardián pasa a WARN/PAUSE y crea `/run/lab/PAUSE`; (b) el scope respeta `MemoryMax` y, si se excede, solo muere ese scope; (c) `lab-stop.sh` funciona sin VMs. Haz una prueba térmica corta (60 s de `stress-ng --cpu 4`) solo si Tctl de partida < 70 °C, vigilando que no pase de 85 °C; aborta si pasa.

### 5. Entregables y verificación
- Scripts y `lab/config/guard.env` versionados; unidades systemd (si las creas) copiadas a `lab/setup/systemd/` con instrucciones de instalación.
- `docs/lab/01_hardware.md`: añade la tabla de presupuesto de recursos y los umbrales con su justificación.
- `docs/lab/03_limitaciones.md`: añade la limitación térmica y de RAM y cómo influyen en el diseño (duración de corridas, enfriamiento, 24 GiB).
- Criterios de aceptación (CUMPLE/NO CUMPLE, con evidencia): guardián corriendo y registrando; PAUSE y ABORT probados con umbrales de simulación; `machine.slice` con límites verificados con `systemctl show machine.slice -p MemoryHigh -p MemoryMax -p AllowedCPUs`; `oom` priorizando VMs del laboratorio.
- Diario y commit. No avances a P05 hasta que todos los criterios estén en CUMPLE.

## FIN DEL PROMPT
