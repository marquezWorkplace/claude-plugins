# Comandos de inventario

Lo que hay que sacar del TV en Fase 2, con el comando exacto y qué interpretar.

Todos estos comandos asumen la variable `$ADB` apuntando a `adb.exe` y `$d` como `<TV_IP>:5555`.

## Identidad del TV (primero siempre)

```powershell
& $ADB -s $d shell "getprop | grep -E 'ro.product.brand|ro.product.manufacturer|ro.product.model|ro.product.name|ro.product.device|ro.build.version.release|ro.build.version.sdk|ro.build.fingerprint|ro.hardware|ro.oem.key1|ro.product.cpu.abilist|persist.vendor.wifi_mac'"
```

De lo que sale decidimos:
- **ODM real**: `ro.product.manufacturer` suele revelar quién hizo el TV aunque la marca sea otra (ej.: marca Daewoo, manufacturer Skyworth).
- **ABI**: `armeabi-v7a` indica TV de 32-bit → elegir APKs 32-bit, no arm64.
- **ATV certificado**: `ro.oem.key1` empezando por `ATV00` indica Google TV certificado.
- **RAM**: ver sección siguiente.
- **MAC Wi-Fi real** vs la en uso: `persist.vendor.wifi_mac` es la original; si no coincide con la MAC que muestra `ip addr show wlan0`, hay randomización por SSID activa.

## Paquetes instalados

```powershell
# Todos (con ruta)
& $ADB -s $d shell "pm list packages -f"

# Solo de usuario (instalados por play store / adb)
& $ADB -s $d shell "pm list packages -3"

# Deshabilitados
& $ADB -s $d shell "pm list packages -d"

# Lanzables desde el launcher Android TV
& $ADB -s $d shell "cmd package query-activities -a android.intent.action.MAIN -c android.intent.category.LEANBACK_LAUNCHER 2>/dev/null | grep -E 'name=|packageName=' | head -80"

# Launcher por defecto (home)
& $ADB -s $d shell "cmd package resolve-activity -c android.intent.category.HOME --brief | tail -1"
& $ADB -s $d shell "cmd role get-role-holders android.app.role.HOME --user 0"
```

Guardar la salida completa de `pm list packages -f` para referencia posterior.

## RAM y procesos

```powershell
# Memoria total/libre
& $ADB -s $d shell "grep -E 'MemTotal|MemFree|MemAvailable|Cached:|SwapCached' /proc/meminfo"

# Top procesos por PSS (consumo real de RAM)
& $ADB -s $d shell "dumpsys meminfo 2>/dev/null | awk '/Total PSS by process/,/Total PSS by OOM/' | head -30"

# Procesos activos (filtrados)
& $ADB -s $d shell "ps -A -o USER,PID,RSS,NAME | head -40"
```

Puntos de referencia:
- TV de 1 GB RAM (como el Daewoo) tiene ~340 MB disponibles en reposo con bloat activo.
- Launcherx de Google TV suele consumir 80-120 MB.
- Play Store (`com.android.vending`) suele consumir 80-100 MB sumando sus procesos.
- Si **`MemAvailable` baja de 150 MB**, el TV va a hacer OOM-kill frecuente de apps en background.

## Servicios en background

```powershell
# Todos los ServiceRecord
& $ADB -s $d shell "dumpsys activity services 2>/dev/null | grep -E '^  \\* ServiceRecord' | wc -l"

# Servicios de interés (OEM, telemetría, MediaTek, AstroTV/Ginga)
& $ADB -s $d shell "dumpsys activity services 2>/dev/null | grep -iE 'smartdevice|coocaa|tianci|cltv|mirakulo|adups|coship|gome|xijia' | grep -i servicerecord"
```

## Receivers de arranque (apps que se auto-lanzan al boot)

```powershell
& $ADB -s $d shell "pm query-receivers --brief android.intent.action.BOOT_COMPLETED 2>/dev/null | head -60"
```

Las apps con BOOT_COMPLETED + permiso `SYSTEM_ALERT_WINDOW` son candidatas adware (pueden dibujar encima de otras apps).

## Permisos sensibles de un paquete sospechoso

```powershell
& $ADB -s $d shell "dumpsys package <pkg> | grep -E 'Receiver|android.permission|android.intent.action' | head -40"
```

Buscar:
- `SYSTEM_ALERT_WINDOW` → puede dibujar overlays (adware típico).
- `INSTALL_PACKAGES` + `DELETE_PACKAGES` → puede instalar/quitar apps (vector adware/updater OEM).
- `RECEIVE_BOOT_COMPLETED` + `WAKE_LOCK` → se auto-arranca y no deja dormir al TV.
- `BIND_ACCESSIBILITY_SERVICE` → puede leer toda la pantalla y simular toques.

## Red saliente

```powershell
# Conexiones TCP establecidas en este momento
& $ADB -s $d shell "ss -tnp 2>/dev/null | head -40"

# DNS lookup en logs
& $ADB -s $d shell "logcat -d -b all -t 500 'DnsClient:V' '*:S' 2>/dev/null | head -40"
```

Destinos normales Google TV:
- `142.251.*`, `172.217.*`, `216.58.*` — Google services
- `*.googleusercontent.com`, `*.googleapis.com`
- `mtalk.google.com:5228` — push FCM/GCM (normal, persistente)

Destinos **a investigar**:
- IPs de China (`1.1.*`, `14.*`, `58.*`, `59.*`, `61.*`, `103.*`, `180.*`, `210.*`, `220.*`) — telémetría OEM habitual.
- Dominios que no son del OEM declarado (ej.: un TV "Daewoo" llamando a dominios chinos random).
- Puertos extraños: 7711, 8899, 9527 (asociados a backdoors conocidos tipo Adups).

## Logcat para auditoría breve

```powershell
# Últimos 2000 eventos filtrando posibles telemetría
& $ADB -s $d shell "logcat -d -t 2000 2>/dev/null | grep -iE 'upload|telemetry|analytics|report|metric|collect|tracking' | grep -vE 'GServices|UsageStats' | head -40"
```

## Espacio en disco

```powershell
& $ADB -s $d shell "df -h /data /system 2>/dev/null"
```

TVs de gama baja suelen tener 4-8 GB de `/data`. Si está arriba del 80% ya conviene limpiar cache / desinstalar apps pesadas.
