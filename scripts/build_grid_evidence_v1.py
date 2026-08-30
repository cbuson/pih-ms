from pathlib import Path
from collections import Counter
import shutil, json, csv, math, re, zipfile, hashlib
import numpy as np
import pandas as pd
import geopandas as gpd

SRC = Path('/mnt/data/pih-ms-v1.2-evidencias-visiveis')
OUT = Path('/mnt/data/pih-ms-v1.3-malhas-evidencia')
if OUT.exists(): shutil.rmtree(OUT)
shutil.copytree(SRC, OUT)

BASE = OUT/'docs/data'
EVDIR = BASE/'evidence'
GRIDOUT = OUT/'data/derived/grid_evidence'
GRIDOUT.mkdir(parents=True, exist_ok=True)
WEBGRID = BASE/'grid_evidence'
WEBGRID.mkdir(parents=True, exist_ok=True)
METH = OUT/'methodology'
METH.mkdir(exist_ok=True)
PROV = OUT/'provenance'
PROV.mkdir(exist_ok=True)
SCRIPTS = OUT/'scripts'
SCRIPTS.mkdir(exist_ok=True)

scales = {250: BASE/'malha_250km2_candidata.geojson', 500: BASE/'malha_500km2_candidata.geojson', 1000: BASE/'malha_1000km2_candidata.geojson'}
ev_files = {i: next(EVDIR.glob(f'E{i:02d}_*.geojson')) for i in range(1,13)}
ev = {i: gpd.read_file(p) for i,p in ev_files.items()}
grids = {s: gpd.read_file(p) for s,p in scales.items()}
registry = pd.read_csv(OUT/'data/derived/evidence/camadas_evidencia_registry.csv')
reg = {r.code:r for _,r in registry.iterrows()}

# Deterministic assignment. We do not assign by nearest neighbor except when the point lies within 50 m
# of a clipped grid due to a documented boundary mismatch between source geometries.
def assign_points(points, grid, tolerance_m=50):
    pts=points[['geometry']].copy(); pts['point_idx']=points.index.astype(int)
    polys=grid[['pih_cell_id','geometry']].copy()
    joined=gpd.sjoin(pts,polys,how='left',predicate='intersects')
    valid=joined.dropna(subset=['pih_cell_id']).copy()
    multi=int((valid.groupby('point_idx').size()>1).sum()) if len(valid) else 0
    chosen=(valid.sort_values(['point_idx','pih_cell_id']).drop_duplicates('point_idx',keep='first')[['point_idx','pih_cell_id']])
    assigned=chosen.set_index('point_idx')['pih_cell_id'].to_dict()
    fallback=[]
    missing=[i for i in points.index if int(i) not in assigned]
    if missing:
        gp=grid[['pih_cell_id','geometry']].to_crs(5880)
        pp=points.loc[missing,['geometry']].to_crs(5880)
        for idx,row in pp.iterrows():
            dist=gp.geometry.distance(row.geometry)
            j=dist.idxmin(); dm=float(dist.loc[j])
            if dm <= tolerance_m:
                assigned[int(idx)] = gp.loc[j,'pih_cell_id']
                fallback.append((int(idx), gp.loc[j,'pih_cell_id'], dm))
    unassigned=[int(i) for i in points.index if int(i) not in assigned]
    return pd.Series(assigned,name='pih_cell_id'), multi, fallback, unassigned

def cell_state(code,nbase,n):
    if code=='E01': return 'WELLS_PRESENT' if n>0 else 'UNKNOWN_NO_WELLS_IN_DATASET'
    if nbase==0: return 'UNKNOWN_NO_WELLS_IN_DATASET'
    if code=='E12': return 'REVIEW_REQUIRED_PRESENT' if n>0 else 'NO_REVIEW_FLAG_IN_AUDITED_WELLS'
    return 'EVIDENCE_PRESENT' if n>0 else 'NO_EVIDENCE_IN_AUDITED_WELLS'

def pct(num,den):
    return round(num/den*100,4) if den else None

def compact_counts(series):
    c=Counter(str(x) for x in series.dropna() if str(x).strip())
    return ' | '.join(f'{k}:{v}' for k,v in sorted(c.items()))

assignment_audit=[]
scale_summary=[]
long_rows=[]
style_meta={}

