#!/usr/bin/env python3
"""Atualiza o dicionário mestre e a página estática para o módulo V2.2."""
from __future__ import annotations

import csv
import html
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DER = ROOT / "data/derived/effective_knowledge"
MASTER = ROOT / "methodology/DICIONARIO_METRICAS_RESULTADOS_V1.csv"
MODULE = "Conhecimento hidrogeológico efetivo V2.2"
SOURCES = (
    "well_effective_knowledge.csv | effective_knowledge_*km2.csv | "
    "effective_knowledge_global_summary.csv | effective_knowledge_scale_summary.csv | "
    "effective_knowledge_registry.csv | effective_knowledge_assignment_audit.csv"
)

FILES = [
    "well_effective_knowledge.csv",
    "effective_knowledge_250km2.csv",
    "effective_knowledge_global_summary.csv",
    "effective_knowledge_scale_summary.csv",
    "effective_knowledge_registry.csv",
    "effective_knowledge_assignment_audit.csv",
]

columns = []
for filename in FILES:
    for column in pd.read_csv(DER / filename, encoding="utf-8-sig", nrows=0).columns:
        if column not in columns:
            columns.append(column)


labels = {
    "spatial_coordinate_review": "poços cuja coordenada está marcada para revisão",
    "spatial_municipality_mismatch": "poços com divergência entre município declarado e município espacial",
    "hydrostrat_unknown": "poços com estado hidroestratigráfico UNKNOWN",
    "hydrostrat_review": "poços cuja comparação hidroestratigráfica requer revisão",
    "vertical_depth_positive": "poços com profundidade total positiva documentada",
    "vertical_metadata_present": "poços com ao menos um metadado vertical além da profundidade",
    "vertical_top_base_raw_coherent": "poços com topo e base brutos positivos e coerentes",
    "vertical_capture_interval_demonstrated": "poços com intervalo captado demonstrado",
    "hydraulic_static_level": "poços com nível estático disponível",
    "hydraulic_dynamic_level": "poços com nível dinâmico disponível",
    "hydraulic_specific_capacity_nonnegative": "poços com capacidade específica não negativa",
    "hydraulic_test_registered": "poços com ensaio de bombeamento cadastrado",
    "hydraulic_test_minimum_metadata": "poços com ensaio e metadados documentais mínimos",
    "hydraulic_transmissivity_reported": "poços com transmissividade informada e não validada",
    "hydrochemical_partial_evidence": "poços com evidência hidroquímica parcial",
    "hydrochemical_dated": "poços com evidência hidroquímica datada",
    "temporal_any_dated": "poços com ao menos um evento hidrogeológico datado",
    "temporal_multiple_domains": "poços com evidência datada em dois ou mais domínios",
    "temporal_time_series_demonstrated": "poços com série temporal demonstrada",
    "independence_duplicate_candidate": "poços candidatos a duplicidade HIGH ou MEDIUM",
    "independence_exact_colocation": "poços em coordenada exatamente compartilhada",
    "independence_nn_lt_500m": "poços com vizinho mais próximo a menos de 500 m",
    "independence_source_snapshot_overlap": "poços presentes nos dois snapshots auditados",
    "documentary_flagged_wells": "poços com ao menos um alerta documental",
    "documentary_invalid_wells": "poços com ao menos um valor objetivamente inválido preservado",
    "hydrochemical_samples": "amostras hidroquímicas cadastradas",
    "hydrochemical_results": "resultados hidroquímicos cadastrados",
    "hydrochemical_parameter_types": "tipos distintos de parâmetro hidroquímico",
}


