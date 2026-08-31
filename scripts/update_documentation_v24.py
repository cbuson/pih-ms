#!/usr/bin/env python3
"""Atualiza documentação web da matriz V2.4."""
from __future__ import annotations

from html import escape
from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


BASE_STYLE = """
body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#eef4f8;color:#183448;line-height:1.6}
header{background:linear-gradient(125deg,#083f67,#0a7890);color:#fff;padding:30px 5vw}
main{max-width:1180px;margin:auto;padding:28px 5vw 60px}.card{background:#fff;border-radius:16px;padding:22px;margin:0 0 20px;box-shadow:0 5px 20px #163f5b18}
h2{color:#0b456e}.rule{background:#f2f8fb;border-left:5px solid #0a7890;padding:14px 16px;border-radius:8px}.danger{border-color:#b65c34;background:#fff6ed}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}.metric{background:#eef6fa;border-left:4px solid #0a7890;padding:14px;border-radius:9px}.metric b{font-size:1.35rem;color:#0b456e;display:block}
table{border-collapse:collapse;width:100%;font-size:14px}th,td{text-align:left;padding:9px;border-bottom:1px solid #d8e3eb;vertical-align:top}th{background:#e8f1f6;color:#0b456e;position:sticky;top:0}.table-wrap{overflow:auto;max-height:68vh;border:1px solid #d8e3eb;border-radius:10px}
.badge{display:inline-block;font-size:12px;font-weight:700;background:#dcecf6;color:#0b456e;border-radius:999px;padding:4px 8px;margin-right:8px}.future{background:#f5ead9;color:#7c4d10}.critical{background:#f3e0df;color:#7b2f2a}
.ref{padding:15px 0;border-top:1px solid #d8e3eb}.ref:first-child{border-top:0}.support{color:#536d7e;font-size:14px;margin-top:6px}a{color:#0b5f97}.search{width:100%;box-sizing:border-box;padding:12px;border:1px solid #afc4d2;border-radius:9px;font:inherit;margin:8px 0 14px}
code{background:#edf2f5;padding:2px 5px;border-radius:4px}
"""


def page(title: str, header: str, subtitle: str, content: str) -> str:
    return (
        "<!doctype html><html lang=\"pt-BR\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        f"<title>{escape(title)}</title><style>{BASE_STYLE}</style></head><body>"
        f"<header><small>PIH MS · V2.4</small><h1>{escape(header)}</h1><p>{escape(subtitle)}</p></header>"
        f"<main>{content}</main></body></html>"
    )


def methodology_page() -> None:
    questions = pd.read_csv(ROOT / "data/derived/question_sufficiency/question_registry.csv")
    requirements = pd.read_csv(ROOT / "data/derived/question_sufficiency/question_requirement_matrix.csv")
    summary = pd.read_csv(ROOT / "data/derived/question_sufficiency/question_global_summary.csv")
    question_cards = []
    for question in questions.itertuples(index=False):
        req = requirements[requirements.question_code == question.question_code]
        items = "".join(
            f"<li><code>{escape(str(row.requirement_code))}</code> {escape(str(row.evaluation_rule))}</li>"
            for row in req.itertuples(index=False)
        )
        question_cards.append(
            f"<section class=\"card\"><h2>{escape(question.question_code)} · {escape(question.question_name)}</h2>"
            f"<p>{escape(question.question_objective)}</p><div class=\"rule\"><b>Evidência direta</b><br>{escape(question.direct_evidence_definition)}</div>"
            f"<h3>Requisitos críticos</h3><ol>{items}</ol><p>{escape(question.cell_interpretation)}</p></section>"
        )
    metrics = "".join(
        f"<div class=\"metric\"><b>{escape(row.question_code)}</b>{escape(row.question_name)}<br>"
        f"Evidência direta {int(row.direct_evidence_n):,}<br>Mínimo documental {int(row.minimum_documentary_n):,}</div>".replace(",", ".")
        for row in summary.itertuples(index=False)
    )
    content = f"""
<section class="card"><h2>Regra central</h2><div class="rule danger"><b>SUFICIÊNCIA DOCUMENTAL LOCAL ≠ REPRESENTATIVIDADE TERRITORIAL</b></div><p>Cada pergunta possui requisitos próprios. Todos os requisitos críticos precisam estar demonstrados no mesmo registro. Não há pesos, score ou quantidade mínima universal de poços.</p></section>
<section class="card"><h2>Resultados globais</h2><div class="grid">{metrics}</div><p>Nenhum poço atende ao mínimo completo nas regras conservadoras atuais. Isso não invalida a evidência parcial. Expõe os requisitos ainda não demonstrados.</p></section>
{''.join(question_cards)}
<section class="card"><h2>Leitura das células</h2><p>Célula sem poço permanece UNKNOWN. Célula com evidência parcial não é classificada como conhecida. Mesmo quando existir um registro mínimo local, a representatividade continuará separada e dependerá de independência e desenho amostral.</p></section>
<section class="card"><h2>Documentação completa</h2><p><a href="guia-resultados.html#suficiencia-pergunta">Guia de leitura</a> · <a href="dicionario-parametros.html">Dicionário com 788 campos</a> · <a href="bibliografia.html">Bibliografia completa</a></p></section>
"""
    (DOCS / "metodologia-suficiencia-pergunta.html").write_text(
        page("PIH MS V2.4 · suficiência por pergunta", "Suficiência por pergunta", "Cinco perguntas, requisitos não compensatórios e representatividade mantida separada", content),
        encoding="utf-8",
    )


