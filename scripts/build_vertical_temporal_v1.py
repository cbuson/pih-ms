import csv, json, math, os, statistics, re
from pathlib import Path
from datetime import datetime, date
from collections import Counter, defaultdict
import numpy as np
from shapely.geometry import shape, Point, mapping
from shapely.strtree import STRtree

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/derived/vertical_temporal'
DOC=ROOT/'docs/data/vertical_temporal'
OUT.mkdir(parents=True,exist_ok=True); DOC.mkdir(parents=True,exist_ok=True)
CUTOFF=date(2026,8,29)

# Load source datasets
well_details=json.load(open(ROOT/'docs/data/well_details.json',encoding='utf-8'))
current_geo=json.load(open(ROOT/'docs/data/siagas_pocos_ms.geojson',encoding='utf-8'))
sgb_geo=json.load(open(ROOT/'docs/data/pocos_sgb_2024.geojson',encoding='utf-8'))
wm_rows=list(csv.DictReader(open(ROOT/'data/source_audit/wells_master.csv',encoding='utf-8-sig')))
wm={r['well_id']:r for r in wm_rows}

# Helpers
def norm_id(x):
    s=str(x or '').strip()
    if s.endswith('.0'): s=s[:-2]
    return s

def parse_date(x):
    if x in (None,'','UNKNOWN','None'): return None
    x=str(x).strip()
    for f in ('%Y-%m-%d','%d/%m/%Y','%d/%m/%y','%Y/%m/%d'):
        try:return datetime.strptime(x,f).date()
        except: pass
    return None

def num(x):
    if x in (None,'','UNKNOWN','None'): return None
    try:return float(str(x).replace(',','.'))
    except:return None

def truthy(x): return str(x).strip().lower() in ('true','1','yes','sim','s')
def present(x): return x not in (None,'','UNKNOWN','None')
def q(vals,p):
    vals=[float(v) for v in vals if v is not None and math.isfinite(float(v))]
    if not vals:return None
    return float(np.quantile(vals,p))
def med(vals):
    vals=[float(v) for v in vals if v is not None and math.isfinite(float(v))]
    return float(np.median(vals)) if vals else None

def years_old(d): return (CUTOFF-d).days/365.2425 if d else None

def iso(d): return d.isoformat() if d else ''

# Current point lookup and RIMAS status from original current SIAGAS export
current_props={}
current_geom={}
for f in current_geo['features']:
    p=f['properties']; wid=norm_id(p.get('idt_ponto') or p.get('well_id') or p.get('ponto'))
    current_props[wid]=p; current_geom[wid]=f['geometry']

# Historical fields including dated measurement, topo/base/diameter
hist_props={}
for f in sgb_geo['features']:
    p=f['properties']; wid=norm_id(p.get('ponto'))
    hist_props[wid]=p

# Per well vertical and temporal table
well_rows=[]
point_features_by_code=defaultdict(list)
layer_defs={
 'V02':('Formação do poço documentada','#00897B'),
 'V03':('Tipo de penetração documentado','#00A6A6'),
 'V04':('Condição hidráulica documentada','#00796B'),
 'V05':('Tipo de captação documentado','#26A69A'),
 'V06':('Topo e base brutos coerentes','#00695C'),
 'V07':('Diâmetro documentado','#4DB6AC'),
 'T01':('Ensaio de bombeamento datado','#6A51A3'),
 'T02':('Evidência química datada','#8C6BB1'),
 'T03':('Medição de nível datada','#4A1486'),
 'T04':('Evidência hidrogeológica datada','#7B1FA2'),
 'T05':('Múltiplos domínios de evidência datada','#9C27B0'),
 'T06':('Cadastro identificado como RIMAS','#5E35B1'),
}

# normalize hydro domains by spatial overlay later from polygon map
hydro_domain_geo=json.load(open(ROOT/'docs/data/dominio_hidrolitologico_sgb_2024.geojson',encoding='utf-8'))
domain_geoms=[shape(f['geometry']) for f in hydro_domain_geo['features']]
domain_tree=STRtree(domain_geoms)
# Shapely 2 query returns indices

