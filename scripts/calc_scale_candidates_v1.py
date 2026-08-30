from pathlib import Path
import math, json, warnings
from itertools import combinations
warnings.filterwarnings('ignore', category=FutureWarning)
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
from scipy.stats import spearmanr

ROOT=Path(__file__).resolve().parents[1]
DER=ROOT/'data/derived/scale_study'
WEB=ROOT/'docs/data/scale_study'
DER.mkdir(parents=True,exist_ok=True);WEB.mkdir(parents=True,exist_ok=True)
CRS='EPSG:5880';SCALES=[100,150,250,500,1000];CODES=[f'E{i:02d}' for i in range(1,13)];MAUP_CODES=['E01','E07','E09','E10'];VARIANTS=[('O00',0.0,0.0),('OX25',0.25,0.0),('OY25',0.0,0.25),('OXY25',0.25,0.25)]
state=gpd.read_file(ROOT/'docs/data/limite_ms_ibge_2025.geojson').to_crs(CRS);state_geom=state.geometry.union_all();minx,miny,maxx,maxy=state_geom.bounds
hydro=gpd.read_file(ROOT/'docs/data/hidrogeologia_sgb_2024.geojson').to_crs(CRS)
ev={code:gpd.read_file(next((ROOT/'data/derived/evidence').glob(f'{code}_*.geojson'))).to_crs(CRS).reset_index(drop=True) for code in CODES}
sdf=pd.read_csv(ROOT/'data/derived/spatial_structure/support_points_5km.csv');support=gpd.GeoDataFrame(sdf,geometry=gpd.points_from_xy(sdf.x_5880,sdf.y_5880),crs=CRS).reset_index(drop=True)
# Classificação hidrogeológica do suporte fixo. É proxy pontual, não fração de área.
hp=hydro.sindex.query(support.geometry,predicate='within');hu=np.full(len(support),None,dtype=object);hc=np.full(len(support),None,dtype=object)
if hp.size:
 order=np.lexsort((hp[1],hp[0]));a=hp[0][order];b=hp[1][order];first=np.r_[True,a[1:]!=a[:-1]]
 for pi,hi in zip(a[first],b[first]):hu[pi]=hydro.iloc[hi].NOM_UE_AFL;hc[pi]=hydro.iloc[hi].CLS_STYLE
support['hydro_unit']=hu;support['hydro_class']=hc

def make_hex(cx,cy,s):return Polygon([(cx+s*math.cos(math.radians(30+60*k)),cy+s*math.sin(math.radians(30+60*k))) for k in range(6)])
def params(area):A=area*1e6;s=math.sqrt(2*A/(3*math.sqrt(3)));return s,math.sqrt(3)*s,2*s,1.5*s
def build_grid(area,name,fx,fy,clip=True):
 s,w,h,v=params(area);bx=math.floor((minx-w)/w)*w+fx*w;by=math.floor((miny-h)/v)*v+fy*v;geoms=[];ids=[];y=by;row=0
 while y<=maxy+h:
  x=bx+(row%2)*w/2
  while x<=maxx+w:
   hh=make_hex(x,y,s)
   if hh.intersects(state_geom):
    q=hh.intersection(state_geom) if clip else hh
    if not q.is_empty and q.area>1:ids.append(f'SCALE-{area}-{name}-{len(ids)+1:05d}');geoms.append(q)
   x+=w
  y+=v;row+=1
 g=gpd.GeoDataFrame({'cell_id':ids,'scale_km2':area,'variant':name},geometry=geoms,crs=CRS).reset_index(drop=True);g['area_effective_km2']=g.geometry.area/1e6;g['area_effective_pct_nominal']=g.area_effective_km2/area*100;return g

def assign_idx(points,grid):
 out=np.full(len(points),-1,dtype=int);pairs=grid.sindex.query(points.geometry,predicate='within')
 if pairs.size:
  order=np.lexsort((pairs[1],pairs[0]));a=pairs[0][order];b=pairs[1][order];first=np.r_[True,a[1:]!=a[:-1]];out[a[first]]=b[first]
 miss=np.where(out<0)[0]
 if len(miss):
  pairs=grid.sindex.query(points.iloc[miss].geometry,predicate='intersects')
  if pairs.size:
   order=np.lexsort((pairs[1],pairs[0]));a=pairs[0][order];b=pairs[1][order];first=np.r_[True,a[1:]!=a[:-1]];out[miss[a[first]]]=b[first]
 return out

