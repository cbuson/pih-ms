# PIH MS · Independência e redundância da evidência · V1

## Estado metodológico

Este módulo não calcula um número de “evidências independentes”, não deduplica automaticamente poços e não altera os 3.877 IDs canônicos provisórios. Seu objetivo é separar fenômenos que podem inflar a percepção de informação disponível.

**REGISTRO ≠ POÇO**  
**POÇO ≠ LOCAL INDEPENDENTE**  
**DOIS SNAPSHOTS ≠ DUAS OBSERVAÇÕES**  
**DOIS ANALITOS ≠ DUAS RÉPLICAS**  
**COORDENADA IDÊNTICA ≠ DUPLICAÇÃO DEMONSTRADA**  
**PROXIMIDADE ESPACIAL ≠ REDUNDÂNCIA HIDRÁULICA DEMONSTRADA**

## 1. Unidade básica preservada

A unidade de cadastro continua sendo `well_id`. O conjunto contém 3,877 IDs canônicos provisórios. Nenhum ID foi eliminado nesta etapa.

## 2. Redundância de fonte

Há 2,194 poços presentes tanto no snapshot atual quanto no snapshot histórico SGB 2024. Se os dois arquivos fossem simplesmente empilhados, seriam 6,071 linhas para 3,877 IDs únicos, uma inflação documental de 56.59%.

Essa inflação é de **representação de fonte**, não de observação hidrogeológica. O mesmo `well_id` em duas versões de base não deve ser interpretado como duas evidências independentes.

Para quatro campos centrais comparáveis — profundidade, nível estático, nível dinâmico e capacidade específica — existem 6,417 pares campo-poço comparáveis e 6,338 coincidem dentro das tolerâncias documentadas, equivalente a 98.77%.

## 3. Coordenadas idênticas e candidatos a duplicação

A auditoria identificou 20 grupos de coordenadas exatamente repetidas, envolvendo 40 IDs. Coordenada idêntica pode significar duplicação cadastral, arredondamento, ponto de captação comum ou múltiplos poços fisicamente distintos no mesmo local.

Existem 29 pares candidatos a duplicação, dos quais 12 são HIGH. Nenhum foi removido.

Três cenários de sensibilidade são mantidos:

1. Compressão somente por coordenada idêntica → 3,857 grupos.
2. Coordenada idêntica + candidatos HIGH → 3,855 grupos.
3. Coordenada idêntica + todos os candidatos → 3,848 grupos.

Esses valores são **cenários de revisão**, não tamanhos amostrais corrigidos.

## 4. Estrutura dos registros

Há 1,970 registros de amostra química associados a 1,767 poços. Há 2,557 resultados analíticos associados aos mesmos tipos de registros. Um resultado por analito não é uma réplica independente da água subterrânea.

Há 7,493 registros de parâmetros hidráulicos em 3,739 poços. Parâmetros diferentes, como capacidade específica, vazão estabilizada e transmissividade, respondem a grandezas diferentes e não devem ser somados como repetições equivalentes.

A capacidade específica aparece simultaneamente nos dois snapshots em 1,509 poços. Em 1,498 deles os valores são numericamente coincidentes, 99.27% dos casos comparáveis.

## 5. Diversidade documental

Para cada poço são avaliados cinco domínios separados:

- contexto aquífero cadastral
- documentação vertical/construtiva
- níveis d'água
- informação hidráulica
- química

`documentary_domains_n` varia de 0 a 5. Ele é uma medida de **diversidade documental**, não de independência estatística nem de qualidade.

518 poços, 13.36%, não apresentam nenhum desses cinco domínios adicionais no conjunto adquirido. 2,531, 65.28%, apresentam quatro ou cinco domínios.

## 6. Proximidade espacial

A distância ao vizinho mais próximo já havia sido calculada na auditoria. Nesta fase são expostos limiares descritivos de 100 m, 500 m e 1 km. 1,128 poços possuem outro poço a menos de 100 m e 2,388 a menos de 500 m.

Isso não autoriza concluir redundância hidrogeológica. Dois poços próximos podem captar profundidades, unidades, intervalos, regimes hidráulicos ou objetivos distintos.

## 7. Malhas

As métricas são agregadas diretamente aos cinco tamanhos sintéticos de 100, 150, 250, 500 e 1000 km². Nenhuma escala deriva de outra. Célula sem poço permanece `SEM_POCO_NO_CONJUNTO_AUDITADO`.

Os percentuais usam `n_wells_raw` da própria célula como denominador, salvo quando o nome do campo explicita outro denominador.

## 8. O que este módulo não faz

- não estima effective sample size
- não aplica correlação espacial para reduzir n
- não funde registros automaticamente
- não usa distância como prova de redundância
- não interpreta diversidade de atributos como independência
- não calcula score PIH
- não transforma UNKNOWN em zero

## 9. Referências metodológicas

Fellegi, I. P., & Sunter, A. B. (1969). A theory for record linkage. *Journal of the American Statistical Association, 64*(328), 1183–1210. https://doi.org/10.1080/01621459.1969.10501049

Christen, P. (2012). *Data Matching: Concepts and Techniques for Record Linkage, Entity Resolution, and Duplicate Detection*. Springer. https://doi.org/10.1007/978-3-642-31164-2

Hurlbert, S. H. (1984). Pseudoreplication and the design of ecological field experiments. *Ecological Monographs, 54*(2), 187–211. https://doi.org/10.2307/1942661

Loaiciga, H. A., Charbeneau, R. J., Everett, L. G., Fogg, G. E., Hobbs, B. F., & Rouhani, S. (1992). Review of ground-water quality monitoring network design. *Journal of Hydraulic Engineering, 118*(1), 11–37. https://doi.org/10.1061/(ASCE)0733-9429(1992)118:1(11)

Nunes, L. M., Cunha, M. C., & Ribeiro, L. (2004). Groundwater monitoring network optimization with redundancy reduction. *Journal of Water Resources Planning and Management, 130*(1), 33–43. https://doi.org/10.1061/(ASCE)0733-9496(2004)130:1(33)

Roberts, D. R., et al. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. *Ecography, 40*, 913–929. https://doi.org/10.1111/ecog.02881
