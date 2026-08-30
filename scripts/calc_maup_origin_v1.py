from pathlib import Path
import math, json
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Polygon, Point
from shapely.strtree import STRtree
from scipy.stats import spearmanr

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/derived/spatial_structure'
OUT.mkdir(parents=True, exist_ok=True)
CRS_METRIC='EPSG:5880'

state=gpd.read_file(ROOT/'docs/data/limite_ms_ibge_2025.geojson').to_crs(CRS_METRIC)
state_geom=state.geometry.union_all()
minx,miny,maxx,maxy=state_geom.bounds

evs={}
for code in ['E01','E07','E09','E10']:
    p=next((ROOT/'data/derived/evidence').glob(f'{code}_*.geojson'))
    g=gpd.read_file(p).to_crs(CRS_METRIC)
    evs[code]=g

variants=[('O00',0.0,0.0),('OX25',0.25,0.0),('OY25',0.0,0.25),('OXY25',0.25,0.25)]
scales=[250,500,1000]
metadata=[]
summary=[]
presence_maps={}

# Pointy top hex centered at cx,cy, vertices at angles 30,90,... produces pointy vertical? same area either way.
def make_hex(cx,cy,s):
    pts=[]
    # pointy top orientation vertices angle 30 deg gives flat? orientation not critical to area but spacing formula must match
    for k in range(6):
        a=math.radians(30+60*k)
        pts.append((cx+s*math.cos(a),cy+s*math.sin(a)))
    return Polygon(pts)

# For this vertex orientation, width = sqrt(3)s, height=2s, horizontal spacing=sqrt(3)s, vertical spacing=1.5s, alternating x half-width.
for area_km2 in scales:
    A=area_km2*1_000_000.0
    s=math.sqrt(2*A/(3*math.sqrt(3)))
    width=math.sqrt(3)*s
    vspace=1.5*s
    for var,fx,fy in variants:
        xshift=fx*width
        yshift=fy*vspace
        # align origin deterministically to global coordinate multiples so shifts relative only
        base_x=math.floor((minx-width)/width)*width + xshift
        base_y=math.floor((miny-2*s)/vspace)*vspace + yshift
        geoms=[]; ids=[]; centers=[]
        row=0; y=base_y
        while y <= maxy+2*s:
            xoff=(row%2)*width/2
            x=base_x+xoff
            col=0
            while x <= maxx+width:
                h=make_hex(x,y,s)
                if h.intersects(state_geom):
                    inter=h.intersection(state_geom)
                    if not inter.is_empty and inter.area>1.0:
                        geoms.append(inter); ids.append(f'MAUP-{area_km2}-{var}-{len(ids)+1:04d}'); centers.append((x,y))
                x+=width; col+=1
            y+=vspace; row+=1
        grid=gpd.GeoDataFrame({'cell_id':ids},geometry=geoms,crs=CRS_METRIC)
        # counts by spatial join within/intersects, boundary points can double under intersects. Use within and fallback nearest uniquely
        counts_by_ev={}
        pres_by_ev={}
        for code,g in evs.items():
            join=gpd.sjoin(g[['geometry']], grid[['cell_id','geometry']], how='left', predicate='within')
            # any unassigned boundary point use intersects, choose first sorted cell id
            miss=join['cell_id'].isna()
            if miss.any():
                sub=g.loc[join.index[miss],['geometry']]
                ji=gpd.sjoin(sub,grid[['cell_id','geometry']],how='left',predicate='intersects')
                mapfirst=ji.dropna(subset=['cell_id']).sort_values('cell_id').groupby(level=0)['cell_id'].first()
                join.loc[miss,'cell_id']=join.index[miss].map(mapfirst)
            cnt=join.dropna(subset=['cell_id']).groupby('cell_id').size()
            arr=grid['cell_id'].map(cnt).fillna(0).astype(int).to_numpy()
            counts_by_ev[code]=arr
            pres=arr>0
            pres_by_ev[code]=set(grid.loc[pres,'cell_id'])
            occupied=int(pres.sum())
            vals=arr[pres]
            summary.append({
                'scale_km2':area_km2,'variant':var,'evidence_code':code,
                'n_cells':len(grid),'occupied_cells':occupied,
                'occupied_pct':100*occupied/len(grid) if len(grid) else np.nan,
                'median_count_occupied':float(np.median(vals)) if len(vals) else np.nan,
                'max_count':int(arr.max()) if len(arr) else 0,
                'n_points_assigned':int(arr.sum()),
            })
        # Need geometric support for pairwise variants. Use fixed 5km points rather than cell ids.
        presence_maps[(area_km2,var)] = (grid, counts_by_ev)
        metadata.append({
            'scale_km2':area_km2,'variant':var,'area_nominal_km2':area_km2,
            'orientation':'regular hexagonal pointy-top',
            'side_m':s,'hex_width_m':width,'row_spacing_m':vspace,
            'x_shift_fraction_width':fx,'y_shift_fraction_row_spacing':fy,
            'x_shift_m':xshift,'y_shift_m':yshift,
            'crs':'EPSG:5880','clipping':'interseção com limite MS IBGE 2025',
            'purpose':'ensaio MAUP de origem; não é malha oficial PIH'
        })

