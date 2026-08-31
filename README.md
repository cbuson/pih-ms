# PIH MS V2.5 · Estabilidade e sensibilidade

Prioridade de Investigação Hidrogeológica de Mato Grosso do Sul.

A V2.5 preserva os produtos anteriores e acrescenta a comparação dos estados documentais entre cinco escalas e quatro origens sobre 14.284 pontos fixos de suporte. Nenhuma escala, origem ou prioridade é escolhida.

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

## Matriz V2.4

- Q01 · nível e profundidade da água
- Q02 · propriedades hidráulicas
- Q03 · hidroquímica
- Q04 · geometria e estratigrafia do aquífero
- Q05 · monitoramento temporal
- 19.385 pares poço-pergunta
- 45.145 pares célula-pergunta
- cinco escalas calculadas diretamente
- nenhuma quantidade mínima universal de poços
- nenhuma célula declarada representativa
- nenhum peso, score ou prioridade

Nenhum poço atende ao mínimo documental completo sob as regras conservadoras atuais. A evidência parcial permanece publicada e os bloqueios são identificados individualmente.

## Interface V2.2.1

- sete acessos principais no menu superior
- módulos científicos reunidos em `Explorar`
- guia, dicionário, bibliografia, metodologia e direitos reunidos em `Documentação`
- ajuda ampliada com 18 temas e busca interna
- 11 resumos estatísticos atuais disponíveis em tabelas completas
- busca e contagem de camadas no painel lateral
- ícone de localização baseado no contorno de Mato Grosso do Sul
- marcador de posição, círculo de precisão e estados visuais de localização
- fichas de poço carregadas em 64 fragmentos de aproximadamente 640 KB em média
- autores, instituições, funções, ORCID, DOI e justificativa de licença na informação do aplicativo

As lacunas de escalas 100 e 150 km² e a validação integral das fichas estão registradas em `BACKLOG_CIENTIFICO_POS_V221.md`.

## Regras centrais

UNKNOWN ≠ ZERO

DENSIDADE DE POÇOS ≠ QUALIDADE DO CONHECIMENTO

CONTAGEM DE REGISTROS ≠ INFORMAÇÃO INDEPENDENTE

PROXIMIDADE ESPACIAL ≠ REDUNDÂNCIA HIDROGEOLÓGICA

PRIORIDADE DE INVESTIGAÇÃO ≠ POTENCIAL AQUÍFERO

Nenhum `well_id` foi removido. Nenhum tamanho amostral efetivo foi inferido. Nenhum índice PIH, peso, AHP, interpolação, predição ou prioridade foi calculado.

## Matriz V2.2

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
- 3 valores objetivamente inválidos preservados sem correção silenciosa

## Malhas V2.2

As métricas são agregadas diretamente às malhas `scale_primary` de 100, 150, 250, 500 e 1000 km². A V2.2 não deriva uma escala da outra e não escolhe uma escala final.

A família contém 3.763, 2.525, 1.537, 791 e 413 células. Em todas as escalas a soma de `n_wells` é 3.877 e coincide com `n_wells_raw` da V2.1 em cada célula.

A malha antiga de 250 km² com 1.554 células pertence ao produto anterior de evidências e não é confundida com a malha `scale_primary` de 1.537 células.

## Documentação

- `ESTUDO_CONHECIMENTO_HIDROGEOLOGICO_EFETIVO_V1.md`
- `methodology/CONHECIMENTO_HIDROGEOLOGICO_EFETIVO_V1.md`
- `methodology/CONHECIMENTO_HIDROGEOLOGICO_EFETIVO_CAMPOS_V1.csv`
- `methodology/DICIONARIO_METRICAS_RESULTADOS_V1.csv`
- `methodology/BIBLIOGRAFIA_MASTER_V1.csv`
- `data/derived/effective_knowledge/`
- `PIH_MS_CONHECIMENTO_HIDROGEOLOGICO_EFETIVO_V1.xlsx`

O dicionário V2.2 documenta 680 campos. A bibliografia master mantém 54 referências classificadas por função e estado de uso.

## Execução local

A partir da raiz da pasta

```bash
py -m http.server 8555 --directory docs
```

Abra

```text
http://localhost:8555/index.html?v=221
```

No topo deve aparecer V2.2.1 e o menu `Explorar`.

## Licenças

O código do aplicativo usa GNU AGPL versão 3 ou posterior. Conteúdos científicos e documentais originais usam CC BY-NC-SA 4.0, salvo indicação diferente. Materiais de terceiros conservam suas próprias condições.

## Referência de reprodutibilidade

Os CSV são a referência principal. O Excel é complementar para revisão humana. Observações, auditorias, cenários de sensibilidade e produtos derivados permanecem separados.
