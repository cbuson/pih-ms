/* SPDX-License-Identifier: AGPL-3.0-or-later */
(() => {
  'use strict';

  const targets = [
    document.getElementById('statsFullDashboard'),
    document.getElementById('statsFullDocument')
  ].filter(Boolean);
  if (!targets.length) return;

  const esc = value => String(value ?? '').replace(/[&<>"']/g, character => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[character]);
  const n = value => Number(value || 0);
  const integer = value => n(value).toLocaleString('pt-BR', { maximumFractionDigits: 0 });
  const decimal = value => n(value).toLocaleString('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 });
  const bytes = value => {
    const amount = n(value);
    if (amount >= 1024 ** 3) return `${decimal(amount / 1024 ** 3)} GB`;
    if (amount >= 1024 ** 2) return `${decimal(amount / 1024 ** 2)} MB`;
    if (amount >= 1024) return `${decimal(amount / 1024)} kB`;
    return `${integer(amount)} B`;
  };

  const section = (id, eyebrow, title, lead, content) => `
    <section class="full-stats-section" id="${esc(id)}">
      <header class="full-stats-section-head"><span>${esc(eyebrow)}</span><h2>${esc(title)}</h2><p>${esc(lead)}</p></header>
      ${content}
    </section>`;

  const table = (headers, rows, label) => `
    <div class="full-stats-table-wrap" tabindex="0" role="region" aria-label="${esc(label)}">
      <table class="full-stats-table"><thead><tr>${headers.map(item => `<th scope="col">${esc(item)}</th>`).join('')}</tr></thead>
      <tbody>${rows.map(row => `<tr>${row.map((item, index) => `<${index === 0 ? 'th scope="row"' : 'td'}>${item}</${index === 0 ? 'th' : 'td'}>`).join('')}</tr>`).join('')}</tbody></table>
    </div>`;

  const metricCards = items => `<div class="full-stats-metric-grid">${items.map(item => `
    <article><strong>${esc(item.value)}</strong><span>${esc(item.label)}</span>${item.note ? `<small>${esc(item.note)}</small>` : ''}</article>`).join('')}</div>`;

  const bars = (items, valueKey, labelKey, note, colorClass = '') => {
    const maximum = Math.max(...items.map(item => n(item[valueKey])), 1);
    return `<div class="full-stats-bars ${esc(colorClass)}">${items.map(item => `
      <div class="full-stats-bar-row"><div><b>${esc(item[labelKey])}</b><span>${integer(item[valueKey])}</span></div><i aria-hidden="true"><span style="width:${(n(item[valueKey]) / maximum * 100).toFixed(4)}%"></span></i></div>`).join('')}${note ? `<p>${esc(note)}</p>` : ''}</div>`;
  };

  function render(payload) {
    const h = payload.headline;
    const base = payload.v27_package_baseline;
    const arch = payload.data_architecture;
    const docs = payload.documentation_inventory;
    const interfaceData = payload.interface_inventory;

    const navigation = `<nav class="full-stats-nav" aria-label="Conteúdo do estudo estatístico">
      <a href="#fs-processo">Processo</a><a href="#fs-arquitetura">Arquitetura</a><a href="#fs-evidencias">Evidências</a><a href="#fs-perguntas">Perguntas</a><a href="#fs-modulos">Módulos</a><a href="#fs-resultados">Resultados</a><a href="#fs-estabilidade">Estabilidade</a><a href="#fs-prioridade">Prioridade</a><a href="#fs-interface">Interface</a><a href="#fs-limites">Limites</a>
    </nav>`;

    const hero = `<section class="full-stats-hero">
      <div class="full-stats-hero-copy"><span>PIH MS ${esc(payload.release)} · inventário reproduzível</span><h1>O estudo por trás do mapa</h1><p>Este painel torna visível o processo completo. Ele reúne fontes, auditorias, camadas, matrizes, escalas, perguntas, requisitos, resultados, documentação e limites científicos.</p></div>
      ${metricCards([
        { value: integer(h.canonical_wells_n), label: 'poços canônicos' },
        { value: integer(h.grid_cells_n), label: 'células em cinco escalas' },
        { value: integer(h.support_points_n), label: 'pontos fixos de suporte' },
        { value: integer(h.requirements_n), label: 'requisitos observáveis' },
        { value: integer(h.evidence_layers_n), label: 'camadas de evidência' },
        { value: integer(h.analytical_modules_n), label: 'módulos analíticos' }
      ])}
      <div class="full-stats-scope"><b>Como ler os grandes números</b><p>${esc(payload.scope_note)}</p></div>
    </section>`;

    const process = section('fs-processo', '01 · percurso científico', 'De uma fonte auditada a uma prioridade por pergunta', 'Cada etapa adiciona uma operação verificável e conserva os produtos anteriores.', `
      <div class="full-stats-timeline">${payload.methodology_stages.map((item, index) => `<article><i>${String(index + 1).padStart(2, '0')}</i><div><b>${esc(item.version)} · ${esc(item.name)}</b><p>${esc(item.description)}</p></div></article>`).join('')}</div>`);

    const packageMetrics = metricCards([
      { value: integer(base.files_n), label: 'arquivos no ZIP V2.7' },
      { value: bytes(base.uncompressed_bytes_n), label: 'volume sem compressão' },
      { value: integer(base.csv_files_n), label: 'arquivos CSV' },
      { value: integer(base.csv_physical_rows_n), label: 'registros físicos em CSV', note: 'não são poços únicos' },
      { value: integer(arch.current_derived_csv.csv_files_n), label: 'CSV derivados atuais' },
      { value: integer(arch.current_derived_csv.physical_rows_n), label: 'registros derivados atuais' }
    ]);
    const fileRows = payload.file_types.map(item => [esc(item.type), integer(item.files_n), bytes(item.bytes_n)]);
    const matrixMetrics = metricCards([
      { value: integer(arch.well_question_pairs_n), label: 'pares poço e pergunta' },
      { value: integer(arch.well_requirement_pairs_n), label: 'pares poço e requisito' },
      { value: integer(arch.cell_question_pairs_n), label: 'pares célula e pergunta' },
      { value: integer(arch.support_question_pairs_n), label: 'pares suporte e pergunta' },
      { value: integer(arch.support_scale_question_pairs_n), label: 'pares suporte, escala e pergunta' },
      { value: integer(arch.support_requirement_pairs_n), label: 'pares suporte e requisito' }
    ]);
    const architecture = section('fs-arquitetura', '02 · arquitetura de dados', 'Uma infraestrutura com milhões de registros analíticos', 'As matrizes repetem unidades legítimas de análise por pergunta, requisito, escala e origem. A repetição é declarada e não aumenta artificialmente o número de poços.', `
      ${packageMetrics}<div class="full-stats-split"><div><h3>Tipos de arquivo no pacote auditado</h3>${table(['Formato', 'Arquivos', 'Volume sem compressão'], fileRows, 'Inventário por tipo de arquivo')}</div><div><h3>Matrizes centrais</h3>${matrixMetrics}<p class="full-stats-footnote">${esc(base.note)}</p></div></div>`);

    const evidenceRows = payload.evidence_layers.map(item => [
      `<b>${esc(item.code)}</b> · ${esc(item.name)}`,
      integer(item.feature_count),
      esc(item.question),
      esc(item.limitation)
    ]);
    const evidence = section('fs-evidencias', '03 · evidências', 'Doze camadas com regra e limitação explícitas', `${integer(payload.evidence_feature_placements_n)} feições estão armazenadas nas 12 camadas. Um mesmo poço pode aparecer em várias delas.`, `
      ${bars(payload.evidence_layers, 'feature_count', 'code', payload.evidence_feature_note, 'evidence-bars')}
      ${table(['Camada', 'Feições', 'Pergunta observável', 'Limitação obrigatória'], evidenceRows, 'Camadas de evidência E01 a E12')}`);

    const dimensionCards = `<div class="full-stats-card-grid">${payload.knowledge_dimensions.map(item => `<article><span>${esc(item.dimension)}</span><h3>${esc(item.what_it_describes)}</h3><p>${esc(item.what_it_does_not_mean)}</p></article>`).join('')}</div>`;
    const questionRows = payload.questions.map(item => [
      `<b>${esc(item.question_code)}</b> · ${esc(item.question_name)}`,
      integer(item.requirements_n),
      integer(item.summary.direct_evidence_n),
      integer(item.summary.unknown_evidence_n),
      esc(item.question_objective)
    ]);
    const requirementRows = payload.requirement_dimensions.map(item => [esc(item.dimension), integer(item.requirements_n)]);
    const questions = section('fs-perguntas', '04 · dimensões e perguntas', 'Nove dimensões, cinco perguntas e 39 requisitos', 'As dimensões não são somadas. Cada pergunta usa um conjunto explícito de requisitos e mantém UNKNOWN separado.', `
      <h3>Nove dimensões de conhecimento efetivo</h3>${dimensionCards}
      <h3>Cinco perguntas de investigação</h3>${table(['Pergunta', 'Requisitos', 'Evidência direta', 'UNKNOWN', 'Objetivo'], questionRows, 'Perguntas e suficiência documental')}
      <h3>Distribuição dos 39 requisitos</h3>${bars(payload.requirement_dimensions, 'requirements_n', 'dimension', '')}${table(['Dimensão', 'Requisitos'], requirementRows, 'Requisitos por dimensão')}`);

    const moduleRows = payload.module_inventory.map(item => [
      `${item.historical ? '<span class="full-stats-tag">histórico</span> ' : ''}${esc(item.name)}`,
      integer(item.csv_files_n),
      integer(item.physical_rows_n),
      integer(item.max_columns_n),
      bytes(item.bytes_n)
    ]);
    const auditRows = payload.source_audit_tables.map(item => [esc(item.file), integer(item.rows_n), integer(item.columns_n)]);
    const modules = section('fs-modulos', '05 · módulos e auditorias', 'Treze famílias de produtos derivados', 'Onze famílias são atuais e duas são históricas. As famílias históricas permanecem identificadas para não confundir geometrias antigas com as vigentes.', `
      ${table(['Família', 'CSV', 'Registros físicos', 'Máximo de campos', 'Volume'], moduleRows, 'Inventário dos módulos derivados')}
      <h3>Onze tabelas de auditoria da fonte</h3>${table(['Tabela', 'Registros', 'Campos'], auditRows, 'Tabelas da auditoria de origem')}`);

    const findingCards = `<div class="full-stats-finding-grid">${payload.key_findings.map(item => `<article class="${n(item.value) === 0 ? 'zero' : ''}"><strong>${integer(item.value)}</strong><span>${esc(item.label)}</span><small>${esc(item.unit)}</small></article>`).join('')}</div>`;
    const scaleRows = payload.scale_effect.map(item => [
      `${esc(item.scale_km2)} km²`, integer(item.n_cells), integer(item.cells_with_wells), `${decimal(item.pct_cells_with_wells)}%`, integer(item.cells_without_wells)
    ]);
    const results = section('fs-resultados', '06 · resultados documentais', 'O que foi demonstrado e o que permanece ausente', 'Zero não significa ausência física. Significa que o requisito completo não foi demonstrado no conjunto adquirido.', `
      ${findingCards}<h3>Efeito da escala na ocupação das células</h3>${table(['Escala', 'Células', 'Com poço', 'Ocupadas', 'Sem poço'], scaleRows, 'Ocupação das cinco escalas')}`);

    const stabilityRows = payload.stability_cross_scale.map(item => [
      esc(item.question_code), `${decimal(item.exact_state_all_scales_pct)}%`, `${decimal(item.direct_all_scales_pct)}%`, `${decimal(item.direct_some_scales_pct)}%`, `${decimal(item.direct_no_scale_pct)}%`
    ]);
    const stability = section('fs-estabilidade', '07 · estabilidade', 'A resposta muda quando a escala muda', 'Os 14.284 pontos fixos permitem comparar as cinco escalas sem trocar o suporte espacial.', `
      ${table(['Pergunta', 'Mesmo estado nas cinco', 'Direta nas cinco', 'Direta em parte', 'Sem direta'], stabilityRows, 'Persistência entre escalas')}
      <p class="full-stats-footnote">Nenhuma relação monotônica foi imposta e nenhuma escala final foi escolhida.</p>`);

    const p = payload.priority_totals;
    const c = payload.confidence_totals;
    const priorityItems = [
      ['UNKNOWN', p.priority_unknown_n], ['P1 crítica', p.priority_p1_critical_n], ['P2 alta', p.priority_p2_high_n], ['P3 moderada', p.priority_p3_moderate_n], ['P4 baixa', p.priority_p4_low_n], ['P5 suficiência', p.priority_p5_documentary_sufficiency_n]
    ].map(([label, value]) => ({ label, value }));
    const confidenceItems = [
      ['UNKNOWN', c.confidence_unknown_n], ['C1 muito baixa', c.confidence_c1_very_low_n], ['C2 baixa', c.confidence_c2_low_n], ['C3 moderada', c.confidence_c3_moderate_n], ['C4 alta', c.confidence_c4_high_n], ['C5 muito alta', c.confidence_c5_very_high_n]
    ].map(([label, value]) => ({ label, value }));
    const priorityQuestionRows = payload.priority_by_question.map(item => [
      `${esc(item.question_code)} · ${esc(item.question_name)}`, integer(item.cell_scale_records_n), integer(item.priority_unknown_n), integer(item.priority_p1_critical_n), integer(item.priority_p2_high_n), integer(item.priority_p3_moderate_n)
    ]);
    const priority = section('fs-prioridade', '08 · prioridade experimental', 'Prioridade e confiança continuam separadas', 'Cada célula em cada escala é um registro distinto. A soma abaixo descreve 45.145 pares célula e pergunta, não células territoriais únicas.', `
      <div class="full-stats-split"><div><h3>Prioridade</h3>${bars(priorityItems, 'value', 'label', '', 'priority-bars')}</div><div><h3>Confiança</h3>${bars(confidenceItems, 'value', 'label', '', 'confidence-bars')}</div></div>
      ${table(['Pergunta', 'Pares célula e escala', 'UNKNOWN', 'P1', 'P2', 'P3'], priorityQuestionRows, 'Prioridade por pergunta nas cinco escalas')}
      <div class="full-stats-warning"><b>Resultado estrutural importante</b><p>P4 e P5 têm zero células na base atual. Isso não autoriza afirmar que todo o território é prioritário. UNKNOWN continua fora das classes P1 a P5 e a prioridade integrada não foi calculada.</p></div>`);

    const selectorRows = interfaceData.selector_inventory.map(item => [
      esc(item.module), integer(item.scales_n), item.questions_n == null ? '—' : integer(item.questions_n), item.metrics_n == null ? 'condicional' : integer(item.metrics_n), item.origins_n == null ? '—' : integer(item.origins_n)
    ]);
    const interfaceSection = section('fs-interface', '09 · interface e documentação', 'O aplicativo também é uma camada de acesso científico', 'A interface oferece camadas diretas, módulos analíticos, fichas fragmentadas, resumos, páginas metodológicas e instalação opcional.', `
      ${metricCards([
        { value: integer(interfaceData.direct_checkbox_layers_n), label: 'camadas diretas selecionáveis' },
        { value: integer(interfaceData.analytical_modules_n), label: 'módulos analíticos' },
        { value: integer(interfaceData.sgb_2024_vector_layers_n), label: 'vetores SGB 2024 no manifesto' },
        { value: integer(interfaceData.sgb_2024_raster_families_n), label: 'famílias raster SGB 2024' },
        { value: integer(docs.well_detail_shards_n), label: 'fragmentos de fichas' },
        { value: integer(docs.wells_in_shards_n), label: 'poços presentes nas fichas' }
      ])}
      ${table(['Módulo', 'Escalas', 'Perguntas', 'Métricas', 'Origens'], selectorRows, 'Controles dos módulos analíticos')}
      ${metricCards([
        { value: integer(docs.documented_fields_n), label: 'campos no dicionário' },
        { value: integer(docs.bibliographic_references_n), label: 'referências bibliográficas' },
        { value: integer(docs.summary_datasets_n), label: 'resumos estatísticos' },
        { value: integer(docs.summary_rows_n), label: 'linhas nos resumos' },
        { value: integer(docs.summary_column_placements_n), label: 'campos distribuídos nos resumos' },
        { value: integer(arch.source_audit_physical_rows_n), label: 'registros nas auditorias de fonte' }
      ])}`);

    const links = `<div class="full-stats-link-grid">${payload.documentation_links.map(([label, href]) => `<a href="${esc(href)}">${esc(label)}<span>abrir documento</span></a>`).join('')}</div>`;
    const limits = section('fs-limites', '10 · limites e rastreabilidade', 'O que o PIH MS ainda não afirma', 'A força do estudo também está em tornar explícito o limite de cada resultado.', `
      <ul class="full-stats-limit-list">${payload.scientific_limits.map(item => `<li>${esc(item)}</li>`).join('')}</ul>
      <h3>Documentos para verificar o processo</h3>${links}`);

    const html = `<div class="full-stats-report">${hero}${navigation}${process}${architecture}${evidence}${questions}${modules}${results}${stability}${priority}${interfaceSection}${limits}<footer class="full-stats-report-footer"><img src="assets/img/pih-ms-icon.svg" alt=""><div><b>PIH MS ${esc(payload.release)}</b><span>Estudo estatístico completo. Conteúdo científico V2.6 preservado.</span></div></footer></div>`;
    targets.forEach(target => { target.innerHTML = html; });
  }

  fetch('./data/statistics/project_statistics_v271.json', { cache: 'no-store' })
    .then(response => {
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.json();
    })
    .then(render)
    .catch(error => {
      targets.forEach(target => {
        target.innerHTML = '<div class="stats-visual-loading" role="alert">O estudo estatístico completo não pôde ser carregado. Consulte as 20 tabelas auditadas.</div>';
      });
      console.error('PIH MS complete statistics', error);
    });
})();
