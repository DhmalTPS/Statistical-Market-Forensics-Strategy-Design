# ls; ls notebooks; ls results; ls output

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
    if pd.isna(x): return pd.NA
    if isinstance(x,(int,np.integer)): return int(x)
    if isinstance(x,(float,np.floating)): return int(x) if not np.isnan(x) else pd.NA
    s = str(x).strip().strip('{}')
    if s.isdigit(): return int(s)
    res = re.search(r'day[_\s]?(\d+)',s,re.IGNORECASE)
    return int(res.group(1)) if res else pd.NA


DATA_DIR = Path('EBX_Dataset')
OUTPUT_DIR = Path('output')
RESULTS_DIR = Path('results')
INV_FILE = OUTPUT_DIR / "15_feature_inventory.csv"
MISS_FILE = OUTPUT_DIR / "15_feature_missing.csv"

HYP_FILE = OUTPUT_DIR / "16_feature_hypotheses.csv"
MATCH_FILE = OUTPUT_DIR / "16_feature_matching.csv"
LAG_FILE = OUTPUT_DIR / "16_feature_lag_matching.csv"
DOSSIER_FILE = OUTPUT_DIR / "16_FEATURE_DOSSIER.md"

SAMPLE_ROWS = 5000
MAX_LAG = 60
TOP_MATCHES = 5

csv_files = sorted(DATA_DIR.glob("*.csv"),key=get_day_number)
comp_files = [f for f in csv_files if get_day_number(f) is not None and get_day_number(f)<=85]
comp_keys = [get_day_number(f) for f in comp_files]

inv_df = pd.read_csv(INV_FILE)
inv_df['days_present'] = pd.to_numeric(inv_df['days_present'],errors='coerce')
inv_df['days_missing'] = pd.to_numeric(inv_df['days_missing'],errors='coerce')
inv_df['T'] = pd.to_numeric(inv_df['T'],errors='coerce')
inv_df['first_valid_index_min'] = pd.to_numeric(inv_df['first_valid_index_min'],errors='coerce')
inv_df['first_valid_index_max'] = pd.to_numeric(inv_df['first_valid_index_max'],errors='coerce')

feat_df = inv_df[inv_df['feature'].notna()].copy()
feat_df['family'] = feat_df['feature'].str.extract(r'^([A-Z]+)')[0]
feat_df['base'] = feat_df['feature'].str.extract(r'^([A-Z]+\d+)')[0]

pb_feats = feat_df[feat_df['family']=='PB']['feature'].tolist()
vb_feats = feat_df[feat_df['family']=='VB']['feature'].tolist()

print("\nFiles found:",len(csv_files))
print("Days used:",len(comp_files))
print("Day range:",min(comp_keys),"-",max(comp_keys))
print("PB features:",len(pb_feats))
print("VB features:",len(vb_feats))


# ------------------------------------------------------------
# 4B — T FORENSICS
# ------------------------------------------------------------

T_ROWS = []

for file in comp_files:
    d = get_day_number(file)
    df = pd.read_csv(file)

    cols = [c for c in feat_df['feature'] if c in df.columns]
    if 'Time' in df.columns: cols = ['Time'] + cols
    if 'Price' in df.columns: cols = ['Price'] + cols

    df = df[cols]

    if len(df)>SAMPLE_ROWS:
        df = df.iloc[np.linspace(0,len(df)-1,SAMPLE_ROWS).astype(int)]

    for fam in ['PB','VB']:
        fcols = [c for c in feat_df.loc[feat_df['family']==fam,'feature'] if c in df.columns]

        for base,g in feat_df[feat_df['family']==fam].groupby('base'):
            tc = [c for c in g['feature'].tolist() if c in df.columns]
            if len(tc)<2: continue

            x = df[tc].apply(pd.to_numeric,errors='coerce')
            corr = x.corr(method='pearson')

            for i in range(len(tc)):
                for j in range(i+1,len(tc)):
                    a = x[tc[i]]
                    b = x[tc[j]]
                    z = pd.concat([a,b],axis=1).dropna()

                    if len(z)<20:
                        continue

                    p = z.iloc[:,0]
                    q = z.iloc[:,1]

                    T_ROWS.append({
                        'day':d,
                        'family':fam,
                        'base':base,
                        'feature_1':tc[i],
                        'feature_2':tc[j],
                        'pearson':corr.loc[tc[i],tc[j]],
                        'spearman':stats.spearmanr(p,q).statistic,
                        'scale_1':p.std(),
                        'scale_2':q.std(),
                        'mean_1':p.mean(),
                        'mean_2':q.mean(),
                        'mae':np.mean(np.abs(p-q)),
                        'rmse':np.sqrt(np.mean((p-q)**2)),
                        'n':len(z)
                    })

