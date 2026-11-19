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

POOL_RET_DIR = OUTPUT_DIR / "03_pooled_returns.csv"
POOL_STAT_DIR = OUTPUT_DIR / "03_pooled_statistics.csv"
DIST_DIR = OUTPUT_DIR / "06_distribution_statistics.csv"

RETURN_DIR = OUTPUT_DIR / "03_day_returns"
ACF_DIR = OUTPUT_DIR / "04_day_acf"
VOL_DIR = OUTPUT_DIR / "08_vol_cluster"
VOL_DIR.mkdir(parents=True,exist_ok=True)

csv_files = sorted(DATA_DIR.glob("*.csv"),key=get_day_number)
comp_files = [f for f in csv_files if get_day_number(f)<=85]
comp_keys = [get_day_number(f) for f in comp_files]

rvar = ['return_1s','return_1m','return_5m']
lvar = ['log_ret_1s','log_ret_1m','log_ret_5m']
ROLL_WIN = [
    ('log_ret_1s',[300,900,1800],3600),
    ('log_ret_1m',[5,15,30],60),
    ('log_ret_5m',[3,6,12],12)
]

def vol_features(file,col,win):
    df = pd.read_csv(RETURN_DIR/f'day{get_day_number(file)}_returns.csv',usecols=['Time',col])
    r = df[col]
    df[f'abs_{col}'] = r.abs()
    df[f'sq_{col}'] = r**2
    for w in win: df[f'{col}_roll_vol_{w}'] = r.rolling(w).std()
    t = pd.to_timedelta(df['Time'].astype(str))
    df['sec_open'] = t.dt.total_seconds().astype(int)
    df['min_open'] = df['sec_open']//60
    return df

def square_ACF(col,mx=60):
    s = col.dropna().to_numpy()**2
    res = [{'lag':l,'acf_sq':(np.corrcoef(s[l:],s[:-l])[0,1]if len(s)>1 else np.nan)} for l in range(1,mx+1)]
    return pd.DataFrame(res) 

for c,w,m in ROLL_WIN:
    vol_org = []
    for f in comp_files:
        df = vol_features(f,c,w)
        df.insert(0,'day',get_day_number(f))
        vol_org.append(df)
    vol_df = pd.concat(vol_org,ignore_index=True)
    print('\nVOLATILITY DATA:\n',vol_df.head())
    vol_df.to_csv(VOL_DIR/f'vol_{c}.csv',index=False)
    pool_vol = vol_df.groupby('min_open').agg(
        roll_vol_win1_mean=(f'{c}_roll_vol_{w[0]}','mean'),
        roll_vol_win1_median=(f'{c}_roll_vol_{w[0]}','median'),
        roll_vol_win2_mean=(f'{c}_roll_vol_{w[1]}','mean'),
        roll_vol_win2_median=(f'{c}_roll_vol_{w[1]}','median'),
        roll_vol_win3_mean=(f'{c}_roll_vol_{w[2]}','mean'),
        roll_vol_win3_median=(f'{c}_roll_vol_{w[2]}','median'),
        abs_ret_mean=(f'abs_{c}','mean'), 
        sq_ret_mean=(f'sq_{c}','mean'), 
        n_days=(f'day','nunique')
    ).reset_index()
    pool_vol = pool_vol.rename(columns={
        'roll_vol_win1_mean': f'roll_vol_{w[0]}_mean',
        'roll_vol_win1_median': f'roll_vol_{w[0]}_median',
        'roll_vol_win2_mean': f'roll_vol_{w[1]}_mean',
        'roll_vol_win2_median': f'roll_vol_{w[1]}_median',
        'roll_vol_win3_mean': f'roll_vol_{w[2]}_mean',
        'roll_vol_win3_median': f'roll_vol_{w[2]}_median',
    })
    pool_vol.to_csv(VOL_DIR/f'roll_{c}.csv',index=False)
    print('\nPOOLED ROLLING VOLATILITY:\n',pool_vol.head(20))
    plt.plot(pool_vol['min_open'],pool_vol[f'roll_vol_{w[0]}_mean'],label=f'{c} {w[0]} win Rolling Volatility')
    plt.plot(pool_vol['min_open'],pool_vol[f'roll_vol_{w[1]}_mean'],label=f'{c} {w[1]} win Rolling Volatility')
    plt.plot(pool_vol['min_open'],pool_vol[f'roll_vol_{w[2]}_mean'],label=f'{c} {w[2]} win Rolling Volatility')
    plt.xlabel('Lag (observations)')
    plt.ylabel(f'Rolling Std. Dev. of {c[8:]} Log Return')
    plt.title('EBX Rolling Volatility Clustering')
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(RESULTS_DIR/f'08_vol_cluster_{c}.png',dpi=150)
    plt.show()
    abs_acf_df = pd.read_csv(ACF_DIR/f'abs_{c}.csv')
    abs_acf_df = abs_acf_df[['lag','mean','median','std','min','max']].copy()
    abs_acf_df = abs_acf_df.rename(columns={
        'mean':'abs_acf_mean',
        'median':'abs_acf_median',
        'std':'abs_acf_std',
        'min':'abs_acf_min',
        'max':'abs_acf_max'
    })
    sq_acf_org = []
    for f in comp_files:
        df = pd.read_csv(RETURN_DIR/f'day{get_day_number(f)}_returns.csv',usecols=[c])
        acf_df = square_ACF(df[c],m)
        acf_df.insert(0,'day',get_day_number(f))
        sq_acf_org.append(acf_df)
    sq_acf_df = pd.concat(sq_acf_org,ignore_index=True)
    sq_acf_df = sq_acf_df.groupby('lag')['acf_sq'].agg(['mean','median','std','min','max']).reset_index()
    sq_acf_df = sq_acf_df.rename(columns={
        'mean':'sq_acf_mean',
        'median':'sq_acf_median',
        'std':'sq_acf_std',
        'min':'sq_acf_min',
        'max':'sq_acf_max'
    })
    vol_acf_df = abs_acf_df.merge(sq_acf_df,on='lag',how='inner')
    vol_acf_df.to_csv(VOL_DIR/f'vol_acf_{c}.csv',index=False)
    print('\nVOLATITLITY ACF:\n',vol_acf_df.head(20))
    plt.plot(vol_acf_df['lag'],vol_acf_df['abs_acf_mean'],label='ACF(|r|)')
    plt.plot(vol_acf_df['lag'],vol_acf_df['sq_acf_mean'],label='ACF(r**2)')
    plt.axhline(0,linewidth=1)
    plt.xlabel('Lag (observations)')
    plt.ylabel('Autocorrelation')
    plt.title(f'EBX Volatility Dependence — {c[8:]} Log Returns')
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(RESULTS_DIR/f'08_vol_acf_{c}.png',dpi=150)
    plt.show()
    print('\nSTRONGEST ACF(|r|):\n', vol_acf_df.sort_values('abs_acf_mean',ascending=False).head(10))
    print('\nSTRONGEST ACF(r**2):\n', vol_acf_df.sort_values('sq_acf_mean',ascending=False).head(10))

    



