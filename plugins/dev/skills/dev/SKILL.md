---
name: dev
description: "Coordina un desarrollo grande con varias sesiones de Claude en paralelo: esta sesión (Opus o Fable) entrevista al usuario, planifica, hace la base común, y reparte el trabajo en «pistas» —conversaciones de Claude anidadas que el propio coordinador abre, cada una con el modelo que elija el usuario (por ejemplo Sonnet)—, las dirige por mensajes, revisa y verifica por su cuenta cada entrega, integra, conduce las pruebas de punta a punta y manda las correcciones. Úsala siempre que el usuario escriba /dev, o pida planificar y repartir un cambio entre varias instancias, conversaciones o pistas de Claude, o pida que esta conversación «lleve el control» o coordine a otras, aunque no diga «skill». No es para un cambio chico que cabe en una sola sesión."
---

# /dev — coordinar pistas en paralelo

Esta sesión es el **coordinador**: el gestor principal del desarrollo. No escribe el código de las pistas: entrevista, planifica, decide con el usuario, reparte, revisa, verifica, integra y documenta. Es el único que ve el cuadro completo.

Las **pistas no son subagentes `Agent`:** son **conversaciones de Claude anidadas que el propio coordinador abre** (Claude Desktop permite que una conversación abra otras), una por área del repo. **El usuario no las crea ni escribe en ellas.** Aparecen como *peer sessions* en `ListAgents` y el coordinador les habla con `SendMessage`. Funciona porque el modelo caro piensa y revisa, el barato ejecuta, y nadie le pisa los archivos a otro.

El coordinador es **reactivo**: no deja tareas en segundo plano esperando respuesta. Reparte, y su turno termina. Cuando una pista le manda un mensaje al cerrar su labor, el coordinador lo analiza y contesta. **No sondea.** Los `SendMessage` entre sesiones son el **empujón en vivo** —«leé esto», «arrancá», «arreglá aquello»—; el registro durable de todo (informes, pedidos, decisiones) vive en la vault, no en los mensajes.

**El coordinador se queda con el modelo con el que arrancó.** Una sesión no puede cambiar su propio modelo a mitad de camino (tendría que releer todo el contexto). Si el usuario quiere orquestar con otro modelo, abre una sesión nueva con ese modelo e invoca `/dev` ahí. El modelo se elige **por pista**, nunca para el coordinador en marcha.

Invocar `/dev` es el pedido explícito del usuario de delegar, aunque la configuración general desaconseje delegar por defecto. No es para un cambio chico que cabe en una sola sesión: usala cuando el desarrollo tenga varias áreas que convenga llevar en paralelo con un contrato compartido entre ellas.

**Git: recomendado, no obligatorio.** El jefe no siempre usa git, así que la skill no depende 100% de él:
- **Con git (recomendado):** cada pista trabaja en su **worktree** y rama; la integración es por *merge*.
- **Sin git:** cada pista trabaja en **su propia copia-carpeta** del proyecto (una carpeta aparte); el coordinador unifica los cambios a mano en una copia principal.
Si el proyecto no está en git, ofrecer `git init`; si el usuario no quiere, usar el modo sin-git. Todo lo demás (dueños, contrato, coordinación, verificación) sigue igual.

**La vault es el cerebro y la memoria del proyecto.** Toda la coordinación durable vive ahí: el plan, el contrato, las notas de tareas —cada una con su **bitácora**, que es el informe vivo de esa pista— y los guiones de prueba. Es una carpeta **compartida, por ruta absoluta, fuera de las copias de trabajo**, que todas las sesiones alcanzan igual con o sin git: la **vault de Obsidian** si existe, o si no una carpeta dedicada al lado del repo (`../<proyecto>-coordinacion/`). **Nunca dentro de los worktrees/copias ni en `docs/` del repo:** un archivo ahí solo lo ve la pista que lo tenga commiteado en su rama, y el coordinador en su copia no lo vería. A cada pista se le pasa la **ruta absoluta** de las notas que necesita. **No hay carpeta de informes aparte:** cada pista reporta en la bitácora de su propia nota de tareas, y los pedidos entre pistas van a «Cambios pedidos»/«Avisos» del contrato.

Plantillas de notas, mensajes y guiones: `references/plantillas.md`. Leerlo antes de escribir cada pieza.

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
- **qué modelo corre cada pista** — el coordinador recomienda uno (por defecto Sonnet; no más capaz ni caro que lo que haga falta, y no por encima del coordinador); el usuario lo elige y el **coordinador lo fija con `model` en el `start_session`** (o con `set_session_model` después). Debe ser igual o más barato que el del coordinador; **si se omite, la pista hereda el modelo del coordinador —caro—, así que pasalo siempre**;
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

Las pistas son **conversaciones anidadas que abre el propio coordinador con `start_session`** (Claude Desktop lo permite), no subagentes. El usuario no las abre ni escribe en ellas. El flujo:

