from pathlib import Path
import csv, json, shutil, math, hashlib, datetime, re, statistics

SRC_PROJECT = Path('/mnt/data/pih-ms-v1.0-selecao-explicita-pocos')
AUDIT = Path('/mnt/data/PIH_MS_SIAGAS_AUDIT_V1/results')
OUT = Path('/mnt/data/pih-ms-v1.1-camadas-evidencia')
CUTOFF = datetime.date(2026,8,29)

if OUT.exists(): shutil.rmtree(OUT)
shutil.copytree(SRC_PROJECT, OUT)

root_data = OUT/'data'
derived = root_data/'derived'/'evidence'
source_audit = root_data/'source_audit'
method_root = OUT/'methodology'
scripts = OUT/'scripts'
prov = OUT/'provenance'
docs_evidence = OUT/'docs'/'data'/'evidence'
for p in [derived, source_audit, method_root, scripts, prov, docs_evidence]: p.mkdir(parents=True, exist_ok=True)

# Copy only audit sources needed to reproduce this phase
needed_sources = [
    'wells_master.csv','well_evidence_presence.csv','pumping_tests.csv','hydraulic_parameters.csv',
    'chem_results.csv','chem_samples.csv','coordinate_quality.csv','aquifer_assignment_audit.csv',
    'data_quality_flags.csv','duplicate_candidates.csv','variable_completeness_matrix.csv'
]
for name in needed_sources:
    shutil.copy2(AUDIT/name, source_audit/name)

def read_csv(p):
    with open(p, 'r', encoding='utf-8-sig', newline='') as f: return list(csv.DictReader(f))

def write_csv(p, rows, fields=None):
    p.parent.mkdir(parents=True, exist_ok=True)
    if fields is None:
        fields = []
        seen=set()
        for row in rows:
            for k in row.keys():
                if k not in seen:
                    seen.add(k); fields.append(k)
    with open(p,'w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

def num(v):
    if v is None or str(v).strip()=='' or str(v).strip().upper()=='UNKNOWN': return None
    try: return float(str(v).replace(',','.'))
    except: return None

def parse_date(v):
    if not v: return None
    s=str(v).strip()
    for fmt in ('%Y-%m-%d','%d/%m/%Y','%Y/%m/%d'):
        try: return datetime.datetime.strptime(s,fmt).date()
        except: pass
    return None

def boolv(v): return str(v).strip().lower() in {'true','1','sim','yes'}

def feature(row, props):
    lat=num(row.get('latitude')); lon=num(row.get('longitude'))
    return {'type':'Feature','geometry':{'type':'Point','coordinates':[lon,lat]},'properties':props}

def dump_geojson(path, feats, name, meta=None):
    obj={'type':'FeatureCollection','name':name,'features':feats}
    if meta: obj['pih_metadata']=meta
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,separators=(',',':')),encoding='utf-8')

wells = read_csv(AUDIT/'wells_master.csv')
flags = read_csv(AUDIT/'data_quality_flags.csv')
aq = {r['well_id']:r for r in read_csv(AUDIT/'aquifer_assignment_audit.csv')}
coord = {r['well_id']:r for r in read_csv(AUDIT/'coordinate_quality.csv')}
flag_by_well={}
for f in flags: flag_by_well.setdefault(f['well_id'],[]).append(f)

# A fixed neutral blue vocabulary. Colors distinguish themes and do not encode priority.
colors = {
 'E01':'#0B4F6C','E02':'#166E9B','E03':'#1D7FAF','E04':'#278FC0','E05':'#359FCB','E06':'#467FC0',
 'E07':'#3659A7','E08':'#263E86','E09':'#0C3C78','E10':'#4A97C2','E11':'#76A9CF','E12':'#5D7FA3'
}

registry=[]
layer_rows={}
layer_feats={}

def add_layer(code, slug, title, short, question, source, inclusion, exclusion, limitations, count_rule, rows, feats, value_field='', value_unit='', readiness='READY_FOR_GRID_COUNTS'):
    layer_rows[code]=rows; layer_feats[code]=feats
    registry.append({
      'code':code,'slug':slug,'name':title,'short_name':short,'scientific_question':question,'source_dataset':source,
      'geometry':'POINT','inclusion_rule':inclusion,'exclusion_rule':exclusion,'feature_count':len(feats),
      'value_field':value_field,'value_unit':value_unit,'color':colors[code],'limitations':limitations,
      'grid_readiness':readiness,'aggregation_rule_provisional':count_rule,'status':'DERIVED_EVIDENCE_LAYER_V1',
      'cutoff_date':CUTOFF.isoformat(),'piH_priority_calculated':'NO'
    })

