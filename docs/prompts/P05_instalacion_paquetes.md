# P05 · Instalación de paquetes del host (paso a paso, con verificación)

**Prioridad: IMPRESCINDIBLE** · Tiempo: 30–60 min (según compilación de AUR)
**Observaciones:** 11 (versiones), 3 (Snort), 1 (NFQUEUE).

---

## PROMPT (copiar desde aquí)

Repo y rama confirmados. Respeta `CLAUDE.md` y los guardarraíles de P04 (el guardián debe estar activo: comprueba con `lab/guard/lab-status.sh`; si no está, arráncalo antes). Vas a instalar **solo** lo aprobado en `docs/lab/plan_instalacion.md` (P03). Si necesitas algo que no está en el plan, pregunta primero.

### Método (repetir por cada grupo)
Para cada grupo del plan, en este orden: 1) virtualización, 2) red (OVS, nftables, captura), 3) generadores, 4) análisis Python, 5) Suricata, 6) Snort 3 (AUR, **opcional**: si la compilación es larga o falla, regístralo como decisión/anomalía y continúa), 7) herramientas de medición.
1. Muestra el comando exacto (`sudo pacman -S --needed …` o `paru -S …`) y espera mi confirmación. Para AUR, **lee el PKGBUILD** (`paru -G` / `paru -Pg`) y dime qué descarga y de dónde antes de compilar.
2. Antes de instalar, `pacman -Syu` puede actualizar el kernel: **no hagas actualización completa sin avisarme**; si hace falta, dime que implica reinicio.
3. Instala el grupo y guarda la salida en `docs/lab/logs/P05_<grupo>.txt`.
4. **Verifica** el grupo antes de seguir:
   - virtualización: `systemctl enable --now libvirtd` (o `virtqemud` según el paquete), `virsh -c qemu:///system list --all`, `virt-host-validate qemu`, usuario en grupo `libvirt` (si hace falta cerrar sesión, dímelo), `qemu-system-x86_64 --version`.
   - red: `systemctl enable --now openvswitch` (o `ovs-vswitchd`/`ovsdb-server`), `ovs-vsctl show`, `ovs-vsctl --version`, `nft --version`.
   - Suricata: `suricata --build-info | grep -i -E 'nfqueue|NFQ|version'` → **debe mostrar soporte NFQueue**. Si no lo trae, es bloqueante: busca otro paquete o compilación y repórtalo.
   - Snort 3: `snort -V`, y comprueba que existe el DAQ `nfq` (`snort --daq-list`).
   - Python: `python -I -c "import numpy, scipy, pandas, matplotlib, scapy; print('ok')"`.
   - `hping3 --version`, `iperf3 --version`, `tcpdump --version`, `sensors`.
5. **No habilites servicios que escuchen en la red** del host más allá de libvirt/OVS. No toques `enp2s0`, `wlan0`, `tailscale0`.
6. Registra en `docs/lab/02_software_versiones.md` la versión exacta de cada elemento (columna "instalado") con fecha UTC y origen (repo/AUR + hash del PKGBUILD si aplica).
7. Tras cada grupo, `lab/guard/lab-status.sh` y una nota en el diario. Commit local por grupo verificado.

### Cierre
- Genera `lab/setup/versions_snapshot.sh` que vuelque a `data/raw/versions_<fecha>.txt` todas las versiones relevantes (se reutilizará en cada corrida como metadato).
- Resumen: lista verificada, lo que falló o se pospuso, y entradas añadidas en `04_decisiones.md` y `05_problemas_anomalias.md`. No continúes a P06 si Suricata no tiene NFQUEUE.

## FIN DEL PROMPT
