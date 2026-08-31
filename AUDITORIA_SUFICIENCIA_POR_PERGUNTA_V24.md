# AUDITORIA CIENTÍFICA E FUNCIONAL PIH MS V2.4

## Escopo

A V2.4 transforma a matriz multidimensional da V2.2 em uma avaliação não compensatória de suficiência documental para cinco perguntas hidrogeológicas. A fase não calcula prioridade, potencial aquífero, score, peso, interpolação ou predição.

## Perguntas avaliadas

| Código | Pergunta | Evidência direta disponível | Mínimo documental completo |
|---|---|---:|---:|
| Q01 | Nível e profundidade da água | 3.213 poços | 0 |
| Q02 | Propriedades hidráulicas | 3.081 poços | 0 |
| Q03 | Hidroquímica | 2.053 poços | 0 |
| Q04 | Geometria e estratigrafia do aquífero | 3.415 poços | 0 |
| Q05 | Monitoramento temporal | 1.637 poços | 0 |

O resultado zero não significa ausência de informação. Significa que nenhum registro atende simultaneamente a todos os requisitos críticos definidos para a pergunta sob a regra conservadora desta versão.

## Estrutura dos resultados

Foram produzidos

- 3.877 poços canônicos preservados
- 19.385 pares poço e pergunta
- 151.203 avaliações de requisito por poço
- 9.029 células em cinco escalas
- 45.145 pares célula e pergunta
- 153 relações descritivas entre indicadores
- 39 requisitos críticos
- 45 relações entre pergunta, dimensão e função
- 788 campos no dicionário científico master
- 55 referências classificadas por uso

## Escalas

| Escala nominal | Células | Pares célula e pergunta |
|---:|---:|---:|
| 100 km² | 3.763 | 18.815 |
| 150 km² | 2.525 | 12.625 |
| 250 km² | 1.537 | 7.685 |
| 500 km² | 791 | 3.955 |
| 1000 km² | 413 | 2.065 |

Todas as escalas pertencem à família principal `SCALE_PRIMARY_O00_V1`. Cada escala foi calculada diretamente a partir dos poços e das evidências auditadas. Nenhum valor foi herdado de outra resolução.

## Principais bloqueios documentais

### Q01

- intervalo captado não demonstrado em 3.877 poços
- data do nível ausente em 3.857 poços
- hidroestratigrafia não demonstrada de forma estrita em 2.244 poços
- nível estático ausente em 664 poços

### Q02

- intervalo captado não demonstrado em 3.877 poços
- unidade hidráulica verificada ausente em 3.877 poços
- método interpretativo ausente em 3.875 poços
- parâmetro hidráulico ausente em 3.826 poços
- metadados mínimos de ensaio ausentes em 2.781 poços

### Q03

- intervalo captado não demonstrado em 3.877 poços
- unidade química verificada ausente em 3.877 poços
- controle analítico completo ausente em 3.877 poços
- data hidroquímica ausente em 3.347 poços
- parâmetro identificado ausente em 2.110 poços

### Q04

- perfil litológico explícito não demonstrado em 3.877 poços
- intervalo captado não demonstrado em 3.877 poços
- hidroestratigrafia não demonstrada de forma estrita em 2.244 poços
- profundidade positiva ausente em 463 poços

### Q05

- série da mesma variável não demonstrada em 3.877 poços
- intervalo captado não demonstrado em 3.877 poços
- variável temporal comparável não demonstrada em 3.877 poços
- independência hidrogeológica não demonstrada em 3.877 poços
- evidência datada ausente em 2.240 poços

## Exemplo na escala de 250 km²

| Pergunta | Células sem poço | Somente evidência parcial | Com poço e sem evidência direta |
|---|---:|---:|---:|
| Q01 | 1.014 | 454 | 69 |
| Q02 | 1.014 | 445 | 78 |
| Q03 | 1.014 | 374 | 149 |
| Q04 | 1.014 | 470 | 53 |
| Q05 | 1.014 | 291 | 232 |

Nenhuma célula alcança um mínimo documental local. Nenhuma célula é declarada representativa.

## Controles científicos

- UNKNOWN foi preservado como estado explícito
- zero foi usado somente quando uma contagem observada é realmente nula
- evidência direta foi separada de completude documental
- completude documental foi separada de representatividade territorial
- não foi adotado número universal de poços por célula
- as nove dimensões da V2.2 continuam separadas
- associações entre indicadores não foram interpretadas como causalidade ou independência
- dados observados, estados derivados e limitações permanecem identificáveis

## Controles funcionais

- cinco perguntas disponíveis no menu Explorar
- cinco escalas disponíveis no módulo V2.4
- fichas de célula abertas em qualquer parte do hexágono ativo
- fichas dos 3.877 poços ampliadas com os cinco estados e bloqueios
- 64 fragmentos leves de ficha regenerados
- 13 resumos estatísticos carregados automaticamente
- malhas de evidência e estrutura espacial de 100 e 150 km² ligadas ao visor
- sintaxe JavaScript validada
- identificadores HTML verificados sem duplicação

## Limite central

Suficiência documental local não equivale a representatividade territorial. Esta versão informa o que o conjunto adquirido permite responder e quais requisitos faltam. Não escolhe áreas prioritárias.

## Resultado da auditoria

A execução de `scripts/qa_release_v24.py` terminou sem erro. As cardinalidades, os estados, os arquivos copiados para o visor, as fichas fragmentadas, o dicionário, a bibliografia e os controles de ausência de score foram verificados.

O livro `PIH_MS_SUFICIENCIA_POR_PERGUNTA_V1.xlsx` foi validado como complemento para revisão humana. Contém a matriz completa poço-pergunta e uma folha de células de 250 km². Os CSV primários preservam a matriz completa nas cinco escalas.
