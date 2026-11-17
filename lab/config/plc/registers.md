# Mapa de registros del PLC simulado (`tank_sim.st`)

OpenPLC Runtime, Modbus/TCP en `192.168.30.10:502`, unit id 1. Ciclo del programa: 100 ms.

| Variable | Dirección IEC | Modbus | Tipo | Significado |
|---|---|---|---|---|
| level | %QW0 | Holding register 0 | UINT | Nivel del tanque (0–1000), sube 5 por ciclo con la bomba encendida y baja 3 sin ella |
| cycles | %QW1 | Holding register 1 | UINT | Contador de ciclos (se desborda en 65535) |
| setpoint | %QW2 | Holding register 2 | UINT | Nivel al que se apaga la bomba (800, escribible) |
| status | %QW3 | Holding register 3 | UINT | bit 0 = bomba, bit 1 = alarma |
| pump | %QX0.0 | Coil 0 | BOOL | Bomba |
| alarm | %QX0.1 | Coil 1 | BOOL | Alarma (nivel > 950) |

El SCADA (`scada_poller.py`) lee los holding registers 0–3 (función 3) a 10 Hz. `cycles` permite comprobar que el PLC sigue ejecutando su ciclo durante un ataque.
