# V2.6.1 · navegação móvel · 2026-09-01

- mapa definido como primeira tela no celular
- nova barra inferior com cinco destinos principais
- painel de camadas e fichas em largura total
- grupos de camadas recolhidos inicialmente
- acesso direto ao módulo de prioridade V2.6
- legenda recolhida por padrão e aberta sob demanda
- zoom por gesto priorizado e controles flutuantes reduzidos
- tipografia e alvos táteis ampliados
- navegação documental unificada e tabelas com rolagem horizontal controlada
- nenhuma alteração nos dados, regras, classes ou resultados científicos da V2.6

# V2.6 experimental · 2026-09-01

- prioridade de investigação calculada separadamente para cinco perguntas
- classes UNKNOWN, P1, P2, P3, P4 e P5 definidas sem compensação
- confiança UNKNOWN, C1, C2, C3, C4 e C5 mantida em camada independente
- estabilidade da prioridade verificada em cinco escalas e quatro origens
- 45.145 pares célula e pergunta classificados
- 1.045 campos documentados e 20 resumos no visor
- nova ficha com bloqueios e ações recomendadas
- paleta em cinza, vermelho, laranja, morado, turquesa e verde
- nenhum peso, score, interpolação, potencial ou prioridade integrada

# V2.5.1 · 2026-08-31

- navegação e identidade visual comuns nas 15 páginas documentais
- documentação aberta sobre o mapa ou como página independente
- guia, estatísticas, métodos, dicionário, bibliografia e autoria reunidos no mesmo padrão
- índice automático e controles de tamanho do texto em cada documento
- tipografia e tabelas ajustadas para leitura em computador e celular
- 17 resumos estatísticos atuais ligados ao visor
- dicionário de 916 campos e bibliografia de 55 referências apresentados corretamente
- informação autoral revisada sem atribuir à V2.5.1 um DOI ainda inexistente
- plano separado para a futura instalação no celular
- nenhum resultado científico da V2.5 recalculado

# V2.5 · 2026-08-31

- estabilidade dos estados de Q01 a Q05 comparada nas cinco escalas sobre 14.284 pontos fixos
- sensibilidade a O00, OX25, OY25 e OXY25 calculada sem deslocar poços ou suportes
- persistência dos 39 requisitos calculada somente em escalas observáveis
- contexto hidrogeológico superficial SGB 2024 mantido como proxy pontual
- 916 campos documentados e 17 resumos no visor
- novo módulo cartográfico com cinco escalas, cinco perguntas e seis métricas
- nenhuma escala, origem, representatividade, peso, score ou prioridade adotada

# Fechamento documental adicional V2.0

- Bibliografia master expandida para 43 referências classificadas por uso.
- Incluídos fundamentos hidrogeológicos de Theis, Cooper–Jacob, Kruseman/de Ridder, Freeze & Cherry, Fetter, ASTM D4043, USGS NFM e ISO 5667-11.
- Incluído Sophocleous 1983 como antecedente de desenho de rede, explicitamente não implementado.
- Guia dos resultados ampliado com interpretação detalhada e exemplos.
- 47 campos anteriormente genéricos receberam definição específica. O dicionário final possui 464 campos e zero descrições genéricas.
- Fichas de malha, estrutura, escala, estratificação e vertical/tempo receberam ligação contextual ao guia.

# CHANGELOG

## V2.3 · 2026-08-30

- malhas de evidência E01 a E12 completadas em 100, 150, 250, 500 e 1000 km²
- estrutura espacial completada nas mesmas cinco escalas
- família principal O00 usada de forma uniforme nos módulos correntes
- família candidata anterior preservada como produto histórico
- fichas de célula habilitadas nas cinco escalas
- estatísticas atualizadas para cinco escalas nos dois módulos
- nenhum score PIH, peso, interpolação, potencial ou prioridade calculado

## V1.1

- adicionadas doze camadas independentes da Matriz de Evidência Hidrogeológica V1
- metodologia individual disponível a partir do menu de camadas
- nenhuma camada recebeu peso, prioridade ou interpolação
- seleção de qualquer feição de evidência abre a ficha completa do poço

## V1.3 · 2026-08-29
- Malhas de evidência E01–E12 em 250, 500 e 1000 km².
- Fichas de célula com matriz completa.
- Auditoria da atribuição espacial.
- Nenhum score PIH.

