#!/usr/bin/env python3
"""Atualiza manifestos de integridade da entrega PIH MS V2.2.1."""
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


ui_files = [
    ROOT / "docs/index.html",
    ROOT / "docs/assets/css/pih.css",
    ROOT / "docs/assets/js/pih.js",
    ROOT / "docs/assets/img/mi-posicao-ms.svg",
    ROOT / "docs/data/statistics/statistics_v221.json",
    ROOT / "docs/autoria-direitos.html",
    ROOT / "docs/licenca-conteudos.html",
    ROOT / "LICENSE",
    ROOT / "LICENSE-CONTENT.md",
    ROOT / "AUDITORIA_NAVEGACAO_USABILIDADE_V221.md",
    ROOT / "BACKLOG_CIENTIFICO_POS_V221.md",
] + sorted((ROOT / "docs/data/well_details_shards").glob("*.json"))
with (PROVENANCE / "ui_v221_manifest.csv").open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=["path", "size_bytes", "sha256", "release"])
    writer.writeheader()
    for path in ui_files:
        writer.writerow({"path": relative(path), "size_bytes": path.stat().st_size, "sha256": sha256(path), "release": "PIH_MS_V2.2.1_UI"})

excluded_manifest = {"provenance/file_manifest.json", "SHA256SUMS_V221.txt"}
all_files = sorted(path for path in ROOT.rglob("*") if path.is_file())
manifest_files = [path for path in all_files if relative(path) not in excluded_manifest]
payload = {
    "project": "PIH MS",
    "version": "2.2.1",
    "scientific_content_version": "2.2",
    "release_scope": "Navegação, usabilidade, acesso, autoria e licenças",
    "manifest_scope": "Todos os arquivos, exceto este manifesto e SHA256SUMS_V221.txt",
    "files": [
        {"file": relative(path), "sha256": sha256(path), "bytes": path.stat().st_size}
        for path in manifest_files
    ],
}
(PROVENANCE / "file_manifest.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

all_files = sorted(path for path in ROOT.rglob("*") if path.is_file() and relative(path) != "SHA256SUMS_V221.txt")
checksum_lines = [f"{sha256(path)}  {relative(path)}" for path in all_files]
(ROOT / "SHA256SUMS_V221.txt").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")
print(f"OK {len(manifest_files)} arquivos no manifesto, {len(all_files)} checksums")

