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

## 2b. Lo que ya se sabe por laptop-dev (no hay que redescubrirlo)

- **ufw u otro firewall del host:** no hace falta tocarlo. Las VMs instalan paquetes por túnel SSH (D12), sin red NAT.
- **Grupos nuevos sin cerrar sesión:** libvirt va por polkit y la captura por `newgrp` (D13).
- **Las VMs necesitan `--video vga`** o el kernel de Debian 13 se reinicia en bucle (A4). Ya está en `create_vm.sh`.
- **Nunca procesar capturas grandes fuera de un scope:** el arnés ya lo hace (A10). No ejecutes tshark a mano sobre capturas de floods.
- **OpenPLC puede morir con el Modbus flood** sin que systemd lo note (A15). El arnés comprueba el PLC antes y después de cada corrida y lo reinicia si hace falta.
- **El techo del IPS:** con un atacante de una sola IP, Suricata usa una sola cola NFQUEUE. En laptop-dev procesa ~58–95 kpps frente a ~150 kpps de ataque. El resto lo descarta el kernel sin distinguir el tráfico legítimo (A11, A14). En pc-miguel hay que medir su propio techo y reportar `nfq_queue_dropped` aparte de `ips.blocked`.
- **Suricata con `exception-policy: ignore`** (D19). Con `auto`, el parser Modbus bloquea el flood en E2 sin reglas (A16).
- **Guardián en pc-miguel:** escritorio sin batería (`GUARD_REQUIRE_AC=0`). Si usa zram con `swappiness` alta como laptop-dev, subir `GUARD_ABORT_SWAP_GROWTH_MIB` (D15).

## 2c. Tiempos medidos en laptop-dev

- Montaje con `lab_up.sh` (5 VMs + paquetes + OpenPLC): unos 15 min de máquina, sin contar la depuración.
- Corrida `piloto` (5 + 30 + 10 s): **64–93 s reales, mediana 76 s** (n = 20). Incluye el cambio de modo del IPS, el enfriamiento hasta Tctl ≤ 65 °C, el conteo de la captura y la validación.
- Estimación para el perfil `final` (15 + 60 + 15 s): unos 120–140 s por corrida, a confirmar en el piloto de pc-miguel.
  - Matriz completa ×10 (E0 + 3 escenarios × 4 ataques = 130 corridas): unas 4,5–5 h.
  - Recorte recomendado si no alcanza: E0, E1 y E3 × {syn, modbus} × 10 = 50 corridas, unas 2 h; después udp e icmp; E2 al final.

## 3. Laboratorio (sin sudo)

```bash
cd ~/code/articulo/ips-dos-ics-lab && export PROFILE=lab/config/profile_pc-miguel.env
lab/guard/guard-start.sh $PROFILE
lab/setup/lab_up.sh            # redes libvirt, 5 VMs, paquetes por túnel SSH, OpenPLC (commit fijado)
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
# recorte prioritario primero (unas 2 h), luego el resto con --resume
lab/harness/run_matrix.sh --run-profile final --reps 10 --seed 2027 --scenarios "E0 E1 E3" --attacks "syn modbus"
lab/harness/run_matrix.sh --run-profile final --reps 10 --seed 2027 --resume
python3 -I lab/analysis/summarize_runs.py --platform pc-miguel --profile final
```

Cada corrida queda en `data/raw/runs/<run_id>/` con `platform=pc-miguel` en `data/raw/runs.csv`. Hacer commit y push de `data/raw/` al terminar cada bloque.

## 6. Qué debe repetirse en pc-miguel (no se hereda de laptop-dev)

- Inventario P02, temperatura en reposo y bajo carga.
- Versiones exactas instaladas en el host y en las VMs (`lab/setup/versions_snapshot.sh`).
- Commit de OpenPLC: usar el mismo de laptop-dev (`OPENPLC_COMMIT=<hash>` al instalar). El hash está en `docs/lab/02_software_versiones.md`.
- Piloto completo y auditoría (P12) antes de las corridas finales.
- Tiempos por corrida (los de laptop-dev son solo una referencia).
