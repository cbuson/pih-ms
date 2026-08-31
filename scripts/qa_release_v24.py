#!/usr/bin/env python3
"""Auditoria reproduzível do pacote PIH MS V2.4."""
from __future__ import annotations

import json
import subprocess
from html.parser import HTMLParser
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DATA = ROOT / "data/derived/question_sufficiency"
SCALES = (100, 150, 250, 500, 1000)
QUESTIONS = tuple(f"Q{i:02d}" for i in range(1, 6))
EXPECTED_CELLS = {100: 3763, 150: 2525, 250: 1537, 500: 791, 1000: 413}


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


assert (ROOT / "VERSION").read_text(encoding="utf-8").strip() == "2.4"
index = (DOCS / "index.html").read_text(encoding="utf-8")
parser = AuditHTML()
parser.feed(index)
assert not {value for value in parser.ids if parser.ids.count(value) > 1}
for select in ("gridEvidenceScale", "spatialScale", "qsScale"):
    assert parser.options[select] == {str(value) for value in SCALES}
assert parser.options["qsQuestion"] == set(QUESTIONS)
for token in (
    "PIH MS V2.4",
    "Suficiência por pergunta",
    "13 resumos vigentes",
    "metodologia-suficiencia-pergunta.html",
):
    assert token in index

registry = pd.read_csv(DATA / "question_registry.csv")
requirements = pd.read_csv(DATA / "question_requirement_matrix.csv")
dimension_roles = pd.read_csv(DATA / "dimension_dependency_matrix.csv")
well_question = pd.read_csv(DATA / "well_question_sufficiency_long.csv")
well_requirement = pd.read_csv(DATA / "well_requirement_status_long.csv")
cell_question = pd.read_csv(DATA / "cell_question_sufficiency_long.csv")
pairwise = pd.read_csv(DATA / "question_dependency_pairwise.csv")
global_summary = pd.read_csv(DATA / "question_global_summary.csv")
scale_summary = pd.read_csv(DATA / "question_scale_summary.csv")

assert set(registry.question_code) == set(QUESTIONS)
assert len(registry) == len(global_summary) == 5
assert len(requirements) == 39
assert len(dimension_roles) == 45
assert len(well_question) == 19385
assert len(well_requirement) == 151203
assert len(cell_question) == 45145
assert len(pairwise) == 153
assert len(scale_summary) == 25
assert well_question.well_id.nunique() == 3877
assert not well_question.minimum_documentary_met.astype(bool).any()
assert int(global_summary.minimum_documentary_n.sum()) == 0
assert int(global_summary.representative_wells_n.sum()) == 0
assert not global_summary.weights_used.astype(bool).any()
assert not global_summary.score_used.astype(bool).any()
assert cell_question.cell_representativeness_state.str.startswith("UNKNOWN").all()
assert not cell_question.universal_well_count_threshold_used.astype(bool).any()
assert not cell_question.weight_used.astype(bool).any()
assert not cell_question.score_used.astype(bool).any()

for scale, expected_cells in EXPECTED_CELLS.items():
    csv_path = DATA / f"question_sufficiency_{scale}km2.csv"
    geojson_path = DATA / f"question_sufficiency_{scale}km2.geojson"
    copied_path = DOCS / f"data/question_sufficiency/question_sufficiency_{scale}km2.geojson"
    table = pd.read_csv(csv_path)
    payload = json.loads(geojson_path.read_text(encoding="utf-8"))
    copied = json.loads(copied_path.read_text(encoding="utf-8"))
    assert len(table) == len(payload["features"]) == len(copied["features"]) == expected_cells
    assert set(table.grid_family) == {"SCALE_PRIMARY_O00_V1"}
    assert set(table.cell_id) == {item["properties"]["cell_id"] for item in payload["features"]}
    for code in QUESTIONS:
        prefix = code.lower()
        assert int(table[f"{prefix}_minimum_documentary_n"].sum()) == 0
        assert table[f"{prefix}_cell_representativeness_state"].str.startswith("UNKNOWN").all()

statistics = json.loads((DOCS / "data/statistics/statistics_v221.json").read_text(encoding="utf-8"))
assert statistics["version"] == "2.4"
assert statistics["dataset_count"] == 13
assert {item["id"] for item in statistics["datasets"]}.issuperset({"question_global", "question_scale"})

details = json.loads((DOCS / "data/well_details.json").read_text(encoding="utf-8"))
manifest = json.loads((DOCS / "data/well_details_shards/manifest.json").read_text(encoding="utf-8"))
assert len(details) == manifest["well_count"] == 3877
assert manifest["version"] == "2.4"
assert all(set(record.get("question_sufficiency", {})) == set(QUESTIONS) for record in details.values())
sharded = {}
for path in sorted((DOCS / "data/well_details_shards").glob("[0-9][0-9].json")):
    part = json.loads(path.read_text(encoding="utf-8"))
    assert not set(sharded).intersection(part)
    sharded.update(part)
assert set(sharded) == set(details)
assert all(set(record.get("question_sufficiency", {})) == set(QUESTIONS) for record in sharded.values())

dictionary = pd.read_csv(ROOT / "methodology/DICIONARIO_METRICAS_RESULTADOS_V1.csv")
bibliography = pd.read_csv(ROOT / "methodology/BIBLIOGRAFIA_MASTER_V1.csv")
assert len(dictionary) == 788
assert len(bibliography) == 55
assert "BR01" in set(bibliography.id)

javascript = (DOCS / "assets/js/pih.js").read_text(encoding="utf-8")
for token in (
    "showQuestionSufficiency",
    "openQuestionSufficiencyFeature",
    "questionSufficiencyFicha",
    "qs100",
    "qs150",
    "qs250",
    "qs500",
    "qs1000",
    "ge100",
    "ge150",
    "se100",
    "se150",
):
    assert token in javascript
subprocess.run(["node", "--check", str(DOCS / "assets/js/pih.js")], check=True)

for path in (
    ROOT / "ESTUDO_SUFICIENCIA_POR_PERGUNTA_V1.md",
    ROOT / "methodology/SUFICIENCIA_POR_PERGUNTA_V1.md",
    DOCS / "metodologia-suficiencia-pergunta.html",
):
    assert path.exists() and path.stat().st_size > 1000

print("OK V2.4")
print("5 perguntas, 5 escalas, 3877 poços, 45145 pares célula-pergunta e 13 resumos")
