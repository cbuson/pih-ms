# Plano da fase final de instalação móvel

## Estado atual

A V2.6.1 não é um aplicativo instalável. Ela continua sendo um visor web estático que funciona quando servido por HTTP ou HTTPS.

Esta separação é intencional. A instalação no celular exige decisões próprias sobre atualização, armazenamento, funcionamento sem rede, permissões e transparência para o usuário.

## Objetivo da fase

Permitir que PIH MS seja adicionado à tela inicial e usado com aparência de aplicativo, sem alterar os resultados científicos nem esconder as limitações dos dados.

## Componentes previstos

### Manifesto do aplicativo

- nome completo e nome curto
- URL inicial e escopo controlados
- modo de exibição independente
- cores de tema e fundo coerentes com PIH MS
- orientação flexível para mapa e documentação
- ícones de 192 e 512 pixels
- ícone adaptável para dispositivos compatíveis

### Atualização e cache

- service worker com versão explícita do cache
- atualização controlada e aviso quando houver nova versão
- limpeza de caches antigos sem apagar preferências do usuário
- página de fallback quando não houver rede
- cache inicial somente da estrutura do aplicativo e da documentação leve
- dados científicos pesados carregados sob demanda

O pacote atual possui arquivos grandes. Não se deve copiar todo o conjunto para o celular automaticamente. Essa decisão pode consumir armazenamento, falhar em aparelhos com pouco espaço e tornar a atualização difícil.

### Instalação orientada

- botão de instalação mostrado somente quando o navegador permitir
- estado claro para aplicativo já instalado
- instruções específicas para Android
- instruções manuais para iPhone e iPad quando necessárias
- explicação dentro da ajuda sobre como atualizar ou remover o aplicativo

### Funcionamento sem rede

O modo sem rede deve informar exatamente o que está disponível.

- mapa base remoto pode não aparecer
- localização do aparelho depende da permissão e do sistema
- documentos já armazenados podem continuar disponíveis
- camadas grandes não armazenadas devem mostrar mensagem de indisponibilidade
- nenhum dado ausente pode ser substituído por zero
- a versão científica e a data do cache devem permanecer visíveis

### Privacidade e permissões

- localização usada somente após ação do usuário
- nenhuma localização enviada ou guardada silenciosamente
- nenhuma coleta analítica adicionada sem decisão e informação prévias
- permissões negadas não devem bloquear o restante do visor

## Verificações obrigatórias

- primeira instalação em Android
- instalação manual em iPhone e iPad
- abertura em modo independente
- atualização da versão instalada
- funcionamento com rede lenta
- funcionamento sem rede
- recuperação depois de cache incompleto
- aparelho com pouco armazenamento
- rotação entre retrato e paisagem
- mapa, ajuda, estatísticas e documentação em tela pequena
- localização permitida, negada e indisponível
- aviso correto da versão científica carregada

## Condições de publicação

- hospedagem por HTTPS
- política de cache documentada
- ícones e manifesto validados
- nenhuma precarga automática do conjunto científico completo
- teste real em pelo menos um Android e um dispositivo Apple
- mecanismo de atualização compreensível para o usuário
- opção de continuar usando PIH MS no navegador sem instalar

## Resultado esperado

A fase poderá gerar uma V2.7 instalável ou uma versão posterior definida no momento da execução. Ela deverá preservar a ciência da versão escolhida e registrar separadamente todas as mudanças de aplicativo, cache e distribuição.
