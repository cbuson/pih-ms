#!/usr/bin/env python3
"""Auditoria reproduzível da navegação móvel PIH MS V2.6.1."""
from __future__ import annotations

import hashlib
import json
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
        self.in_mobile_nav = False
        self.mobile_labels: list[str] = []
        self.in_mobile_button = False
        self.button_text: list[str] = []
        self.mobile_modal_actions: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        element_id = values.get("id")
        if element_id:
            self.ids.append(element_id)
        if element_id == "mobileBottomNav":
            self.in_mobile_nav = True
        if self.in_mobile_nav and tag == "button":
            self.in_mobile_button = True
            self.button_text = []
        action = values.get("data-mobile-action")
        modal = values.get("data-modal")
        if action and modal:
            self.mobile_modal_actions[action] = modal

    def handle_data(self, data: str) -> None:
        if self.in_mobile_button and data.strip():
            self.button_text.append(data.strip())

    def handle_endtag(self, tag: str) -> None:
        if self.in_mobile_button and tag == "button":
            self.mobile_labels.append(" ".join(self.button_text))
            self.in_mobile_button = False
        if self.in_mobile_nav and tag == "nav":
            self.in_mobile_nav = False


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


def main() -> None:
    require((ROOT / "VERSION").read_text(encoding="utf-8").strip() == "2.6.1-mobile", "VERSION incorreta")
    index_path = DOCS / "index.html"
    index = index_path.read_text(encoding="utf-8")
    parser = IndexAudit()
    parser.feed(index)

    duplicates = [element_id for element_id, count in Counter(parser.ids).items() if count > 1]
    require(not duplicates, f"IDs duplicados em index.html {duplicates}")
    for element_id in [
        "map",
        "sidePanel",
        "rightPanel",
        "mobileBottomNav",
        "mobileMoreSheet",
        "mobileMoreBackdrop",
        "mobileLegendToggle",
        "mobileViewMap",
        "mobileViewMapFromFicha",
    ]:
        require(element_id in parser.ids, f"Controle móvel ausente {element_id}")

    require(len(parser.mobile_labels) == 5, "A barra inferior não possui cinco destinos")
    for label in ["Mapa", "Camadas", "Prioridade", "Poço", "Mais"]:
        require(any(label in item for item in parser.mobile_labels), f"Destino móvel ausente {label}")
    require(
        parser.mobile_modal_actions
        == {
            "statistics": "statsModal",
            "documentation": "docsModal",
            "help": "helpModal",
            "information": "authorModal",
        },
        "Abertura móvel dos painéis documentais está incompleta",
    )
    require("assets/css/pih-mobile.css?v=261000" in index, "CSS móvel não está carregado")
    require("assets/js/pih-mobile.js?v=261000" in index, "JavaScript móvel não está carregado")

    mobile_js = (DOCS / "assets" / "js" / "pih-mobile.js").read_text(encoding="utf-8")
    mobile_css = (DOCS / "assets" / "css" / "pih-mobile.css").read_text(encoding="utf-8")
    require("collapseGroupsForMobile" in mobile_js and "showMap();" in mobile_js, "Primeira tela móvel não está definida")
    require("openPriority" in mobile_js and "openWellSearch" in mobile_js, "Atalhos móveis incompletos")
    require("max-width: 760px" in mobile_css, "Breakpoint móvel ausente")
    require("min-height: 44px" in mobile_css, "Alvo tátil mínimo ausente")
    require("#zoomIn" in mobile_css and "#zoomOut" in mobile_css, "Zoom móvel não foi simplificado")
    require("body.mobile-legend-open .legend-card" in mobile_css, "Legenda recolhível ausente")
    require("100dvh" in mobile_css and "safe-area-inset-bottom" in mobile_css, "Altura ou área segura móvel ausente")
    require("color-scheme: only light" in mobile_css, "Proteção da identidade visual ausente")

    docs_pages = sorted(path for path in DOCS.glob("*.html") if path.name != "index.html")
    require(len(docs_pages) == 16, "Quantidade inesperada de páginas documentais")
    for page in docs_pages:
        content = page.read_text(encoding="utf-8")
        require("assets/css/documentation.css" in content, f"CSS documental ausente em {page.name}")
        require("assets/js/documentation.js" in content, f"Navegação documental ausente em {page.name}")
    documentation_js = (DOCS / "assets" / "js" / "documentation.js").read_text(encoding="utf-8")
    require("table-wrap" in documentation_js, "Proteção móvel das tabelas ausente")

    registry = json.loads((ROOT / "data" / "derived" / "research_priority" / "research_priority_registry.json").read_text(encoding="utf-8"))
    require(registry["cells_n"] == 9029, "Quantidade de células alterada")
    require(registry["cell_question_pairs_n"] == 45145, "Quantidade de pares alterada")
    require(registry["wells_n"] == 3877, "Quantidade de poços alterada")
    require(registry["requirements_n"] == 39, "Quantidade de requisitos alterada")

    science_files = verify_science()
    print("OK V2.6.1 MOBILE")
    print(f"5 destinos, 16 páginas documentais e {science_files} arquivos científicos preservados")
    print("9029 células, 45145 pares, 3877 poços, 39 requisitos e 20 resumos")


if __name__ == "__main__":
    main()
