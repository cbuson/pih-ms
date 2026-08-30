# PIH MS

## Estratificação hidrogeológica e comportamento das escalas V1

Data de corte 29 de agosto de 2026.

Esta etapa testa se o comportamento das malhas candidatas permanece comparável quando a evidência é condicionada pelas 16 unidades hidroestratigráficas do Mapa Hidrogeológico SGB 2024 e pelos três domínios hidrolitológicos oficiais. Nenhuma escala é adotada e nenhum score PIH é calculado.

## Princípio central

**EVIDÊNCIA EM OUTRA UNIDADE ≠ EVIDÊNCIA NO ESTRATO LOCAL**

Uma célula pode conter um poço e ainda assim não conter observação do sistema hidrogeológico que ocupa outra parte da mesma célula. Esta etapa mede explicitamente esse mascaramento por agregação.

## Fontes e referência espacial

A estratificação utiliza o Mapa Hidrogeológico do Estado de Mato Grosso do Sul SGB 2024, escala 1:1.000.000, já congelado na FASE P0. As operações métricas são executadas em SIRGAS 2000 / Brazil Polyconic, EPSG 5880.

São utilizados 3.877 poços canônicos provisórios do snapshot SIAGAS auditado e 14.284 pontos fixos de suporte de 5 km para comparação espacial.

## Atribuição dos estratos

Os poços preservam a atribuição espacial à unidade aflorante SGB já registrada na Auditoria Mestra. O domínio hidrolitológico é obtido por interseção espacial com a camada oficial SGB. Pontos de suporte que coincidam de forma ambígua com limites não são forçados a um estrato.

## Cobertura por evidência

Para cada unidade e domínio são contabilizadas E01 a E12. A proporção de uma evidência E_k usa E01 do próprio estrato como denominador quando E01 existe. A proporção não é qualidade nem suficiência.

## Distância à evidência do mesmo estrato

Para um ponto de suporte s pertencente ao estrato h e uma evidência E_k,

`d_h,k(s) = min ||s - e||` para `e` pertencente a `E_k` e ao mesmo estrato `h`.

Se o estrato não contém nenhuma observação E_k, a distância permanece UNKNOWN. Não se usa uma observação de outra unidade para preencher o vazio.

## Mascaramento por agregação

Para cada ponto de suporte e cada escala, definem-se dois estados.

`A_k = 1` quando a célula contém ao menos uma observação E_k de qualquer estrato.

`L_k = 1` quando a mesma célula contém ao menos uma observação E_k atribuída ao estrato local do ponto de suporte.

O mascaramento ocorre quando `A_k = 1` e `L_k = 0`.

A porcentagem de mascaramento é calculada sobre os pontos de suporte com atribuição estratigráfica válida. Ela mede uma consequência cartográfica da agregação e não uma probabilidade de erro geológico.

## Mistura e pureza da célula

A composição das células é calculada por interseção vetorial exata entre a geometria de cada malha e as unidades ou domínios SGB em EPSG 5880.

Uma célula é considerada mista de forma descritiva quando intersecta mais de uma unidade ou domínio. Não é aplicado limiar mínimo de área para declarar a interseção. Por isso esta métrica é deliberadamente sensível a contatos e deve ser lida junto com a pureza ponderada.

Para a unidade h na célula c, a fração é `f_hc = A_hc / A_c`.

A pureza ponderada de uma unidade nas células em que aparece é a média de `100 f_hc` ponderada pela própria área `A_hc`. Não é um índice de qualidade.

## Resultados principais

Serra Geral e Caiuá concentram aproximadamente 76,48 por cento dos 3.877 poços E01. Isto demonstra forte desigualdade de observação entre unidades.

O Grupo Rio Ivaí tem zero poços E01 atribuídos no conjunto auditado. Portanto E01, E07, E09, E10 e E11 permanecem sem observação atribuída nesta unidade nesta base. Isto não significa ausência de água subterrânea.

Nove das 16 unidades não possuem E09 transmissividade informada.

Quando a análise usa distância à evidência da própria unidade, surgem vazios que a distância a qualquer poço pode ocultar. Em Depósitos aluvionares, por exemplo, o P90 da distância a E01 do mesmo estrato é cerca de 217,21 km, enquanto o P90 até qualquer E01 é cerca de 133,42 km. Para E09 a diferença é ainda maior.

## Efeito da escala sobre o mascaramento

No conjunto estadual, o mascaramento E01 por unidade aumenta de 2.64 por cento em 100 km² para 5.00 em 250 km² e 8.74 em 1000 km².

Para E07, o mascaramento por unidade passa de 1.24 para 10.35 por cento entre 100 e 1000 km².

Para E10 passa de 1.81 para 9.56 por cento.

A área estadual situada em células que intersectam mais de uma unidade aumenta de 48.27 por cento em 100 km² para 78.14 em 1000 km².

## Diferença entre domínios

O comportamento não é uniforme. Na malha de 250 km², o mascaramento E01 por domínio é aproximadamente 1.74 por cento no domínio granular, 7.14 no fraturado e 14.34 no cárstico.

Para E10 na mesma escala, os valores são aproximadamente 1.20, 6.87 e 18.03 por cento, respectivamente.

Este resultado impede assumir que uma única escala tenha comportamento equivalente em meios granular, fraturado e cárstico.

## Decisão desta etapa

Nenhuma escala é adotada.

250 km² continua sendo uma candidata central para comparação, mas a estratificação mostra que seu comportamento varia fortemente por domínio e por unidade.

100 e 150 km² continuam úteis como diagnóstico fino.

500 e 1000 km² continuam úteis para persistência regional, mas ampliam mistura e mascaramento.

A próxima decisão deve incorporar representatividade vertical, temporalidade e objetivo específico de cada domínio de conhecimento. Isto poderá conduzir a uma arquitetura multiescalar em vez de uma única malha universal.

## Regras de leitura

AUSÊNCIA DE DADO ≠ AUSÊNCIA DE ÁGUA SUBTERRÂNEA

EVIDÊNCIA EM OUTRA UNIDADE ≠ EVIDÊNCIA NO ESTRATO LOCAL

MASCARAMENTO POR AGREGAÇÃO ≠ COBERTURA REAL

MAIOR CÉLULA ≠ MAIOR CONHECIMENTO

UNIDADE DOMINANTE ≠ ÚNICA UNIDADE DA CÉLULA

NENHUMA ESCALA FOI ADOTADA

NENHUM SCORE PIH FOI CALCULADO

## Referências

Serviço Geológico do Brasil. 2024. Mapa hidrogeológico do estado de Mato Grosso do Sul. Escala 1:1.000.000. SGB.

Fotheringham, A. S., & Wong, D. W. S. 1991. The modifiable areal unit problem in multivariate statistical analysis. Environment and Planning A, 23(7), 1025–1044. https://doi.org/10.1068/a231025

Clark, P. J., & Evans, F. C. 1954. Distance to nearest neighbor as a measure of spatial relationships in populations. Ecology, 35(4), 445–453. https://doi.org/10.2307/1931034
