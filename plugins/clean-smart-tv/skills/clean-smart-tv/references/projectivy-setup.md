# Projectivy: instalación y configuración probada

## APKs

Siempre desde fuentes oficiales del developer o F-Droid. Verificar sha256 al descargar.

### Projectivy Launcher (versión gratis)
- Release API: `https://api.github.com/repos/spocky/miproja1/releases/latest`
- Pattern: `ProjectivyLauncher-<ver>-c<n>-xda-release.apk`
- \~11 MB
- `com.spocky.projengmenu`

### TV Bro (navegador D-pad friendly)
- Release API: `https://api.github.com/repos/truefedex/tv-bro/releases/latest`
- **Usar la variante `geckoExcluded`** (6.5 MB) — usa WebView del sistema. La `geckoIncluded` pesa 150 MB (trae Gecko entero) y es overkill para un TV de 1 GB.
- `com.phlox.tvwebbrowser`

### Material Files (file manager)
- F-Droid info: `https://f-droid.org/api/v1/packages/me.zhanghai.android.files`
- APK URL: `https://f-droid.org/repo/me.zhanghai.android.files_<versionCode>.apk` (el versionCode sale del JSON de la API)
- \~5-11 MB
- `me.zhanghai.android.files`

### WebFetch desde la skill
```
WebFetch("https://api.github.com/repos/spocky/miproja1/releases/latest", "return tag_name, assets[].name + browser_download_url")
WebFetch("https://api.github.com/repos/truefedex/tv-bro/releases/latest", "return tag_name, assets[].name + browser_download_url")
WebFetch("https://f-droid.org/api/v1/packages/me.zhanghai.android.files", "return suggestedVersionCode")
```

## Instalación

```powershell
$dir = "<scratchpad>\apks"
New-Item -ItemType Directory -Force -Path $dir | Out-Null

# Descargar los 3
Invoke-WebRequest -Uri "<URL Projectivy>" -OutFile "$dir\projectivy.apk" -UseBasicParsing
Invoke-WebRequest -Uri "<URL TV Bro geckoExcluded>" -OutFile "$dir\tvbro.apk" -UseBasicParsing
Invoke-WebRequest -Uri "https://f-droid.org/repo/me.zhanghai.android.files_<code>.apk" -OutFile "$dir\materialfiles.apk" -UseBasicParsing

# Loguear hashes
Get-FileHash "$dir\*.apk" -Algorithm SHA256

# Instalar — SIN -g (falla en Android 14 por permisos runtime). Usar solo -r.
& $ADB -s $d install -r "$dir\projectivy.apk"
& $ADB -s $d install -r "$dir\tvbro.apk"
& $ADB -s $d install -r "$dir\materialfiles.apk"
```

Si una instalación falla silenciosamente, re-intentar sin `-g`. Si sigue fallando, verificar:
- `df -h /data` (espacio)
- `getprop ro.product.cpu.abilist` (ABI compatible con el APK)
- `getprop ro.build.version.sdk` (minSDK del APK)

## Fijar Projectivy como home

Dos pasos: primero asignar el rol, después matar al launcher viejo.

```powershell
# Asignar rol HOME a Projectivy
& $ADB -s $d shell "cmd package set-home-activity com.spocky.projengmenu/com.spocky.projengmenu.ui.home.MainActivity"
# Verificar
& $ADB -s $d shell "cmd role get-role-holders android.app.role.HOME --user 0"
# Debe retornar: com.spocky.projengmenu

# Deshabilitar el Google TV Launcher (si está). Sin esto el botón HOME del control sigue yendo al launcher viejo porque el framework de Google TV tiene un atajo cableado.
& $ADB -s $d shell "pm disable-user --user 0 com.google.android.apps.tv.launcherx"
```

**Nota**: en algunos Google TV el nombre es `com.google.android.tvlauncher` en vez de `com.google.android.apps.tv.launcherx`. Buscar con:
```
pm list packages | grep -iE 'launcherx|tvlauncher'
```

### Si el usuario necesita volver atrás
```
pm enable com.google.android.apps.tv.launcherx
cmd package set-home-activity com.google.android.apps.tv.launcherx/com.google.android.apps.tv.launcherx.home.HomeActivity
```

## Onboarding (el usuario con el remoto)

Después de instalar y fijar, al apretar HOME Projectivy entra en `OnboardingActivity`. Son 4-5 pantallas:

1. Welcome / idioma (DPAD\\_CENTER).
2. Overview de features (DPAD\\_CENTER).
3. Permiso de notificaciones → abre Ajustes de Android, el usuario tiene que activar Projectivy en la lista. Volver con BACK.
4. Permiso de ubicación (opcional, para wallpaper dinámico por hora/clima).
5. Ignorar optimización de batería (recomendado en TV para que no mate servicios).

**El usuario tiene que hacer esto con el control físico — no se puede automatizar bien vía ADB porque son dialogos del sistema.** Esperar confirmación del usuario antes de aplicar config.

## Configuración probada (del Daewoo)

Cuatro cambios, en este orden. Entre cada uno, screenshot para verificar.

