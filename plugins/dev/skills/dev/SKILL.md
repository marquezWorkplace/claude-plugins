---
name: dev
description: "Coordina un desarrollo grande con varias sesiones de Claude en paralelo: esta sesión (Opus o Fable) entrevista al usuario, planifica, hace la base común, y reparte el trabajo en «pistas» —conversaciones de Claude anidadas que el propio coordinador abre, cada una con el modelo que elija el usuario (por ejemplo Sonnet)—, las dirige por mensajes, revisa y verifica por su cuenta cada entrega, integra, conduce las pruebas de punta a punta y manda las correcciones. Úsala siempre que el usuario escriba /dev, o pida planificar y repartir un cambio entre varias instancias, conversaciones o pistas de Claude, o pida que esta conversación «lleve el control» o coordine a otras, aunque no diga «skill». No es para un cambio chico que cabe en una sola sesión."
---

# /dev — coordinar pistas en paralelo

Esta sesión es el **coordinador**: el gestor principal del desarrollo. No escribe el código de las pistas: entrevista, planifica, decide con el usuario, reparte, revisa, verifica, integra y documenta. Es el único que ve el cuadro completo.

Las **pistas no son subagentes `Agent`:** son **conversaciones de Claude anidadas que el propio coordinador abre** (en Desktop con `start_session`; en el CLI con `claude --bg` — ver §0 y «Modo CLI»), una por área del repo. **El usuario no las crea ni escribe en ellas.** Aparecen como *peer sessions* en `ListAgents` y el coordinador les habla con `SendMessage`. Funciona porque el modelo caro piensa y revisa, el barato ejecuta, y nadie le pisa los archivos a otro.

El coordinador es **reactivo**: no deja tareas en segundo plano esperando respuesta. Reparte, y su turno termina. Cuando una pista le manda un mensaje al cerrar su labor, el coordinador lo analiza y contesta. **No sondea.** Los `SendMessage` entre sesiones son el **empujón en vivo** —«leé esto», «arrancá», «arreglá aquello»—; el registro durable de todo (informes, pedidos, decisiones) vive en la vault, no en los mensajes.

**El coordinador se queda con el modelo con el que arrancó.** Una sesión no puede cambiar su propio modelo a mitad de camino (tendría que releer todo el contexto). Si el usuario quiere orquestar con otro modelo, abre una sesión nueva con ese modelo e invoca `/dev` ahí. El modelo se elige **por pista**, nunca para el coordinador en marcha.

Invocar `/dev` es el pedido explícito del usuario de delegar, aunque la configuración general desaconseje delegar por defecto. No es para un cambio chico que cabe en una sola sesión: usala cuando el desarrollo tenga varias áreas que convenga llevar en paralelo con un contrato compartido entre ellas.

**Dónde corre: Desktop o CLI.** La skill necesita poder **abrir y dirigir otras sesiones de Claude**, y hay dos backends; el **§0** detecta cuál:
- **Claude Desktop** — con el MCP de sesiones (`start_session`, `list_sessions`, `set_session_model`…).
- **Claude Code CLI** — con las **sesiones en segundo plano nativas** del propio `claude` (`claude --bg`, más `claude agents/attach/logs/stop/rm`).

En los dos casos las pistas son **sesiones peer dirigibles por mensaje** (no subagentes `Agent`, sin fan-out), y `ListAgents`/`SendMessage` son el bus común. Las mecánicas que cambian entre backends —abrir, ver, frenar, retomar— van en §4/§5 para Desktop y en la sección **«Modo CLI»** al final, resumidas en una tabla de equivalencias.

**Git: recomendado, no obligatorio.** El jefe no siempre usa git, así que la skill no depende 100% de él:
- **Con git (recomendado):** cada pista trabaja en su **worktree** y rama; la integración es por *merge*.
- **Sin git:** cada pista trabaja en **su propia copia-carpeta** del proyecto (una carpeta aparte); el coordinador unifica los cambios a mano en una copia principal.
Si el proyecto no está en git, ofrecer `git init`; si el usuario no quiere, usar el modo sin-git. Todo lo demás (dueños, contrato, coordinación, verificación) sigue igual.

