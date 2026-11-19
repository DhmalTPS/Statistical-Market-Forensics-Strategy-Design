# FILE 16

from pathlib import Path
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

try:
    import torch
    GPU_OK = torch.cuda.is_available()
except Exception:
    torch = None
    GPU_OK = False


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

HYP_FILE = OUTPUT_DIR / "16_feature_hypotheses.csv"
MATCH_FILE = OUTPUT_DIR / "16_feature_matching.csv"
LAG_FILE = OUTPUT_DIR / "16_feature_lag_matching.csv"
T_FILE = OUTPUT_DIR / "16_T_structure.csv"
DOSSIER_FILE = OUTPUT_DIR / "16_FEATURE_DOSSIER.md"

WINDOWS = [5,10,30,60,90,120,300,600,900,1500,1800,3600]

MAX_LAG = 60
TOP_MATCHES = 5
TOP_LAG_CAND = 3

MIN_N = 100
GPU_BATCH = 64

csv_files = sorted(DATA_DIR.glob("*.csv"),key=get_day_number)
comp_files = [
    f for f in csv_files
    if get_day_number(f) is not None and get_day_number(f)<=85
]
comp_keys = [get_day_number(f) for f in comp_files]

inv_df = pd.read_csv(INV_FILE)

inv_df['T'] = pd.to_numeric(inv_df['T'],errors='coerce')
inv_df['first_valid_index_min'] = pd.to_numeric(
    inv_df['first_valid_index_min'],errors='coerce'
)
inv_df['first_valid_index_max'] = pd.to_numeric(
    inv_df['first_valid_index_max'],errors='coerce'
)
inv_df['days_present'] = pd.to_numeric(
    inv_df['days_present'],errors='coerce'
)
inv_df['days_missing'] = pd.to_numeric(
    inv_df['days_missing'],errors='coerce'
)

feat_df = inv_df[inv_df['feature'].notna()].copy()
feat_df['family'] = feat_df['feature'].str.extract(r'^([A-Z]+)')[0]
feat_df['base'] = feat_df['feature'].str.extract(r'^([A-Z]+\d+)')[0]

feat_df = feat_df.sort_values(
    ['family','base','T']
).reset_index(drop=True)

features = feat_df['feature'].tolist()
finfo = feat_df.set_index('feature')

pb_feats = feat_df[feat_df['family']=='PB']['feature'].tolist()
vb_feats = feat_df[feat_df['family']=='VB']['feature'].tolist()

print("\nFiles found:",len(csv_files))
print("Days used:",len(comp_files))
print("Day range:",min(comp_keys),"-",max(comp_keys))
print("PB features:",len(pb_feats))
print("VB features:",len(vb_feats))
print("Total features:",len(features))
print("GPU:",GPU_OK)

if GPU_OK:
    print("GPU device:",torch.cuda.get_device_name(0))


# ------------------------------------------------------------
# 4B — T FORENSICS
# ------------------------------------------------------------

T_ROWS = []

for file in comp_files:

    d = get_day_number(file)
    df = pd.read_csv(file)

    cols = [c for c in features if c in df.columns]
    if 'Price' not in df.columns:
        continue

    df = df[['Price'] + cols]

    p = pd.to_numeric(df['Price'],errors='coerce').to_numpy(dtype=np.float64)

    for base,g in feat_df.groupby('base'):

        tc = [c for c in g['feature'].tolist() if c in df.columns]

        if len(tc)<2:
            continue

        x = df[tc].apply(pd.to_numeric,errors='coerce')

        for c in tc:

            a = x[c].to_numpy(dtype=np.float64)

            ok = np.isfinite(a)
            if ok.sum()<MIN_N:
                continue

            av = a[ok]

            if len(av)>1:
                sd = np.std(av)
                ds = np.diff(av)
                dsd = np.std(ds)
                smooth = dsd/(sd+1e-12)
            else:
                sd = np.nan
                dsd = np.nan
                smooth = np.nan

            valid_idx = np.flatnonzero(ok)

            dp = np.diff(p)
            da = np.diff(a)

            okr = (
                np.isfinite(dp) &
                np.isfinite(da)
            )

            if okr.sum()>=MIN_N:
                resp = np.corrcoef(
                    da[okr],
                    dp[okr]
                )[0,1]
            else:
                resp = np.nan

            pc = pd.Series(a).corr(
                pd.Series(p),
                method='pearson'
            )

            T_ROWS.append({
                'day':d,
                'family':finfo.loc[c,'family'],
                'base':base,
                'feature':c,
                'T':finfo.loc[c,'T'],
                'scale':sd,
                'diff_scale':dsd,
                'smoothness':smooth,
                'responsiveness':resp,
                'price_corr':pc,
                'first_valid':int(valid_idx[0]),
                'last_valid':int(valid_idx[-1]),
                'n':int(ok.sum())
            })


