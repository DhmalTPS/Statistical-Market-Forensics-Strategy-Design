from pathlib import Path
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def get_day_number(file):
    res = re.search(r'day[_\s]?(\d+)',file.stem,re.IGNORECASE)
    return int(res.group(1)) if res else None

DATA_DIR = Path(r'.\EBX_Dataset')
OUTPUT_DIR = Path(r'.\output')
RESULTS_DIR = Path(r'.\results')
RETURN_DIR = OUTPUT_DIR / "03_day_returns"
ACF_DIR = OUTPUT_DIR / "04_day_acf"
ACF_DIR.mkdir(parents=True,exist_ok=True)

csv_files = sorted(DATA_DIR.glob("*.csv"),key=get_day_number)
comp_files = [f for f in csv_files if get_day_number(f)<=85]
comp_keys = [get_day_number(f) for f in comp_files]
var = ['return_1s','return_1m','return_5m','log_ret_1s','log_ret_1m','log_ret_5m']

def autocorrelation(col,mx=60):
    s = col.dropna().to_numpy()
    r = col.dropna().abs().to_numpy()
    res = []
    for l in range(1,mx+1):
        res.append({
            'lag': l,
            'acf': np.corrcoef(s[l:],s[:-l])[0,1],
            'abs_acf': np.corrcoef(r[l:],r[:-l])[0,1]
        })
    return pd.DataFrame(res)

def day_acf(file,col,mx):
    df = pd.read_csv(RETURN_DIR/f'day{get_day_number(file)}_returns.csv')
    acf_df = autocorrelation(df[col],mx)
    acf_df.insert(0,'day',get_day_number(file))
    return acf_df

for c in var:
    acf_org = [day_acf(f,c,60) for f in comp_files]
    acf_df  = pd.concat(acf_org,ignore_index=True)
    acf_df['acf__abs'] = acf_df['acf'].abs()

    sum_df = acf_df.groupby('lag')['acf'].agg(['mean','median','std','min','max']).reset_index()
    abs_df = acf_df.groupby('lag')['abs_acf'].agg(['mean','median','std','min','max']).reset_index()

    print(acf_df.head(20),'\nShape:',acf_df.shape)
    print(sum_df.head(20),'\nShape:',sum_df.shape)

    print('STRONGEST\n',acf_df.sort_values('acf__abs',ascending=False).head(20))
    print('MOST POSITIVE:\n',acf_df.sort_values('acf',ascending=False).head(20))
    print('MOST NEGATIVE:\n',acf_df.sort_values('acf',ascending=True).head(20))

    sum_df.to_csv(ACF_DIR/f'sum_{c}.csv', index=False)
    acf_df.to_csv(ACF_DIR/f'acf_{c}.csv', index=False)
    abs_df.to_csv(ACF_DIR/f'abs_{c}.csv', index=False)

    plt.plot(sum_df['lag'], sum_df['mean'], label='Mean ACF')
    plt.plot(sum_df['lag'], sum_df['mean']+sum_df['std'], label='+1 std')
    plt.plot(sum_df['lag'], sum_df['mean']-sum_df['std'], label='-1 std')
    plt.plot(abs_df['lag'], abs_df['mean'], label='ACF(abs)')
    plt.axhline(0,linewidth=1)

    plt.xlabel('Lag (second)')
    plt.ylabel('Autocorrelation')
    plt.title(f'Pooled {c} AC')
    plt.savefig(RESULTS_DIR/f'04_acf_{c}.png')
    plt.show()

# Understand 1m, 5m returns are straight lines
