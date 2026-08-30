# PIH MS

## Estrutura espacial da evidência hidrogeológica V1

Data de corte 29 de agosto de 2026

Estado metodológico

Módulo descritivo e experimental. Não existe pontuação PIH. Não existem pesos. Não existe classificação de prioridade. Não existe interpolação de propriedade hidrogeológica.

## 1. Pergunta científica

Este módulo avalia como as observações hidrogeológicas auditadas estão distribuídas no espaço.

O objetivo não é estimar onde existe água subterrânea. O objetivo é medir características observáveis da distribuição da informação cadastrada e auditada.

A análise diferencia quantidade de poços, cobertura espacial interna, concentração, redundância espacial, distância até evidência cadastrada e sensibilidade à unidade espacial adotada.

## 2. Fontes de entrada

As feições E01 a E12 procedem da Matriz de Evidência Hidrogeológica V1.

A camada E01 contém 3.877 poços canônicos provisórios do snapshot SIAGAS de trabalho auditado.

As malhas candidatas de 250, 500 e 1000 km² são analisadas independentemente.

O limite de Mato Grosso do Sul empregado nesta etapa é o limite estadual IBGE 2025 integrado ao projeto.

## 3. Sistema de referência para cálculo

Todos os cálculos métricos são executados em SIRGAS 2000 Brasil Polyconic, EPSG 5880.

Os arquivos originais não são reprojetados nem substituídos. A reprojeção é realizada somente em copias derivadas de cálculo.

## 4. Distância de vizinho mais próximo em E01

Para cada poço i de E01 é calculada a distância euclidiana ao poço diferente mais próximo.

\[
d_i = \min_{j \ne i} ||x_i-x_j||
\]

Por célula são armazenadas a mediana e o percentil 90 dessas distâncias globais.

Também são calculadas distâncias internas entre poços pertencentes à mesma célula quando existem pelo menos dois poços.

Essas medidas descrevem espaçamento entre registros. Não medem produtividade, conectividade hidráulica ou distância até água subterrânea.

O uso de distância ao vizinho mais próximo tem antecedente clássico em Clark e Evans 1954. Nesta aplicação não é adotado automaticamente o índice R de Clark e Evans porque a pergunta atual é descritiva e as feições apresentam forte heterogeneidade territorial e de processo de cadastro.

## 5. Suporte espacial interno multirresolução

E01 é analisada por três suportes quadrados internos independentes.

2,5 km

5 km

10 km

Para cada tamanho s cada poço é atribuído à unidade de suporte correspondente.

Para cada célula da malha é calculada a proporção de área da própria célula intersectada pelas unidades de suporte que contêm pelo menos um poço E01.

\[
C_s = 100 \times \frac{A\left(H \cap \bigcup B_s^+\right)}{A(H)}
\]

H representa a célula analisada.

B_s^+ representa o conjunto de unidades de suporte de tamanho s que contém pelo menos um poço E01.

C_s não é a porcentagem da célula hidrogeologicamente conhecida. É somente uma medida experimental de ocupação espacial da distribuição dos poços sob um suporte definido.

A manutenção simultânea de 2,5, 5 e 10 km é deliberada. Nenhum desses suportes foi adotado como definitivo.

## 6. Proxy de redundância espacial

Para cada suporte interno é calculado

\[
R_s = 1 - \frac{k_s}{n}
\]

n é o número de poços E01 da célula.

k_s é o número de unidades de suporte ocupadas por pelo menos um poço.

R_s próximo de zero indica que os poços tendem a ocupar unidades distintas naquele suporte.

R_s elevado indica concentração de vários registros nas mesmas unidades de suporte.

Esta variável é um proxy geométrico. Não mede independência hidrogeológica real. Dois poços espacialmente próximos podem observar intervalos, unidades ou tempos distintos. Dois poços distantes também podem compartilhar informação redundante.

## 7. Entropia espacial normalizada

Quando pelo menos duas unidades de suporte estão ocupadas, a distribuição dos poços entre essas unidades é resumida por entropia de Shannon normalizada.

