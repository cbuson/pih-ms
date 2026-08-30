# PIH MS · Documentação vertical e temporal V1

Data de corte 29 de agosto de 2026

## Finalidade

Esta etapa não calcula prioridade hidrogeológica. Ela verifica quanto da evidência disponível permite descrever a dimensão vertical dos poços e a dimensão temporal das observações.

A análise mantém separados cadastro, construção, observação, derivação e série temporal.

## Princípios

Profundidade total não equivale a intervalo captado.

Topo e base brutos não equivalem automaticamente a filtro ou tela.

Um nível sem data de medição não constitui evidência temporal datada.

Uma única medição datada não constitui série temporal.

Cadastro RIMAS não equivale a série RIMAS adquirida.

Amplitude de datas entre poços de uma célula não equivale a duração de uma série em um poço.

UNKNOWN permanece UNKNOWN quando o conjunto adquirido não demonstra o elemento necessário.

## Camadas verticais

V01 reutiliza E02 e indica profundidade total positiva no cadastro auditado. Há 3.414 poços.

V02 indica formação geológica documentada no registro enriquecido SGB 2024. Há 1.425 poços.

V03 indica tipo de penetração documentado. Há 416 poços. Os valores encontrados incluem parcial e total.

V04 indica condição hidráulica documentada. Há 380 poços. Os valores incluem livre, confinado, semi-livre e semi-confinado.

V05 indica tipo de captação documentado. Há 333 poços. Os valores registrados incluem captação única e simultânea.

V06 indica presença simultânea de topo bruto positivo e base bruta maior que o topo. Há 316 poços. Esta camada não interpreta esses campos como intervalo de filtro.

V07 indica diâmetro bruto documentado. Há 412 poços.

V08 representa o intervalo de filtro ou tela efetivamente demonstrado. O conjunto adquirido não contém uma tabela relacional de filtros ou telas que permita produzir esta camada. O estado permanece UNKNOWN.

## Camadas temporais

T01 indica ensaio de bombeamento com data interpretável. Há 1.581 poços.

T02 indica evidência química com data de coleta ou, quando a coleta não está disponível, data de análise. Há 530 poços.

T03 indica medição de nível com `data_medic` associada a `nivel_agua` no conjunto histórico SGB 2024. Há 20 poços. Uma medição isolada não é tratada como série.

T04 indica pelo menos um evento hidrogeológico datado entre ensaio, química ou nível. Há 1.637 poços.

T05 indica evidência datada em pelo menos dois domínios distintos entre ensaio, química e nível. Há 475 poços. Isto representa diversidade documental e não continuidade temporal.

T06 identifica 22 registros cujo campo original `status_rimas` no snapshot SIAGAS 2026 é `Rimas`. Esta camada corrige uma inconsistência da primeira tabela `wells_master`, na qual esse campo havia sido convertido incorretamente para falso. O registro original foi usado como autoridade para esta variável.

T07 representa série temporal demonstrada da mesma variável no conjunto adquirido. Nenhuma série completa foi adquirida nesta etapa. O estado permanece UNKNOWN. Isso não significa que as séries RIMAS não existam em sua fonte original.

## Resultados globais

A profundidade positiva está disponível em aproximadamente 88,06 por cento dos 3.877 poços.

A formação documentada está disponível em aproximadamente 36,76 por cento.

O tipo de penetração está disponível em aproximadamente 10,73 por cento.

A condição hidráulica está disponível em aproximadamente 9,80 por cento.

O tipo de captação está disponível em aproximadamente 8,59 por cento.

Topo e base brutos coerentes aparecem em aproximadamente 8,15 por cento.

Somente aproximadamente 0,52 por cento dos poços possuem uma medição de nível com data explícita no conjunto histórico adquirido.

A evidência hidrogeológica datada T04 aparece em aproximadamente 42,22 por cento dos poços.

Entre os poços com alguma evidência datada, a mediana da idade da evidência mais recente é aproximadamente 23,46 anos no corte de 29 de agosto de 2026.

Nenhuma série temporal completa foi demonstrada com os arquivos atualmente adquiridos.

## Comportamento nas malhas sintéticas

As malhas de 100, 150, 250, 500 e 1000 km² foram calculadas diretamente a partir dos poços.

Em 250 km², entre as células ocupadas por poços, a mediana da proporção de poços com formação documentada é aproximadamente 14,29 por cento.

Na mesma escala, a mediana da proporção de poços com tipo de penetração documentado é zero.

A mediana da proporção de poços com topo e base brutos coerentes também é zero.

A mediana da proporção de poços com alguma evidência hidrogeológica datada é 24 por cento.

A idade mediana da última evidência datada, calculada por célula ocupada e depois resumida entre as células, é aproximadamente 21,22 anos.

Esses resultados mostram que uma célula com vários poços pode continuar muito pouco documentada verticalmente e temporalmente.

## Referências metodológicas institucionais

O USGS National Ground-Water Monitoring Network considera entre os elementos mínimos a profundidade do poço, intervalos de tela, revestimento, data e hora de medição do nível, método e precisão da medição, além de data da amostra, analito, unidade e limite de detecção para qualidade da água.

https://www.usgs.gov/apps/ngwmn/remote-content/content/tipsheets/ngwmn_minimum_data_elements_tip_sheet.pdf

O National Groundwater Information System da Austrália mantém separadamente localização do poço, litologia, construção, hidroestratigrafia e, no explorador, séries de nível e salinidade. O modelo de construção utiliza profundidades de início e fim e identifica a unidade hidrogeológica efetivamente interceptada ou drenada.

https://www.bom.gov.au/water/groundwater/ngis/

https://www.bom.gov.au/water/groundwater/explorer/terminology.shtml

GroundWaterML 2.2 separa poço, construção do poço, observações e ensaios de aquífero, e exige que elementos de construção sejam posicionados ao longo do furo por profundidades de início e fim quando disponíveis.

https://www.ogc.org/standards/gwml2/

https://docs.ogc.org/is/19-013/19-013.html

## Limitações

Não foram adquiridos intervalos de filtros ou telas em estrutura relacional.

Não foram adquiridas séries RIMAS completas.

NE e ND da exportação atual permanecem sem data de medição.

Topo e base do snapshot SGB são preservados como campos brutos e não reinterpretados como filtro.

A amplitude de datas dentro de uma célula descreve apenas a distribuição temporal do conjunto documental. Não representa duração de monitoramento.

Nenhuma destas camadas recebe peso ou classificação de prioridade nesta fase.
