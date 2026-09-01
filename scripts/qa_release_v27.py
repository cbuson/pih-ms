#!/usr/bin/env python3
"""Auditoria reproduzível da interface PIH MS V2.7."""
from __future__ import annotations

import hashlib
import json
import struct
import subprocess
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SCIENCE_PREFIXES = ("data/", "docs/data/", "methodology/")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


class IndexAudit(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.controls: dict[str, dict[str, str | None]] = {}
        self.modal_targets: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        element_id = values.get("id")
        if element_id:
            self.ids.append(element_id)
            self.controls[element_id] = values
        if values.get("data-modal"):
            self.modal_targets.append(str(values["data-modal"]))


def verify_science() -> int:
    manifest = ROOT / "SHA256SUMS_V26.txt"
    require(manifest.exists(), "Manifesto científico V2.6 ausente")
    checked = 0
    for line in manifest.read_text(encoding="utf-8").splitlines():
        expected, relative = line.split("  ", 1)
        if not relative.startswith(SCIENCE_PREFIXES):
            continue
        path = ROOT / relative
        require(path.is_file(), f"Arquivo científico ausente em {relative}")
        require(digest(path) == expected, f"Arquivo científico alterado em {relative}")
        checked += 1
    require(checked > 300, "Manifesto científico incompleto")
    return checked


def png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    require(data[:8] == b"\x89PNG\r\n\x1a\n", f"PNG inválido em {path.name}")
    return struct.unpack(">II", data[16:24])


def main() -> None:
    require((ROOT / "VERSION").read_text(encoding="utf-8").strip() == "2.7.0-pwa", "VERSION incorreta")
    index = (DOCS / "index.html").read_text(encoding="utf-8")
    parser = IndexAudit()
    parser.feed(index)
    duplicates = [element_id for element_id, count in Counter(parser.ids).items() if count > 1]
    require(not duplicates, f"IDs duplicados em index.html {duplicates}")

    required_ids = {
        "activeLayersToggle", "activeLayersSheet", "mapLegendPanel", "mapVisibleLayersPanel",
        "legendCard", "activeLayersList", "statsVisualPanel", "statsTablesPanel",
        "statsVisualDashboard", "pwaModal", "pwaInstallButton", "pwaStatus",
    }
    require(required_ids.issubset(parser.controls), f"Controles ausentes {sorted(required_ids - parser.controls.keys())}")
    require("mobileLegendToggle" not in parser.controls, "Botão antigo de legenda ainda presente")
    require(parser.controls["activeLayersToggle"].get("aria-controls") == "activeLayersSheet", "Relação acessível da legenda incorreta")
    require(parser.modal_targets.count("helpModal") >= 3, "Ajuda não está disponível na barra azul e nos menus")
    require(parser.modal_targets.count("authorModal") >= 4, "Informação não está disponível na barra azul e nos menus")
    require("pih-v27.css?v=270000" in index, "CSS V2.7 não carregado")
    require("pih-stats-visual.js?v=270000" in index, "Estatísticas visuais não carregadas")
    require("pih-pwa.js?v=270000" in index, "Controlador PWA não carregado")
    require("manifest.webmanifest" in index, "Manifesto PWA não ligado")

    css = (DOCS / "assets/css/pih-v27.css").read_text(encoding="utf-8")
    visual_js = (DOCS / "assets/js/pih-visual-controls.js").read_text(encoding="utf-8")
    stats_js = (DOCS / "assets/js/pih-stats-visual.js").read_text(encoding="utf-8")
    pwa_js = (DOCS / "assets/js/pih-pwa.js").read_text(encoding="utf-8")
    service_worker = (DOCS / "service-worker.js").read_text(encoding="utf-8")
    require("flex-direction: row" in css and ".map-tools" in css, "Ferramentas horizontais ausentes")
    require("data-map-display-tab" in visual_js and "showTab('legend')" in visual_js, "Legenda integrada incompleta")
    require("statistics_v26.json" in stats_js and "20 tabelas" in stats_js, "Visão estatística não está ligada aos resumos")
    require("beforeinstallprompt" in pwa_js and "appinstalled" in pwa_js, "Fluxo de instalação PWA incompleto")
    require("scientificData" in service_worker and "startsWith('data/')" in service_worker, "Dados científicos não estão excluídos do cache automático")

    manifest = json.loads((DOCS / "manifest.webmanifest").read_text(encoding="utf-8"))
    require(manifest["display"] == "standalone", "Modo PWA incorreto")
    require(manifest["start_url"] == "./index.html" and manifest["scope"] == "./", "Escopo PWA incorreto")
    require(png_size(DOCS / "assets/img/pih-ms-icon-192.png") == (192, 192), "Ícone 192 incorreto")
    require(png_size(DOCS / "assets/img/pih-ms-icon-512.png") == (512, 512), "Ícone 512 incorreto")

    statistics = json.loads((DOCS / "data/statistics/statistics_v26.json").read_text(encoding="utf-8"))
    require(statistics["dataset_count"] == 20 and len(statistics["datasets"]) == 20, "Quantidade de resumos alterada")
    by_id = {item["id"]: item for item in statistics["datasets"]}
    grids = by_id["grid_evidence"]["rows"]
    questions = by_id["question_global"]["rows"]
    priority = by_id["research_priority_summary"]["rows"]
    require(sum(int(row["n_cells"]) for row in grids) == 9029, "Quantidade de células alterada")
    require(all(int(row["direct_evidence_n"]) + int(row["unknown_evidence_n"]) == 3877 for row in questions), "Denominador das perguntas alterado")
    priority_fields = [
        "priority_unknown_n", "priority_p1_critical_n", "priority_p2_high_n",
        "priority_p3_moderate_n", "priority_p4_low_n", "priority_p5_documentary_sufficiency_n",
    ]
    require(sum(sum(int(row[field]) for field in priority_fields) for row in priority) == 45145, "Classes de prioridade não fecham")
    require(sum(int(row["priority_unknown_n"]) for row in priority) == 32405, "UNKNOWN de prioridade alterado")

    for script in ["pih.js", "pih-mobile.js", "pih-visual-controls.js", "pih-stats-visual.js", "pih-pwa.js"]:
        subprocess.run(["node", "--check", str(DOCS / "assets/js" / script)], check=True, capture_output=True, text=True)
    subprocess.run(["node", "--check", str(DOCS / "service-worker.js")], check=True, capture_output=True, text=True)

    science_files = verify_science()
    print("OK V2.7 EXPERIÊNCIA MÓVEL, ESTATÍSTICAS E PWA")
    print(f"165 IDs únicos, 20 resumos e {science_files} arquivos científicos preservados")
    print("Legenda unificada, ferramentas horizontais e instalação limitada ao shell verificadas")


if __name__ == "__main__":
    main()
