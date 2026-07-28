#!/usr/bin/env python3
"""Build every figure in the thesis from its source directory.

Layout contract
---------------
A figure is a directory named for the figure, holding exactly one entry point:

    <name>/render.py      matplotlib figure
    <name>/render.tex     standalone TikZ figure

Output goes to the ``fig/`` directory beside the figure directory's parent:

    chapters/03-methods/settling_time/render.py
        -> chapters/03-methods/fig/settling_time.pdf
        -> chapters/03-methods/fig/settling_time.png

so a chapter includes its own figures with ``\\includegraphics{fig/settling_time}``.
The PDF is what the document includes. The PNG exists for render inspection and
the reviewer pass.

Shared styling lives beside this script at the project root: ``plot_defaults.py``
for matplotlib, ``tikz_defaults.tex`` for TikZ, and the generated
``tikz_colours.tex`` that carries one palette into both. Nothing registers a
figure; adding the directory is what adds the figure.

Usage
-----
    python build_figures.py                 build everything that is stale
    python build_figures.py --force         rebuild everything
    python build_figures.py --only NAME     build one figure, repeatable
    python build_figures.py --list          list discovered figures and exit
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PY_ENTRY = "render.py"
TEX_ENTRY = "render.tex"
OUTPUT_DIR = "fig"
# Dot-directories are skipped by the walk filter, so none are listed here.
SKIP_DIRS = {OUTPUT_DIR, "venv", "env", "__pycache__", "node_modules", "_build", "build"}
STYLE_SOURCES = ("plot_defaults.py", "tikz_defaults.tex", "tikz_colours.tex")


class BuildError(RuntimeError):
    """A figure failed to build."""


def discover(root: Path) -> list[Path]:
    """Return every figure directory under root, sorted by path."""
    found: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(
            name for name in dirnames
            if name not in SKIP_DIRS and not name.startswith(".")
        )
        has_py = PY_ENTRY in filenames
        has_tex = TEX_ENTRY in filenames
        if has_py and has_tex:
            raise BuildError(
                f"{dirpath}: contains both {PY_ENTRY} and {TEX_ENTRY}; a figure has one entry point"
            )
        if has_py or has_tex:
            found.append(Path(dirpath))
    return sorted(found)


def entry_point(figure_dir: Path) -> Path:
    for name in (PY_ENTRY, TEX_ENTRY):
        candidate = figure_dir / name
        if candidate.exists():
            return candidate
    raise BuildError(f"{figure_dir}: no {PY_ENTRY} or {TEX_ENTRY}")


def output_stem(figure_dir: Path) -> Path:
    return figure_dir.parent / OUTPUT_DIR / figure_dir.name


def newest_style_mtime() -> float:
    times = [(ROOT / name).stat().st_mtime for name in STYLE_SOURCES if (ROOT / name).exists()]
    return max(times, default=0.0)


def is_stale(figure_dir: Path, stem: Path, style_mtime: float) -> bool:
    pdf = stem.with_suffix(".pdf")
    if not pdf.exists():
        return True
    target = pdf.stat().st_mtime
    if style_mtime > target:
        return True
    return any(
        path.stat().st_mtime > target
        for path in figure_dir.rglob("*")
        if path.is_file()
    )


def dpi() -> int:
    sys.path.insert(0, str(ROOT))
    try:
        import plot_defaults  # type: ignore
        return int(plot_defaults.DPI)
    except Exception:
        return 300
    finally:
        sys.path.pop(0)


def regenerate_tikz_colours() -> None:
    """Re-emit tikz_colours.tex from the matplotlib palette when the palette changed.

    The write is content-conditional. Touching the file on every run would make
    its mtime beat every built figure, so nothing would ever be current.
    """
    if not (ROOT / "plot_defaults.py").exists():
        return
    sys.path.insert(0, str(ROOT))
    try:
        import plot_defaults  # type: ignore
        writer = getattr(plot_defaults, "write_tikz_colours", None)
        if writer is None:
            return
        target = ROOT / "tikz_colours.tex"
        staging = ROOT / "tikz_colours.tex.new"
        writer(str(staging))
        fresh = staging.read_text(encoding="utf-8")
        if not target.exists() or target.read_text(encoding="utf-8") != fresh:
            target.write_text(fresh, encoding="utf-8")
        staging.unlink(missing_ok=True)
    finally:
        sys.path.pop(0)


def run(command: list[str], cwd: Path, env: dict[str, str] | None = None) -> None:
    result = subprocess.run(
        command, cwd=cwd, env=env,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if result.returncode != 0:
        detail = (result.stdout or "") + (result.stderr or "")
        raise BuildError(f"{' '.join(command)} failed in {cwd}:\n{detail.strip()}")


def build_python(figure_dir: Path, stem: Path) -> None:
    env = dict(os.environ)
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(ROOT) + (os.pathsep + existing if existing else "")
    env["MPLBACKEND"] = "Agg"
    run([sys.executable, PY_ENTRY, str(stem)], cwd=figure_dir, env=env)
    missing = [
        suffix for suffix in (".pdf", ".png")
        if not stem.with_suffix(suffix).exists()
    ]
    if missing:
        raise BuildError(
            f"{figure_dir/PY_ENTRY}: produced no {', '.join(missing)}. "
            f"Save through plot_defaults.savefig(fig, sys.argv[1])."
        )


def build_tikz(figure_dir: Path, stem: Path) -> None:
    if shutil.which("pdflatex") is None:
        raise BuildError("pdflatex is not on PATH")
    env = dict(os.environ)
    env["TEXINPUTS"] = str(ROOT) + os.pathsep + env.get("TEXINPUTS", "")
    run(
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", TEX_ENTRY],
        cwd=figure_dir, env=env,
    )
    produced = figure_dir / "render.pdf"
    if not produced.exists():
        raise BuildError(f"{figure_dir/TEX_ENTRY}: pdflatex produced no PDF")
    shutil.move(str(produced), str(stem.with_suffix(".pdf")))
    for leftover in ("render.aux", "render.log", "render.out"):
        (figure_dir / leftover).unlink(missing_ok=True)
    rasterise(stem.with_suffix(".pdf"), stem.with_suffix(".png"))


def rasterise(pdf: Path, png: Path) -> None:
    """Write a PNG beside the PDF for inspection and review."""
    resolution = dpi()
    try:
        import fitz  # type: ignore

        with fitz.open(pdf) as document:
            document[0].get_pixmap(dpi=resolution).save(png)
        return
    except ImportError:
        pass
    if shutil.which("pdftoppm") is not None:
        run(
            ["pdftoppm", "-png", "-r", str(resolution), "-singlefile",
             pdf.name, png.with_suffix("").name],
            cwd=pdf.parent,
        )
        return
    raise BuildError(
        f"{pdf}: cannot rasterise. Install PyMuPDF (pip install pymupdf) or poppler's pdftoppm. "
        f"The PDF was built; only the review PNG is missing."
    )


def build_one(figure_dir: Path) -> Path:
    source = entry_point(figure_dir)
    stem = output_stem(figure_dir)
    stem.parent.mkdir(parents=True, exist_ok=True)
    if source.name == PY_ENTRY:
        build_python(figure_dir, stem)
    else:
        build_tikz(figure_dir, stem)
    return stem


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=ROOT, help="project directory to scan")
    parser.add_argument("--only", action="append", default=[], metavar="NAME", help="build only this figure; repeatable")
    parser.add_argument("--force", action="store_true", help="rebuild even when outputs are current")
    parser.add_argument("--list", action="store_true", help="list discovered figures and exit")
    args = parser.parse_args()

    try:
        figures = discover(args.root.resolve())
    except BuildError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    if args.only:
        wanted = set(args.only)
        figures = [path for path in figures if path.name in wanted]
        unknown = wanted - {path.name for path in figures}
        if unknown:
            print(f"error: no such figure: {', '.join(sorted(unknown))}", file=sys.stderr)
            return 2

    if args.list:
        for figure_dir in figures:
            print(f"{figure_dir.name}\t{entry_point(figure_dir).name}\t{output_stem(figure_dir)}")
        return 0

    if not figures:
        print("no figures found")
        return 0

    regenerate_tikz_colours()
    style_mtime = newest_style_mtime()

    built: list[str] = []
    skipped: list[str] = []
    failures: list[tuple[str, str]] = []

    for figure_dir in figures:
        stem = output_stem(figure_dir)
        if not args.force and not is_stale(figure_dir, stem, style_mtime):
            skipped.append(figure_dir.name)
            continue
        try:
            build_one(figure_dir)
            built.append(figure_dir.name)
        except BuildError as error:
            failures.append((figure_dir.name, str(error)))

    for name in built:
        print(f"built    {name}")
    for name in skipped:
        print(f"current  {name}")
    for name, detail in failures:
        print(f"FAILED   {name}\n{detail}\n", file=sys.stderr)

    print(f"\n{len(built)} built, {len(skipped)} current, {len(failures)} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
