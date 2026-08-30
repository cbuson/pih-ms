# PIH MS

## Estrutura espacial da evidência V1

Data de corte 29 de agosto de 2026.

Esta etapa descreve a distribuição espacial das observações que alimentam E01 a E12. Nenhuma métrica desta etapa é um índice PIH, peso, prioridade, favorabilidade aquífera ou probabilidade de ocorrência de água subterrânea.

## Sistema de referência de cálculo

As operações métricas foram realizadas em SIRGAS 2000 / Brazil Polyconic, EPSG 5880. Os resultados de distância são expressos em quilômetros. As geometrias destinadas ao visor web são cópias reprojetadas para EPSG 4326. Os arquivos fonte não foram alterados.

## 1. Vizinho mais próximo

Para cada poço E01 calcula-se a distância ao poço E01 mais próximo no conjunto estadual auditado. A estatística é agregada por hexágono mediante mediana e percentil 90. Distâncias iguais a zero são preservadas, pois podem indicar coordenadas coincidentes e não devem ser corrigidas automaticamente.

Também se calcula, quando existem pelo menos dois poços na célula, a distância ao vizinho mais próximo restrita aos pontos da própria célula. Esta medida descreve agrupamento local, não qualidade hidrogeológica.

## 2. Suporte espacial multirresolução

A distribuição interna E01 é examinada por quadrículas regulares de 2,5, 5 e 10 km, com origem fixa e documentada. Para cada hexágono são calculados

- número de unidades de suporte ocupadas
- percentagem da área do hexágono interceptada pelas unidades de suporte que contêm pelo menos um poço
- proxy de redundância espacial igual a 1 menos unidades ocupadas dividido pelo número de poços
- entropia normalizada de Shannon entre as unidades ocupadas
- percentagem de poços concentrada na unidade de suporte dominante

Os três tamanhos são mantidos simultaneamente para não transformar a escolha arbitrária de uma única quadrícula interna em verdade física.

A entropia normalizada é

Hn = - soma p_i ln p_i / ln k

quando existem pelo menos duas unidades de suporte ocupadas. Para uma única unidade ocupada a entropia permanece não avaliável. Esta métrica descreve distribuição das contagens, não independência hidrogeológica.

## 3. Distância à evidência e vazios observacionais

Foi criada uma malha de pontos de suporte espaçados 5 km dentro de Mato Grosso do Sul. Para cada ponto de suporte calcula-se a distância ao registro mais próximo de cada camada E01 a E12. Em cada hexágono são armazenadas mediana, P90 e distância máxima.

Uma grande distância indica afastamento espacial da evidência cadastrada considerada. Não demonstra ausência de água, ausência da propriedade hidrogeológica nem prioridade por si só. E12 deve ser lida como distância a registros com flag de revisão hidroestratigráfica, não como vazio de conhecimento.

Quando um fragmento marginal de hexágono não contém centro da malha de suporte de 5 km, utiliza-se apenas para essa célula um ponto representativo interno. O uso desse fallback é registrado no campo gap_support_fallback.

## 4. Cobertura convexa e deslocamento do centro médio

Quando existem três ou mais poços calcula-se a razão entre a área do envoltório convexo dos pontos e a área efetiva da célula. Esta razão é somente descritiva e é sensível ao número de pontos e a valores extremos. Não é tratada como cobertura real.

Também é calculada a distância entre o centro médio dos poços e o centroide da célula, normalizada pelo raio do círculo de área equivalente.

## 5. Estabilidade entre escalas

As malhas originais de 250, 500 e 1000 km² são comparadas sobre a mesma malha de suporte de 5 km. Para cada evidência são calculados

- correlação de Spearman da densidade de evidências por 100 km²
- índice de Jaccard para presença ou ausência de evidência
- percentagem de pontos de suporte cuja presença muda entre escalas

Estas estatísticas quantificam sensibilidade à escala. Não selecionam automaticamente uma escala vencedora.

## 6. Sensibilidade ao zoneamento e MAUP

Como primeiro ensaio de zoneamento foram geradas malhas hexagonais sintéticas de área nominal equivalente a 250, 500 e 1000 km² em EPSG 5880. Para cada área são utilizados quatro posicionamentos de origem

O00

OX25 com deslocamento horizontal igual a 25 por cento da largura do hexágono

OY25 com deslocamento vertical igual a 25 por cento do espaçamento entre linhas

OXY25 com ambos os deslocamentos

Este é um ensaio de sensibilidade e não substitui as malhas oficiais candidatas. São comparadas E01, E07, E09 e E10 por proporção de células ocupadas e concordância de presença sobre a malha fixa de suporte de 5 km.

## 7. Regras de interpretação

AUSÊNCIA DE DADO ≠ AUSÊNCIA DE ÁGUA SUBTERRÂNEA

DISTÂNCIA À EVIDÊNCIA ≠ DISTÂNCIA À ÁGUA

AGRUPAMENTO DE POÇOS ≠ QUALIDADE DO CONHECIMENTO

ENTROPIA ESPACIAL ≠ INFORMAÇÃO HIDROGEOLÓGICA INDEPENDENTE

INTERPOLAÇÃO NÃO FOI UTILIZADA NESTA ETAPA

NENHUM SCORE PIH FOI CALCULADO

## Referências metodológicas

Clark, P. J., & Evans, F. C. (1954). Distance to nearest neighbor as a measure of spatial relationships in populations. Ecology, 35(4), 445–453. https://doi.org/10.2307/1931034

Fotheringham, A. S., & Wong, D. W. S. (1991). The modifiable areal unit problem in multivariate statistical analysis. Environment and Planning A, 23(7), 1025–1044. https://doi.org/10.1068/a231025

Shannon, C. E. (1948). A mathematical theory of communication. Bell System Technical Journal, 27(3), 379–423. https://doi.org/10.1002/j.1538-7305.1948.tb01338.x

Shannon, C. E. (1948). A mathematical theory of communication. Bell System Technical Journal, 27(4), 623–656. https://doi.org/10.1002/j.1538-7305.1948.tb00917.x

Alfonso, L., Ridolfi, E., Gaytan-Aguilar, S., Napolitano, F., & Russo, F. (2017). Entropy applications to water monitoring network design: A review. Entropy, 19(11), 613. https://doi.org/10.3390/e19110613

U.S. Geological Survey. Statistical design of water-level monitoring networks. Circular 1217. https://pubs.usgs.gov/circ/circ1217/html/boxc.html
