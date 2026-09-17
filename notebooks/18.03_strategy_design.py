# FILE 18

from pathlib import Path
import re
import numpy as np
import pandas as pd


def get_day_number(file):
    res = re.search(r'day[\s]?(\d+)',file.stem,re.IGNORECASE)
    return int(res.group(1)) if res else None


def normalize_day(x):
    if pd.isna(x): return pd.NA
    if isinstance(x,(int,np.integer)): return int(x)
    if isinstance(x,(float,np.floating)): return int(x) if not np.isnan(x) else pd.NA
    s = str(x).strip().strip('{}')
    if s.isdigit(): return int(s)
    res = re.search(r'day[\s]?(\d+)',s,re.IGNORECASE)
    return int(res.group(1)) if res else pd.NA


DATA_DIR = Path(r'.\EBX_Dataset')
OUTPUT_DIR = Path(r'.\output')

ALPHA_FILE = OUTPUT_DIR / "17_feature_alpha_rank.csv"
CORR_FILE = OUTPUT_DIR / "17_feature_correlation.csv"

SELECTION_FILE = OUTPUT_DIR / "18_strategy_selection.csv"
CONFIG_FILE = OUTPUT_DIR / "18_strategy_config.csv"
FAMILY_FILE = OUTPUT_DIR / "18_family_summary.csv"
FINALISTS_FILE = OUTPUT_DIR / "18_strategy_finalists.csv"
AVAILABILITY_FILE = OUTPUT_DIR / "18_feature_availability.csv"

REBALANCE = 1
HORIZON = 10
EXECUTION_LAG = 1
COST_BPS = 7.5
MAX_EXPOSURE = 1.0

THRESHOLDS = [0.5,0.75,1.0,1.25,1.5]

TRAIN_DAYS = list(range(1,44))
VALIDATION_DAYS = list(range(44,55))
TEST_DAYS = list(range(55,65)) + list(range(80,86))

DISCOVERY_DAYS = TRAIN_DAYS + VALIDATION_DAYS
ALL_DAYS = DISCOVERY_DAYS + TEST_DAYS
EXPECTED_DAYS = list(range(1,65)) + list(range(80,86))

FINALISTS = 10


# ------------------------------------------------------------
# 5A — STRATEGY UNIVERSE
# ------------------------------------------------------------

if len(TRAIN_DAYS) != 43:
    raise ValueError("Training split must contain 43 days")

if len(VALIDATION_DAYS) != 11:
    raise ValueError("Validation split must contain 11 days")

if len(TEST_DAYS) != 16:
    raise ValueError("Test split must contain 16 days")

if len(DISCOVERY_DAYS) != 54:
    raise ValueError("Discovery split must contain 54 days")

if len(ALL_DAYS) != 70:
    raise ValueError("Strategy day universe is not 70 days")

if len(set(ALL_DAYS)) != 70:
    raise ValueError("Duplicate days in strategy split")

if set(ALL_DAYS) != set(EXPECTED_DAYS):
    raise ValueError("Strategy split does not match usable-day universe")

if set(TRAIN_DAYS) & set(VALIDATION_DAYS):
    raise ValueError("Train/validation overlap")

if set(TRAIN_DAYS) & set(TEST_DAYS):
    raise ValueError("Train/test overlap")

if set(VALIDATION_DAYS) & set(TEST_DAYS):
    raise ValueError("Validation/test overlap")


print("\n--- TASK 5 STRATEGY DESIGN ---")

print(
    "\nTrain days:",
    TRAIN_DAYS[0],
    "-",
    TRAIN_DAYS[-1],
    len(TRAIN_DAYS)
)

print(
    "Validation days:",
    VALIDATION_DAYS[0],
    "-",
    VALIDATION_DAYS[-1],
    len(VALIDATION_DAYS)
)

print(
    "Discovery days:",
    DISCOVERY_DAYS[0],
    "-",
    DISCOVERY_DAYS[-1],
    len(DISCOVERY_DAYS)
)

print(
    "Test days:",
    TEST_DAYS,
    len(TEST_DAYS)
)