def domain_for_point(lon,lat):
    pt=Point(lon,lat)
    try:
        cand=domain_tree.query(pt)
        for idx in cand:
            g=domain_geoms[int(idx)]
            if g.covers(pt):
                p=hydro_domain_geo['features'][int(idx)]['properties']
                for k in ('U_HL_AFL','dominio','Domínio','DOMINIO','classe','Classe','class','hidrolitologia','tipo'):
                    if p.get(k):
                        raw=str(p[k]).strip()
                        low=raw.lower()
                        if 'granular' in low: return 'Granular'
                        if 'fratur' in low: return 'Fraturada'
                        if 'cárst' in low or 'carst' in low: return 'Cárstica'
                        return raw
                for v in p.values():
                    if isinstance(v,str):
                        low=v.strip().lower()
                        if 'granular' in low: return 'Granular'
                        if 'fratur' in low: return 'Fraturada'
                        if 'cárst' in low or 'carst' in low: return 'Cárstica'
    except Exception: pass
    return ''

for wid,row in wm.items():
    wd=well_details.get(wid,{})
    con=wd.get('construction',{})
    hyd=wd.get('hydraulics',{})
    dates=wd.get('dates',{})
    hp=hist_props.get(wid,{})
    cp=current_props.get(wid,{})
    lon=num(row.get('longitude')); lat=num(row.get('latitude'))
    depth=num(row.get('depth_current_m'))
    formation=con.get('formation_sgb2024') or hp.get('tipo_forma')
    pen=con.get('penetration_type_sgb2024') or hp.get('tipo_penet')
    hcond=con.get('hydraulic_condition_sgb2024') or hp.get('condicao')
    capture=con.get('capture_type_sgb2024') or hp.get('tipo_capta')
    diameter=con.get('diameter_raw_sgb2024') or hp.get('diametro_b')
    top=num(con.get('top_raw_sgb2024') if present(con.get('top_raw_sgb2024')) else hp.get('topo'))
    base=num(con.get('base_raw_sgb2024') if present(con.get('base_raw_sgb2024')) else hp.get('base'))
    topbase= bool(top is not None and base is not None and top>0 and base>top)
    topbase_thickness=(base-top) if topbase else None
    explicit_profile=truthy(wd.get('quality',{}).get('atlas_explicit_profile'))
    # vertical metadata count, excluding depth itself
    vert_flags=[bool(present(formation)),bool(present(pen)),bool(present(hcond)),bool(present(capture)),bool(present(diameter)),topbase,explicit_profile]
    vertical_metadata_n=sum(vert_flags)
    if depth is None or depth<=0:
        vertical_documentation_state='SEM_PROFUNDIDADE_POSITIVA'
    elif vertical_metadata_n==0:
        vertical_documentation_state='PROFUNDIDADE_APENAS'
    else:
        vertical_documentation_state='PROFUNDIDADE_MAIS_METADADOS'
    # capture interval cannot be demonstrated from current acquired source because no screen/filter interval table
    capture_interval_status='UNKNOWN_SEM_INTERVALO_DE_FILTRO_DEMONSTRADO'

    test_date=parse_date(hyd.get('test_date_sgb2024'))
    chem_date=parse_date(dates.get('collection_date_sgb2024')) or parse_date(dates.get('analysis_date_sgb2024'))
    level_date=parse_date(hp.get('data_medic'))
    events=[]
    if test_date: events.append(('TESTE',test_date))
    if chem_date: events.append(('QUIMICA',chem_date))
    if level_date: events.append(('NIVEL',level_date))
    event_domains=sorted(set(k for k,d in events))
    event_dates=sorted(set(d for k,d in events))
    latest=max(event_dates) if event_dates else None
    earliest=min(event_dates) if event_dates else None
    current_status=str(cp.get('status_rimas') or '').strip()
    is_rimas=current_status.lower()=='rimas'
    temporal_state='UNKNOWN_SEM_EVIDENCIA_DATADA'
    if len(event_domains)==1: temporal_state='EVIDENCIA_DATADA_UM_DOMINIO'
    elif len(event_domains)>=2: temporal_state='EVIDENCIA_DATADA_MULTIPLOS_DOMINIOS'
    series_status='UNKNOWN_SERIE_TEMPORAL_NAO_ADQUIRIDA'
    # a single historical level measurement is not a series
    domain=domain_for_point(lon,lat) if lon is not None and lat is not None else ''
    rec={
      'well_id':wid,'longitude':lon,'latitude':lat,
      'sgb2024_unit_aflorante':row.get('sgb2024_unit_aflorante',''),
      'hydrolithologic_domain':domain,
      'depth_positive':bool(depth is not None and depth>0),'depth_m':depth,
      'formation_documented':bool(present(formation)),'formation':formation or '',
      'penetration_type_documented':bool(present(pen)),'penetration_type':pen or '',
      'hydraulic_condition_documented':bool(present(hcond)),'hydraulic_condition':hcond or '',
      'capture_type_documented':bool(present(capture)),'capture_type':capture or '',
      'diameter_documented':bool(present(diameter)),'diameter_raw':diameter or '',
      'top_base_raw_coherent':topbase,'top_raw_m':top,'base_raw_m':base,'top_base_raw_thickness_m':topbase_thickness,
      'explicit_profile_documented':explicit_profile,
      'vertical_metadata_n':vertical_metadata_n,'vertical_documentation_state':vertical_documentation_state,
      'capture_interval_status':capture_interval_status,
      'test_dated':bool(test_date),'test_date':iso(test_date),
      'chemistry_dated':bool(chem_date),'chemistry_date':iso(chem_date),
      'level_measurement_dated':bool(level_date),'level_measurement_date':iso(level_date),'level_measurement_raw':hp.get('nivel_agua') or '',
      'dated_evidence_any':bool(events),'dated_domains_n':len(event_domains),'dated_domains':'|'.join(event_domains),
      'dated_distinct_dates_n':len(event_dates),'earliest_evidence_date':iso(earliest),'latest_evidence_date':iso(latest),
      'latest_evidence_age_years':years_old(latest),'evidence_date_span_years':((latest-earliest).days/365.2425 if latest and earliest else None),
      'rimas_status_current':current_status,'rimas_registered':is_rimas,
      'temporal_documentation_state':temporal_state,'time_series_status':series_status,
    }
    well_rows.append(rec)
    # point layers
    codes=[]
    if rec['formation_documented']: codes.append('V02')
    if rec['penetration_type_documented']: codes.append('V03')
    if rec['hydraulic_condition_documented']: codes.append('V04')
    if rec['capture_type_documented']: codes.append('V05')
    if rec['top_base_raw_coherent']: codes.append('V06')
    if rec['diameter_documented']: codes.append('V07')
    if rec['test_dated']: codes.append('T01')
    if rec['chemistry_dated']: codes.append('T02')
    if rec['level_measurement_dated']: codes.append('T03')
    if rec['dated_evidence_any']: codes.append('T04')
    if rec['dated_domains_n']>=2: codes.append('T05')
    if rec['rimas_registered']: codes.append('T06')
    geom=current_geom.get(wid)
    if geom:
      baseprops={'well_id':wid,'municipality':row.get('municipality_declared',''),'hydro_unit':row.get('sgb2024_unit_aflorante',''),'domain':domain}
      for code in codes:
        pp=dict(baseprops); pp.update({'layer_code':code,'layer_name':layer_defs[code][0]})
        # selected diagnostic values
        if code.startswith('V'):
          pp.update({'depth_m':depth,'vertical_metadata_n':vertical_metadata_n,'capture_interval_status':capture_interval_status})
        else:
          pp.update({'latest_evidence_date':iso(latest),'latest_evidence_age_years':years_old(latest),'dated_domains_n':len(event_domains),'time_series_status':series_status})
        point_features_by_code[code].append({'type':'Feature','geometry':geom,'properties':pp})

