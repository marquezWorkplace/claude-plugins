# clean-smart-tv

Skill para limpiar y optimizar un **Smart TV Android** (Android TV, Google TV) por ADB en 5 fases: conexión, inventario, instalación de **Projectivy Launcher** con la configuración probada, lista de candidatos de limpieza, y ejecución con autorización explícita del usuario.

## Qué hace

1. **ADB** — conecta a la IP del TV, maneja el popup de autorización ADB por red.
2. **Inventario** — paquetes instalados, RAM libre, servicios en background, conexiones de red, launcher actual, identidad del ODM (Skyworth, Hisense, TCL, MediaTek…) a partir de `getprop`.
3. **Projectivy Launcher** — descarga la versión gratis desde el GitHub oficial del developer (`spocky/miproja1`), **TV Bro** (navegador, variante `geckoExcluded` para TVs de 1 GB) y **Material Files** (F-Droid). Instala, fija Projectivy como home, deshabilita el Google TV Launcher, aplica las 4 configs probadas (tamaño de tarjeta 150%, categoría "Aplicaciones de TV" en L, fila "Entradas" oculta si no usa HDMI, screensaver OFF).
4. **Candidatos** — tabla clasificada (OEM bloat Skyworth/Coocaa/CLTV, adware vector PlayAutoInstallStub, telemetría, streaming preinstalado, accesorios inútiles en TV). Pregunta al usuario por antena broadcast, streaming que usa, "Find my remote" y agresividad (`uninstall` vs `disable-user`).
5. **Ejecución** — con el plan aprobado, loguea cada comando (y su revert), mide delta de RAM antes/después, monitorea Wi-Fi tras cada tanda.

## Quién sacó qué del Daewoo original

Lecciones encoded en la skill (aprendidas en carne propia):

- **Nunca** quitar `com.google.android.safetycenter.resources` en Android 14 → soft-reboot de `system_server` + pérdida de Wi-Fi.
- `pm uninstall --user 0` **no mata** apps con flag `PERSISTENT` → usar `pm disable-user`.
- `pm disable` sobre priv-app del sistema devuelve `SecurityException` → caer a la UI de Projectivy (Editar categorías → Gestionar aplicaciones → toggle OFF).
- `adb install -g` falla silencioso en Android 14 por permisos runtime → usar solo `-r`.
- Deshabilitar **launcherx con `pm disable-user`** aunque Projectivy sea el role holder, si no el botón HOME del remoto sigue yendo al launcher viejo.
- Panel lateral de Projectivy absorbe `KEYCODE_DPAD_DOWN` inconsistentemente → `KEYCODE_PAGE_DOWN` o tap preciso en toggles por coordenadas.
- **Siempre preguntar** por apps "del usuario" antes de empezar (ej.: CamWay era la app crítica del TV original).

## Prerrequisitos

- Windows con `adb.exe` en `%LOCALAPPDATA%\Android\Sdk\platform-tools\` (o instalado via `winget install Google.PlatformTools`).
- TV encendido, en el mismo Wi-Fi que el PC, con **Depuración ADB por red** activada en Opciones de desarrollador.
- Saber la IP del TV (Ajustes → Red → Estado).

## Cómo usarla

Decile a Claude Code una de estas (o algo parecido):

- `/clean-smart-tv`
- "limpiá el TV de la sala"
- "sacale el bloatware a este smart TV"
- "cambiale el launcher a Projectivy al TV"
- "optimizá la RAM del Google TV"

## Alcance

Sólo **Android TV / Google TV**. NO sirve para Tizen (Samsung), webOS (LG) ni Roku: esos no tienen ADB abierto.
