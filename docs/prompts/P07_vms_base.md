# P07 · Crear las VMs base con límites duros (sin configurar aún el software de cada rol)

**Prioridad: IMPRESCINDIBLE** · Tiempo: 45–60 min
**Observaciones:** 11 (tabla de configuración de VMs: CPU, RAM, disco, SO), 24.

---

## PROMPT (copiar desde aquí)

Repo y rama confirmados; guardián activo (`lab/guard/lab-status.sh`); red de P06 creada. Respeta `CLAUDE.md`. Crea las VMs una por una; **no arranques la siguiente hasta verificar la anterior**, y vigila RAM/temperatura tras cada arranque.

### Presupuesto (ajústalo a P03/P04 y justifica cualquier cambio)
| VM | Rol | vCPU | RAM | Disco | SO | Red |
|---|---|---|---|---|---|---|
| `kali` | Atacante (hping3, scapy) | 2 | 2 GiB | 15 GB | Kali (o Debian + herramientas, documentado) | VLAN 10 + gestión |
| `fw` | Firewall/router | 1 | 1 GiB | 8 GB | pfSense CE (ver P08) o Linux+nftables | VLAN 10, VLAN 20 + gestión |
| `ips` | Suricata / Snort en línea (uno a la vez) | 3 | 2–3 GiB | 20 GB | Ubuntu Server 24.04 | VLAN 20 (eth1), VLAN 30 (eth2) + gestión |
| `plc` | OpenPLC Runtime | 1 | 1 GiB | 8 GB | Ubuntu Server 24.04 | VLAN 30 + gestión |
| `scada` | HMI y cliente Modbus | 1 | 1–1,5 GiB | 10 GB | Ubuntu Server 24.04 | VLAN 20 + gestión |

Suma de RAM ≈ 8–9 GiB < `MemoryHigh` de `machine.slice`. Si la suma no cabe, reduce y justifica; **nunca** superes el presupuesto.

### Pasos por VM
1. Descarga la imagen base desde la URL oficial a `~/lab-images/` (fuera del repo) y **verifica el hash/firma** publicado por el proveedor. Registra URL, fecha y hash en `docs/lab/02_software_versiones.md`.
2. Crea el disco con `qemu-img create -f qcow2 -b <base> -F qcow2` (copia ligera) y un seed `cloud-init` (usuario `lab`, clave SSH pública mía o generada para el laboratorio, hostname, IP estática por interfaz según P06). Guarda las plantillas cloud-init en `lab/setup/cloud-init/` **sin claves privadas ni contraseñas** (usa claves SSH, no commitees secretos).
3. Define la VM con `virt-install --import` o XML en `lab/setup/libvirt/<vm>.xml`, con: `<memory>` = `<currentMemory>`, `<memtune><hard_limit>`, `<cputune><vcpupin>` en los hilos no reservados, **sin memballoon dinámico**, CPU `host-passthrough`, discos `virtio`, NIC `virtio` con `<virtualport type='openvswitch'/>` y VLAN según P06. Los XML se versionan.
4. Arranca la VM con la red de instalación temporal solo si hace falta para actualizar paquetes; después apágala.
5. Verifica antes de la siguiente: la VM arranca, SSH desde el host por la red de gestión funciona, IP y VLAN correctas (`ip -br addr` dentro, `ovs-vsctl list port` fuera), RAM y vCPU realmente aplicadas (`virsh dominfo`, `virsh memtune`, `virsh vcpupin`), `lab-status.sh` sigue en OK, Tctl < 80 °C.
6. Con las 5 VMs encendidas a la vez durante 5 minutos en reposo, registra `MemAvailable`, swap y Tctl: **debe quedar ≥ 6 GiB libres y sin swap creciente**. Si no, reduce RAM y vuelve a probar.
7. Haz un **snapshot/copia** (`qemu-img` o `virsh snapshot-create-as`) de cada VM limpia con nombre `clean-base`, para reconstruir tras fallos.

### Entregables
- `docs/lab/01_hardware.md`: tabla de VMs reales (vCPU, RAM, disco, SO, IP, VLAN, núcleos fijados) lista para pegar en el paper (obs. 11).
- `docs/lab/02_software_versiones.md` (SO y kernel de cada VM), diario, anomalías, decisiones (D8: Kali vs Debian; D9: cloud-init), commit.

### Verificación final
Tabla CUMPLE/NO CUMPLE por VM: arranque, SSH, IP/VLAN, límites aplicados, RAM libre del host ≥ 6 GiB con todo encendido. No sigas a P08 con algún NO CUMPLE.

## FIN DEL PROMPT