**La vault es el cerebro y la memoria del proyecto.** Toda la coordinación durable vive ahí: el plan, el contrato, las notas de tareas —cada una con su **bitácora**, que es el informe vivo de esa pista— y los guiones de prueba. Es una carpeta **compartida, por ruta absoluta, fuera de las copias de trabajo**, que todas las sesiones alcanzan igual con o sin git: la **vault de Obsidian** si existe, o si no una carpeta dedicada al lado del repo (`../<proyecto>-coordinacion/`). **Nunca dentro de los worktrees/copias ni en `docs/` del repo:** un archivo ahí solo lo ve la pista que lo tenga commiteado en su rama, y el coordinador en su copia no lo vería. A cada pista se le pasa la **ruta absoluta** de las notas que necesita. **No hay carpeta de informes aparte:** cada pista reporta en la bitácora de su propia nota de tareas, y los pedidos entre pistas van a «Cambios pedidos»/«Avisos» del contrato.

Plantillas de notas, mensajes y guiones: `references/plantillas.md`. Leerlo antes de escribir cada pieza.

## 0. Antes de nada: ¿con qué backend se orquesta?

**Primer paso, antes de entrevistar o planificar.** Detectá cómo vas a abrir y dirigir pistas:

- **Desktop** — ¿está el MCP de sesiones? `ToolSearch` (`select:mcp__ccd_session__start_session`). Si resuelve → **modo Desktop**: §4/§5 tal cual (`start_session`).
- **CLI** — ¿está el `claude` con sesiones en segundo plano? (`claude --help` muestra `--bg` y los subcomandos `agents/attach/logs/stop/rm`.) Si sí → **modo CLI**: §4/§5 con las variantes de la sección «Modo CLI» al final. `ListAgents`/`SendMessage` son el bus en ambos.
- **Ninguno** → avisá al usuario: sin backend no se abren pistas. Ofrecé seguir en una sola sesión, o abrir el entorno que falte.

**Preflight del modo CLI, antes de lanzar pistas:**
1. **Toolchain del proyecto instalado y en el PATH** (p. ej. `pnpm`, `cargo`): la pista hereda el entorno al nacer; si falta, se traba en el `install`.
2. **PATH de Windows no inflado:** miles de caracteres con duplicados rompen los scripts de npm/pnpm al correr por `cmd.exe` (`'node' no se reconoce`). Avisá al usuario y deduplicá si hace falta.
3. **Confianza de worktrees:** es interactiva y **no se pre-siembra por config** — pero no hace falta tocarla si la pista **nace en una carpeta ya confiada y crea su worktree ella misma** (ver «Modo CLI»).

## 1. Entender el pedido

1. **Leer antes de preguntar:**
   - la memoria del proyecto y su CLAUDE.md;
   - la vault o los `docs/` existentes;
   - `git worktree list` y las ramas recientes (si hay git).
   Si el área es grande, lanzar hasta 3 agentes `Explore` en paralelo (esto sí son subagentes del coordinador, para su propia investigación), uno por zona (por ejemplo: nube/web, servidor, apps), con preguntas concretas y pidiendo rutas y líneas.
2. **Preguntar solo lo que cambia el plan,** con `AskUserQuestion`: de 2 a 4 preguntas con opciones y una recomendada. Ejemplos: dónde vive el estado, quién es dueño de qué dato, qué se elimina, cómo se da de alta algo.
   - No adivinar decisiones de producto.
   - Si una respuesta del usuario trae una idea propia («depende de…»), tomarla tal cual y no forzarla a la opción recomendada.
3. **No preguntar todavía por modelos ni número de pistas:** eso se decide con el usuario **después** del plan (sección 2), cuando ya se ve el corte del trabajo.

## 2. Planificar y registrar

Escribir el plan en la **carpeta de coordinación** (vault, o la carpeta dedicada por ruta absoluta). Son tres tipos de nota, con las plantillas de referencia:

- **Nota principal del plan:**
  - contexto (qué está mal hoy, con rutas reales);
  - decisiones del usuario y propuestas propias (marcadas como tales);
  - modelo objetivo y fases;
  - reparto de dueños de archivos;
  - verificación;
  - preguntas abiertas;
  - una tabla «Estado por fase» que el coordinador mantiene al día.
