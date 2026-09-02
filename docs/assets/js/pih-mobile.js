/* SPDX-License-Identifier: AGPL-3.0-or-later */
(() => {
  'use strict';

  const mobileQuery = window.matchMedia('(max-width: 760px)');
  const app = document.getElementById('app');
  const bottomNav = document.getElementById('mobileBottomNav');
  const moreSheet = document.getElementById('mobileMoreSheet');
  const moreBackdrop = document.getElementById('mobileMoreBackdrop');
  const legendToggle = document.getElementById('mobileLegendToggle');
  const legendCard = document.getElementById('legendCard');
  const legendCount = document.getElementById('mobileLegendCount');
  let mobileInitialized = false;

  const isMobile = () => mobileQuery.matches;

  function invalidateMap() {
    window.dispatchEvent(new Event('resize'));
  }

  function setActiveNav(name) {
    bottomNav?.querySelectorAll('[data-mobile-nav]').forEach(button => {
      const active = button.dataset.mobileNav === name;
      button.classList.toggle('active', active);
      if (active) button.setAttribute('aria-current', 'page');
      else button.removeAttribute('aria-current');
    });
  }

  function closeLegend() {
    document.body.classList.remove('mobile-legend-open');
    legendToggle?.setAttribute('aria-expanded', 'false');
  }

  function closeMore() {
    if (moreSheet) moreSheet.hidden = true;
    if (moreBackdrop) moreBackdrop.hidden = true;
    document.body.classList.remove('mobile-sheet-open');
  }

  function openMore() {
    closeLegend();
    if (moreSheet) moreSheet.hidden = false;
    if (moreBackdrop) moreBackdrop.hidden = false;
    document.body.classList.add('mobile-sheet-open');
    setActiveNav('more');
    setTimeout(() => document.getElementById('closeMobileMore')?.focus(), 0);
  }

  function showMap() {
    closeMore();
    closeLegend();
    app?.classList.add('left-closed');
    app?.classList.remove('right-open');
    document.getElementById('basemapMenu')?.setAttribute('hidden', '');
    document.getElementById('baseMapButton')?.setAttribute('aria-expanded', 'false');
    setActiveNav('map');
    setTimeout(invalidateMap, 260);
  }

  function openLayers(group = null, navName = 'layers') {
    closeMore();
    closeLegend();
    app?.classList.remove('right-open');
    app?.classList.remove('left-closed');
    if (group) {
      group.hidden = false;
      group.classList.add('open');
      group.querySelector('.group-title')?.setAttribute('aria-expanded', 'true');
      setTimeout(() => group.scrollIntoView({ behavior: 'smooth', block: 'start' }), 120);
    }
    setActiveNav(navName);
    setTimeout(invalidateMap, 260);
  }

  function openPriority() {
    const group = document.getElementById('researchPriorityGroup');
    openLayers(group, 'priority');
  }

  function openWellSearch() {
    const input = document.getElementById('wellSearchInput');
    const group = input?.closest('.layer-group');
    openLayers(group, 'well');
    setTimeout(() => {
      input?.scrollIntoView({ behavior: 'smooth', block: 'center' });
      input?.focus({ preventScroll: true });
    }, 330);
  }

  function updateLegendCount() {
    if (!legendCount || !legendCard) return;
    const sections = legendCard.querySelectorAll('.legend-section').length;
    legendCount.textContent = sections ? String(sections) : '';
    legendCount.hidden = sections === 0;
  }

  function updateVersionCopy() {
    document.title = 'PIH MS V2.7.1 · estudo estatístico completo';
    document.querySelector('.brand .version')?.replaceChildren('V2.7.1');
    document.getElementById('authorTitle')?.replaceChildren('PIH MS V2.7.1');
    const ribbon = document.querySelector('.science-ribbon');
    if (ribbon) ribbon.innerHTML = '<strong>PIH MS · V2.7.1</strong><span>Estudo estatístico completo, nova identidade visual e instalação opcional. Conteúdo científico experimental V2.6 preservado.</span>';
    const helpKicker = document.querySelector('#helpModal .modal-kicker');
    if (helpKicker) helpKicker.textContent = 'Ajuda completa · V2.7.1';
    const docsKicker = document.querySelector('#docsModal .modal-kicker');
    if (docsKicker) docsKicker.textContent = 'Documentação integrada · V2.7.1';
    const intro = document.querySelector('#authorModal .project-intro span');
    if (intro) intro.textContent = 'Infraestrutura científica em desenvolvimento. A V2.7.1 torna visível o processo científico completo, integra a nova identidade hexagonal e preserva os resultados experimentais da V2.6.';
    const mobileHelp = {
      help03: 'No celular use a barra inferior. Mapa volta à visão principal. Camadas abre o catálogo completo. Prioridade leva diretamente ao módulo V2.6. Poço abre a busca. Mais reúne estatísticas, documentação, instalação, ajuda, informação e mapa base. A ajuda e a informação também têm acesso direto na barra azul.',
      help04: 'No celular, arraste o mapa com um dedo e use o gesto de pinça para o zoom. As ferramentas do alto formam uma única linha horizontal. Elas enquadram o estado, localizam o dispositivo e trocam o mapa base. O seletor Poço ou Mover fica ao lado.',
      help05: 'No celular as camadas abrem em uma folha de largura total. O único botão Legenda reúne a leitura de cores e símbolos com o controle das camadas visíveis. A transparência altera apenas a aparência do mapa.',
      help09: 'No celular as fichas abrem em uma folha de largura total e podem ser fechadas com Ver mapa. Em telas amplas aparecem à direita. Elas mostram prioridade, confiança, bloqueios, ações recomendadas, procedência e limites.',
      help10: 'No celular toque em Poço na barra inferior. Em telas amplas use Poço no menu superior. Pesquise por ID SIAGAS, município, localidade, nome ou aquífero. Um ID numérico completo permite tentar a abertura direta da ficha.',
      help11: 'Abra Legenda e alterne entre Legenda e Camadas visíveis. A transparência pode variar entre 10 e 100 por cento sem alterar valores científicos. Cinza representa UNKNOWN, vermelho P1 ou C1, laranja P2 ou C2, roxo P3 ou C3, turquesa P4 ou C4 e verde P5 ou C5.',
      help12: 'A visão geral apresenta os principais gráficos. Estudo completo revela arquivos, matrizes, etapas, cálculos, resultados e limites. A opção 20 tabelas mantém os resumos auditados.',
      help18: 'A navegação documental abre sobre o mapa e mantém o mesmo cabeçalho, menu e tamanho de leitura. A V2.7.1 acrescenta o estudo estatístico completo e o novo símbolo sem alterar os resultados científicos experimentais da V2.6.'
    };
    Object.entries(mobileHelp).forEach(([id, text]) => {
      const paragraph = document.querySelector(`#${id} p`);
      if (paragraph) paragraph.textContent = text;
    });
  }

  function collapseGroupsForMobile() {
    document.querySelectorAll('.layer-group').forEach(group => {
      group.classList.remove('open');
      group.querySelector('.group-title')?.setAttribute('aria-expanded', 'false');
    });
  }

  function setCompactMapLabels(compact) {
    const select = document.getElementById('selectWellMode');
    const move = document.getElementById('moveMapMode');
    if (select) select.textContent = compact ? '⌖ Poço' : '⌖ Selecionar poço';
    if (move) move.textContent = compact ? '✋ Mover' : '✋ Mover mapa';
  }

  function initializeMobile() {
    if (!isMobile()) {
      document.body.classList.remove('mobile-ui', 'mobile-sheet-open', 'mobile-legend-open');
      closeMore();
      setCompactMapLabels(false);
      return;
    }
    document.body.classList.add('mobile-ui');
    setCompactMapLabels(true);
    if (!mobileInitialized) {
      collapseGroupsForMobile();
      showMap();
      mobileInitialized = true;
    }
    updateLegendCount();
  }

  bottomNav?.addEventListener('click', event => {
    const button = event.target.closest('[data-mobile-nav]');
    if (!button) return;
    const action = button.dataset.mobileNav;
    if (action === 'map') showMap();
    else if (action === 'layers') openLayers();
    else if (action === 'priority') openPriority();
    else if (action === 'well') openWellSearch();
    else if (action === 'more') openMore();
  });

  document.getElementById('mobileViewMap')?.addEventListener('click', showMap);
  document.getElementById('mobileViewMapFromFicha')?.addEventListener('click', showMap);
  document.getElementById('closeMobileMore')?.addEventListener('click', () => {
    closeMore();
    setActiveNav('map');
  });
  moreBackdrop?.addEventListener('click', () => {
    closeMore();
    setActiveNav('map');
  });

  legendToggle?.addEventListener('click', () => {
    const open = document.body.classList.toggle('mobile-legend-open');
    legendToggle.setAttribute('aria-expanded', String(open));
    if (open) closeMore();
  });

  document.querySelector('.mobile-action-grid')?.addEventListener('click', event => {
    const button = event.target.closest('[data-mobile-action]');
    if (!button) return;
    const action = button.dataset.mobileAction;
    if (['statistics', 'documentation', 'help', 'information', 'install'].includes(action)) closeMore();
    else if (action === 'basemap') {
      closeMore();
      showMap();
      document.getElementById('baseMapButton')?.click();
    } else if (action === 'clear') {
      document.getElementById('clearOptional')?.click();
      closeMore();
      showMap();
    }
  });

  document.getElementById('closeLayers')?.addEventListener('click', () => setActiveNav('map'));
  document.getElementById('closeFicha')?.addEventListener('click', () => setActiveNav('map'));

  document.addEventListener('keydown', event => {
    if (event.key !== 'Escape' || !isMobile()) return;
    if (!moreSheet?.hidden) {
      closeMore();
      setActiveNav('map');
    } else if (document.body.classList.contains('mobile-legend-open')) closeLegend();
  });

  new MutationObserver(updateLegendCount).observe(legendCard, { childList: true, subtree: true });
  mobileQuery.addEventListener?.('change', initializeMobile);
  updateVersionCopy();
  initializeMobile();
})();
