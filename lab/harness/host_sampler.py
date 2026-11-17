#!/usr/bin/env python3
"""Muestreador del host a 1 Hz durante una corrida (sin sudo; requiere grupo libvirt).

Escribe en formato largo (crudo, sin procesar):  ts_unix_ns, source, entity, key, value
  - source=domstats : `virsh domstats --cpu-total --interface` de las VMs lab-* (contadores acumulados)
  - source=link     : contadores de los puertos espejo del host mir20 / mir30 (/sys/class/net/*/statistics)
  - source=host     : MemAvailable (KiB), Tctl (°C), load1
Uso: host_sampler.py --seconds 80 --out ts_host.csv
"""
import argparse, csv, glob, subprocess, sys, time

def tctl():
    for h in glob.glob("/sys/class/hwmon/hwmon*"):
        try:
            if open(f"{h}/name").read().strip() not in ("k10temp", "coretemp"):
                continue
            for lab in glob.glob(f"{h}/temp*_label"):
                if open(lab).read().strip() in ("Tctl", "Tdie", "Package id 0"):
                    return int(open(lab.replace("_label", "_input")).read()) / 1000
        except OSError:
            pass
    return ""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=float, required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.monotonic()
    with open(a.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ts_unix_ns", "source", "entity", "key", "value"])
        i = 0
        while time.monotonic() - t0 < a.seconds:
            target = t0 + i
            if target > time.monotonic():
                time.sleep(target - time.monotonic())
            ts = time.time_ns()
            out = subprocess.run(["virsh", "-c", "qemu:///system", "domstats", "--cpu-total", "--interface",
                                  "--list-active"], capture_output=True, text=True).stdout
            dom = None
            for line in out.splitlines():
                line = line.strip()
                if line.startswith("Domain:"):
                    dom = line.split("'")[1]
                elif "=" in line and dom and dom.startswith("lab-"):
                    k, v = line.split("=", 1)
                    w.writerow([ts, "domstats", dom, k, v])
            for port in ("mir20", "mir30"):
                for k in ("rx_packets", "rx_bytes", "rx_dropped"):
                    try:
                        v = open(f"/sys/class/net/{port}/statistics/{k}").read().strip()
                        w.writerow([ts, "link", port, k, v])
                    except OSError:
                        pass
            mem = next((l.split()[1] for l in open("/proc/meminfo") if l.startswith("MemAvailable")), "")
            w.writerow([ts, "host", "host", "mem_avail_kib", mem])
            w.writerow([ts, "host", "host", "tctl_c", tctl()])
            w.writerow([ts, "host", "host", "load1", open("/proc/loadavg").read().split()[0]])
            f.flush()
            i += 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
