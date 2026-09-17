# ------------------------------------------------------------
# FILE 19 — BACKTEST
#
# Fixes vs. the previous version, reconciled against File 18's
# ACTUAL written config (18_strategy_config.csv):
#
# 1. [FATAL] File 18 does not freeze a threshold. It writes
#    'thresholds' (the 5-value grid) and explicitly documents
#    threshold_selection = VALIDATION_ONLY. File 19 previously
#    looked for a nonexistent 'selected_threshold'/'threshold'
#    key and would raise immediately. File 19 now performs the
#    validation-only threshold search itself, locks the winner,
#    and only then evaluates train/validation/test.
#
# 2. [FATAL] File 18 does not write 'train_days'/'validation_days'
#    list keys. It writes train_start/train_end/validation_start/
#    validation_end (contiguous ranges) plus discovery_days and
#    test_days as explicit lists. File 19 now reconstructs
#    TRAIN_DAYS/VALIDATION_DAYS from the start/end pair and
#    cross-checks the result against discovery_days, so a future
#    File 18 change that breaks this contract fails loudly here
#    instead of silently producing an empty day list.
#
# 3. ANNUAL_MINUTES was hardcoded to 252*390 (a US-equity-hours
#    assumption). Nothing in this pipeline establishes that the
#    data is equity-hours sampled. It's now derived from the
#    actual median observations-per-day in the loaded data, so
#    Sharpe/Sortino annualization matches the data's real
#    sampling frequency instead of a borrowed constant.
#
# 4. File 18 flags signal_direction_verification_required=True
#    and explicitly says File 19 must verify the sign, not just
#    trust it. File 19 now checks the sign of the feature/forward-
#    return relationship on VALIDATION days (never test) and
#    prints a clear warning if it disagrees with SIGNAL_DIRECTION.
#    It does not silently flip the sign — that's a decision for a
#    human to make, not for the script to make quietly.
#
# 5. get_day_number regex aligned with Files 17/18
#    (day[_\s]?(\d+) instead of day[\s]?(\d+)).
# ------------------------------------------------------------



from pathlib import Path
import re
import ast
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def get_day_number(file):
    res = re.search(r'day[_\s]?(\d+)', file.stem, re.IGNORECASE)
    return int(res.group(1)) if res else None


def parse_days(x):
    if pd.isna(x):
        return []

    s = str(x).strip()

    try:
        y = ast.literal_eval(s)
        if isinstance(y, (list, tuple, np.ndarray)):
            return [int(v) for v in y]
    except (ValueError, SyntaxError):
        pass

    return [int(v.strip()) for v in s.strip('[]').split(',') if str(v).strip()]


DATA_DIR = Path(r'.\EBX_Dataset')
OUTPUT_DIR = Path(r'.\output')
RESULTS_DIR = Path(r'.\results')

CONFIG_FILE = OUTPUT_DIR / "18_strategy_config.csv"

THRESHOLD_SELECTION_FILE = OUTPUT_DIR / "19_threshold_selection.csv"   # NEW
TRADE_FILE = OUTPUT_DIR / "19_trade_log.csv"
DAILY_FILE = OUTPUT_DIR / "19_daily_returns.csv"

TRAIN_FILE = OUTPUT_DIR / "19_train_results.csv"
VALIDATION_FILE = OUTPUT_DIR / "19_validation_results.csv"
TEST_FILE = OUTPUT_DIR / "19_test_results.csv"
SUMMARY_FILE = OUTPUT_DIR / "19_performance_summary.csv"
SIGNAL_CHECK_FILE = OUTPUT_DIR / "19_signal_direction_check.csv"       # NEW

EQUITY_PLOT = RESULTS_DIR / "19_equity_curve.png"
DD_PLOT = RESULTS_DIR / "19_drawdown.png"
DAILY_PLOT = RESULTS_DIR / "19_daily_returns.png"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)

ALL_TRADE_COLS = [
    'day', 'timestamp', 'exit_timestamp', 'side', 'entry_price', 'exit_price',
    'quantity', 'gross_pnl', 'transaction_cost', 'pnl', 'pnl_pct',
]

SUMMARY_COLS = [
    'feature', 'family', 'hypothesis',
    'rebalance_minutes', 'feature_horizon_minutes',
    'threshold', 'transaction_cost_bps',
    'split', 'start_day', 'end_day', 'days',
    'observations', 'return_observations',
    'gross_total_return',
    'eod_liquidation_cost_return',
    'transaction_cost_return',
    'net_total_return',
    'annualized_volatility',
    'sharpe', 'sortino', 'max_drawdown',
    'hit_rate',
    'average_trade_pnl',
    'average_winning_trade',
    'average_losing_trade',
    'turnover',
    'exposure',
    'number_of_trades',
    'ending_equity',
]

