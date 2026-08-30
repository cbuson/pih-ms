from pathlib import Path
import csv,json,math
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

OUT=Path('/mnt/data/pih-ms-v1.8-estratificacao-hidrogeologica')
RES=OUT/'data/derived/stratified_scale'; DOC=OUT/'docs/data/stratified_scale'
CRS=5880; SCALES=[100,150,250,500,1000]; ECODES=['E01','E07','E09','E10']

def write_csv(path,df): Path(path).parent.mkdir(parents=True,exist_ok=True); df.to_csv(path,index=False,encoding='utf-8-sig')
def P(a,b): return np.where(b>0,100*a/b,np.nan)

# inputs
hydro=gpd.read_file(OUT/'docs/data/hidrogeologia_sgb_2024.geojson').to_crs(CRS)[['NOM_UE_AFL','geometry']].rename(columns={'NOM_UE_AFL':'unit'})
domain=gpd.read_file(OUT/'docs/data/dominio_hidrolitologico_sgb_2024.geojson').to_crs(CRS)[['U_HL_AFL','geometry']].rename(columns={'U_HL_AFL':'domain'})
unit_area=(hydro.assign(area_km2=hydro.area/1e6).groupby('unit',as_index=False).area_km2.sum()); units=sorted(unit_area.unit.dropna()); unit_area_map=dict(zip(unit_area.unit,unit_area.area_km2))
dom_area=(domain.assign(area_km2=domain.area/1e6).groupby('domain',as_index=False).area_km2.sum()); domains=sorted(dom_area.domain.dropna()); dom_area_map=dict(zip(dom_area.domain,dom_area.area_km2))

w=pd.read_csv(OUT/'data/source_audit/wells_master.csv',dtype=str,encoding='utf-8-sig').fillna('')
wg=gpd.GeoDataFrame(w[['well_id','sgb2024_unit_aflorante']].rename(columns={'sgb2024_unit_aflorante':'unit'}),geometry=gpd.points_from_xy(w.longitude.astype(float),w.latitude.astype(float)),crs=4326).to_crs(CRS)
# domain assign wells
wj=gpd.sjoin(wg[['well_id','geometry']],domain,how='left',predicate='intersects')
wdom=wj.groupby('well_id').domain.agg(lambda x: sorted(set(x.dropna().astype(str))))
wdom=wdom.map(lambda x:x[0] if len(x)==1 else ('AMBIGUOUS_BOUNDARY' if len(x)>1 else 'UNKNOWN'))
wg['domain']=wg.well_id.map(wdom).fillna('UNKNOWN')

# evidence sets
sets={}
for code in ECODES:
 p=next((OUT/'data/derived/evidence').glob(f'{code}_*.csv')); sets[code]=set(pd.read_csv(p,dtype=str,encoding='utf-8-sig').well_id.astype(str))

# support assignment existing
spa=pd.read_csv(RES/'support_strata_assignment.csv',dtype=str,encoding='utf-8-sig')
spg=gpd.GeoDataFrame(spa[['support_id','unit','domain']],geometry=gpd.points_from_xy(spa.x_5880.astype(float),spa.y_5880.astype(float)),crs=CRS)

