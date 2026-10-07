---
description: Prende o apaga la delegación por modelo en esta sesión
argument-hint: on | off
---

Cambiá el modo de delegación de esta sesión a: **$ARGUMENTS**

- `on` — Aplicá el ruteo de "Delegación por modelo" del CLAUDE.md por el resto de la sesión: ejecutar va a `sonnet-exec`, y planificar, revisar o cazar bugs va a `opus-review`.
- `off` — Volvé al default: no deleges nada por tu cuenta, hacé el trabajo vos.

En cualquiera de los dos modos, si nombro un agente explícitamente, usalo: la orden directa manda sobre el modo.

Si no te pasé argumento, decime en qué modo está la sesión y cuál es el otro.

Confirmá en una línea y no hagas nada más. Este comando solo cambia el modo; no es una tarea.