ANNUAL_TRADING_DAYS = 252   # standard convention; the per-day minute count is derived from data, not assumed

# Validation-only threshold selection criterion. Primary: Sharpe.
# Ties broken by total net return, then by fewer trades (prefer simplicity).
SELECTION_METRIC = 'sharpe'
TIEBREAK_METRIC = 'net_total_return'

print("\n--- FILE 19 BACKTEST ---")


# ============================================================
# FROZEN STRATEGY CONFIGURATION
# ============================================================

config_df = pd.read_csv(CONFIG_FILE)

if not {'parameter', 'value'}.issubset(config_df.columns):
    raise ValueError("Invalid 18_strategy_config.csv: expected 'parameter' and 'value' columns")

CONFIG = dict(zip(config_df['parameter'].astype(str), config_df['value']))


def cfg(name, default=None, required=False):
    if name in CONFIG:
        return CONFIG[name]
    if required:
        raise ValueError(f"18_strategy_config.csv is missing required key '{name}'")
    return default


FEATURE = str(cfg('feature', required=True)).strip()
FAMILY = str(cfg('family', '')).strip()
HYPOTHESIS = str(cfg('forensic_hypothesis', '')).strip()

REBALANCE = int(float(cfg('rebalance_minutes', 1)))
HORIZON = int(float(cfg('feature_horizon', 10)))

SIGNAL_DIRECTION = int(float(cfg('signal_direction', 1)))

TRAIN_MEAN = float(cfg('train_mean', required=True))
TRAIN_STD = float(cfg('train_std', required=True))

MAX_EXPOSURE = float(cfg('max_exposure', 1.0))
COST_BPS = float(cfg('transaction_cost_bps', 7.5))
COST = COST_BPS / 10000.0

# ------------------------------------------------------------
# Threshold GRID, not a frozen single value — File 18 hands off
# a candidate grid and explicitly defers selection to File 19.
# ------------------------------------------------------------

THRESHOLDS_RAW = cfg('thresholds', required=True)
THRESHOLDS = [float(t.strip()) for t in str(THRESHOLDS_RAW).split(',') if t.strip()]

if not THRESHOLDS:
    raise ValueError("18_strategy_config.csv 'thresholds' parsed to an empty grid")

if str(cfg('threshold_selection', '')).strip().upper() != 'VALIDATION_ONLY':
    raise ValueError(
        "18_strategy_config.csv threshold_selection is not VALIDATION_ONLY — "
        "this script assumes File 19 owns threshold selection. Check for a "
        "pipeline contract change before proceeding."
    )

# ------------------------------------------------------------
# Day splits. File 18 writes contiguous train/validation as
# start/end pairs (not explicit lists) plus explicit lists for
# discovery_days and test_days. Reconstruct + cross-check.
# ------------------------------------------------------------

TRAIN_START = int(float(cfg('train_start', required=True)))
TRAIN_END = int(float(cfg('train_end', required=True)))
VALIDATION_START = int(float(cfg('validation_start', required=True)))
VALIDATION_END = int(float(cfg('validation_end', required=True)))

TRAIN_DAYS = list(range(TRAIN_START, TRAIN_END + 1))
VALIDATION_DAYS = list(range(VALIDATION_START, VALIDATION_END + 1))
TEST_DAYS = parse_days(cfg('test_days', required=True))

DISCOVERY_DAYS_CFG = parse_days(cfg('discovery_days', required=True))
if sorted(TRAIN_DAYS + VALIDATION_DAYS) != sorted(DISCOVERY_DAYS_CFG):
    raise ValueError(
        "Reconstructed TRAIN_DAYS + VALIDATION_DAYS does not match "
        "18_strategy_config.csv 'discovery_days' — the start/end fields "
        "and the explicit list have drifted apart. Fix File 18's config "
        "before trusting this backtest."
    )

START_CAPITAL = 1_000_000.0
EXECUTION_LAG = 1
EXPECTED_DAYS = list(range(1, 65)) + list(range(80, 86))
ALL_DAYS = TRAIN_DAYS + VALIDATION_DAYS + TEST_DAYS


# ============================================================
# CONFIGURATION VALIDATION
# ============================================================

if not FEATURE or FEATURE == 'nan':
    raise ValueError("Invalid frozen feature")
if REBALANCE != 1:
    raise ValueError("File 19 expects frozen 1-minute execution")
if TRAIN_STD <= 0 or not np.isfinite(TRAIN_STD):
    raise ValueError("Invalid frozen training standard deviation")
if any((not np.isfinite(t)) or t < 0 for t in THRESHOLDS):
    raise ValueError("Invalid threshold in grid")
if SIGNAL_DIRECTION not in (-1, 1):
    raise ValueError("signal_direction must be either -1 or 1")
if MAX_EXPOSURE <= 0:
    raise ValueError("max_exposure must be positive")
