# P03 · Comprobación de dependencias (sin instalar)

**Prioridad: IMPRESCINDIBLE** · Tiempo: 15 min · Solo consulta.
**Observaciones:** 11 (versiones de software), 3 (Snort disponible), 1 (Suricata con soporte NFQUEUE). Alimenta `02_software_versiones.md`.

---

## PROMPT (copiar desde aquí)

Repo y rama confirmados (verifica con `pwd` y `git branch --show-current`). Respeta `CLAUDE.md`. **No instales ni quites nada.** Solo comprueba qué hay y qué falta, y prepara el plan de instalación para que yo lo apruebe en P05.

### 1. Inventario de lo que ya está instalado
Para cada elemento: ¿está instalado? ¿versión exacta? Usa `pacman -Q <pkg>`, `command -v`, `<cmd> --version`. Guarda la salida en `docs/lab/logs/P03_inventario.txt`.

| Grupo | Paquetes / herramientas a comprobar |
|---|---|
| Virtualización | `qemu-desktop` (o `qemu-full`), `libvirt`, `virt-install`, `virt-manager`, `edk2-ovmf`, `dnsmasq`, `swtpm`, `libguestfs` (opcional), `cloud-image-utils` / `cloud-localds` / `genisoimage` |
| Red | `openvswitch`, `nftables`, `iproute2`, `bridge-utils`, `tcpdump`, `wireshark-cli`, `tcpreplay`, `ethtool` |
| IPS | `suricata`, `snort` (Snort 3, probablemente AUR), `libnetfilter_queue`, `libnfnetlink` |
| Generadores | `hping`, `python-scapy`, `iperf3`, `nmap`, `ncat` |
| Industrial | `python-pymodbus`, `mbpoll`, OpenPLC Runtime (se instala dentro de una VM, no en el host), FUXA (`node`/`npm`) o ScadaBR (Java/Tomcat, más pesado) |
| Medición/análisis | `python`, `python-numpy`, `python-scipy`, `python-pandas`, `python-matplotlib`, `jq`, `sysstat`, `lm_sensors`, `stress-ng`, `htop`, `btop`, `smartmontools`, `pv`, `tmux` |
| Gestión de recursos | `systemd` (versión), `systemd-oomd`, `earlyoom`, `zram-generator`, `cpupower` |
| AUR | `paru` o `yay` disponible |

### 2. Disponibilidad en repositorios (sin instalar)
Con `pacman -Si <pkg>` y `paru -Si <pkg>` (solo consulta), indica el nombre real del paquete y la versión disponible, y si viene de `extra`, `cachyos*` o AUR. Para Snort 3 y OpenPLC investiga qué opción existe y cuál es su riesgo (compilar desde AUR, tiempo, dependencias). Para pfSense CE: indica que es una ISO (descargar de netgate.com tras registro gratuito; la descarga no es automatizable sin mi intervención) y propón alternativa 100 % libre (VM con `nftables` o OPNsense) si no es viable.

### 3. Imágenes base de VM (solo comprobar disponibilidad y tamaño)
Ubuntu Server 24.04 cloud image (para Suricata/Snort/OpenPLC/SCADA, como en el paper), Kali Linux (imagen qcow2 de la web oficial) o Debian cloud image + herramientas, ISO de pfSense CE. Para cada una: URL oficial, tamaño, método de verificación del hash. No descargues aún.

### 4. Presupuesto de recursos (propuesta, a falta de P02)
Con los datos de `01_hardware.md`, propón una tabla de VMs que respete: reserva del host ≥ 6 GiB de RAM libre, tope total de VMs ≈ 12 GiB, un núcleo físico (2 hilos) reservado al host. Punto de partida: atacante 2 GiB/2 vCPU, firewall 1 GiB/1 vCPU, IPS (Suricata y Snort, uno a la vez) 2 GiB/3 vCPU, OpenPLC 1 GiB/1 vCPU, SCADA 1.5 GiB/1 vCPU. Ajusta si P02 mostró menos RAM libre y justifica.

### 5. Entregables
- `docs/lab/02_software_versiones.md`: tabla componente | instalado (sí/no) | versión instalada | versión disponible | origen.
- `docs/lab/04_decisiones.md`: decisiones D1 (hipervisor KVM/libvirt), D2 (OVS), D3 (firewall: pfSense vs nftables VM), D4 (SCADA: FUXA/ScadaBR/pymodbus), D5 (presupuesto de recursos), cada una con alternativas y motivo.
- `docs/lab/plan_instalacion.md`: lista **exacta** de paquetes a instalar con `pacman`/`paru`, en el orden que usarás en P05, con tamaño estimado. Marca lo opcional.
- Diario y commit local.

### Verificación y cierre
Dime en un párrafo qué falta y qué riesgo ves (Snort 3 en AUR, pfSense manual, OpenPLC). **Espera mi aprobación del plan** antes de P05; no instales nada.

## FIN DEL PROMPT
