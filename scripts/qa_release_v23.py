#!/usr/bin/env python3
"""Auditoria reproduzível do pacote PIH MS V2.3."""
from __future__ import annotations

import json
import subprocess
from html.parser import HTMLParser
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SCALES = (100, 150, 250, 500, 1000)
CODES = tuple(f"E{i:02d}" for i in range(1, 13))
EXPECTED_CELLS = {100: 3763, 150: 2525, 250: 1537, 500: 791, 1000: 413}
EXPECTED_EVIDENCE = {
    "E01": 3877, "E02": 3414, "E03": 3097, "E04": 3213,
    "E05": 3180, "E06": 3051, "E07": 1106, "E08": 1096,
    "E09": 51, "E10": 2053, "E11": 1637, "E12": 1823,
}


class AuditHTML(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.options: dict[str, set[str]] = {}
        self.current_select: str | None = None
        self.ids: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        attributes = dict(attrs)
        if attributes.get("id"):
            self.ids.append(attributes["id"])
        if tag == "select" and attributes.get("id"):
            self.current_select = attributes["id"]
            self.options[self.current_select] = set()
        elif tag == "option" and self.current_select and attributes.get("value"):
            self.options[self.current_select].add(attributes["value"])

    def handle_endtag(self, tag: str) -> None:
        if tag == "select":
            self.current_select = None


assert (ROOT / "VERSION").read_text(encoding="utf-8").strip() == "2.3"
index = (DOCS / "index.html").read_text(encoding="utf-8")
parser = AuditHTML()
parser.feed(index)
assert not {value for value in parser.ids if parser.ids.count(value) > 1}
for select in ("gridEvidenceScale", "spatialScale"):
    assert parser.options[select] == {str(value) for value in SCALES}
assert "PIH MS V2.3" in index

for scale, expected_cells in EXPECTED_CELLS.items():
    grid_csv = ROOT / f"data/derived/grid_evidence/malha_evidencia_{scale}km2.csv"
    spatial_csv = ROOT / f"data/derived/spatial_structure/spatial_structure_{scale}km2.csv"
    grid = pd.read_csv(grid_csv)
    spatial = pd.read_csv(spatial_csv)
    assert len(grid) == len(spatial) == expected_cells
    assert set(grid.cell_id) == set(spatial.cell_id)
    assert set(grid.grid_family) == {"SCALE_PRIMARY_O00_V1"}
    assert set(spatial.grid_family) == {"SCALE_PRIMARY_O00_V1"}
    for code, expected in EXPECTED_EVIDENCE.items():
        assert int(grid[f"n_{code}"].sum()) == expected
    for folder, stem in (
        ("grid_evidence", "malha_evidencia"),
        ("spatial_structure", "spatial_structure"),
    ):
        path = DOCS / f"data/{folder}/{stem}_{scale}km2.geojson"
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert len(payload["features"]) == expected_cells
        for position in (0, expected_cells // 2, expected_cells - 1):
            properties = payload["features"][position]["properties"]
            assert properties["cell_id"]
            assert int(properties["scale_km2"]) == scale
            assert properties["grid_family"] == "SCALE_PRIMARY_O00_V1"

statistics = json.loads((DOCS / "data/statistics/statistics_v221.json").read_text(encoding="utf-8"))
assert statistics["version"] == "2.3"
for dataset_id in ("grid_evidence", "spatial_structure"):
    dataset = next(item for item in statistics["datasets"] if item["id"] == dataset_id)
    assert dataset["row_count"] == 5

details = json.loads((DOCS / "data/well_details.json").read_text(encoding="utf-8"))
manifest = json.loads((DOCS / "data/well_details_shards/manifest.json").read_text(encoding="utf-8"))
assert len(details) == manifest["well_count"] == 3877
assert manifest["version"] == "2.3"
sharded = {}
for path in sorted((DOCS / "data/well_details_shards").glob("[0-9][0-9].json")):
    part = json.loads(path.read_text(encoding="utf-8"))
    assert not set(sharded).intersection(part)
    sharded.update(part)
assert set(sharded) == set(details)

javascript = (DOCS / "assets/js/pih.js").read_text(encoding="utf-8")
for token in ("showGridEvidence", "showSpatialStructure", "openActiveCellAt", "openGridEvidenceFeature", "openSpatialStructureFeature"):
    assert token in javascript
subprocess.run(["node", "--check", str(DOCS / "assets/js/pih.js")], check=True)

print("OK V2.3")
print("5 escalas em evidência e estrutura espacial, 12 somas preservadas e 3877 fichas")
