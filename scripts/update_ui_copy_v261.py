#!/usr/bin/env python3
"""Alinha textos estáticos e dinâmicos da interface com a V2.6.1."""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def update(path: Path, replacements: dict[str, str]) -> None:
    content = path.read_text(encoding="utf-8")
    for old, new in replacements.items():
        content = content.replace(old, new)
    path.write_text(content, encoding="utf-8")


update(
    ROOT / "docs" / "index.html",
    {
        "<title>PIH MS V2.6 · prioridade por pergunta</title>": "<title>PIH MS V2.6.1 · navegação móvel</title>",
        "916 definições, fórmulas e unidades": "1.045 definições, fórmulas e unidades",
        "Histórico científico V2.0 a V2.5": "Histórico científico V2.0 a V2.6",
        "V2.5.1 · DOCUMENTAÇÃO INTEGRADA · CIÊNCIA V2.5": "V2.6.1 · NAVEGAÇÃO MÓVEL · CIÊNCIA EXPERIMENTAL V2.6",
        "Documentação integrada · V2.5.1": "Documentação integrada · V2.6.1",
        "Histórico científico completo desde as evidências até a V2.5.": "Histórico científico completo desde as evidências até a V2.6.",
        "Estatísticas completas · conteúdo V2.5": "Estatísticas completas · ciência V2.6",
        "Os 17 resumos vigentes são apresentados por família e sem criar uma nota geral.": "Os 20 resumos vigentes são apresentados por família e sem criar uma nota geral.",
        "<strong>17</strong><span>resumos atuais</span>": "<strong>20</strong><span>resumos atuais</span>",
        "Metodologia científica · V2.0 a V2.5": "Metodologia científica · V2.0 a V2.6",
        "Cada etapa conserva sua própria versão científica. A V2.5 acrescenta estabilidade entre escalas e sensibilidade à origem sem substituir os módulos anteriores.": "Cada etapa conserva sua própria versão científica. A V2.6 acrescenta prioridade experimental por pergunta e confiança separada sem substituir os módulos anteriores.",
        "Sem pesos, interpolação ou prioridade</div>": "Sem pesos, interpolação ou prioridade integrada</div>",
        "Ajuda completa · V2.5.1": "Ajuda completa · V2.6.1",
        "No topo deve aparecer V2.6. A versão é experimental": "No topo deve aparecer V2.6.1. A ciência V2.6 é experimental",
        "PIH MS V2.6 experimental</h2>": "PIH MS V2.6.1</h2>",
        "Infraestrutura científica em desenvolvimento. A V2.6 classifica prioridade de investigação por pergunta e confiança separada, sem pesos, score, potencial aquífero ou prioridade integrada.": "Infraestrutura científica em desenvolvimento. A V2.6.1 melhora a experiência móvel sobre os resultados científicos experimentais da V2.6, sem pesos, score, potencial aquífero ou prioridade integrada.",
        "A V2.6 experimental ainda não possui uma versão Zenodo própria.": "A V2.6.1 ainda não possui uma versão Zenodo própria.",
    },
)

update(
    ROOT / "docs" / "assets" / "js" / "pih.js",
    {
        "replaceChildren('V2.5.1')": "replaceChildren('V2.6.1')",
        "replaceChildren('PIH MS V2.5.1')": "replaceChildren('PIH MS V2.6.1')",
        "document.title='PIH MS V2.6 · prioridade por pergunta'": "document.title='PIH MS V2.6.1 · navegação móvel'",
        "replaceChildren('V2.6');document.getElementById('authorTitle')?.replaceChildren('PIH MS V2.6 experimental')": "replaceChildren('V2.6.1');document.getElementById('authorTitle')?.replaceChildren('PIH MS V2.6.1')",
        "<strong>PIH MS · V2.6 experimental</strong><span>Prioridade de investigação derivada do déficit documental demonstrado. Cinco perguntas separadas e nenhuma prioridade integrada.</span>": "<strong>PIH MS · V2.6.1</strong><span>Navegação móvel renovada sobre a prioridade experimental V2.6. Cinco perguntas separadas e nenhuma prioridade integrada.</span>",
        "Estatísticas completas · V2.6 experimental": "Estatísticas completas · ciência V2.6",
        "Documentação integrada · V2.6'": "Documentação integrada · V2.6.1'",
        "Ajuda completa · V2.6'": "Ajuda completa · V2.6.1'",
        "Infraestrutura científica em desenvolvimento. A V2.6 classifica prioridade de investigação por pergunta e confiança separada, sem pesos, score, potencial aquífero ou prioridade integrada.": "Infraestrutura científica em desenvolvimento. A V2.6.1 melhora a experiência móvel sobre os resultados científicos experimentais da V2.6, sem pesos, score, potencial aquífero ou prioridade integrada.",
        "A V2.6 experimental ainda não possui uma versão Zenodo própria.": "A V2.6.1 ainda não possui uma versão Zenodo própria.",
    },
)

print("OK textos de interface V2.6.1")
