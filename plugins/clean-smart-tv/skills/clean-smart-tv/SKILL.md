---
name: clean-smart-tv
description: "Limpia un Smart TV Android (Android TV, Google TV) por ADB: inventario del software, detección de bloatware/adware/telemetría OEM, instalación del launcher Projectivy con la configuración probada en un Daewoo AI Smart TV (Skyworth ODM, Android 14), y lista de candidatos de limpieza esperando autorización del usuario antes de ejecutar. Usala siempre que el usuario escriba /CleanSmartTV o /clean-smart-tv, o pida limpiar/sanear/optimizar/«debloatear» cualquier televisor inteligente, cambiar el launcher a Projectivy, bajar el consumo de RAM de un TV, sacarle el adware o la telemetría a un TV Android, o pida auditar las apps de un TV conectado por red. No es para teclas lentas o un TV que no responde (eso es soporte de hardware), ni para TVs que no corren Android (Tizen, webOS, Roku)."
---

# /CleanSmartTV — limpieza y launcher nuevo en un Smart TV Android

Esta skill cubre el flujo completo que se usó para dejar operativo un Daewoo AI Smart TV (modelo `SW14_Daewoo`, ODM Skyworth, Android 14, 1 GB RAM) y lo generaliza para cualquier Android TV / Google TV accesible por red local.

El TV Daewoo YA está limpio. Esta skill es para **otros** TVs. Si el usuario pide limpiar "el TV de siempre", "el Daewoo" o `172.16.10.122`, contestar que ya está hecho y preguntar cuál TV es el nuevo.

El flujo es, en este orden exacto:

1. **ADB** — confirmar conexión al TV, autorizar si hace falta.
2. **Inventario** — listar paquetes, servicios, RAM, red; identificar marca / ODM / Android.
3. **Projectivy** — instalar + fijar como home + aplicar la config del Daewoo, **sin pedir permiso para cada paso**: estos cambios son seguros y reversibles.
4. **Candidatos de limpieza** — clasificar y presentar la lista. **Detenerse acá y esperar autorización explícita antes de desinstalar nada.**
5. **Ejecución** — con la lista aprobada, desinstalar/desactivar y medir RAM antes/después.

## Antes de empezar

Lo único que necesita el usuario:
- El TV encendido y conectado al mismo Wi-Fi que esta PC.
- Que haya activado una vez **Depuración por ADB en red** en Ajustes del desarrollador (requiere activar opciones del desarrollador tocando varias veces la versión de Android en Ajustes).
- La IP del TV (se ve en Ajustes → Red → Estado), o que el usuario la averigüe si no la sabe.

`adb.exe` normalmente está en `%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe`. Si no está, decirle al usuario que instale Android Platform Tools de Google (o pedir permiso para hacerlo via `winget install Google.PlatformTools`).

## Fase 1 — ADB

Pedir la IP del TV si el usuario no la dio. Luego:

```powershell
$ADB = "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe"
& $ADB connect <TV_IP>:5555
& $ADB devices -l
```

Si el TV aparece como `unauthorized`, **avisar al usuario que mire la pantalla del TV y acepte el popup "¿Permitir depuración USB desde este equipo?"**. Es un popup de una vez; una vez aceptado con "Permitir siempre", no vuelve a aparecer.

Confirmar que la conexión funciona con un comando trivial:
```powershell
& $ADB -s <TV_IP>:5555 shell "getprop ro.product.brand; getprop ro.product.model; getprop ro.build.version.release"
```

Si el TV se cae de la red durante el proceso (dispositivo `offline`), revisar la «Sección de red» de `references/safety-rules.md`. Casi siempre es un soft-reboot inofensivo del `system_server` por haber tocado algo del sistema; el Wi-Fi vuelve solo o con reconexión manual del usuario.

## Fase 2 — Inventario y clasificación