- **Contrato:** la única fuente compartida (esquema, rutas, formatos, reglas). Lleva una sección «Cambios pedidos» donde las pistas piden cambios y otra «Avisos» donde el dueño del contrato anuncia lo que cambió.
- **Una nota de tareas por pista,** autosuficiente para una sesión que no vio esta conversación:
  - dónde trabaja (copia de trabajo y rama, por ruta absoluta);
  - de qué archivos es dueña y cuáles no toca;
  - las tareas con el criterio de «hecho» y el orden;
  - las dependencias con las otras pistas;
  - cómo se prueba, las reglas y la **bitácora de la pista** —su informe vivo: ahí la pista escribe, por tarea, qué hizo, commit, pruebas con números, decisiones a confirmar, bloqueos y qué desbloquea, y el coordinador deja sus pedidos (entradas «Coordinador: …»)—.

**El reparto debe evitar choques:** cada archivo tiene un solo dueño. El contrato compartido (esquema, tipos) lo edita **una sola pista**; las demás piden cambios por escrito. Así no hay dos versiones del contrato.

Mostrar el plan con `ExitPlanMode` si se está en modo plan.

**Después del plan, preguntar al usuario** con `AskUserQuestion` (salvo que ya lo haya dicho al invocar, p. ej. «/dev ejecuta Sonnet, 3 pistas»):
- **qué modelo corre cada pista** — el coordinador recomienda uno (por defecto Sonnet: suele alcanzar para ejecutar sin gastar de más) y el usuario elige con libertad; el **coordinador lo fija con `model` en el `start_session`** (o con `set_session_model` después). No hay tope rígido respecto al coordinador, pero sí el criterio de no usar un modelo más capaz ni más caro de lo que la pista necesita. **Si se omite, la pista hereda el modelo del coordinador, así que pasalo siempre**;
- **cuántas pistas** — el coordinador recomienda un número y qué área lleva cada una (según lo independientes que sean y la contención de recursos); el usuario aprueba cuántas y cuáles. Típico 2–4; cada pista de más es más costo de coordinación.

El modelo del **coordinador** no se pregunta: es el de esta sesión y no cambia.

**Registrar en la vault (al aprobar el plan):** crear el plan hub, el contrato (esqueleto; se completa en F0) y una nota de tareas por pista; marcar «reemplazado por…» en las notas que quedan viejas y actualizar el rumbo (p. ej. `Home.md`); y guardar en la memoria una entrada breve con el rumbo y dónde está el plan.

## 3. Fase 0: la base común

La hace **el coordinador**, antes de abrir las pistas, porque todas dependen de ella:

1. **Una rama base** que contenga todo lo necesario (sin git: una **copia base** del proyecto). Si hay ramas divergentes, comprobar con `git merge-base --is-ancestor` cuál contiene a cuál.
2. **Una copia de trabajo propia** —con git, `git worktree add ../<proyecto>-<base> -b <base> <commit>`; sin git, una carpeta aparte— para no tocar la de otras sesiones.
3. **Las notas de coordinación en la vault** al día (plan, contrato y una nota de tareas por pista, cada una con su bitácora vacía lista para reportar). No hay carpeta de informes aparte: cada pista reporta en la bitácora de su nota de tareas, que el coordinador lee para instruirla. Vive en la vault —fuera de las copias de trabajo— así que la ven todas las sesiones con o sin git y nunca choca al fusionar ramas.
4. El esquema, las migraciones, los contratos y los generadores que todas usan, con sus pruebas.
5. **Las pruebas que quedan rojas a propósito,** porque suponen el comportamiento viejo: listarlas en el contrato con la pista que las arregla.
6. **Commit en la rama base** (sin git: fijar la copia base) y completar la nota del contrato.

## 4. Repartir y lanzar las pistas

Las pistas son **conversaciones anidadas que abre el propio coordinador con `start_session`** (Claude Desktop lo permite), no subagentes. El usuario no las abre ni escribe en ellas. (En **modo CLI**, las pistas se abren con `claude --bg` en vez de `start_session`; ver la sección **«Modo CLI»** al final para el equivalente de §4 y §5.) El flujo Desktop:

