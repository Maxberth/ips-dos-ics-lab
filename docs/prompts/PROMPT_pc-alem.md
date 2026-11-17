# Prompt para pc-alem

Lo pega Alem en Claude Code, en su PC de escritorio (pc-alem). pc-miguel no está disponible.

## PROMPT (copiar desde aquí)

Soy Alem y ejecuto esto en mi PC de escritorio (pc-alem). Trabaja en el repo privado `ips-dos-ics-lab`, rama `lab/ips-icits27` (si no está clonado, pregúntame la URL o la ruta). Lee `CLAUDE.md` y `docs/lab/pasar_a_pc-miguel.md`. Paso 1, solo lectura (sin instalar ni sudo): analiza mi PC con `lab/setup/inventario_plataforma.sh pc-alem` y guarda la ficha en `docs/lab/plataformas/pc-alem.md`: CPU, hilos y topología; RAM libre; disco; refrigeración y temperaturas en reposo (3 lecturas); KVM/IOMMU; distro y paquetes ya instalados; Docker, VPN o redes que choquen con 192.168.10/20/30.0/24. Paso 2: mapea los requisitos e instrucciones que el repo tenía para pc-miguel (`lab/config/profile_pc-miguel.env`, la guía, umbrales del guardián, presupuesto de RAM y núcleos, tiempos de corrida) y readáptalos a pc-alem: crea `lab/config/profile_pc-alem.env` y `docs/lab/pasar_a_pc-alem.md`, con cada cambio y su justificación. Los umbrales térmicos salen de mis mediciones, no de supuestos. Si mi distro no es CachyOS/Arch, adapta los comandos de instalación. Cada corrida llevará `platform=pc-alem`, sin mezclarse con `laptop-dev`. Paso 3: resume en 15 líneas o menos qué cambió, los riesgos y el comando exacto con sudo (si hace falta), haz commit local en la rama `lab/pc-alem` y DETENTE. No instales ni ejecutes nada del laboratorio hasta que yo te diga «ejecuta la prueba real».

## FIN DEL PROMPT
