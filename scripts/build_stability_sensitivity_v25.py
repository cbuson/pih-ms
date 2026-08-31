#!/usr/bin/env python3
"""Constrói a análise PIH MS V2.5 de estabilidade e sensibilidade.

O suporte fixo de 5 km permite comparar cinco escalas e quatro origens sem
confundir mudança de malha com mudança de universo. Os estados são apenas
documentais. O módulo não calcula peso, score, prioridade, potencial,
interpolação, predição ou representatividade territorial.
"""
from __future__ import annotations

from itertools import combinations
from pathlib import Path
import json
import math
import shutil

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from shapely.geometry import Polygon


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/derived/stability_sensitivity"
WEB = ROOT / "docs/data/stability_sensitivity"
SCALES = (100, 150, 250, 500, 1000)
ORIGINS = (("O00", 0.0, 0.0), ("OX25", 0.25, 0.0), ("OY25", 0.0, 0.25), ("OXY25", 0.25, 0.25))
QUESTIONS = ("Q01", "Q02", "Q03", "Q04", "Q05")
EXPECTED_CELLS = {100: 3763, 150: 2525, 250: 1537, 500: 791, 1000: 413}
METHOD = "PIH_MS_V2.5_ESTABILIDADE_SENSIBILIDADE_V1"
GRID_FAMILY = "SCALE_PRIMARY_O00_V1"
CUTOFF = "2026-08-29"
CRS = "EPSG:5880"

STATE_LABELS = {
    0: "SEM_POCOS_NO_CONJUNTO_AUDITADO",
    1: "POCOS_SEM_EVIDENCIA_DIRETA_DA_PERGUNTA",
    2: "EVIDENCIA_DIRETA_PRESENTE",
}


def write_csv(frame: pd.DataFrame, name: str) -> None:
    frame.to_csv(OUT / name, index=False, encoding="utf-8-sig")


def pct(num: int | float, den: int | float) -> float | None:
    return round(100.0 * float(num) / float(den), 6) if den else None


def make_hex(cx: float, cy: float, side: float) -> Polygon:
    return Polygon(
        [
            (cx + side * math.cos(math.radians(30 + 60 * k)), cy + side * math.sin(math.radians(30 + 60 * k)))
            for k in range(6)
        ]
    )


def hex_params(area_km2: int) -> tuple[float, float, float]:
    side = math.sqrt(2 * area_km2 * 1_000_000.0 / (3 * math.sqrt(3)))
    return side, math.sqrt(3) * side, 1.5 * side


def build_shifted_grid(
    area_km2: int,
    origin: str,
    fx: float,
    fy: float,
    state_geom,
) -> gpd.GeoDataFrame:
    side, width, row_spacing = hex_params(area_km2)
    minx, miny, maxx, maxy = state_geom.bounds
    base_x = math.floor((minx - width) / width) * width + fx * width
    base_y = math.floor((miny - 2 * side) / row_spacing) * row_spacing + fy * row_spacing
    geoms: list[Polygon] = []
    ids: list[str] = []
    y = base_y
    row = 0
    while y <= maxy + 2 * side:
        x = base_x + (row % 2) * width / 2
        while x <= maxx + width:
            geom = make_hex(x, y, side)
            if geom.intersects(state_geom):
                ids.append(f"SCALE-{area_km2}-{origin}-{len(ids) + 1:05d}")
                geoms.append(geom)
            x += width
        y += row_spacing
        row += 1
    return gpd.GeoDataFrame(
        {"cell_id": ids, "scale_km2": area_km2, "variant": origin},
        geometry=geoms,
        crs=CRS,
    ).reset_index(drop=True)


def assign_idx(points: gpd.GeoDataFrame, grid: gpd.GeoDataFrame) -> np.ndarray:
    assigned = np.full(len(points), -1, dtype=int)
    pairs = grid.sindex.query(points.geometry, predicate="within")
    if pairs.size:
        order = np.lexsort((pairs[1], pairs[0]))
        point_pos, grid_pos = pairs[0][order], pairs[1][order]
        first = np.r_[True, point_pos[1:] != point_pos[:-1]]
        assigned[point_pos[first]] = grid_pos[first]
    missing = np.where(assigned < 0)[0]
    if len(missing):
        pairs = grid.sindex.query(points.iloc[missing].geometry, predicate="intersects")
        if pairs.size:
            order = np.lexsort((pairs[1], pairs[0]))
            point_local, grid_pos = pairs[0][order], pairs[1][order]
            first = np.r_[True, point_local[1:] != point_local[:-1]]
            assigned[missing[point_local[first]]] = grid_pos[first]
    if (assigned < 0).any():
        raise RuntimeError(f"{int((assigned < 0).sum())} pontos não atribuídos à malha")
    return assigned


def state_from_counts(n_wells: np.ndarray, n_direct: np.ndarray) -> np.ndarray:
    return np.where(n_wells == 0, 0, np.where(n_direct > 0, 2, 1)).astype(np.int8)


def concordance(a: np.ndarray, b: np.ndarray) -> dict[str, float | int | None]:
    direct_a = a == 2
    direct_b = b == 2
    union = int(np.logical_or(direct_a, direct_b).sum())
    inter = int(np.logical_and(direct_a, direct_b).sum())
    rho = None
    if np.std(a) > 0 and np.std(b) > 0:
        rho = float(spearmanr(a, b).statistic)
    return {
        "support_points_n": len(a),
        "exact_state_agreement_n": int((a == b).sum()),
        "exact_state_agreement_pct": pct(int((a == b).sum()), len(a)),
        "direct_presence_jaccard": round(inter / union, 8) if union else 1.0,
        "direct_presence_mismatch_n": int((direct_a != direct_b).sum()),
        "direct_presence_mismatch_pct": pct(int((direct_a != direct_b).sum()), len(a)),
        "spearman_state_code": rho,
    }


