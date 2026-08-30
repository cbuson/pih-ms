# Guia detalhado de leitura das malhas e resultados PIH MS V2.2

A V2.2 mantém os módulos anteriores e acrescenta a matriz de conhecimento hidrogeológico efetivo. Nenhum score PIH, peso, AHP, interpolação ou modelo preditivo é introduzido.

## Regras de leitura

AUSÊNCIA DE DADO ≠ AUSÊNCIA DE ÁGUA SUBTERRÂNEA.

PREDIÇÃO ≠ OBSERVAÇÃO.

PRIORIDADE DE INVESTIGAÇÃO ≠ POTENCIAL AQUÍFERO.

DENSIDADE DE POÇOS ≠ QUALIDADE DO CONHECIMENTO.

NÚMERO DE REGISTROS ≠ INFORMAÇÃO INDEPENDENTE.

Antes de interpretar qualquer valor, verificar pergunta, unidade, denominador, escala, área efetiva, estrato, data e estado UNKNOWN.

## Malhas

As malhas de 100, 150, 250, 500 e 1000 km² são unidades analíticas sintéticas. Um hexágono não é um aquífero, bacia ou unidade geológica. Área nominal é a área-alvo antes do recorte. Área efetiva é a parte que permanece em Mato Grosso do Sul. Células de borda podem possuir suporte muito menor que o nominal.

Células maiores tendem a incorporar mais poços e reduzir visualmente vazios sem criar observações novas. Também tendem a misturar mais unidades hidroestratigráficas. Células menores preservam detalhe, mas são mais esparsas e sensíveis à origem da tesselação.

## E01 a E12

E01 é o conjunto-base de 3.877 poços canônicos provisórios. Para E02 a E12, quando n_E01 > 0, pct_E##_of_E01 = 100 × n_E## / n_E01. Quando n_E01 = 0, a porcentagem é UNKNOWN e não 0%.

E02 representa profundidade total positiva, não intervalo captado. E03 representa nome de aquífero informado, não atribuição demonstrada. E04 e E05 representam disponibilidade de níveis, não uma superfície potenciométrica contemporânea. E06 representa vazão específica documental e não transmissividade. E07 é ensaio cadastrado. E08 é completude documental mínima e não certificação científica. E09 é transmissividade reportada e não transmissividade recalculada ou comparável automaticamente. E10 é hidroquímica parcial. E11 é presença de alguma evidência datada. E12 é necessidade de revisão e não erro demonstrado.

## Quantis

Mediana, P10, P25, P75, P90 e máximo são calculados apenas sobre valores válidos. Ausências não entram como zero. O tamanho da amostra deve acompanhar a interpretação. Profundidade P90 é P90 das profundidades cadastradas, não profundidade do aquífero.

## Estrutura espacial

Vizinho mais próximo mede espaçamento geométrico. Centro médio mede deslocamento da nuvem de E01 em relação ao centro da célula. Envoltória convexa mede extensão externa e pode incluir áreas sem observação. Suportes de 2,5, 5 e 10 km são mantidos separadamente.

Redundância proxy R = 1 - k/n, onde n é o número de E01 e k o número de suportes ocupados. É co-localização espacial e não independência estatística ou hidrogeológica.

Entropia normalizada Hn = -Σ p_i ln(p_i) / ln(k), quando existem pelo menos dois suportes ocupados. Dominância é 100 vezes a maior contagem em um suporte dividida por n.

## Distância à evidência

A rede fixa contém 14.284 pontos espaçados em 5 km. Para cada suporte s e evidência E calcula-se d(s,E) como a menor distância euclidiana até uma feição E. Cada célula resume mediana, P90 e máximo. DISTÂNCIA À EVIDÊNCIA ≠ DISTÂNCIA À ÁGUA SUBTERRÂNEA.

## Escala e MAUP

Jaccard compara presença entre representações. Mismatch mede a fração dos suportes que muda de estado. Spearman compara ordenação relativa das densidades. O00, OX25, OY25 e OXY25 alteram somente a origem da malha. Os poços nunca são deslocados.

## Estratificação hidrogeológica

A composição formal usa interseção vetorial com 16 unidades hidroestratigráficas e três domínios SGB 2024. Pureza é a fração areal da classe dominante. Unidade dominante não significa unidade única.

Mascaramento ocorre quando a célula tem uma evidência no total mas não a tem no mesmo estrato analisado. Same-stratum gap mede distância exigindo evidência da mesma unidade ou domínio. Evidência próxima de outra unidade não substitui evidência do estrato local.

