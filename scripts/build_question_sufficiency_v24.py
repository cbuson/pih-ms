#!/usr/bin/env python3
"""Constrói a matriz PIH MS V2.4 de suficiência por pergunta.

A rotina separa quatro níveis que não podem ser confundidos.

1. Evidência direta disponível no registro adquirido
2. Requisitos documentais mínimos por pergunta
3. Estado agregado local da célula
4. Representatividade territorial da célula

Não são usados pesos, score, interpolação, predição ou limiares universais de
quantidade de poços. A presença de um registro que atende ao mínimo documental
não demonstra representatividade da célula.
"""
from __future__ import annotations

from collections import Counter
from itertools import combinations
from pathlib import Path
import csv
import json
import math
import shutil

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data/derived/question_sufficiency"
WEB = ROOT / "docs/data/question_sufficiency"
PROVENANCE = ROOT / "provenance"
SCALES = (100, 150, 250, 500, 1000)
EXPECTED_CELLS = {100: 3763, 150: 2525, 250: 1537, 500: 791, 1000: 413}
CUTOFF = "2026-08-29"
METHOD_VERSION = "PIH_MS_V2.4_SUF_PERGUNTA_V1"
GRID_FAMILY = "SCALE_PRIMARY_O00_V1"

QUESTIONS = [
    {
        "question_code": "Q01",
        "question_name": "Nível e profundidade da água",
        "question_objective": "Avaliar se o conjunto adquirido permite interpretar uma observação pontual de nível de água no contexto construtivo e hidrogeológico do poço.",
        "direct_evidence_definition": "Nível estático informado no conjunto adquirido.",
        "minimum_documentary_definition": "Coordenada válida, nível estático, data explícita da medição, profundidade positiva, intervalo captado demonstrado, atribuição hidroestratigráfica consistente e ausência de valor objetivamente inválido nas regras atuais.",
        "cell_interpretation": "Presença local de registros documentais. Não demonstra superfície potenciométrica, tendência, independência ou representatividade da célula.",
        "source_ids": "IN02|IN03|OF02|OF04",
    },
    {
        "question_code": "Q02",
        "question_name": "Propriedades hidráulicas",
        "question_objective": "Avaliar se há documentação suficiente para interpretar uma propriedade hidráulica derivada de ensaio de poço.",
        "direct_evidence_definition": "Capacidade específica não negativa, ensaio cadastrado ou transmissividade informada.",
        "minimum_documentary_definition": "Coordenada válida, intervalo captado, atribuição hidroestratigráfica consistente, ensaio com metadados mínimos, data, método interpretativo, parâmetro informado, unidade verificada e ausência de valor objetivamente inválido nas regras atuais.",
        "cell_interpretation": "Presença local de ensaio documentado. Não demonstra comparabilidade entre ensaios nem parâmetro representativo da célula.",
        "source_ids": "HY01|HY02|HY06|OF02",
    },
    {
        "question_code": "Q03",
        "question_name": "Hidroquímica",
        "question_objective": "Avaliar se um resultado químico pode ser interpretado no contexto do poço, da amostragem e do controle de qualidade.",
        "direct_evidence_definition": "Ao menos uma evidência hidroquímica ou físico-química parcial.",
        "minimum_documentary_definition": "Coordenada válida, intervalo captado, atribuição hidroestratigráfica consistente, amostra ou resultado, data, parâmetro, unidade verificada, QA analítico demonstrado e ausência de valor objetivamente inválido nas regras atuais.",
        "cell_interpretation": "Presença local de resultado documentado. Não demonstra qualidade natural, contaminação, tendência ou comparabilidade regional.",
        "source_ids": "HY07|HY08|OF08|BR01",
    },
    {
        "question_code": "Q04",
        "question_name": "Geometria e estratigrafia do aquífero",
        "question_objective": "Avaliar se o poço possui informação vertical suficiente para relacionar construção, perfil e intervalo efetivamente captado.",
        "direct_evidence_definition": "Profundidade positiva ou metadado vertical documentado.",
        "minimum_documentary_definition": "Coordenada válida, profundidade positiva, perfil litológico explícito, intervalo captado demonstrado, atribuição hidroestratigráfica consistente e ausência de valor objetivamente inválido nas regras atuais.",
        "cell_interpretation": "Presença local de documentação vertical. Não demonstra geometria tridimensional contínua do aquífero.",
        "source_ids": "IN01|IN03|IN04|OF01|OF02",
    },
    {
        "question_code": "Q05",
        "question_name": "Monitoramento temporal",
        "question_objective": "Avaliar se existe uma série adquirida da mesma variável que permita estudar mudança no tempo.",
        "direct_evidence_definition": "Ao menos um evento hidrogeológico datado.",
        "minimum_documentary_definition": "Coordenada válida, série da mesma variável demonstrada, datas explícitas, intervalo captado, atribuição hidroestratigráfica consistente, identificação da variável, controle documental e ausência de valor objetivamente inválido nas regras atuais.",
        "cell_interpretation": "Presença local de eventos datados. Não demonstra continuidade, tendência ou cobertura temporal da célula.",
        "source_ids": "IN02|IN03|OF04|FU04|FU05",
    },
]


