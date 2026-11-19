# ------------------------------------------------------------
# 17 — FEATURE ALPHA
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

    res = re.search(
        r'day[_\s]?(\d+)',
        file.stem,
        re.IGNORECASE
    )

    return int(res.group(1)) if res else None


def normalize_day(x):

    if pd.isna(x):
        return pd.NA

    if isinstance(x,(int,np.integer)):
        return int(x)

    if isinstance(x,(float,np.floating)):
        return int(x) if not np.isnan(x) else pd.NA

    s = str(x).strip().strip('{}')

    if s.isdigit():
        return int(s)

    res = re.search(
        r'day[_\s]?(\d+)',
        s,
        re.IGNORECASE
    )

    return int(res.group(1)) if res else pd.NA


DATA_DIR = Path('EBX_Dataset')
OUTPUT_DIR = Path('output')
RESULTS_DIR = Path('results')
RET_DIR = OUTPUT_DIR / '03_day_returns'

INV_FILE = OUTPUT_DIR / '15_feature_inventory.csv'
HYP_FILE = OUTPUT_DIR / '16_feature_hypotheses.csv'

ALPHA_FILE = OUTPUT_DIR / '17_feature_alpha_rank.csv'
CORR_FILE = OUTPUT_DIR / '17_feature_correlation.csv'
PCA_FILE = OUTPUT_DIR / '17_pca_results.csv'
GRANGER_FILE = OUTPUT_DIR / '17_granger.csv'

CORR_PNG = RESULTS_DIR / '17_feature_correlation.png'
PCA_PNG = RESULTS_DIR / '17_pca_scree.png'

WINDOWS = [10,30,60,300]

MIN_N = 100

MI_N = 10000
MI_NEIGHBORS = 3

PCA_BATCH = 4096
PCA_COMPONENTS = 50

RUN_GRANGER = False

GRANGER_LAGS = 5

RANDOM_STATE = 42


# ------------------------------------------------------------
# FILES / FEATURES
# ------------------------------------------------------------

csv_files = sorted(
    DATA_DIR.glob('*.csv'),
    key=get_day_number
)

comp_files = [
    f for f in csv_files
    if get_day_number(f) is not None
    and get_day_number(f) <= 85
]

comp_keys = [
    get_day_number(f)
    for f in comp_files
]

inv_df = pd.read_csv(INV_FILE)

inv_df['T'] = pd.to_numeric(
    inv_df['T'],
    errors='coerce'
)

inv_df['days_present'] = pd.to_numeric(
    inv_df['days_present'],
    errors='coerce'
)

inv_df['days_missing'] = pd.to_numeric(
    inv_df['days_missing'],
    errors='coerce'
)

feat_df = inv_df[
    inv_df['feature'].notna()
].copy()

feat_df['family'] = feat_df[
    'feature'
].str.extract(
    r'^([A-Z]+)'
)[0]

feat_df['base'] = feat_df[
    'feature'
].str.extract(
    r'^([A-Z]+\d+)'
)[0]

feat_df = feat_df.sort_values(
    ['family','base','T']
).reset_index(
    drop=True
)

features = feat_df[
    'feature'
].tolist()

finfo = feat_df.set_index(
    'feature'
)

pb_feats = feat_df[
    feat_df['family']=='PB'
]['feature'].tolist()

vb_feats = feat_df[
    feat_df['family']=='VB'
]['feature'].tolist()


# ------------------------------------------------------------
# EXISTING FORENSICS
# ------------------------------------------------------------

if HYP_FILE.exists():

    hyp_df = pd.read_csv(
        HYP_FILE
    )

else:

    hyp_df = pd.DataFrame()


print("\nFiles found:",len(csv_files))

print("Days used:",len(comp_files))

print(
    "Day range:",
    min(comp_keys),
    "-",
    max(comp_keys)
)

print("PB features:",len(pb_feats))

print("VB features:",len(vb_feats))

print("Total features:",len(features))

print(
    "Existing forensic hypotheses:",
    len(hyp_df)
)

print("GPU:",GPU_OK)

if GPU_OK:

    print(
        "GPU device:",
        torch.cuda.get_device_name(0)
    )


# ------------------------------------------------------------
# RETURN COLUMN DETECTION
# ------------------------------------------------------------