# E01 all canonical wells with coordinates
rows=[]; feats=[]
for r in wells:
    if num(r['latitude']) is None or num(r['longitude']) is None: continue
    p={'well_id':r['well_id'],'municipality':r['municipality_declared'],'aquifer':r['siagas_aquifer'],'coordinate_quality':r['coordinate_quality_status'],'source':'SIAGAS_MS_20260814','evidence_code':'E01'}
    rr=p.copy(); rr.update({'latitude':r['latitude'],'longitude':r['longitude']}); rows.append(rr); feats.append(feature(r,p))
add_layer('E01','pocos_canonicos','Poços canônicos provisórios','Poços canônicos','Quantos identificadores SIAGAS espacialmente utilizáveis existem','SIAGAS_MS_20260814 + AUDITORIA_V1','ID SIAGAS canônico provisório com coordenadas numéricas','Nenhum ID é removido por possível duplicação física nesta fase','ID digital não demonstra independência física entre poços', 'COUNT_DISTINCT(well_id)', rows,feats)

# E02 positive current depth
rows=[]; feats=[]
for r in wells:
    v=num(r['depth_current_m'])
    if v is None or v<=0: continue
    p={'well_id':r['well_id'],'municipality':r['municipality_declared'],'aquifer':r['siagas_aquifer'],'depth_m':v,'source':'SIAGAS_MS_20260814','evidence_code':'E02'}
    rr=p.copy(); rr.update({'latitude':r['latitude'],'longitude':r['longitude']}); rows.append(rr); feats.append(feature(r,p))
add_layer('E02','profundidade_positiva','Profundidade positiva informada','Profundidade','Onde existe profundidade total positiva no snapshot atual','SIAGAS_MS_20260814','num_profundidade numérico e maior que zero','Nulo, vazio e zero não entram nesta camada','Profundidade total não equivale a intervalo captado nem cobertura vertical', 'COUNT_DISTINCT(well_id); MEDIAN(depth_m); P10/P90 somente em análise de malha', rows,feats,'depth_m','m')

# E03 aquifer informed
rows=[]; feats=[]
for r in wells:
    a=r['siagas_aquifer'].strip()
    if not a: continue
    p={'well_id':r['well_id'],'municipality':r['municipality_declared'],'aquifer_informed':a,'comparison_status':r['aquifer_comparison_status'],'source':'SIAGAS_MS_20260814','evidence_code':'E03'}
    rr=p.copy(); rr.update({'latitude':r['latitude'],'longitude':r['longitude']}); rows.append(rr); feats.append(feature(r,p))
add_layer('E03','aquifero_informado','Aquífero informado no cadastro','Aquífero informado','Onde o cadastro SIAGAS informa um nome de aquífero','SIAGAS_MS_20260814','str_aquifero não vazio','Nomes vazios não entram','O nome cadastral pode usar taxonomias diferentes e não é reclassificado automaticamente', 'COUNT_DISTINCT(well_id); DIVERSITY(aquifer_informed) sem interpretar diversidade como qualidade', rows,feats,'aquifer_informed','text')

# E04 static level available, zero preserved and flagged
rows=[]; feats=[]
for r in wells:
    v=num(r['static_level_current_m'])
    if v is None: continue
    zero=(v==0)
    p={'well_id':r['well_id'],'municipality':r['municipality_declared'],'aquifer':r['siagas_aquifer'],'static_level_m':v,'zero_requires_review':zero,'measurement_date':'UNKNOWN','source':'SIAGAS_MS_20260814','evidence_code':'E04'}
    rr=p.copy(); rr.update({'latitude':r['latitude'],'longitude':r['longitude']}); rows.append(rr); feats.append(feature(r,p))
add_layer('E04','nivel_estatico_disponivel','Nível estático disponível','Nível estático','Onde existe valor numérico de nível estático no snapshot atual','SIAGAS_MS_20260814','NE numérico presente','Ausência do campo não é convertida em zero','A camada indica disponibilidade. A data de medição não está disponível na extração plana e 33 zeros permanecem para revisão', 'COUNT_DISTINCT(well_id); zero_count separado; não interpolar nesta fase', rows,feats,'static_level_m','m')

