#!/usr/bin/env python3
"""Constrói a PIH MS V2.6 experimental por pergunta.

A prioridade descreve a necessidade de investigação que decorre do déficit
documental demonstrado no conjunto PIH MS V2.5. A classificação é categórica,
não compensatória e mantida separada da confiança. Não há pesos, score,
interpolação, prioridade integrada ou inferência de potencial aquífero.
"""
from __future__ import annotations

from pathlib import Path
import json
import shutil

import geopandas as gpd
import numpy as np
import pandas as pd

from build_stability_sensitivity_v25 import build_shifted_grid, assign_idx


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/derived/research_priority"
WEB = ROOT / "docs/data/research_priority"
SCALES = (100, 150, 250, 500, 1000)
ORIGINS = (("O00", 0.0, 0.0), ("OX25", 0.25, 0.0), ("OY25", 0.0, 0.25), ("OXY25", 0.25, 0.25))
QUESTIONS = ("Q01", "Q02", "Q03", "Q04", "Q05")
EXPECTED_CELLS = {100: 3763, 150: 2525, 250: 1537, 500: 791, 1000: 413}
METHOD = "PIH_MS_V2.6_PRIORIDADE_POR_PERGUNTA_V1"
GRID_FAMILY = "SCALE_PRIMARY_O00_V1"
CUTOFF = "2026-08-29"
CRS = "EPSG:5880"

PALETTE = {
    "0": "#7C8793",
    "1": "#B2182B",
    "2": "#F28E2B",
    "3": "#7B4AB4",
    "4": "#1B9E9A",
    "5": "#2E8B57",
}

PRIORITY = {
    0: ("UNKNOWN", "Não classificável"),
    1: ("P1", "Crítica"),
    2: ("P2", "Alta"),
    3: ("P3", "Moderada"),
    4: ("P4", "Baixa"),
    5: ("P5", "Suficiência documental"),
}

CONFIDENCE = {
    0: ("UNKNOWN", "Não classificável"),
    1: ("C1", "Muito baixa"),
    2: ("C2", "Baixa"),
    3: ("C3", "Moderada"),
    4: ("C4", "Alta"),
    5: ("C5", "Muito alta"),
}

CONTEXT_REQUIREMENTS = {
    "Q01": ("Q01_R01", "Q01_R02", "Q01_R04", "Q01_R06", "Q01_R07"),
    "Q02": ("Q02_R01", "Q02_R03", "Q02_R04", "Q02_R09"),
    "Q03": ("Q03_R01", "Q03_R03", "Q03_R04", "Q03_R05", "Q03_R06", "Q03_R09"),
    "Q04": ("Q04_R01", "Q04_R02", "Q04_R05", "Q04_R06"),
    "Q05": ("Q05_R01", "Q05_R03", "Q05_R05", "Q05_R08"),
}

QUESTION_ACTIONS = {
    "Q01": "Medir nível de água com data explícita e validar o contexto construtivo e hidroestratigráfico do poço.",
    "Q02": "Executar ou documentar ensaio hidráulico com metadados mínimos e validar o aquífero captado.",
    "Q03": "Realizar amostragem hidroquímica documentada e validar parâmetro, unidade, data e aquífero captado.",
    "Q04": "Documentar perfil vertical, profundidade, intervalo captado e atribuição hidroestratigráfica.",
    "Q05": "Estabelecer série da mesma variável com datas, contexto do poço e controle de independência.",
}


def pct(num: int | float, den: int | float) -> float | None:
    return round(100.0 * float(num) / float(den), 6) if den else None


def write_csv(frame: pd.DataFrame, name: str) -> None:
    frame.to_csv(OUT / name, index=False, encoding="utf-8-sig")