DIMENSION_ROLES = {
    "Q01": {
        "ESPACIAL": "CRITICA_REGISTRO",
        "HIDROESTRATIGRAFICA": "CRITICA_REGISTRO",
        "VERTICAL": "CRITICA_REGISTRO",
        "HIDRAULICA": "CRITICA_REGISTRO",
        "HIDROQUIMICA": "NAO_APLICAVEL",
        "TEMPORAL": "CRITICA_REGISTRO",
        "INDEPENDENCIA": "CRITICA_CELULA",
        "QUALIDADE_DOCUMENTAL": "CRITICA_REGISTRO",
        "INCERTEZA": "TRANSVERSAL",
    },
    "Q02": {
        "ESPACIAL": "CRITICA_REGISTRO",
        "HIDROESTRATIGRAFICA": "CRITICA_REGISTRO",
        "VERTICAL": "CRITICA_REGISTRO",
        "HIDRAULICA": "CRITICA_REGISTRO",
        "HIDROQUIMICA": "NAO_APLICAVEL",
        "TEMPORAL": "SUPORTE",
        "INDEPENDENCIA": "CRITICA_CELULA",
        "QUALIDADE_DOCUMENTAL": "CRITICA_REGISTRO",
        "INCERTEZA": "TRANSVERSAL",
    },
    "Q03": {
        "ESPACIAL": "CRITICA_REGISTRO",
        "HIDROESTRATIGRAFICA": "CRITICA_REGISTRO",
        "VERTICAL": "CRITICA_REGISTRO",
        "HIDRAULICA": "NAO_APLICAVEL",
        "HIDROQUIMICA": "CRITICA_REGISTRO",
        "TEMPORAL": "CRITICA_REGISTRO",
        "INDEPENDENCIA": "CRITICA_CELULA",
        "QUALIDADE_DOCUMENTAL": "CRITICA_REGISTRO",
        "INCERTEZA": "TRANSVERSAL",
    },
    "Q04": {
        "ESPACIAL": "CRITICA_REGISTRO",
        "HIDROESTRATIGRAFICA": "CRITICA_REGISTRO",
        "VERTICAL": "CRITICA_REGISTRO",
        "HIDRAULICA": "SUPORTE",
        "HIDROQUIMICA": "NAO_APLICAVEL",
        "TEMPORAL": "NAO_APLICAVEL",
        "INDEPENDENCIA": "CRITICA_CELULA",
        "QUALIDADE_DOCUMENTAL": "CRITICA_REGISTRO",
        "INCERTEZA": "TRANSVERSAL",
    },
    "Q05": {
        "ESPACIAL": "CRITICA_REGISTRO",
        "HIDROESTRATIGRAFICA": "CRITICA_REGISTRO",
        "VERTICAL": "CRITICA_REGISTRO",
        "HIDRAULICA": "CONDICIONAL_VARIAVEL",
        "HIDROQUIMICA": "CONDICIONAL_VARIAVEL",
        "TEMPORAL": "CRITICA_REGISTRO",
        "INDEPENDENCIA": "CRITICA_CELULA",
        "QUALIDADE_DOCUMENTAL": "CRITICA_REGISTRO",
        "INCERTEZA": "TRANSVERSAL",
    },
}


REQUIREMENTS = [
    ("Q01", "Q01_R01", "ESPACIAL", "COORDENADA_VALIDA", "spatial_coordinate_valid", "Coordenada válida nas regras atuais", "OF02|IN03"),
    ("Q01", "Q01_R02", "HIDRAULICA", "NIVEL_ESTATICO", "hydraulic_static_level_available", "Nível estático informado", "OF02|IN02"),
    ("Q01", "Q01_R03", "TEMPORAL", "DATA_NIVEL", "level_measurement_dated", "Data explícita associada à medição de nível", "IN02|IN03"),
    ("Q01", "Q01_R04", "VERTICAL", "PROFUNDIDADE_POSITIVA", "vertical_depth_positive", "Profundidade total positiva informada", "OF02|IN03"),
    ("Q01", "Q01_R05", "VERTICAL", "INTERVALO_CAPTADO", "capture_interval_demonstrated", "Intervalo filtrado ou aberto demonstrado", "IN03"),
    ("Q01", "Q01_R06", "HIDROESTRATIGRAFICA", "HIDROESTRATIGRAFIA_CONSISTENTE", "hydrostrat_consistent", "Atribuição hidroestratigráfica consistente nas regras atuais", "OF01|OF02"),
    ("Q01", "Q01_R07", "QUALIDADE_DOCUMENTAL", "SEM_INVALIDO_OBJETIVO", "no_objective_invalid", "Nenhum valor objetivamente inválido nas regras atuais", "OF02"),
    ("Q02", "Q02_R01", "ESPACIAL", "COORDENADA_VALIDA", "spatial_coordinate_valid", "Coordenada válida nas regras atuais", "OF02|IN03"),
    ("Q02", "Q02_R02", "VERTICAL", "INTERVALO_CAPTADO", "capture_interval_demonstrated", "Intervalo filtrado ou aberto demonstrado", "IN03|HY06"),
    ("Q02", "Q02_R03", "HIDROESTRATIGRAFICA", "HIDROESTRATIGRAFIA_CONSISTENTE", "hydrostrat_consistent", "Atribuição hidroestratigráfica consistente nas regras atuais", "OF01|HY06"),
    ("Q02", "Q02_R04", "HIDRAULICA", "ENSAIO_METADADOS_MINIMOS", "hydraulic_test_minimum_metadata", "Ensaio com metadados cadastrais mínimos", "HY01|HY02|HY06"),
    ("Q02", "Q02_R05", "TEMPORAL", "DATA_ENSAIO", "test_dated", "Data explícita do ensaio", "HY06"),
    ("Q02", "Q02_R06", "HIDRAULICA", "METODO_INTERPRETATIVO", "interpretation_method_documented", "Método de interpretação documentado", "HY01|HY02|HY06"),
    ("Q02", "Q02_R07", "HIDRAULICA", "PARAMETRO_HIDRAULICO", "hydraulic_parameter_reported", "Transmissividade informada", "HY01|HY02|HY06"),
    ("Q02", "Q02_R08", "HIDRAULICA", "UNIDADE_HIDRAULICA_VERIFICADA", "hydraulic_unit_verified", "Unidade do parâmetro verificada documentalmente", "HY06"),
    ("Q02", "Q02_R09", "QUALIDADE_DOCUMENTAL", "SEM_INVALIDO_OBJETIVO", "no_objective_invalid", "Nenhum valor objetivamente inválido nas regras atuais", "OF02"),
    ("Q03", "Q03_R01", "ESPACIAL", "COORDENADA_VALIDA", "spatial_coordinate_valid", "Coordenada válida nas regras atuais", "OF02|IN03"),
    ("Q03", "Q03_R02", "VERTICAL", "INTERVALO_CAPTADO", "capture_interval_demonstrated", "Intervalo filtrado ou aberto demonstrado", "IN03|HY08"),
    ("Q03", "Q03_R03", "HIDROESTRATIGRAFICA", "HIDROESTRATIGRAFIA_CONSISTENTE", "hydrostrat_consistent", "Atribuição hidroestratigráfica consistente nas regras atuais", "OF01|HY08"),
    ("Q03", "Q03_R04", "HIDROQUIMICA", "EVIDENCIA_HIDROQUIMICA", "hydrochemical_partial_evidence", "Amostra ou resultado químico parcial presente", "HY07|HY08"),
    ("Q03", "Q03_R05", "TEMPORAL", "DATA_HIDROQUIMICA", "chemistry_dated", "Data de coleta ou análise disponível", "HY07|HY08|BR01"),
    ("Q03", "Q03_R06", "HIDROQUIMICA", "PARAMETRO_IDENTIFICADO", "chem_parameter_identified", "Parâmetro químico identificado", "HY07|HY08"),
    ("Q03", "Q03_R07", "HIDROQUIMICA", "UNIDADE_QUIMICA_VERIFICADA", "chem_unit_verified", "Unidade do resultado verificada documentalmente", "HY07|HY08"),
    ("Q03", "Q03_R08", "HIDROQUIMICA", "QA_ANALITICO_COMPLETO", "chem_qa_complete", "Amostragem, método e QA analítico demonstrados", "HY07|HY08|BR01"),
    ("Q03", "Q03_R09", "QUALIDADE_DOCUMENTAL", "SEM_INVALIDO_OBJETIVO", "no_objective_invalid", "Nenhum valor objetivamente inválido nas regras atuais", "OF02"),
    ("Q04", "Q04_R01", "ESPACIAL", "COORDENADA_VALIDA", "spatial_coordinate_valid", "Coordenada válida nas regras atuais", "OF02|IN03"),
    ("Q04", "Q04_R02", "VERTICAL", "PROFUNDIDADE_POSITIVA", "vertical_depth_positive", "Profundidade total positiva informada", "OF02|IN03"),
    ("Q04", "Q04_R03", "VERTICAL", "PERFIL_LITOLOGICO", "explicit_profile_documented", "Perfil litológico explícito adquirido", "IN01|IN03"),
    ("Q04", "Q04_R04", "VERTICAL", "INTERVALO_CAPTADO", "capture_interval_demonstrated", "Intervalo filtrado ou aberto demonstrado", "IN01|IN03"),
    ("Q04", "Q04_R05", "HIDROESTRATIGRAFICA", "HIDROESTRATIGRAFIA_CONSISTENTE", "hydrostrat_consistent", "Atribuição hidroestratigráfica consistente nas regras atuais", "OF01|OF02"),
    ("Q04", "Q04_R06", "QUALIDADE_DOCUMENTAL", "SEM_INVALIDO_OBJETIVO", "no_objective_invalid", "Nenhum valor objetivamente inválido nas regras atuais", "OF02"),
    ("Q05", "Q05_R01", "ESPACIAL", "COORDENADA_VALIDA", "spatial_coordinate_valid", "Coordenada válida nas regras atuais", "OF02|IN03"),
    ("Q05", "Q05_R02", "TEMPORAL", "SERIE_MESMA_VARIAVEL", "time_series_demonstrated", "Série adquirida da mesma variável", "IN02|IN03|OF04"),
    ("Q05", "Q05_R03", "TEMPORAL", "EVIDENCIA_DATADA", "temporal_any_dated", "Ao menos um evento datado", "IN02|IN03"),
    ("Q05", "Q05_R04", "VERTICAL", "INTERVALO_CAPTADO", "capture_interval_demonstrated", "Intervalo filtrado ou aberto demonstrado", "IN03"),
    ("Q05", "Q05_R05", "HIDROESTRATIGRAFICA", "HIDROESTRATIGRAFIA_CONSISTENTE", "hydrostrat_consistent", "Atribuição hidroestratigráfica consistente nas regras atuais", "OF01|IN03"),
    ("Q05", "Q05_R06", "TEMPORAL", "VARIAVEL_TEMPORAL_IDENTIFICADA", "temporal_variable_identified", "Variável da série identificada e repetida", "IN02|IN03"),
    ("Q05", "Q05_R07", "INDEPENDENCIA", "INDEPENDENCIA_HIDROGEOLOGICA", "independence_demonstrated", "Independência necessária para inferência de rede demonstrada", "IN03|IR03"),
    ("Q05", "Q05_R08", "QUALIDADE_DOCUMENTAL", "SEM_INVALIDO_OBJETIVO", "no_objective_invalid", "Nenhum valor objetivamente inválido nas regras atuais", "OF02"),
]


