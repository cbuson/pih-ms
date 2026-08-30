# Backlog científico posterior à V2.2.1

Este arquivo impede que as lacunas identificadas durante a revisão de interface sejam esquecidas. Nenhum item abaixo foi resolvido por inferência nesta versão.

## Cobertura atual de escalas

| Módulo | 100 | 150 | 250 | 500 | 1000 | Situação |
|---|---:|---:|---:|---:|---:|---|
| Comparação de escalas `scale_primary` | sim | sim | sim | sim | sim | completa |
| Estratificação hidrogeológica | sim | sim | sim | sim | sim | completa |
| Documentação vertical e temporal | sim | sim | sim | sim | sim | completa |
| Independência e redundância | sim | sim | sim | sim | sim | completa |
| Conhecimento hidrogeológico efetivo | sim | sim | sim | sim | sim | completa |
| Malha de evidência E01 a E12 | não | não | sim | sim | sim | falta 100 e 150 |
| Estrutura espacial | não | não | sim | sim | sim | falta 100 e 150 |
| Malhas candidatas anteriores | não | não | sim | sim | sim | decidir extensão ou retirada |

Contagens da família principal

- 100 km² com 3.763 células
- 150 km² com 2.525 células
- 250 km² com 1.537 células
- 500 km² com 791 células
- 1000 km² com 413 células

A malha de evidência anterior possui 1.554 células em 250 km² e não é equivalente à malha principal de 1.537 células.

## Próximos trabalhos obrigatórios

### P1 · Malhas de evidência em 100 e 150 km²

Recalcular diretamente de E01 a E12. Não derivar uma escala da outra. Publicar GeoJSON, CSV, resumo, metadados de estilo, procedência e testes de soma.

### P2 · Estrutura espacial em 100 e 150 km²

Recalcular distâncias, suporte, lacunas, sensibilidade e metadados nas duas escalas. Verificar comparabilidade antes de incorporar ao visor.

### P3 · Contrato completo das fichas de célula

Cada ficha deverá explicar a métrica, o cálculo, a interpretação permitida, a interpretação proibida, a unidade, os limites, a regra de UNKNOWN, a procedência e a metodologia correspondente.

### P4 · Teste funcional de fichas

Executar uma matriz automatizada de módulo, escala, métrica e célula. Confirmar abertura, valores, estado vazio, links metodológicos, legenda e resposta em dispositivos móveis.

### P5 · Coexistência das duas famílias de malha

Decidir se as malhas candidatas anteriores de 250, 500 e 1000 km² devem receber 100 e 150 km² ou ser apresentadas apenas como produto histórico. Evitar que 1.554 e 1.537 células de 250 km² sejam confundidas.

### P6 · Validação integral das fichas de poço

Os 3.877 poços possuem registro detalhado e a V2.2.1 reduz a carga por fragmentação. Ainda é necessário testar amostras estratificadas e casos com muitos campos, UNKNOWN, alertas, duplicações candidatas e registros SGB 2024.

## Regra para a próxima fase

Nenhuma ausência de escala, ficha ou atributo autoriza preencher valores por interpolação, herança entre escalas ou suposição documental.