def requirement_action(row: pd.Series) -> str:
    field = str(row.source_field)
    actions = {
        "spatial_coordinate_valid": "Revisar coordenadas, município espacial e referência geodésica.",
        "hydraulic_static_level_available": "Medir e registrar o nível estático.",
        "level_measurement_dated": "Associar data explícita à medição de nível.",
        "vertical_depth_positive": "Confirmar e documentar profundidade total positiva.",
        "capture_interval_demonstrated": "Documentar topo e base do intervalo efetivamente captado.",
        "hydrostrat_consistent": "Revisar e validar a unidade hidroestratigráfica captada.",
        "no_objective_invalid": "Revisar o valor inválido preservando o registro original e a correção rastreável.",
        "hydraulic_test_minimum_metadata": "Documentar tipo de ensaio, duração, vazão e observações mínimas.",
        "test_dated": "Registrar a data explícita do ensaio hidráulico.",
        "interpretation_method_documented": "Documentar o método de interpretação do ensaio.",
        "hydraulic_parameter_reported": "Informar o parâmetro hidráulico derivado e sua procedência.",
        "hydraulic_unit_verified": "Verificar documentalmente a unidade do parâmetro hidráulico.",
        "hydrochemical_partial_evidence": "Adquirir amostra ou resultado hidroquímico identificável.",
        "chemistry_dated": "Registrar a data de coleta ou análise hidroquímica.",
        "chem_parameter_identified": "Identificar o parâmetro químico analisado.",
        "chem_unit_verified": "Verificar a unidade do resultado hidroquímico.",
        "chem_qa_complete": "Documentar amostragem, método analítico e controle de qualidade.",
        "explicit_profile_documented": "Adquirir ou digitalizar o perfil litológico explícito.",
        "time_series_demonstrated": "Adquirir observações repetidas da mesma variável no mesmo poço.",
        "temporal_any_dated": "Registrar ao menos um evento hidrogeológico com data explícita.",
        "temporal_variable_identified": "Identificar a variável temporal e manter sua definição entre observações.",
        "independence_demonstrated": "Verificar a independência hidrogeológica necessária à interpretação da rede.",
    }
    return actions.get(field, f"Adquirir ou revisar o requisito {row.requirement_name} com procedência explícita.")


def priority_codes(n_wells: np.ndarray, n_direct: np.ndarray, n_context: np.ndarray, n_minimum: np.ndarray) -> np.ndarray:
    return np.where(
        n_wells == 0,
        0,
        np.where(n_direct == 0, 1, np.where(n_context == 0, 2, np.where(n_minimum == 0, 3, 4))),
    ).astype(np.int8)


def confidence_codes(priority: np.ndarray, support_n: np.ndarray, cross_pct: np.ndarray, origin_pct: np.ndarray) -> np.ndarray:
    result = np.zeros(len(priority), dtype=np.int8)
    valid = (priority > 0) & (support_n > 0) & np.isfinite(cross_pct) & np.isfinite(origin_pct)
    cross_zero = cross_pct == 0
    origin_zero = origin_pct == 0
    cross_some = cross_pct > 0
    origin_some = origin_pct > 0
    cross_full = cross_pct == 100
    origin_full = origin_pct == 100
    result[valid & cross_zero & origin_zero] = 1
    result[valid & ((cross_some & origin_zero) | (cross_zero & origin_some))] = 2
    result[valid & cross_some & origin_some & ~cross_full & ~origin_full] = 3
    result[valid & ((cross_full & origin_some & ~origin_full) | (origin_full & cross_some & ~cross_full))] = 4
    result[valid & cross_full & origin_full] = 5
    return result


def priority_explanation(code: int) -> str:
    return {
        0: "Não há poço do conjunto auditado na célula para classificar a prioridade.",
        1: "Há poço na célula, mas não existe evidência direta para a pergunta.",
        2: "Existe evidência direta, porém nenhum poço satisfaz o contexto mínimo de interpretação.",
        3: "Ao menos um poço satisfaz o contexto mínimo, mas nenhum satisfaz o mínimo documental completo.",
        4: "Existe mínimo documental completo local, mas a representatividade territorial não foi demonstrada.",
        5: "O mínimo documental e a representatividade territorial foram demonstrados para a pergunta.",
    }[int(code)]


def confidence_explanation(code: int) -> str:
    return {
        0: "A prioridade não é classificável ou a célula não possui ponto fixo de suporte.",
        1: "Não há concordância exata da prioridade entre escalas nem entre origens no suporte da célula.",
        2: "A prioridade apresenta concordância apenas em uma das duas verificações de estabilidade.",
        3: "Há concordância parcial entre escalas e entre origens, sem estabilidade completa.",
        4: "Uma verificação é completamente estável e a outra apresenta concordância parcial.",
        5: "A prioridade é completamente estável entre escalas e entre origens no suporte da célula.",
    }[int(code)]


