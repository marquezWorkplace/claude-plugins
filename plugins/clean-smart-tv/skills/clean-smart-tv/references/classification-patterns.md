# Patrones de clasificación: qué es qué en un Smart TV Android

Un paquete puede pertenecer a más de un cajón. Elegir el más restrictivo (cajón "nunca tocar" gana sobre "candidato a quitar").

## áNunca tocar!  (sistema crítico)

Cualquiera de estos rompía el TV (crash del system\\_server, soft reboot, pérdida de Wi-Fi):

- **APEX**: todo lo que vive en `/apex/`. Son módulos de sistema de Android firmados por Google. `pm uninstall` los rechaza, pero `pm disable` en algunos puede pegarle al wificond, mediaprovider, etc.
- **Overlays**: `com.*.overlay.*`, `com.google.android.overlay.*`, `*__auto_generated_rro_product`, `*__auto_generated_rro_vendor`. Son RROs (runtime resource overlays) que aportan recursos UI. Quitar uno privilegiado como `com.google.android.safetycenter.resources` **en Android 14** reinicia `system_server` y a veces hace caer el Wi-Fi.
- **Framework**: `android`, `com.android.systemui`, `com.android.providers.settings`, `com.android.networkstack*`, `com.android.providers.media*`, `com.android.permissioncontroller` (o su variante Google: `com.google.android.permissioncontroller`).
- **Google Play / GMS**: `com.android.vending`, `com.google.android.gms`, `com.google.android.gsf`, `com.google.android.webview`, `com.google.android.ext.services`, `com.google.android.modulemetadata`, `com.google.android.tungsten.setupwraith` (si el usuario nunca factory-reset; si sí, igual innecesario).
- **Input methods base**: `com.android.inputdevices`, `com.google.android.inputmethod.latin` (Gboard) — quitar Gboard sin tener otro IME lo deja sin teclado.
- **Chipset core**: `com.droidlogic` (Amlogic), `com.realtek.*` base, `com.mediatek.*` que NO sea `mediatek.tv.retaildemo`, `com.hisilicon.*` base.
- **Bluetooth y conectividad**: `com.android.bluetooth`, `com.android.providers.bluetooth`, APEX de `com.android.btservices`, `com.android.wifi.*`.
- **HDMI / inputs del TV**: `com.droidlogic.tvinput`, `com.google.android.tv.inputplayer` + cualquier `*.inputsource` del chipset (si el usuario usa entradas HDMI).

## Seguro de quitar: adware / telemetría / OEM bloat

Agrupado por familia OEM. Si el TV es de otra marca pero mismo ODM (Daewoo/Hisense/TCL/Philips/Noblex suelen compartir ODM), buscar por prefijo.

### Skyworth / Coocaa (ODM de muchas marcas LATAM)
- `com.smartdevice.global.service` — "Find my remote" + telemetría `AfterSaleActivity` + `TimeRecordReceiver`. 16 MB RAM. **Persistent**; solo cede con `disable-user`.
- `com.smartdevice.dailyshortcut` — atajos promocionales.
- `com.smartdevice.factory` — modo fábrica/diagnóstico.
- `com.smartdevice.leanbacklauncher.customizer` — customizer del launcher legacy (inservible con Projectivy).
- `com.smartdevice.tv.setupwraith` — override del setup wizard de Skyworth.
- `com.smartdevice.myapp` — app placeholder de fábrica.
- `com.tianci.*` — Coocaa (filial de Skyworth). `com.tianci.localmedia` es su player.
- `com.coocaa.*` — lo mismo.

### CLTV (Common Live TV - stack HbbTV/broadcast)
- `com.cltv.hybrid` — companion de HbbTV broadcast. Innecesaria si no se usa HbbTV.
- `com.cltv.mal` — CltvMalService (middleware MAL). **Tiene `SYSTEM_ALERT_WINDOW`** (vector adware potencial). 46 MB RAM. Quitar si no se usa antena broadcast interactiva.

### AstroTV / Ginga (middleware brasileño ISDB-Tb)
- `com.mirakulo.astrotv.service` — Ginga. Solo útil en TVs de Brasil con antena ISDB-Tb. Innecesario en Venezuela/Colombia/resto de LATAM aunque haya antena.

