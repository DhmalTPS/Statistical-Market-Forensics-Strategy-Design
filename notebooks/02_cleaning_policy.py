'''
PHASE 9
│
├── 9.1 Timestamp policy
│      └── Already clean → retain
│
├── 9.2 Price policy
│      ├── NaN? → none found
│      ├── ≤0? → none found
│      └── retain valid prices
│
├── 9.3 Feature NaN classification
│      ├── leading
│      ├── internal
│      └── trailing
│
├── 9.4 Extreme-return policy
│      └── DON'T remove yet
│
├── 9.5 Flat-price policy
│      └── DON'T remove
│
└── 9.6 Write cleaning-policy justification
'''

from pathlib import Path
import re
import pandas as pd

def get_day_number(path):
    match = re.search(r'day[_\s]?(\d+)', path.stem, re.IGNORECASE)
    return int(match.group(1)) if match else None

DATA_DIR = Path("EBX_Dataset")
OUTPUT_DIR = Path("output")

csv_files = sorted(DATA_DIR.glob("*.csv"), key=get_day_number)
comp_files = [f for f in csv_files if get_day_number(f) <= 85]

def classify_missingness(file):
    df = pd.read_csv(file)
    fea = df.columns[2:]
    res=[]
    for col in fea:
        na = df[col].isna()
        if not na.any(): continue
        fidx = df[col].first_valid_index()
        lidx = df[col].last_valid_index()
        lead = na.iloc[:fidx].sum() if fidx is not None else len(df)
        trail = na.iloc[lidx+1:].sum() if lidx is not None else 0
        inter = na.sum()-(lead+trail)
        res.append({
            'day':get_day_number(file),
            'feature':col,
            'missing_count':na.sum(),
            'nan_leading':lead,
            'nan_internal':inter,
            'nan_trailing':trail,
            'first_index':fidx,
            'last_index':lidx
        })
    return pd.DataFrame(res)

miss_classify_org = [classify_missingness(f) for f in comp_files]
miss_classify_df = pd.concat(miss_classify_org,ignore_index=True)
print(miss_classify_df)
miss_classify_df.to_csv(OUTPUT_DIR/'missing_classify.csv',index=False)

'''
PHASE 9 — CLEANING POLICY

9.1 Timestamp policy
    └── No missing timestamps
    └── No duplicate timestamps
    └── No non-1s gaps
    └── Monotonic
    └── RETAIN

9.2 Price policy
    └── No Price NaNs
    └── No non-positive prices
    └── RETAIN

9.3 Feature NaN policy
    ├── Leading NaNs → expected warm-up
    ├── Internal NaNs → none / essentially none
    ├── Trailing NaNs → none / essentially none
    └── DO NOT IMPUTE WARM-UP NaNs

9.4 Extreme-return policy
    └── Identify, DON'T remove yet

9.5 Flat-price policy
    └── Identify, DON'T remove

9.6 Cleaning-policy justification
    └── Document findings
'''

print('\n===== PHASE 9 COMPLETE =====')
print('Timestamp policy: RETAIN')
print('Price policy: RETAIN')
print('Leading feature NaNs: KEEP — expected warm-up')
print('Internal feature NaNs: INVESTIGATE IF PRESENT')
print('Trailing feature NaNs: INVESTIGATE IF PRESENT')
print('Extreme returns: FLAG ONLY — DO NOT REMOVE')
print('Flat prices: KEEP')
print('Raw data: NEVER MODIFY')
print('\nTotal internal NaNs:', miss_classify_df['nan_internal'].sum())
print('Total trailing NaNs:', miss_classify_df['nan_trailing'].sum())

'''
┌──────────────────────────────┬──────────────────────┐
│ Issue                        │ Action               │
├──────────────────────────────┼──────────────────────┤
│ Missing timestamps           │ None                 │
│ Duplicate timestamps         │ None                 │
│ Non-1s gaps                  │ None                 │
│ Non-monotonic time           │ None                 │
│ Price NaN                    │ None                 │
│ Price <= 0                   │ None                 │
│ Leading feature NaNs         │ KEEP                 │
│ Internal feature NaNs        │ Investigate          │
│ Trailing feature NaNs        │ Investigate          │
│ Extreme returns              │ FLAG, don't remove   │
│ Flat prices                  │ KEEP                 │
└──────────────────────────────┴──────────────────────┘
'''