DIRECT_FIELDS = {
    "Q01": "hydraulic_static_level_available",
    "Q02": "hydraulic_direct_evidence",
    "Q03": "hydrochemical_partial_evidence",
    "Q04": "vertical_direct_evidence",
    "Q05": "temporal_any_dated",
}


UNKNOWN_STATUS = {
    "spatial_coordinate_valid": "REVISAO_COORDENADA_NAO_VALIDA",
    "hydraulic_static_level_available": "UNKNOWN_NIVEL_ESTATICO_NAO_DOCUMENTADO",
    "level_measurement_dated": "UNKNOWN_DATA_DA_MEDICAO_DE_NIVEL",
    "vertical_depth_positive": "UNKNOWN_PROFUNDIDADE_POSITIVA_NAO_DOCUMENTADA",
    "capture_interval_demonstrated": "UNKNOWN_INTERVALO_CAPTADO_NAO_ADQUIRIDO",
    "hydrostrat_consistent": "UNKNOWN_OU_REVISAO_HIDROESTRATIGRAFICA",
    "no_objective_invalid": "REVISAO_VALOR_OBJETIVAMENTE_INVALIDO",
    "hydraulic_test_minimum_metadata": "UNKNOWN_ENSAIO_COM_METADADOS_MINIMOS",
    "test_dated": "UNKNOWN_DATA_DO_ENSAIO",
    "interpretation_method_documented": "UNKNOWN_METODO_INTERPRETATIVO",
    "hydraulic_parameter_reported": "UNKNOWN_PARAMETRO_HIDRAULICO_VALIDAVEL",
    "hydraulic_unit_verified": "UNKNOWN_UNIDADE_HIDRAULICA_VERIFICADA",
    "hydrochemical_partial_evidence": "UNKNOWN_EVIDENCIA_HIDROQUIMICA",
    "chemistry_dated": "UNKNOWN_DATA_HIDROQUIMICA",
    "chem_parameter_identified": "UNKNOWN_PARAMETRO_HIDROQUIMICO",
    "chem_unit_verified": "UNKNOWN_UNIDADE_HIDROQUIMICA_VERIFICADA",
    "chem_qa_complete": "UNKNOWN_QA_HIDROQUIMICO_COMPLETO",
    "explicit_profile_documented": "UNKNOWN_PERFIL_LITOLOGICO_EXPLICITO",
    "time_series_demonstrated": "UNKNOWN_SERIE_TEMPORAL_NAO_ADQUIRIDA",
    "temporal_any_dated": "UNKNOWN_EVIDENCIA_TEMPORAL_DATADA",
    "temporal_variable_identified": "UNKNOWN_VARIAVEL_TEMPORAL_REPETIDA",
    "independence_demonstrated": "UNKNOWN_INDEPENDENCIA_HIDROGEOLOGICA",
}


