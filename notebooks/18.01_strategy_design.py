from pathlib import Path

import re

import numpy as np

import pandas as pd

import matplotlib.pyplot as plt


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
RESULTS_DIR = Path(r'.\results')

ALPHA_FILE = OUTPUT_DIR / "17_feature_alpha_rank.csv"
CORR_FILE = OUTPUT_DIR / "17_feature_correlation.csv"

SELECTION_FILE = OUTPUT_DIR / "18_strategy_selection.csv"
CONFIG_FILE = OUTPUT_DIR / "18_strategy_config.csv"

REBALANCE = 1
HORIZON = 10
COST_BPS = 7.5
MAX_EXPOSURE = 1.0

THRESHOLDS = [0.5,0.75,1.0,1.25,1.5]

TRAIN_DAYS = list(range(1,44))
VALIDATION_DAYS = list(range(44,55))
TEST_DAYS = list(range(55,65)) + list(range(80,86))

ALL_DAYS = TRAIN_DAYS + VALIDATION_DAYS + TEST_DAYS

if len(ALL_DAYS) != 70:
    raise ValueError("Strategy day universe is not 70 days")

if len(set(ALL_DAYS)) != 70:
    raise ValueError("Duplicate days in strategy split")

if set(ALL_DAYS) != set(list(range(1,65)) + list(range(80,86))):
    raise ValueError("Strategy split does not match usable-day universe")

print("\n--- TASK 5 STRATEGY DESIGN ---")

print("\nTrain days:",TRAIN_DAYS[0],"-",TRAIN_DAYS[-1],len(TRAIN_DAYS))
print("Validation days:",VALIDATION_DAYS[0],"-",VALIDATION_DAYS[-1],len(VALIDATION_DAYS))
print("Test days:",TEST_DAYS[:1],"...",TEST_DAYS[-1],len(TEST_DAYS))

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

if 'alpha_score' not in alpha_df.columns:
    raise ValueError("alpha_score missing from 17_feature_alpha_rank.csv")

if 'feature' not in alpha_df.columns:
    raise ValueError("feature missing from 17_feature_alpha_rank.csv")

if 'horizon' not in alpha_df.columns:
    raise ValueError("horizon missing from 17_feature_alpha_rank.csv")

if 'family' not in alpha_df.columns:
    raise ValueError("family missing from 17_feature_alpha_rank.csv")

if 'spearman' not in alpha_df.columns:
    raise ValueError("spearman missing from 17_feature_alpha_rank.csv")

if 'mutual_information' not in alpha_df.columns:
    raise ValueError("mutual_information missing from 17_feature_alpha_rank.csv")

alpha_df['horizon'] = pd.to_numeric(alpha_df['horizon'],errors='coerce')
alpha_df['alpha_score'] = pd.to_numeric(alpha_df['alpha_score'],errors='coerce')
alpha_df['mutual_information'] = pd.to_numeric(alpha_df['mutual_information'],errors='coerce')
alpha_df['spearman'] = pd.to_numeric(alpha_df['spearman'],errors='coerce')

alpha_df = alpha_df.dropna(subset=['feature','horizon','alpha_score'])

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
        corr_df['abs_pearson'] = corr_df['pearson'].abs()
    else:
        raise ValueError("Correlation strength column missing")

corr_df['abs_pearson'] = pd.to_numeric(
    corr_df['abs_pearson'],errors='coerce'
)

corr_df = corr_df.dropna(
    subset=['feature_1','feature_2','abs_pearson']
)

rank_map = dict(
    zip(cand['feature'],cand['predictive_rank'])
)

red = {}

for f in cand['feature']:
    q = corr_df[
        ((corr_df['feature_1']==f) |
         (corr_df['feature_2']==f))
        &
        (corr_df['abs_pearson']<0.999999999)
    ]

    if len(q):
        red[f] = q['abs_pearson'].max()
    else:
        red[f] = np.nan

cand['max_redundancy'] = cand['feature'].map(red)

cand['stability'] = cand['days'].fillna(0)/len(ALL_DAYS)

cand['forensic_ok'] = (
    cand['best_candidate'].notna()
    &
    cand['best_candidate'].astype(str).str.len().gt(0)
)

