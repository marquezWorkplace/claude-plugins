# dev

Skill para coordinar un desarrollo grande con **varias conversaciones de Claude en paralelo**.

Esta sesión (el **coordinador**, Opus o Fable) entrevista, planifica, hace la base común y reparte el trabajo en **pistas** —conversaciones anidadas que el propio coordinador abre, cada una dueña de un área del repo y ejecutando con el modelo que elijas (por ejemplo Sonnet)—. El coordinador las dirige por mensajes, revisa y verifica por su cuenta cada entrega, integra, conduce las pruebas de punta a punta y manda las correcciones.

La idea: el modelo caro piensa y revisa, el barato ejecuta, y nadie le pisa los archivos a otro.

No es para un cambio chico que cabe en una sola sesión. Usala cuando el desarrollo tenga **varias áreas** que convenga llevar en paralelo con un contrato compartido entre ellas.

> ⚠️ **Dónde funciona: solo Claude Desktop.** Se puede instalar e invocar en Claude Code CLI, pero su flujo central —abrir y dirigir las «pistas» con `start_session`— depende del **MCP de sesiones del Desktop** (`mcp__ccd_session__*`), que el CLI no tiene. En el CLI la skill carga pero se traba al intentar abrir la primera pista. El CLI tiene otro modelo de paralelismo (subagentes `Agent`, `Workflow`), pero es un patrón distinto —agentes efímeros, no conversaciones peer dirigibles por mensajes—, no un reemplazo de esta skill.

## Prerrequisitos

- **Claude Desktop con el MCP de sesiones** (`mcp__ccd_session__*` / `mcp__ccd_session_mgmt__*`): es lo que abre y dirige las pistas con `start_session`. Sin ese MCP, el reparto en pistas no funciona (en el CLI pelado no aplica).
- Una **vault de Obsidian** (o una carpeta de coordinación al lado del repo): es el cerebro/memoria del proyecto —plan, contrato, notas de tareas con su bitácora, guiones—. El coordinador la usa solo; vos no tenés que tocarla.
- **git con worktrees** recomendado (hay un modo sin-git de primera clase para quien no lo use).

## Cómo usarla (paso a paso, desde tu lado)

1. **Arrancá en Claude Desktop con un modelo capaz como coordinador** (Opus o Fable). Ese modelo piensa, planifica y revisa, así que conviene que sea el bueno. El modelo del coordinador es el de la sesión donde escribís `/dev` y **no se cambia a mitad de camino**.
2. **Escribí `/dev`** y contá qué querés construir (o pedí «planificá y repartí este cambio entre varias conversaciones de Claude»).
3. El coordinador **lee el proyecto y te hace solo las preguntas que cambian el plan** (dónde vive el estado, quién es dueño de qué dato, qué se elimina, cómo se da de alta algo). Respondé con tu criterio; si tenés una idea propia, decila y la toma tal cual.
4. Te muestra **el plan**: fases, reparto de áreas, qué archivo es de quién, cómo se verifica.
5. **Te pregunta el modelo de cada pista y cuántas pistas** (ver abajo). Acá elegís.
6. El coordinador hace la **base común** (esquema, contratos, migraciones) y después **abre las pistas él mismo** y las dirige. **Vos no abrís las pistas ni escribís en ellas.**
7. A partir de ahí **hablás solo con el coordinador.** Preguntale «¿cómo va?» cuando quieras: mira el estado real y te responde corto, con números de pruebas y qué falta.
8. El coordinador **revisa y verifica cada entrega por su cuenta** (no confía en lo que reporta la pista), integra las ramas, corre la prueba de punta a punta y te propone qué sigue. **Nada se sube ni se despliega sin tu orden explícita.**

### ¿Y si solo escribo `/dev` sin decir el modelo?

**Te pregunta.** Después de mostrarte el plan, el coordinador abre un diálogo y te deja elegir:

- **Qué modelo corre cada pista** — te recomienda **Sonnet** por defecto (suele alcanzar para ejecutar sin gastar de más), pero elegís con libertad.
- **Cuántas pistas y qué área lleva cada una** — te recomienda un número (típico **2–4**) y vos aprobás.

Podés adelantarlo al invocar y se saltea la pregunta, por ejemplo: `/dev ejecuta Sonnet, 3 pistas`.

El **modelo del coordinador nunca se pregunta**: es el de la sesión donde escribiste `/dev`.

## Lo que vos NO tenés que hacer

- **No abras ni escribas en las pistas.** Son conversaciones que maneja el coordinador; si les escribís, confundís la coordinación.
- **No hace falta que sepas git ni worktrees:** el coordinador arma las copias de trabajo y las ramas.
- **No repartas archivos ni resuelvas choques a mano:** el plan asigna un solo dueño por archivo.
- **No tenés que mantener la vault:** es la memoria del coordinador, no tu tablero.

Tu trabajo es decidir (producto, modelos, cuántas pistas), responder dudas y dar la orden final de subir/desplegar.

## Recomendaciones

- **Coordinador = modelo capaz** (Opus o Fable). Es quien piensa y revisa; ahí es donde conviene gastar.
- **Pistas = Sonnet** por defecto. Subí a algo más capaz solo si esa área lo justifica; no hay tope rígido respecto al coordinador, pero no uses más de lo que la pista necesita.
- **Pocas pistas (2–4).** Cada pista de más es más costo de coordinación. Sumá una solo si el área es de verdad independiente.
- **Dejá que el coordinador planifique antes de pedir ejecutar.** Las preguntas de producto que te hace al inicio son las que evitan rehacer trabajo.
- **Una sesión, un modelo.** Si querés orquestar con otro modelo, abrí una sesión nueva con ese modelo e invocá `/dev` ahí; el coordinador en marcha no cambia de modelo.
- **Relevo:** si el coordinador se satura de contexto, abrí otra sesión con `/dev`. El nuevo solo lee hasta que le confirmes que el viejo cerró; evitá tener dos coordinadores activos a la vez.
- **Recursos del PC:** cada copia de trabajo y cada compilación (Rust, Android…) cuesta GB. Al cerrar una ronda, pedile que borre las copias de verificación. Vigilá el disco.
- **Secretos:** nunca al chat, la vault ni git. Van en una carpeta local fuera de los repos; al coordinador le pasás solo la ruta y las reglas de uso.

## Qué trae

- `skills/dev/SKILL.md` — el flujo completo en 8 pasos (lo ejecuta el coordinador).
- `skills/dev/references/plantillas.md` — esqueletos de las notas, briefs, mensajes y guiones.
