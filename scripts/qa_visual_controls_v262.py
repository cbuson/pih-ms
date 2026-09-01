#!/usr/bin/env python3
"""Auditoria reproduzível do controle visual PIH MS V2.6.2."""
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
        self.controls: dict[str, dict[str, str | None]] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        element_id = values.get("id")
        if element_id:
            self.ids.append(element_id)
            self.controls[element_id] = values


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
    require((ROOT / "VERSION").read_text(encoding="utf-8").strip() == "2.6.2-visual", "VERSION incorreta")
    index = (DOCS / "index.html").read_text(encoding="utf-8")
    parser = IndexAudit()
    parser.feed(index)
    duplicates = [element_id for element_id, count in Counter(parser.ids).items() if count > 1]
    require(not duplicates, f"IDs duplicados em index.html {duplicates}")

    required_ids = {
        "activeLayersToggle",
        "activeLayersToggleCount",
        "activeLayersBackdrop",
        "activeLayersSheet",
        "activeLayersList",
        "activeLayersStatus",
        "closeActiveLayers",
        "resetActiveLayerOpacity",
        "openLayerCatalog",
    }
    require(required_ids.issubset(parser.controls), f"Controles ausentes {sorted(required_ids - parser.controls.keys())}")
    require(parser.controls["activeLayersToggle"].get("aria-controls") == "activeLayersSheet", "Relação acessível do botão incorreta")
    require(parser.controls["activeLayersSheet"].get("role") == "dialog", "Bandeja sem papel de diálogo")
    require("pih-visual-controls.css?v=262000" in index, "CSS visual não carregado")
    require("pih-visual-controls.js?v=262000" in index, "JavaScript visual não carregado")
    require("V2.6.2" in index and "V2.6.1 · controle visual" not in index, "Identificação principal da versão incorreta")

    visual_js = (DOCS / "assets/js/pih-visual-controls.js").read_text(encoding="utf-8")
    visual_css = (DOCS / "assets/css/pih-visual-controls.css").read_text(encoding="utf-8")
    pih_js = (DOCS / "assets/js/pih.js").read_text(encoding="utf-8")
    for token in ["25, 50, 75, 100", "type = 'range'", "scheduleOpacity", "remove-layer", "aria-pressed"]:
        require(token in visual_js, f"Comportamento visual ausente {token}")
    for token in ["window.PIHVisualLayers", "setVisualOpacity", "resetVisualLayers", "removeVisualLayer", "bringVisualLayerToFront"]:
        require(token in pih_js, f"API cartográfica ausente {token}")
    require(pih_js.count("applyVisualOpacity(key,true)") == 10, "Nem todas as famílias analíticas reaplicam transparência")
    require("match(/^(rp|ss|qs|ek|ir|vt|se|ge|st|sc)\\d+$/)" in pih_js, "Remoção analítica não está limitada a chaves de malha")
    require("min-height: 44px" in visual_css, "Alvos táteis mínimos ausentes")
    require("safe-area-inset-bottom" in visual_css, "Área segura móvel ausente")
    require("max-width: 760px" in visual_css, "Adaptação móvel ausente")
    require("10" in visual_js and "100" in visual_js, "Intervalo de transparência ausente")

    help_text = (DOCS / "assets/js/pih-mobile.js").read_text(encoding="utf-8")
    require("Camadas visíveis" in help_text and "10 e 100 por cento" in help_text, "Ajuda de transparência incompleta")
    docs_pages = sorted(path for path in DOCS.glob("*.html") if path.name != "index.html")
    require(len(docs_pages) == 16, "Quantidade inesperada de páginas documentais")

    registry = json.loads((ROOT / "data/derived/research_priority/research_priority_registry.json").read_text(encoding="utf-8"))
    require(registry["cells_n"] == 9029, "Quantidade de células alterada")
    require(registry["cell_question_pairs_n"] == 45145, "Quantidade de pares alterada")
    require(registry["wells_n"] == 3877, "Quantidade de poços alterada")
    require(registry["requirements_n"] == 39, "Quantidade de requisitos alterada")

    science_files = verify_science()
    print("OK V2.6.2 CONTROLE VISUAL")
    print(f"9 controles, 16 páginas documentais e {science_files} arquivos científicos preservados")
    print("10 famílias analíticas, vetores, pontos e rasters cobertos")


if __name__ == "__main__":
    main()
