# Estabilidade e sensibilidade PIH MS V2.5

## Objetivo

A V2.5 verifica quanto os estados documentais das cinco perguntas da V2.4 mudam quando se altera a escala da malha ou sua origem. A comparação não escolhe uma escala final nem transforma estabilidade em qualidade.

## Universo fixo

- 3.877 poços canônicos provisórios
- 14.284 pontos fixos de suporte espaçados em 5 km
- perguntas Q01 a Q05
- escalas de 100, 150, 250, 500 e 1000 km²
- origens O00, OX25, OY25 e OXY25
- 39 requisitos documentais críticos
- data de corte 2026-08-29

Os poços e os pontos de suporte nunca são deslocados. Somente a origem da tesselação muda.

## Estados comparados

Cada ponto de suporte recebe o estado da célula em que está contido.

| Código | Estado | Leitura permitida |
|---|---|---|
| 0 | SEM_POCOS_NO_CONJUNTO_AUDITADO | A célula não contém poços do universo adquirido |
| 1 | POCOS_SEM_EVIDENCIA_DIRETA_DA_PERGUNTA | Há poços, mas nenhum apresenta a evidência direta definida para a pergunta |
| 2 | EVIDENCIA_DIRETA_PRESENTE | Ao menos um poço apresenta a evidência direta definida para a pergunta |

O código zero é uma categoria documental. Não representa ausência física de água subterrânea, aquífero ou propriedade.

## Estabilidade entre escalas

A família principal O00 é comparada nas dez combinações possíveis entre as cinco escalas. Para cada pergunta são publicados

- concordância exata dos três estados
- Jaccard da presença de evidência direta
- discordância da presença direta
- Spearman dos códigos de estado
- presença direta em todas, algumas ou nenhuma escala

Nenhuma relação monotônica é pressuposta. Uma célula maior pode incorporar poços e também misturar contextos diferentes.

## Sensibilidade à origem

Em cada escala são comparadas as quatro origens. OX25 desloca a origem em um quarto da largura do hexágono. OY25 desloca em um quarto do espaçamento entre linhas. OXY25 aplica ambos. A análise usa os mesmos pontos de suporte e os mesmos poços.

Concordância não valida uma origem. Discordância não identifica erro. Ambas descrevem dependência do resultado em relação à tesselação.

## Persistência dos bloqueios

Os 39 requisitos são avaliados sem pesos. Um ponto de suporte é observável em uma escala somente quando sua célula contém ao menos um poço. A persistência é calculada exclusivamente nessas escalas observáveis.

Para cada requisito são separados

- prevalência entre os 3.877 poços
- ocorrência de algum bloqueio na célula do suporte
- bloqueio completo quando todos os poços da célula não demonstram o requisito
- persistência entre as escalas observáveis

Um requisito não demonstrado em todos os poços descreve o conjunto adquirido. Não prova ausência física da informação no território nem impossibilidade de adquiri-la.

## Contexto hidrogeológico superficial

Os 14.284 pontos de suporte conservam a unidade hidrogeológica e o domínio hidrolitológico do mapa SGB 2024. Por célula são contadas as classes superficiais observadas no suporte fixo.

Este resultado é um proxy pontual. Não é fração vetorial exata de área, não demonstra a unidade captada por cada poço e não representa estrutura vertical.

## Regras negativas

- UNKNOWN não é zero
- concordância não é qualidade
- estabilidade não é representatividade
- persistência de bloqueio não é ausência física
- unidade superficial não é intervalo captado
- nenhuma escala ou origem é selecionada
- nenhum peso, score, interpolação, predição, potencial ou prioridade é calculado

## Produtos primários

- `support_scale_question_long.csv`
- `support_question_cross_scale.csv`
- `cross_scale_question_summary.csv`
- `cross_scale_pairwise.csv`
- `origin_scale_question_counts.csv`
- `origin_scale_question_summary.csv`
- `origin_pairwise.csv`
- `support_requirement_persistence.csv`
- `blocker_requirement_summary.csv`
- `hydro_context_scale_summary.csv`
- `cell_stability_sensitivity_long.csv`
- cinco CSV e cinco GeoJSON cartográficos

Os CSV são a referência científica principal. O Excel é complementar para inspeção humana.
