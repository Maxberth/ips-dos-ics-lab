# Plataforma: laptop-dev

Laptop del usuario. Es la plataforma de todas las mediciones del estudio: en ella se instalaron y probaron los scripts de red, VM, firewall, Suricata y el arnés, y se hicieron las corridas piloto y las 130 finales.

**Medido el 2026-11-17 a las 12:16 (hora de Perú)**, en modo solo lectura y sin sudo. Las salidas literales están en [`../logs/laptop_P02_*.txt`](../logs/).

## Ficha

| Componente | Medido | Log |
|---|---|---|
| Equipo | Lenovo IdeaPad Gaming 3 15ARH7 (82SB), firmware JNCN52WW (2024-10-04), hostname `maxberth` | 01 |
| Sistema | CachyOS (rolling), kernel `linux-cachyos` 7.3.3-1 (PREEMPT_DYNAMIC). También tiene `linux-cachyos-lts` 6.18.60 instalado. Repos `cachyos-v3` | 01, 09 |
| CPU | AMD Ryzen 5 6600H: 6 núcleos / 12 hilos, pares SMT (0-1, 2-3 … 10-11), 412 MHz–4,57 GHz, L2 3 MiB, L3 16 MiB. `svm` presente | 02 |
| Frecuencia | Driver `amd-pstate-epp` (activo), gobernador `performance`, EPP `performance` | 02 |
| RAM | 14,8 GiB totales (15 161 MiB). **Disponible ahora: 9,5 GiB** (`MemAvailable`) | 03 |
| Swap | zram de 14,8 GiB (zstd), 2,4 GiB en uso. `swappiness` = 150. Sin swap en disco | 03 |
| OOM | `systemd-oomd` activo, `earlyoom` inactivo. Presión de memoria (PSI) en 0 | 03 |
| Procesos que más RAM usan | claude-desktop ≈ 1,8 GiB, caelestia ≈ 0,56 GiB, qs ≈ 0,55 GiB, notify-send ≈ 0,41 GiB, claude ≈ 0,36 GiB | 03 |
| Temperatura en reposo | Tres lecturas separadas 20 s: CPU (Tctl) 46,1 / 46,0 / 45,6 °C. GPU integrada 43–44 °C. NVMe 48,9 °C. Carga ≈ 0,6 | 04 |
| Ventiladores | `sensors` no muestra RPM: **no medido** | 04 |
| GPU | NVIDIA RTX 3050 Mobile (driver `nvidia`, paquetes `nvidia-open`) y AMD Radeon 680M integrada (`amdgpu`) | 09 |
| Energía | Enchufada (AC `online`), batería al 100 % y llena. Salud de la batería: 83 % de su capacidad original. Perfil `performance` | 04 |
| KVM | `/dev/kvm` existe (crw-rw-rw-), `kvm_amd` cargado con `nested=1`. IOMMU (AMD-Vi) activo, 27 grupos. No es una VM (`systemd-detect-virt` = none) | 05 |
| Disco | NVMe Kingston NV2 1 TB (`SNV2S1000G`), Btrfs. **617 GB libres** en `/` | 06 |
| Red | `wlan0` en 192.168.1.13/24 (LAN de casa), `enp2s0` sin cable, `tailscale0` | 07 |
| Redes en conflicto | Ninguna interfaz ni ruta usa 192.168.10/20/30.0/24. Docker usa 172.17–172.20.0.0/16 | 07 |
| Servicios | Tailscale activo. Docker: el servicio estaba inactivo, pero el socket está activo, así que arranca solo cuando algo lo usa (ver Riesgos). libvirtd y ovs-vswitchd no instalados | 07 |
| Paquetes del laboratorio | Instalados: nftables, iptables, dnsmasq, paru, texlive-binextra. Faltan, en repos oficiales: qemu, libvirt, virt-install, openvswitch, hping, python-scapy, iperf3, tcpdump, wireshark-cli, edk2-ovmf. Faltan, solo en AUR: **suricata 8.0.7**, snort 3.12.2, python-pymodbus 3.16.2 | 08 |
| Estabilidad | 4 arranques desde el 9-nov. Sin OOM del kernel, sin eventos térmicos ni MCE. Solo avisos `NVRM … Out of memory` del driver NVIDIA (memoria de la GPU), en este arranque y en el anterior | 10 |

## Veredictos

| Criterio | Veredicto | Dato |
|---|---|---|
| KVM | **CUMPLE** | `/dev/kvm`, `kvm_amd`, `svm`, IOMMU |
| ≥ 8 hilos | **CUMPLE** | 12 hilos |
| RAM libre para ~6 GiB de VMs + 4 GiB para el host (10 GiB) | **INCIERTO** | Ahora hay 9,5 GiB disponibles, justo por debajo. Cerrar Claude Desktop y la barra del escritorio liberaría unos 2–3 GiB más (**estimado, no medido**). Con 4 VMs del piloto (≈ 6 GiB) cabe si se cierran apps |
| Disco ≥ 120 GB libres | **CUMPLE** | 617 GB |
| Temperatura en reposo < 70 °C | **CUMPLE** | 45,6–46,1 °C. Bajo carga sostenida: **no medido** |
| Enchufada | **CUMPLE** | AC conectado, 100 % |

## Riesgos y notas

- **RAM al límite.** Con 14,8 GiB, 4 VMs del piloto entran solo cerrando aplicaciones. Las 5 VMs del escenario completo (10 GiB) no entran con margen. zram ayuda, pero si las VMs empiezan a usar swap, las mediciones salen distorsionadas.
- **Es una laptop.** Bajo carga sostenida (floods + Suricata) puede bajar la frecuencia por temperatura o por el perfil de energía. No se midió bajo carga. Sirve para calibrar, no para los números finales.
- **Suricata, Snort y pymodbus vienen de AUR** (compilación). Las versiones se fijan y se registran en `data/raw/versions/`.
- **Docker por socket.** Durante este inventario, `docker network ls` arrancó `dockerd` (12:16:46) por activación de socket. Sigue activo. No hay contenedores corriendo. Para medir, conviene detenerlo.
- **La LAN de casa es 192.168.1.0/24.** El paper usaba direcciones 192.168.1.x para el PLC. El plan nuevo (P06) usa 192.168.10/20/30/99, así que no choca. No hay que volver a las direcciones del paper.
- **Logs con datos del equipo.** Los logs incluyen MAC, IP local, IP de Tailscale y UUID del disco. El repositorio es privado. Si se publica, hay que anonimizarlos.
