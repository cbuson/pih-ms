#!/usr/bin/env python3
"""Amplia malhas de evidência e estrutura espacial para cinco escalas.

Entradas científicas congeladas
  data/derived/evidence/E01 a E12
  docs/data/scale_study/scale_primary_100 a 1000km2.geojson
  data/derived/spatial_structure/support_points_5km.csv

As cinco escalas são recalculadas diretamente. A família candidata anterior de
250, 500 e 1000 km2 é arquivada uma única vez e não é misturada com a família
principal O00. O script não calcula score PIH, pesos, interpolação ou predição.
"""
from __future__ import annotations

from collections import Counter
from itertools import combinations
from pathlib import Path
import hashlib
import json
import math
import shutil

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from scipy.stats import spearmanr
from shapely.geometry import box


ROOT = Path(__file__).resolve().parents[1]
DER_EVIDENCE = ROOT / "data/derived/evidence"
WEB_EVIDENCE = ROOT / "docs/data/evidence"
DER_GRID = ROOT / "data/derived/grid_evidence"
WEB_GRID = ROOT / "docs/data/grid_evidence"
DER_SPATIAL = ROOT / "data/derived/spatial_structure"
WEB_SPATIAL = ROOT / "docs/data/spatial_structure"
PROVENANCE = ROOT / "provenance"
SCALES = (100, 150, 250, 500, 1000)
CODES = tuple(f"E{i:02d}" for i in range(1, 13))
METRIC_CRS = "EPSG:5880"
GRID_FAMILY = "SCALE_PRIMARY_O00_V1"
DATA_CUTOFF = "2026-08-29"
FALLBACK_TOLERANCE_M = 50.0
MICRO_SCALES_KM = (2.5, 5.0, 10.0)


def archive_once() -> None:
    """Preserva a família candidata anterior antes de substituir a vista atual."""
    grid_history = ROOT / "data/derived/grid_evidence_historical_candidate_v13"
    if not grid_history.exists():
        grid_history.mkdir(parents=True)
        for name in (
            "grid_assignment_audit.csv",
            "grid_evidence_long.csv",
            "grid_scale_summary.csv",
            "grid_evidence_style_metadata.json",
        ):
            source = DER_GRID / name
            if not source.exists():
                source = WEB_GRID / name
            if source.exists():
                shutil.copy2(source, grid_history / source.name)
        for scale in (250, 500, 1000):
            for suffix in ("csv", "geojson"):
                source = DER_GRID / f"malha_evidencia_{scale}km2.{suffix}"
                if source.exists():
                    shutil.copy2(source, grid_history / source.name)
        (grid_history / "README.md").write_text(
            "# Família histórica de malhas de evidência\n\n"
            "Produto V1.3 baseado nas malhas candidatas PIH de 250, 500 e 1000 km². "
            "As contagens de células são 1.554, 793 e 412. Esta família é preservada "
            "para rastreabilidade e não integra as comparações correntes da V2.3.\n",
            encoding="utf-8",
        )

    spatial_history = ROOT / "data/derived/spatial_structure_historical_candidate_v16"
    if not spatial_history.exists():
        spatial_history.mkdir(parents=True)
        for name in (
            "spatial_assignment_audit.csv",
            "spatial_structure_scale_summary.csv",
            "scale_stability_evidence.csv",
            "spatial_structure_style_metadata.json",
            "maup_origin_concordance.csv",
            "maup_origin_sensitivity_summary.csv",
            "maup_variant_metadata.csv",
            "maup_variant_summary.csv",
        ):
            source = DER_SPATIAL / name
            if not source.exists():
                source = WEB_SPATIAL / name
            if source.exists():
                shutil.copy2(source, spatial_history / source.name)
        for scale in (250, 500, 1000):
            for suffix in ("csv", "geojson"):
                source = DER_SPATIAL / f"spatial_structure_{scale}km2.{suffix}"
                if source.exists():
                    shutil.copy2(source, spatial_history / source.name)
        (spatial_history / "README.md").write_text(
            "# Família histórica de estrutura espacial\n\n"
            "Produto V1.6 calculado sobre a família candidata anterior de 250, 500 "
            "e 1000 km². É preservado para rastreabilidade e não integra as "
            "comparações correntes da V2.3.\n",
            encoding="utf-8",
        )


def read_evidence() -> dict[str, gpd.GeoDataFrame]:
    result = {}
    for code in CODES:
        paths = sorted(DER_EVIDENCE.glob(f"{code}_*.geojson"))
        if not paths:
            paths = sorted(WEB_EVIDENCE.glob(f"{code}_*.geojson"))
        if len(paths) != 1:
            raise RuntimeError(f"{code}: esperada uma feição GeoJSON, encontradas {len(paths)}")
        result[code] = gpd.read_file(paths[0]).to_crs(METRIC_CRS).reset_index(drop=True)
    return result


