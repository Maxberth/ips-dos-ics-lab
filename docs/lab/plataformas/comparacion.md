# Comparación de plataformas: laptop-dev vs. pc-miguel

> **Documento histórico:** no aplica al estudio final: desde el 2026-11-18 la única plataforma es `laptop-dev` (ver `CLAUDE.md` y `docs/lab/03_limitaciones.md`, L3). Se conserva como registro de cómo se planeó el trabajo.

- Los datos de laptop-dev se midieron el 2026-11-17 ([ficha](laptop-dev.md), [logs](../logs/)).
- Los de pc-miguel son los que reportó el usuario ([ficha](pc-miguel.md)); no hay logs crudos.
- «No medido» quiere decir que no hay dato. **No se compara rendimiento**: no hay mediciones de carga en ninguna de las dos.

| Aspecto | laptop-dev | pc-miguel |
|---|---|---|
| Tipo | Laptop (Lenovo IdeaPad Gaming 3) | Escritorio (ASUS PRIME B450M-A II) |
| CPU | Ryzen 5 6600H (Zen 3+, móvil) | Ryzen 5 5600X (Zen 3, escritorio) |
| Núcleos / hilos | 6 / 12 | 6 / 12 |
| Frecuencia máxima | 4,57 GHz | 4,65 GHz |
| L3 | 16 MiB | 32 MB |
| RAM total | 14,8 GiB | 24 GB (3 × 8 GB, sin doble canal simétrico) |
| RAM disponible | 9,5 GiB con las apps habituales abiertas | No medido |
| Swap | zram 14,8 GiB (2,4 GiB en uso), swappiness 150 | No medido |
| Disco libre | 617 GB en NVMe Kingston NV2 | 566 GB en NVMe Kingston NV2 (+ HDD 500 GB) |
| Temperatura de CPU en reposo | 45,6–46,1 °C | No medido |
| Temperatura de CPU en uso | No medido | 74 °C en uso normal con Docker |
| NVMe | 48,9 °C | 52 °C |
| KVM / IOMMU | AMD-V, `kvm_amd` (nested=1), IOMMU con 27 grupos | AMD-V, IOMMU con 22 grupos. `/dev/kvm`: no medido |
| GPU | RTX 3050 Mobile + Radeon 680M | RTX 3060 |
| Energía | Enchufada, batería al 100 % (salud 83 %), perfil `performance` | Escritorio, sin UPS |
| Sistema | CachyOS, kernel 7.3.3-1-cachyos | CachyOS según el usuario. Kernel: no medido |
| Docker | Activo por socket. Redes 172.17–172.20/16, sin contenedores | Activo (docker0, ~13 br-*, ~18 veth). Subredes: no medido |
| Tailscale | Activo | Activo |
| Conflicto con 192.168.10/20/30.0/24 | Ninguno | No medido |
| Paquetes del laboratorio | Solo nftables, iptables, dnsmasq. Falta el resto (ver ficha) | No medido |
| Estabilidad (journal) | Sin OOM del kernel ni eventos térmicos. Avisos de memoria de la GPU NVIDIA | No medido |
| Uso | Estación de trabajo del usuario | Estación de trabajo, no dedicada |

## Lectura

- **Las dos sirven para el laboratorio virtual.** Las dos tienen KVM, 12 hilos y disco de sobra. El laboratorio es 100 % virtual (QEMU/KVM + Open vSwitch), así que el único puerto Ethernet de pc-miguel ya no es un problema.
- **La diferencia que importa es la RAM.** Con 24 GB, pc-miguel puede correr las 5 VMs completas con margen. La laptop llega justa para el piloto de 4 VMs.
- **Mismo sistema no significa mismos números.** CPU distinta (móvil y escritorio, caché L3 de la mitad), RAM distinta y comportamiento térmico distinto. Los scripts y la configuración sí se pueden calibrar en la laptop y llevar tal cual. Las mediciones del paper deben salir todas de una sola máquina (pc-miguel), sin mezclar resultados de las dos.
- **Para que la calibración se traslade,** hay que fijar las mismas versiones de paquetes (sobre todo Suricata desde AUR) y las mismas imágenes de VM. Los valores propios de cada máquina (RAM por VM, núcleos fijados) van en un archivo de configuración por plataforma.
