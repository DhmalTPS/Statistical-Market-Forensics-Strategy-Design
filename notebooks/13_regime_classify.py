# ls; ls notebooks; ls results; ls output; ls output/03_day_returns; ls output/04_day_acf; ls output/05_intraday_season; ls output/07_sigma_events; ls output/08_vol_cluster; ls output/09_extreme_events; ls output/11_hurst_expo; ls output/12_regime_acf;
from pathlib import Path
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

def get_day_number(file):
    res = re.search(r'day[_\s]?(\d+)',file.stem,re.IGNORECASE)
    return int(res.group(1)) if res else None

def normalize_day(x):
    if pd.isna(x):return pd.NA
    if isinstance(x, (int, np.integer)): return int(x)
    if isinstance(x, (float, np.floating)): return int(x) if not np.isnan(x) else pd.NA
    s = str(x).strip().strip('{}')
    if s.isdigit(): return int(s)
    res = re.search(r'day[_\s]?(\d+)', s, re.IGNORECASE)
    return int(res.group(1)) if res else pd.NA

DATA_DIR = Path('EBX_Dataset')
OUTPUT_DIR = Path('output')
RESULTS_DIR = Path('results')

VR_FILE = OUTPUT_DIR / "10_variance_ratio.csv"
RETURN_DIR = OUTPUT_DIR / "03_day_returns"
ACF_DIR = OUTPUT_DIR / "04_day_acf"
HURST_DIR = OUTPUT_DIR / "11_hurst_expo"
REGACF_DIR = OUTPUT_DIR / "12_regime_acf"
REGIME_DIR = OUTPUT_DIR / "13_regime_classify"
REGIME_DIR.mkdir(parents=True, exist_ok=True)

csv_files = sorted(DATA_DIR.glob("*.csv"),key=get_day_number)
comp_files = [f for f in csv_files if get_day_number(f)<=85]
comp_keys = [get_day_number(f) for f in comp_files]
ret_files = sorted(RETURN_DIR.glob("day*_returns.csv"),key=get_day_number)

rvar = ['return_1s','return_1m','return_5m']
lvar = ['log_ret_1s','log_ret_1m','log_ret_5m']

ACF_CONFIG = {
    "log_ret_1s": {"lag": [300, 900, 1800], "lbl": ["5m", "15m", "30m"], "qvl":[2, 5, 30]},
    "log_ret_1m": {"lag": [1, 5, 30],  "lbl": ["1m", "5m", "30m"], "qvl":[2, 5, 30]},
    "log_ret_5m": {"lag": [1, 3, 6], "lbl": ["5m", "15m", "30m"], "qvl":[2, 5, 30]}
}

ALPHA = 0.05
HURST_LOW = 0.45
HURST_HIGH = 0.55

def classify_vr(vr,pv):
    if pd.isna(vr) or pd.isna(pv): return "INSUFFICIENT_EVIDENCE"
    if pv < ALPHA: 
        if vr<1: return "MEAN_REVERTING"
        elif vr>1: return "MOMENTUM"
    return "RANDOM_WALK_LIKE"

def classify_hur(h):
    if pd.isna(h): return "INSUFFICIENT_EVIDENCE"
    if h<HURST_LOW: return "MEAN_REVERTING"
    elif h>HURST_HIGH: return "MOMENTUM"
    else: return "RANDOM_WALK_LIKE"

def classify_acf(row,lag):
    nc = pc = 0
    for l in lag:
        acf_col = f'acf_{l}'
        p_col = f'p_{l}'
        if acf_col not in row.index: continue
        if p_col not in row.index: continue
        acf = row[acf_col]
        p = row[p_col]
        if pd.isna(acf) or pd.isna(p): continue
        if p<ALPHA: 
            if acf<0: nc+=1
            elif acf>0: pc+=1
    if nc==0 and pc==0: return "RANDOM_WALK_LIKE"
    if nc>pc: return "MEAN_REVERTING" 
    if nc<pc: return "MOMENTUM"
    return "MIXED_INCONCLUSIVE"

