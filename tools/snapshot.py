#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
snapshot.py — Genera un resumen compacto del proyecto para pegarlo en una
conversacion con un LLM, sin dependencias externas (solo biblioteca estandar).

Filosofia: enviar SIEMPRE la estructura completa (barata en tokens) y SOLO el
contenido de los archivos que pidas explicitamente (caro en tokens).

Uso tipico
----------
    python tools/snapshot.py
        -> estado del proyecto + arbol + git + inventario de codigo

    python tools/snapshot.py src/data/standardize.py src/data/loaders.py
        -> lo anterior + esos dos archivos con numeros de linea

    python tools/snapshot.py notebooks/01_eda.ipynb
        -> extrae solo las celdas de codigo del notebook (ignora las salidas)

    python tools/snapshot.py --all
        -> incluye todo src/ (usar con cuidado: mira el conteo de tokens)

    python tools/snapshot.py -t "Bug en la desalinizacion de SMILES" src/data/standardize.py
        -> agrega un encabezado con la tarea en curso

Opciones
--------
    -t, --tarea TEXTO   Descripcion de la tarea en curso (va al principio).
    -n, --lineas N      Maximo de lineas por archivo volcado (0 = sin limite). Def: 400
    -d, --depth N       Profundidad del arbol de directorios. Def: 3
        --all           Incluye todos los archivos de codigo de SRC_DIRS.
        --out RUTA      Archivo de salida. Def: snapshot.md en la raiz.
        --no-clip       No copiar al portapapeles.
        --list          Solo lista los archivos de codigo y sale.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# --------------------------------------------------------------------------
# Configuracion. Ajusta esto a tu proyecto y olvidate del resto.
# --------------------------------------------------------------------------

EXCLUDE_DIRS = {
    ".git", ".github", "__pycache__", ".ipynb_checkpoints", ".venv", "venv",
    "env", "node_modules", ".mypy_cache", ".ruff_cache", ".pytest_cache",
    ".idea", ".vscode", ".obsidian", "site-packages", "wandb", "mlruns",
    "literatura", "logs",
}

# Directorios cuyo CONTENIDO no interesa, pero cuya EXISTENCIA si.
# Se muestran en el arbol como una linea resumen con el numero de archivos.
COLLAPSE_DIRS = {"data", "models", "figuras", "figures", "checkpoints", "outputs"}

CODE_EXTS = {".py", ".ipynb", ".r", ".R", ".qmd", ".yml", ".yaml", ".toml", ".cfg"}
TEXT_EXTS = CODE_EXTS | {".md", ".tex", ".bib", ".txt", ".json", ".csv", ".sh", ".ps1"}

SRC_DIRS = ["src", "scripts", "tools", "tests"]
ESTADO_FILE = Path("docs") / "00_estado.md"

TOKEN_WARN = 8000       # avisa si el snapshot supera este tamano aproximado
CHARS_PER_TOKEN = 4     # aproximacion suficiente para decidir si recortar

LANG_BY_EXT = {
    ".py": "python", ".ipynb": "python", ".r": "r", ".R": "r", ".qmd": "markdown",
    ".yml": "yaml", ".yaml": "yaml", ".toml": "toml", ".md": "markdown",
    ".tex": "latex", ".bib": "bibtex", ".json": "json", ".sh": "bash",
    ".ps1": "powershell", ".csv": "text", ".cfg": "ini", ".txt": "text",
}


# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------

def find_root() -> Path:
    """Raiz del repo git; si no hay git, el padre de la carpeta del script."""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=10,
        )
        if out.returncode == 0 and out.stdout.strip():
            return Path(out.stdout.strip()).resolve()
    except (OSError, subprocess.SubprocessError):
        pass
    here = Path(__file__).resolve().parent
    return here.parent if here.name == "tools" else here


def read_text(path: Path) -> str:
    """Lectura tolerante: Windows suele defaultear a cp1252 y romper acentos."""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return f"[no se pudo leer: {exc}]"


def git(root: Path, *args: str) -> str:
    try:
        out = subprocess.run(
            ["git", *args], cwd=root, capture_output=True, text=True, timeout=15,
        )
        return out.stdout.strip() if out.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def is_excluded(path: Path, root: Path) -> bool:
    rel_parts = path.relative_to(root).parts
    return any(part in EXCLUDE_DIRS for part in rel_parts)