t_df = pd.DataFrame(T_ROWS)

print("\n--- T STRUCTURE ---")
print("Rows:",len(t_df))

if len(t_df):

    t_sum = t_df.groupby(
        ['family','base','feature','T'],
        as_index=False
    ).agg({
        'scale':'median',
        'diff_scale':'median',
        'smoothness':'median',
        'responsiveness':'median',
        'price_corr':'median',
        'first_valid':'median',
        'last_valid':'median',
        'n':'sum'
    })

else:
    t_sum = pd.DataFrame()


# within-base T correlations

TP_ROWS = []

for file in comp_files:

    d = get_day_number(file)
    df = pd.read_csv(file)

    cols = [c for c in features if c in df.columns]

    for base,g in feat_df.groupby('base'):

        tc = [c for c in g['feature'].tolist() if c in cols]

        if len(tc)<2:
            continue

        x = df[tc].apply(pd.to_numeric,errors='coerce')

        for i in range(len(tc)):
            for j in range(i+1,len(tc)):

                a = x[tc[i]]
                b = x[tc[j]]

                z = pd.concat([a,b],axis=1).dropna()

                if len(z)<MIN_N:
                    continue

                p = z.iloc[:,0].to_numpy()
                q = z.iloc[:,1].to_numpy()

                pear = np.corrcoef(p,q)[0,1]
                spear = stats.spearmanr(p,q).statistic

                TP_ROWS.append({
                    'day':d,
                    'family':finfo.loc[tc[i],'family'],
                    'base':base,
                    'feature_1':tc[i],
                    'feature_2':tc[j],
                    'T1':finfo.loc[tc[i],'T'],
                    'T2':finfo.loc[tc[j],'T'],
                    'pearson':pear,
                    'spearman':spear,
                    'scale_1':np.std(p),
                    'scale_2':np.std(q),
                    'mae':np.mean(np.abs(p-q)),
                    'rmse':np.sqrt(np.mean((p-q)**2)),
                    'n':len(z)
                })


tp_df = pd.DataFrame(TP_ROWS)

if len(tp_df):

    tp_sum = tp_df.groupby(
        [
            'family','base',
            'feature_1','feature_2',
            'T1','T2'
        ],
        as_index=False
    ).agg({
        'pearson':'median',
        'spearman':'median',
        'scale_1':'median',
        'scale_2':'median',
        'mae':'median',
        'rmse':'median',
        'n':'sum'
    })

else:
    tp_sum = pd.DataFrame()


# T-level summary

if len(tp_sum):

    t_pair = tp_sum.groupby(
        ['family','base','T1'],
        as_index=False
    ).agg({
        'pearson':'mean',
        'spearman':'mean'
    }).rename(columns={
        'T1':'T',
        'pearson':'mean_pair_pearson',
        'spearman':'mean_pair_spearman'
    })

    t_sum = t_sum.merge(
        t_pair,
        on=['family','base','T'],
        how='left'
    )


# ------------------------------------------------------------
# 4C — CANDIDATE FEATURE LIBRARY
# ------------------------------------------------------------

