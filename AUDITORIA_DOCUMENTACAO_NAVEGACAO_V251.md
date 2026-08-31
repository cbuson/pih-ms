# Auditoria da documentação e navegação V2.5.1

## Escopo

Esta auditoria verifica a integração visual e funcional da documentação PIH MS sobre o conteúdo científico V2.5.

Foram avaliados navegação, legibilidade, abertura dos documentos, ajuda, estatísticas, bibliografia, dicionário, autoria, links locais, fichas de poço e preservação dos controles científicos.

## Resultado geral

A V2.5.1 passou na auditoria automatizada.

- 317 verificações da interface aprovadas
- 16 páginas HTML verificadas
- 15 páginas documentais com o mesmo CSS e JavaScript de navegação
- nenhum identificador HTML duplicado
- todos os destinos HTML locais encontrados
- âncoras locais verificadas
- sintaxe dos dois arquivos JavaScript aprovada
- dez páginas metodológicas presentes na navegação comum
- 17 resumos estatísticos atuais
- 916 campos apresentados no dicionário
- 55 referências apresentadas na bibliografia
- 64 fragmentos de ficha
- 3.877 fichas únicas sem duplicação entre fragmentos
- arquivos principais respondendo corretamente por HTTP

## Navegação documental

As páginas de guia, métodos, dicionário, bibliografia, autoria e licença usam agora o mesmo cabeçalho e o mesmo rodapé.

Cada página oferece

- retorno ao mapa
- acesso ao guia
- acesso às estatísticas
- catálogo completo de metodologias
- acesso ao dicionário
- acesso à bibliografia
- acesso à autoria
- índice da página quando há mais de uma seção
- ajuste de tamanho do texto
- botão de retorno ao início

No visor principal os documentos locais abrem em uma janela ampla sobre o mapa. A mesma página pode ser aberta separadamente em outra janela.

## Legibilidade

O texto documental usa base de 17 pixels em telas amplas e 16,5 pixels em telas de até 720 pixels. O usuário pode escolher texto reduzido, normal ou ampliado. A escolha permanece no navegador.

As tabelas, cartões, menus e títulos possuem regras específicas para telas menores. O menu documental se recolhe no celular e os alvos interativos mantêm dimensão adequada para toque.

## Ajuda e estatísticas

A ajuda explica a documentação integrada e o conteúdo V2.5. O painel estatístico carrega `statistics_v251.json` e apresenta os 17 resumos atuais.

Os quatro resumos acrescentados pela V2.5 permanecem identificados

- estabilidade entre escalas
- sensibilidade à origem
- persistência dos bloqueios
- contexto hidrogeológico superficial

Nenhum resumo cria nota geral, peso ou prioridade.

## Autoria e identificador

A informação autoral conserva o formato de cartões da janela de informação do aplicativo.

O DOI `10.5281/zenodo.22180863` é apresentado somente como identificador do depósito V2.2.1. A interface informa que a V2.5.1 ainda não possui publicação própria no Zenodo.

## Preservação científica

A auditoria científica V2.5 também foi executada novamente e aprovada.

- cinco perguntas separadas
- cinco escalas
- quatro origens
- 14.284 pontos fixos de suporte
- 3.877 poços
- 17 resumos
- nenhuma escala final
- nenhuma origem final
- nenhum peso
- nenhum score
- nenhuma interpolação
- nenhuma prioridade

## Teste de carregamento

Foram servidos e abertos por HTTP o visor, o guia, o dicionário, a bibliografia, a autoria, a metodologia V2.5, os recursos visuais comuns, o arquivo de estatísticas e um fragmento de fichas. Todos responderam corretamente.

## Limite desta auditoria

Não foi executada inspeção visual em navegador controlado. A auditoria cobre estrutura HTML, CSS responsivo, JavaScript, links, arquivos, cardinalidades, carregamento HTTP e preservação científica.

A revisão final em aparelhos reais deve observar pelo menos um computador, um Android e um iPhone ou iPad. Essa revisão poderá registrar correções pequenas sem recalcular a ciência.

## Instalação no celular

A V2.5.1 ainda não instala como aplicativo. A fase posterior está definida em `PLANO_FASE_FINAL_INSTALACAO_MOVEL.md` e inclui manifesto, ícones, atualização, cache seletivo, modo sem rede, permissões e testes em aparelhos reais.
