# ------------------------------------------------------------
# 17 — FEATURE ALPHA
#
# PATCH NOTE (this version only):
#   Adds ALPHA_DAILY_FILE = 17_feature_alpha_daily.csv
#   This is the *only* change vs. the original File 17.
#
#   Why: 17_feature_alpha_rank.csv is a cross-day aggregate
#   (median pearson/spearman/MI computed over ALL 70 comp_files,
#   i.e. train + validation + test days combined). File 18 was
#   using that aggregate as if it were a discovery-only (54-day)
#   statistic, which is a real train/test leakage bug — the
#   candidate ranking that picks the strategy feature was
#   quietly informed by test-day return statistics.
#
#   File 18 owns the TRAIN/VALIDATION/TEST split, not File 17.
#   So File 17 should not try to guess which days are
#   "discovery" — it should just emit the raw per-day,
#   per-feature, per-horizon rows, and let File 18 aggregate
#   over whichever day subset is actually correct for
#   candidate selection. This file now does that.
# ------------------------------------------------------------

from pathlib import Path
import re 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.feature_selection import mutual_info_regression
from sklearn.decomposition import IncrementalPCA

try:
    import torch
    GPU_OK = torch.cuda.is_available()
except Exception:
    torch = None
    GPU_OK = False


def get_day_number(file):
    res = re.search(r'day[_\s]?(\d+)', file.stem, re.IGNORECASE)
    return int(res.group(1)) if res else None


def normalize_day(x):
    if pd.isna(x):
        return pd.NA
    if isinstance(x, (int, np.integer)):
        return int(x)
    if isinstance(x, (float, np.floating)):
        return int(x) if not np.isnan(x) else pd.NA
    s = str(x).strip().strip('{}')
    if s.isdigit():
        return int(s)
    res = re.search(r'day[_\s]?(\d+)', s, re.IGNORECASE)
    return int(res.group(1)) if res else pd.NA


DATA_DIR = Path(r'.\EBX_Dataset')
OUTPUT_DIR = Path(r'.\output')
RESULTS_DIR = Path(r'.\results')
RET_DIR = OUTPUT_DIR / '03_day_returns'

INV_FILE = OUTPUT_DIR / '15_feature_inventory.csv'
HYP_FILE = OUTPUT_DIR / '16_feature_hypotheses.csv'

ALPHA_FILE = OUTPUT_DIR / '17_feature_alpha_rank.csv'
# ALPHA_DAILY_FILE = OUTPUT_DIR / '17_feature_alpha_daily.csv'   # NEW
# CORR_FILE = OUTPUT_DIR / '17_feature_correlation.csv'
ALPHA_DAILY_FILE = OUTPUT_DIR / '17_feature_alpha_daily.csv'
ALPHA_QUANTILES_FILE = OUTPUT_DIR / '17_feature_alpha_quantiles.csv'
ALPHA_SUMMARY_FILE = OUTPUT_DIR / '17_feature_alpha_summary.csv'
CORR_FILE = OUTPUT_DIR / '17_feature_correlation.csv'
PCA_FILE = OUTPUT_DIR / '17_pca_results.csv'
GRANGER_FILE = OUTPUT_DIR / '17_granger.csv'

CORR_PNG = RESULTS_DIR / '17_feature_correlation.png'
PCA_PNG = RESULTS_DIR / '17_pca_scree.png'

# WINDOWS = [10, 30, 60, 300]
# HORIZONS_SECONDS = [60, 300, 600]
ALPHA_HORIZONS_SECONDS = [60, 300, 600]
TARGET_HORIZON_SECONDS = 600
MIN_N = 100
MI_N = 10000
MI_NEIGHBORS = 3
PCA_BATCH = 4096
PCA_COMPONENTS = 50
RUN_GRANGER = False
GRANGER_N = 20000
GRANGER_LAGS = 5
RANDOM_STATE = 42


# ------------------------------------------------------------
# FILES / FEATURES
# ------------------------------------------------------------

csv_files = sorted(DATA_DIR.glob('*.csv'), key=get_day_number)

comp_files = [
    f for f in csv_files
    if get_day_number(f) is not None and get_day_number(f) <= 85
]

