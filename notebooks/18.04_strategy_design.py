# ------------------------------------------------------------
# FILE 18 — STRATEGY DESIGN (robust)
#
# What changed vs. the previous version, and why:
#
# 1. [CRITICAL FIX] Candidate ranking no longer uses
#    17_feature_alpha_rank.csv's alpha_score. That file is a
#    median over ALL 70 comp_files (train+validation+test), so
#    using it for feature selection was test-day leakage even
#    though the code print()ed "test days are NOT used for
#    feature ranking." This file now reads the new
#    17_feature_alpha_daily.csv (per-day granular rows, one
#    per day/feature/horizon) and re-aggregates pearson/
#    spearman/MI itself, restricted to DISCOVERY_DAYS only.
#    That re-aggregation is what candidate selection is based on.
#
# 2. The full-universe alpha_rank.csv is still loaded, but only
#    as a labeled diagnostic column (full_alpha_score,
#    full_universe_days) so you can see how much the discovery-
#    only ranking differs from the old, leaky one. It never
#    feeds selection_score.
#
# 3. Redundancy penalty is now continuous (ramps from 0.80 to
#    1.00 correlation instead of a hard 0.95 cliff), removing
#    the near-duplicate-candidates-treated-wildly-differently
#    problem.
#
# 4. FINALISTS is now guarded: raises if fewer than FINALISTS
#    discovery-eligible candidates exist, instead of silently
#    truncating.
#
# 5. get_day_number regex now matches File 17's regex exactly
#    (both allow an underscore before the day number).
#
# 6. CONFIG carries two extra, unambiguous instructions for
#    File 19: the bps->decimal cost conversion and the
#    day-boundary position reset rule, so neither can be
#    silently implemented wrong downstream.
# ------------------------------------------------------------

from pathlib import Path
import re
import numpy as np
import pandas as pd


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

ALPHA_DAILY_FILE = OUTPUT_DIR / "17_feature_alpha_daily.csv"     # NEW primary source
ALPHA_FULL_FILE = OUTPUT_DIR / "17_feature_alpha_rank.csv"       # diagnostic only now
CORR_FILE = OUTPUT_DIR / "17_feature_correlation.csv"

SELECTION_FILE = OUTPUT_DIR / "18_strategy_selection.csv"
CONFIG_FILE = OUTPUT_DIR / "18_strategy_config.csv"
THRESHOLD_FILE = OUTPUT_DIR / "18_validation_thresholds.csv"
FAMILY_FILE = OUTPUT_DIR / "18_family_summary.csv"
FINALISTS_FILE = OUTPUT_DIR / "18_strategy_finalists.csv"
AVAILABILITY_FILE = OUTPUT_DIR / "18_feature_availability.csv"

REBALANCE = 1
HORIZON = 10
HORIZON_SECONDS = 600
EXECUTION_LAG = 1
COST_BPS = 7.5
MAX_EXPOSURE = 1.0

THRESHOLDS = [0.5, 0.75, 1.0, 1.25, 1.5]
VALIDATION_MIN_ACTIVE_FRACTION = 0.005 #0.01
VALIDATION_MIN_TRADES = 2 #5

TRAIN_DAYS = list(range(1, 44))
VALIDATION_DAYS = list(range(44, 55))
TEST_DAYS = list(range(55, 65)) + list(range(80, 86))

DISCOVERY_DAYS = TRAIN_DAYS + VALIDATION_DAYS
ALL_DAYS = DISCOVERY_DAYS + TEST_DAYS
EXPECTED_DAYS = list(range(1, 65)) + list(range(80, 86))

FINALISTS = 10
MIN_DISCOVERY_DAY_COVERAGE = 0.90   # a candidate needs stats on >=90% of discovery days to be trusted


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

print("\n--- FILE 18: STRATEGY DESIGN ---")
print("\nTrain days:", TRAIN_DAYS[0], "-", TRAIN_DAYS[-1], len(TRAIN_DAYS))
print("Validation days:", VALIDATION_DAYS[0], "-", VALIDATION_DAYS[-1], len(VALIDATION_DAYS))
print("Discovery days:", DISCOVERY_DAYS[0], "-", DISCOVERY_DAYS[-1], len(DISCOVERY_DAYS))
print("Test days:", TEST_DAYS, len(TEST_DAYS))

if not ALPHA_DAILY_FILE.exists():
    raise FileNotFoundError(
        f"{ALPHA_DAILY_FILE} not found. File 18 now requires the "
        "per-day granular alpha table from the patched File 17 "
        "(it writes 17_feature_alpha_daily.csv). Re-run File 17."
    )
if not CORR_FILE.exists():
    raise FileNotFoundError(CORR_FILE)
if not DATA_DIR.exists():
    raise FileNotFoundError(DATA_DIR)


daily_df = pd.read_csv(ALPHA_DAILY_FILE)
corr_df = pd.read_csv(CORR_FILE)

print("\nDaily alpha shape:", daily_df.shape)
print("Correlation shape:", corr_df.shape)


# ------------------------------------------------------------
# 5B — DISCOVERY-ONLY CANDIDATE STATISTICS
#
# This is the fix for the leakage bug. We take the raw per-day
# rows and aggregate ONLY over DISCOVERY_DAYS, ourselves, right
# here — instead of trusting a pre-aggregated file whose day
# scope we could not verify.
# ------------------------------------------------------------

daily_df.columns = [str(x).strip('*').strip() for x in daily_df.columns]

req = ['day', 'feature', 'family', 'horizon', 'pearson', 'spearman', 'mutual_information']
for col in req:
    if col not in daily_df.columns:
        raise ValueError(f"{col} missing from 17_feature_alpha_daily.csv")

