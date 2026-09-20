#!/usr/bin/env python3
"""Cuál es el próximo número de fase libre, y de dónde sale.

Los números de fase son globales entre todos los planes de un repo y no se
reúsan nunca, así que «el que sigue» es el más alto en uso más uno. Suena
trivial y tiene una trampa: hay que mirar en tres lados, no en uno.

    1. Los planes, en la rama por defecto.
    2. Los diarios, porque una fase cerrada conserva su número para siempre.
    3. **Los PR abiertos**, porque un traspaso sin mergear es invisible en
       los dos primeros. El 2026-09-19 dos requerimientos aprobados con
       minutos de diferencia quisieron los dos la fase 39; salió bien de
       casualidad, porque uno leyó el issue del otro.

Todo se lee de `origin/HEAD`, nunca del árbol de trabajo: un checkout
parado en otra rama da un número equivocado y no avisa.

Uso:
    ./siguiente-fase.py <ruta-al-repo>
    ./siguiente-fase.py <ruta-al-repo> --repo owner/repo   # incluye PR abiertos

Necesita `git`, y `gh` autenticado solo si pasás --repo.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys

FASE = re.compile(r"^##\s+(?:Phase|Fase)\s+(\d{1,4})\b", re.M)


def git(repo: str, *args: str) -> str | None:
    try:
        out = subprocess.run(["git", "-C", repo, *args],
                             capture_output=True, text=True)
    except OSError:
        return None
    return out.stdout if out.returncode == 0 else None


def rama_por_defecto(repo: str) -> str:
    ref = git(repo, "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD")
    if ref and ref.strip():
        return ref.strip().removeprefix("refs/remotes/")
    return "origin/main"


def archivos_de_plan(repo: str, rama: str) -> list[str]:
    salida = git(repo, "ls-tree", "-r", "--name-only", rama) or ""
    return [l for l in salida.splitlines()
            if re.search(r"(PLAN|JOURNAL)\.md$", l)]


def fases_en(repo: str, rama: str, ruta: str) -> list[tuple[int, str]]:
    texto = git(repo, "show", f"{rama}:{ruta}") or ""
    return [(int(m.group(1)), ruta) for m in FASE.finditer(texto)]


def fases_en_pr_abiertos(slug: str) -> list[tuple[int, str]]:
    """Fases que un PR abierto agrega y todavía no están en la rama."""
    try:
        raw = subprocess.run(
            ["gh", "pr", "list", "-R", slug, "--state", "open",
             "--limit", "50", "--json", "number,title"],
            capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"  (no pude leer los PR abiertos: {exc})", file=sys.stderr)
        return []
    encontradas: list[tuple[int, str]] = []
    for pr in json.loads(raw or "[]"):
        n = pr["number"]
        try:
            diff = subprocess.run(["gh", "pr", "diff", str(n), "-R", slug],
                                  capture_output=True, text=True, check=True).stdout
        except (OSError, subprocess.CalledProcessError):
            continue
        for linea in diff.splitlines():
            if not linea.startswith("+"):
                continue
            m = FASE.match(linea[1:])
            if m:
                encontradas.append((int(m.group(1)), f"PR #{n} (sin mergear)"))
    return encontradas


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo", help="ruta a un clon local")
    ap.add_argument("--repo", dest="slug", metavar="owner/repo",
                    help="mirar también las fases que agregan los PR abiertos")
    args = ap.parse_args()

    if git(args.repo, "rev-parse", "--git-dir") is None:
        sys.exit(f"{args.repo} no parece un repo git.")
    subprocess.run(["git", "-C", args.repo, "fetch", "-q", "origin"],
                   capture_output=True)

    rama = rama_por_defecto(args.repo)
    hallazgos: list[tuple[int, str]] = []
    for ruta in archivos_de_plan(args.repo, rama):
        hallazgos.extend(fases_en(args.repo, rama, ruta))
    if not hallazgos:
        sys.exit(f"No encontré ninguna fase en {rama}. ¿Es el repo correcto?")

    if args.slug:
        hallazgos.extend(fases_en_pr_abiertos(args.slug))

    mayor, donde = max(hallazgos, key=lambda h: h[0])
    usadas = sorted({n for n, _ in hallazgos})

    print(f"\nRama leída: {rama}")
    print(f"Fases en uso: {', '.join(str(n) for n in usadas)}")
    print(f"La más alta: {mayor} · {donde}")
    if not args.slug:
        print("\n⚠ No se miraron los PR abiertos. Un traspaso sin mergear es")
        print("  invisible acá y es justo como dos pedidos piden el mismo")
        print("  número. Volvé a correrlo con --repo owner/repo.")
    print(f"\n→ La siguiente fase libre es la {mayor + 1}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
