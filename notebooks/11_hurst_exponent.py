from pathlib import Path
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

def get_day_number(file):
    res = re.search(r'day[_\s]?(\d+)',file.stem,re.IGNORECASE)
    return int(res.group(1)) if res else None

DATA_DIR = Path('EBX_Dataset')
OUTPUT_DIR = Path('output')
RESULTS_DIR = Path('results')

RETURN_DIR = OUTPUT_DIR / "03_day_returns"
HURST_DIR = OUTPUT_DIR / "11_hurst_expo"
HURST_DIR.mkdir(parents=True,exist_ok=True)

csv_files = sorted(DATA_DIR.glob("*.csv"),key=get_day_number)
comp_files = [f for f in csv_files if get_day_number(f)<=85]
comp_keys = [get_day_number(f) for f in comp_files]
ret_files = sorted(RETURN_DIR.glob("day*_returns.csv"),key=get_day_number)

rvar = ['return_1s','return_1m','return_5m']
lvar = ['log_ret_1s','log_ret_1m','log_ret_5m']

def hurst_expo(col):
    r = pd.Series(col).dropna().to_numpy(dtype=float)
    n = len(r)
    if n<100: return np.nan
    mx = min(n//4,1000)
    lag = np.unique(np.logspace(np.log10(2),np.log10(mx),20).astype(int))
    tau = []
    vlg = []
    for l in lag:
        if l>=n: continue
        std = np.std(r[l:]-r[:-l],ddof=1)
        if std>0 and np.isfinite(std):
            tau.append(std)
            vlg.append(l)
    if len(tau) < 2: return np.nan
    llg = np.log(vlg)
    lta = np.log(tau)
    return np.polyfit(llg,lta,1)[0]

for c in lvar:
    res = []
    for f in ret_files:
        df = pd.read_csv(f,usecols=[c])
        res.append({
            'day': get_day_number(f), 
            'hurst': hurst_expo(df[c]),
            'n_obs': df[c].notna().sum()
        })
    hur_df = pd.DataFrame(res)
    hur_df = hur_df.sort_values('day').reset_index(drop=True)
    hur_df.to_csv(HURST_DIR/f'{c}_hurst_exp.csv',index=False)
    print(hur_df,"\nShape:",hur_df.shape)