def candidate_features(p):

    p = pd.Series(
        pd.to_numeric(p,errors='coerce')
    )

    c = {}

    for w in WINDOWS:

        r = p.rolling(
            w,
            min_periods=w
        )

        ma = r.mean()
        sd = r.std()
        mn = r.min()
        mx = r.max()

        c[f'rolling_mean_{w}'] = ma
        c[f'rolling_std_{w}'] = sd
        c[f'rolling_min_{w}'] = mn
        c[f'rolling_max_{w}'] = mx

        c[f'sma_{w}'] = ma

        c[f'momentum_{w}'] = p-p.shift(w)

        c[f'rolling_return_{w}'] = p.pct_change(w)

        c[f'log_return_{w}'] = np.log(
            p/p.shift(w)
        )

        c[f'price_minus_ma_{w}'] = p-ma

        c[f'price_ma_ratio_{w}'] = p/ma-1

        c[f'drawdown_{w}'] = p/mx-1

        c[f'range_{w}'] = mx-mn

        c[f'zscore_{w}'] = (
            (p-ma)/sd.replace(0,np.nan)
        )

        a = 2/(w+1)

        c[f'ema_{w}'] = p.ewm(
            alpha=a,
            adjust=False,
            min_periods=w
        ).mean()

    return pd.DataFrame(c,index=p.index)


# ------------------------------------------------------------
# GPU MATCHING
# ------------------------------------------------------------

def gpu_match(x,cand):

    n = len(x)
    nc = cand.shape[1]
    nf = x.shape[1]

    rows = []

    if GPU_OK:

        dev = torch.device('cuda')

        xb = torch.tensor(
            x,
            dtype=torch.float32,
            device=dev
        )

        cb = torch.tensor(
            cand,
            dtype=torch.float32,
            device=dev
        )

        for st in range(0,nf,GPU_BATCH):

            en = min(st+GPU_BATCH,nf)

            a = xb[:,st:en]
            b = cb

            va = torch.isfinite(a)
            vb = torch.isfinite(b)

            for j in range(nc):

                bj = b[:,j:j+1]
                vbj = vb[:,j:j+1]

                ok = va & vbj

                nn = ok.sum(dim=0)

                aa = torch.where(
                    ok,
                    a,
                    torch.tensor(
                        0.0,
                        device=dev
                    )
                )

                bb = torch.where(
                    ok,
                    bj,
                    torch.tensor(
                        0.0,
                        device=dev
                    )
                )

                nnf = nn.float().clamp_min(1)

                ma = aa.sum(dim=0)/nnf
                mb = bb.sum(dim=0)/nnf

                da = aa-ma
                db = bb-mb

                da = torch.where(ok,da,0)
                db = torch.where(ok,db,0)

                vaa = (da*da).sum(dim=0)
                vbb = (db*db).sum(dim=0)

                cov = (da*db).sum(dim=0)

                pear = cov/torch.sqrt(
                    vaa*vbb
                ).clamp_min(1e-12)

                beta = cov/vbb.clamp_min(1e-12)
                alpha = ma-beta*mb

                pred = beta.unsqueeze(0)*bb+alpha.unsqueeze(0)

                err = torch.where(
                    ok,
                    aa-pred,
                    0
                )

                mae = torch.abs(err).sum(dim=0)/nnf
                rmse = torch.sqrt(
                    (err*err).sum(dim=0)/nnf
                )

                sca = torch.sqrt(
                    vaa/nnf
                )

                scb = torch.sqrt(
                    vbb/nnf
                )

                for k in range(en-st):

                    if int(nn[k].item())<MIN_N:
                        continue

                    rows.append({
                        'feature_idx':st+k,
                        'candidate_idx':j,
                        'pearson':float(pear[k].item()),
                        'beta':float(beta[k].item()),
                        'alpha':float(alpha[k].item()),
                        'mae':float(mae[k].item()),
                        'rmse':float(rmse[k].item()),
                        'feature_scale':float(sca[k].item()),
                        'candidate_scale':float(scb[k].item()),
                        'n':int(nn[k].item())
                    })

        del xb,cb
        torch.cuda.empty_cache()

    else:

        for i in range(nf):

            a = x[:,i]

            for j in range(nc):

                b = cand[:,j]

                ok = np.isfinite(a)&np.isfinite(b)

                if ok.sum()<MIN_N:
                    continue

                aa = a[ok]
                bb = b[ok]

                if np.std(aa)==0 or np.std(bb)==0:
                    continue

                beta,alpha = np.polyfit(bb,aa,1)

                pred = beta*bb+alpha

                rows.append({
                    'feature_idx':i,
                    'candidate_idx':j,
                    'pearson':np.corrcoef(aa,bb)[0,1],
                    'beta':beta,
                    'alpha':alpha,
                    'mae':np.mean(np.abs(aa-pred)),
                    'rmse':np.sqrt(np.mean((aa-pred)**2)),
                    'feature_scale':np.std(aa),
                    'candidate_scale':np.std(bb),
                    'n':len(aa)
                })

    return pd.DataFrame(rows)