for scale, grid in grids.items():
    out=grid.copy()
    assignments={}
    for i,points in ev.items():
        ser,multi,fallback,unassigned=assign_points(points,grid)
        assignments[i]=ser
        assignment_audit.append({
            'scale_km2':scale,'evidence_code':f'E{i:02d}','n_points':len(points),'n_assigned':len(ser),
            'multi_intersections':multi,'fallback_nearest_50m':len(fallback),'n_unassigned':len(unassigned),
            'fallback_details':' | '.join(f"{points.loc[idx,'well_id']}->{cell}@{dm:.2f}m" for idx,cell,dm in fallback),
            'rule':'INTERSECTS; deterministic cell-id tie-break. Nearest fallback only <=50 m for clipped-boundary mismatch.'
        })
        counts=ser.value_counts()
        out[f'n_E{i:02d}']=out['pih_cell_id'].map(counts).fillna(0).astype(int)
    out['state_E01']=[cell_state('E01',n,n) for n in out.n_E01]
    for i in range(2,13):
        out[f'pct_E{i:02d}_of_E01']=[pct(n,b) for n,b in zip(out[f'n_E{i:02d}'],out.n_E01)]
        out[f'state_E{i:02d}']=[cell_state(f'E{i:02d}',b,n) for b,n in zip(out.n_E01,out[f'n_E{i:02d}'])]
    # Evidence-specific descriptive statistics. These are not scores.
    tmp=ev[2].copy(); tmp['cell']=tmp.index.map(assignments[2]); grp=tmp.dropna(subset=['cell']).groupby('cell')['depth_m']
    out['E02_depth_median_m']=out.pih_cell_id.map(grp.median()); out['E02_depth_p10_m']=out.pih_cell_id.map(grp.quantile(.10)); out['E02_depth_p90_m']=out.pih_cell_id.map(grp.quantile(.90))
    tmp=ev[3].copy(); tmp['cell']=tmp.index.map(assignments[3]); grp=tmp.dropna(subset=['cell']).groupby('cell')['aquifer_informed']
    out['E03_aquifer_n_unique']=out.pih_cell_id.map(grp.nunique()).fillna(0).astype(int)
    for i in (4,5):
        tmp=ev[i].copy(); tmp['cell']=tmp.index.map(assignments[i]); grp=tmp.dropna(subset=['cell']).groupby('cell')['zero_requires_review'].sum()
        out[f'E{i:02d}_zero_review_count']=out.pih_cell_id.map(grp).fillna(0).astype(int)
    tmp=ev[7].copy(); tmp['cell']=tmp.index.map(assignments[7]); tc=tmp.dropna(subset=['cell']).groupby('cell')['test_type'].apply(compact_counts)
    out['E07_test_types']=out.pih_cell_id.map(tc).fillna('')
    tmp=ev[9].copy(); tmp['cell']=tmp.index.map(assignments[9]); zz=tmp.dropna(subset=['cell']).groupby('cell')['zero_requires_review'].sum()
    out['E09_zero_review_count']=out.pih_cell_id.map(zz).fillna(0).astype(int)
    tmp=ev[10].copy(); tmp['cell']=tmp.index.map(assignments[10]); grp=tmp.dropna(subset=['cell']).groupby('cell')
    out['E10_available_fields_median']=out.pih_cell_id.map(grp['available_count'].median())
    for prop,label in [('pH','pH'),('electrical_conductivity','EC'),('temperature','temperature'),('chemical_parameter','chemical_parameter')]:
        ser=grp[prop].apply(lambda s:int(s.notna().sum())); out[f'E10_n_{label}']=out.pih_cell_id.map(ser).fillna(0).astype(int)
    tmp=ev[11].copy(); tmp['cell']=tmp.index.map(assignments[11]); grp=tmp.dropna(subset=['cell']).groupby('cell')['age_years']
    out['E11_age_median_years']=out.pih_cell_id.map(grp.median()); out['E11_age_p25_years']=out.pih_cell_id.map(grp.quantile(.25)); out['E11_age_p75_years']=out.pih_cell_id.map(grp.quantile(.75))
    tmp=ev[12].copy(); tmp['cell']=tmp.index.map(assignments[12]); sc=tmp.dropna(subset=['cell']).groupby('cell')['comparison_status'].apply(compact_counts)
    out['E12_comparison_statuses']=out.pih_cell_id.map(sc).fillna('')
    out['analysis_status']='MALHA_EVIDENCE_MATRIX_V1_NO_PIH_SCORE'
    out['cutoff_date']='2026-08-29'
    # tidy long table
    for _,r in out.iterrows():
        for i in range(1,13):
            code=f'E{i:02d}'; n=int(r[f'n_{code}']); base_n=int(r.n_E01)
            long_rows.append({
                'scale_km2':scale,'pih_cell_id':r.pih_cell_id,'source_hex_id':r.source_hex_id,
                'area_efetiva_ms_km2':r.area_efetiva_ms_km2,'evidence_code':code,'evidence_name':reg[code]['name'],
                'n_evidence':n,'n_wells_E01':base_n,'pct_of_wells':100.0 if code=='E01' and base_n else (pct(n,base_n) if code!='E01' else None),
                'support_state':r[f'state_{code}'],'interpretation':'DATA_SUPPORT_ONLY_NO_PIH_PRIORITY'
            })
    # summary for scale
    sr={'scale_km2':scale,'n_cells':len(out),'cells_with_wells':int((out.n_E01>0).sum()),'cells_without_wells':int((out.n_E01==0).sum()),
        'pct_cells_with_wells':round((out.n_E01>0).mean()*100,2),'cells_with_one_well':int((out.n_E01==1).sum()),
        'median_wells_in_occupied_cells':float(out.loc[out.n_E01>0,'n_E01'].median()),'p90_wells_in_occupied_cells':float(out.loc[out.n_E01>0,'n_E01'].quantile(.90)),
        'max_wells_in_cell':int(out.n_E01.max())}
    for i in range(2,13):
        sr[f'cells_with_E{i:02d}']=int((out[f'n_E{i:02d}']>0).sum())
        sr[f'cells_without_E{i:02d}_despite_wells']=int(((out.n_E01>0)&(out[f'n_E{i:02d}']==0)).sum())
    scale_summary.append(sr)
    # style metadata: positive-count quantiles for each evidence
    style_meta[str(scale)]={}
    for i in range(1,13):
        vals=out.loc[out[f'n_E{i:02d}']>0,f'n_E{i:02d}'].astype(float)
        qs=[] if vals.empty else [float(vals.quantile(q)) for q in (.25,.50,.75,.90)]
        breaks=[]
        for q in qs:
            v=max(1,int(math.ceil(q)))
            if v not in breaks: breaks.append(v)
        style_meta[str(scale)][f'E{i:02d}']={'positive_cells':int((out[f'n_E{i:02d}']>0).sum()),'max_count':int(out[f'n_E{i:02d}'].max()),'count_breaks':breaks}
    # save CSV and GeoJSON
    csv_df=pd.DataFrame(out.drop(columns='geometry'))
    csv_path=GRIDOUT/f'malha_evidencia_{scale}km2.csv'; csv_df.to_csv(csv_path,index=False,encoding='utf-8-sig')
    geo_path=GRIDOUT/f'malha_evidencia_{scale}km2.geojson'; out.to_file(geo_path,driver='GeoJSON')
    shutil.copy2(geo_path, WEBGRID/geo_path.name)