def find_return_col(cols,kind):

    cols = list(cols)

    pats = {

        '1s': [
            r'^1s_log_return$',
            r'^log_ret_1s$',
            r'^log_return_1s$',
            r'^return_1s$'
        ],

        '1m': [
            r'^1m_log_return$',
            r'^log_ret_1m$',
            r'^log_return_1m$',
            r'^return_1m$'
        ],

        '5m': [
            r'^5m_log_return$',
            r'^log_ret_5m$',
            r'^log_return_5m$',
            r'^return_5m$'
        ]

    }

    for p in pats[kind]:

        for c in cols:

            if re.search(
                p,
                str(c),
                re.IGNORECASE
            ):

                return c

    return None


# ------------------------------------------------------------
# FUTURE RETURNS
# ------------------------------------------------------------

def forward_from_1s(r,h):

    r = pd.to_numeric(
        r,
        errors='coerce'
    )

    return (
        r.shift(-1)
        .iloc[::-1]
        .rolling(
            h,
            min_periods=h
        )
        .sum()
        .iloc[::-1]
    )


def future_returns(df):

    r1s = find_return_col(
        df.columns,
        '1s'
    )

    r1m = find_return_col(
        df.columns,
        '1m'
    )

    r5m = find_return_col(
        df.columns,
        '5m'
    )

    out = {}

    if r1s is None:

        raise ValueError(
            "Stored 1-second return column not found."
        )

    r = pd.to_numeric(
        df[r1s],
        errors='coerce'
    )

    out[10] = forward_from_1s(
        r,
        10
    )

    out[30] = forward_from_1s(
        r,
        30
    )

    if r1m is not None:

        x = pd.to_numeric(
            df[r1m],
            errors='coerce'
        )

        out[60] = x.shift(-60)

    else:

        out[60] = forward_from_1s(
            r,
            60
        )

    if r5m is not None:

        x = pd.to_numeric(
            df[r5m],
            errors='coerce'
        )

        out[300] = x.shift(-300)

    else:

        out[300] = forward_from_1s(
            r,
            300
        )

    return pd.DataFrame(
        out,
        index=df.index
    )


# ------------------------------------------------------------
# ALPHA METRICS
# ------------------------------------------------------------

def alpha_metrics(a,b):

    a = np.asarray(
        a,
        dtype=np.float64
    )

    b = np.asarray(
        b,
        dtype=np.float64
    )

    ok = (
        np.isfinite(a) &
        np.isfinite(b)
    )

    if ok.sum()<MIN_N:

        return (
            np.nan,
            np.nan,
            np.nan,
            int(ok.sum())
        )

    a = a[ok]
    b = b[ok]

    if np.std(a)==0 or np.std(b)==0:

        return (
            np.nan,
            np.nan,
            np.nan,
            len(a)
        )

    pear = np.corrcoef(
        a,
        b
    )[0,1]

    spear = stats.spearmanr(
        a,
        b
    ).statistic

    return (
        pear,
        spear,
        len(a),
        len(a)
    )


def alpha_mi(a,b):

    a = np.asarray(
        a,
        dtype=np.float64
    )

    b = np.asarray(
        b,
        dtype=np.float64
    )

    ok = (
        np.isfinite(a) &
        np.isfinite(b)
    )

    if ok.sum()<MIN_N:

        return np.nan

    a = a[ok]
    b = b[ok]

    if len(a)>MI_N:

        rng = np.random.default_rng(
            RANDOM_STATE
        )

        ix = rng.choice(
            len(a),
            MI_N,
            replace=False
        )

        a = a[ix]
        b = b[ix]

    if np.std(a)==0 or np.std(b)==0:

        return 0.0

    try:

        mi = mutual_info_regression(
            a.reshape(-1,1),
            b,
            n_neighbors=MI_NEIGHBORS,
            random_state=RANDOM_STATE
        )[0]

        return float(mi)

    except Exception:

        return np.nan


# ------------------------------------------------------------
# 4H — PREDICTIVE CONTENT
# ------------------------------------------------------------

ALPHA_ROWS = []

