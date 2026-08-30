# PIH MS

## Estudo das camadas antes das malhas

Data de corte 29 de agosto de 2026.

Esta etapa implementa doze camadas observacionais ou documentais independentes. Nenhuma é agregada ainda a uma malha e nenhuma recebe peso.

| Código | Camada | Feições | Percentual dos 3.877 | Pronta para contagem em malha |
| --- | --- | ---: | ---: | --- |
| E01 | Poços canônicos provisórios | 3877 | 100.0 % | READY_FOR_GRID_COUNTS |
| E02 | Profundidade positiva informada | 3414 | 88.06 % | READY_FOR_GRID_COUNTS |
| E03 | Aquífero informado no cadastro | 3097 | 79.88 % | READY_FOR_GRID_COUNTS |
| E04 | Nível estático disponível | 3213 | 82.87 % | READY_FOR_GRID_COUNTS |
| E05 | Nível dinâmico disponível | 3180 | 82.02 % | READY_FOR_GRID_COUNTS |
| E06 | Vazão específica não negativa | 3051 | 78.69 % | READY_FOR_GRID_COUNTS |
| E07 | Ensaio de bombeamento cadastrado | 1106 | 28.53 % | READY_FOR_GRID_COUNTS |
| E08 | Ensaio com metadados mínimos de cadastro | 1096 | 28.27 % | READY_FOR_GRID_COUNTS |
| E09 | Transmissividade informada | 51 | 1.32 % | READY_FOR_GRID_COUNTS |
| E10 | Evidência hidroquímica e físico-química parcial | 2053 | 52.95 % | READY_FOR_GRID_COUNTS |
| E11 | Última evidência hidrogeológica datada | 1637 | 42.22 % | READY_FOR_GRID_COUNTS |
| E12 | Revisão hidroestratigráfica necessária | 1823 | 47.02 % | READY_FOR_GRID_COUNTS |

## Decisões científicas

Nível estático e nível dinâmico são representados como disponibilidade de valor. A extração plana atual não fornece a data de medição e por isso não são chamados de séries temporais.

Vazão específica negativa foi excluída da camada derivada de presença utilizável, mas os valores originais permanecem preservados e sinalizados na auditoria.

Ensaio com metadados mínimos exige tipo, data, nível estático, nível dinâmico e vazão estabilizada. Essa regra mede documentação cadastral e não certifica a interpretação do ensaio.

Transmissividade é mapeada como valor informado. Sua unidade e método permanecem não congelados para a maioria dos registros.

Hidroquímica parcial significa presença de pelo menos um campo físico-químico ou químico. Não significa painel hidroquímico completo.

Antiguidade usa apenas data de ensaio ou data de coleta ou análise química. Data de perfuração e data de cadastro não substituem uma data de observação.

A revisão hidroestratigráfica não é chamada de contradição. Divergência cartográfica pode ocorrer porque o poço capta uma unidade profunda.