pd.DataFrame(assignment_audit).to_csv(GRIDOUT/'grid_assignment_audit.csv',index=False,encoding='utf-8-sig')
pd.DataFrame(scale_summary).to_csv(GRIDOUT/'grid_scale_summary.csv',index=False,encoding='utf-8-sig')
pd.DataFrame(long_rows).to_csv(GRIDOUT/'grid_evidence_long.csv',index=False,encoding='utf-8-sig')
(WEBGRID/'grid_evidence_style_metadata.json').write_text(json.dumps(style_meta,ensure_ascii=False,indent=2),encoding='utf-8')
shutil.copy2(GRIDOUT/'grid_scale_summary.csv', WEBGRID/'grid_scale_summary.csv')

# Methodology markdown
md='''# PIH MS\n\n## Malhas de evidência hidrogeológica V1\n\nData de corte 29 de agosto de 2026.\n\nEsta etapa agrega diretamente as camadas E01 a E12 às geometrias candidatas de 250, 500 e 1000 km². Nenhuma escala é derivada de outra. Nenhum peso, índice PIH, favorabilidade aquífera ou prioridade foi calculado.\n\n## Regra espacial\n\nCada ponto é intersectado diretamente com a geometria da malha correspondente. Em caso de coincidência com mais de uma célula seria aplicado desempate determinístico pelo identificador da célula. Não ocorreu interseção múltipla nesta execução.\n\nNa malha de 250 km² um único poço SIAGAS, 3500073933, ficou 19,14 m fora da geometria recortada da malha apesar de pertencer à base estadual. Para não perder uma observação por uma discrepância subpixel entre geometrias de limite, foi aplicada uma única regra de contingência previamente registrada. O ponto foi associado à célula PIH-250-0007 por distância mínima, abaixo do limite de 50 m. Não houve qualquer outra atribuição por proximidade.\n\n## Estados de suporte\n\n`WELLS_PRESENT` indica presença de pelo menos um poço E01.\n\n`UNKNOWN_NO_WELLS_IN_DATASET` indica que a célula não contém poços no conjunto auditado. Não significa ausência de água subterrânea.\n\n`EVIDENCE_PRESENT` indica presença de pelo menos um poço da camada E02 a E11.\n\n`NO_EVIDENCE_IN_AUDITED_WELLS` indica que existem poços E01 na célula, mas nenhum deles possui a evidência considerada na camada. Não prova que a informação não exista em outras fontes.\n\nPara E12, `REVIEW_REQUIRED_PRESENT` indica pelo menos um poço sinalizado para revisão hidroestratigráfica. `NO_REVIEW_FLAG_IN_AUDITED_WELLS` significa apenas que nenhum dos poços auditados na célula recebeu esse flag.\n\n## Métricas\n\nPara cada célula são mantidos os números absolutos `n_E01` a `n_E12`. Para E02 a E12 calcula-se também a proporção em relação aos poços E01 da própria célula. Essa proporção mede cobertura do atributo no cadastro auditado e não conhecimento hidrogeológico total.\n\nForam acrescentadas estatísticas descritivas apenas quando já estavam autorizadas na metodologia das camadas, incluindo mediana e P10/P90 da profundidade E02, diversidade nominal de aquíferos E03, zeros em revisão em E04, E05 e E09, tipos de ensaio E07, composição parcial da evidência E10, antiguidade E11 e classes de revisão E12.\n\n## O que não foi calculado\n\nNão foi calculada independência espacial, cobertura vertical, autocorrelação, distância à evidência, kernel density, kriging, ML, score PIH ou prioridade. Essas operações pertencem às próximas etapas.\n'''
(METH/'MALHAS_EVIDENCIA_V1.md').write_text(md,encoding='utf-8')
(OUT/'ESTUDO_MALHAS_EVIDENCIA_V1.md').write_text(md,encoding='utf-8')

