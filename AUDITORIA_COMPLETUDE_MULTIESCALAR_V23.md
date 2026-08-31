# Auditoria de completude multiescalar V2.3

## Escopo

A V2.3 completa as escalas de 100 e 150 km² nos módulos de malhas de evidência e estrutura espacial. As cinco escalas usam a família principal `SCALE_PRIMARY_O00_V1`.

Nenhuma escala foi adotada como definitiva. Nenhum peso, score PIH, potencial, interpolação ou prioridade foi calculado.

## Cobertura concluída

| Módulo | 100 | 150 | 250 | 500 | 1000 |
|---|---:|---:|---:|---:|---:|
| Malhas de evidência E01 a E12 | sim | sim | sim | sim | sim |
| Estrutura espacial | sim | sim | sim | sim | sim |

Contagens da família principal

- 100 km² com 3.763 células
- 150 km² com 2.525 células
- 250 km² com 1.537 células
- 500 km² com 791 células
- 1000 km² com 413 células

## Preservação científica

Cada escala foi recalculada diretamente desde as feições auditadas E01 a E12. As somas por escala coincidem com 3.877 registros E01, 3.414 E02, 3.097 E03, 3.213 E04, 3.180 E05, 3.051 E06, 1.106 E07, 1.096 E08, 51 E09, 2.053 E10, 1.637 E11 e 1.823 E12.

A família candidata anterior de 250, 500 e 1000 km² foi preservada como produto histórico. Seus 1.554 hexágonos de 250 km² não são misturados com os 1.537 hexágonos da família principal.

## Fichas

As fichas de célula usam os atributos do GeoJSON ativo. Foram verificados casos iniciais, centrais e finais de cada combinação entre módulo e escala. Os 3.877 poços continuam distribuídos em 64 fragmentos de ficha sem perda de identificadores.

## Limites

A prova visual remota do visor não pôde ser concluída porque o ambiente de prévia não aceita diretamente este pacote estático sem uma estrutura de desenvolvimento adicional. A validação local cobriu HTML, JavaScript, arquivos carregados, seletores, cardinalidades, contratos de ficha e integridade dos pacotes.