# ------------------------------------------------------------
# 4D + 4F — MATCHING
# ------------------------------------------------------------

MATCH_ROWS = []
LAG_ROWS = []

for di,file in enumerate(comp_files,1):

    d = get_day_number(file)

    print(
        f"\n[{di}/{len(comp_files)}] "
        f"Day {d} matching"
    )

    df = pd.read_csv(file)

    if 'Price' not in df.columns:
        continue

    fcols = [c for c in features if c in df.columns]

    if len(fcols)==0:
        continue

    p = pd.to_numeric(
        df['Price'],
        errors='coerce'
    ).to_numpy(dtype=np.float64)

    cand_df = candidate_features(p)

    x_df = df[fcols].apply(
        pd.to_numeric,
        errors='coerce'
    )

    x = x_df.to_numpy(dtype=np.float64)
    cand = cand_df.to_numpy(dtype=np.float64)

    m = gpu_match(x,cand)

    if len(m)==0:
        continue

    m['feature'] = m['feature_idx'].map(
        dict(enumerate(fcols))
    )

    m['candidate'] = m['candidate_idx'].map(
        dict(enumerate(cand_df.columns))
    )

    m['day'] = d

    m['family'] = m['feature'].map(
        finfo['family']
    )

    m['base'] = m['feature'].map(
        finfo['base']
    )

    m['T'] = m['feature'].map(
        finfo['T']
    )

    m['abs_pearson'] = m['pearson'].abs()

    # Cheap first-stage score.
    # Spearman is calculated only after this shortlist.
    m['score0'] = (
        0.60*m['abs_pearson'] -
        0.20*(m['mae']/(m['feature_scale']+1e-12)) -
        0.20*(m['rmse']/(m['feature_scale']+1e-12))
    )

    # Keep enough candidates for robust second-stage ranking.
    m = (
        m.sort_values(
            ['feature','score0'],
            ascending=[True,False]
        )
        .groupby('feature',as_index=False)
        .head(TOP_MATCHES*2)
        .copy()
    )

    # --------------------------------------------------------
    # SPEARMAN ONLY FOR SHORTLIST
    # --------------------------------------------------------

    for _,r in m.iterrows():

        f = r['feature']
        c = r['candidate']

        a = x_df[f].to_numpy(dtype=np.float64)
        b = cand_df[c].to_numpy(dtype=np.float64)

        ok = np.isfinite(a)&np.isfinite(b)

        if ok.sum()<MIN_N:
            continue

        aa = a[ok]
        bb = b[ok]

        sp = stats.spearmanr(
            aa,
            bb
        ).statistic

        MATCH_ROWS.append({
            'day':d,
            'feature':f,
            'family':r['family'],
            'base':r['base'],
            'T':r['T'],
            'candidate':c,
            'pearson':r['pearson'],
            'spearman':sp,
            'beta':r['beta'],
            'alpha':r['alpha'],
            'mae':r['mae'],
            'rmse':r['rmse'],
            'feature_scale':r['feature_scale'],
            'candidate_scale':r['candidate_scale'],
            'n':r['n']
        })

    # --------------------------------------------------------
    # PRELIMINARY RANKING FOR LAG TEST
    # --------------------------------------------------------

    cur = pd.DataFrame(MATCH_ROWS)

    if len(cur):

        cur = cur[cur['day']==d].copy()

        cur['score'] = (
            0.45*cur['pearson'].abs() +
            0.35*cur['spearman'].abs() -
            0.10*(cur['mae']/(cur['feature_scale']+1e-12)) -
            0.10*(cur['rmse']/(cur['feature_scale']+1e-12))
        )

        cur = (
            cur.sort_values(
                ['feature','score'],
                ascending=[True,False]
            )
            .groupby('feature',as_index=False)
            .head(TOP_LAG_CAND)
        )

        # ----------------------------------------------------
        # LAG MATCHING ONLY ON GOOD CANDIDATES
        # ----------------------------------------------------

        for _,r in cur.iterrows():

            f = r['feature']
            c = r['candidate']

            a = x_df[f].to_numpy(dtype=np.float64)
            b = cand_df[c].to_numpy(dtype=np.float64)

            for lag in range(1,MAX_LAG+1):

                aa = a[lag:]
                bb = b[:-lag]

                ok = np.isfinite(aa)&np.isfinite(bb)

                if ok.sum()<MIN_N:
                    continue

                av = aa[ok]
                bv = bb[ok]

                if np.std(av)==0 or np.std(bv)==0:
                    continue

                lc = np.corrcoef(av,bv)[0,1]

                LAG_ROWS.append({
                    'day':d,
                    'feature':f,
                    'candidate':c,
                    'lag':lag,
                    'lag_corr':lc,
                    'n':len(av)
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
        [
            'feature',
            'family',
            'base',
            'T',
            'candidate'
        ],
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
        [
            'feature',
            'candidate',
            'lag'
        ],
        as_index=False
    ).agg({
        'lag_corr':'median',
        'n':'sum',
        'day':'nunique'
    })

    lsum['abs_lag_corr'] = lsum['lag_corr'].abs()

    lbest = (
        lsum.sort_values(
            ['feature','abs_lag_corr'],
            ascending=[True,False]
        )
        .groupby('feature',as_index=False)
        .head(5)
    )

else:
    lsum = pd.DataFrame()
    lbest = pd.DataFrame()


# ------------------------------------------------------------
# BEST HYPOTHESES
# ------------------------------------------------------------

if len(msum):

    best = (
        msum
        .groupby('feature',as_index=False)
        .head(TOP_MATCHES)
        .copy()
    )

    rows = []

    for f,g in best.groupby('feature'):

        g = g.sort_values(
            'score',
            ascending=False
        ).reset_index(drop=True)

        b = g.iloc[0]

        gap = (
            b['score']-g.iloc[1]['score']
            if len(g)>=2 else np.nan
        )

        if (
            b['abs_pearson']>=0.95 and
            b['abs_spearman']>=0.95 and
            (pd.isna(gap) or gap>=0.02) and
            b['day']>=10
        ):
            conf = 'HIGH'

        elif (
            b['abs_pearson']>=0.80 and
            b['abs_spearman']>=0.80
        ):
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
# T INTERPRETATION HELPERS
# ------------------------------------------------------------

def t_direction(g):

    g = g.sort_values('T')

    if len(g)<3:
        return "INSUFFICIENT_EVIDENCE"

    s = g['smoothness'].to_numpy()
    r = g['responsiveness'].to_numpy()
    pc = g['price_corr'].to_numpy()

    def corr_idx(a):
        ok = np.isfinite(a)
        if ok.sum()<3:
            return np.nan
        return np.corrcoef(
            g.loc[ok,'T'],
            a[ok]
        )[0,1]

    cs = corr_idx(s)
    cr = corr_idx(r)
    cp = corr_idx(pc)

    vals = []

    if np.isfinite(cs):
        vals.append(
            "SMOOTHNESS_INCREASES_WITH_T"
            if cs>0.5 else
            "SMOOTHNESS_DECREASES_WITH_T"
            if cs<-0.5 else
            "SMOOTHNESS_NON_MONOTONIC"
        )

    if np.isfinite(cr):
        vals.append(
            "RESPONSIVENESS_INCREASES_WITH_T"
            if cr>0.5 else
            "RESPONSIVENESS_DECREASES_WITH_T"
            if cr<-0.5 else
            "RESPONSIVENESS_NON_MONOTONIC"
        )

    if np.isfinite(cp):
        vals.append(
            "PRICE_CORR_INCREASES_WITH_T"
            if cp>0.5 else
            "PRICE_CORR_DECREASES_WITH_T"
            if cp<-0.5 else
            "PRICE_CORR_NON_MONOTONIC"
        )

    return " | ".join(vals) if vals else "INSUFFICIENT_EVIDENCE"


if len(t_sum):

    t_sum['T_pattern'] = (
        t_sum.groupby(
            ['family','base'],
            group_keys=False
        )
        .apply(
            lambda g: pd.Series(
                [t_direction(g)]*len(g),
                index=g.index
            )
        )
        .reset_index(drop=True)
    )


# ------------------------------------------------------------
# SAVE
# ------------------------------------------------------------

if len(t_sum):
    t_sum.to_csv(
        T_FILE,
        index=False
    )

if len(msum):
    msum.to_csv(
        MATCH_FILE,
        index=False
    )

if len(lsum):
    lsum.to_csv(
        LAG_FILE,
        index=False
    )

if len(hyp_df):
    hyp_df.to_csv(
        HYP_FILE,
        index=False
    )


# ------------------------------------------------------------
# 4G — FEATURE DOSSIER
# ------------------------------------------------------------

lines = []

lines.append(
    "# EBX FEATURE FORENSICS DOSSIER\n"
)

lines.append(
    "## Task 4 — Reverse Engineering of PB / VB Features\n"
)

lines.append(
    f"\nFiles used: {len(comp_files)} "
    f"(Days 1–64 and 80–85)\n"
)

lines.append(
    f"Feature count: {len(feat_df)} "
    f"(PB={len(pb_feats)}, VB={len(vb_feats)})\n"
)

lines.append(
    f"GPU acceleration: {GPU_OK}\n"
)

lines.append(
    "\n## Methodology\n"
)

lines.append(
    "- T structure is investigated using within-base correlations, "
    "scale, smoothness, responsiveness, price correlation and first-valid behaviour.\n"
)

lines.append(
    "- Candidate features are generated only from raw Price.\n"
)

lines.append(
    "- Candidate windows tested at: "
    + ", ".join(map(str,WINDOWS))
    + ".\n"
)

lines.append(
    "- Pearson, affine beta/alpha, MAE and RMSE are calculated for the full candidate library.\n"
)

lines.append(
    "- Spearman correlation is calculated only after preliminary matching shortlisting.\n"
)

lines.append(
    "- Lagged correlations are calculated only for strong candidate matches.\n"
)

lines.append(
    "- No feature identity is declared solely from high correlation.\n"
)

if len(t_sum):

    lines.append(
        "\n## T Structure Findings\n"
    )

    for fam in ['PB','VB']:

        lines.append(
            f"\n# {fam}\n"
        )

        tf = t_sum[
            t_sum['family']==fam
        ].copy()

        for base,g in tf.groupby('base'):

            lines.append(
                f"\n## {base}\n"
            )

            pat = t_direction(g)

            lines.append(
                f"- T pattern: **{pat}**\n"
            )

            for _,r in g.sort_values('T').iterrows():

                lines.append(
                    f"\n### T{int(r['T'])}\n"
                )

                lines.append(
                    f"- Feature = `{r['feature']}`\n"
                    f"- Scale = {r['scale']:.6g}\n"
                    f"- Difference scale = {r['diff_scale']:.6g}\n"
                    f"- Smoothness = {r['smoothness']:.6g}\n"
                    f"- Responsiveness = {r['responsiveness']:.6f}\n"
                    f"- Price correlation = {r['price_corr']:.6f}\n"
                    f"- First valid index = {r['first_valid']:.0f}\n"
                    f"- Last valid index = {r['last_valid']:.0f}\n"
                    f"- Mean pairwise Pearson = "
                    f"{r.get('mean_pair_pearson',np.nan):.6f}\n"
                )


if len(hyp_df):

    lines.append(
        "\n## Feature Hypotheses\n"
    )

    for fam in ['PB','VB']:

        lines.append(
            f"\n# {fam}\n"
        )

        hf = hyp_df[
            hyp_df['family']==fam
        ].copy()

        for base,g in hf.groupby('base'):

            lines.append(
                f"\n## {base}\n"
            )

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
                    f"- Score gap = {r['score_gap']:.6f}\n"
                    f"- Days represented = {r['days']}\n"
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
                            f"with lag correlation = "
                            f"{lr['lag_corr']:.6f}\n"
                        )

