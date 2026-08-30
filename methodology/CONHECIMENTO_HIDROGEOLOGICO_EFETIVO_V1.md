# PIH MS · Conhecimento hidrogeológico efetivo · V1

## Estado metodológico

Este módulo implementa a fase V2.2 como uma matriz descritiva não agregada. Cada poço e cada célula recebem nove estados separados. Nenhum estado é convertido em peso, nota, índice, potencial aquífero ou prioridade de investigação.

**AUSÊNCIA DE DADO ≠ AUSÊNCIA DE ÁGUA SUBTERRÂNEA**  
**PREVISÃO ≠ OBSERVAÇÃO**  
**PRIORIDADE DE INVESTIGAÇÃO ≠ POTENCIAL AQUÍFERO**  
**POÇO CADASTRADO ≠ CONHECIMENTO HIDROGEOLÓGICO SUFICIENTE**  
**INTERPOLAÇÃO ≠ EVIDÊNCIA OBSERVADA**  
**DENSIDADE DE POÇOS ≠ QUALIDADE DO CONHECIMENTO**  
**CONTAGEM DE REGISTROS ≠ INFORMAÇÃO INDEPENDENTE**  
**REDUNDÂNCIA ESPACIAL ≠ REDUNDÂNCIA HIDROGEOLÓGICA**  
**UNKNOWN ≠ ZERO**

## 1. Objetivo

O objetivo é declarar o que está documentado, o que é apenas parcial, o que requer revisão e o que permanece UNKNOWN. A matriz serve como base auditável para fases posteriores. Ela não define ainda uma função de decisão.

## 2. Universo e corte

- corte dos dados em 2026-08-29
- 3.877 `well_id` canônicos provisórios
- nenhum poço removido ou fundido
- referência hidrogeológica SGB 2024 na escala 1:1.000.000
- cinco malhas sintéticas `scale_primary` de 100, 150, 250, 500 e 1000 km²
- variante de origem O00 em todas as escalas
- nenhuma escala selecionada como final

A tabela antiga `malha_evidencia_250km2.csv` contém 1.554 células e pertence ao universo anterior das malhas de evidência. A V2.2 usa a família `scale_primary`, cuja malha de 250 km² contém 1.537 células. Esses universos não são tratados como equivalentes.

## 3. Fontes internas reutilizadas

- `wells_master.csv`
- `well_evidence_presence.csv`
- `data_quality_flags.csv`
- `aquifer_assignment_audit.csv`
- `pumping_tests.csv`
- `chem_samples.csv`
- `chem_results.csv`
- `well_vertical_temporal.csv`
- `well_independence_redundancy.csv`
- camadas E04 a E10
- malhas `scale_primary_*km2.geojson`
- estratificação `stratified_scale_*km2.geojson`

Não são criadas observações novas. O módulo apenas organiza estados e agregações descritivas derivadas dessas fontes.

## 4. As nove dimensões

| Dimensão | O que descreve | Estados principais | Limite obrigatório |
|---|---|---|---|
| Espacial | validade da coordenada, concordância municipal e alertas | documentado sem alerta, documentado com revisão, UNKNOWN de localização | proximidade não é qualidade nem independência |
| Hidroestratigráfica | comparação entre o cadastro SIAGAS e a referência espacial SGB 2024 | consistente, possivelmente consistente, revisão, UNKNOWN | divergência cartográfica não conclusiva não é contradição demonstrada |
| Vertical | profundidade total e metadados construtivos disponíveis | parcial com metadados, parcial com profundidade apenas, UNKNOWN | topo e base brutos não são intervalo captado |
| Hidráulica | presença de níveis, capacidade específica, ensaio e transmissividade | valores isolados, ensaio cadastrado, ensaio com metadados mínimos, transmissividade informada, UNKNOWN | transmissividade informada não é parâmetro validado |
| Hidroquímica | presença de resultado parcial e data | parcial datada, parcial sem data, UNKNOWN | não demonstra painel completo, unidade validada ou QA analítico completo |
| Temporal | presença e diversidade de eventos datados | um domínio, múltiplos domínios, UNKNOWN | datas isoladas não formam série temporal |
| Independência | estado da independência hidrogeológica | UNKNOWN em todos os poços e células | duplicidade, colocalização e proximidade são somente contexto de revisão |
| Qualidade documental | alertas objetivos preservados | inválido preservado, revisão presente, sem alerta objetivo | ausência de alerta não certifica qualidade total |
| Incerteza | códigos explícitos de limitações | vetor de códigos não agregados | não se somam códigos para produzir nota |

