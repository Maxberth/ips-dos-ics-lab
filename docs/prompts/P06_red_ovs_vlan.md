# P06 · Red virtual: Open vSwitch, VLAN 10/20/30 y aislamiento

**Prioridad: IMPRESCINDIBLE** · Tiempo: 30–45 min
**Observaciones:** 4 (switch virtual declarado; contadores por puerto), 10 (segmentación), 11, 26.

---

## PROMPT (copiar desde aquí)

Repo y rama confirmados; guardián activo; respeta `CLAUDE.md`. Vas a crear la red virtual del laboratorio. **Todo el laboratorio es virtual: el switch OVS no tiene ningún puerto físico** (ni `enp2s0`, ni `wlan0`, ni `tailscale0`). Salida a Internet solo mediante una red NAT libvirt temporal de instalación, que se desactiva para las mediciones.

### Topología objetivo (estilo Purdue)
```
VLAN 10 (IT / atacante)      192.168.10.0/24   Kali .100         pfSense/FW .1
VLAN 20 (DMZ / SCADA)        192.168.20.0/24   FW .1  IPS(eth1) .2   SCADA/HMI .20
VLAN 30 (Planta / PLC)       192.168.30.0/24   IPS(eth2) .1   OpenPLC .10
VLAN 99 (gestión, opcional)  192.168.99.0/24   acceso del host a cada VM por SSH
```
Flujo: Kali → firewall → (VLAN 20) → **IPS en línea, enrutado, 192.168.20.2 ↔ 192.168.30.1** → OpenPLC. SCADA vive en VLAN 20, de modo que su tráfico legítimo también cruza el IPS (decisión D6; el paper actual lo ubica a veces en VLAN 30 y usa 192.168.1.10 para el PLC: anótalo en `05_problemas_anomalias.md` para corregir el texto).

### Tareas
1. Crea el bridge `ovs-ot` con `ovs-vsctl` (sin puertos físicos). Define cómo se conectará cada VM (puertos *access* con `tag=10/20/30` y, para firewall e IPS, puertos de VM con interfaces separadas por VLAN, preferible a trunk dentro de la VM por simplicidad y medición). Escribe todo en un script idempotente `lab/setup/net_up.sh` y otro `net_down.sh`, y un XML/definición libvirt de la red `ovs-ot` (`<virtualport type='openvswitch'/>`, `<portgroup>` con VLAN) en `lab/setup/libvirt/`.
2. Puerto espejo: crea un **mirror** OVS (`ovs-vsctl -- set Bridge ovs-ot mirrors=…`) o taps de captura dedicados para observar, fuera de banda, el tráfico de VLAN 20 (antes del IPS) y de VLAN 30 (después del IPS). La captura debe correr en el host, no dentro de las VMs. Explica en `04_decisiones.md` por qué (no contaminar la medición) y qué limitación tiene (el mirror no es 100 % fiel bajo carga).
3. Red de instalación temporal: `net_install_nat.sh` que levanta/baja un NAT libvirt aislado solo para descargar paquetes dentro de las VMs. Comprueba que, con ella apagada, ninguna VM tiene ruta a Internet ni al host.
4. Contadores: documenta y prueba `ovs-ofctl dump-ports ovs-ot` y `ovs-vsctl list interface` para leer paquetes/bytes/drops por puerto (los usaremos en P18).
5. Guarda la configuración en `lab/config/` y las salidas en `docs/lab/logs/P06_*.txt`.

### Verificación (todo con evidencia)
- `ovs-vsctl show`: bridge `ovs-ot` sin interfaces físicas (`ovs-vsctl list-ports ovs-ot` no contiene `enp2s0`, `wlan0` ni `tailscale0`). 
- `ip -br addr` del host: ninguna dirección 192.168.10/20/30 asignada al host salvo que lo decidas y documentes; no hay `ip_forward` del host hacia el laboratorio (`sysctl net.ipv4.ip_forward` documentado; no lo cambies si estaba en 0).
- Prueba con dos `ip netns` temporales (o dos VMs mínimas del P07) en puertos con distinta VLAN: **no se ven entre sí** (aislamiento 802.1Q), y se ven los de la misma VLAN. Registra el resultado.
- `net_down.sh` desmonta todo y `net_up.sh` lo recrea sin errores (idempotencia).
- Entradas en `04_decisiones.md` (D6 ubicación de SCADA, D7 mirror vs tap), `02_software_versiones.md` (OVS y libvirt), `03_limitaciones.md` (switch virtual: mide segmentación y aislamiento, no hardware industrial), diario, commit. No sigas a P07 si la prueba de aislamiento falla.

## FIN DEL PROMPT