\[
H_n = -\frac{\sum_i p_i \ln p_i}{\ln k}
\]

p_i é a proporção dos poços na unidade de suporte i.

k é o número de unidades ocupadas.

H_n próximo de 1 indica distribuição relativamente equilibrada entre as unidades ocupadas.

H_n menor indica maior concentração relativa.

A entropia é utilizada somente como descritor da distribuição espacial dos registros. Não é tratada como quantidade total de conhecimento. O uso de teoria da informação em desenho de redes de monitoramento possui ampla literatura, mas sua aplicação operacional depende do objetivo da rede e da estrutura dos dados.

## 8. Dominância espacial

Para cada suporte s é calculada a porcentagem de poços presente na unidade de suporte mais ocupada.

\[
D_s = 100 \times \frac{\max n_i}{n}
\]

Valores altos mostram concentração dos registros em uma única unidade interna.

## 9. Deslocamento médio em relação ao centro da célula

É calculado o centro médio das coordenadas dos poços E01 de cada célula.

A distância entre esse centro médio e o centroide geométrico da célula é registrada em quilômetros.

Também é produzida uma versão normalizada pelo raio do círculo de área equivalente à célula.

Esta medida ajuda a identificar concentração assimétrica. Não substitui a análise de cobertura interna.

## 10. Envoltória convexa

Quando existem pelo menos três poços E01 em uma célula é calculada a razão entre a área da envoltória convexa dos pontos e a área efetiva da célula em Mato Grosso do Sul.

\[
CH = \frac{A\left(ConvexHull(P)\right)}{A(H)}
\]

A medida é somente descritiva. A envoltória convexa pode incluir áreas sem qualquer observação e não deve ser interpretada como superfície conhecida.

## 11. Distância espacial até E01 a E12

Foi criada uma malha fixa de 14.284 pontos de suporte com espaçamento de 5 km dentro de Mato Grosso do Sul.

Para cada ponto de suporte é calculada a distância até a feição mais próxima de cada conjunto E01 a E12.

Para cada célula são resumidas

mediana

percentil 90

máximo

Quando uma célula recortada é tão pequena que não contém nenhum ponto da malha fixa de 5 km é usado um ponto representativo interno da geometria. O uso dessa contingência fica registrado no campo gap_support_fallback.

A distância é até evidência cadastrada no conjunto auditado.

DISTÂNCIA À EVIDÊNCIA ≠ DISTÂNCIA À ÁGUA SUBTERRÂNEA

DISTÂNCIA À EVIDÊNCIA ≠ INCERTEZA HIDROGEOLÓGICA TOTAL

## 12. Comparação entre 250, 500 e 1000 km²

A estabilidade entre escalas é medida sobre os mesmos 14.284 pontos de suporte de 5 km.

Para cada evidência E01 a E12 são comparados

correlação de Spearman da densidade por 100 km²

Jaccard da presença ou ausência de evidência

porcentagem dos pontos de suporte cuja classificação presença ou ausência muda

porcentagem territorial de suporte classificada com presença em cada escala

Essa abordagem evita comparar diretamente células que não possuem a mesma geometria.

Os resultados mostram que aumentar a célula amplia a proporção espacial associada a células que contêm pelo menos uma observação. Esse efeito não deve ser interpretado como aumento real do conhecimento.

## 13. Primeiro ensaio MAUP de origem

Além das três malhas candidatas existentes foi realizado um ensaio independente de sensibilidade ao zoneamento.

Foram geradas malhas hexagonais regulares sintéticas em EPSG 5880 com áreas nominais de 250, 500 e 1000 km².

Para cada escala foram testadas quatro origens.

O00 sem deslocamento adicional

OX25 deslocamento horizontal equivalente a 25 por cento da largura do hexágono

OY25 deslocamento vertical equivalente a 25 por cento do espaçamento entre fileiras

OXY25 combinação dos dois deslocamentos

Esse ensaio não substitui as malhas candidatas do projeto. Ele serve somente para verificar sensibilidade ao posicionamento arbitrário da tesselação.

