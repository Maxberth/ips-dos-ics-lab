# Laboratorio ICITS'27 desde cero: hardware, arquitectura y costo de cómputo

**Base de cálculo:** no existen scripts, configuraciones ni datos de las pruebas originales. Todo lo que sigue se diseña de nuevo. Los números de consumo son **estimaciones de planificación**; se validan con una prueba piloto antes de comprar o asignar recursos.

**Sistema operativo de todos los equipos:** Linux basado en Arch (CachyOS o Arch). Kernel con soporte KVM (`/dev/kvm`), `nftables`, `libnetfilter_queue`.

**Enfoque 100 % software libre:** todos los componentes son FOSS (GPL, MIT, BSD o Apache): Arch Linux, QEMU/KVM, libvirt, Open vSwitch, nftables, Suricata, OpenPLC Runtime, hping3, Scapy, iperf3, Wireshark, tcpdump, pymodbus. Ningún componente requiere licencia comercial, lo que permite replicar el laboratorio en empresas sin presupuesto para licencias.

**Referencia de este equipo** (medido hoy en el PC de Alberth):

| Recurso | Valor medido | Lectura |
|---|---|---|
| CPU | 12 hilos, 1 socket | Suficiente para el laboratorio con 3–4 VMs |
| RAM | 14 GiB totales, 8,4 GiB en uso, 6,4 GiB disponibles | **Insuficiente** para el laboratorio completo en un solo equipo |
| Disco | NVMe, 643 GiB libres en `/home` | Suficiente |
| Virtualización | `/dev/kvm` presente, 12 banderas `vmx`/`svm` | Apto para KVM/QEMU |
| Red | `enp2s0` (cable, sin conexión), `wlan0`, `tailscale0` | Hace falta un adaptador cableado y, si se usa un solo PC, sin Wi-Fi para el laboratorio |
| Herramientas | Sin QEMU, libvirt, Suricata, hping3, tcpdump, iperf3 | Todo debe instalarse |

---

## 1. Recomendación de arquitectura

**Recomendación:** usar **KVM/QEMU con libvirt** como hipervisor. En Arch es lo nativo, tiene mejor rendimiento de red virtual y permite fijar CPU (`cpuset`). El switch se simula con **Open vSwitch** (VLAN 802.1Q, trunks y contadores por puerto). No se usa GNS3 ni VirtualBox.

**Por qué no basta un solo PC:** los floods (`hping3 --flood`, `ping -f`) consumen CPU del host. Si el atacante, el IPS y el PLC están en el mismo equipo, la CPU medida del PLC y la latencia quedan contaminadas por el propio generador de ataque. Para que la medición sea defendible, el atacante debe correr en una máquina distinta o, como mínimo, con núcleos fijados y sin compartir con el IPS.

Por eso se proponen dos escenarios.

---

## 2. Escenario A: un solo PC (válido para empezar y para validar la metodología)

### 2.1 Topología
- Un switch virtual Open vSwitch `ovs-ot` con VLAN 10 (IT/atacante), VLAN 20 (DMZ/SCADA) y VLAN 30 (PLC).
- Las VMs se conectan a `ovs-ot` con etiquetas VLAN (puertos access) y los enlaces entre equipos son trunks.
- Un router Linux con `nftables` separa VLAN 10 de VLAN 20. Es la opción 100 % FOSS y la más ligera. pfSense CE (Apache 2.0) u OPNsense (BSD) son alternativas válidas si el equipo prefiere interfaz web.
- Suricata corre en una VM con dos interfaces: una en VLAN 20 y otra en VLAN 30, con reenvío inline por NFQUEUE.

### 2.2 Máquinas virtuales

| VM | Función | vCPU | RAM | Disco | Notas |
|---|---|---|---|---|---|
| Atacante (Arch con `hping3`, `scapy`, `iperf3`) | Genera floods | 2 | 3 GB | 20 GB | Fijar a núcleos 0–1 |
| Router/firewall (Arch con nftables) | Separa VLAN 10/20 | 1 | 1 GB | 8 GB | Alternativa: pfSense CE u OPNsense |
| Suricata (Arch o Ubuntu Server) | IPS inline NFQUEUE | 3 | 4 GB | 25 GB | Fijar a núcleos 4–6 |
| OpenPLC Runtime | PLC simulado (Modbus/TCP 502) | 1 | 1 GB | 8 GB | Fijar a núcleo 7 |
| SCADA/cliente Modbus (Python `pymodbus`) | Consultas periódicas | 1 | 1 GB | 8 GB | Fijar a núcleo 8 |
| Host (Arch) | Hipervisor, captura, medición | 3 libres | 4 GB | — | Reservado |
| **Total asignado a VMs** | | **8 vCPU** | **10 GB** | ~95 GB | |

Con esta tabla, las VMs suman 10 GB y el host reserva 4 GB, o sea 14 GB en total. Ese es justo el RAM de este PC, pero sin margen: el sistema ya usa 8,4 GB con las aplicaciones abiertas, así que **hoy no cabe** sin cerrar programas. Para no degradar mediciones (caché, swap), **32 GB** es lo recomendable.