def iter_code_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for d in SRC_DIRS:
        base = root / d
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*")):
            if p.is_file() and p.suffix in CODE_EXTS and not is_excluded(p, root):
                files.append(p)
    for p in sorted(root.glob("*")):
        if p.is_file() and p.suffix in CODE_EXTS:
            files.append(p)
    return files


def count_lines(path: Path) -> int:
    try:
        with path.open("rb") as fh:
            return sum(1 for _ in fh)
    except OSError:
        return 0


# --------------------------------------------------------------------------
# Secciones del reporte
# --------------------------------------------------------------------------

def build_tree(root: Path, max_depth: int) -> str:
    """Arbol de directorios compacto, con carpetas de datos colapsadas."""
    lines: list[str] = [f"{root.name}/"]

    def walk(directory: Path, prefix: str, depth: int) -> None:
        if depth > max_depth:
            return
        try:
            entries = sorted(
                (p for p in directory.iterdir() if p.name not in EXCLUDE_DIRS),
                key=lambda p: (p.is_file(), p.name.lower()),
            )
        except OSError:
            return
        for i, entry in enumerate(entries):
            last = i == len(entries) - 1
            branch = "\\-- " if last else "|-- "
            child_prefix = prefix + ("    " if last else "|   ")
            if entry.is_dir():
                # Solo se colapsan en el primer nivel: src/data SI es codigo.
                if entry.name in COLLAPSE_DIRS and entry.parent == root:
                    n = sum(1 for _ in entry.rglob("*") if _.is_file())
                    lines.append(f"{prefix}{branch}{entry.name}/  [{n} archivos, contenido omitido]")
                    continue
                lines.append(f"{prefix}{branch}{entry.name}/")
                walk(entry, child_prefix, depth + 1)
            else:
                if entry.suffix in TEXT_EXTS or entry.name.startswith("."):
                    lines.append(f"{prefix}{branch}{entry.name}")
                else:
                    size = entry.stat().st_size if entry.exists() else 0
                    lines.append(f"{prefix}{branch}{entry.name}  ({size/1e6:.1f} MB)")

    walk(root, "", 1)
    return "\n".join(lines)


def build_git_section(root: Path) -> str:
    if not (root / ".git").exists():
        return ""
    branch = git(root, "branch", "--show-current") or "(sin rama)"
    log = git(root, "log", "--oneline", "-8") or "(sin commits)"
    status = git(root, "status", "--short") or "(arbol limpio)"
    return (
        f"rama: {branch}\n\n"
        f"--- ultimos commits ---\n{log}\n\n"
        f"--- cambios sin commitear ---\n{status}"
    )


def build_inventory(root: Path) -> str:
    files = iter_code_files(root)
    if not files:
        return "(sin archivos de codigo)"
    rows = []
    total = 0
    for f in files:
        n = count_lines(f)
        total += n
        rows.append((n, f.relative_to(root).as_posix()))
    rows.sort(reverse=True)
    width = max(len(str(n)) for n, _ in rows)
    body = "\n".join(f"{n:>{width}}  {name}" for n, name in rows)
    return f"{body}\n{'-' * (width + 2)}\n{total:>{width}}  TOTAL ({len(rows)} archivos)"


def notebook_code(path: Path, keep_markdown: bool = True) -> str:
    """Extrae celdas de un .ipynb sin salidas ni metadatos (ahorra ~10x tokens)."""
    try:
        nb = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        return f"[notebook ilegible: {exc}]"
    chunks: list[str] = []
    for i, cell in enumerate(nb.get("cells", []), start=1):
        src = "".join(cell.get("source", [])).rstrip()
        if not src:
            continue
        kind = cell.get("cell_type")
        if kind == "code":
            chunks.append(f"# --- celda {i} (code) ---\n{src}")
        elif kind == "markdown" and keep_markdown:
            commented = "\n".join(f"# {ln}" for ln in src.splitlines())
            chunks.append(f"# --- celda {i} (markdown) ---\n{commented}")
    return "\n\n".join(chunks) if chunks else "[notebook vacio]"


