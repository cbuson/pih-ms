#!/usr/bin/env python3
"""Atualiza manifestos e somas de integridade da entrega PIH MS V2.5."""
from __future__ import annotations

from pathlib import Path
import csv
import hashlib
import json


ROOT = Path(__file__).resolve().parents[1]
PROVENANCE = ROOT / "provenance"
MODULE = ROOT / "data/derived/stability_sensitivity"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


module_files = sorted(path for path in MODULE.iterdir() if path.is_file())
with (PROVENANCE / "stability_sensitivity_manifest_v25.csv").open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=["path", "size_bytes", "sha256", "release"])
    writer.writeheader()
    for path in module_files:
        writer.writerow({"path": relative(path), "size_bytes": path.stat().st_size, "sha256": sha256(path), "release": "PIH_MS_V2.5"})

excluded = {"provenance/file_manifest.json", "SHA256SUMS_V25.txt"}
all_files = sorted(path for path in ROOT.rglob("*") if path.is_file() and "__pycache__" not in path.parts)
manifest_files = [path for path in all_files if relative(path) not in excluded]
payload = {
    "project": "PIH MS",
    "version": "2.5",
    "scientific_content_version": "2.5",
    "release_scope": "Estabilidade entre escalas, sensibilidade à origem e persistência dos bloqueios por pergunta",
    "manifest_scope": "Todos os arquivos, exceto este manifesto, SHA256SUMS_V25.txt e caches Python",
    "files": [
        {"file": relative(path), "sha256": sha256(path), "bytes": path.stat().st_size}
        for path in manifest_files
    ],
}
(PROVENANCE / "file_manifest.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

checksum_files = sorted(path for path in ROOT.rglob("*") if path.is_file() and "__pycache__" not in path.parts and relative(path) != "SHA256SUMS_V25.txt")
(ROOT / "SHA256SUMS_V25.txt").write_text(
    "\n".join(f"{sha256(path)}  {relative(path)}" for path in checksum_files) + "\n",
    encoding="utf-8",
)
print(f"OK {len(module_files)} arquivos V2.5, {len(manifest_files)} arquivos no manifesto e {len(checksum_files)} checksums")
