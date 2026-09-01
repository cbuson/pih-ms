/* SPDX-License-Identifier: AGPL-3.0-or-later */
(() => {
  'use strict';

  const installButton = document.getElementById('pwaInstallButton');
  const title = document.getElementById('pwaInstallTitle');
  const description = document.getElementById('pwaInstallDescription');
  const status = document.getElementById('pwaStatus');
  const moreInstall = document.querySelector('[data-mobile-action="install"]');
  let installPrompt = null;

  const installed = () => window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;
  const isIOS = /iphone|ipad|ipod/i.test(navigator.userAgent);

  function setMessage(message) {
    if (status) status.textContent = message;
  }

  function showInstalled() {
    if (title) title.textContent = 'PIH MS já está instalado';
    if (description) description.textContent = 'Abra o ícone criado na tela inicial para usar a janela própria do aplicativo.';
    if (installButton) {
      installButton.textContent = 'Instalado';
      installButton.disabled = true;
    }
    moreInstall?.classList.add('installed');
    setMessage('A instalação está ativa neste dispositivo. A conexão continua necessária para camadas e conteúdos que ainda não foram abertos.');
  }

  function showPromptReady() {
    if (title) title.textContent = 'Instalação disponível';
    if (description) description.textContent = 'Use o botão para solicitar a instalação ao navegador.';
    if (installButton) {
      installButton.textContent = 'Instalar PIH MS';
      installButton.disabled = false;
    }
    setMessage('O navegador confirmou que a instalação pode ser solicitada.');
  }

  function showManualInstructions() {
    if (title) title.textContent = 'Instalação pelo menu do navegador';
    if (description) description.textContent = isIOS
      ? 'No Safari, abra Compartilhar e escolha Adicionar à Tela de Início.'
      : 'Abra o menu do navegador e procure Instalar aplicativo ou Adicionar à tela inicial.';
    if (installButton) {
      installButton.textContent = 'Ver instrução';
      installButton.disabled = false;
    }
    setMessage('O navegador não ofereceu a solicitação automática. A disponibilidade depende do navegador, do sistema e do acesso por HTTPS.');
  }

  window.addEventListener('beforeinstallprompt', event => {
    event.preventDefault();
    installPrompt = event;
    if (!installed()) showPromptReady();
  });

  window.addEventListener('appinstalled', () => {
    installPrompt = null;
    showInstalled();
  });

  installButton?.addEventListener('click', async () => {
    if (installed()) {
      showInstalled();
      return;
    }
    if (!installPrompt) {
      showManualInstructions();
      return;
    }
    const prompt = installPrompt;
    installPrompt = null;
    await prompt.prompt();
    const choice = await prompt.userChoice;
    if (choice.outcome === 'accepted') setMessage('A instalação foi aceita. O ícone será criado pelo sistema.');
    else setMessage('A instalação foi cancelada. Você pode solicitá-la novamente quando o navegador voltar a oferecer essa opção.');
    if (!installed()) showManualInstructions();
  });

  if ('serviceWorker' in navigator && window.isSecureContext) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('./service-worker.js', { scope: './' }).catch(error => {
        setMessage('A interface continua funcionando, mas o recurso de instalação não pôde ser preparado neste acesso.');
        console.error('PIH MS service worker', error);
      });
    });
  } else if (!window.isSecureContext) {
    setMessage('A instalação exige acesso por HTTPS ou localhost.');
  }

  if (installed()) showInstalled();
  else showManualInstructions();
})();
