from pathlib import Path
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def get_day_number(file):
    res = re.search(r'day[_\s]?(\d+)',file.stem,re.IGNORECASE)
    return int(res.group(1)) if res else None

DATA_DIR = Path('EBX_Dataset')
OUTPUT_DIR = Path('output')
RESULTS_DIR = Path('results')
RETURN_DIR = OUTPUT_DIR / "03_day_returns"
INTRA_DIR = OUTPUT_DIR / "05_intraday_season"
INTRA_DIR.mkdir(parents=True,exist_ok=True)

csv_files = sorted(DATA_DIR.glob("*.csv"),key=get_day_number)
comp_files = [f for f in csv_files if get_day_number(f)<=85]
comp_keys = [get_day_number(f) for f in comp_files]
var = ['return_1s','return_1m','return_5m','log_ret_1s','log_ret_1m','log_ret_5m']
BUCKET = [(300,'return_1s'),(1200,'return_1m'),(3600,'return_5m'),(300,'log_ret_1s'),(1200,'log_ret_1m'),(3600,'log_ret_5m')]

def add_time_feature(df,b):
    t = pd.to_timedelta(df['Time'])
    df['seconds_open'] = t.dt.total_seconds().astype(int)
    df['bucket'] = df['seconds_open']//b
    return df

def intraday_stats(file,b,c):
    df = pd.read_csv(RETURN_DIR/f'day{get_day_number(file)}_returns.csv')
    df = add_time_feature(df,b)
    res = []
    for buc, grp in df.groupby('bucket'):
        r = grp[c].dropna()
        if len(r)==0: continue
        res.append({
            'day':get_day_number(file),
            'bucket':buc,
            'start_sec':buc*b,
            'end_sec':(buc+1)*b-1,
            'n_obs':len(r),
            'mean_return':r.mean(),
            'std_return':r.std(),
            'median_return':r.median(),
            'mean_abs_ret':r.abs().mean(),
            'pos_frac':(r>0).mean(),
            'neg_frac':(r<0).mean(),
            'zero_frac':(r==0).mean(),
            'q01':r.quantile(0.01),
            'q99':r.quantile(0.99)
        })
    return pd.DataFrame(res)

for b,c in BUCKET:

    # PER-DAY INTRADAY ANALYSIS
    intra_org = [intraday_stats(f,b,c) for f in comp_files]
    intra_df = pd.concat(intra_org,ignore_index=True)
    print(intra_df.head(20),'\nShape:',intra_df.shape)
    intra_df.to_csv(INTRA_DIR/f'intraday_{c}.csv',index=False)

    # POOLED INTRADAY PROFILE
    pool_df = intra_df.groupby('bucket').agg(
        start_sec = ('start_sec','first'),
        end_sec = ('end_sec','first'),
        mean_vol = ('std_return','mean'),
        median_vol = ('std_return','median'),
        std_vol = ('std_return','std'),
        min_vol = ('std_return','min'),
        max_vol = ('std_return','max'),
        mean_abs_ret = ('mean_abs_ret','mean'),
        mean_return = ('mean_return','mean'),
        mean_pos_frac = ('pos_frac','mean'),
        mean_neg_frac = ('neg_frac','mean'),
        mean_zero_frac = ('zero_frac','mean'),
        day_present = ('day','count')
    ).reset_index()
    pool_df['time_min'] = pool_df['start_sec'] / 60
    print(pool_df.head(20),'\nShape:',pool_df.shape)
    pool_df.to_csv(INTRA_DIR/f'pooled_{c}.csv',index=False)

    # MAIN VOLATILITY PLOT
    plt.plot(pool_df['time_min'],pool_df['mean_vol'],label=f'Mean {c} volatility')
    plt.xlabel('Minutes passed')
    plt.ylabel(f'{c} Std. Dev.')
    plt.title('Intraday Volatility Profile (EBX)')
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(RESULTS_DIR/f'05_intra_vol_{c}.png',dpi=150)
    plt.show()

    # VOLATILITY + CROSS-DAY DISPERSION
    tim = pool_df['time_min']
    mea = pool_df['mean_vol']
    std = pool_df['std_vol']
    plt.plot(tim,mea,label='Mean volatility')
    plt.fill_between(tim,mea-std,mea+std,alpha=0.2,label='Day level ±1 std')
    plt.xlabel('Minutes passed')
    plt.ylabel(f'{c} Volatility')
    plt.title('Intraday Volatility with Crossday Dispersion')
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(RESULTS_DIR/f'05_intra_dis_{c}.png',dpi=150)
    plt.show()

    # MOST / LEAST VOLATILE PERIODS
    rank_df = pool_df.sort_values('mean_vol',ascending=False)
    print('\nMOST VOLATILE PERIODS:\n',rank_df[['bucket','time_min','mean_vol','median_vol','day_present']].head(15))
    print('\nMOST VOLATILE PERIODS:\n',rank_df[['bucket','time_min','mean_vol','median_vol','day_present']].tail(15))

    # ABSOLUTE RETURN PROFILE
    plt.plot(pool_df['time_min'],pool_df['mean_abs_ret'],label=f'Mean abs({c})')
    plt.xlabel('Minutes passed')
    plt.ylabel(f'Mean |{c}|')
    plt.title('Intraday Absoulute Return Profile')
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(RESULTS_DIR/f'05_intra_abs_{c}.png',dpi=150)
    plt.show()

    # EARLY / MIDDLE / LATE
    time_region = lambda s: 'early' if s<3600 else ('middle' if s<7200 else 'late')
    pool_df['region'] = pool_df['start_sec'].apply(time_region)
    region_df = pool_df.groupby('region').agg(
        mean_vol = ('mean_vol','mean'),
        median_vol = ('median_vol','median'),
        max_vol = ('mean_vol','max'),
        min_vol = ('mean_vol','min')
    )
    print('EARLY / MIDDLE / LATE:\n',region_df)
    region_df.to_csv(INTRA_DIR/f'region_{c}.csv',index=False)
    
### UNDERSTAND THIS CODE ###