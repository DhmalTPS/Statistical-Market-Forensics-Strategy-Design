from pathlib import Path
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

def get_day_number(file):
    res = re.search(r'day[_\s]?(\d+)',file.stem,re.IGNORECASE)
    return int(res.group(1)) if res else None

DATA_DIR = Path(r'.\EBX_Dataset')
OUTPUT_DIR = Path(r'.\output')
RESULTS_DIR = Path(r'.\results')

POOL_RET_DIR = OUTPUT_DIR / "03_pooled_returns.csv"
POOL_STAT_DIR = OUTPUT_DIR / "03_pooled_statistics.csv"
DIST_DIR = OUTPUT_DIR / "06_distribution_statistics.csv"

RETURN_DIR = OUTPUT_DIR / "03_day_returns"
ACF_DIR = OUTPUT_DIR / "04_day_acf"
EXTREME_DIR = OUTPUT_DIR / "09_extreme_events"
EXTREME_DIR.mkdir(parents=True,exist_ok=True)

csv_files = sorted(DATA_DIR.glob("*.csv"),key=get_day_number)
comp_files = [f for f in csv_files if get_day_number(f)<=85]
comp_keys = [get_day_number(f) for f in comp_files]

rvar = ['return_1s','return_1m','return_5m']
lvar = ['log_ret_1s','log_ret_1m','log_ret_5m']

for c in lvar:
    pool_df = pd.read_csv(POOL_RET_DIR,usecols=['day','Time','Price',c])
    df = pool_df.dropna(subset=[c]).copy()
    myu = df[c].mean()
    sig = df[c].std()
    df[f'ABS_{c}'] = df[c].abs()
    df[f'zscore_{c}'] = (df[c]-myu)/sig
    df[f'dir_{c}'] = np.where(df[c]>0,'UP','DOWN')
    ext_df = df.sort_values(f'ABS_{c}',ascending=False).head(20).copy()
    ext_df.insert(0,'rank',np.arange(1,len(ext_df)+1))
    ext_df = ext_df[['rank','day','Time','Price',c,f'ABS_{c}',f'zscore_{c}',f'dir_{c}']]
    ext_df.to_csv(EXTREME_DIR/f'{c}_top20.csv')
    print("\nTOP 20 EXTREME 1-MINUTE RETURNS:\n",ext_df.to_string(index=False))