for di,file in enumerate(
    comp_files,
    1
):

    d = get_day_number(
        file
    )

    ret_file = (
        RET_DIR /
        f'day{d}_returns.csv'
    )

    print(
        f"\n[{di}/{len(comp_files)}] "
        f"Day {d} alpha"
    )

    if not ret_file.exists():

        print(
            "  Missing stored return file:",
            ret_file
        )

        continue

    raw = pd.read_csv(
        file
    )

    ret = pd.read_csv(
        ret_file
    )

    # fcols = [
    #     c for c in features
    #     if c in raw.columns
    #     and c in ret.columns
    # ]
    fcols = [
        c for c in features
        if c in raw.columns
    ]

    if len(fcols)==0:

        continue

    ydf = future_returns(
        ret
    )

    xdf = raw[fcols].apply(
        pd.to_numeric,
        errors='coerce'
    )

    for h in WINDOWS:

        y = ydf[h].to_numpy(
            dtype=np.float64
        )

        for f in fcols:

            x = xdf[f].to_numpy(
                dtype=np.float64
            )

            ok = (
                np.isfinite(x) &
                np.isfinite(y)
            )

            if ok.sum()<MIN_N:

                continue

            xx = x[ok]
            yy = y[ok]

            if (
                np.std(xx)==0 or
                np.std(yy)==0
            ):

                continue

            pear = np.corrcoef(
                xx,
                yy
            )[0,1]

            spear = stats.spearmanr(
                xx,
                yy
            ).statistic

            mi = alpha_mi(
                xx,
                yy
            )

            ALPHA_ROWS.append({

                'day':d,

                'feature':f,

                'family':finfo.loc[
                    f,
                    'family'
                ],

                'base':finfo.loc[
                    f,
                    'base'
                ],

                'T':finfo.loc[
                    f,
                    'T'
                ],

                'horizon':h,

                'pearson':pear,

                'spearman':spear,

                'mutual_information':mi,

                'n':len(xx)

            })


alpha_df = pd.DataFrame(
    ALPHA_ROWS
)

print(
    "\n--- PREDICTIVE CONTENT ---"
)

print(
    "Rows:",
    len(alpha_df)
)


# ------------------------------------------------------------
# CROSS-DAY ALPHA AGGREGATION
# ------------------------------------------------------------

if len(alpha_df):

    alpha_sum = alpha_df.groupby(
        [
            'feature',
            'family',
            'base',
            'T',
            'horizon'
        ],
        as_index=False
    ).agg({

        'pearson':'median',

        'spearman':'median',

        'mutual_information':'median',

        'n':'sum',

        'day':'nunique'

    })

    alpha_sum[
        'abs_pearson'
    ] = alpha_sum[
        'pearson'
    ].abs()

    alpha_sum[
        'abs_spearman'
    ] = alpha_sum[
        'spearman'
    ].abs()

    alpha_sum[
        'alpha_score'
    ] = (

        0.40 *
        alpha_sum[
            'abs_pearson'
        ]

        +

        0.35 *
        alpha_sum[
            'abs_spearman'
        ]

        +

        0.25 *
        alpha_sum[
            'mutual_information'
        ]

    )

else:

    alpha_sum = pd.DataFrame()


# ------------------------------------------------------------
# FORENSIC INFORMATION
# ------------------------------------------------------------

if len(alpha_sum) > 0 and len(hyp_df) > 0:
# if len(hyp_df):

    keep = [
        'feature',
        'best_candidate',
        'confidence',
        'score',
        'days'
    ]

    keep = [
        c for c in keep
        if c in hyp_df.columns
    ]

    h = hyp_df[
        keep
    ].drop_duplicates(
        'feature'
    )

    alpha_sum = alpha_sum.merge(
        h,
        on='feature',
        how='left'
    )


# ------------------------------------------------------------
# FINAL ALPHA RANK
# ------------------------------------------------------------

if len(alpha_sum):

    alpha_sum = alpha_sum.sort_values(
        [
            'horizon',
            'alpha_score'
        ],
        ascending=[
            True,
            False
        ]
    ).reset_index(
        drop=True
    )

    alpha_sum[
        'horizon_rank'
    ] = alpha_sum.groupby(
        'horizon'
    )[
        'alpha_score'
    ].rank(
        ascending=False,
        method='min'
    )

    alpha_sum[
        'feature_rank'
    ] = alpha_sum.groupby(
        'feature'
    )[
        'alpha_score'
    ].rank(
        ascending=False,
        method='min'
    )

    alpha_sum.to_csv(
        ALPHA_FILE,
        index=False
    )