1. **Cargar las herramientas diferidas** en una sola `ToolSearch`: `select:mcp__ccd_session__start_session,SendMessage,mcp__ccd_session_mgmt__set_session_model,mcp__ccd_session_mgmt__list_sessions,mcp__ccd_session_mgmt__stop_session,mcp__ccd_session_mgmt__archive_session`. `ListAgents` ya está disponible. (`TaskStop` es para subagentes propios; a las pistas no se les aplica.)
2. **Abrir una pista por área con `start_session`** —las independientes en el mismo turno, para que arranquen en paralelo—. Una línea en negrita por pista antes de las llamadas. Parámetros:
   - `initiation: "user_asked"` (abrir pistas es parte de lo que el usuario pidió al invocar `/dev`);
   - `title` descriptivo («Pista WEB: nube por sucursal») y `name` corto (`pista-web`);
   - `context: "fresh"` (no hereda esta conversación) + `background` con el contexto general (**obligatorio con `fresh`, mínimo 80 caracteres**);
   - **`model` (y `effort`) explícitos**, el elegido para la pista. **Pasalo siempre:** si lo omitís, la pista hereda el modelo del coordinador —caro—. Debe ser igual o más barato que el del coordinador;
   - `use_worktree: false` (cada pista crea su propio worktree desde su brief, para controlar el nombre de rama y la propiedad de archivos);
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

- **Reactivo, no sondear.** El turno del coordinador termina después de repartir. Los avisos llegan solos: el `SendMessage` de una pista aparece como `<cross-session-message>`, y al cerrar un turno la app inyecta los primeros ~400 caracteres de su informe (y continúa el turno del coordinador con un `<side-sessions-event>` si está ocioso). El coordinador los analiza y responde. El informe vivo de cada pista es la **bitácora de su nota de tareas** en la vault. Si el usuario pregunta «¿cómo va?», leer esas bitácoras y mirar el estado con `ListAgents` / `list_sessions` (ociosa/ocupada), los commits (`git log <base>..<rama>`) y lo sin commitear (`git status`) —o el estado de las copias, sin git—.
- **El coordinador es el intermediario:** las pistas no se hablan entre sí. Los pedidos entre pistas y los cambios de contrato se **escriben en la vault** —«Cambios pedidos» y «Avisos» del contrato—; el coordinador los registra ahí (y, si hace falta, deja una entrada «Coordinador: …» en la bitácora de la pista) y recién entonces avisa a las afectadas con `SendMessage` (al nombre/id que lista `ListAgents`), apuntando a lo que deben leer.
- **Dependencias:** retener una pista hasta que esté lo que necesita, o dejarla avanzar con lo que no depende.
- **Decisiones nuevas del usuario a mitad de camino:** anotarlas enseguida en el contrato, la nota de tareas que corresponda y la memoria, y avisar a las pistas afectadas. Si contradice algo ya hecho, decir cuál commit se revierte.
- **Los mensajes a una sesión ocupada quedan en su bandeja** y los recibe en su **próxima ronda de herramientas** (no al final del turno). Sirven para encargos «para después»; para algo urgente, decirlo en el mensaje («no interrumpas X; esto es para cuando lo termines»).
- **Si una sesión se detiene o falla** (error de autenticación, interrupción, se cerró):
  - ver su estado con `ListAgents` / `list_sessions` (ociosa, detenida, archivada o desaparecida) y el avance real en su copia (`git log`/`git status`, o los archivos) y la bitácora;
  - preguntar al usuario si la detuvo él;
  - al retomar: si sigue viva (ociosa o detenida), un `SendMessage` a su `session_id` la continúa con todo su contexto; si está archivada, `unarchive_session` (la app pide aprobación); si se perdió de verdad, un `start_session` nuevo **con `fresh`** (no `fork`, que heredaría la conversación del coordinador, no la de la pista) apuntándola a su worktree y su bitácora. En todos los casos, pedirle primero que **anote lo ya hecho**.
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
- **Memoria:** el rumbo, dónde están el plan y la rama/copia base, y las trampas aprendidas que no estén en el código.
- **Lo que sigue** (despliegue, decisiones pendientes, fases siguientes) se le propone al usuario. **Nada se sube ni se despliega sin su orden explícita.**
- **Credenciales y secretos:** nunca en el chat, la vault ni git. Van en una carpeta local fuera de los repos (por ejemplo `.secrets/` con una plantilla `.example`) y a las pistas solo se les pasa la ruta y las reglas de uso.

## Cómo hablarle al usuario

Él sigue el trabajo desde aquí:
- respuestas cortas, con el estado de cada pista referida por su nombre/id (el que lista `ListAgents`);
- números concretos de pruebas;
- qué falta.

Cuando pregunte «¿cómo va?», mirar el estado real (las bitácoras en la vault + `ListAgents` + commits/archivos); no repetir lo que dijo el último mensaje de la pista. Si una pista está lenta, explicar por qué (pruebas pesadas, más tareas, el modelo elegido) y qué se puede hacer.
