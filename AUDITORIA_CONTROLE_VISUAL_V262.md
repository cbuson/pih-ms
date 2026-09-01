# Auditoria de controle visual PIH MS V2.6.2

## Escopo

A V2.6.2 resolve o controle de transparência das camadas com prioridade para uso em celular. Nenhum dado científico, regra, classe, estatística ou resultado da V2.6 foi recalculado.

## Problema observado

No celular o catálogo completo é adequado para descobrir e ativar camadas, mas é longo demais para administrar repetidamente a aparência do mapa. Um controle global de transparência também seria inadequado porque impediria comparar duas camadas com intensidades diferentes.

## Solução adotada

Foi criada uma bandeja Camadas visíveis sobre o mapa. Ela mostra somente as camadas realmente ativas e oferece para cada uma

- transparência individual de 10 a 100 por cento
- atalhos de 25, 50, 75 e 100 por cento
- valor atual explícito
- remoção direta do mapa
- envio à frente dentro da ordem cartográfica compatível

Também existe restauração conjunta a 100 por cento e ligação direta ao catálogo completo.

## Arquitetura

O catálogo continua responsável por ativar novas camadas. A bandeja contextual administra somente o estado visual das camadas já carregadas. Essa separação reduz rolagem e evita duplicar o catálogo inteiro sobre o mapa.

A aplicação da transparência preserva a opacidade original de bordas e preenchimentos. O percentual escolhido atua como multiplicador visual reversível. Em rasters preserva a opacidade original definida pelo projeto. No mapa hidrogeológico aplica o mesmo fator aos polígonos e aos contatos associados.

## Cobertura

O controle cobre

- camadas vetoriais de referência e contexto
- pontos e evidências E01 a E12
- documentação vertical e temporal
- rasters de visualização
- dez famílias de malhas analíticas

As famílias analíticas cobertas são prioridade, estabilidade, suficiência, conhecimento efetivo, independência, vertical e temporal, estrutura espacial, malha de evidência, estratificação e estudo de escala.

## Decisões para celular

- botão contextual separado de Legenda
- folha inferior acima da navegação principal
- alvos táteis mínimos de 44 pixels
- valores rápidos que evitam depender da precisão do deslizador
- processamento do deslizador limitado por intervalo curto para reduzir trabalho repetido em malhas extensas
- área segura inferior para Android e iOS
- fechamento por botão, fundo ou tecla Escape

## Limites deliberados

O mapa base não entra no controle porque já possui seletor próprio. A posição do usuário e o destaque temporário da feição selecionada também não são tratados como camadas científicas. A ordem entre painéis cartográficos incompatíveis permanece protegida pelos painéis internos do mapa. A ação Trazer à frente atua dentro dessa ordem segura.

Os ajustes são temporários durante a sessão. Não alteram arquivos e não são guardados como preferência permanente. A validação final em dispositivos físicos continua recomendada para confirmar conforto tátil em diferentes navegadores e tamanhos de tela.

## Controles executados

- sintaxe de todos os JavaScript alterados
- identificadores HTML únicos
- relações acessíveis entre botão e bandeja
- cobertura de dez famílias analíticas
- tratamento separado de vetores, pontos e rasters
- intervalo e atalhos de transparência
- ajuda atualizada
- 16 páginas documentais preservadas
- cardinalidades científicas preservadas
- verificação SHA 256 dos arquivos científicos contra o manifesto V2.6

## Resultado

A V2.6.2 acrescenta controle visual avançado sem modificar a ciência congelada. A fase seguinte pode ser a validação em celulares reais e, depois, a instalação como PWA em uma versão separada.
