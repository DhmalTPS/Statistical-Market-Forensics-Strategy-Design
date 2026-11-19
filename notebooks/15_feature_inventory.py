# FILE 15

from pathlib import Path
import re
import numpy as np
import pandas as pd


def get_day_number(file):
    res = re.search(r'day[_\s]?(\d+)',file.stem,re.IGNORECASE)
    return int(res.group(1)) if res else None


DATA_DIR = Path('EBX_Dataset')
OUTPUT_DIR = Path('output')
RESULTS_DIR = Path('results')

INV_FILE = OUTPUT_DIR / "15_feature_inventory.csv"
MISS_FILE = OUTPUT_DIR / "15_feature_missing.csv"

csv_files = sorted(DATA_DIR.glob("*.csv"),key=get_day_number)
comp_files = [f for f in csv_files if get_day_number(f) is not None and get_day_number(f)<=85]
comp_files = sorted(comp_files,key=get_day_number)

print(f"\nFiles found: {len(csv_files)}")
print(f"Days used: {len(comp_files)}")
print(f"Day range: {get_day_number(comp_files[0])} - {get_day_number(comp_files[-1])}" if comp_files else "No valid files found")

if not comp_files:
    raise FileNotFoundError("No Day 1-85 CSV files found in .\\EBX_Dataset")

rows = []
miss_rows = []

for i,file in enumerate(comp_files,1):
    day = get_day_number(file)
    df = pd.read_csv(file)

    print(f"\n[{i}/{len(comp_files)}] Day {day} | rows={len(df)} | cols={len(df.columns)}")

    feat_cols = [c for c in df.columns if re.fullmatch(r'(PB|VB)\d+_T\d+',str(c),re.IGNORECASE)]

    if not feat_cols:
        print("  WARNING: no PB/VB features found")
        continue

    if i == 1:
        all_features = sorted(
            set(feat_cols),
            key=lambda x: (
                re.match(r'(PB|VB)(\d+)_T(\d+)',x,re.IGNORECASE).group(1).upper(),
                int(re.match(r'(PB|VB)(\d+)_T(\d+)',x,re.IGNORECASE).group(2)),
                int(re.match(r'(PB|VB)(\d+)_T(\d+)',x,re.IGNORECASE).group(3))
            )
        )

    for col in feat_cols:
        m = re.fullmatch(r'(PB|VB)(\d+)_T(\d+)',col,re.IGNORECASE)
        if not m:
            continue

        family = m.group(1).upper()
        idx = int(m.group(2))
        t = int(m.group(3))

        s = df[col]
        nn = s.notna()

        rows.append({
            'day': day,
            'feature': col,
            'family': family,
            'index': idx,
            'T': t,
            'dtype': str(s.dtype),
            'rows': len(s),
            'missing_count': int(s.isna().sum()),
            'missing_pct': float(s.isna().mean()*100),
            'valid_count': int(nn.sum()),
            'first_valid_index': int(nn.idxmax()) if nn.any() else np.nan,
            'last_valid_index': int(nn[::-1].idxmax()) if nn.any() else np.nan
        })

        miss_rows.append({
            'day': day,
            'feature': col,
            'family': family,
            'index': idx,
            'T': t,
            'first_valid_index': int(nn.idxmax()) if nn.any() else np.nan,
            'last_valid_index': int(nn[::-1].idxmax()) if nn.any() else np.nan,
            'missing_count': int(s.isna().sum()),
            'missing_pct': float(s.isna().mean()*100),
            'valid_count': int(nn.sum())
        })


inv_day_df = pd.DataFrame(rows)
miss_day_df = pd.DataFrame(miss_rows)

if inv_day_df.empty:
    raise ValueError("No PB/VB features were detected in Days 1-85.")

inv_day_df = inv_day_df.sort_values(
    ['day','family','index','T']
).reset_index(drop=True)

miss_day_df = miss_day_df.sort_values(
    ['day','family','index','T']
).reset_index(drop=True)

feature_order = (
    inv_day_df[['feature','family','index','T']]
    .drop_duplicates()
    .sort_values(['family','index','T'])
    .reset_index(drop=True)
)

inventory = []

for _,r in feature_order.iterrows():
    cur = inv_day_df[inv_day_df['feature']==r['feature']].copy()

    inventory.append({
        'feature': r['feature'],
        'family': r['family'],
        'index': int(r['index']),
        'T': int(r['T']),
        'days_present': int(cur['day'].nunique()),
        'days_missing': int(85-cur['day'].nunique()),
        'dtype': ', '.join(sorted(cur['dtype'].dropna().unique())),
        'missing_count_total': int(cur['missing_count'].sum()),
        'missing_pct_mean': float(cur['missing_pct'].mean()),
        'valid_count_total': int(cur['valid_count'].sum()),
        'first_valid_index_min': float(cur['first_valid_index'].min()) if cur['first_valid_index'].notna().any() else np.nan,
        'first_valid_index_max': float(cur['first_valid_index'].max()) if cur['first_valid_index'].notna().any() else np.nan,
        'last_valid_index_min': float(cur['last_valid_index'].min()) if cur['last_valid_index'].notna().any() else np.nan,
        'last_valid_index_max': float(cur['last_valid_index'].max()) if cur['last_valid_index'].notna().any() else np.nan
    })

inventory_df = pd.DataFrame(inventory)

inventory_df.to_csv(INV_FILE,index=False)
miss_day_df.to_csv(MISS_FILE,index=False)

print("\n--- FEATURE INVENTORY ---")
print(inventory_df.to_string(index=False))

print("\n--- FEATURE COUNTS ---")
print(inventory_df.groupby('family').size())

print("\n--- FEATURES BY T ---")
print(
    inventory_df
    .groupby(['family','T'])
    .size()
    .unstack(fill_value=0)
)

print("\n--- MISSINGNESS ---")
print(
    inventory_df[
        ['feature','family','T','days_present','days_missing',
         'missing_pct_mean','first_valid_index_min','first_valid_index_max']
    ].to_string(index=False)
)

print("\n--- FILES WRITTEN ---")
print(INV_FILE)
print(MISS_FILE)

print("\nFeature count:",len(inventory_df))
print("Families:",inventory_df['family'].unique().tolist())
print("T values:",sorted(inventory_df['T'].unique().tolist()))