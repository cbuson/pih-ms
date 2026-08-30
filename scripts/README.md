# Scripts reproduzíveis PIH MS V2.2.1

- `build_ui_support_v221.py` gera os 11 resumos para o visor, os 64 fragmentos de fichas, o ícone de localização e a cópia da AGPL v3.
- `update_ui_v221.py` aplica a estrutura HTML de navegação, ajuda, estatísticas e autoria.
- `update_ui_logic_v221.py` normaliza os controladores da interface.

- `build_evidence_layers_v1.py` cria E01 a E12.
- `build_grid_evidence_v1.py` calcula evidência nas malhas candidatas.
- `calc_spatial_structure_v1.py` calcula estrutura espacial e vazios.
- `calc_maup_origin_v1.py` testa deslocamento de origem.
- `calc_scale_candidates_v1.py` compara 100, 150, 250, 500 e 1000 km².
- `calc_stratified_hydro_v1.py` estratifica evidência e escalas por unidade hidroestratigráfica e domínio hidrolitológico.
- `build_vertical_temporal_v1.py` constrói as camadas V01–V08 e T01–T07, as tabelas por poço e as malhas verticais e temporais.

Os scripts não devem converter UNKNOWN em ausência hidrogeológica nem em prioridade.

- `build_independence_grids_v1.py` recalcula as agregações de independência e redundância a partir do CSV auditado por poço.
- `build_effective_knowledge_v1.py` constrói o vetor V2.2 por poço, agrega-o às cinco malhas e atualiza as fichas do visor.
- `update_effective_knowledge_documentation_v1.py` atualiza o anexo metodológico de campos, o dicionário mestre e a página pesquisável.
- `qa_release_v22.py` audita cardinalidade, estados UNKNOWN, equivalência entre malhas, JSON, HTML, dicionário e bibliografia.
- `finalize_release_v22.py` atualiza os manifestos e os checksums da entrega V2.2.
- `package_release_v22.py` cria o ZIP final com diretório superior identificado como V2.2.
