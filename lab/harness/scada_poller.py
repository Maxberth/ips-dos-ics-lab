#!/usr/bin/env python3
"""Cliente SCADA legítimo: lee registros Modbus/TCP del PLC a tasa fija y registra CADA solicitud.

Corre dentro de la VM lab-scada. Solo biblioteca estándar (sin depender de la versión de pymodbus).
RTT = tiempo entre el envío de la solicitud y la recepción completa de la respuesta, medido con el
mismo reloj monotónico de la VM SCADA (no necesita sincronizar relojes entre VMs). Es RTT, no una vía.

CSV de salida (una fila por solicitud):
  seq, ts_send_unix_ns, ts_send_mono_ns, ts_recv_mono_ns, ok, rtt_ms, error, tx_id, reconnects
  - ok=1 solo si llegó una respuesta Modbus válida con el mismo transaction id y sin excepción.
  - Si no hay respuesta en --timeout, ok=0 y error=timeout (no se inventa ningún RTT).

Uso: scada_poller.py --plc 192.168.30.10 --hz 10 --seconds 75 --out polls.csv
"""
import argparse, csv, os, socket, struct, sys, time

def connect(host, port, timeout):
    s = socket.create_connection((host, port), timeout=timeout)
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    s.settimeout(timeout)
    return s

def recv_exact(s, n, deadline):
    buf = b""
    while len(buf) < n:
        left = deadline - time.monotonic()
        if left <= 0:
            raise socket.timeout()
        s.settimeout(left)
        chunk = s.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("conexión cerrada por el PLC")
        buf += chunk
    return buf

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plc", default="192.168.30.10")
    ap.add_argument("--port", type=int, default=502)
    ap.add_argument("--unit", type=int, default=1)
    ap.add_argument("--register", type=int, default=0, help="primer holding register")
    ap.add_argument("--count", type=int, default=4, help="número de registros por lectura")
    ap.add_argument("--hz", type=float, default=10.0)
    ap.add_argument("--seconds", type=float, required=True)
    ap.add_argument("--timeout", type=float, default=0.5)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    period = 1.0 / a.hz
    n_total = int(round(a.seconds * a.hz))
    sock, reconnects, tx = None, 0, 0
    with open(a.out, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["seq", "ts_send_unix_ns", "ts_send_mono_ns", "ts_recv_mono_ns", "ok",
                    "rtt_ms", "error", "tx_id", "reconnects"])
        t0 = time.monotonic()
        for seq in range(n_total):
            # Planificación absoluta: un retraso no desplaza las solicitudes siguientes.
            target = t0 + seq * period
            now = time.monotonic()
            if target > now:
                time.sleep(target - now)
            tx = (tx + 1) & 0xFFFF
            pdu = struct.pack(">BHH", 3, a.register, a.count)
            adu = struct.pack(">HHHB", tx, 0, len(pdu) + 1, a.unit) + pdu
            send_unix, send_mono, recv_mono, ok, err = time.time_ns(), time.monotonic_ns(), "", 0, ""
            deadline = time.monotonic() + a.timeout
            try:
                if sock is None:
                    sock = connect(a.plc, a.port, a.timeout)
                    reconnects += 1 if seq > 0 else 0
                    send_unix, send_mono = time.time_ns(), time.monotonic_ns()
                    deadline = time.monotonic() + a.timeout
                sock.sendall(adu)
                while True:
                    hdr = recv_exact(sock, 7, deadline)
                    rtx, _proto, length, _unit = struct.unpack(">HHHB", hdr)
                    body = recv_exact(sock, length - 1, deadline)
                    if rtx == tx:
                        break  # respuestas tardías de solicitudes anteriores se descartan
                recv_mono = time.monotonic_ns()
                fc = body[0]
                if fc & 0x80:
                    err = f"modbus_exception_{body[1]}"
                elif fc == 3 and body[1] == 2 * a.count:
                    ok = 1
                else:
                    err = "respuesta_inesperada"
            except socket.timeout:
                err = "timeout"
            except (ConnectionError, OSError) as e:
                err = type(e).__name__
            if not ok and not err.startswith(("modbus_exception", "respuesta_inesperada")):
                # Tras un timeout o error de socket la conexión queda en estado incierto: se reabre.
                try:
                    if sock: sock.close()
                except OSError:
                    pass
                sock = None
            rtt = f"{(recv_mono - send_mono) / 1e6:.3f}" if recv_mono else ""
            w.writerow([seq, send_unix, send_mono, recv_mono, ok, rtt, err, tx, reconnects])
            if seq % 50 == 0:
                f.flush()
    return 0

if __name__ == "__main__":
    sys.exit(main())