special = {
    "municipality_declared": ("Município declarado no cadastro do poço.", "texto"),
    "municipality_spatial": ("Município obtido pela associação espacial auditada.", "texto"),
    "method_version": ("Identificador da versão da regra que produziu o registro.", "texto"),
    "spatial_coordinate_valid": ("Indicador de coordenada válida segundo as regras objetivas vigentes.", "booleano"),
    "spatial_coordinate_review": ("Indicador de coordenada preservada com alerta de revisão.", "booleano"),
    "spatial_municipality_agreement": ("Indicador de concordância entre município declarado e município espacial.", "booleano"),
    "spatial_nearest_neighbor_m": ("Distância ao poço canônico mais próximo, usada somente como contexto espacial.", "m"),
    "hydrostrat_comparison_status_source": ("Estado original da comparação entre aquífero SIAGAS e referência SGB 2024.", "categoria"),
    "hydrostrat_manual_review_required": ("Indicador de revisão manual requerida pela auditoria hidroestratigráfica.", "booleano"),
    "vertical_depth_positive": ("Indicador de profundidade total positiva documentada.", "booleano"),
    "vertical_top_base_raw_coherent": ("Indicador de topo e base brutos positivos com base maior que topo.", "booleano"),
    "vertical_capture_interval_status": ("Estado explícito da disponibilidade de intervalo filtrado ou aberto.", "categoria"),
    "hydraulic_static_level_available": ("Indicador de nível estático disponível.", "booleano"),
    "hydraulic_dynamic_level_available": ("Indicador de nível dinâmico disponível.", "booleano"),
    "hydraulic_specific_capacity_nonnegative": ("Indicador de capacidade específica disponível e não negativa.", "booleano"),
    "hydraulic_test_registered": ("Indicador de ensaio de bombeamento cadastrado.", "booleano"),
    "hydraulic_test_minimum_metadata": ("Indicador de ensaio com metadados documentais mínimos segundo E08.", "booleano"),
    "hydraulic_transmissivity_reported": ("Indicador de transmissividade informada, sem validação do parâmetro.", "booleano"),
    "hydraulic_components_documented_n": ("Número de componentes documentais E04 a E09 presentes no poço.", "n"),
    "hydrochemical_partial_evidence": ("Indicador de evidência hidroquímica parcial segundo E10.", "booleano"),
    "hydrochemical_dated": ("Indicador de data de coleta ou análise hidroquímica interpretável.", "booleano"),
    "hydrochemical_samples_n": ("Número de registros de amostra hidroquímica associados ao poço ou à célula.", "n"),
    "hydrochemical_results_n": ("Número de resultados hidroquímicos associados ao poço ou à célula.", "n"),
    "hydrochemical_parameter_types_n": ("Número de tipos distintos de parâmetro hidroquímico associados ao poço ou à célula.", "n"),
    "temporal_any_dated": ("Indicador de pelo menos um evento datado entre teste, química e nível.", "booleano"),
    "temporal_dated_domains_n": ("Número de domínios distintos com evidência datada no poço.", "n"),
    "temporal_latest_evidence_date": ("Data mais recente entre os eventos datados adquiridos.", "data"),
    "temporal_latest_evidence_age_years": ("Idade da evidência datada mais recente no corte de 2026-08-29.", "anos"),
    "temporal_rimas_registered": ("Indicador de cadastro identificado como RIMAS no snapshot atual.", "booleano"),
    "temporal_time_series_status": ("Estado explícito da disponibilidade de série temporal completa.", "categoria"),
    "independence_review_context": ("Contexto documental ou espacial que motiva ou não revisão de independência.", "categoria"),
    "independence_duplicate_candidate_level": ("Nível NONE, MEDIUM ou HIGH do candidato a duplicidade documental.", "categoria"),
    "independence_exact_coordinate_colocation": ("Indicador de coordenada exatamente compartilhada por outro ID.", "booleano"),
    "independence_source_snapshot_overlap": ("Indicador de presença do mesmo ID nos dois snapshots auditados.", "booleano"),
    "documentary_quality_flags_n": ("Número total de alertas de qualidade associados ao poço.", "n"),
    "documentary_review_flags_n": ("Número de alertas de severidade REVIEW associados ao poço.", "n"),
    "documentary_invalid_flags_n": ("Número de alertas de severidade INVALID associados ao poço.", "n"),
    "uncertainty_codes": ("Lista delimitada de limitações e UNKNOWN aplicáveis ao registro.", "lista categórica"),
    "dimension_vector_json": ("Objeto JSON com o estado separado das nove dimensões.", "JSON"),
    "spatial_gap_E01_p90_km": ("Percentil 90 da distância do suporte fixo da célula ao poço canônico mais próximo.", "km"),
    "hydrostrat_units_n": ("Número de unidades hidroestratigráficas que intersectam a célula.", "n"),
    "hydrostrat_dominant_unit": ("Unidade hidroestratigráfica de maior fração areal na célula.", "categoria"),
    "hydrostrat_dominant_unit_pct": ("Fração areal da unidade hidroestratigráfica dominante na célula.", "%"),
    "hydrostrat_domains_n": ("Número de domínios hidrolitológicos que intersectam a célula.", "n"),
    "hydrostrat_dominant_domain": ("Domínio hidrolitológico de maior fração areal na célula.", "categoria"),
    "hydrostrat_dominant_domain_pct": ("Fração areal do domínio hidrolitológico dominante na célula.", "%"),
    "hydrostrat_E01_unit_masked": ("Indicador de poço E01 presente apenas fora da unidade dominante da célula.", "booleano"),
    "hydrostrat_E01_domain_masked": ("Indicador de poço E01 presente apenas fora do domínio dominante da célula.", "booleano"),
    "temporal_latest_evidence_age_median_years": ("Mediana da idade da evidência mais recente entre poços datados da célula.", "anos"),
    "documentary_domains_median": ("Mediana do número de domínios documentais por poço na célula.", "n"),
    "metric": ("Código da métrica registrada no resumo global.", "texto"),
    "cells_with_wells_n": ("Número de células com ao menos um poço canônico atribuído.", "n"),
    "cells_without_wells_n": ("Número de células sem poço no conjunto auditado.", "n"),
    "cells_with_wells_pct": ("Percentual de células com ao menos um poço canônico atribuído.", "%"),
    "canonical_wells_assigned_n": ("Número de IDs canônicos atribuídos à escala.", "n"),
    "scale_selection_status": ("Estado explícito da seleção de escala.", "categoria"),
    "dimension": ("Nome de uma das nove dimensões mantidas separadamente.", "categoria"),
    "state_field": ("Campo que armazena o estado categórico da dimensão.", "texto"),
    "what_it_describes": ("Leitura permitida para a dimensão.", "texto"),
    "what_it_does_not_mean": ("Leitura que a dimensão não autoriza.", "texto"),
    "assignment_method": ("Método usado para associar o poço à célula.", "categoria"),
    "assignment_distance_m": ("Distância registrada pela contingência de associação espacial.", "m"),
    "boundary_candidates_n": ("Número de células candidatas no tratamento determinístico de fronteira.", "n"),
}


