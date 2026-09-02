#!/usr/bin/env python3
"""Build the auditable project-scale statistics used by PIH MS V2.7.1."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/data/statistics/project_statistics_v271.json"


def csv_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return max(sum(1 for _ in handle) - 1, 0)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def number(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        try:
            return float(value)
        except (TypeError, ValueError):
            return value


def dataset(stats: dict, dataset_id: str) -> list[dict]:
    return next(item["rows"] for item in stats["datasets"] if item["id"] == dataset_id)


def metric(rows: list[dict], metric_id: str):
    return next(number(row["value"]) for row in rows if row["metric"] == metric_id)


def count_csv_group(paths: list[Path]) -> dict:
    rows = 0
    bytes_n = 0
    max_columns = 0
    for path in paths:
        rows += csv_rows(path)
        bytes_n += path.stat().st_size
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            header = next(csv.reader(handle), [])
        max_columns = max(max_columns, len(header))
    return {
        "csv_files_n": len(paths),
        "physical_rows_n": rows,
        "bytes_n": bytes_n,
        "max_columns_n": max_columns,
    }


def build() -> dict:
    stats = read_json(ROOT / "docs/data/statistics/statistics_v26.json")
    effective = dataset(stats, "effective_global")
    question_rows = dataset(stats, "question_global")
    scale_rows = dataset(stats, "grid_evidence")
    stability_rows = dataset(stats, "stability_cross_scale")
    priority_rows = dataset(stats, "research_priority_summary")

    evidence_rows = read_csv(ROOT / "data/derived/evidence/camadas_evidencia_registry.csv")
    evidence_layers = [
        {
            "code": row["code"],
            "name": row["name"],
            "question": row["scientific_question"],
            "feature_count": int(row["feature_count"]),
            "source": row["source_dataset"],
            "limitation": row["limitations"],
        }
        for row in evidence_rows
    ]

    dimensions = read_csv(ROOT / "data/derived/effective_knowledge/effective_knowledge_registry.csv")
    question_registry = read_csv(ROOT / "data/derived/question_sufficiency/question_registry.csv")
    requirements = read_csv(ROOT / "data/derived/question_sufficiency/question_requirement_matrix.csv")
    requirement_dimensions = Counter(row["dimension"] for row in requirements)
    requirements_by_question = Counter(row["question_code"] for row in requirements)

    derived_csv = sorted((ROOT / "data/derived").rglob("*.csv"))
    all_csv = sorted(ROOT.rglob("*.csv"))
    source_audit_csv = sorted((ROOT / "data/source_audit").glob("*.csv"))

    historical_markers = {
        "grid_evidence_historical_candidate_v13",
        "spatial_structure_historical_candidate_v16",
    }
    module_paths: dict[str, list[Path]] = defaultdict(list)
    for path in derived_csv:
        module_paths[path.relative_to(ROOT / "data/derived").parts[0]].append(path)

    module_labels = {
        "effective_knowledge": "Conhecimento hidrogeológico efetivo",
        "evidence": "Evidências E01 a E12",
        "grid_evidence": "Malhas de evidência",
        "grid_evidence_historical_candidate_v13": "Malhas históricas preservadas",
        "independence_redundancy": "Independência e redundância",
        "question_sufficiency": "Suficiência por pergunta",
        "research_priority": "Prioridade de investigação por pergunta",
        "scale_study": "Estudo de escalas",
        "spatial_structure": "Estrutura espacial",
        "spatial_structure_historical_candidate_v16": "Estrutura espacial histórica",
        "stability_sensitivity": "Estabilidade e sensibilidade",
        "stratified_scale": "Estratificação hidrogeológica",
        "vertical_temporal": "Documentação vertical e temporal",
    }
    module_order = list(module_labels)
    module_inventory = []
    for key in module_order:
        if key not in module_paths:
            continue
        item = count_csv_group(module_paths[key])
        item.update({
            "id": key,
            "name": module_labels[key],
            "historical": key in historical_markers,
        })
        module_inventory.append(item)

    current_derived = [p for p in derived_csv if p.relative_to(ROOT / "data/derived").parts[0] not in historical_markers]
    current_derived_summary = count_csv_group(current_derived)
    all_derived_summary = count_csv_group(derived_csv)
    all_csv_summary = count_csv_group(all_csv)

    source_audit_tables = []
    for path in source_audit_csv:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            columns = next(csv.reader(handle), [])
        source_audit_tables.append({
            "file": path.name,
            "rows_n": csv_rows(path),
            "columns_n": len(columns),
        })

    priority_totals = Counter()
    confidence_totals = Counter()
    for row in priority_rows:
        for key in (
            "priority_unknown_n", "priority_p1_critical_n", "priority_p2_high_n",
            "priority_p3_moderate_n", "priority_p4_low_n",
            "priority_p5_documentary_sufficiency_n",
        ):
            priority_totals[key] += int(row[key])
        for key in (
            "confidence_unknown_n", "confidence_c1_very_low_n", "confidence_c2_low_n",
            "confidence_c3_moderate_n", "confidence_c4_high_n", "confidence_c5_very_high_n",
        ):
            confidence_totals[key] += int(row[key])

    priority_by_question = []
    for question in question_registry:
        rows = [row for row in priority_rows if row["question_code"] == question["question_code"]]
        totals = Counter()
        for row in rows:
            for key in priority_totals:
                totals[key] += int(row[key])
        priority_by_question.append({
            "question_code": question["question_code"],
            "question_name": question["question_name"],
            "cell_scale_records_n": sum(int(row["cells_n"]) for row in rows),
            **totals,
        })

    index_html = (ROOT / "docs/index.html").read_text(encoding="utf-8")
    checkbox_layers = len(re.findall(r'<input\b[^>]*\btype=["\']checkbox["\']', index_html, re.I))
    web_manifest = read_json(ROOT / "docs/data/sgb_2024_layers_web_manifest.json")

    shards = sorted((ROOT / "docs/data/well_details_shards").glob("[0-9][0-9].json"))
    shard_wells = sum(len(read_json(path)) for path in shards)

    bibliography_n = csv_rows(ROOT / "methodology/BIBLIOGRAFIA_MASTER_V1.csv")
    dictionary_n = csv_rows(ROOT / "methodology/DICIONARIO_METRICAS_RESULTADOS_V1.csv")
    summary_rows_n = sum(len(item["rows"]) for item in stats["datasets"])
    summary_columns_n = sum(len(item["columns"]) for item in stats["datasets"])

    methodology_stages = [
        ["P0", "Congelamento e auditoria das fontes", "Preservação de procedência, campos originais, estados UNKNOWN e valores inválidos."],
        ["V2.0", "Evidências E01 a E12", "Doze perguntas documentais observáveis derivadas sem transformar presença em qualidade."],
        ["V2.1", "Independência e redundância", "Separação entre quantidade aparente, sobreposição documental e evidência independente não demonstrada."],
        ["V2.2", "Conhecimento efetivo", "Nove dimensões mantidas separadas, sem nota única e sem compensação."],
        ["V2.3", "Completude multiescalar", "Cinco escalas comparáveis para malhas de evidência e estrutura espacial."],
        ["V2.4", "Suficiência por pergunta", "Cinco perguntas e 39 requisitos conjuntivos avaliados sem pesos."],
        ["V2.5", "Estabilidade e sensibilidade", "Comparação entre cinco escalas, quatro origens e 14.284 pontos fixos de suporte."],
        ["V2.6", "Prioridade por pergunta", "Classificação experimental não compensatória com confiança separada e UNKNOWN preservado."],
        ["V2.7", "Experiência móvel e PWA", "Navegação móvel, legenda integrada, estatísticas visuais e instalação opcional."],
        ["V2.7.1", "Estudo estatístico completo", "Inventário reproduzível do processo, dos produtos, dos resultados e dos limites."],
    ]

    file_types = [
        ["CSV", 254, 854_880_929],
        ["GeoJSON", 161, 613_571_460],
        ["JSON", 109, 97_342_906],
        ["XLSX", 12, 10_861_592],
        ["PNG", 6, 4_780_834],
        ["HTML", 18, 783_023],
        ["TXT", 13, 677_072],
        ["Python", 44, 527_632],
        ["Markdown", 45, 268_185],
        ["JavaScript", 8, 240_248],
        ["CSS", 5, 90_757],
        ["SVG", 2, 4_191],
        ["Webmanifest", 1, 650],
        ["BAT", 4, 352],
        ["Sem extensão", 3, 35_106],
    ]

    key_findings = [
        ["Poços canônicos preservados", metric(effective, "canonical_wells_n"), "poços"],
        ["Coordenadas para revisão", metric(effective, "spatial_coordinate_review_n"), "poços"],
        ["Hidroestratigrafia UNKNOWN", metric(effective, "hydrostrat_unknown_n"), "poços"],
        ["Revisão hidroestratigráfica", metric(effective, "hydrostrat_review_n"), "poços"],
        ["Profundidade total positiva", metric(effective, "vertical_depth_positive_n"), "poços"],
        ["Intervalo captado completo", metric(effective, "vertical_capture_interval_demonstrated_n"), "poços"],
        ["Ensaios com metadados mínimos", metric(effective, "hydraulic_test_minimum_metadata_n"), "poços"],
        ["Transmissividade informada", metric(effective, "hydraulic_transmissivity_reported_n"), "poços"],
        ["Hidroquímica parcial", metric(effective, "hydrochemical_partial_evidence_n"), "poços"],
        ["Evidência datada", metric(effective, "temporal_any_dated_n"), "poços"],
        ["Série temporal completa", metric(effective, "temporal_time_series_demonstrated_n"), "poços"],
        ["Independência demonstrada", metric(effective, "independence_demonstrated_n"), "poços"],
        ["Alertas documentais", metric(effective, "documentary_flagged_wells_n"), "poços"],
        ["Valores objetivamente inválidos", metric(effective, "documentary_invalid_wells_n"), "poços"],
    ]

    selector_inventory = [
        ["Conhecimento efetivo", 5, None, 10, None],
        ["Suficiência por pergunta", 5, 5, None, None],
        ["Estabilidade e sensibilidade", 5, 5, 6, 4],
        ["Independência e redundância", 5, None, 13, None],
        ["Vertical e temporal", 5, None, 15, None],
        ["Estratificação", 5, None, 16, None],
        ["Estudo de escalas", 5, None, 10, None],
        ["Estrutura espacial", 5, None, 6, None],
        ["Malhas de evidência", 5, None, None, None],
        ["Prioridade por pergunta", 5, 5, 8, None],
    ]

    return {
        "schema_version": "PIH_MS_PROJECT_STATISTICS_V271",
        "release": "V2.7.1",
        "scientific_content": "V2.6 preservado",
        "scope_note": "Inventário do pacote V2.7 e das matrizes científicas preservadas na V2.7.1. Registros físicos não equivalem a poços únicos nem a evidências independentes.",
        "headline": {
            "canonical_wells_n": 3877,
            "grid_cells_n": sum(int(row["n_cells"]) for row in scale_rows),
            "support_points_n": int(stability_rows[0]["support_points_n"]),
            "scales_n": len(scale_rows),
            "origins_n": 4,
            "questions_n": len(question_registry),
            "requirements_n": len(requirements),
            "evidence_layers_n": len(evidence_layers),
            "knowledge_dimensions_n": len(dimensions),
            "analytical_modules_n": 10,
        },
        "v27_package_baseline": {
            "files_n": 685,
            "uncompressed_bytes_n": 1_584_064_937,
            "compressed_bytes_n": 132_301_527,
            "csv_files_n": 254,
            "csv_physical_rows_n": 3_839_462,
            "csv_bytes_n": 854_880_929,
            "note": "Contagem física do ZIP auditado V2.7. Inclui vistas analíticas repetidas por escala, pergunta e finalidade de uso.",
        },
        "file_types": [
            {"type": name, "files_n": count, "bytes_n": bytes_n}
            for name, count, bytes_n in file_types
        ],
        "data_architecture": {
            "all_csv": all_csv_summary,
            "all_derived_csv": all_derived_summary,
            "current_derived_csv": current_derived_summary,
            "source_audit_csv_files_n": len(source_audit_csv),
            "source_audit_physical_rows_n": sum(item["rows_n"] for item in source_audit_tables),
            "well_question_pairs_n": 19_385,
            "well_requirement_pairs_n": 151_203,
            "cell_question_pairs_n": 45_145,
            "support_question_pairs_n": 71_420,
            "support_scale_question_pairs_n": 357_100,
            "support_requirement_pairs_n": 557_076,
        },
        "methodology_stages": [
            {"version": version, "name": name, "description": description}
            for version, name, description in methodology_stages
        ],
        "evidence_layers": evidence_layers,
        "evidence_feature_placements_n": sum(item["feature_count"] for item in evidence_layers),
        "evidence_feature_note": "Soma das feições armazenadas nas 12 camadas. Um mesmo poço pode integrar várias evidências e não deve ser contado como novo poço em cada camada.",
        "knowledge_dimensions": dimensions,
        "questions": [
            {
                **row,
                "requirements_n": requirements_by_question[row["question_code"]],
                "summary": next(item for item in question_rows if item["question_code"] == row["question_code"]),
            }
            for row in question_registry
        ],
        "requirement_dimensions": [
            {"dimension": name, "requirements_n": count}
            for name, count in sorted(requirement_dimensions.items())
        ],
        "module_inventory": module_inventory,
        "source_audit_tables": source_audit_tables,
        "scale_effect": scale_rows,
        "stability_cross_scale": stability_rows,
        "priority_totals": dict(priority_totals),
        "confidence_totals": dict(confidence_totals),
        "priority_by_question": priority_by_question,
        "key_findings": [
            {"label": label, "value": value, "unit": unit}
            for label, value, unit in key_findings
        ],
        "interface_inventory": {
            "direct_checkbox_layers_n": checkbox_layers,
            "analytical_modules_n": len(selector_inventory),
            "selector_inventory": [
                {"module": module, "scales_n": scales, "questions_n": questions, "metrics_n": metrics, "origins_n": origins}
                for module, scales, questions, metrics, origins in selector_inventory
            ],
            "sgb_2024_vector_layers_n": len(web_manifest["vector_layers"]),
            "sgb_2024_raster_families_n": len(web_manifest["rasters"]),
        },
        "documentation_inventory": {
            "documented_fields_n": dictionary_n,
            "bibliographic_references_n": bibliography_n,
            "summary_datasets_n": stats["dataset_count"],
            "summary_rows_n": summary_rows_n,
            "summary_column_placements_n": summary_columns_n,
            "well_detail_shards_n": len(shards),
            "wells_in_shards_n": shard_wells,
        },
        "scientific_limits": [
            "Não calcula potencial aquífero.",
            "Não produz prioridade integrada entre as cinco perguntas.",
            "Não usa pesos nem nota numérica compensatória.",
            "Não interpola nem prediz valores entre poços.",
            "Não converte UNKNOWN em zero, ausência física ou prioridade automática.",
            "Não demonstra representatividade territorial dos poços.",
            "Não demonstra independência hidrogeológica entre registros.",
            "Não seleciona uma escala ou origem de malha como definitiva.",
        ],
        "documentation_links": [
            ["Guia de resultados", "guia-resultados.html"],
            ["Prioridade por pergunta", "metodologia-prioridade-investigacao.html"],
            ["Estabilidade e sensibilidade", "metodologia-estabilidade-sensibilidade.html"],
            ["Suficiência por pergunta", "metodologia-suficiencia-pergunta.html"],
            ["Conhecimento efetivo", "metodologia-conhecimento-efetivo.html"],
            ["Independência e redundância", "metodologia-independencia-redundancia.html"],
            ["Vertical e temporal", "metodologia-vertical-temporal.html"],
            ["Estratificação hidrogeológica", "metodologia-estratificacao-hidrogeologica.html"],
            ["Escalas candidatas", "metodologia-escalas-candidatas.html"],
            ["Estrutura espacial", "metodologia-estrutura-espacial.html"],
            ["Malhas de evidência", "metodologia-malhas-evidencia.html"],
            ["Evidências E01 a E12", "metodologia-evidencias.html"],
            ["Dicionário de parâmetros", "dicionario-parametros.html"],
            ["Bibliografia", "bibliografia.html"],
        ],
    }


if __name__ == "__main__":
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    payload = build()
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(OUTPUT)
    print(json.dumps(payload["headline"], ensure_ascii=False, sort_keys=True))