# E05 dynamic
rows=[]; feats=[]
for r in wells:
    v=num(r['dynamic_level_current_m'])
    if v is None: continue
    p={'well_id':r['well_id'],'municipality':r['municipality_declared'],'aquifer':r['siagas_aquifer'],'dynamic_level_m':v,'zero_requires_review':v==0,'measurement_date':'UNKNOWN','source':'SIAGAS_MS_20260814','evidence_code':'E05'}
    rr=p.copy(); rr.update({'latitude':r['latitude'],'longitude':r['longitude']}); rows.append(rr); feats.append(feature(r,p))
add_layer('E05','nivel_dinamico_disponivel','Nível dinâmico disponível','Nível dinâmico','Onde existe valor numérico de nível dinâmico','SIAGAS_MS_20260814','ND numérico presente','Ausência do campo não é convertida em zero','A camada indica disponibilidade. Sem contexto completo do ensaio o valor não é interpretado isoladamente', 'COUNT_DISTINCT(well_id); zero_count separado; não interpolar nesta fase', rows,feats,'dynamic_level_m','m')

# E06 nonnegative specific capacity, units pending
rows=[]; feats=[]
for r in wells:
    v=num(r['specific_capacity_current'])
    if v is None or v<0: continue
    p={'well_id':r['well_id'],'municipality':r['municipality_declared'],'aquifer':r['siagas_aquifer'],'specific_capacity':v,'unit':'SOURCE_UNIT_NOT_VERIFIED','source':'SIAGAS_MS_20260814','evidence_code':'E06'}
    rr=p.copy(); rr.update({'latitude':r['latitude'],'longitude':r['longitude']}); rows.append(rr); feats.append(feature(r,p))
add_layer('E06','vazao_especifica_nao_negativa','Vazão específica não negativa','Vazão específica','Onde existe valor de vazão específica não negativo','SIAGAS_MS_20260814 + AUDITORIA_V1','Valor numérico maior ou igual a zero','Três valores negativos foram excluídos da camada derivada e permanecem na fonte com flag de revisão','Unidade ainda não congelada documentalmente. Não comparar magnitudes até resolver a unidade', 'COUNT_DISTINCT(well_id); somente presença na primeira malha', rows,feats,'specific_capacity','SOURCE_UNIT_NOT_VERIFIED')

# E07 pumping test exists
rows=[]; feats=[]
for r in wells:
    tt=r['test_type_sgb2024'].strip()
    if not tt: continue
    p={'well_id':r['well_id'],'municipality':r['municipality_declared'],'aquifer':r['siagas_aquifer'],'test_type':tt,'test_date':r['test_date_sgb2024'],'source':'SGB_HIDRO_MS_2024_POCOS','evidence_code':'E07'}
    rr=p.copy(); rr.update({'latitude':r['latitude'],'longitude':r['longitude']}); rows.append(rr); feats.append(feature(r,p))
add_layer('E07','ensaio_bombeamento_cadastrado','Ensaio de bombeamento cadastrado','Ensaio cadastrado','Onde o snapshot enriquecido SGB 2024 informa tipo de ensaio','SGB_HIDRO_MS_2024_POCOS','test_type_sgb2024 não vazio','Ausência de tipo não é inferida a partir de NE ou ND','Existência cadastral do ensaio não demonstra qualidade metodológica nem adequação para estimar parâmetros', 'COUNT_DISTINCT(well_id); COUNT_BY(test_type)', rows,feats,'test_type','text')

# E08 minimum metadata test
rows=[]; feats=[]
for r in wells:
    keys=['test_type_sgb2024','test_date_sgb2024','static_level_sgb2024_m','dynamic_level_sgb2024_m','stabilized_yield_sgb2024']
    if not all(r[k].strip() for k in keys): continue
    p={'well_id':r['well_id'],'municipality':r['municipality_declared'],'aquifer':r['siagas_aquifer'],'test_type':r['test_type_sgb2024'],'test_date':r['test_date_sgb2024'],'static_level_m':num(r['static_level_sgb2024_m']),'dynamic_level_m':num(r['dynamic_level_sgb2024_m']),'stabilized_yield':num(r['stabilized_yield_sgb2024']),'interpretation_method':r['interpretation_method_sgb2024'] or 'UNKNOWN','source':'SGB_HIDRO_MS_2024_POCOS','evidence_code':'E08'}
    rr=p.copy(); rr.update({'latitude':r['latitude'],'longitude':r['longitude']}); rows.append(rr); feats.append(feature(r,p))
