# Problemas y anomalías

Todo lo raro, aunque se resuelva: síntoma, hipótesis, evidencia y resolución.

## A1. Prueba de scope con `bytearray` no reservó memoria real (resuelta)
- **Síntoma:** un scope con `MemoryMax=256M` que crea `bytearray(600 MiB)` terminó con exit 0.
- **Causa:** `bytearray(n)` usa páginas a cero que el kernel no asigna hasta escribirlas.
- **Resolución:** la prueba escribe los datos (`b'\x01'*600MiB`) y el scope muere con exit 137. Evidencia: `docs/lab/logs/P04_pruebas_guardian.txt`.

## A2. Las simulaciones del guardián escribieron en `data/raw/` (resuelta)
- **Síntoma:** filas con umbrales simulados en `data/raw/guard/guard_laptop-dev_*.csv`.
- **Resolución:** se borró el archivo y `guard.sh` acepta `GUARD_CSV` para que las simulaciones escriban fuera de `data/raw`.

## A3. `docker network ls` arrancó dockerd por socket durante P02
- Ver `docs/lab/contenedores_apagados.md`. `root_setup.sh` lo detiene.

## A4. Las VMs entraban en bucle de reinicio justo después de GRUB (resuelta)
- **Síntoma:** la consola serie de lab-fw mostraba solo `Booting 'Debian GNU/Linux'` en bucle (unas 2 veces por segundo). El disco nunca se escribió (196 KiB).
- **Descartado, con prueba:** `hard_limit`, `cputune`, el modelo de CPU (host-passthrough, host-model EPYC-Milan) y la RAM (512 MiB arranca en QEMU directo).
- **Causa:** sin tarjeta de vídeo. `virt-install --graphics none` no crea dispositivo de vídeo, y el kernel cloud de Debian 13 (6.12.117) se reinicia al arrancar sin él. Reproducido con QEMU directo: `-vga none` provoca 40 reinicios en 15 s; con VGA arranca hasta `login:`.
- **Resolución:** `create_vm.sh` añade `--video vga`. No afecta a las mediciones.

## A5. El firewall del host (ufw) bloquea el DHCP de la red NAT de libvirt (evitada)
- **Síntoma:** la NIC `nat` de lab-fw no obtuvo IPv4 y cloud-init no pudo instalar paquetes.
- **Causa:** `ufw` está activo en laptop-dev y descarta el tráfico entrante desde `virbr-labi` (DHCP, DNS y reenvío).
- **Resolución sin tocar el firewall del usuario:** las VMs instalan paquetes a través de la conexión SSH del host: un proxy SOCKS inverso (`ssh -R 1080`) para apt, y para OpenPLC un proxy HTTP local (`lab/setup/http_proxy.py`, solo en 127.0.0.1) que llega por `ssh -R 3128`. Ver D12. La red NAT `lab-install` deja de ser necesaria.

## A6. `sg` no existe en CachyOS (resuelta)
- **Síntoma:** `sudo: sg: command not found` en el paso 8 de `root_setup.sh`.
- **Resolución:** libvirt autoriza por polkit según `/etc/group`, así que `virsh` funciona sin reiniciar la sesión. Para `dumpcap` (grupo wireshark) se usa `newgrp`, que sí existe (setuid). Ver D13.

## A7. Mirror de CachyOS con 404 para rdma-core (sin efecto)
- pacman no pudo bajar `rdma-core-65.0-1.1` de dos mirrors (404), pero lo instaló desde otro. `pacman -Q rdma-core` = 65.0-1.1 y `pacman -Qk` no muestra archivos faltantes. Evidencia: `docs/lab/logs/P05_verificacion_host_laptop-dev.txt`.

## A8. cloud-init queda en `status: error` en lab-fw
- Ocurrió porque cloud-init intentó instalar paquetes sin red (A5). La VM funciona y los paquetes se instalaron después por el proxy. Las VMs creadas después ya no piden paquetes a cloud-init.