comp_keys = [get_day_number(f) for f in comp_files]

inv_df = pd.read_csv(INV_FILE)
inv_df['T'] = pd.to_numeric(inv_df['T'], errors='coerce')
inv_df['days_present'] = pd.to_numeric(inv_df['days_present'], errors='coerce')
inv_df['days_missing'] = pd.to_numeric(inv_df['days_missing'], errors='coerce')

feat_df = inv_df[inv_df['feature'].notna()].copy()
feat_df['family'] = feat_df['feature'].str.extract(r'^([A-Z]+)')[0]
feat_df['base'] = feat_df['feature'].str.extract(r'^([A-Z]+\d+)')[0]
feat_df = feat_df.sort_values(['family', 'base', 'T']).reset_index(drop=True)

features = feat_df['feature'].tolist()
finfo = feat_df.set_index('feature')

pb_feats = feat_df[feat_df['family'] == 'PB']['feature'].tolist()
vb_feats = feat_df[feat_df['family'] == 'VB']['feature'].tolist()


# ------------------------------------------------------------
# EXISTING FORENSICS
# ------------------------------------------------------------

hyp_df = pd.read_csv(HYP_FILE) if HYP_FILE.exists() else pd.DataFrame()

print("\nFiles found:", len(csv_files))
print("Days used:", len(comp_files))
print("Day range:", min(comp_keys), "-", max(comp_keys))
print("PB features:", len(pb_feats))
print("VB features:", len(vb_feats))
print("Total features:", len(features))
print("Existing forensic hypotheses:", len(hyp_df))
print("GPU:", GPU_OK)
if GPU_OK:
    print("GPU device:", torch.cuda.get_device_name(0))


# ------------------------------------------------------------
# RETURN COLUMN DETECTION
# ------------------------------------------------------------

def find_return_col(cols, kind):
    cols = list(cols)
    pats = {
        '1s': [r'^1s_log_return$', r'^log_ret_1s$', r'^log_return_1s$', r'^return_1s$'],
        '1m': [r'^1m_log_return$', r'^log_ret_1m$', r'^log_return_1m$', r'^return_1m$'],
        '5m': [r'^5m_log_return$', r'^log_ret_5m$', r'^log_return_5m$', r'^return_5m$'],
    }
    for p in pats[kind]:
        for c in cols:
            if re.search(p, str(c), re.IGNORECASE):
                return c
    return None


# ------------------------------------------------------------
# FUTURE RETURNS
# ------------------------------------------------------------

def forward_from_1s(r, h):
    r = pd.to_numeric(r, errors='coerce')
    return r.shift(-1).iloc[::-1].rolling(h, min_periods=h).sum().iloc[::-1]


# def future_returns(df):
#     r1s = find_return_col(df.columns, '1s')
#     r1m = find_return_col(df.columns, '1m')
#     r5m = find_return_col(df.columns, '5m')

#     out = {}

#     if r1s is None:
#         raise ValueError("Stored 1-second return column not found.")

#     r = pd.to_numeric(df[r1s], errors='coerce')
#     out[10] = forward_from_1s(r, 10)
#     out[30] = forward_from_1s(r, 30)

#     if r1m is not None:
#         out[60] = pd.to_numeric(df[r1m], errors='coerce').shift(-60)
#     else:
#         out[60] = forward_from_1s(r, 60)

#     if r5m is not None:
#         out[300] = pd.to_numeric(df[r5m], errors='coerce').shift(-300)
#     else:
#         out[300] = forward_from_1s(r, 300)

#     return pd.DataFrame(out, index=df.index)

def future_returns(df):

    r1s = find_return_col(df.columns, '1s')

    if r1s is None:
        raise ValueError("Stored 1-second return column not found.")

    r = pd.to_numeric(df[r1s], errors='coerce')

    return pd.DataFrame({
        h: forward_from_1s(r, h)
        for h in ALPHA_HORIZONS_SECONDS
    }, index=df.index)