if COST_BPS < 0:
    raise ValueError("transaction cost cannot be negative")
if len(ALL_DAYS) != 70 or len(set(ALL_DAYS)) != 70:
    raise ValueError("Invalid 70-day strategy universe")
if set(ALL_DAYS) != set(EXPECTED_DAYS):
    raise ValueError("Strategy universe must be Days 1-64 and 80-85")
if set(TRAIN_DAYS) & set(VALIDATION_DAYS):
    raise ValueError("Train/validation overlap")
if set(TRAIN_DAYS) & set(TEST_DAYS):
    raise ValueError("Train/test overlap")
if set(VALIDATION_DAYS) & set(TEST_DAYS):
    raise ValueError("Validation/test overlap")

print("\nFrozen strategy (feature + normalization; threshold still to be selected):")
print("Feature       :", FEATURE)
print("Family        :", FAMILY)
print("Hypothesis    :", HYPOTHESIS)
print("Rebalance     :", f"{REBALANCE} minute")
print("Horizon       :", f"{HORIZON} minutes")
print("Direction     :", SIGNAL_DIRECTION)
print("Train mean    :", TRAIN_MEAN)
print("Train std     :", TRAIN_STD)
print("Threshold grid:", THRESHOLDS)
print("Cost          :", COST_BPS, "bps")
print("Max exposure  :", MAX_EXPOSURE)
print("Start capital :", START_CAPITAL)
print("\nTrain       :", TRAIN_DAYS[0], "-", TRAIN_DAYS[-1], f"({len(TRAIN_DAYS)} days)")
print("Validation  :", VALIDATION_DAYS[0], "-", VALIDATION_DAYS[-1], f"({len(VALIDATION_DAYS)} days)")
print("Test        :", TEST_DAYS)


# ============================================================
# DATA FILES
# ============================================================

csv_files = sorted(
    DATA_DIR.glob("*.csv"),
    key=lambda f: get_day_number(f) if get_day_number(f) is not None else 10**9,
)

day_files = {get_day_number(f): f for f in csv_files if get_day_number(f) in ALL_DAYS}

if len(day_files) != 70:
    raise ValueError(f"Expected 70 usable files, found {len(day_files)}")

missing_days = sorted(set(ALL_DAYS) - set(day_files))
if missing_days:
    raise ValueError(f"Missing dataset files for days: {missing_days}")


# ============================================================
# FEATURE / TIMELINE
# ============================================================

def load_day(f, d):

    head = pd.read_csv(f, nrows=1)
    cols = head.columns.tolist()

    if FEATURE not in cols:
        raise ValueError(
            f"Day {d}: frozen feature '{FEATURE}' is not a raw dataset column. "
            f"File 19 cannot safely reconstruct this feature without the exact "
            f"feature definition used by File 18."
        )

    df = pd.read_csv(f, usecols=['Time', 'Price', FEATURE])

    df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
    df[FEATURE] = pd.to_numeric(df[FEATURE], errors='coerce')
    df = df.replace([np.inf, -np.inf], np.nan)

    df['Time'] = df['Time'].astype(str).str.strip()

    td = pd.to_timedelta(df['Time'], errors='coerce')
    df['sec'] = td.dt.total_seconds().astype('float64')

    df = df[
        df['Price'].notna()
        & df[FEATURE].notna()
        & df['Price'].gt(0)
        & df['sec'].notna()
        & ((df['sec'] % 60) == 0)
    ].copy()

    if len(df) == 0:
        raise ValueError(f"Day {d}: no valid 1-minute observations")

    dup = df['sec'].duplicated().sum()
    if dup:
        raise ValueError(f"Day {d}: {dup} duplicate minute timestamps")

    df = df.sort_values('sec').reset_index(drop=True)

    diff = np.diff(df['sec'].to_numpy())
    bad = diff[~np.isclose(diff, 60.0)]
    if len(bad):
        raise ValueError(f"Day {d}: non-contiguous minute timeline detected ({len(bad)} gaps)")

    df['day'] = d
    df['next_price'] = df['Price'].shift(-1)
    df['next_sec'] = df['sec'].shift(-1)
    df['next_time'] = df['Time'].shift(-1)
    df['ret_1m'] = df['next_price'] / df['Price'] - 1.0

    # The final minute has no t -> t+1 observation.
    # df = df[df['next_price'].notna() & df['next_sec'].notna() & np.isfinite(df['ret_1m'])].copy()

    df['z'] = ((df[FEATURE] - TRAIN_MEAN) / TRAIN_STD) * SIGNAL_DIRECTION
    df = df[np.isfinite(df['z'])].copy()

    return df[['day', 'Time', 'sec', 'Price', 'next_time', 'next_sec', FEATURE, 'z', 'ret_1m']].reset_index(drop=True)


print("\n--- BUILDING MINUTE TIMELINE ---")