**Qué extraer** (ver `references/inventory-commands.md` para el set completo de comandos):
- Lista de paquetes (`pm list packages -f`), desactivados (`-d`), de usuario (`-3`).
- RAM total/libre (`/proc/meminfo`), top PSS por proceso (`dumpsys meminfo`).
- Servicios en background (`dumpsys activity services`).
- Launcher actual (`cmd package resolve-activity -c android.intent.category.HOME`).
- Build fingerprint y OEM (`ro.product.brand`, `ro.product.manufacturer`, `ro.oem.key1`, `ro.hardware`).
- Conexiones de red salientes (`ss -tnp`) — útil para detectar telemetría activa.

**Guardar la inventario** en el directorio de scratchpad en un archivo `inventory.txt` con fecha; servirá de evidencia de "estado antes" y de referencia para ver qué reinstalar si algo se rompe.

**Clasificar** los paquetes contra los patrones de `references/classification-patterns.md`. Grosso modo salen 5 cajones:

| Cajón | Qué contiene | Default |
|---|---|---|
| **Core sistema** | APEX, overlays, framework, Google GMS, keyboards, WebView, Bluetooth, mdnsoffload, drivers de chipset | **Nunca tocar** |
| **HDMI / inputs** | `com.droidlogic.tvinput`, `com.google.android.tv.inputplayer`, `com.*.inputsource` | Mantener (si usa HDMI) |
| **Antena DVB/ISDB** | `com.droidlogic.android.tv`, `com.droidlogic.dtvkit.*`, `com.cltv.*`, `com.mirakulo.*` (Ginga) | Depende de si usa antena — preguntar |
| **Streaming preinstalado** | Netflix, Prime, YouTube, Disney+, Pluto, Rakuten, Tubi, Xumo | Depende del uso — preguntar |
| **OEM bloat / adware / telemetría** | ver `classification-patterns.md` por OEM (Skyworth/Coocaa/CLTV/MediaTek demo/PlayAutoInstallStub/fabricante local) | Candidatos a quitar |

El usuario también puede tener **apps propias protegidas** (en el Daewoo fue CamWay, su sistema de cámaras). **Siempre preguntar antes de tocar** cualquier app con prefijo de dominio ajeno a Google/Android/OEM detectado: suele ser software del usuario. Si en la Fase 1 el usuario no mencionó cuáles son "suyas", pedírselas antes de la Fase 4.

## Fase 3 — Projectivy (instalación + configuración)

Ver `references/projectivy-setup.md` para URLs oficiales, comandos de instalación y navegación UI paso a paso.

Resumen de lo que hace esta fase, en orden:

1. **Descargar** los 3 APKs desde fuentes oficiales (GitHub del developer para Projectivy y TV Bro, F-Droid para Material Files). Guardar SHA256 para log.
2. **Instalar** con `adb install -r` (sin `-g` — falla en Android 14 por permisos runtime).
3. **Fijar Projectivy como home**:
   ```
   cmd package set-home-activity com.spocky.projengmenu/com.spocky.projengmenu.ui.home.MainActivity
   pm disable-user --user 0 com.google.android.apps.tv.launcherx
   ```
4. **Avisar al usuario** que complete el onboarding de Projectivy con el control remoto (4-5 pantallas de bienvenida + conceder permisos de notificación y ubicación cuando los pida). **Esperar confirmación** antes de seguir.
5. **Aplicar config** (via `am start -a tv.projectivy.SETTINGS` + keyevents DPAD + swipes):
   - Apariencia → Tarjetas → **Tamaño 150%** (slider al final, aprox 8 x DPAD\\_RIGHT desde 50%).
   - Editar categorías → **Aplicaciones de TV** → Tamaño **L**.
   - Editar categorías → **Entradas** → Visible **OFF** (solo si el usuario no usa inputs HDMI; preguntar antes).
   - Deshabilitar screensaver: `settings put secure screensaver_enabled 0`.

La config UI de Projectivy es frágil vía ADB porque el panel lateral absorbe DPAD events de forma inconsistente. Si algo no toma al primer intento, usar **tap de coordenadas precisas en los toggles** (ver `projectivy-setup.md` seccion "trucos de navegación"). Hacer screenshot después de cada paso para verificar.

**Importante**: mientras el TV está en uso real (p.ej. mostrando cámaras), lanzar `tv.projectivy.SETTINGS` abre un **panel lateral superpuesto** sin cerrar la app en primer plano. Aprovechar eso en vez de mandar HOME, que sí interrumpiría.