## 5. Regras por poço

### 5.1 Espacial

`DOCUMENTADO_SEM_ALERTA_OBJETIVO` exige coordenada válida e ausência dos alertas objetivos avaliados. `DOCUMENTADO_COM_REVISAO` preserva coordenada utilizável com marca de revisão ou divergência municipal. Coordenada não válida produz `UNKNOWN_COORDENADA_NAO_VALIDA`.

A distância ao vizinho mais próximo é mantida como contexto. Ela não altera o estado para melhor ou pior.

### 5.2 Hidroestratigráfica

O campo `comparison_status` é traduzido sem ampliar sua força interpretativa. `DIVERGÊNCIA CARTOGRÁFICA NÃO CONCLUSIVA` permanece revisão não conclusiva. `UNKNOWN` permanece UNKNOWN.

A unidade aflorante da referência 1:1.000.000 não é tratada como demonstração do intervalo efetivamente captado em profundidade.

### 5.3 Vertical

São reutilizados profundidade positiva, formação, tipo de penetração, condição hidráulica, tipo de captação, diâmetro e coerência aritmética de topo e base brutos. O intervalo filtrado ou aberto não foi adquirido de forma demonstrável. Por isso `vertical_capture_interval_status` permanece UNKNOWN para os 3.877 poços.

### 5.4 Hidráulica

Os componentes E04 a E09 são mantidos separados. O estado mais informativo presente é usado apenas como rótulo documental.

1. E09 produz `TRANSMISSIVIDADE_INFORMADA_NAO_VALIDADA`
2. E08 produz `ENSAIO_COM_METADADOS_MINIMOS_DOCUMENTAIS`
3. E07 sem E08 produz `ENSAIO_CADASTRADO_SEM_METADADOS_MINIMOS`
4. E04, E05 ou E06 sem ensaio suficiente produz `VALORES_HIDRAULICOS_ISOLADOS_SEM_ENSAIO_SUFICIENTE`
5. ausência de todos os componentes produz `UNKNOWN_SEM_EVIDENCIA_HIDRAULICA_NO_CONJUNTO`

Essa sequência organiza documentação. Ela não classifica qualidade hidráulica.

### 5.5 Hidroquímica

E10 indica evidência parcial. Uma data interpretável permite distinguir evidência parcial datada de evidência parcial sem data. Nenhum dos dois estados demonstra QA analítico completo ou comparabilidade entre campanhas.

### 5.6 Temporal

T04 e T05 separam presença de um evento datado e presença de eventos em múltiplos domínios. T07 permanece UNKNOWN porque nenhuma série completa da mesma variável foi adquirida. O cadastro RIMAS é mantido como indicador separado e não prova disponibilidade local da série.

### 5.7 Independência

Todos os registros recebem `UNKNOWN_INDEPENDENCIA_HIDROGEOLOGICA_NAO_DEMONSTRADA`. Candidatos a duplicidade, coordenadas compartilhadas, sobreposição de snapshots e proximidade espacial são preservados em `independence_review_context`.

Nenhum tamanho amostral efetivo é calculado.

### 5.8 Qualidade documental

Alertas `INVALID` prevalecem sobre alertas `REVIEW`. A ausência de alerta nas regras atuais recebe `SEM_ALERTA_OBJETIVO_NAS_REGRAS_ATUAIS`. Isso não equivale a certificação de qualidade.

### 5.9 Incerteza

Cada poço recebe uma lista de códigos. Quatro códigos são estruturais nesta fase.