### MediaTek
- `com.mediatek.tv.retaildemo` — demo de tienda. Siempre quitar.
- Otros `com.mediatek.*` revisar manualmente; algunos son drivers.

### PlayAutoInstallStub (!!!)
- `android.autoinstalls.config.soc.amlogic` (o `.soc.mediatek`, etc.) — **vector adware OEM**. Es la config que dice al Play Store qué apps preinstalar automaticamente. Es por eso que apps borradas "reaparecen". Siempre quitar.

### Google TV extras (si el usuario los pidió fuera)
- `com.google.android.feedback` — "send feedback" telemetría.
- `com.google.android.syncadapters.calendar` — sync Google Calendar (inservible en TV).
- `com.google.android.marvin.talkback` — TalkBack accesibilidad (opcional).
- `com.google.android.tv.googletvremotepairer` — pairing de control remoto Google TV via app del celular.
- `com.google.android.tv.dfuservice` — updates OTA de firmware Google TV.
- `com.google.android.apps.tv.dreamx` — salvapantallas Google TV (36 MB).
- `com.google.android.tv.inputplayer` — **mantener** (HDMI).
- `com.google.android.safetycenter.resources` — **¡NO TOCAR!** Soft-reboot garantizado.
- `com.google.android.partnersetup` — wizard de partner setup (post-setup innecesario).

### Android TV sistema (si no se necesita)
- `com.android.providers.calendar` — Calendar Provider (TV no usa calendar).
- `com.android.providers.contacts` — Contacts Provider (idem).
- `com.android.printspooler` — spooler de impresión.
- `com.android.wallpaperbackup` — backup de fondos.
- `com.android.managedprovisioning` — MDM empresarial.
- `com.android.tv.dashboardintegration` — dashboard de Google TV (desaparece con launcherx).

## Preguntas al usuario — depende de él

### Antena TV broadcast
- `com.droidlogic.android.tv` + `com.droidlogic.dtvkit.*` + `com.droidlogic.setup.provider` + `com.cltv.*` + `com.mirakulo.*`
- **Mantener si** el usuario usa antena DVB/ISDB/ATSC. **Quitar si no.**

### Streaming preinstalado
- `com.netflix.ninja` + `com.netflix.tokenmanager` + integración chipset (p.ej. Amlogic `.NetflixService`).
- `com.amazon.amazonvideo.livingroom` — Prime Video.
- `com.google.android.youtube.tv` — YouTube TV.
- `com.disney.disneyplus` — Disney+.
- `com.pluto.tv`, `tv.pluto.android.tv.leanback` — Pluto TV.
- `tv.tubitv.tv` — Tubi.
- Otros: Rakuten, Xumo, Crackle, Globo Play, HBO Max, etc.

Preguntar cuáles usa.

### "Find my remote" (buzzer del control)
- Variar por OEM: `com.smartdevice.global.service` en Skyworth, `com.hisense.findmycontroller.*` en Hisense, etc.

## Apps del usuario — ¡nunca borrar sin confirmación!

Detectables por:
- Prefijos de dominio que no son de Google/Android/un OEM conocido.
- Instaladas en `/data/app/~~<hash>==/...` (no en `/system/` o `/system\\_ext/`) → usuario las puso via Play Store o sideload.
- `installerPackageName` ≠ null y ≠ `com.google.android.packageinstaller`.

Ejemplos reales:
- **CamWay** (`com.pacific.camwaytv`) — app de monitoreo de cámaras del usuario Pacific Logging. Instalada manualmente por ellos. Protegida.
- **Kodi** (`org.xbmc.kodi`), **VLC** (`org.videolan.vlc`), **Jellyfin** — reproductores que el usuario puede haber instalado.
- Clientes de Home Assistant, dashboards de domotica, etc.

**Regla**: si el prefijo del paquete no aparece en esta lista de clasificación y la app está en `/data/app/`, **preguntar**.

## Cómo detectar la familia OEM con un comando

```powershell
& $ADB -s $d shell "getprop ro.product.manufacturer; getprop ro.product.brand; getprop ro.oem.key1; pm list packages | grep -iE 'smartdevice|coocaa|tianci|hisense|tcl|xiaomi|skyworth|changhong|haier|konka' | head -10"
```

Si salen más de 2 paquetes con el prefijo del fabricante, aplicar la familia correspondiente de esta lista.