# HTML methodology page
rows=''.join(f"<tr><td><b>{r.code}</b></td><td>{r['name']}</td><td>{r['aggregation_rule_provisional']}</td><td>{r['limitations']}</td></tr>" for _,r in registry.iterrows())
html=f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PIH MS · Malhas de evidência</title><link rel="stylesheet" href="assets/css/pih.css"><style>body{{padding:24px;max-width:1200px;margin:auto;background:#f5f8fb}}.doc{{background:#fff;padding:28px;border-radius:16px}}table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #d7e1e8;padding:9px;text-align:left;vertical-align:top}}th{{background:#eaf3f9}}code{{background:#eef3f7;padding:2px 5px;border-radius:4px}}</style></head><body><div class="doc"><h1>PIH MS · Malhas de evidência hidrogeológica V1</h1><p><b>Data de corte</b> 29 de agosto de 2026.</p><p>As malhas de 250, 500 e 1000 km² são calculadas diretamente a partir das feições E01 a E12. Nenhuma escala é média ou agregação de outra escala.</p><div class="panel-note"><b>Nenhum PIH foi calculado.</b> A cor da malha representa somente quantidade de registros com a evidência selecionada. Hexágono transparente não significa ausência de água subterrânea.</div><h2>Estados de suporte</h2><p><code>UNKNOWN_NO_WELLS_IN_DATASET</code> significa ausência de poços no conjunto auditado. <code>NO_EVIDENCE_IN_AUDITED_WELLS</code> significa existência de poços, mas ausência daquela evidência nos registros auditados.</p><h2>Regra espacial</h2><p>Interseção ponto-polígono direta. Um único poço, 3500073933, precisou de associação de contingência à célula PIH-250-0007 por estar 19,14 m fora da geometria recortada da malha de 250 km². O limite de contingência é 50 m e não foi usado em nenhum outro ponto.</p><h2>Camadas agregadas</h2><table><thead><tr><th>Código</th><th>Camada</th><th>Agregação permitida nesta etapa</th><th>Limitação</th></tr></thead><tbody>{rows}</tbody></table><h2>Limite desta etapa</h2><p>Não foram calculados independência espacial, cobertura vertical, autocorrelação, distância à evidência, interpolação, aprendizado de máquina, score PIH ou prioridade.</p></div></body></html>'''
(OUT/'docs/metodologia-malhas-evidencia.html').write_text(html,encoding='utf-8')

# Patch index HTML. Add button and grid evidence block above old experimental grids.
index=OUT/'docs/index.html'; txt=index.read_text(encoding='utf-8')
txt=txt.replace('V1.2','V1.3').replace('V1.1','V1.3')
# top nav add Malhas button if not there
if 'id="navGridEvidence"' not in txt:
    txt=txt.replace('<button id="navEvidence"', '<button id="navEvidence"')
    # insert immediately after Evidências button closing based on known fragment
    txt=txt.replace('</button><button id="navData"', '</button><button id="navGridEvidence" class="nav-btn">⬡ Malhas</button><button id="navData"',1)
# Insert block before old Malhas experimentais group
block='''<div class="layer-group open grid-evidence-group" id="gridEvidenceGroup"><button class="group-title"><span>⬡ Malhas de evidência · E01–E12</span><span>⌄</span></button><div class="group-body"><div class="panel-note"><b>Matriz por hexágono</b><br>Escolha a escala e a evidência. A cor representa somente contagem observada no conjunto auditado.</div><label class="control-label">Escala candidata<select id="gridEvidenceScale"><option value="250">250 km²</option><option value="500">500 km²</option><option value="1000">1000 km²</option></select></label><label class="control-label">Evidência<select id="gridEvidenceCode">''' + ''.join(f'<option value="E{i:02d}">E{i:02d} · {reg[f"E{i:02d}"]["short_name"]}</option>' for i in range(1,13)) + '''</select></label><button id="showGridEvidence" class="panel-action">Mostrar malha de evidência</button><button id="hideGridEvidence" class="panel-action secondary">Ocultar</button><small><a href="metodologia-malhas-evidencia.html" target="_blank">metodologia completa das malhas</a></small></div></div>'''
if 'id="gridEvidenceGroup"' not in txt:
    marker='<div class="layer-group"><button class="group-title"><span>Malhas experimentais PIH</span>'
    txt=txt.replace(marker,block+marker)
index.write_text(txt,encoding='utf-8')

# Patch CSS controls
css=OUT/'docs/assets/css/pih.css'; c=css.read_text(encoding='utf-8')
if '.control-label' not in c:
    c += '''\n.control-label{display:block;font-size:12px;font-weight:700;color:#27485e;margin:9px 0}.control-label select{display:block;width:100%;margin-top:5px;padding:8px 10px;border:1px solid #c8d8e3;border-radius:8px;background:white;color:#17384f}.panel-action{width:100%;padding:9px 10px;margin-top:7px;border:0;border-radius:9px;background:#0b6694;color:#fff;font-weight:800;cursor:pointer}.panel-action.secondary{background:#eaf2f7;color:#23465d}.grid-evidence-group{border-color:#9cc6df}.grid-evidence-chip{display:inline-block;padding:2px 7px;border-radius:999px;background:#e7f2f9;color:#154b69;font-size:11px;font-weight:800}.grid-cell-matrix{display:grid;grid-template-columns:1fr 1fr;gap:7px}.grid-cell-item{border:1px solid #d8e4eb;border-radius:9px;padding:7px;background:#f8fbfd}.grid-cell-item b{display:block;font-size:11px;color:#214a63}.grid-cell-item strong{font-size:16px;color:#092f49}.grid-unknown{color:#71808a;font-style:italic}.grid-evidence-legend .legend-row{align-items:center}.count-swatch{display:inline-block;width:18px;height:12px;border:1px solid #4b545d;margin-right:7px;border-radius:2px}\n'''
css.write_text(c,encoding='utf-8')

# Patch JS. Add specs and implementation just before setBase.
js=OUT/'docs/assets/js/pih.js'; j=js.read_text(encoding='utf-8')
j=j.replace("const V='1.1'","const V='1.3'").replace('PIH MS V1.1','PIH MS V1.3')
# Add grid evidence specs after g1000 line
old="g250:{url:'data/malha_250km2_candidata.geojson',kind:'geo'},g500:{url:'data/malha_500km2_candidata.geojson',kind:'geo'},g1000:{url:'data/malha_1000km2_candidata.geojson',kind:'geo'},"
new=old+"\nge250:{url:'data/grid_evidence/malha_evidencia_250km2.geojson',kind:'geo'},ge500:{url:'data/grid_evidence/malha_evidencia_500km2.geojson',kind:'geo'},ge1000:{url:'data/grid_evidence/malha_evidencia_1000km2.geojson',kind:'geo'},"
j=j.replace(old,new)
# Extend polygon style function via special keys. Locate styleFor beginning
# We patch a known function declaration string.
if 'function gridEvidenceColor' not in j:
    inject=r'''
let activeGridEvidenceKey=null, activeGridEvidenceCode='E01', gridEvidenceStyleMeta=null;
async function ensureGridEvidenceMeta(){if(gridEvidenceStyleMeta)return gridEvidenceStyleMeta;gridEvidenceStyleMeta=await getJSON('data/grid_evidence/grid_evidence_style_metadata.json');return gridEvidenceStyleMeta;}
function gridEvidenceColor(code,count,breaks){if(!count||count<=0)return 'transparent';const palette=code==='E12'?['#fee8c8','#fdbb84','#fc8d59','#d7301f','#8c2d04']:['#dbeef7','#a6cee3','#6baed6','#3182bd','#08519c'];let idx=0;for(let i=0;i<breaks.length;i++)if(count>breaks[i])idx=i+1;return palette[Math.min(idx,palette.length-1)];}
function gridEvidenceStyle(f,key){const code=activeGridEvidenceCode||'E01';const n=Number(f.properties?.['n_'+code]||0);const meta=gridEvidenceStyleMeta?.[key.replace('ge','')]?.[code]||{count_breaks:[]};return {pane:'gridPane',color:'#4b545d',weight:.8,opacity:.85,fillColor:gridEvidenceColor(code,n,meta.count_breaks||[]),fillOpacity:n>0?.68:0};}
function gridEvidenceFicha(p){const code=activeGridEvidenceCode||'E01';let items='';for(let i=1;i<=12;i++){const c='E'+String(i).padStart(2,'0'),n=Number(p['n_'+c]||0),pc=i===1?(n?100:null):p['pct_'+c+'_of_E01'];items+=`<div class="grid-cell-item"><b>${c} · ${esc(evidenceInfo[c.toLowerCase()]?.name||c)}</b><strong>${n.toLocaleString('pt-BR')}</strong><div>${pc===null||pc===undefined||Number.isNaN(Number(pc))?'<span class="grid-unknown">UNKNOWN</span>':Number(pc).toFixed(1)+'% dos poços E01'}</div><small>${esc(p['state_'+c]||'')}</small></div>`;}return `<div class="well-ficha"><div class="well-hero"><div class="well-id">${esc(p.pih_cell_id)}</div><div class="well-sub">Malha candidata ${esc(p.area_nominal_km2)} km² · área efetiva em MS ${fmt(p.area_efetiva_ms_km2,2)} km²</div><div class="well-badges"><span class="well-badge unknown">SEM SCORE PIH</span><span class="well-badge review">Camada ativa ${esc(code)}</span></div></div><section class="ficha-section"><h4>Matriz de evidência da célula</h4><div class="grid-cell-matrix">${items}</div><div class="ficha-note">Percentuais usam E01 da própria célula como denominador e medem cobertura cadastral do atributo. Não medem conhecimento hidrogeológico total.</div></section><section class="ficha-section"><h4>Estatísticas descritivas disponíveis</h4><div class="ficha-grid">${frow('Profundidade mediana',p.E02_depth_median_m,'derived',' m')}${frow('Profundidade P10',p.E02_depth_p10_m,'derived',' m')}${frow('Profundidade P90',p.E02_depth_p90_m,'derived',' m')}${frow('Aquíferos nominais distintos',p.E03_aquifer_n_unique,'derived')}${frow('Zeros NE em revisão',p.E04_zero_review_count,'derived')}${frow('Zeros ND em revisão',p.E05_zero_review_count,'derived')}${frow('Mediana campos hidroquímicos disponíveis',p.E10_available_fields_median,'derived')}${frow('Antiguidade mediana E11',p.E11_age_median_years,'derived',' anos')}</div></section><section class="ficha-section"><h4>Leitura obrigatória</h4><div class="ficha-note">Hexágono sem E01 é UNKNOWN no conjunto auditado e não significa ausência de água subterrânea. Hexágono com E01 mas sem outra evidência significa somente ausência desse atributo nos poços auditados desta célula.</div><p><a href="metodologia-malhas-evidencia.html" target="_blank">Abrir metodologia completa</a></p></section></div>`;}
async function showGridEvidence(){const scale=document.getElementById('gridEvidenceScale')?.value||'250',code=document.getElementById('gridEvidenceCode')?.value||'E01';const key='ge'+scale;await ensureGridEvidenceMeta();activeGridEvidenceCode=code;if(activeGridEvidenceKey&&activeGridEvidenceKey!==key&&layers[activeGridEvidenceKey])map.removeLayer(layers[activeGridEvidenceKey]);activeGridEvidenceKey=key;const layer=await ensureLayer(key);layer.setStyle(f=>gridEvidenceStyle(f,key));if(!map.hasLayer(layer))layer.addTo(map);layer.bringToFront();updateLegend();}
function hideGridEvidence(){if(activeGridEvidenceKey&&layers[activeGridEvidenceKey]&&map.hasLayer(layers[activeGridEvidenceKey]))map.removeLayer(layers[activeGridEvidenceKey]);activeGridEvidenceKey=null;updateLegend();}
'''
    j=j.replace('function setBase(k){',inject+'\nfunction setBase(k){')
# Patch styleFor function to recognize ge keys using regex replacement simple
j=j.replace("function styleFor(key,f){", "function styleFor(key,f){if(/^ge(250|500|1000)$/.test(key))return gridEvidenceStyle(f,key);")
# Patch feature click handling. Find onEach function declaration and prepend case based on regex known.
j=j.replace("function onEach(key,f,l){", "function onEach(key,f,l){if(/^ge(250|500|1000)$/.test(key)){l.on('click',e=>{L.DomEvent.stopPropagation(e);lastSelection={key,feature:f};document.getElementById('featureTitle').textContent='Malha de evidência';info.innerHTML=gridEvidenceFicha(f.properties||{});openRight();});return;}")
# Extend legend before old malhas exp
legend_insert="if(activeGridEvidenceKey&&layers[activeGridEvidenceKey]&&map.hasLayer(layers[activeGridEvidenceKey])){const sc=activeGridEvidenceKey.replace('ge',''),code=activeGridEvidenceCode,e=evidenceInfo[code.toLowerCase()]||{name:code};const meta=gridEvidenceStyleMeta?.[sc]?.[code]||{count_breaks:[]};const br=meta.count_breaks||[];const vals=[1,...br.map(x=>x+1)];const labels=vals.map((v,i)=>i===0?(br.length?'1–'+br[0]:'≥1'):(i<br.length?(v+'–'+br[i]):('≥'+v)));const pal=code==='E12'?['#fee8c8','#fdbb84','#fc8d59','#d7301f','#8c2d04']:['#dbeef7','#a6cee3','#6baed6','#3182bd','#08519c'];sec.push(`<div class=\"legend-section grid-evidence-legend\"><div class=\"legend-title\">Malha ${sc} km² · ${code} ${esc(e.name)}</div>${labels.slice(0,pal.length).map((x,i)=>`<div class=\"legend-row\"><span class=\"count-swatch\" style=\"background:${pal[i]}\"></span>${x} registros</div>`).join('')}<div class=\"legend-row\"><span class=\"count-swatch\" style=\"background:transparent\"></span>0 registros · transparente</div><div class=\"legend-note\">Contagem de evidência observada. Não representa prioridade ou potencial aquífero.</div></div>`);}"
j=j.replace("if(['g250','g500','g1000'].some(isOn))sec.push", legend_insert+"if(['g250','g500','g1000'].some(isOn))sec.push")
# Event handlers before init call
handlers="const gridShow=document.getElementById('showGridEvidence'),gridHide=document.getElementById('hideGridEvidence'),gridCode=document.getElementById('gridEvidenceCode');if(gridShow)gridShow.onclick=showGridEvidence;if(gridHide)gridHide.onclick=hideGridEvidence;if(gridCode)gridCode.onchange=()=>{if(activeGridEvidenceKey)showGridEvidence()};const gridScale=document.getElementById('gridEvidenceScale');if(gridScale)gridScale.onchange=()=>{if(activeGridEvidenceKey)showGridEvidence()};const navGrid=document.getElementById('navGridEvidence');if(navGrid)navGrid.onclick=()=>{app.classList.add('left-open');const g=document.getElementById('gridEvidenceGroup');if(g){g.classList.add('open');setTimeout(()=>g.scrollIntoView({behavior:'smooth',block:'start'}),100)}setTimeout(()=>map.invalidateSize(),180)};\n"
j=j.replace("init();\n})();",handlers+"init();\n})();")
js.write_text(j,encoding='utf-8')

# Version and readme/changelog
(OUT/'VERSION').write_text('1.3\n',encoding='utf-8')
readme=OUT/'README.md'; rt=readme.read_text(encoding='utf-8') if readme.exists() else '# PIH MS\n'
rt=rt.replace('V1.2','V1.3').replace('V1.1','V1.3')+"\n\n## V1.3\n\nAgregação direta E01–E12 nas malhas candidatas de 250, 500 e 1000 km². Nenhum score PIH calculado.\n"
readme.write_text(rt,encoding='utf-8')
with open(OUT/'CHANGELOG.md','a',encoding='utf-8') as f:f.write('\n## V1.3 · 2026-08-29\n- Malhas de evidência E01–E12 em 250, 500 e 1000 km².\n- Fichas de célula com matriz completa.\n- Auditoria da atribuição espacial.\n- Nenhum score PIH.\n')
with open(OUT/'DECISION_LOG.md','a',encoding='utf-8') as f:f.write('\n## D13\nAs três escalas são calculadas diretamente das feições originais E01–E12. Zero não é convertido em ausência de água. Células sem E01 permanecem UNKNOWN.\n')
# starter
(OUT/'INICIAR_PIH_MS_8563.bat').write_text('@echo off\ncd /d "%~dp0docs"\nstart http://localhost:8563/?v=13\npy -m http.server 8563\n',encoding='utf-8')
# Copy build script itself
shutil.copy2('/mnt/data/build_pih_v13_grids.py', SCRIPTS/'build_grid_evidence_v1.py')

# Basic checks
assert len(pd.read_csv(GRIDOUT/'malha_evidencia_250km2.csv'))==1554
assert len(pd.read_csv(GRIDOUT/'malha_evidencia_500km2.csv'))==793
assert len(pd.read_csv(GRIDOUT/'malha_evidencia_1000km2.csv'))==412
for scale in (250,500,1000):
    df=pd.read_csv(GRIDOUT/f'malha_evidencia_{scale}km2.csv')
    assert int(df.n_E01.sum())==3877, (scale,df.n_E01.sum())
for row in assignment_audit:
    assert row['n_unassigned']==0

# Manifest hashes for generated data
manifest=[]
for p in sorted(GRIDOUT.glob('*')):
    if p.is_file():
        manifest.append({'file':str(p.relative_to(OUT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})
pd.DataFrame(manifest).to_csv(PROV/'grid_evidence_manifest.csv',index=False,encoding='utf-8-sig')

# zip
zip_path=Path('/mnt/data/pih-ms-v1.3-malhas-evidencia.zip')
if zip_path.exists(): zip_path.unlink()
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
    for p in OUT.rglob('*'):
        if p.is_file(): z.write(p,p.relative_to(OUT.parent))
print(json.dumps({'out':str(OUT),'zip':str(zip_path),'summary':scale_summary,'assignment_audit':assignment_audit},ensure_ascii=False,indent=2))