for col in ['day', 'horizon', 'pearson', 'spearman', 'mutual_information', 'n']:
    if col in daily_df.columns:
        daily_df[col] = pd.to_numeric(daily_df[col], errors='coerce')

daily_df['feature'] = daily_df['feature'].astype(str).str.strip()
daily_df['family'] = daily_df['family'].astype(str).str.strip()

daily_df = daily_df.dropna(subset=['day', 'feature', 'family', 'horizon', 'pearson', 'spearman', 'mutual_information'])

disc = daily_df[
    (daily_df['horizon'] == HORIZON)
    & (daily_df['day'].isin(DISCOVERY_DAYS))
].copy()

if len(disc) == 0:
    raise ValueError(f"No discovery-day horizon-{HORIZON} rows found in {ALPHA_DAILY_FILE}")

print("\nDiscovery-day horizon-10 rows:", len(disc))
print("Unique features with >=1 discovery-day row:", disc['feature'].nunique())

cand = disc.groupby(['feature', 'family'], as_index=False).agg(
    pearson=('pearson', 'median'),
    spearman=('spearman', 'median'),
    mutual_information=('mutual_information', 'median'),
    n=('n', 'sum'),
    discovery_days=('day', 'nunique'),
)

if 'base' in daily_df.columns:
    base_map = daily_df[['feature', 'base']].drop_duplicates('feature').set_index('feature')['base']
    cand['base'] = cand['feature'].map(base_map)

if 'T' in daily_df.columns:
    t_map = daily_df[['feature', 'T']].drop_duplicates('feature').set_index('feature')['T']
    cand['T'] = cand['feature'].map(t_map)

cand['abs_pearson'] = cand['pearson'].abs()
cand['abs_spearman'] = cand['spearman'].abs()

cand['alpha_score'] = (
    0.40 * cand['abs_pearson']
    + 0.35 * cand['abs_spearman']
    + 0.25 * cand['mutual_information']
)

# True discovery-day coverage — not divided by the 70-day universe.
cand['coverage'] = (cand['discovery_days'] / len(DISCOVERY_DAYS)).clip(0, 1)

thin = cand[cand['coverage'] < MIN_DISCOVERY_DAY_COVERAGE]
if len(thin):
    print(
        f"\nWARNING: {len(thin)} candidates have discovery-day coverage "
        f"below {MIN_DISCOVERY_DAY_COVERAGE:.0%} (thin evidence). They stay "
        "in the pool but their coverage multiplier will penalize them."
    )

print("\nHorizon-10 candidates (discovery-only):", len(cand))


# ------------------------------------------------------------
# 5C — DIAGNOSTIC COMPARISON AGAINST THE OLD FULL-UNIVERSE STATS
#
# Not used for selection. Purely so you can see how much the
# previous (leaky) ranking would have differed from this one.
# ------------------------------------------------------------

if ALPHA_FULL_FILE.exists():

    full_df = pd.read_csv(ALPHA_FULL_FILE)
    full_df.columns = [str(x).strip('*').strip() for x in full_df.columns]

    if 'horizon' in full_df.columns and 'alpha_score' in full_df.columns:

        full_h = full_df[pd.to_numeric(full_df['horizon'], errors='coerce') == HORIZON].copy()
        full_h['feature'] = full_h['feature'].astype(str).str.strip()

        full_keep = full_h[['feature', 'alpha_score']].rename(
            columns={'alpha_score': 'full_universe_alpha_score'}
        )

        if 'days' in full_h.columns:
            full_keep['full_universe_days'] = full_h['days'].values

        cand = cand.merge(full_keep, on='feature', how='left')

        cand['alpha_score_drift'] = (
            cand['alpha_score'] - cand['full_universe_alpha_score']
        ).abs()

        drift = cand.sort_values('alpha_score_drift', ascending=False).head(5)
        print("\nLargest discovery-only vs full-universe alpha_score drift (diagnostic):")
        print(drift[['feature', 'alpha_score', 'full_universe_alpha_score', 'alpha_score_drift']].to_string(index=False))

    # Forensic hypothesis labels are feature-level, not return-statistics,
    # so pulling them from the full file carries no leakage risk.
    forensic_cols = [c for c in ['feature', 'best_candidate', 'confidence'] if c in full_df.columns]
    if len(forensic_cols) > 1:
        forensic = full_df[forensic_cols].drop_duplicates('feature')
        cand = cand.merge(forensic, on='feature', how='left')


# ------------------------------------------------------------
# 5D — RANK BY DISCOVERY-ONLY ALPHA SCORE
# ------------------------------------------------------------

# cand = cand.sort_values(['alpha_score', 'mutual_information'], ascending=[False, False]).reset_index(drop=True)
# cand['predictive_rank'] = np.arange(1, len(cand) + 1)

# print("\nTop Task-4 horizon-10 candidates (discovery-only):")
# cols = ['feature', 'family', 'alpha_score', 'spearman', 'mutual_information', 'discovery_days', 'coverage']
# cols = [c for c in cols if c in cand.columns]
# print(cand[cols].head(15).to_string(index=False))


# ------------------------------------------------------------
# 5E — REDUNDANCY
#
# Feature-vs-feature structural correlation. Computed across the
# full 70-day universe upstream in File 17 — that's fine, it does
# not touch the return target, so it carries no leakage risk.
# ------------------------------------------------------------

corr_df.columns = [str(x).strip('*').strip() for x in corr_df.columns]

