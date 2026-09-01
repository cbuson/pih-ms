# PIH MS V2.6 experimental

Prioridade de Investigação Hidrogeológica de Mato Grosso do Sul.

## Prioridade de investigação por pergunta

A V2.6 classifica a necessidade de adquirir ou revisar informação para cinco perguntas separadas. A prioridade deriva do déficit documental demonstrado e a confiança deriva da estabilidade da própria classe entre escalas e origens.

- 45.145 pares célula e pergunta
- 32.405 UNKNOWN
- 2.801 P1 crítica
- 5.448 P2 alta
- 4.491 P3 moderada
- P4 e P5 não aparecem na base atual
- confiança mantida em camada separada
- nenhuma prioridade integrada
- nenhum peso, score, interpolação ou predição

Documentos principais da fase

- `ESTUDO_PRIORIDADE_INVESTIGACAO_POR_PERGUNTA_V1.md`
- `methodology/PRIORIDADE_INVESTIGACAO_POR_PERGUNTA_V1.md`
- `AUDITORIA_CIENTIFICA_V26.md`
- `data/derived/research_priority/`

A interface documental da V2.5.1 foi preservada e ampliada para a ciência experimental V2.6. Os resultados anteriores continuam congelados e identificados por sua versão.

## Interface documental V2.6

- 15 páginas documentais com cabeçalho, navegação e rodapé comuns
- documentos abertos sobre o mapa em uma janela ampla e também disponíveis como páginas independentes
- acesso uniforme ao guia, estatísticas, métodos, dicionário, bibliografia e autoria
- índice automático em cada página documental
- controles de tamanho do texto com preferência conservada no navegador
- tipografia legível e adaptação para telas menores
- 20 resumos estatísticos atuais carregados a partir dos arquivos do projeto
- dicionário com 1.045 campos documentados
- bibliografia com 55 referências
- informação autoral completa e DOI atribuído somente à versão efetivamente publicada
- ajuda atualizada para explicar a navegação integrada

A instalação no celular ainda não faz parte desta entrega. O escopo proposto para essa fase está em `PLANO_FASE_FINAL_INSTALACAO_MOVEL.md`.

## Estabilidade e sensibilidade V2.5

- 14.284 pontos fixos de suporte
- 3.877 poços canônicos provisórios
- cinco perguntas e 39 requisitos mantidos separados
- cinco escalas e quatro origens comparadas
- 71.420 pares suporte e pergunta
- 357.100 pares suporte, escala e pergunta
- 557.076 pares suporte e requisito
- 45.145 pares célula e pergunta
- contexto hidrogeológico superficial SGB 2024 mantido como proxy pontual
- nenhum peso, score, potencial, interpolação, predição ou prioridade

## Suficiência condicionada V2.4

- Q01 · nível e profundidade da água
- Q02 · propriedades hidráulicas
- Q03 · hidroquímica
- Q04 · geometria e estratigrafia do aquífero
- Q05 · monitoramento temporal
- 19.385 pares poço e pergunta
- 45.145 pares célula e pergunta
- cinco escalas calculadas diretamente
- nenhuma quantidade mínima universal de poços
- nenhuma célula declarada representativa
- nenhum peso, score ou prioridade

Nenhum poço atende ao mínimo documental completo sob as regras conservadoras atuais. A evidência parcial permanece publicada e os bloqueios são identificados individualmente.

## Regras centrais

UNKNOWN ≠ ZERO

DENSIDADE DE POÇOS ≠ QUALIDADE DO CONHECIMENTO

CONTAGEM DE REGISTROS ≠ INFORMAÇÃO INDEPENDENTE

PROXIMIDADE ESPACIAL ≠ REDUNDÂNCIA HIDROGEOLÓGICA

PRIORIDADE DE INVESTIGAÇÃO ≠ POTENCIAL AQUÍFERO

Nenhum `well_id` foi removido. Nenhum tamanho amostral efetivo foi inferido. Nenhum índice PIH, peso, AHP, interpolação, predição ou prioridade foi calculado.

## Matriz de conhecimento efetivo V2.2

As nove dimensões são espacial, hidroestratigráfica, vertical, hidráulica, hidroquímica, temporal, independência, qualidade documental e incerteza.

- 3.877 IDs canônicos provisórios preservados
- 3.766 poços sem alerta objetivo de localização e 111 em revisão
- 842 poços com estado hidroestratigráfico UNKNOWN
- 3.414 poços com profundidade positiva e nenhum intervalo captado demonstrado
- 1.096 poços com ensaio e metadados documentais mínimos
- 51 poços com transmissividade informada e não validada
- 2.053 poços com evidência hidroquímica parcial
- 1.637 poços com ao menos um evento datado
- nenhuma série temporal completa adquirida
- independência hidrogeológica não demonstrada para os 3.877 poços
- três valores objetivamente inválidos preservados sem correção silenciosa

## Malhas vigentes

As métricas são agregadas diretamente às malhas `scale_primary` de 100, 150, 250, 500 e 1000 km². Nenhuma escala deriva de outra e nenhuma escala final é escolhida.

A família contém 3.763, 2.525, 1.537, 791 e 413 células. Em todas as escalas a soma de `n_wells` é 3.877.

A malha antiga de 250 km² com 1.554 células pertence ao produto histórico de evidências. Ela não é confundida com a malha `scale_primary` de 1.537 células.

## Documentação principal

- `ESTUDO_ESTABILIDADE_SENSIBILIDADE_V1.md`
- `methodology/ESTABILIDADE_SENSIBILIDADE_V1.md`
- `ESTUDO_SUFICIENCIA_HIDROGEOLOGICA_POR_PERGUNTA_V1.md`
- `methodology/SUFICIENCIA_HIDROGEOLOGICA_POR_PERGUNTA_V1.md`
- `methodology/DICIONARIO_METRICAS_RESULTADOS_V1.csv`
- `methodology/BIBLIOGRAFIA_MASTER_V1.csv`
- `data/derived/stability_sensitivity/`
- `PIH_MS_ESTABILIDADE_SENSIBILIDADE_V1.xlsx`

Os CSV são a referência principal. Os livros Excel são complementares para revisão humana.

## Execução local

A partir da raiz da pasta

```bash
py -m http.server 8555 --directory docs
```

Abra

```text
http://localhost:8555/index.html?v=260
```

No topo deve aparecer V2.6. O menu `Explorar` deve mostrar a prioridade por pergunta e `Documentação` deve abrir todos os materiais no mesmo padrão visual.

## Licenças

O código do aplicativo usa GNU AGPL versão 3 ou posterior. Conteúdos científicos e documentais originais usam CC BY-NC-SA 4.0, salvo indicação diferente. Materiais de terceiros conservam suas próprias condições.

## Referência de reprodutibilidade

Os CSV são a referência principal. Observações, auditorias, cenários de sensibilidade e produtos derivados permanecem separados. A V2.6 acrescenta uma classificação experimental por pergunta sem modificar os resultados das fases anteriores.