if not ALPHA_FILE.exists():
    raise FileNotFoundError(ALPHA_FILE)

if not CORR_FILE.exists():
    raise FileNotFoundError(CORR_FILE)

if not DATA_DIR.exists():
    raise FileNotFoundError(DATA_DIR)


alpha_df = pd.read_csv(ALPHA_FILE)
corr_df = pd.read_csv(CORR_FILE)

print("\nAlpha shape:",alpha_df.shape)
print("Correlation shape:",corr_df.shape)


# ------------------------------------------------------------
# 5B — TASK 4 ALPHA ARTIFACT
# ------------------------------------------------------------

alpha_df.columns = [
    str(x).strip('*').strip()
    for x in alpha_df.columns
]

req = [
    'feature',
    'family',
    'horizon',
    'alpha_score',
    'spearman',
    'mutual_information'
]

for col in req:
    if col not in alpha_df.columns:
        raise ValueError(
            f"{col} missing from 17_feature_alpha_rank.csv"
        )


for col in [
    'horizon',
    'alpha_score',
    'mutual_information',
    'spearman',
    'pearson',
    'days'
]:

    if col in alpha_df.columns:

        alpha_df[col] = pd.to_numeric(
            alpha_df[col],
            errors='coerce'
        )


alpha_df['feature'] = (
    alpha_df['feature']
    .astype(str)
    .str.strip()
)

alpha_df['family'] = (
    alpha_df['family']
    .astype(str)
    .str.strip()
)


alpha_df = alpha_df.dropna(
    subset=[
        'feature',
        'family',
        'horizon',
        'alpha_score'
    ]
)


print("\nHorizon counts:")
print(
    alpha_df['horizon']
    .value_counts()
    .sort_index()
)


# ------------------------------------------------------------
# IMPORTANT:
#
# File 17 contains feature-level Task-4 candidates.
# Its 1152 rows = 288 features x 4 horizons.
#
# Therefore a column called `day`, if present, is NOT
# automatically interpreted as a day-level observation.
#
# Never filter this aggregated artifact by TRAIN_DAYS,
# VALIDATION_DAYS or TEST_DAYS.
# ------------------------------------------------------------

cand = alpha_df[
    alpha_df['horizon']==HORIZON
].copy()


if len(cand)==0:
    raise ValueError(
        f"No Task 4 candidates found for horizon {HORIZON}"
    )


# One feature should have one horizon-10 candidate.
dup = (
    cand
    .groupby(['feature','horizon'])
    .size()
)

if (dup>1).any():

    print(
        "\nWARNING: duplicate feature/horizon rows found in "
        "File 17. Aggregating duplicate Task-4 rows."
    )

    rows = []

    for key,g in cand.groupby(
        ['feature','horizon'],
        dropna=False
    ):

        row = {
            'feature':key[0],
            'horizon':key[1],
            'family':g['family'].dropna().iloc[0]
            if g['family'].notna().any()
            else ""
        }

        for col in [
            'pearson',
            'spearman',
            'mutual_information',
            'alpha_score',
            'score',
            'stability'
        ]:

            if col in g.columns:
                row[col] = g[col].mean()

        for col in [
            'best_candidate',
            'confidence'
        ]:

            if col in g.columns:

                x = (
                    g[col]
                    .dropna()
                    .astype(str)
                    .str.strip()
                )

                row[col] = x.iloc[0] if len(x) else ""

        if 'days' in g.columns:
            row['days'] = g['days'].max()

        rows.append(row)

    cand = pd.DataFrame(rows)


if cand['feature'].duplicated().any():

    raise ValueError(
        "File 17 still contains multiple horizon-10 rows "
        "for the same feature after normalization"
    )


if len(cand) != 288:

    print(
        "\nWARNING: horizon-10 candidate count is",
        len(cand),
        "(expected 288 from the current File 17 artifact)"
    )


print(
    "\nHorizon-10 candidates:",
    len(cand)
)


# ------------------------------------------------------------
# 5C — TASK 4 DISCOVERY COVERAGE
# ------------------------------------------------------------