def as_bool(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.fillna(False)
    return series.fillna(False).astype(str).str.strip().str.lower().isin({"true", "1", "sim", "yes"})


def pct(numerator: int, denominator: int) -> float | None:
    return round(100.0 * numerator / denominator, 6) if denominator else None


def read_inputs() -> pd.DataFrame:
    effective = pd.read_csv(ROOT / "PIH_MS_WELL_EFFECTIVE_KNOWLEDGE.csv", low_memory=False)
    vertical = pd.read_csv(ROOT / "data/derived/vertical_temporal/well_vertical_temporal.csv", low_memory=False)
    presence = pd.read_csv(ROOT / "data/source_audit/well_evidence_presence.csv", low_memory=False)
    hydraulic = pd.read_csv(ROOT / "data/source_audit/hydraulic_parameters.csv", low_memory=False)
    chemistry = pd.read_csv(ROOT / "data/source_audit/chem_results.csv", low_memory=False)

    vertical_fields = [
        "well_id",
        "level_measurement_dated",
        "test_dated",
        "chemistry_dated",
        "explicit_profile_documented",
        "capture_interval_status",
        "time_series_status",
    ]
    presence_fields = ["well_id", "has_interpretation_method_sgb2024"]
    wells = effective.merge(vertical[vertical_fields], on="well_id", how="left", validate="one_to_one")
    wells = wells.merge(presence[presence_fields], on="well_id", how="left", validate="one_to_one")

    hyd_unit = hydraulic.assign(
        verified=~hydraulic["unit"].fillna("").astype(str).str.contains("NOT_VERIFIED|UNKNOWN", case=False, regex=True)
    ).groupby("well_id")["verified"].any()
    chem_unit = chemistry.assign(
        verified=~chemistry["unit"].fillna("").astype(str).str.contains("NOT_VERIFIED|UNKNOWN", case=False, regex=True)
    ).groupby("well_id")["verified"].any()
    chem_parameter = chemistry.assign(
        identified=chemistry["parameter"].fillna("").astype(str).str.strip().ne("")
    ).groupby("well_id")["identified"].any()

    wells["hydraulic_unit_verified"] = wells["well_id"].map(hyd_unit).fillna(False)
    wells["chem_unit_verified"] = wells["well_id"].map(chem_unit).fillna(False)
    wells["chem_parameter_identified"] = wells["well_id"].map(chem_parameter).fillna(False)
    wells["interpretation_method_documented"] = as_bool(wells["has_interpretation_method_sgb2024"])
    wells["capture_interval_demonstrated"] = wells["capture_interval_status"].fillna("").astype(str).str.startswith("DEMONSTRADO")
    wells["time_series_demonstrated"] = wells["time_series_status"].fillna("").astype(str).str.startswith("DEMONSTRADA")
    wells["hydrostrat_consistent"] = wells["hydrostrat_state"].eq("DOCUMENTADO_CONSISTENTE")
    wells["no_objective_invalid"] = pd.to_numeric(wells["documentary_invalid_flags_n"], errors="coerce").fillna(0).eq(0)
    wells["hydraulic_parameter_reported"] = as_bool(wells["hydraulic_transmissivity_reported"])
    wells["chem_qa_complete"] = False
    wells["temporal_variable_identified"] = False
    wells["independence_demonstrated"] = False
    wells["hydraulic_direct_evidence"] = (
        as_bool(wells["hydraulic_specific_capacity_nonnegative"])
        | as_bool(wells["hydraulic_test_registered"])
        | as_bool(wells["hydraulic_transmissivity_reported"])
    )
    wells["vertical_direct_evidence"] = (
        as_bool(wells["vertical_depth_positive"])
        | pd.to_numeric(wells["vertical_metadata_n"], errors="coerce").fillna(0).gt(0)
    )
    for field in {
        req[4] for req in REQUIREMENTS
    } | set(DIRECT_FIELDS.values()):
        wells[field] = as_bool(wells[field])
    assert len(wells) == 3877
    assert wells["well_id"].nunique() == 3877
    return wells


def requirement_status(row: pd.Series, field: str) -> str:
    if bool(row[field]):
        return "DEMONSTRADO_NAS_REGRAS_ATUAIS"
    if field == "hydrostrat_consistent":
        source = str(row.get("hydrostrat_state", ""))
        if source.startswith("REVISAO") or source == "DOCUMENTADO_POSSIVELMENTE_CONSISTENTE":
            return "REVISAO_HIDROESTRATIGRAFICA_NAO_CONCLUSIVA"
        return "UNKNOWN_HIDROESTRATIGRAFIA"
    return UNKNOWN_STATUS[field]


def build_requirement_registry() -> pd.DataFrame:
    rows = []
    for question, code, dimension, name, field, rule, sources in REQUIREMENTS:
        rows.append(
            {
                "question_code": question,
                "requirement_code": code,
                "dimension": dimension,
                "requirement_name": name,
                "source_field": field,
                "role": "CRITICO_REGISTRO",
                "evaluation_rule": rule,
                "demonstrated_rule": f"{field} = TRUE",
                "not_demonstrated_state": UNKNOWN_STATUS[field],
                "source_ids": sources,
                "universal_numeric_threshold_used": False,
                "weight_used": False,
                "unknown_rule": "Falha do requisito descreve o conjunto adquirido e não ausência física da propriedade.",
                "method_version": METHOD_VERSION,
            }
        )
    return pd.DataFrame(rows)


def build_dimension_dependency() -> pd.DataFrame:
    rows = []
    for question in [item["question_code"] for item in QUESTIONS]:
        for dimension, role in DIMENSION_ROLES[question].items():
            rows.append(
                {
                    "question_code": question,
                    "dimension": dimension,
                    "role": role,
                    "aggregation_allowed": False,
                    "substitution_allowed": False,
                    "interpretation": "Dimensão mantida separada. O papel indica dependência da pergunta e não peso.",
                    "method_version": METHOD_VERSION,
                }
            )
    return pd.DataFrame(rows)


def build_well_tables(wells: pd.DataFrame, requirement_registry: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    requirement_rows = []
    question_rows = []
    base_fields = [
        "well_id",
        "latitude",
        "longitude",
        "municipality_declared",
        "municipality_spatial",
        "sgb2024_unit_aflorante",
        "hydrolithologic_domain",
    ]
    question_by_code = {item["question_code"]: item for item in QUESTIONS}
    for _, well in wells.iterrows():
        base = {field: well.get(field) for field in base_fields}
        for question_code, group in requirement_registry.groupby("question_code", sort=False):
            statuses = []
            for req in group.itertuples(index=False):
                status = requirement_status(well, req.source_field)
                statuses.append((req.requirement_code, status))
                requirement_rows.append(
                    {
                        **base,
                        "question_code": question_code,
                        "requirement_code": req.requirement_code,
                        "dimension": req.dimension,
                        "requirement_name": req.requirement_name,
                        "requirement_status": status,
                        "demonstrated": status == "DEMONSTRADO_NAS_REGRAS_ATUAIS",
                        "source_field": req.source_field,
                        "source_value": bool(well[req.source_field]),
                        "cutoff_date": CUTOFF,
                        "method_version": METHOD_VERSION,
                    }
                )
            demonstrated = sum(status == "DEMONSTRADO_NAS_REGRAS_ATUAIS" for _, status in statuses)
            review = sum(status.startswith("REVISAO") for _, status in statuses)
            unknown = len(statuses) - demonstrated - review
            direct = bool(well[DIRECT_FIELDS[question_code]])
            minimum = demonstrated == len(statuses)
            if minimum:
                state = "MINIMO_DOCUMENTAL_ATENDIDO_COM_LIMITES"
            elif direct and review:
                state = "EVIDENCIA_PARCIAL_COM_REVISAO"
            elif direct:
                state = "EVIDENCIA_PARCIAL"
            else:
                state = "UNKNOWN_SEM_EVIDENCIA_DIRETA_NO_CONJUNTO"
            blockers = [code for code, status in statuses if status != "DEMONSTRADO_NAS_REGRAS_ATUAIS"]
            question_rows.append(
                {
                    **base,
                    "question_code": question_code,
                    "question_name": question_by_code[question_code]["question_name"],
                    "direct_evidence_present": direct,
                    "critical_requirements_n": len(statuses),
                    "critical_demonstrated_n": demonstrated,
                    "critical_review_n": review,
                    "critical_unknown_n": unknown,
                    "minimum_documentary_met": minimum,
                    "record_state": state,
                    "blocking_requirements_n": len(blockers),
                    "blocking_codes": "|".join(blockers),
                    "representativeness_state": "NAO_AVALIAVEL_NO_NIVEL_DO_REGISTRO",
                    "weight_used": False,
                    "score_used": False,
                    "cutoff_date": CUTOFF,
                    "method_version": METHOD_VERSION,
                }
            )
    well_requirements = pd.DataFrame(requirement_rows)
    well_questions = pd.DataFrame(question_rows)
    assert len(well_requirements) == 3877 * len(requirement_registry)
    assert len(well_questions) == 3877 * len(QUESTIONS)
    return well_requirements, well_questions


def top_blockers(series: pd.Series, limit: int = 5) -> str:
    counter = Counter()
    for value in series.fillna(""):
        counter.update(item for item in str(value).split("|") if item)
    return "|".join(f"{code}={count}" for code, count in counter.most_common(limit))


def build_cells(well_questions: pd.DataFrame) -> tuple[pd.DataFrame, dict[int, pd.DataFrame]]:
    assignments = pd.read_csv(DERIVED.parent / "effective_knowledge/effective_knowledge_assignment_audit.csv")
    assignments = assignments[["well_id", "scale_km2", "cell_id", "assignment_method"]]
    joined = assignments.merge(well_questions, on="well_id", how="left", validate="many_to_many")
    assert len(joined) == 3877 * len(SCALES) * len(QUESTIONS)
    cell_rows = []
    wide_by_scale = {}
    question_codes = [item["question_code"] for item in QUESTIONS]
    question_names = {item["question_code"]: item["question_name"] for item in QUESTIONS}
    for scale in SCALES:
        base = pd.read_csv(DERIVED.parent / f"effective_knowledge/effective_knowledge_{scale}km2.csv", low_memory=False)
        assert len(base) == EXPECTED_CELLS[scale]
        scale_joined = joined[joined["scale_km2"] == scale]
        wide = base[[
            "cell_id",
            "scale_km2",
            "variant",
            "area_effective_km2",
            "n_wells",
            "hydrostrat_dominant_unit",
            "hydrostrat_dominant_unit_pct",
            "hydrostrat_dominant_domain",
            "hydrostrat_dominant_domain_pct",
        ]].copy()
        for question_code in question_codes:
            subset = scale_joined[scale_joined["question_code"] == question_code]
            grouped = {cell_id: group for cell_id, group in subset.groupby("cell_id", sort=False)}
            q_rows = []
            for row in base.itertuples(index=False):
                cell_id = row.cell_id
                n_wells = int(row.n_wells)
                group = grouped.get(cell_id)
                if group is None:
                    direct_n = minimum_n = partial_n = review_n = unknown_n = 0
                    blockers = ""
                else:
                    direct_n = int(group["direct_evidence_present"].sum())
                    minimum_n = int(group["minimum_documentary_met"].sum())
                    partial_n = int(group["record_state"].eq("EVIDENCIA_PARCIAL").sum())
                    review_n = int(group["record_state"].eq("EVIDENCIA_PARCIAL_COM_REVISAO").sum())
                    unknown_n = int(group["record_state"].eq("UNKNOWN_SEM_EVIDENCIA_DIRETA_NO_CONJUNTO").sum())
                    blockers = top_blockers(group["blocking_codes"])
                assert minimum_n + partial_n + review_n + unknown_n == n_wells
                if n_wells == 0:
                    cell_state = "UNKNOWN_SEM_POCOS_NO_CONJUNTO_AUDITADO"
                    rep_state = "UNKNOWN_SEM_POCOS_NO_CONJUNTO_AUDITADO"
                elif minimum_n > 0:
                    cell_state = "MINIMO_DOCUMENTAL_LOCAL_PRESENTE_NAO_REPRESENTATIVO"
                    rep_state = "UNKNOWN_REPRESENTATIVIDADE_NAO_DEMONSTRADA"
                elif partial_n + review_n > 0:
                    cell_state = "SOMENTE_EVIDENCIA_PARCIAL"
                    rep_state = "UNKNOWN_REPRESENTATIVIDADE_NAO_DEMONSTRADA"
                else:
                    cell_state = "UNKNOWN_SEM_EVIDENCIA_DIRETA_DA_PERGUNTA"
                    rep_state = "UNKNOWN_REPRESENTATIVIDADE_NAO_DEMONSTRADA"
                q_rows.append(
                    {
                        "cell_id": cell_id,
                        "scale_km2": scale,
                        "grid_family": GRID_FAMILY,
                        "area_effective_km2": row.area_effective_km2,
                        "n_wells": n_wells,
                        "question_code": question_code,
                        "question_name": question_names[question_code],
                        "direct_evidence_n": direct_n,
                        "direct_evidence_pct_of_wells": pct(direct_n, n_wells),
                        "minimum_documentary_n": minimum_n,
                        "minimum_documentary_pct_of_wells": pct(minimum_n, n_wells),
                        "partial_evidence_n": partial_n,
                        "review_evidence_n": review_n,
                        "unknown_evidence_n": unknown_n,
                        "cell_documentary_state": cell_state,
                        "cell_representativeness_state": rep_state,
                        "top_blocking_requirements": blockers,
                        "universal_well_count_threshold_used": False,
                        "weight_used": False,
                        "score_used": False,
                        "cutoff_date": CUTOFF,
                        "method_version": METHOD_VERSION,
                    }
                )
            q_frame = pd.DataFrame(q_rows)
            cell_rows.extend(q_rows)
            prefix = question_code.lower()
            renamed = q_frame[[
                "cell_id",
                "direct_evidence_n",
                "minimum_documentary_n",
                "partial_evidence_n",
                "review_evidence_n",
                "unknown_evidence_n",
                "cell_documentary_state",
                "cell_representativeness_state",
                "top_blocking_requirements",
            ]].rename(columns={field: f"{prefix}_{field}" for field in q_frame.columns if field != "cell_id"})
            wide = wide.merge(renamed, on="cell_id", how="left", validate="one_to_one")
        wide["grid_family"] = GRID_FAMILY
        wide["cutoff_date"] = CUTOFF
        wide["method_version"] = METHOD_VERSION
        wide_by_scale[scale] = wide
    cell_long = pd.DataFrame(cell_rows)
    assert len(cell_long) == sum(EXPECTED_CELLS.values()) * len(QUESTIONS)
    return cell_long, wide_by_scale


def phi_coefficient(a: np.ndarray, b: np.ndarray) -> float | None:
    n11 = int(np.logical_and(a, b).sum())
    n10 = int(np.logical_and(a, ~b).sum())
    n01 = int(np.logical_and(~a, b).sum())
    n00 = int(np.logical_and(~a, ~b).sum())
    denominator = math.sqrt((n11 + n10) * (n01 + n00) * (n11 + n01) * (n10 + n00))
    return (n11 * n00 - n10 * n01) / denominator if denominator else None


def build_pairwise_dependency(wells: pd.DataFrame) -> pd.DataFrame:
    flags = {
        "PROFUNDIDADE_POSITIVA": "vertical_depth_positive",
        "NIVEL_ESTATICO": "hydraulic_static_level_available",
        "NIVEL_DINAMICO": "hydraulic_dynamic_level_available",
        "VAZAO_ESPECIFICA_NAO_NEGATIVA": "hydraulic_specific_capacity_nonnegative",
        "ENSAIO_CADASTRADO": "hydraulic_test_registered",
        "ENSAIO_METADADOS_MINIMOS": "hydraulic_test_minimum_metadata",
        "TRANSMISSIVIDADE_INFORMADA": "hydraulic_transmissivity_reported",
        "HIDROQUIMICA_PARCIAL": "hydrochemical_partial_evidence",
        "HIDROQUIMICA_DATADA": "hydrochemical_dated",
        "EVIDENCIA_DATADA": "temporal_any_dated",
        "NIVEL_DATADO": "level_measurement_dated",
        "ENSAIO_DATADO": "test_dated",
        "QUIMICA_DATADA": "chemistry_dated",
        "HIDROESTRATIGRAFIA_CONSISTENTE": "hydrostrat_consistent",
        "PERFIL_LITOLOGICO": "explicit_profile_documented",
        "INTERVALO_CAPTADO": "capture_interval_demonstrated",
        "SERIE_TEMPORAL": "time_series_demonstrated",
        "INDEPENDENCIA_DEMONSTRADA": "independence_demonstrated",
    }
    rows = []
    for (label_a, field_a), (label_b, field_b) in combinations(flags.items(), 2):
        a = as_bool(wells[field_a]).to_numpy(dtype=bool)
        b = as_bool(wells[field_b]).to_numpy(dtype=bool)
        n11 = int(np.logical_and(a, b).sum())
        n10 = int(np.logical_and(a, ~b).sum())
        n01 = int(np.logical_and(~a, b).sum())
        n00 = int(np.logical_and(~a, ~b).sum())
        union = n11 + n10 + n01
        rows.append(
            {
                "indicator_a": label_a,
                "source_field_a": field_a,
                "indicator_b": label_b,
                "source_field_b": field_b,
                "n11_both": n11,
                "n10_a_only": n10,
                "n01_b_only": n01,
                "n00_neither": n00,
                "jaccard_presence": round(n11 / union, 8) if union else None,
                "phi_presence": phi_coefficient(a, b),
                "a_implies_b_in_acquired_set": bool(a.sum() > 0 and n10 == 0),
                "b_implies_a_in_acquired_set": bool(b.sum() > 0 and n01 == 0),
                "causal_interpretation_allowed": False,
                "independence_demonstrated": False,
                "method_version": METHOD_VERSION,
            }
        )
    return pd.DataFrame(rows)


def build_summaries(well_questions: pd.DataFrame, cell_long: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    global_rows = []
    for question, group in well_questions.groupby("question_code", sort=False):
        global_rows.append(
            {
                "question_code": question,
                "question_name": group["question_name"].iloc[0],
                "n_wells": len(group),
                "direct_evidence_n": int(group["direct_evidence_present"].sum()),
                "minimum_documentary_n": int(group["minimum_documentary_met"].sum()),
                "partial_evidence_n": int(group["record_state"].eq("EVIDENCIA_PARCIAL").sum()),
                "review_evidence_n": int(group["record_state"].eq("EVIDENCIA_PARCIAL_COM_REVISAO").sum()),
                "unknown_evidence_n": int(group["record_state"].eq("UNKNOWN_SEM_EVIDENCIA_DIRETA_NO_CONJUNTO").sum()),
                "top_blocking_requirements": top_blockers(group["blocking_codes"], 8),
                "representative_wells_n": 0,
                "weights_used": False,
                "score_used": False,
                "method_version": METHOD_VERSION,
            }
        )
    scale_rows = []
    for (scale, question), group in cell_long.groupby(["scale_km2", "question_code"], sort=True):
        scale_rows.append(
            {
                "scale_km2": int(scale),
                "question_code": question,
                "question_name": group["question_name"].iloc[0],
                "cells_n": len(group),
                "cells_without_wells_n": int(group["n_wells"].eq(0).sum()),
                "cells_with_local_minimum_n": int(group["cell_documentary_state"].eq("MINIMO_DOCUMENTAL_LOCAL_PRESENTE_NAO_REPRESENTATIVO").sum()),
                "cells_partial_only_n": int(group["cell_documentary_state"].eq("SOMENTE_EVIDENCIA_PARCIAL").sum()),
                "cells_without_direct_evidence_n": int(group["cell_documentary_state"].eq("UNKNOWN_SEM_EVIDENCIA_DIRETA_DA_PERGUNTA").sum()),
                "cells_representative_n": 0,
                "sum_wells": int(group["n_wells"].sum()),
                "sum_direct_evidence": int(group["direct_evidence_n"].sum()),
                "sum_minimum_documentary": int(group["minimum_documentary_n"].sum()),
                "method_version": METHOD_VERSION,
            }
        )
    return pd.DataFrame(global_rows), pd.DataFrame(scale_rows)


def write_csv(frame: pd.DataFrame, name: str) -> None:
    frame.to_csv(DERIVED / name, index=False, encoding="utf-8-sig")


def build_geojson(wide_by_scale: dict[int, pd.DataFrame]) -> None:
    for scale, frame in wide_by_scale.items():
        source = DERIVED.parent / f"effective_knowledge/effective_knowledge_{scale}km2.geojson"
        payload = json.loads(source.read_text(encoding="utf-8"))
        by_id = {str(row["cell_id"]): row for row in frame.replace({np.nan: None}).to_dict("records")}
        for feature in payload["features"]:
            cell_id = str(feature["properties"]["cell_id"])
            feature["properties"] = by_id[cell_id]
        target = DERIVED / f"question_sufficiency_{scale}km2.geojson"
        target.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


def add_bibliography_reference() -> None:
    path = ROOT / "methodology/BIBLIOGRAFIA_MASTER_V1.csv"
    frame = pd.read_csv(path)
    if "BR01" not in set(frame["id"]):
        frame.loc[len(frame)] = {
            "id": "BR01",
            "group": "Normas brasileiras",
            "status": "REFERÊNCIA NORMATIVA",
            "year": 2008,
            "author": "Conselho Nacional do Meio Ambiente",
            "title": "Resolução CONAMA nº 396, de 3 de abril de 2008",
            "citation": "Conselho Nacional do Meio Ambiente. (2008). Resolução CONAMA nº 396, de 3 de abril de 2008. Dispõe sobre a classificação e diretrizes ambientais para o enquadramento das águas subterrâneas.",
            "url": "https://conama.mma.gov.br/?id=545&option=com_sisconama&task=arquivo.download",
            "supports": "Reforça que parâmetros, frequência, análise estatística e incerteza dependem do objetivo e do contexto hidrogeológico. Não fornece um limiar universal de quantidade de poços.",
        }
        frame.to_csv(path, index=False, encoding="utf-8-sig")
    shutil.copy2(path, ROOT / "docs/data/bibliografia_master_v1.csv")


def field_definition(field: str, sources: str) -> dict[str, str]:
    defaults = {
        "definition": "Campo da matriz de suficiência por pergunta da V2.4.",
        "formula_or_rule": "Definido pelas regras documentadas em SUFICIENCIA_POR_PERGUNTA_V1.md.",
        "unit": "texto",
        "how_to_read": "Descreve disponibilidade documental condicionada à pergunta selecionada.",
        "does_not_mean": "Não é potencial aquífero, prioridade, peso, score ou representatividade territorial.",
        "unknown_rule": "UNKNOWN permanece distinto de zero e de ausência física.",
    }
    numeric_n = field.endswith("_n") or field in {"n11_both", "n10_a_only", "n01_b_only", "n00_neither"}
    boolean = field.endswith("_met") or field.endswith("_used") or field.endswith("_allowed") or field.endswith("_demonstrated") or field.endswith("_present") or field.startswith("a_implies") or field.startswith("b_implies")
    percent = "pct" in field or field in {"jaccard_presence", "phi_presence"}
    if numeric_n:
        defaults["unit"] = "n"
        defaults["formula_or_rule"] = "Contagem direta no universo indicado pelo arquivo e pelo denominador explícito."
    if boolean:
        defaults["unit"] = "booleano"
    if percent:
        defaults["unit"] = "%" if "pct" in field else "0 a 1 ou UNKNOWN"
    specific = {
        "question_code": ("Código estável da pergunta científica.", "Q01 a Q05."),
        "question_name": ("Nome da pergunta científica.", "Rótulo controlado pelo registro de perguntas."),
        "requirement_code": ("Código estável do requisito.", "Combinação de pergunta e requisito."),
        "requirement_status": ("Estado observado do requisito no poço.", "DEMONSTRADO nas regras atuais ou código explícito de revisão ou UNKNOWN."),
        "record_state": ("Estado documental do poço para a pergunta.", "Mínimo somente quando todos os requisitos críticos são demonstrados."),
        "cell_documentary_state": ("Estado documental local da célula para a pergunta.", "Derivado dos estados dos poços associados diretamente à célula."),
        "cell_representativeness_state": ("Estado da representatividade territorial da célula.", "Permanece UNKNOWN sem independência e desenho amostral demonstrados."),
        "blocking_codes": ("Requisitos críticos não demonstrados no poço.", "Lista categórica separada por barra vertical e nunca somada como nota."),
        "top_blocking_requirements": ("Requisitos bloqueadores mais frequentes na célula ou síntese.", "Pares código e contagem ordenados apenas para auditoria."),
        "direct_evidence_present": ("Presença da evidência direta definida para a pergunta.", "Regra booleana indicada no registro de perguntas."),
        "minimum_documentary_met": ("Indica atendimento simultâneo de todos os requisitos críticos do registro.", "Conjunção lógica sem compensação."),
        "representativeness_state": ("Estado de representatividade no nível indicado.", "Não é inferido por proximidade ou contagem."),
        "universal_numeric_threshold_used": ("Declara se foi usado limiar numérico universal.", "FALSE em toda a V2.4."),
        "universal_well_count_threshold_used": ("Declara se a célula foi classificada por quantidade universal de poços.", "FALSE em toda a V2.4."),
        "weight_used": ("Declara uso de peso.", "FALSE em toda a V2.4."),
        "weights_used": ("Declara uso de pesos.", "FALSE em toda a V2.4."),
        "score_used": ("Declara uso de score.", "FALSE em toda a V2.4."),
    }
    if field in specific:
        defaults["definition"], defaults["formula_or_rule"] = specific[field]
    return {
        "field": field,
        "modules": "Suficiência por pergunta",
        "source_files": sources,
        **defaults,
    }


def update_dictionary(output_frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    master_path = ROOT / "methodology/DICIONARIO_METRICAS_RESULTADOS_V1.csv"
    master = pd.read_csv(master_path)
    sources_by_field: dict[str, set[str]] = {}
    for filename, frame in output_frames.items():
        for field in frame.columns:
            sources_by_field.setdefault(field, set()).add(filename)
    existing = set(master["field"])
    additions = [
        field_definition(field, " | ".join(sorted(sources)))
        for field, sources in sorted(sources_by_field.items())
        if field not in existing
    ]
    if additions:
        master = pd.concat([master, pd.DataFrame(additions)], ignore_index=True).sort_values("field", kind="stable")
        master.to_csv(master_path, index=False, encoding="utf-8-sig")
    shutil.copy2(master_path, ROOT / "docs/data/dicionario_metricas_resultados_v1.csv")
    annex = pd.DataFrame([field_definition(field, " | ".join(sorted(sources))) for field, sources in sorted(sources_by_field.items())])
    annex.to_csv(ROOT / "methodology/SUFICIENCIA_POR_PERGUNTA_CAMPOS_V1.csv", index=False, encoding="utf-8-sig")
    shutil.copy2(ROOT / "methodology/SUFICIENCIA_POR_PERGUNTA_CAMPOS_V1.csv", DERIVED / "question_sufficiency_field_dictionary.csv")
    return master


def write_registry_json(question_registry: pd.DataFrame, requirement_registry: pd.DataFrame) -> None:
    payload = {
        "version": "2.4",
        "method_version": METHOD_VERSION,
        "questions": question_registry.to_dict("records"),
        "requirements": requirement_registry.to_dict("records"),
        "states": {
            "MINIMO_DOCUMENTAL_ATENDIDO_COM_LIMITES": "Todos os requisitos críticos do registro estão demonstrados. Não implica representatividade territorial.",
            "EVIDENCIA_PARCIAL": "Há evidência direta, mas um ou mais requisitos críticos permanecem não demonstrados.",
            "EVIDENCIA_PARCIAL_COM_REVISAO": "Há evidência direta e ao menos um alerta objetivo de revisão.",
            "UNKNOWN_SEM_EVIDENCIA_DIRETA_NO_CONJUNTO": "O conjunto adquirido não contém a evidência direta da pergunta para o poço.",
        },
        "rules": {
            "unknown_is_zero": False,
            "weight_used": False,
            "score_used": False,
            "universal_well_count_threshold_used": False,
            "cell_presence_is_representativeness": False,
        },
    }
    (DERIVED / "question_sufficiency_registry.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def update_well_details(well_questions: pd.DataFrame) -> None:
    path = ROOT / "docs/data/well_details.json"
    details = json.loads(path.read_text(encoding="utf-8"))
    grouped = {}
    for well_id, group in well_questions.groupby("well_id", sort=False):
        grouped[str(int(well_id))] = {
            str(row.question_code): {
                "question_name": row.question_name,
                "direct_evidence_present": bool(row.direct_evidence_present),
                "minimum_documentary_met": bool(row.minimum_documentary_met),
                "record_state": row.record_state,
                "critical_requirements_n": int(row.critical_requirements_n),
                "critical_demonstrated_n": int(row.critical_demonstrated_n),
                "blocking_requirements_n": int(row.blocking_requirements_n),
                "blocking_codes": row.blocking_codes,
                "representativeness_state": row.representativeness_state,
            }
            for row in group.itertuples(index=False)
        }
    assert set(grouped) == set(details)
    for well_id, record in details.items():
        record["question_sufficiency"] = grouped[well_id]
    path.write_text(json.dumps(details, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


def copy_web_files() -> None:
    WEB.mkdir(parents=True, exist_ok=True)
    for path in DERIVED.iterdir():
        if path.suffix.lower() in {".csv", ".json", ".geojson"}:
            shutil.copy2(path, WEB / path.name)


def build_manifest() -> None:
    files = sorted(path for path in DERIVED.iterdir() if path.is_file())
    with (PROVENANCE / "question_sufficiency_manifest.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["path", "size_bytes", "method_version", "cutoff_date"])
        writer.writeheader()
        for path in files:
            writer.writerow(
                {
                    "path": path.relative_to(ROOT).as_posix(),
                    "size_bytes": path.stat().st_size,
                    "method_version": METHOD_VERSION,
                    "cutoff_date": CUTOFF,
                }
            )


def main() -> None:
    DERIVED.mkdir(parents=True, exist_ok=True)
    add_bibliography_reference()
    wells = read_inputs()
    question_registry = pd.DataFrame(QUESTIONS)
    question_registry["universal_numeric_threshold_used"] = False
    question_registry["weight_used"] = False
    question_registry["score_used"] = False
    question_registry["cutoff_date"] = CUTOFF
    question_registry["method_version"] = METHOD_VERSION
    requirement_registry = build_requirement_registry()
    dimension_dependency = build_dimension_dependency()
    well_requirements, well_questions = build_well_tables(wells, requirement_registry)
    cell_long, wide_by_scale = build_cells(well_questions)
    dependency_pairwise = build_pairwise_dependency(wells)
    global_summary, scale_summary = build_summaries(well_questions, cell_long)

    outputs = {
        "question_registry.csv": question_registry,
        "question_requirement_matrix.csv": requirement_registry,
        "dimension_dependency_matrix.csv": dimension_dependency,
        "well_requirement_status_long.csv": well_requirements,
        "well_question_sufficiency_long.csv": well_questions,
        "cell_question_sufficiency_long.csv": cell_long,
        "question_dependency_pairwise.csv": dependency_pairwise,
        "question_global_summary.csv": global_summary,
        "question_scale_summary.csv": scale_summary,
    }
    for name, frame in outputs.items():
        write_csv(frame, name)
    for scale, frame in wide_by_scale.items():
        name = f"question_sufficiency_{scale}km2.csv"
        outputs[name] = frame
        write_csv(frame, name)
    build_geojson(wide_by_scale)
    write_registry_json(question_registry, requirement_registry)
    master = update_dictionary(outputs)
    update_well_details(well_questions)
    copy_web_files()
    build_manifest()

    assert int(global_summary["minimum_documentary_n"].sum()) == 0
    assert int(scale_summary["cells_representative_n"].sum()) == 0
    print(f"OK {len(wells)} poços, {len(cell_long)} pares célula-pergunta e {len(master)} campos no dicionário")
    print(global_summary[["question_code", "direct_evidence_n", "minimum_documentary_n", "partial_evidence_n", "review_evidence_n", "unknown_evidence_n"]].to_string(index=False))


if __name__ == "__main__":
    main()