1. **Cargar las herramientas diferidas** en una sola `ToolSearch`: `select:mcp__ccd_session__start_session,SendMessage,mcp__ccd_session_mgmt__set_session_model,mcp__ccd_session_mgmt__list_sessions,mcp__ccd_session_mgmt__get_session,mcp__ccd_session_mgmt__list_events,mcp__ccd_session_mgmt__stop_session,mcp__ccd_session_mgmt__archive_session,mcp__ccd_session_mgmt__unarchive_session`. `ListAgents` ya está disponible. (`TaskStop` es para subagentes propios; a las pistas no se les aplica.) Verificá los nombres exactos contra el schema real del MCP de sesiones de tu Claude Desktop antes de confiar en esta lista.
2. **Abrir una pista por área con `start_session`** —las independientes en el mismo turno, para que arranquen en paralelo—. Una línea en negrita por pista antes de las llamadas. Parámetros:
   - `initiation: "user_asked"` (abrir pistas es parte de lo que el usuario pidió al invocar `/dev`);
   - `title` descriptivo («Pista WEB: nube por sucursal») y `name` corto (`pista-web`);
   - `context: "fresh"` (no hereda esta conversación) + `background` con el contexto general (**obligatorio con `fresh`, mínimo 80 caracteres**);
   - **`model` explícito**, el elegido para la pista. **Pasalo siempre:** si lo omitís, la pista hereda el modelo del coordinador. Pasá `effort` solo si el usuario lo pidió; si no, omitilo y la pista usa el del modelo;
   - `use_worktree: false` (cada pista crea su propio worktree desde su brief, para controlar el nombre de rama y la propiedad de archivos); la pista no debe editar nada hasta crear y entrar en esa copia —si nace en la copia del coordinador, un edit temprano iría al lugar equivocado—;
   - `prompt`: **el brief** (plantilla en las referencias). El brief se entrega acá, en el `start_session`; no hay un `SendMessage` aparte para arrancar.
   Guardá el `session_id` que devuelve (`local_…`): con él —o con el título— la dirigís después.
3. **Verlas y dirigirlas:** `SendMessage` (a `session_id` o título) para hablarles; `ListAgents` y `list_sessions {"linked": true}` para el estado (ociosa/ocupada, carpeta, rama); `get_session` para modelo/esfuerzo; `list_events` para qué hizo. Anotar en la nota de la pista su `session_id` y la ruta absoluta de su copia de trabajo.

El **brief** (plantilla en las referencias) dice:
- qué notas leer primero, **por ruta absoluta** (el plan, el contrato y su nota de tareas);
- cómo crear su copia: con git `git worktree add ../<proyecto>-<pista> -b <rama> <base>`; sin git, copiar la carpeta base a `../<proyecto>-<pista>`; luego instalar y compilar;
- el orden de sus tareas y qué desbloquea a otras pistas;
- las reglas del proyecto (sin push ni despliegue sin orden, cómo compilar, recursos compartidos como un equipo físico);
- **cómo reportar:** al cerrar cada tarea, **agregar una entrada en la «Bitácora de la pista» de su nota de tareas** (qué hizo, commit, qué probó y qué no con números, decisiones propias a confirmar, bloqueos y qué desbloquea) y **avisarle al coordinador con un `SendMessage` corto** —a la sesión coordinadora por su nombre (incluirlo en el brief)— que apunte a esa entrada. El mensaje es solo el aviso; el informe vive en la bitácora. El coordinador no ve la salida de la pista: su ventana es esa bitácora. Sin esto, una pista encadena todo sin avisar y el coordinador queda a ciegas;
- al terminar, **una nota de «cómo funciona ahora»** de su pieza, no la historia, y un aviso en las notas que quedaron viejas.

## 5. Coordinar mientras trabajan

