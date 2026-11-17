# Pasar el laboratorio a pc-miguel

Todo lo calibrado en laptop-dev se reproduce en pc-miguel con los **mismos scripts, reglas y arnés**. Solo cambia el perfil `lab/config/profile_pc-miguel.env`. Los datos de laptop-dev no se copian a las tablas del paper.

Tiempo estimado de montaje: unos 45–60 min. La parte larga es la compilación de OpenPLC, de unos 15–20 min.

## 0. Antes de empezar

1. Clonar el repo (privado) y cambiar a la rama del laboratorio:
   ```bash
   git clone https://github.com/Maxberth/ips-dos-ics-lab.git ~/code/articulo/ips-dos-ics-lab
   cd ~/code/articulo/ips-dos-ics-lab && git switch lab/ips-icits27
   ```
2. Inventario de la máquina (solo lectura, ~45 s). Luego se revisan los logs:
   ```bash
   cd ~/code/articulo/ips-dos-ics-lab && lab/setup/inventario_plataforma.sh pc-miguel
   ```
3. Completar `lab/config/profile_pc-miguel.env`:
   - `LAB_USER` = usuario de pc-miguel.
   - Confirmar la topología con `lscpu -e`: núcleo N = hilos 2N y 2N+1. Si no, ajustar `*_PIN`, `HOST_CPUS`, `VM_ALLOWED_CPUS` y `EMULATOR_CPUS`.
   - Confirmar que la RAM libre con Docker detenido deja ≥ 6 GiB al host con 8 GiB de VMs.
4. Comprobar que ninguna red de Docker usa 192.168.10/20/30/99.0/24 ni 192.168.250.0/24 (`docker network inspect`).

## 1. Paso con sudo (una vez)

```bash
cd ~/code/articulo/ips-dos-ics-lab && sudo bash lab/setup/root_setup.sh lab/config/profile_pc-miguel.env 2>&1 | tee docs/lab/logs/P05_root_setup_pc-miguel.txt
```

Instala los mismos paquetes del host, detiene Docker, crea `ovs-ot` y sus espejos, y aplica los límites de `machine.slice`. Después de reiniciar el equipo hay que volver a ejecutarlo, porque la IP de `mgmt99` no es persistente.

## 2. Imagen base (la misma que en laptop-dev)

```bash
mkdir -p ~/.cache/ips-lab && cd ~/.cache/ips-lab && curl -fLO https://cloud.debian.org/images/cloud/trixie/latest/SHA512SUMS && curl -fLO https://cloud.debian.org/images/cloud/trixie/latest/debian-13-genericcloud-amd64.qcow2 && grep ' debian-13-genericcloud-amd64.qcow2$' SHA512SUMS | sha512sum -c -
```

`latest` cambia con el tiempo. Para tener exactamente la misma imagen que laptop-dev, comparar el SHA512 con el de `docs/lab/02_software_versiones.md`. Si no coincide, usar la carpeta con fecha de cloud.debian.org que corresponda, o copiar el archivo desde laptop-dev.

## 3. Laboratorio (sin sudo)

```bash
cd ~/code/articulo/ips-dos-ics-lab && export PROFILE=lab/config/profile_pc-miguel.env
lab/guard/guard-start.sh $PROFILE
lab/setup/lab_up.sh            # redes libvirt, 5 VMs, aprovisionamiento, OpenPLC, quita la NIC NAT
lab/guard/lab-status.sh
```

Los pasos de `lab_up.sh` están detallados en `docs/lab/reproducir.md`.

## 4. Verificaciones antes de medir (puerta de calidad de P12)

```bash
lab/harness/check_chain.sh     # rutas, aislamiento VLAN, SCADA->PLC, prueba de drop real
```

Todas deben dar CUMPLE. Luego el piloto (una corrida por escenario y ataque):

```bash
lab/harness/run_matrix.sh --run-profile piloto --reps 1
```

## 5. Corridas finales

```bash
lab/harness/run_matrix.sh --run-profile final --reps 10 --seed 2027
```

Cada corrida queda en `data/raw/runs/<run_id>/` con `platform=pc-miguel` en `data/raw/runs.csv`. Hacer commit y push de `data/raw/` al terminar cada bloque.

## 6. Qué debe repetirse en pc-miguel (no se hereda de laptop-dev)

- Inventario P02, temperatura en reposo y bajo carga.
- Versiones exactas instaladas en el host y en las VMs (`lab/setup/versions_snapshot.sh`).
- Commit de OpenPLC: usar el mismo de laptop-dev (`OPENPLC_COMMIT=<hash>` al instalar). El hash está en `docs/lab/02_software_versiones.md`.
- Piloto completo y auditoría (P12) antes de las corridas finales.
- Tiempos por corrida (los de laptop-dev son solo una referencia).