- `UNKNOWN_INTERVALO_CAPTADO`
- `UNKNOWN_SERIE_TEMPORAL`
- `UNKNOWN_INDEPENDENCIA_HIDROGEOLOGICA`
- `UNKNOWN_QA_HIDROQUIMICO_COMPLETO`

Outros códigos são adicionados somente quando a dimensão correspondente não é demonstrada. Os códigos são categóricos e não são somados.

## 6. Regras por célula

Cada poço é associado diretamente a cada uma das cinco malhas. As células não são derivadas umas das outras.

Para uma condição booleana (I_i) e uma célula com (n) poços, a contagem é

\[
N_I = \sum_{i=1}^{n} I_i
\]

Quando (n > 0), o percentual é

\[
P_I = 100 \times \frac{N_I}{n}
\]

Quando (n = 0), `N_I` pode ser zero como contagem do conjunto adquirido, mas `P_I` permanece vazio e deve ser lido como UNKNOWN. Essa regra impede que ausência de poço seja convertida em ausência física de uma propriedade.

As idades de evidência usam somente poços com data interpretável. A mediana fica vazia quando não há idade disponível.

As propriedades de unidade dominante, domínio dominante e mascaramento vêm da estratificação hidrogeológica anterior. Elas não substituem o vetor por poço.

## 7. Associação espacial e continuidade com a V2.1

A rotina usa teste ponto em polígono em WGS84 sobre os GeoJSON já distribuídos. Todas as 19.385 associações, 3.877 poços em cinco escalas, foram resolvidas.

O poço `3500027053` está a aproximadamente 0,16 m da fronteira exportada entre duas células de 100 km². Para preservar a atribuição já consolidada em EPSG:5880 na V2.1, foi mantida a célula `SCALE-100-O00-01772`. A exceção está explícita em `effective_knowledge_assignment_audit.csv`.

Depois desse tratamento, a contagem de poços por célula coincide exatamente com `n_wells_raw` do módulo V2.1 nas cinco escalas.

## 8. Produtos normativos

- `well_effective_knowledge.csv`
- `effective_knowledge_{100,150,250,500,1000}km2.csv`
- GeoJSON equivalentes para o visor
- `effective_knowledge_global_summary.csv`
- `effective_knowledge_scale_summary.csv`
- `effective_knowledge_registry.csv`
- `effective_knowledge_assignment_audit.csv`
- `effective_knowledge_field_dictionary.csv`
- bloco `effective_knowledge` em `well_details.json`

O CSV é a fonte científica principal. O Excel é uma camada complementar para revisão humana.

## 9. Dicionário integral dos campos

O anexo normativo `CONHECIMENTO_HIDROGEOLOGICO_EFETIVO_CAMPOS_V1.csv` documenta todos os 127 campos introduzidos pela V2.2. Ele contém definição, regra, unidade, leitura permitida, leitura proibida e tratamento de UNKNOWN. Os mesmos 127 campos foram incorporados ao dicionário mestre, que passa de 553 para 680 campos.

Nenhum campo novo pode ser publicado sem atualização simultânea desse anexo e do dicionário mestre.

## 10. O que a V2.2 não autoriza afirmar

- não existe índice PIH calculado
- não existe ponderação entre dimensões
- não existe potencial de água subterrânea estimado
- não existe classificação de prioridade
- não existe interpolação ou predição
- não existe escala final adotada
- não existe independência hidrogeológica demonstrada
- não existe série temporal completa adquirida
- não existe intervalo captado demonstrado
- não existe painel hidroquímico integralmente comparável

## 11. Referências metodológicas do acervo

- OF01 para a referência hidrogeológica SGB 2024
- OF02 para a estrutura cadastral SIAGAS
- IN01 para a separação entre poço, construção, observação, amostra e ensaio
- IN02 e IN03 para a dimensão temporal e os objetivos de redes de monitoramento
- IN04 para a separação institucional entre localização, litologia, construção, hidroestratigrafia e séries
- HY07 e HY08 para distinguir resultado químico parcial de amostragem e QA comparáveis

