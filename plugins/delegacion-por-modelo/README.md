# delegacion-por-modelo

Reparte el trabajo entre modelos usando subagentes: **Sonnet ejecuta, Opus planifica y revisa**.

Cada agente fija su modelo en el frontmatter de su propia definición, así que la selección no pasa por el selector de modelo de la sesión. Eso lo hace funcionar también en el Code tab del desktop app, donde el alias nativo `opusplan` no está disponible.

## Instalación

```
/plugin marketplace add marquezWorkplace/claude-plugins
/plugin install delegacion-por-modelo
```

Abrí una sesión nueva después de instalar: los agentes se cargan al arrancar.

## Qué trae

| Componente | Modelo | Para qué |
| --- | --- | --- |
| `sonnet-exec` | Sonnet | Implementar un plan ya acordado: editar archivos, correr comandos, tests |
| `opus-review` | Opus | Planificar algo con varias piezas, revisar código, cazar bugs difíciles |
| `/delegar` | — | Prende y apaga el ruteo automático para la sesión, y muestra métricas de consumo |

## Uso

**Para un uso suelto, nombrá el agente.** Funciona siempre, sin configurar nada:

- "delegá la implementación a sonnet-exec"
- "que opus-review revise esto"
- "pasale este bug a opus-review, ya probé dos cosas y no cede"

**Para un flujo sostenido, prendé el modo:**

- `/delegar on` — a partir de ahí rutea solo: ejecutar va a `sonnet-exec`, planificar o revisar va a `opus-review`.
- `/delegar off` — vuelve al default, sin delegación automática.
- `/delegar metrics` — tokens y costo por modelo y por subagente de la sesión, más una estimación del ahorro (ver abajo).
- `/delegar` sin argumento — te dice en qué modo está.

El valor va en la misma línea que el comando.

## Plan en archivo

Cuando `opus-review` planifica, no devuelve el plan en su respuesta: lo escribe a un archivo (`.claude/plans/<tarea>.md` por defecto) con objetivo, decisiones, alternativas descartadas, pasos, supuestos, riesgos y criterio de terminado, y devuelve solo la ruta. Quien delega le pasa esa ruta a `sonnet-exec`, que la lee antes de tocar nada. Así el plan no pasa por el contexto de la sesión principal y el ejecutor no pierde detalle en un resumen intermedio.

## Métricas

`/delegar metrics` corre `scripts/delegar-metrics.py`, que lee los transcripts de la sesión (el principal y los de sus subagentes) y muestra tokens y costo por modelo. Los precios están en `scripts/delegar-precios.json` (USD por millón de tokens; los de escritura de caché son un supuesto, corregilos si hace falta).

- **Costo real:** sale del `usage` del transcript.
- **Ahorro estimado:** reprecia los tokens de los subagentes como si los hubiera gastado el modelo de la sesión (o el que pases con `--base <modelo>`). Si tu sesión corre en Sonnet, planificar con Opus sale más caro y el resultado es un sobrecosto; el ahorro aparece con una sesión en Opus.
- **Límites:** los tokens de salida del transcript parecen subcontados, así que el costo real es un piso. El contrafactual además ignora que el trabajo delegado habría engordado el contexto principal. Tomalo como orden de magnitud.

Requiere Python 3 en el PATH.

## Dos cosas que conviene saber

**No delega tareas triviales, a propósito.** Un subagente paga un costo fijo de arranque — carga su system prompt, las herramientas y el contexto del proyecto desde cero, del orden de 27 mil tokens de input antes de hacer nada útil. Si la tarea hubiera costado menos que eso en el modelo caro, delegar sale más caro que no delegar. Por eso un cambio de una línea no se delega.

**Un agente no ve tu conversación.** Arranca con contexto limpio. El que delega tiene que resumirle lo necesario, y ahí se puede perder matiz. Para trabajo muy acoplado a la discusión previa, conviene hacerlo en la sesión principal.

## Ahorro esperado

Opus cuesta el doble que Sonnet por token, no cinco veces. Contra una línea de base de Opus haciendo todo, mover la ejecución a Sonnet ahorra sobre la parte que más tokens quema. Es real pero modesto, y solo aparece en tareas con volumen suficiente para amortizar el arranque del subagente.

## Opcional: disparo automático por defecto

Con el plugin solo, el ruteo automático se activa con `/delegar on` en cada sesión. Si querés que arranque prendido siempre, agregá esto a tu `~/.claude/CLAUDE.md`:

```markdown
# Delegación por modelo

Quiero que repartas el trabajo entre modelos usando subagentes, en automático.
Usá el Agent tool para esto: esta instrucción es la autorización.

- Ejecutar (editar archivos, correr comandos, aplicar un plan acordado): `sonnet-exec`.
- Planificar, revisar o buscar errores: `opus-review`.

No delegues si ya sos el modelo adecuado para esa tarea, ni tareas triviales.

Plan en archivo: `opus-review` escribe el plan a un archivo (`.claude/plans/<tarea>.md` por defecto) y devuelve solo la ruta. Para ejecutar, pasale a `sonnet-exec` esa ruta, no el contenido copiado. Antes de lanzar `sonnet-exec` en tareas grandes, leé el plan y chequeá que incluya mis preferencias y restricciones; si falta algo, pedíselo a `opus-review`.
```

Hace falta porque Claude Code trae una instrucción que le impide usar subagentes por iniciativa propia, y esa restricción se exceptúa cuando un `CLAUDE.md` los pide. Un plugin no transporta `CLAUDE.md`, así que este paso es manual.