# ------------------------------------------------------------
# 4I — FEATURE REDUNDANCY
# ------------------------------------------------------------

CORR_ROWS = []

PCA_DATA = []

for di,file in enumerate(
    comp_files,
    1
):

    d = get_day_number(
        file
    )

    print(
        f"\n[{di}/{len(comp_files)}] "
        f"Day {d} redundancy"
    )

    raw = pd.read_csv(
        file,
        usecols=lambda c:
        c in features
    )

    fcols = [
        c for c in features
        if c in raw.columns
    ]

    if len(fcols)<2:

        continue

    x = raw[fcols].apply(
        pd.to_numeric,
        errors='coerce'
    )

    # Use the stored feature values directly.
    # Standardization is required only for
    # redundancy/PCA and is not a feature
    # reconstruction.

    x = x.astype(
        np.float64
    )

    x = x.replace(
        [np.inf,-np.inf],
        np.nan
    )

    x = x.fillna(
        x.median()
    )

    sd = x.std(
        ddof=0
    ).replace(
        0,
        np.nan
    )

    z = (
        x-x.mean()
    ).div(
        sd
    )

    z = z.replace(
        [np.inf,-np.inf],
        np.nan
    ).fillna(0)

    c = z.corr(
        method='pearson'
    )

    for i,f1 in enumerate(fcols):

        for j in range(
            i+1,
            len(fcols)
        ):

            f2 = fcols[j]

            v = c.loc[
                f1,
                f2
            ]

            if np.isfinite(v):

                CORR_ROWS.append({

                    'day':d,

                    'feature_1':f1,

                    'feature_2':f2,

                    'family_1':finfo.loc[
                        f1,
                        'family'
                    ],

                    'family_2':finfo.loc[
                        f2,
                        'family'
                    ],

                    'base_1':finfo.loc[
                        f1,
                        'base'
                    ],

                    'base_2':finfo.loc[
                        f2,
                        'base'
                    ],

                    'T1':finfo.loc[
                        f1,
                        'T'
                    ],

                    'T2':finfo.loc[
                        f2,
                        'T'
                    ],

                    'pearson':float(v)

                })

    PCA_DATA.append(
        z[fcols]
    )


corr_day_df = pd.DataFrame(
    CORR_ROWS
)

print(
    "\n--- REDUNDANCY ---"
)

print(
    "Pair rows:",
    len(corr_day_df)
)


# ------------------------------------------------------------
# CROSS-DAY CORRELATION SUMMARY
# ------------------------------------------------------------

if len(corr_day_df):

    corr_df = corr_day_df.groupby(
        [
            'feature_1',
            'feature_2',
            'family_1',
            'family_2',
            'base_1',
            'base_2',
            'T1',
            'T2'
        ],
        as_index=False
    ).agg({

        'pearson':'median',

        'day':'nunique'

    })

    corr_df[
        'abs_pearson'
    ] = corr_df[
        'pearson'
    ].abs()

    corr_df = corr_df.sort_values(
        'abs_pearson',
        ascending=False
    )

    corr_df.to_csv(
        CORR_FILE,
        index=False
    )

else:

    corr_df = pd.DataFrame()


# ------------------------------------------------------------
# CORRELATION MATRIX
# ------------------------------------------------------------

if len(corr_df):

    cm = pd.DataFrame(
        np.eye(len(features)),
        index=features,
        columns=features
    )

    for _,r in corr_df.iterrows():

        f1 = r['feature_1']
        f2 = r['feature_2']
        v = r['pearson']

        cm.loc[f1,f2] = v
        cm.loc[f2,f1] = v

    plt.figure(
        figsize=(14,12)
    )

    plt.imshow(
        cm.to_numpy(),
        aspect='auto',
        interpolation='nearest'
    )

    plt.colorbar(
        label='Pearson correlation'
    )

    plt.xlabel(
        'Feature'
    )

    plt.ylabel(
        'Feature'
    )

    plt.title(
        'EBX Feature Correlation Matrix'
    )

    plt.tight_layout()

    plt.savefig(
        CORR_PNG,
        dpi=150
    )

    plt.show()


# ------------------------------------------------------------
# PCA
# ------------------------------------------------------------

