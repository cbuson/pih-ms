from pathlib import Path
import math, json, hashlib, warnings
from collections import Counter
warnings.filterwarnings('ignore', category=FutureWarning)
import numpy as np, pandas as pd, geopandas as gpd
from shapely.geometry import box, Point
from scipy.spatial import cKDTree
from scipy.stats import spearmanr

OUT=Path(__file__).resolve().parents[1]
BASE=OUT/'docs/data'; EVDIR=BASE/'evidence'; GRIDDIR=OUT/'data/derived/grid_evidence'
SPDIR=OUT/'data/derived/spatial_structure'; WEBSP=BASE/'spatial_structure'; PROV=OUT/'provenance'; METH=OUT/'methodology'
for p in (SPDIR,WEBSP,PROV,METH):p.mkdir(parents=True,exist_ok=True)
CRS=5880; SCALES=[250,500,1000]; CODES=[f'E{i:02d}' for i in range(1,13)]; MICS=[2.5,5.0,10.0]; SUPKM=5.; SUPM=5000.
state=gpd.read_file(BASE/'limite_ms_ibge_2025.geojson').to_crs(CRS); state_geom=state.geometry.union_all(); minx,miny,maxx,maxy=state_geom.bounds
origins={km:(math.floor(minx/(km*1000))*km*1000,math.floor(miny/(km*1000))*km*1000) for km in MICS}
ev={}
for code in CODES: ev[code]=gpd.read_file(next(EVDIR.glob(f'{code}_*.geojson'))).to_crs(CRS)
grids={s:gpd.read_file(GRIDDIR/f'malha_evidencia_{s}km2.geojson').to_crs(CRS) for s in SCALES}

def assign(points,grid,tol=50):
 p=points[['geometry']].copy();p['i']=points.index.astype(int);q=grid[['pih_cell_id','geometry']]
 j=gpd.sjoin(p,q,how='left',predicate='intersects').dropna(subset=['pih_cell_id']).sort_values(['i','pih_cell_id']).drop_duplicates('i')
 d=j.set_index('i')['pih_cell_id'].to_dict(); fb=[]
 for i in [x for x in points.index if int(x) not in d]:
  dist=q.geometry.distance(points.loc[i].geometry); k=dist.idxmin(); dm=float(dist.loc[k])
  if dm<=tol:d[int(i)]=q.loc[k,'pih_cell_id'];fb.append((int(i),q.loc[k,'pih_cell_id'],dm))
 return pd.Series(d),fb

def qnt(v,p):
 a=np.asarray(v,float);a=a[np.isfinite(a)];return float(np.quantile(a,p)) if len(a) else np.nan

def ent(counts):
 a=np.asarray(list(counts),float);a=a[a>0]
 if len(a)<2:return np.nan
 p=a/a.sum();return float(-(p*np.log(p)).sum()/np.log(len(a)))

def tag(km):return '2p5km' if abs(km-2.5)<1e-8 else f'{int(km)}km'
def square(binid,km):
 ix,iy=binid;m=km*1000;ox,oy=origins[km];x=ox+ix*m;y=oy+iy*m;return box(x,y,x+m,y+m)

# E01 global NN and micro bins
e01=ev['E01'].copy();xy=np.c_[e01.geometry.x,e01.geometry.y];tree=cKDTree(xy);dd,_=tree.query(xy,k=2);e01['nn_global_km']=dd[:,1]/1000
for km in MICS:
 m=km*1000;ox,oy=origins[km];e01[f'micro_{tag(km)}']=list(zip(np.floor((e01.geometry.x-ox)/m).astype(int),np.floor((e01.geometry.y-oy)/m).astype(int)))

# fixed 5km support lattice
ox,oy=origins[5.0]; pts=[]; ids=[]
for ix,x in enumerate(np.arange(ox+SUPM/2,maxx+SUPM,SUPM)):
 for iy,y in enumerate(np.arange(oy+SUPM/2,maxy+SUPM,SUPM)):
  p=Point(float(x),float(y))
  if state_geom.covers(p):pts.append(p);ids.append(f'SP5-{ix:04d}-{iy:04d}')
support=gpd.GeoDataFrame({'support_id':ids},geometry=pts,crs=CRS); sxy=np.c_[support.geometry.x,support.geometry.y]
for code,g in ev.items():
 t=cKDTree(np.c_[g.geometry.x,g.geometry.y]);dist,_=t.query(sxy,k=1);support[f'gap_{code}_km']=dist/1000