def read_primary_grid(scale: int) -> gpd.GeoDataFrame:
    path = ROOT / f"docs/data/scale_study/scale_primary_{scale}km2.geojson"
    grid = gpd.read_file(path).to_crs(METRIC_CRS)
    required = {
        "cell_id",
        "scale_km2",
        "variant",
        "area_effective_km2",
        "area_effective_pct_nominal",
        "geometry",
    }
    missing = required.difference(grid.columns)
    if missing:
        raise RuntimeError(f"{path}: campos ausentes {sorted(missing)}")
    grid = grid[list(required)].copy().sort_values("cell_id").reset_index(drop=True)
    if grid.cell_id.duplicated().any():
        raise RuntimeError(f"{scale}: cell_id duplicado")
    if set(grid.variant.astype(str)) != {"O00"}:
        raise RuntimeError(f"{scale}: a família principal deve usar somente O00")
    return grid


def assign_features(
    features: gpd.GeoDataFrame,
    grid: gpd.GeoDataFrame,
) -> tuple[pd.Series, int, list[dict[str, object]], list[int]]:
    """Atribuição topológica determinística com contingência documentada de 50 m."""
    assigned = np.full(len(features), -1, dtype=int)
    matches_per_feature: Counter[int] = Counter()

    pairs = grid.sindex.query(features.geometry, predicate="within")
    if pairs.size:
        order = np.lexsort((pairs[1], pairs[0]))
        feature_pos = pairs[0][order]
        grid_pos = pairs[1][order]
        for fp, gp in zip(feature_pos, grid_pos):
            matches_per_feature[int(fp)] += 1
            if assigned[int(fp)] < 0:
                assigned[int(fp)] = int(gp)

    missing = np.where(assigned < 0)[0]
    if len(missing):
        pairs = grid.sindex.query(features.iloc[missing].geometry, predicate="intersects")
        if pairs.size:
            order = np.lexsort((pairs[1], pairs[0]))
            feature_local = pairs[0][order]
            grid_pos = pairs[1][order]
            for local_pos, gp in zip(feature_local, grid_pos):
                fp = int(missing[int(local_pos)])
                matches_per_feature[fp] += 1
                if assigned[fp] < 0:
                    assigned[fp] = int(gp)

    fallbacks: list[dict[str, object]] = []
    for fp in np.where(assigned < 0)[0]:
        distances = grid.geometry.distance(features.geometry.iloc[int(fp)])
        gp = int(distances.idxmin())
        distance_m = float(distances.loc[gp])
        if distance_m <= FALLBACK_TOLERANCE_M:
            assigned[int(fp)] = gp
            props = features.iloc[int(fp)]
            feature_id = props.get("well_id", props.get("idt_ponto", int(fp)))
            fallbacks.append(
                {
                    "feature_index": int(fp),
                    "feature_id": str(feature_id),
                    "cell_id": str(grid.loc[gp, "cell_id"]),
                    "distance_m": distance_m,
                }
            )

    unassigned = [int(value) for value in np.where(assigned < 0)[0]]
    values = pd.Series(pd.NA, index=features.index, dtype="string", name="cell_id")
    valid = assigned >= 0
    values.loc[valid] = grid.iloc[assigned[valid]].cell_id.to_numpy()
    multiple = sum(1 for value in matches_per_feature.values() if value > 1)
    return values, multiple, fallbacks, unassigned


def state_for(code: str, n_base: int, n_evidence: int) -> str:
    if code == "E01":
        return "WELLS_PRESENT" if n_evidence > 0 else "UNKNOWN_NO_WELLS_IN_DATASET"
    if n_base == 0:
        return "UNKNOWN_NO_WELLS_IN_DATASET"
    if code == "E12":
        return "REVIEW_REQUIRED_PRESENT" if n_evidence > 0 else "NO_REVIEW_FLAG_IN_AUDITED_WELLS"
    return "EVIDENCE_PRESENT" if n_evidence > 0 else "NO_EVIDENCE_IN_AUDITED_WELLS"


def percentage(numerator: int | float, denominator: int | float) -> float | None:
    if not denominator:
        return None
    return round(float(numerator) / float(denominator) * 100.0, 4)


def compact_counts(values: pd.Series) -> str:
    counts = Counter(str(value) for value in values.dropna() if str(value).strip())
    return " | ".join(f"{key}:{value}" for key, value in sorted(counts.items()))


