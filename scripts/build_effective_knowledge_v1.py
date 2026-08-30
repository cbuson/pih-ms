#!/usr/bin/env python3
"""Constrói a matriz V2.2 de conhecimento hidrogeológico efetivo.

Esta rotina é deliberadamente não agregadora. Ela mantém nove dimensões
separadas, preserva UNKNOWN e não calcula peso, nota, índice, potencial ou
prioridade de investigação.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/derived/effective_knowledge"
WEB = ROOT / "docs/data/effective_knowledge"
SCALES = (100, 150, 250, 500, 1000)
CUTOFF_DATE = "2026-08-29"
METHOD_VERSION = "PIH_MS_V2.2_CHE_V1"
# O ponto abaixo está a aproximadamente 0,16 m da fronteira exportada em WGS84.
# Preserva-se a atribuição projetada EPSG 5880 já consolidada na V2.1.
V21_ASSIGNMENT_CONTINUITY = {
    (100, "3500027053"): "SCALE-100-O00-01772",
}
OUT.mkdir(parents=True, exist_ok=True)
WEB.mkdir(parents=True, exist_ok=True)


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig", dtype={"well_id": str})


def as_bool(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.lower().isin({"true", "1", "sim", "yes", "s"})


def bool_value(value) -> bool:
    return str(value).strip().lower() in {"true", "1", "sim", "yes", "s"}


def clean_text(value) -> str:
    if value is None or pd.isna(value):
        return ""
    value = str(value).strip()
    return "" if value in {"", "nan", "None"} else value


def pct(count: int, total: int):
    return None if total == 0 else 100.0 * count / total


def evidence_set(code: str, filename: str) -> set[str]:
    frame = read_csv(ROOT / "data/derived/evidence" / filename)
    return set(frame["well_id"].astype(str))


def state_hydrostrat(status: str) -> str:
    mapping = {
        "CONSISTENTE": "DOCUMENTADO_CONSISTENTE",
        "POSSIVELMENTE CONSISTENTE": "DOCUMENTADO_POSSIVELMENTE_CONSISTENTE",
        "DIVERGÊNCIA CARTOGRÁFICA NÃO CONCLUSIVA": "REVISAO_DIVERGENCIA_CARTOGRAFICA_NAO_CONCLUSIVA",
        "NOME FORA DA TAXONOMIA ESTADUAL, REVISAR": "REVISAO_NOME_FORA_TAXONOMIA",
        "NÃO COMPARÁVEL DIRETAMENTE": "REVISAO_NAO_COMPARAVEL_DIRETAMENTE",
        "UNKNOWN": "UNKNOWN_HIDROESTRATIGRAFIA",
    }
    return mapping.get(clean_text(status).upper(), "UNKNOWN_HIDROESTRATIGRAFIA")


def state_vertical(raw: str) -> str:
    mapping = {
        "PROFUNDIDADE_MAIS_METADADOS": "PARCIAL_PROFUNDIDADE_MAIS_METADADOS_SEM_INTERVALO_CAPTADO",
        "PROFUNDIDADE_APENAS": "PARCIAL_PROFUNDIDADE_APENAS_SEM_INTERVALO_CAPTADO",
        "SEM_PROFUNDIDADE_POSITIVA": "UNKNOWN_SEM_PROFUNDIDADE_E_SEM_INTERVALO_CAPTADO",
    }
    return mapping.get(clean_text(raw), "UNKNOWN_SEM_PROFUNDIDADE_E_SEM_INTERVALO_CAPTADO")


def state_temporal(raw: str) -> str:
    mapping = {
        "EVIDENCIA_DATADA_MULTIPLOS_DOMINIOS": "EVIDENCIA_DATADA_MULTIPLOS_DOMINIOS_SEM_SERIE",
        "EVIDENCIA_DATADA_UM_DOMINIO": "EVIDENCIA_DATADA_UM_DOMINIO_SEM_SERIE",
        "UNKNOWN_SEM_EVIDENCIA_DATADA": "UNKNOWN_SEM_EVIDENCIA_DATADA_E_SEM_SERIE",
    }
    return mapping.get(clean_text(raw), "UNKNOWN_SEM_EVIDENCIA_DATADA_E_SEM_SERIE")


def json_compact(value) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def native_scalar(value):
    if value is None or pd.isna(value):
        return None
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.bool_):
        return bool(value)
    return value


def iter_rings(geometry: dict):
    """Produz polígonos GeoJSON sem depender de biblioteca SIG externa."""
    if geometry["type"] == "Polygon":
        yield geometry["coordinates"]
    elif geometry["type"] == "MultiPolygon":
        yield from geometry["coordinates"]
    else:
        raise ValueError(f"Geometria não suportada {geometry['type']}")


def geometry_bbox(geometry: dict):
    xs, ys = [], []
    for polygon in iter_rings(geometry):
        for ring in polygon:
            for x, y, *_ in ring:
                xs.append(x)
                ys.append(y)
    return min(xs), min(ys), max(xs), max(ys)


def point_on_segment(x, y, x1, y1, x2, y2, tolerance=1e-11):
    cross = (x - x1) * (y2 - y1) - (y - y1) * (x2 - x1)
    if abs(cross) > tolerance:
        return False
    return min(x1, x2) - tolerance <= x <= max(x1, x2) + tolerance and min(y1, y2) - tolerance <= y <= max(y1, y2) + tolerance


def point_in_ring(x, y, ring):
    inside = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        if point_on_segment(x, y, xi, yi, xj, yj):
            return True
        intersects = (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi
        if intersects:
            inside = not inside
        j = i
    return inside


def point_in_geometry(x, y, geometry):
    for polygon in iter_rings(geometry):
        if point_in_ring(x, y, polygon[0]) and not any(point_in_ring(x, y, hole) for hole in polygon[1:]):
            return True
    return False


def assign_points_to_grid(well_frame: pd.DataFrame, features: list[dict], scale: int):
    """Atribuição WGS84 por índice de caixas e teste ponto em polígono."""
    step = 0.25
    bboxes = [geometry_bbox(feature["geometry"]) for feature in features]
    buckets = defaultdict(list)
    for feature_index, (xmin, ymin, xmax, ymax) in enumerate(bboxes):
        for bx in range(int(np.floor(xmin / step)), int(np.floor(xmax / step)) + 1):
            for by in range(int(np.floor(ymin / step)), int(np.floor(ymax / step)) + 1):
                buckets[(bx, by)].append(feature_index)
    assigned = {}
    audit = []
    for row_index, row in well_frame.iterrows():
        x, y = float(row["longitude"]), float(row["latitude"])
        candidates = buckets.get((int(np.floor(x / step)), int(np.floor(y / step))), [])
        matches = []
        for feature_index in candidates:
            xmin, ymin, xmax, ymax = bboxes[feature_index]
            if xmin - 1e-11 <= x <= xmax + 1e-11 and ymin - 1e-11 <= y <= ymax + 1e-11:
                if point_in_geometry(x, y, features[feature_index]["geometry"]):
                    matches.append(feature_index)
        if not matches:
            # Tolerância de fronteira. Só é usada se o teste exato não atribuir.
            nearby = []
            for feature_index, (xmin, ymin, xmax, ymax) in enumerate(bboxes):
                dx = max(xmin - x, 0.0, x - xmax)
                dy = max(ymin - y, 0.0, y - ymax)
                distance2 = dx * dx + dy * dy
                nearby.append((distance2, feature_index))
            distance2, feature_index = min(nearby)
            if distance2 > 1e-8:
                raise RuntimeError(f"{scale} km² não atribuiu o poço {row['well_id']}")
            matches = [feature_index]
            method = "NEAREST_BBOX_BOUNDARY_TOLERANCE"
        else:
            method = "POINT_IN_POLYGON_WGS84"
        # Pontos exatamente sobre fronteiras podem ter mais de uma célula candidata.
        # A ordenação por cell_id torna a decisão determinística e auditável.
        feature_index = sorted(matches, key=lambda i: features[i]["properties"]["cell_id"])[0]
        cell_id = features[feature_index]["properties"]["cell_id"]
        assigned[row_index] = cell_id
        audit.append({
            "well_id": row["well_id"], "scale_km2": scale, "cell_id": cell_id,
            "assignment_method": method, "assignment_distance_m": 0.0,
            "boundary_candidates_n": len(matches),
        })
    return assigned, audit


# Base científica por poço
wm = read_csv(ROOT / "data/source_audit/wells_master.csv")
ev = read_csv(ROOT / "data/source_audit/well_evidence_presence.csv")
aq = read_csv(ROOT / "data/source_audit/aquifer_assignment_audit.csv")
vt = read_csv(ROOT / "data/derived/vertical_temporal/well_vertical_temporal.csv")
ir = read_csv(ROOT / "data/derived/independence_redundancy/well_independence_redundancy.csv")
flags = read_csv(ROOT / "data/source_audit/data_quality_flags.csv")
chem_samples = read_csv(ROOT / "data/source_audit/chem_samples.csv")
chem_results = read_csv(ROOT / "data/source_audit/chem_results.csv")

for frame in (wm, ev, aq, vt, ir, flags, chem_samples, chem_results):
    frame["well_id"] = frame["well_id"].astype(str)

base = wm.merge(ev, on="well_id", how="left", validate="one_to_one", suffixes=("", "_ev"))
base = base.merge(
    aq[["well_id", "comparison_status", "comparison_reason", "manual_review_required"]],
    on="well_id",
    how="left",
    validate="one_to_one",
)
vt_keep = [
    "well_id", "hydrolithologic_domain", "depth_positive", "vertical_metadata_n",
    "vertical_documentation_state", "capture_interval_status", "top_base_raw_coherent",
    "test_dated", "chemistry_dated", "level_measurement_dated", "dated_evidence_any",
    "dated_domains_n", "latest_evidence_date", "latest_evidence_age_years",
    "rimas_registered", "temporal_documentation_state", "time_series_status",
]
base = base.merge(vt[vt_keep], on="well_id", how="left", validate="one_to_one")
ir_keep = [
    "well_id", "source_snapshot_overlap", "duplicate_candidate_level",
    "exact_coordinate_colocation", "nn_lt_100m", "nn_lt_500m",
    "nn_lt_1000m", "documentary_domains_n", "source_core_pairs_comparable_n",
    "source_core_pairs_matching_n", "pumping_test_records_n", "chem_sample_records_n",
    "chem_result_records_n", "hydraulic_parameter_records_n", "chem_parameter_types_n",
]
base = base.merge(ir[ir_keep], on="well_id", how="left", validate="one_to_one")

if len(base) != 3877 or base["well_id"].nunique() != 3877:
    raise RuntimeError("A base canônica deixou de conter exatamente 3.877 IDs únicos")

for col in [
    "has_valid_coordinates", "has_static_level_current", "has_dynamic_level_current",
    "has_specific_capacity_current", "has_transmissivity_sgb2024", "depth_positive",
    "top_base_raw_coherent", "test_dated", "chemistry_dated", "level_measurement_dated",
    "dated_evidence_any", "rimas_registered", "source_snapshot_overlap",
    "exact_coordinate_colocation", "nn_lt_100m", "nn_lt_500m", "nn_lt_1000m",
    "manual_review_required",
]:
    base[col] = as_bool(base[col])

numeric_cols = [
    "latitude", "longitude", "nearest_neighbor_m", "vertical_metadata_n", "dated_domains_n",
    "latest_evidence_age_years", "documentary_domains_n", "source_core_pairs_comparable_n",
    "source_core_pairs_matching_n", "pumping_test_records_n", "chem_sample_records_n",
    "chem_result_records_n", "hydraulic_parameter_records_n", "chem_parameter_types_n",
]
for col in numeric_cols:
    base[col] = pd.to_numeric(base[col], errors="coerce")

E04 = evidence_set("E04", "E04_nivel_estatico_disponivel.csv")
E05 = evidence_set("E05", "E05_nivel_dinamico_disponivel.csv")
E06 = evidence_set("E06", "E06_vazao_especifica_nao_negativa.csv")
E07 = evidence_set("E07", "E07_ensaio_bombeamento_cadastrado.csv")
E08 = evidence_set("E08", "E08_ensaio_metadados_minimos.csv")
E09 = evidence_set("E09", "E09_transmissividade_informada.csv")
E10 = evidence_set("E10", "E10_evidencia_hidroquimica_parcial.csv")

flag_counts = flags.groupby(["well_id", "severity"]).size().unstack(fill_value=0)
for severity in ("REVIEW", "INVALID"):
    if severity not in flag_counts:
        flag_counts[severity] = 0
flag_counts["quality_flags_n"] = flag_counts.sum(axis=1)

chem_sample_counts = chem_samples.groupby("well_id").size()
chem_result_counts = chem_results.groupby("well_id").size()
chem_parameter_counts = chem_results.groupby("well_id")["parameter"].nunique()

well_rows = []
for row in base.to_dict("records"):
    wid = row["well_id"]
    valid_coord = bool(row["has_valid_coordinates"])
    coord_review = clean_text(row["coordinate_quality_status"]).upper() == "REVIEW"
    declared = clean_text(row["municipality_declared"])
    spatial = clean_text(row["municipality_spatial"])
    municipality_agreement = None if not declared or not spatial else declared.casefold() == spatial.casefold()
    if not valid_coord:
        spatial_state = "UNKNOWN_COORDENADA_NAO_VALIDA"
    elif coord_review or municipality_agreement is False:
        spatial_state = "DOCUMENTADO_COM_REVISAO"
    else:
        spatial_state = "DOCUMENTADO_SEM_ALERTA_OBJETIVO"

    hydro_state = state_hydrostrat(row.get("comparison_status"))
    vertical_state = state_vertical(row.get("vertical_documentation_state"))

    e04, e05, e06 = wid in E04, wid in E05, wid in E06
    e07, e08, e09 = wid in E07, wid in E08, wid in E09
    hydraulic_components = sum((e04, e05, e06, e07, e08, e09))
    if e09:
        hydraulic_state = "TRANSMISSIVIDADE_INFORMADA_NAO_VALIDADA"
    elif e08:
        hydraulic_state = "ENSAIO_COM_METADADOS_MINIMOS_DOCUMENTAIS"
    elif e07:
        hydraulic_state = "ENSAIO_CADASTRADO_SEM_METADADOS_MINIMOS"
    elif hydraulic_components:
        hydraulic_state = "VALORES_HIDRAULICOS_ISOLADOS_SEM_ENSAIO_SUFICIENTE"
    else:
        hydraulic_state = "UNKNOWN_SEM_EVIDENCIA_HIDRAULICA_NO_CONJUNTO"

    e10 = wid in E10
    chem_dated = bool(row["chemistry_dated"])
    if e10 and chem_dated:
        hydrochem_state = "PARCIAL_DATADA_SEM_QA_ANALITICO_COMPLETO"
    elif e10:
        hydrochem_state = "PARCIAL_SEM_DATA_E_SEM_QA_ANALITICO_COMPLETO"
    else:
        hydrochem_state = "UNKNOWN_SEM_EVIDENCIA_HIDROQUIMICA_NO_CONJUNTO"

    temporal_state = state_temporal(row.get("temporal_documentation_state"))
    independence_state = "UNKNOWN_INDEPENDENCIA_HIDROGEOLOGICA_NAO_DEMONSTRADA"
    duplicate_level = clean_text(row.get("duplicate_candidate_level")).upper() or "NONE"
    if duplicate_level in {"HIGH", "MEDIUM"}:
        independence_context = f"REVISAO_DUPLICIDADE_{duplicate_level}"
    elif bool(row["exact_coordinate_colocation"]):
        independence_context = "REVISAO_COLOCALIZACAO_EXATA"
    elif bool(row["source_snapshot_overlap"]):
        independence_context = "SOBREPOSICAO_DE_SNAPSHOTS_SEM_DUPLICACAO_DE_ID"
    elif bool(row["nn_lt_500m"]):
        independence_context = "PROXIMIDADE_ESPACIAL_SEM_INFERENCIA_DE_REDUNDANCIA"
    else:
        independence_context = "SEM_ALERTA_DE_REDUNDANCIA_NAS_REGRAS_ATUAIS"

    q_review = int(flag_counts.loc[wid, "REVIEW"]) if wid in flag_counts.index else 0
    q_invalid = int(flag_counts.loc[wid, "INVALID"]) if wid in flag_counts.index else 0
    q_total = int(flag_counts.loc[wid, "quality_flags_n"]) if wid in flag_counts.index else 0
    if q_invalid:
        documentary_state = "VALOR_INVALIDO_PRESERVADO"
    elif q_review:
        documentary_state = "ALERTAS_DE_REVISAO_PRESENTES"
    else:
        documentary_state = "SEM_ALERTA_OBJETIVO_NAS_REGRAS_ATUAIS"

    uncertainty = [
        "UNKNOWN_INTERVALO_CAPTADO",
        "UNKNOWN_SERIE_TEMPORAL",
        "UNKNOWN_INDEPENDENCIA_HIDROGEOLOGICA",
        "UNKNOWN_QA_HIDROQUIMICO_COMPLETO",
    ]
    if spatial_state.startswith("UNKNOWN"):
        uncertainty.append("UNKNOWN_LOCALIZACAO_VALIDA")
    if hydro_state.startswith("UNKNOWN"):
        uncertainty.append("UNKNOWN_HIDROESTRATIGRAFIA")
    if vertical_state.startswith("UNKNOWN"):
        uncertainty.append("UNKNOWN_PROFUNDIDADE_POSITIVA")
    if hydraulic_state.startswith("UNKNOWN"):
        uncertainty.append("UNKNOWN_EVIDENCIA_HIDRAULICA")
    if hydrochem_state.startswith("UNKNOWN"):
        uncertainty.append("UNKNOWN_EVIDENCIA_HIDROQUIMICA")
    if temporal_state.startswith("UNKNOWN"):
        uncertainty.append("UNKNOWN_EVIDENCIA_DATADA")

    dimensions = {
        "espacial": spatial_state,
        "hidroestratigrafica": hydro_state,
        "vertical": vertical_state,
        "hidraulica": hydraulic_state,
        "hidroquimica": hydrochem_state,
        "temporal": temporal_state,
        "independencia": independence_state,
        "qualidade_documental": documentary_state,
        "incerteza": "INCERTEZA_EXPLICITA_NAO_AGREGADA",
    }
    well_rows.append({
        "well_id": wid,
        "latitude": row["latitude"],
        "longitude": row["longitude"],
        "municipality_declared": declared,
        "municipality_spatial": spatial,
        "sgb2024_unit_aflorante": clean_text(row["sgb2024_unit_aflorante"]),
        "hydrolithologic_domain": clean_text(row["hydrolithologic_domain"]),
        "cutoff_date": CUTOFF_DATE,
        "method_version": METHOD_VERSION,
        "spatial_coordinate_valid": valid_coord,
        "spatial_coordinate_review": coord_review,
        "spatial_municipality_agreement": municipality_agreement,
        "spatial_nearest_neighbor_m": row["nearest_neighbor_m"],
        "spatial_state": spatial_state,
        "hydrostrat_comparison_status_source": clean_text(row.get("comparison_status")) or "UNKNOWN",
        "hydrostrat_manual_review_required": bool(row["manual_review_required"]),
        "hydrostrat_state": hydro_state,
        "vertical_depth_positive": bool(row["depth_positive"]),
        "vertical_metadata_n": row["vertical_metadata_n"],
        "vertical_top_base_raw_coherent": bool(row["top_base_raw_coherent"]),
        "vertical_capture_interval_status": clean_text(row["capture_interval_status"]),
        "vertical_state": vertical_state,
        "hydraulic_static_level_available": e04,
        "hydraulic_dynamic_level_available": e05,
        "hydraulic_specific_capacity_nonnegative": e06,
        "hydraulic_test_registered": e07,
        "hydraulic_test_minimum_metadata": e08,
        "hydraulic_transmissivity_reported": e09,
        "hydraulic_components_documented_n": hydraulic_components,
        "hydraulic_state": hydraulic_state,
        "hydrochemical_partial_evidence": e10,
        "hydrochemical_dated": chem_dated,
        "hydrochemical_samples_n": int(chem_sample_counts.get(wid, 0)),
        "hydrochemical_results_n": int(chem_result_counts.get(wid, 0)),
        "hydrochemical_parameter_types_n": int(chem_parameter_counts.get(wid, 0)),
        "hydrochemical_state": hydrochem_state,
        "temporal_any_dated": bool(row["dated_evidence_any"]),
        "temporal_dated_domains_n": int(row["dated_domains_n"]) if pd.notna(row["dated_domains_n"]) else 0,
        "temporal_latest_evidence_date": clean_text(row["latest_evidence_date"]),
        "temporal_latest_evidence_age_years": row["latest_evidence_age_years"],
        "temporal_rimas_registered": bool(row["rimas_registered"]),
        "temporal_time_series_status": clean_text(row["time_series_status"]),
        "temporal_state": temporal_state,
        "independence_state": independence_state,
        "independence_review_context": independence_context,
        "independence_duplicate_candidate_level": duplicate_level,
        "independence_exact_coordinate_colocation": bool(row["exact_coordinate_colocation"]),
        "independence_source_snapshot_overlap": bool(row["source_snapshot_overlap"]),
        "documentary_domains_n": int(row["documentary_domains_n"]) if pd.notna(row["documentary_domains_n"]) else 0,
        "documentary_quality_flags_n": q_total,
        "documentary_review_flags_n": q_review,
        "documentary_invalid_flags_n": q_invalid,
        "documentary_state": documentary_state,
        "uncertainty_state": "INCERTEZA_EXPLICITA_NAO_AGREGADA",
        "uncertainty_codes": "|".join(sorted(set(uncertainty))),
        "dimension_vector_json": json_compact(dimensions),
    })

well = pd.DataFrame(well_rows)
well.to_csv(OUT / "well_effective_knowledge.csv", index=False, encoding="utf-8-sig")


# Agregação descritiva por célula, sem escore ou ordenação
assignment_rows = []
scale_summaries = []

for scale in SCALES:
    grid_path = ROOT / f"docs/data/scale_study/scale_primary_{scale}km2.geojson"
    strat_path = ROOT / f"docs/data/stratified_scale/stratified_scale_{scale}km2.geojson"
    with open(grid_path, encoding="utf-8") as handle:
        grid_features = json.load(handle)["features"]
    with open(strat_path, encoding="utf-8") as handle:
        strat_features = json.load(handle)["features"]
    strat_props = pd.DataFrame([f["properties"] for f in strat_features]).set_index("cell_id")

    assignments, audit = assign_points_to_grid(well, grid_features, scale)
    for (override_scale, override_well), override_cell in V21_ASSIGNMENT_CONTINUITY.items():
        if override_scale != scale:
            continue
        row_index = well.index[well["well_id"] == override_well][0]
        assignments[row_index] = override_cell
        for item in audit:
            if item["well_id"] == override_well and item["scale_km2"] == scale:
                item["cell_id"] = override_cell
                item["assignment_method"] = "V21_PROJECTED_ASSIGNMENT_PRESERVED_NEAR_BOUNDARY"
                item["assignment_distance_m"] = 0.16
                item["boundary_candidates_n"] = 2
                break
    assignment_rows.extend(audit)
    if len(assignments) != 3877:
        raise RuntimeError(f"{scale} km² não preservou os 3.877 IDs")
    grouped = defaultdict(list)
    for row_index, cell_id in assignments.items():
        grouped[cell_id].append(row_index)
    records = []
    features = []
    for feature in grid_features:
        cell = feature["properties"]
        cid = cell["cell_id"]
        sw = well.loc[grouped.get(cid, [])]
        n = len(sw)
        sp = strat_props.loc[cid]
        base_record = {
            "cell_id": cid,
            "scale_km2": scale,
            "variant": clean_text(cell.get("variant")) or "O00",
            "area_effective_km2": cell.get("area_effective_km2"),
            "n_wells": n,
            "analysis_status": "COM_POCO_NO_CONJUNTO_AUDITADO" if n else "SEM_POCO_NO_CONJUNTO_AUDITADO",
            "spatial_gap_E01_p90_km": cell.get("gap_E01_p90_km"),
            "hydrostrat_units_n": sp.get("units_n"),
            "hydrostrat_dominant_unit": clean_text(sp.get("dominant_unit")) or "UNKNOWN",
            "hydrostrat_dominant_unit_pct": sp.get("dominant_unit_pct"),
            "hydrostrat_domains_n": sp.get("domains_n"),
            "hydrostrat_dominant_domain": clean_text(sp.get("dominant_domain")) or "UNKNOWN",
            "hydrostrat_dominant_domain_pct": sp.get("dominant_domain_pct"),
            "hydrostrat_E01_unit_masked": bool_value(sp.get("E01_dominant_unit_masked")),
            "hydrostrat_E01_domain_masked": bool_value(sp.get("E01_dominant_domain_masked")),
        }
        if n == 0:
            spatial_state = "SEM_POCO_NO_CONJUNTO_AUDITADO"
            hydro_state = "UNKNOWN_SEM_POCO_PARA_AVALIACAO_LOCAL"
            vertical_state = "UNKNOWN_SEM_POCO_PARA_AVALIACAO_VERTICAL"
            hydraulic_state = "UNKNOWN_SEM_POCO_PARA_AVALIACAO_HIDRAULICA"
            hydrochem_state = "UNKNOWN_SEM_POCO_PARA_AVALIACAO_HIDROQUIMICA"
            temporal_state = "UNKNOWN_SEM_POCO_PARA_AVALIACAO_TEMPORAL"
            independence_state = "UNKNOWN_INDEPENDENCIA_HIDROGEOLOGICA_NAO_DEMONSTRADA"
            documentary_state = "UNKNOWN_SEM_POCO_PARA_AVALIACAO_DOCUMENTAL"
            uncertainty_codes = ["UNKNOWN_SEM_POCO_NO_CONJUNTO_AUDITADO"]
            metrics = {
                "spatial_coordinate_review_n": 0, "spatial_coordinate_review_pct": None,
                "spatial_municipality_mismatch_n": 0, "spatial_municipality_mismatch_pct": None,
                "hydrostrat_unknown_n": 0, "hydrostrat_unknown_pct": None,
                "hydrostrat_review_n": 0, "hydrostrat_review_pct": None,
                "vertical_depth_positive_n": 0, "vertical_depth_positive_pct": None,
                "vertical_metadata_present_n": 0, "vertical_metadata_present_pct": None,
                "vertical_top_base_raw_coherent_n": 0, "vertical_top_base_raw_coherent_pct": None,
                "vertical_capture_interval_demonstrated_n": 0,
                "hydraulic_static_level_n": 0, "hydraulic_static_level_pct": None,
                "hydraulic_dynamic_level_n": 0, "hydraulic_dynamic_level_pct": None,
                "hydraulic_specific_capacity_nonnegative_n": 0, "hydraulic_specific_capacity_nonnegative_pct": None,
                "hydraulic_test_registered_n": 0, "hydraulic_test_registered_pct": None,
                "hydraulic_test_minimum_metadata_n": 0, "hydraulic_test_minimum_metadata_pct": None,
                "hydraulic_transmissivity_reported_n": 0, "hydraulic_transmissivity_reported_pct": None,
                "hydrochemical_partial_evidence_n": 0, "hydrochemical_partial_evidence_pct": None,
                "hydrochemical_dated_n": 0, "hydrochemical_dated_pct": None,
                "hydrochemical_samples_n": 0, "hydrochemical_results_n": 0, "hydrochemical_parameter_types_n": 0,
                "temporal_any_dated_n": 0, "temporal_any_dated_pct": None,
                "temporal_multiple_domains_n": 0, "temporal_multiple_domains_pct": None,
                "temporal_latest_evidence_age_median_years": None,
                "temporal_time_series_demonstrated_n": 0,
                "independence_duplicate_candidate_n": 0, "independence_duplicate_candidate_pct": None,
                "independence_exact_colocation_n": 0, "independence_exact_colocation_pct": None,
                "independence_nn_lt_500m_n": 0, "independence_nn_lt_500m_pct": None,
                "independence_source_snapshot_overlap_n": 0, "independence_source_snapshot_overlap_pct": None,
                "documentary_flagged_wells_n": 0, "documentary_flagged_wells_pct": None,
                "documentary_invalid_wells_n": 0, "documentary_invalid_wells_pct": None,
                "documentary_domains_median": None,
            }
        else:
            coord_review_n = int(sw["spatial_coordinate_review"].sum())
            municipality_mismatch_n = int((sw["spatial_municipality_agreement"] == False).sum())
            hydro_unknown_n = int(sw["hydrostrat_state"].str.startswith("UNKNOWN").sum())
            hydro_review_n = int(sw["hydrostrat_state"].str.startswith("REVISAO").sum())
            depth_n = int(sw["vertical_depth_positive"].sum())
            vmeta_n = int((pd.to_numeric(sw["vertical_metadata_n"], errors="coerce").fillna(0) > 0).sum())
            topbase_n = int(sw["vertical_top_base_raw_coherent"].sum())
            e04n = int(sw["hydraulic_static_level_available"].sum())
            e05n = int(sw["hydraulic_dynamic_level_available"].sum())
            e06n = int(sw["hydraulic_specific_capacity_nonnegative"].sum())
            e07n = int(sw["hydraulic_test_registered"].sum())
            e08n = int(sw["hydraulic_test_minimum_metadata"].sum())
            e09n = int(sw["hydraulic_transmissivity_reported"].sum())
            e10n = int(sw["hydrochemical_partial_evidence"].sum())
            chem_dated_n = int(sw["hydrochemical_dated"].sum())
            temporal_any_n = int(sw["temporal_any_dated"].sum())
            temporal_multi_n = int((sw["temporal_dated_domains_n"] >= 2).sum())
            dup_n = int(sw["independence_duplicate_candidate_level"].isin(["HIGH", "MEDIUM"]).sum())
            exact_n = int(sw["independence_exact_coordinate_colocation"].sum())
            nn500_n = int((pd.to_numeric(sw["spatial_nearest_neighbor_m"], errors="coerce") < 500).sum())
            overlap_n = int(sw["independence_source_snapshot_overlap"].sum())
            flagged_n = int((sw["documentary_quality_flags_n"] > 0).sum())
            invalid_n = int((sw["documentary_invalid_flags_n"] > 0).sum())
            latest_age_values = pd.to_numeric(sw["temporal_latest_evidence_age_years"], errors="coerce").dropna()
            spatial_state = "COM_COORDENADA_OU_MUNICIPIO_EM_REVISAO" if coord_review_n or municipality_mismatch_n else "SEM_ALERTA_OBJETIVO_DE_LOCALIZACAO"
            hydro_state = "REVISAO_OU_UNKNOWN_PRESENTE" if hydro_review_n or hydro_unknown_n else "DOCUMENTACAO_HIDROESTRATIGRAFICA_SEM_ALERTA_OBJETIVO"
            vertical_state = "PARCIAL_SEM_INTERVALO_CAPTADO_DEMONSTRADO"
            if e09n:
                hydraulic_state = "TRANSMISSIVIDADE_INFORMADA_NAO_VALIDADA_PRESENTE"
            elif e08n:
                hydraulic_state = "ENSAIO_COM_METADADOS_MINIMOS_PRESENTE"
            elif e07n or e04n or e05n or e06n:
                hydraulic_state = "EVIDENCIA_HIDRAULICA_PARCIAL_PRESENTE"
            else:
                hydraulic_state = "UNKNOWN_SEM_EVIDENCIA_HIDRAULICA_NO_CONJUNTO"
            hydrochem_state = "EVIDENCIA_HIDROQUIMICA_PARCIAL_PRESENTE_SEM_QA_COMPLETO" if e10n else "UNKNOWN_SEM_EVIDENCIA_HIDROQUIMICA_NO_CONJUNTO"
            temporal_state = "EVIDENCIA_DATADA_PRESENTE_SEM_SERIE" if temporal_any_n else "UNKNOWN_SEM_EVIDENCIA_DATADA_E_SEM_SERIE"
            independence_state = "UNKNOWN_INDEPENDENCIA_HIDROGEOLOGICA_NAO_DEMONSTRADA"
            documentary_state = "VALOR_INVALIDO_PRESERVADO" if invalid_n else ("ALERTAS_DE_REVISAO_PRESENTES" if flagged_n else "SEM_ALERTA_OBJETIVO_NAS_REGRAS_ATUAIS")
            uncertainty_codes = [
                "UNKNOWN_INTERVALO_CAPTADO", "UNKNOWN_SERIE_TEMPORAL",
                "UNKNOWN_INDEPENDENCIA_HIDROGEOLOGICA", "UNKNOWN_QA_HIDROQUIMICO_COMPLETO",
            ]
            if hydro_unknown_n:
                uncertainty_codes.append("UNKNOWN_HIDROESTRATIGRAFIA_EM_PARTE_DOS_POCOS")
            if not e04n and not e05n and not e06n and not e07n and not e08n and not e09n:
                uncertainty_codes.append("UNKNOWN_EVIDENCIA_HIDRAULICA")
            if not e10n:
                uncertainty_codes.append("UNKNOWN_EVIDENCIA_HIDROQUIMICA")
            if not temporal_any_n:
                uncertainty_codes.append("UNKNOWN_EVIDENCIA_DATADA")
            if bool_value(sp.get("E01_dominant_unit_masked")) or bool_value(sp.get("E01_dominant_domain_masked")):
                uncertainty_codes.append("MASCARAMENTO_HIDROESTRATIGRAFICO_POSSIVEL")
            metrics = {
                "spatial_coordinate_review_n": coord_review_n, "spatial_coordinate_review_pct": pct(coord_review_n, n),
                "spatial_municipality_mismatch_n": municipality_mismatch_n, "spatial_municipality_mismatch_pct": pct(municipality_mismatch_n, n),
                "hydrostrat_unknown_n": hydro_unknown_n, "hydrostrat_unknown_pct": pct(hydro_unknown_n, n),
                "hydrostrat_review_n": hydro_review_n, "hydrostrat_review_pct": pct(hydro_review_n, n),
                "vertical_depth_positive_n": depth_n, "vertical_depth_positive_pct": pct(depth_n, n),
                "vertical_metadata_present_n": vmeta_n, "vertical_metadata_present_pct": pct(vmeta_n, n),
                "vertical_top_base_raw_coherent_n": topbase_n, "vertical_top_base_raw_coherent_pct": pct(topbase_n, n),
                "vertical_capture_interval_demonstrated_n": 0,
                "hydraulic_static_level_n": e04n, "hydraulic_static_level_pct": pct(e04n, n),
                "hydraulic_dynamic_level_n": e05n, "hydraulic_dynamic_level_pct": pct(e05n, n),
                "hydraulic_specific_capacity_nonnegative_n": e06n, "hydraulic_specific_capacity_nonnegative_pct": pct(e06n, n),
                "hydraulic_test_registered_n": e07n, "hydraulic_test_registered_pct": pct(e07n, n),
                "hydraulic_test_minimum_metadata_n": e08n, "hydraulic_test_minimum_metadata_pct": pct(e08n, n),
                "hydraulic_transmissivity_reported_n": e09n, "hydraulic_transmissivity_reported_pct": pct(e09n, n),
                "hydrochemical_partial_evidence_n": e10n, "hydrochemical_partial_evidence_pct": pct(e10n, n),
                "hydrochemical_dated_n": chem_dated_n, "hydrochemical_dated_pct": pct(chem_dated_n, n),
                "hydrochemical_samples_n": int(sw["hydrochemical_samples_n"].sum()),
                "hydrochemical_results_n": int(sw["hydrochemical_results_n"].sum()),
                "hydrochemical_parameter_types_n": int(chem_results[chem_results["well_id"].isin(sw["well_id"])]["parameter"].nunique()),
                "temporal_any_dated_n": temporal_any_n, "temporal_any_dated_pct": pct(temporal_any_n, n),
                "temporal_multiple_domains_n": temporal_multi_n, "temporal_multiple_domains_pct": pct(temporal_multi_n, n),
                "temporal_latest_evidence_age_median_years": None if latest_age_values.empty else float(latest_age_values.median()),
                "temporal_time_series_demonstrated_n": 0,
                "independence_duplicate_candidate_n": dup_n, "independence_duplicate_candidate_pct": pct(dup_n, n),
                "independence_exact_colocation_n": exact_n, "independence_exact_colocation_pct": pct(exact_n, n),
                "independence_nn_lt_500m_n": nn500_n, "independence_nn_lt_500m_pct": pct(nn500_n, n),
                "independence_source_snapshot_overlap_n": overlap_n, "independence_source_snapshot_overlap_pct": pct(overlap_n, n),
                "documentary_flagged_wells_n": flagged_n, "documentary_flagged_wells_pct": pct(flagged_n, n),
                "documentary_invalid_wells_n": invalid_n, "documentary_invalid_wells_pct": pct(invalid_n, n),
                "documentary_domains_median": float(sw["documentary_domains_n"].median()),
            }
        dimensions = {
            "espacial": spatial_state, "hidroestratigrafica": hydro_state,
            "vertical": vertical_state, "hidraulica": hydraulic_state,
            "hidroquimica": hydrochem_state, "temporal": temporal_state,
            "independencia": independence_state, "qualidade_documental": documentary_state,
            "incerteza": "INCERTEZA_EXPLICITA_NAO_AGREGADA",
        }
        rec = {
            **base_record, **metrics,
            "spatial_state": spatial_state,
            "hydrostrat_state": hydro_state,
            "vertical_state": vertical_state,
            "hydraulic_state": hydraulic_state,
            "hydrochemical_state": hydrochem_state,
            "temporal_state": temporal_state,
            "independence_state": independence_state,
            "documentary_state": documentary_state,
            "uncertainty_state": "INCERTEZA_EXPLICITA_NAO_AGREGADA",
            "uncertainty_codes": "|".join(sorted(set(uncertainty_codes))),
            "dimension_vector_json": json_compact(dimensions),
        }
        # Converte NaN em vazio para preservar UNKNOWN sem produzir JSON inválido.
        rec = {k: native_scalar(v) for k, v in rec.items()}
        records.append(rec)
        features.append({"type": "Feature", "geometry": feature["geometry"], "properties": rec})

    cell_frame = pd.DataFrame(records)
    cell_frame.to_csv(OUT / f"effective_knowledge_{scale}km2.csv", index=False, encoding="utf-8-sig")
    collection = {"type": "FeatureCollection", "features": features}
    for target in (OUT, WEB):
        with open(target / f"effective_knowledge_{scale}km2.geojson", "w", encoding="utf-8") as handle:
            json.dump(collection, handle, ensure_ascii=False, separators=(",", ":"))

    occupied = cell_frame[cell_frame["n_wells"] > 0]
    scale_summaries.append({
        "scale_km2": scale,
        "grid_cells_n": len(cell_frame),
        "cells_with_wells_n": len(occupied),
        "cells_without_wells_n": int((cell_frame["n_wells"] == 0).sum()),
        "cells_with_wells_pct": 100.0 * len(occupied) / len(cell_frame),
        "canonical_wells_assigned_n": int(cell_frame["n_wells"].sum()),
        "cells_with_coordinate_review_n": int((occupied["spatial_coordinate_review_n"] > 0).sum()),
        "cells_with_hydrostrat_review_or_unknown_n": int(((occupied["hydrostrat_review_n"] + occupied["hydrostrat_unknown_n"]) > 0).sum()),
        "cells_with_hydraulic_minimum_test_metadata_n": int((occupied["hydraulic_test_minimum_metadata_n"] > 0).sum()),
        "cells_with_transmissivity_reported_n": int((occupied["hydraulic_transmissivity_reported_n"] > 0).sum()),
        "cells_with_partial_hydrochemistry_n": int((occupied["hydrochemical_partial_evidence_n"] > 0).sum()),
        "cells_with_dated_evidence_n": int((occupied["temporal_any_dated_n"] > 0).sum()),
        "cells_with_duplicate_review_n": int((occupied["independence_duplicate_candidate_n"] > 0).sum()),
        "cells_with_documentary_flags_n": int((occupied["documentary_flagged_wells_n"] > 0).sum()),
        "scale_selection_status": "NAO_SELECIONADA",
    })

pd.DataFrame(assignment_rows).to_csv(OUT / "effective_knowledge_assignment_audit.csv", index=False, encoding="utf-8-sig")
scale_summary = pd.DataFrame(scale_summaries)
scale_summary.to_csv(OUT / "effective_knowledge_scale_summary.csv", index=False, encoding="utf-8-sig")
scale_summary.to_csv(WEB / "effective_knowledge_scale_summary.csv", index=False, encoding="utf-8-sig")


# Sumário global e registro de interpretação
def count_state(column: str) -> Counter:
    return Counter(well[column].astype(str))


global_rows = [
    {"metric": "canonical_wells_n", "value": len(well), "unit": "poços", "interpretation": "IDs canônicos preservados sem deduplicação"},
    {"metric": "spatial_coordinate_review_n", "value": int(well["spatial_coordinate_review"].sum()), "unit": "poços", "interpretation": "Coordenada marcada para revisão"},
    {"metric": "hydrostrat_unknown_n", "value": int(well["hydrostrat_state"].str.startswith("UNKNOWN").sum()), "unit": "poços", "interpretation": "Estado hidroestratigráfico não demonstrado"},
    {"metric": "hydrostrat_review_n", "value": int(well["hydrostrat_state"].str.startswith("REVISAO").sum()), "unit": "poços", "interpretation": "Comparação que requer revisão, sem afirmar contradição"},
    {"metric": "vertical_depth_positive_n", "value": int(well["vertical_depth_positive"].sum()), "unit": "poços", "interpretation": "Profundidade total positiva disponível"},
    {"metric": "vertical_capture_interval_demonstrated_n", "value": 0, "unit": "poços", "interpretation": "Nenhum intervalo captado foi demonstrado no conjunto adquirido"},
    {"metric": "hydraulic_test_minimum_metadata_n", "value": int(well["hydraulic_test_minimum_metadata"].sum()), "unit": "poços", "interpretation": "Ensaio com metadados documentais mínimos, sem validar parâmetro"},
    {"metric": "hydraulic_transmissivity_reported_n", "value": int(well["hydraulic_transmissivity_reported"].sum()), "unit": "poços", "interpretation": "Transmissividade informada, não validada"},
    {"metric": "hydrochemical_partial_evidence_n", "value": int(well["hydrochemical_partial_evidence"].sum()), "unit": "poços", "interpretation": "Evidência hidroquímica parcial, sem QA analítico completo"},
    {"metric": "temporal_any_dated_n", "value": int(well["temporal_any_dated"].sum()), "unit": "poços", "interpretation": "Ao menos um evento hidrogeológico datado"},
    {"metric": "temporal_time_series_demonstrated_n", "value": 0, "unit": "poços", "interpretation": "Nenhuma série temporal completa foi adquirida"},
    {"metric": "independence_demonstrated_n", "value": 0, "unit": "poços", "interpretation": "Independência hidrogeológica não foi demonstrada"},
    {"metric": "documentary_flagged_wells_n", "value": int((well["documentary_quality_flags_n"] > 0).sum()), "unit": "poços", "interpretation": "Ao menos um alerta de qualidade preservado"},
    {"metric": "documentary_invalid_wells_n", "value": int((well["documentary_invalid_flags_n"] > 0).sum()), "unit": "poços", "interpretation": "Ao menos um valor objetivamente inválido preservado"},
    {"metric": "pih_score_status", "value": "NAO_CALCULADO", "unit": "estado", "interpretation": "A V2.2 não agrega dimensões"},
    {"metric": "research_priority_status", "value": "NAO_CLASSIFICADA", "unit": "estado", "interpretation": "Prioridade não é inferida nesta fase"},
]
global_summary = pd.DataFrame(global_rows)
global_summary.to_csv(OUT / "effective_knowledge_global_summary.csv", index=False, encoding="utf-8-sig")
global_summary.to_csv(WEB / "effective_knowledge_global_summary.csv", index=False, encoding="utf-8-sig")

registry_rows = [
    ("ESPACIAL", "spatial_state", "Validade e alertas objetivos da localização", "Não mede representatividade hidrogeológica e não interpreta proximidade como qualidade"),
    ("HIDROESTRATIGRAFICA", "hydrostrat_state", "Estado da comparação entre cadastro e referência cartográfica", "Divergência cartográfica não conclusiva não é contradição demonstrada"),
    ("VERTICAL", "vertical_state", "Profundidade total e metadados verticais disponíveis", "Topo e base brutos não são tratados como intervalo captado"),
    ("HIDRAULICA", "hydraulic_state", "Componentes hidráulicos documentados em níveis graduais de completude", "Transmissividade informada não é parâmetro validado"),
    ("HIDROQUIMICA", "hydrochemical_state", "Presença de evidência hidroquímica parcial e data", "Não demonstra painel completo, unidade validada ou comparabilidade analítica"),
    ("TEMPORAL", "temporal_state", "Presença e diversidade de evidência datada", "Uma ou mais datas isoladas não formam série temporal"),
    ("INDEPENDENCIA", "independence_state", "Estado da independência hidrogeológica", "Redundância espacial ou documental não demonstra independência hidrogeológica"),
    ("QUALIDADE_DOCUMENTAL", "documentary_state", "Alertas objetivos preservados sem correção silenciosa", "Ausência de alerta nas regras atuais não certifica qualidade total"),
    ("INCERTEZA", "uncertainty_state", "Códigos explícitos de desconhecimento e limitação", "Os códigos não são somados e não produzem escore"),
]
registry = pd.DataFrame(registry_rows, columns=["dimension", "state_field", "what_it_describes", "what_it_does_not_mean"])
registry["method_version"] = METHOD_VERSION
registry["cutoff_date"] = CUTOFF_DATE
registry.to_csv(OUT / "effective_knowledge_registry.csv", index=False, encoding="utf-8-sig")
registry.to_csv(WEB / "effective_knowledge_registry.csv", index=False, encoding="utf-8-sig")

style_metadata = {
    "version": "1.0",
    "method_version": METHOD_VERSION,
    "no_overall_score": True,
    "unknown_is_not_zero": True,
    "default_metric": "n_wells",
    "metrics": {
        "n_wells": {"label": "Poços canônicos por célula", "palette": ["#F7FBFF", "#C6DBEF", "#6BAED6", "#2171B5", "#08306B"]},
        "spatial_gap_E01_p90_km": {"label": "Lacuna espacial E01 P90, km", "palette": ["#F7FCF5", "#C7E9C0", "#74C476", "#238B45", "#00441B"]},
        "spatial_coordinate_review_pct": {"label": "Coordenadas em revisão, %", "palette": ["#FFF7EC", "#FDD49E", "#FC8D59", "#D7301F", "#7F0000"]},
        "hydrostrat_review_pct": {"label": "Revisão hidroestratigráfica, %", "palette": ["#FFF7EC", "#FDD49E", "#FC8D59", "#D7301F", "#7F0000"]},
        "vertical_depth_positive_pct": {"label": "Profundidade positiva documentada, %", "palette": ["#F7FCFD", "#CCECE6", "#66C2A4", "#238B45", "#00441B"]},
        "hydraulic_test_minimum_metadata_pct": {"label": "Ensaio com metadados mínimos, %", "palette": ["#F7FCFD", "#CCECE6", "#66C2A4", "#238B45", "#00441B"]},
        "hydrochemical_partial_evidence_pct": {"label": "Evidência hidroquímica parcial, %", "palette": ["#FCFBFD", "#DADAEB", "#9E9AC8", "#6A51A3", "#3F007D"]},
        "temporal_any_dated_pct": {"label": "Evidência datada, %", "palette": ["#FCFBFD", "#DADAEB", "#9E9AC8", "#6A51A3", "#3F007D"]},
        "independence_duplicate_candidate_pct": {"label": "Candidatos a duplicidade, %", "palette": ["#FFF7EC", "#FDD49E", "#FC8D59", "#D7301F", "#7F0000"]},
        "documentary_flagged_wells_pct": {"label": "Poços com alertas documentais, %", "palette": ["#FFF7EC", "#FDD49E", "#FC8D59", "#D7301F", "#7F0000"]},
    },
    "interpretation_note": "As paletas representam magnitude da métrica selecionada. Não representam potencial aquífero, qualidade total ou prioridade.",
}
style_metadata["scales"] = {}
for scale in SCALES:
    frame = pd.read_csv(OUT / f"effective_knowledge_{scale}km2.csv", encoding="utf-8-sig")
    frame = frame[frame["n_wells"] > 0]
    style_metadata["scales"][str(scale)] = {}
    for field in style_metadata["metrics"]:
        values = pd.to_numeric(frame[field], errors="coerce").dropna()
        style_metadata["scales"][str(scale)][field] = {
            "min": None if values.empty else float(values.min()),
            "max": None if values.empty else float(values.max()),
            "quantiles": [] if values.empty else [float(values.quantile(q)) for q in (0.2, 0.4, 0.6, 0.8)],
        }
for target in (OUT, WEB):
    with open(target / "effective_knowledge_style_metadata.json", "w", encoding="utf-8") as handle:
        json.dump(style_metadata, handle, ensure_ascii=False, indent=2)


# Acrescenta o vetor V2.2 às fichas sem remover os blocos anteriores.
details_path = ROOT / "docs/data/well_details.json"
with open(details_path, encoding="utf-8") as handle:
    details = json.load(handle)
well_index = well.set_index("well_id")
for wid, detail in details.items():
    if wid not in well_index.index:
        continue
    r = well_index.loc[wid]
    detail["effective_knowledge"] = {
        "method_version": METHOD_VERSION,
        "cutoff_date": CUTOFF_DATE,
        "states": {
            "spatial": r["spatial_state"],
            "hydrostratigraphic": r["hydrostrat_state"],
            "vertical": r["vertical_state"],
            "hydraulic": r["hydraulic_state"],
            "hydrochemical": r["hydrochemical_state"],
            "temporal": r["temporal_state"],
            "independence": r["independence_state"],
            "documentary_quality": r["documentary_state"],
            "uncertainty": r["uncertainty_state"],
        },
        "uncertainty_codes": str(r["uncertainty_codes"]).split("|"),
        "interpretation_note": "Vetor descritivo não agregado. Não é índice, potencial ou prioridade.",
    }
with open(details_path, "w", encoding="utf-8") as handle:
    json.dump(details, handle, ensure_ascii=False, separators=(",", ":"))


# Auditorias finais da rotina
if int(scale_summary["canonical_wells_assigned_n"].min()) != 3877 or int(scale_summary["canonical_wells_assigned_n"].max()) != 3877:
    raise RuntimeError("Alguma escala não preservou a base canônica")
if not (well["independence_state"] == "UNKNOWN_INDEPENDENCIA_HIDROGEOLOGICA_NAO_DEMONSTRADA").all():
    raise RuntimeError("A independência foi indevidamente inferida")
if "score" in "|".join(well.columns).lower() or "priority" in "|".join(well.columns).lower():
    raise RuntimeError("Campo agregador proibido detectado na tabela por poço")

print(f"OK {len(well)} poços, {sum(x['grid_cells_n'] for x in scale_summaries)} células em cinco escalas")
