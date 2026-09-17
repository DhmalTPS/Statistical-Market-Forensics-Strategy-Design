from pathlib import Path
import re
import numpy as np
import pandas as pd

def get_day_number(file):
    res = re.search(r'day[_\s]?(\d+)',file.stem,re.IGNORECASE)
    return int(res.group(1)) if res else None

DATA_DIR = Path(r'.\EBX_Dataset')
OUTPUT_DIR = Path(r'.\output')
RETURN_DIR = OUTPUT_DIR / "03_day_returns"
EDA_DIR = OUTPUT_DIR / "03_returns_eda.csv"
RETURN_DIR.mkdir(parents=True,exist_ok=True)

csv_files = sorted(DATA_DIR.glob("*.csv"),key=get_day_number)
comp_files = [f for f in csv_files if get_day_number(f)<=85]
comp_keys = [get_day_number(f) for f in comp_files]
var = ['return_1s','return_1m','return_5m','log_ret_1s','log_ret_1m','log_ret_5m']

# --------------------------------------------------
# PHASE 10 — RETURNS
# --------------------------------------------------

def calculate_returns(file):
    df = pd.read_csv(file)
    df['return_1s'] = df['Price'].pct_change(1)
    df['return_1m'] = df['Price'].pct_change(60)
    df['return_5m'] = df['Price'].pct_change(300)
    df['log_ret_1s'] = np.log(df['Price']/df['Price'].shift(1))
    df['log_ret_1m'] = np.log(df['Price']/df['Price'].shift(60))
    df['log_ret_5m'] = np.log(df['Price']/df['Price'].shift(300))
    return df[['Time','Price']+var].copy()

for f in comp_files:
    calculate_returns(f).to_csv(RETURN_DIR/f"day{get_day_number(f)}_returns.csv",index=False)
    print(f'Day {get_day_number(f)}: returns calculated')

test = pd.read_csv(RETURN_DIR / "day1_returns.csv")
print(test.head(65))
print(test[['return_1s', 'return_1m', 'return_5m']].isna().sum())
print(test[['return_1s', 'return_1m', 'return_5m']].isna().sum())

# --------------------------------------------------
# PHASE 11 — PER-DAY EDA
# --------------------------------------------------

def return_statistics(file):
    df = pd.read_csv(RETURN_DIR/f'day{get_day_number(file)}_returns.csv')
    res = []
    for v in ['Price']+var:
        s = df[v].dropna()
        res.append({
            'day':get_day_number(file),
            'variable':v,
            'mean':s.mean(),
            'median':s.median(),
            'std':s.std(),
            'skew':s.skew(),
            'kurtosis': s.kurtosis()
        })
    return pd.DataFrame(res)

ret_eda_org = [return_statistics(f) for f in comp_files]
ret_eda_df  = pd.concat(ret_eda_org,ignore_index=True)
print(ret_eda_df.head(20),'\nShape:',ret_eda_df.shape)
ret_eda_df.to_csv(EDA_DIR,index=False)

vol_org = ret_eda_df[ret_eda_df['variable'].isin(var)] [['day','variable','std']]
vol_sort = vol_org.sort_values(['variable','std'],ascending=[True,False]).groupby('variable')
print(vol_sort.head(10))

# --------------------------------------------------
# PHASE 12 — POOLED ANALYSIS
# --------------------------------------------------

def pooled_statistics(df):
    res= []
    for v in var:
        s = df[v].dropna()
        res.append({
            'variable': v,
            'count': s.count(),
            'mean': s.mean(),
            'median': s.median(),
            'std': s.std(),
            'skew': s.skew(),
            'kurtosis': s.kurtosis(),
            'min': s.min(),
            'max': s.max(),
            'q01': s.quantile(0.01),
            'q05': s.quantile(0.05),
            'q25': s.quantile(0.25),
            'q50': s.quantile(0.50),
            'q75': s.quantile(0.75),
            'q95': s.quantile(0.95),
            'q99': s.quantile(0.99)
        })
    return pd.DataFrame(res)

def pooled_direction(df):
    res = []
    for v in var:
        s = df[v].dropna()
        res.append({
            'variable':v,
            'pos_fraction':(s>0).mean(),
            'neg_fraction':(s<0).mean(),
            'zero_fraction':(s==0).mean()
        })
    return pd.DataFrame(res)

def pooled_extremes(df):
    res = []
    for v in var:
            s = df[v].dropna()
            res.append({
                'variable': v,
                'large_pos': s.max(),
                'large_neg': s.min(),
                'large_abs': s.abs().max(),
                'abs_percentile_990':s.abs().quantile(0.990),
                'abs_percentile_999':s.abs().quantile(0.999)
            })
    return pd.DataFrame(res)


pool_ret_org = []
for f in comp_files:
    df = pd.read_csv(RETURN_DIR/f'day{get_day_number(f)}_returns.csv')
    df['day'] = get_day_number(f)
    pool_ret_org.append(df[['day','Time','Price']+var])
    
pool_ret_df = pd.concat(pool_ret_org,ignore_index=True)
print(pool_ret_df.head())
print(pool_ret_df.tail(),'\nShape:',pool_ret_df.shape)
pool_ret_df.to_csv(OUTPUT_DIR/'03_pooled_returns.csv',index=False)

pooled_statistics(pool_ret_df).to_csv(OUTPUT_DIR/'03_pooled_statistics.csv',index=False)
pooled_direction(pool_ret_df).to_csv(OUTPUT_DIR/'03_pooled_direction.csv',index=False)
pooled_extremes(pool_ret_df).to_csv(OUTPUT_DIR/'03_pooled_extremes.csv',index=False)
print(pd.read_csv(OUTPUT_DIR/'03_pooled_statistics.csv'))
print(pd.read_csv(OUTPUT_DIR/'03_pooled_direction.csv'))
print(pd.read_csv(OUTPUT_DIR/'03_pooled_extremes.csv'))