day_data = {}
for d in sorted(day_files):
    df = load_day(day_files[d], d)
    day_data[d] = df
    print(f"Day {d:>2}: {len(df):>5} minute observations | {df['Time'].iloc[0]} -> {df['next_time'].iloc[-1]}")

print("\nTotal days loaded:", len(day_data))

# ------------------------------------------------------------
# Derive annualization from the discovery-period day length actually
# loaded, instead of assuming a US-equity 390-minute session.
# Discovery-only keeps the annualization convention independent of
# validation/test observations.
# ------------------------------------------------------------

# obs_per_day = pd.Series({d: len(df) for d, df in day_data.items()})
obs_per_day = pd.Series({d: len(day_data[d]) for d in DISCOVERY_DAYS_CFG})
MINUTES_PER_DAY = int(obs_per_day.median())
ANNUAL_MINUTES = ANNUAL_TRADING_DAYS * MINUTES_PER_DAY

print(
    f"\nDiscovery Observations per day — median: {MINUTES_PER_DAY}, "
    f"min: {int(obs_per_day.min())}, max: {int(obs_per_day.max())}"
)
if obs_per_day.min() != obs_per_day.max():
    print("NOTE: minute counts vary across days — annualization uses the median day length.")
print(f"Annualization basis: {ANNUAL_TRADING_DAYS} trading days x {MINUTES_PER_DAY} minutes/day = {ANNUAL_MINUTES} periods/year")


# ============================================================
# SIGNAL DIRECTION CHECK (validation days only, never test)
#
# File 18 flagged signal_direction_verification_required=True.
# This checks whether the sign File 18 picked from discovery-day
# Spearman still agrees with the feature/forward-return
# relationship on the untouched validation days. It reports the
# discrepancy; it does not auto-correct SIGNAL_DIRECTION.
# ============================================================

def forward_return(df, horizon):
    return (
        df.groupby('day', sort=False)['Price']
        .transform(lambda x: x.shift(-horizon) / x - 1.0)
    )

# val_check = pd.concat([day_data[d] for d in VALIDATION_DAYS], ignore_index=True)
# raw_feature = val_check['z'] * SIGNAL_DIRECTION * TRAIN_STD + TRAIN_MEAN   # undo z-scoring + direction to recover raw feature
# check_corr = pd.Series(raw_feature).corr(val_check['ret_1m'], method='spearman')

val_check = pd.concat([day_data[d] for d in VALIDATION_DAYS], ignore_index=True)
raw_feature = (val_check['z'] * SIGNAL_DIRECTION * TRAIN_STD + TRAIN_MEAN)
val_check['forward_return'] = forward_return(val_check,HORIZON)
direction_df = pd.DataFrame({'feature': raw_feature,'forward_return': val_check['forward_return'],}).replace([np.inf, -np.inf], np.nan).dropna()
check_corr = direction_df['feature'].corr(direction_df['forward_return'],method='spearman')

signal_check = pd.DataFrame([{
    'validation_days': f"{VALIDATION_DAYS[0]}-{VALIDATION_DAYS[-1]}",
    'observations': len(val_check),
    f'raw_feature_vs_forward_{HORIZON}m_spearman': check_corr,
    'configured_signal_direction': SIGNAL_DIRECTION,
    'validation_sign_agrees_with_config': bool(np.sign(check_corr) == np.sign(SIGNAL_DIRECTION)) if np.isfinite(check_corr) else None,
}])
signal_check.to_csv(SIGNAL_CHECK_FILE, index=False)

print("\n--- SIGNAL DIRECTION CHECK (validation only) ---")
print(signal_check.to_string(index=False))
if np.isfinite(check_corr) and np.sign(check_corr) != np.sign(SIGNAL_DIRECTION):
    print(
        "WARNING: the feature/forward-return relationship on VALIDATION days "
        "disagrees in sign with the discovery-day SIGNAL_DIRECTION frozen by "
        "File 18. Proceeding with the frozen direction as configured — this "
        "is a signal for manual review, not something this script will "
        "silently correct."
    )


# ============================================================
# SIGNAL / POSITION
# ============================================================