def dump_file(path: Path, root: Path, max_lines: int) -> str:
    rel = path.relative_to(root).as_posix() if path.is_relative_to(root) else str(path)
    lang = LANG_BY_EXT.get(path.suffix, "")
    if path.suffix == ".ipynb":
        content = notebook_code(path)
    else:
        content = read_text(path)
    lines = content.splitlines()
    truncated = False
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        truncated = True
    width = len(str(len(lines)))
    numbered = "\n".join(f"{i:>{width}}  {ln}" for i, ln in enumerate(lines, start=1))
    out = f"## Archivo: {rel}\n\n```{lang}\n{numbered}\n```"
    if truncated:
        out += f"\n\n> Truncado en {max_lines} lineas. Usa `-n 0` para el archivo completo."
    return out


# --------------------------------------------------------------------------
# Portapapeles (Windows / macOS / Linux)
# --------------------------------------------------------------------------

def to_clipboard(text: str) -> str | None:
    try:
        if sys.platform == "win32":
            data = b"\xff\xfe" + text.encode("utf-16-le")   # BOM + UTF-16LE
            subprocess.run("clip", input=data, check=True, shell=True)
            return "clip"
        if sys.platform == "darwin":
            subprocess.run("pbcopy", input=text.encode("utf-8"), check=True)
            return "pbcopy"
        for cmd in (["wl-copy"], ["xclip", "-selection", "clipboard"]):
            try:
                subprocess.run(cmd, input=text.encode("utf-8"), check=True)
                return cmd[0]
            except (OSError, subprocess.SubprocessError):
                continue
    except (OSError, subprocess.SubprocessError):
        return None
    return None


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(
        description="Genera un snapshot compacto del proyecto para pegar en el chat.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("archivos", nargs="*", help="Archivos a volcar completos.")
    ap.add_argument("-t", "--tarea", default="", help="Tarea en curso.")
    ap.add_argument("-n", "--lineas", type=int, default=400,
                    help="Maximo de lineas por archivo (0 = sin limite).")
    ap.add_argument("-d", "--depth", type=int, default=3, help="Profundidad del arbol.")
    ap.add_argument("--all", action="store_true", help="Incluir todo el codigo de SRC_DIRS.")
    ap.add_argument("--out", default=None, help="Ruta de salida.")
    ap.add_argument("--no-clip", action="store_true", help="No copiar al portapapeles.")
    ap.add_argument("--list", action="store_true", help="Solo listar archivos de codigo.")
    args = ap.parse_args()

    root = find_root()

    if args.list:
        for f in iter_code_files(root):
            print(f"{count_lines(f):>6}  {f.relative_to(root).as_posix()}")
        return 0

    targets: list[Path] = []
    if args.all:
        targets = iter_code_files(root)
    for raw in args.archivos:
        p = Path(raw)
        p = p if p.is_absolute() else (root / raw)
        p = p.resolve()
        if p.is_file():
            if p not in targets:
                targets.append(p)
        else:
            print(f"  aviso: no existe -> {raw}", file=sys.stderr)

    parts: list[str] = [
        f"# Snapshot — {root.name} — {datetime.now():%Y-%m-%d %H:%M}",
    ]
    if args.tarea:
        parts.append(f"**Tarea en curso:** {args.tarea}")

    estado = root / ESTADO_FILE
    if estado.is_file():
        parts.append("## Estado del proyecto\n\n" + read_text(estado).strip())

    parts.append(f"## Estructura\n\n```\n{build_tree(root, args.depth)}\n```")

    git_section = build_git_section(root)
    if git_section:
        parts.append(f"## Git\n\n```\n{git_section}\n```")

    parts.append(f"## Inventario de codigo (lineas por archivo)\n\n```\n{build_inventory(root)}\n```")

    for f in targets:
        parts.append(dump_file(f, root, args.lineas))

    report = "\n\n".join(parts) + "\n"

    out_path = Path(args.out) if args.out else root / "snapshot.md"
    out_path.write_text(report, encoding="utf-8")

    approx = len(report) // CHARS_PER_TOKEN
    print(f"Escrito: {out_path}")
    print(f"Tamano: {len(report):,} caracteres  (~{approx:,} tokens)")
    if approx > TOKEN_WARN:
        print(f"  AVISO: supera {TOKEN_WARN:,} tokens. Recorta archivos o usa -n 200.",
              file=sys.stderr)

    if not args.no_clip:
        used = to_clipboard(report)
        print(f"Copiado al portapapeles ({used})." if used
              else "No se pudo copiar; abre el archivo manualmente.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())