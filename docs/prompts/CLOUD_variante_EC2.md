# Variante cloud: el mismo laboratorio en un servidor (EC2 u otro)

> **Documento histórico:** no aplica al estudio final: desde el 2026-11-18 la única plataforma es `laptop-dev` (ver `CLAUDE.md` y `docs/lab/03_limitaciones.md`, L3). Se conserva como registro de cómo se planeó el trabajo.

**Prioridad: OPCIONAL** (la ruta principal es la PC local con CachyOS). Útil si la PC no aguanta térmicamente o si quieres correr las 40+ corridas sin riesgo para el equipo.

## ¿Se puede? Sí, con tres matices

| Opción | Qué es | Veredicto |
|---|---|---|
| **1. Instancia metal o con virtualización anidada** | `*.metal` (p. ej. `c5.metal`, `m5.metal`, `c6a.metal`, `m6a.metal`) permiten KVM real. Las instancias normales de EC2 (Nitro) **no** exponen `/dev/kvm`, salvo familias con virtualización anidada habilitada (verifica en la documentación de AWS vigente, la lista cambia). | Réplica más fiel al diseño local (mismas VMs). Cara por hora (varios USD/h); se usa solo durante las corridas y se apaga. |
| **2. Contenedores + network namespaces** | Sin VMs: cada rol en un `netns`/contenedor, Open vSwitch o bridges Linux, Suricata con NFQUEUE en el namespace del IPS, OpenPLC en contenedor. | Funciona en cualquier instancia Linux normal (barata), pero cambia el sistema bajo prueba (kernel compartido): es una **desviación metodológica** que debe declararse. pfSense no corre así: usar nftables. |
| **3. Un servidor dedicado/VPS con KVM (Hetzner, OVH, etc.)** | Mismo diseño que local. | Alternativa más barata que EC2 metal. |

**Medición y aislamiento:** con una sola instancia cloud los floods generan mucho tráfico interno; no se ataca nada fuera de la red virtual. Revisa la política de uso aceptable del proveedor (los floods deben quedar dentro de la VPC/instancia, sin salir a Internet; no uses IP públicas como objetivo). Sin acceso físico, deja `ssh` solo por clave, sin exponer puertos de laboratorio.

**Limitación a declarar:** CPU, temperatura y vecinos ruidosos no son comparables con la PC local; resultados de la nube y de la PC **no se mezclan** en la misma tabla sin declararlo como otra plataforma (columna `platform` en `runs.csv`).

## Diferencias frente a los prompts P01–P22

| Prompt | Cambio en la variante cloud |
|---|---|
| P01 | Igual: clonar el repo en la instancia (`git clone`, rama `lab/ips-icits27`), mismas reglas. Subir datos con `git`/`rsync` y no dejar claves en el repo. |
| P02 | Usa `lscpu`, `free`, `cat /sys/devices/system/cpu/vulnerabilities`, `ls /dev/kvm` (sin KVM → Opción 2); en lugar de temperatura, vigila `steal` (`mpstat`, `vmstat`: columna `st`) y créditos de CPU en instancias *burstable* (evita `t3`, usa instancias de CPU dedicada). IOMMU irrelevante. |
| P03 | Mismo inventario; SO típico: **Ubuntu Server 24.04** (`apt` en vez de `pacman`). Paquetes: `qemu-kvm libvirt-daemon-system virtinst openvswitch-switch nftables suricata hping3 python3-scapy iperf3 tcpdump tshark jq sysstat python3-pandas python3-scipy python3-matplotlib cloud-image-utils`. Snort 3 por compilación o PPA verificado. |
| P04 | Sin límite térmico; sí límites de RAM/CPU con `systemd`/cgroups igual que local (`machine.slice`, `MemoryMax`), ahora con más margen (p. ej. instancia de 64 GB). El guardián cambia temperatura por `steal` > 10 % sostenido → PAUSE. Añade una **alarma de facturación** (AWS Budgets) y un temporizador de apagado (`shutdown -h +480`) por si te olvidas de apagar. |
| P05 | `apt` con paquetes anteriores; mismas verificaciones (`suricata --build-info | grep -i nfq`, `virt-host-validate`). |
| P06 | Idéntico con OVS; puede usarse `ovs-vsctl` y libvirt tal cual. En Opción 2: `ip netns add` + `veth` + puertos OVS `tag=`. Ninguna interfaz de la instancia (`ens5`) se conecta al bridge del laboratorio. |
| P07 | VMs Ubuntu con cloud-init igual. Sin virtualización anidada: sustituir VMs por contenedores/namespaces (OpenPLC en Docker/Podman con red `macvlan`/`veth` hacia OVS). |
| P08 | pfSense solo en Opción 1/3 (ISO instalada vía consola serie VNC); en Opción 2, `nftables` en un netns router (decisión B de P08). |
| P09 | NFQUEUE igual: el namespace/VM del IPS con `nft … queue num 0` y Suricata `-q 0`. Verifica que los drivers `virtio` no pierdan checksums (`ethtool -K`). |
| P10–P12 | Igual. Relojes: `chrony` contra la fuente del proveedor; mide RTT en un mismo reloj. |
| P13–P19 | Igual, con más repeticiones posibles por tiempo; vigila `steal` y registra `platform`, tipo de instancia (`ec2-instance-type`), región y fecha en `runs.csv`. Ejecuta dentro de `tmux`. |
| P20–P22 | Igual; los scripts de análisis pueden ejecutarse en la PC con los CSV descargados (`rsync`). |

## Prompt corto para arrancar en la nube (pegar en Claude Code dentro de la instancia)

> Estamos en una instancia cloud Linux (Ubuntu 24.04), no en mi PC CachyOS. Lee `CLAUDE.md` del repo (clónalo primero: pregúntame la URL y la ruta) y los prompts `P01`–`P22` en `prompts_laboratorio/`. Aplica la sección "Variante cloud" del archivo `CLOUD_variante_EC2.md`: usa `apt`, no `pacman`; comprueba `/dev/kvm` y, si no existe, usa contenedores/namespaces y registra la desviación; sustituye la vigilancia de temperatura por `steal`; añade `platform=cloud`, tipo de instancia y región al `runs.csv`; no expongas puertos y no ataques nada fuera de la red virtual. Empieza por P02 en modo solo lectura y espera mi confirmación entre prompts.

## Costos (orientativo; verifica precios actuales)
Una máquina `.metal` de 48+ vCPU puede costar varios USD/hora; las corridas completas caben en ≈ 8–10 h, más montaje. Apaga y destruye la instancia al terminar y descarga `data/raw/`, `docs/lab/` y `figures/` al repo antes de hacerlo.
