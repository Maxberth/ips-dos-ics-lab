# Auditoría del piloto (laptop-dev, perfil piloto_final)

Generado por `lab/analysis/audit_pilot.py` a partir de `data/processed/run_summary_laptop-dev_piloto_final.csv`. Datos de calibración: no se usan en el paper.

Leyenda: (a) ataque capturado en la VLAN 20 (antes del IPS), (b) en la VLAN 30 (después), (c) `ips.blocked` de Suricata, (d) `queue_dropped` de NFQUEUE.

| Corrida | Control | Resultado | Veredicto |
|---|---|---|---|
| `20261117T184754Z` E0 none | captura sin pérdidas relevantes (dumpcap) | 0.00 % descartado | OK |
| `20261117T184754Z` E0 none | tráfico legítimo (SCADA) | disponibilidad 100.00 %, timeouts 0, RTT mediana 0.804 ms, p95 0.905 ms | OK |
| `20261117T184754Z` E0 none | valores imposibles | ninguno | OK |
| `20261117T184754Z` E0 none | temperatura máxima del host | 53.8 °C | OK |
| `20261117T190931Z` E1 udp | el ataque ocurrió (pps del kernel del atacante) | 178116 pps | OK |
| `20261117T190931Z` E1 udp | E1 (router): (a) ≈ (b) | (a)=5287876 (b)=5288920 eliminado -0.02 % | OK |
| `20261117T190931Z` E1 udp | captura sin pérdidas relevantes (dumpcap) | 1.01 % descartado | ADVERTENCIA |
| `20261117T190931Z` E1 udp | tráfico legítimo (SCADA) | disponibilidad 100.00 %, timeouts 0, RTT mediana 0.802 ms, p95 3.942 ms | OK |
| `20261117T190931Z` E1 udp | valores imposibles | ninguno | OK |
| `20261117T190931Z` E1 udp | temperatura máxima del host | 81.6 °C | OK |
| `20261117T191113Z` E1 modbus | el ataque ocurrió (pps del kernel del atacante) | 5324 pps | OK |
| `20261117T191113Z` E1 modbus | E1 (router): (a) ≈ (b) | (a)=159713 (b)=159551 eliminado 0.10 % | OK |
| `20261117T191113Z` E1 modbus | captura sin pérdidas relevantes (dumpcap) | 0.05 % descartado | OK |
| `20261117T191113Z` E1 modbus | tráfico legítimo (SCADA) | disponibilidad 99.67 %, timeouts 0, RTT mediana 0.192 ms, p95 0.419 ms | OK |
| `20261117T191113Z` E1 modbus | valores imposibles | ninguno | OK |
| `20261117T191113Z` E1 modbus | temperatura máxima del host | 67.8 °C | OK |
| `20261117T192635Z` E1 icmp | el ataque ocurrió (pps del kernel del atacante) | 148695 pps | OK |
| `20261117T192635Z` E1 icmp | E1 (router): (a) ≈ (b) | (a)=4240729 (b)=4070842 eliminado 4.01 % | OK |
| `20261117T192635Z` E1 icmp | captura sin pérdidas relevantes (dumpcap) | 4.22 % descartado | ADVERTENCIA |
| `20261117T192635Z` E1 icmp | tráfico legítimo (SCADA) | disponibilidad 100.00 %, timeouts 0, RTT mediana 11.175 ms, p95 34.417 ms | OK |
| `20261117T192635Z` E1 icmp | valores imposibles | ninguno | OK |
| `20261117T192635Z` E1 icmp | temperatura máxima del host | 82.0 °C | OK |
| `20261117T193542Z` E1 syn | el ataque ocurrió (pps del kernel del atacante) | 176533 pps | OK |
| `20261117T193542Z` E1 syn | E1 (router): (a) ≈ (b) | (a)=4188773 (b)=4119392 eliminado 1.66 % | OK |
| `20261117T193542Z` E1 syn | captura sin pérdidas relevantes (dumpcap) | 13.60 % descartado | ANOMALÍA |
| `20261117T193542Z` E1 syn | tráfico legítimo (SCADA) | disponibilidad 99.33 %, timeouts 2, RTT mediana 31.706 ms, p95 264.428 ms | OK |
| `20261117T193542Z` E1 syn | valores imposibles | ninguno | OK |
| `20261117T193542Z` E1 syn | temperatura máxima del host | 82.5 °C | OK |
| `20261117T194819Z` E1 modbus | el ataque ocurrió (pps del kernel del atacante) | 5203 pps | OK |
| `20261117T194819Z` E1 modbus | E1 (router): (a) ≈ (b) | (a)=156083 (b)=156066 eliminado 0.01 % | OK |
| `20261117T194819Z` E1 modbus | captura sin pérdidas relevantes (dumpcap) | 0.01 % descartado | OK |
| `20261117T194819Z` E1 modbus | tráfico legítimo (SCADA) | disponibilidad 99.67 %, timeouts 0, RTT mediana 0.199 ms, p95 0.584 ms | OK |
| `20261117T194819Z` E1 modbus | valores imposibles | ninguno | OK |
| `20261117T194819Z` E1 modbus | temperatura máxima del host | 69.2 °C | OK |
| `20261117T195015Z` E3 syn | el ataque ocurrió (pps del kernel del atacante) | 149228 pps | OK |
| `20261117T195015Z` E3 syn | (a)−(b) ≈ (c)+(d) | (a)−(b)=4459442; (c)+(d)=4468387 (regla 2934356, cola 1534031); dif 0.20 % de (a) | OK |
| `20261117T195015Z` E3 syn | parte eliminada por regla frente a saturación | regla 65.7 %, cola llena 34.3 % | ANOMALÍA (saturación del IPS) |
| `20261117T195015Z` E3 syn | captura sin pérdidas relevantes (dumpcap) | 0.31 % descartado | OK |
| `20261117T195015Z` E3 syn | tráfico legítimo (SCADA) | disponibilidad 87.67 %, timeouts 37, RTT mediana 1.93 ms, p95 103.889 ms | OK |
| `20261117T195015Z` E3 syn | valores imposibles | ninguno | OK |
| `20261117T195015Z` E3 syn | temperatura máxima del host | 80.9 °C | OK |
| `20261117T195133Z` E2 syn | el ataque ocurrió (pps del kernel del atacante) | 174869 pps | OK |
| `20261117T195133Z` E2 syn | E2 (alert): (a) ≈ (b) | (a)=5213301 (b)=1623751 eliminado 68.85 %; cola llena 4710250 | ANOMALÍA (saturación del IPS) |
| `20261117T195133Z` E2 syn | captura sin pérdidas relevantes (dumpcap) | 0.69 % descartado | OK |
| `20261117T195133Z` E2 syn | tráfico legítimo (SCADA) | disponibilidad 80.73 %, timeouts 58, RTT mediana 0.138 ms, p95 0.161 ms | OK |
| `20261117T195133Z` E2 syn | valores imposibles | ninguno | OK |
| `20261117T195133Z` E2 syn | temperatura máxima del host | 83.0 °C | OK |
| `20261117T195300Z` E2 icmp | el ataque ocurrió (pps del kernel del atacante) | 151818 pps | OK |
| `20261117T195300Z` E2 icmp | E2 (alert): (a) ≈ (b) | (a)=4524333 (b)=1777879 eliminado 60.70 %; cola llena 3814430 | ANOMALÍA (saturación del IPS) |
| `20261117T195300Z` E2 icmp | captura sin pérdidas relevantes (dumpcap) | 0.75 % descartado | OK |
| `20261117T195300Z` E2 icmp | tráfico legítimo (SCADA) | disponibilidad 100.00 %, timeouts 0, RTT mediana 5.166 ms, p95 37.84 ms | OK |
| `20261117T195300Z` E2 icmp | valores imposibles | ninguno | OK |
| `20261117T195300Z` E2 icmp | temperatura máxima del host | 82.4 °C | OK |
| `20261117T195422Z` E3 icmp | el ataque ocurrió (pps del kernel del atacante) | 154112 pps | OK |
| `20261117T195422Z` E3 icmp | (a)−(b) ≈ (c)+(d) | (a)−(b)=4614260; (c)+(d)=4618259 (regla 2922755, cola 1695504); dif 0.09 % de (a) | OK |
| `20261117T195422Z` E3 icmp | parte eliminada por regla frente a saturación | regla 63.3 %, cola llena 36.7 % | ANOMALÍA (saturación del IPS) |
| `20261117T195422Z` E3 icmp | captura sin pérdidas relevantes (dumpcap) | 0.16 % descartado | OK |
| `20261117T195422Z` E3 icmp | tráfico legítimo (SCADA) | disponibilidad 100.00 %, timeouts 0, RTT mediana 0.579 ms, p95 6.371 ms | OK |
| `20261117T195422Z` E3 icmp | valores imposibles | ninguno | OK |
| `20261117T195422Z` E3 icmp | temperatura máxima del host | 81.1 °C | OK |
| `20261117T195539Z` E3 udp | el ataque ocurrió (pps del kernel del atacante) | 154909 pps | OK |
| `20261117T195539Z` E3 udp | (a)−(b) ≈ (c)+(d) | (a)−(b)=4626133; (c)+(d)=4622408 (regla 2646646, cola 1975762); dif 0.08 % de (a) | OK |
| `20261117T195539Z` E3 udp | parte eliminada por regla frente a saturación | regla 57.3 %, cola llena 42.7 % | ANOMALÍA (saturación del IPS) |
| `20261117T195539Z` E3 udp | captura sin pérdidas relevantes (dumpcap) | 0.10 % descartado | OK |
| `20261117T195539Z` E3 udp | tráfico legítimo (SCADA) | disponibilidad 82.68 %, timeouts 44, RTT mediana 1.399 ms, p95 110.938 ms | OK |
| `20261117T195539Z` E3 udp | valores imposibles | ninguno | OK |
| `20261117T195539Z` E3 udp | temperatura máxima del host | 80.4 °C | OK |
| `20261117T195655Z` E2 udp | el ataque ocurrió (pps del kernel del atacante) | 190909 pps | OK |
| `20261117T195655Z` E2 udp | E2 (alert): (a) ≈ (b) | (a)=5708281 (b)=2332838 eliminado 59.13 %; cola llena 3370800 | ANOMALÍA (saturación del IPS) |
| `20261117T195655Z` E2 udp | captura sin pérdidas relevantes (dumpcap) | 0.41 % descartado | OK |
| `20261117T195655Z` E2 udp | tráfico legítimo (SCADA) | disponibilidad 50.00 %, timeouts 52, RTT mediana 0.142 ms, p95 150.461 ms | OK |
| `20261117T195655Z` E2 udp | valores imposibles | ninguno | OK |
| `20261117T195655Z` E2 udp | temperatura máxima del host | 81.0 °C | OK |
| `20261117T195819Z` E2 modbus | el ataque ocurrió (pps del kernel del atacante) | 4728 pps | OK |
| `20261117T195819Z` E2 modbus | E2 (alert): (a) ≈ (b) | (a)=141830 (b)=141830 eliminado 0.00 % | OK |
| `20261117T195819Z` E2 modbus | captura sin pérdidas relevantes (dumpcap) | 0.00 % descartado | OK |
| `20261117T195819Z` E2 modbus | tráfico legítimo (SCADA) | disponibilidad 99.67 %, timeouts 0, RTT mediana 4.203 ms, p95 4.358 ms | OK |
| `20261117T195819Z` E2 modbus | valores imposibles | ninguno | OK |
| `20261117T195819Z` E2 modbus | temperatura máxima del host | 70.4 °C | OK |
| `20261117T195929Z` E3 modbus | el ataque ocurrió (pps del kernel del atacante) | 148 pps | ANOMALÍA |
| `20261117T195929Z` E3 modbus | (a)−(b) ≈ (c)+(d) | (a)−(b)=762; (c)+(d)=762 (regla 762, cola 0); dif 0.00 % de (a) | OK |
| `20261117T195929Z` E3 modbus | parte eliminada por regla frente a saturación | regla 100.0 %, cola llena 0.0 % | OK |
| `20261117T195929Z` E3 modbus | captura sin pérdidas relevantes (dumpcap) | 0.00 % descartado | OK |
| `20261117T195929Z` E3 modbus | tráfico legítimo (SCADA) | disponibilidad 100.00 %, timeouts 0, RTT mediana 0.787 ms, p95 1.074 ms | OK |
| `20261117T195929Z` E3 modbus | valores imposibles | ninguno | OK |
| `20261117T195929Z` E3 modbus | temperatura máxima del host | 63.6 °C | OK |

