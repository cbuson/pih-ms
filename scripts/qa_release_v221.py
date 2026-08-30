#!/usr/bin/env python3
"""Auditoria reproduzível da interface e do pacote PIH MS V2.2.1."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


class AuditHTML(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.help_sections = 0
        self.modals: list[dict[str, str | None]] = []
        self.map_buttons: list[dict[str, str | None]] = []
        self.in_topnav = False
        self.topnav_depth = 0
        self.topnav_direct: list[tuple[str, str | None]] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        attributes = dict(attrs)
        if attributes.get("id"):
            self.ids.append(attributes["id"])
        classes = set((attributes.get("class") or "").split())
        if tag == "nav" and "topnav" in classes:
            self.in_topnav = True
            self.topnav_depth = 1
            return
        if self.in_topnav:
            if self.topnav_depth == 1 and tag in {"button", "div"}:
                self.topnav_direct.append((tag, attributes.get("id")))
            if tag not in {"meta", "link", "img", "input", "br", "hr"}:
                self.topnav_depth += 1
        if "help-section" in classes:
            self.help_sections += 1
        if "modal" in classes:
            self.modals.append(attributes)
        if attributes.get("id") in {"fitState", "zoomIn", "zoomOut", "locateMe", "clearOptional", "baseMapButton"}:
            self.map_buttons.append(attributes)

    def handle_endtag(self, tag: str) -> None:
        if self.in_topnav:
            self.topnav_depth -= 1
            if self.topnav_depth == 0:
                self.in_topnav = False


assert (ROOT / "VERSION").read_text(encoding="utf-8").strip() == "2.2.1"

index_text = (DOCS / "index.html").read_text(encoding="utf-8")
parser = AuditHTML()
parser.feed(index_text)
duplicates = {value for value in parser.ids if parser.ids.count(value) > 1}
assert not duplicates, f"IDs duplicados {sorted(duplicates)}"
assert parser.help_sections == 18
assert all(modal.get("role") == "dialog" and modal.get("aria-modal") == "true" for modal in parser.modals)
assert all(button.get("aria-label") for button in parser.map_buttons)

top_level_controls = [item for item in parser.topnav_direct if item[0] in {"button", "div"}]
assert len(top_level_controls) == 7, top_level_controls
for required in ("navMap", "navExplore", "navStatistics", "navWellSearch", "navDocumentation", "statsModal", "helpModal", "authorModal"):
    assert required in parser.ids
assert "dataModal" not in parser.ids
assert "AGPL-3.0-or-later" in index_text
assert "0000-0002-1446-2252" in index_text
assert "0000-0002-1027-0288" in index_text

statistics = json.loads((DOCS / "data/statistics/statistics_v221.json").read_text(encoding="utf-8"))
assert statistics["version"] == "2.2.1"
assert statistics["dataset_count"] == 11 == len(statistics["datasets"])
assert {item["id"] for item in statistics["datasets"]} == {
    "effective_global", "effective_scale", "grid_evidence", "independence_global",
    "independence_scale", "scale_candidate", "maup_origin", "maup_variant",
    "spatial_structure", "stratified", "vertical_temporal",
}
for dataset in statistics["datasets"]:
    assert (ROOT / dataset["source"]).exists()
    assert dataset["row_count"] == len(dataset["rows"])
assert all("previous" not in item["source"] for item in statistics["datasets"])

details = json.loads((DOCS / "data/well_details.json").read_text(encoding="utf-8"))
manifest = json.loads((DOCS / "data/well_details_shards/manifest.json").read_text(encoding="utf-8"))
shard_paths = sorted((DOCS / "data/well_details_shards").glob("[0-9][0-9].json"))
assert manifest["shard_count"] == 64 == len(shard_paths)
assert manifest["well_count"] == 3877 == len(details)
sharded: dict[str, object] = {}
for path in shard_paths:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert not set(sharded).intersection(payload)
    sharded.update(payload)
    assert path.stat().st_size < 1_000_000
assert set(sharded) == set(details)
assert sum(manifest["counts"].values()) == 3877

coverage = {
    "scale_study": {100, 150, 250, 500, 1000},
    "stratified_scale": {100, 150, 250, 500, 1000},
    "independence_redundancy": {100, 150, 250, 500, 1000},
    "effective_knowledge": {100, 150, 250, 500, 1000},
    "grid_evidence": {250, 500, 1000},
    "spatial_structure": {250, 500, 1000},
}
patterns = {
    "scale_study": "scale_primary_{scale}km2.geojson",
    "stratified_scale": "stratified_scale_{scale}km2.geojson",
    "independence_redundancy": "independence_redundancy_{scale}km2.geojson",
    "effective_knowledge": "effective_knowledge_{scale}km2.geojson",
    "grid_evidence": "malha_evidencia_{scale}km2.geojson",
    "spatial_structure": "spatial_structure_{scale}km2.geojson",
}
for folder, scales in coverage.items():
    found = {
        scale for scale in (100, 150, 250, 500, 1000)
        if (DOCS / f"data/{folder}" / patterns[folder].format(scale=scale)).exists()
    }
    assert found == scales, (folder, found)

ET.parse(DOCS / "assets/img/mi-posicao-ms.svg")
assert (ROOT / "LICENSE").read_text(encoding="utf-8").count("GNU AFFERO GENERAL PUBLIC LICENSE") >= 1
assert "CC BY-NC-SA 4.0" in (ROOT / "LICENSE-CONTENT.md").read_text(encoding="utf-8")
assert (ROOT / "BACKLOG_CIENTIFICO_POS_V221.md").exists()
assert (ROOT / "AUDITORIA_NAVEGACAO_USABILIDADE_V221.md").exists()

subprocess.run(["node", "--check", str(DOCS / "assets/js/pih.js")], check=True)

old_checksums = {}
for line in (ROOT / "SHA256SUMS_V22.txt").read_text(encoding="utf-8").splitlines():
    digest, relative = line.split("  ", 1)
    old_checksums[relative] = digest
scientific_prefixes = ("data/derived/", "data/source/", "methodology/")
scientific_files = [path for path in old_checksums if path.startswith(scientific_prefixes)]
assert scientific_files
for relative in scientific_files:
    path = ROOT / relative
    assert path.exists() and sha256(path) == old_checksums[relative], relative

print("OK V2.2.1")
print("7 acessos principais, 18 temas de ajuda, 11 resumos, 64 fragmentos e 3877 fichas")
print(f"{len(scientific_files)} arquivos científicos preservados em relação à V2.2")

