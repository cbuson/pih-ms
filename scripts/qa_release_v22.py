#!/usr/bin/env python3
"""Auditoria reproduzível dos produtos V2.2 antes do empacotamento."""
from __future__ import annotations

import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EFFECTIVE = ROOT / "data/derived/effective_knowledge"
SCALES = (100, 150, 250, 500, 1000)
EXPECTED_CELLS = {100: 3763, 150: 2525, 250: 1537, 500: 791, 1000: 413}
VECTOR_DIMENSIONS = {
    "espacial",
    "hidroestratigrafica",
    "vertical",
    "hidraulica",
    "hidroquimica",
    "temporal",
    "independencia",
    "qualidade_documental",
    "incerteza",
}
DETAIL_DIMENSIONS = {
    "spatial",
    "hydrostratigraphic",
    "vertical",
    "hydraulic",
    "hydrochemical",
    "temporal",
    "independence",
    "documentary_quality",
    "uncertainty",
}


def strict_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


class IdCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []

    def handle_starttag(self, tag, attrs):
        self.ids.extend(value for name, value in attrs if name == "id")


well = pd.read_csv(EFFECTIVE / "well_effective_knowledge.csv", dtype={"well_id": str})
canonical = pd.read_csv(
    ROOT / "data/derived/vertical_temporal/well_vertical_temporal.csv",
    dtype={"well_id": str},
)
assert well.shape == (3877, 56)
assert well["well_id"].is_unique
assert set(well["well_id"]) == set(canonical["well_id"])
assert set(well["independence_state"]) == {"UNKNOWN_INDEPENDENCIA_HIDROGEOLOGICA_NAO_DEMONSTRADA"}
assert well["vertical_capture_interval_status"].str.startswith("UNKNOWN").all()
assert well["temporal_time_series_status"].str.startswith("UNKNOWN").all()
assert not any(re.search(r"(^|_)(pih_score|priority_class|indice_pih)($|_)", name) for name in well.columns)
for value in well["dimension_vector_json"]:
    assert set(json.loads(value)) == VECTOR_DIMENSIONS

for scale in SCALES:
    current = pd.read_csv(EFFECTIVE / f"effective_knowledge_{scale}km2.csv")
    prior = pd.read_csv(ROOT / f"data/derived/independence_redundancy/independence_redundancy_{scale}km2.csv")
    assert len(current) == EXPECTED_CELLS[scale]
    assert current["cell_id"].is_unique
    assert int(current["n_wells"].sum()) == 3877
    joined = current[["cell_id", "n_wells"]].merge(
        prior[["cell_id", "n_wells_raw"]], on="cell_id", how="outer", validate="one_to_one"
    )
    assert joined.notna().all().all()
    assert (joined["n_wells"] == joined["n_wells_raw"]).all()
    empty = current["n_wells"].eq(0)
    percentage_columns = [
        name
        for name in current.columns
        if name.endswith("_pct")
        and name not in {"hydrostrat_dominant_unit_pct", "hydrostrat_dominant_domain_pct"}
    ]
    assert current.loc[empty, percentage_columns].isna().all().all()
    assert (current.loc[empty, "analysis_status"] == "SEM_POCO_NO_CONJUNTO_AUDITADO").all()
    for value in current["dimension_vector_json"]:
        assert set(json.loads(value)) == VECTOR_DIMENSIONS
    geojson = strict_json(EFFECTIVE / f"effective_knowledge_{scale}km2.geojson")
    assert len(geojson["features"]) == EXPECTED_CELLS[scale]
    web_copy = ROOT / f"docs/data/effective_knowledge/effective_knowledge_{scale}km2.geojson"
    assert sha256(web_copy) == sha256(EFFECTIVE / f"effective_knowledge_{scale}km2.geojson")

details = strict_json(ROOT / "docs/data/well_details.json")
assert len(details) == 3877
assert all(set(record["effective_knowledge"]["states"]) == DETAIL_DIMENSIONS for record in details.values())
assert pd.read_csv(ROOT / "methodology/DICIONARIO_METRICAS_RESULTADOS_V1.csv").shape[0] == 680
assert pd.read_csv(ROOT / "docs/data/bibliografia_master_v1.csv").shape[0] == 54
assert pd.read_csv(EFFECTIVE / "effective_knowledge_field_dictionary.csv").shape[0] == 127

for html_path in (ROOT / "docs").glob("*.html"):
    parser = IdCollector()
    parser.feed(html_path.read_text(encoding="utf-8"))
    duplicates = {value for value in parser.ids if parser.ids.count(value) > 1}
    assert not duplicates, f"IDs HTML duplicados em {html_path.name}: {sorted(duplicates)}"

workbook = ROOT.parent.parent / "outputs/6b2168c6942b/PIH_MS_CONHECIMENTO_HIDROGEOLOGICO_EFETIVO_V1.xlsx"
assert workbook.exists() and workbook.stat().st_size > 1_000_000
print("OK V2.2")
print("3877 poços, 9029 células, 680 campos, 54 referências, 9 dimensões sem agregação")