## Interpretación y puerta de calidad (P12)

Corridas incluidas: 14, de configuración final. E0 y E1 de todo el piloto, porque D18/D19 no les afectan. E2 y E3 solo desde las 19:50 UTC (2 colas, `exception-policy: ignore`, `stream.drop-invalid: no`, regla 1000004 rev 2). Las corridas descartadas o de configuraciones anteriores siguen en `data/raw/runs.csv` con su nota.

1. **Segunda fuente del bloqueo (obs. 1 y 20): CUMPLE.** En las 4 corridas E3, (a)−(b) coincide con (c)+(d) dentro del 5 %. En la corrida de A11 (1 cola), la cuenta firewall frente a Suricata + cola cuadró a 9 paquetes de 4,47 M.
2. **El IPS se satura (hallazgo, no error de medición).** Con un atacante de una IP, toda la carga entra en una cola NFQUEUE (A14). En laptop-dev, entre el 34 % y el 43 % de lo eliminado en E3 fue desbordamiento de cola, y en E2 (alert) se perdió entre el 59 % y el 69 % del ataque por la misma razón. **En el paper hay que reportar por separado los descartes por regla y por saturación**, y declarar que la saturación también afecta al tráfico legítimo.
3. **E1 (sin IPS): CUMPLE (a) ≈ (b)** en todos los ataques (eliminado < 1 %).
4. **Tráfico legítimo / falsos positivos: INCIERTO sin evidencia en contra.** Las reglas usan `track by_src` con umbrales de 50–100/s y el SCADA envía 10 solicitudes/s desde otra IP, así que ninguna regla puede activarse con su tráfico. Las pérdidas del SCADA en E2/E3 coinciden con el desbordamiento de cola. Para confirmarlo por paquete conviene una corrida E3 con `suricata-lab.yaml` (alertas en eve) y comprobar que ninguna alerta tiene origen 192.168.20.20.
5. **El ataque ocurrió:** 129–209 kpps según el ataque (kernel del atacante). La excepción es E3 modbus (148 pps): ahí el IPS descarta y las conexiones TCP del atacante se quedan sin avanzar. Es efecto del IPS, no un fallo del generador.
6. **Captura:** dumpcap descarta del 1 % al 14 % a más de ~170 kpps (E1 syn, E1 icmp). Los conteos de la captura son una cota inferior en esas corridas. El contador del firewall y el del kernel del atacante no dependen de la captura.
7. **Temperatura:** máximo de 82,6 °C, por debajo del PAUSE (88 °C). El guardián no pasó de OK/WARN durante las corridas válidas.
8. **OpenPLC (A15, A18):** el Modbus flood sin prevención (E1 ×2, E2) dejó el runtime caído al terminar el ataque. Con E3, el SCADA mantuvo el 100 % durante el ataque, pero el PLC cayó una vez al final. Es un resultado del escenario (`alive_after`).
9. **Variabilidad:** dos E3 syn casi iguales dieron un 88 % y un 93 % de disponibilidad. Hacen falta 10 repeticiones.

**Veredicto de la puerta de calidad:** la cadena de medición es defendible: las fuentes cuadran, los fallos se detectan y no hay valores imposibles. Se puede pasar a las corridas finales. Antes hay que decidir dos cosas:
- el umbral de la regla Modbus (A18);
- cómo se reporta la saturación del IPS en el paper.

Los datos de laptop-dev son de calibración y no van al paper.
