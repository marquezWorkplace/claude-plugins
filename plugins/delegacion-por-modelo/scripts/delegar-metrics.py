"""Métricas de delegación: tokens y costo por modelo y por subagente en una sesión.

Uso: python delegar-metrics.py [sesion.jsonl | id-de-sesion] [--base <modelo>]

Sin argumento toma el transcript principal más reciente. El ahorro es una
estimación: reprecia los tokens de los subagentes como si los hubiera gastado
el modelo base (por defecto, el modelo de la sesión principal).
"""
import glob
import json
import os
import sys
from collections import defaultdict

RAIZ = os.path.expanduser("~/.claude")
CAMPOS = ("input", "output", "cache_read", "cache_write_5m", "cache_write_1h")


def buscar_sesion(arg):
    if arg and os.path.isfile(arg):
        return arg
    patron = os.path.join(RAIZ, "projects", "*", (arg or "*") + ".jsonl")
    archivos = glob.glob(patron)
    return max(archivos, key=os.path.getmtime) if archivos else None


def leer_uso(ruta):
    """Devuelve {modelo: tokens}. Un mensaje se repite por bloque: dejo la última versión por id."""
    por_id = {}
    with open(ruta, encoding="utf-8") as f:
        for linea in f:
            try:
                o = json.loads(linea)
            except ValueError:
                continue
            m = o.get("message")
            if not isinstance(m, dict) or not m.get("usage") or not m.get("model"):
                continue
            if m["model"].startswith("<"):
                continue
            clave = m.get("id") or o.get("uuid")
            u = m["usage"]
            cc = u.get("cache_creation") or {}
            w1h = cc.get("ephemeral_1h_input_tokens", 0)
            w5m = cc.get("ephemeral_5m_input_tokens", 0)
            if not cc:
                w5m = u.get("cache_creation_input_tokens", 0)
            t = {
                "input": u.get("input_tokens", 0),
                "output": u.get("output_tokens", 0),
                "cache_read": u.get("cache_read_input_tokens", 0),
                "cache_write_5m": w5m,
                "cache_write_1h": w1h,
            }
            previo = por_id.get(clave)
            if previo is None or t["output"] >= previo[1]["output"]:
                por_id[clave] = (m["model"], t)
    por_modelo = defaultdict(lambda: dict.fromkeys(CAMPOS, 0))
    for modelo, t in por_id.values():
        for c in CAMPOS:
            por_modelo[modelo][c] += t[c]
    return por_modelo


def costo(tokens, precio):
    return sum(tokens[c] * precio[c] for c in CAMPOS) / 1_000_000


def total(tokens):
    return sum(tokens.values())


def fmt_tok(n):
    return f"{n / 1000:.1f}k" if n >= 1000 else str(n)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = sys.argv[1:]
    base = None
    if "--base" in args:
        i = args.index("--base")
        base = args[i + 1] if i + 1 < len(args) else None
        del args[i:i + 2]
    sesion = buscar_sesion(args[0] if args else None)
    if not sesion:
        sys.exit("No encontré ningún transcript de sesión.")

    junto = os.path.join(os.path.dirname(os.path.abspath(__file__)), "delegar-precios.json")
    ruta_precios = junto if os.path.isfile(junto) else os.path.join(RAIZ, "delegar-precios.json")
    with open(ruta_precios, encoding="utf-8") as f:
        precios = {k: v for k, v in json.load(f).items() if not k.startswith("_")}

    principal = leer_uso(sesion)
    carpeta_sub = os.path.join(sesion[:-6], "subagents")
    agentes = []  # (tipo, descripción, {modelo: tokens})
    for ruta in sorted(glob.glob(os.path.join(carpeta_sub, "agent-*.jsonl"))):
        meta = {}
        try:
            with open(ruta[:-6] + ".meta.json", encoding="utf-8") as f:
                meta = json.load(f)
        except (OSError, ValueError):
            pass
        agentes.append((meta.get("agentType", "?"), meta.get("description", ""), leer_uso(ruta)))

    if base is None and principal:
        base = max(principal, key=lambda m: total(principal[m]))
    print(f"Sesión: {os.path.basename(sesion)[:-6]}")
    print(f"Modelo base para la comparación: {base}\n")

    sin_precio = set()

    def precio_de(modelo):
        if modelo not in precios:
            sin_precio.add(modelo)
            return None
        return precios[modelo]

    def costo_de(modelo, tokens):
        p = precio_de(modelo)
        return costo(tokens, p) if p else None

    def fila(nombre, modelo, tokens):
        c = costo_de(modelo, tokens)
        cs = f"${c:.4f}" if c is not None else "?"
        print(f"{nombre:<26}{modelo:<20}{fmt_tok(total(tokens)):>9}{fmt_tok(tokens['output']):>9}{cs:>11}")

    print(f"{'':<26}{'modelo':<20}{'tokens':>9}{'salida':>9}{'costo':>11}")
    costo_real_sub = 0.0
    costo_cf_sub = 0.0
    completo = True
    for modelo, t in principal.items():
        fila("principal", modelo, t)
    for tipo, desc, usos in agentes:
        for modelo, t in usos.items():
            fila(f"{tipo}", modelo, t)
            real = costo_de(modelo, t)
            cf = costo_de(base, t) if base else None
            if real is None or cf is None:
                completo = False
            else:
                costo_real_sub += real
                costo_cf_sub += cf
    if not agentes:
        print("(sin subagentes en esta sesión)")
        return

    if sin_precio:
        print(f"\nSin precio en delegar-precios.json: {', '.join(sorted(sin_precio))}")
    print("\nDelegación (solo subagentes):")
    print(f"  Costo real:                      ${costo_real_sub:.4f}")
    print(f"  Si lo hubiera hecho {base}: ${costo_cf_sub:.4f}")
    dif = costo_cf_sub - costo_real_sub
    etiqueta = "Ahorro estimado" if dif >= 0 else "Sobrecosto estimado"
    pct = abs(dif) / costo_cf_sub * 100 if costo_cf_sub else 0
    print(f"  {etiqueta}: ${abs(dif):.4f} ({pct:.0f}%)")
    if not completo:
        print("  (incompleto: faltan precios para algún modelo)")
    print("\nLímites: el costo real es exacto (usage del transcript). El contrafactual supone los mismos")
    print("tokens en el modelo base, e ignora que el trabajo delegado habría engordado el contexto")
    print("principal y que el subagente paga su propio arranque de contexto. Es un orden de magnitud.")


if __name__ == "__main__":
    main()
