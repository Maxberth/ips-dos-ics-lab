# Plataforma: pc-miguel

> **Documento histórico:** no aplica al estudio final: desde el 2026-11-18 la única plataforma es `laptop-dev` (ver `CLAUDE.md` y `docs/lab/03_limitaciones.md`, L3). Se conserva como registro de cómo se planeó el trabajo.

PC de escritorio donde se harán las mediciones finales del laboratorio.

**Origen de los datos:** el usuario pasó el resultado de un chequeo solo lectura hecho **en pc-miguel** (prompt P02, 2026-11-16 o 17). No se midió desde la laptop, y aquí no hay logs crudos de esa máquina. Cuando se trabaje en pc-miguel, conviene guardar sus salidas en `docs/lab/logs/pc-miguel_P02_*.txt` con el mismo script que se usó para la laptop: `lab/setup/inventario_plataforma.sh pc-miguel`.

## Ficha

| Componente | Dato reportado |
|---|---|
| CPU | AMD Ryzen 5 5600X, 6 núcleos / 12 hilos, 560 MHz–4,65 GHz, 32 MB L3 |
| RAM | 24 GB DDR4-3200 en 3 módulos de 8 GB (DIMM_A1, A2, B2), marcas distintas. Sin doble canal simétrico. 1 ranura libre (DIMM_B1), máximo 128 GB |
| Disco | NVMe Kingston NV2 1 TB con **566 GB libres** en `/`. Además, un HDD WD de 500 GB |
| Placa / BIOS | ASUS PRIME B450M-A II, BIOS 3202 (16-06-2021) |
| GPU | NVIDIA RTX 3060 en PCIEX16 |
| Ranuras PCIe libres | PCIEX1_1, PCIEX1_2 y posiblemente una x2 del chipset (sin confirmar) |
| Red física | Un solo puerto Ethernet: Realtek RTL8111H (`enp8s0`, driver r8169), 1 Gb/s con link. **Ya no importa:** el laboratorio es 100 % virtual (QEMU/KVM + Open vSwitch), sin NIC extra |
| Virtualización | AMD-V activo. IOMMU (AMD-Vi) activo, 22 grupos |
| Temperaturas | CPU (Tctl) **74 °C en uso normal con Docker**. NVMe 52 °C |
| Energía | Escritorio, sin batería ni UPS detectado |
| Redes y servicios | Docker (`docker0`, ~13 `br-*`, ~18 `veth*`) y `tailscale0` presentes |
| Uso | Estación de trabajo, no dedicada (Docker, Tailscale, GPU) |
| Sistema operativo | Según el usuario, el mismo que la laptop (CachyOS). **No medido**: versión de kernel y paquetes |

## Veredictos para el laboratorio

| Criterio | Veredicto | Nota |
|---|---|---|
| KVM disponible | CUMPLE | AMD-V e IOMMU activos. No se reportó si `/dev/kvm` es accesible por el usuario |
| ≥ 8 hilos | CUMPLE | 12 hilos |
| RAM para ~6 GiB de VMs + 4 GiB para el host | CUMPLE | 24 GB totales. **No medido**: RAM libre con Docker funcionando |
| Disco ≥ 120 GB libres | CUMPLE | 566 GB libres |
| Temperatura en reposo < 70 °C | NO CUMPLE / INCIERTO | 74 °C se midió en uso normal con Docker, no en reposo. Hay que medir en reposo con Docker detenido |
| Enchufada | CUMPLE | Escritorio |

## Pendiente de medir en pc-miguel

- Versión exacta de CachyOS, kernel y paquetes (`pacman -Q`).
- RAM libre real con Docker detenido.
- Temperatura en reposo y bajo carga sostenida.
- Si alguna red de Docker usa `192.168.10.0/24`, `192.168.20.0/24` o `192.168.30.0/24`, que son las subredes del laboratorio.
- `journalctl` de arranques anteriores (OOM, temperatura).
