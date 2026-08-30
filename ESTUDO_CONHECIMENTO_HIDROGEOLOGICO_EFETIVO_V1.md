# PIH MS · Matriz de conhecimento hidrogeológico efetivo · V1

## Resultado principal

A V2.2 foi calculada para 3.877 poços e 9.029 células distribuídas em cinco escalas. O resultado é um vetor de nove dimensões separadas. Não foi criado índice, peso ou classificação de prioridade.

## 1. Resultados por poço

| Dimensão | Resultado observado |
|---|---|
| Espacial | 3.766 poços sem alerta objetivo de localização e 111 em revisão |
| Hidroestratigráfica | 1.633 consistentes, 421 possivelmente consistentes, 981 em revisão e 842 UNKNOWN |
| Vertical | 1.651 com profundidade e metadados, 1.763 com profundidade apenas e 463 sem profundidade positiva |
| Hidráulica | 51 com transmissividade informada, 1.046 com ensaio e metadados mínimos, 10 com ensaio sem metadados mínimos, 2.106 com valores isolados e 664 UNKNOWN |
| Hidroquímica | 521 com evidência parcial datada, 1.532 com evidência parcial sem data e 1.824 UNKNOWN |
| Temporal | 475 com múltiplos domínios datados, 1.162 com um domínio datado e 2.240 UNKNOWN |
| Independência | 3.877 UNKNOWN quanto à independência hidrogeológica |
| Qualidade documental | 3 com valor inválido preservado, 2.188 com alertas de revisão e 1.686 sem alerta objetivo nas regras atuais |
| Incerteza | códigos explícitos por poço, sem soma ou nota |

## 2. Evidências que permanecem ausentes do conjunto adquirido

- intervalo filtrado ou aberto demonstrado em 0 poços
- série temporal completa demonstrada em 0 poços
- independência hidrogeológica demonstrada em 0 poços
- QA hidroquímico completo demonstrado em 0 poços

Esses zeros são contagens do conjunto documental adquirido. Eles não significam inexistência física das características.

## 3. Resultados por escala

| Escala km² | Células | Com poço | Sem poço | Poços preservados |
|---:|---:|---:|---:|---:|
| 100 | 3.763 | 774 | 2.989 | 3.877 |
| 150 | 2.525 | 657 | 1.868 | 3.877 |
| 250 | 1.537 | 523 | 1.014 | 3.877 |
| 500 | 791 | 354 | 437 | 3.877 |
| 1000 | 413 | 240 | 173 | 3.877 |

O aumento da escala reduz o número de células vazias por agregação. Isso não demonstra melhoria do conhecimento local. Células maiores também aumentam mistura hidrogeológica e podem mascarar vazios internos.

## 4. Achados científicos

### 4.1 Número de poços e conhecimento vertical são diferentes

Embora 3.414 poços tenham profundidade total positiva, nenhum intervalo captado foi demonstrado. A base é numerosa, mas a ligação entre observação e intervalo aquífero permanece incompleta.

### 4.2 Evidência hidráulica tem níveis documentais distintos

Há 1.096 poços com ensaio e metadados documentais mínimos. Apenas 51 possuem transmissividade informada. O valor informado continua sem validação do método, do ajuste e da unidade nesta fase.

### 4.3 Evidência hidroquímica é parcial

Há 2.053 poços com algum componente hidroquímico parcial. Somente 521 possuem uma data interpretável associada. Nenhum estado autoriza tratar os resultados como painel completo e comparável entre campanhas.

### 4.4 A dimensão temporal é o maior vazio estrutural

Há 1.637 poços com pelo menos um evento datado, mas nenhuma série completa adquirida. O cadastro RIMAS em 22 poços foi preservado como indicador separado e não como prova de série disponível.

### 4.5 Independência continua não demonstrada

Os alertas V2.1 ajudam a revisar snapshots, coordenadas e candidatos a duplicidade. Eles não resolvem conectividade hidráulica, intervalos captados ou representatividade de observações próximas. Por isso a dimensão permanece UNKNOWN para todos os poços e células.

## 5. Problemas encontrados e tratamento

| Problema | Tratamento adotado |
|---|---|
| Universo antigo de 250 km² com 1.554 células | não utilizado na matriz V2.2 e documentado como produto de fase anterior |
| Exportação WGS84 desloca um ponto limítrofe em cerca de 0,16 m | preservada a atribuição projetada V2.1 e registrada a exceção |
| Percentuais em células sem poço | mantidos vazios, nunca preenchidos com zero |
| Alertas e valores inválidos | preservados sem correção silenciosa |
| Vários registros por poço | contados como registros documentais, nunca como observações independentes |

## 6. O que foi descoberto

O conjunto oferece boa extensão cadastral, mas o conhecimento efetivo é desigual entre dimensões. Profundidade total e alguns componentes hidráulicos são relativamente frequentes. Intervalo captado, séries temporais, QA hidroquímico completo e independência hidrogeológica continuam não demonstrados.

Essa assimetria é o principal resultado da V2.2. Ela mostra por que uma contagem única de poços ou registros não pode substituir uma matriz multidimensional.

## 7. Próximo passo cientificamente admissível

O próximo passo é auditar dependências entre as nove dimensões e definir critérios de suficiência por pergunta de investigação. Isso deve ser feito antes de qualquer ponderação. A etapa precisa distinguir perguntas sobre nível, hidráulica, hidroquímica, geometria aquífera e monitoramento temporal, pois cada uma exige evidências diferentes.

Ainda não é admissível calcular um índice PIH.