### 2.3 Requisitos del equipo (Escenario A)

| Componente | Mínimo para piloto | Recomendado para pruebas finales |
|---|---|---|
| CPU | 8 hilos | 12–16 hilos, con virtualización |
| RAM | 16 GB (piloto con 4 VMs y el host) | **32 GB** |
| Almacenamiento | 150 GB libres en NVMe | 300 GB libres en NVMe (capturas `pcap` de floods de 5 min pueden ocupar varios GB por corrida) |
| Red | 1 puerto Ethernet (para `enp2s0`) y un adaptador USB 3.0 Gigabit para segundo puerto | 2 puertos Ethernet dedicados al laboratorio |
| Software | QEMU, libvirt, virt-manager, edk2-ovmf, dnsmasq, Suricata 7.x, nftables, hping3, scapy, iperf3, wireshark-cli, tcpdump | Igual, versiones fijadas |

**Lectura para el equipo:** con este PC (12 hilos, 14 GB), el piloto es posible reduciendo a 4 VMs, cerrando los programas de escritorio. Para las pruebas finales se necesita **ampliar la RAM a 32 GB**. Es la inversión más barata y la que más desbloquea el proyecto.

### 2.4 Limitación de este escenario
- El PLC es simulado (OpenPLC en VM), su CPU no es la de un PLC físico. Esto debe declararse en el paper.
- Mismo host para todo: el ruido de CPU entre VMs afecta la medición de latencia. Se mitiga con `cpuset` y con repeticiones.
- No hay switch físico. El switch es virtual (Open vSwitch). Mide segmentación y aislamiento VLAN, no el hardware de un switch industrial; eso debe declararse en el paper.

---

## 3. Escenario B: varios equipos (recomendado para medición defendible)

Tres equipos para aislar atacante, IPS y PLC, con el switch virtual en PC-2:

| Equipo | Rol | CPU | RAM | Almacenamiento | Red | Software |
|---|---|---|---|---|---|---|
| **PC-1 Atacante** | Genera floods | 4 núcleos (4–6 hilos) | 8 GB | 128 GB SSD | 1 GbE (idealmente 2,5 GbE) | Arch, `hping3`, `scapy`, `ping`, `iperf3` |
| **PC-2 IPS/Firewall** | Suricata inline + nftables | **6 núcleos / 12 hilos** (Suricata es intensivo en CPU) | 16 GB | 256 GB NVMe | **2 puertos Ethernet Intel (i210/i350 PCIe)** para NFQUEUE entre VLAN 20 y 30 | Arch, Suricata 7.x, nftables, libnetfilter_queue, tcpdump |
| **PC-3 PLC/SCADA** | OpenPLC + cliente SCADA + medición | 4 núcleos | 8 GB | 128 GB SSD | 1 GbE | Arch, OpenPLC Runtime, `pymodbus`, `sar`/`pidstat` |
| Switch virtual (Open vSwitch, en PC-2 o en PC-3) | Segmentación VLAN 802.1Q | — | 0,5 GB | — | Virtual, sin hardware extra | Open vSwitch con `vlan_mode=access/trunk`; contadores con `ovs-ofctl dump-ports` |
| **Mini PC / Raspberry Pi 4** (opcional, no requerido) | PLC físico (no lo pidió el revisor) | 4 núcleos | 4–8 GB | 32 GB | 1 GbE | OpenPLC en Raspberry Pi, si el equipo quiere validar con hardware real |

**Por qué PC-2 necesita más CPU:** Suricata en modo inline (NFQUEUE) procesa cada paquete en CPU. Con floods de SYN pequeños, el cuello de botella es la tasa de paquetes por segundo (pps), no el ancho de banda. Un PC con 6 núcleos y NIC Intel evita que el IPS mismo sature y falsifique la medición.

**Por qué 2 puertos Intel en PC-2:** los puertos integrados y los USB no son estables para pps altos. La NIC Intel PCIe (i350 de dos puertos, o dos i210) es la más segura en Linux.

### 3.1 Conexión física
```
PC-1 (atacante) ──VLAN 10── [OVS en PC-2] ──VLAN 20/30── PC-2 (IPS inline) ──VLAN 30── PC-3 (PLC/SCADA)
                                                     │
                                          eth1 VLAN 20 / eth2 VLAN 30 (bridge inline)
```
Dos puertos de PC-2 forman el puente inline. Todo el tráfico entre VLAN 20 y 30 pasa por Suricata.

### 3.2 Costo de cómputo total (Escenario B)
- CPU: 14 núcleos en total entre PC-1, PC-2 y PC-3.
- RAM: 32 GB en total.
- Disco: ~512 GB SSD en total.
- Red: 1 PC con NIC Intel de dos puertos y un switch Open vSwitch virtual (sin hardware extra). Un switch físico de 8 puertos es opcional.

---

## 4. Tiempo estimado de cómputo para las pruebas (validar en piloto)

