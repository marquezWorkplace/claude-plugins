# claude-plugins

Marketplace propio de plugins para Claude Code.

## Agregarlo

```
/plugin marketplace add marquezWorkplace/claude-plugins
```

Después, instalá el que quieras con `/plugin install <nombre>`.

## Plugins

| Plugin | Qué hace |
| --- | --- |
| [delegacion-por-modelo](plugins/delegacion-por-modelo) | Reparte trabajo entre modelos con subagentes: Sonnet ejecuta, Opus planifica y revisa |

## Agregar un plugin nuevo

1. Creá `plugins/<nombre>/` con su `.claude-plugin/plugin.json`.
2. Poné adentro lo que corresponda: `agents/`, `commands/`, `skills/`, `hooks/`.
3. Registralo en el array `plugins` de `.claude-plugin/marketplace.json`, con `source` apuntando a `./plugins/<nombre>`.
