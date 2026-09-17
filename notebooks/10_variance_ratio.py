# ls; ls notebooks; ls results; ls output; ls output/03_day_returns; ls output/04_day_acf; ls output/05_intraday_season; ls output/07_sigma_events; ls output/08_vol_cluster; ls output/09_extreme_events
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

RETURN_DIR = OUTPUT_DIR / "03_day_returns"
EXTREME_DIR = OUTPUT_DIR / "09_var_ratio"

csv_files = sorted(DATA_DIR.glob("*.csv"),key=get_day_number)
comp_files = [f for f in csv_files if get_day_number(f)<=85]
comp_keys = [get_day_number(f) for f in comp_files]
ret_files = sorted(RETURN_DIR.glob("day*_returns.csv"),key=get_day_number)

rvar = ['return_1s','return_1m','return_5m']
lvar = ['log_ret_1s','log_ret_1m','log_ret_5m']
qval = [2,5,30]

def var_ratio(col,q):
    r = pd.Series(col).dropna().to_numpy(dtype=float)
    n = len(r)
    if n<=q+1: return np.nan, np.nan, np.nan
    dem = r - np.mean(r)
    var = np.sum(dem**2)/(n-1)
    if var==0: return np.nan, np.nan, np.nan
    rq = np.array([np.sum(r[i-q+1:i+1]) for i in range(q-1,n)])
    vr = np.var(rq,ddof=1)/(q*var)
    deno = np.sum(dem**2)**2
    if deno==0: return np.nan, np.nan, np.nan
    t = sum(4*n*np.sum(dem[j:]**2*dem[:-j]**2)/deno*(1-j/q)**2 for j in range(1,q))
    if t<=0 or not np.isfinite(t): return vr, np.nan, np.nan
    se = np.sqrt(t)
    st = (vr-1)/se
    pv = 2*stats.norm.sf(abs(st))
    return vr, st, pv

res = []
for c in lvar:
    for f in ret_files:
        df = pd.read_csv(f,usecols=[c])
        # ob = df[c].notna().sum()
        for q in qval:
            vr,st,pv = var_ratio(df[c],q)
            res.append({
                'day':get_day_number(f),
                'ret_series':c,
                'q_val':q,
                'VR':vr,
                'VR_stats':st,
                'p_val':pv
            })

vr_df = pd.DataFrame(res)
vr_df = vr_df.sort_values(['ret_series','day','q_val']).reset_index(drop=True)
vr_df.to_csv(OUTPUT_DIR/'10_variance_ratio.csv',index=False)