unit_out=[]; dom_out=[]; scale_out=[]
for scale in SCALES:
 print('scale',scale,flush=True)
 grid=gpd.read_file(OUT/f'docs/data/scale_study/scale_primary_{scale}km2.geojson').to_crs(CRS)[['cell_id','geometry']]
 grid['cell_area_km2']=grid.area/1e6
 # exact composition
 hu=gpd.overlay(grid[['cell_id','geometry']],hydro,how='intersection',keep_geom_type=False); hu['int_area_km2']=hu.area/1e6
 hd=gpd.overlay(grid[['cell_id','geometry']],domain,how='intersection',keep_geom_type=False); hd['int_area_km2']=hd.area/1e6
 # cell composition summaries
 hu_sum=hu.groupby(['cell_id','unit'],as_index=False).int_area_km2.sum(); hd_sum=hd.groupby(['cell_id','domain'],as_index=False).int_area_km2.sum()
 hu_cell_total=hu_sum.groupby('cell_id').int_area_km2.sum().rename('cell_hydro_area'); hd_cell_total=hd_sum.groupby('cell_id').int_area_km2.sum().rename('cell_domain_area')
 hu_sum=hu_sum.merge(hu_cell_total,on='cell_id'); hu_sum['frac_pct']=100*hu_sum.int_area_km2/hu_sum.cell_hydro_area
 hd_sum=hd_sum.merge(hd_cell_total,on='cell_id'); hd_sum['frac_pct']=100*hd_sum.int_area_km2/hd_sum.cell_domain_area
 hu_n=hu_sum.groupby('cell_id').unit.nunique().rename('units_n'); hd_n=hd_sum.groupby('cell_id').domain.nunique().rename('domains_n')
 hu_dom=hu_sum.loc[hu_sum.groupby('cell_id').int_area_km2.idxmax(),['cell_id','unit','frac_pct']].rename(columns={'unit':'dominant_unit','frac_pct':'dominant_unit_pct'})
 hd_dom=hd_sum.loc[hd_sum.groupby('cell_id').int_area_km2.idxmax(),['cell_id','domain','frac_pct']].rename(columns={'domain':'dominant_domain','frac_pct':'dominant_domain_pct'})
 cell_comp=grid[['cell_id']].merge(hu_n,on='cell_id',how='left').merge(hu_dom,on='cell_id',how='left').merge(hd_n,on='cell_id',how='left').merge(hd_dom,on='cell_id',how='left').fillna({'units_n':0,'domains_n':0})
 # exact per unit mix metrics
 hux=hu_sum.merge(hu_n,on='cell_id').merge(hu_dom,on='cell_id'); hux['mixed_area']=np.where(hux.units_n>1,hux.int_area_km2,0); hux['nondom_area']=np.where(hux.unit!=hux.dominant_unit,hux.int_area_km2,0); hux['purity_weighted_num']=hux.int_area_km2*hux.frac_pct
 um=hux.groupby('unit').agg(unit_area_in_grid=('int_area_km2','sum'),mixed_area=('mixed_area','sum'),nondom_area=('nondom_area','sum'),purity_num=('purity_weighted_num','sum'),cells_intersecting=('cell_id','nunique')).reset_index()
 domcells=hu_dom.rename(columns={'dominant_unit':'unit'}).groupby('unit').cell_id.nunique().rename('cells_dominant').reset_index(); um=um.merge(domcells,on='unit',how='left').fillna({'cells_dominant':0}); um['mixed_pct']=100*um.mixed_area/um.unit_area_in_grid; um['nondom_pct']=100*um.nondom_area/um.unit_area_in_grid; um['weighted_purity_pct']=um.purity_num/um.unit_area_in_grid
 hdx=hd_sum.merge(hd_n,on='cell_id').merge(hd_dom,on='cell_id'); hdx['mixed_area']=np.where(hdx.domains_n>1,hdx.int_area_km2,0); hdx['nondom_area']=np.where(hdx.domain!=hdx.dominant_domain,hdx.int_area_km2,0); hdx['purity_weighted_num']=hdx.int_area_km2*hdx.frac_pct
 dm=hdx.groupby('domain').agg(domain_area_in_grid=('int_area_km2','sum'),mixed_area=('mixed_area','sum'),nondom_area=('nondom_area','sum'),purity_num=('purity_weighted_num','sum'),cells_intersecting=('cell_id','nunique')).reset_index()
 domdcells=hd_dom.rename(columns={'dominant_domain':'domain'}).groupby('domain').cell_id.nunique().rename('cells_dominant').reset_index(); dm=dm.merge(domdcells,on='domain',how='left').fillna({'cells_dominant':0}); dm['mixed_pct']=100*dm.mixed_area/dm.domain_area_in_grid; dm['nondom_pct']=100*dm.nondom_area/dm.domain_area_in_grid; dm['weighted_purity_pct']=dm.purity_num/dm.domain_area_in_grid
 # assign support to cell
 sj=gpd.sjoin(spg,grid[['cell_id','geometry']],how='left',predicate='intersects')[['support_id','unit','domain','cell_id']]
 # boundary duplicates deterministic
 sj=sj.sort_values(['support_id','cell_id']).drop_duplicates('support_id',keep='first')
 # wells to cell
 gj=gpd.sjoin(wg[['well_id','unit','domain','geometry']],grid[['cell_id','geometry']],how='left',predicate='intersects')[['well_id','unit','domain','cell_id']]
 gj=gj.sort_values(['well_id','cell_id']).drop_duplicates('well_id',keep='first')
 # count tables and attach flags to support
 support=sj.copy()
 counts_cell={}; counts_unit={}; counts_dom={}
 for code in ECODES:
  e=gj[gj.well_id.isin(sets[code]) & gj.cell_id.notna()].copy()
  cc=e.groupby('cell_id').size().rename(f'{code}_total').reset_index(); counts_cell[code]=cc
  cu=e.groupby(['cell_id','unit']).size().rename(f'{code}_same_unit').reset_index(); counts_unit[code]=cu
  cd=e.groupby(['cell_id','domain']).size().rename(f'{code}_same_domain').reset_index(); counts_dom[code]=cd
  support=support.merge(cc,on='cell_id',how='left').merge(cu,on=['cell_id','unit'],how='left').merge(cd,on=['cell_id','domain'],how='left')
  for c in [f'{code}_total',f'{code}_same_unit',f'{code}_same_domain']: support[c]=support[c].fillna(0).astype(int)
  support[f'{code}_unit_has']=(support[f'{code}_same_unit']>0).astype(int); support[f'{code}_domain_has']=(support[f'{code}_same_domain']>0).astype(int); support[f'{code}_apparent']=(support[f'{code}_total']>0).astype(int); support[f'{code}_unit_mask']=((support[f'{code}_total']>0)&(support[f'{code}_same_unit']==0)).astype(int); support[f'{code}_domain_mask']=((support[f'{code}_total']>0)&(support[f'{code}_same_domain']==0)).astype(int)
 # unit rows
 for u in units:
  su=support[support.unit==u]; mix=um[um.unit==u]
  base={'scale_km2':scale,'unit':u,'unit_area_km2':unit_area_map[u],'support_points_n':len(su)}
  if len(mix):
   m=mix.iloc[0]; base.update({'cells_intersecting_unit':int(m.cells_intersecting),'cells_where_unit_dominant':int(m.cells_dominant),'unit_area_in_mixed_cells_pct':m.mixed_pct,'unit_area_in_non_dominant_cells_pct':m.nondom_pct,'unit_area_weighted_cell_purity_pct':m.weighted_purity_pct})
  else: base.update({'cells_intersecting_unit':0,'cells_where_unit_dominant':0,'unit_area_in_mixed_cells_pct':None,'unit_area_in_non_dominant_cells_pct':None,'unit_area_weighted_cell_purity_pct':None})
  for code in ECODES:
   apparent=su[f'{code}_apparent'].sum(); base[f'{code}_same_unit_support_coverage_pct']=100*su[f'{code}_unit_has'].mean() if len(su) else None; base[f'{code}_apparent_total_support_coverage_pct']=100*su[f'{code}_apparent'].mean() if len(su) else None; base[f'{code}_cross_unit_masking_pct']=100*su[f'{code}_unit_mask'].mean() if len(su) else None; base[f'{code}_masking_share_of_apparent_pct']=100*su[f'{code}_unit_mask'].sum()/apparent if apparent else None
  unit_out.append(base)
 # domain rows
 for d in domains:
  sd=support[support.domain==d]; mix=dm[dm.domain==d]
  base={'scale_km2':scale,'domain':d,'domain_area_km2':dom_area_map[d],'support_points_n':len(sd)}
  if len(mix):
   m=mix.iloc[0]; base.update({'cells_intersecting_domain':int(m.cells_intersecting),'cells_where_domain_dominant':int(m.cells_dominant),'domain_area_in_mixed_cells_pct':m.mixed_pct,'domain_area_in_non_dominant_cells_pct':m.nondom_pct,'domain_area_weighted_cell_purity_pct':m.weighted_purity_pct})
  else: base.update({'cells_intersecting_domain':0,'cells_where_domain_dominant':0,'domain_area_in_mixed_cells_pct':None,'domain_area_in_non_dominant_cells_pct':None,'domain_area_weighted_cell_purity_pct':None})
  for code in ECODES:
   apparent=sd[f'{code}_apparent'].sum(); base[f'{code}_same_domain_support_coverage_pct']=100*sd[f'{code}_domain_has'].mean() if len(sd) else None; base[f'{code}_apparent_total_support_coverage_pct']=100*sd[f'{code}_apparent'].mean() if len(sd) else None; base[f'{code}_cross_domain_masking_pct']=100*sd[f'{code}_domain_mask'].mean() if len(sd) else None; base[f'{code}_masking_share_of_apparent_pct']=100*sd[f'{code}_domain_mask'].sum()/apparent if apparent else None
  dom_out.append(base)
 # overall summary
 state_area=grid.area.sum()/1e6
 mixed_unit_cells=set(hu_n[hu_n>1].index); mixed_dom_cells=set(hd_n[hd_n>1].index)
 mixed_unit_area=sum(grid.set_index('cell_id').loc[list(mixed_unit_cells)].area/1e6) if mixed_unit_cells else 0
 mixed_dom_area=sum(grid.set_index('cell_id').loc[list(mixed_dom_cells)].area/1e6) if mixed_dom_cells else 0
 ss={'scale_km2':scale,'grid_cells_n':len(grid),'support_points_n':len(support),'state_area_in_unit_mixed_cells_pct':100*mixed_unit_area/state_area,'state_area_in_domain_mixed_cells_pct':100*mixed_dom_area/state_area}
 for code in ECODES:
  validu=support[support.unit.isin(units)]; validd=support[support.domain.isin(domains)]; ss[f'{code}_same_unit_support_coverage_pct']=100*validu[f'{code}_unit_has'].mean(); ss[f'{code}_cross_unit_masking_pct']=100*validu[f'{code}_unit_mask'].mean(); ss[f'{code}_same_domain_support_coverage_pct']=100*validd[f'{code}_domain_has'].mean(); ss[f'{code}_cross_domain_masking_pct']=100*validd[f'{code}_domain_mask'].mean()
 scale_out.append(ss)
 # UI geojson enrich
 cellcomp=cell_comp.copy()
 for code in ECODES:
  cellcomp=cellcomp.merge(counts_cell[code],on='cell_id',how='left')
  # same dominant unit/domain counts via merge long counts
  cu=counts_unit[code].merge(hu_dom,on='cell_id',how='left'); cu=cu[cu.unit==cu.dominant_unit][['cell_id',f'{code}_same_unit']].rename(columns={f'{code}_same_unit':f'{code}_dominant_unit_n'})
  cd=counts_dom[code].merge(hd_dom,on='cell_id',how='left'); cd=cd[cd.domain==cd.dominant_domain][['cell_id',f'{code}_same_domain']].rename(columns={f'{code}_same_domain':f'{code}_dominant_domain_n'})
  cellcomp=cellcomp.merge(cu,on='cell_id',how='left').merge(cd,on='cell_id',how='left')
  for c in [f'{code}_total',f'{code}_dominant_unit_n',f'{code}_dominant_domain_n']: cellcomp[c]=cellcomp[c].fillna(0).astype(int)
  cellcomp[f'{code}_dominant_unit_masked']=((cellcomp[f'{code}_total']>0)&(cellcomp[f'{code}_dominant_unit_n']==0))
  cellcomp[f'{code}_dominant_domain_masked']=((cellcomp[f'{code}_total']>0)&(cellcomp[f'{code}_dominant_domain_n']==0))
 src=json.load(open(OUT/f'docs/data/scale_study/scale_primary_{scale}km2.geojson',encoding='utf-8')); mp=cellcomp.set_index('cell_id').to_dict(orient='index')
 for feat in src['features']:
  p=feat['properties']; p.update(mp.get(p['cell_id'],{}))
 json.dump(src,open(DOC/f'stratified_scale_{scale}km2.geojson','w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))

write_csv(RES/'scale_by_hydro_unit.csv',pd.DataFrame(unit_out)); write_csv(RES/'scale_by_hydrolithologic_domain.csv',pd.DataFrame(dom_out)); write_csv(RES/'stratified_scale_summary.csv',pd.DataFrame(scale_out))
meta={'version':'V1.8','date_cutoff':'2026-08-29','crs_metric':'EPSG:5880','scales_km2':SCALES,'evidence_codes':ECODES,'official_hydro_units_n':len(units),'official_domains_n':len(domains),'support_points_n':len(spg),'method_notes':['Composição das células calculada por interseção vetorial exata em EPSG:5880.','Cobertura e mascaramento avaliados em 14.284 pontos fixos de suporte de 5 km.','Evidência em outra unidade não é tratada como evidência do estrato local.','Nenhuma escala foi selecionada e nenhum score PIH foi calculado.']}
json.dump(meta,open(RES/'stratified_scale_metadata.json','w',encoding='utf-8'),ensure_ascii=False,indent=2); json.dump(meta,open(DOC/'stratified_scale_metadata.json','w',encoding='utf-8'),ensure_ascii=False,indent=2)
print(pd.DataFrame(scale_out).to_string(index=False))
