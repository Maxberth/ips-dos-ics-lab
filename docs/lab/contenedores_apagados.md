# Contenedores y Docker durante el laboratorio

**Revisado:** 2026-11-17 17:45 UTC (12:45 hora de Perú), en laptop-dev.

## Contenedores en ejecución

**Ninguno.** `docker ps` no mostró contenedores en ejecución, así que no se apagó ninguno.
Todos los contenedores de la máquina ya estaban detenidos (`Exited`) desde antes; no se tocaron (ni `stop`, ni `rm`, ni cambios de restart policy).

| Contenedor | Imagen | ID (corto) | Restart policy | Proyecto compose (directorio) | Estado |
|---|---|---|---|---|---|
| forja-embeddings | forja-embeddings:local | 0533f0244366 | no | /home/maxberth/code/forja-workspace/forja-api | exited (hace 8 días) |
| forja-db | pgvector/pgvector:pg16 | aa14225bb0da | no | /home/maxberth/code/forja-workspace/forja-api | exited (hace 8 días) |
| memoria-viva-db | pgvector/pgvector:pg16 | 2ea6597fc921 | no | /home/maxberth/orca/workspaces/memoria-viva/bowfin | exited (hace 8 días) |
| memoria-viva-embeddings | bowfin-embeddings | ae493db9114b | no | /home/maxberth/orca/workspaces/memoria-viva/bowfin | exited (hace 8 días) |
| patriac-minio-setup | bitnamilegacy/minio:latest | 903f84e7598a | no | /home/maxberth/code/patriac-platform | exited (hace 4 semanas) |
| patriac-minio | bitnamilegacy/minio:latest | 280136b16a0b | unless-stopped | /home/maxberth/code/patriac-platform | exited (hace 3 semanas) |
| patriac-postgres | postgres:16-alpine | 1e7d61255acd | unless-stopped | /home/maxberth/code/patriac-platform | exited (hace 3 semanas) |

Para encender uno: `docker start <nombre>`. O, con su compose: `cd <directorio> && docker compose up -d`.

## Servicio Docker

- Antes del laboratorio, `docker.service` estaba **inactivo** y `docker.socket` **activo** (Docker arranca solo cuando algo lo usa).
- A las 17:16:46 UTC, el inventario P02 ejecutó `docker network ls` y eso arrancó `dockerd` por activación de socket. Fue un efecto no buscado; el script ya está corregido.
- `lab/setup/root_setup.sh` detiene `docker.service` y `docker.socket` (no los deshabilita), para que Docker no consuma recursos ni toque la red durante las mediciones.

Para reactivar Docker después del laboratorio:

```bash
sudo systemctl start docker.socket docker.service
```