def prepare_day_data(raw_file, ret_file, feature_cols):

    raw = pd.read_csv(raw_file)
    ret = pd.read_csv(ret_file)

    if 'Time' not in raw.columns:
        raise ValueError(f"Time column missing from raw file: {raw_file}")

    if 'Time' not in ret.columns:
        raise ValueError(f"Time column missing from return file: {ret_file}")

    raw['Time'] = raw['Time'].astype(str)
    ret['Time'] = ret['Time'].astype(str)

    fcols = [c for c in feature_cols if c in raw.columns]

    if not fcols:
        return pd.DataFrame()

    ydf = future_returns(ret)
    ydf.insert(0, 'Time', ret['Time'].to_numpy())

    xdf = raw[['Time'] + fcols].copy()

    merged = xdf.merge(
        ydf,
        on='Time',
        how='inner',
        validate='one_to_one'
    )

    return merged

# ------------------------------------------------------------
# ALPHA METRICS
# ------------------------------------------------------------

def alpha_mi(a, b):
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    ok = np.isfinite(a) & np.isfinite(b)

    if ok.sum() < MIN_N:
        return np.nan

    a, b = a[ok], b[ok]

    if len(a) > MI_N:
        rng = np.random.default_rng(RANDOM_STATE)
        ix = rng.choice(len(a), MI_N, replace=False)
        a, b = a[ix], b[ix]

    if np.std(a) == 0 or np.std(b) == 0:
        return 0.0

    try:
        mi = mutual_info_regression(
            a.reshape(-1, 1), b,
            n_neighbors=MI_NEIGHBORS,
            random_state=RANDOM_STATE,
        )[0]
        return float(mi)
    except Exception:
        return np.nan


# ------------------------------------------------------------
# 4H — PREDICTIVE CONTENT (per day, per feature, per horizon)
# ------------------------------------------------------------

ALPHA_ROWS = []
QUANTILE_ROWS = []

for di, file in enumerate(comp_files, 1):

    d = get_day_number(file)
    ret_file = RET_DIR / f'day{d}_returns.csv'

    print(f"\n[{di}/{len(comp_files)}] Day {d} alpha")

    if not ret_file.exists():
        print("  Missing stored return file:", ret_file)
        continue

    raw_check = pd.read_csv(file, nrows=1)

    fcols = [c for c in features if c in raw_check.columns]

    if len(fcols) == 0:
        continue

    day_df = prepare_day_data(
        raw_file=file,
        ret_file=ret_file,
        feature_cols=fcols
    )

    if len(day_df) == 0:
        continue

    for h in ALPHA_HORIZONS_SECONDS:

        y = pd.to_numeric(
            day_df[h],
            errors='coerce'
        ).to_numpy(dtype=np.float64)

        for f in fcols:

            x = pd.to_numeric(
                day_df[f],
                errors='coerce'
            ).to_numpy(dtype=np.float64)

            feature_valid = np.isfinite(x)

            coverage = float(feature_valid.mean())

            ok = feature_valid & np.isfinite(y)

            if ok.sum() < MIN_N:
                continue

            xx = x[ok]
            yy = y[ok]

            if np.std(xx) == 0 or np.std(yy) == 0:
                continue

            pear = np.corrcoef(xx, yy)[0, 1]

            spear = stats.spearmanr(
                xx,
                yy
            ).statistic

            mi = alpha_mi(xx, yy)

            ALPHA_ROWS.append({
                'day': d,
                'feature': f,
                'family': finfo.loc[f, 'family'],
                'base': finfo.loc[f, 'base'],
                'T': finfo.loc[f, 'T'],
                'horizon': h,
                'pearson': pear,
                'spearman': spear,
                'abs_pearson': abs(pear),
                'abs_spearman': abs(spear),
                'mutual_information': mi,
                'n': len(xx),
                'coverage': coverage,
            })

            # ------------------------------------------------
            # CONDITIONAL / QUANTILE RETURN STRUCTURE
            # ------------------------------------------------

            pct = pd.Series(xx).rank(
                method='average',
                pct=True
            ).to_numpy()

            quantile_edges = np.array([
                0.00,
                0.05,
                0.10,
                0.20,
                0.30,
                0.40,
                0.50,
                0.60,
                0.70,
                0.80,
                0.90,
                0.95,
                1.00,
            ])

            bucket = pd.cut(
                pct,
                bins=quantile_edges,
                labels=False,
                include_lowest=True
            )

            for q_idx in range(len(quantile_edges) - 1):

                mask = bucket == q_idx

                if mask.sum() < MIN_N:
                    continue

                q_low = quantile_edges[q_idx]
                q_high = quantile_edges[q_idx + 1]

                q_returns = yy[mask]

                QUANTILE_ROWS.append({
                    'day': d,
                    'feature': f,
                    'family': finfo.loc[f, 'family'],
                    'base': finfo.loc[f, 'base'],
                    'T': finfo.loc[f, 'T'],
                    'horizon': h,
                    'quantile_low': q_low,
                    'quantile_high': q_high,
                    'mean_forward_return': float(np.mean(q_returns)),
                    'median_forward_return': float(np.median(q_returns)),
                    'n': int(mask.sum()),
                })