## Fase 4 — Candidatos y autorización

Esta es la fase que requiere **parada obligatoria**. Nunca borrar sin autorización explícita del usuario para cada grupo.

Presentar al usuario en una tabla:

```
| Paquete | Qué es | RAM que libera | Riesgo | Mi recomendación |
```

Agrupar por cajón (OEM bloat / telemetría / streaming no usado / accesorios inservibles en TV).

Hacer **al menos estas 4 preguntas** con `AskUserQuestion` antes de ejecutar:
1. ¿Usa antena TV por aire (DVB/ISDB/ATSC)? → define si mantener LiveTV / DtvKit / cltv.mal / AstroTV.
2. ¿Qué apps de streaming conserva? (multi-select: Netflix / Prime / YouTube / ninguna / otras) → define si quitar com.netflix.ninja / com.amazon.amazonvideo.livingroom / com.google.android.youtube.tv.
3. ¿Mantener "Find my remote" (buzzer del control), TalkBack (lector de pantalla), proveedores Calendar/Contactos?
4. ¿Nivel: `pm uninstall --user 0` (más agresivo, más reversible por `pm install-existing`) o `pm disable-user --user 0` (más conservador)?

Esperar las respuestas. **No ejecutar hasta tenerlas todas.**

## Fase 5 — Ejecución

Reglas duras (ver `references/safety-rules.md` para el detalle y el porqué):

- **Nunca tocar** paquetes `com.*.overlay.*`, `com.google.android.safetycenter.resources`, nada en `/apex/`, `com.android.systemui`, `com.android.vending`, `com.google.android.gms`, `com.google.android.webview`, `com.android.networkstack`, drivers de chipset (`com.droidlogic` base).
- `pm uninstall --user 0` no funciona en apps marcadas `persistent=true` (el proceso sigue vivo hasta el próximo reboot y muchas veces vuelve). Para esas, usar `pm disable-user --user 0`.
- Algunas apps privilegiadas del sistema rechazan `pm disable` con `SecurityException` (shell no puede). Para esas, solo la UI de Projectivo (Editar categorías → Gestionar aplicaciones → toggle OFF) las esconde del launcher.
- **Loguear cada acción** en `scratchpad/clean-smart-tv-<fecha>/uninstalled.txt` con el comando exacto para revertir.
- **Medir RAM antes y después** (`MemAvailable` de `/proc/meminfo`). Reportar el delta al usuario al final.
- **Monitorear Wi-Fi** después de cada tanda de 5-10 cambios (`ping` al TV). Si se cae, parar y esperar a que vuelva; nunca encadenar más cambios sobre un TV offline.

Al terminar:
- Resumen al usuario: cuántos paquetes fuera, RAM liberada, launcher activo, apps nuevas instaladas.
- Decir dónde quedó el log y cómo revertir cualquiera.
- Sugerir reboot para que los procesos persistentes deshabilitados terminen de morir y la RAM baje a su piso real.

## Patrones de interacción con el TV

- **Prefer usar `cmd package` sobre `pm`** cuando ambos funcionen; `cmd package` da errores más claros en Android 14.
- **Tomar screenshot después de cada cambio UI** (`screencap -p /sdcard/s.png` + `adb pull`). Mandarlo con `SendUserFile` cuando el usuario necesite ver lo que pasó; usar `Read` para leerlo nosotros mismos antes de seguir, especialmente si la navegación UI se complica.
- **Si hay que apagar el launcher viejo del sistema (`com.google.android.apps.tv.launcherx`)**, hacerlo DESPUÉS de instalar Projectivy y fijarlo como home; si no, el TV queda sin launcher y se traba.
- **Nunca** hacer `reboot` del TV sin avisar al usuario; puede cortarle lo que esté haciendo (mirando una app, en una llamada, etc.).

## Sobre el idioma

Responder al usuario en el idioma que el usuario esté usando. El Daewoo original y la interacción original fueron en español; la skill está escrita en español porque el usuario escribe en español. Si un próximo usuario escribe en inglés o portugués, cambiar.
