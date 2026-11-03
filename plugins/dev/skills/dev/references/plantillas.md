# Plantillas de /dev

Son esqueletos. Hay que adaptar los nombres al proyecto y escribir para alguien que no vio la conversación.

## Contenido

1. Nota principal del plan
2. Contrato
3. Nota de tareas de una pista
4. Brief para lanzar una pista (el `prompt` del `start_session`)
5. Mensajes del coordinador a una pista
6. Guion de prueba de punta a punta
7. Formato de entrada de la bitácora (el informe vivo, dentro de la nota de tareas)
8. Nota «Estado actual» (para retomar o relevar)

---

## 1. Nota principal del plan

```markdown
---
tags: [plan, <tema>]
estado: aprobado
creado: <fecha>
---

# <Tema> — plan por fases

> [!info] Nota principal
> <una frase: qué cambia y por qué>. Contrato: [[<Tema> - contrato]]. Tareas: [[Tareas - A]] · [[Tareas - B]] · [[Tareas - C]].

## Contexto
<qué está mal hoy, con rutas y líneas reales: lo que encontraron los agentes Explore>

## Decisiones
<del usuario, numeradas y con fecha>
Propuestas del coordinador (se aprueban con el plan): <…>

## Modelo objetivo
<diagrama corto en texto>

## Fases
### Fase 0: base común (coordinador)
### Fase 1…N: <tareas por pista, con id (A1, B2…), los archivos y el criterio de «hecho»>; puntos de encuentro ⇄

## Reparto entre pistas
| Pista | Copia de trabajo / rama | Es dueña de | No toca |

## Verificación
<comandos de prueba por pista y la prueba de punta a punta>

## Preguntas abiertas

## Estado por fase
| Fase | Estado |
```

## 2. Contrato

```markdown
# <Tema> — contrato

> [!info] Es la única fuente compartida. Solo la pista <X> edita <rutas del contrato>. Las demás piden cambios abajo.

## 1. Quién escribe qué
## 2. Esquema / migraciones
## 3. Rutas y formatos
## …
## Estado al cerrar la fase 0
<pruebas que pasan, y pruebas rojas a propósito con la pista que las arregla>

## Avisos de <X>
`fecha · commit · qué cambia para las otras pistas`

## Cambios pedidos
`fecha · pista · pedido · estado` (pendiente / hecho (`commit`) / parcial / no se hará: por qué)
```

**Regla:** el coordinador no escribe secciones numeradas del contrato mientras su dueño lo está editando, porque ya hubo choques de numeración. Las decisiones del usuario van como entrada en «Cambios pedidos» («Coordinador (decisión del usuario)»), y el dueño las integra.

## 3. Nota de tareas de una pista

```markdown
# Tareas — pista <X>

> [!info] Para una instancia nueva: leé primero [[plan]] (Decisiones) y [[contrato]] (por ruta absoluta).

## Dónde se trabaja
- Copia de trabajo: `<ruta absoluta>`. Al crearla: con git `git worktree add ../<proyecto>-<x> -b <rama-x> <base>`; sin git, copiar la carpeta base a `../<proyecto>-<x>`.
- **Archivos propios:** … · **No tocar:** …

## Tareas
| Id | Qué (archivos) | Hecho cuando |

**Orden:** … · **Desbloquea a:** …

## Pruebas
<comandos exactos, trampas conocidas del entorno>

## Reglas
<sin push ni despliegue; cómo compilar; recursos compartidos y cómo avisar>

## Bitácora de la pista
> El informe vivo de la pista (formato de entrada en §7). Orden cronológico, la entrada nueva **al final**. El coordinador también escribe acá (entradas «Coordinador: …»).
- <fecha> · **<tarea>** (`<commit>` · `<rama>`) — Hecho… · Probado (números)… · Decisiones a confirmar… · Bloqueos/pedidos… · Desbloquea a…
```

## 4. Brief para lanzar una pista

El brief es el **`prompt` del `start_session`** con que el coordinador abre la pista (no un `SendMessage` aparte); el contexto general va en `background` (mínimo 80 caracteres). Las rutas van **absolutas**: la pista no vio esta conversación.

> **En modo CLI (`claude --bg`):** el `prompt` posicional **no arranca** la pista (queda ociosa), así que el brief se entrega **por `SendMessage`** después de lanzarla, y la pista **crea su propio worktree** desde el brief (al ser dueña, commitea sin trabarse). El mismo texto de abajo sirve de brief; solo cambia por dónde llega. Ver «Modo CLI» en el SKILL.