#
# `days` is retained as Task-4 evidence/coverage.
#
# It is NOT silently interpreted as discovery-day coverage.
# It is NOT multiplied by a fabricated 54-day denominator.
#
# If File 17 was computed on the complete Task-4 usable universe,
# that information remains part of the Task-4 evidence.
#

if 'days' in cand.columns:

    cand['days'] = pd.to_numeric(
        cand['days'],
        errors='coerce'
    )

    cand['coverage'] = (
        cand['days']
        / len(ALL_DAYS)
    ).clip(0,1)

else:

    cand['coverage'] = 1.0


cand = cand.sort_values(
    [
        'alpha_score',
        'mutual_information'
    ],
    ascending=[False,False]
).reset_index(drop=True)

cand['predictive_rank'] = (
    np.arange(1,len(cand)+1)
)


print("\nTop Task-4 horizon-10 candidates:")

cols = [
    'feature',
    'family',
    'horizon',
    'alpha_score',
    'spearman',
    'mutual_information',
    'days',
    'coverage'
]

cols = [
    x for x in cols
    if x in cand.columns
]

print(
    cand[cols]
    .head(15)
    .to_string(index=False)
)


# ------------------------------------------------------------
# 5D — REDUNDANCY
# ------------------------------------------------------------

corr_df.columns = [
    str(x).strip('*').strip()
    for x in corr_df.columns
]


if (
    'feature_1' not in corr_df.columns
    or
    'feature_2' not in corr_df.columns
):

    raise ValueError(
        "Feature-pair columns missing from "
        "17_feature_correlation.csv"
    )


if 'abs_pearson' not in corr_df.columns:

    if 'pearson' in corr_df.columns:

        corr_df['abs_pearson'] = (
            pd.to_numeric(
                corr_df['pearson'],
                errors='coerce'
            )
            .abs()
        )

    else:

        raise ValueError(
            "Correlation strength column missing"
        )


corr_df['feature_1'] = (
    corr_df['feature_1']
    .astype(str)
    .str.strip()
)

corr_df['feature_2'] = (
    corr_df['feature_2']
    .astype(str)
    .str.strip()
)

corr_df['abs_pearson'] = pd.to_numeric(
    corr_df['abs_pearson'],
    errors='coerce'
)

corr_df = corr_df.dropna(
    subset=[
        'feature_1',
        'feature_2',
        'abs_pearson'
    ]
)


# Only redundancy among the actual Task-4 candidate universe.
candidate_features = set(
    cand['feature']
)


corr_df = corr_df[
    corr_df['feature_1'].isin(candidate_features)
    &
    corr_df['feature_2'].isin(candidate_features)
].copy()


# Remove self-pairs.
corr_df = corr_df[
    corr_df['feature_1']
    !=
    corr_df['feature_2']
].copy()


red = {}

for f in cand['feature'].unique():

    q = corr_df[
        (
            (corr_df['feature_1']==f)
            |
            (corr_df['feature_2']==f)
        )
    ]

    red[f] = (
        q['abs_pearson'].max()
        if len(q)
        else np.nan
    )


cand['max_redundancy'] = (
    cand['feature'].map(red)
)


print(
    "\nCandidate-pool correlation pairs:",
    len(corr_df)
)


# ------------------------------------------------------------
# 5E — FORENSIC EVIDENCE
# ------------------------------------------------------------

cand['forensic_ok'] = True


if 'best_candidate' in cand.columns:

    cand['forensic_ok'] = (
        cand['best_candidate']
        .notna()
        &
        cand['best_candidate']
        .astype(str)
        .str.strip()
        .ne('')
    )


cand['selection_score'] = (
    cand['alpha_score']
    * cand['coverage']
    * np.where(cand['max_redundancy'].isna(),1.0,np.where(cand['max_redundancy']<=0.80,1.0, 1.0 - 0.35*(cand['max_redundancy']-0.80)/0.20))
    * np.where(cand['forensic_ok'],1.0,0.90)
)


