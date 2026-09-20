#!/usr/bin/env python3
"""Todas las preguntas abiertas de los requerimientos, en una sola lista.

Por qué existe: el estado de un pedido vive en su issue, y con cuatro pedidos
a la vez nadie sabe qué le toca contestar sin abrir cuatro pestañas. El
2026-09-19, con tres requerimientos vivos, la pregunta que hubo que hacer fue
literalmente «pasame las preguntas que faltan, se me enredó todo».

Esto lee los issues con etiqueta `req:*`, saca su bloque de preguntas y las
agrupa **por quién las tiene que contestar**, no por issue. Los números de
issue salen al final de cada línea y en gris, porque son la referencia, no la
forma de pensar en el pedido.

Uso:
    ./preguntas-abiertas.py <owner/repo>
    ./preguntas-abiertas.py <owner/repo> --para Leo
    ./preguntas-abiertas.py <owner/repo> --porque    # incluye el "por qué importa"
    ./preguntas-abiertas.py <owner/repo> --repo-local ~/Projects/x \
        --plan docs/tecnico/PLAN.md --plan docs/hr/PLAN.md

Necesita `gh` autenticado. Nada más.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import textwrap

# El formato que la skill product-owner exige para cada pregunta:
#   - **Para <nombre> —** <la pregunta>
#     _Por qué importa:_ <el razonamiento>
PREGUNTA = re.compile(r"^\s*[-*]\s*\*\*Para\s+(?P<quien>[^—\-*]+?)\s*(?:—|--)\*\*\s*(?P<texto>.+?)\s*$")
PORQUE = re.compile(r"^\s*_Por qué importa:_\s*(?P<texto>.+?)\s*$")
# Toleramos el formato viejo, sin negritas ni raya, para no perder issues
# analizados antes de que la skill lo exigiera.
PREGUNTA_VIEJA = re.compile(r"^\s*[-*]\s*(?:Para\s+)?(?P<quien>Maikol|Leo|Caro)\s*[:—-]\s*(?P<texto>.+?)\s*$", re.I)
CERRADA = re.compile(r"^\s*[-*]\s*\(?cerrada\)?", re.I)


def gh(*args: str) -> str:
    try:
        out = subprocess.run(["gh", *args], capture_output=True, text=True, check=True)
    except FileNotFoundError:
        sys.exit("No encontré `gh`. Instalalo o ponelo en el PATH.")
    except subprocess.CalledProcessError as exc:
        sys.exit(f"`gh {' '.join(args)}` falló:\n{exc.stderr.strip()}")
    return out.stdout


def tarea_citada(issue: dict) -> str | None:
    """El número de tarea que el traspaso dejó escrito, si lo dejó."""
    for m in re.finditer(r"\b(\d{1,3}\.\d{1,3})\b", issue.get("body", "") or ""):
        return m.group(1)
    return None


def leer_plan(ruta: str, repo_local: str | None) -> str | None:
    """El plan **de la rama por defecto**, no el del árbol de trabajo.

    Un checkout puede llevar semanas parado en otra rama, y entonces el
    archivo del disco no dice lo que dice el proyecto. Medido dos veces el
    2026-09-19: una búsqueda de prior art devolvió nada desde una rama vieja,
    y después este mismo chequeo inventó un desfase porque la tarea 30.11
    no existía en la rama del checkout. Un archivo viejo y un archivo sin la
    tarea se ven idénticos, y el viejo es el caro.
    """
    if repo_local:
        try:
            out = subprocess.run(
                ["git", "-C", repo_local, "show", f"origin/HEAD:{ruta}"],
                capture_output=True, text=True)
            if out.returncode != 0:
                out = subprocess.run(
                    ["git", "-C", repo_local, "show", f"origin/main:{ruta}"],
                    capture_output=True, text=True)
            if out.returncode == 0:
                return out.stdout
        except OSError:
            pass
        return None
    try:
        return open(ruta, encoding="utf-8").read()
    except OSError:
        return None


def seccion_en_el_plan(numero: str, planes: list[str], repo_local: str | None) -> str | None:
    """En qué sección del plan vive esa tarea: la última cabecera `## …`
    antes de su casilla. Devuelve None si no la encuentra."""
    for ruta in planes:
        texto = leer_plan(ruta, repo_local)
        if texto is None:
            continue
        seccion = None
        for linea in texto.splitlines():
            if linea.startswith("## "):
                seccion = linea[3:].strip()
            if re.match(rf"^\s*[-*]\s*\[[ x]\]\s*\*\*{re.escape(numero)}\s*[—-]", linea):
                return seccion
    return None


def desfases(filas: list[dict], planes: list[str], repo_local: str | None) -> list[str]:
    """La bandera `req:esperando` no se quita sola: se levanta cuando alguien
    mueve la tarea en el plan, y nadie vigila eso. Esto lo vuelve visible.
    Con cuatro pedidos se nota a ojo; con treinta, no."""
    avisos = []
    for i in filas:
        etiquetas = i["_etiquetas"]
        if "req:en-plan" not in etiquetas:
            continue
        numero = tarea_citada(i)
        if not numero:
            avisos.append(f"#{i['number']} dice en-plan pero no nombra ninguna tarea "
                          f"— no hay cómo saltar del pedido al plan")
            continue
        if not planes:
            continue
        seccion = seccion_en_el_plan(numero, planes, repo_local)
        if seccion is None:
            avisos.append(f"#{i['number']} cita la tarea {numero} y no la encontré en los "
                          f"planes de la rama por defecto — ¿el número está mal, o falta "
                          f"pasar ese plan con --plan?")
            continue
        espera = seccion.lower().startswith("esperando")
        marcada = "req:esperando" in etiquetas
        if espera and not marcada:
            avisos.append(f"#{i['number']} · la tarea {numero} está en «{seccion}» "
                          f"pero al issue le falta req:esperando")
        elif marcada and not espera:
            avisos.append(f"#{i['number']} · la tarea {numero} ya está en «{seccion}» "
                          f"— sacale req:esperando, el bloqueo se levantó")
    return avisos


def issues(repo: str) -> list[dict]:
    raw = gh("issue", "list", "-R", repo, "--state", "open", "--limit", "100",
             "--json", "number,title,labels,body")
    rows = json.loads(raw or "[]")
    out = []
    for r in rows:
        etiquetas = {l["name"] for l in r.get("labels", [])}
        if any(e.startswith("req:") for e in etiquetas):
            r["_etiquetas"] = etiquetas
            out.append(r)
    return out


def bloque_de_preguntas(body: str) -> list[str]:
    """Las líneas entre '**Preguntas.**' y el siguiente bloque en negrita."""
    if not body:
        return []
    lineas = body.splitlines()
    inicio = next((i for i, l in enumerate(lineas)
                   if re.match(r"^\s*\*\*Preguntas", l, re.I)), None)
    if inicio is None:
        return []
    fin = len(lineas)
    for i in range(inicio + 1, len(lineas)):
        if re.match(r"^\s*\*\*(Tarea propuesta|Recomendación|Historial)", lineas[i], re.I):
            fin = i
            break
    return lineas[inicio:fin]


def extraer(issue: dict) -> list[dict]:
    preguntas: list[dict] = []
    for linea in bloque_de_preguntas(issue.get("body", "")):
        if CERRADA.match(linea):
            continue
        m = PREGUNTA.match(linea) or PREGUNTA_VIEJA.match(linea)
        if m:
            preguntas.append({
                "quien": m.group("quien").strip(),
                "texto": m.group("texto").strip(),
                "porque": "",
                "issue": issue["number"],
                "titulo": issue["title"],
            })
            continue
        m = PORQUE.match(linea)
        if m and preguntas:
            preguntas[-1]["porque"] = m.group("texto").strip()
    return preguntas


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo", help="owner/repo")
    ap.add_argument("--para", help="solo las de esta persona")
    ap.add_argument("--porque", action="store_true", help="incluir el «por qué importa»")
    ap.add_argument("--plan", action="append", default=[], metavar="RUTA",
                    help="un PLAN.md contra el que verificar la bandera req:esperando; "
                         "ruta dentro del repo, repetible")
    ap.add_argument("--repo-local", metavar="DIR",
                    help="clon local del repo: los planes se leen de la rama por defecto "
                         "(origin/HEAD), no del árbol de trabajo, que puede estar en otra "
                         "rama. Sin esto, --plan se lee como ruta de disco tal cual.")
    args = ap.parse_args()

    filas = issues(args.repo)
    if not filas:
        print("No hay issues abiertos con etiqueta req:*.")
        return 0

    todas: list[dict] = []
    sin_analisis: list[dict] = []
    for i in filas:
        p = extraer(i)
        todas.extend(p)
        if not p and "req:analizar" in i["_etiquetas"]:
            sin_analisis.append(i)

    if args.para:
        todas = [p for p in todas if p["quien"].lower() == args.para.lower()]

    if not todas:
        print("Ninguna pregunta abierta." if not args.para
              else f"Ninguna pregunta abierta para {args.para}.")
    else:
        por_quien: dict[str, list[dict]] = {}
        for p in todas:
            por_quien.setdefault(p["quien"], []).append(p)

        for quien in sorted(por_quien, key=lambda q: (-len(por_quien[q]), q.lower())):
            grupo = por_quien[quien]
            print(f"\n══ Para {quien} · {len(grupo)} "
                  f"{'pregunta' if len(grupo) == 1 else 'preguntas'} ══\n")
            for n, p in enumerate(grupo, 1):
                cuerpo = textwrap.fill(p["texto"], width=76,
                                       initial_indent=f"{n}. ", subsequent_indent="   ")
                print(cuerpo)
                if args.porque and p["porque"]:
                    print(textwrap.fill(p["porque"], width=72,
                                        initial_indent="   · ", subsequent_indent="     "))
                print(f"   ({p['titulo'][:56]} · #{p['issue']})\n")

    if args.repo_local:
        subprocess.run(["git", "-C", args.repo_local, "fetch", "-q", "origin"],
                       capture_output=True)
    avisos = desfases(filas, args.plan, args.repo_local)
    if avisos:
        print("\n── Desfases entre las etiquetas y el plan ──\n")
        for a in avisos:
            print(textwrap.fill(a, width=76, initial_indent="   ⚠ ", subsequent_indent="     "))
        print()

    if sin_analisis:
        print("\n── Esperando análisis, todavía sin preguntas ──\n")
        for i in sin_analisis:
            print(f"   {i['title'][:60]} · #{i['number']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