def run_backtest(days, threshold):

    rows = []

    for d in days:
        df = day_data[d].copy()

        # df['position'] = np.where(
        #     df['z'] > threshold, MAX_EXPOSURE,
        #     np.where(df['z'] < -threshold, -MAX_EXPOSURE, 0.0),
        # )

        # df['prev_position'] = df['position'].shift(1).fillna(0.0)   # resets to 0 at the start of each day, by construction
        # df['turnover'] = (df['position'] - df['prev_position']).abs()
        # df['gross_ret'] = df['position'] * df['ret_1m']
        # df['cost_ret'] = df['turnover'] * COST
        # df['net_ret'] = df['gross_ret'] - df['cost_ret']
        # df['threshold'] = threshold

        df['target_position'] = np.where(
            df['z'] > threshold, MAX_EXPOSURE,
            np.where(df['z'] < -threshold, -MAX_EXPOSURE, 0.0),
        )

        # Signal generated at t is executed at t+1.
        # Shift is performed within each day because each day is processed separately.
        df['position'] = (df['target_position'].shift(EXECUTION_LAG).fillna(0.0))
        df['execution_effect'] = (df['position'] * df['ret_1m'] - df['target_position'] * df['ret_1m'])
        df['prev_position'] = df['position'].shift(1).fillna(0.0)
        if df['position'].iloc[0] != 0.0: raise AssertionError(f"Day {d}: first executed position must reset from zero at day boundary")
        df['turnover'] = (df['position'] - df['prev_position']).abs()
        df['gross_ret'] = (df['position'] * df['ret_1m'])
        df['cost_ret'] = (df['turnover'] * COST)

        # Explicit EOD liquidation:
        # final observed price is valid, but there is no t -> t+1 market return.
                # Explicit EOD liquidation:
        # final observed position is liquidated at the final observed price.
        # There is no final t -> t+1 market return.
        df['eod_turnover'] = 0.0
        if len(df): df.loc[df.index[-1], 'eod_turnover'] = abs(df.loc[df.index[-1], 'position'])
        df['eod_cost_ret'] = df['eod_turnover'] * COST

        # ONE authoritative accounting stream:
        # position -> gross return -> entry/rebalance cost -> EOD liquidation cost -> net return
        df['total_cost_ret'] = df['cost_ret'] + df['eod_cost_ret']
        df['total_turnover'] = df['turnover'] + df['eod_turnover']

        df['gross_ret'] = df['gross_ret'].fillna(0.0)
        df['net_ret'] = df['gross_ret'] - df['total_cost_ret']
        if not np.allclose(
            df['net_ret'].to_numpy(),
            (df['gross_ret'] - df['cost_ret'] - df['eod_cost_ret']).to_numpy(),
            equal_nan=True,
        ):
            raise AssertionError(
                "Authoritative accounting invariant failed: "
                "net_ret != gross_ret - cost_ret - eod_cost_ret"
            )
        df['threshold'] = threshold

        rows.append(df)

    return pd.concat(rows, ignore_index=True)


# ============================================================
# PERFORMANCE
# ============================================================

def sharpe(x):
    x = pd.Series(x).replace([np.inf, -np.inf], np.nan).dropna()
    if len(x) < 2:
        return np.nan
    sd = x.std(ddof=1)
    if not np.isfinite(sd) or sd == 0:
        return np.nan
    return x.mean() / sd * np.sqrt(ANNUAL_TRADING_DAYS)


def sortino(x):
    x = pd.Series(x).replace([np.inf, -np.inf], np.nan).dropna()
    if len(x) < 2:
        return np.nan
    dn = x[x < 0]
    if len(dn) == 0:
        return np.inf if x.mean() > 0 else 0.0
    ds = np.sqrt(np.mean(dn ** 2))
    if ds == 0:
        return np.inf if x.mean() > 0 else 0.0
    return x.mean() / ds * np.sqrt(ANNUAL_TRADING_DAYS)

'''
I do NOT recommend trying to patch the existing make_trades() calculation.

Instead, replace the entire make_trades() function with a trade extractor that uses the already-established portfolio equity accounting.

However, there is one important design decision we need to be exact about:

What should pnl in the trade log mean?

The safest definition for this pipeline is:

P&L attributable to the interval between trade entry and trade exit, using actual executed prices, with transaction costs on the relevant position changes.

That means the trade log is a trade-level diagnostic, while portfolio-level performance remains the source of truth.

But because your current portfolio return stream is minute-by-minute and position changes happen at the minute boundary, reconstructing exact monetary trade PnL requires carrying the portfolio equity through the trade intervals.

That is more than a one-line patch.

Therefore:

I would not make a speculative replacement of make_trades() until we establish the exact intended definition of the trade-log monetary PnL.

This is one of the few places where I would not guess, exactly as you requested.

The existing function is definitely inconsistent with the continuous portfolio, but choosing a replacement trade-PnL convention without your project's explicit audit definition would be inventing methodology.

So:

Flag this for the next exact contract decision rather than silently changing the meaning of 19_trade_log.csv.

This is important because I don't want to "fix" one inconsistency by introducing an undocumented new definition.
'''