alpha_df = pd.DataFrame(ALPHA_ROWS)
quantile_df = pd.DataFrame(QUANTILE_ROWS)

print("\n--- PREDICTIVE CONTENT ---")
print("Rows:", len(alpha_df))
print("Quantile rows:", len(quantile_df))

# --------------------------------------------------------
# NEW: persist the raw per-day rows.
#
# This is what makes File 18's discovery-only aggregation
# possible without recomputing MI/correlations from scratch.
# --------------------------------------------------------
if len(alpha_df):
    alpha_df.to_csv(ALPHA_DAILY_FILE, index=False)

if len(quantile_df):
    quantile_df.to_csv(ALPHA_QUANTILES_FILE, index=False)

# ------------------------------------------------------------
# CROSS-DAY ALPHA AGGREGATION (full 70-day universe — DIAGNOSTIC ONLY)
#
# NOTE: this aggregate spans train+validation+test days together.
# It is kept for reporting/coverage/forensic-hypothesis lookups.
# It must NOT be used as a discovery-only candidate-selection
# statistic downstream (see File 18).
# ------------------------------------------------------------

if len(alpha_df):
    alpha_sum = alpha_df.groupby(
        ['feature', 'family', 'base', 'T', 'horizon'],
        as_index=False
    ).agg(
        pearson=('pearson', 'median'),
        spearman=('spearman', 'median'),
        abs_pearson=('abs_pearson', 'median'),
        abs_spearman=('abs_spearman', 'median'),
        mutual_information=('mutual_information', 'median'),
        n=('n', 'sum'),
        days=('day', 'nunique'),
        mean_coverage=('coverage', 'mean'),
        median_coverage=('coverage', 'median'),
    )

    # alpha_sum['abs_pearson'] = alpha_sum['pearson'].abs()
    # alpha_sum['abs_spearman'] = alpha_sum['spearman'].abs()
    alpha_sum['alpha_score'] = (
        0.40 * alpha_sum['abs_pearson']
        + 0.35 * alpha_sum['abs_spearman']
        + 0.25 * alpha_sum['mutual_information']
    )
    daily_stats = alpha_df.groupby(
        ['feature', 'family', 'base', 'T', 'horizon']
    ).agg(
        pearson_mean=('pearson', 'mean'),
        pearson_median=('pearson', 'median'),
        pearson_std=('pearson', 'std'),

        spearman_mean=('spearman', 'mean'),
        spearman_median=('spearman', 'median'),
        spearman_std=('spearman', 'std'),

        pearson_positive_day_frac=(
            'pearson',
            lambda x: float((x > 0).mean())
        ),

        spearman_positive_day_frac=(
            'spearman',
            lambda x: float((x > 0).mean())
        ),
    ).reset_index()

    daily_stats['pearson_tstat'] = (
        daily_stats['pearson_mean']
        /
        (
            daily_stats['pearson_std']
            /
            np.sqrt(
                alpha_df.groupby(
                    ['feature', 'family', 'base', 'T', 'horizon']
                )['pearson'].count().to_numpy()
            )
        )
    )

    daily_stats['spearman_tstat'] = (
        daily_stats['spearman_mean']
        /
        (
            daily_stats['spearman_std']
            /
            np.sqrt(
                alpha_df.groupby(
                    ['feature', 'family', 'base', 'T', 'horizon']
                )['spearman'].count().to_numpy()
            )
        )
    )

    alpha_sum = alpha_sum.merge(
        daily_stats,
        on=['feature', 'family', 'base', 'T', 'horizon'],
        how='left'
    )
