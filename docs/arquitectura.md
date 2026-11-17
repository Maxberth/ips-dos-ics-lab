# Arquitectura del laboratorio

Un solo equipo físico (CachyOS, Ryzen 5 5600X, 24 GB RAM). Todo es virtual y 100 % software libre. El switch Open vSwitch `ovs-ot` no tiene puertos físicos.

```mermaid
flowchart LR
  subgraph HOST["Host CachyOS: KVM/libvirt + Open vSwitch (ovs-ot, sin NIC físicas)"]
    direction LR
    subgraph V10["VLAN 10 · IT · 192.168.10.0/24"]
      K["Kali<br/>hping3 / scapy<br/>.100"]
    end
    subgraph V20["VLAN 20 · DMZ/SCADA · 192.168.20.0/24"]
      FW["Firewall<br/>pfSense CE o nftables<br/>.10.1 / .20.1"]
      SC["SCADA/HMI<br/>pymodbus 10 Hz<br/>.20"]
    end
    IPS["IPS en línea (enrutado)<br/>Suricata/Snort · NFQUEUE<br/>.20.2 / .30.1"]
    subgraph V30["VLAN 30 · Planta · 192.168.30.0/24"]
      PLC["OpenPLC + proceso simulado<br/>Modbus/TCP 502<br/>.10"]
    end
    MON["Medición fuera de banda en el host<br/>mirror OVS + tcpdump + contadores"]
  end
  K --> FW --> IPS --> PLC
  SC --> IPS
  IPS -.-> MON
  FW -.-> MON
  PLC -.-> MON
```

## Escenarios
| Id | Condición |
|---|---|
| E0 | Base, sin ataque |
| E1 | Solo firewall/VLAN (IPS solo enrutando) |
| E2 | Suricata en línea, `alert` |
| E3 | Suricata en línea, `drop` |
| E4 | Snort 3 en línea, `drop` (opcional) |

Ataques: SYN flood a 502, UDP flood, ICMP flood, Modbus flood. 10 repeticiones por combinación; media, DE e IC 95 %.

## Medición
Fuera de banda en el host (mirror/taps de OVS, tcpdump) como segunda fuente frente a los contadores de Suricata, del firewall y de los puertos OVS. Guardián de RAM/swap/temperatura (ver `docs/prompts/P04_guardarrailes_ram_temp.md`).