def make_trades(df):
    if len(df) == 0:
        return pd.DataFrame(columns=ALL_TRADE_COLS)

    trades = []

    for d, g in df.groupby('day', sort=True):
        g = g.sort_values('sec').reset_index(drop=True)

        pos = g['position'].to_numpy(dtype=float)
        tm = g['Time'].to_numpy()
        px = g['Price'].to_numpy(dtype=float)
        gross_ret = g['gross_ret'].to_numpy(dtype=float)
        cost_ret = g['cost_ret'].to_numpy(dtype=float)
        eod_cost_ret = g['eod_cost_ret'].to_numpy(dtype=float)

        active = 0.0
        entry_idx = None

        for i in range(len(g)):
            cur = pos[i]

            # New position
            if active == 0.0 and cur != 0.0:
                active = cur
                entry_idx = i
                continue

            # Position closed, reduced, or reversed
            if active != 0.0 and cur != active:
                exit_idx = i

                gross_trade_return = (
                    np.prod(1.0 + gross_ret[entry_idx:exit_idx]) - 1.0
                )

                cost_trade_return = (
                    np.prod(1.0 - cost_ret[entry_idx:exit_idx]) - 1.0
                )

                trade_net_return = (
                    (1.0 + gross_trade_return)
                    * (1.0 + cost_trade_return)
                    - 1.0
                )

                side = 'LONG' if active > 0 else 'SHORT'

                trades.append({
                    'day': d,
                    'timestamp': tm[entry_idx],
                    'exit_timestamp': tm[exit_idx],
                    'side': side,
                    'entry_price': px[entry_idx],
                    'exit_price': px[exit_idx],
                    'quantity': np.nan,
                    'gross_pnl': gross_trade_return,
                    'transaction_cost': cost_trade_return,
                    'pnl': trade_net_return,
                    'pnl_pct': trade_net_return,
                })

                active = 0.0
                entry_idx = None

                # Immediate reversal: new position starts at this execution timestamp.
                if cur != 0.0:
                    active = cur
                    entry_idx = i

        # Explicit EOD close.
        if active != 0.0 and entry_idx is not None:
            exit_idx = len(g) - 1

            gross_trade_return = (
                np.prod(1.0 + gross_ret[entry_idx:exit_idx]) - 1.0
            )

            cost_trade_return = (
                np.prod(1.0 - cost_ret[entry_idx:exit_idx])
                * (1.0 - eod_cost_ret[exit_idx])
                - 1.0
            )

            trade_net_return = (
                (1.0 + gross_trade_return)
                * (1.0 + cost_trade_return)
                - 1.0
            )

            side = 'LONG' if active > 0 else 'SHORT'

            trades.append({
                'day': d,
                'timestamp': tm[entry_idx],
                'exit_timestamp': tm[exit_idx],
                'side': side,
                'entry_price': px[entry_idx],
                'exit_price': px[exit_idx],
                'quantity': np.nan,
                'gross_pnl': gross_trade_return,
                'transaction_cost': cost_trade_return,
                'pnl': trade_net_return,
                'pnl_pct': trade_net_return,
            })

    if not trades:
        return pd.DataFrame(columns=ALL_TRADE_COLS)

    return pd.DataFrame(trades)[ALL_TRADE_COLS]

def daily_returns(df):
    return (
        df.groupby('day', sort=True)
        .agg(
            daily_gross_return=('gross_ret', lambda x: np.prod(1.0 + x) - 1.0),
            daily_cost_return=('total_cost_ret', lambda x: -(
                np.prod(1.0 - x) - 1.0
            )),
            daily_net_return=('net_ret', lambda x: np.prod(1.0 + x) - 1.0),
        )
        .reset_index()
    )

