# PC-ALEM · Preparar mi PC para la tanda real (sin ejecutarla)

Lo ejecuta Alem en su PC (pc-alem), dentro de Claude Code.

## PROMPT (copiar desde aquí)

Soy Alem y esta es mi PC de escritorio (pc-alem). Quiero preparar el laboratorio del paper ICITS'27, pero **sin ejecutar todavía ninguna prueba ni instalar nada**.

1. **Analiza mi PC en modo solo lectura.** Clona el repo privado `Maxberth/ips-dos-ics-lab`, rama `lab/ips-icits27`, en `~/code/articulo/ips-dos-ics-lab`. Respeta `CLAUDE.md`. Ejecuta `lab/setup/inventario_plataforma.sh pc-alem` y resume:
   - CPU con su topología (`lscpu -e`);
   - RAM libre;
   - disco;
   - temperatura en reposo;
   - KVM e IOMMU;
   - Docker y otras redes que puedan chocar con 192.168.10/20/30/99/250.0/24;
   - firewall del host;
   - versión del sistema.
   Compáralo con laptop-dev y pc-miguel en `docs/lab/plataformas/comparacion.md`, y crea `docs/lab/plataformas/pc-alem.md`.
2. **Lee las instrucciones previstas para pc-miguel** en `docs/lab/pasar_a_pc-miguel.md` (y las lecciones A1–A18 y D1–D20 de `docs/lab/`) y **readáptalas a mi PC**:
   - crea `lab/config/profile_pc-alem.env` con la RAM y vCPU por VM, el pinning según mi topología y los umbrales del guardián para un escritorio con buena refrigeración (sin batería);
   - crea `docs/lab/pasar_a_pc-alem.md` con los comandos exactos para mi PC, incluida la línea de `sudo bash lab/setup/root_setup.sh lab/config/profile_pc-alem.env` que tendré que ejecutar yo.
   No cambies los scripts, las reglas ni el arnés: solo el perfil.
3. Haz commit en la rama, con `platform=pc-alem`, y **detente**. Dime:
   - qué cumple y qué no, con evidencia;
   - qué riesgos ves;
   - cuánto estimas que tarda la tanda real (E0, E1 y E3 × syn y modbus × 10, perfil `final`).
   **Espera mi decisión antes de instalar paquetes, crear VMs o lanzar cualquier prueba.**

## FIN DEL PROMPT
