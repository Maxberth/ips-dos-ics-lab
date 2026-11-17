(* Proceso simulado del laboratorio: tanque con bomba y alarma. Ciclo de 100 ms.
   Mapa de registros en registers.md. Determinista: no depende del tráfico. *)
PROGRAM tank_sim
  VAR
    level    AT %QW0 : UINT := 500;
    cycles   AT %QW1 : UINT := 0;
    setpoint AT %QW2 : UINT := 800;
    status   AT %QW3 : UINT := 0;
    pump     AT %QX0.0 : BOOL := FALSE;
    alarm    AT %QX0.1 : BOOL := FALSE;
  END_VAR
  cycles := cycles + 1;
  IF pump THEN
    level := level + 5;
  ELSIF level > 3 THEN
    level := level - 3;
  END_IF;
  IF level < 200 THEN
    pump := TRUE;
  ELSIF level > setpoint THEN
    pump := FALSE;
  END_IF;
  alarm := level > 950;
  status := BOOL_TO_UINT(pump) + 2 * BOOL_TO_UINT(alarm);
END_PROGRAM

CONFIGURATION Config0
  RESOURCE Res0 ON PLC
    TASK task0(INTERVAL := T#100ms, PRIORITY := 0);
    PROGRAM instance0 WITH task0 : tank_sim;
  END_RESOURCE
END_CONFIGURATION