if 'feature_1' not in corr_df.columns or 'feature_2' not in corr_df.columns:
    raise ValueError("Feature-pair columns missing from 17_feature_correlation.csv")

if 'abs_pearson' not in corr_df.columns:
    if 'pearson' in corr_df.columns:
        corr_df['abs_pearson'] = pd.to_numeric(corr_df['pearson'], errors='coerce').abs()
    else:
        raise ValueError("Correlation strength column missing")

corr_df['feature_1'] = corr_df['feature_1'].astype(str).str.strip()
corr_df['feature_2'] = corr_df['feature_2'].astype(str).str.strip()
corr_df['abs_pearson'] = pd.to_numeric(corr_df['abs_pearson'], errors='coerce')
corr_df = corr_df.dropna(subset=['feature_1', 'feature_2', 'abs_pearson'])

candidate_features = set(cand['feature'])
corr_df = corr_df[
    corr_df['feature_1'].isin(candidate_features) & corr_df['feature_2'].isin(candidate_features)
].copy()
corr_df = corr_df[corr_df['feature_1'] != corr_df['feature_2']].copy()

red = {}
for f in cand['feature'].unique():
    q = corr_df[(corr_df['feature_1'] == f) | (corr_df['feature_2'] == f)]
    red[f] = q['abs_pearson'].max() if len(q) else np.nan

cand['max_redundancy'] = cand['feature'].map(red)

print("\nCandidate-pool correlation pairs:", len(corr_df))


# ------------------------------------------------------------
# 5F — FORENSIC EVIDENCE + SELECTION SCORE
#
# Redundancy penalty is now continuous: no penalty up to 0.80
# correlation, ramping linearly down to a 0.65x multiplier at
# 1.00 correlation. Fixes the 0.9499 vs 0.9501 cliff from the
# previous version.
# ------------------------------------------------------------

cand['forensic_ok'] = True
if 'best_candidate' in cand.columns:
    cand['forensic_ok'] = cand['best_candidate'].notna() & cand['best_candidate'].astype(str).str.strip().ne('')

redundancy_multiplier = np.where(
    cand['max_redundancy'].isna(),
    1.0,
    np.where(
        cand['max_redundancy'] <= 0.80,
        1.0,
        1.0 - 0.35 * (cand['max_redundancy'] - 0.80) / 0.20,
    ),
)

cand['selection_score'] = (
    cand['alpha_score']
    * cand['coverage']
    * redundancy_multiplier
    * np.where(cand['forensic_ok'], 1.0, 0.90)
)

cand = cand.sort_values(
    ['selection_score', 'alpha_score', 'mutual_information', 'coverage'],
    ascending=[False, False, False, False],
).reset_index(drop=True)
cand['selection_rank'] = np.arange(1, len(cand) + 1)

print("\n--- CANDIDATE SELECTION (discovery-only, leakage-free) ---")
cols = [
    'selection_rank', 'feature', 'family', 'alpha_score', 'mutual_information',
    'spearman', 'max_redundancy', 'coverage', 'forensic_ok', 'selection_score',
]
cols = [c for c in cols if c in cand.columns]
print(cand[cols].head(20).to_string(index=False))

# ------------------------------------------------------------
# 5F — INPUT FILE / FEATURE AVAILABILITY
# ------------------------------------------------------------

csv_files = sorted(
    DATA_DIR.glob("*.csv"),
    key=lambda x: (
        get_day_number(x) is None,
        get_day_number(x) if get_day_number(x) is not None else 10**9
    ),
)

files = {
    get_day_number(f): f
    for f in csv_files
    if get_day_number(f) is not None
}

missing_days = [d for d in ALL_DAYS if d not in files]

if missing_days:
    raise ValueError(f"Missing strategy input files for days: {missing_days}")

comp_files = [files[d] for d in ALL_DAYS]

print("\nFiles available for strategy:", len(comp_files))

headers = {
    d: set(pd.read_csv(files[d], nrows=0).columns)
    for d in ALL_DAYS
}

# ------------------------------------------------------------
# AVAILABILITY ELIGIBILITY
# ------------------------------------------------------------

av = []

for d in DISCOVERY_DAYS:
    h = headers[d]

    for feat in cand['feature'].unique():
        av.append({
            'day': d,
            'feature': feat,
            'available': feat in h,
            'split': (
                'train'
                if d in TRAIN_DAYS
                else 'validation'
            ),
        })

av_df = pd.DataFrame(av)

av_sum = (
    av_df
    .groupby(['feature', 'split'])
    .agg(
        days_available=('available', 'sum'),
        days_checked=('day', 'nunique')
    )
    .reset_index()
)

av_sum['coverage'] = (
    av_sum['days_available'] /
    av_sum['days_checked']
)

print("\nDiscovery availability:")
print(
    av_sum
    .sort_values(['feature', 'split'])
    .to_string(index=False)
)

av_full = (
    av_df
    .groupby('feature')
    .agg(
        days_available=('available', 'sum'),
        days_checked=('day', 'nunique')
    )
    .reset_index()
)

av_full['discovery_file_coverage'] = (
    av_full['days_available'] /
    av_full['days_checked']
)

av_full.to_csv(AVAILABILITY_FILE, index=False)

cand = cand.merge(
    av_full[
        [
            'feature',
            'days_available',
            'days_checked',
            'discovery_file_coverage'
        ]
    ],
    on='feature',
    how='left'
)

cand['discovery_file_coverage'] = (
    cand['discovery_file_coverage']
    .fillna(0)
)

# Candidate must exist on every discovery day.
cand = cand[
    cand['discovery_file_coverage'] == 1.0
].copy()

