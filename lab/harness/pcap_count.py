#!/usr/bin/env python3
"""Conteo por segundo de una captura pcapng, en streaming y con memoria constante.

Sustituye a `tshark -z io,stat`, que guarda estado por paquete y agotó la RAM del host con 16 M de
paquetes (anomalía A10). Lee los bloques pcapng uno a uno (IDB para los nombres de interfaz,
EPB para los paquetes) y decodifica a mano Ethernet + 802.1Q + IPv4 + TCP/UDP/ICMP.
Se ejecuta dentro de un scope con MemoryMax (run_once.sh), nunca suelto.

Uso: pcap_count.py <captura.pcapng> --t0 <unix_s> --out pcap_counts.csv
CSV: iface,second,attack_to_plc,attack_syn,attack_udp,attack_icmp,attack_tcp_other,
     scada_req_payload,plc_resp_payload,other,total
  second            : segundos desde t0 (inicio de la corrida)
  attack_*          : IPv4 192.168.10.100 -> 192.168.30.10
  scada_req_payload : TCP 192.168.20.20 -> 192.168.30.10:502 con datos (solicitudes Modbus)
  plc_resp_payload  : TCP 192.168.30.10:502 -> 192.168.20.20 con datos (respuestas Modbus)
"""
import argparse, csv, struct, sys
from collections import defaultdict

ATT, PLC, SCADA = bytes([192, 168, 10, 100]), bytes([192, 168, 30, 10]), bytes([192, 168, 20, 20])
COLS = ["attack_to_plc", "attack_syn", "attack_udp", "attack_icmp", "attack_tcp_other",
        "scada_req_payload", "plc_resp_payload", "other", "total"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pcap"); ap.add_argument("--t0", type=float, required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    counts = defaultdict(lambda: [0] * len(COLS))  # (iface, second) -> contadores (≈ 2 x duración filas)
    ifaces, tsres, endian = [], [], "<"
    with open(a.pcap, "rb", buffering=1 << 20) as f:
        while True:
            hdr = f.read(8)
            if len(hdr) < 8:
                break
            btype, blen = struct.unpack(endian + "II", hdr)
            if btype == 0x0A0D0D0A:  # Section Header Block: fija el orden de bytes
                magic = f.read(4)
                endian = "<" if magic == b"\x4d\x3c\x2b\x1a" else ">"
                blen = struct.unpack(endian + "I", hdr[4:8])[0]
                f.read(blen - 12); ifaces, tsres = [], []
                continue
            body = f.read(blen - 8)
            if btype == 1:  # Interface Description Block
                name, res, off = f"if{len(ifaces)}", 1e-6, 8
                while off + 4 <= len(body) - 4:
                    code, ln = struct.unpack(endian + "HH", body[off:off + 4])
                    if code == 0: break
                    val = body[off + 4: off + 4 + ln]
                    if code == 2: name = val.decode(errors="replace")
                    if code == 9: res = 10 ** -(val[0] & 0x7F) if not val[0] & 0x80 else 2 ** -(val[0] & 0x7F)
                    off += 4 + ((ln + 3) & ~3)
                ifaces.append(name); tsres.append(res)
            elif btype == 6:  # Enhanced Packet Block
                iid, th, tl, caplen = struct.unpack(endian + "IIII", body[:16])
                ts = ((th << 32) | tl) * tsres[iid]
                pkt = body[20:20 + caplen]
                c = counts[(ifaces[iid], int(ts - a.t0))]
                c[8] += 1
                et, off = struct.unpack("!H", pkt[12:14])[0] if len(pkt) >= 14 else 0, 14
                while et in (0x8100, 0x88A8) and len(pkt) >= off + 4:
                    et = struct.unpack("!H", pkt[off + 2:off + 4])[0]; off += 4
                if et != 0x0800 or len(pkt) < off + 20:
                    c[7] += 1; continue
                ihl = (pkt[off] & 0x0F) * 4; proto = pkt[off + 9]
                tot = struct.unpack("!H", pkt[off + 2:off + 4])[0]
                src, dst = pkt[off + 12:off + 16], pkt[off + 16:off + 20]
                l4 = off + ihl
                if src == ATT and dst == PLC:
                    c[0] += 1
                    if proto == 6 and len(pkt) >= l4 + 14:
                        flags = pkt[l4 + 13]
                        c[1 if (flags & 0x02 and not flags & 0x10) else 4] += 1
                    elif proto == 17: c[2] += 1
                    elif proto == 1: c[3] += 1
                    else: c[4] += 1
                elif proto == 6 and len(pkt) >= l4 + 14 and {src, dst} == {SCADA, PLC}:
                    sport, dport = struct.unpack("!HH", pkt[l4:l4 + 4])
                    payload = tot - ihl - (pkt[l4 + 12] >> 4) * 4
                    if src == SCADA and dport == 502 and payload > 0: c[5] += 1
                    elif src == PLC and sport == 502 and payload > 0: c[6] += 1
                    else: c[7] += 1
                else:
                    c[7] += 1
    with open(a.out, "w", newline="") as o:
        w = csv.writer(o); w.writerow(["iface", "second"] + COLS)
        for (ifc, s) in sorted(counts):
            w.writerow([ifc, s] + counts[(ifc, s)])
    print(f"interfaces={ifaces} filas={len(counts)}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
