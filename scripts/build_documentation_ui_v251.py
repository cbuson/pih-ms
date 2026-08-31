#!/usr/bin/env python3
"""Unifica a experiência documental da interface PIH MS V2.5.1."""
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def replace_required(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        if new in text:
            return text
        raise RuntimeError(f"Trecho obrigatório não encontrado em {label}")
    return text.replace(old, new)


def replace_block(text: str, start: str, end: str, replacement: str, label: str) -> str:
    begin = text.find(start)
    if begin < 0:
        raise RuntimeError(f"Início do bloco não encontrado em {label}")
    finish = text.find(end, begin)
    if finish < 0:
        raise RuntimeError(f"Fim do bloco não encontrado em {label}")
    return text[:begin] + replacement + "\n" + text[finish:]


DOCS_MODAL = """<div class="modal" id="docsModal" role="dialog" aria-modal="true" aria-labelledby="docsTitle" hidden><div class="modal-card wide-modal"><button class="modal-close" type="button" data-close aria-label="Fechar documentação">×</button><div class="modal-kicker">Documentação integrada · V2.5.1</div><h2 id="docsTitle">Ler, verificar e navegar</h2><p>Todas as páginas usam agora a mesma navegação, tipografia e estrutura de leitura. Elas abrem sobre o mapa e também funcionam como páginas independentes.</p><div class="docs-link-grid"><a class="docs-link-card" href="guia-resultados.html">Guia de resultados<small>Como interpretar malhas, evidências, escalas, estados e limites.</small></a><a class="docs-link-card" href="metodologia-estabilidade-sensibilidade.html">Estabilidade e sensibilidade<small>Cinco escalas, quatro origens, cinco perguntas e seis métricas.</small></a><a class="docs-link-card" href="dicionario-parametros.html">Dicionário de parâmetros<small>916 campos com definição, regra, unidade e tratamento de UNKNOWN.</small></a><a class="docs-link-card" href="bibliografia.html">Bibliografia completa<small>55 referências com função e estado de uso explícitos.</small></a><a class="docs-link-card" href="metodologia-suficiencia-pergunta.html">Suficiência por pergunta<small>Requisitos críticos e estados separados para as cinco perguntas.</small></a><button class="docs-link-card docs-card-button" type="button" data-modal="methodModal">Todas as metodologias<small>Histórico científico completo desde as evidências até a V2.5.</small></button></div></div></div>"""


STATS_MODAL = """<div class="modal" id="statsModal" role="dialog" aria-modal="true" aria-labelledby="statsTitle" hidden><div class="modal-card full-modal statistics-modal-card"><button class="modal-close" type="button" data-close aria-label="Fechar estatísticas">×</button><div class="modal-kicker">Estatísticas completas · conteúdo V2.5</div><h2 id="statsTitle">Todos os resumos atuais</h2><p>Os 17 resumos vigentes são apresentados por família e sem criar uma nota geral. Resultados históricos incompatíveis permanecem separados.</p><div class="metric-grid stats-overview"><div><strong>17</strong><span>resumos atuais</span></div><div><strong>5</strong><span>perguntas separadas</span></div><div><strong>5</strong><span>escalas comparadas</span></div><div><strong>4</strong><span>origens de malha</span></div><div><strong>3.877</strong><span>poços canônicos</span></div></div><div id="statisticsStatus" class="statistics-status" role="status">Carregando resumos</div><div class="statistics-layout"><aside class="statistics-datasets" id="statisticsDatasets" aria-label="Resumos estatísticos"></aside><section class="statistics-content"><label class="statistics-mobile-select">Resumo<select id="statisticsSelect"></select></label><div class="statistics-heading"><div><small id="statisticsFamily"></small><h3 id="statisticsDatasetTitle">Resumo</h3></div><span id="statisticsRowCount"></span></div><p class="statistics-source" id="statisticsSource"></p><div class="statistics-table-wrap" id="statisticsTable"></div><p class="statistics-note">Os nomes dos campos são preservados como nos CSV para favorecer a verificação. UNKNOWN, vazio e zero não são tratados como equivalentes.</p></section></div></div></div>"""


METHOD_MODAL = """<div class="modal" id="methodModal" role="dialog" aria-modal="true" aria-labelledby="methodTitle" hidden><div class="modal-card full-modal method-catalog-card"><button class="modal-close" type="button" data-close aria-label="Fechar metodologia">×</button><div class="modal-kicker">Metodologia científica · V2.0 a V2.5</div><h2 id="methodTitle">Histórico metodológico completo</h2><p>Cada etapa conserva sua própria versão científica. A V2.5 acrescenta estabilidade entre escalas e sensibilidade à origem sem substituir os módulos anteriores.</p><div class="docs-link-grid method-grid"><a class="docs-link-card featured" href="metodologia-estabilidade-sensibilidade.html">V2.5 · Estabilidade e sensibilidade<small>Comparações sobre suporte fixo e persistência dos bloqueios.</small></a><a class="docs-link-card" href="metodologia-suficiencia-pergunta.html">V2.4 · Suficiência por pergunta<small>Cinco perguntas, requisitos críticos e regras conjuntivas.</small></a><a class="docs-link-card" href="metodologia-conhecimento-efetivo.html">V2.2 · Conhecimento efetivo<small>Nove dimensões mantidas separadas.</small></a><a class="docs-link-card" href="metodologia-independencia-redundancia.html">V2.1 · Independência e redundância<small>Sobreposição, proximidade e diversidade documental.</small></a><a class="docs-link-card" href="metodologia-vertical-temporal.html">Vertical e temporal<small>Documentação por poço e por célula.</small></a><a class="docs-link-card" href="metodologia-estratificacao-hidrogeologica.html">Estratificação hidrogeológica<small>Mistura, dominância e mascaramento.</small></a><a class="docs-link-card" href="metodologia-escalas-candidatas.html">Escalas candidatas<small>Comparação das cinco resoluções sintéticas.</small></a><a class="docs-link-card" href="metodologia-estrutura-espacial.html">Estrutura espacial<small>Distâncias, distribuição interna e MAUP.</small></a><a class="docs-link-card" href="metodologia-malhas-evidencia.html">Malhas de evidência<small>Agregação E01 a E12 por hexágono.</small></a><a class="docs-link-card" href="metodologia-evidencias.html">Evidências E01 a E12<small>Definições, procedência e controles.</small></a></div><div class="principle-list"><div>UNKNOWN permanece UNKNOWN</div><div>Contagem não é qualidade</div><div>Concordância não é representatividade</div><div>Sem escala ou origem final</div><div>Sem pesos, interpolação ou prioridade</div></div></div></div>"""


AUTHOR_MODAL = """<div class="modal" id="authorModal" role="dialog" aria-modal="true" aria-labelledby="authorTitle" hidden><div class="modal-card full-modal author-modal-card"><button class="modal-close" type="button" data-close aria-label="Fechar autoria e licença">×</button><div class="modal-kicker">Informação · Autoria · Direitos</div><h2 id="authorTitle">PIH MS V2.5.1</h2><div class="project-intro"><b>Prioridade de Investigação Hidrogeológica de Mato Grosso do Sul</b><span>Infraestrutura científica em desenvolvimento. A interface V2.5.1 integra a documentação do conteúdo científico V2.5 sem calcular score, potencial ou prioridade.</span></div><div class="authors-grid"><article class="author-card"><div class="author-head"><div class="author-mark">CB</div><div><h3>Carlos Busón Buesa</h3><p>Concepção, arquitetura científica e digital, integração territorial, documentação e desenvolvimento metodológico.</p></div></div><div class="author-meta"><div><span>Instituição</span><strong>Universidade Federal de Mato Grosso do Sul · UFMS</strong></div><div><span>Programa e unidade</span><strong>PPGTA · FAENG</strong></div><div><span>ORCID</span><a href="https://orcid.org/0000-0002-1446-2252" target="_blank" rel="noopener">0000-0002-1446-2252</a></div></div></article><article class="author-card"><div class="author-head"><div class="author-mark">SG</div><div><h3>Sandra Garcia Gabas</h3><p>Coautoria científica, geologia, hidrogeologia, geotecnia ambiental, geoquímica e revisão da integração geocientífica.</p></div></div><div class="author-meta"><div><span>Instituição</span><strong>Universidade Federal de Mato Grosso do Sul · UFMS</strong></div><div><span>Programa e unidade</span><strong>PPGTA · FAENG</strong></div><div><span>ORCID</span><a href="https://orcid.org/0000-0002-1027-0288" target="_blank" rel="noopener">0000-0002-1027-0288</a></div></div></article></div><section class="license-card"><div class="license-badge">AGPL-3.0-or-later</div><div><h3>Por que esta licença foi escolhida</h3><p>O código do aplicativo é software livre e de código aberto. A GNU Affero General Public License permite usar, estudar, modificar e compartilhar o código. Quando uma versão modificada é oferecida por uma rede, seu código-fonte correspondente também deve ser oferecido às pessoas que a utilizam.</p><p>Esta escolha reduz o risco de que melhorias do aplicativo sejam fechadas e retiradas da comunidade. A licença permite uso comercial. Proibir todo uso comercial faria o código deixar de cumprir a definição de Open Source da OSI.</p><p><a href="licenca-software.txt" target="_blank">Texto da licença do código</a> · <a href="licenca-conteudos.html">Licença dos conteúdos originais</a></p></div></section><section class="content-license-card"><h3>Conteúdos e dados</h3><p>Textos científicos, documentação e figuras originais são disponibilizados sob CC BY-NC-SA 4.0, salvo indicação diferente. Essa licença exige atribuição, impede uso comercial desses conteúdos e exige compartilhar adaptações sob a mesma licença. Dados e materiais de terceiros conservam suas licenças, créditos e condições de origem.</p></section><div class="doi-note"><b>Identificador persistente</b><p>O DOI <a href="https://doi.org/10.5281/zenodo.22180863" target="_blank" rel="noopener">10.5281/zenodo.22180863</a> identifica o depósito PIH MS V2.2.1 no Zenodo. A V2.5.1 ainda não possui uma versão Zenodo própria.</p><p><a href="https://github.com/cbuson/pih-ms" target="_blank" rel="noopener">Repositório oficial no GitHub</a> · <a href="autoria-direitos.html">Abrir informação legal completa</a></p></div></div></div>"""


DOC_VIEWER_MODAL = """<div class="modal" id="docViewerModal" role="dialog" aria-modal="true" aria-labelledby="docViewerTitle" hidden><div class="modal-card document-viewer-card"><div class="document-viewer-toolbar"><div><span>Documentação PIH MS</span><h2 id="docViewerTitle">Documento</h2></div><div class="document-viewer-actions"><a id="docViewerExternal" href="guia-resultados.html" target="_blank" rel="noopener">Abrir em nova janela</a><button class="modal-close" type="button" data-close aria-label="Fechar documento">×</button></div></div><div class="document-viewer-loading" id="docViewerLoading" role="status">Carregando documento</div><iframe id="docViewerFrame" title="Documento PIH MS" loading="eager"></iframe></div></div>"""


def update_index() -> None:
    path = DOCS / "index.html"
    text = read(path)
    replacements = [
        ("Carregando PIH MS V2.4", "Carregando PIH MS V2.5.1"),
        ("<div class=\"version-stamp\">V2.5 · ESTABILIDADE E SENSIBILIDADE · SEM SCORE PIH</div>", "<div class=\"version-stamp\">V2.5.1 · DOCUMENTAÇÃO INTEGRADA · CIÊNCIA V2.5</div>"),
        ("Ajuda completa · V2.4", "Ajuda completa · V2.5.1"),
        ("O painel reúne 13 resumos atuais.", "O painel reúne 17 resumos atuais."),
        ("No topo deve aparecer V2.4.", "No topo deve aparecer V2.5.1."),
        ("O Excel da V2.4 é complementar para revisão humana.", "O Excel científico da V2.5 é complementar para revisão humana."),
        ("A primeira ficha de poço usa carregamento fragmentado para reduzir a espera.", "A primeira ficha de poço usa carregamento fragmentado para reduzir a espera. As fichas da V2.5 mostram também estabilidade entre escalas, sensibilidade à origem e bloqueios documentais locais."),
        ("A V2.4 calcula cada pergunta diretamente nas cinco escalas da família principal O00.", "A V2.4 calcula cada pergunta diretamente nas cinco escalas da família principal O00. A V2.5 compara esses estados entre as cinco escalas e entre quatro origens sem escolher uma solução final."),
        ("A V2.4 usa essas dimensões em cinco perguntas distintas", "A V2.4 usa essas dimensões em cinco perguntas distintas"),
        ("Na V2.4 cinza identifica célula sem poços no conjunto auditado, violeta ausência de evidência direta, laranja evidência parcial e verde um mínimo documental local demonstrado.", "Nas camadas de suficiência, cinza identifica célula sem poços, violeta ausência de evidência direta, laranja evidência parcial e verde um mínimo documental local demonstrado. Na V2.5 as cores continuam descritivas e variam conforme a métrica selecionada."),
        ("Esta revisão introduz suficiência por pergunta sem calcular score PIH, interpolação ou prioridade final.", "A V2.5.1 integra todas as páginas de documentação. O conteúdo científico V2.5 compara estabilidade e sensibilidade sem calcular score PIH, interpolação ou prioridade final."),
        ("<script src=\"./assets/js/pih.js?v=250100\"></script><script src=\"./assets/js/metric-help.js?v=250100\"></script>", "<script src=\"./assets/js/pih.js?v=251000\"></script><script src=\"./assets/js/metric-help.js?v=251000\"></script>")
    ]
    for old, new in replacements:
        if old in text:
            text = text.replace(old, new)
    text = replace_block(text, '<div class="modal" id="docsModal"', '<div class="modal" id="statsModal"', DOCS_MODAL, "index docsModal")
    text = replace_block(text, '<div class="modal" id="statsModal"', '<div class="modal" id="methodModal"', STATS_MODAL, "index statsModal")
    text = replace_block(text, '<div class="modal" id="methodModal"', '<div class="modal" id="helpModal"', METHOD_MODAL, "index methodModal")
    text = replace_block(text, '<div class="modal" id="authorModal"', '<script src="https://cdnjs.cloudflare.com', AUTHOR_MODAL + "\n" + DOC_VIEWER_MODAL, "index authorModal")
    write(path, text)


def update_pages() -> None:
    for path in sorted(DOCS.glob("*.html")):
        if path.name == "index.html":
            continue
        text = read(path)
        if "documentation.css" not in text:
            text = text.replace("</head>", '<link rel="stylesheet" href="assets/css/documentation.css?v=251000"></head>')
        if "documentation.js" not in text:
            text = text.replace("</body>", '<script src="assets/js/documentation.js?v=251000"></script></body>')
        text = text.replace("documentation.css?v=251000", "documentation.css?v=251000")
        text = text.replace("documentation.js?v=251000", "documentation.js?v=251000")
        write(path, text)

    guide = DOCS / "guia-resultados.html"
    text = read(guide)
    text = text.replace('<span class="tag">PIH MS V2.2</span>', '<span class="tag">PIH MS V2.5</span>')
    text = text.replace("A V2.4 inclui um dicionário automático e auditável para <b>788 campos distintos</b>", "A V2.5 inclui um dicionário automático e auditável para <b>916 campos distintos</b>")
    write(guide, text)

    sufficiency = DOCS / "metodologia-suficiencia-pergunta.html"
    text = read(sufficiency).replace("Dicionário com 788 campos", "Dicionário atual com 916 campos")
    write(sufficiency, text)

    knowledge = DOCS / "metodologia-conhecimento-efetivo.html"
    text = read(knowledge).replace("Dicionário com 680 campos", "Dicionário vigente com 916 campos")
    write(knowledge, text)

    bibliography = DOCS / "bibliografia.html"
    text = read(bibliography)
    text = text.replace("Bibliografia completa PIH MS V2.4", "Bibliografia completa PIH MS V2.5")
    text = text.replace("PIH MS · V2.4", "PIH MS · V2.5")
    text = text.replace("A V2.4 acrescenta a referência normativa brasileira usada na separação entre resultado químico parcial e monitoramento de qualidade.", "A bibliografia vigente cobre as fontes oficiais, os fundamentos hidrogeológicos e os métodos usados até a V2.5. Jaccard, Spearman e MAUP estão identificados como métodos implementados. Antecedentes futuros permanecem separados dos métodos executados.")
    write(bibliography, text)

    authors = DOCS / "autoria-direitos.html"
    text = read(authors)
    text = text.replace("A V2.3 completa a família multiescalar nos módulos de evidência e estrutura espacial sem calcular prioridade.", "A interface V2.5.1 integra a documentação do conteúdo científico V2.5 sem calcular score, potencial ou prioridade.")
    text = text.replace('<section class="card"><h2>Estado do identificador persistente</h2><div class="note">PIH MS ainda não possui DOI próprio nesta fase. O DOI 10.5281/zenodo.21923101 corresponde ao projeto PAG ETR e não é reutilizado como identificador do PIH MS.</div></section>', '<section class="card"><h2>Identificador persistente e repositório</h2><div class="note">O DOI <a href="https://doi.org/10.5281/zenodo.22180863" target="_blank" rel="noopener">10.5281/zenodo.22180863</a> identifica o depósito PIH MS V2.2.1 no Zenodo. A V2.5.1 ainda não possui uma versão Zenodo própria.</div><p><a href="https://github.com/cbuson/pih-ms" target="_blank" rel="noopener">Abrir o repositório oficial no GitHub</a></p></section>')
    write(authors, text)


update_index()
update_pages()
print("OK documentação V2.5.1 atualizada")
