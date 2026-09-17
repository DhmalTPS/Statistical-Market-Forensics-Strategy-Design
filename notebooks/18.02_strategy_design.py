
'The baseline strategy trades VB5_T12, a VB-family feature selected from the Task 4 horizon-10 predictive candidates after accounting for feature redundancy and availability. The feature is standardized using mean and standard deviation estimated exclusively from the 43 training days. The strategy is evaluated at a 1-minute rebalance frequency, with candidate thresholds of 0.5–1.5 standard deviations; a standardized feature above the threshold generates a long position, below the negative threshold generates a short position, and otherwise the strategy remains flat. Positions are capped at 1× exposure, transaction costs are assumed to be 7.5 bps, and execution must occur at t+1 after the signal is formed at t. Days 1–43 are training, 44–54 validation, and 55–64 plus 80–85 are the untouched test set.'

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
FAMILY_FILE = OUTPUT_DIR / '18_family_summary.csv'
FINALISTS_FILE = OUTPUT_DIR / "18_strategy_finalists.csv"

REBALANCE = 1
HORIZON = 10
COST_BPS = 7.5
MAX_EXPOSURE = 1.0
FINALISTS = 10

THRESHOLDS = [0.5,0.75,1.0,1.25,1.5]

TRAIN_DAYS = list(range(1,44))
VALIDATION_DAYS = list(range(44,55))
TEST_DAYS = list(range(55,65)) + list(range(80,86))

ALL_DAYS = TRAIN_DAYS + VALIDATION_DAYS + TEST_DAYS
EXPECTED_DAYS = list(range(1,65)) + list(range(80,86))

if len(ALL_DAYS) != 70:
    raise ValueError("Strategy day universe is not 70 days")

if len(set(ALL_DAYS)) != 70:
    raise ValueError("Duplicate days in strategy split")

if set(ALL_DAYS) != set(EXPECTED_DAYS):
    raise ValueError("Strategy split does not match usable-day universe")

if set(TRAIN_DAYS) & set(VALIDATION_DAYS) or set(TRAIN_DAYS) & set(TEST_DAYS) or set(VALIDATION_DAYS) & set(TEST_DAYS):
    raise ValueError("Train/validation/test days overlap")

print("\n--- TASK 5 STRATEGY DESIGN ---")

print("\nTrain days:",TRAIN_DAYS[0],"-",TRAIN_DAYS[-1],len(TRAIN_DAYS))
print("Validation days:",VALIDATION_DAYS[0],"-",VALIDATION_DAYS[-1],len(VALIDATION_DAYS))
print("Test days:",TEST_DAYS,len(TEST_DAYS))

alpha_df = pd.read_csv(ALPHA_FILE)
corr_df = pd.read_csv(CORR_FILE)

print("\nAlpha shape:",alpha_df.shape)
print("Correlation shape:",corr_df.shape)

if 'day' in alpha_df.columns:
    alpha_df['day'] = alpha_df['day'].apply(normalize_day).astype('Int64')
    alpha_df = alpha_df.dropna(subset=['day'])
    alpha_df['day'] = alpha_df['day'].astype(int)

if 'days' in alpha_df.columns:
    alpha_df['days'] = pd.to_numeric(alpha_df['days'],errors='coerce')

req = [
    'feature','family','horizon','alpha_score',
    'spearman','mutual_information'
]

for col in req:
    if col not in alpha_df.columns:
        raise ValueError(f"{col} missing from 17_feature_alpha_rank.csv")

for col in ['horizon','alpha_score','mutual_information','spearman','days']:
    if col in alpha_df.columns:
        alpha_df[col] = pd.to_numeric(alpha_df[col],errors='coerce')

alpha_df = alpha_df.dropna(
    subset=['feature','family','horizon','alpha_score']
)

print("\nHorizon counts:")
print(alpha_df['horizon'].value_counts().sort_index())

cand = alpha_df[alpha_df['horizon']==HORIZON].copy()

if len(cand)==0:
    raise ValueError(f"No Task 4 candidates found for horizon {HORIZON}")

cand = cand.sort_values(
    ['alpha_score','mutual_information'],
    ascending=[False,False]
).reset_index(drop=True)

cand['predictive_rank'] = np.arange(1,len(cand)+1)

print("\nTop predictive candidates:")
print(
    cand[
        ['feature','family','horizon','pearson','spearman',
         'mutual_information','alpha_score','best_candidate',
         'confidence','days']
    ].head(15).to_string(index=False)
)

corr_df.columns = [str(x).strip('*') for x in corr_df.columns]

if 'feature_1' not in corr_df.columns or 'feature_2' not in corr_df.columns:
    raise ValueError("Feature-pair columns missing from 17_feature_correlation.csv")

if 'abs_pearson' not in corr_df.columns:
    if 'pearson' in corr_df.columns:
        corr_df['abs_pearson'] = pd.to_numeric(
            corr_df['pearson'],errors='coerce'
        ).abs()
    else:
        raise ValueError("Correlation strength column missing")

