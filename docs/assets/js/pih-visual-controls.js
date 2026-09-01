/* SPDX-License-Identifier: AGPL-3.0-or-later */
(() => {
  'use strict';

  const toggle = document.getElementById('activeLayersToggle');
  const count = document.getElementById('activeLayersToggleCount');
  const sheet = document.getElementById('activeLayersSheet');
  const backdrop = document.getElementById('activeLayersBackdrop');
  const closeButton = document.getElementById('closeActiveLayers');
  const list = document.getElementById('activeLayersList');
  const status = document.getElementById('activeLayersStatus');
  const resetAll = document.getElementById('resetActiveLayerOpacity');
  const openCatalog = document.getElementById('openLayerCatalog');
  const tabs = [...document.querySelectorAll('[data-map-display-tab]')];
  const legendPanel = document.getElementById('mapLegendPanel');
  const layersPanel = document.getElementById('mapVisibleLayersPanel');
  const pendingOpacity = new Map();

  if (!toggle || !sheet || !backdrop || !list || !legendPanel || !layersPanel) return;

  const api = () => window.PIHVisualLayers;
  const kindLabels = { base: 'Base', evidence: 'Evidência', analysis: 'Análise', context: 'Contexto' };

  function announce(message) {
    if (!status) return;
    status.textContent = '';
    window.setTimeout(() => { status.textContent = message; }, 20);
  }

  function showTab(name, focus = false) {
    const legendActive = name === 'legend';
    legendPanel.hidden = !legendActive;
    layersPanel.hidden = legendActive;
    tabs.forEach(tab => {
      const active = tab.dataset.mapDisplayTab === name;
      tab.classList.toggle('active', active);
      tab.setAttribute('aria-selected', String(active));
      tab.tabIndex = active ? 0 : -1;
      if (active && focus) tab.focus();
    });
    if (!legendActive) render();
  }

  function close(restoreFocus = true) {
    sheet.hidden = true;
    backdrop.hidden = true;
    document.body.classList.remove('visual-layers-open');
    toggle.setAttribute('aria-expanded', 'false');
    if (restoreFocus) toggle.focus({ preventScroll: true });
  }

  function open() {
    render();
    sheet.hidden = false;
    backdrop.hidden = false;
    document.body.classList.add('visual-layers-open');
    toggle.setAttribute('aria-expanded', 'true');
    window.setTimeout(() => closeButton?.focus(), 0);
  }

  function setOpacity(key, value, label) {
    const normalized = Math.max(10, Math.min(100, Number(value) || 100));
    api()?.setOpacity(key, normalized);
    announce(`${label} com ${normalized} por cento de opacidade`);
  }

  function scheduleOpacity(key, value, label) {
    window.clearTimeout(pendingOpacity.get(key));
    pendingOpacity.set(key, window.setTimeout(() => {
      pendingOpacity.delete(key);
      setOpacity(key, value, label);
    }, 110));
  }

  function createButton(label, className = '') {
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = label;
    if (className) button.className = className;
    return button;
  }

  function createLayerCard(item) {
    const card = document.createElement('article');
    card.className = 'active-layer-card';
    card.dataset.layerKey = item.key;
    const head = document.createElement('div');
    head.className = 'active-layer-card-head';
    const name = document.createElement('h3');
    name.className = 'active-layer-name';
    name.textContent = item.label;
    const kind = document.createElement('span');
    kind.className = 'active-layer-kind';
    kind.dataset.kind = item.category;
    kind.textContent = kindLabels[item.category] || 'Camada';
    head.append(name, kind);

    const opacityRow = document.createElement('div');
    opacityRow.className = 'active-layer-opacity-row';
    const slider = document.createElement('input');
    slider.type = 'range';
    slider.min = '10';
    slider.max = '100';
    slider.step = '5';
    slider.value = String(item.opacity);
    slider.id = `visual-opacity-${item.key}`;
    slider.setAttribute('aria-label', `Opacidade de ${item.label}`);
    const output = document.createElement('output');
    output.className = 'active-layer-opacity-value';
    output.htmlFor = slider.id;
    output.textContent = `${item.opacity}%`;
    opacityRow.append(slider, output);

    const presets = document.createElement('div');
    presets.className = 'active-layer-presets';
    [25, 50, 75, 100].forEach(value => {
      const button = createButton(`${value}%`);
      button.setAttribute('aria-pressed', String(Number(item.opacity) === value));
      button.addEventListener('click', () => {
        slider.value = String(value);
        output.textContent = `${value}%`;
        presets.querySelectorAll('button').forEach(candidate => candidate.setAttribute('aria-pressed', String(candidate === button)));
        setOpacity(item.key, value, item.label);
      });
      presets.append(button);
    });

    slider.addEventListener('input', () => {
      output.textContent = `${slider.value}%`;
      presets.querySelectorAll('button').forEach(button => button.setAttribute('aria-pressed', String(button.textContent === `${slider.value}%`)));
      scheduleOpacity(item.key, slider.value, item.label);
    });
    slider.addEventListener('change', () => {
      window.clearTimeout(pendingOpacity.get(item.key));
      pendingOpacity.delete(item.key);
      setOpacity(item.key, slider.value, item.label);
    });

    const actions = document.createElement('div');
    actions.className = 'active-layer-actions';
    const front = createButton('Trazer à frente');
    front.addEventListener('click', () => {
      api()?.bringToFront(item.key);
      announce(`${item.label} trazida à frente dentro da sua ordem cartográfica`);
    });
    const remove = createButton('Remover do mapa', 'remove-layer');
    remove.addEventListener('click', async () => {
      remove.disabled = true;
      await api()?.remove(item.key);
      announce(`${item.label} removida do mapa`);
      render();
    });
    actions.append(front, remove);
    card.append(head, opacityRow, presets, actions);
    return card;
  }

  function render() {
    const items = api()?.list?.() || [];
    if (count) count.textContent = String(items.length);
    list.replaceChildren();
    if (!items.length) {
      const empty = document.createElement('div');
      empty.className = 'active-layer-empty';
      empty.textContent = 'Nenhuma camada controlável está visível. Abra o catálogo para escolher camadas.';
      list.append(empty);
      return;
    }
    items.forEach(item => list.append(createLayerCard(item)));
  }

  tabs.forEach(tab => tab.addEventListener('click', () => showTab(tab.dataset.mapDisplayTab)));
  toggle.addEventListener('click', () => sheet.hidden ? open() : close());
  closeButton?.addEventListener('click', () => close());
  backdrop.addEventListener('click', () => close());
  document.addEventListener('keydown', event => {
    if (sheet.hidden) return;
    if (event.key === 'Escape') {
      close();
      return;
    }
    if ((event.key === 'ArrowLeft' || event.key === 'ArrowRight') && tabs.includes(document.activeElement)) {
      event.preventDefault();
      showTab(document.activeElement.dataset.mapDisplayTab === 'legend' ? 'layers' : 'legend', true);
      return;
    }
    if (event.key !== 'Tab') return;
    const focusable = [...sheet.querySelectorAll('button:not([disabled]), input:not([disabled])')].filter(item => item.offsetParent !== null);
    if (!focusable.length) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  });

  resetAll?.addEventListener('click', () => {
    api()?.resetAll();
    announce('Opacidade de todas as camadas visíveis restaurada para 100 por cento');
    render();
  });
  openCatalog?.addEventListener('click', () => {
    close(false);
    const mobileLayers = document.querySelector('[data-mobile-nav="layers"]');
    const desktopLayers = document.getElementById('navLayers');
    if (window.matchMedia('(max-width: 760px)').matches && mobileLayers) mobileLayers.click();
    else desktopLayers?.click();
  });

  window.addEventListener('pih:layers-changed', event => {
    if (event.detail?.reason !== 'opacity' && event.detail?.reason !== 'order') render();
  });
  window.addEventListener('resize', () => { if (!sheet.hidden) render(); });
  showTab('legend');
  render();
  window.setTimeout(render, 800);
  window.setTimeout(render, 2200);
})();
