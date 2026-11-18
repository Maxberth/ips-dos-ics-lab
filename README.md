# ips-dos-ics-lab

Laboratorio virtual reproducible, datos crudos, scripts de análisis y documentación del artículo **ICITS'27** (submission 418): *Implementation of an Intrusion Prevention System for Mitigating DoS Attacks in Industrial Control Networks Based on PLC and Industrial Switch Protection*.

Repositorio público. El texto del artículo (LaTeX) está en [`Maxberth/ips-dos-ics-paper`](https://github.com/Maxberth/ips-dos-ics-paper). La versión de este repositorio que cita el artículo es la etiqueta **`icits27-final`**.

## Qué contiene

- Un laboratorio virtual con 5 máquinas (atacante, firewall, IPS con Suricata, PLC con OpenPLC y cliente SCADA) sobre QEMU/KVM, Open vSwitch y nftables, con medición fuera de banda en el host.
- **130 corridas del perfil final** (10 repeticiones por combinación: 4 condiciones × 4 ataques, más la línea base) medidas en una sola plataforma, `laptop-dev`, y los scripts que las generan y las analizan.
- Los scripts que producen las tablas y las figuras del artículo directamente desde los datos crudos, con una verificación independiente de esos datos.
- La bitácora del trabajo: limitaciones, decisiones, anomalías y su explicación.

## Resultados principales (resumen; detalle en `docs/lab/09_analisis_tanda_real_laptop-dev.md`)

- Con firewall y VLAN solos (E1) el PLC siguió respondiendo al SCADA frente a los floods SYN, UDP e ICMP, pero el flood Modbus/TCP tumbó el runtime de OpenPLC en todas las corridas.
- El IPS en modo `drop` (E3) eliminó el 99,7–100 % del ataque volumétrico, pero el cliente legítimo recibió respuesta a solo el 42–49 % de sus solicitudes programadas, porque la VM del IPS se convirtió en el cuello de botella; en modo `alert` (E2) fue peor.
- La regla Modbus por umbral produjo falsos positivos sobre el SCADA legítimo (calibración, `docs/lab/05_problemas_anomalias.md`, A23).

## Estructura

```
CLAUDE.md       reglas de trabajo del laboratorio (no inventar datos, una plataforma, guardián de recursos)
docs/
  lab/          bitácora: hardware, versiones, limitaciones (L1–L8), decisiones (D1–D22), anomalías (A1–A24),
                logros, resultados auditados, análisis de la tanda real, seguimiento de los revisores y auditoría
  arquitectura.md, definiciones_metricas (en docs/lab/), reproducir.md (en docs/lab/)
  prompts/      prompts históricos con los que se construyó el laboratorio (ver su README)
lab/
  config/       perfiles de plataforma, reglas de Suricata, configuración de nftables y de los experimentos
  setup/        creación de la red, las VM y el software
  guard/        guardián de RAM, swap y temperatura
  harness/      arnés de medición: una corrida, una matriz de corridas, validación
  analysis/     resúmenes, estadística, tablas y figuras del artículo y sus verificaciones
data/
  raw/          datos crudos: runs.csv, una carpeta por corrida, guardián y versiones
  processed/    resúmenes por corrida, estadística y tablas intermedias
  captures/     solo el manifiesto con el hash de las capturas (las capturas pesan GB y no se versionan)
figures/ tables/   figuras y tablas del artículo generadas por scripts (ver sus README)
```

## Cómo usarlo

- **Reproducir los resultados sin correr el laboratorio:** `docs/lab/reproducir.md`, sección 6 (basta Python 3 con SciPy y matplotlib; no hacen falta VMs).
- **Montar y correr el laboratorio desde cero:** `docs/lab/reproducir.md`, secciones 1 a 5 (requiere sudo una vez, KVM y unos 14 GiB de RAM).

## Estado

- Tanda real completa y analizada; los resultados, tablas y figuras del artículo salen de estos datos.
- Limitaciones declaradas: una sola máquina física con VM, un switch virtual (no se evalúa hardware de switch industrial), regla Modbus no recalibrada y Snort no evaluado (`docs/lab/03_limitaciones.md`).
- Aún no hay archivo de licencia: hay que elegir una (código y datos) antes de que otras personas reutilicen el repositorio.