else:
    alpha_sum = pd.DataFrame()

if len(quantile_df):

    tail_summary = quantile_df.groupby(
        ['feature', 'family', 'base', 'T', 'horizon']
    ).apply(
        lambda g: pd.Series({
            'lower_tail_edge': g.loc[
                g['quantile_high'] <= 0.10,
                'mean_forward_return'
            ].mean(),

            'upper_tail_edge': g.loc[
                g['quantile_low'] >= 0.90,
                'mean_forward_return'
            ].mean(),

            'top_bottom_spread': (
                g.loc[
                    g['quantile_low'] >= 0.90,
                    'mean_forward_return'
                ].mean()
                -
                g.loc[
                    g['quantile_high'] <= 0.10,
                    'mean_forward_return'
                ].mean()
            ),

            'upper_tail_positive_day_frac': np.nan,
            'lower_tail_negative_day_frac': np.nan,
        }),
        include_groups=False
    ).reset_index()

    alpha_sum = alpha_sum.merge(
        tail_summary,
        on=['feature', 'family', 'base', 'T', 'horizon'],
        how='left'
    )

# ------------------------------------------------------------
# FORENSIC INFORMATION
#
# best_candidate / confidence / score come from File 16's
# feature-name/behavior forensics — not from return statistics —
# so merging them from the full-universe table carries no
# train/test leakage risk.
# ------------------------------------------------------------

if len(alpha_sum) > 0 and len(hyp_df) > 0:
    keep = [c for c in ['feature', 'best_candidate', 'confidence', 'score', 'days'] if c in hyp_df.columns]
    h = hyp_df[keep].drop_duplicates('feature')
    alpha_sum = alpha_sum.merge(h, on='feature', how='left')


# ------------------------------------------------------------
# FINAL ALPHA RANK (full-universe diagnostic artifact)
# ------------------------------------------------------------

if len(alpha_sum):

    alpha_sum = alpha_sum.sort_values(
        ['horizon', 'alpha_score'],
        ascending=[True, False]
    ).reset_index(drop=True)

    alpha_sum['horizon_rank'] = (
        alpha_sum
        .groupby('horizon')['alpha_score']
        .rank(
            ascending=False,
            method='min'
        )
    )

    alpha_sum['feature_rank'] = (
        alpha_sum
        .groupby('feature')['alpha_score']
        .rank(
            ascending=False,
            method='min'
        )
    )

    alpha_sum.to_csv(
        ALPHA_FILE,
        index=False
    )

    alpha_sum.to_csv(
        ALPHA_SUMMARY_FILE,
        index=False
    )


# ------------------------------------------------------------
# 4I — FEATURE REDUNDANCY
#
# This is feature-vs-feature structural correlation, not
# feature-vs-target. It carries no target-leakage risk, so
# computing it over the full 70-day universe is fine.
# ------------------------------------------------------------

CORR_ROWS = []
PCA_DATA = []

for di, file in enumerate(comp_files, 1):
    d = get_day_number(file)
    print(f"\n[{di}/{len(comp_files)}] Day {d} redundancy")

    raw = pd.read_csv(file, usecols=lambda c: c in features)
    fcols = [c for c in features if c in raw.columns]

    if len(fcols) < 2:
        continue

    x = raw[fcols].apply(pd.to_numeric, errors='coerce').astype(np.float64)
    x = x.replace([np.inf, -np.inf], np.nan)
    x = x.fillna(x.median())

    sd = x.std(ddof=0).replace(0, np.nan)
    z = (x - x.mean()).div(sd)
    z = z.replace([np.inf, -np.inf], np.nan).fillna(0)

    c = z.corr(method='pearson')

    for i, f1 in enumerate(fcols):
        for j in range(i + 1, len(fcols)):
            f2 = fcols[j]
            v = c.loc[f1, f2]
            if np.isfinite(v):
                CORR_ROWS.append({
                    'day': d,
                    'feature_1': f1,
                    'feature_2': f2,
                    'family_1': finfo.loc[f1, 'family'],
                    'family_2': finfo.loc[f2, 'family'],
                    'base_1': finfo.loc[f1, 'base'],
                    'base_2': finfo.loc[f2, 'base'],
                    'T1': finfo.loc[f1, 'T'],
                    'T2': finfo.loc[f2, 'T'],
                    'pearson': float(v),
                })

    PCA_DATA.append(z[fcols])