if len(cand) == 0:
    raise ValueError(
        "No candidates are available across all "
        "54 train/validation discovery days"
    )

print(
    "\nCandidates after discovery availability eligibility:",
    len(cand)
)

# ------------------------------------------------------------
# 5G — STATISTICAL ELIGIBILITY + RANK
# ------------------------------------------------------------

# Candidate must also have sufficient statistical coverage.
cand = cand[
    cand['coverage'] >= MIN_DISCOVERY_DAY_COVERAGE
].copy()

if len(cand) == 0:
    raise ValueError(
        "No candidates remain after statistical eligibility filtering"
    )

cand = cand.sort_values(
    [
        'selection_score',
        'alpha_score',
        'mutual_information',
        'coverage'
    ],
    ascending=[False, False, False, False]
).reset_index(drop=True)

cand['predictive_rank'] = np.arange(1, len(cand) + 1)
cand['selection_rank'] = np.arange(1, len(cand) + 1)

print(
    "\nCandidates after statistical eligibility:",
    len(cand)
)

print("\n--- FINAL DISCOVERY-ELIGIBLE RANKING ---")

cols = [
    'selection_rank',
    'feature',
    'family',
    'alpha_score',
    'mutual_information',
    'spearman',
    'max_redundancy',
    'coverage',
    'discovery_file_coverage',
    'forensic_ok',
    'selection_score',
]

cols = [c for c in cols if c in cand.columns]

print(
    cand[cols]
    .head(20)
    .to_string(index=False)
)

if len(cand) < FINALISTS:
    raise ValueError(
        f"Only {len(cand)} candidates remain after "
        f"availability/statistical eligibility; "
        f"{FINALISTS} finalists required"
    )

fcols = cand['feature'].head(FINALISTS).tolist()

print("\nFinalists:", fcols)

# Test availability is checked only AFTER the finalists are selected.
for feat in fcols:
    test_missing = [
        d for d in TEST_DAYS
        if feat not in headers[d]
    ]

    if test_missing:
        raise ValueError(
            f"Finalist {feat} is unavailable on test days "
            f"{test_missing}"
        )

# ------------------------------------------------------------
# GUARD: fail loudly instead of silently truncating below
# FINALISTS candidates (fix for the previous unguarded .head()).
# ------------------------------------------------------------

if len(cand) < FINALISTS:
    raise ValueError(
        f"Only {len(cand)} strategy candidates available after discovery "
        f"filtering, expected at least {FINALISTS}"
    )

fcols = cand['feature'].head(FINALISTS).tolist()

av = []
for d in ALL_DAYS:
    h = headers[d]
    for feat in fcols:
        av.append({
            'day': d,
            'feature': feat,
            'available': feat in h,
            'split': 'train' if d in TRAIN_DAYS else 'validation' if d in VALIDATION_DAYS else 'test',
        })

av_df = pd.DataFrame(av)

av_sum = av_df.groupby(['feature', 'split']).agg(
    days_available=('available', 'sum'), days_checked=('day', 'nunique')
).reset_index()
av_sum['coverage'] = av_sum['days_available'] / av_sum['days_checked']

print("\nFinalist availability:")
print(av_sum.sort_values(['feature', 'split']).to_string(index=False))

av_full = av_df.groupby('feature').agg(
    days_available=('available', 'sum'), days_checked=('day', 'nunique')
).reset_index()
av_full['file_coverage'] = av_full['days_available'] / av_full['days_checked']
av_full.to_csv(AVAILABILITY_FILE, index=False)

cand = cand.merge(
    av_full[['feature', 'days_available', 'days_checked', 'file_coverage']], on='feature', how='left'
)
cand['file_coverage'] = cand['file_coverage'].fillna(0)

disc_av = (
    av_df[av_df['day'].isin(DISCOVERY_DAYS)]
    .groupby('feature')
    .agg(
        discovery_days_available=('available', 'sum'),
        discovery_days_checked=('day', 'nunique')
    )
    .reset_index()
)

disc_av['discovery_file_coverage'] = (
    disc_av['discovery_days_available']
    / disc_av['discovery_days_checked']
)

# Remove any stale column before merging.
cand = cand.drop(
    columns=[
        'discovery_days_available',
        'discovery_days_checked',
        'discovery_file_coverage'
    ],
    errors='ignore'
)

cand = cand.merge(
    disc_av[
        [
            'feature',
            'discovery_days_available',
            'discovery_days_checked',
            'discovery_file_coverage'
        ]
    ],
    on='feature',
    how='left'
)

cand['discovery_file_coverage'] = (
    cand['discovery_file_coverage'].fillna(0)
)

# A strategy candidate must be implementable throughout train + validation.
cand = cand[cand['discovery_file_coverage'] == 1.0].copy()

if len(cand) == 0:
    raise ValueError("No Task-4 candidates are available across all 54 train/validation discovery days")

cand = cand.sort_values(
    ['selection_score', 'alpha_score', 'mutual_information', 'coverage'],
    ascending=[False, False, False, False],
).reset_index(drop=True)
cand['selection_rank'] = np.arange(1, len(cand) + 1)


# ------------------------------------------------------------
# 5H — SELECT FEATURE
# ------------------------------------------------------------

top = cand.iloc[0]
FEATURE = str(top['feature'])
FAMILY = str(top['family'])

BEST_CANDIDATE = str(top['best_candidate']) if 'best_candidate' in top.index and not pd.isna(top['best_candidate']) else ""

SPEARMAN = (
    float(top['spearman'])
    if 'spearman' in top.index and not pd.isna(top['spearman'])
    else 0.0
)

