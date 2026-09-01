# Auditoria de navegação móvel PIH MS V2.6.1

## Escopo

Revisão da experiência do visor em celular a partir das capturas reais fornecidas em 31 de agosto de 2026 e da inspeção do HTML, CSS e JavaScript da V2.6.

Nenhum dado, requisito, estado, classe, regra de prioridade ou resultado científico foi recalculado.

## Problemas confirmados nas capturas

1. O cabeçalho ocupava espaço com sete controles representados quase somente por símbolos.
2. A faixa científica reduzia ainda mais a altura útil do mapa.
3. Seis controles flutuantes formavam uma coluna visualmente dominante.
4. O seletor do modo do mapa ocupava grande parte da largura.
5. A legenda aberta cobria a maior parte do mapa.
6. O painel de camadas ocupava 86 por cento da largura e deixava uma faixa inútil do mapa.
7. Os controles do mapa continuavam visíveis ao lado do painel.
8. Muitos grupos de camadas começavam abertos.
9. A busca, os textos auxiliares e os títulos não tinham uma hierarquia móvel suficiente.
10. Faltava um acesso direto ao novo módulo de prioridade V2.6.
11. As fichas laterais conservavam uma lógica de interface de computador.
12. O modo escuro automático do navegador alterava de forma severa a identidade visual.

## Arquitetura adotada

### Primeira tela

O visor começa com o mapa completo. Os painéis de camadas e fichas permanecem fechados.

### Barra inferior

A navegação móvel tem cinco destinos estáveis.

- Mapa
- Camadas
- Prioridade
- Pozo
- Mais

A prioridade ocupa uma posição principal porque é o novo resultado operacional da V2.6.

### Painel de camadas

O painel abre como uma folha de largura completa. Os grupos começam recolhidos. A busca e o contador permanecem fixos durante a rolagem. O botão Ver mapa permite voltar sem depender do símbolo de fechamento.

### Legenda

A legenda começa recolhida. Um botão visível informa sua existência e o número de seções ativas. Quando aberta, ocupa no máximo uma parte controlada da tela.

### Controles do mapa

O gesto de pinça substitui os botões de zoom como interação principal. Permanecem visíveis enquadrar MS, minha posição e mapa base. Limpar camadas passa para o menu Mais.

### Fichas

As fichas abrem em largura completa. Os pares campo e valor passam a uma só coluna. Títulos, notas, alertas e controles expansíveis foram ampliados.

### Documentação

Todas as páginas conservam o mesmo cabeçalho e a mesma navegação. O menu móvel tem altura limitada e rolagem própria. As tabelas recebem um contêiner horizontal para evitar que comprimam o texto.

## Acessibilidade e ergonomia

- alvos táteis mínimos de 44 px
- áreas seguras inferiores mediante safe area inset
- estados ativos visíveis e anunciados com aria current
- etiquetas textuais sob os ícones
- fechamento mediante Escape quando existe teclado
- respeito à preferência de movimento reduzido
- contraste conservado em superfícies claras
- color scheme declarado como only light

## Verificações executadas

- sintaxe dos três arquivos JavaScript principais
- presença e unicidade dos identificadores da interface
- cinco destinos da barra inferior
- abertura móvel de Estatísticas, Documentação, Ajuda e Informação como painéis sobre o mapa
- dezesseis páginas documentais com o mesmo CSS e JavaScript de navegação
- adaptação horizontal automática das tabelas documentais
- presença das áreas seguras e dos alvos táteis mínimos
- preservação por SHA-256 de 522 arquivos científicos da V2.6
- preservação de 9.029 células, 45.145 pares célula-pergunta, 3.877 poços e 39 requisitos

A arquitetura foi definida a partir das duas capturas reais fornecidas. O navegador remoto desta sessão bloqueou a abertura do servidor local. Por isso, a inspeção visual final da V2.6.1 publicada deve ser repetida em um aparelho Android antes de iniciar a fase PWA.

## Limites

A V2.6.1 não instala o aplicativo, não cria service worker e não configura o manifesto PWA. Essa fase requer uma auditoria separada de funcionamento sem conexão, tamanho de cache, atualizações e armazenamento móvel.

## Resultado

A navegação móvel deixa de ser uma redução da interface de computador. Passa a ser uma interface própria centrada no mapa, na prioridade por pergunta, na consulta de camadas e na leitura de fichas.
