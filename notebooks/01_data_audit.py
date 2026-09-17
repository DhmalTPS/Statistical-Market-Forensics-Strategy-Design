from pathlib import Path
import re
import pandas as pd

def get_day_number(path):
    match = re.search(r'day[_\s]?(\d+)',path.stem, re.IGNORECASE)
    return int(match.group(1)) if match else None

DATA_DIR = Path(r".\.\EBX_Dataset")
OUTPUT_DIR = Path(r".\.\output")
csv_files = sorted(DATA_DIR.glob("*.csv"),key=get_day_number)
comp_files = [f for f in csv_files if get_day_number(f)<=85]
comp_keys = [get_day_number(f) for f in comp_files]

print("CSV Files Count:",len(csv_files),'\n')
print("Comp Files Count:",len(comp_files),'\n')
for f in csv_files: print(F"{get_day_number(f)}.) ",f.name)
for f in comp_files: print(F"{get_day_number(f)}.) ",f.name)

# print("\n\n\n\t____________________________\n\t###___ DAY 1 ANALYSIS ___###\n\n\n")

# df001 = pd.read_csv(csv_files[0])
# print(df001.info(),'\n',df001.columns.tolist())
# print(df001.head(),'\n',df001.tail())

# print('\nShape:',df001.shape)
# print('Datatypes:',df001.dtypes)

# print('Missing Values:',df001.isna().sum())
# print('Duplicate Row:', df001.duplicated().sum())
# print('Duplicate Timestamps:', df001['Time'].duplicated().sum())

# print('Non-Postive Prices:',(df001['Price']<=0).sum())
# print(f'Price Summary:\n{df001['Price'].describe()}')

# print(f'Time Sample:\n{df001['Time'].head(10)}')
# print('Time Datatype:',df001['Time'].dtype)
# print('First Timestamp:',df001['Time'].iloc[0])
# print('Last Timestamp:',df001['Time'].iloc[-1])

# t001 = pd.to_datetime(df001['Time'],format="%H:%M:%S")
# print(f'Converted Time:\n{t001.head()}')

# print('Time Difference:',t001.diff().value_counts().head(10))
# print('Non 1s Gaps:',(t001.diff().dropna()!=pd.Timedelta(seconds=1)).sum())
# print('Time Monotonicity Check:', t001.is_monotonic_increasing)

# print('Expected Timestamps:',len(pd.date_range(start=t001.iloc[0],end=t001.iloc[-1],freq='1s')))
# print('Actual Timestamps:  ',len(t001))
# print('Missing Timestamps: ',len(pd.date_range(start=t001.iloc[0],end=t001.iloc[-1],freq='1s').difference(t001)))

# del_p001 = df001['Price'].diff()
# r001_1s = df001['Price'].pct_change()
# print(f'1s Return Summary:\n{r001_1s.describe()}')
# print(f'Largest Abs(1sR):\n{r001_1s.abs().sort_values(ascending=False).head(20)}')

# eq_p001 = df001['Price'].eq(df001['Price'].shift())
# gr_p001 = eq_p001.ne(eq_p001.shift()).cumsum()
# fl_p001 = eq_p001.groupby(gr_p001).sum()
# print('Consecutive Indentical Price:',eq_p001.sum())
# print(f'Longest Flat Stretches:\n{fl_p001[fl_p001>0].sort_values(ascending=False).head(20)}')

# miss_col001 = df001.isna().sum()
# fidx_col001 = df001.apply(lambda col:col.first_valid_index())
# print(f'Missing Values Columns:\n{miss_col001[miss_col001>0].sort_values(ascending=False)}')
# print(f'First Valid Index:\n{fidx_col001.head(50)}')

def audit_day(file):
    df = pd.read_csv(file)
    t = pd.to_datetime(df['Time'],format='%H:%M:%S')
    r = df['Price'].pct_change()
    eq_p = df['Price'].eq(df['Price'].shift())
    gr_p = eq_p.ne(eq_p.shift()).cumsum()
    fl_p = eq_p.groupby(gr_p).sum()
    return {
        'day': get_day_number(file),
        'rows': len(df),
        'columns':len(df.columns),
        ########
        'first_time': df['Time'].iloc[0],
        'last_time': df['Time'].iloc[-1],
        'missing_timestamps': len(pd.date_range(t.iloc[0],t.iloc[-1],freq='1s').difference(t)),
        'duplicate_timestamp': df['Time'].duplicated().sum(),
        'non_1s_gaps': (t.diff().dropna()!=pd.Timedelta(seconds=1)).sum(),
        'monotonic_time': t.is_monotonic_increasing,
        ########
        'price_nan': df['Price'].isna().sum(),
        'nonpos_prices': (df['Price']<=0).sum(),
        'price_min': df['Price'].min(),
        'price_max': df['Price'].max(),
        'price_mean': df['Price'].mean(),
        'price_std': df['Price'].std(),
        ########
        'return_1s_mean': r.mean(),
        'return_1s_std': r.std(),
        'return_1s_min': r.min(),
        'return_1s_max': r.max(),
        'zero_return_frac': (r==0).mean(),
        'max_abs_return': r.abs().max(),
        ########
        'number_of_unchanged_transitions': eq_p.sum(),
        'long_flat_stretch': fl_p.max()
    }

audit_res = [audit_day(f) for f in comp_files]
audit_df = pd.DataFrame(audit_res)
print(audit_df)
audit_df.to_csv(OUTPUT_DIR/"audit_days.csv")

def feature_missingness(file):
    df = pd.read_csv(file)
    fea = df.columns[2:]
    res = pd.DataFrame({
        'feature':fea,
        'missing_count':df[fea].isna().sum().values,
        'missing_fraction': df[fea].isna().mean().values,
        'first_valid_index':df[fea].apply(lambda col: col.first_valid_index()).values
    })
    return res[res['missing_count']>0].sort_values('missing_count',ascending=False)

feat_miss_org = [feature_missingness(f) for f in comp_files]
feat_miss_df = pd.concat(feat_miss_org,keys=comp_keys,names=['day'])
print(feat_miss_df.head(60))
feat_miss_df.to_csv(OUTPUT_DIR/"feature_missing.csv")

def extreme_moves(file):
    df = pd.read_csv(file)
    r = df['Price'].pct_change()
    return pd.DataFrame({
        'day': get_day_number(file),
        'timestamp': df['Time'],
        'price_before': df['Price'].shift(),
        'price_after':df['Price'],
        'return': r,
        'abs_return': r.abs()
    }).sort_values('abs_return',ascending=False)

extreme_org = [extreme_moves(f).head(25) for f in comp_files]
extreme_df = pd.concat(extreme_org,keys=comp_keys,names=['day'])
print(extreme_df.sort_values('abs_return', ascending=False).head(60))
extreme_df.to_csv(OUTPUT_DIR/"extreme_moves.csv")