PEARSON = (
    float(top['pearson'])
    if 'pearson' in top.index and not pd.isna(top['pearson'])
    else 0.0
)

# Direction is determined from TRAIN evidence only.
train_alpha = daily_df[
    (daily_df['feature'] == FEATURE)
    & (daily_df['family'] == FAMILY)
    & (daily_df['horizon'] == HORIZON)
    & (daily_df['day'].isin(TRAIN_DAYS))
].copy()

if len(train_alpha) == 0:
    raise ValueError(
        f"No TRAIN alpha evidence found for selected feature {FEATURE}"
    )

TRAIN_SPEARMAN = train_alpha['spearman'].median()
TRAIN_PEARSON = train_alpha['pearson'].median()

if pd.notna(TRAIN_SPEARMAN) and TRAIN_SPEARMAN != 0:
    SIGNAL_SIGN = 1 if TRAIN_SPEARMAN > 0 else -1
elif pd.notna(TRAIN_PEARSON) and TRAIN_PEARSON != 0:
    SIGNAL_SIGN = 1 if TRAIN_PEARSON > 0 else -1
else:
    raise ValueError(
        f"Cannot determine signal direction from TRAIN evidence for {FEATURE}"
    )

print("\nSelected Task-4 feature:", FEATURE)
print("Selected family:", FAMILY)
print("Forensic hypothesis:", BEST_CANDIDATE)
print("Signal direction (TRAIN evidence):", SIGNAL_SIGN)
# print(
#     "NOTE: sign is only mechanically consistent with discovery-day "
#     "Spearman. File 19 must still verify it matches the intended "
#     "target orientation (see CONFIG['signal_direction_verification_required'])."
# )

# test_missing = [d for d in TEST_DAYS if FEATURE not in headers[d]]
# if test_missing:
#     raise ValueError(f"Selected feature {FEATURE} is unavailable on test days {test_missing}")


# ------------------------------------------------------------
# 5I — SELECTION OUTPUT
# ------------------------------------------------------------

sel_cols = [
    'selection_rank', 'feature', 'family', 'base', 'T', 'pearson', 'spearman',
    'mutual_information', 'n', 'abs_pearson', 'abs_spearman', 'alpha_score',
    'best_candidate', 'confidence', 'discovery_days', 'predictive_rank',
    'coverage', 'max_redundancy', 'forensic_ok', 'discovery_days_available',
    'discovery_days_checked', 'discovery_file_coverage', 'days_available',
    'days_checked', 'file_coverage', 'selection_score',
    'full_universe_alpha_score', 'full_universe_days', 'alpha_score_drift',
]
sel_cols = [c for c in sel_cols if c in cand.columns]

cand[sel_cols].head(max(FINALISTS, 20)).to_csv(SELECTION_FILE, index=False)
cand.head(FINALISTS).to_csv(FINALISTS_FILE, index=False)


# ------------------------------------------------------------
# 5J — TRAIN-ONLY NORMALIZATION
# ------------------------------------------------------------

train_vals = []
for d in TRAIN_DAYS:
    f = files.get(d)
    if f is None:
        raise ValueError(f"Missing training file for day {d}")
    if FEATURE not in headers[d]:
        raise ValueError(f"{FEATURE} missing from training day {d}")

    df = pd.read_csv(f, usecols=[FEATURE])
    x = pd.to_numeric(df[FEATURE], errors='coerce').replace([np.inf, -np.inf], np.nan).dropna()
    if len(x):
        train_vals.append(x)

if not train_vals:
    raise ValueError("No training feature data found for selected feature")

train_x = pd.concat(train_vals, ignore_index=True)
TRAIN_MEAN = train_x.mean()
TRAIN_STD = train_x.std(ddof=0)

if not np.isfinite(TRAIN_MEAN):
    raise ValueError("Invalid training mean")
if not np.isfinite(TRAIN_STD) or TRAIN_STD <= 0:
    raise ValueError("Invalid training standard deviation")

print("\nTraining normalization:")
print("Mean:", TRAIN_MEAN)
print("Std :", TRAIN_STD)


# ------------------------------------------------------------
# 5K — VALIDATION THRESHOLD SELECTION
# ------------------------------------------------------------
def build_minute_series(file_path, feature):
    df = pd.read_csv(
        file_path,
        usecols=['Time', 'Price', feature]
    )

    # --------------------------------------------------------
    # TIME PARSING
    # --------------------------------------------------------
    time_raw = df['Time']

    time_numeric = pd.to_numeric(
        time_raw,
        errors='coerce'
    )

    time_text = time_raw.astype(str).str.strip()

    time_parsed = pd.to_timedelta(
        time_text,
        errors='coerce'
    ).dt.total_seconds()

    df['Time'] = time_numeric.where(
        time_numeric.notna(),
        time_parsed
    )

    # --------------------------------------------------------
    # PRICE / FEATURE
    # --------------------------------------------------------
    df['Price'] = pd.to_numeric(
        df['Price'],
        errors='coerce'
    )

    df[feature] = pd.to_numeric(
        df[feature],
        errors='coerce'
    )

    print(
        f"    Time usable: "
        f"{df['Time'].notna().sum()}/{len(df)}"
    )

    print(
        f"    Price usable: "
        f"{df['Price'].notna().sum()}/{len(df)}"
    )

    print(
        f"    {feature} usable: "
        f"{df[feature].notna().sum()}/{len(df)}"
    )

    df = df.dropna(
        subset=['Time', 'Price', feature]
    ).copy()

    if len(df) == 0:
        return pd.DataFrame(
            columns=[
                'Time',
                'Price',
                feature,
                'z',
                'ret_1m'
            ]
        )

    df = df.sort_values('Time')

    # One observation per minute.
    df['minute'] = (
        df['Time'] // 60
    ).astype(int)

    minute = (
        df.groupby('minute', as_index=False)
        .agg({
            'Time': 'last',
            'Price': 'last',
            feature: 'last'
        })
    )

    # TRAIN-ONLY normalization.
    minute['z'] = (
        (minute[feature] - TRAIN_MEAN) /
        TRAIN_STD
    )

    # 1-minute realized return.
    minute['ret_1m'] = (
        np.log(
            minute['Price'] /
            minute['Price'].shift(1)
        )
    )

    return minute