t_df = pd.DataFrame(T_ROWS)

if len(t_df):
    t_sum = t_df.groupby(['family','base','feature_1','feature_2'],as_index=False).agg({
        'pearson':'median',
        'spearman':'median',
        'scale_1':'median',
        'scale_2':'median',
        'mean_1':'median',
        'mean_2':'median',
        'mae':'median',
        'rmse':'median',
        'n':'sum'
    })
else:
    t_sum = pd.DataFrame()

print("\n--- T CORRELATION SUMMARY ---")
if len(t_sum):
    print(t_sum.sort_values(['family','base','pearson'],ascending=[True,True,False]).head(30).to_string(index=False))
else:
    print("No sufficient T-pair observations.")


# ------------------------------------------------------------
# 4C — CANDIDATE FEATURE LIBRARY
# ------------------------------------------------------------

WINDOWS = [5,10,30,60,90,120,300,600,900,1500,1800,3600]

def candidate_features(p):
    c = {}

    p = pd.to_numeric(p,errors='coerce')

    for w in WINDOWS:
        r = p.rolling(w,min_periods=w)

        c[f'rolling_mean_{w}'] = r.mean()
        c[f'rolling_std_{w}'] = r.std()
        c[f'rolling_min_{w}'] = r.min()
        c[f'rolling_max_{w}'] = r.max()
        c[f'sma_{w}'] = r.mean()
        c[f'momentum_{w}'] = p-p.shift(w)
        c[f'rolling_return_{w}'] = p.pct_change(w)
        c[f'log_return_{w}'] = np.log(p/p.shift(w))
        c[f'price_minus_ma_{w}'] = p-r.mean()
        c[f'price_ma_ratio_{w}'] = p/r.mean()-1
        c[f'drawdown_{w}'] = p/r.max()-1
        c[f'range_{w}'] = r.max()-r.min()

        sd = r.std()
        c[f'zscore_{w}'] = (p-r.mean())/sd.replace(0,np.nan)

        a = 2/(w+1)
        c[f'ema_{w}'] = p.ewm(alpha=a,adjust=False,min_periods=w).mean()

    return pd.DataFrame(c,index=p.index)


# ------------------------------------------------------------
# 4D + 4F — MATCHING + SCALE / TRANSFORMATION
# ------------------------------------------------------------

MATCH_ROWS = []
LAG_ROWS = []

for file in comp_files:
    d = get_day_number(file)
    df = pd.read_csv(file)

    if 'Price' not in df.columns:
        continue

    if len(df)>SAMPLE_ROWS:
        ix = np.linspace(0,len(df)-1,SAMPLE_ROWS).astype(int)
        df = df.iloc[ix].reset_index(drop=True)

    p = pd.to_numeric(df['Price'],errors='coerce')
    cand = candidate_features(p)

    fcols = [c for c in feat_df['feature'] if c in df.columns]

    for f in fcols:
        x = pd.to_numeric(df[f],errors='coerce')

        for c in cand.columns:
            z = pd.concat([x,cand[c]],axis=1).dropna()

            if len(z)<100:
                continue

            a = z.iloc[:,0].to_numpy()
            b = z.iloc[:,1].to_numpy()

            if np.std(a)==0 or np.std(b)==0:
                continue

            pear = stats.pearsonr(a,b).statistic
            spear = stats.spearmanr(a,b).statistic

            beta,alpha = np.polyfit(b,a,1)
            pred = beta*b+alpha

            mae = np.mean(np.abs(a-pred))
            rmse = np.sqrt(np.mean((a-pred)**2))

            MATCH_ROWS.append({
                'day':d,
                'feature':f,
                'family':feat_df.loc[feat_df['feature']==f,'family'].iloc[0],
                'base':feat_df.loc[feat_df['feature']==f,'base'].iloc[0],
                'T':feat_df.loc[feat_df['feature']==f,'T'].iloc[0],
                'candidate':c,
                'pearson':pear,
                'spearman':spear,
                'beta':beta,
                'alpha':alpha,
                'mae':mae,
                'rmse':rmse,
                'feature_scale':np.std(a),
                'candidate_scale':np.std(b),
                'n':len(z)
            })

            for lag in range(1,MAX_LAG+1):
                if len(a)<=lag+20:
                    continue

                aa = a[lag:]
                bb = b[:-lag]

                if np.std(aa)==0 or np.std(bb)==0:
                    continue

                lc = np.corrcoef(aa,bb)[0,1]

                LAG_ROWS.append({
                    'day':d,
                    'feature':f,
                    'candidate':c,
                    'lag':lag,
                    'lag_corr':lc,
                    'n':len(aa)
                })

