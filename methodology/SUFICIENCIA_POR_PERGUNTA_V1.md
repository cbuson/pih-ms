# PIH MS · Suficiência por pergunta · V1

## Estado metodológico

A V2.4 transforma a matriz de conhecimento efetivo em cinco avaliações condicionadas por pergunta. Ela não agrega as nove dimensões em uma nota e não calcula prioridade de investigação.

**SUFICIÊNCIA DOCUMENTAL LOCAL ≠ REPRESENTATIVIDADE TERRITORIAL**  
**UM REGISTRO COMPLETO ≠ UMA CÉLULA CONHECIDA**  
**CONTAGEM DE REQUISITOS ≠ SCORE**  
**ASSOCIAÇÃO ENTRE CAMPOS ≠ INDEPENDÊNCIA**  
**UNKNOWN ≠ ZERO**

## 1. Objetivo

O objetivo é responder uma pergunta anterior à priorização.

> Quais perguntas hidrogeológicas podem ser abordadas com o conjunto adquirido, em que nível documental e sob quais bloqueios explícitos?

A suficiência é avaliada separadamente para nível de água, propriedades hidráulicas, hidroquímica, geometria aquífera e monitoramento temporal. Cada pergunta exige um conjunto próprio de requisitos críticos. Não existe um limiar universal de quantidade de poços.

## 2. Universo e continuidade

- corte dos dados em 2026-08-29
- 3.877 `well_id` canônicos provisórios
- cinco malhas `SCALE_PRIMARY_O00_V1`
- 3.763 células em 100 km²
- 2.525 células em 150 km²
- 1.537 células em 250 km²
- 791 células em 500 km²
- 413 células em 1000 km²
- 9.029 células no conjunto das cinco escalas
- 45.145 pares célula-pergunta
- nove dimensões preservadas separadamente

A associação entre poço e célula reutiliza `effective_knowledge_assignment_audit.csv`. Nenhum ponto é reassociado e nenhuma escala é derivada de outra.

## 3. Quatro níveis que não podem ser confundidos

### 3.1 Evidência direta

Indica apenas a presença do tipo de registro central da pergunta.

- Q01 usa nível estático informado
- Q02 usa capacidade específica não negativa, ensaio cadastrado ou transmissividade informada
- Q03 usa evidência hidroquímica ou físico-química parcial
- Q04 usa profundidade positiva ou metadado vertical
- Q05 usa ao menos um evento hidrogeológico datado

Evidência direta não demonstra suficiência.

### 3.2 Mínimo documental do registro

O mínimo é uma conjunção não compensatória. Todos os requisitos críticos da pergunta precisam estar demonstrados no mesmo registro.

Para um poço \(w\), uma pergunta \(q\) e o conjunto de requisitos críticos \(R_q\)

\[
M_{wq}=\bigwedge_{r\in R_q} I_{wr}
\]

onde \(I_{wr}=1\) somente quando o requisito está demonstrado pelas regras atuais.

Um requisito demonstrado não compensa outro requisito UNKNOWN. Não existem pesos e a contagem de requisitos demonstrados não é utilizada para ordenar poços.

### 3.3 Estado documental local da célula

Para cada célula \(c\), pergunta \(q\) e conjunto de poços associados \(W_c\)

\[
N^{mín}_{cq}=\sum_{w\in W_c} M_{wq}
\]

A célula recebe um dos seguintes estados.

| Estado | Regra | Leitura permitida |
|---|---|---|
| `UNKNOWN_SEM_POCOS_NO_CONJUNTO_AUDITADO` | nenhum poço associado | o conjunto adquirido não contém poço na célula |
| `UNKNOWN_SEM_EVIDENCIA_DIRETA_DA_PERGUNTA` | há poço, mas não há evidência direta da pergunta | ausência documental condicionada ao conjunto |
| `SOMENTE_EVIDENCIA_PARCIAL` | há evidência direta, mas nenhum poço atende ao mínimo | presença documental parcial |
| `MINIMO_DOCUMENTAL_LOCAL_PRESENTE_NAO_REPRESENTATIVO` | ao menos um poço atende ao mínimo | presença local de registro mínimo, sem inferência territorial |

Quando `n_wells = 0`, contagens podem ser zero como contagem do conjunto. Percentuais permanecem vazios.

### 3.4 Representatividade territorial

