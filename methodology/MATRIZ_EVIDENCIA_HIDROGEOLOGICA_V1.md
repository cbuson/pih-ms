# PIH MS

## Matriz de Evidência Hidrogeológica V1

Data de corte 29 de agosto de 2026.

Esta fase cria camadas independentes de disponibilidade e qualidade documental. Não calcula prioridade, peso, índice, interpolação ou favorabilidade aquífera.

Princípios de leitura

- Ausência de dado não significa ausência de água subterrânea
- Predição não é observação
- Interpolação não é evidência observada
- Poço cadastrado não é poço com informação hidrogeológica suficiente
- Uma camada de disponibilidade não certifica a qualidade científica do parâmetro
- Cada domínio será agregado às malhas separadamente

## E01 · Poços canônicos provisórios

Pergunta científica

Quantos identificadores SIAGAS espacialmente utilizáveis existem

Fonte

SIAGAS_MS_20260814 + AUDITORIA_V1

Regra de inclusão

ID SIAGAS canônico provisório com coordenadas numéricas

Regra de exclusão

Nenhum ID é removido por possível duplicação física nesta fase

Número de feições

3877

Geometria

Pontos. Cada feição mantém o identificador canônico provisório SIAGAS.

Valor principal

presença da evidência

Unidade

não aplicável

Limitações

ID digital não demonstra independência física entre poços

Preparação para malha

COUNT_DISTINCT(well_id)

Estado

Camada derivada de evidência V1. Nenhuma prioridade foi calculada.

## E02 · Profundidade positiva informada

Pergunta científica

Onde existe profundidade total positiva no snapshot atual

Fonte

SIAGAS_MS_20260814

Regra de inclusão

num_profundidade numérico e maior que zero

Regra de exclusão

Nulo, vazio e zero não entram nesta camada

Número de feições

3414

Geometria

Pontos. Cada feição mantém o identificador canônico provisório SIAGAS.

Valor principal

depth_m

Unidade

m

Limitações

Profundidade total não equivale a intervalo captado nem cobertura vertical

Preparação para malha

COUNT_DISTINCT(well_id); MEDIAN(depth_m); P10/P90 somente em análise de malha

Estado

Camada derivada de evidência V1. Nenhuma prioridade foi calculada.

## E03 · Aquífero informado no cadastro

Pergunta científica

Onde o cadastro SIAGAS informa um nome de aquífero

Fonte

SIAGAS_MS_20260814

Regra de inclusão

str_aquifero não vazio

Regra de exclusão

Nomes vazios não entram

Número de feições

3097

Geometria

Pontos. Cada feição mantém o identificador canônico provisório SIAGAS.

Valor principal

aquifer_informed

Unidade

text

Limitações

O nome cadastral pode usar taxonomias diferentes e não é reclassificado automaticamente

Preparação para malha

COUNT_DISTINCT(well_id); DIVERSITY(aquifer_informed) sem interpretar diversidade como qualidade

Estado

Camada derivada de evidência V1. Nenhuma prioridade foi calculada.

## E04 · Nível estático disponível

Pergunta científica

Onde existe valor numérico de nível estático no snapshot atual

Fonte

SIAGAS_MS_20260814

Regra de inclusão

NE numérico presente

Regra de exclusão

Ausência do campo não é convertida em zero

Número de feições

3213

Geometria

Pontos. Cada feição mantém o identificador canônico provisório SIAGAS.

Valor principal

static_level_m

Unidade

m

Limitações

A camada indica disponibilidade. A data de medição não está disponível na extração plana e 33 zeros permanecem para revisão

Preparação para malha

COUNT_DISTINCT(well_id); zero_count separado; não interpolar nesta fase

Estado

Camada derivada de evidência V1. Nenhuma prioridade foi calculada.

## E05 · Nível dinâmico disponível

Pergunta científica

Onde existe valor numérico de nível dinâmico

Fonte

SIAGAS_MS_20260814

Regra de inclusão

ND numérico presente

Regra de exclusão

Ausência do campo não é convertida em zero

Número de feições

3180

Geometria

Pontos. Cada feição mantém o identificador canônico provisório SIAGAS.

Valor principal

dynamic_level_m

Unidade

m

Limitações

A camada indica disponibilidade. Sem contexto completo do ensaio o valor não é interpretado isoladamente

Preparação para malha

COUNT_DISTINCT(well_id); zero_count separado; não interpolar nesta fase

Estado

Camada derivada de evidência V1. Nenhuma prioridade foi calculada.

## E06 · Vazão específica não negativa

Pergunta científica

Onde existe valor de vazão específica não negativo

Fonte

SIAGAS_MS_20260814 + AUDITORIA_V1

Regra de inclusão

Valor numérico maior ou igual a zero

Regra de exclusão

Três valores negativos foram excluídos da camada derivada e permanecem na fonte com flag de revisão

Número de feições

3051

Geometria

Pontos. Cada feição mantém o identificador canônico provisório SIAGAS.

Valor principal

specific_capacity

Unidade

SOURCE_UNIT_NOT_VERIFIED

Limitações

Unidade ainda não congelada documentalmente. Não comparar magnitudes até resolver a unidade

Preparação para malha

COUNT_DISTINCT(well_id); somente presença na primeira malha

Estado