corr_df['abs_pearson'] = pd.to_numeric(
    corr_df['abs_pearson'],errors='coerce'
)

corr_df = corr_df.dropna(
    subset=['feature_1','feature_2','abs_pearson']
)

red = {}

for f in cand['feature'].unique():

    q = corr_df[
        ((corr_df['feature_1']==f) |
         (corr_df['feature_2']==f))
        &
        (corr_df['abs_pearson']<0.999999999)
    ]

    red[f] = q['abs_pearson'].max() if len(q) else np.nan

cand['max_redundancy'] = cand['feature'].map(red)

cand['coverage'] = (
    cand['days'].fillna(0)/len(ALL_DAYS)
    if 'days' in cand.columns
    else 0.0
)

cand['forensic_ok'] = (
    cand['best_candidate'].notna()
    &
    cand['best_candidate'].astype(str).str.len().gt(0)
    if 'best_candidate' in cand.columns
    else False
)

cand['selection_score'] = (
    cand['alpha_score'] 
    * cand['coverage']
    # * np.where(cand['max_redundancy'].fillna(0)<=0.95,1.0,0.75)
    * np.where(cand['max_redundancy'].isna(), 1.0, 1.0 - 0.35*cand['max_redundancy'])
    * np.where(cand['forensic_ok'],1.0,0.90)
)

cand = cand.sort_values(
    ['selection_score','alpha_score','mutual_information'],
    ascending=[False,False,False]
).reset_index(drop=True)

cand['selection_rank'] = np.arange(1,len(cand)+1)

print("\n--- CANDIDATE SELECTION ---")

print(
    cand[
        ['selection_rank','feature','family','horizon','alpha_score',
         'mutual_information','spearman','max_redundancy',
         'coverage','best_candidate','confidence',
         'selection_score']
    ].head(20).to_string(index=False)
)

top = cand.iloc[0]

FEATURE = str(top['feature'])
FAMILY = str(top['family'])
BEST_CANDIDATE = str(top['best_candidate'])

SPEARMAN = float(top['spearman']) if not pd.isna(top['spearman']) else 0.0

if SPEARMAN != 0:
    SIGNAL_SIGN = 1 if SPEARMAN > 0 else -1
else:
    PEARSON = float(top['pearson']) if 'pearson' in top.index and not pd.isna(top['pearson']) else 0.0
    SIGNAL_SIGN = 1 if PEARSON >= 0 else -1

print("\nSelected feature:",FEATURE)
print("Selected family:",FAMILY)
print("Forensic hypothesis:",BEST_CANDIDATE)
print("Signal direction:",SIGNAL_SIGN)

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
    'horizon_rank',
    'feature_rank',
    'max_redundancy',
    'stability',
    'forensic_ok',
    'selection_score'
]

sel_cols = [x for x in sel_cols if x in cand.columns]

cand[sel_cols].head(20).to_csv(
    SELECTION_FILE,
    index=False
)

print("\nSelection file written:",SELECTION_FILE)

csv_files = sorted(
    DATA_DIR.glob("*.csv"),
    key=get_day_number
)

comp_files = [
    f for f in csv_files
    if get_day_number(f) in ALL_DAYS
]

print("\nFiles available for strategy:",len(comp_files))

if len(comp_files) != 70:
    raise ValueError("Strategy input file count is not 70")

feature_check = []

for f in comp_files:

    d = get_day_number(f)
    df = pd.read_csv(f,nrows=2)

    if FEATURE not in df.columns:
        raise ValueError(f"{FEATURE} not found in {f.name}")

    feature_check.append({
        'day':d,
        'file':f.name,
        'feature':FEATURE,
        'available':True
    })

feature_check = pd.DataFrame(feature_check)

print("\nFeature availability:")
print(feature_check['available'].value_counts())

train_vals = []

for f in comp_files:

    d = get_day_number(f)

    if d not in TRAIN_DAYS:
        continue

    df = pd.read_csv(
        f,
        usecols=[FEATURE]
    )

    x = pd.to_numeric(
        df[FEATURE],
        errors='coerce'
    ).replace([np.inf,-np.inf],np.nan).dropna()

    if len(x):
        train_vals.append(x)

if len(train_vals)==0:
    raise ValueError("No training feature data found")

train_x = pd.concat(train_vals,ignore_index=True)

TRAIN_MEAN = train_x.mean()
TRAIN_STD = train_x.std(ddof=0)

if pd.isna(TRAIN_MEAN) or pd.isna(TRAIN_STD):
    raise ValueError("Invalid training normalization statistics")

if TRAIN_STD <= 0:
    raise ValueError("Training feature standard deviation is zero")

print("\nTraining normalization:")
print("Mean:",TRAIN_MEAN)
print("Std :",TRAIN_STD)

print("\n--- THRESHOLD GRID ---")

threshold_rows = []