def entropy(vals):
 c=pd.Series(vals).dropna().value_counts()
 if len(c)<2:return np.nan
 p=c/c.sum();return float(-(p*np.log(p)).sum()/np.log(len(p)))
def q(v,p):
 a=pd.to_numeric(pd.Series(v),errors='coerce').dropna();return float(a.quantile(p)) if len(a) else np.nan

primary={};support_maps={};sumrows=[]
for scale in SCALES:
 g=build_grid(scale,'O00',0,0,clip=True)
 for code in CODES:
  ix=assign_idx(ev[code],g);cnt=np.bincount(ix[ix>=0],minlength=len(g));g[f'n_{code}']=cnt
 six=assign_idx(support,g);support_maps[scale]=six;sg=support.copy();sg['cell_idx']=six;sg=sg[sg.cell_idx>=0]
 for code in MAUP_CODES:
  grp=sg.groupby('cell_idx')[f'gap_{code}_km'];g[f'gap_{code}_median_km']=g.index.to_series().map(grp.median());g[f'gap_{code}_p90_km']=g.index.to_series().map(grp.quantile(.9))
 hs=[]
 for ci,x in sg.groupby('cell_idx'):
  u=x.hydro_unit.dropna();c=x.hydro_class.dropna();vc=u.value_counts();hs.append({'cell_idx':ci,'hydro_support_points_n':len(x),'hydro_support_units_n':int(u.nunique()),'hydro_support_dominant_pct':float(vc.iloc[0]/vc.sum()*100) if len(vc) else np.nan,'hydro_support_entropy':entropy(u),'hydro_support_classes_n':int(c.nunique())})
 g=g.merge(pd.DataFrame(hs),left_index=True,right_on='cell_idx',how='left').sort_values('cell_idx').reset_index(drop=True);g.drop(columns=['cell_idx'],inplace=True)
 for c in ['hydro_support_points_n','hydro_support_units_n','hydro_support_classes_n']:g[c]=g[c].fillna(0).astype(int)
 occ=g[g.n_E01>0];s,w,h,v=params(scale)
 sumrows.append({'scale_km2':scale,'n_cells':len(g),'hex_side_km':s/1000,'hex_width_km':w/1000,'hex_height_km':h/1000,'E01_empty_cells_pct':float((g.n_E01==0).mean()*100),'E01_occupied_cells_pct':float((g.n_E01>0).mean()*100),'median_E01_count_occupied':float(occ.n_E01.median()),'p90_E01_count_occupied':q(occ.n_E01,.9),'max_E01_count':int(g.n_E01.max()),'E07_occupied_cells_pct':float((g.n_E07>0).mean()*100),'E09_occupied_cells_pct':float((g.n_E09>0).mean()*100),'E10_occupied_cells_pct':float((g.n_E10>0).mean()*100),'median_gap_E01_p90_km':float(g.gap_E01_p90_km.median()),'median_gap_E07_p90_km':float(g.gap_E07_p90_km.median()),'median_gap_E09_p90_km':float(g.gap_E09_p90_km.median()),'median_gap_E10_p90_km':float(g.gap_E10_p90_km.median()),'median_hydro_support_units':float(g.hydro_support_units_n.median()),'pct_cells_hydro_support_mixed':float((g.hydro_support_units_n>1).mean()*100),'median_hydro_support_dominant_pct':float(g.hydro_support_dominant_pct.median(skipna=True)),'median_hydro_support_entropy':float(g.hydro_support_entropy.median(skipna=True)),'edge_cells_lt50pct_nominal':int((g.area_effective_pct_nominal<50).sum())})
 g.drop(columns='geometry').to_csv(DER/f'scale_primary_{scale}km2.csv',index=False,encoding='utf-8-sig');g.to_crs(4326).to_file(WEB/f'scale_primary_{scale}km2.geojson',driver='GeoJSON');primary[scale]=g
