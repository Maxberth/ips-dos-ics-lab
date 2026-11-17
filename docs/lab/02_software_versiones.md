# Versiones de software

Una fila por componente y plataforma. Fecha en UTC.

| Plataforma | Componente | Versión exacta | Origen | Fecha (UTC) |
|---|---|---|---|---|
| laptop-dev | Imagen base VMs: debian-13-genericcloud-amd64.qcow2 | Last-Modified 2026-11-16 16:59 UTC, 344 260 608 bytes, SHA512 37cb32b320820417eb04b335afcf489b… (OK con SHA512SUMS) | https://cloud.debian.org/images/cloud/trixie/latest/ | 2026-11-17 |
| laptop-dev | nftables (host) | 1:1.1.7-3.1 | pacman (instalado previamente) | 2026-11-17 |
| laptop-dev | iptables (host) | 1:1.8.13-1.1 | pacman (instalado previamente) | 2026-11-17 |
| laptop-dev | dnsmasq (host) | 2.93-1.1 | pacman (instalado previamente) | 2026-11-17 |
| laptop-dev | python (host) | 3.14.9-2 | pacman (instalado previamente) | 2026-11-17 |
| laptop-dev | python-numpy (host) | 2.5.4-1.1 | pacman (instalado previamente) | 2026-11-17 |
| laptop-dev | python-matplotlib (host) | 3.11.2-1 | pacman (instalado previamente) | 2026-11-17 |
| laptop-dev | jq (host) | 1.8.2-1.1 | pacman (instalado previamente) | 2026-11-17 |
| laptop-dev | lm_sensors (host) | 1:3.6.2-1.1 | pacman (instalado previamente) | 2026-11-17 |
| laptop-dev | systemd (host) | 262.2-1 | pacman (instalado previamente) | 2026-11-17 |
| laptop-dev | linux-cachyos (host) | 7.3.3-1 | pacman (instalado previamente) | 2026-11-17 |
| laptop-dev | Punto de reversión del sistema | snapper root 121 (antes) / 122 (después) de instalar los paquetes del laboratorio | snap-pac | 2026-11-17 |
| laptop-dev | qemu-base / qemu-system-x86 / qemu-img (host) | 11.1.3-1 | pacman extra | 2026-11-17 |
| laptop-dev | libvirt (host) | 1:12.9.0-1.1 | pacman cachyos-extra-v3 | 2026-11-17 |
| laptop-dev | virt-install (host) | 5.1.0-4 | pacman extra | 2026-11-17 |
| laptop-dev | openvswitch (host) | 4.0.0-2.1 (arrastra dpdk 25.11.3-3) | pacman cachyos-extra-v3 | 2026-11-17 |
| laptop-dev | edk2-ovmf (host) | 202608-1 | pacman extra | 2026-11-17 |
| laptop-dev | wireshark-cli: dumpcap y tshark (host) | 4.7.4-1 | pacman extra | 2026-11-17 |
| laptop-dev | tcpdump (host) | 4.99.7-2.1 | pacman cachyos-extra-v3 | 2026-11-17 |
| laptop-dev | python-scipy / python-pandas (host) | 1.18.1-1.1 / 2.3.3-7.1 | pacman cachyos-extra-v3 | 2026-11-17 |
| laptop-dev | stress-ng / sysstat (host) | 0.22.02-1.1 / 12.8.0-1.1 | pacman cachyos-extra-v3 | 2026-11-17 |
| laptop-dev | Kernel del host | linux-cachyos 7.3.3-1, sin cambios (mkinitcpio regeneró los initramfs por los hooks, sin actualizar el kernel) | — | 2026-11-17 |
| laptop-dev | lab-fw (VM) | Debian 13, kernel 6.12.117+deb13-cloud-amd64; nftables 1.1.3-1, conntrack 1:1.4.8-2, tcpdump 4.99.5-2, sysstat 12.7.5-2, jq 1.7.1-6+deb13u4 | deb.debian.org (trixie) | 2026-11-17 |
| todas | OpenPLC_v3 (commit fijado) | b5d41356dab4aeadca0dd7ca64ba542f870b595d | github.com/thiagoralves/OpenPLC_v3 | 2026-11-17 |