# Write well table
fields=list(well_rows[0].keys())
with open(OUT/'well_vertical_temporal.csv','w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(well_rows)

# Point layers, CSV and geojson
for code,(name,color) in layer_defs.items():
    feats=point_features_by_code[code]
    gj={'type':'FeatureCollection','features':feats}
    for target in (OUT,DOC):
      json.dump(gj,open(target/f'{code}.geojson','w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
    with open(OUT/f'{code}.csv','w',encoding='utf-8-sig',newline='') as f:
      if feats:
        hs=list(feats[0]['properties'].keys())
        w=csv.DictWriter(f,fieldnames=hs); w.writeheader(); w.writerows([x['properties'] for x in feats])
      else:
        f.write('well_id\n')

# registry and statistics
stats=[]
for code,(name,color) in layer_defs.items():
    stats.append({'code':code,'name':name,'feature_count':len(point_features_by_code[code]),'pct_of_3877':round(len(point_features_by_code[code])/3877*100,4),'color':color})
# T07 explicit no-series state
stats.append({'code':'T07','name':'Série temporal demonstrada no conjunto adquirido','feature_count':0,'pct_of_3877':0,'color':'#5B5B88'})
with open(OUT/'vertical_temporal_layer_statistics.csv','w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(stats[0].keys())); w.writeheader(); w.writerows(stats)

registry=[
 {'code':'V01','name':'Profundidade positiva','source':'E02','question':'Existe profundidade total positiva no cadastro auditado','rule':'Reutiliza E02. Não demonstra intervalo captado','status':'IMPLEMENTADA_POR_E02'},
 {'code':'V02','name':'Formação do poço documentada','source':'SGB 2024 poços','question':'Existe formação geológica registrada para o poço','rule':'Campo tipo_forma ou formation_sgb2024 não vazio','status':'IMPLEMENTADA'},
 {'code':'V03','name':'Tipo de penetração documentado','source':'SGB 2024 poços','question':'Existe indicação parcial ou total de penetração','rule':'Campo tipo_penet não vazio','status':'IMPLEMENTADA'},
 {'code':'V04','name':'Condição hidráulica documentada','source':'SGB 2024 poços','question':'Existe condição livre, confinada ou intermediária registrada','rule':'Campo condicao não vazio','status':'IMPLEMENTADA'},
 {'code':'V05','name':'Tipo de captação documentado','source':'SGB 2024 poços','question':'Existe indicação de captação única ou simultânea','rule':'Campo tipo_capta não vazio','status':'IMPLEMENTADA'},
 {'code':'V06','name':'Topo e base brutos coerentes','source':'SGB 2024 poços','question':'Existem valores positivos de topo e base com base maior que topo','rule':'topo > 0 e base > topo. Sem inferir que sejam filtros','status':'IMPLEMENTADA'},
 {'code':'V07','name':'Diâmetro documentado','source':'SGB 2024 poços','question':'Existe diâmetro bruto informado','rule':'Campo diametro_b não vazio','status':'IMPLEMENTADA'},
 {'code':'V08','name':'Intervalo de filtro ou tela demonstrado','source':'SIAGAS e SGB adquiridos','question':'É possível demonstrar o intervalo efetivamente filtrado ou aberto','rule':'Nenhuma tabela de filtros ou telas foi adquirida nesta fase','status':'UNKNOWN_NAO_DEMONSTRADO'},
 {'code':'T01','name':'Ensaio de bombeamento datado','source':'SGB 2024 poços','question':'Existe data do ensaio hidráulico','rule':'data_teste interpretável','status':'IMPLEMENTADA'},
 {'code':'T02','name':'Evidência química datada','source':'SGB 2024 poços','question':'Existe data de coleta ou análise química','rule':'Prioriza data_colet e usa data_anali quando coleta não está disponível','status':'IMPLEMENTADA'},
 {'code':'T03','name':'Medição de nível datada','source':'SGB 2024 poços','question':'Existe data_medic associada a nivel_agua','rule':'data_medic interpretável. Uma medição não forma série','status':'IMPLEMENTADA'},
 {'code':'T04','name':'Evidência hidrogeológica datada','source':'T01 T02 T03','question':'Existe ao menos um evento hidrogeológico datado','rule':'União de teste, química e medição de nível datados','status':'IMPLEMENTADA'},
 {'code':'T05','name':'Múltiplos domínios datados','source':'T01 T02 T03','question':'O poço possui evidência datada em pelo menos dois domínios distintos','rule':'Dois ou mais entre teste, química e nível','status':'IMPLEMENTADA'},
 {'code':'T06','name':'Cadastro identificado como RIMAS','source':'SIAGAS 2026 snapshot','question':'O campo status_rimas identifica o registro como Rimas','rule':'status_rimas = Rimas. Não prova disponibilidade local da série','status':'IMPLEMENTADA'},
 {'code':'T07','name':'Série temporal demonstrada','source':'Dados adquiridos até o corte','question':'Existe sequência temporal da mesma variável suficiente para caracterizar uma série','rule':'Nenhuma série completa foi adquirida nesta fase','status':'UNKNOWN_NAO_DEMONSTRADO'},
]
with open(OUT/'vertical_temporal_registry.csv','w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(registry[0].keys())); w.writeheader(); w.writerows(registry)

# Hydro unit and domain summaries
by_unit=defaultdict(list); by_domain=defaultdict(list)
for r in well_rows:
    by_unit[r['sgb2024_unit_aflorante'] or 'UNKNOWN'].append(r)
    by_domain[r['hydrolithologic_domain'] or 'UNKNOWN'].append(r)

def group_summary(group,name_key,name):
    out=[]
    for key,rows in sorted(group.items()):
      n=len(rows)
      dated=[r for r in rows if r['dated_evidence_any']]
      ages=[r['latest_evidence_age_years'] for r in dated if r['latest_evidence_age_years'] is not None]
      rec={name_key:key,'n_wells':n,
        'depth_positive_pct':sum(r['depth_positive'] for r in rows)/n*100 if n else None,
        'formation_documented_pct':sum(r['formation_documented'] for r in rows)/n*100 if n else None,
        'penetration_documented_pct':sum(r['penetration_type_documented'] for r in rows)/n*100 if n else None,
        'hydraulic_condition_documented_pct':sum(r['hydraulic_condition_documented'] for r in rows)/n*100 if n else None,
        'capture_type_documented_pct':sum(r['capture_type_documented'] for r in rows)/n*100 if n else None,
        'top_base_raw_pct':sum(r['top_base_raw_coherent'] for r in rows)/n*100 if n else None,
        'diameter_documented_pct':sum(r['diameter_documented'] for r in rows)/n*100 if n else None,
        'test_dated_pct':sum(r['test_dated'] for r in rows)/n*100 if n else None,
        'chemistry_dated_pct':sum(r['chemistry_dated'] for r in rows)/n*100 if n else None,
        'level_measurement_dated_pct':sum(r['level_measurement_dated'] for r in rows)/n*100 if n else None,
        'dated_any_pct':sum(r['dated_evidence_any'] for r in rows)/n*100 if n else None,
        'multi_domain_dated_pct':sum(r['dated_domains_n']>=2 for r in rows)/n*100 if n else None,
        'rimas_registered_n':sum(r['rimas_registered'] for r in rows),
        'latest_evidence_age_median_years':med(ages),'latest_evidence_age_p90_years':q(ages,.9),
        'series_demonstrated_n':0}
      out.append(rec)
    return out
unit_summary=group_summary(by_unit,'hydro_unit','unit')
domain_summary=group_summary(by_domain,'hydrolithologic_domain','domain')
for fn,rows in [('vertical_temporal_by_hydro_unit.csv',unit_summary),('vertical_temporal_by_domain.csv',domain_summary)]:
  with open(OUT/fn,'w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

# Build synthetic scale grids from existing geojson and assign wells
# point geometry source from current snapshot
well_pts={wid:Point(rec['longitude'],rec['latitude']) for wid,rec in [(r['well_id'],r) for r in well_rows] if rec['longitude'] is not None and rec['latitude'] is not None}
well_rec={r['well_id']:r for r in well_rows}
scale_summary=[]
for scale in (100,150,250,500,1000):
    grid=json.load(open(ROOT/f'docs/data/scale_study/scale_primary_{scale}km2.geojson',encoding='utf-8'))
    geoms=[shape(f['geometry']) for f in grid['features']]
    tree=STRtree(geoms)
    cell_wells=[[] for _ in geoms]
    for wid,pt in well_pts.items():
      cand=tree.query(pt)
      hit=None
      for idx in cand:
        if geoms[int(idx)].covers(pt): hit=int(idx); break
      if hit is not None: cell_wells[hit].append(wid)
    output_features=[]; csvrows=[]
    for i,f in enumerate(grid['features']):
      p=dict(f.get('properties',{})); ids=cell_wells[i]; rows=[well_rec[x] for x in ids]; n=len(rows)
      def cnt(k):return sum(bool(r[k]) for r in rows)
      ages=[r['latest_evidence_age_years'] for r in rows if r['latest_evidence_age_years'] is not None]
      latest_dates=[parse_date(r['latest_evidence_date']) for r in rows if r['latest_evidence_date']]
      all_dates=[]
      for r in rows:
        for k in ('test_date','chemistry_date','level_measurement_date'):
          d=parse_date(r[k]);
          if d: all_dates.append(d)
      fields={
        'vt_n_wells':n,
        'V01_depth_positive_n':cnt('depth_positive'),'V02_formation_n':cnt('formation_documented'),'V03_penetration_n':cnt('penetration_type_documented'),'V04_hydraulic_condition_n':cnt('hydraulic_condition_documented'),'V05_capture_type_n':cnt('capture_type_documented'),'V06_top_base_raw_n':cnt('top_base_raw_coherent'),'V07_diameter_n':cnt('diameter_documented'),'V08_screen_interval_n':0,
        'T01_test_dated_n':cnt('test_dated'),'T02_chemistry_dated_n':cnt('chemistry_dated'),'T03_level_dated_n':cnt('level_measurement_dated'),'T04_any_dated_n':cnt('dated_evidence_any'),'T05_multi_domain_dated_n':sum(r['dated_domains_n']>=2 for r in rows),'T06_rimas_registered_n':cnt('rimas_registered'),'T07_series_demonstrated_n':0,
        'latest_evidence_age_median_years':med(ages),'latest_evidence_age_p90_years':q(ages,.9),
        'dated_distinct_years_n':len(set(d.year for d in all_dates)),
        'dated_dataset_span_years':((max(all_dates)-min(all_dates)).days/365.2425 if len(all_dates)>=2 else None),
        'depth_median_m':med([r['depth_m'] for r in rows]),'depth_p10_m':q([r['depth_m'] for r in rows],.1),'depth_p90_m':q([r['depth_m'] for r in rows],.9),
        'top_base_raw_thickness_median_m':med([r['top_base_raw_thickness_m'] for r in rows]),
        'capture_interval_status':'UNKNOWN_SEM_INTERVALO_DE_FILTRO_DEMONSTRADO',
        'time_series_status':'UNKNOWN_SERIE_TEMPORAL_NAO_ADQUIRIDA',
      }
      for codefield in ['V01_depth_positive_n','V02_formation_n','V03_penetration_n','V04_hydraulic_condition_n','V05_capture_type_n','V06_top_base_raw_n','V07_diameter_n','T01_test_dated_n','T02_chemistry_dated_n','T03_level_dated_n','T04_any_dated_n','T05_multi_domain_dated_n','T06_rimas_registered_n']:
        fields[codefield.replace('_n','_pct_of_wells')]=(fields[codefield]/n*100 if n else None)
      p.update(fields)
      out_f={'type':'Feature','geometry':f['geometry'],'properties':p}; output_features.append(out_f)
      row={'cell_id':p.get('cell_id') or p.get('pih_cell_id') or p.get('id') or str(i),'scale_km2':scale}; row.update(fields); csvrows.append(row)
    gj={'type':'FeatureCollection','features':output_features}
    json.dump(gj,open(OUT/f'vertical_temporal_{scale}km2.geojson','w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
    json.dump(gj,open(DOC/f'vertical_temporal_{scale}km2.geojson','w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
    with open(OUT/f'vertical_temporal_{scale}km2.csv','w',encoding='utf-8-sig',newline='') as fcsv:
      w=csv.DictWriter(fcsv,fieldnames=list(csvrows[0].keys())); w.writeheader(); w.writerows(csvrows)
    occupied=[r for r in csvrows if r['vt_n_wells']>0]
    scale_summary.append({'scale_km2':scale,'n_cells':len(csvrows),'cells_with_wells':len(occupied),'cells_without_wells':len(csvrows)-len(occupied),
      'median_formation_pct_occupied':med([r['V02_formation_pct_of_wells'] for r in occupied]),
      'median_penetration_pct_occupied':med([r['V03_penetration_pct_of_wells'] for r in occupied]),
      'median_top_base_raw_pct_occupied':med([r['V06_top_base_raw_pct_of_wells'] for r in occupied]),
      'median_any_dated_pct_occupied':med([r['T04_any_dated_pct_of_wells'] for r in occupied]),
      'median_latest_age_years_occupied':med([r['latest_evidence_age_median_years'] for r in occupied]),
      'cells_with_dated_level_measurement':sum(r['T03_level_dated_n']>0 for r in csvrows),
      'cells_with_rimas_registration':sum(r['T06_rimas_registered_n']>0 for r in csvrows),
      'cells_with_demonstrated_time_series':0})
with open(OUT/'vertical_temporal_scale_summary.csv','w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(scale_summary[0].keys())); w.writeheader(); w.writerows(scale_summary)

# Global audit notes and consistency issue with previous wells_master rimas flag
rimas_current=[wid for wid,p in current_props.items() if str(p.get('status_rimas') or '').strip().lower()=='rimas']
with open(OUT/'vertical_temporal_audit.csv','w',encoding='utf-8-sig',newline='') as f:
  fields=['check','result','status','note']; w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
  w.writerow({'check':'CURRENT_SIAGAS_RIMAS_STATUS','result':len(rimas_current),'status':'VERIFIED_FROM_ORIGINAL_GEOJSON','note':'22 registros possuem status_rimas = Rimas no snapshot atual. O campo rimas_flag_current do wells_master V1 estava incorreto e não foi reutilizado.'})
  w.writerow({'check':'DATED_LEVEL_MEASUREMENTS_SGB2024','result':sum(r['level_measurement_dated'] for r in well_rows),'status':'VERIFIED','note':'data_medic associada a nivel_agua. Uma medição não constitui série temporal.'})
  w.writerow({'check':'EXPLICIT_FILTER_SCREEN_INTERVALS','result':0,'status':'NOT_ACQUIRED','note':'Não foi adquirida tabela relacional de filtros ou telas. Representatividade do intervalo captado permanece UNKNOWN.'})
  w.writerow({'check':'DEMONSTRATED_TIME_SERIES','result':0,'status':'NOT_ACQUIRED','note':'O conjunto atual não contém séries completas da mesma variável por poço. Cadastro RIMAS não foi convertido em série observacional.'})

print('well rows',len(well_rows))
print('stats',stats)
print('rimas',len(rimas_current),rimas_current[:5])
print('scale summary',scale_summary)
