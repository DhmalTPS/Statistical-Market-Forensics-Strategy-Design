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
REGACF_DIR = OUTPUT_DIR / "12_regime_acf"
REGACF_DIR.mkdir(parents=True,exist_ok=True)

csv_files = sorted(DATA_DIR.glob("*.csv"),key=get_day_number)
comp_files = [f for f in csv_files if get_day_number(f)<=85]
comp_keys = [get_day_number(f) for f in comp_files]
ret_files = sorted(RETURN_DIR.glob("day*_returns.csv"),key=get_day_number)

rvar = ['return_1s','return_1m','return_5m']
lvar = ['log_ret_1s','log_ret_1m','log_ret_5m']

ROLL_WIN = [
    ('log_ret_1s', [300, 900, 1800], 3600),
    ('log_ret_1m', [1, 5, 30], 60),
    ('log_ret_5m', [1, 3, 6], 12)
]

def acf_signify(col,l):
    r = pd.Series(col).dropna().to_numpy(dtype=float)
    n = len(r)
    if n<=l: return np.nan, np.nan, np.nan
    x = r - np.mean(r)
    den = np.sum(x**2)
    if den==0: return np.nan, np.nan, np.nan
    num = np.sum(x[l:]*x[:-l])
    acf = num/den
    se = 1/np.sqrt(n)
    zs = acf/se
    pv = 2*stats.norm.sf(abs(zs))
    return acf, zs, pv

for c,w,_ in ROLL_WIN:
    res = []
    for f in ret_files:
        df = pd.read_csv(f,usecols=[c])
        a1,z1,p1 = acf_signify(df[c],l=w[0])
        a2,z2,p2 = acf_signify(df[c],l=w[1])
        a3,z3,p3 = acf_signify(df[c],l=w[2])
        res.append({
            'day':get_day_number(f), 
            'n_obs':df[c].notna().sum(),
            f'acf_{w[0]}':a1, f'z_{w[0]}':z1, f'p_{w[0]}':p1,
            f'acf_{w[1]}':a2, f'z_{w[1]}':z2, f'p_{w[1]}':p2,
            f'acf_{w[2]}':a3, f'z_{w[2]}':z3, f'p_{w[2]}':p3
        })
    acf_df = pd.DataFrame(res)
    acf_df = acf_df.sort_values('day').reset_index(drop=True)
    acf_df.to_csv(REGACF_DIR/f'{c}_reg_acf.csv',index=False)
    print(acf_df.to_string(index=False))