cand = cand.sort_values(
    [
        'selection_score',
        'alpha_score',
        'mutual_information',
        'coverage'
    ],
    ascending=[False,False,False,False]
).reset_index(drop=True)

cand['selection_rank'] = (
    np.arange(1,len(cand)+1)
)


print("\n--- CANDIDATE SELECTION ---")

cols = [
    'selection_rank',
    'feature',
    'family',
    'horizon',
    'alpha_score',
    'mutual_information',
    'spearman',
    'max_redundancy',
    'coverage',
    'forensic_ok',
    'selection_score'
]

cols = [
    x for x in cols
    if x in cand.columns
]

print(
    cand[cols]
    .head(20)
    .to_string(index=False)
)


# ------------------------------------------------------------
# 5F — INPUT FILE / FEATURE AVAILABILITY
# ------------------------------------------------------------

csv_files = sorted(
    DATA_DIR.glob("*.csv"),
    key=lambda x: (
        get_day_number(x) is None,
        get_day_number(x)
        if get_day_number(x) is not None
        else 10**9
    )
)


files = {
    get_day_number(f):f
    for f in csv_files
    if get_day_number(f) is not None
}


missing_days = [
    d for d in ALL_DAYS
    if d not in files
]


if missing_days:

    raise ValueError(
        f"Missing strategy input files for days: {missing_days}"
    )


comp_files = [
    files[d]
    for d in ALL_DAYS
]


print(
    "\nFiles available for strategy:",
    len(comp_files)
)


# Read headers once.
headers = {}

for d in ALL_DAYS:

    headers[d] = set(
        pd.read_csv(
            files[d],
            nrows=0
        ).columns
    )


# ------------------------------------------------------------
# Check ALL finalists, but do NOT let test availability
# alter selection score.
# ------------------------------------------------------------

fcols = (
    cand['feature']
    .head(FINALISTS)
    .tolist()
)


if not fcols:
    raise ValueError(
        "No strategy finalists available"
    )


av = []

for d in ALL_DAYS:

    h = headers[d]

    for feat in fcols:

        av.append({
            'day':d,
            'feature':feat,
            'available':feat in h,
            'split':(
                'train'
                if d in TRAIN_DAYS
                else
                'validation'
                if d in VALIDATION_DAYS
                else
                'test'
            )
        })


av_df = pd.DataFrame(av)


av_sum = (
    av_df
    .groupby(['feature','split'])
    .agg(
        days_available=('available','sum'),
        days_checked=('day','nunique')
    )
    .reset_index()
)


av_sum['coverage'] = (
    av_sum['days_available']
    /
    av_sum['days_checked']
)


print("\nFinalist availability:")
print(
    av_sum
    .sort_values(
        ['feature','split']
    )
    .to_string(index=False)
)


# Full implementation availability is diagnostic only.
av_full = (
    av_df
    .groupby('feature')
    .agg(
        days_available=('available','sum'),
        days_checked=('day','nunique')
    )
    .reset_index()
)

av_full['file_coverage'] = (
    av_full['days_available']
    /
    av_full['days_checked']
)


av_full.to_csv(
    AVAILABILITY_FILE,
    index=False
)


# ------------------------------------------------------------
# IMPORTANT:
#
# Availability does NOT participate in feature ranking.
#
# A feature can only be selected using Task-4 evidence.
# File availability is checked afterward as an implementation
# requirement.
# ------------------------------------------------------------

cand = cand.merge(
    av_full[
        [
            'feature',
            'days_available',
            'days_checked',
            'file_coverage'
        ]
    ],
    on='feature',
    how='left'
)


cand['file_coverage'] = (
    cand['file_coverage']
    .fillna(0)
)


# Discovery availability is allowed to act as an
# implementation filter because the strategy cannot be
# trained/validated without the feature.
#
# Test availability is NOT used here.

disc_av = (
    av_df[
        av_df['day'].isin(DISCOVERY_DAYS)
    ]
    .groupby('feature')
    .agg(
        discovery_days_available=('available','sum'),
        discovery_days_checked=('day','nunique')
    )
    .reset_index()
)