## Documentação vertical

V01 profundidade positiva. V02 formação documentada. V03 tipo de penetração. V04 condição hidráulica. V05 tipo de captação. V06 topo e base brutos coerentes. V07 diâmetro. V08 intervalo explícito de filtro ou tela. V08 permanece UNKNOWN no conjunto adquirido. Profundidade total não é intervalo captado.

## Documentação temporal

T01 ensaio datado. T02 química datada. T03 nível datado. T04 qualquer evidência hidrogeológica datada. T05 múltiplos domínios documentais datados. T06 cadastro RIMAS. T07 série temporal completa adquirida e auditada. T07 permanece UNKNOWN. Evento datado não é série temporal.

Idade da última evidência é calculada em relação à data de corte e não é idade da água ou do poço. dated_dataset_span_years pode ser produzido por apenas dois eventos e não representa duração contínua de monitoramento.

## Densidade e independência

Densidade padroniza contagem por área. Ela não corrige concentração espacial, profundidade, intervalo captado, idade, método ou qualidade. A independência hidrogeológica efetiva ainda não é calculada porque exige metadados adicionais.

## Dicionário exaustivo

O arquivo methodology/DICIONARIO_METRICAS_RESULTADOS_V1.csv documenta 680 campos derivados. Para cada campo informa módulos e arquivos fonte, definição, fórmula ou regra, unidade, leitura permitida, leitura proibida e tratamento de UNKNOWN. Nenhum dos 680 campos permanece com descrição genérica na V2.2 final.

## Bibliografia

A bibliografia master separa fontes usadas diretamente, padrões e sistemas internacionais, fundamentos hidrogeológicos, métodos já implementados e métodos futuros não implementados. A presença de uma referência não implica aplicação de seu método.


## Independência e redundância · V2.1

A V2.1 não calcula uma contagem corrigida de evidências independentes. Ela separa fenômenos que podem inflar a percepção de informação.

`pct_source_snapshot_overlap` informa que fração dos poços da célula aparece nas duas versões da base. Isso é repetição de representação de fonte.

`coordinate_compression_pct` mede quanto a contagem cairia se IDs em coordenadas exatamente idênticas fossem tratados como um único local cadastral. Não é porcentagem de poços redundantes.

`review_all_reduction_pct` é o cenário máximo de sensibilidade documental, unindo coordenadas idênticas e todos os pares candidatos. Continua sendo hipótese de revisão.

`nn_lt_500m_pct` informa a fração dos poços com outro poço a menos de 500 m. Proximidade espacial não demonstra que os poços capturem o mesmo intervalo, tenham o mesmo regime hidráulico ou representem a mesma informação.

`documentary_domains_median` resume a variedade de cinco domínios documentais por poço. Diversidade documental não equivale a independência estatística.

`chem_sample_records_per_well` e `hydraulic_parameter_records_per_well` mostram volume de registros por poço. Analitos diferentes e parâmetros diferentes não são réplicas equivalentes.

Regra obrigatória: **REDUNDÂNCIA ESPACIAL ≠ REDUNDÂNCIA HIDROGEOLÓGICA**.

## Conhecimento hidrogeológico efetivo · V2.2

A V2.2 reúne as evidências anteriores em um vetor de nove estados separados. O vetor não é uma soma.

- espacial descreve validade e alertas da localização
- hidroestratigráfica preserva a força da comparação cadastral e cartográfica
- vertical separa profundidade total de intervalo captado
- hidráulica separa valores isolados, ensaio cadastrado, metadados mínimos e transmissividade informada
- hidroquímica separa evidência parcial, data e ausência de QA completo
- temporal separa eventos datados de séries temporais
- independência permanece UNKNOWN porque não foi demonstrada hidrogeologicamente
- qualidade documental preserva REVIEW e INVALID sem correção silenciosa
- incerteza lista códigos sem agregá-los

Em células com poços, cada porcentagem usa `n_wells` como denominador. Em células sem poço, a contagem documental pode ser zero, mas o percentual permanece vazio. Portanto célula sem poço não deve ser lida como 0% de água subterrânea, 0% de potencial ou 0% de conhecimento físico.

`dimension_vector_json` permite recuperar os nove estados sem perder sua separação. `uncertainty_codes` lista limitações explícitas. Nenhum dos dois campos deve ser convertido em nota.

As paletas do visor representam somente magnitude da métrica selecionada. Cor mais intensa não significa melhor conhecimento, maior potencial ou maior prioridade.
