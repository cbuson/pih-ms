#!/usr/bin/env python3
"""Recalcula as malhas IR V2.1 a partir do CSV auditado por poço.

Entrada científica congelada
  data/derived/independence_redundancy/well_independence_redundancy.csv
  docs/data/scale_study/scale_primary_*km2.geojson

O script não deduplica poços. Os clusters são somente cenários de sensibilidade.
"""
from pathlib import Path
import pandas as pd, geopandas as gpd, numpy as np
ROOT=Path(__file__).resolve().parents[1]
INP=ROOT/'data/derived/independence_redundancy/well_independence_redundancy.csv'
OUT=ROOT/'data/derived/independence_redundancy'
WEB=ROOT/'docs/data/independence_redundancy'
SCALES=(100,150,250,500,1000)

def as_bool(s): return s.astype(str).str.lower().isin(['true','1','sim','yes'])
w=pd.read_csv(INP,dtype={'well_id':str})
for c in ['source_snapshot_overlap','exact_coordinate_colocation','nn_lt_100m','nn_lt_500m','nn_lt_1000m','specific_capacity_both_sources','specific_capacity_source_echo']:
    if c in w: w[c]=as_bool(w[c])
for c in ['latitude','longitude','source_core_pairs_comparable_n','source_core_pairs_matching_n','nearest_neighbor_m','pumping_test_records_n','chem_sample_records_n','chem_result_records_n','hydraulic_parameter_records_n','documentary_domains_n','dated_domains_n']:
    if c in w: w[c]=pd.to_numeric(w[c],errors='coerce')
pts=gpd.GeoDataFrame(w,geometry=gpd.points_from_xy(w.longitude,w.latitude),crs=4326).to_crs(5880)
for scale in SCALES:
    grid=gpd.read_file(ROOT/f'docs/data/scale_study/scale_primary_{scale}km2.geojson').to_crs(5880)
    j=gpd.sjoin(pts,grid[['cell_id','geometry']],predicate='within',how='left')
    if j.cell_id.isna().any():
        near=gpd.sjoin_nearest(pts.loc[j.cell_id.isna()],grid[['cell_id','geometry']],how='left',max_distance=50,distance_col='distance_m')
        near=near[~near.index.duplicated(keep='first')]
        for idx,row in near.iterrows():
            if pd.notna(row.cell_id): j.loc[idx,'cell_id']=row.cell_id
    if j.cell_id.isna().any(): raise RuntimeError(f'{scale}: há poços não atribuídos')
    groups={cid:sub.index for cid,sub in j.groupby('cell_id')}
    recs=[]
    for _,cell in grid.iterrows():
        idx=groups.get(cell.cell_id,[]); sw=w.loc[idx]; n=len(sw)
        if not n:
            recs.append({'cell_id':cell.cell_id,'scale_km2':scale,'area_effective_km2':cell.area_effective_km2,'n_wells_raw':0,'analysis_status':'SEM_POCO_NO_CONJUNTO_AUDITADO'}); continue
        pct=lambda x:100*x/n
        sites=sw.coordinate_site_id.fillna(sw.well_id).astype(str).nunique()
        high=sw.review_cluster_high_id.fillna(sw.well_id).astype(str).nunique()
        allc=sw.review_cluster_all_id.fillna(sw.well_id).astype(str).nunique()
        comp=int(sw.source_core_pairs_comparable_n.fillna(0).sum()); match=int(sw.source_core_pairs_matching_n.fillna(0).sum())
        dup=sw.duplicate_candidate_level.astype(str).str.upper()
        recs.append({'cell_id':cell.cell_id,'scale_km2':scale,'area_effective_km2':cell.area_effective_km2,'n_wells_raw':n,
          'source_snapshot_overlap_n':int(sw.source_snapshot_overlap.sum()),'pct_source_snapshot_overlap':pct(int(sw.source_snapshot_overlap.sum())),
          'coordinate_sites_n':sites,'coordinate_compression_n':n-sites,'coordinate_compression_pct':pct(n-sites),
          'review_high_clusters_n':high,'review_high_reduction_n':n-high,'review_high_reduction_pct':pct(n-high),
          'review_all_clusters_n':allc,'review_all_reduction_n':n-allc,'review_all_reduction_pct':pct(n-allc),
          'duplicate_candidate_wells_n':int((dup!='NONE').sum()),'duplicate_candidate_wells_pct':pct(int((dup!='NONE').sum())),
          'exact_colocation_wells_n':int(sw.exact_coordinate_colocation.sum()),'exact_colocation_wells_pct':pct(int(sw.exact_coordinate_colocation.sum())),
          'nn_lt_500m_n':int(sw.nn_lt_500m.sum()),'nn_lt_500m_pct':pct(int(sw.nn_lt_500m.sum())),
          'documentary_domains_median':float(sw.documentary_domains_n.median()),'zero_domains_pct':pct(int((sw.documentary_domains_n==0).sum())),'fourplus_domains_pct':pct(int((sw.documentary_domains_n>=4).sum())),
          'source_core_pairs_comparable_n':comp,'source_core_pairs_matching_n':match,'source_core_match_pct':None if comp==0 else 100*match/comp,
          'chem_sample_records_n':int(sw.chem_sample_records_n.fillna(0).sum()),'hydraulic_parameter_records_n':int(sw.hydraulic_parameter_records_n.fillna(0).sum()),
          'chem_sample_records_per_well':float(sw.chem_sample_records_n.fillna(0).sum()/n),'hydraulic_parameter_records_per_well':float(sw.hydraulic_parameter_records_n.fillna(0).sum()/n),
          'analysis_status':'COM_POCO_NO_CONJUNTO_AUDITADO'})
    df=pd.DataFrame(recs); df.to_csv(OUT/f'independence_redundancy_{scale}km2_rebuilt.csv',index=False,encoding='utf-8-sig')
print('OK')