# pairwise concordance evaluated on fixed support points already built
supp=pd.read_csv(OUT/'support_points_5km.csv')
# Inspect coordinate names
print('support cols',supp.columns.tolist()[:20])
# Find x/y columns in metric
xcol=next((c for c in supp.columns if c in ['x_m','x_5880','x']),None)
ycol=next((c for c in supp.columns if c in ['y_m','y_5880','y']),None)
if not xcol or not ycol:
    # derive from lon/lat
    loncol=next(c for c in supp.columns if c in ['longitude','lon','x_wgs84'])
    latcol=next(c for c in supp.columns if c in ['latitude','lat','y_wgs84'])
    sg=gpd.GeoDataFrame(supp,geometry=gpd.points_from_xy(supp[loncol],supp[latcol]),crs='EPSG:4326').to_crs(CRS_METRIC)
else:
    sg=gpd.GeoDataFrame(supp,geometry=gpd.points_from_xy(supp[xcol],supp[ycol]),crs=CRS_METRIC)

# assign each support point to each variant and fetch counts/presence
support_arrays={}
for key,(grid,counts_by_ev) in presence_maps.items():
    joined=gpd.sjoin(sg[['geometry']],grid[['cell_id','geometry']],how='left',predicate='within')
    if joined['cell_id'].isna().any():
        # support points inside state should fall in a cell but boundary fallback intersects
        miss=joined['cell_id'].isna()
        ji=gpd.sjoin(sg.loc[joined.index[miss],['geometry']],grid[['cell_id','geometry']],how='left',predicate='intersects')
        first=ji.dropna(subset=['cell_id']).sort_values('cell_id').groupby(level=0)['cell_id'].first()
        joined.loc[miss,'cell_id']=joined.index[miss].map(first)
    cell_index={cid:i for i,cid in enumerate(grid['cell_id'])}
    for code,arr in counts_by_ev.items():
        vals=np.array([arr[cell_index[cid]] if cid in cell_index else 0 for cid in joined['cell_id']],dtype=float)
        support_arrays[(key[0],key[1],code)]=vals

concord=[]
from itertools import combinations
for area in scales:
    for code in ['E01','E07','E09','E10']:
        for va,vb in combinations([v[0] for v in variants],2):
            a=support_arrays[(area,va,code)]
            b=support_arrays[(area,vb,code)]
            pa=a>0; pb=b>0
            union=(pa|pb).sum(); inter=(pa&pb).sum()
            j=inter/union if union else 1.0
            mismatch=(pa!=pb).mean()*100
            rho=spearmanr(a,b).statistic if np.std(a)>0 and np.std(b)>0 else np.nan
            concord.append({'scale_km2':area,'evidence_code':code,'variant_a':va,'variant_b':vb,
                            'support_points_n':len(a),'presence_jaccard':j,'presence_mismatch_pct':mismatch,
                            'spearman_counts_support':rho,
                            'presence_a_pct':pa.mean()*100,'presence_b_pct':pb.mean()*100})

summary_df=pd.DataFrame(summary)
concord_df=pd.DataFrame(concord)
meta_df=pd.DataFrame(metadata)
# Sensitivity summary by scale/evidence
sens=[]
for (area,code),g in summary_df.groupby(['scale_km2','evidence_code']):
    cg=concord_df[(concord_df.scale_km2==area)&(concord_df.evidence_code==code)]
    sens.append({
        'scale_km2':area,'evidence_code':code,
        'n_variants':len(g),
        'occupied_pct_min':g.occupied_pct.min(),'occupied_pct_max':g.occupied_pct.max(),
        'occupied_pct_range':g.occupied_pct.max()-g.occupied_pct.min(),
        'occupied_cells_min':g.occupied_cells.min(),'occupied_cells_max':g.occupied_cells.max(),
        'max_count_min':g.max_count.min(),'max_count_max':g.max_count.max(),
        'presence_jaccard_min':cg.presence_jaccard.min(),'presence_jaccard_median':cg.presence_jaccard.median(),
        'presence_mismatch_pct_max':cg.presence_mismatch_pct.max(),
        'spearman_counts_min':cg.spearman_counts_support.min(),'spearman_counts_median':cg.spearman_counts_support.median(),
    })
sens_df=pd.DataFrame(sens)

summary_df.to_csv(OUT/'maup_variant_summary.csv',index=False)
meta_df.to_csv(OUT/'maup_variant_metadata.csv',index=False)
concord_df.to_csv(OUT/'maup_origin_concordance.csv',index=False)
sens_df.to_csv(OUT/'maup_origin_sensitivity_summary.csv',index=False)
print('\nSummary')
print(summary_df.to_string(index=False))
print('\nSensitivity')
print(sens_df.to_string(index=False))