match_df = pd.DataFrame(MATCH_ROWS)
lag_df = pd.DataFrame(LAG_ROWS)

print("\n--- MATCHING ---")
print("Matching rows:",len(match_df))
print("Lag rows:",len(lag_df))


# ------------------------------------------------------------
# CROSS-DAY AGGREGATION
# ------------------------------------------------------------

if len(match_df):

    msum = match_df.groupby(
        ['feature','family','base','T','candidate'],
       as_index=False
    ).agg({
        'pearson':'median',
        'spearman':'median',
        'beta':'median',
        'alpha':'median',
        'mae':'median',
        'rmse':'median',
        'feature_scale':'median',
        'candidate_scale':'median',
        'n':'sum',
        'day':'nunique'
    })

    msum['abs_pearson'] = msum['pearson'].abs()
    msum['abs_spearman'] = msum['spearman'].abs()

    msum['score'] = (
        0.45*msum['abs_pearson'] +
        0.35*msum['abs_spearman'] -
        0.10*(msum['mae']/(msum['feature_scale']+1e-12)) -
        0.10*(msum['rmse']/(msum['feature_scale']+1e-12))
    )

    msum = msum.sort_values(
        ['feature','score'],
       ascending=[True,False]
    ).reset_index(drop=True)

else:
    msum = pd.DataFrame()


# ------------------------------------------------------------
# LAG MATCHING SUMMARY
# ------------------------------------------------------------

if len(lag_df):

    lsum = lag_df.groupby(
        ['feature','candidate','lag'],
       as_index=False
    ).agg({
        'lag_corr':'median',
        'n':'sum',
        'day':'nunique'
    })

    lsum['abs_lag_corr'] = lsum['lag_corr'].abs()

    lbest = lsum.sort_values(
        ['feature','abs_lag_corr'],
       ascending=[True,False]
    ).groupby('feature',as_index=False).head(5)

else:
    lsum = pd.DataFrame()
    lbest = pd.DataFrame()


# ------------------------------------------------------------
# BEST HYPOTHESES
# ------------------------------------------------------------

if len(msum):

    best = msum.groupby('feature',as_index=False).head(TOP_MATCHES).copy()

    rows = []

    for f,g in best.groupby('feature'):

        g = g.sort_values('score',ascending=False).reset_index(drop=True)
        b = g.iloc[0]

        if len(g)>=2:
            gap = b['score']-g.iloc[1]['score']
        else:
            gap = np.nan

        if b['abs_pearson']>=0.95 and b['abs_spearman']>=0.95 and gap>=0.02:
            conf = 'HIGH'
        elif b['abs_pearson']>=0.80 and b['abs_spearman']>=0.80:
            conf = 'MEDIUM'
        else:
            conf = 'LOW'

        rows.append({
            'feature':f,
            'family':b['family'],
            'base':b['base'],
            'T':b['T'],
            'best_candidate':b['candidate'],
            'pearson':b['pearson'],
            'spearman':b['spearman'],
            'beta':b['beta'],
            'alpha':b['alpha'],
            'mae':b['mae'],
            'rmse':b['rmse'],
            'score':b['score'],
            'score_gap':gap,
            'days':b['day'],
            'confidence':conf
        })

    hyp_df = pd.DataFrame(rows)

else:
    hyp_df = pd.DataFrame()


# ------------------------------------------------------------
# SAVE
# ------------------------------------------------------------

if len(msum):
    msum.to_csv(MATCH_FILE,index=False)

if len(lsum):
    lsum.to_csv(LAG_FILE,index=False)

if len(hyp_df):
    hyp_df.to_csv(HYP_FILE,index=False)

print("\n--- BEST HYPOTHESES ---")
if len(hyp_df):
    print(
        hyp_df[
            ['feature','best_candidate','pearson','spearman',
             'beta','alpha','rmse','score','confidence']
        ].to_string(index=False)
    )
else:
    print("No hypotheses generated.")


# ------------------------------------------------------------
# 4G — FEATURE DOSSIER
# ------------------------------------------------------------

