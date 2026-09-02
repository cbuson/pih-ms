#!/usr/bin/env python3
"""Release checks for PIH MS V2.7.1."""

from __future__ import annotations

import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_ZIP = ROOT.parents[1] / "restored/pih-ms-v2.7-pwa-estatisticas-visuais.zip"
ERRORS: list[str] = []


def check(condition: bool, message: str) -> None:
    if not condition:
        ERRORS.append(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def scientific_integrity() -> tuple[int, int]:
    checked_files = 0
    checked_bytes = 0
    with zipfile.ZipFile(BASE_ZIP) as archive:
        prefix = archive.namelist()[0].split("/", 1)[0] + "/"
        for info in archive.infolist():
            if info.is_dir() or not info.filename.startswith(prefix):
                continue
            relative = info.filename[len(prefix):]
            if not (
                relative.startswith("data/")
                or relative.startswith("methodology/")
                or relative.startswith("docs/data/")
            ):
                continue
            path = ROOT / relative
            check(path.is_file(), f"Arquivo científico ausente: {relative}")
            if not path.is_file():
                continue
            current = path.read_bytes()
            original = archive.read(info.filename)
            check(sha256_bytes(current) == sha256_bytes(original), f"Arquivo científico alterado: {relative}")
            checked_files += 1
            checked_bytes += len(current)
    return checked_files, checked_bytes


def main() -> int:
    check(BASE_ZIP.is_file(), "ZIP V2.7 de referência ausente")
    if not BASE_ZIP.is_file():
        print("FAIL\n" + "\n".join(ERRORS))
        return 1

    required = [
        "docs/index.html",
        "docs/estatisticas-estudo-completo.html",
        "docs/data/statistics/project_statistics_v271.json",
        "docs/assets/js/pih-stats-full.js",
        "docs/assets/css/pih-v271.css",
        "docs/assets/img/pih-ms-icon.svg",
        "docs/assets/img/pih-ms-icon-192.png",
        "docs/assets/img/pih-ms-icon-512.png",
        "scripts/build_project_statistics_v271.py",
    ]
    for relative in required:
        check((ROOT / relative).is_file(), f"Arquivo obrigatório ausente: {relative}")

    index = (ROOT / "docs/index.html").read_text(encoding="utf-8")
    ids = re.findall(r'\bid=["\']([^"\']+)["\']', index)
    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    check(not duplicates, f"IDs duplicados no index: {duplicates}")
    check(index.count('data-stats-view=') == 3, "O modal deve ter três vistas estatísticas")
    check('id="statsFullPanel"' in index, "Painel Estudo completo ausente")
    check('assets/js/pih-stats-full.js?v=271000' in index, "Script do estudo completo ausente")
    check('assets/css/pih-v271.css?v=271000' in index, "CSS V2.7.1 ausente")
    check('V2.7.1' in index, "Versão V2.7.1 ausente do visor")

    svg = (ROOT / "docs/assets/img/pih-ms-icon.svg").read_text(encoding="utf-8")
    check("Gota de água dentro de um hexágono" in svg, "Descrição do novo ícone ausente")
    check('M256 34 448 145v222L256 478 64 367V145Z' in svg, "Geometria hexagonal ausente")

    payload = json.loads((ROOT / "docs/data/statistics/project_statistics_v271.json").read_text(encoding="utf-8"))
    expected_headline = {
        "canonical_wells_n": 3877,
        "grid_cells_n": 9029,
        "support_points_n": 14284,
        "scales_n": 5,
        "origins_n": 4,
        "questions_n": 5,
        "requirements_n": 39,
        "evidence_layers_n": 12,
        "knowledge_dimensions_n": 9,
        "analytical_modules_n": 10,
    }
    check(payload.get("headline") == expected_headline, "Indicadores estruturais divergentes")
    check(payload["v27_package_baseline"]["csv_physical_rows_n"] == 3_839_462, "Contagem física dos CSV divergente")
    check(payload["data_architecture"]["current_derived_csv"]["physical_rows_n"] == 2_006_817, "Registros derivados atuais divergentes")
    check(payload["evidence_feature_placements_n"] == 27_598, "Feições das evidências divergentes")
    check(payload["priority_totals"]["priority_unknown_n"] == 32_405, "Prioridade UNKNOWN divergente")
    check(payload["priority_totals"]["priority_p1_critical_n"] == 2_801, "Prioridade P1 divergente")
    check(payload["priority_totals"]["priority_p2_high_n"] == 5_448, "Prioridade P2 divergente")
    check(payload["priority_totals"]["priority_p3_moderate_n"] == 4_491, "Prioridade P3 divergente")
    check(payload["documentation_inventory"]["documented_fields_n"] == 1_045, "Dicionário divergente")
    check(payload["documentation_inventory"]["bibliographic_references_n"] == 55, "Bibliografia divergente")
    check(payload["documentation_inventory"]["wells_in_shards_n"] == 3_877, "Fichas fragmentadas incompletas")

    service_worker = (ROOT / "docs/service-worker.js").read_text(encoding="utf-8")
    check("pih-ms-shell-v271000" in service_worker, "Cache PWA sem nova versão")
    check("pih-stats-full.js?v=271000" in service_worker, "Script estatístico fora do shell")
    check("scientificData" in service_worker and "return;" in service_worker, "Proteção do cache científico ausente")

    doc_pages = sorted((ROOT / "docs").glob("*.html"))
    unified_pages = [path for path in doc_pages if "documentation.js" in path.read_text(encoding="utf-8")]
    check(len(unified_pages) == 17, f"Páginas documentais unificadas: {len(unified_pages)}")
    for path in unified_pages:
        html = path.read_text(encoding="utf-8")
        check("documentation.js?v=271000" in html, f"Cache documental antigo em {path.name}")

    checked_files, checked_bytes = scientific_integrity()
    check(checked_files == 522, f"Arquivos científicos comparados: {checked_files}, esperado 522")

    if ERRORS:
        print("FAIL")
        for error in ERRORS:
            print(f"- {error}")
        return 1

    print("PASS")
    print(f"scientific_files_identical={checked_files}")
    print(f"scientific_bytes_identical={checked_bytes}")
    print(f"documentation_pages={len(unified_pages)}")
    print(f"index_ids={len(ids)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