cand['family_count'] = cand.groupby('family')['feature'].transform('count')

cand['selection_score'] = (
    cand['alpha_score']
    * cand['stability']
    * np.where(
        cand['max_redundancy'].fillna(0)<=0.95,
        1.0,
        0.75
    )
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
        ['selection_rank','feature','family','alpha_score',
         'mutual_information','spearman','max_redundancy',
         'stability','best_candidate','confidence',
         'selection_score']
    ].head(20).to_string(index=False)
)

top = cand.iloc[0]

FEATURE = str(top['feature'])
FAMILY = str(top['family'])
BEST_CANDIDATE = str(top['best_candidate'])

SPEARMAN = float(top['spearman'])

if not pd.isna(SPEARMAN) and SPEARMAN != 0:
    SIGNAL_SIGN = 1 if SPEARMAN > 0 else -1
else:
    PEARSON = float(top['pearson']) if 'pearson' in top.index and not pd.isna(top['pearson']) else 0
    SIGNAL_SIGN = 1 if PEARSON >= 0 else -1

print("\nSelected feature:",FEATURE)
print("Selected family:",FAMILY)
print("Forensic hypothesis:",BEST_CANDIDATE)
print("Signal direction:",SIGNAL_SIGN)

top_row = cand.iloc[0].copy()

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

sel_df = cand[sel_cols].head(20).copy()

sel_df.to_csv(SELECTION_FILE,index=False)

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
        raise ValueError(
            f"{FEATURE} not found in {f.name}"
        )

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
    ).replace([np.inf,-np.inf],np.nan)

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
    'signal':'training_standardized_feature',
    'signal_direction':SIGNAL_SIGN,
    'normalization':'TRAIN_ONLY_MEAN_STD',
    'train_mean':TRAIN_MEAN,
    'train_std':TRAIN_STD,
    'thresholds':','.join(map(str,THRESHOLDS)),
    'position_rule':'LONG=+1, FLAT=0, SHORT=-1',
    'max_exposure':MAX_EXPOSURE,
    'transaction_cost_bps':COST_BPS,
    'train_start':TRAIN_DAYS[0],
    'train_end':TRAIN_DAYS[-1],
    'validation_start':VALIDATION_DAYS[0],
    'validation_end':VALIDATION_DAYS[-1],
    'test_start':TEST_DAYS[0],
    'test_end':TEST_DAYS[-1],
    'train_days':','.join(map(str,TRAIN_DAYS)),
    'validation_days':','.join(map(str,VALIDATION_DAYS)),
    'test_days':','.join(map(str,TEST_DAYS)),
    'lookahead_rule':'feature_t_signal_t_execute_t+1'
}

config_df = pd.DataFrame(
    [{'parameter':k,'value':v} for k,v in CONFIG.items()]
)

config_df.to_csv(CONFIG_FILE,index=False)

print("\nConfiguration file written:",CONFIG_FILE)

print("\n--- STRATEGY SPECIFICATION ---")

print("FEATURE       :",FEATURE)
print("FAMILY        :",FAMILY)
print("HYPOTHESIS    :",BEST_CANDIDATE)
print("REBALANCE     :",f"{REBALANCE} minute")
print("HORIZON       :",f"{HORIZON} minutes")
print("DIRECTION     :",SIGNAL_SIGN)
print("NORMALIZATION : TRAIN ONLY")
print("TRAIN MEAN    :",TRAIN_MEAN)
print("TRAIN STD     :",TRAIN_STD)
print("THRESHOLDS    :",THRESHOLDS)
print("POSITION      : LONG=+1, FLAT=0, SHORT=-1")
print("MAX EXPOSURE  :",MAX_EXPOSURE)
print("COST           :",COST_BPS,"bps")

print("\nTrain      :",TRAIN_DAYS[0],"-",TRAIN_DAYS[-1])
print("Validation :",VALIDATION_DAYS[0],"-",VALIDATION_DAYS[-1])
print("Test       :",TEST_DAYS)

print("\n--- FILES WRITTEN ---")
print(SELECTION_FILE)
print(CONFIG_FILE)

print("\nDone.")