validation_rows = []

for d in VALIDATION_DAYS:

    f = files[d]

    minute = build_minute_series(
        f,
        FEATURE
    )

    # --------------------------------------------------------
    # Every validation day MUST be represented.
    #
    # A day with no usable data is economically treated as
    # zero-return / zero-trade for every threshold.
    # --------------------------------------------------------
    if minute.empty:

        print(
            f"\nVALIDATION DAY {d}: "
            f"NO USABLE MINUTE DATA -> "
            f"all thresholds recorded as zero."
        )

        for threshold in THRESHOLDS:

            validation_rows.append({
                'day': d,
                'threshold': threshold,
                'gross_return': 0.0,
                'net_return': 0.0,
                'active_fraction': 0.0,
                'trade_count': 0,
                'turnover': 0.0,
                'eligible_under_old_rule': False,
            })

        continue

    valid = minute['ret_1m'].notna()

    print(
        f"\nValidation day {d}: "
        f"raw minute rows={len(minute)}, "
        f"valid return rows={int(valid.sum())}, "
        f"z min={minute['z'].min():.4f}, "
        f"z max={minute['z'].max():.4f}, "
        f"z mean={minute['z'].mean():.4f}"
    )

    # No valid returns: still record this day for every threshold.
    if valid.sum() == 0:

        print(
            f"  -> NO VALID RETURNS -> "
            f"all thresholds recorded as zero."
        )

        for threshold in THRESHOLDS:

            validation_rows.append({
                'day': d,
                'threshold': threshold,
                'gross_return': 0.0,
                'net_return': 0.0,
                'active_fraction': 0.0,
                'trade_count': 0,
                'turnover': 0.0,
                'eligible_under_old_rule': False,
            })

        continue

    signal = SIGNAL_SIGN * minute['z']

    for threshold in THRESHOLDS:

        position = pd.Series(
            np.where(
                signal > threshold,
                MAX_EXPOSURE,
                np.where(
                    signal < -threshold,
                    -MAX_EXPOSURE,
                    0.0
                )
            ),
            index=minute.index
        )

        # signal_t -> execution at t+1
        executed = position.shift(
            EXECUTION_LAG,
            fill_value=0.0
        )

        # Position change = transaction turnover.
        turnover = (
            executed -
            executed.shift(1).fillna(0.0)
        ).abs()

        gross_ret = (
            executed *
            minute['ret_1m']
        )

        cost_decimal = COST_BPS / 10000.0

        net_ret = (
            gross_ret -
            turnover * cost_decimal
        )

        active_fraction = (
            executed[valid].abs() > 0
        ).mean()

        trade_count = (
            turnover[valid] > 0
        ).sum()

        gross_return = gross_ret[valid].sum()
        net_return = net_ret[valid].sum()
        total_turnover = turnover[valid].sum()

        # ----------------------------------------------------
        # OLD eligibility rule is retained ONLY as a diagnostic.
        #
        # It NO LONGER removes the day from threshold selection.
        # ----------------------------------------------------
        eligible_old_rule = (
            active_fraction >=
            VALIDATION_MIN_ACTIVE_FRACTION
            and
            trade_count >=
            VALIDATION_MIN_TRADES
        )

        if not eligible_old_rule:
            print(
                f"  threshold={threshold}: "
                f"LOW-EVIDENCE DAY "
                f"active_fraction={active_fraction:.6f}, "
                f"trades={int(trade_count)}, "
                f"net_return={net_return:.8f}"
            )
        else:
            print(
                f"  threshold={threshold}: "
                f"ACCEPT "
                f"active_fraction={active_fraction:.6f}, "
                f"trades={int(trade_count)}, "
                f"net_return={net_return:.8f}"
            )

        # ----------------------------------------------------
        # CRITICAL:
        # ALWAYS append the day.
        #
        # No threshold/day combination is discarded.
        # Zero-trade days therefore contribute exactly 0 return.
        # ----------------------------------------------------
        validation_rows.append({
            'day': d,
            'threshold': threshold,
            'gross_return': gross_return,
            'net_return': net_return,
            'active_fraction': active_fraction,
            'trade_count': int(trade_count),
            'turnover': total_turnover,
            'eligible_under_old_rule': eligible_old_rule,
        })


validation_df = pd.DataFrame(
    validation_rows
)

if validation_df.empty:
    raise ValueError(
        "No validation results were produced."
    )

# ------------------------------------------------------------
# HARD CHECK:
# Every threshold must have exactly one result for every
# validation day.
# ------------------------------------------------------------
expected_validation_rows = (
    len(VALIDATION_DAYS) *
    len(THRESHOLDS)
)

if len(validation_df) != expected_validation_rows:
    raise ValueError(
        f"Validation grid incomplete: "
        f"got {len(validation_df)} rows, "
        f"expected {expected_validation_rows} "
        f"({len(VALIDATION_DAYS)} days x "
        f"{len(THRESHOLDS)} thresholds)."
    )

