# PIH MS · preparação do primeiro DOI no Zenodo

## Arquivos que devem ficar na raiz do repositório

CITATION.cff

.zenodo.json

Os dois arquivos podem coexistir. Para a importação de um release pelo Zenodo, .zenodo.json tem prioridade. CITATION.cff continua sendo útil no GitHub para gerar a sugestão de citação.

## Antes de criar o release

1. Copiar CITATION.cff para a raiz de pih-ms
2. Copiar .zenodo.json para a raiz de pih-ms
3. Fazer commit
4. Fazer push para main
5. Confirmar que a versão continua sendo 2.2.1
6. Confirmar que LICENSE, LICENSE-CONTENT.md, NOTICE e THIRD_PARTY_NOTICES.md estão presentes

## No Zenodo

1. Entrar na área GitHub da conta Zenodo
2. Sincronizar os repositórios
3. Ativar cbuson/pih-ms
4. Voltar ao GitHub
5. Criar o release v2.2.1
6. Usar como título PIH MS v2.2.1
7. Colar o conteúdo de RELEASE_NOTES_v2.2.1.md na descrição do release
8. Publicar o release
9. Aguardar o processamento do Zenodo

## Verificação do registro Zenodo

Título

PIH MS · Prioridade de Investigação Hidrogeológica de Mato Grosso do Sul

Versão

2.2.1

Tipo

Software

Criadores

Carlos Busón Buesa
ORCID 0000-0002-1446-2252
Universidade Federal de Mato Grosso do Sul

Sandra Garcia Gabas
ORCID 0000-0002-1027-0288
Universidade Federal de Mato Grosso do Sul

Licença principal do software

AGPL-3.0-or-later

Licença dos conteúdos científicos e documentais originais

CC BY-NC-SA 4.0

O repositório possui licenciamento misto. Como .zenodo.json usa uma licença principal para o registro de software, AGPL-3.0-or-later foi indicada como licença principal. Depois que o registro for criado, verificar a área de direitos do Zenodo e acrescentar CC BY-NC-SA 4.0 como segunda licença para os conteúdos científicos e documentais. Não substituir as condições próprias dos materiais de terceiros.

## Depois que o DOI existir

Guardar dois identificadores diferentes quando o Zenodo os apresentar

DOI específico da versão 2.2.1

DOI de conceito que reúne todas as futuras versões

Para artigos que dependam exatamente desta versão, usar o DOI específico da versão.

Para citar o projeto de forma geral e acompanhar futuras versões, pode ser útil o DOI de conceito.

Não inserir um DOI inventado no repositório. Atualizar os metadados somente depois de o Zenodo fornecer o identificador real.
