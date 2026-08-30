#!/usr/bin/env python3
"""Atualiza manifestos de integridade da entrega PIH MS V2.2."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROVENANCE = ROOT / "provenance"
EFFECTIVE = ROOT / "data/derived/effective_knowledge"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


effective_files = sorted(
    [path for path in EFFECTIVE.iterdir() if path.is_file()]
    + [path for path in (ROOT / "docs/data/effective_knowledge").iterdir() if path.is_file()]
    + [
        ROOT / "ESTUDO_CONHECIMENTO_HIDROGEOLOGICO_EFETIVO_V1.md",
        ROOT / "methodology/CONHECIMENTO_HIDROGEOLOGICO_EFETIVO_V1.md",
        ROOT / "methodology/CONHECIMENTO_HIDROGEOLOGICO_EFETIVO_CAMPOS_V1.csv",
        ROOT / "PIH_MS_CONHECIMENTO_HIDROGEOLOGICO_EFETIVO_V1.xlsx",
        ROOT / "PIH_MS_WELL_EFFECTIVE_KNOWLEDGE.csv",
        ROOT / "PIH_MS_EFFECTIVE_KNOWLEDGE_GLOBAL_SUMMARY.csv",
        ROOT / "PIH_MS_EFFECTIVE_KNOWLEDGE_SCALE_SUMMARY.csv",
    ]
)
with (PROVENANCE / "effective_knowledge_manifest.csv").open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=["path", "size_bytes", "sha256", "method_version"])
    writer.writeheader()
    for path in effective_files:
        writer.writerow(
            {
                "path": relative(path),
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
                "method_version": "PIH_MS_V2.2_CHE_V1",
            }
        )

excluded_manifest = {"provenance/file_manifest.json", "SHA256SUMS_V22.txt"}
all_files = sorted(path for path in ROOT.rglob("*") if path.is_file())
manifest_files = [path for path in all_files if relative(path) not in excluded_manifest]
payload = {
    "project": "PIH MS",
    "version": "2.2",
    "manifest_scope": "Todos os arquivos, exceto este manifesto e SHA256SUMS_V22.txt",
    "files": [
        {"file": relative(path), "sha256": sha256(path), "bytes": path.stat().st_size}
        for path in manifest_files
    ],
}
(PROVENANCE / "file_manifest.json").write_text(
    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)

all_files = sorted(path for path in ROOT.rglob("*") if path.is_file() and relative(path) != "SHA256SUMS_V22.txt")
checksum_lines = [f"{sha256(path)}  {relative(path)}" for path in all_files]
(ROOT / "SHA256SUMS_V22.txt").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")
print(f"OK {len(manifest_files)} arquivos no manifesto, {len(all_files)} checksums")