state_fields = {
    "spatial_state": "Estado descritivo da dimensão espacial.",
    "hydrostrat_state": "Estado descritivo da dimensão hidroestratigráfica.",
    "vertical_state": "Estado descritivo da dimensão vertical.",
    "hydraulic_state": "Estado descritivo da dimensão hidráulica.",
    "hydrochemical_state": "Estado descritivo da dimensão hidroquímica.",
    "temporal_state": "Estado descritivo da dimensão temporal.",
    "independence_state": "Estado da independência hidrogeológica, mantido UNKNOWN nesta fase.",
    "documentary_state": "Estado descritivo dos alertas de qualidade documental.",
    "uncertainty_state": "Estado que declara a incerteza explícita sem agregação.",
}


cell_summary_labels = {
    "cells_with_coordinate_review_n": "células com ao menos uma coordenada em revisão",
    "cells_with_hydrostrat_review_or_unknown_n": "células com revisão ou UNKNOWN hidroestratigráfico",
    "cells_with_hydraulic_minimum_test_metadata_n": "células com ao menos um ensaio com metadados mínimos",
    "cells_with_transmissivity_reported_n": "células com ao menos uma transmissividade informada",
    "cells_with_partial_hydrochemistry_n": "células com evidência hidroquímica parcial",
    "cells_with_dated_evidence_n": "células com ao menos uma evidência datada",
    "cells_with_duplicate_review_n": "células com ao menos um candidato a duplicidade",
    "cells_with_documentary_flags_n": "células com ao menos um alerta documental",
}


def module_for(field: str) -> str:
    prefix = field.split("_", 1)[0]
    mapping = {
        "spatial": "Dimensão espacial", "hydrostrat": "Dimensão hidroestratigráfica",
        "vertical": "Dimensão vertical", "hydraulic": "Dimensão hidráulica",
        "hydrochemical": "Dimensão hidroquímica", "temporal": "Dimensão temporal",
        "independence": "Dimensão de independência", "documentary": "Qualidade documental",
        "uncertainty": "Incerteza", "dimension": "Matriz não agregada",
    }
    return f"{MODULE} | {mapping.get(prefix, 'Registro e auditoria')}"