- **Reactivo, no sondear.** El turno del coordinador termina después de repartir. Los avisos llegan solos: el `SendMessage` de una pista aparece como `<cross-session-message>`, y al cerrar un turno la app inyecta los primeros ~400 caracteres de su informe (y continúa el turno del coordinador con un `<side-sessions-event>` si está ocioso). El coordinador los analiza y responde. El informe vivo de cada pista es la **bitácora de su nota de tareas** en la vault. Si el usuario pregunta «¿cómo va?», leer esas bitácoras y mirar el estado con `ListAgents` / `list_sessions` (ociosa/ocupada), los commits (`git log <base>..<rama>`) y lo sin commitear (`git status`) —o el estado de las copias, sin git—. **No uses `notify_when_idle` en los `SendMessage` a las pistas:** no funciona con las sesiones de Claude Desktop; dependé del aviso de la propia pista o del usuario para saber cuándo terminó.
- **El coordinador es el intermediario:** las pistas no se hablan entre sí. Los pedidos entre pistas y los cambios de contrato se **escriben en la vault** —«Cambios pedidos» y «Avisos» del contrato—; el coordinador los registra ahí (y, si hace falta, deja una entrada «Coordinador: …» en la bitácora de la pista) y recién entonces avisa a las afectadas con `SendMessage` (al nombre/id que lista `ListAgents`), apuntando a lo que deben leer.
- **Dependencias:** retener una pista hasta que esté lo que necesita, o dejarla avanzar con lo que no depende.
- **Decisiones nuevas del usuario a mitad de camino:** anotarlas enseguida en el contrato, la nota de tareas que corresponda y la memoria, y avisar a las pistas afectadas. Si contradice algo ya hecho, decir cuál commit se revierte.
- **Los mensajes a una sesión ocupada quedan en su bandeja** y los recibe en su **próxima ronda de herramientas** (no al final del turno). Sirven para encargos «para después»; para algo urgente, decirlo en el mensaje («no interrumpas X; esto es para cuando lo termines»).
- **Si una sesión se detiene o falla** (error de autenticación, interrupción, se cerró):
  - ver su estado con `ListAgents` / `list_sessions` (ociosa, detenida, archivada o desaparecida) y el avance real en su copia (`git log`/`git status`, o los archivos) y la bitácora;
  - preguntar al usuario si la detuvo él;
  - al retomar: si sigue viva (ociosa o detenida), un `SendMessage` a su `session_id` la continúa con todo su contexto; si está archivada, `unarchive_session` (la app pide aprobación); si se perdió de verdad, un `start_session` nuevo **con `fresh`** (no `fork`, que heredaría la conversación del coordinador, no la de la pista) apuntándola a su worktree y su bitácora. En todos los casos, pedirle primero que **anote lo ya hecho**.
- **Si relevan al coordinador** (esta sesión se saturó de contexto y el usuario abrió otra con `/dev` para retomar): el coordinador nuevo **solo lee** (vault, git, `list_events` del viejo) hasta que el usuario confirme que el viejo cerró; recién entonces avisa **una sola vez** a cada pista. Las pistas aceptan el cambio solo si lo confirma el usuario o el coordinador anterior —si no, deben negarse—. No reutilizar a ciegas: si el usuario pide pistas nuevas, abrir conversaciones nuevas que retomen la rama/copia de cada área. Nunca verificar ni probar en la copia de una pista que sigue trabajando (choques de demonio compartido, p. ej. Gradle, dan fallos falsos): usar una copia aparte o esperar.
- **Para detener una pista:** `stop_session(session_id)` corta su turno en curso (como apretar Stop); la conversación queda abierta y ociosa, y si tenía un mensaje en cola, ese corre después. Para cerrarla del todo y limpiar su worktree, `archive_session` (reversible con `unarchive_session`; la app pide aprobación — **solo con acuerdo explícito del usuario**). `TaskStop` no aplica (es para subagentes propios). Después **cerrar lo que dejó corriendo** (servidores, bases de prueba): identificar cada proceso por su línea de comando antes de cerrarlo y nunca cerrar procesos que no sean de esa pista.

## 6. Revisar cada entrega: no confiar en el reporte

Cuando una pista dice «terminé», antes de decírselo al usuario:

1. **Alcance:** `git diff --name-only <base> <rama>` (o comparar las carpetas, sin git) no toca archivos de otros dueños, y la copia de trabajo quedó limpia.
2. **Pruebas corridas por el coordinador, no las del reporte.** Si la pista está quieta, en su copia; si sigue trabajando, en una copia aparte (`git worktree add --detach`, o una copia nueva sin git).
   - **Compilar antes los paquetes internos.** Si no, las pruebas fallan por dependencias faltantes y parece un error del código.
   - **Compilar desde cero** lo que una prueba de punta a punta va a usar: un resultado viejo compilado engaña.
   - Si una prueba falla solo bajo carga, correrla sola varias veces antes de culpar al código.