A representatividade exige mais que presença documental. Ela depende do objetivo da rede, do estrato, da cobertura espacial e temporal, da independência das observações e do desenho de amostragem.

Na V2.4, independência hidrogeológica permanece não demonstrada nos 3.877 poços. Também não foi adquirido um desenho amostral capaz de transformar a presença local em inferência válida para toda a célula. Por isso `cell_representativeness_state` permanece UNKNOWN em todas as células.

## 4. Perguntas e requisitos críticos

### 4.1 Q01 · Nível e profundidade da água

Pergunta operacional

> O registro permite interpretar uma observação pontual de nível de água no contexto construtivo e hidrogeológico do poço?

Requisitos críticos

1. coordenada válida
2. nível estático informado
3. data explícita da medição
4. profundidade total positiva
5. intervalo captado demonstrado
6. atribuição hidroestratigráfica consistente nas regras atuais
7. ausência de valor objetivamente inválido nas regras atuais

Um nível sem data não forma uma superfície contemporânea. Profundidade total não substitui intervalo captado. Um nível datado isolado não forma série temporal.

### 4.2 Q02 · Propriedades hidráulicas

Pergunta operacional

> O registro permite interpretar uma propriedade hidráulica derivada de ensaio de poço?

Requisitos críticos

1. coordenada válida
2. intervalo captado demonstrado
3. atribuição hidroestratigráfica consistente
4. ensaio com metadados mínimos
5. data explícita do ensaio
6. método interpretativo documentado
7. parâmetro hidráulico informado
8. unidade verificada documentalmente
9. ausência de valor objetivamente inválido nas regras atuais

Capacidade específica, nível dinâmico e transmissividade informada permanecem evidências diferentes. Um valor reportado não demonstra o método, as hipóteses ou a unidade.

### 4.3 Q03 · Hidroquímica

Pergunta operacional

> O resultado pode ser interpretado no contexto do poço, da amostragem e do controle de qualidade?

Requisitos críticos

1. coordenada válida
2. intervalo captado demonstrado
3. atribuição hidroestratigráfica consistente
4. amostra ou resultado parcial presente
5. data de coleta ou análise
6. parâmetro identificado
7. unidade verificada documentalmente
8. amostragem, método e QA analítico demonstrados
9. ausência de valor objetivamente inválido nas regras atuais

E10 continua sendo evidência parcial. Não equivale a painel completo, campanha comparável ou condição de qualidade da célula.

### 4.4 Q04 · Geometria e estratigrafia do aquífero

Pergunta operacional

> O poço possui informação vertical suficiente para relacionar construção, perfil e intervalo efetivamente captado?

Requisitos críticos

1. coordenada válida
2. profundidade positiva
3. perfil litológico explícito adquirido
4. intervalo captado demonstrado
5. atribuição hidroestratigráfica consistente
6. ausência de valor objetivamente inválido nas regras atuais

A unidade aflorante do mapa SGB 2024 é referência espacial em 1:1.000.000. Ela não demonstra o aquífero captado em profundidade.

### 4.5 Q05 · Monitoramento temporal

Pergunta operacional

> Existe uma série adquirida da mesma variável que permita estudar mudança no tempo?

Requisitos críticos

1. coordenada válida
2. série adquirida da mesma variável
3. eventos com datas explícitas
4. intervalo captado demonstrado
5. atribuição hidroestratigráfica consistente
6. variável temporal identificada e repetida
7. independência hidrogeológica demonstrada para inferência de rede
8. ausência de valor objetivamente inválido nas regras atuais

Datas de eventos diferentes não são reunidas como uma série. Amplitude entre a data mais antiga e a mais recente do acervo não é duração de monitoramento.

## 5. Estados por poço

| Estado | Regra |
|---|---|
| `MINIMO_DOCUMENTAL_ATENDIDO_COM_LIMITES` | todos os requisitos críticos demonstrados |
| `EVIDENCIA_PARCIAL` | existe evidência direta e ao menos um requisito crítico não está demonstrado |
| `EVIDENCIA_PARCIAL_COM_REVISAO` | existe evidência direta e ao menos um requisito possui alerta de revisão |
| `UNKNOWN_SEM_EVIDENCIA_DIRETA_NO_CONJUNTO` | a evidência direta não foi encontrada no conjunto adquirido |