def top_items(blocked_by_cell: np.ndarray, n_wells: np.ndarray, req_codes: list[str], action_lookup: dict[str, str]) -> tuple[list[str], list[str], np.ndarray]:
    blockers: list[str] = []
    actions: list[str] = []
    fully = np.zeros(len(n_wells), dtype=int)
    for cell_index in range(len(n_wells)):
        if n_wells[cell_index] == 0:
            blockers.append("")
            actions.append("")
            continue
        counts = blocked_by_cell[cell_index]
        fully[cell_index] = int(np.sum(counts == n_wells[cell_index]))
        order = sorted(range(len(req_codes)), key=lambda i: (-int(counts[i]), req_codes[i]))
        selected = [i for i in order if counts[i] > 0][:5]
        blockers.append("|".join(f"{req_codes[i]}={int(counts[i])}" for i in selected))
        actions.append("|".join(dict.fromkeys(action_lookup[req_codes[i]] for i in selected[:3])))
    return blockers, actions, fully


def build() -> dict[str, pd.DataFrame]:
    OUT.mkdir(parents=True, exist_ok=True)
    WEB.mkdir(parents=True, exist_ok=True)

    well_questions = pd.read_csv(ROOT / "data/derived/question_sufficiency/well_question_sufficiency_long.csv", low_memory=False)
    well_requirements = pd.read_csv(ROOT / "data/derived/question_sufficiency/well_requirement_status_long.csv", low_memory=False)
    requirement_registry = pd.read_csv(ROOT / "data/derived/question_sufficiency/question_requirement_matrix.csv")
    question_registry = pd.read_csv(ROOT / "data/derived/question_sufficiency/question_registry.csv")
    question_names = question_registry.set_index("question_code").question_name.to_dict()
    question_definitions = question_registry.set_index("question_code").to_dict("index")

    req_actions = requirement_registry.copy()
    req_actions["recommended_action"] = req_actions.apply(requirement_action, axis=1)
    req_actions["method_version"] = METHOD
    action_lookup = req_actions.set_index("requirement_code").recommended_action.to_dict()

    well_base = well_questions[well_questions.question_code == "Q01"][["well_id", "longitude", "latitude"]].copy()
    wells = gpd.GeoDataFrame(
        well_base,
        geometry=gpd.points_from_xy(well_base.longitude, well_base.latitude),
        crs="EPSG:4326",
    ).to_crs(CRS).reset_index(drop=True)
    if len(wells) != 3877:
        raise RuntimeError("O conjunto canônico deve conter 3.877 poços")
    well_index = {str(value): index for index, value in enumerate(wells.well_id)}

    requirement_pivot = well_requirements.pivot_table(
        index=["well_id", "question_code"],
        columns="requirement_code",
        values="demonstrated",
        aggfunc="first",
        fill_value=False,
    ).reset_index()
    well_questions = well_questions.merge(requirement_pivot, on=["well_id", "question_code"], how="left", validate="one_to_one")

    direct = np.zeros((len(wells), len(QUESTIONS)), dtype=bool)
    context = np.zeros_like(direct)
    minimum = np.zeros_like(direct)
    review = np.zeros_like(direct)
    unknown = np.zeros_like(direct)
    question_frames: dict[str, pd.DataFrame] = {}
    question_req_codes: dict[str, list[str]] = {}
    blocked_by_question: dict[str, np.ndarray] = {}
    for question_index, question in enumerate(QUESTIONS):
        subset = well_questions[well_questions.question_code == question].copy()
        subset["_well_position"] = subset.well_id.astype(str).map(well_index)
        subset = subset.sort_values("_well_position").reset_index(drop=True)
        question_frames[question] = subset
        direct[:, question_index] = subset.direct_evidence_present.astype(bool)
        gate = direct[:, question_index].copy()
        for code in CONTEXT_REQUIREMENTS[question]:
            gate &= subset[code].astype(bool).to_numpy()
        context[:, question_index] = gate
        minimum[:, question_index] = subset.minimum_documentary_met.astype(bool)
        review[:, question_index] = subset.critical_review_n.to_numpy() > 0
        unknown[:, question_index] = subset.critical_unknown_n.to_numpy() > 0
        req_codes = requirement_registry.loc[requirement_registry.question_code == question, "requirement_code"].tolist()
        question_req_codes[question] = req_codes
        demonstrated = subset[req_codes].astype(bool).to_numpy()
        blocked_by_question[question] = ~demonstrated

    support_base = pd.read_csv(ROOT / "data/derived/spatial_structure/support_points_5km.csv")
    support = gpd.GeoDataFrame(
        support_base,
        geometry=gpd.points_from_xy(support_base.x_5880, support_base.y_5880),
        crs=CRS,
    ).reset_index(drop=True)
    if len(support) != 14284:
        raise RuntimeError("O suporte fixo deve conter 14.284 pontos")
    support_strata = pd.read_csv(ROOT / "data/derived/stratified_scale/support_strata_assignment.csv")
    support = support.merge(
        support_strata[["support_id", "unit", "unit_assignment_status", "domain", "domain_assignment_status"]],
        on="support_id",
        how="left",
        validate="one_to_one",
    )

    state_boundary = gpd.read_file(ROOT / "docs/data/limite_ms_ibge_2025.geojson").to_crs(CRS)
    state_geom = state_boundary.geometry.union_all()
    grids: dict[int, gpd.GeoDataFrame] = {}
    well_cells: dict[tuple[int, str], np.ndarray] = {}
    support_cells: dict[tuple[int, str], np.ndarray] = {}
    priority_support: dict[tuple[int, str, str], np.ndarray] = {}
    cell_arrays: dict[tuple[int, str, str], dict[str, np.ndarray]] = {}

    for scale in SCALES:
        primary = gpd.read_file(ROOT / f"docs/data/scale_study/scale_primary_{scale}km2.geojson").to_crs(CRS)
        primary = primary.sort_values("cell_id").reset_index(drop=True)
        if len(primary) != EXPECTED_CELLS[scale]:
            raise RuntimeError(f"{scale} km² com cardinalidade inesperada")
        grids[scale] = primary
        for origin, fx, fy in ORIGINS:
            grid = primary if origin == "O00" else build_shifted_grid(scale, origin, fx, fy, state_geom)
            wi = assign_idx(wells, grid)
            si = assign_idx(support, grid)
            well_cells[(scale, origin)] = wi
            support_cells[(scale, origin)] = si
            n_wells = np.bincount(wi, minlength=len(grid)).astype(int)
            for question_index, question in enumerate(QUESTIONS):
                n_direct = np.bincount(wi, weights=direct[:, question_index], minlength=len(grid)).astype(int)
                n_context = np.bincount(wi, weights=context[:, question_index], minlength=len(grid)).astype(int)
                n_minimum = np.bincount(wi, weights=minimum[:, question_index], minlength=len(grid)).astype(int)
                codes = priority_codes(n_wells, n_direct, n_context, n_minimum)
                priority_support[(scale, origin, question)] = codes[si]
                cell_arrays[(scale, origin, question)] = {
                    "n_wells": n_wells,
                    "n_direct": n_direct,
                    "n_context": n_context,
                    "n_minimum": n_minimum,
                    "priority": codes,
                }

    support_cross_frames: list[pd.DataFrame] = []
    cross_exact_by_question: dict[str, np.ndarray] = {}
    for question in QUESTIONS:
        matrix = np.column_stack([priority_support[(scale, "O00", question)] for scale in SCALES])
        exact = np.all(matrix == matrix[:, [0]], axis=1)
        cross_exact_by_question[question] = exact
        support_cross_frames.append(
            pd.DataFrame(
                {
                    "support_id": support.support_id,
                    "x_5880": support.x_5880,
                    "y_5880": support.y_5880,
                    "hydro_surface_unit": support.unit,
                    "hydro_surface_domain": support.domain,
                    "question_code": question,
                    **{f"priority_code_{scale}km2": matrix[:, index] for index, scale in enumerate(SCALES)},
                    "priority_exact_all_scales": exact,
                    "priority_changes_across_scales_n": np.sum(matrix[:, 1:] != matrix[:, :-1], axis=1),
                    "priority_min_code_across_scales": matrix.min(axis=1),
                    "priority_max_code_across_scales": matrix.max(axis=1),
                    "integrated_priority_calculated": False,
                    "method_version": METHOD,
                }
            )
        )
    support_cross = pd.concat(support_cross_frames, ignore_index=True)

    support_origin_frames: list[pd.DataFrame] = []
    origin_exact_by_scale_question: dict[tuple[int, str], np.ndarray] = {}
    for scale in SCALES:
        for question in QUESTIONS:
            matrix = np.column_stack([priority_support[(scale, origin, question)] for origin, _, _ in ORIGINS])
            exact = np.all(matrix == matrix[:, [0]], axis=1)
            origin_exact_by_scale_question[(scale, question)] = exact
            support_origin_frames.append(
                pd.DataFrame(
                    {
                        "support_id": support.support_id,
                        "x_5880": support.x_5880,
                        "y_5880": support.y_5880,
                        "question_code": question,
                        "scale_km2": scale,
                        **{f"priority_code_{origin}": matrix[:, index] for index, (origin, _, _) in enumerate(ORIGINS)},
                        "priority_exact_all_origins": exact,
                        "priority_changes_across_origins_n": np.sum(matrix[:, 1:] != matrix[:, [0]], axis=1),
                        "priority_min_code_across_origins": matrix.min(axis=1),
                        "priority_max_code_across_origins": matrix.max(axis=1),
                        "origins_n": len(ORIGINS),
                        "integrated_priority_calculated": False,
                        "method_version": METHOD,
                    }
                )
            )
    support_origin = pd.concat(support_origin_frames, ignore_index=True)

    v24_cells = pd.read_csv(ROOT / "data/derived/question_sufficiency/cell_question_sufficiency_long.csv", low_memory=False)
    stability_cells = pd.read_csv(ROOT / "data/derived/stability_sensitivity/cell_stability_sensitivity_long.csv", low_memory=False)
    long_frames: list[pd.DataFrame] = []
    wide_by_scale: dict[int, pd.DataFrame] = {}
    summary_rows: list[dict[str, object]] = []

    for scale in SCALES:
        grid = grids[scale]
        si = support_cells[(scale, "O00")]
        support_n = np.bincount(si, minlength=len(grid)).astype(int)
        wide = pd.DataFrame(
            {
                "cell_id": grid.cell_id,
                "scale_km2": scale,
                "variant": "O00",
                "area_effective_km2": grid.area_effective_km2,
                "support_points_n": support_n,
                "n_wells": cell_arrays[(scale, "O00", "Q01")]["n_wells"],
                "grid_family": GRID_FAMILY,
                "cutoff_date": CUTOFF,
                "method_version": METHOD,
                "weight_used": False,
                "score_used": False,
                "integrated_priority_calculated": False,
            }
        )
        for question_index, question in enumerate(QUESTIONS):
            arrays = cell_arrays[(scale, "O00", question)]
            exact_cross = cross_exact_by_question[question]
            exact_origin = origin_exact_by_scale_question[(scale, question)]
            cross_n = np.bincount(si, weights=exact_cross, minlength=len(grid)).astype(int)
            origin_n = np.bincount(si, weights=exact_origin, minlength=len(grid)).astype(int)
            cross_pct = np.divide(cross_n * 100.0, support_n, out=np.full(len(grid), np.nan), where=support_n > 0)
            origin_pct = np.divide(origin_n * 100.0, support_n, out=np.full(len(grid), np.nan), where=support_n > 0)
            confidence = confidence_codes(arrays["priority"], support_n, cross_pct, origin_pct)
            wi = well_cells[(scale, "O00")]
            n_review = np.bincount(wi, weights=review[:, question_index], minlength=len(grid)).astype(int)
            n_unknown = np.bincount(wi, weights=unknown[:, question_index], minlength=len(grid)).astype(int)
            req_codes = question_req_codes[question]
            blocked = blocked_by_question[question]
            blocked_by_cell = np.zeros((len(grid), len(req_codes)), dtype=int)
            for req_index in range(len(req_codes)):
                blocked_by_cell[:, req_index] = np.bincount(
                    wi,
                    weights=blocked[:, req_index],
                    minlength=len(grid),
                ).astype(int)
            blockers, actions, fully_blocked = top_items(blocked_by_cell, arrays["n_wells"], req_codes, action_lookup)
            v24 = v24_cells[(v24_cells.scale_km2 == scale) & (v24_cells.question_code == question)].sort_values("cell_id")
            ss = stability_cells[(stability_cells.scale_km2 == scale) & (stability_cells.question_code == question)].sort_values("cell_id")
            if len(v24) != len(grid) or len(ss) != len(grid):
                raise RuntimeError("Produtos antecedentes com cardinalidade incompatível")
            priority_class = [PRIORITY[int(value)][0] for value in arrays["priority"]]
            priority_label = [PRIORITY[int(value)][1] for value in arrays["priority"]]
            confidence_class = [CONFIDENCE[int(value)][0] for value in confidence]
            confidence_label = [CONFIDENCE[int(value)][1] for value in confidence]
            recommendations = ["" if code == 0 else QUESTION_ACTIONS[question] for code in arrays["priority"]]
            rows = pd.DataFrame(
                {
                    "cell_id": grid.cell_id,
                    "scale_km2": scale,
                    "grid_family": GRID_FAMILY,
                    "area_effective_km2": grid.area_effective_km2,
                    "question_code": question,
                    "question_name": question_names[question],
                    "n_wells": arrays["n_wells"],
                    "direct_evidence_n": arrays["n_direct"],
                    "context_gate_n": arrays["n_context"],
                    "minimum_documentary_n": arrays["n_minimum"],
                    "review_evidence_n": n_review,
                    "unknown_evidence_n": n_unknown,
                    "fully_blocked_requirements_n": fully_blocked,
                    "top_blocking_requirements": blockers,
                    "recommended_actions": actions,
                    "priority_code": arrays["priority"],
                    "priority_class": priority_class,
                    "priority_label": priority_label,
                    "priority_explanation": [priority_explanation(value) for value in arrays["priority"]],
                    "confidence_code": confidence,
                    "confidence_class": confidence_class,
                    "confidence_label": confidence_label,
                    "confidence_explanation": [confidence_explanation(value) for value in confidence],
                    "support_points_n": support_n,
                    "cross_scale_priority_exact_support_n": cross_n,
                    "cross_scale_priority_exact_pct": cross_pct,
                    "origin_priority_exact_support_n": origin_n,
                    "origin_priority_exact_pct": origin_pct,
                    "hydro_surface_units_n": ss.hydro_surface_units_n.to_numpy(),
                    "hydro_surface_domains_n": ss.hydro_surface_domains_n.to_numpy(),
                    "hydro_context_state": ss.hydro_context_state.to_numpy(),
                    "hydro_dominant_unit": ss.hydro_dominant_unit.to_numpy(),
                    "hydro_dominant_domain": ss.hydro_dominant_domain.to_numpy(),
                    "independence_state": "UNKNOWN_NAO_DEMONSTRADA",
                    "representativeness_state": "UNKNOWN_NAO_DEMONSTRADA",
                    "recommendation": recommendations,
                    "unknown_is_zero": False,
                    "weight_used": False,
                    "score_used": False,
                    "integrated_priority_calculated": False,
                    "potential_calculated": False,
                    "interpolation_used": False,
                    "prediction_used": False,
                    "cutoff_date": CUTOFF,
                    "method_version": METHOD,
                }
            )
            long_frames.append(rows)
            prefix = question.lower()
            for column in (
                "priority_code", "priority_class", "priority_label", "confidence_code", "confidence_class", "confidence_label",
                "direct_evidence_n", "context_gate_n", "minimum_documentary_n", "review_evidence_n", "unknown_evidence_n",
                "fully_blocked_requirements_n", "cross_scale_priority_exact_pct", "origin_priority_exact_pct",
                "top_blocking_requirements", "recommended_actions", "independence_state", "representativeness_state", "recommendation",
            ):
                wide[f"{prefix}_{column}"] = rows[column].to_numpy()
            summary = {
                "scale_km2": scale,
                "question_code": question,
                "question_name": question_names[question],
                "cells_n": len(rows),
                "priority_unknown_n": int((rows.priority_code == 0).sum()),
                "priority_p1_critical_n": int((rows.priority_code == 1).sum()),
                "priority_p2_high_n": int((rows.priority_code == 2).sum()),
                "priority_p3_moderate_n": int((rows.priority_code == 3).sum()),
                "priority_p4_low_n": int((rows.priority_code == 4).sum()),
                "priority_p5_documentary_sufficiency_n": int((rows.priority_code == 5).sum()),
                "confidence_unknown_n": int((rows.confidence_code == 0).sum()),
                "confidence_c1_very_low_n": int((rows.confidence_code == 1).sum()),
                "confidence_c2_low_n": int((rows.confidence_code == 2).sum()),
                "confidence_c3_moderate_n": int((rows.confidence_code == 3).sum()),
                "confidence_c4_high_n": int((rows.confidence_code == 4).sum()),
                "confidence_c5_very_high_n": int((rows.confidence_code == 5).sum()),
                "independence_demonstrated": False,
                "weight_used": False,
                "score_used": False,
                "integrated_priority_calculated": False,
                "method_version": METHOD,
            }
            summary_rows.append(summary)
        wide_by_scale[scale] = wide

    cell_long = pd.concat(long_frames, ignore_index=True)
    summary = pd.DataFrame(summary_rows)

    priority_registry = pd.DataFrame(
        [
            {
                "priority_code": code,
                "priority_class": value[0],
                "priority_label": value[1],
                "observable_rule": priority_explanation(code),
                "color_hex": PALETTE[str(code)],
                "weight_used": False,
                "method_version": METHOD,
            }
            for code, value in PRIORITY.items()
        ]
    )
    confidence_registry = pd.DataFrame(
        [
            {
                "confidence_code": code,
                "confidence_class": value[0],
                "confidence_label": value[1],
                "observable_rule": confidence_explanation(code),
                "color_hex": PALETTE[str(code)],
                "method_version": METHOD,
            }
            for code, value in CONFIDENCE.items()
        ]
    )
    question_rule_rows: list[dict[str, object]] = []
    for question in QUESTIONS:
        meta = question_definitions[question]
        question_rule_rows.append(
            {
                "question_code": question,
                "question_name": question_names[question],
                "question_objective": meta["question_objective"],
                "direct_evidence_definition": meta["direct_evidence_definition"],
                "context_gate_requirement_codes": "|".join(CONTEXT_REQUIREMENTS[question]),
                "context_gate_rule": "Ao menos um poço demonstra conjuntamente a evidência direta e todos os requisitos do portal de contexto.",
                "full_minimum_requirement_codes": "|".join(question_req_codes[question]),
                "full_minimum_rule": meta["minimum_documentary_definition"],
                "question_recommendation": QUESTION_ACTIONS[question],
                "independence_required_for_network_inference": True,
                "representativeness_required_for_p5": True,
                "weight_used": False,
                "score_used": False,
                "method_version": METHOD,
            }
        )
    question_rules = pd.DataFrame(question_rule_rows)

    outputs = {
        "cell_question_priority_long.csv": cell_long,
        "priority_scale_question_summary.csv": summary,
        "priority_class_registry.csv": priority_registry,
        "confidence_class_registry.csv": confidence_registry,
        "priority_question_rules.csv": question_rules,
        "requirement_action_registry.csv": req_actions,
        "support_priority_cross_scale.csv": support_cross,
        "support_priority_origin_scale.csv": support_origin,
    }
    for name, frame in outputs.items():
        write_csv(frame, name)
    for scale, wide in wide_by_scale.items():
        name = f"research_priority_{scale}km2.csv"
        write_csv(wide, name)
        outputs[name] = wide
        payload = grids[scale].to_crs(4326)[["cell_id", "geometry"]].merge(wide, on="cell_id", how="left", validate="one_to_one")
        geo_path = OUT / f"research_priority_{scale}km2.geojson"
        geo_path.unlink(missing_ok=True)
        payload.to_file(geo_path, driver="GeoJSON", index=False)

    style = {
        "version": "2.6-experimental",
        "priority_palette": PALETTE,
        "confidence_palette": PALETTE,
        "priority_labels": {str(code): {"class": value[0], "label": value[1]} for code, value in PRIORITY.items()},
        "confidence_labels": {str(code): {"class": value[0], "label": value[1]} for code, value in CONFIDENCE.items()},
        "metrics": {
            "priority_code": "Prioridade de investigação por pergunta",
            "confidence_code": "Confiança da classificação",
            "cross_scale_priority_exact_pct": "Concordância exata da prioridade entre escalas",
            "origin_priority_exact_pct": "Concordância exata da prioridade entre origens",
            "direct_evidence_n": "Poços com evidência direta",
            "context_gate_n": "Poços que satisfazem o portal de contexto",
            "fully_blocked_requirements_n": "Requisitos ausentes em todos os poços da célula",
        },
    }
    (OUT / "research_priority_style_metadata.json").write_text(json.dumps(style, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    registry = {
        "version": "2.6-experimental",
        "method_version": METHOD,
        "wells_n": len(wells),
        "support_points_n": len(support),
        "cells_n": sum(EXPECTED_CELLS.values()),
        "cell_question_pairs_n": len(cell_long),
        "requirements_n": len(requirement_registry),
        "questions": list(QUESTIONS),
        "scales_km2": list(SCALES),
        "origins": [item[0] for item in ORIGINS],
        "rules": {
            "unknown_is_zero": False,
            "weight_used": False,
            "score_used": False,
            "integrated_priority_calculated": False,
            "potential_calculated": False,
            "interpolation_used": False,
            "prediction_used": False,
            "independence_demonstrated": False,
            "representativeness_demonstrated": False,
        },
    }
    (OUT / "research_priority_registry.json").write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return outputs


def field_definition(field: str, sources: str) -> dict[str, str]:
    unit = "texto"
    if field.endswith("_n") or field.endswith("_code") or field == "scale_km2":
        unit = "n"
    if field.endswith("_pct"):
        unit = "%"
    if field.endswith("_used") or field.endswith("_calculated") or field.endswith("_demonstrated") or field.startswith("priority_exact_"):
        unit = "booleano"
    readable = field.replace("_", " ")
    if field.endswith("_pct"):
        definition = f"Percentual associado a {readable}, com denominador explícito no produto V2.6."
    elif field.endswith("_n") or field.endswith("_code"):
        definition = f"Contagem ou código controlado associado a {readable} no produto V2.6."
    elif unit == "booleano":
        definition = f"Indicador lógico associado a {readable} nas regras da V2.6."
    else:
        definition = f"Valor auditável de {readable} no módulo experimental V2.6."
    if "priority" in field and "confidence" not in field:
        rule = "Classificação categórica não compensatória derivada do déficit documental demonstrado para uma pergunta explícita."
    elif "confidence" in field:
        rule = "Classe separada derivada da concordância exata da prioridade entre cinco escalas e quatro origens."
    elif "context_gate" in field:
        rule = "Conjunção de evidência direta e requisitos intermediários explicitados no registro de regras da pergunta."
    elif "blocked" in field or "blocking" in field:
        rule = "Requisito não demonstrado nos poços atribuídos à célula, sem inferir ausência física da propriedade."
    elif field in {"weight_used", "score_used", "integrated_priority_calculated"}:
        rule = "FALSE em toda a V2.6 experimental."
    else:
        rule = "Calculado diretamente no universo, pergunta, escala, origem e denominador declarados no arquivo de origem."
    return {
        "field": field,
        "modules": "Prioridade de investigação por pergunta",
        "source_files": sources,
        "definition": definition,
        "formula_or_rule": rule,
        "unit": unit,
        "how_to_read": "Ler junto da pergunta, da escala, da classe de confiança, dos bloqueios e dos limites declarados.",
        "does_not_mean": "Não é potencial aquífero, prioridade absoluta, prioridade integrada, representatividade territorial, peso ou score.",
        "unknown_rule": "Sem base classificável, permanece UNKNOWN e não é convertido em zero.",
    }


def update_dictionary(outputs: dict[str, pd.DataFrame]) -> None:
    master_path = ROOT / "methodology/DICIONARIO_METRICAS_RESULTADOS_V1.csv"
    master = pd.read_csv(master_path)
    master = master[~master.modules.eq("Prioridade de investigação por pergunta")].copy()
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
    if additions:
        master = pd.concat([master, pd.DataFrame(additions)], ignore_index=True).sort_values("field", kind="stable")
    module_mask = master.modules.eq("Prioridade de investigação por pergunta")
    for field, sources in sources_by_field.items():
        if (module_mask & master.field.eq(field)).any():
            definition = field_definition(field, " | ".join(sorted(sources)))
            mask = module_mask & master.field.eq(field)
            for column, value in definition.items():
                if column in master.columns and column != "field":
                    master.loc[mask, column] = value
    master.to_csv(master_path, index=False, encoding="utf-8-sig")
    annex = master[master.modules.eq("Prioridade de investigação por pergunta")].copy()
    annex.to_csv(ROOT / "methodology/PRIORIDADE_INVESTIGACAO_CAMPOS_V1.csv", index=False, encoding="utf-8-sig")
    annex.to_csv(OUT / "research_priority_field_dictionary.csv", index=False, encoding="utf-8-sig")
    shutil.copy2(master_path, ROOT / "docs/data/dicionario_metricas_resultados_v1.csv")


def publish() -> None:
    for source in OUT.iterdir():
        if source.is_file():
            shutil.copy2(source, WEB / source.name)


def main() -> None:
    outputs = build()
    update_dictionary(outputs)
    publish()
    long = outputs["cell_question_priority_long.csv"]
    priority_counts = long.priority_code.value_counts().sort_index().to_dict()
    confidence_counts = long.confidence_code.value_counts().sort_index().to_dict()
    fields = pd.read_csv(ROOT / "methodology/DICIONARIO_METRICAS_RESULTADOS_V1.csv")
    print("OK V2.6")
    print(f"{sum(EXPECTED_CELLS.values())} células, {len(long)} pares, 3877 poços, 39 requisitos e {len(fields)} campos")
    print(f"Prioridade {priority_counts}")
    print(f"Confiança {confidence_counts}")


if __name__ == "__main__":
    main()
