#!/usr/bin/env python3
"""Auditoria reproduzível da entrega PIH MS V2.5."""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from zipfile import ZipFile
import json
import math
import subprocess

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/derived/stability_sensitivity"
WEB = ROOT / "docs/data/stability_sensitivity"
SCALES = (100, 150, 250, 500, 1000)
QUESTIONS = ("Q01", "Q02", "Q03", "Q04", "Q05")
EXPECTED_CELLS = {100: 3763, 150: 2525, 250: 1537, 500: 791, 1000: 413}


class AuditHTML(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.options: dict[str, set[str]] = {}
        self.current_select: str | None = None

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


assert (ROOT / "VERSION").read_text(encoding="utf-8").strip() == "2.5"
registry = json.loads((OUT / "stability_sensitivity_registry.json").read_text(encoding="utf-8"))
assert registry["version"] == "2.5"
assert registry["support_points_n"] == 14284
assert registry["wells_n"] == 3877
assert registry["questions"] == list(QUESTIONS)
assert registry["scales_km2"] == list(SCALES)
assert registry["origins"] == ["O00", "OX25", "OY25", "OXY25"]
assert not any(
    registry["rules"][field]
    for field in ("unknown_is_zero", "weight_used", "score_used", "priority_calculated", "potential_calculated", "interpolation_used", "prediction_used", "final_scale_selected", "final_origin_selected")
)

support_scale = pd.read_csv(OUT / "support_scale_question_long.csv", low_memory=False)
support_question = pd.read_csv(OUT / "support_question_cross_scale.csv", low_memory=False)
persistence = pd.read_csv(OUT / "support_requirement_persistence.csv", low_memory=False)
cell_long = pd.read_csv(OUT / "cell_stability_sensitivity_long.csv", low_memory=False)
origin_counts = pd.read_csv(OUT / "origin_scale_question_counts.csv")
assert len(support_scale) == 357100
assert len(support_question) == 71420
assert len(persistence) == 557076
assert len(cell_long) == 45145 and len(cell_long.columns) == 29
assert len(origin_counts) == 100
assert support_scale.support_id.nunique() == 14284
assert persistence.requirement_code.nunique() == 39
assert set(support_scale.question_code) == set(QUESTIONS)
assert set(support_scale.scale_km2) == set(SCALES)
assert origin_counts.control_total_ok.all()
assert (origin_counts[["state_no_wells_n", "state_wells_without_direct_n", "state_direct_present_n"]].sum(axis=1) == 14284).all()

cross = pd.read_csv(OUT / "cross_scale_question_summary.csv").set_index("question_code")
expected_cross = {
    "Q01": (45.400448, 11.565388, 51.729208, 36.705405),
    "Q02": (45.127415, 11.278353, 51.001120, 37.720526),
    "Q03": (43.223187, 9.080090, 47.948754, 42.971157),
    "Q04": (45.981518, 12.174461, 51.848222, 35.977317),
    "Q05": (40.730888, 5.684682, 44.511341, 49.803976),
}
for question, expected in expected_cross.items():
    actual = tuple(cross.loc[question, ["exact_state_all_scales_pct", "direct_all_scales_pct", "direct_some_scales_pct", "direct_no_scale_pct"]])
    assert all(math.isclose(float(a), float(b), abs_tol=1e-6) for a, b in zip(actual, expected))
assert not cross.monotonic_relation_asserted.any()
assert not cross.final_scale_selected.any()

origin = pd.read_csv(OUT / "origin_scale_question_summary.csv")
expected_origin = {
    100: (76.778213, 78.633436, 12.552506, 18.608233),
    150: (72.080650, 74.852982, 16.024923, 22.031644),
    250: (66.178941, 70.463456, 21.996640, 27.233268),
    500: (60.333240, 67.432092, 27.961355, 30.348642),
    1000: (59.521143, 71.730608, 27.296276, 32.602912),
}
for scale, expected in expected_origin.items():
    group = origin[origin.scale_km2 == scale]
    actual = (
        group.exact_state_all_origins_pct.min(), group.exact_state_all_origins_pct.max(),
        group.direct_some_origins_pct.min(), group.direct_some_origins_pct.max(),
    )
    assert all(math.isclose(float(a), float(b), abs_tol=1e-6) for a, b in zip(actual, expected))
assert not origin.final_origin_selected.any()

blockers = pd.read_csv(OUT / "blocker_requirement_summary.csv")
full = blockers[blockers.fully_blocked_all_wells & blockers.fully_blocked_all_observable_support]
assert len(blockers) == 39 and len(full) == 12
assert set(full.requirement_code) == {
    "Q01_R05", "Q02_R02", "Q02_R08", "Q03_R02", "Q03_R07", "Q03_R08",
    "Q04_R03", "Q04_R04", "Q05_R02", "Q05_R04", "Q05_R06", "Q05_R07",
}
assert not blockers.physical_absence_inferred.any()
unknown_persistence = persistence.observable_scales_n.eq(0)
assert persistence.loc[unknown_persistence, "persistence_state"].eq("UNKNOWN_SEM_ESCALA_OBSERVAVEL").all()
assert persistence.loc[unknown_persistence, "full_blocker_persistence_pct"].isna().all()
assert not persistence.unknown_is_zero.any()

hydro = pd.read_csv(OUT / "hydro_context_scale_summary.csv").set_index("scale_km2")
expected_hydro = {100: (1026, 2654, 83), 150: (885, 1596, 44), 250: (708, 803, 26), 500: (479, 296, 16), 1000: (280, 124, 9)}
for scale, expected in expected_hydro.items():
    actual = tuple(int(value) for value in hydro.loc[scale, ["cells_multiple_surface_units_n", "cells_one_surface_unit_n", "cells_unknown_surface_context_n"]])
    assert actual == expected
    assert sum(actual) == EXPECTED_CELLS[scale]
assert hydro.surface_point_proxy_used.all()
assert not hydro.area_fraction_calculated.any()
assert not hydro.vertical_structure_inferred.any()

for scale, expected in EXPECTED_CELLS.items():
    csv_frame = pd.read_csv(OUT / f"stability_sensitivity_{scale}km2.csv", low_memory=False)
    source_geo = OUT / f"stability_sensitivity_{scale}km2.geojson"
    web_geo = WEB / source_geo.name
    assert len(csv_frame) == expected
    assert int(csv_frame.n_wells.sum()) == 3877
    assert not csv_frame.weight_used.any() and not csv_frame.score_used.any()
    payload = json.loads(source_geo.read_text(encoding="utf-8"))
    assert len(payload["features"]) == expected
    assert source_geo.read_bytes() == web_geo.read_bytes()
    for position in (0, expected // 2, expected - 1):
        props = payload["features"][position]["properties"]
        assert props["cell_id"] and int(props["scale_km2"]) == scale
        for question in QUESTIONS:
            prefix = question.lower()
            assert f"{prefix}_cell_state_code" in props
            assert f"{prefix}_cross_scale_exact_pct" in props
            assert f"{prefix}_origin_exact_pct" in props

dictionary = pd.read_csv(ROOT / "methodology/DICIONARIO_METRICAS_RESULTADOS_V1.csv")
v25_fields = dictionary[dictionary.modules.eq("Estabilidade e sensibilidade")]
assert len(dictionary) == 916 and len(v25_fields) == 128
assert not v25_fields.definition.str.startswith("Campo ").any()
assert (ROOT / "methodology/BIBLIOGRAFIA_MASTER_V1.csv").read_text(encoding="utf-8-sig").count("\n") == 56

statistics = json.loads((ROOT / "docs/data/statistics/statistics_v221.json").read_text(encoding="utf-8"))
assert statistics["version"] == "2.5" and statistics["dataset_count"] == 17
assert {item["id"] for item in statistics["datasets"]}.issuperset({"stability_cross_scale", "stability_origin", "stability_blockers", "stability_hydro"})

index = (ROOT / "docs/index.html").read_text(encoding="utf-8")
parser = AuditHTML()
parser.feed(index)
assert not {item for item in parser.ids if parser.ids.count(item) > 1}
assert parser.options["ssScale"] == {str(value) for value in SCALES}
assert parser.options["ssQuestion"] == set(QUESTIONS)
assert parser.options["ssMetric"] == {"cell_state_code", "direct_evidence_n", "cross_scale_exact_pct", "origin_exact_pct", "n_wells", "hydro_surface_units_n"}
for token in ("PIH MS V2.5", "stabilitySensitivityGroup", "metodologia-estabilidade-sensibilidade.html", "916 campos"):
    assert token in index or token in (ROOT / "docs/dicionario-parametros.html").read_text(encoding="utf-8")
javascript = (ROOT / "docs/assets/js/pih.js").read_text(encoding="utf-8")
for token in ("showStabilitySensitivity", "hideStabilitySensitivity", "stabilitySensitivityFicha", "installV25Navigation", "navStabilitySensitivity", "stability_sensitivity_"):
    assert token in javascript
subprocess.run(["node", "--check", str(ROOT / "docs/assets/js/pih.js")], check=True)

details = json.loads((ROOT / "docs/data/well_details.json").read_text(encoding="utf-8"))
manifest = json.loads((ROOT / "docs/data/well_details_shards/manifest.json").read_text(encoding="utf-8"))
assert len(details) == manifest["well_count"] == 3877
assert manifest["version"] == "2.5" and sum(manifest["counts"].values()) == 3877

for path in (
    ROOT / "methodology/ESTABILIDADE_SENSIBILIDADE_V1.md",
    ROOT / "ESTUDO_ESTABILIDADE_SENSIBILIDADE_V1.md",
    ROOT / "AUDITORIA_ESTABILIDADE_SENSIBILIDADE_V25.md",
    ROOT / "docs/metodologia-estabilidade-sensibilidade.html",
    ROOT / "PIH_MS_ESTABILIDADE_SENSIBILIDADE_V1.xlsx",
):
    assert path.exists() and path.stat().st_size > 1000

with ZipFile(ROOT / "PIH_MS_ESTABILIDADE_SENSIBILIDADE_V1.xlsx") as archive:
    workbook_xml = archive.read("xl/workbook.xml").decode("utf-8")
    for sheet in (
        "README", "Cross_Scale", "Cross_Pairwise", "Origin_Summary", "Origin_Pairwise", "Origin_Counts",
        "Blockers", "Hydro_Context", "Cell_250km2", "Field_Dictionary", "Visual_Summary", "Cell_Cardinality", "Review_Checks",
    ):
        assert f'name="{sheet}"' in workbook_xml

print("OK V2.5")
print("5 perguntas, 5 escalas, 4 origens, 14284 suportes, 3877 poços e 17 resumos")