## V1.6 · 2026-08-29
- Estrutura espacial E01 com vizinho mais próximo, suporte 2,5/5/10 km, redundância proxy, entropia e concentração.
- Distância à evidência E01–E12 mediante suporte fixo de 5 km.
- Estabilidade 250/500/1000 km² sobre suporte comum.
- Primeiro ensaio MAUP com quatro origens sintéticas por escala.
- Nenhum score PIH.

## V1.6 fechamento técnico

- estrutura do pacote limpa de iniciadores legados de versões anteriores
- README consolidado para V1.6
- scripts de estrutura espacial e MAUP convertidos para caminhos relativos ao projeto
- Excel de revisão `PIH_MS_ESTRUTURA_ESPACIAL_V1.xlsx` incorporado
- sintaxe JavaScript e Python verificada


## V1.7

- adicionadas escalas sintéticas comparáveis de 100 e 150 km², além de 250, 500 e 1000 km²
- adicionado estudo de estabilidade entre escalas sobre 14.284 pontos fixos
- adicionado MAUP por quatro deslocamentos de origem em E01, E07, E09 e E10
- adicionada heterogeneidade hidrogeológica baseada no suporte fixo de 5 km
- nenhuma escala adotada

## V1.8 · 2026-08-29
- Estratificação pelas 16 unidades hidroestratigráficas SGB 2024 e 3 domínios hidrolitológicos.
- Distância à evidência do mesmo estrato.
- Mascaramento por agregação medido com 14.284 pontos fixos de suporte.
- Composição de células calculada por overlay vetorial exato em EPSG 5880.
- Novo módulo Estratos no visor.
- Nenhuma escala ou score PIH adotado.

## V1.9 · 2026-08-29
- documentação vertical V01–V08 e temporal T01–T07
- malhas verticais e temporais em 100, 150, 250, 500 e 1000 km²
- V08 permanece UNKNOWN por ausência de tabela relacional de filtros ou telas
- T07 permanece UNKNOWN por ausência de série completa adquirida da mesma variável
- identificação de 22 registros RIMAS diretamente pelo campo original status_rimas
- correção transparente do indicador RIMAS incorreto na primeira tabela wells_master
- ficha individual do poço ampliada com documentação vertical e temporal
- nenhuma prioridade, peso ou score PIH calculado

## V2.0 · documentação científica

- Bibliografia master consolidada e separada por estado de uso.
- Guia extenso de leitura das malhas e dos resultados.
- Dicionário exaustivo dos campos derivados.
- Ajuda contextual para os seletores de evidência, estrutura espacial, escalas, estratos e vertical-temporal.
- Links transversais inseridos em todas as páginas metodológicas.
- Nenhum cálculo científico da V1.9 foi alterado.

- Bibliografia master ampliada para 51 referências, incluindo crítica conceitual de groundwater potential e antecedentes adicionais de desenho de redes.


## V2.1 · 2026-08-29
- módulo Independência e redundância
- malhas 100, 150, 250, 500 e 1000 km²
- diagnóstico de sobreposição entre snapshots
- cenários de revisão sem deduplicação automática
- diversidade documental 0–5 por poço
- fichas de poço e célula ampliadas
- bibliografia e dicionário atualizados

## V2.2.1 · 2026-08-30

- menu superior reduzido de 17 botões para 7 acessos principais
- módulos reunidos em `Explorar` e materiais reunidos em `Documentação`
- ajuda ampliada para 18 temas com índice e busca
- painel de estatísticas com os 11 resumos atuais completos
- busca, contagem ativa, expansão e recolhimento no painel de camadas
- localização com ícone baseado no contorno de MS, precisão e estados visuais
- carregamento de fichas de poço dividido em 64 fragmentos
- clique de célula reforçado para todos os módulos de malha
- autoria completa, ORCID, DOI e justificativa da licença na informação
- código sob AGPL-3.0-or-later
- conteúdos originais sob CC BY-NC-SA 4.0
- lacunas de 100 e 150 km² e validação de fichas registradas no backlog
- nenhum resultado científico da V2.2 alterado

## V2.2 · 2026-08-30

- matriz de conhecimento hidrogeológico efetivo por poço e célula
- nove dimensões mantidas separadamente
- estados documentado, parcial, revisão e UNKNOWN sem agregação
- malhas `scale_primary` de 100, 150, 250, 500 e 1000 km²
- 3.877 IDs preservados em cada escala
- ficha individual do poço ampliada com vetor V2.2
- novo módulo `Conhecimento` no visor
- dicionário mestre ampliado de 553 para 680 campos
- Excel complementar de revisão humana
- nenhum índice, peso, potencial, predição ou prioridade calculado