lines = []

lines.append("# EBX FEATURE FORENSICS DOSSIER\n")
lines.append("## Task 4 — Reverse Engineering of PB / VB Features\n")
lines.append(
    f"\nFiles used: {len(comp_files)} "
    f"(Days 1–64 and 80–85)\n"
)
lines.append(
    f"Feature count: {len(feat_df)} "
    f"(PB={len(pb_feats)}, VB={len(vb_feats)})\n"
)

lines.append("\n## Methodology\n")
lines.append(
    "- T structure investigated using within-base correlation, scale and missingness behaviour.\n"
)
lines.append(
    "- Candidate features generated only from raw Price.\n"
)
lines.append(
    "- Candidate windows tested at: "
    + ", ".join(map(str,WINDOWS))
    + ".\n"
)
lines.append(
    "- Matching uses Pearson, Spearman, affine beta/alpha, MAE and RMSE.\n"
)
lines.append(
    "- Lagged correlations are tested separately.\n"
)
lines.append(
    "- No feature identity is declared solely from high correlation.\n"
)

if len(hyp_df):

    for fam in ['PB','VB']:

        lines.append(f"\n# {fam}\n")

        hf = hyp_df[hyp_df['family']==fam].copy()

        for base,g in hf.groupby('base'):

            lines.append(f"\n## {base}\n")

            for _,r in g.sort_values('T').iterrows():

                lines.append(
                    f"\n### {r['feature']}\n"
                )

                lines.append(
                    f"- T = {r['T']}\n"
                    f"- Best hypothesis = `{r['best_candidate']}`\n"
                    f"- Pearson = {r['pearson']:.6f}\n"
                    f"- Spearman = {r['spearman']:.6f}\n"
                    f"- beta = {r['beta']:.6g}\n"
                    f"- alpha = {r['alpha']:.6g}\n"
                    f"- MAE = {r['mae']:.6g}\n"
                    f"- RMSE = {r['rmse']:.6g}\n"
                    f"- Score = {r['score']:.6f}\n"
                    f"- Confidence = **{r['confidence']}**\n"
                )

                if len(lbest):

                    lg = lbest[
                        lbest['feature']==r['feature']
                    ]

                    if len(lg):
                        lr = lg.iloc[0]
                        lines.append(
                            f"- Best lag = {int(lr['lag'])} "
                            f"with lag correlation = {lr['lag_corr']:.6f}\n"
                        )

else:
    lines.append(
        "\nNo sufficiently strong feature hypotheses were generated.\n"
    )

lines.append("\n## Interpretation Rule\n")
lines.append(
    "A candidate is treated as a hypothesis rather than a confirmed identity. "
    "High correlation, stable affine parameters and low reconstruction error "
    "across days increase confidence; isolated correlation does not.\n"
)

DOSSIER_FILE.write_text(''.join(lines),encoding='utf-8')


# ------------------------------------------------------------
# PLOTS
# ------------------------------------------------------------

if len(t_sum):

    for fam in ['PB','VB']:

        x = t_sum[t_sum['family']==fam].copy()

        if len(x)==0:
            continue

        q = x.groupby('base')['pearson'].mean().sort_values(ascending=False)

        plt.bar(q.index,q.values)
        plt.xlabel("Feature base")
        plt.ylabel("Mean pairwise Pearson correlation")
        plt.title(f"EBX {fam} Within-Base T Correlation")
        plt.xticks(rotation=45)
        plt.grid(axis='y',alpha=0.3)
        plt.tight_layout()
        plt.savefig(
            RESULTS_DIR/f"16_{fam.lower()}_T_correlation.png",
           dpi=150
        )
        plt.show()


if len(hyp_df):

    q = hyp_df.groupby('confidence').size()

    plt.bar(q.index,q.values)
    plt.xlabel("Confidence")
    plt.ylabel("Number of features")
    plt.title("EBX Feature Forensics Confidence")
    plt.grid(axis='y',alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        RESULTS_DIR/"16_feature_confidence.png",
       dpi=150
    )
    plt.show()


print("\n--- FILES WRITTEN ---")
print(HYP_FILE)
print(MATCH_FILE)
print(LAG_FILE)
print(DOSSIER_FILE)

print("\nHypotheses:",len(hyp_df))
print("Matching rows:",len(match_df))
print("Lag matching rows:",len(lag_df))

if len(hyp_df):
    print("\nConfidence counts:")
    print(hyp_df['confidence'].value_counts())

print("\nDone.")