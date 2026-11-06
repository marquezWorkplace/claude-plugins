# Reglas de seguridad y cómo recuperarse

## Lo que nunca hay que hacer (con el porqué)

### No quitar overlays
Los paquetes `com.*.overlay.*` y los `*__auto_generated_rro_*` son **Runtime Resource Overlays** — aportan recursos UI (strings, colores, layouts) a otros paquetes del sistema. Quitarlos puede crashear al que dependa de ellos, o peor, al `system_server`.

**Caso real documentado**: en el Daewoo, al quitar `com.google.android.safetycenter.resources` (un overlay de Google), en Android 14 `system_server` se reinició (~60s), el TV se desconectó del Wi-Fi, y el usuario tuvo que reconectar a mano. Los procesos reaparecieron con nuevos PIDs. **El TV no se rompe**, pero susta.

### No quitar APEX
`/apex/` son módulos de Android firmados por Google (mediaprovider, wifi, bluetooth, networkstack, tethering, etc). `pm uninstall` los rechaza; `pm disable` en algunos también falla; en los que no falla, revienta funciones centrales.

### No quitar privilegiados que todavía usamos
Aunque `pm disable-user` o `pm uninstall --user 0` acepten el comando, estos siempre quedan:
- `com.android.vending` — Play Store, cualquiera que instale/actualice apps lo necesita.
- `com.google.android.gms` + `com.google.android.gsf` — Play Services, requerido por 99% de las apps.
- `com.google.android.webview` — WebView del sistema (usado por TV Bro y muchas otras).
- `com.android.systemui` — barra de estado, diálogos del sistema.
- `com.android.networkstack*` — stack de red.
- `com.android.providers.media*` — provider de archivos media.
- `com.android.permissioncontroller` o `com.google.android.permissioncontroller` — UI de permisos.
- `com.droidlogic` base (no sus servicios opcionales) — driver del Amlogic.

### No usar `pm uninstall` en apps persistent
Los paquetes con flag `PERSISTENT` (verificable con `dumpsys package <pkg> | grep flags=`) siguen vivos incluso tras `pm uninstall --user 0`. El proceso sobrevive hasta el próximo reboot y muchas veces reaparece. Para esos usar `pm disable-user --user 0`.

Caso real: `com.smartdevice.global.service` del Daewoo tiene `PERSISTENT`. Tras `pm uninstall --user 0` quedó `installed=false enabled=0` pero el proceso con PID 1622 (16 MB RAM) siguió corriendo. Solo con `pm disable-user --user 0` quedó oficialmente muerto.

### No encadenar cambios con el TV offline
Si ADB reporta `device offline` entre comandos, **parar**. Hacer:
```
Test-Connection <TV_IP> -Count 3
```
Si no pingea, esperar 30-60s a que vuelva. No iniciar la próxima tanda de cambios hasta que el `adb connect` reconecte sin pedir autorización.

### No hacer reboot sin avisar
Un `adb reboot` corta cualquier cosa que el usuario esté mirando (cámaras, película, llamada). Antes de reboot, **avisar y esperar el OK** del usuario.

## Comandos y sus equivalentes seguros/riesgosos

| Lo que uno quiere | Opción agresiva | Opción segura | Cuándo usar cuál |
|---|---|---|---|
| Quitar app de usuario | `pm uninstall --user 0 <pkg>` | `pm disable-user --user 0 <pkg>` | Uninstall cuando la app es de `/system` o `/system_ext` y no es `PERSISTENT`. Disable-user cuando es `PERSISTENT` o cuando queres poder revertir con un click (desde Settings). |
| Ocultar icono de launcher | `pm disable <pkg>/<activity>` | Toggle Visible OFF en Projectivy | `pm disable` en priv-app del sistema devuelve `SecurityException` (shell no puede). La UI de Projectivy funciona siempre. |
| Liberar RAM temporalmente | `am kill-all` | `am force-stop <pkg>` | Force-stop para apps puntuales; kill-all para limpieza masiva de caché (el sistema re-arranca lo esencial). |
| Ver el estado real post-cambio | polling repetitivo | Un solo `dumpsys meminfo` tras 3-5 segundos de espera | Los procesos no mueren instantáneo. Esperar y medir una vez. |

## Revertir cambios

Todo lo que hace esta skill es reversible. Patrón:

### Reactivar un paquete deshabilitado
```
pm enable <paquete>
```

### Reinstalar un paquete removido con `--user 0`
```
cmd package install-existing <paquete>
```
Esto funciona porque el APK sigue vivo en `/system/` o `/system_ext/`; solo se había "desinstalado" del usuario 0. Si falla con "package not found", el APK se removió realmente (raro con `--user 0`) y hay que reinstalar manualmente o factory reset.

### Restaurar el launcher viejo
```
pm enable com.google.android.apps.tv.launcherx
cmd package set-home-activity com.google.android.apps.tv.launcherx/com.google.android.apps.tv.launcherx.home.HomeActivity
```

### Reactivar el screensaver
```
settings put secure screensaver_enabled 1
settings put secure screensaver_activate_on_sleep 1
```

## Log obligatorio

Para que todo sea reversible sin memorizar nada, al principio de la Fase 5 crear:
```
<scratchpad>/clean-smart-tv-<fecha>/
    inventory.txt       # salida completa de pm list packages -f + dumpsys meminfo
    apks/               # los APKs descargados con sus sha256
    uninstalled.txt     # cada comando ejecutado y su revert
```

Formato de `uninstalled.txt`:
```
# Removidos de user 0 el <YYYY-MM-DD HH:MM> en <TV_IP>
# Revertir con: adb -s <TV_IP>:5555 shell cmd package install-existing <paquete>
#         o:   adb -s <TV_IP>:5555 shell pm enable <paquete>

com.smartdevice.dailyshortcut                           -> Success (uninstall --user 0)
com.smartdevice.global.service                          -> Success (disable-user)
...
```

Cuando el usuario diga "a esta la quiero de vuelta", abrir el log, buscar la línea, ejecutar el revert.

## Checklist antes de dar por terminada la skill

- [ ] RAM antes vs después reportada al usuario (delta claro).
- [ ] Log guardado y su ruta comunicada al usuario.
- [ ] Projectivy funcionando como home (botón HOME del remoto cae ahí).
- [ ] TV Bro, Material Files, Projectivy instalados y aparecen en la fila.
- [ ] Wi-Fi del TV OK después de todos los cambios.
- [ ] Ninguna app protegida del usuario tocada.
- [ ] Usuario sabe cómo entrar a los Ajustes del sistema si ocultó el icono (ruedita arriba a la derecha de Projectivy → "Ajustes de Android").
- [ ] Sugerido un reboot para liberar RAM de procesos `PERSISTENT` que quedaron corriendo hasta el próximo arranque.