for th in THRESHOLDS:

    threshold_rows.append({
        'threshold':th,
        'long_rule':f'z > {th}',
        'short_rule':f'z < {-th}',
        'flat_rule':f'{-th} <= z <= {th}',
        'position_rule':'LONG=+1, FLAT=0, SHORT=-1'
    })

threshold_df = pd.DataFrame(threshold_rows)

print(threshold_df.to_string(index=False))

CONFIG = {
    'feature':FEATURE,
    'family':FAMILY,
    'forensic_hypothesis':BEST_CANDIDATE,
    'rebalance_minutes':REBALANCE,
    'feature_horizon':HORIZON,
    'execution_lag_minutes':1,
    'holding_period_minutes':HORIZON,
    'entry_rule':'signal_at_t_execute_at_t+1',
    'exit_rule':'t+HORIZON',
    'signal':'signal_t = signal_direction * z_t',
    'z_score':'z_t = (feature_t - train_mean) / train_std',
    'signal_direction':SIGNAL_SIGN,
    'normalization':'TRAIN_ONLY_MEAN_STD',
    'train_mean':TRAIN_MEAN,
    'train_std':TRAIN_STD,
    'thresholds':','.join(map(str,THRESHOLDS)),
    'position_rule':
        'LONG=+1 if signal>threshold; '
        'FLAT=0 if abs(signal)<=threshold; '
        'SHORT=-1 if signal<-threshold',
    'max_exposure':MAX_EXPOSURE,
    'transaction_cost_bps':COST_BPS,
    'turnover_model':'absolute_position_change',
    'cost_application':'abs(position_t - position_t_minus_1) * cost_bps',
    'train_start':TRAIN_DAYS[0],
    'train_end':TRAIN_DAYS[-1],
    'validation_start':VALIDATION_DAYS[0],
    'validation_end':VALIDATION_DAYS[-1],
    'test_start':TEST_DAYS[0],
    'test_end':TEST_DAYS[-1],
    'train_days':','.join(map(str,TRAIN_DAYS)),
    'validation_days':','.join(map(str,VALIDATION_DAYS)),
    'test_days':','.join(map(str,TEST_DAYS)),
    'lookahead_rule':'feature_t_signal_t_execute_t+1',
    'candidate_selection_source':'17_feature_alpha_rank',
    'candidate_selection_scope':'ALL_70_DAYS_TASK4_DISCOVERY',
    'parameter_selection_rule':'TRAIN_DISCOVERY_VALIDATION_SELECTION_TEST_LOCKED',
    'alpha_type':'nonlinear_or_distributional_candidate',
    'test_usage':'NO_PARAMETER_SELECTION',
    'diagnostics_required':
        'long_fraction,short_fraction,flat_fraction,'
        'active_fraction,mean_abs_position,'
        'trade_count,turnover,gross_return,net_return'
}

config_df = pd.DataFrame(
    [{'parameter':k,'value':v} for k,v in CONFIG.items()]
)

config_df.to_csv(
    CONFIG_FILE,
    index=False
)

family_summary = (
    cand.groupby('family')
    .agg(
        candidates=('feature','count'),
        best_selection_score=('selection_score','max'),
        best_alpha=('alpha_score','max'),
        mean_alpha=('alpha_score','mean')
    )
    .sort_values('best_selection_score',ascending=False)
    .reset_index()
)
family_summary.to_csv(FAMILY_FILE,index=False)

finalists_df = cand.head(FINALISTS).copy()
finalists_df.to_csv(FINALISTS_FILE,index=False)

print("\nConfiguration file written:",CONFIG_FILE)

print("\n--- STRATEGY SPECIFICATION ---")

print("FEATURE       :",FEATURE)
print("FAMILY        :",FAMILY)
print("HYPOTHESIS    :",BEST_CANDIDATE)
print("REBALANCE     :",f"{REBALANCE} minute")
print("HORIZON       :",f"{HORIZON} minutes")
print("DIRECTION     :",SIGNAL_SIGN)
print("SIGNAL        : signal = direction * z")
print("NORMALIZATION : TRAIN ONLY")
print("EXECUTION     : signal_t -> execute_t+1")
print("HOLDING       :",f"{HORIZON} minutes")
print("POSITION RULE : threshold-based LONG/FLAT/SHORT")
print("TRAIN MEAN    :",TRAIN_MEAN)
print("TRAIN STD     :",TRAIN_STD)
print("THRESHOLDS    :",THRESHOLDS)
print("POSITION      : LONG=+1, FLAT=0, SHORT=-1")
print("MAX EXPOSURE  :",MAX_EXPOSURE)
print("COST          :",COST_BPS,"bps")

print("\nTrain      :",TRAIN_DAYS[0],"-",TRAIN_DAYS[-1])
print("Validation :",VALIDATION_DAYS[0],"-",VALIDATION_DAYS[-1])
print("Test       :",TEST_DAYS)

print("\n--- FILES WRITTEN ---")
print(SELECTION_FILE)
print(FINALISTS_FILE)
print(FAMILY_FILE)
print(CONFIG_FILE)

print("\nDone.")