O estado `MINIMO_DOCUMENTAL_ATENDIDO_COM_LIMITES` não certifica o dado e não autoriza inferência espacial.

## 6. Dependências entre dimensões

As nove dimensões recebem papéis por pergunta.

- `CRITICA_REGISTRO` indica requisito necessário no mesmo poço
- `CRITICA_CELULA` indica requisito necessário para inferência territorial
- `SUPORTE` acrescenta contexto sem substituir requisitos críticos
- `CONDICIONAL_VARIAVEL` depende da variável temporal investigada
- `TRANSVERSAL` mantém incertezas explícitas
- `NAO_APLICAVEL` impede incorporar uma dimensão sem relação direta com a pergunta

`dimension_dependency_matrix.csv` registra os 45 pares pergunta-dimensão. O papel não é peso.

## 7. Auditoria de associação documental

`question_dependency_pairwise.csv` cruza indicadores binários por poço e publica

- `n11_both`
- `n10_a_only`
- `n01_b_only`
- `n00_neither`
- Jaccard de presença
- coeficiente phi quando calculável
- implicações observadas no conjunto adquirido

Essas métricas descrevem coocorrência documental. Elas não demonstram causalidade, conexão hidráulica ou independência. Quando uma variável é constante, phi permanece vazio.

## 8. Fontes científicas e normativas

As regras reutilizam referências já registradas na bibliografia master.

- GWML2 para separar poço, construção, observação, amostra e ensaio
- Taylor e Alley para distinguir medição isolada de monitoramento de nível
- National Framework for Ground-Water Monitoring para objetivos, poço, quantidade e qualidade
- Theis, Cooper e Jacob e ASTM D4043 para interpretação de ensaios
- USGS National Field Manual e ISO 5667-11 para amostragem e QA hidroquímico
- Resolução CONAMA nº 396 de 2008 para parâmetros, frequência, incerteza e objetivo do monitoramento

As referências sustentam a separação entre componentes. A seleção operacional conservadora dos requisitos pertence à V2.4 e não é apresentada como norma universal.

## 9. Resultados globais

| Pergunta | Evidência direta | Mínimo documental | Parcial | Parcial com revisão | UNKNOWN sem evidência direta |
|---|---:|---:|---:|---:|---:|
| Q01 | 3.213 | 0 | 1.869 | 1.344 | 664 |
| Q02 | 3.081 | 0 | 1.791 | 1.290 | 796 |
| Q03 | 2.053 | 0 | 1.195 | 858 | 1.824 |
| Q04 | 3.415 | 0 | 2.012 | 1.403 | 462 |
| Q05 | 1.637 | 0 | 962 | 675 | 2.240 |

Nenhum resultado zero é convertido em ausência física. O mínimo documental é zero porque requisitos estruturais continuam não demonstrados, especialmente intervalo captado, perfil litológico explícito, unidade verificada, QA hidroquímico completo, série da mesma variável e independência.

## 10. Produtos normativos

- `question_registry.csv`
- `question_requirement_matrix.csv`
- `dimension_dependency_matrix.csv`
- `well_requirement_status_long.csv`
- `well_question_sufficiency_long.csv`
- `cell_question_sufficiency_long.csv`
- `question_dependency_pairwise.csv`
- `question_global_summary.csv`
- `question_scale_summary.csv`
- `question_sufficiency_{100,150,250,500,1000}km2.csv`
- GeoJSON equivalentes para o visor
- `question_sufficiency_registry.json`
- `question_sufficiency_field_dictionary.csv`

Os CSV são a referência científica principal. O Excel é complementar para revisão humana.

## 11. O que a V2.4 não autoriza afirmar

- nenhuma célula foi demonstrada como representativa
- nenhum poço recebeu certificação de qualidade
- nenhum número mínimo universal de poços foi adotado
- nenhuma dimensão recebeu peso
- nenhuma contagem de requisitos foi convertida em score
- nenhuma escala foi escolhida como definitiva
- nenhuma ausência documental foi convertida em ausência de água
- nenhum mapa de potencial aquífero foi produzido
- nenhuma prioridade PIH foi calculada

## 12. Próxima fase admissível

A V2.5 poderá avaliar estabilidade dos estados entre escalas, persistência dos bloqueios, sensibilidade à origem da malha e efeito da heterogeneidade hidrogeológica. Somente depois dessa auditoria será admissível discutir uma lógica de prioridade não compensatória.
