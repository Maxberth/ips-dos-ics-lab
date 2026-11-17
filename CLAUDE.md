# Reglas permanentes del laboratorio (ICITS'27, IPS contra DoS en ICS)

Se aplican a todos los prompts de `docs/prompts/` y a cualquier trabajo en este repo.

- **Idioma:** documentación y respuestas en español. Código y nombres de archivo en inglés o en español sin tildes.
- **Prohibido inventar, estimar o rellenar datos.** Un valor en un CSV solo sale de una medición real hecha por un script del repo. Si una medición falla, se registra `status=failed` y no se sustituye. Los datos de prueba de los scripts van marcados `SYNTHETIC` y nunca van a `data/raw/` ni a figuras del paper.
- **Dudar siempre.** Cada resultado importante necesita una segunda fuente independiente (por ejemplo, contadores de Suricata frente a paquetes contados en la captura del host). Si no coinciden, es una anomalía: va a `docs/lab/05_problemas_anomalias.md` y no se avanza hasta explicarla o declararla.
- **Verificar antes de avanzar.** Cada paso termina con una comprobación objetiva y su salida en `docs/lab/logs/`. Si falla, se detiene y se reporta.
- **Plataformas:** cada corrida lleva `platform=<nombre>` (`laptop-dev` o `pc-miguel`). Los datos de `laptop-dev` son de calibración. Los números del paper salen de una sola plataforma (`pc-miguel`). Nunca se mezclan plataformas en una tabla o figura.
- **Perfiles:** los scripts, reglas y el arnés son idénticos en todas las plataformas. Solo cambia `lab/config/profile_<plataforma>.env` (RAM, vCPU, pinning, umbrales).
- **Recursos:** el equipo no debe llegar al 100 % de RAM ni a temperaturas peligrosas. El guardián (`lab/guard/guard.sh`) debe estar activo antes de crear VMs o lanzar ataques, y sus umbrales salen del perfil. Si pide PAUSE o ABORT, se obedece.
- **Aislamiento:** el switch `ovs-ot` no tiene puertos físicos. El laboratorio no toca `enp2s0`, `wlan0`, `tailscale0` ni las redes de Docker. Ningún ataque sale del host. No se usa `--rand-source` ni se apunta fuera de 192.168.10/20/30.0/24.
- **sudo:** solo el script `lab/setup/root_setup.sh`, que ejecuta el usuario. Todo lo demás corre sin privilegios (grupos `libvirt` y `wireshark`). Nunca `pacman -Sy` solo. Nunca `rm -rf` fuera de `lab/`, `data/` o el directorio de imágenes del laboratorio.
- **Documentación:** al cerrar cada prompt se actualiza `docs/lab/00_diario.md` y lo que corresponda (`01`–`08`). Un commit por paso verificado.
- **Metadatos:** cada artefacto lleva fecha UTC, commit del repo, plataforma y versiones relevantes.
- **Observaciones:** se mantiene `docs/lab/08_mapa_observaciones.md` con qué observación (0–26 de `docs/observaciones_icits27.md`) cubre cada paso.