def add_descriptive_fields(
    output: gpd.GeoDataFrame,
    evidence: dict[str, gpd.GeoDataFrame],
    assignments: dict[str, pd.Series],
) -> None:
    def grouped(code: str, column: str):
        frame = evidence[code].copy()
        frame["cell_id"] = assignments[code]
        return frame.dropna(subset=["cell_id"]).groupby("cell_id")[column]

    depth = grouped("E02", "depth_m")
    output["E02_depth_median_m"] = output.cell_id.map(depth.median())
    output["E02_depth_p10_m"] = output.cell_id.map(depth.quantile(0.10))
    output["E02_depth_p90_m"] = output.cell_id.map(depth.quantile(0.90))

    aquifer = grouped("E03", "aquifer_informed")
    output["E03_aquifer_n_unique"] = output.cell_id.map(aquifer.nunique()).fillna(0).astype(int)

    for code in ("E04", "E05"):
        zero_review = grouped(code, "zero_requires_review").sum()
        output[f"{code}_zero_review_count"] = output.cell_id.map(zero_review).fillna(0).astype(int)

    tests = grouped("E07", "test_type").apply(compact_counts)
    output["E07_test_types"] = output.cell_id.map(tests).fillna("")

    transmissivity_review = grouped("E09", "zero_requires_review").sum()
    output["E09_zero_review_count"] = output.cell_id.map(transmissivity_review).fillna(0).astype(int)

    chem = evidence["E10"].copy()
    chem["cell_id"] = assignments["E10"]
    chem_group = chem.dropna(subset=["cell_id"]).groupby("cell_id")
    output["E10_available_fields_median"] = output.cell_id.map(chem_group.available_count.median())
    for field, label in (
        ("pH", "pH"),
        ("electrical_conductivity", "EC"),
        ("temperature", "temperature"),
        ("chemical_parameter", "chemical_parameter"),
    ):
        counts = chem_group[field].apply(lambda values: int(values.notna().sum()))
        output[f"E10_n_{label}"] = output.cell_id.map(counts).fillna(0).astype(int)

    age = grouped("E11", "age_years")
    output["E11_age_median_years"] = output.cell_id.map(age.median())
    output["E11_age_p25_years"] = output.cell_id.map(age.quantile(0.25))
    output["E11_age_p75_years"] = output.cell_id.map(age.quantile(0.75))

    comparisons = grouped("E12", "comparison_status").apply(compact_counts)
    output["E12_comparison_statuses"] = output.cell_id.map(comparisons).fillna("")


def quantile_breaks(values: pd.Series) -> list[int]:
    positive = pd.to_numeric(values, errors="coerce")
    positive = positive[positive > 0]
    breaks: list[int] = []
    for probability in (0.25, 0.50, 0.75, 0.90):
        if positive.empty:
            continue
        value = max(1, int(math.ceil(float(positive.quantile(probability)))))
        if value not in breaks:
            breaks.append(value)
    return breaks