Camada derivada de evidência V1. Nenhuma prioridade foi calculada.

## E07 · Ensaio de bombeamento cadastrado

Pergunta científica

Onde o snapshot enriquecido SGB 2024 informa tipo de ensaio

Fonte

SGB_HIDRO_MS_2024_POCOS

Regra de inclusão

test_type_sgb2024 não vazio

Regra de exclusão

Ausência de tipo não é inferida a partir de NE ou ND

Número de feições

1106

Geometria

Pontos. Cada feição mantém o identificador canônico provisório SIAGAS.

Valor principal

test_type

Unidade

text

Limitações

Existência cadastral do ensaio não demonstra qualidade metodológica nem adequação para estimar parâmetros

Preparação para malha

COUNT_DISTINCT(well_id); COUNT_BY(test_type)

Estado

Camada derivada de evidência V1. Nenhuma prioridade foi calculada.

## E08 · Ensaio com metadados mínimos de cadastro

Pergunta científica

Onde o registro contém um conjunto mínimo explícito de metadados de ensaio

Fonte

SGB_HIDRO_MS_2024_POCOS

Regra de inclusão

Tipo + data + NE + ND + vazão estabilizada presentes

Regra de exclusão

Não exige método interpretativo porque ele está disponível em apenas dois registros

Número de feições

1096

Geometria

Pontos. Cada feição mantém o identificador canônico provisório SIAGAS.

Valor principal

test_type

Unidade

text

Limitações

Esta é uma classe documental, não uma certificação de validade hidrogeológica do ensaio

Preparação para malha

COUNT_DISTINCT(well_id); no futuro separar presença de método e duração

Estado

Camada derivada de evidência V1. Nenhuma prioridade foi calculada.

## E09 · Transmissividade informada

Pergunta científica

Onde existe número de transmissividade no snapshot histórico enriquecido

Fonte

SGB_HIDRO_MS_2024_POCOS

Regra de inclusão

transmissivity_sgb2024 numérica

Regra de exclusão

Nulo não entra. Zero permanece com flag de revisão

Número de feições

51

Geometria

Pontos. Cada feição mantém o identificador canônico provisório SIAGAS.

Valor principal

transmissivity

Unidade

SOURCE_UNIT_NOT_VERIFIED

Limitações

Unidade e método não estão documentados para a maioria. A camada mapeia disponibilidade, não qualidade do parâmetro

Preparação para malha

COUNT_DISTINCT(well_id); zero_count separado; magnitude não agregada até congelar unidade

Estado

Camada derivada de evidência V1. Nenhuma prioridade foi calculada.

## E10 · Evidência hidroquímica e físico-química parcial

Pergunta científica

Onde existe pelo menos um campo físico-químico ou químico na extração atual

Fonte

SIAGAS_MS_20260814

Regra de inclusão

Pelo menos um entre pH, condutividade elétrica, temperatura, turbidez ou parâmetro químico exposto

Regra de exclusão

Ausência de parâmetro não é zero

Número de feições

2053

Geometria

Pontos. Cada feição mantém o identificador canônico provisório SIAGAS.

Valor principal

available_count

Unidade

count

Limitações

Não representa análise hidroquímica completa. O parâmetro químico massivo identificado é sólidos dissolvidos totais

Preparação para malha

COUNT_DISTINCT(well_id); COUNT_BY(available_fields); não combinar analitos diferentes

Estado

Camada derivada de evidência V1. Nenhuma prioridade foi calculada.

## E11 · Última evidência hidrogeológica datada

Pergunta científica

Onde existe data explícita de ensaio hidráulico ou amostragem/análise química e qual é a mais recente

Fonte

SGB_HIDRO_MS_2024_POCOS

Regra de inclusão

Pelo menos uma data válida entre ensaio, coleta ou análise

Regra de exclusão

Datas de perfuração, cadastro e instalação não são usadas como substitutas de data de observação hidrogeológica

Número de feições

1637

Geometria

Pontos. Cada feição mantém o identificador canônico provisório SIAGAS.

Valor principal

age_years

Unidade

years

Limitações

A camada não demonstra série temporal. Um único evento datado continua sendo uma única observação temporal

Preparação para malha

COUNT_DISTINCT(well_id); MEDIAN(age_years); P25/P75; UNKNOWN preservado

Estado

Camada derivada de evidência V1. Nenhuma prioridade foi calculada.

## E12 · Revisão hidroestratigráfica necessária

Pergunta científica

Onde a comparação entre cadastro e cartografia exige revisão manual

Fonte

SIAGAS_MS_20260814 + SGB_HIDRO_MS_2024 + AUDITORIA_V1

Regra de inclusão

manual_review_required = TRUE na auditoria hidroestratigráfica

Regra de exclusão

Casos consistentes e possíveis consistências sem revisão não entram

Número de feições

1823

Geometria

Pontos. Cada feição mantém o identificador canônico provisório SIAGAS.

Valor principal

comparison_status

Unidade

text

Limitações

Divergência cartográfica não conclusiva não é tratada como contradição. Um poço pode captar unidade profunda

Preparação para malha

COUNT_DISTINCT(well_id); COUNT_BY(comparison_status); nunca converter revisão em ausência de água

Estado

Camada derivada de evidência V1. Nenhuma prioridade foi calculada.