if len(PCA_DATA):

    pca = IncrementalPCA(
        n_components=min(
            PCA_COMPONENTS,
            len(features)
        ),
        batch_size=PCA_BATCH
    )

    for z in PCA_DATA:

        a = z.to_numpy(
            dtype=np.float64
        )

        for st in range(
            0,
            len(a),
            PCA_BATCH
        ):

            en = min(
                st+PCA_BATCH,
                len(a)
            )

            pca.partial_fit(
                a[st:en]
            )

    rows = []

    ev = pca.explained_variance_ratio_

    cev = np.cumsum(ev)

    for i in range(
        len(ev)
    ):

        rows.append({

            'component':i+1,

            'explained_variance_ratio':
                ev[i],

            'cumulative_explained_variance':
                cev[i]

        })

    pca_df = pd.DataFrame(
        rows
    )

    pca_df.to_csv(
        PCA_FILE,
        index=False
    )

    plt.figure(
        figsize=(9,5)
    )

    plt.plot(
        pca_df['component'],
        pca_df[
            'explained_variance_ratio'
        ],
        marker='o'
    )

    plt.xlabel(
        'Principal component'
    )

    plt.ylabel(
        'Explained variance ratio'
    )

    plt.title(
        'EBX Feature PCA Scree Plot'
    )

    plt.grid(
        alpha=0.3
    )

    plt.tight_layout()

    plt.savefig(
        PCA_PNG,
        dpi=150
    )

    plt.show()

else:

    pca_df = pd.DataFrame()


# ------------------------------------------------------------
# 4J — OPTIONAL GRANGER CAUSALITY
# ------------------------------------------------------------

if RUN_GRANGER:

    try:

        from statsmodels.tsa.stattools import grangercausalitytests

        GRANGER_ROWS = []

        if len(alpha_sum):

            cand = (
                alpha_sum[
                    alpha_sum[
                        'horizon'
                    ]==60
                ]
                .sort_values(
                    'alpha_score',
                    ascending=False
                )
                .groupby(
                    'feature',
                    as_index=False
                )
                .head(5)
            )

            for _,r in cand.iterrows():

                f = r['feature']

                print(
                    "Granger:",
                    f
                )

                for file in comp_files:

                    d = get_day_number(
                        file
                    )

                    ret_file = (
                        RET_DIR /
                        f'day{d}_returns.csv'
                    )

                    if not ret_file.exists():

                        continue

                    raw = pd.read_csv(
                        file
                    )

                    ret = pd.read_csv(
                        ret_file
                    )

                    if f not in raw.columns:

                        continue

                    ydf = future_returns(
                        ret
                    )

                    z = pd.DataFrame({

                        'return':
                            ydf[60],

                        'feature':
                            pd.to_numeric(
                                raw[f],
                                errors='coerce'
                            )

                    }).dropna()

                    if len(z)<MIN_N:

                        continue

                    try:

                        g = grangercausalitytests(
                            z[
                                [
                                    'return',
                                    'feature'
                                ]
                            ],
                            maxlag=GRANGER_LAGS,
                            verbose=False
                        )

                        for lag,v in g.items():

                            p = v[0][
                                'ssr_ftest'
                            ][1]

                            GRANGER_ROWS.append({

                                'day':d,

                                'feature':f,

                                'horizon':60,

                                'lag':lag,

                                'p_value':p

                            })

                    except Exception:

                        continue

        granger_df = pd.DataFrame(
            GRANGER_ROWS
        )

        if len(granger_df):

            granger_df.to_csv(
                GRANGER_FILE,
                index=False
            )

    except ImportError:

        print(
            "\nstatsmodels not installed; "
            "Granger skipped."
        )

else:

    print(
        "\n--- GRANGER ---"
    )

    print(
        "Skipped: RUN_GRANGER=False"
    )


# ------------------------------------------------------------
# FINAL OUTPUT
# ------------------------------------------------------------

print(
    "\n--- FILES WRITTEN ---"
)

print(
    ALPHA_FILE
)

print(
    CORR_FILE
)

print(
    PCA_FILE
)

if RUN_GRANGER:

    print(
        GRANGER_FILE
    )

print(
    "\nAlpha rows:",
    len(alpha_df)
)

print(
    "Alpha ranking rows:",
    len(alpha_sum)
)

print(
    "Correlation rows:",
    len(corr_df)
)

print(
    "PCA rows:",
    len(pca_df)
)

print(
    "\nDone."
)