#!/usr/bin/env python3
"""Atualiza os resumos estatísticos e os recursos de interface da V2.6."""
from __future__ import annotations

from pathlib import Path
import json

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/data/statistics/statistics_v251.json"
OUT = ROOT / "docs/data/statistics/statistics_v26.json"
DERIVED = ROOT / "data/derived/ui_support/statistics_v26.json"


def serializable(value: object) -> object:
    if pd.isna(value):
        return ""
    if isinstance(value, (bool, int, float, str)):
        return value
    if hasattr(value, "item"):
        return value.item()
    return str(value)


def dataset(identifier: str, label: str, family: str, source: str) -> dict[str, object]:
    frame = pd.read_csv(ROOT / source, low_memory=False)
    columns = frame.columns.tolist()
    rows = [{column: serializable(row[column]) for column in columns} for _, row in frame.iterrows()]
    return {
        "id": identifier,
        "label": label,
        "family": family,
        "source": source,
        "columns": columns,
        "rows": rows,
        "row_count": len(rows),
    }


def main() -> None:
    bundle = json.loads(SOURCE.read_text(encoding="utf-8"))
    additions = [
        dataset(
            "research_priority_summary",
            "Prioridade por escala e pergunta",
            "Prioridade por pergunta",
            "data/derived/research_priority/priority_scale_question_summary.csv",
        ),
        dataset(
            "research_priority_classes",
            "Classes de prioridade P1 a P5",
            "Prioridade por pergunta",
            "data/derived/research_priority/priority_class_registry.csv",
        ),
        dataset(
            "research_confidence_classes",
            "Classes de confiança C1 a C5",
            "Prioridade por pergunta",
            "data/derived/research_priority/confidence_class_registry.csv",
        ),
    ]
    bundle["version"] = "2.6-experimental"
    bundle["scientific_content_version"] = "2.6-experimental"
    bundle["datasets"] = bundle["datasets"] + additions
    bundle["dataset_count"] = len(bundle["datasets"])
    bundle["note"] = "Vinte resumos vigentes. Prioridade e confiança permanecem separadas e não existe prioridade integrada."
    text = json.dumps(bundle, ensure_ascii=False, indent=2) + "\n"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    DERIVED.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    DERIVED.write_text(text, encoding="utf-8")
    print(f"OK statistics_v26.json · {len(bundle['datasets'])} resumos")


if __name__ == "__main__":
    main()
