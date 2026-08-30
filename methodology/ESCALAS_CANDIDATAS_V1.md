# PIH MS

## Estudo de escalas candidatas V1

Data de corte 29 de agosto de 2026.

Esta etapa testa cinco áreas nominais de hexágono sob uma geometria sintética controlada. As escalas são 100, 150, 250, 500 e 1000 km². Nenhuma é adotada como escala definitiva do PIH MS nesta etapa.

## Objetivo

O objetivo é medir o compromisso entre resolução espacial, esparsidade de observações, mistura hidrogeológica e sensibilidade ao problema da unidade espacial modificável. O experimento não mede potencial aquífero e não produz prioridade.

## Geometria

Os hexágonos regulares foram construídos em SIRGAS 2000 / Brazil Polyconic, EPSG 5880. Para área nominal A e lado s,

A = 3 sqrt(3) s² / 2

A geometria principal utiliza a origem O00. Para testar sensibilidade ao zoneamento foram utilizados ainda OX25, OY25 e OXY25, deslocados em 25 por cento da largura do hexágono, do espaçamento entre linhas ou de ambos.

As malhas sintéticas são ferramentas de comparação. Não substituem automaticamente as malhas candidatas existentes de 250, 500 e 1000 km².

## Evidências

E01 a E12 são contadas diretamente desde as feições auditadas. Nenhum resultado é herdado de uma escala menor. Para o ensaio de deslocamento de origem foram selecionadas E01, E07, E09 e E10 por representarem cadastro geral, ensaios, parâmetro hidráulico raro e hidroquímica parcial.

## Suporte fixo

A comparação multiescalar usa os mesmos 14.284 pontos de suporte de 5 km empregados na V1.6. Isto permite perguntar se o mesmo lugar é classificado como pertencente a uma célula com ou sem determinada evidência quando a escala muda.

## Heterogeneidade hidrogeológica

A heterogeneidade é avaliada de forma descritiva nos pontos fixos de suporte de 5 km, cada um classificado pela unidade aflorante do Mapa Hidrogeológico SGB 2024. São calculados número de unidades distintas, dominância da unidade mais frequente e entropia normalizada.

Esta é uma aproximação baseada em suporte pontual. Não é uma fração de área exata e não deve substituir um overlay vetorial de detalhe quando esse cálculo for necessário. O mapa SGB 2024 é 1 a 1.000.000. Seus limites não devem ser tratados como precisão local de campo.

## Resultados principais

A porcentagem de células O00 sem E01 diminui sistematicamente quando o hexágono cresce. É 79,43 por cento em 100 km², 73,98 em 150 km², 65,97 em 250 km², 55,25 em 500 km² e 41,89 em 1000 km². Isto não significa que o conhecimento aumente. É um efeito de agregação.

A mistura hidrogeológica no suporte de 5 km aumenta com a área. A proporção de células contendo mais de uma unidade no suporte é aproximadamente 27,27 por cento em 100 km², 35,05 em 150 km², 46,06 em 250 km², 60,56 em 500 km² e 67,80 em 1000 km².

Para E01, o Jaccard mínimo entre deslocamentos de origem cresce de aproximadamente 0,514 em 100 km² para 0,558 em 150 km², 0,612 em 250 km², 0,683 em 500 km² e 0,763 em 1000 km². Escalas maiores são mais estáveis quanto à mera presença, mas fazem isso à custa de maior agregação e mistura espacial.

A comparação O00 entre 100 e 1000 km² mostra Jaccard de presença E01 próximo de 0,333 e aproximadamente 41,76 por cento dos pontos fixos mudam de estado presença ou ausência. O efeito de escala é, portanto, material.

E09 permanece extremamente escassa. Somente cerca de 0,98 por cento das células de 100 km² e 6,78 por cento das células de 1000 km² contêm transmissividade informada. O aumento aparente de cobertura em células maiores é agregação, não aquisição de novos dados.

## Leitura das cinco escalas

100 km² preserva maior detalhe local, mas produz extrema esparsidade e forte sensibilidade à origem.

150 km² continua muito esparsa, embora reduza parcialmente a fragmentação de 100 km².

250 km² ocupa uma posição intermediária entre esparsidade, estabilidade e mistura hidrogeológica. Este resultado transforma 250 km² em uma candidata importante para testes adicionais, não em escala adotada.

500 km² reduz visualmente os vazios, mas aumenta a mistura de unidades hidrogeológicas e a agregação de observações espacialmente distantes.

1000 km² apresenta maior estabilidade de presença e menor proporção de células vazias, mas é a escala com maior risco de mascarar vazios locais e combinar contextos hidrogeológicos distintos.

## Decisão desta etapa

Nenhuma escala é selecionada.

250 km² permanece como candidata central de trabalho porque apresenta um compromisso intermediário e é próxima da ordem de área usada pelo SGB para sua malha de densidade de poços. Essa coincidência institucional não constitui validação.

100 e 150 km² permanecem como escalas de diagnóstico fino.

500 e 1000 km² permanecem como escalas complementares para verificar persistência regional dos padrões.

A próxima decisão requer estratificação por sistema aquífero, análise de representatividade vertical e temporal e confronto com a escala real das fontes utilizadas.

## Regras

AUSÊNCIA DE DADO ≠ AUSÊNCIA DE ÁGUA SUBTERRÂNEA

MAIOR CÉLULA ≠ MAIOR CONHECIMENTO

MAIOR ESTABILIDADE DE PRESENÇA ≠ MELHOR ESCALA

HETEROGENEIDADE NO SUPORTE ≠ INCERTEZA HIDROGEOLÓGICA TOTAL

MALHA SINTÉTICA ≠ MALHA DEFINITIVA

NENHUM SCORE PIH FOI CALCULADO

## Referências metodológicas

Fotheringham, A. S., & Wong, D. W. S. (1991). The modifiable areal unit problem in multivariate statistical analysis. Environment and Planning A, 23(7), 1025–1044. https://doi.org/10.1068/a231025

Clark, P. J., & Evans, F. C. (1954). Distance to nearest neighbor as a measure of spatial relationships in populations. Ecology, 35(4), 445–453. https://doi.org/10.2307/1931034

Serviço Geológico do Brasil. (2024). Mapa hidrogeológico do estado de Mato Grosso do Sul, escala 1:1.000.000. SGB.
