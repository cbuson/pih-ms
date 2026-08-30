# DECISION LOG

- E04 e E05 são camadas de disponibilidade, não de série temporal
- E06 exclui somente três valores negativos da camada derivada e preserva a fonte original
- E08 representa metadados mínimos de cadastro e não certificação do ensaio
- E09 representa transmissividade informada e não parâmetro validado
- E10 é hidroquímica parcial e não painel químico completo
- E11 usa apenas datas de ensaio, coleta ou análise química
- E12 representa necessidade de revisão hidroestratigráfica e não contradição demonstrada

## D13
As três escalas são calculadas diretamente das feições originais E01–E12. Zero não é convertido em ausência de água. Células sem E01 permanecem UNKNOWN.

## D16
Métricas espaciais são mantidas descritivas e separadas. A malha interna de 5 km não é adotada como resolução definitiva e é acompanhada por sensibilidade 2,5/5/10 km. Distância à evidência não é interpretada como distância à água ou prioridade.

## D-V16-04 · Reprodutibilidade operacional

Os scripts científicos da etapa V1.6 usam caminhos relativos à raiz do projeto. O pacote não depende de diretórios temporários externos para reproduzir a estrutura espacial a partir das evidências já auditadas.

## D-V16-05 · Escala ainda não adotada

As áreas nominais de 250, 500 e 1000 km² permanecem candidatas. Os resultados de estabilidade e MAUP não autorizam escolher uma malha definitiva nesta etapa.


## D-V17-01 · Nenhuma escala vencedora

A comparação mostra trade-offs incompatíveis com a escolha automática de uma escala. 250 km² permanece candidata central, mas não adotada. 100 e 150 km² são mantidas para diagnóstico fino e 500 e 1000 km² para persistência regional.

## D-V17-02 · Heterogeneidade hidrogeológica

Nesta etapa a heterogeneidade usa pontos fixos de suporte de 5 km classificados pelo mapa SGB 2024. É um proxy de suporte e não uma fração vetorial exata de área.

## V1.8 · estratificação hidrogeológica
Decisão. Evidência pertencente a outra unidade ou domínio não reduz automaticamente o vazio do estrato local. O efeito de mascaramento por agregação passa a ser medido explicitamente. Nenhuma escala é adotada nesta etapa.

## V1.9 · documentação vertical e temporal

### D-V19-01 · profundidade não representa intervalo captado
V01 conserva profundidade total como evidência documental. V06 conserva topo e base brutos quando coerentes. Nenhum desses campos é convertido automaticamente em intervalo de filtro ou tela.

### D-V19-02 · filtro e tela permanecem UNKNOWN
Nenhuma tabela relacional de filtros ou telas foi adquirida. V08 não é inferida a partir de profundidade, topo, base, formação ou tipo de penetração.

### D-V19-03 · medição datada não equivale a série
T03 identifica somente medições de nível que possuem data explícita no conjunto histórico adquirido. T07 permanece UNKNOWN porque não foi adquirida sequência completa da mesma variável por poço.

### D-V19-04 · RIMAS corrigido desde a fonte original
O campo rimas_flag_current da primeira tabela wells_master estava incorreto. A V1.9 usa o campo original status_rimas e encontra 22 registros Rimas. O erro derivado é documentado e o dado fonte permanece intacto.

### D-V19-05 · temporalidade sem falsa continuidade
A amplitude de datas observada entre registros dentro de uma célula não é interpretada como duração de monitoramento. Ela descreve somente a distribuição temporal do conjunto documental.

## Decisão V2.0

Antes de prosseguir para independência da informação ou qualquer construção de prioridade, PIH MS exige documentação transversal dos parâmetros já produzidos. Toda métrica exibida deve ter definição, fórmula ou regra, unidade, interpretação permitida, interpretação proibida e tratamento de UNKNOWN. A bibliografia distingue métodos implementados de antecedentes futuros.


## V2.1 · decisão metodológica
Não calcular “n independente” por distância, correlação ou fusão automática. Nesta fase, independência permanece uma hipótese a testar. São publicados apenas descritores de dependência documental e espacial e cenários de sensibilidade.

## V2.2 · matriz não agregada

### D-V22-01 · nove dimensões separadas

Espacial, hidroestratigráfica, vertical, hidráulica, hidroquímica, temporal, independência, qualidade documental e incerteza são publicadas como estados distintos. Não se aplicam pesos e não se calcula uma nota total.

### D-V22-02 · independência permanece UNKNOWN

Proximidade, co-localização, repetição de fonte e candidatos a duplicidade não demonstram independência hidrogeológica. A dimensão permanece UNKNOWN para os 3.877 poços e para todas as células.

### D-V22-03 · zeros documentais não substituem UNKNOWN

Em célula sem poço, contagens do conjunto adquirido podem ser zero. Percentuais condicionados ao número de poços permanecem vazios. Nenhuma ausência cadastral é convertida em ausência física.

### D-V22-04 · família de malhas

A V2.2 usa as cinco malhas `scale_primary` da comparação multiescalar. A malha antiga de 250 km² com 1.554 células não é tratada como equivalente à malha `scale_primary` de 1.537 células.

### D-V22-05 · continuidade espacial auditada

O poço 3500027053 está a aproximadamente 0,16 m de uma fronteira exportada em WGS84 na escala de 100 km². Preserva-se a atribuição projetada EPSG:5880 consolidada na V2.1, com exceção explícita no arquivo de auditoria.

### D-V22-06 · próxima fase

Antes de qualquer ponderação, devem ser definidos critérios de suficiência por pergunta de investigação e auditadas as dependências entre dimensões. A V2.2 não autoriza calcular o índice PIH.

## V2.2.1 · navegação e licença

### D-V221-01 · resultados científicos preservados

A V2.2.1 altera interface, acesso, desempenho das fichas e documentação legal. Não recalcula nenhuma métrica e não modifica a matriz científica V2.2.

### D-V221-02 · software Open Source com reciprocidade de rede

O código do aplicativo usa AGPL-3.0-or-later. A licença permite uso comercial e exige oferta do código-fonte correspondente quando uma versão modificada é disponibilizada por rede.

### D-V221-03 · conteúdos originais não comerciais

Textos científicos, documentação e figuras originais usam CC BY-NC-SA 4.0, salvo indicação diferente. Dados e materiais de terceiros não são relicenciados.

### D-V221-04 · escalas incompletas permanecem explícitas

Malhas de evidência e estrutura espacial ainda não possuem 100 e 150 km². A ausência não é preenchida por herança entre escalas e permanece registrada no backlog posterior à V2.2.1.