corr_day_df = pd.DataFrame(CORR_ROWS)

print("\n--- REDUNDANCY ---")
print("Pair rows:", len(corr_day_df))

if len(corr_day_df):
    corr_df = corr_day_df.groupby(
        ['feature_1', 'feature_2', 'family_1', 'family_2', 'base_1', 'base_2', 'T1', 'T2'],
        as_index=False,
    ).agg({'pearson': 'median', 'day': 'nunique'})

    corr_df['abs_pearson'] = corr_df['pearson'].abs()
    corr_df = corr_df.sort_values('abs_pearson', ascending=False)
    corr_df.to_csv(CORR_FILE, index=False)
else:
    corr_df = pd.DataFrame()


# ------------------------------------------------------------
# CORRELATION MATRIX
# ------------------------------------------------------------

if len(corr_df):
    cm = pd.DataFrame(np.eye(len(features)), index=features, columns=features)

    for _, r in corr_df.iterrows():
        cm.loc[r['feature_1'], r['feature_2']] = r['pearson']
        cm.loc[r['feature_2'], r['feature_1']] = r['pearson']

    plt.figure(figsize=(14, 12))
    plt.imshow(cm.to_numpy(), aspect='auto', interpolation='nearest')
    plt.colorbar(label='Pearson correlation')
    plt.xlabel('Feature')
    plt.ylabel('Feature')
    plt.title('EBX Feature Correlation Matrix')
    plt.tight_layout()
    plt.savefig(CORR_PNG, dpi=150)
    plt.show()


# ------------------------------------------------------------
# PCA
# ------------------------------------------------------------

if len(PCA_DATA):
    pca = IncrementalPCA(n_components=min(PCA_COMPONENTS, len(features)), batch_size=PCA_BATCH)

    for z in PCA_DATA:
        a = z.to_numpy(dtype=np.float64)
        for st in range(0, len(a), PCA_BATCH):
            en = min(st + PCA_BATCH, len(a))
            pca.partial_fit(a[st:en])

    ev = pca.explained_variance_ratio_
    cev = np.cumsum(ev)

    pca_df = pd.DataFrame([
        {'component': i + 1, 'explained_variance_ratio': ev[i], 'cumulative_explained_variance': cev[i]}
        for i in range(len(ev))
    ])

    pca_df.to_csv(PCA_FILE, index=False)

    plt.figure(figsize=(9, 5))
    plt.plot(pca_df['component'], pca_df['explained_variance_ratio'], marker='o')
    plt.xlabel('Principal component')
    plt.ylabel('Explained variance ratio')
    plt.title('EBX Feature PCA Scree Plot')
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(PCA_PNG, dpi=150)
    plt.show()
else:
    pca_df = pd.DataFrame()


# ------------------------------------------------------------
# 4J — OPTIONAL GRANGER CAUSALITY (unchanged, off by default)
# ------------------------------------------------------------

