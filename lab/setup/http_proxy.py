#!/usr/bin/env python3
"""Proxy HTTP mínimo (CONNECT para HTTPS y GET/POST para HTTP) que escucha SOLO en 127.0.0.1.
Se usa durante el aprovisionamiento: la VM lo alcanza por `ssh -R 3128:127.0.0.1:3128`, sin NAT y
sin tocar el firewall del host. Registra cada destino en stderr para dejar constancia de qué se descargó.
Uso: http_proxy.py [puerto]   (se detiene con Ctrl+C o kill)
"""
import socket, sys, threading, select
from urllib.parse import urlsplit

def pipe(a, b):
    socks = [a, b]
    try:
        while True:
            r, _, _ = select.select(socks, [], [], 120)
            if not r:
                return
            for s in r:
                d = s.recv(65536)
                if not d:
                    return
                (b if s is a else a).sendall(d)
    except OSError:
        pass
    finally:
        a.close(); b.close()

def handle(c):
    try:
        head = b""
        while b"\r\n\r\n" not in head:
            d = c.recv(65536)
            if not d:
                return c.close()
            head += d
        line = head.split(b"\r\n", 1)[0].decode()
        method, target, ver = line.split(" ", 2)
        if method == "CONNECT":
            host, port = target.rsplit(":", 1)
            up = socket.create_connection((host, int(port)), timeout=30)
            c.sendall(b"HTTP/1.1 200 Connection established\r\n\r\n")
            rest = head.split(b"\r\n\r\n", 1)[1]
            if rest:
                up.sendall(rest)
        else:
            u = urlsplit(target)
            up = socket.create_connection((u.hostname, u.port or 80), timeout=30)
            path = (u.path or "/") + (("?" + u.query) if u.query else "")
            up.sendall(head.replace(target.encode(), path.encode(), 1))
            host = u.hostname
        print(f"proxy: {method} {target}", file=sys.stderr, flush=True)
        up.settimeout(None); c.settimeout(None)
        pipe(c, up)
    except Exception as e:
        print(f"proxy: error {type(e).__name__}: {e}", file=sys.stderr, flush=True)
        c.close()

def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 3128
    s = socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("127.0.0.1", port)); s.listen(64)
    print(f"proxy escuchando en 127.0.0.1:{port}", file=sys.stderr, flush=True)
    while True:
        c, _ = s.accept()
        threading.Thread(target=handle, args=(c,), daemon=True).start()

if __name__ == "__main__":
    main()
