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

## D11. NFQUEUE sin `bypass` (fail-closed) y Suricata con cambios mínimos
- Sin `bypass`, si Suricata no lee la cola el tráfico se corta. Es más fiel a un IPS en línea y evita medir un "bloqueo" que en realidad es tráfico que pasa sin inspección. Se verifica en `check_chain.sh`.
- `suricata-lab.yaml` se genera con `lab/setup/make_suricata_yaml.py` sobre el `suricata.yaml` del paquete de Debian. Cambia solo: HOME_NET, `nfq: mode accept, fail-open no`, parser Modbus en el puerto 502, eve.json con alert, drop y stats cada 1 s, y stats.log.

## D12. Instalación de paquetes en las VMs por túnel SSH, sin NAT
- **Contexto:** ufw está activo en laptop-dev (A5) y no se debe cambiar el firewall del usuario.
- **Elección:** apt usa un proxy SOCKS inverso (`ssh -R 1080`) y OpenPLC un proxy HTTP local (`http_proxy.py`, solo en 127.0.0.1, `ssh -R 3128`). El proxy registra cada destino en `docs/lab/logs/P10_openplc_proxy_<plataforma>.txt`.
- **Ventaja:** las VMs solo salen a Internet mientras dura el comando de instalación. No hay NIC NAT que quitar antes de medir.

## D13. Grupos nuevos sin reiniciar la sesión
- libvirt: polkit (`/etc/group`). dumpcap/tshark: `newgrp wireshark` (CachyOS no trae `sg`). Así no hace falta cerrar la sesión gráfica.

## D14. Sistema de las VMs: Debian 13 con vídeo VGA mínimo
- Cada VM lleva `--video vga` (A4). Sin pantalla gráfica (`--graphics none`); la consola es el puerto serie.

## D15. Umbral de crecimiento de swap en laptop-dev: 3 GiB
- **Contexto:** con las 5 VMs encendidas, el guardián pasó a WARN por swap +884 MiB (el ABORT estaba en +1024). Al mismo tiempo, el PSI de memoria era 0,3 % y había 4,3 GiB disponibles.
- **Causa:** laptop-dev usa zram (swap comprimido en RAM) con `vm.swappiness=150`: el kernel manda páginas frías a zram aunque haya memoria. El crecimiento de swap no indica presión en esta configuración.
- **Elección:** en el perfil laptop-dev, ABORT por swap sube a +3072 MiB. Los criterios principales siguen siendo RAM disponible (PAUSE < 3 GiB, ABORT < 2 GiB) y PSI (PAUSE > 20 %). pc-miguel mantiene 1024 MiB hasta medir su configuración de swap.
- Evidencia: `data/raw/guard/guard_laptop-dev_20261117.csv` (18:41 UTC).

## D16. Aislamiento de la VLAN 99 de gestión en cada VM
- **Contexto:** todas las VMs tienen una NIC en la VLAN 99 para que el host las gestione por SSH. Sin más, el atacante podría alcanzar a las demás VMs por esa VLAN, saltándose el firewall y el IPS.
- **Elección:** tabla nftables `mgmtguard` (`lab/config/mgmt-guard.nft`) en todas las VMs: por la interfaz `mgmt` solo entra y sale tráfico con el host (192.168.99.1). En fw e ips va incluida en sus archivos de reglas.
- **Verificación:** `check_chain.sh` comprueba que el atacante no llega a la gestión de otra VM ni por la VLAN 99 ni a través del firewall.

## D17. En las corridas, eve.json registra solo estadísticas
- **Contexto:** con `drop`, cada paquete descartado de un flood genera una alerta: unos 4 M de líneas (≈ 3 GB) en 30 s. Llenaría el disco de lab-ips (6 GB) y añadiría carga de escritura que no es parte de la inspección.
- **Elección:** `suricata-lab-measure.yaml` (corridas E2/E3) registra en eve.json solo `stats` cada 1 s. Los contadores `detect.alert` e `ips.blocked/accepted` siguen contando todas las alertas y descartes. Como cada corrida tiene un solo tipo de ataque y una sola regla aplicable, la atribución por regla se mantiene. `suricata-lab.yaml` (con alert y drop en eve) se usa en las pruebas de `check_chain.sh`.
- eve.json se vacía al inicio de cada corrida. El tamaño final y el espacio libre quedan en `suricata_disk.txt`.
- **Limitación:** un IPS real registraría las alertas con limitación de tasa. Este coste de registro no se mide aquí (declarar en el paper).

## D18. Dos colas NFQUEUE con fanout y dos hilos de recepción en Suricata
- **Contexto:** A11. Con una cola, Suricata se satura en unos 58 kpps en laptop-dev y el kernel descarta lo demás sin distinguir ataque de tráfico legítimo.
- **Elección:** `queue num 0-1` en nftables (reparto por hash de flujo entre colas; `fanout` reparte por CPU y desequilibra, ver A13) y `suricata -q 0 -q 1`: una cola por vCPU del IPS (2 en los dos perfiles). Sigue sin `bypass` (D11).
- **Se mide en cada corrida:** `queue_dropped` por cola. En el paper se reportan por separado los descartes por regla (`ips.blocked`, `drop_reason.rules`) y por desbordamiento (`queue_dropped`).
- La corrida E3 con una cola queda en `data/raw` como evidencia, marcada en `notes`.