disc_av['discovery_file_coverage'] = (
    disc_av['discovery_days_available']
    /
    disc_av['discovery_days_checked']
)


cand = cand.merge(
    disc_av,
    on='feature',
    how='left'
)


cand['discovery_file_coverage'] = (
    cand['discovery_file_coverage']
    .fillna(0)
)


# A strategy candidate must be implementable throughout
# train + validation. Test is checked later.
cand = cand[
    cand['discovery_file_coverage']==1.0
].copy()


if len(cand)==0:

    raise ValueError(
        "No Task-4 candidates are available across all "
        "54 train/validation discovery days"
    )


# Selection score is NOT multiplied by test availability.
cand = cand.sort_values(
    [
        'selection_score',
        'alpha_score',
        'mutual_information',
        'coverage'
    ],
    ascending=[False,False,False,False]
).reset_index(drop=True)

cand['selection_rank'] = (
    np.arange(1,len(cand)+1)
)


# ------------------------------------------------------------
# 5G — SELECT FEATURE
# ------------------------------------------------------------

top = cand.iloc[0]

FEATURE = str(top['feature'])
FAMILY = str(top['family'])

BEST_CANDIDATE = (
    str(top['best_candidate'])
    if
    'best_candidate' in top.index
    and
    not pd.isna(top['best_candidate'])
    else ""
)


SPEARMAN = (
    float(top['spearman'])
    if
    'spearman' in top.index
    and
    not pd.isna(top['spearman'])
    else 0.0
)


if SPEARMAN!=0:

    SIGNAL_SIGN = (
        1
        if SPEARMAN>0
        else -1
    )

else:

    PEARSON = (
        float(top['pearson'])
        if
        'pearson' in top.index
        and
        not pd.isna(top['pearson'])
        else 0.0
    )

    SIGNAL_SIGN = (
        1
        if PEARSON>=0
        else -1
    )


print(
    "\nSelected Task-4 feature:",
    FEATURE
)

print(
    "Selected family:",
    FAMILY
)

print(
    "Forensic hypothesis:",
    BEST_CANDIDATE
)

print(
    "Signal direction:",
    SIGNAL_SIGN
)


# ------------------------------------------------------------
# Explicit test availability check.
#
# This does NOT alter selection.
# It only determines whether the locked strategy can actually
# be executed on the untouched test universe.
# ------------------------------------------------------------

test_missing = [
    d
    for d in TEST_DAYS
    if FEATURE not in headers[d]
]


if test_missing:

    raise ValueError(
        f"Selected feature {FEATURE} is unavailable on "
        f"test days {test_missing}"
    )


# ------------------------------------------------------------
# 5H — SELECTION OUTPUT
# ------------------------------------------------------------

sel_cols = [
    'selection_rank',
    'feature',
    'family',
    'base',
    'T',
    'horizon',
    'pearson',
    'spearman',
    'mutual_information',
    'n',
    'day',
    'abs_pearson',
    'abs_spearman',
    'alpha_score',
    'best_candidate',
    'confidence',
    'score',
    'days',
    'predictive_rank',
    'coverage',
    'horizon_rank',
    'feature_rank',
    'max_redundancy',
    'stability',
    'forensic_ok',
    'discovery_days_available',
    'discovery_days_checked',
    'discovery_file_coverage',
    'days_available',
    'days_checked',
    'file_coverage',
    'selection_score'
]

sel_cols = [
    x for x in sel_cols
    if x in cand.columns
]


cand[sel_cols].head(
    max(FINALISTS,20)
).to_csv(
    SELECTION_FILE,
    index=False
)


cand.head(
    FINALISTS
).to_csv(
    FINALISTS_FILE,
    index=False
)


# ------------------------------------------------------------
# 5I — TRAIN-ONLY NORMALIZATION
# ------------------------------------------------------------

train_vals = []


