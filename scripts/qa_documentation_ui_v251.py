#!/usr/bin/env python3
"""Auditoria reproduzível da documentação integrada PIH MS V2.5.1."""
from __future__ import annotations

from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json
import re
import subprocess
import unicodedata


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EXPECTED_PAGES = {
    "index.html",
    "autoria-direitos.html",
    "bibliografia.html",
    "dicionario-parametros.html",
    "guia-resultados.html",
    "licenca-conteudos.html",
    "metodologia-conhecimento-efetivo.html",
    "metodologia-escalas-candidatas.html",
    "metodologia-estabilidade-sensibilidade.html",
    "metodologia-estratificacao-hidrogeologica.html",
    "metodologia-estrutura-espacial.html",
    "metodologia-evidencias.html",
    "metodologia-independencia-redundancia.html",
    "metodologia-malhas-evidencia.html",
    "metodologia-suficiencia-pergunta.html",
    "metodologia-vertical-temporal.html",
}
EXPECTED_METHODS = {
    "metodologia-estabilidade-sensibilidade.html",
    "metodologia-suficiencia-pergunta.html",
    "metodologia-conhecimento-efetivo.html",
    "metodologia-independencia-redundancia.html",
    "metodologia-vertical-temporal.html",
    "metodologia-estratificacao-hidrogeologica.html",
    "metodologia-escalas-candidatas.html",
    "metodologia-estrutura-espacial.html",
    "metodologia-malhas-evidencia.html",
    "metodologia-evidencias.html",
}


def slug(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value)
    without_marks = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
    return re.sub(r"(^-+|-+$)", "", re.sub(r"[^a-z0-9]+", "-", without_marks.lower())) or "secao"


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.hrefs: list[str] = []
        self.h2_texts: list[str] = []
        self._in_h2 = False
        self._h2_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.append(values["id"])
        if tag == "a" and values.get("href"):
            self.hrefs.append(values["href"])
        if tag == "h2":
            self._in_h2 = True
            self._h2_parts = []

    def handle_data(self, data: str) -> None:
        if self._in_h2:
            self._h2_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "h2" and self._in_h2:
            self.h2_texts.append(" ".join("".join(self._h2_parts).split()))
            self._in_h2 = False


def parse_page(path: Path) -> tuple[str, PageParser]:
    text = path.read_text(encoding="utf-8")
    parser = PageParser()
    parser.feed(text)
    return text, parser


failures: list[str] = []
checks: list[str] = []


def check(condition: bool, message: str) -> None:
    if condition:
        checks.append(message)
    else:
        failures.append(message)


pages = {path.name: path for path in DOCS.glob("*.html")}
check(set(pages) == EXPECTED_PAGES, "16 páginas HTML esperadas")

parsed: dict[str, tuple[str, PageParser]] = {}
for name, path in sorted(pages.items()):
    text, parser = parse_page(path)
    parsed[name] = (text, parser)
    duplicates = [value for value, count in Counter(parser.ids).items() if count > 1]
    check(not duplicates, f"IDs únicos em {name}")
    if name != "index.html":
        check(text.count("assets/css/documentation.css?v=251000") == 1, f"CSS comum único em {name}")
        check(text.count("assets/js/documentation.js?v=251000") == 1, f"JavaScript comum único em {name}")

for source_name, (_, parser) in parsed.items():
    for href in parser.hrefs:
        parts = urlsplit(href)
        if parts.scheme or parts.netloc or href.startswith(("mailto:", "tel:", "javascript:")):
            continue
        raw_path = unquote(parts.path)
        if not raw_path and not parts.fragment:
            continue
        target_name = Path(raw_path).name if raw_path else source_name
        if not target_name.endswith(".html"):
            continue
        check(target_name in pages, f"Destino local de {source_name} existe em {target_name}")
        if target_name not in parsed or not parts.fragment:
            continue
        _, target_parser = parsed[target_name]
        possible = set(target_parser.ids) | {slug(text) for text in target_parser.h2_texts}
        check(unquote(parts.fragment) in possible, f"Âncora de {source_name} existe em {target_name}#{parts.fragment}")

index, index_parser = parsed["index.html"]
for modal_id in ("docsModal", "statsModal", "methodModal", "helpModal", "authorModal", "docViewerModal"):
    check(modal_id in index_parser.ids, f"Modal {modal_id} presente")
for token in (
    "PIH MS V2.5.1",
    "17 resumos vigentes",
    "916 campos",
    "55 referências",
    "Abrir em nova janela",
    "conteúdo científico V2.5",
):
    check(token in index, f"Texto de interface presente em {token}")

