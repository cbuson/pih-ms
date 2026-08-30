#!/usr/bin/env python3
"""Empacota a árvore auditada com nome externo de versão V2.2."""
from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT.parent.parent / "outputs/6b2168c6942b/pih-ms-v2.2-conhecimento-efetivo.zip"
TOP_LEVEL = "pih-ms-v2.2-conhecimento-efetivo"
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

files = sorted(path for path in ROOT.rglob("*") if path.is_file())
with ZipFile(OUTPUT, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
    for path in files:
        archive.write(path, f"{TOP_LEVEL}/{path.relative_to(ROOT).as_posix()}")

print(f"OK {len(files)} arquivos em {OUTPUT}")