for d in TRAIN_DAYS:

    f = files.get(d)

    if f is None:

        raise ValueError(
            f"Missing training file for day {d}"
        )

    if FEATURE not in headers[d]:

        raise ValueError(
            f"{FEATURE} missing from training day {d}"
        )


    df = pd.read_csv(
        f,
        usecols=[FEATURE]
    )


    x = pd.to_numeric(
        df[FEATURE],
        errors='coerce'
    ).replace(
        [np.inf,-np.inf],
        np.nan
    ).dropna()


    if len(x):

        train_vals.append(x)


if not train_vals:

    raise ValueError(
        "No training feature data found for selected feature"
    )


train_x = pd.concat(
    train_vals,
    ignore_index=True
)


TRAIN_MEAN = train_x.mean()
TRAIN_STD = train_x.std(ddof=0)


if not np.isfinite(TRAIN_MEAN):

    raise ValueError(
        "Invalid training mean"
    )


if not np.isfinite(TRAIN_STD) or TRAIN_STD<=0:

    raise ValueError(
        "Invalid training standard deviation"
    )


print("\nTraining normalization:")

print(
    "Mean:",
    TRAIN_MEAN
)

print(
    "Std :",
    TRAIN_STD
)


# ------------------------------------------------------------
# 5J — THRESHOLD GRID
# ------------------------------------------------------------

threshold_rows = []

for th in THRESHOLDS:

    threshold_rows.append({

        'threshold':th,

        'long_rule':
            f'z > {th}',

        'short_rule':
            f'z < {-th}',

        'flat_rule':
            f'{-th} <= z <= {th}',

        'position_rule':
            'LONG=+1, FLAT=0, SHORT=-1',

        'execution':
            f't+{EXECUTION_LAG}'

    })


threshold_df = pd.DataFrame(
    threshold_rows
)


print("\n--- THRESHOLD GRID ---")

print(
    threshold_df
    .to_string(index=False)
)


# ------------------------------------------------------------
# 5K — STRATEGY CONFIGURATION
# ------------------------------------------------------------

CONFIG = {

    'feature':
        FEATURE,

    'family':
        FAMILY,

    'forensic_hypothesis':
        BEST_CANDIDATE,

    'rebalance_minutes':
        REBALANCE,

    'feature_horizon':
        HORIZON,

    'horizon_semantics':
        'PREDICTIVE_TARGET_HORIZON_NOT_HOLDING_PERIOD',

    'execution_lag_minutes':
        EXECUTION_LAG,

    'signal':
        'signal_t = signal_direction * z_t',

    'z_score':
        'z_t = (feature_t - train_mean) / train_std',

    'signal_direction':
        SIGNAL_SIGN,

    'normalization':
        'TRAIN_ONLY_MEAN_STD',

    'train_mean':
        TRAIN_MEAN,

    'train_std':
        TRAIN_STD,

    'thresholds':
        ','.join(map(str,THRESHOLDS)),

    'position_rule':
        'LONG=+1 if signal>threshold; '
        'FLAT=0 if abs(signal)<=threshold; '
        'SHORT=-1 if signal<-threshold',

    'max_exposure':
        MAX_EXPOSURE,

    'transaction_cost_bps':
        COST_BPS,

    'turnover_model':
        'absolute_position_change',

    'cost_application':
        'abs(position_t-position_t_minus_1)*cost_bps',

    'train_start':
        TRAIN_DAYS[0],

    'train_end':
        TRAIN_DAYS[-1],

    'validation_start':
        VALIDATION_DAYS[0],

    'validation_end':
        VALIDATION_DAYS[-1],

    'test_days':
        ','.join(map(str,TEST_DAYS)),

    'lookahead_rule':
        'feature_t -> signal_t -> execute_t+1',

    'candidate_selection_source':
        '17_feature_alpha_rank',

    'candidate_selection_scope':
        'TASK4_AGGREGATED_DISCOVERY_ARTIFACT',

    'discovery_days':
        ','.join(map(str,DISCOVERY_DAYS)),

    'parameter_selection_rule':
        'TRAIN_DISCOVERY_VALIDATION_SELECTION_TEST_LOCKED',

    'test_usage':
        'NO_FEATURE_OR_THRESHOLD_SELECTION',

    'threshold_selection':
        'VALIDATION_ONLY',

    'final_test_rule':
        'LOCK_FEATURE_AND_THRESHOLD_BEFORE_TEST',

    'position_continuity':
        '1_MINUTE_REBALANCE',

    'test_availability':
        'VALIDATE_ONLY_NOT_SELECTION_CRITERION',

    'diagnostics_required':
        'long_fraction,short_fraction,flat_fraction,'
        'active_fraction,mean_abs_position,'
        'trade_count,turnover,gross_return,net_return'

}