pd.DataFrame(sumrows).to_csv(DER/'scale_candidate_summary.csv',index=False,encoding='utf-8-sig')
# Cross-scale O00 on same support points
rows=[]
for code in CODES:
 for a,b in combinations(SCALES,2):
  ga=primary[a];gb=primary[b];ia=support_maps[a];ib=support_maps[b];ca=np.where(ia>=0,ga[f'n_{code}'].to_numpy()[np.maximum(ia,0)],0);cb=np.where(ib>=0,gb[f'n_{code}'].to_numpy()[np.maximum(ib,0)],0);pa=ca>0;pb=cb>0;u=(pa|pb).sum();inter=(pa&pb).sum();da=np.where(ia>=0,(ga[f'n_{code}']/ga.area_effective_km2*100).to_numpy()[np.maximum(ia,0)],0);db=np.where(ib>=0,(gb[f'n_{code}']/gb.area_effective_km2*100).to_numpy()[np.maximum(ib,0)],0);rho=float(spearmanr(da,db).statistic) if np.std(da)>0 and np.std(db)>0 else np.nan;rows.append({'evidence_code':code,'scale_a_km2':a,'scale_b_km2':b,'presence_jaccard':inter/u if u else 1.0,'presence_mismatch_pct':float((pa!=pb).mean()*100),'presence_a_pct':float(pa.mean()*100),'presence_b_pct':float(pb.mean()*100),'spearman_density_per100km2':rho})
pd.DataFrame(rows).to_csv(DER/'scale_candidate_cross_scale_stability.csv',index=False,encoding='utf-8-sig')
# Origin sensitivity on full regular hexagons, restricted to cells intersecting MS
vr=[];arrays={}
for scale in SCALES:
 for name,fx,fy in VARIANTS:
  g=build_grid(scale,name,fx,fy,clip=False)
  for code in MAUP_CODES:
   ix=assign_idx(ev[code],g);cnt=np.bincount(ix[ix>=0],minlength=len(g));g[f'n_{code}']=cnt;v=cnt[cnt>0];vr.append({'scale_km2':scale,'variant':name,'evidence_code':code,'n_cells':len(g),'occupied_cells':int((cnt>0).sum()),'occupied_pct':float((cnt>0).mean()*100),'median_count_occupied':float(np.median(v)) if len(v) else np.nan,'max_count':int(cnt.max())})
  six=assign_idx(support,g)
  for code in MAUP_CODES: arrays[(scale,name,code)]=np.where(six>=0,g[f'n_{code}'].to_numpy()[np.maximum(six,0)],0).astype(float)
vr=pd.DataFrame(vr);vr.to_csv(DER/'scale_candidate_origin_variants.csv',index=False,encoding='utf-8-sig')
conc=[];sens=[]
for scale in SCALES:
 for code in MAUP_CODES:
  sub=vr[(vr.scale_km2==scale)&(vr.evidence_code==code)];pairs=[]
  for va,vb in combinations([x[0] for x in VARIANTS],2):
   a=arrays[(scale,va,code)];b=arrays[(scale,vb,code)];pa=a>0;pb=b>0;u=(pa|pb).sum();inter=(pa&pb).sum();rho=float(spearmanr(a,b).statistic) if np.std(a)>0 and np.std(b)>0 else np.nan;rec={'scale_km2':scale,'evidence_code':code,'variant_a':va,'variant_b':vb,'presence_jaccard':inter/u if u else 1.0,'presence_mismatch_pct':float((pa!=pb).mean()*100),'spearman_counts_support':rho,'presence_a_pct':float(pa.mean()*100),'presence_b_pct':float(pb.mean()*100)};conc.append(rec);pairs.append(rec)
  p=pd.DataFrame(pairs);sens.append({'scale_km2':scale,'evidence_code':code,'occupied_pct_min':float(sub.occupied_pct.min()),'occupied_pct_max':float(sub.occupied_pct.max()),'occupied_pct_range':float(sub.occupied_pct.max()-sub.occupied_pct.min()),'presence_jaccard_min':float(p.presence_jaccard.min()),'presence_jaccard_median':float(p.presence_jaccard.median()),'presence_mismatch_pct_max':float(p.presence_mismatch_pct.max()),'spearman_counts_min':float(p.spearman_counts_support.min()),'spearman_counts_median':float(p.spearman_counts_support.median())})