add_layer('E08','ensaio_metadados_minimos','Ensaio com metadados mínimos de cadastro','Ensaio documentado','Onde o registro contém um conjunto mínimo explícito de metadados de ensaio','SGB_HIDRO_MS_2024_POCOS','Tipo + data + NE + ND + vazão estabilizada presentes','Não exige método interpretativo porque ele está disponível em apenas dois registros','Esta é uma classe documental, não uma certificação de validade hidrogeológica do ensaio', 'COUNT_DISTINCT(well_id); no futuro separar presença de método e duração', rows,feats,'test_type','text')

# E09 transmissivity reported
rows=[]; feats=[]
for r in wells:
    v=num(r['transmissivity_sgb2024'])
    if v is None: continue
    p={'well_id':r['well_id'],'municipality':r['municipality_declared'],'aquifer':r['siagas_aquifer'],'transmissivity':v,'zero_requires_review':v==0,'unit':'SOURCE_UNIT_NOT_VERIFIED','test_date':r['test_date_sgb2024'] or 'UNKNOWN','interpretation_method':r['interpretation_method_sgb2024'] or 'UNKNOWN','source':'SGB_HIDRO_MS_2024_POCOS','evidence_code':'E09'}
    rr=p.copy(); rr.update({'latitude':r['latitude'],'longitude':r['longitude']}); rows.append(rr); feats.append(feature(r,p))
add_layer('E09','transmissividade_informada','Transmissividade informada','Transmissividade','Onde existe número de transmissividade no snapshot histórico enriquecido','SGB_HIDRO_MS_2024_POCOS','transmissivity_sgb2024 numérica','Nulo não entra. Zero permanece com flag de revisão','Unidade e método não estão documentados para a maioria. A camada mapeia disponibilidade, não qualidade do parâmetro', 'COUNT_DISTINCT(well_id); zero_count separado; magnitude não agregada até congelar unidade', rows,feats,'transmissivity','SOURCE_UNIT_NOT_VERIFIED')

# E10 partial hydrochemical / physicochemical evidence
rows=[]; feats=[]
for r in wells:
    available=[]
    if r['ph_current'].strip(): available.append('pH')
    if r['electrical_conductivity_current'].strip(): available.append('CONDUTIVIDADE_ELETRICA')
    if r['temperature_current'].strip(): available.append('TEMPERATURA')
    if r['turbidity_current'].strip(): available.append('TURBIDEZ')
    if r['chemical_parameter_current'].strip(): available.append(r['chemical_parameter_current'])
    if not available: continue
    p={'well_id':r['well_id'],'municipality':r['municipality_declared'],'aquifer':r['siagas_aquifer'],'available_fields':' | '.join(available),'available_count':len(available),'pH':num(r['ph_current']),'electrical_conductivity':num(r['electrical_conductivity_current']),'temperature':num(r['temperature_current']),'chemical_parameter':r['chemical_parameter_current'],'chemical_concentration':num(r['chemical_concentration_current']),'source':'SIAGAS_MS_20260814','evidence_code':'E10'}
    rr=p.copy(); rr.update({'latitude':r['latitude'],'longitude':r['longitude']}); rows.append(rr); feats.append(feature(r,p))
add_layer('E10','evidencia_hidroquimica_parcial','Evidência hidroquímica e físico-química parcial','Hidroquímica parcial','Onde existe pelo menos um campo físico-químico ou químico na extração atual','SIAGAS_MS_20260814','Pelo menos um entre pH, condutividade elétrica, temperatura, turbidez ou parâmetro químico exposto','Ausência de parâmetro não é zero','Não representa análise hidroquímica completa. O parâmetro químico massivo identificado é sólidos dissolvidos totais', 'COUNT_DISTINCT(well_id); COUNT_BY(available_fields); não combinar analitos diferentes', rows,feats,'available_count','count')