config_df = pd.DataFrame(
    [
        {
            'parameter':k,
            'value':v
        }
        for k,v in CONFIG.items()
    ]
)


config_df.to_csv(
    CONFIG_FILE,
    index=False
)


# ------------------------------------------------------------
# 5L — FAMILY SUMMARY
# ------------------------------------------------------------

family_summary = (
    cand
    .groupby('family')
    .agg(
        candidates=('feature','count'),
        best_selection_score=('selection_score','max'),
        best_alpha=('alpha_score','max'),
        mean_alpha=('alpha_score','mean'),
        mean_coverage=('coverage','mean'),
        mean_discovery_file_coverage=(
            'discovery_file_coverage',
            'mean'
        )
    )
    .sort_values(
        'best_selection_score',
        ascending=False
    )
    .reset_index()
)


family_summary.to_csv(
    FAMILY_FILE,
    index=False
)


# ------------------------------------------------------------
# 5M — FINAL REPORT
# ------------------------------------------------------------

print(
    "\n--- STRATEGY SPECIFICATION ---"
)

print(
    "FEATURE       :",
    FEATURE
)

print(
    "FAMILY        :",
    FAMILY
)

print(
    "HYPOTHESIS    :",
    BEST_CANDIDATE
)

print(
    "REBALANCE     :",
    f"{REBALANCE} minute"
)

print(
    "HORIZON       :",
    f"{HORIZON} predictive minutes"
)

print(
    "EXECUTION     :",
    f"signal_t -> execute_t+{EXECUTION_LAG}"
)

print(
    "DIRECTION     :",
    SIGNAL_SIGN
)

print(
    "NORMALIZATION : TRAIN ONLY"
)

print(
    "TRAIN MEAN    :",
    TRAIN_MEAN
)

print(
    "TRAIN STD     :",
    TRAIN_STD
)

print(
    "THRESHOLDS    :",
    THRESHOLDS
)

print(
    "POSITION      : LONG=+1, FLAT=0, SHORT=-1"
)

print(
    "MAX EXPOSURE  :",
    MAX_EXPOSURE
)

print(
    "COST          :",
    COST_BPS,
    "bps"
)

print(
    "\nTrain       :",
    TRAIN_DAYS[0],
    "-",
    TRAIN_DAYS[-1]
)

print(
    "Validation  :",
    VALIDATION_DAYS[0],
    "-",
    VALIDATION_DAYS[-1]
)

print(
    "Test        :",
    TEST_DAYS
)

print(
    "\nDiscovery feature coverage:",
    top['coverage']
)

print(
    "Discovery file coverage:",
    top['discovery_file_coverage']
)

print(
    "Full file coverage:",
    top['file_coverage']
)

print(
    "\n--- FILES WRITTEN ---"
)

print(
    SELECTION_FILE
)

print(
    FINALISTS_FILE
)

print(
    FAMILY_FILE
)

print(
    CONFIG_FILE
)

print(
    AVAILABILITY_FILE
)


print(
    "\n--- TEST LOCK ---"
)

print(
    "Test days are NOT used for feature ranking."
)

print(
    "Test days are NOT used for normalization."
)

print(
    "Test days are NOT used for threshold selection."
)

print(
    "Test availability is checked but does NOT affect selection."
)

print(
    "HORIZON is NOT treated as a holding period."
)

print(
    "File 19 must select the threshold on VALIDATION only."
)

print(
    "File 19 must lock feature + threshold before TEST."
)

print(
    "\nDone."
)