| Concepto | Cálculo | Total |
|---|---|---|
| Escenarios | 4 ataques (SYN, ICMP, UDP, Modbus) | 4 |
| Condiciones | con IPS y sin IPS | 2 |
| Repeticiones | 10 por combinación | 10 |
| Duración por corrida | 5 min de ataque + 1 min de calentamiento | 6 min |
| Tiempo total de ataques | 4 × 2 × 10 × 6 min | **480 min ≈ 8 h** |
| Línea base | 10 corridas × 5 min | 50 min |
| Montaje y depuración | — | 1–2 días |

**Conclusión:** la ejecución de las pruebas cabe en una jornada. El cuello de botella es el montaje y la depuración del laboratorio, no el cómputo.

---

## 5. Lo que no se puede resolver en dos días (sin decisión del equipo)

- **Conseguir hardware:** comprar RAM, NIC Intel o PC adicional toma días. Si no llega antes del 18 de noviembre, el piloto debe hacerse en este PC (Escenario A con 4 VMs, sin repeticiones de 10).
- **Duración real del montaje:** instalar Suricata inline con NFQUEUE, validar la topología VLAN y depurar la cadena (PLC responde, Suricata ve el tráfico, la regla `drop` funciona) toma entre 1 y 2 días.
- **Afirmación de prevención:** si no se llega a montar NFQUEUE con `drop`, el texto debe reducir la afirmación a detección y alerta, tal como indica la matriz de observaciones.

---

## 6. Próximos pasos recomendados (en orden)

1. **Hoy:** instalar `qemu-desktop libvirt virt-manager edk2-ovmf dnsmasq nftables suricata hping scapy iperf3 wireshark-cli tcpdump`. Verificar con los repositorios oficiales y AUR; los nombres de paquetes pueden variar.
2. **Hoy:** crear la topología Escenario A con 4 VMs (atacante, Suricata, PLC, SCADA) con VLAN, y comprobar que el PLC responde por Modbus y que Suricata ve el tráfico.
3. **Mañana:** montar reglas `drop` con NFQUEUE y probar un flood SYN corto (30 s) con y sin IPS.
4. **Decisión del equipo:** ampliar la RAM de este PC a 32 GB o usar el Escenario B con PC-2 dedicado.

---

## 7. Resumen de cómputo por escenario (stack 100 % libre)

Cifras de planificación. Cada una incluye el switch Open vSwitch (≈0,5 GB RAM, <1 núcleo) y el host Arch con su propio consumo.

### 7.1 Escenario A: un solo PC

| Concepto | Mínimo (piloto, 4 VMs) | Recomendado (5 VMs + host) |
|---|---|---|
| vCPU asignados a VMs | 5 (atacante 2, Suricata 2, OpenPLC 1) | 8 (atacante 2, router 1, Suricata 3, OpenPLC 1, SCADA 1) |
| RAM asignada a VMs | 8 GB | 10 GB |
| Reserva del host (Arch + Open vSwitch + captura) | 3 GB | 4 GB |
| **Hilos de CPU del equipo** | **≥ 8** | **≥ 12 (16 cómodo)** |
| **RAM del equipo** | **16 GB** | **32 GB** |
| **Disco libre (SSD/NVMe)** | 120 GB | 300 GB (capturas `pcap` por corrida) |
| Nota | Con este PC (12 hilos, 14 GB) el piloto cabe cerrando programas. | Con este PC, requiere ampliar RAM a 32 GB. |

Limitación: el atacante y Suricata comparten CPU con las VMs del mismo equipo. Fijar núcleos con `cpuset` reduce la contaminación de la medición, pero no la elimina.

### 7.2 Escenario B: varios PC

| Equipo | Rol | Núcleos / hilos mínimos | RAM mínima | Disco | Red |
|---|---|---|---|---|---|
| PC-1 | Atacante (Arch, hping3, Scapy) | 4 / 4 | 8 GB | 128 GB SSD | 1 GbE |
| PC-2 | IPS inline (Suricata + nftables) + switch OVS | 6 / 12 (mínimo 4 / 8) | 16 GB | 256 GB NVMe | NIC Intel de 2 puertos PCIe (i350 o 2× i210) |
| PC-3 | PLC OpenPLC + SCADA + medición | 4 / 4 | 8 GB | 128 GB SSD | 1 GbE |
| **Total** | | **14 / 20** | **32 GB** | **~512 GB** | |

Motivo para PC-2: Suricata en NFQUEUE consume CPU por paquete. Con floods de SYN, el límite es la tasa de paquetes por segundo, no el ancho de banda. La NIC Intel es más estable que puertos USB para pps altos.

### 7.3 Lectura para el equipo

- **Un solo PC:** es la opción más barata y rápida de arrancar. Su costo real es **llevar la RAM a 32 GB**. Con eso, el piloto y las pruebas finales caben.
- **Varios PC:** es la opción más defendible para medir, porque el atacante y el IPS no compiten por CPU. Exige reunir tres equipos y una NIC Intel de dos puertos.
- **Tiempo de cómputo de las pruebas:** unas 8 horas en total (ver §4). El cuello de botella es montar y depurar la cadena, no la ejecución.