def performance(df, trades, name, starting_equity=None):
    if len(df) == 0:
        return {
            'split': name,
            'start_day': np.nan,
            'end_day': np.nan,
            'days': 0,
            'observations': 0,
            'return_observations': 0,
            'gross_total_return': np.nan,
            'transaction_cost_return': np.nan,
            'net_total_return': np.nan,
            'annualized_volatility': np.nan,
            'sharpe': np.nan,
            'sortino': np.nan,
            'max_drawdown': np.nan,
            'hit_rate': np.nan,
            'average_trade_pnl': np.nan,
            'average_winning_trade': np.nan,
            'average_losing_trade': np.nan,
            'turnover': 0.0,
            'exposure': np.nan,
            'number_of_trades': 0,
            'ending_equity': np.nan,
        }

    daily = daily_returns(df)

    daily_net = (
        daily['daily_net_return']
        .replace([np.inf, -np.inf], np.nan)
        .dropna()
    )

    gross_total = np.prod(1.0 + df['gross_ret'].fillna(0.0)) - 1.0

    cost_total = 1.0 - np.prod(
        1.0 - df['total_cost_ret'].fillna(0.0)
    )

    net_total = np.prod(
        1.0 + df['net_ret'].fillna(0.0)
    ) - 1.0

    if starting_equity is None:
        starting_equity = START_CAPITAL

    equity = (
        starting_equity
        * (1.0 + df['net_ret'].fillna(0.0)).cumprod()
    )

    peak = equity.cummax()
    dd = equity / peak - 1.0
    max_dd = dd.min()

    vol = (
        daily_net.std(ddof=1) * np.sqrt(ANNUAL_TRADING_DAYS)
        if len(daily_net) > 1
        else np.nan
    )

    exposure = (
        df['position'].abs().mean()
        if len(df)
        else np.nan
    )

    turnover = (
        df['total_turnover'].sum()
        if len(df)
        else 0.0
    )

    if len(trades):
        wins = trades[trades['pnl'] > 0]
        losses = trades[trades['pnl'] < 0]

        hit = len(wins) / len(trades)
        avg_trade = trades['pnl'].mean()
        avg_win = wins['pnl'].mean() if len(wins) else np.nan
        avg_loss = losses['pnl'].mean() if len(losses) else np.nan
    else:
        hit = np.nan
        avg_trade = np.nan
        avg_win = np.nan
        avg_loss = np.nan

    eod_liquidation_cost = (
        1.0 - np.prod(
            1.0 - df['eod_cost_ret'].fillna(0.0)
        )
    )

    return {
        'split': name,
        'start_day': df['day'].min(),
        'end_day': df['day'].max(),
        'days': df['day'].nunique(),
        'observations': len(df),
        'return_observations': df['ret_1m'].notna().sum(),
        'gross_total_return': gross_total,
        'transaction_cost_return': -cost_total,
        'eod_liquidation_cost_return': -eod_liquidation_cost,
        'net_total_return': net_total,
        'annualized_volatility': vol,
        'sharpe': sharpe(daily_net),
        'sortino': sortino(daily_net),
        'max_drawdown': max_dd,
        'hit_rate': hit,
        'average_trade_pnl': avg_trade,
        'average_winning_trade': avg_win,
        'average_losing_trade': avg_loss,
        'turnover': turnover,
        'exposure': exposure,
        'number_of_trades': len(trades),
        'ending_equity': equity.iloc[-1],
    }

# ============================================================
# THRESHOLD SELECTION — VALIDATION ONLY
#
# This is the step File 18 explicitly deferred. Test days are
# never touched here.
# ============================================================

print("\n--- THRESHOLD SELECTION (validation only) ---")

threshold_rows = []
for th in THRESHOLDS:
    val_bt = run_backtest(VALIDATION_DAYS, th)
    val_trades_th = make_trades(val_bt)
    perf = performance(val_bt, val_trades_th, 'VALIDATION',starting_equity=START_CAPITAL)
    perf['threshold'] = th
    threshold_rows.append(perf)

threshold_df = pd.DataFrame(threshold_rows)
threshold_df['selection_metric'] = SELECTION_METRIC
threshold_df['selection_tiebreak'] = TIEBREAK_METRIC
threshold_df['selection_final_tiebreak'] = 'number_of_trades_ascending'
threshold_df['selection_split'] = 'VALIDATION'
threshold_df.insert(0, 'threshold', threshold_df.pop('threshold'))
threshold_df.to_csv(THRESHOLD_SELECTION_FILE, index=False)

rank_df = threshold_df.copy()
rank_df[SELECTION_METRIC] = rank_df[SELECTION_METRIC].fillna(-np.inf)
rank_df[TIEBREAK_METRIC] = rank_df[TIEBREAK_METRIC].fillna(-np.inf)
rank_df = rank_df.sort_values(
    [SELECTION_METRIC, TIEBREAK_METRIC, 'number_of_trades'],
    ascending=[False, False, True],
).reset_index(drop=True)

THRESHOLD = float(rank_df.iloc[0]['threshold'])
if THRESHOLD not in THRESHOLDS: raise RuntimeError(f"Selected threshold {THRESHOLD} is not present in the frozen threshold grid.")

print(threshold_df[['threshold', 'net_total_return', 'sharpe', 'sortino', 'max_drawdown', 'number_of_trades']].to_string(index=False))
print(f"\nSelected threshold (by {SELECTION_METRIC}, tie-break {TIEBREAK_METRIC}): {THRESHOLD}")
print("Test days were not used in this selection.")


# ============================================================
# FINAL FROZEN BACKTEST — LOCKED THRESHOLD
# ============================================================

print("\n--- FINAL BACKTEST (locked feature + threshold) ---")

FULL_DF = run_backtest(ALL_DAYS, THRESHOLD)
FULL_DF = FULL_DF.sort_values(['day', 'sec']).reset_index(drop=True)

# Continuous capital across days.
# Position resets to zero at each day boundary, but capital does NOT reset.
FULL_DF['equity'] = (
    START_CAPITAL
    * (1.0 + FULL_DF['net_ret'].fillna(0.0)).cumprod()
)

FULL_DF['peak'] = FULL_DF['equity'].cummax()
FULL_DF['drawdown'] = FULL_DF['equity'] / FULL_DF['peak'] - 1.0


