# Fase posterior de instalação móvel

## Condición de inicio

Começar somente depois de testar a V2.6.1 no Android e confirmar que a navegação, as fichas, a prioridade, a ajuda e a documentação funcionam corretamente.

## Trabalho pendente

1. Criar um manifesto web com nome, descrição, cores e ícones próprios.
2. Projetar ícones PIH MS de 192 e 512 px e uma variante maskable.
3. Registrar um service worker com estratégia explícita por tipo de arquivo.
4. Definir quais camadas podem funcionar sem conexão.
5. Evitar que os grandes GeoJSON saturem o armazenamento do celular.
6. Mostrar o estado de disponibilidade sem conexão de cada módulo.
7. Incorporar um fluxo de instalação compreensível para Android.
8. Testar a atualização de versão e a eliminação segura de caches antigos.
9. Testar o funcionamento com conexão lenta e interrompida.
10. Revisar armazenamento, memória, bateria e uso de GPS.
11. Verificar a política de privacidade da localização.
12. Executar testes reais em vários tamanhos e navegadores móveis.

## Regla

Instalar não significa baixar toda a base científica. A futura PWA deve separar o núcleo do aplicativo, as camadas essenciais e os dados pesados opcionais.
