#!/usr/bin/env bash
# Instala OpenPLC Runtime v3 dentro de lab-plc y carga tank_sim.st en modo RUN. Corre en la VM.
# Fija el commit: OPENPLC_COMMIT (si está vacío usa el último de master y lo registra).
set -euo pipefail
OPENPLC_COMMIT="${OPENPLC_COMMIT:-}"
# Salida a Internet solo por el proxy del host (ssh -R 3128), si se pasó LAB_PROXY.
if [ -n "${LAB_PROXY:-}" ]; then
  export http_proxy=$LAB_PROXY https_proxy=$LAB_PROXY HTTP_PROXY=$LAB_PROXY HTTPS_PROXY=$LAB_PROXY
  echo "Acquire::http::Proxy \"$LAB_PROXY\"; Acquire::https::Proxy \"$LAB_PROXY\";" | sudo tee /etc/apt/apt.conf.d/90lab-proxy >/dev/null
  trap 'sudo rm -f /etc/apt/apt.conf.d/90lab-proxy' EXIT
fi
cd /opt/lab
[ -d OpenPLC_v3 ] || git clone --quiet https://github.com/thiagoralves/OpenPLC_v3.git
cd OpenPLC_v3
[ -n "$OPENPLC_COMMIT" ] && git checkout --quiet "$OPENPLC_COMMIT"
echo "openplc_commit=$(git rev-parse HEAD) fecha=$(git log -1 --format=%cI)" | tee /opt/lab/openplc_commit.txt
[ -f /opt/lab/.openplc_built ] || { ./install.sh linux > /opt/lab/openplc_install.log 2>&1; touch /opt/lab/.openplc_built; }

# Programa del laboratorio
cp /tmp/tank_sim.st webserver/st_files/tank_sim.st
cd webserver
./scripts/compile_program.sh tank_sim.st > /opt/lab/openplc_compile.log 2>&1
echo tank_sim.st > active_program
# Arranque en modo RUN con Modbus en 502 (tabla Settings de la base de datos del webserver)
python3 - <<'EOF'
import sqlite3
db = sqlite3.connect("openplc.db"); c = db.cursor()
for k, v in (("Modbus_port", "502"), ("Start_run_mode", "true"), ("Dnp3_port", "disabled"),
             ("Enip_port", "disabled"), ("Pstorage_polling", "disabled")):
    c.execute("UPDATE Settings SET Value=? WHERE Key=?", (v, k))
c.execute("DELETE FROM Programs WHERE file='tank_sim.st'")
c.execute("INSERT INTO Programs (Name, Description, File, Date_upload) VALUES ('tank_sim','IPS lab','tank_sim.st',strftime('%s','now'))")
db.commit(); print(list(c.execute("SELECT Key, Value FROM Settings")))
EOF
sudo systemctl restart openplc
for i in $(seq 60); do ss -ltn | grep -q ':502 ' && break; sleep 1; done
ss -ltnp | grep -E ':502|:8080' || { echo "OpenPLC no escucha en 502"; exit 1; }
echo "OpenPLC en RUN con tank_sim.st"
