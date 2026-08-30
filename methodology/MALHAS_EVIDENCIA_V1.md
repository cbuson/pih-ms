# PIH MS

## Malhas de evidência hidrogeológica V1

Data de corte 29 de agosto de 2026.

Esta etapa agrega diretamente as camadas E01 a E12 às geometrias candidatas de 250, 500 e 1000 km². Nenhuma escala é derivada de outra. Nenhum peso, índice PIH, favorabilidade aquífera ou prioridade foi calculado.

## Regra espacial

Cada ponto é intersectado diretamente com a geometria da malha correspondente. Em caso de coincidência com mais de uma célula seria aplicado desempate determinístico pelo identificador da célula. Não ocorreu interseção múltipla nesta execução.

Na malha de 250 km² um único poço SIAGAS, 3500073933, ficou 19,14 m fora da geometria recortada da malha apesar de pertencer à base estadual. Para não perder uma observação por uma discrepância subpixel entre geometrias de limite, foi aplicada uma única regra de contingência previamente registrada. O ponto foi associado à célula PIH-250-0007 por distância mínima, abaixo do limite de 50 m. Não houve qualquer outra atribuição por proximidade.

## Estados de suporte

`WELLS_PRESENT` indica presença de pelo menos um poço E01.

`UNKNOWN_NO_WELLS_IN_DATASET` indica que a célula não contém poços no conjunto auditado. Não significa ausência de água subterrânea.

`EVIDENCE_PRESENT` indica presença de pelo menos um poço da camada E02 a E11.

`NO_EVIDENCE_IN_AUDITED_WELLS` indica que existem poços E01 na célula, mas nenhum deles possui a evidência considerada na camada. Não prova que a informação não exista em outras fontes.

Para E12, `REVIEW_REQUIRED_PRESENT` indica pelo menos um poço sinalizado para revisão hidroestratigráfica. `NO_REVIEW_FLAG_IN_AUDITED_WELLS` significa apenas que nenhum dos poços auditados na célula recebeu esse flag.

## Métricas

Para cada célula são mantidos os números absolutos `n_E01` a `n_E12`. Para E02 a E12 calcula-se também a proporção em relação aos poços E01 da própria célula. Essa proporção mede cobertura do atributo no cadastro auditado e não conhecimento hidrogeológico total.

Foram acrescentadas estatísticas descritivas apenas quando já estavam autorizadas na metodologia das camadas, incluindo mediana e P10/P90 da profundidade E02, diversidade nominal de aquíferos E03, zeros em revisão em E04, E05 e E09, tipos de ensaio E07, composição parcial da evidência E10, antiguidade E11 e classes de revisão E12.

## O que não foi calculado

Não foi calculada independência espacial, cobertura vertical, autocorrelação, distância à evidência, kernel density, kriging, ML, score PIH ou prioridade. Essas operações pertencem às próximas etapas.
