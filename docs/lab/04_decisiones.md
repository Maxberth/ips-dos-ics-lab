# Decisiones

Una entrada por decisión: contexto, alternativas, elección y motivo.

## D1. Hipervisor: QEMU/KVM con libvirt (`qemu:///system`)
- **Contexto:** hay que correr 5 VMs con límites duros de RAM y CPU en una sola máquina.
- **Alternativas:** VirtualBox, GNS3, contenedores.
- **Elección:** KVM/libvirt. Es nativo en Arch/CachyOS, permite `memtune hard_limit`, `vcpupin` y que todas las VMs queden en `machine.slice` con un tope común.
- **Uso sin sudo:** el usuario entra en el grupo `libvirt` una sola vez (`lab/setup/root_setup.sh`). Mientras la sesión gráfica no se reinicie, los scripts usan `sg libvirt`.

## D2. Switch: Open vSwitch `ovs-ot` sin puertos físicos
- **Elección:** OVS con VLAN 802.1Q 10/20/30, gestión en la 99 y dos espejos (VLAN 20 → `mir20`, VLAN 30 → `mir30`) para capturar en el host.
- **Motivo:** el paper habla de un switch industrial, pero no hay hardware. OVS mide segmentación y aislamiento VLAN, no el hardware de un switch (ver limitaciones).

## D3. Firewall: Linux + nftables en una VM Debian (opción B)
- **Alternativas:** A) pfSense CE 2.8 (fiel al paper, ISO de descarga manual e instalación interactiva). B) nftables en Linux.
- **Elección:** B, aprobada por el usuario el 2026-11-17. Es 100 % libre, se configura por script y se reproduce igual en las dos plataformas.
- **Consecuencia:** desviación respecto al paper (pfSense 2.8.0-1), declarada en `03_limitaciones.md`.

## D4. SCADA: cliente `pymodbus` en lugar de HMI gráfica
- **Elección:** script `scada_poller.py` a 10 Hz. Mide cada solicitud (RTT, éxito). Una HMI gráfica (FUXA o ScadaBR) no cabe en la RAM de laptop-dev y no aporta a la medición.

## D5. Presupuesto de recursos por plataforma
- Se define en `lab/config/profile_<plataforma>.env`. Los scripts no cambian entre plataformas.
- **laptop-dev:** VMs 4,75 GiB (atacante 1,25, fw 0,5, ips 1,5, plc 0,75, scada 0,75). `machine.slice` MemoryHigh 6 GiB y MemoryMax 6,5 GiB, sin swap. Núcleo 0 (hilos 0-1) reservado al host.
- **pc-miguel:** VMs 8 GiB, MemoryHigh 11 GiB, MemoryMax 12 GiB. Pendiente de confirmar con su inventario.

## D8. Sistema de las VMs: Debian 13 (trixie) genericcloud, atacante incluido
- **Alternativas:** Kali (paper) para el atacante, Ubuntu Server 24.04 para el resto.
- **Elección:** una sola imagen base, Debian 13 genericcloud amd64, con copias ligeras (`qcow2` con backing file). El atacante usa `hping3` y `scapy` de Debian, que son las mismas herramientas que en Kali.
- **Motivo:** una sola descarga (344 MB, verificada con SHA512), menos RAM y la misma imagen en las dos plataformas. Aprobado por el usuario el 2026-11-17.

## D9. Aprovisionamiento con cloud-init y NAT temporal
- Cada VM se crea con `lab/setup/create_vm.sh` (seed NoCloud con `cloud-localds`, IP fijas por MAC determinista).
- Para instalar paquetes se añade una NIC temporal en la red NAT `lab-install` (192.168.250.0/24), que se quita antes de medir. Sin ella, las VMs no tienen ruta a Internet ni al host, salvo la gestión (VLAN 99).
- La clave SSH del laboratorio (`~/.ssh/ips-lab_ed25519`) se genera en el equipo y no se versiona.
- Se desactivan en las VMs los timers de mantenimiento (`apt-daily`, `man-db`, `fstrim`…) para no contaminar las mediciones.

## D10. El guardián corre como servicio de usuario
- **Elección:** `systemd-run --user` (`lab/guard/guard-start.sh`), con los indicadores en `$XDG_RUNTIME_DIR/ips-lab/` en lugar de `/run/lab/`, para no necesitar root.
- Ante ABORT destruye solo las VMs con prefijo `lab-`. Los umbrales salen del perfil de plataforma.
