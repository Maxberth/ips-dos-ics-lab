#!/usr/bin/env python3
"""Genera /etc/suricata/suricata-lab.yaml a partir del suricata.yaml de la distribución.
Corre dentro de lab-ips (python3-yaml viene con cloud-init). Solo cambia lo que se lista aquí;
todo lo demás queda como en el paquete. La copia resultante se versiona en lab/config/ips/.

Cambios (documentados en docs/lab/04_decisiones.md, D11-D12):
  - HOME_NET = 192.168.20.0/24 y 192.168.30.0/24
  - Modo NFQUEUE: mode accept, fail-open no (fail-closed)
  - Parser Modbus activado (puerto 502)
  - exception-policy: ignore y stream.drop-invalid: no (D19)
  - Salidas: solo eve.json con alert, drop y stats cada 1 s, y stats.log; sin fast.log ni otros eventos
"""
import sys, yaml

src, dst = sys.argv[1], sys.argv[2]
MEASURE = "--measure" in sys.argv[3:]   # corridas: eve solo con stats (ver D17)
text = open(src).read()
body = text.split("---", 1)[1] if text.lstrip().startswith("%YAML") else text
c = yaml.safe_load(body)

c["vars"]["address-groups"]["HOME_NET"] = "[192.168.20.0/24,192.168.30.0/24]"
c["vars"]["address-groups"]["EXTERNAL_NET"] = "!$HOME_NET"
c["nfq"] = {"mode": "accept", "fail-open": False}
# D19: solo las reglas deciden. Con "auto" (por defecto), en modo IPS un error del parser (p. ej. el límite
# request-flood de Modbus) descarta el flujo incluso en E2 (alert), lo que mezcla la atribución (A16).
c["exception-policy"] = "ignore"
# D19 (ampliación): en modo IPS el motor TCP descarta paquetes "inválidos" (stream.drop-invalid=yes por
# defecto) sin ninguna regla; en E2 (alert) eso bloqueó 2,7 M SYN (A17). Solo deciden las reglas.
c.setdefault("stream", {})["drop-invalid"] = False
c.setdefault("app-layer", {}).setdefault("protocols", {})["modbus"] = {
    "enabled": "yes", "detection-ports": {"dp": 502}, "stream-depth": 0}
c["stats"] = {"enabled": True, "interval": 1}
outs = []
for o in c.get("outputs", []):
    name = list(o.keys())[0]
    if name == "eve-log":
        o[name].update({"enabled": True, "filetype": "regular", "filename": "eve.json",
                        "types": ([] if MEASURE else [{"alert": {"tagged-packets": False}}, {"drop": {"alerts": True, "flows": "all"}}])
                                 + [{"stats": {"totals": True, "threads": False, "deltas": False}}]})
        outs.append(o)
    elif name == "stats":
        o[name].update({"enabled": True, "filename": "stats.log", "append": True, "totals": True, "threads": False})
        outs.append(o)
    # el resto de salidas (fast.log, http, pcap...) se omiten para no añadir carga
c["outputs"] = outs
c["default-rule-path"] = "/etc/suricata/rules"
c["rule-files"] = ["lab.rules"]

with open(dst, "w") as f:
    f.write("%YAML 1.1\n---\n# Generado por lab/setup/make_suricata_yaml.py a partir de " + src + "\n")
    yaml.safe_dump(c, f, default_flow_style=False, sort_keys=False)
print("escrito", dst)