out_by_scale={}; support_assignment={}; aud=[]
for scale,grid in grids.items():
 ass,fb=assign(e01,grid); e=e01.copy();e['cell']=e.index.map(ass);aud.append({'scale_km2':scale,'n_E01':len(e),'fallback_50m':len(fb),'unassigned':int(e.cell.isna().sum())})
 sj=gpd.sjoin(support[['support_id','geometry']],grid[['pih_cell_id','geometry']],how='left',predicate='intersects').dropna(subset=['pih_cell_id']).sort_values(['support_id','pih_cell_id']).drop_duplicates('support_id'); sc=sj.set_index('support_id')['pih_cell_id'];support_assignment[scale]=sc
 sup=support.copy();sup['cell']=sup.support_id.map(sc);supgrp={c:g for c,g in sup.dropna(subset=['cell']).groupby('cell')}; grp={c:g for c,g in e.dropna(subset=['cell']).groupby('cell')}
 rows=[]
 for _,cell in grid.iterrows():
  cid=cell.pih_cell_id; geom=cell.geometry; area=geom.area/1e6; g=grp.get(cid);n=0 if g is None else len(g)
  r={'pih_cell_id':cid,'scale_km2':scale,'area_effective_km2':area,'n_E01':n,'metric_crs':'EPSG:5880','classification_status':'DESCRIPTIVE_NO_PIH_SCORE'}
  if n:
   r['nn_global_median_km']=qnt(g.nn_global_km,.5);r['nn_global_p90_km']=qnt(g.nn_global_km,.9);xy2=np.c_[g.geometry.x,g.geometry.y];mx,my=xy2.mean(axis=0);cc=geom.centroid;off=math.hypot(mx-cc.x,my-cc.y)/1000;eq=math.sqrt(geom.area/math.pi)/1000;r['mean_center_offset_km']=off;r['mean_center_offset_norm_eqradius']=off/eq
   if n>=2:
    t=cKDTree(xy2);x,_=t.query(xy2,k=2);r['nn_within_median_km']=qnt(x[:,1]/1000,.5);r['nn_within_p90_km']=qnt(x[:,1]/1000,.9)
   else:r['nn_within_median_km']=r['nn_within_p90_km']=np.nan
   if n>=3:
    h=g.geometry.union_all().convex_hull;r['convex_hull_area_ratio']=float(h.area/geom.area) if h.geom_type in ('Polygon','MultiPolygon') else 0.
   else:r['convex_hull_area_ratio']=np.nan
   for km in MICS:
    tg=tag(km);counts=Counter(g[f'micro_{tg}']);covered=sum(geom.intersection(square(b,km)).area for b in counts);k=len(counts)
    r[f'support_units_{tg}_n']=k;r[f'support_area_{tg}_pct']=min(100.,covered/geom.area*100);r[f'redundancy_proxy_{tg}']=1-k/n;r[f'entropy_norm_{tg}']=ent(counts.values());r[f'dominance_{tg}_pct']=max(counts.values())/n*100
  else:
   for k in ['nn_global_median_km','nn_global_p90_km','mean_center_offset_km','mean_center_offset_norm_eqradius','nn_within_median_km','nn_within_p90_km','convex_hull_area_ratio']:r[k]=np.nan
   for km in MICS:
    tg=tag(km);r[f'support_units_{tg}_n']=0;r[f'support_area_{tg}_pct']=0.;r[f'redundancy_proxy_{tg}']=np.nan;r[f'entropy_norm_{tg}']=np.nan;r[f'dominance_{tg}_pct']=np.nan
  sg=supgrp.get(cid)
  if sg is None or len(sg)==0:
   rp=geom.representative_point();pnt=np.array([[rp.x,rp.y]]);r['gap_support_points_n']=0;r['gap_support_fallback']='REPRESENTATIVE_POINT'
   for code,gg in ev.items():
    t=cKDTree(np.c_[gg.geometry.x,gg.geometry.y]);d,_=t.query(pnt,k=1);v=float(d[0]/1000);r[f'gap_{code}_median_km']=v;r[f'gap_{code}_p90_km']=v;r[f'gap_{code}_max_km']=v
  else:
   r['gap_support_points_n']=len(sg);r['gap_support_fallback']='NONE'
   for code in CODES:
    v=sg[f'gap_{code}_km'];r[f'gap_{code}_median_km']=qnt(v,.5);r[f'gap_{code}_p90_km']=qnt(v,.9);r[f'gap_{code}_max_km']=qnt(v,1)
  rows.append(r)
 df=pd.DataFrame(rows); orig=pd.DataFrame(grid.drop(columns='geometry'));keep=['pih_cell_id']+[c for c in orig if ((c.startswith('n_E') and c!='n_E01') or c.startswith('state_E') or c.startswith('pct_E'))];df=df.merge(orig[keep],on='pih_cell_id',how='left');out_by_scale[scale]=df
 df.to_csv(SPDIR/f'spatial_structure_{scale}km2.csv',index=False,encoding='utf-8-sig'); gw=grid[['pih_cell_id','geometry']].merge(df,on='pih_cell_id').to_crs(4326);gw.to_file(WEBSP/f'spatial_structure_{scale}km2.geojson',driver='GeoJSON')
