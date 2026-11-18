# Cómo reproducir el laboratorio desde cero

La plataforma del estudio es `laptop-dev` (`lab/config/profile_laptop-dev.env`); en otra máquina solo cambia el perfil.

## 1. Host (una vez, con sudo)
```bash
sudo bash lab/setup/root_setup.sh lab/config/profile_<plataforma>.env
```
Instala los paquetes, añade al usuario a los grupos libvirt, kvm y wireshark, y detiene Docker. También activa libvirtd y OVS, crea `ovs-ot` (sin puertos físicos) con `mgmt99`, `mir20`, `mir30` y sus espejos, y limita `machine.slice`.
Después de reiniciar el equipo hay que volver a ejecutarlo, porque la IP de `mgmt99` no es persistente.

## 2. Imagen base
Debian 13 genericcloud amd64 en `~/.cache/ips-lab/`, verificada con SHA512 (ver `02_software_versiones.md`).

## 3. Laboratorio (sin sudo)
```bash
export PROFILE=lab/config/profile_<plataforma>.env
lab/guard/guard-start.sh $PROFILE      # guardián: obligatorio antes de crear VMs
lab/setup/lab_up.sh                    # redes, 5 VMs, paquetes por túnel SSH, OpenPLC (commit fijado)
lab/harness/check_chain.sh             # verificaciones: deben dar 0 NO CUMPLE
```

`lab_up.sh` hace, por cada VM:
1. `create_vm.sh`: overlay qcow2, seed cloud-init, `virt-install` con `--video vga`, pinning, `hard_limit` y sin balloon.
2. `provision_vm.sh`: paquetes apt por proxy SOCKS inverso (`ssh -R 1080`), aislamiento de gestión (`mgmt-guard.nft`) y configuración del rol.

Después compila OpenPLC dentro de lab-plc, por un proxy HTTP local (`http_proxy.py`, `ssh -R 3128`).

## 4. Corridas
```bash
lab/harness/run_once.sh --scenario E3 --attack syn --run-profile piloto --rep 1
lab/harness/run_matrix.sh --run-profile final --reps 10 --seed 2027
python3 -I lab/analysis/summarize_runs.py --platform <plataforma> --profile final
```
Cada corrida deja sus datos crudos en `data/raw/runs/<run_id>/` y una fila en `data/raw/runs.csv`. La captura va a `~/.cache/ips-lab/captures/` (fuera de Git) y su sha256 a `data/captures/manifest.csv`. Las capturas de más de 300 MB se borran después de contarlas.

## 5. Parar
```bash
lab/guard/lab-stop.sh          # apaga VMs y guardián
lab/guard/lab-stop.sh --clear  # además borra PAUSE/ABORT
```

## 6. Regenerar resultados, tablas y figuras (sin correr el laboratorio)
Todo sale de `data/raw/` y no necesita VMs. Con Python 3 y SciPy/matplotlib:
```bash
python3 -I lab/analysis/summarize_runs.py --platform laptop-dev --profile final      # métricas por corrida
python3 -I lab/analysis/verificar_figuras.py --platform laptop-dev --profile final   # recálculo independiente (debe decir COHERENTE)
python3 -I lab/analysis/verificar_conservacion_nfq.py --platform laptop-dev --profile final
python3 -I lab/analysis/tablas_paper.py --platform laptop-dev --profile final        # tablas LaTeX y pruebas estadísticas
python3 -I lab/analysis/figuras_paper.py --platform laptop-dev --profile final --layout acm
python3 -I lab/analysis/figuras_arquitectura.py --platform laptop-dev --layout acm
```
Las figuras quedan en `figures/paper_acm/` (dos columnas) y `figures/paper/` (una columna), y las tablas en `tables/paper/`. La versión de este repositorio que cita el artículo es la etiqueta `icits27-final`.

