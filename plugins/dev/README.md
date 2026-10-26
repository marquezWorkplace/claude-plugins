# dev

Skill para coordinar un desarrollo grande con **varias conversaciones de Claude en paralelo**.

Esta sesión (el **coordinador**, Opus o Fable) entrevista, planifica, hace la base común y reparte el trabajo en **pistas** —conversaciones anidadas que el propio coordinador abre, cada una dueña de un área del repo y ejecutando con el modelo que elijas (por ejemplo Sonnet)—. El coordinador las dirige por mensajes, revisa y verifica por su cuenta cada entrega, integra, conduce las pruebas de punta a punta y manda las correcciones.

La idea: el modelo caro piensa y revisa, el barato ejecuta, y nadie le pisa los archivos a otro.

## Uso

Escribí `/dev` (o pedí planificar y repartir un cambio entre varias conversaciones de Claude). No es para un cambio chico que cabe en una sola sesión.

## Prerrequisitos

- **Claude Desktop con el MCP de sesiones** (`mcp__ccd_session__*` / `mcp__ccd_session_mgmt__*`): es lo que abre y dirige las pistas con `start_session`. Sin ese MCP, el reparto en pistas no funciona.
- Una **vault de Obsidian** (o una carpeta de coordinación): es el cerebro/memoria del proyecto —plan, contrato, notas de tareas con su bitácora, guiones—.
- **git con worktrees** recomendado (hay un modo sin-git de primera clase para quien no lo use).

## Qué trae

- `skills/dev/SKILL.md` — el flujo completo en 8 pasos.
- `skills/dev/references/plantillas.md` — esqueletos de las notas, briefs, mensajes y guiones.