pd.DataFrame(aud).to_csv(SPDIR/'spatial_assignment_audit.csv',index=False,encoding='utf-8-sig')

# scale stability using support lattice
sm={}
for scale,df in out_by_scale.items():
 d=df.set_index('pih_cell_id');x=pd.DataFrame({'support_id':support.support_id});x['cell']=x.support_id.map(support_assignment[scale])
 for code in CODES:
  n=f'n_{code}';x[f'{code}_density100']=x.cell.map((d[n]/d.area_effective_km2*100).to_dict());x[f'{code}_presence']=x.cell.map((d[n]>0).to_dict()).fillna(False).astype(bool)
 sm[scale]=x.set_index('support_id')
rows=[]
for code in CODES:
 for a,b in [(250,500),(250,1000),(500,1000)]:
  x=sm[a][f'{code}_density100'];y=sm[b][f'{code}_density100'];m=x.notna()&y.notna();rho=float(spearmanr(x[m],y[m]).statistic) if m.sum()>2 and x[m].nunique()>1 and y[m].nunique()>1 else np.nan;pa=sm[a][f'{code}_presence'];pb=sm[b][f'{code}_presence'];u=(pa|pb).sum();i=(pa&pb).sum();rows.append({'evidence_code':code,'scale_a_km2':a,'scale_b_km2':b,'support_points_n':len(pa),'spearman_density_per100km2':rho,'presence_jaccard':i/u if u else np.nan,'presence_mismatch_pct':(pa!=pb).mean()*100,'presence_a_pct':pa.mean()*100,'presence_b_pct':pb.mean()*100})
pd.DataFrame(rows).to_csv(SPDIR/'scale_stability_evidence.csv',index=False,encoding='utf-8-sig')

# summaries and support file
sr=[]
for scale,d in out_by_scale.items():
 o=d[d.n_E01>0];sr.append({'scale_km2':scale,'n_cells':len(d),'cells_with_E01':int((d.n_E01>0).sum()),'median_nn_global_km_occupied':o.nn_global_median_km.median(),'median_support_area_2p5km_pct_occupied':o.support_area_2p5km_pct.median(),'median_support_area_5km_pct_occupied':o.support_area_5km_pct.median(),'median_support_area_10km_pct_occupied':o.support_area_10km_pct.median(),'median_redundancy_proxy_5km_occupied':o.redundancy_proxy_5km.median(),'median_entropy_5km_occupied':o.entropy_norm_5km.median(),'median_gap_E01_p90_km_all_cells':d.gap_E01_p90_km.median(),'median_gap_E07_p90_km_all_cells':d.gap_E07_p90_km.median(),'median_gap_E09_p90_km_all_cells':d.gap_E09_p90_km.median(),'median_gap_E10_p90_km_all_cells':d.gap_E10_p90_km.median()})
pd.DataFrame(sr).to_csv(SPDIR/'spatial_structure_scale_summary.csv',index=False,encoding='utf-8-sig')
sup=support.drop(columns='geometry').copy();sup['x_5880']=support.geometry.x;sup['y_5880']=support.geometry.y;sup.to_csv(SPDIR/'support_points_5km.csv',index=False,encoding='utf-8-sig')
# style meta
metrics={'gap_p90':{'label':'Distância P90 à evidência','unit':'km','kind':'gap'},'gap_max':{'label':'Distância máxima à evidência','unit':'km','kind':'gap'},'support_area_5km_pct':{'label':'Cobertura de suporte espacial 5 km · E01','unit':'%','kind':'e01'},'redundancy_proxy_5km':{'label':'Redundância espacial proxy 5 km · E01','unit':'0–1','kind':'e01'},'entropy_norm_5km':{'label':'Entropia espacial normalizada 5 km · E01','unit':'0–1','kind':'e01'},'nn_global_median_km':{'label':'Vizinho mais próximo mediano · E01','unit':'km','kind':'e01'}};sty={}
for scale,d in out_by_scale.items():
 sty[str(scale)]={}
 for key,md in metrics.items():
  if md['kind']=='gap':
   sty[str(scale)][key]={}
   for code in CODES:
    c=f'gap_{code}_{"p90_km" if key=="gap_p90" else "max_km"}';v=d[c].dropna();sty[str(scale)][key][code]={'quantiles':[float(v.quantile(x)) for x in [.2,.4,.6,.8]],'min':float(v.min()),'max':float(v.max())}
  else:
   v=d[key].dropna();sty[str(scale)][key]={'quantiles':[float(v.quantile(x)) for x in [.2,.4,.6,.8]],'min':float(v.min()) if len(v) else None,'max':float(v.max()) if len(v) else None}
(WEBSP/'spatial_structure_style_metadata.json').write_text(json.dumps({'metrics':metrics,'scales':sty},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'support_points':len(support),'summary':sr},ensure_ascii=False,indent=2))