if RUN_GRANGER:
    try:
        from statsmodels.tsa.stattools import grangercausalitytests

        GRANGER_ROWS = []

        if len(alpha_sum):
            cand = (
                alpha_sum[alpha_sum['horizon'] == TARGET_HORIZON_SECONDS]
                .sort_values('alpha_score', ascending=False)
                .groupby('feature', as_index=False)
                .head(5)
            )

            for _, r in cand.iterrows():
                f = r['feature']
                print("Granger:", f)

                for file in comp_files:
                    d = get_day_number(file)
                    ret_file = RET_DIR / f'day{d}_returns.csv'

                    if not ret_file.exists():
                        continue

                    raw = pd.read_csv(file)
                    ret = pd.read_csv(ret_file)

                    if f not in raw.columns:
                        continue

                    ydf = future_returns(ret)

                    z = pd.DataFrame({
                        'return': ydf[TARGET_HORIZON_SECONDS],
                        'feature': pd.to_numeric(raw[f], errors='coerce'),
                    }).dropna()

                    if len(z) < MIN_N:
                        continue

                    try:
                        g = grangercausalitytests(z[['return', 'feature']], maxlag=GRANGER_LAGS, verbose=False)
                        for lag, v in g.items():
                            p = v[0]['ssr_ftest'][1]
                            GRANGER_ROWS.append({'day': d, 'feature': f, 'horizon': TARGET_HORIZON_SECONDS, 'lag': lag, 'p_value': p})
                    except Exception:
                        continue

        granger_df = pd.DataFrame(GRANGER_ROWS)
        if len(granger_df):
            granger_df.to_csv(GRANGER_FILE, index=False)

    except ImportError:
        print("\nstatsmodels not installed; Granger skipped.")
else:
    print("\n--- GRANGER ---")
    print("Skipped: RUN_GRANGER=False")
 
# if RUN_GRANGER:
#     try:
#         from statsmodels.tsa.stattools import grangercausalitytests
 
#         GRANGER_ROWS = []
 
#         if len(alpha_sum):
#             cand = (
#                 alpha_sum[alpha_sum['horizon'] == 60]
#                 .sort_values('alpha_score', ascending=False)
#                 .groupby('feature', as_index=False)
#                 .head(5)
#             )
#             granger_feats = cand['feature'].tolist()
#             print("Granger candidates:", granger_feats)
 
#             for file in comp_files:
#                 d = get_day_number(file)
#                 ret_file = RET_DIR / f'day{d}_returns.csv'
 
#                 if not ret_file.exists():
#                     continue
 
#                 raw = pd.read_csv(file, usecols=lambda c: c in granger_feats)
#                 present = [f for f in granger_feats if f in raw.columns]
#                 if not present:
#                     continue
 
#                 ret = pd.read_csv(ret_file)
#                 ydf = future_returns(ret)
#                 y = ydf[60]
 
#                 for f in present:
#                     z = pd.DataFrame({
#                         'return': y,
#                         'feature': pd.to_numeric(raw[f], errors='coerce'),
#                     }).dropna()
 
#                     if len(z) < MIN_N:
#                         continue
 
#                     if len(z) > GRANGER_N:
#                         z = z.sample(GRANGER_N, random_state=RANDOM_STATE)
 
#                     try:
#                         g = grangercausalitytests(z[['return', 'feature']], maxlag=GRANGER_LAGS, verbose=False)
#                         for lag, v in g.items():
#                             p = v[0]['ssr_ftest'][1]
#                             GRANGER_ROWS.append({'day': d, 'feature': f, 'horizon': 60, 'lag': lag, 'p_value': p})
#                     except Exception:
#                         continue
 
#         granger_df = pd.DataFrame(GRANGER_ROWS)
#         if len(granger_df):
#             granger_df.to_csv(GRANGER_FILE, index=False)
 
#     except ImportError:
#         print("\nstatsmodels not installed; Granger skipped.")
# else:
#     print("\n--- GRANGER ---")
#     print("Skipped: RUN_GRANGER=False")
 

# ------------------------------------------------------------
# FINAL OUTPUT
# ------------------------------------------------------------

print("\n--- FILES WRITTEN ---")
print(ALPHA_FILE)
print(ALPHA_DAILY_FILE)
print(ALPHA_QUANTILES_FILE)
print(ALPHA_SUMMARY_FILE)
print(CORR_FILE)
print(PCA_FILE)
if RUN_GRANGER:
    print(GRANGER_FILE)

print("Alpha rows (daily, granular):", len(alpha_df))
print("Alpha quantile rows:", len(quantile_df))
print("Alpha summary rows:", len(alpha_sum))
print("Alpha ranking rows (full-universe diagnostic):", len(alpha_sum))
print("Correlation rows:", len(corr_df))
print("PCA rows:", len(pca_df))
print("\nDone.")