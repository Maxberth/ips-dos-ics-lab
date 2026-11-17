# P08 · Firewall entre VLAN 10 y VLAN 20 (pfSense CE o nftables)

**Prioridad: IMPRESCINDIBLE** · Tiempo: 30–60 min
**Observaciones:** 10 (separar el efecto de firewall/VLAN del de Suricata), 4, 11.

---

## PROMPT (copiar desde aquí)

Repo y rama confirmados; guardián activo; VMs de P07 creadas. Respeta `CLAUDE.md`. Configura la VM `fw` como router/firewall entre VLAN 10 (Kali) y VLAN 20 (DMZ), con una ruta estática hacia VLAN 30 vía el IPS (192.168.20.2).

### Decisión previa (pregúntame antes de seguir)
El paper usa **pfSense 2.8.0**. La ISO de pfSense CE exige descarga manual desde netgate.com y su instalador es interactivo (consola). Presenta las dos opciones con su coste y recomienda una:
- **A) pfSense CE** (fiel al paper): yo descargo la ISO a `~/lab-images/`, tú verificas el hash, la instalas con `virsh console`/`virt-viewer` guiándome en lo que no se pueda automatizar, y aplicas la configuración con un `config.xml` versionado (sin contraseñas) o pasos documentados.
- **B) Linux + nftables** (VM Ubuntu o Debian mínima, 100 % libre, totalmente scriptable y reproducible). Documentar como desviación del paper en `03_limitaciones.md` y en `04_decisiones.md`.
Espera mi respuesta y registra la decisión.

### Configuración (ambas opciones)
1. Interfaces: VLAN 10 `192.168.10.1/24`, VLAN 20 `192.168.20.1/24`, gestión. Ruta estática `192.168.30.0/24 via 192.168.20.2`. Reenvío IPv4 activo.
2. Política **E1 "solo firewall/VLAN"** (la usada como "sin IPS"): permite de VLAN 10 solo hacia VLAN 20/30 el tráfico necesario para el experimento (TCP 502 hacia el PLC, ICMP, UDP hacia el PLC y hacia SCADA), registra con contadores por regla, y **no** limita tasa. Bloquea VLAN 10 → gestión y todo lo demás. Documenta exactamente cada regla (copia en `lab/config/fw/`).
3. Habilita **contadores por regla** y guarda un comando para leerlos (`nft list ruleset -a` o pfctl `-vvsr`), que se usarán como tercera fuente en las pruebas.
4. Sin NAT hacia Internet durante las mediciones.

### Verificación
- Desde `kali`: `ping 192.168.20.1` responde; hacia el PLC `192.168.30.10` aún no (el IPS y el PLC se configuran en P09 y P10: registra "pendiente").
- La regla de bloqueo de ejemplo funciona (p. ej. VLAN 10 → gestión): intento fallido con el contador de la regla incrementado.
- `fw` queda en `clean-base-fw` (snapshot) con su configuración exportada a `lab/config/fw/`.
- Anota en `02_software_versiones.md` la versión del firewall; en `04_decisiones.md` A/B; en `05_problemas_anomalias.md` cualquier fricción. Diario y commit.

## FIN DEL PROMPT
