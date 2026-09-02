/* SPDX-License-Identifier: AGPL-3.0-or-later */
(() => {
  'use strict';

  const dashboard = document.getElementById('statsVisualDashboard');
  const tabs = [...document.querySelectorAll('[data-stats-view]')];
  const visualPanel = document.getElementById('statsVisualPanel');
  const fullPanel = document.getElementById('statsFullPanel');
  const tablesPanel = document.getElementById('statsTablesPanel');
  if (!dashboard || !visualPanel || !fullPanel || !tablesPanel || tabs.length < 3) return;

  const colors = {
    red: '#b2182b',
    orange: '#f28e2b',
    purple: '#7b4ab4',
    turquoise: '#1b9e9a',
    green: '#2e8b57',
    grey: '#7c8793',
    pale: '#dce6eb'
  };

  const number = value => Number(value || 0);
  const integer = value => number(value).toLocaleString('pt-BR', { maximumFractionDigits: 0 });
  const decimal = value => number(value).toLocaleString('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 });
  const escape = value => String(value ?? '').replace(/[&<>"]/g, character => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[character]);

  function dataset(payload, id) {
    return payload.datasets.find(item => item.id === id);
  }

  function metric(rows, id) {
    return rows.find(row => row.metric === id)?.value;
  }

  function legend(items) {
    return `<div class="stats-legend-inline">${items.map(item => `<span><i style="background:${item.color}"></i>${escape(item.label)}</span>`).join('')}</div>`;
  }

  function stackedRows(rows, segments, totalKey, labelKey = 'question_name') {
    return `<div class="stats-bar-list">${rows.map(row => {
      const total = number(row[totalKey]);
      const bars = segments.map(segment => {
        const value = number(row[segment.key]);
        const percentage = total ? value / total * 100 : 0;
        return `<span style="width:${percentage.toFixed(4)}%;background:${segment.color}" title="${escape(segment.label)} ${integer(value)}" aria-hidden="true"></span>`;
      }).join('');
      const description = segments.map(segment => `${segment.label} ${integer(row[segment.key])}`).join(', ');
      return `<div><div class="stats-bar-label"><b>${escape(row[labelKey])}</b><span>${integer(total)}</span></div><div class="stats-stacked-bar" role="img" aria-label="${escape(row[labelKey])}. ${escape(description)}">${bars}</div></div>`;
    }).join('')}</div>`;
  }

  function card(title, description, content, wide = false) {
    return `<article class="stats-chart-card${wide ? ' wide' : ''}"><div class="stats-chart-head"><h3>${escape(title)}</h3><p>${escape(description)}</p></div>${content}</article>`;
  }

  function aggregatePriority(rows) {
    const fields = [
      'priority_unknown_n',
      'priority_p1_critical_n',
      'priority_p2_high_n',
      'priority_p3_moderate_n',
      'priority_p4_low_n',
      'priority_p5_documentary_sufficiency_n'
    ];
    const grouped = new Map();
    rows.forEach(row => {
      if (!grouped.has(row.question_code)) {
        grouped.set(row.question_code, { question_code: row.question_code, question_name: row.question_name, cell_scale_n: 0 });
      }
      const target = grouped.get(row.question_code);
      target.cell_scale_n += number(row.cells_n);
      fields.forEach(field => { target[field] = number(target[field]) + number(row[field]); });
    });
    return [...grouped.values()];
  }

  function render(payload) {
    const globalRows = dataset(payload, 'effective_global')?.rows || [];
    const questions = dataset(payload, 'question_global')?.rows || [];
    const priority = aggregatePriority(dataset(payload, 'research_priority_summary')?.rows || []);
    const grids = dataset(payload, 'grid_evidence')?.rows || [];
    const stability = dataset(payload, 'stability_cross_scale')?.rows || [];
    const wells = number(metric(globalRows, 'canonical_wells_n'));
    const cells = grids.reduce((sum, row) => sum + number(row.n_cells), 0);
    const supportPoints = stability.length ? number(stability[0].support_points_n) : 0;

    const evidenceSegments = [
      { key: 'direct_evidence_n', label: 'Evidência direta', color: colors.turquoise },
      { key: 'unknown_evidence_n', label: 'UNKNOWN', color: colors.grey }
    ];
    const prioritySegments = [
      { key: 'priority_unknown_n', label: 'UNKNOWN', color: colors.grey },
      { key: 'priority_p1_critical_n', label: 'P1 crítica', color: colors.red },
      { key: 'priority_p2_high_n', label: 'P2 alta', color: colors.orange },
      { key: 'priority_p3_moderate_n', label: 'P3 moderada', color: colors.purple },
      { key: 'priority_p4_low_n', label: 'P4 baixa', color: colors.turquoise },
      { key: 'priority_p5_documentary_sufficiency_n', label: 'P5 suficiência documental', color: colors.green }
    ];
    const stabilitySegments = [
      { key: 'direct_all_scales_n', label: 'Direta nas cinco escalas', color: colors.green },
      { key: 'direct_some_scales_n', label: 'Direta em parte das escalas', color: colors.turquoise },
      { key: 'direct_no_scale_n', label: 'Sem evidência direta', color: colors.grey }
    ];

    const scaleBars = `<div class="stats-scale-bars">${grids.map(row => {
      const pct = number(row.pct_cells_with_wells);
      return `<div class="stats-scale-column"><strong>${decimal(pct)}%</strong><i style="height:${Math.max(4, pct / 60 * 130).toFixed(1)}px" aria-hidden="true"></i><span>${escape(row.scale_km2)} km²</span><small>${integer(row.cells_with_wells)} de ${integer(row.n_cells)}</small></div>`;
    }).join('')}</div>`;

    const gapItems = [
      ['vertical_capture_interval_demonstrated_n', 'Intervalos captados completos', 'Nenhum foi demonstrado no conjunto adquirido', 'critical'],
      ['temporal_time_series_demonstrated_n', 'Séries temporais completas', 'O acompanhamento completo permanece ausente', 'critical'],
      ['independence_demonstrated_n', 'Independência demonstrada', 'A independência hidrogeológica permanece não demonstrada', 'purple'],
      ['hydraulic_transmissivity_reported_n', 'Transmissividade informada', 'Valores informados e ainda não validados', 'warning'],
      ['hydrostrat_unknown_n', 'Hidroestratigrafia UNKNOWN', 'Poços sem estado hidroestratigráfico demonstrado', 'purple'],
      ['documentary_flagged_wells_n', 'Poços com alertas', 'Ao menos um alerta documental preservado', 'warning']
    ];
    const gaps = `<div class="stats-gap-grid">${gapItems.map(([id, label, note, tone]) => `<div class="stats-gap-card" data-tone="${tone}"><strong>${integer(metric(globalRows, id))}</strong><span>${escape(label)}</span><small>${escape(note)}</small></div>`).join('')}</div>`;

    dashboard.innerHTML = `
      <section class="stats-visual-hero">
        <div><h3>Uma infraestrutura científica multiescalar</h3><p>Os gráficos abaixo são calculados no navegador a partir de statistics_v26.json. Eles resumem disponibilidade documental, prioridade experimental e estabilidade sem alterar os dados e sem produzir uma prioridade integrada.</p></div>
        <div class="stats-hero-badges"><div><strong>${integer(wells)}</strong><span>poços canônicos</span></div><div><strong>${integer(cells)}</strong><span>células em cinco escalas</span></div><div><strong>${integer(supportPoints)}</strong><span>pontos fixos de suporte</span></div><div><strong>${integer(payload.dataset_count)}</strong><span>resumos completos</span></div></div>
      </section>
      <div class="stats-visual-grid">
        ${card('Evidência direta por pergunta', 'Cada barra representa os 3.877 poços. UNKNOWN permanece separado.', stackedRows(questions, evidenceSegments, 'n_wells') + legend(evidenceSegments))}
        ${card('O efeito da escala', 'Percentual de células que contém ao menos um poço na família principal O00.', scaleBars)}
        ${card('Prioridade experimental por pergunta', 'Soma descritiva das células nas cinco escalas. Uma célula em cada escala é uma observação distinta.', stackedRows(priority, prioritySegments, 'cell_scale_n') + legend(prioritySegments), true)}
        ${card('Persistência entre escalas', 'Situação da evidência direta nos 14.284 pontos fixos de suporte para cada pergunta.', stackedRows(stability, stabilitySegments, 'support_points_n', 'question_code') + legend(stabilitySegments), true)}
        ${card('Carências documentais decisivas', 'Valores globais preservados pelo auditor científico.', gaps, true)}
      </div>
      <p class="stats-visual-note">Leitura obrigatória. As barras descrevem o conjunto adquirido. Elas não demonstram ausência física, representatividade territorial, potencial aquífero ou prioridade integrada. Abra Estudo completo para conhecer todo o processo ou 20 tabelas para consultar os resumos auditados.</p>`;
  }

  function selectView(name, focus = false) {
    const panels = { visual: visualPanel, full: fullPanel, tables: tablesPanel };
    Object.entries(panels).forEach(([id, panel]) => { panel.hidden = id !== name; });
    tabs.forEach(tab => {
      const active = tab.dataset.statsView === name;
      tab.classList.toggle('active', active);
      tab.setAttribute('aria-selected', String(active));
      tab.tabIndex = active ? 0 : -1;
      if (active && focus) tab.focus();
    });
  }

  tabs.forEach(tab => tab.addEventListener('click', () => selectView(tab.dataset.statsView)));
  tabs.forEach(tab => tab.addEventListener('keydown', event => {
    if (!['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
    event.preventDefault();
    const index = tabs.indexOf(tab);
    const offset = event.key === 'ArrowRight' ? 1 : -1;
    selectView(tabs[(index + offset + tabs.length) % tabs.length].dataset.statsView, true);
  }));

  fetch('./data/statistics/statistics_v26.json', { cache: 'no-store' })
    .then(response => {
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.json();
    })
    .then(render)
    .catch(error => {
      dashboard.innerHTML = '<div class="stats-visual-loading" role="alert">A visão gráfica não pôde ser carregada. As 20 tabelas completas continuam disponíveis.</div>';
      console.error('PIH MS visual statistics', error);
    });

  selectView('visual');
})();