3. **Leer las piezas delicadas** (seguridad, plata, borrados, réplica, bloqueos) y **cruzarlas con lo de las otras pistas**. Los errores más caros aparecen en la juntura: un valor nuevo que el otro lado rechaza, un texto que otro módulo compara, dos que escriben el mismo dato.
4. **Contar honesto:**
   - qué se probó y con qué números;
   - qué no se probó;
   - qué encontraste;
   - qué decisiones tomó la pista por su cuenta, que el usuario debe confirmar.
5. **Hallazgos:** las correcciones chicas que el usuario ya aprobó en espíritu, mandarlas (el pedido anotado en la bitácora de la pista o en «Cambios pedidos», y un `SendMessage` que lo apunte); las que cambian el producto, preguntarlas primero.

Al terminar la revisión, borrar las copias de verificación y los procesos que hayas dejado.

## 7. Integrar y probar de punta a punta

1. **Fusionar las ramas de las pistas** en la base, en el orden del plan (primero el dueño del contrato). Sin git, incorporar a mano cada copia a la copia principal, en ese orden. Regenerar lo que dependa de todas juntas (esquemas generados, catálogos) y correr **todas** las pruebas.
2. **Antes de cada ronda nueva,** que cada pista fusione la base (o reciba la copia principal al día), así nadie trabaja sobre un contrato viejo.
3. **La prueba de punta a punta la conduce una sola sesión** (la que conoce los equipos físicos), para no chocar en puertos ni dispositivos.
   - El coordinador escribe el **guion** en la carpeta de coordinación: preparación, pasos numerados, limpieza, y una sección de resultado donde cada paso queda ✅, ❌ (con a qué pista le toca) o ⏭.
   - Pedir que anote **cada paso apenas lo termina**, no al final.
4. **Ronda de arreglos:** con los ❌ del guion más lo que el usuario fue encolando, una tanda por pista en paralelo (un `SendMessage` a cada una). Después, una prueba corta solo de lo que cambió.

## 8. Cerrar

- **La nota principal** con la tabla de estado al día, y las notas viejas con su aviso.
- **Una nota «Estado actual»** en la vault, reescrita al cerrar cada ronda (producción, rama/copia base, qué falta, decisiones abiertas, notas viejas): es lo que permite retomar —o relevar al coordinador— sin releer todas las bitácoras.
- **Memoria:** el rumbo, dónde están el plan y la rama/copia base, y las trampas aprendidas que no estén en el código.
- **Lo que sigue** (despliegue, decisiones pendientes, fases siguientes) se le propone al usuario. **Nada se sube ni se despliega sin su orden explícita.**
- **Credenciales y secretos:** nunca en el chat, la vault ni git. Van en una carpeta local fuera de los repos (por ejemplo `.secrets/` con una plantilla `.example`) y a las pistas solo se les pasa la ruta y las reglas de uso.

## Cómo hablarle al usuario

Él sigue el trabajo desde aquí:
- respuestas cortas, con el estado de cada pista referida por su nombre/id (el que lista `ListAgents`);
- números concretos de pruebas;
- qué falta.

Cuando pregunte «¿cómo va?», mirar el estado real (las bitácoras en la vault + `ListAgents` + commits/archivos); no repetir lo que dijo el último mensaje de la pista. Si una pista está lenta, explicar por qué (pruebas pesadas, más tareas, el modelo elegido) y qué se puede hacer.

## Modo CLI (`claude --bg`) — equivalente de §4 y §5

En el CLI las pistas son **sesiones en segundo plano** del propio `claude`: sesiones peer completas (no subagentes `Agent`, sin fan-out), visibles con `claude attach`, en el mismo bus que `ListAgents`/`SendMessage`. Todo lo demás (contrato, dueños, vault/bitácora, verificación §6, integración §7, cierre §8) es idéntico a Desktop. Lo que cambia:

**Lanzar (reemplaza §4.2):**
1. **Herramientas:** `ListAgents` ya está; cargá `SendMessage` con `ToolSearch` (`select:SendMessage`). Las sesiones se manejan por shell (`claude …`), no por un MCP.
2. **Lanzá cada pista desde una carpeta ya confiada** (p. ej. el home) **con `--add-dir "<carpeta del repo>"`**, una por área, en el mismo turno las independientes:
   `claude --bg --name pista-<area> --model <modelo> --add-dir "<repo>" "esperá el brief"`
   Devuelve un **id corto**; anotalo. El prompt posicional **no arranca la pista** (queda ociosa), así que es solo un placeholder.