def mode_text(values: pd.Series) -> str:
    clean = values.dropna().astype(str)
    if clean.empty:
        return ""
    counts = clean.value_counts()
    return str(sorted(counts[counts == counts.max()].index)[0])


def build() -> dict[str, pd.DataFrame]:
    OUT.mkdir(parents=True, exist_ok=True)
    WEB.mkdir(parents=True, exist_ok=True)

    support_base = pd.read_csv(ROOT / "data/derived/spatial_structure/support_points_5km.csv")
    support_strata = pd.read_csv(ROOT / "data/derived/stratified_scale/support_strata_assignment.csv")
    support_base = support_base.merge(
        support_strata[["support_id", "unit", "unit_assignment_status", "domain", "domain_assignment_status"]],
        on="support_id",
        how="left",
        validate="one_to_one",
    )
    support = gpd.GeoDataFrame(
        support_base,
        geometry=gpd.points_from_xy(support_base.x_5880, support_base.y_5880),
        crs=CRS,
    ).reset_index(drop=True)
    if len(support) != 14284:
        raise RuntimeError("O suporte fixo deve conter 14.284 pontos")

    well_questions = pd.read_csv(OUT.parent / "question_sufficiency/well_question_sufficiency_long.csv", low_memory=False)
    well_base = well_questions[well_questions.question_code == "Q01"][["well_id", "longitude", "latitude"]].copy()
    wells = gpd.GeoDataFrame(
        well_base,
        geometry=gpd.points_from_xy(well_base.longitude, well_base.latitude),
        crs="EPSG:4326",
    ).to_crs(CRS).reset_index(drop=True)
    if len(wells) != 3877:
        raise RuntimeError("O conjunto canônico deve conter 3.877 poços")
    well_index = {str(value): i for i, value in enumerate(wells.well_id)}
    direct = np.zeros((len(wells), len(QUESTIONS)), dtype=np.int8)
    for qi, question in enumerate(QUESTIONS):
        subset = well_questions[well_questions.question_code == question]
        for row in subset.itertuples(index=False):
            direct[well_index[str(row.well_id)], qi] = int(bool(row.direct_evidence_present))

    state_boundary = gpd.read_file(ROOT / "docs/data/limite_ms_ibge_2025.geojson").to_crs(CRS)
    state_geom = state_boundary.geometry.union_all()
    states: dict[tuple[int, str, str], np.ndarray] = {}
    support_cells: dict[tuple[int, str], np.ndarray] = {}
    well_cells: dict[tuple[int, str], np.ndarray] = {}
    cell_well_counts: dict[tuple[int, str], np.ndarray] = {}
    cell_direct_counts: dict[tuple[int, str, str], np.ndarray] = {}
    primary_grids: dict[int, gpd.GeoDataFrame] = {}
    origin_count_rows: list[dict[str, object]] = []

    for scale in SCALES:
        primary = gpd.read_file(ROOT / f"docs/data/scale_study/scale_primary_{scale}km2.geojson").to_crs(CRS)
        primary = primary.sort_values("cell_id").reset_index(drop=True)
        if len(primary) != EXPECTED_CELLS[scale]:
            raise RuntimeError(f"{scale} km² com cardinalidade inesperada")
        primary_grids[scale] = primary
        for origin, fx, fy in ORIGINS:
            grid = primary if origin == "O00" else build_shifted_grid(scale, origin, fx, fy, state_geom)
            si = assign_idx(support, grid)
            wi = assign_idx(wells, grid)
            support_cells[(scale, origin)] = si
            well_cells[(scale, origin)] = wi
            n_wells = np.bincount(wi, minlength=len(grid)).astype(int)
            cell_well_counts[(scale, origin)] = n_wells
            for qi, question in enumerate(QUESTIONS):
                n_direct = np.bincount(wi, weights=direct[:, qi], minlength=len(grid)).astype(int)
                cell_direct_counts[(scale, origin, question)] = n_direct
                support_state = state_from_counts(n_wells[si], n_direct[si])
                states[(scale, origin, question)] = support_state
                counts = np.bincount(support_state, minlength=3)
                origin_count_rows.append(
                    {
                        "scale_km2": scale,
                        "origin": origin,
                        "question_code": question,
                        "support_points_n": len(support),
                        "state_no_wells_n": int(counts[0]),
                        "state_wells_without_direct_n": int(counts[1]),
                        "state_direct_present_n": int(counts[2]),
                        "state_no_wells_pct": pct(counts[0], len(support)),
                        "state_wells_without_direct_pct": pct(counts[1], len(support)),
                        "state_direct_present_pct": pct(counts[2], len(support)),
                        "control_total_ok": int(counts.sum()) == len(support),
                        "method_version": METHOD,
                    }
                )

    support_scale_rows: list[pd.DataFrame] = []
    for scale in SCALES:
        si = support_cells[(scale, "O00")]
        grid = primary_grids[scale]
        n_wells = cell_well_counts[(scale, "O00")]
        for question in QUESTIONS:
            n_direct = cell_direct_counts[(scale, "O00", question)]
            state = states[(scale, "O00", question)]
            support_scale_rows.append(
                pd.DataFrame(
                    {
                        "support_id": support.support_id,
                        "x_5880": support.x_5880,
                        "y_5880": support.y_5880,
                        "hydro_surface_unit": support.unit,
                        "hydro_unit_assignment_status": support.unit_assignment_status,
                        "hydro_surface_domain": support.domain,
                        "hydro_domain_assignment_status": support.domain_assignment_status,
                        "question_code": question,
                        "scale_km2": scale,
                        "origin": "O00",
                        "cell_id": grid.cell_id.to_numpy()[si],
                        "cell_n_wells": n_wells[si],
                        "cell_direct_evidence_n": n_direct[si],
                        "state_code": state,
                        "state_label": [STATE_LABELS[int(value)] for value in state],
                        "direct_evidence_present_in_cell": state == 2,
                        "weight_used": False,
                        "score_used": False,
                        "method_version": METHOD,
                    }
                )
            )
    support_scale = pd.concat(support_scale_rows, ignore_index=True)

    support_question_frames: list[pd.DataFrame] = []
    cross_summary_rows: list[dict[str, object]] = []
    cross_pair_rows: list[dict[str, object]] = []
    origin_summary_rows: list[dict[str, object]] = []
    origin_pair_rows: list[dict[str, object]] = []
    support_question_lookup: dict[str, pd.DataFrame] = {}
    origin_support_flags: dict[tuple[int, str], pd.DataFrame] = {}

    for question in QUESTIONS:
        matrix = np.column_stack([states[(scale, "O00", question)] for scale in SCALES])
        exact = np.all(matrix == matrix[:, [0]], axis=1)
        direct_matrix = matrix == 2
        direct_all = direct_matrix.all(axis=1)
        direct_any = direct_matrix.any(axis=1)
        direct_some = direct_any & ~direct_all
        direct_none = ~direct_any
        frame = pd.DataFrame(
            {
                "support_id": support.support_id,
                "x_5880": support.x_5880,
                "y_5880": support.y_5880,
                "hydro_surface_unit": support.unit,
                "hydro_unit_assignment_status": support.unit_assignment_status,
                "hydro_surface_domain": support.domain,
                "hydro_domain_assignment_status": support.domain_assignment_status,
                "question_code": question,
                **{f"state_code_{scale}km2": matrix[:, index] for index, scale in enumerate(SCALES)},
                **{f"direct_presence_{scale}km2": direct_matrix[:, index] for index, scale in enumerate(SCALES)},
                "exact_state_all_scales": exact,
                "state_changes_across_scales_n": np.sum(matrix[:, 1:] != matrix[:, :-1], axis=1),
                "direct_scales_n": direct_matrix.sum(axis=1),
                "direct_all_scales": direct_all,
                "direct_some_scales": direct_some,
                "direct_no_scale": direct_none,
                "scale_selection_allowed": False,
                "weight_used": False,
                "score_used": False,
                "method_version": METHOD,
            }
        )
        support_question_frames.append(frame)
        support_question_lookup[question] = frame
        cross_summary_rows.append(
            {
                "question_code": question,
                "support_points_n": len(support),
                "exact_state_all_scales_n": int(exact.sum()),
                "exact_state_all_scales_pct": pct(exact.sum(), len(support)),
                "direct_all_scales_n": int(direct_all.sum()),
                "direct_all_scales_pct": pct(direct_all.sum(), len(support)),
                "direct_some_scales_n": int(direct_some.sum()),
                "direct_some_scales_pct": pct(direct_some.sum(), len(support)),
                "direct_no_scale_n": int(direct_none.sum()),
                "direct_no_scale_pct": pct(direct_none.sum(), len(support)),
                "monotonic_relation_asserted": False,
                "final_scale_selected": False,
                "method_version": METHOD,
            }
        )
        for scale_a, scale_b in combinations(SCALES, 2):
            cross_pair_rows.append(
                {
                    "question_code": question,
                    "scale_a_km2": scale_a,
                    "scale_b_km2": scale_b,
                    **concordance(states[(scale_a, "O00", question)], states[(scale_b, "O00", question)]),
                    "method_version": METHOD,
                }
            )
        for scale in SCALES:
            origin_matrix = np.column_stack([states[(scale, origin, question)] for origin, _, _ in ORIGINS])
            origin_exact = np.all(origin_matrix == origin_matrix[:, [0]], axis=1)
            origin_direct = origin_matrix == 2
            origin_all = origin_direct.all(axis=1)
            origin_any = origin_direct.any(axis=1)
            origin_some = origin_any & ~origin_all
            origin_none = ~origin_any
            origin_support_flags[(scale, question)] = pd.DataFrame(
                {
                    "origin_exact": origin_exact,
                    "origin_direct_all": origin_all,
                    "origin_direct_some": origin_some,
                    "origin_direct_none": origin_none,
                }
            )
            origin_summary_rows.append(
                {
                    "scale_km2": scale,
                    "question_code": question,
                    "support_points_n": len(support),
                    "origins_n": len(ORIGINS),
                    "exact_state_all_origins_n": int(origin_exact.sum()),
                    "exact_state_all_origins_pct": pct(origin_exact.sum(), len(support)),
                    "direct_all_origins_n": int(origin_all.sum()),
                    "direct_all_origins_pct": pct(origin_all.sum(), len(support)),
                    "direct_some_origins_n": int(origin_some.sum()),
                    "direct_some_origins_pct": pct(origin_some.sum(), len(support)),
                    "direct_no_origin_n": int(origin_none.sum()),
                    "direct_no_origin_pct": pct(origin_none.sum(), len(support)),
                    "final_origin_selected": False,
                    "method_version": METHOD,
                }
            )
            for origin_a, origin_b in combinations([item[0] for item in ORIGINS], 2):
                origin_pair_rows.append(
                    {
                        "scale_km2": scale,
                        "question_code": question,
                        "origin_a": origin_a,
                        "origin_b": origin_b,
                        **concordance(states[(scale, origin_a, question)], states[(scale, origin_b, question)]),
                        "method_version": METHOD,
                    }
                )

    support_question = pd.concat(support_question_frames, ignore_index=True)
    cross_summary = pd.DataFrame(cross_summary_rows)
    cross_pair = pd.DataFrame(cross_pair_rows)
    origin_counts = pd.DataFrame(origin_count_rows)
    origin_summary = pd.DataFrame(origin_summary_rows)
    origin_pair = pd.DataFrame(origin_pair_rows)

    requirement_registry = pd.read_csv(OUT.parent / "question_sufficiency/question_requirement_matrix.csv")
    well_requirement = pd.read_csv(OUT.parent / "question_sufficiency/well_requirement_status_long.csv", low_memory=False)
    req_codes = requirement_registry.requirement_code.tolist()
    req_meta = requirement_registry.set_index("requirement_code")
    req_pos = {value: index for index, value in enumerate(req_codes)}
    demonstrated = np.zeros((len(wells), len(req_codes)), dtype=bool)
    for row in well_requirement.itertuples(index=False):
        demonstrated[well_index[str(row.well_id)], req_pos[row.requirement_code]] = bool(row.demonstrated)
    blocked = ~demonstrated
    observable_scales = np.zeros((len(support), len(req_codes)), dtype=np.int8)
    any_blocked_scales = np.zeros_like(observable_scales)
    fully_blocked_scales = np.zeros_like(observable_scales)
    blocked_pct_sum = np.zeros((len(support), len(req_codes)), dtype=float)
    support_scale_instances = np.zeros(len(req_codes), dtype=np.int64)
    any_blocked_instances = np.zeros(len(req_codes), dtype=np.int64)
    fully_blocked_instances = np.zeros(len(req_codes), dtype=np.int64)

    for scale in SCALES:
        wi = well_cells[(scale, "O00")]
        si = support_cells[(scale, "O00")]
        n_cells = len(primary_grids[scale])
        n_wells = cell_well_counts[(scale, "O00")]
        blocked_by_cell = np.zeros((n_cells, len(req_codes)), dtype=np.int32)
        for req_index in range(len(req_codes)):
            blocked_by_cell[:, req_index] = np.bincount(
                wi,
                weights=blocked[:, req_index].astype(np.int8),
                minlength=n_cells,
            ).astype(np.int32)
        support_n = n_wells[si]
        support_blocked = blocked_by_cell[si, :]
        observable = support_n > 0
        observable_matrix = observable[:, None]
        any_b = support_blocked > 0
        full_b = observable_matrix & (support_blocked == support_n[:, None])
        observable_scales += observable_matrix.astype(np.int8)
        any_blocked_scales += any_b.astype(np.int8)
        fully_blocked_scales += full_b.astype(np.int8)
        blocked_pct_sum += np.where(observable_matrix, support_blocked / np.maximum(support_n[:, None], 1) * 100.0, 0.0)
        support_scale_instances += int(observable.sum())
        any_blocked_instances += any_b.sum(axis=0)
        fully_blocked_instances += full_b.sum(axis=0)

    repeated_support = np.repeat(np.arange(len(support)), len(req_codes))
    tiled_req = np.tile(np.arange(len(req_codes)), len(support))
    obs_flat = observable_scales.ravel()
    persistence = pd.DataFrame(
        {
            "support_id": support.support_id.to_numpy()[repeated_support],
            "x_5880": support.x_5880.to_numpy()[repeated_support],
            "y_5880": support.y_5880.to_numpy()[repeated_support],
            "hydro_surface_unit": support.unit.to_numpy()[repeated_support],
            "hydro_surface_domain": support.domain.to_numpy()[repeated_support],
            "question_code": [str(req_codes[index]).split("_")[0] for index in tiled_req],
            "requirement_code": np.array(req_codes, dtype=object)[tiled_req],
            "requirement_name": req_meta.loc[req_codes, "requirement_name"].to_numpy()[tiled_req],
            "dimension": req_meta.loc[req_codes, "dimension"].to_numpy()[tiled_req],
            "observable_scales_n": obs_flat,
            "any_blocked_scales_n": any_blocked_scales.ravel(),
            "fully_blocked_scales_n": fully_blocked_scales.ravel(),
            "mean_blocked_wells_pct_observable_scales": np.where(
                obs_flat > 0,
                blocked_pct_sum.ravel() / np.maximum(obs_flat, 1),
                np.nan,
            ),
            "any_blocker_persistence_pct": np.where(
                obs_flat > 0,
                any_blocked_scales.ravel() / np.maximum(obs_flat, 1) * 100.0,
                np.nan,
            ),
            "full_blocker_persistence_pct": np.where(
                obs_flat > 0,
                fully_blocked_scales.ravel() / np.maximum(obs_flat, 1) * 100.0,
                np.nan,
            ),
            "fully_blocked_all_observable_scales": (obs_flat > 0) & (fully_blocked_scales.ravel() == obs_flat),
            "persistence_state": np.where(
                obs_flat == 0,
                "UNKNOWN_SEM_ESCALA_OBSERVAVEL",
                np.where(
                    fully_blocked_scales.ravel() == obs_flat,
                    "BLOQUEIO_COMPLETO_EM_TODAS_AS_ESCALAS_OBSERVAVEIS",
                    np.where(any_blocked_scales.ravel() > 0, "BLOQUEIO_PRESENTE_EM_PARTE_DO_SUPORTE", "SEM_BLOQUEIO_NAS_ESCALAS_OBSERVAVEIS"),
                ),
            ),
            "unknown_is_zero": False,
            "method_version": METHOD,
        }
    )
    blocker_rows: list[dict[str, object]] = []
    for req_index, req_code in enumerate(req_codes):
        obs_support = observable_scales[:, req_index] > 0
        all_obs_full = obs_support & (fully_blocked_scales[:, req_index] == observable_scales[:, req_index])
        blocked_wells_n = int(blocked[:, req_index].sum())
        blocker_rows.append(
            {
                "question_code": req_code.split("_")[0],
                "requirement_code": req_code,
                "requirement_name": req_meta.loc[req_code, "requirement_name"],
                "dimension": req_meta.loc[req_code, "dimension"],
                "wells_n": len(wells),
                "blocked_wells_n": blocked_wells_n,
                "blocked_wells_pct": pct(blocked_wells_n, len(wells)),
                "fully_blocked_all_wells": blocked_wells_n == len(wells),
                "observable_support_scale_instances_n": int(support_scale_instances[req_index]),
                "any_blocked_support_scale_instances_n": int(any_blocked_instances[req_index]),
                "any_blocked_support_scale_instances_pct": pct(any_blocked_instances[req_index], support_scale_instances[req_index]),
                "fully_blocked_support_scale_instances_n": int(fully_blocked_instances[req_index]),
                "fully_blocked_support_scale_instances_pct": pct(fully_blocked_instances[req_index], support_scale_instances[req_index]),
                "observable_support_points_n": int(obs_support.sum()),
                "fully_blocked_all_observable_support_points_n": int(all_obs_full.sum()),
                "fully_blocked_all_observable_support_points_pct": pct(all_obs_full.sum(), obs_support.sum()),
                "fully_blocked_all_observable_support": bool(obs_support.any() and all_obs_full[obs_support].all()),
                "physical_absence_inferred": False,
                "method_version": METHOD,
            }
        )
    blocker_summary = pd.DataFrame(blocker_rows)

    hydro_rows: list[dict[str, object]] = []
    hydro_by_scale: dict[int, pd.DataFrame] = {}
    for scale in SCALES:
        grid = primary_grids[scale]
        si = support_cells[(scale, "O00")]
        support_cells_frame = support[["support_id", "unit", "unit_assignment_status", "domain", "domain_assignment_status"]].copy()
        support_cells_frame["cell_id"] = grid.cell_id.to_numpy()[si]
        cell_rows: list[dict[str, object]] = []
        for cell_id, group in support_cells_frame.groupby("cell_id", sort=False):
            valid_units = group.loc[group.unit_assignment_status.eq("OK"), "unit"].dropna().astype(str)
            valid_domains = group.loc[group.domain_assignment_status.eq("OK"), "domain"].dropna().astype(str)
            units_n = int(valid_units.nunique())
            domains_n = int(valid_domains.nunique())
            state = "MULTIPLAS_UNIDADES_SUPERFICIAIS" if units_n > 1 else "UMA_UNIDADE_SUPERFICIAL" if units_n == 1 else "UNKNOWN_SEM_CONTEXTO_CLASSIFICADO"
            cell_rows.append(
                {
                    "cell_id": cell_id,
                    "support_points_n": len(group),
                    "hydro_surface_classified_support_n": int(len(valid_units)),
                    "hydro_surface_units_n": units_n,
                    "hydro_surface_domains_n": domains_n,
                    "hydro_context_state": state,
                    "hydro_dominant_unit": mode_text(valid_units),
                    "hydro_dominant_domain": mode_text(valid_domains),
                }
            )
        hydro_cell = pd.DataFrame(cell_rows)
        missing = grid.loc[~grid.cell_id.isin(hydro_cell.cell_id), "cell_id"]
        if len(missing):
            hydro_cell = pd.concat(
                [
                    hydro_cell,
                    pd.DataFrame(
                        {
                            "cell_id": missing,
                            "support_points_n": 0,
                            "hydro_surface_classified_support_n": 0,
                            "hydro_surface_units_n": 0,
                            "hydro_surface_domains_n": 0,
                            "hydro_context_state": "UNKNOWN_SEM_CONTEXTO_CLASSIFICADO",
                            "hydro_dominant_unit": "",
                            "hydro_dominant_domain": "",
                        }
                    ),
                ],
                ignore_index=True,
            )
        hydro_by_scale[scale] = hydro_cell
        counts = hydro_cell.hydro_context_state.value_counts()
        hydro_rows.append(
            {
                "scale_km2": scale,
                "cells_n": len(grid),
                "cells_multiple_surface_units_n": int(counts.get("MULTIPLAS_UNIDADES_SUPERFICIAIS", 0)),
                "cells_one_surface_unit_n": int(counts.get("UMA_UNIDADE_SUPERFICIAL", 0)),
                "cells_unknown_surface_context_n": int(counts.get("UNKNOWN_SEM_CONTEXTO_CLASSIFICADO", 0)),
                "surface_point_proxy_used": True,
                "area_fraction_calculated": False,
                "vertical_structure_inferred": False,
                "method_version": METHOD,
            }
        )
    hydro_summary = pd.DataFrame(hydro_rows)

    cell_frames: list[pd.DataFrame] = []
    wide_by_scale: dict[int, pd.DataFrame] = {}
    question_names = well_questions.groupby("question_code").question_name.first().to_dict()
    v24_cell = pd.read_csv(OUT.parent / "question_sufficiency/cell_question_sufficiency_long.csv", low_memory=False)
    for scale in SCALES:
        grid = primary_grids[scale]
        si = support_cells[(scale, "O00")]
        hydro_cell = hydro_by_scale[scale].set_index("cell_id")
        wide = pd.DataFrame(
            {
                "cell_id": grid.cell_id,
                "scale_km2": scale,
                "variant": "O00",
                "area_effective_km2": grid.area_effective_km2,
                "n_wells": cell_well_counts[(scale, "O00")],
                "support_points_n": grid.cell_id.map(hydro_cell.support_points_n).fillna(0).astype(int),
                "hydro_surface_units_n": grid.cell_id.map(hydro_cell.hydro_surface_units_n).fillna(0).astype(int),
                "hydro_surface_domains_n": grid.cell_id.map(hydro_cell.hydro_surface_domains_n).fillna(0).astype(int),
                "hydro_context_state": grid.cell_id.map(hydro_cell.hydro_context_state).fillna("UNKNOWN_SEM_CONTEXTO_CLASSIFICADO"),
                "hydro_dominant_unit": grid.cell_id.map(hydro_cell.hydro_dominant_unit).fillna(""),
                "hydro_dominant_domain": grid.cell_id.map(hydro_cell.hydro_dominant_domain).fillna(""),
            }
        )
        for question in QUESTIONS:
            n_wells = cell_well_counts[(scale, "O00")]
            n_direct = cell_direct_counts[(scale, "O00", question)]
            cell_state = state_from_counts(n_wells, n_direct)
            cross = support_question_lookup[question]
            origin_flags = origin_support_flags[(scale, question)]
            support_flags = pd.DataFrame(
                {
                    "cell_id": grid.cell_id.to_numpy()[si],
                    "cross_exact": cross.exact_state_all_scales.to_numpy(),
                    "cross_all": cross.direct_all_scales.to_numpy(),
                    "cross_some": cross.direct_some_scales.to_numpy(),
                    "cross_none": cross.direct_no_scale.to_numpy(),
                    "origin_exact": origin_flags.origin_exact.to_numpy(),
                    "origin_all": origin_flags.origin_direct_all.to_numpy(),
                    "origin_some": origin_flags.origin_direct_some.to_numpy(),
                    "origin_none": origin_flags.origin_direct_none.to_numpy(),
                }
            )
            aggregated = support_flags.groupby("cell_id").agg(
                support_points_n=("cell_id", "size"),
                cross_scale_exact_state_support_n=("cross_exact", "sum"),
                cross_scale_direct_all_support_n=("cross_all", "sum"),
                cross_scale_direct_some_support_n=("cross_some", "sum"),
                cross_scale_direct_none_support_n=("cross_none", "sum"),
                origin_exact_state_support_n=("origin_exact", "sum"),
                origin_direct_all_support_n=("origin_all", "sum"),
                origin_direct_some_support_n=("origin_some", "sum"),
                origin_direct_none_support_n=("origin_none", "sum"),
            )
            v24 = v24_cell[(v24_cell.scale_km2 == scale) & (v24_cell.question_code == question)].set_index("cell_id")
            rows = pd.DataFrame(
                {
                    "cell_id": grid.cell_id,
                    "scale_km2": scale,
                    "grid_family": GRID_FAMILY,
                    "area_effective_km2": grid.area_effective_km2,
                    "question_code": question,
                    "question_name": question_names[question],
                    "n_wells": n_wells,
                    "direct_evidence_n": n_direct,
                    "direct_evidence_pct_of_wells": [pct(value, total) for value, total in zip(n_direct, n_wells)],
                    "cell_state_code": cell_state,
                    "cell_state_label": [STATE_LABELS[int(value)] for value in cell_state],
                    "support_points_n": grid.cell_id.map(aggregated.support_points_n).fillna(0).astype(int),
                    "cross_scale_exact_state_support_n": grid.cell_id.map(aggregated.cross_scale_exact_state_support_n).fillna(0).astype(int),
                    "cross_scale_exact_state_support_pct": [pct(value, total) for value, total in zip(grid.cell_id.map(aggregated.cross_scale_exact_state_support_n).fillna(0), grid.cell_id.map(aggregated.support_points_n).fillna(0))],
                    "cross_scale_direct_all_support_n": grid.cell_id.map(aggregated.cross_scale_direct_all_support_n).fillna(0).astype(int),
                    "cross_scale_direct_some_support_n": grid.cell_id.map(aggregated.cross_scale_direct_some_support_n).fillna(0).astype(int),
                    "cross_scale_direct_none_support_n": grid.cell_id.map(aggregated.cross_scale_direct_none_support_n).fillna(0).astype(int),
                    "origin_exact_state_support_n": grid.cell_id.map(aggregated.origin_exact_state_support_n).fillna(0).astype(int),
                    "origin_exact_state_support_pct": [pct(value, total) for value, total in zip(grid.cell_id.map(aggregated.origin_exact_state_support_n).fillna(0), grid.cell_id.map(aggregated.support_points_n).fillna(0))],
                    "origin_direct_all_support_n": grid.cell_id.map(aggregated.origin_direct_all_support_n).fillna(0).astype(int),
                    "origin_direct_some_support_n": grid.cell_id.map(aggregated.origin_direct_some_support_n).fillna(0).astype(int),
                    "origin_direct_none_support_n": grid.cell_id.map(aggregated.origin_direct_none_support_n).fillna(0).astype(int),
                    "hydro_surface_units_n": grid.cell_id.map(hydro_cell.hydro_surface_units_n).fillna(0).astype(int),
                    "hydro_surface_domains_n": grid.cell_id.map(hydro_cell.hydro_surface_domains_n).fillna(0).astype(int),
                    "hydro_context_state": grid.cell_id.map(hydro_cell.hydro_context_state).fillna("UNKNOWN_SEM_CONTEXTO_CLASSIFICADO"),
                    "hydro_dominant_unit": grid.cell_id.map(hydro_cell.hydro_dominant_unit).fillna(""),
                    "hydro_dominant_domain": grid.cell_id.map(hydro_cell.hydro_dominant_domain).fillna(""),
                    "top_blocking_requirements": grid.cell_id.map(v24.top_blocking_requirements).fillna(""),
                    "method_version": METHOD,
                }
            )
            if len(rows.columns) != 29:
                raise RuntimeError("A tabela por célula deve conservar 29 campos auditáveis")
            cell_frames.append(rows)
            prefix = question.lower()
            wide[f"{prefix}_cell_state_code"] = cell_state
            wide[f"{prefix}_cell_state_label"] = [STATE_LABELS[int(value)] for value in cell_state]
            wide[f"{prefix}_direct_evidence_n"] = n_direct
            wide[f"{prefix}_cross_scale_exact_pct"] = rows.cross_scale_exact_state_support_pct
            wide[f"{prefix}_origin_exact_pct"] = rows.origin_exact_state_support_pct
            wide[f"{prefix}_top_blocking_requirements"] = rows.top_blocking_requirements
        wide["grid_family"] = GRID_FAMILY
        wide["cutoff_date"] = CUTOFF
        wide["method_version"] = METHOD
        wide["weight_used"] = False
        wide["score_used"] = False
        wide_by_scale[scale] = wide
    cell_long = pd.concat(cell_frames, ignore_index=True)

    outputs = {
        "support_scale_question_long.csv": support_scale,
        "support_question_cross_scale.csv": support_question,
        "cross_scale_question_summary.csv": cross_summary,
        "cross_scale_pairwise.csv": cross_pair,
        "origin_scale_question_counts.csv": origin_counts,
        "origin_scale_question_summary.csv": origin_summary,
        "origin_pairwise.csv": origin_pair,
        "support_requirement_persistence.csv": persistence,
        "blocker_requirement_summary.csv": blocker_summary,
        "hydro_context_scale_summary.csv": hydro_summary,
        "cell_stability_sensitivity_long.csv": cell_long,
    }
    for name, frame in outputs.items():
        write_csv(frame, name)
    for scale, wide in wide_by_scale.items():
        write_csv(wide, f"stability_sensitivity_{scale}km2.csv")
        payload = primary_grids[scale].to_crs(4326)[["cell_id", "geometry"]].copy()
        payload = payload.merge(wide, on="cell_id", how="left", validate="one_to_one")
        geo_path = OUT / f"stability_sensitivity_{scale}km2.geojson"
        geo_path.unlink(missing_ok=True)
        payload.to_file(geo_path, driver="GeoJSON", index=False)

    registry = {
        "version": "2.5",
        "method_version": METHOD,
        "support_points_n": len(support),
        "wells_n": len(wells),
        "questions": list(QUESTIONS),
        "scales_km2": list(SCALES),
        "origins": [item[0] for item in ORIGINS],
        "state_codes": {str(key): value for key, value in STATE_LABELS.items()},
        "rules": {
            "unknown_is_zero": False,
            "weight_used": False,
            "score_used": False,
            "priority_calculated": False,
            "potential_calculated": False,
            "interpolation_used": False,
            "prediction_used": False,
            "final_scale_selected": False,
            "final_origin_selected": False,
            "surface_hydro_context_is_point_proxy": True,
        },
    }
    (OUT / "stability_sensitivity_registry.json").write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    style = {
        "version": "2.5",
        "state_palette": {"0": "#cbd5df", "1": "#7b61a8", "2": "#27856b"},
        "percent_palette": ["#f1f5f9", "#d7e7ec", "#a8d5d0", "#65b7a8", "#197665"],
        "hydro_palette": ["#edf3f8", "#9ecae1", "#4d7ea8", "#684a8a"],
        "metrics": {
            "cell_state_code": "Estado documental local",
            "direct_evidence_n": "Registros com evidência direta",
            "cross_scale_exact_pct": "Concordância exata entre escalas no suporte",
            "origin_exact_pct": "Concordância exata entre origens no suporte",
            "n_wells": "Poços do conjunto auditado",
            "hydro_surface_units_n": "Unidades hidrogeológicas superficiais no suporte",
        },
    }
    (OUT / "stability_sensitivity_style_metadata.json").write_text(json.dumps(style, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return outputs | {f"stability_sensitivity_{scale}km2.csv": frame for scale, frame in wide_by_scale.items()}


def field_definition(field: str, sources: str) -> dict[str, str]:
    unit = "texto"
    if field.endswith("_n") or field in {"scale_km2", "state_code"}:
        unit = "n"
    if field.endswith("_pct") or "pct_" in field:
        unit = "%"
    if field.endswith("_used") or field.endswith("_selected") or field.startswith("fully_blocked_all") or field.startswith("exact_state_all") or field.startswith("direct_") and field.endswith("scales"):
        unit = "booleano"
    readable = field.replace("_", " ")
    if field.endswith("_pct") or "pct_" in field:
        definition = f"Percentual associado a {readable}, com denominador explícito no produto V2.5."
    elif field.endswith("_n") or field.endswith("_count"):
        definition = f"Contagem associada a {readable} no universo explicitado pelo produto V2.5."
    elif unit == "booleano":
        definition = f"Indicador lógico associado a {readable} nas regras da V2.5."
    elif "state" in field:
        definition = f"Estado categórico de {readable} nas regras documentais da V2.5."
    elif field.endswith("_code"):
        definition = f"Código controlado de {readable} usado para rastrear a regra V2.5."
    else:
        definition = f"Valor auditável de {readable} no módulo V2.5."
    rule = "Calculado diretamente no universo e denominador declarados no arquivo de origem."
    how = "Ler com a pergunta, a escala, a origem, o suporte e o denominador explícitos."
    if "exact" in field:
        rule = "Concordância exata entre estados documentais no suporte fixo de 5 km."
    elif "jaccard" in field:
        rule = "Interseção dividida pela união da presença de evidência direta."
    elif "mismatch" in field:
        rule = "Fração do suporte fixo com presença direta diferente entre os dois cenários."
    elif "spearman" in field:
        rule = "Correlação ordinal de Spearman entre códigos de estado no mesmo suporte fixo."
    elif "persistence" in field:
        rule = "Persistência calculada somente nas escalas em que a célula do suporte contém ao menos um poço."
    elif "hydro_" in field:
        rule = "Contexto superficial SGB 2024 observado nos pontos fixos de 5 km."
    elif field in {"weight_used", "score_used"}:
        rule = "FALSE em toda a V2.5."
    return {
        "field": field,
        "modules": "Estabilidade e sensibilidade",
        "source_files": sources,
        "definition": definition,
        "formula_or_rule": rule,
        "unit": unit,
        "how_to_read": how,
        "does_not_mean": "Não é potencial, prioridade, representatividade territorial, peso ou score.",
        "unknown_rule": "Sem escala observável ou suporte classificado, permanece UNKNOWN e não é convertido em zero.",
    }


def update_dictionary(outputs: dict[str, pd.DataFrame]) -> None:
    master_path = ROOT / "methodology/DICIONARIO_METRICAS_RESULTADOS_V1.csv"
    master = pd.read_csv(master_path)
    sources_by_field: dict[str, set[str]] = {}
    for filename, frame in outputs.items():
        for field in frame.columns:
            sources_by_field.setdefault(field, set()).add(filename)
    existing = set(master.field)
    additions = [
        field_definition(field, " | ".join(sorted(sources)))
        for field, sources in sorted(sources_by_field.items())
        if field not in existing
    ]
    annex = pd.DataFrame([field_definition(field, " | ".join(sorted(sources))) for field, sources in sorted(sources_by_field.items())])
    annex.to_csv(ROOT / "methodology/ESTABILIDADE_SENSIBILIDADE_CAMPOS_V1.csv", index=False, encoding="utf-8-sig")
    if additions:
        master = pd.concat([master, pd.DataFrame(additions)], ignore_index=True).sort_values("field", kind="stable")
    definitions = {row["field"]: row for row in additions}
    for field, sources in sources_by_field.items():
        if field in set(master.loc[master.modules.eq("Estabilidade e sensibilidade"), "field"]):
            definitions[field] = field_definition(field, " | ".join(sorted(sources)))
    for field, definition in definitions.items():
        mask = master.field.eq(field) & master.modules.eq("Estabilidade e sensibilidade")
        for column in master.columns:
            if column != "field" and column in definition:
                master.loc[mask, column] = definition[column]
    master.to_csv(master_path, index=False, encoding="utf-8-sig")
    shutil.copy2(master_path, ROOT / "docs/data/dicionario_metricas_resultados_v1.csv")
    shutil.copy2(ROOT / "methodology/ESTABILIDADE_SENSIBILIDADE_CAMPOS_V1.csv", OUT / "stability_sensitivity_field_dictionary.csv")


def publish() -> None:
    for source in OUT.iterdir():
        if source.is_file():
            shutil.copy2(source, WEB / source.name)


def main() -> None:
    outputs = build()
    update_dictionary(outputs)
    publish()
    print("OK V2.5")
    print("14284 pontos, 71420 pares suporte-pergunta, 357100 pares suporte-escala-pergunta, 557076 pares suporte-requisito")
    print(f"45145 pares célula-pergunta e {len(pd.read_csv(ROOT / 'methodology/DICIONARIO_METRICAS_RESULTADOS_V1.csv'))} campos documentados")


if __name__ == "__main__":
    main()