coverage_check = (
    validation_df
    .groupby('threshold')['day']
    .nunique()
)

if not (coverage_check == len(VALIDATION_DAYS)).all():
    raise ValueError(
        "At least one threshold does not have "
        "a result for every validation day."
    )

# ------------------------------------------------------------
# FULL VALIDATION-DAY THRESHOLD SUMMARY
# ------------------------------------------------------------
validation_summary = (
    validation_df
    .groupby('threshold', as_index=False)
    .agg(
        mean_net_return=('net_return', 'mean'),
        median_net_return=('net_return', 'median'),
        total_net_return=('net_return', 'sum'),

        mean_gross_return=('gross_return', 'mean'),

        mean_active_fraction=('active_fraction', 'mean'),

        total_trade_count=('trade_count', 'sum'),
        total_turnover=('turnover', 'sum'),

        days_evaluated=('day', 'nunique'),

        days_with_trades=(
            'trade_count',
            lambda x: (x > 0).sum()
        ),

        zero_trade_days=(
            'trade_count',
            lambda x: (x == 0).sum()
        ),

        days_passing_old_rule=(
            'eligible_under_old_rule',
            'sum'
        ),
    )
)

# ------------------------------------------------------------
# FINAL THRESHOLD RANKING
#
# Primary criterion:
#   mean NET return over ALL 11 validation days.
#
# Secondary:
#   median NET return over ALL 11 validation days.
#
# Tertiary:
#   mean active fraction.
# ------------------------------------------------------------
validation_summary = validation_summary.sort_values(
    [
        'mean_net_return',
        'median_net_return',
        'mean_active_fraction'
    ],
    ascending=[False, False, False]
).reset_index(drop=True)

if len(validation_summary) == 0:
    raise ValueError(
        "No threshold results available."
    )

# ------------------------------------------------------------
# HARD CHECK:
# Threshold selection must use all 11 validation days.
# ------------------------------------------------------------
if not (
    validation_summary['days_evaluated']
    == len(VALIDATION_DAYS)
).all():
    raise ValueError(
        "Threshold selection is not using the full "
        "validation-day universe."
    )

SELECTED_THRESHOLD = float(
    validation_summary.iloc[0]['threshold']
)

print("\n--- VALIDATION THRESHOLD SELECTION ---")

print(
    validation_summary.to_string(index=False)
)

print(
    "\nSelected validation threshold:",
    SELECTED_THRESHOLD
)

print(
    "\nThreshold selection uses ALL",
    len(VALIDATION_DAYS),
    "validation days."
)

validation_summary.to_csv(
    THRESHOLD_FILE,
    index=False
)

# ------------------------------------------------------------
# 5L — STRATEGY CONFIGURATION
# ------------------------------------------------------------

CONFIG = {
    'feature': FEATURE,
    'family': FAMILY,
    'forensic_hypothesis': BEST_CANDIDATE,
    'rebalance_minutes': REBALANCE,
    'feature_horizon': HORIZON,
    'horizon_semantics': 'PREDICTIVE_TARGET_HORIZON_NOT_HOLDING_PERIOD',
    'execution_lag_minutes': EXECUTION_LAG,
    'signal': 'signal_t = signal_direction * z_t',
    'z_score': 'z_t = (feature_t - train_mean) / train_std',
    'signal_direction': SIGNAL_SIGN,
    'direction_source': 'TRAIN_ONLY_ALPHA_EVIDENCE',
    'signal_direction_verification_required': True,
    'normalization': 'TRAIN_ONLY_MEAN_STD',
    'train_mean': TRAIN_MEAN,
    'train_std': TRAIN_STD,
    'threshold_grid': ','.join(map(str, THRESHOLDS)),
    'selected_threshold': SELECTED_THRESHOLD,
    'position_rule': 'LONG=+1 if signal>selected_threshold; FLAT=0 if abs(signal)<=selected_threshold; SHORT=-1 if signal<-selected_threshold',
    'max_exposure': MAX_EXPOSURE,
    'transaction_cost_bps': COST_BPS,
    'cost_bps_to_decimal': 'cost_decimal = transaction_cost_bps / 10000  (do NOT subtract raw bps from returns)',
    'turnover_model': 'absolute_position_change',
    'cost_application': 'net_ret_t = gross_ret_t - abs(position_t - position_t_minus_1) * (transaction_cost_bps / 10000)',
    'day_boundary_rule': 'RESET_POSITION_TO_ZERO_AT_START_OF_EACH_DAY (no overnight carry, one file per day)',
    'train_start': TRAIN_DAYS[0],
    'train_end': TRAIN_DAYS[-1],
    'validation_start': VALIDATION_DAYS[0],
    'validation_end': VALIDATION_DAYS[-1],
    'test_days': ','.join(map(str, TEST_DAYS)),
    'lookahead_rule': 'feature_t -> signal_t -> execute_t+1',
    'candidate_selection_source': '17_feature_alpha_daily (re-aggregated in File 18)',
    'candidate_selection_scope': 'DISCOVERY_ONLY_54_DAYS',
    'discovery_days': ','.join(map(str, DISCOVERY_DAYS)),
    'parameter_selection_rule': 'TRAIN_FEATURE_DIRECTION_NORMALIZATION_VALIDATION_THRESHOLD_LOCK_TEST',
    'test_usage': 'NO_FEATURE_OR_THRESHOLD_SELECTION',
    'threshold_selection': (
        'VALIDATION_ONLY_FULL_11_DAY_GRID; '
        'EVERY_THRESHOLD_EVALUATED_ON_EVERY_VALIDATION_DAY; '
        'ZERO_RETURN_ON_ZERO_TRADE_DAY; '
        'PRIMARY_CRITERION_MEAN_NET_RETURN'
    ),
    'selected_threshold': SELECTED_THRESHOLD,
    'final_test_rule': 'LOCK_FEATURE_AND_THRESHOLD_BEFORE_TEST',
    'position_continuity': '1_MINUTE_REBALANCE',
    'test_availability': 'VALIDATE_ONLY_NOT_SELECTION_CRITERION',
    'diagnostics_required': (
        'long_fraction,short_fraction,flat_fraction,active_fraction,'
        'mean_abs_position,trade_count,turnover,gross_return,net_return,'
        'days_evaluated,days_with_trades,zero_trade_days'
    ),
}

