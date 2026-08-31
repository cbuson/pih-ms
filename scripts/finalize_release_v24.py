#!/usr/bin/env python3
"""Atualiza os manifestos de integridade da entrega PIH MS V2.4."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROVENANCE = ROOT / "provenance"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def publishable(path: Path) -> bool:
    relative_parts = path.relative_to(ROOT).parts
    return (
        path.is_file()
        and "__pycache__" not in relative_parts
        and not any(part.startswith(".") for part in relative_parts)
        and path.suffix != ".pyc"
    )


PROVENANCE.mkdir(parents=True, exist_ok=True)

ui_files = [
    ROOT / "VERSION",
    ROOT / "docs/index.html",
    ROOT / "docs/assets/css/pih.css",
    ROOT / "docs/assets/js/pih.js",
    ROOT / "docs/assets/img/mi-posicao-ms.svg",
    ROOT / "docs/data/statistics/statistics_v221.json",
    ROOT / "docs/autoria-direitos.html",
    ROOT / "docs/licenca-conteudos.html",
    ROOT / "docs/metodologia-suficiencia-pergunta.html",
    ROOT / "docs/guia-resultados.html",
    ROOT / "LICENSE",
    ROOT / "LICENSE-CONTENT.md",
    ROOT / "README.md",
    ROOT / "ESTUDO_SUFICIENCIA_POR_PERGUNTA_V1.md",
    ROOT / "AUDITORIA_SUFICIENCIA_POR_PERGUNTA_V24.md",
    ROOT / "PIH_MS_SUFICIENCIA_POR_PERGUNTA_V1.xlsx",
] + sorted((ROOT / "docs/data/question_sufficiency").glob("*")) + sorted(
    (ROOT / "docs/data/well_details_shards").glob("*.json")
)

missing = [relative(path) for path in ui_files if not path.is_file()]
if missing:
    raise FileNotFoundError(f"Arquivos ausentes no manifesto V2.4: {missing}")

with (PROVENANCE / "ui_v24_manifest.csv").open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=["path", "size_bytes", "sha256", "release"])
    writer.writeheader()
    for path in ui_files:
        writer.writerow(
            {
                "path": relative(path),
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
                "release": "PIH_MS_V2.4_SUFICIENCIA_POR_PERGUNTA",
            }
        )

excluded_manifest = {"provenance/file_manifest.json", "SHA256SUMS_V24.txt"}
all_files = sorted(path for path in ROOT.rglob("*") if publishable(path))
manifest_files = [path for path in all_files if relative(path) not in excluded_manifest]
payload = {
    "project": "PIH MS",
    "version": "2.4",
    "scientific_content_version": "2.4",
    "release_scope": "Suficiencia documental nao compensatoria por pergunta hidrogeologica",
    "manifest_scope": "Todos os arquivos publicaveis, exceto este manifesto e SHA256SUMS_V24.txt",
    "files": [
        {"file": relative(path), "sha256": sha256(path), "bytes": path.stat().st_size}
        for path in manifest_files
    ],
}
(PROVENANCE / "file_manifest.json").write_text(
    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)

all_files = sorted(path for path in ROOT.rglob("*") if publishable(path))
checksum_files = [path for path in all_files if relative(path) != "SHA256SUMS_V24.txt"]
checksum_lines = [f"{sha256(path)}  {relative(path)}" for path in checksum_files]
(ROOT / "SHA256SUMS_V24.txt").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")

print(f"OK {len(manifest_files)} arquivos no manifesto e {len(checksum_files)} checksums")