def write_geojson(frame: gpd.GeoDataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.unlink(missing_ok=True)
    frame.to_crs(4326).to_file(path, driver="GeoJSON", index=False)


def build_grid_evidence(evidence: dict[str, gpd.GeoDataFrame]) -> dict[int, gpd.GeoDataFrame]:
    DER_GRID.mkdir(parents=True, exist_ok=True)
    WEB_GRID.mkdir(parents=True, exist_ok=True)
    registry = pd.read_csv(DER_EVIDENCE / "camadas_evidencia_registry.csv")
    registry_by_code = registry.set_index("code").to_dict("index")
    assignment_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []
    long_rows: list[dict[str, object]] = []
    style: dict[str, object] = {
        "_metadata": {
            "version": "2.3",
            "grid_family": GRID_FAMILY,
            "scales_km2": list(SCALES),
            "interpretation": "CONTAGEM_DIRETA_SEM_SCORE_PIH",
        }
    }
    outputs: dict[int, gpd.GeoDataFrame] = {}

    for scale in SCALES:
        grid = read_primary_grid(scale)
        output = grid.copy()
        output["grid_family"] = GRID_FAMILY
        assignments: dict[str, pd.Series] = {}

        for code in CODES:
            assigned, multiple, fallbacks, unassigned = assign_features(evidence[code], grid)
            assignments[code] = assigned
            counts = assigned.value_counts()
            output[f"n_{code}"] = output.cell_id.map(counts).fillna(0).astype(int)
            assignment_rows.append(
                {
                    "scale_km2": scale,
                    "grid_family": GRID_FAMILY,
                    "evidence_code": code,
                    "n_points": len(evidence[code]),
                    "n_assigned": int(assigned.notna().sum()),
                    "multi_intersections": multiple,
                    "fallback_nearest_50m": len(fallbacks),
                    "n_unassigned": len(unassigned),
                    "fallback_details": " | ".join(
                        f"{item['feature_id']}->{item['cell_id']}@{item['distance_m']:.2f}m"
                        for item in fallbacks
                    ),
                    "rule": "WITHIN; INTERSECTS para borda; desempate por cell_id; proximidade somente <=50 m",
                }
            )

        output["state_E01"] = [
            state_for("E01", int(value), int(value)) for value in output.n_E01
        ]
        for code in CODES[1:]:
            output[f"pct_{code}_of_E01"] = [
                percentage(value, base)
                for value, base in zip(output[f"n_{code}"], output.n_E01)
            ]
            output[f"state_{code}"] = [
                state_for(code, int(base), int(value))
                for value, base in zip(output[f"n_{code}"], output.n_E01)
            ]

        add_descriptive_fields(output, evidence, assignments)
        output["analysis_status"] = "MALHA_EVIDENCE_MATRIX_V2_FIVE_SCALES_NO_PIH_SCORE"
        output["cutoff_date"] = DATA_CUTOFF

        for _, row in output.iterrows():
            for code in CODES:
                n_evidence = int(row[f"n_{code}"])
                n_base = int(row.n_E01)
                long_rows.append(
                    {
                        "scale_km2": scale,
                        "grid_family": GRID_FAMILY,
                        "cell_id": row.cell_id,
                        "area_effective_km2": row.area_effective_km2,
                        "evidence_code": code,
                        "evidence_name": registry_by_code[code]["name"],
                        "n_evidence": n_evidence,
                        "n_wells_E01": n_base,
                        "pct_of_wells": (
                            100.0
                            if code == "E01" and n_base
                            else percentage(n_evidence, n_base) if code != "E01" else None
                        ),
                        "support_state": row[f"state_{code}"],
                        "interpretation": "DATA_SUPPORT_ONLY_NO_PIH_PRIORITY",
                    }
                )

        occupied = output.n_E01 > 0
        summary: dict[str, object] = {
            "scale_km2": scale,
            "grid_family": GRID_FAMILY,
            "n_cells": len(output),
            "cells_with_wells": int(occupied.sum()),
            "cells_without_wells": int((~occupied).sum()),
            "pct_cells_with_wells": round(float(occupied.mean() * 100), 2),
            "cells_with_one_well": int((output.n_E01 == 1).sum()),
            "median_wells_in_occupied_cells": float(output.loc[occupied, "n_E01"].median()),
            "p90_wells_in_occupied_cells": float(output.loc[occupied, "n_E01"].quantile(0.90)),
            "max_wells_in_cell": int(output.n_E01.max()),
        }
        for code in CODES[1:]:
            summary[f"cells_with_{code}"] = int((output[f"n_{code}"] > 0).sum())
            summary[f"cells_without_{code}_despite_wells"] = int(
                ((output.n_E01 > 0) & (output[f"n_{code}"] == 0)).sum()
            )
        summary_rows.append(summary)

        style[str(scale)] = {}
        for code in CODES:
            style[str(scale)][code] = {
                "positive_cells": int((output[f"n_{code}"] > 0).sum()),
                "max_count": int(output[f"n_{code}"].max()),
                "count_breaks": quantile_breaks(output[f"n_{code}"]),
            }

        csv_path = DER_GRID / f"malha_evidencia_{scale}km2.csv"
        output.drop(columns="geometry").to_csv(csv_path, index=False, encoding="utf-8-sig")
        write_geojson(output, DER_GRID / f"malha_evidencia_{scale}km2.geojson")
        write_geojson(output, WEB_GRID / f"malha_evidencia_{scale}km2.geojson")
        outputs[scale] = output

    pd.DataFrame(assignment_rows).to_csv(
        DER_GRID / "grid_assignment_audit.csv", index=False, encoding="utf-8-sig"
    )
    pd.DataFrame(summary_rows).to_csv(
        DER_GRID / "grid_scale_summary.csv", index=False, encoding="utf-8-sig"
    )
    pd.DataFrame(long_rows).to_csv(
        DER_GRID / "grid_evidence_long.csv", index=False, encoding="utf-8-sig"
    )
    shutil.copy2(DER_GRID / "grid_scale_summary.csv", WEB_GRID / "grid_scale_summary.csv")
    (DER_GRID / "grid_evidence_style_metadata.json").write_text(
        json.dumps(style, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    shutil.copy2(
        DER_GRID / "grid_evidence_style_metadata.json",
        WEB_GRID / "grid_evidence_style_metadata.json",
    )
    return outputs


def numeric_quantile(values, probability: float) -> float:
    array = np.asarray(values, dtype=float)
    array = array[np.isfinite(array)]
    return float(np.quantile(array, probability)) if len(array) else np.nan


def normalized_entropy(counts) -> float:
    array = np.asarray(list(counts), dtype=float)
    array = array[array > 0]
    if len(array) < 2:
        return np.nan
    proportions = array / array.sum()
    return float(-(proportions * np.log(proportions)).sum() / np.log(len(array)))


def micro_tag(km: float) -> str:
    return "2p5km" if abs(km - 2.5) < 1e-8 else f"{int(km)}km"


def build_spatial_structure(
    evidence: dict[str, gpd.GeoDataFrame],
    grids: dict[int, gpd.GeoDataFrame],
) -> None:
    DER_SPATIAL.mkdir(parents=True, exist_ok=True)
    WEB_SPATIAL.mkdir(parents=True, exist_ok=True)
    state = gpd.read_file(ROOT / "docs/data/limite_ms_ibge_2025.geojson").to_crs(METRIC_CRS)
    state_geom = state.geometry.union_all()
    min_x, min_y, _, _ = state_geom.bounds
    origins = {
        km: (
            math.floor(min_x / (km * 1000)) * km * 1000,
            math.floor(min_y / (km * 1000)) * km * 1000,
        )
        for km in MICRO_SCALES_KM
    }

    support_table = pd.read_csv(DER_SPATIAL / "support_points_5km.csv")
    support = gpd.GeoDataFrame(
        support_table.copy(),
        geometry=gpd.points_from_xy(support_table.x_5880, support_table.y_5880),
        crs=METRIC_CRS,
    )
    if len(support) != 14284:
        raise RuntimeError(f"Suporte fixo alterado: {len(support)} pontos")
    for code in CODES:
        if f"gap_{code}_km" not in support:
            raise RuntimeError(f"Suporte sem gap_{code}_km")

    e01 = evidence["E01"].copy()
    xy = np.column_stack((e01.geometry.x, e01.geometry.y))
    nearest_tree = cKDTree(xy)
    nearest_distance, _ = nearest_tree.query(xy, k=2)
    e01["nn_global_km"] = nearest_distance[:, 1] / 1000.0
    evidence_trees = {
        code: cKDTree(np.column_stack((frame.geometry.x, frame.geometry.y)))
        for code, frame in evidence.items()
    }

    for km in MICRO_SCALES_KM:
        metres = km * 1000.0
        origin_x, origin_y = origins[km]
        e01[f"micro_{micro_tag(km)}"] = list(
            zip(
                np.floor((e01.geometry.x - origin_x) / metres).astype(int),
                np.floor((e01.geometry.y - origin_y) / metres).astype(int),
            )
        )

    def micro_square(bin_id: tuple[int, int], km: float):
        ix, iy = bin_id
        metres = km * 1000.0
        origin_x, origin_y = origins[km]
        x = origin_x + ix * metres
        y = origin_y + iy * metres
        return box(x, y, x + metres, y + metres)

    outputs: dict[int, pd.DataFrame] = {}
    support_assignments: dict[int, pd.Series] = {}
    audit_rows: list[dict[str, object]] = []

    for scale in SCALES:
        grid = grids[scale].copy().to_crs(METRIC_CRS).sort_values("cell_id").reset_index(drop=True)
        e01_assignment, multiple, fallbacks, unassigned = assign_features(e01, grid)
        support_assignment, support_multiple, support_fallbacks, support_unassigned = assign_features(
            support, grid
        )
        if unassigned or support_unassigned:
            raise RuntimeError(
                f"{scale}: E01 sem célula {len(unassigned)}, suporte sem célula {len(support_unassigned)}"
            )
        audit_rows.append(
            {
                "scale_km2": scale,
                "grid_family": GRID_FAMILY,
                "n_E01": len(e01),
                "E01_multi_intersections": multiple,
                "E01_fallback_50m": len(fallbacks),
                "E01_unassigned": len(unassigned),
                "support_points_n": len(support),
                "support_multi_intersections": support_multiple,
                "support_fallback_50m": len(support_fallbacks),
                "support_unassigned": len(support_unassigned),
            }
        )

        wells = e01.copy()
        wells["cell_id"] = e01_assignment
        well_groups = {
            cell_id: frame for cell_id, frame in wells.dropna(subset=["cell_id"]).groupby("cell_id")
        }
        support_scale = support.copy()
        support_scale["cell_id"] = support_assignment
        support_groups = {
            cell_id: frame
            for cell_id, frame in support_scale.dropna(subset=["cell_id"]).groupby("cell_id")
        }
        support_assignments[scale] = support_assignment
        rows: list[dict[str, object]] = []

        for _, cell in grid.iterrows():
            cell_id = cell.cell_id
            geometry = cell.geometry
            area_km2 = float(geometry.area / 1e6)
            group = well_groups.get(cell_id)
            n_wells = 0 if group is None else len(group)
            row: dict[str, object] = {
                "cell_id": cell_id,
                "scale_km2": scale,
                "grid_family": GRID_FAMILY,
                "area_effective_km2": area_km2,
                "n_E01": n_wells,
                "metric_crs": METRIC_CRS,
                "classification_status": "DESCRIPTIVE_NO_PIH_SCORE",
            }

            if n_wells:
                row["nn_global_median_km"] = numeric_quantile(group.nn_global_km, 0.50)
                row["nn_global_p90_km"] = numeric_quantile(group.nn_global_km, 0.90)
                group_xy = np.column_stack((group.geometry.x, group.geometry.y))
                mean_x, mean_y = group_xy.mean(axis=0)
                centroid = geometry.centroid
                offset_km = math.hypot(mean_x - centroid.x, mean_y - centroid.y) / 1000.0
                equivalent_radius_km = math.sqrt(geometry.area / math.pi) / 1000.0
                row["mean_center_offset_km"] = offset_km
                row["mean_center_offset_norm_eqradius"] = offset_km / equivalent_radius_km
                if n_wells >= 2:
                    local_tree = cKDTree(group_xy)
                    local_distance, _ = local_tree.query(group_xy, k=2)
                    row["nn_within_median_km"] = numeric_quantile(local_distance[:, 1] / 1000, 0.50)
                    row["nn_within_p90_km"] = numeric_quantile(local_distance[:, 1] / 1000, 0.90)
                else:
                    row["nn_within_median_km"] = np.nan
                    row["nn_within_p90_km"] = np.nan
                if n_wells >= 3:
                    hull = group.geometry.union_all().convex_hull
                    row["convex_hull_area_ratio"] = (
                        float(hull.area / geometry.area)
                        if hull.geom_type in ("Polygon", "MultiPolygon")
                        else 0.0
                    )
                else:
                    row["convex_hull_area_ratio"] = np.nan
                for km in MICRO_SCALES_KM:
                    tag = micro_tag(km)
                    counts = Counter(group[f"micro_{tag}"])
                    covered_area = sum(
                        geometry.intersection(micro_square(bin_id, km)).area for bin_id in counts
                    )
                    occupied_units = len(counts)
                    row[f"support_units_{tag}_n"] = occupied_units
                    row[f"support_area_{tag}_pct"] = min(100.0, covered_area / geometry.area * 100.0)
                    row[f"redundancy_proxy_{tag}"] = 1.0 - occupied_units / n_wells
                    row[f"entropy_norm_{tag}"] = normalized_entropy(counts.values())
                    row[f"dominance_{tag}_pct"] = max(counts.values()) / n_wells * 100.0
            else:
                for field in (
                    "nn_global_median_km",
                    "nn_global_p90_km",
                    "mean_center_offset_km",
                    "mean_center_offset_norm_eqradius",
                    "nn_within_median_km",
                    "nn_within_p90_km",
                    "convex_hull_area_ratio",
                ):
                    row[field] = np.nan
                for km in MICRO_SCALES_KM:
                    tag = micro_tag(km)
                    row[f"support_units_{tag}_n"] = 0
                    row[f"support_area_{tag}_pct"] = 0.0
                    row[f"redundancy_proxy_{tag}"] = np.nan
                    row[f"entropy_norm_{tag}"] = np.nan
                    row[f"dominance_{tag}_pct"] = np.nan

            support_group = support_groups.get(cell_id)
            if support_group is None or support_group.empty:
                representative = geometry.representative_point()
                point_xy = np.array([[representative.x, representative.y]])
                row["gap_support_points_n"] = 0
                row["gap_support_fallback"] = "REPRESENTATIVE_POINT"
                for code, tree in evidence_trees.items():
                    distance, _ = tree.query(point_xy, k=1)
                    value = float(distance[0] / 1000.0)
                    row[f"gap_{code}_median_km"] = value
                    row[f"gap_{code}_p90_km"] = value
                    row[f"gap_{code}_max_km"] = value
            else:
                row["gap_support_points_n"] = len(support_group)
                row["gap_support_fallback"] = "NONE"
                for code in CODES:
                    values = support_group[f"gap_{code}_km"]
                    row[f"gap_{code}_median_km"] = numeric_quantile(values, 0.50)
                    row[f"gap_{code}_p90_km"] = numeric_quantile(values, 0.90)
                    row[f"gap_{code}_max_km"] = numeric_quantile(values, 1.00)
            rows.append(row)

        frame = pd.DataFrame(rows)
        source = grid.drop(columns="geometry")
        keep = ["cell_id"] + [
            column
            for column in source.columns
            if (column.startswith("n_E") and column != "n_E01")
            or column.startswith("state_E")
            or column.startswith("pct_E")
        ]
        frame = frame.merge(source[keep], on="cell_id", how="left", validate="one_to_one")
        outputs[scale] = frame
        frame.to_csv(
            DER_SPATIAL / f"spatial_structure_{scale}km2.csv",
            index=False,
            encoding="utf-8-sig",
        )
        web = grid[["cell_id", "geometry"]].merge(frame, on="cell_id", validate="one_to_one")
        write_geojson(web, DER_SPATIAL / f"spatial_structure_{scale}km2.geojson")
        write_geojson(web, WEB_SPATIAL / f"spatial_structure_{scale}km2.geojson")

    pd.DataFrame(audit_rows).to_csv(
        DER_SPATIAL / "spatial_assignment_audit.csv", index=False, encoding="utf-8-sig"
    )

    support_metrics: dict[int, pd.DataFrame] = {}
    for scale, frame in outputs.items():
        indexed = frame.set_index("cell_id")
        current = pd.DataFrame({"support_id": support.support_id})
        current["cell_id"] = support_assignments[scale]
        for code in CODES:
            count_field = f"n_{code}"
            density = indexed[count_field] / indexed.area_effective_km2 * 100.0
            current[f"{code}_density100"] = current.cell_id.map(density)
            current[f"{code}_presence"] = (
                current.cell_id.map(indexed[count_field] > 0).fillna(False).astype(bool)
            )
        support_metrics[scale] = current.set_index("support_id")

    stability_rows: list[dict[str, object]] = []
    for code in CODES:
        for scale_a, scale_b in combinations(SCALES, 2):
            density_a = support_metrics[scale_a][f"{code}_density100"]
            density_b = support_metrics[scale_b][f"{code}_density100"]
            valid = density_a.notna() & density_b.notna()
            rho = (
                float(spearmanr(density_a[valid], density_b[valid]).statistic)
                if valid.sum() > 2
                and density_a[valid].nunique() > 1
                and density_b[valid].nunique() > 1
                else np.nan
            )
            presence_a = support_metrics[scale_a][f"{code}_presence"]
            presence_b = support_metrics[scale_b][f"{code}_presence"]
            union = int((presence_a | presence_b).sum())
            intersection = int((presence_a & presence_b).sum())
            stability_rows.append(
                {
                    "evidence_code": code,
                    "scale_a_km2": scale_a,
                    "scale_b_km2": scale_b,
                    "grid_family": GRID_FAMILY,
                    "support_points_n": len(presence_a),
                    "spearman_density_per100km2": rho,
                    "presence_jaccard": intersection / union if union else np.nan,
                    "presence_mismatch_pct": float((presence_a != presence_b).mean() * 100),
                    "presence_a_pct": float(presence_a.mean() * 100),
                    "presence_b_pct": float(presence_b.mean() * 100),
                }
            )
    pd.DataFrame(stability_rows).to_csv(
        DER_SPATIAL / "scale_stability_evidence.csv", index=False, encoding="utf-8-sig"
    )

    summary_rows: list[dict[str, object]] = []
    for scale, frame in outputs.items():
        occupied = frame[frame.n_E01 > 0]
        summary_rows.append(
            {
                "scale_km2": scale,
                "grid_family": GRID_FAMILY,
                "n_cells": len(frame),
                "cells_with_E01": int((frame.n_E01 > 0).sum()),
                "median_nn_global_km_occupied": occupied.nn_global_median_km.median(),
                "median_support_area_2p5km_pct_occupied": occupied.support_area_2p5km_pct.median(),
                "median_support_area_5km_pct_occupied": occupied.support_area_5km_pct.median(),
                "median_support_area_10km_pct_occupied": occupied.support_area_10km_pct.median(),
                "median_redundancy_proxy_5km_occupied": occupied.redundancy_proxy_5km.median(),
                "median_entropy_5km_occupied": occupied.entropy_norm_5km.median(),
                "median_gap_E01_p90_km_all_cells": frame.gap_E01_p90_km.median(),
                "median_gap_E07_p90_km_all_cells": frame.gap_E07_p90_km.median(),
                "median_gap_E09_p90_km_all_cells": frame.gap_E09_p90_km.median(),
                "median_gap_E10_p90_km_all_cells": frame.gap_E10_p90_km.median(),
            }
        )
    pd.DataFrame(summary_rows).to_csv(
        DER_SPATIAL / "spatial_structure_scale_summary.csv",
        index=False,
        encoding="utf-8-sig",
    )
    shutil.copy2(
        DER_SPATIAL / "spatial_structure_scale_summary.csv",
        WEB_SPATIAL / "spatial_structure_scale_summary.csv",
    )

    metrics = {
        "gap_p90": {"label": "Distância P90 à evidência", "unit": "km", "kind": "gap"},
        "gap_max": {"label": "Distância máxima à evidência", "unit": "km", "kind": "gap"},
        "support_area_5km_pct": {
            "label": "Cobertura de suporte espacial 5 km · E01",
            "unit": "%",
            "kind": "e01",
        },
        "redundancy_proxy_5km": {
            "label": "Redundância espacial proxy 5 km · E01",
            "unit": "0–1",
            "kind": "e01",
        },
        "entropy_norm_5km": {
            "label": "Entropia espacial normalizada 5 km · E01",
            "unit": "0–1",
            "kind": "e01",
        },
        "nn_global_median_km": {
            "label": "Vizinho mais próximo mediano · E01",
            "unit": "km",
            "kind": "e01",
        },
    }
    style: dict[str, object] = {
        "version": "2.3",
        "grid_family": GRID_FAMILY,
        "metrics": metrics,
        "scales": {},
    }
    for scale, frame in outputs.items():
        style["scales"][str(scale)] = {}
        for metric, definition in metrics.items():
            if definition["kind"] == "gap":
                style["scales"][str(scale)][metric] = {}
                for code in CODES:
                    field = f"gap_{code}_{'p90_km' if metric == 'gap_p90' else 'max_km'}"
                    values = pd.to_numeric(frame[field], errors="coerce").dropna()
                    style["scales"][str(scale)][metric][code] = {
                        "quantiles": [float(values.quantile(value)) for value in (0.2, 0.4, 0.6, 0.8)],
                        "min": float(values.min()),
                        "max": float(values.max()),
                    }
            else:
                values = pd.to_numeric(frame[metric], errors="coerce").dropna()
                style["scales"][str(scale)][metric] = {
                    "quantiles": [float(values.quantile(value)) for value in (0.2, 0.4, 0.6, 0.8)],
                    "min": float(values.min()) if len(values) else None,
                    "max": float(values.max()) if len(values) else None,
                }
    (DER_SPATIAL / "spatial_structure_style_metadata.json").write_text(
        json.dumps(style, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    shutil.copy2(
        DER_SPATIAL / "spatial_structure_style_metadata.json",
        WEB_SPATIAL / "spatial_structure_style_metadata.json",
    )


def write_manifest(directory: Path, target: Path) -> None:
    rows = []
    for path in sorted(directory.glob("*")):
        if path.is_file():
            rows.append(
                {
                    "file": str(path.relative_to(ROOT)),
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "bytes": path.stat().st_size,
                }
            )
    pd.DataFrame(rows).to_csv(target, index=False, encoding="utf-8-sig")


def validate(evidence: dict[str, gpd.GeoDataFrame]) -> None:
    expected_cells = {100: 3763, 150: 2525, 250: 1537, 500: 791, 1000: 413}
    for scale, expected in expected_cells.items():
        grid = pd.read_csv(DER_GRID / f"malha_evidencia_{scale}km2.csv")
        spatial = pd.read_csv(DER_SPATIAL / f"spatial_structure_{scale}km2.csv")
        if len(grid) != expected or len(spatial) != expected:
            raise RuntimeError(f"{scale}: cardinalidade incorreta")
        if set(grid.cell_id) != set(spatial.cell_id):
            raise RuntimeError(f"{scale}: IDs divergentes entre módulos")
        for code in CODES:
            if int(grid[f"n_{code}"].sum()) != len(evidence[code]):
                raise RuntimeError(f"{scale} {code}: soma divergente")
        if int(spatial.n_E01.sum()) != len(evidence["E01"]):
            raise RuntimeError(f"{scale}: soma E01 divergente na estrutura espacial")
    audit = pd.read_csv(DER_GRID / "grid_assignment_audit.csv")
    spatial_audit = pd.read_csv(DER_SPATIAL / "spatial_assignment_audit.csv")
    if int(audit.n_unassigned.sum()) != 0:
        raise RuntimeError("Há evidências sem célula")
    if int(spatial_audit.E01_unassigned.sum()) != 0 or int(spatial_audit.support_unassigned.sum()) != 0:
        raise RuntimeError("Há pontos sem célula na estrutura espacial")


def main() -> None:
    archive_once()
    evidence = read_evidence()
    grids = build_grid_evidence(evidence)
    build_spatial_structure(evidence, grids)
    validate(evidence)
    write_manifest(DER_GRID, PROVENANCE / "grid_evidence_manifest_v23.csv")
    write_manifest(DER_SPATIAL, PROVENANCE / "spatial_structure_manifest_v23.csv")
    print(
        json.dumps(
            {
                "status": "OK",
                "version": "2.3",
                "grid_family": GRID_FAMILY,
                "scales": list(SCALES),
                "cells": {scale: len(grids[scale]) for scale in SCALES},
                "evidence_counts": {code: len(evidence[code]) for code in CODES},
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