config_df = pd.DataFrame([{'parameter': k, 'value': v} for k, v in CONFIG.items()])
config_df.to_csv(CONFIG_FILE, index=False)


# ------------------------------------------------------------
# 5M — FAMILY SUMMARY
# ------------------------------------------------------------

family_summary = (
    cand.groupby('family')
    .agg(
        candidates=('feature', 'count'),
        best_selection_score=('selection_score', 'max'),
        best_alpha=('alpha_score', 'max'),
        mean_alpha=('alpha_score', 'mean'),
        mean_coverage=('coverage', 'mean'),
        mean_discovery_file_coverage=('discovery_file_coverage', 'mean'),
    )
    .sort_values('best_selection_score', ascending=False)
    .reset_index()
)
family_summary.to_csv(FAMILY_FILE, index=False)


# ------------------------------------------------------------
# 5N — FINAL REPORT
# ------------------------------------------------------------

print("\n--- STRATEGY SPECIFICATION ---")
print("FEATURE       :", FEATURE)
print("FAMILY        :", FAMILY)
print("HYPOTHESIS    :", BEST_CANDIDATE)
print("REBALANCE     :", f"{REBALANCE} minute")
print("HORIZON       :", f"{HORIZON} predictive minutes")
print("EXECUTION     :", f"signal_t -> execute_t+{EXECUTION_LAG}")
print("DIRECTION     :", "LONG" if SIGNAL_SIGN == 1 else "SHORT")
print("NORMALIZATION : TRAIN ONLY")
print("TRAIN MEAN    :", TRAIN_MEAN)
print("TRAIN STD     :", TRAIN_STD)
print("SELECTED THRESHOLD :", SELECTED_THRESHOLD)
_selected_row = validation_summary[
    validation_summary['threshold'] == SELECTED_THRESHOLD
].iloc[0]

print(
    "SELECTED THRESHOLD VALIDATION DAYS :",
    int(_selected_row['days_evaluated'])
)

print(
    "SELECTED THRESHOLD DAYS WITH TRADES :",
    int(_selected_row['days_with_trades'])
)

print(
    "SELECTED THRESHOLD ZERO-TRADE DAYS :",
    int(_selected_row['zero_trade_days'])
)

print(
    "SELECTED THRESHOLD DAYS PASSING OLD RULE :",
    int(_selected_row['days_passing_old_rule'])
)

print(
    "SELECTED THRESHOLD TOTAL NET RETURN :",
    float(_selected_row['total_net_return'])
)

print(
    "SELECTED THRESHOLD MEAN DAILY NET RETURN :",
    float(_selected_row['mean_net_return'])
)

print(
    "SELECTED THRESHOLD MEDIAN DAILY NET RETURN :",
    float(_selected_row['median_net_return'])
)
print("POSITION      : LONG=+1, FLAT=0, SHORT=-1")
print("MAX EXPOSURE  :", MAX_EXPOSURE)
print("COST          :", COST_BPS, "bps")

print("\nTrain       :", TRAIN_DAYS[0], "-", TRAIN_DAYS[-1])
print("Validation  :", VALIDATION_DAYS[0], "-", VALIDATION_DAYS[-1])
print("Test        :", TEST_DAYS)

print("\nDiscovery feature coverage (share of 54 discovery days with stats):", top['coverage'])
print("Discovery file coverage (share of 54 discovery days feature is present in raw data):", top['discovery_file_coverage'])
print("Full file coverage (share of all 70 days feature is present in raw data):", top['file_coverage'])
if 'full_universe_alpha_score' in top.index:
    print("Full-universe alpha_score (diagnostic only, NOT used for selection):", top['full_universe_alpha_score'])

print("\n--- FILES WRITTEN ---")
print(SELECTION_FILE)
print(FINALISTS_FILE)
print(FAMILY_FILE)
print(THRESHOLD_FILE)
print(AVAILABILITY_FILE)

print("\n--- TEST LOCK ---")
print(
    "Test days are NOT used for candidate ranking."
)

print(
    "Test days are NOT used for feature selection."
)

print(
    "Test days are NOT used for direction selection."
)

print(
    "Test days are NOT used for normalization."
)

print(
    "Test days are NOT used for threshold selection."
)

print(
    "Test availability is checked only after finalist selection."
)

print(
    "HORIZON is NOT treated as a holding period."
)

print(
    "Feature, direction, normalization and threshold "
    "are frozen before TEST."
)

print(
    "File 19 must use the locked strategy configuration "
    "without redesigning the strategy."
)

print(
    "File 19 must apply cost_bps_to_decimal and "
    "day_boundary_rule exactly as specified in "
    "18_strategy_config.csv."
)
print("\nDone.")