pd.DataFrame(conc).to_csv(DER/'scale_candidate_origin_concordance.csv',index=False,encoding='utf-8-sig');sens=pd.DataFrame(sens);sens.to_csv(DER/'scale_candidate_origin_sensitivity.csv',index=False,encoding='utf-8-sig')
# Decision matrix, without score
summary=pd.read_csv(DER/'scale_candidate_summary.csv')
for code in MAUP_CODES:
 x=sens[sens.evidence_code==code].set_index('scale_km2');summary[f'{code}_origin_jaccard_min']=summary.scale_km2.map(x.presence_jaccard_min);summary[f'{code}_origin_mismatch_max_pct']=summary.scale_km2.map(x.presence_mismatch_pct_max)
summary['selection_status']='CANDIDATA_NAO_ADOTADA';summary.to_csv(DER/'scale_candidate_decision_matrix.csv',index=False,encoding='utf-8-sig')
print(summary.to_string(index=False))

# Metadados de estilo e leitura final do visor
labels={100:'RESOLUÇÃO ALTA · ESPARSIDADE MUITO ALTA',150:'RESOLUÇÃO ALTA · ESPARSIDADE ALTA',250:'COMPROMISSO INTERMEDIÁRIO EM TESTE',500:'AGREGAÇÃO ALTA · MAIOR MISTURA HIDROGEOLÓGICA',1000:'AGREGAÇÃO MUITO ALTA · MAIOR RISCO DE MASCARAR VAZIOS'}
dec=pd.read_csv(DER/'scale_candidate_decision_matrix.csv')
dec['descriptive_tradeoff']=dec.scale_km2.map(labels)
dec['selection_status']='CANDIDATA_NAO_ADOTADA'
dec.to_csv(DER/'scale_candidate_decision_matrix.csv',index=False,encoding='utf-8-sig')
metrics={'n_E01':{'label':'Contagem E01 · poços canônicos','unit':'registros','palette':'blue'},'n_E07':{'label':'Contagem E07 · ensaios cadastrados','unit':'registros','palette':'blue'},'n_E09':{'label':'Contagem E09 · transmissividade informada','unit':'registros','palette':'blue'},'n_E10':{'label':'Contagem E10 · hidroquímica parcial','unit':'registros','palette':'blue'},'hydro_support_units_n':{'label':'Unidades hidrogeológicas no suporte fixo 5 km','unit':'unidades','palette':'purple'},'hydro_support_dominant_pct':{'label':'Dominância hidrogeológica no suporte fixo 5 km','unit':'%','palette':'purple'},'gap_E01_p90_km':{'label':'Distância P90 à E01','unit':'km','palette':'blue'},'gap_E07_p90_km':{'label':'Distância P90 à E07','unit':'km','palette':'blue'},'gap_E09_p90_km':{'label':'Distância P90 à E09','unit':'km','palette':'blue'},'gap_E10_p90_km':{'label':'Distância P90 à E10','unit':'km','palette':'blue'}}
style={'metrics':metrics,'scales':{}}
for scale in SCALES:
    d=pd.read_csv(DER/f'scale_primary_{scale}km2.csv');style['scales'][str(scale)]={}
    for k in metrics:
        v=pd.to_numeric(d[k],errors='coerce').dropna();style['scales'][str(scale)][k]={'min':float(v.min()) if len(v) else None,'max':float(v.max()) if len(v) else None,'quantiles':[float(v.quantile(x)) for x in [.2,.4,.6,.8]] if len(v) else []}
(WEB/'scale_candidate_style_metadata.json').write_text(json.dumps(style,ensure_ascii=False,indent=2),encoding='utf-8')
(DER/'scale_candidate_style_metadata.json').write_text(json.dumps(style,ensure_ascii=False,indent=2),encoding='utf-8')
