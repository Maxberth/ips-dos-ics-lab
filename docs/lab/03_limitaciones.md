# Limitaciones

Cada limitación con su impacto sobre la validez del estudio.

## L1. Laboratorio virtual en una sola máquina
Todo corre en una sola máquina física: VMs con QEMU/KVM y un switch Open vSwitch. El "PLC" es OpenPLC en una VM y su CPU no es la de un PLC físico. El switch es virtual: mide segmentación y aislamiento VLAN, no el hardware de un switch industrial. Debe declararse en el paper (obs. 4, 24, 25).

## L2. Desviaciones de software respecto al paper
| Paper | Laboratorio | Motivo |
|---|---|---|
| Kali Linux (atacante) | Debian 13 con `hping3` y `scapy` | Misma herramienta, una sola imagen base (D8) |
| pfSense 2.8.0-1 | nftables en Debian 13 | 100 % libre y reproducible por script (D3) |
| Ubuntu Server (Suricata, OpenPLC, SCADA) | Debian 13 | Una sola imagen base (D8) |
| HMI/SCADA gráfico | Cliente `pymodbus` a 10 Hz | Medición por solicitud y RAM (D4) |
| PLC en 192.168.1.10 | PLC en 192.168.30.10 (VLAN 30) | Topología Purdue de P06; la LAN de casa del host es 192.168.1.0/24 |

## L3. laptop-dev solo calibra
laptop-dev (Ryzen 5 6600H, 14,8 GiB) tiene menos RAM que pc-miguel y es una laptop: puede bajar la frecuencia por temperatura. Sus VMs tienen menos RAM (perfil `laptop-dev`). Sus datos son de calibración y no se usan en tablas ni figuras del paper ni se mezclan con los de pc-miguel.

## L4. Límites de RAM y temperatura condicionan las corridas
El guardián pausa (PAUSE) o aborta (ABORT) según la RAM disponible, la presión de memoria, el swap, la temperatura y, en laptop-dev, si el cargador está conectado. Puede alargar las corridas (enfriamiento entre repeticiones) y obliga a perfiles de corrida más cortos si el equipo no aguanta el perfil `final`.
