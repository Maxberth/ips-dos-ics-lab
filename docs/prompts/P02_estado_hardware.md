# P02 · Estado del hardware y del sistema (solo lectura)

**Prioridad: IMPRESCINDIBLE** · Tiempo: 10 min · No instala ni modifica nada.
**Observaciones:** 11 (detalle experimental: hardware, CPU, RAM), 24 (limitación de virtualización). Alimenta `01_hardware.md` y `03_limitaciones.md`.

---

## PROMPT (copiar desde aquí)

Trabaja en el repo confirmado en P01 (confirma la ruta con `pwd` y `git branch --show-current`; si no estás en `lab/ips-icits27`, avísame). Lee `CLAUDE.md` y respétalo. Este paso es de **solo lectura**: no instales paquetes, no cambies configuración, no uses `sudo` salvo para leer (`dmesg`, `dmidecode`, `lscpu` no lo necesitan; pídeme permiso si algo lo exige).

### Recolecta y guarda cada salida literal en `docs/lab/logs/P02_*.txt`
1. **SO y kernel:** `cat /etc/os-release`, `uname -a`, `pacman -Q linux-cachyos* 2>/dev/null`, `cat /proc/cmdline`.
2. **CPU:** `lscpu`, `lscpu -e` (topología de hilos y núcleos: identifica qué pares de hilos comparten núcleo físico del Ryzen 5 5600X), gobernador de frecuencia (`cpupower frequency-info` o `/sys/devices/system/cpu/cpu0/cpufreq/`), driver (`amd-pstate`?), flags `svm`.
3. **RAM:** `free -h`, `cat /proc/meminfo | head -30`, `swapon --show`, `zramctl`, `cat /proc/sys/vm/swappiness`, `systemctl is-active systemd-oomd earlyoom`, `systemctl status systemd-oomd --no-pager`, `cat /proc/pressure/memory`. Lista los 15 procesos que más RAM usan (`ps -eo pid,comm,rss --sort=-rss | head -16`) y estima cuánta RAM queda libre con mi escritorio normal abierto.
4. **Temperatura y refrigeración:** `sensors` (módulo `k10temp`, campo Tctl/Tccd1), `ls /sys/class/hwmon/*/name`; velocidad de ventiladores si aparece. Toma **tres lecturas separadas 20 s** en reposo y registra el máximo. Si Tctl ≥ 75 °C en reposo, anótalo como anomalía y sugiere causas (pasta térmica, curva de ventiladores, procesos en segundo plano) sin tocar nada.
5. **Virtualización:** `ls -l /dev/kvm`, `lsmod | grep -E 'kvm|vhost'`, `zgrep -i -E 'iommu|amd_iommu' /proc/config.gz` y `dmesg | grep -i -E 'iommu|AMD-Vi'` (si exige sudo, pregúntame), `systemd-detect-virt`, `grep -c svm /proc/cpuinfo`.
6. **Disco:** `lsblk -f`, `df -h`, sistema de archivos de `/home` y del repo, espacio libre (necesito ≥ 120 GB), `smartctl -H` solo si ya está instalado.
7. **Red:** `ip -br link`, `ip -br addr`, `ip route`, `nmcli device status` (si existe). Confirma que `enp2s0`, `wlan0` y `tailscale0` **no se usarán** en el laboratorio y anota si hay Docker/otras redes que choquen con 192.168.10/20/30.0/24 (`ip route | grep 192.168`).
8. **Energía y estabilidad:** historial reciente de reinicios inesperados: `journalctl --list-boots | tail -5`, `journalctl -b -1 -p err --no-pager | tail -50`, y `journalctl -k -b -1 | grep -i -E 'oom|thermal|mce|watchdog|panic' | tail`. Si hay indicios de que la PC se reinició por OOM, temperatura o fallo, repórtalo con evidencia.

### Entregables
- `docs/lab/01_hardware.md`: tabla con CPU (modelo, núcleos/hilos, topología de pares), RAM total/disponible en reposo, swap/zram, disco, NIC, kernel, temperaturas medidas (con fecha y hora), estado de KVM/IOMMU.
- `docs/lab/03_limitaciones.md` (crear con primeras entradas): al menos (a) un solo equipo físico: atacante, IPS, PLC comparten CPU; (b) PLC simulado en VM, no PLC físico; (c) switch virtual Open vSwitch, no hardware industrial; (d) RAM y temperatura limitan el número de VMs; (e) sin NIC extra: el laboratorio es 100 % virtual. Cada una con su impacto sobre la validez.
- `docs/lab/05_problemas_anomalias.md`: lo anómalo detectado (temperatura en reposo, reinicios, poco RAM libre…).
- Entrada en `00_diario.md` y commit local.

### Verificación
Termina con un veredicto explícito por requisito (**CUMPLE / NO CUMPLE / INCIERTO**) para: KVM disponible, ≥ 12 hilos, RAM libre suficiente para 8–10 GiB de VMs más 6 GiB de reserva del host, disco ≥ 120 GB, IOMMU, temperatura en reposo < 70 °C. Señala qué debo cerrar o cambiar antes de seguir. No continúes a P03.

## FIN DEL PROMPT
