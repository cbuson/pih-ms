#!/usr/bin/env python3
"""Gera recursos leves e reproduzíveis da interface PIH MS V2.3."""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

STATISTICS = (
    ("effective_global", "Conhecimento efetivo · síntese global", "Conhecimento efetivo", "data/derived/effective_knowledge/effective_knowledge_global_summary.csv"),
    ("effective_scale", "Conhecimento efetivo · cinco escalas", "Conhecimento efetivo", "data/derived/effective_knowledge/effective_knowledge_scale_summary.csv"),
    ("grid_evidence", "Malhas de evidência · cinco escalas", "Malhas de evidência", "data/derived/grid_evidence/grid_scale_summary.csv"),
    ("independence_global", "Independência · síntese global", "Independência", "data/derived/independence_redundancy/independence_global_summary.csv"),
    ("independence_scale", "Independência · cinco escalas", "Independência", "data/derived/independence_redundancy/independence_scale_summary.csv"),
    ("scale_candidate", "Comparação das cinco escalas", "Escalas", "data/derived/scale_study/scale_candidate_summary.csv"),
    ("maup_origin", "Sensibilidade à origem da malha", "Estrutura espacial", "data/derived/spatial_structure/maup_origin_sensitivity_summary.csv"),
    ("maup_variant", "Variantes de origem da malha", "Estrutura espacial", "data/derived/spatial_structure/maup_variant_summary.csv"),
    ("spatial_structure", "Estrutura espacial · cinco escalas", "Estrutura espacial", "data/derived/spatial_structure/spatial_structure_scale_summary.csv"),
    ("stratified", "Estratificação hidrogeológica · cinco escalas", "Estratos", "data/derived/stratified_scale/stratified_scale_summary.csv"),
    ("vertical_temporal", "Documentação vertical e temporal · cinco escalas", "Vertical e temporal", "data/derived/vertical_temporal/vertical_temporal_scale_summary.csv"),
    ("question_global", "Suficiência por pergunta · síntese global", "Suficiência por pergunta", "data/derived/question_sufficiency/question_global_summary.csv"),
    ("question_scale", "Suficiência por pergunta · cinco escalas", "Suficiência por pergunta", "data/derived/question_sufficiency/question_scale_summary.csv"),
)


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = [dict(row) for row in reader]
        return list(reader.fieldnames or []), rows