### Abrir el panel lateral de ajustes
```
am start -a tv.projectivy.SETTINGS
```
Esto abre un **panel lateral superpuesto**. **No cierra la app que el usuario tenía abierta** (ej.: CamWay seguirá visible abajo). Perfecto si el TV está en uso real.

### 1. Tamaño global de tarjetas 150%

Navegación:
- Side panel abierto → DOWN×3 CENTER (va a "Ajustes de Projectivy").
- DOWN×1 CENTER (Apariencia).
- DOWN×1 CENTER (Tarjetas).
- DOWN×2 llega al slider "Tamaño de tarjeta".
- RIGHT×8 lleva al 150%.
- BACK×3 para cerrar.

```powershell
& $ADB -s $d shell "am start -a tv.projectivy.SETTINGS"
Start-Sleep 2
& $ADB -s $d shell "input keyevent KEYCODE_DPAD_DOWN KEYCODE_DPAD_DOWN KEYCODE_DPAD_DOWN KEYCODE_DPAD_CENTER"
Start-Sleep 1
& $ADB -s $d shell "input keyevent KEYCODE_DPAD_DOWN KEYCODE_DPAD_CENTER"  # Apariencia
Start-Sleep 1
& $ADB -s $d shell "input keyevent KEYCODE_DPAD_DOWN KEYCODE_DPAD_CENTER"  # Tarjetas
Start-Sleep 1
& $ADB -s $d shell "input keyevent KEYCODE_DPAD_DOWN KEYCODE_DPAD_DOWN"
for($i=0;$i -lt 8;$i++){ & $ADB -s $d shell "input keyevent KEYCODE_DPAD_RIGHT"; Start-Sleep -Milliseconds 150 }
```

### 2. Tamaño L para la categoría "Aplicaciones de TV"

Navegación:
- Side panel → DOWN×1 CENTER (Editar categorías).
- Encontrar "Aplicaciones de TV" en la lista. Orden típico: Nueva categoría, Entradas, Aplicaciones de TV, Aplicaciones Móviles, Ajustes, Pantalla, Aplicaciones, Sistema. Entonces **DOWN×2 CENTER** desde el top.
  - Pero cuidado: el initial focus a veces NO es Nueva categoría sino Entradas. Si cae en Aplicaciones Móviles, hacer BACK y UP×1 CENTER.
- En el edit menu: hay que llegar al slider Tamaño. DPAD\\_DOWN no siempre scrollea el panel. **Truco: usar `input swipe 1050 650 1050 100 300` para scrollear,** después PAGE\\_DOWN o tap preciso.
- RIGHT×2 lleva de S a L.

### 3. Ocultar fila "Entradas" (HDMI inputs) — opcional

Preguntar al usuario si usa inputs HDMI antes.

Navegación:
- Side panel → Editar categorías → Entradas → edit menu.
- En edit menu: DOWN×2 CENTER → toggle "Visible" a OFF.

### 4. Screensaver OFF

Puro ADB, sin UI:
```
settings put secure screensaver_enabled 0
settings put secure screensaver_activate_on_sleep 0
settings put secure screensaver_activate_on_dock 0
am force-stop com.google.android.apps.tv.dreamx
```

Libera ~36 MB PSS.

## Trucos de navegación UI (cuando la automación es frágil)

El panel lateral de Projectivy es **frágil vía ADB** por varias razones:
- DPAD\\_DOWN a veces NO scrollea el panel para traer items off-screen al foco.
- `input swipe` para scrollear funciona a veces sí, a veces no.
- `KEYCODE_PAGE_DOWN` sí suele scrollear cuando swipe no funciona.
- CENTER en un slider lo cambia, no lo "entra".
- Tap de coordenadas: si cae fuera del panel, cierra el panel y activa lo que esté debajo (ej.: activar la app CamWay).

**Patrón recomendado**:
1. Siempre screenshot después de cada paso para verificar el estado.
2. `KEYCODE_PAGE_DOWN` si DPAD\\_DOWN no scrollea.
3. Tap directo en toggles por coordenadas: en el Daewoo, los toggles de "Gestionar aplicaciones" estaban en x=1180, cada row aparte 64 px (y=227, 291, 355, 419, 483, 547). Confirmar en screenshot.
4. Si algo se arruinó, BACK hasta cerrar y reabrir desde `am start -a tv.projectivy.SETTINGS`.

## Recordatorios al usuario

Una vez termines la fase 3, decirle al usuario:
- "Ahora lo que no te podés saltar: terminá el onboarding de Projectivy en el TV con el control. Avisame cuando llegues a la home de Projectivy."
- Que el icono del gear "Ajustes" en la fila es el **System Settings de Android TV**, NO Projectivy. Projectivy se configura desde la ruedita arriba a la derecha de su propia home (o `am start tv.projectivy.SETTINGS`).
- Que si queda encendido el "Dream" de Google TV, el delta de RAM no se ve hasta hacer reboot.

## Apps protegidas del usuario

Antes de empezar la Fase 4, preguntar: "¿Tenés apps propias instaladas en el TV que no quieras que toque?" (ej.: Camway, Kodi, Home Assistant, clientes de cámaras, apps de cadenas, lo que sea). Anotarlas y agregarlas a la lista de "nunca borrar" de esta sesión.