else:

    lines.append(
        "\nNo sufficiently strong feature hypotheses were generated.\n"
    )


lines.append(
    "\n## Interpretation Rule\n"
)

lines.append(
    "A candidate is treated as a hypothesis rather than a confirmed identity. "
    "High correlation, stable affine parameters, low reconstruction error, "
    "cross-day persistence and sensible lag behaviour increase confidence; "
    "isolated correlation does not.\n"
)

DOSSIER_FILE.write_text(
    ''.join(lines),
    encoding='utf-8'
)


# ------------------------------------------------------------
# PLOTS
# ------------------------------------------------------------

if len(t_sum):

    for fam in ['PB','VB']:

        x = t_sum[
            t_sum['family']==fam
        ].copy()

        if len(x)==0:
            continue

        q = (
            x.groupby('base')['mean_pair_pearson']
            .mean()
            .sort_values(ascending=False)
        )

        plt.bar(
            q.index,
            q.values
        )

        plt.xlabel("Feature base")
        plt.ylabel("Mean pairwise Pearson correlation")
        plt.title(
            f"EBX {fam} Within-Base T Correlation"
        )
        plt.xticks(rotation=45)
        plt.grid(
            axis='y',
            alpha=0.3
        )
        plt.tight_layout()

        plt.savefig(
            RESULTS_DIR/
            f"16_{fam.lower()}_T_correlation.png",
            dpi=150
        )

        plt.show()


if len(hyp_df):

    q = hyp_df.groupby(
        'confidence'
    ).size()

    plt.bar(
        q.index,
        q.values
    )

    plt.xlabel("Confidence")
    plt.ylabel("Number of features")
    plt.title(
        "EBX Feature Forensics Confidence"
    )

    plt.grid(
        axis='y',
        alpha=0.3
    )

    plt.tight_layout()

    plt.savefig(
        RESULTS_DIR/
        "16_feature_confidence.png",
        dpi=150
    )

    plt.show()


# ------------------------------------------------------------
# FINAL OUTPUT
# ------------------------------------------------------------

print("\n--- FILES WRITTEN ---")

print(T_FILE)
print(HYP_FILE)
print(MATCH_FILE)
print(LAG_FILE)
print(DOSSIER_FILE)

print("\nT structure rows:",len(t_sum))
print("Hypotheses:",len(hyp_df))
print("Matching rows:",len(match_df))
print("Lag matching rows:",len(lag_df))

if len(hyp_df):

    print(
        "\nConfidence counts:"
    )

    print(
        hyp_df['confidence']
        .value_counts()
    )

print("\nDone.")