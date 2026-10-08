---
description: Prende o apaga la delegación por modelo, o muestra sus métricas
argument-hint: on | off | metrics [id-de-sesión] [--base modelo]
---

Argumentos: **$ARGUMENTS**

- `on` — Aplicá el ruteo de "Delegación por modelo" del CLAUDE.md por el resto de la sesión: ejecutar va a `sonnet-exec`, y planificar, revisar o cazar bugs va a `opus-review`.
- `off` — Volvé al default: no deleges nada por tu cuenta, hacé el trabajo vos.
- `metrics` — Corré `python <ruta>/delegar-metrics.py` pasándole el resto de los argumentos tal cual (id de sesión y/o `--base <modelo>`; sin id usa la sesión más reciente). Ubicá el script sin recorrer todo el disco: buscá `delegar-metrics.py` solo dentro de `~/.claude/plugins/` (ahí queda instalado el plugin `delegacion-por-modelo`) y, si no está, usá `~/.claude/scripts/delegar-metrics.py`. Mostrame la salida completa y sumá una línea con lo que más importa. Avisame que los tokens de salida del transcript pueden estar subcontados, así que el costo real es un piso. Los precios están en `delegar-precios.json`, junto al script.

En cualquiera de los modos, si nombro un agente explícitamente, usalo: la orden directa manda sobre el modo.

Si no te pasé argumento, decime en qué modo está la sesión y cuál es el otro.

Para `on` y `off`: confirmá en una línea y no hagas nada más, porque solo cambian el modo y no son una tarea. Para `metrics`, mostrá el resultado y nada más.