def make_row(field: str):
    if field in state_fields:
        definition, unit = state_fields[field], "categoria"
        formula = "Regra categórica determinística definida na metodologia V2.2."
        read = "Ler junto aos indicadores e aos códigos de incerteza da mesma dimensão."
        not_mean = "Não é nota, peso, potencial aquífero ou prioridade."
        unknown = "UNKNOWN é mantido como resultado quando a evidência não demonstra o estado."
    elif field in cell_summary_labels:
        definition, unit = f"Número de {cell_summary_labels[field]} na escala.", "n"
        formula = "Contagem direta das células que satisfazem a condição nomeada."
        read = "Resume a distribuição espacial do estado na escala indicada."
        not_mean = "Não seleciona escala e não classifica prioridade."
        unknown = "Zero é contagem observada na tabela. Ausência de dados continua descrita nos estados das células."
    elif field.endswith("_n") and field[:-2] in labels:
        definition, unit = f"Número de {labels[field[:-2]]} na unidade de análise.", "n"
        formula = f"Contagem direta do indicador {field[:-2]} entre os poços atribuídos."
        read = "Quantifica presença documental segundo a regra indicada."
        not_mean = "Não mede independência, potencial ou prioridade."
        unknown = "Em célula sem poço a contagem é zero e percentuais condicionados permanecem UNKNOWN."
    elif field.endswith("_pct") and field[:-4] in labels:
        definition, unit = f"Percentual de {labels[field[:-4]]} entre os poços da célula.", "%"
        formula = f"100 × {field[:-4]}_n ÷ n_wells quando n_wells > 0."
        read = "Comparar somente dentro da mesma regra e com denominador conhecido."
        not_mean = "Não é probabilidade, qualidade total, potencial ou prioridade."
        unknown = "UNKNOWN em célula sem poço. Nunca convertido para zero."
    elif field in special:
        definition, unit = special[field]
        formula = "Preservado ou derivado diretamente pelas regras documentadas da V2.2."
        read = "Ler no contexto da dimensão e da unidade de análise correspondente."
        not_mean = "Não autoriza agregação das nove dimensões nem inferência de potencial ou prioridade."
        unknown = "UNKNOWN ou vazio quando a fonte ou o denominador necessário não está disponível."
    else:
        raise RuntimeError(f"Campo novo sem documentação específica {field}")
    return {
        "field": field,
        "modules": module_for(field),
        "source_files": SOURCES,
        "definition": definition,
        "formula_or_rule": formula,
        "unit": unit,
        "how_to_read": read,
        "does_not_mean": not_mean,
        "unknown_rule": unknown,
    }


master = pd.read_csv(MASTER, encoding="utf-8-sig", dtype=str).fillna("")
old_fields = set(master["field"])
module_existing_fields = set(master.loc[master["modules"].str.contains(MODULE, regex=False), "field"])
target_fields = [field for field in columns if field not in old_fields or field in module_existing_fields]
new_rows = [make_row(field) for field in target_fields]
new_dictionary = pd.DataFrame(new_rows)
new_dictionary.to_csv(DER / "effective_knowledge_field_dictionary.csv", index=False, encoding="utf-8-sig")
new_dictionary.to_csv(ROOT / "methodology/CONHECIMENTO_HIDROGEOLOGICO_EFETIVO_CAMPOS_V1.csv", index=False, encoding="utf-8-sig")

master = master[~master["field"].isin(set(new_dictionary["field"]))]
master = pd.concat([master, new_dictionary], ignore_index=True).sort_values("field", key=lambda s: s.str.casefold())
master.to_csv(MASTER, index=False, encoding="utf-8-sig", quoting=csv.QUOTE_MINIMAL)
master.to_csv(ROOT / "docs/data/dicionario_metricas_resultados_v1.csv", index=False, encoding="utf-8-sig", quoting=csv.QUOTE_MINIMAL)


def td(value):
    return f"<td>{html.escape(str(value))}</td>"


