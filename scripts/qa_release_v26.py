#!/usr/bin/env python3
"""Auditoria final reproduzível da entrega PIH MS V2.6."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "derived" / "research_priority"
WEB = ROOT / "docs" / "data" / "research_priority"
EXPECTED_CELLS = {100: 3763, 150: 2525, 250: 1537, 500: 791, 1000: 413}
EXPECTED_PRIORITY = {0: 32405, 1: 2801, 2: 5448, 3: 4491, 4: 0, 5: 0}
EXPECTED_CONFIDENCE = {0: 32430, 1: 2229, 2: 3783, 3: 5512, 4: 873, 5: 318}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    registry = json.loads((DATA / "research_priority_registry.json").read_text(encoding="utf-8"))
    long = pd.read_csv(DATA / "cell_question_priority_long.csv", low_memory=False)
    requirements = pd.read_csv(DATA / "requirement_action_registry.csv", low_memory=False)
    dictionary = pd.read_csv(ROOT / "methodology" / "DICIONARIO_METRICAS_RESULTADOS_V1.csv", low_memory=False)
    stats = json.loads((ROOT / "docs" / "data" / "statistics" / "statistics_v26.json").read_text(encoding="utf-8"))

    require(registry["wells_n"] == 3877, "Quantidade de poços alterada")
    require(registry["support_points_n"] == 14284, "Quantidade de pontos fixos alterada")
    require(registry["cells_n"] == 9029, "Quantidade total de células alterada")
    require(registry["cell_question_pairs_n"] == 45145, "Quantidade de pares alterada")
    require(registry["requirements_n"] == 39, "Quantidade de requisitos alterada")
    require(registry["questions"] == ["Q01", "Q02", "Q03", "Q04", "Q05"], "Perguntas alteradas")
    require(registry["scales_km2"] == [100, 150, 250, 500, 1000], "Escalas alteradas")
    require(registry["origins"] == ["O00", "OX25", "OY25", "OXY25"], "Origens alteradas")
    require(len(long) == 45145, "CSV longo incompleto")
    require(long["cell_id"].nunique() == 9029, "Células não são únicas no universo esperado")
    require(len(requirements) == 39, "Registro de requisitos incompleto")
    require(len(dictionary) == 1045, "Dicionário mestre não possui 1.045 campos")
    require(len(stats["datasets"]) == 20, "Painel não possui 20 resumos")

    priority = Counter(int(value) for value in long["priority_code"])
    confidence = Counter(int(value) for value in long["confidence_code"])
    require({code: priority.get(code, 0) for code in range(6)} == EXPECTED_PRIORITY, "Distribuição de prioridade alterada")
    require({code: confidence.get(code, 0) for code in range(6)} == EXPECTED_CONFIDENCE, "Distribuição de confiança alterada")

    for column in ["weight_used", "score_used", "integrated_priority_calculated", "potential_calculated", "interpolation_used", "prediction_used"]:
        require(not long[column].fillna(False).astype(bool).any(), f"Proibição violada em {column}")
    require((long.loc[long["priority_code"] == 0, "priority_class"] == "UNKNOWN").all(), "UNKNOWN foi convertido em classe")
    require((long["independence_state"] == "UNKNOWN_NAO_DEMONSTRADA").all(), "Independência foi inferida")
    require((long["representativeness_state"] == "UNKNOWN_NAO_DEMONSTRADA").all(), "Representatividade foi inferida")

    geo_priority = Counter()
    geo_confidence = Counter()
    feature_total = 0
    for scale, expected in EXPECTED_CELLS.items():
        source = DATA / f"research_priority_{scale}km2.geojson"
        mirror = WEB / source.name
        require(source.read_bytes() == mirror.read_bytes(), f"Espelho web divergente em {scale} km²")
        geo = json.loads(source.read_text(encoding="utf-8"))
        require(len(geo["features"]) == expected, f"GeoJSON incompleto em {scale} km²")
        feature_total += len(geo["features"])
        for feature in geo["features"]:
            properties = feature["properties"]
            require(properties["scale_km2"] == scale, f"Escala incorreta em {scale} km²")
            for question in registry["questions"]:
                prefix = question.lower()
                geo_priority[int(properties[f"{prefix}_priority_code"])] += 1
                geo_confidence[int(properties[f"{prefix}_confidence_code"])] += 1
    require(feature_total == 9029, "GeoJSON não preserva 9.029 células")
    require({code: geo_priority.get(code, 0) for code in range(6)} == EXPECTED_PRIORITY, "Prioridade do GeoJSON diverge do CSV")
    require({code: geo_confidence.get(code, 0) for code in range(6)} == EXPECTED_CONFIDENCE, "Confiança do GeoJSON diverge do CSV")

    shards = ROOT / "docs" / "data" / "well_details_shards"
    manifest = json.loads((shards / "manifest.json").read_text(encoding="utf-8"))
    shard_files = sorted(path for path in shards.glob("[0-9][0-9].json"))
    require(len(shard_files) == 64, "Quantidade de fragmentos de ficha alterada")
    require(manifest["shard_count"] == 64 and manifest["well_count"] == 3877, "Manifesto de fichas alterado")
    well_ids = []
    for shard in shard_files:
        well_ids.extend(json.loads(shard.read_text(encoding="utf-8")).keys())
    require(len(well_ids) == 3877 and len(set(well_ids)) == 3877, "Fichas de poço incompletas ou duplicadas")

    index = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
    script = (ROOT / "docs" / "assets" / "js" / "pih.js").read_text(encoding="utf-8")
    method = (ROOT / "docs" / "metodologia-prioridade-investigacao.html").read_text(encoding="utf-8")
    require("V2.6" in index and "help12" in index and "20 resumos" in index, "Ajuda V2.6 incompleta")
    require("navResearchPriority" in script and "researchPriorityGroup" in script, "Navegação V2.6 ausente")
    require("research_priority_" in script and "priority_code" in script and "confidence_code" in script, "Camada V2.6 não registrada")
    require("Prioridade de investigação por pergunta" in method and "UNKNOWN" in method, "Metodologia web V2.6 incompleta")
    require((ROOT / "docs" / "dicionario-parametros.html").read_text(encoding="utf-8").count("<tr>") == 1046, "Página do dicionário incompleta")

    workbook = ROOT.parent.parent / "outputs" / "6b2168c6942b" / "PIH_MS_PRIORIDADE_INVESTIGACAO_POR_PERGUNTA_V1.xlsx"
    require(workbook.exists() and workbook.stat().st_size > 100_000, "Excel científico ausente")

    print("OK V2.6")
    print("9029 células, 45145 pares, 3877 poços, 39 requisitos, 1045 campos e 20 resumos")
    print("Prioridade", dict(EXPECTED_PRIORITY))
    print("Confiança", dict(EXPECTED_CONFIDENCE))


if __name__ == "__main__":
    main()
