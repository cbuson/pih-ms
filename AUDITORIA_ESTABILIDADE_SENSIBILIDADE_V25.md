# Auditoria da entrega PIH MS V2.5

## Escopo

A auditoria verifica cálculo, cardinalidade, denominadores, estados UNKNOWN, consistência cartográfica, documentação, visor e ausência de agregação indevida.

## Controles aprovados

- 14.284 pontos fixos de suporte
- 3.877 poços canônicos provisórios
- cinco perguntas separadas
- cinco escalas calculadas diretamente
- quatro origens comparadas
- 39 requisitos documentais
- 357.100 pares suporte, escala e pergunta
- 71.420 pares suporte e pergunta
- 557.076 pares suporte e requisito
- 45.145 pares célula e pergunta
- 100 controles de origem, escala e pergunta
- 9.029 células da família principal O00
- 916 campos no dicionário mestre
- 17 resumos disponíveis no visor

As partições de estado somam exatamente 14.284 em cada um dos 100 controles. Os cinco GeoJSON cartográficos conservam 3.763, 2.525, 1.537, 791 e 413 células.

## UNKNOWN

A persistência de um bloqueio só usa escalas em que a célula do ponto de suporte contém ao menos um poço. Pontos sem escala observável permanecem `UNKNOWN_SEM_ESCALA_OBSERVAVEL`. Nenhum UNKNOWN foi convertido em zero.

## Integridade científica

- nenhum peso
- nenhum score PIH
- nenhuma prioridade
- nenhum potencial aquífero
- nenhuma interpolação ou predição
- nenhuma escala final
- nenhuma origem final
- nenhuma representatividade territorial inferida
- nenhuma ausência documental convertida em ausência física

## Visor

Foram verificados sintaxe JavaScript, identificadores HTML, seletores, contratos de campos, arquivos GeoJSON, fichas, estatísticas e vínculos metodológicos. A camada V2.5 oferece cinco escalas, cinco perguntas e seis métricas sem substituir os módulos anteriores.

A captura automática do visor renderizado não pôde ser executada porque o ambiente não possui navegador Chromium instalado. Não foi instalado software adicional. Essa limitação é visual e não afeta os controles estáticos, cartográficos e funcionais executados sobre os arquivos.

## Resultado

A entrega é aprovada para publicação como V2.5 de estabilidade e sensibilidade, desde que permaneçam visíveis os limites metodológicos documentados.