def bibliography_page() -> None:
    bibliography = pd.read_csv(ROOT / "methodology/BIBLIOGRAFIA_MASTER_V1.csv").fillna("")
    sections = []
    for group, frame in bibliography.groupby("group", sort=False):
        articles = []
        for row in frame.itertuples(index=False):
            status = str(row.status)
            cls = " future" if "NÃO IMPLEMENT" in status or "ANTECEDENTE" in status else " critical" if "CRÍT" in status else ""
            articles.append(
                f"<article class=\"ref\"><span class=\"badge{cls}\">{escape(status)}</span>"
                f"<b>{escape(str(row.citation))}</b><div class=\"support\">Função no PIH MS · {escape(str(row.supports))}</div>"
                f"<div><a href=\"{escape(str(row.url), quote=True)}\" target=\"_blank\" rel=\"noopener\">Abrir fonte</a></div></article>"
            )
        sections.append(f"<section class=\"card\"><h2>{escape(str(group))}</h2>{''.join(articles)}</section>")
    content = (
        "<section class=\"card\"><h2>Como ler</h2><div class=\"rule\"><b>Método citado ≠ método implementado.</b> "
        "Cada referência informa seu estado e sua função. A V2.4 acrescenta a referência normativa brasileira usada na separação entre resultado químico parcial e monitoramento de qualidade.</div></section>"
        + "".join(sections)
    )
    (DOCS / "bibliografia.html").write_text(
        page("Bibliografia completa PIH MS V2.4", "Bibliografia completa", f"{len(bibliography)} referências classificadas por função e estado de uso", content),
        encoding="utf-8",
    )


def dictionary_page() -> None:
    dictionary = pd.read_csv(ROOT / "methodology/DICIONARIO_METRICAS_RESULTADOS_V1.csv").fillna("")
    columns = ["field", "modules", "definition", "formula_or_rule", "unit", "how_to_read", "does_not_mean", "unknown_rule"]
    header = "".join(f"<th>{escape(column)}</th>" for column in columns)
    rows = "".join(
        "<tr>" + "".join(f"<td>{escape(str(row[column]))}</td>" for column in columns) + "</tr>"
        for _, row in dictionary.iterrows()
    )
    content = f"""
<section class="card"><h2>Pesquisar campos</h2><p>Cada campo possui definição, regra, unidade, leitura permitida, leitura proibida e tratamento de UNKNOWN.</p><input class="search" id="q" type="search" placeholder="Campo, módulo, fórmula ou regra"><div id="count">{len(dictionary)} campos visíveis de {len(dictionary)}</div></section>
<section class="card"><div class="table-wrap"><table id="tbl"><thead><tr>{header}</tr></thead><tbody>{rows}</tbody></table></div><p><a href="data/dicionario_metricas_resultados_v1.csv" download>Baixar CSV completo</a></p></section>
<script>const q=document.getElementById('q'),rows=[...document.querySelectorAll('#tbl tbody tr')],count=document.getElementById('count');function f(){{const s=q.value.trim().toLowerCase();let n=0;rows.forEach(r=>{{const ok=!s||r.innerText.toLowerCase().includes(s);r.style.display=ok?'':'none';if(ok)n++}});count.textContent=n+' campos visíveis de {len(dictionary)}';}}q.addEventListener('input',f);</script>
"""
    (DOCS / "dicionario-parametros.html").write_text(
        page("Dicionário de parâmetros PIH MS V2.4", "Dicionário exaustivo", f"{len(dictionary)} campos documentados e pesquisáveis", content),
        encoding="utf-8",
    )


def guide_page() -> None:
    path = DOCS / "guia-resultados.html"
    text = path.read_text(encoding="utf-8")
    if 'id="suficiencia-pergunta"' not in text:
        section = """<section class="card"><h2 id="suficiencia-pergunta">14. Suficiência por pergunta · V2.4</h2><p>A suficiência é avaliada separadamente para nível de água, propriedades hidráulicas, hidroquímica, geometria aquífera e monitoramento temporal. Evidência direta, mínimo documental do registro, estado local da célula e representatividade territorial são resultados diferentes.</p><div class="danger rule"><b>SUFICIÊNCIA DOCUMENTAL LOCAL ≠ REPRESENTATIVIDADE TERRITORIAL.</b> Nenhuma quantidade universal de poços foi adotada.</div><div class="grid"><div class="metric"><b>Q01</b>Nível e profundidade da água</div><div class="metric"><b>Q02</b>Propriedades hidráulicas</div><div class="metric"><b>Q03</b>Hidroquímica</div><div class="metric"><b>Q04</b>Geometria aquífera</div><div class="metric"><b>Q05</b>Monitoramento temporal</div></div><p>Nenhum poço atende ao mínimo documental completo sob as regras conservadoras atuais. A evidência parcial permanece válida e os bloqueios são publicados por requisito.</p><p><a href="metodologia-suficiencia-pergunta.html"><b>Abrir metodologia completa da V2.4</b></a></p></section>"""
        marker = '<section class="card"><h2 id="cores">14. Como ler as cores do mapa</h2>'
        text = text.replace(marker, section + '<section class="card"><h2 id="cores">15. Como ler as cores do mapa</h2>')
        text = text.replace('id="fichas">15.', 'id="fichas">16.')
        text = text.replace('id="dicionario">16.', 'id="dicionario">17.')
    text = text.replace("A V2.2 inclui um dicionário automático e auditável para <b>680 campos distintos</b>", "A V2.4 inclui um dicionário automático e auditável para <b>788 campos distintos</b>")
    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    methodology_page()
    bibliography_page()
    dictionary_page()
    guide_page()
    print("OK documentação web V2.4")