# E11 latest dated hydro evidence from test or chem collection/analysis
rows=[]; feats=[]
for r in wells:
    cand=[]
    for fld,typ in [('test_date_sgb2024','PUMPING_TEST'),('analysis_date_sgb2024','CHEM_ANALYSIS'),('collection_date_sgb2024','CHEM_COLLECTION')]:
        d=parse_date(r[fld])
        if d: cand.append((d,typ))
    if not cand: continue
    d,typ=max(cand,key=lambda x:x[0])
    age=(CUTOFF-d).days/365.25
    p={'well_id':r['well_id'],'municipality':r['municipality_declared'],'aquifer':r['siagas_aquifer'],'latest_evidence_date':d.isoformat(),'evidence_type':typ,'age_years':round(age,3),'source':'SGB_HIDRO_MS_2024_POCOS','evidence_code':'E11'}
    rr=p.copy(); rr.update({'latitude':r['latitude'],'longitude':r['longitude']}); rows.append(rr); feats.append(feature(r,p))
add_layer('E11','ultima_evidencia_datada','Última evidência hidrogeológica datada','Evidência datada','Onde existe data explícita de ensaio hidráulico ou amostragem/análise química e qual é a mais recente','SGB_HIDRO_MS_2024_POCOS','Pelo menos uma data válida entre ensaio, coleta ou análise','Datas de perfuração, cadastro e instalação não são usadas como substitutas de data de observação hidrogeológica','A camada não demonstra série temporal. Um único evento datado continua sendo uma única observação temporal', 'COUNT_DISTINCT(well_id); MEDIAN(age_years); P25/P75; UNKNOWN preservado', rows,feats,'age_years','years')

# E12 hydrostratigraphic review, only manual_review_required
rows=[]; feats=[]
for r in wells:
    a=aq.get(r['well_id'])
    if not a or not boolv(a['manual_review_required']): continue
    p={'well_id':r['well_id'],'municipality':r['municipality_declared'],'siagas_aquifer':a['siagas_aquifer'],'sgb2024_unit_aflorante':a['sgb2024_unit_aflorante'],'sgb2024_unit_subjacente':a['sgb2024_unit_subjacente'],'comparison_status':a['comparison_status'],'comparison_reason':a['comparison_reason'],'source':'AUDITORIA_HIDROESTRATIGRAFICA_V1','evidence_code':'E12'}
    rr=p.copy(); rr.update({'latitude':r['latitude'],'longitude':r['longitude']}); rows.append(rr); feats.append(feature(r,p))
add_layer('E12','revisao_hidroestratigrafica','Revisão hidroestratigráfica necessária','Revisão aquífera','Onde a comparação entre cadastro e cartografia exige revisão manual','SIAGAS_MS_20260814 + SGB_HIDRO_MS_2024 + AUDITORIA_V1','manual_review_required = TRUE na auditoria hidroestratigráfica','Casos consistentes e possíveis consistências sem revisão não entram','Divergência cartográfica não conclusiva não é tratada como contradição. Um poço pode captar unidade profunda', 'COUNT_DISTINCT(well_id); COUNT_BY(comparison_status); nunca converter revisão em ausência de água', rows,feats,'comparison_status','text')

# Write per-layer files
for reg in registry:
    code=reg['code']; slug=reg['slug']
    write_csv(derived/f'{code}_{slug}.csv', layer_rows[code])
    meta={k:reg[k] for k in ['code','name','scientific_question','source_dataset','inclusion_rule','limitations','feature_count','grid_readiness','aggregation_rule_provisional','cutoff_date']}
    dump_geojson(derived/f'{code}_{slug}.geojson', layer_feats[code], f'{code}_{slug}',meta)
    shutil.copy2(derived/f'{code}_{slug}.geojson', docs_evidence/f'{code}_{slug}.geojson')