def build_statistics() -> None:
    datasets = []
    for dataset_id, label, family, source in STATISTICS:
        columns, rows = read_csv(ROOT / source)
        datasets.append(
            {
                "id": dataset_id,
                "label": label,
                "family": family,
                "source": source,
                "columns": columns,
                "rows": rows,
                "row_count": len(rows),
            }
        )
    payload = {
        "project": "PIH MS",
        "version": "2.4",
        "dataset_count": len(datasets),
        "historical_summaries_excluded": [
            "data/derived/independence_redundancy/independence_scale_summary_previous.csv"
        ],
        "note": "Resumos atuais preservados sem agregação adicional. O resumo histórico anterior não é misturado.",
        "datasets": datasets,
    }
    target = DOCS / "data/statistics/statistics_v221.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_well_shards() -> None:
    source = DOCS / "data/well_details.json"
    details = json.loads(source.read_text(encoding="utf-8"))
    shard_count = 64
    shards: list[dict[str, object]] = [dict() for _ in range(shard_count)]
    for well_id, record in details.items():
        shards[int(well_id) % shard_count][well_id] = record
    target_dir = DOCS / "data/well_details_shards"
    target_dir.mkdir(parents=True, exist_ok=True)
    counts = {}
    for index, shard in enumerate(shards):
        name = f"{index:02d}.json"
        (target_dir / name).write_text(
            json.dumps(shard, ensure_ascii=False, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
        counts[name] = len(shard)
    manifest = {
        "version": "2.4",
        "source": "docs/data/well_details.json",
        "rule": "integer well_id modulo 64",
        "shard_count": shard_count,
        "well_count": len(details),
        "counts": counts,
    }
    (target_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def perpendicular_distance(point: list[float], start: list[float], end: list[float]) -> float:
    x, y = point
    x1, y1 = start
    x2, y2 = end
    if start == end:
        return math.hypot(x - x1, y - y1)
    numerator = abs((y2 - y1) * x - (x2 - x1) * y + x2 * y1 - y2 * x1)
    return numerator / math.hypot(y2 - y1, x2 - x1)


def simplify(points: list[list[float]], tolerance: float) -> list[list[float]]:
    if len(points) < 3:
        return points
    distance_max = 0.0
    index = 0
    for current in range(1, len(points) - 1):
        distance = perpendicular_distance(points[current], points[0], points[-1])
        if distance > distance_max:
            index = current
            distance_max = distance
    if distance_max <= tolerance:
        return [points[0], points[-1]]
    left = simplify(points[: index + 1], tolerance)
    right = simplify(points[index:], tolerance)
    return left[:-1] + right


def build_location_icon() -> None:
    boundary = json.loads((DOCS / "data/limite_ms_ibge_2025.geojson").read_text(encoding="utf-8"))
    rings = boundary["features"][0]["geometry"]["coordinates"]
    ring = max(rings, key=len)
    reduced = simplify(ring, 0.025)
    xs = [point[0] for point in reduced]
    ys = [point[1] for point in reduced]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    width, height = max_x - min_x, max_y - min_y
    scale = min(34 / width, 38 / height)
    offset_x = 32 - width * scale / 2
    offset_y = 32 - height * scale / 2
    projected = [
        (offset_x + (x - min_x) * scale, offset_y + (max_y - y) * scale)
        for x, y in reduced
    ]
    path = " ".join(
        ("M" if index == 0 else "L") + f"{x:.2f},{y:.2f}"
        for index, (x, y) in enumerate(projected)
    ) + " Z"
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-labelledby="title desc">
  <title id="title">Minha posição em Mato Grosso do Sul</title>
  <desc id="desc">Ícone circular azul com a forma verde de Mato Grosso do Sul e ponto de localização amarelo.</desc>
  <circle cx="32" cy="32" r="29" fill="#006CB7" stroke="#ffffff" stroke-width="3"/>
  <path d="{path}" fill="#009444" stroke="#ffffff" stroke-width="1.7" stroke-linejoin="round"/>
  <circle cx="32" cy="32" r="5.2" fill="#FFDD00" stroke="#ffffff" stroke-width="2.2"/>
  <circle cx="32" cy="32" r="1.7" fill="#006CB7"/>
</svg>
'''
    target = DOCS / "assets/img/mi-posicao-ms.svg"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(svg, encoding="utf-8")


def install_agpl_text() -> None:
    """Extrai a cópia integral da AGPL v3 já instalada no ambiente."""
    source = Path("/usr/share/doc/ocrmypdf/copyright")
    lines = source.read_text(encoding="utf-8").splitlines()[177:838]
    cleaned = []
    for line in lines:
        if line == " .":
            cleaned.append("")
        elif line.startswith(" "):
            cleaned.append(line[1:])
        else:
            cleaned.append(line)
    license_text = "\n".join(cleaned).rstrip() + "\n"
    if "GNU AFFERO GENERAL PUBLIC LICENSE" not in license_text or "END OF TERMS AND CONDITIONS" not in license_text:
        raise RuntimeError("Texto AGPL v3 incompleto no arquivo de origem")
    (ROOT / "LICENSE").write_text(license_text, encoding="utf-8")
    (DOCS / "licenca-software.txt").write_text(license_text, encoding="utf-8")


if __name__ == "__main__":
    build_statistics()
    build_well_shards()
    build_location_icon()
    install_agpl_text()
    print("OK estatísticas, 64 fragmentos de ficha, ícone de localização e AGPL v3")