stale_tokens = (
    "O painel reúne 13 resumos atuais",
    "Dicionário com 680 campos",
    "Dicionário com 788 campos",
    "Carregando PIH MS V2.4",
    "statistics_v221.json",
    "10.5281/zenodo.21923101",
)
public_text = "\n".join(text for text, _ in parsed.values())
for token in stale_tokens:
    check(token not in public_text, f"Texto desatualizado ausente em {token}")

for name in ("index.html", "autoria-direitos.html"):
    text = parsed[name][0]
    check("10.5281/zenodo.22180863" in text and "V2.2.1" in text, f"DOI delimitado corretamente em {name}")
    check("V2.5.1 ainda não possui" in text, f"Ausência de DOI próprio explícita em {name}")

statistics_path = DOCS / "data/statistics/statistics_v251.json"
check(statistics_path.exists(), "Arquivo estatístico V2.5.1 presente")
statistics = json.loads(statistics_path.read_text(encoding="utf-8"))
check(statistics.get("version") == "2.5.1", "Versão da interface estatística")
check(statistics.get("scientific_content_version") == "2.5", "Versão do conteúdo científico")
check(statistics.get("dataset_count") == len(statistics.get("datasets", [])) == 17, "17 resumos estatísticos")
dataset_ids = {item.get("id") for item in statistics.get("datasets", [])}
check(
    {"stability_cross_scale", "stability_origin", "stability_blockers", "stability_hydro"}.issubset(dataset_ids),
    "Quatro resumos de estabilidade V2.5 presentes",
)

dictionary = parsed["dicionario-parametros.html"][0]
bibliography = parsed["bibliografia.html"][0]
check(dictionary.count("<tr>") - 1 == 916, "916 linhas documentadas no dicionário")
check(bibliography.count('class="ref"') == 55, "55 referências apresentadas")

doc_js_path = DOCS / "assets/js/documentation.js"
app_js_path = DOCS / "assets/js/pih.js"
doc_css_path = DOCS / "assets/css/documentation.css"
doc_js = doc_js_path.read_text(encoding="utf-8")
app_js = app_js_path.read_text(encoding="utf-8")
doc_css = doc_css_path.read_text(encoding="utf-8")
for method in EXPECTED_METHODS:
    check(method in doc_js, f"Método na navegação comum em {method}")
for token in ("setupDocumentationViewer", "openDocumentation", "openRequestedModal", "statistics_v251.json"):
    check(token in app_js, f"Integração do visor presente em {token}")
for token in ("calc(17px * var(--doc-font-scale))", "calc(16.5px * var(--doc-font-scale))", "@media (max-width: 720px)"):
    check(token in doc_css, f"Regra de legibilidade presente em {token}")

subprocess.run(["node", "--check", str(app_js_path)], check=True)
subprocess.run(["node", "--check", str(doc_js_path)], check=True)
checks.append("Sintaxe dos dois arquivos JavaScript")

shard_dir = DOCS / "data/well_details_shards"
manifest = json.loads((shard_dir / "manifest.json").read_text(encoding="utf-8"))
shard_paths = sorted(path for path in shard_dir.glob("*.json") if path.name != "manifest.json")
check(manifest.get("shard_count") == len(shard_paths) == 64, "64 fragmentos de ficha")
actual_counts: dict[str, int] = {}
all_ids: set[str] = set()
for path in shard_paths:
    payload = json.loads(path.read_text(encoding="utf-8"))
    actual_counts[path.name] = len(payload)
    overlap = all_ids.intersection(payload)
    check(not overlap, f"IDs sem duplicação em {path.name}")
    all_ids.update(payload)
check(actual_counts == manifest.get("counts"), "Cardinalidade de cada fragmento")
check(len(all_ids) == manifest.get("well_count") == 3877, "3.877 fichas únicas")

for path in (
    ROOT / "README.md",
    ROOT / "CHANGELOG.md",
    ROOT / "DECISION_LOG.md",
    ROOT / "PLANO_FASE_FINAL_INSTALACAO_MOVEL.md",
):
    check(path.exists() and path.stat().st_size > 500, f"Documento de entrega presente em {path.name}")
check((ROOT / "VERSION").read_text(encoding="utf-8").strip() == "2.5.1", "Arquivo VERSION atualizado")

if failures:
    print("FALHA V2.5.1")
    for failure in failures:
        print(f"- {failure}")
    raise SystemExit(1)

print("OK V2.5.1")
print(f"{len(checks)} verificações aprovadas")
print("16 páginas, 17 resumos, 916 campos, 55 referências, 64 fragmentos e 3877 fichas")
