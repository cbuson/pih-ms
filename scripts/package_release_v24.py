#!/usr/bin/env python3
"""Empacota a entrega independente PIH MS V2.4."""
from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT.parent.parent / "outputs/6b2168c6942b/pih-ms-v2.4-suficiencia-por-pergunta.zip"
TOP_LEVEL = "pih-ms-v2.4-suficiencia-por-pergunta"


def publishable(path: Path) -> bool:
    relative_parts = path.relative_to(ROOT).parts
    return (
        path.is_file()
        and "__pycache__" not in relative_parts
        and not any(part.startswith(".") for part in relative_parts)
        and path.suffix != ".pyc"
    )


OUTPUT.parent.mkdir(parents=True, exist_ok=True)
files = sorted(path for path in ROOT.rglob("*") if publishable(path))

with ZipFile(OUTPUT, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
    for path in files:
        archive.write(path, f"{TOP_LEVEL}/{path.relative_to(ROOT).as_posix()}")

print(f"OK {len(files)} arquivos em {OUTPUT}")