def final_regime(vr_reg, h_reg, acf_reg):
    reg = [vr_reg,h_reg,acf_reg]
    val = [x for x in reg if x in ["MEAN_REVERTING","RANDOM_WALK_LIKE","MOMENTUM"]]
    if len(val)==0: return "INSUFFICIENT_EVIDENCE"
    c = pd.Series(val).value_counts()
    top_reg = c.index[0]
    top_c = c.iloc[0]
    if top_c>=2: return top_reg
    return 'MIXED_INCONCLUSIVE'

vr_df = pd.read_csv(VR_FILE)
vr_df['day'] = vr_df['day'].apply(normalize_day).astype('Int64')
vr_df = vr_df.dropna(subset=['day'])          # <-- add this
vr_df['day'] = vr_df['day'].astype(int)       # optional: back to plain int, avoids Int64/NA merge quirks entirely
# vr_df['day'] = pd.to_numeric(vr_df['day'], errors='coerce').astype('Int64')
vr_df['VR_Regime_q'] = vr_df.apply(lambda row: classify_vr(row['VR'],row['p_val']), axis=1)
print('\nVR DATA:\n',vr_df.head())

table = []
summy = []

for col in lvar:
    hur_df = pd.read_csv(HURST_DIR/f'{col}_hurst_exp.csv')

    print(f"\n--- {col} hurst raw ---")
    print(hur_df.columns.tolist())
    print(hur_df[['day', 'hurst']].head(10))
    print("day dtype:", hur_df['day'].dtype)
    print("hurst non-null count:", hur_df['hurst'].notna().sum(), "/", len(hur_df))

    hur_df['day'] = hur_df['day'].apply(normalize_day).astype('Int64')
    hur_df = hur_df.dropna(subset=['day'])
    hur_df['day'] = hur_df['day'].astype(int)
    # hur_df['day'] = pd.to_numeric(hur_df['day'], errors='coerce').astype('Int64')
    hur_df['H_Regime'] = hur_df['hurst'].apply(classify_hur)
    acf_df = pd.read_csv(REGACF_DIR/f'{col}_reg_acf.csv')
    acf_df['day'] = acf_df['day'].apply(normalize_day).astype('Int64')
    acf_df = acf_df.dropna(subset=['day'])
    acf_df['day'] = acf_df['day'].astype(int)
    # acf_df['day'] = pd.to_numeric(acf_df['day'], errors='coerce').astype('Int64')
    acf_lag = ACF_CONFIG[col]['lag']
    acf_lbl = ACF_CONFIG[col]['lbl']
    acf_df['ACF_Regime'] = acf_df.apply(lambda row: classify_acf(row,acf_lag),axis=1)
    cur_vr = vr_df[vr_df['ret_series']==col].copy()
    cur_vr = cur_vr.sort_values(['day','q_val'])
    vr_row = []
    for d,g in cur_vr.groupby('day'):
        r = g['VR_Regime_q'].tolist()
        mr = r.count("MEAN_REVERTING")
        rw = r.count('RANDOM_WALK_LIKE')
        mo = r.count('MOMENTUM')
        c = {"MEAN_REVERTING": mr,"RANDOM_WALK_LIKE": rw, "MOMENTUM": mo}
        top_reg = max(c,key=c.get)
        top_c = c[top_reg]
        if top_c >= 2: vr_reg = top_reg
        else: vr_reg = 'MIXED_INCONCLUSIVE'
        row = {
            'day':d,
            'VR_Regime':vr_reg,
            'VR_MR_count':mr,
            'VR_RW_count':rw,
            'VR_MOM_count':mo
        }
        for q in ACF_CONFIG[col]['qvl']:
            qrow = g[g['q_val']==q]
            if len(qrow)==1:
                qrow = qrow.iloc[0]
                row[f"VR_q{q}"] = qrow["VR"]
                row[f"VR_stat_q{q}"] = qrow["VR_stats"]
                row[f"VR_p_q{q}"] = qrow["p_val"]
                row[f"VR_regime_q{q}"] = qrow["VR_Regime_q"]
            else:
                row[f"VR_q{q}"] = np.nan
                row[f"VR_stat_q{q}"] = np.nan
                row[f"VR_p_q{q}"] = np.nan
                row[f"VR_regime_q{q}"] = "INSUFFICIENT_EVIDENCE"
        vr_row.append(row)
    vr_sum = pd.DataFrame(vr_row)
    reg_df = vr_sum.merge(hur_df[['day', 'hurst', 'H_Regime']],on='day',how='outer')
    reg_df = reg_df.merge(acf_df,on='day',how='outer',suffixes=("","_acf"))
    reg_df['Final'] = reg_df.apply(lambda row: final_regime(
        row.get('VR_Regime','INSUFFICIENT_EVIDENCE'),
        row.get('H_Regime','INSUFFICIENT_EVIDENCE'),
        row.get('ACF_Regime','INSUFFICIENT_EVIDENCE'),
    ),axis=1)
    def agree_count(row):
        reg = [row.get('VR_Regime'),row.get('H_Regime'),row.get('ACF_Regime')]
        reg = [x for x in reg if x in ["MEAN_REVERTING","RANDOM_WALK_LIKE","MOMENTUM"]]
        if len(reg)==0: return 0
        return max(reg.count("MEAN_REVERTING"),reg.count("RANDOM_WALK_LIKE"),reg.count("MOMENTUM"))
    reg_df['Agreement_Count'] = reg_df.apply(agree_count,axis=1)
    reg_df['Agreement_Strength'] = reg_df['Agreement_Count'].map({3:'UNANIMOUS', 2:'MAJORITY', 1:'NO_CONSENSUS', 0:'NO_EVIDENCE'})
    reg_df.insert(1,'ret_series',col)
    reg_df = reg_df.sort_values('day').reset_index(drop=True)
    reg_df.to_csv(REGIME_DIR / f"reg_tab_{col}.csv",index=False)
    sum_df = reg_df['Final'].value_counts().reindex(["MEAN_REVERTING","RANDOM_WALK_LIKE","MOMENTUM","MIXED_INCONCLUSIVE","INSUFFICIENT_EVIDENCE"],fill_value=0).rename_axis('regime').reset_index(name='count')
    sum_df['fraction'] = sum_df['count']/len(reg_df)
    sum_df.insert(0,'ret_series',col)
    sum_df.to_csv(REGIME_DIR / f"reg_sum_{col}.csv",index=False) 
    table.append(reg_df)
    summy.append(sum_df)
    #print("\nREGIME TABLE:\n",reg_df[["day","VR_Regime","H_Regime","ACF_Regime","Final","Agreement_Count","Agreement_Strength"]].to_string(index=False))
    plt.hist(cur_vr[cur_vr['q_val']==5].copy()['VR'].dropna(),bins=20)
    plt.axvline(1,linestyle='--',linewidth=1)
    plt.xlabel('Variance Ratio')
    plt.ylabel('Number of Days')
    plt.title(f'EBX Variance Ratio Distribution - {col}')
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / f"{col}_vr_dist.png",dpi=150)
    plt.show()
    plt.hist(hur_df['hurst'].dropna(),bins=20)
    plt.axvline(0.5,linestyle='--',linewidth=1)
    plt.xlabel("Hurst Exponent")
    plt.ylabel("Number of Days")
    plt.title(f"EBX Hurst Exponent Distribution — {col}")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / f"{col}_hur_dist.png",dpi=150)
    plt.show()
    plot_sum = sum_df[sum_df['regime'].isin(["MEAN_REVERTING","RANDOM_WALK_LIKE","MOMENTUM","MIXED_INCONCLUSIVE"])]
    plt.bar(plot_sum['regime'],plot_sum['count'])
    plt.xlabel("Regime")
    plt.ylabel("Number of Days")
    plt.title(f"EBX Regime Classification — {col}")
    plt.xticks(rotation=20)
    plt.grid(axis='y',alpha=0.3)
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / f"{col}_reg_count.png",dpi=150)
    plt.show()

tcom_df = pd.concat(table,ignore_index=True)
tcom_df = tcom_df.sort_values(['day','ret_series']).reset_index(drop=True)
tcom_df.to_csv(OUTPUT_DIR/"13_regime_cum_table.csv",index=False)
scom_df = pd.concat(summy,ignore_index=True)
scom_df.to_csv(OUTPUT_DIR/"13_regime_sum_table.csv",index=False)

print("\nShape:\n",tcom_df.shape)
print("\nDays:\n",sorted(tcom_df["day"].dropna().unique()))
print("\nReturn frequencies:\n",tcom_df["ret_series"].unique())
print("\nFinal regime counts:\n",tcom_df.groupby(["ret_series","Final"]).size())