```text
Eres la instancia de la pista <X> del plan «<tema>». Respondé siempre en <idioma>.
1. Leé primero (rutas absolutas): <plan> (Decisiones), <contrato>, y tu nota de tareas <ruta>.
2. No edites nada hasta crear y entrar en tu copia. Creála: con git, git worktree add ../<proyecto>-<x> -b <rama-x> <base> (base @ <commit>); sin git, copiá la carpeta base <ruta base> a ../<proyecto>-<x>. Trabajá solo ahí. Después: <instalar y compilar>.
3. Hacé las tareas en el orden de la nota: <ids>. Commiteá por tarea (sin git: fijá un hito por tarea).
Al cerrar cada tarea: agregá una entrada en la «Bitácora de la pista» de tu nota de tareas (qué, commit, qué probaste y qué no con números, decisiones propias a confirmar, bloqueos, qué desbloquea) y avisame a mí (el coordinador, sesión «<nombre del coordinador>») con un SendMessage corto que apunte a esa entrada. El mensaje es solo el aviso; el informe vive en la bitácora. No encadenes todo sin avisar: la bitácora es mi única ventana a tu avance.
Contrato: <quién es dueño; cómo se piden cambios>.
Reglas: <no tocar …; no commitear …; sin push ni despliegue sin orden del usuario; cómo compilar; avisar antes de usar <recurso compartido>>.
Al terminar: una nota «<pieza> — cómo funciona ahora» (estado actual, decisiones y su porqué, cómo probar, qué no está probado) y un aviso en las notas que quedaron viejas.
Si algo del plan no cierra, decímelo en vez de inventar.
```

El `background` lleva el objetivo general, las decisiones tomadas y cómo encaja esta pista (3 a 6 líneas). Para que la pista pueda contestarte, el brief debe incluir **el nombre/`session_id` de la sesión coordinadora** (el que `ListAgents` muestra como «This session is …»), porque el brief llega por `start_session` y la pista no lo conoce de otro modo.

## 5. Mensajes del coordinador a una pista

> Los mensajes son el **empujón en vivo**; el contenido durable (informe, pedidos, decisiones) va a la vault y el mensaje lo apunta.

- **Empezar o seguir:** «Mensaje del coordinador. <contexto en una línea>. **Primero:** fusioná `<base>` @ `<commit>`. Tus puntos (commiteá cada uno): 1… 2… Reglas: … Al cerrar cada punto, anotá en tu bitácora y mandame un `SendMessage` corto que apunte a ella.»
- **Corrección tras la revisión:** di qué viste, con archivo y línea, por qué está mal (el caso concreto que falla) y qué esperás. Si el usuario lo aprobó, decilo.
- **Retomar tras una interrupción:** «Tu turno se interrumpió en <paso>. Antes de seguir, anotá lo que ya hiciste. Revisá que el entorno siga vivo. Seguí desde <paso>, anotando cada paso al terminarlo.»
- **Encargo para después** (la pista está ocupada): «No interrumpas <tarea actual>. Esto es para hacer apenas la termines: …»

## 6. Guion de prueba de punta a punta

```markdown
# <Prueba> — guion

> La conduce una sola sesión: <pista>. Rama `<base>` @ `<commit>`, todo compilado desde cero.

## Preparación
<servicios, puertos, copias de datos propias, equipos físicos y cómo dejarlos limpios>

## Guion
Marcá cada paso con ✅, ❌ (qué pasó y a qué pista le toca) o ⏭ (por qué), **apenas lo termines**.
1. …

## Al terminar
Limpiar procesos y redirecciones, liberar los equipos y escribir el resultado.

## Resultado
### Resumen: ✅ … · ❌ … · ⏭ …
### Qué le toca a cada pista
```

## 7. Formato de entrada de la bitácora (el informe vivo)

No es un archivo aparte: es la sección **«Bitácora de la pista»** dentro de la nota de tareas (§3), en la vault. La pista agrega una entrada al cerrar cada tarea/entrega (orden cronológico, la nueva al final) y le avisa al coordinador con un `SendMessage` corto que la apunta. El coordinador la lee para instruir y también escribe ahí (entradas «Coordinador: …»). Lo que un pedido al contrato necesita va **además** a «Cambios pedidos» del contrato. Formato de cada entrada:

```markdown
- <fecha> · **<tarea o entrega>** (`<commit>` · `<rama>`)
  - **Hecho:** <qué quedó, archivos>
  - **Probado:** <qué corriste y con qué números> · **Sin probar:** <qué falta>
  - **Decisiones propias (a confirmar):** <las que el usuario debe confirmar>
  - **Bloqueos / pedidos al contrato:** <qué te traba, qué pediste>
  - **Desbloquea a:** <pistas>
```

## 8. Nota «Estado actual» (para retomar o relevar)

Una sola nota en la vault, **reescrita al cerrar cada ronda** (no un historial). Es lo que permite que una sesión nueva —o un coordinador de relevo— retome sin leer todas las bitácoras.

```markdown
# Estado actual — <tema>

> Reescrita el <fecha>. Reemplaza lo anterior; para el detalle histórico, las bitácoras.

## Producción / base
- Rama o copia base: `<nombre>` @ `<commit>`. Qué hay desplegado: <…>.

## Pistas
| Pista | Sesión (`session_id`) | Copia / rama | Estado | Última entrega |

## Qué falta
<lo pendiente por pista, en una línea cada uno>

## Decisiones abiertas
<las que esperan al usuario>

## Notas viejas
<cuáles quedaron reemplazadas y por cuál>
```
