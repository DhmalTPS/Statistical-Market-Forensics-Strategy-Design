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

SIGMA_DIR = OUTPUT_DIR / "07_sigma_events"
SIGMA_DIR.mkdir(parents=True,exist_ok=True)

csv_files = sorted(DATA_DIR.glob("*.csv"),key=get_day_number)
comp_files = [f for f in csv_files if get_day_number(f)<=85]
comp_keys = [get_day_number(f) for f in comp_files]

rvar = ['return_1s','return_1m','return_5m']
lvar = ['log_ret_1s','log_ret_1m','log_ret_5m']
pool_df = pd.read_csv(POOL_RET_DIR,usecols=['day','Time','Price']+lvar)

for c in lvar:

    # POOLED SIGMA-EVENT ANALYSIS
    s = pool_df[c].dropna()
    myu = s.mean()
    sig = s.std()
    pool_df[f'{c}_z_score'] = (pool_df[c]-myu)/sig
    thr = [1,2,3]
    res = []
    for t in thr:
        pos_count = (pool_df[f'{c}_z_score']>t).sum()
        neg_count = (pool_df[f'{c}_z_score']<-t).sum()
        act_count = (pool_df[f'{c}_z_score'].abs()>t).sum()
        act_prob = act_count/len(s)
        exp_prob = 2*stats.norm.sf(t)
        exp_count = len(s)*exp_prob
        res.append({
            'horizon':f'{c[-2::1]}',
            'threshold_sigma':t,
            'mean':myu,
            'std':sig,
            'n_obs':len(s),
            'expected_probability':exp_prob,
            'actual_probability':act_prob,
            'expected_count':exp_count,
            'actual_count':act_count,
            'positive_count':pos_count,
            'negative_count':neg_count,
            'positive_probability':pos_count/len(s),
            'negative_probability':neg_count/len(s),
            'tail_inflation':act_prob/exp_prob
        })
    sigma_df = pd.DataFrame(res)
    sigma_df.to_csv(SIGMA_DIR/f'sigma_pool_{c}.csv',index=False)
    print(sigma_df)

    # PER-DAY SIGMA-EVENT ANALYSIS
    res = []
    for f in comp_files:
        df = pd.read_csv(RETURN_DIR/f'day{get_day_number(f)}_returns.csv')
        s = df[c].dropna()
        z = (s-myu)/sig
        res.append({
            'day':get_day_number(f),
            'n_obs':len(s),
            'sig_1_event':(z.abs()>1).sum(),
            'sig_2_event':(z.abs()>2).sum(),
            'sig_3_event':(z.abs()>3).sum(),
            'sig_1_frac':(z.abs()>1).mean(),
            'sig_2_frac':(z.abs()>2).mean(),
            'sig_3_frac':(z.abs()>3).mean()
        })
    daily_df = pd.DataFrame(res)
    print('\nMOST 3-SIGMA EVENTS:\n',daily_df.sort_values('sig_3_event',ascending=False).head(15))
    print('\nHIGHEST 3-SIGMA EVENT RATE:\n',daily_df.sort_values('sig_3_frac',ascending=False).head(15))
    daily_df.to_csv(SIGMA_DIR/f'sigma_daily_{c}.csv',index=False)
