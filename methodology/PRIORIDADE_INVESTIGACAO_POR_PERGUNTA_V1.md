# PIH MS V2.6 experimental

## Prioridade de investigação por pergunta

### Objetivo

Classificar a necessidade de adquirir ou revisar informação para responder cinco perguntas hidrogeológicas explícitas. A classificação deriva somente dos requisitos e estados demonstrados nas versões V2.4 e V2.5.

### Universo

- 3.877 poços canônicos
- cinco perguntas
- 39 requisitos documentais
- cinco escalas de 100, 150, 250, 500 e 1000 km²
- quatro origens O00, OX25, OY25 e OXY25
- 14.284 pontos fixos de suporte
- 9.029 células da família principal O00
- 45.145 pares célula e pergunta

### Perguntas

- Q01 nível e profundidade da água
- Q02 propriedades hidráulicas
- Q03 hidroquímica
- Q04 geometria e estratigrafia do aquífero
- Q05 monitoramento temporal

### Portal de contexto

O portal de contexto é uma conjunção. Todos os requisitos indicados devem coexistir no mesmo poço.

| Pergunta | Requisitos do portal |
| --- | --- |
| Q01 | Q01_R01, Q01_R02, Q01_R04, Q01_R06 e Q01_R07 |
| Q02 | Q02_R01, Q02_R03, Q02_R04 e Q02_R09 |
| Q03 | Q03_R01, Q03_R03, Q03_R04, Q03_R05, Q03_R06 e Q03_R09 |
| Q04 | Q04_R01, Q04_R02, Q04_R05 e Q04_R06 |
| Q05 | Q05_R01, Q05_R03, Q05_R05 e Q05_R08 |

O portal não substitui o mínimo documental completo. Ele separa evidência direta sem contexto suficiente de evidência que já pode ser interpretada parcialmente.

### Classes de prioridade

| Código | Classe | Regra |
| --- | --- | --- |
| 0 | UNKNOWN | nenhum poço do conjunto auditado na célula |
| 1 | P1 crítica | há poço, mas não há evidência direta para a pergunta |
| 2 | P2 alta | há evidência direta, mas nenhum poço satisfaz o portal de contexto |
| 3 | P3 moderada | ao menos um poço satisfaz o portal, mas nenhum satisfaz o mínimo completo |
| 4 | P4 baixa | existe mínimo completo local, mas a representatividade não foi demonstrada |
| 5 | P5 suficiência documental | mínimo completo e representatividade demonstrados |

P5 é uma classe documental. Não significa conhecimento absoluto ou encerramento da investigação.

### Confiança

A confiança é calculada separadamente a partir da concordância exata da própria classe de prioridade nos 14.284 pontos fixos.

- C1 quando a concordância é zero entre escalas e entre origens
- C2 quando apenas uma verificação apresenta alguma concordância
- C3 quando as duas apresentam alguma concordância e nenhuma é completa
- C4 quando uma é completa e a outra apresenta alguma concordância
- C5 quando ambas são completas
- UNKNOWN quando a prioridade não é classificável ou a célula não possui ponto fixo de suporte

Não são usados limiares intermediários inventados.

### Paleta

- UNKNOWN cinza `#7C8793`
- P1 ou C1 vermelho `#B2182B`
- P2 ou C2 laranja `#F28E2B`
- P3 ou C3 morado `#7B4AB4`
- P4 ou C4 turquesa `#1B9E9A`
- P5 ou C5 verde `#2E8B57`

### Resultados da execução

Prioridade nos 45.145 pares

- UNKNOWN 32.405
- P1 2.801
- P2 5.448
- P3 4.491
- P4 0
- P5 0

Confiança

- UNKNOWN 32.430
- C1 2.229
- C2 3.783
- C3 5.512
- C4 873
- C5 318

### Limites

- UNKNOWN não é convertido em prioridade
- prioridade não representa potencial aquífero
- confiança não substitui prioridade
- estabilidade não demonstra representatividade
- proximidade e repetição documental não demonstram independência hidrogeológica
- nenhuma pergunta compensa outra
- nenhuma prioridade integrada é calculada
- nenhum peso, score, AHP, interpolação ou predição é usado

### Reprodutibilidade

O cálculo é executado por `scripts/build_research_priority_v26.py`. Os CSV longos são a referência primária. Os GeoJSON e o Excel são produtos complementares de visualização e revisão.