Foram avaliadas inicialmente E01, E07, E09 e E10 porque representam cadastro geral, ensaio hidráulico, transmissividade e informação hidroquímica parcial.

São registrados

número de células

células ocupadas

porcentagem de células ocupadas

mediana de registros nas células ocupadas

máximo de registros em uma célula

Jaccard entre origens calculado sobre os mesmos pontos fixos de suporte

porcentagem de desacordo presença ou ausência entre origens

correlação de Spearman dos contadores atribuídos aos pontos fixos

A literatura sobre MAUP demonstra que resultados agregados podem depender tanto da escala como do sistema de zoneamento. Por isso nenhuma escala será adotada apenas porque produza uma cartografia visualmente conveniente.

## 14. Resultados descritivos desta etapa

Na malha candidata de 250 km² a mediana de ocupação interna E01 é aproximadamente 4,59 por cento com suporte de 2,5 km, 12,25 por cento com suporte de 5 km e 38,51 por cento com suporte de 10 km entre células que possuem E01.

Esses três resultados diferentes mostram que a estimativa de ocupação depende fortemente do suporte adotado.

Na mesma escala a mediana do percentil 90 da distância até evidência é aproximadamente 16,72 km para E01, 28,03 km para E07, 68,68 km para E09 e 20,98 km para E10 quando se consideram todas as células.

A escassez espacial de E09 é muito maior que a simples distribuição de poços E01.

A comparação entre escalas também mostra perda de estabilidade espacial. Para E01 a comparação entre 250 e 1000 km² apresenta Jaccard de presença de aproximadamente 0,547 sobre a malha fixa de suporte e desacordo de aproximadamente 28,58 por cento. Para E09 o Jaccard cai para aproximadamente 0,194.

Esses resultados impedem considerar automaticamente a malha mais grossa como representação mais completa do conhecimento.

## 15. Limitações obrigatórias

A posição dos poços herda a qualidade das coordenadas das fontes auditadas.

A densidade de poços é afetada por finalidades de perfuração e cadastro.

A distância euclidiana não representa distância hidráulica.

As unidades de suporte de 2,5, 5 e 10 km são experimentais.

A entropia espacial não incorpora diferenças hidroestratigráficas, temporais ou verticais.

A envoltória convexa pode superestimar a área efetivamente amostrada.

Os pontos fixos de 5 km são uma ferramenta de comparação, não observações hidrogeológicas.

O teste MAUP utiliza malhas sintéticas e não define a tesselação final.

Nenhuma métrica desta fase pode ser transformada automaticamente em prioridade.

## 16. Arquivos reproduzíveis

spatial_structure_250km2.csv

spatial_structure_500km2.csv

spatial_structure_1000km2.csv

support_points_5km.csv

scale_stability_evidence.csv

maup_variant_summary.csv

maup_origin_sensitivity_summary.csv

maup_origin_concordance.csv

maup_variant_metadata.csv

spatial_assignment_audit.csv

## 17. Referências

Clark, P. J., & Evans, F. C. (1954). Distance to nearest neighbor as a measure of spatial relationships in populations. Ecology, 35(4), 445–453. https://doi.org/10.2307/1931034

Fotheringham, A. S., & Wong, D. W. S. (1991). The modifiable areal unit problem in multivariate statistical analysis. Environment and Planning A, 23(7), 1025–1044. https://doi.org/10.1068/a231025

Keum, J., Kornelsen, K. C., Leach, J. M., & Coulibaly, P. (2017). Entropy applications to water monitoring network design. A review. Entropy, 19(11), 613. https://doi.org/10.3390/e19110613

Shannon, C. E. (1948). A mathematical theory of communication. Bell System Technical Journal, 27(3), 379–423. https://doi.org/10.1002/j.1538-7305.1948.tb01338.x

Taylor, C. J., & Alley, W. M. (2001). Ground-water-level monitoring and the importance of long-term water-level data. U.S. Geological Survey Circular 1217. https://doi.org/10.3133/cir1217