body_rows = []
for row in master.to_dict("records"):
    body_rows.append(
        "<tr>" + td(row["field"]) + td(row["modules"]) + td(row["definition"]) +
        td(row["formula_or_rule"]) + td(row["unit"]) + td(row["how_to_read"]) +
        td(row["does_not_mean"]) + td(row["unknown_rule"]) + "</tr>"
    )
total = len(master)
page = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Dicionário de parâmetros PIH MS V2.2</title><style>:root{{--navy:#0b456e;--line:#d7e4ec;--ink:#183044;--muted:#647b8a}}*{{box-sizing:border-box}}body{{margin:0;background:#eef5f9;color:var(--ink);font:16px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}}.wrap{{max-width:1280px;margin:auto;padding:26px}}.hero{{background:linear-gradient(125deg,#083b61,#0b6b9e);color:#fff;padding:28px;border-radius:18px}}.card{{background:#fff;border:1px solid var(--line);border-radius:16px;padding:22px;margin:18px 0}}.rule{{padding:13px 15px;border-left:5px solid #147cad;background:#edf6fb;border-radius:9px}}.table-wrap{{overflow:auto;border:1px solid var(--line);border-radius:12px;max-height:72vh}}table{{width:100%;border-collapse:collapse;font-size:.86rem}}th{{position:sticky;top:0;background:#0b456e;color:#fff;text-align:left;padding:10px;z-index:2}}td{{vertical-align:top;padding:9px 10px;border-bottom:1px solid #e7eef2;min-width:130px}}td:first-child{{font-family:ui-monospace,Consolas,monospace;color:#0b456e;font-weight:700}}.search{{width:100%;max-width:680px;padding:11px;border:1px solid #b9cfdb;border-radius:10px;font:inherit}}.back,a{{color:#0b6699}}.back{{font-weight:800;text-decoration:none}}.note{{color:var(--muted)}}</style></head><body><main class="wrap"><a class="back" href="index.html">← Voltar ao PIH MS</a><section class="hero"><b>PIH MS V2.2</b><h1>Dicionário exaustivo de parâmetros</h1><p>{total} campos documentados individualmente, incluindo a matriz de conhecimento hidrogeológico efetivo.</p></section><section class="card"><h2>Como usar</h2><div class="rule"><b>REGISTRO ≠ POÇO ≠ LOCAL INDEPENDENTE.</b> As nove dimensões V2.2 permanecem separadas. UNKNOWN não é zero.</div><p><input class="search" id="q" placeholder="Pesquisar parâmetro…"></p><p class="note" id="count">{total} campos</p><div class="table-wrap"><table id="tbl"><thead><tr><th>Campo</th><th>Módulo</th><th>Definição</th><th>Fórmula ou regra</th><th>Unidade</th><th>Como ler</th><th>Não significa</th><th>UNKNOWN</th></tr></thead><tbody>{''.join(body_rows)}</tbody></table></div><p><a href="data/dicionario_metricas_resultados_v1.csv" download>Baixar CSV completo</a></p></section><script>const q=document.getElementById('q'),rows=[...document.querySelectorAll('#tbl tbody tr')],count=document.getElementById('count');function f(){{const s=q.value.trim().toLowerCase();let n=0;rows.forEach(r=>{{const ok=!s||r.innerText.toLowerCase().includes(s);r.style.display=ok?'':'none';if(ok)n++}});count.textContent=n+' campos visíveis de {total}';}}q.addEventListener('input',f);</script></main></body></html>'''
(ROOT / "docs/dicionario-parametros.html").write_text(page, encoding="utf-8")


# Bloco exaustivo usado também pela metodologia.
lines = ["| Campo | Definição | Regra | Unidade | UNKNOWN |", "|---|---|---|---|---|"]
for row in new_dictionary.to_dict("records"):
    esc = lambda value: str(value).replace("|", "\\|").replace("\n", " ")
    lines.append(f"| `{esc(row['field'])}` | {esc(row['definition'])} | {esc(row['formula_or_rule'])} | {esc(row['unit'])} | {esc(row['unknown_rule'])} |")
(DER / "effective_knowledge_methodology_fields.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

print(f"OK {len(new_dictionary)} campos novos, {len(master)} campos no dicionário mestre")
