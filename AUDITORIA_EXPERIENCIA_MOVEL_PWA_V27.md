# Auditoria de experiência móvel e instalação V2.7

## Escopo

A V2.7 modifica a interface do PIH MS e preserva o conteúdo científico experimental V2.6.

Foram auditados o cabeçalho móvel, os controles do mapa, a legenda, a gestão de camadas visíveis, as estatísticas e o fluxo de instalação como Progressive Web App.

## Problemas confirmados nas capturas móveis

- ajuda e informação não tinham identificação direta na barra azul
- o seletor de interação e as ferramentas do mapa formavam dois eixos visuais concorrentes
- Legenda e Camadas visíveis ocupavam o mapa como duas funções separadas
- a área de estatísticas exigia entrar nas tabelas para perceber a dimensão do projeto
- a instalação móvel ainda não estava integrada ao fluxo principal

## Solução aplicada

### Barra azul

Dois botões táteis de 42 px foram adicionados.

- `?` abre a ajuda completa
- `i` abre informação, autoria, direitos e licenças

Os nomes completos permanecem disponíveis para leitores de tela e como descrição do controle.

### Ferramentas do mapa

No celular, Poço e Mover continuam como um grupo compacto. Enquadrar MS, Minha posição e Mapa base passam a formar uma segunda fila horizontal no mesmo eixo superior.

Zoom continua disponível por gesto. Os botões redundantes de zoom e limpeza permanecem fora da vista móvel.

### Legenda única

Existe um único botão `Legenda` sobre o mapa. Ele abre uma folha inferior com duas vistas.

- Legenda para interpretar símbolos, cores e classes
- Camadas visíveis para controlar transparência, ordem e remoção

A transparência continua limitada entre 10 e 100 por cento e não altera dados, cálculos, classes ou estatísticas.

### Estatísticas visuais

A visão geral é calculada diretamente de `docs/data/statistics/statistics_v26.json`.

Ela apresenta.

- 3.877 poços canônicos
- 9.029 células em cinco escalas
- 14.284 pontos fixos de suporte
- 20 resumos científicos completos
- evidência direta e UNKNOWN nas cinco perguntas
- classes experimentais de prioridade nas cinco escalas
- persistência da evidência entre escalas
- ocupação das células em cada escala
- seis carências documentais decisivas

As 20 tabelas anteriores permanecem completas e acessíveis na mesma janela.

### Instalação PWA

O botão `Instalar PIH MS` foi incluído em Mais.

A instalação.

- cria um ícone na tela inicial
- permite abrir o visor em uma janela própria
- guarda somente a interface essencial
- verifica atualizações quando há conexão

A instalação não baixa automaticamente a base científica completa, não guarda todos os mapas base, não concede acesso à localização e não envia a posição para um servidor próprio do PIH MS.

O service worker exclui `data/`, CSV, GeoJSON, XLSX e ZIP do cache automático. Camadas ainda não abertas podem exigir conexão.

## Controles automatizados

- HTML sem IDs duplicados
- relações ARIA dos novos controles verificadas
- sintaxe dos cinco JavaScript da interface e do service worker verificada com Node.js
- manifesto PWA válido
- ícones PNG em 192 e 512 px
- 20 conjuntos estatísticos preservados
- 9.029 células preservadas
- 45.145 classificações célula e pergunta fechadas
- 32.405 classificações UNKNOWN preservadas
- arquivos científicos comparados com o manifesto SHA-256 da V2.6

## Limite da auditoria

A verificação estrutural, científica e técnica foi concluída. A instalação depende de HTTPS, do navegador e do sistema operacional. Uma prova de conforto em aparelho físico continua recomendada porque barras do navegador, escala de texto e áreas seguras variam entre dispositivos.