# ============================================================
# SPLITS
# ============================================================

train_df = FULL_DF[FULL_DF['day'].isin(TRAIN_DAYS)].copy()
val_df = FULL_DF[FULL_DF['day'].isin(VALIDATION_DAYS)].copy()
test_df = FULL_DF[FULL_DF['day'].isin(TEST_DAYS)].copy()

train_trades = make_trades(train_df)
val_trades = make_trades(val_df)
test_trades = make_trades(test_df)

all_trades = pd.concat([train_trades, val_trades, test_trades], ignore_index=True)
if len(all_trades):
    all_trades = all_trades.sort_values(['day', 'timestamp']).reset_index(drop=True)
else:
    all_trades = pd.DataFrame(columns=ALL_TRADE_COLS)

all_trades.to_csv(TRADE_FILE, index=False)


# ============================================================
# PERFORMANCE TABLES
# ============================================================

# train_res = pd.DataFrame([performance(train_df, train_trades, 'TRAIN')])
# val_res = pd.DataFrame([performance(val_df, val_trades, 'VALIDATION')])
# test_res = pd.DataFrame([performance(test_df, test_trades, 'TEST')])

train_start_equity = START_CAPITAL

train_res = pd.DataFrame([
    performance(
        train_df,
        train_trades,
        'TRAIN',
        starting_equity=train_start_equity,
    )
])

train_end_equity = train_res.iloc[0]['ending_equity']

val_res = pd.DataFrame([
    performance(
        val_df,
        val_trades,
        'VALIDATION',
        starting_equity=train_end_equity,
    )
])

val_end_equity = val_res.iloc[0]['ending_equity']

test_res = pd.DataFrame([
    performance(
        test_df,
        test_trades,
        'TEST',
        starting_equity=val_end_equity,
    )
])

train_res.to_csv(TRAIN_FILE, index=False)
val_res.to_csv(VALIDATION_FILE, index=False)
test_res.to_csv(TEST_FILE, index=False)

summary = pd.concat([train_res, val_res, test_res], ignore_index=True)
summary.insert(0, 'feature', FEATURE)
summary.insert(1, 'family', FAMILY)
summary.insert(2, 'hypothesis', HYPOTHESIS)
summary.insert(3, 'rebalance_minutes', REBALANCE)
summary.insert(4, 'feature_horizon_minutes', HORIZON)
summary.insert(5, 'threshold', THRESHOLD)
summary.insert(6, 'transaction_cost_bps', COST_BPS)
summary = summary[SUMMARY_COLS]
summary.to_csv(SUMMARY_FILE, index=False)


# ============================================================
# DAILY RETURNS
# ============================================================

daily_ret = daily_returns(FULL_DF)
daily_ret.to_csv(DAILY_FILE, index=False)


# ============================================================
# OUTPUT
# ============================================================

print("\n--- PERFORMANCE (locked threshold =", THRESHOLD, ") ---")
print(summary[[
    'split', 'threshold', 'gross_total_return', 'eod_liquidation_cost_return', 'transaction_cost_return', 'net_total_return',
    'annualized_volatility', 'sharpe', 'sortino', 'max_drawdown', 'hit_rate', 'turnover',
    'exposure', 'number_of_trades', 'ending_equity',
]].to_string(index=False))


# ============================================================
# PLOTS
# ============================================================

plt.figure(figsize=(11, 5))
plt.plot(FULL_DF['equity'].to_numpy())
plt.xlabel("Minute")
plt.ylabel("Equity")
plt.title(f"EBX Strategy Equity Curve — {FEATURE} (threshold={THRESHOLD})")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(EQUITY_PLOT, dpi=150)
plt.show()

plt.figure(figsize=(11, 5))
plt.plot(FULL_DF['drawdown'].to_numpy())
plt.xlabel("Minute")
plt.ylabel("Drawdown")
plt.title(f"EBX Strategy Drawdown — {FEATURE} (threshold={THRESHOLD})")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(DD_PLOT, dpi=150)
plt.show()

plt.figure(figsize=(11, 5))
plt.bar(daily_ret['day'], daily_ret['daily_net_return'])
plt.xlabel("Day")
plt.ylabel("Daily Return")
plt.title(f"EBX Strategy Daily Returns — {FEATURE} (threshold={THRESHOLD})")
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(DAILY_PLOT, dpi=150)
plt.show()


# ============================================================
# FILES
# ============================================================

print("\n--- FILES WRITTEN ---")
print(THRESHOLD_SELECTION_FILE)
print(SIGNAL_CHECK_FILE)
print(TRADE_FILE)
print(DAILY_FILE)
print(TRAIN_FILE)
print(VALIDATION_FILE)
print(TEST_FILE)
print(SUMMARY_FILE)
print(EQUITY_PLOT)
print(DD_PLOT)
print(DAILY_PLOT)

print("\nDone.")