write_csv(derived/'camadas_evidencia_registry.csv', registry)
(OUT/'docs'/'data'/'evidence'/'camadas_evidencia_registry.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2),encoding='utf-8')

# Stats table
stats=[]
for reg in registry:
    rows=layer_rows[reg['code']]
    stat={'code':reg['code'],'name':reg['name'],'feature_count':len(rows),'pct_of_3877':round(100*len(rows)/len(wells),2),'source_dataset':reg['source_dataset'],'grid_readiness':reg['grid_readiness']}
    if reg['code']=='E11':
        ages=[float(x['age_years']) for x in rows]
        stat.update({'median_age_years':round(statistics.median(ages),2),'min_age_years':round(min(ages),2),'max_age_years':round(max(ages),2)})
    stats.append(stat)
write_csv(derived/'camadas_evidencia_statistics.csv',stats)

# Full methodology markdown and HTML
intro='''# PIH MS\n\n## Matriz de Evidência Hidrogeológica V1\n\nData de corte 29 de agosto de 2026.\n\nEsta fase cria camadas independentes de disponibilidade e qualidade documental. Não calcula prioridade, peso, índice, interpolação ou favorabilidade aquífera.\n\nPrincípios de leitura\n\n- Ausência de dado não significa ausência de água subterrânea\n- Predição não é observação\n- Interpolação não é evidência observada\n- Poço cadastrado não é poço com informação hidrogeológica suficiente\n- Uma camada de disponibilidade não certifica a qualidade científica do parâmetro\n- Cada domínio será agregado às malhas separadamente\n\n'''
sections=[]
for reg in registry:
    sections.append(f'''## {reg['code']} · {reg['name']}\n\nPergunta científica\n\n{reg['scientific_question']}\n\nFonte\n\n{reg['source_dataset']}\n\nRegra de inclusão\n\n{reg['inclusion_rule']}\n\nRegra de exclusão\n\n{reg['exclusion_rule']}\n\nNúmero de feições\n\n{reg['feature_count']}\n\nGeometria\n\nPontos. Cada feição mantém o identificador canônico provisório SIAGAS.\n\nValor principal\n\n{reg['value_field'] or 'presença da evidência'}\n\nUnidade\n\n{reg['value_unit'] or 'não aplicável'}\n\nLimitações\n\n{reg['limitations']}\n\nPreparação para malha\n\n{reg['aggregation_rule_provisional']}\n\nEstado\n\nCamada derivada de evidência V1. Nenhuma prioridade foi calculada.\n''')
(method_root/'MATRIZ_EVIDENCIA_HIDROGEOLOGICA_V1.md').write_text(intro+'\n'.join(sections),encoding='utf-8')

# HTML, no external dependencies
html=['''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PIH MS · Metodologia das camadas de evidência</title><style>body{font-family:system-ui,-apple-system,Segoe UI,sans-serif;margin:0;background:#eef5fa;color:#183144}.top{background:#0b456e;color:white;padding:28px 7vw}.top h1{margin:3px 0;font-size:30px}.wrap{max-width:1120px;margin:auto;padding:28px}.principles,.card{background:white;border:1px solid #cbdce8;border-radius:16px;padding:22px;margin-bottom:18px;box-shadow:0 5px 18px #0b456e12}.card{scroll-margin-top:18px}.code{display:inline-block;background:#dcecf6;color:#0b456e;padding:5px 9px;border-radius:999px;font-weight:800}.grid{display:grid;grid-template-columns:180px 1fr;gap:8px 18px}.grid b{color:#0b456e}.count{font-size:25px;font-weight:800;color:#0b456e}.back{display:inline-block;margin-top:14px;color:white}.nav{display:flex;flex-wrap:wrap;gap:7px;margin:18px 0}.nav a{background:white;border:1px solid #b8d2e2;border-radius:999px;padding:7px 10px;text-decoration:none;color:#0b456e;font-size:13px}@media(max-width:700px){.grid{grid-template-columns:1fr}.wrap{padding:16px}}</style></head><body><header class="top"><small>PIH MS</small><h1>Metodologia das camadas de evidência</h1><p>Matriz de Evidência Hidrogeológica V1 · corte em 29 de agosto de 2026</p><a class="back" href="index.html">Voltar ao mapa</a></header><main class="wrap"><section class="principles"><h2>Como ler estas camadas</h2><p>As camadas abaixo representam disponibilidade, estrutura documental ou necessidade de revisão. Nenhuma delas representa prioridade de investigação ou potencial aquífero.</p><p>Ausência de dado não significa ausência de água subterrânea. Dados derivados permanecem separados de observações. UNKNOWN não é preenchido por interpolação.</p></section><nav class="nav">''']
for reg in registry: html.append(f'<a href="#{reg["code"]}">{reg["code"]} {reg["short_name"]}</a>')
html.append('</nav>')
for reg in registry:
    html.append(f'''<section class="card" id="{reg['code']}"><span class="code">{reg['code']}</span><h2>{reg['name']}</h2><div class="count">{reg['feature_count']} feições</div><div class="grid"><b>Pergunta científica</b><span>{reg['scientific_question']}</span><b>Fonte</b><span>{reg['source_dataset']}</span><b>Inclusão</b><span>{reg['inclusion_rule']}</span><b>Exclusão</b><span>{reg['exclusion_rule']}</span><b>Limitações</b><span>{reg['limitations']}</span><b>Preparação para malha</b><span>{reg['aggregation_rule_provisional']}</span><b>Estado</b><span>Camada derivada de evidência V1. Não calcula prioridade.</span></div></section>''')
html.append('</main></body></html>')
(OUT/'docs'/'metodologia-evidencias.html').write_text(''.join(html),encoding='utf-8')

# Study report
study=['# PIH MS\n','## Estudo das camadas antes das malhas\n','Data de corte 29 de agosto de 2026.\n','Esta etapa implementa doze camadas observacionais ou documentais independentes. Nenhuma é agregada ainda a uma malha e nenhuma recebe peso.\n','| Código | Camada | Feições | Percentual dos 3.877 | Pronta para contagem em malha |','| --- | --- | ---: | ---: | --- |']
for s in stats: study.append(f"| {s['code']} | {s['name']} | {s['feature_count']} | {s['pct_of_3877']} % | {s['grid_readiness']} |")
study += ['\n## Decisões científicas\n','Nível estático e nível dinâmico são representados como disponibilidade de valor. A extração plana atual não fornece a data de medição e por isso não são chamados de séries temporais.\n','Vazão específica negativa foi excluída da camada derivada de presença utilizável, mas os valores originais permanecem preservados e sinalizados na auditoria.\n','Ensaio com metadados mínimos exige tipo, data, nível estático, nível dinâmico e vazão estabilizada. Essa regra mede documentação cadastral e não certifica a interpretação do ensaio.\n','Transmissividade é mapeada como valor informado. Sua unidade e método permanecem não congelados para a maioria dos registros.\n','Hidroquímica parcial significa presença de pelo menos um campo físico-químico ou químico. Não significa painel hidroquímico completo.\n','Antiguidade usa apenas data de ensaio ou data de coleta ou análise química. Data de perfuração e data de cadastro não substituem uma data de observação.\n','A revisão hidroestratigráfica não é chamada de contradição. Divergência cartográfica pode ocorrer porque o poço capta uma unidade profunda.\n']
(OUT/'ESTUDO_CAMADAS_EVIDENCIA_V1.md').write_text('\n'.join(study),encoding='utf-8')

# Reproduction script copy itself
shutil.copy2(Path(__file__), scripts/'build_evidence_layers_v1.py')

# Update README and version
(OUT/'VERSION').write_text('1.1\n',encoding='utf-8')
readme=(OUT/'README.md').read_text(encoding='utf-8') if (OUT/'README.md').exists() else ''
readme += '''\n\n## V1.1 · Matriz de Evidência Hidrogeológica\n\nEsta versão acrescenta doze camadas independentes derivadas da Auditoria Mestra SIAGAS MS V1. As camadas representam disponibilidade de evidência e necessidade de revisão. Não há PIH, peso, prioridade ou interpolação.\n\nA metodologia completa está em `docs/metodologia-evidencias.html` e `methodology/MATRIZ_EVIDENCIA_HIDROGEOLOGICA_V1.md`.\n'''
(OUT/'README.md').write_text(readme,encoding='utf-8')

# Hash manifest for new derived outputs
manifest=[]
for p in sorted(list(derived.glob('*'))+[OUT/'ESTUDO_CAMADAS_EVIDENCIA_V1.md',method_root/'MATRIZ_EVIDENCIA_HIDROGEOLOGICA_V1.md']):
    if p.is_file():
        h=hashlib.sha256(p.read_bytes()).hexdigest(); manifest.append({'relative_path':str(p.relative_to(OUT)),'size_bytes':p.stat().st_size,'sha256':h})
write_csv(prov/'evidence_layers_manifest.csv',manifest)

print('Built evidence layers')
for s in stats: print(s['code'],s['feature_count'],s['name'])
print(OUT)