3. **Entregá el brief por `SendMessage`** (no por el prompt posicional): un mensaje a `pista-<area>` con el brief completo. En el brief, **la pista crea su propio worktree** (`git worktree add ../<proyecto>-<area> -b <rama> <base>`) y entra ahí; al ser **dueña** del worktree, edita y commitea sin trabarse. Si el coordinador le pasa un worktree ya hecho, la pista se **niega** a commitear pidiendo confirmación del usuario (guardarraíl anti permission-laundering) — por eso la pista lo crea.
4. Dirigí las pistas **por nombre** (`pista-<area>`). El id corto del CLI (para `attach/logs/stop/rm`) es **distinto** del ref de `ListAgents`; para dirigir, el nombre alcanza.

**Ver y dirigir (reemplaza §4.3 y las mecánicas de §5):**
- **Estado:** `claude agents --json` o `ListAgents` (ociosa/ocupada).
- **Ver en vivo:** una terminal con `claude attach <nombre|id>`; un panel por pista (p. ej. Windows Terminal `wt … split-pane`) da el tablero tipo Desktop. Espiar sin entrar: `claude logs <id>`.
- **Dirigir:** `SendMessage` al nombre. El **idle-wake funciona**: el aviso de una pista despierta al coordinador 100 % ocioso (modelo reactivo, igual que en Desktop; `notify_when_idle` no hace falta).
- **Frenar:** `claude stop <id-corto>` (por **id**, no por nombre; conserva la conversación). Una pista detenida **sale del bus** y no recibe `SendMessage` hasta retomarla.
- **Retomar:** `claude --bg --resume <UUID-completo>` **desde carpeta confiada** (`--resume` re-chequea confianza contra el cwd). Con el **id corto** arranca una **copia**; con el **UUID completo** (de `claude agents --json`) despierta la **misma** sesión y restaura `--name/--add-dir/--model`. El contexto sobrevive al stop/resume.
- **Cerrar y limpiar su worktree:** `claude rm <id>` (solo con acuerdo explícito del usuario).

**Trampas del CLI (validadas):**
- **Confianza interactiva:** un worktree nuevo no es de confianza y `--bg` no puede mostrar el diálogo; por eso se lanza desde carpeta confiada + `--add-dir` y la pista crea su worktree (crear + `cd` **no** dispara el diálogo). Pre-confiar editando `~/.claude.json` no se honra (y el auto-mode lo bloquea como "Self-Modification").
- **Toolchain / PATH:** ver el preflight del §0.
- **Hooks (husky, etc.):** con dependencias instaladas **pasan**; usá `git commit --no-verify` solo si el worktree no tiene `node_modules`. pnpm usa store con hardlinks, así que N worktrees cuestan poco disco (borralos al terminar la ronda).
- **Background service compartido:** un servicio atiende las sesiones `--bg`; **nunca lo reinicies** (puede tumbar otras sesiones, incluso de Desktop). Frená/cerrá solo por pista con `stop`/`rm`.

**Tabla de equivalencias Desktop ↔ CLI**

| Acción | Desktop | CLI |
|---|---|---|
| Abrir pista | `start_session` (`fresh`, `model`, `prompt`=brief) | `claude --bg --name --model --add-dir` desde carpeta confiada; **brief por `SendMessage`** |
| Dirigir | `SendMessage` | `SendMessage` (igual) |
| Estado | `list_sessions` | `claude agents --json` / `ListAgents` |
| Ver en vivo | la ventana de la pista | `claude attach <nombre>` (`logs` para espiar) |
| Frenar | `stop_session` | `claude stop <id-corto>` |
| Cerrar / limpiar | `archive_session` | `claude rm <id>` |
| Retomar | `SendMessage` al `session_id` | `claude --bg --resume <UUID-completo>` desde carpeta confiada |
| Worktree de la pista | la crea la pista desde el brief | igual (la crea la pista; es dueña) |

Validado end-to-end el 2026-11-03 (abrir, dirigir, worktree propio, `install`+`typecheck`+`test`, integración por merge, stop/resume con contexto, idle-wake).
