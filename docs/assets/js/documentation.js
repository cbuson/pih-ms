(() => {
  'use strict';

  const current = location.pathname.split('/').pop() || 'index.html';
  const methods = [
    ['metodologia-prioridade-investigacao.html', 'Prioridade por pergunta · V2.6'],
    ['metodologia-estabilidade-sensibilidade.html', 'Estabilidade e sensibilidade · V2.5'],
    ['metodologia-suficiencia-pergunta.html', 'Suficiência por pergunta · V2.4'],
    ['metodologia-conhecimento-efetivo.html', 'Conhecimento efetivo · V2.2'],
    ['metodologia-independencia-redundancia.html', 'Independência e redundância · V2.1'],
    ['metodologia-vertical-temporal.html', 'Documentação vertical e temporal'],
    ['metodologia-estratificacao-hidrogeologica.html', 'Estratificação hidrogeológica'],
    ['metodologia-escalas-candidatas.html', 'Escalas candidatas'],
    ['metodologia-estrutura-espacial.html', 'Estrutura espacial'],
    ['metodologia-malhas-evidencia.html', 'Malhas de evidência'],
    ['metodologia-evidencias.html', 'Evidências E01 a E12']
  ];

  const mainLinks = [
    ['index.html', 'Mapa', '_top'],
    ['guia-resultados.html', 'Guia', '_self'],
    ['index.html?open=stats', 'Estatísticas', '_top'],
    ['dicionario-parametros.html', 'Dicionário', '_self'],
    ['bibliografia.html', 'Bibliografia', '_self'],
    ['autoria-direitos.html', 'Autoria', '_self']
  ];

  const esc = value => String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');

  const slug = value => value
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '') || 'secao';

  document.body.classList.add('pih-documentation');

  const skip = document.createElement('a');
  skip.className = 'pih-doc-skip';
  skip.href = '#pih-doc-content';
  skip.textContent = 'Ir para o conteúdo';

  const progress = document.createElement('div');
  progress.className = 'pih-doc-progress';
  progress.setAttribute('aria-hidden', 'true');

  const header = document.createElement('header');
  header.className = 'pih-docbar';
  header.innerHTML = `
    <div class="pih-docbar-inner">
      <a class="pih-doc-brand" href="index.html" target="_top" aria-label="Voltar ao mapa PIH MS">
        <span class="pih-doc-brand-mark" aria-hidden="true">PIH</span>
        <span class="pih-doc-brand-copy"><strong>Documentação PIH MS</strong><small>V2.6.2 · controle visual</small></span>
      </a>
      <button class="pih-doc-menu-toggle" type="button" aria-expanded="false" aria-controls="pihDocNav">Seções</button>
      <nav class="pih-doc-nav" id="pihDocNav" aria-label="Navegação da documentação">
        ${mainLinks.slice(0, 2).map(([href, label, target]) => `<a href="${href}" target="${target}">${label}</a>`).join('')}
        <details class="pih-doc-methods"><summary>Metodologias</summary><div class="pih-doc-method-list">${methods.map(([href, label]) => `<a href="${href}">${label}</a>`).join('')}</div></details>
        ${mainLinks.slice(2).map(([href, label, target]) => `<a href="${href}" target="${target}">${label}</a>`).join('')}
        <div class="pih-doc-reading-tools" aria-label="Tamanho do texto">
          <button type="button" data-doc-font="small" aria-label="Diminuir texto">A−</button>
          <button type="button" data-doc-font="normal" aria-label="Texto normal">A</button>
          <button type="button" data-doc-font="large" aria-label="Aumentar texto">A+</button>
        </div>
      </nav>
    </div>`;

  document.body.prepend(progress);
  document.body.prepend(header);
  document.body.prepend(skip);

  const main = document.querySelector('main') || document.body;
  if (main !== document.body) {
    main.id = main.id || 'pih-doc-content';
    main.tabIndex = -1;
  }

  main.querySelectorAll('table').forEach(table => {
    if (table.closest('.table-wrap')) return;
    const wrapper = document.createElement('div');
    wrapper.className = 'table-wrap';
    table.before(wrapper);
    wrapper.append(table);
  });

  document.querySelectorAll('.pih-doc-nav a, .pih-doc-method-list a').forEach(link => {
    const targetFile = link.getAttribute('href').split('?')[0].split('#')[0];
    if (targetFile === current) link.setAttribute('aria-current', 'page');
  });

  const menuButton = document.querySelector('.pih-doc-menu-toggle');
  menuButton?.addEventListener('click', () => {
    const open = header.classList.toggle('menu-open');
    menuButton.setAttribute('aria-expanded', String(open));
  });

  document.querySelectorAll('.pih-doc-nav a').forEach(link => link.addEventListener('click', () => {
    header.classList.remove('menu-open');
    menuButton?.setAttribute('aria-expanded', 'false');
  }));

  document.addEventListener('click', event => {
    const details = document.querySelector('.pih-doc-methods[open]');
    if (details && !details.contains(event.target)) details.removeAttribute('open');
  });

  const headings = [...main.querySelectorAll('h2')].filter(heading => !heading.closest('.pih-page-nav'));
  if (headings.length > 1) {
    const used = new Set();
    headings.forEach((heading, index) => {
      let id = heading.id || slug(heading.textContent);
      while (used.has(id) || document.querySelectorAll(`#${CSS.escape(id)}`).length > 1) id = `${id}-${index + 1}`;
      heading.id = id;
      used.add(id);
    });
    const pageNav = document.createElement('details');
    pageNav.className = 'pih-page-nav';
    pageNav.innerHTML = `<summary>Nesta página</summary><nav class="pih-page-nav-links" aria-label="Índice desta página">${headings.map(heading => `<a href="#${esc(heading.id)}">${esc(heading.textContent.trim())}</a>`).join('')}</nav>`;
    const intro = [...main.children].find(element =>
      element.matches('header, .hero') || element.querySelector(':scope > h1')
    );
    if (intro) intro.after(pageNav);
    else main.prepend(pageNav);
  }

  let savedSize = 'normal';
  try {
    savedSize = localStorage.getItem('pih-doc-font-size') || 'normal';
  } catch (error) {}
  if (!['small', 'normal', 'large'].includes(savedSize)) savedSize = 'normal';
  document.body.dataset.fontSize = savedSize;

  document.querySelectorAll('[data-doc-font]').forEach(button => button.addEventListener('click', () => {
    const value = button.dataset.docFont;
    document.body.dataset.fontSize = value;
    try { localStorage.setItem('pih-doc-font-size', value); } catch (error) {}
  }));

  const footer = document.createElement('footer');
  footer.className = 'pih-doc-footer';
  footer.innerHTML = `<div class="pih-doc-footer-inner"><div><strong>PIH MS · documentação unificada V2.6.2</strong><small>Prioridade e confiança separadas · UNKNOWN permanece distinto de zero</small></div><div><a href="index.html?open=author" target="_top">Autoria, direitos e licenças</a></div></div>`;
  document.body.append(footer);

  const topButton = document.createElement('button');
  topButton.className = 'pih-doc-top';
  topButton.type = 'button';
  topButton.setAttribute('aria-label', 'Voltar ao início');
  topButton.textContent = '↑';
  topButton.addEventListener('click', () => scrollTo({ top: 0, behavior: 'smooth' }));
  document.body.append(topButton);

  const updateScroll = () => {
    const distance = document.documentElement.scrollHeight - innerHeight;
    const ratio = distance > 0 ? Math.min(1, Math.max(0, scrollY / distance)) : 0;
    progress.style.width = `${ratio * 100}%`;
    topButton.classList.toggle('visible', scrollY > 520);
  };
  addEventListener('scroll', updateScroll, { passive: true });
  addEventListener('resize', updateScroll);
  updateScroll();
})();