## D19. `exception-policy: ignore` en Suricata y regla Modbus sin depender del parser
- **Contexto:** A16. Con `auto`, un error del parser en modo IPS descarta el flujo aunque la regla esté en alert. Así no se puede atribuir el bloqueo a las reglas (obs. 10) y E2 deja de ser "solo detección".
- **Elección:** `exception-policy: ignore` y `stream.drop-invalid: no` (A17) en `suricata-lab*.yaml`. Regla 1000004 rev 2 con `dsize:>0` y `detection_filter` por origen.
- **Consecuencia:** el laboratorio mide la prevención por reglas. Lo que haría la configuración por defecto (`auto`) queda medido en las corridas previas a D19 y se reporta como hallazgo aparte.

## D20. Regla Modbus: umbral 20 segmentos/s por origen (rev 3). Cerrada por D22 (se mantiene y se declara como limitación)
- **Contexto:** con la rev 2 (100 segmentos/s), E3 mantuvo al SCADA al 100 % durante el ataque, pero OpenPLC cayó al final en 3 de 3 corridas `reduced`. Cada segmento del flood lleva 32 solicitudes, así que pasaban ~3 200 solicitudes/s antes del umbral.
- **Calibración en laptop-dev (perfil `reduced`, datos en `data/raw/runs/*E3_modbus_reduced*`):**
  - rev 2 (100/s): SCADA 100 %, PLC caído al final 3/3.
  - rev 3 (20/s): SCADA 100 %, llegan ~1 000–1 300 paquetes de ataque al PLC, PLC caído 2/2.
  - rev 4 + 1000005 (`flowbits`, descarta el flujo completo tras el umbral): PLC caído 1/1. La corrida siguiente quedó `failed` porque el PLC no se recuperó a tiempo.
- **Elección provisional:** rev 3. Es la más estricta sin riesgo para el SCADA (10 solicitudes/s) y no depende del parser.
- **Conclusión honesta:** con un único atacante y reglas por umbral, Suricata **protege la disponibilidad del SCADA durante el ataque, pero no evita que OpenPLC caiga al terminar el flood**. La causa en OpenPLC no está determinada (A18).
- **Opciones para decidir antes de las corridas finales:**
  1. Reportarlo tal cual: el resultado del escenario incluye "PLC caído tras el ataque".
  2. (No se hizo; pc-miguel no se usó) Probar `reject` (RST al atacante) en lugar de `drop`.
  3. Aislar la causa en OpenPLC (fuera del alcance del plazo).

## D21. Tanda real (perfil `final`) en laptop-dev
- **Contexto:** pc-miguel no está disponible. El usuario pidió el 2026-11-17 a las 21:23 UTC intentar la tanda real en esta laptop: en el piloto, la RAM no fue el límite (Tctl máximo de 82,6 °C, por debajo del PAUSE de 88 °C).
- **Alcance:** E0, E1 y E3 × {syn, modbus} × 10 repeticiones, perfil `final` (15 + 60 + 15 s), semilla 2027, regla Modbus rev 3 (D20, opción 1: "PLC caído tras el ataque" se reporta como resultado del escenario).
- **Regla que se mantiene:** cada corrida lleva `platform=laptop-dev` y `run_profile=final`. Si luego se mide en otra plataforma (pc-alem), sus datos van en tablas y figuras aparte. Nunca se mezclan.
- **Qué plataforma alimenta el paper** lo decide el usuario al final. Si es laptop-dev, se declaran sus limitaciones (L3: laptop, posible reducción de frecuencia por temperatura; techo del IPS de ~60–95 kpps).

## D22. La regla Modbus (rev 3) se mantiene tal cual y sus falsos positivos se declaran como limitación (decisión de Alberth, 2026-11-18)
- **Contexto:** A23. En modo `drop`, la regla 1000004 descarta paquetes legítimos del SCADA al final del ataque y en el enfriamiento (133–162 por corrida en las 4 calibraciones). Con D20 sigue abierto el umbral y el PLC cae tras el flood Modbus (E3: 6/10).
- **Opciones valoradas:** (a) dejarla y declararla; (b) recalibrar la regla (umbral o lista del SCADA) y repetir E3; (c) estudio adicional "E3 recalibrada" sin reemplazar las 130 corridas.
- **Elección:** (a). Las 130 corridas del perfil `final` usan una sola versión de reglas y de configuración (comprobado por hash), no se repiten corridas y el dataset queda homogéneo.
- **Consecuencias:** los resultados de E3 incluyen el efecto de esos falsos positivos en la fase de recuperación; se declara en L8 y en la sección de E3. La recalibración de la regla queda como trabajo futuro.

