# ------------------------------------------------------------
# FILE 19 — BACKTEST  (fixed)
#
# This version fixes four issues found in the prior File 19,
# reconciled against File 18's ACTUAL written config. File 18
# is NOT modified; every fix here only changes how File 19
# reads/uses the contract File 18 already specifies.
#
# 1. [FATAL] Execution lag was declared by File 18
#    (execution_lag_minutes=1, lookahead_rule =
#    'feature_t -> signal_t -> execute_t+1') but File 19 never
#    read that key and formed position_t * return(t -> t+1),
#    i.e. executed at t, not t+1. That is look-ahead bias.
#    Fixed: EXECUTION_LAG is now read from config and applied
#    via a per-day shift of the raw signal before it becomes a
#    tradable position. Turnover/cost are computed on the
#    EXECUTED (lagged) position, never the raw signal.
#
# 2. [FATAL] The last minute of every day was being dropped
#    (any row without a next_price was filtered out), so the
#    "Explicit EOD close" branch in make_trades was closing at
#    the second-to-last real minute, not the true close.
#    Fixed: the true final minute of each day is now retained.
#    Its ret_1m is (correctly) undefined -- there is no forward
#    price to earn a return against -- but its Price is kept for
#    reference. Combined with fix #1, the executed position is
#    forced flat on that final minute (day-boundary reset, no
#    overnight carry), which charges the correct exit cost at
#    the correct, true closing price. This also means every
#    trade now closes naturally within its own day, so the old
#    special-cased EOD-close branch is no longer needed at all.
#
# 3. [FATAL] The validation-only signal-direction check compared
#    the raw feature against the 1-minute forward return, but
#    File 17/18 selected and signed the feature against the
#    HORIZON-minute (10-minute) forward return. Checking the
#    wrong target isn't actually verifying the relationship the
#    sign was chosen from. Fixed: the check now uses a
#    HORIZON-minute forward return computed within-day, on
#    validation days only, same as before -- never test days.
#
# 4. [HIGH] Trade-log PnL was computed from an independent
#    entry-to-exit price difference, while the equity curve
#    compounds net_ret minute by minute -- two different
#    accounting models that don't reconcile. Fixed: trade PnL is
#    now built from the same minute-level gross_ret/cost_ret
#    series used for the equity curve. Each trade's gross PnL is
#    the compounded gross return over the minutes it was
#    actually held, marked against the real running equity at
#    entry; entry/exit transaction-cost legs are attributed
#    explicitly so a reversal's combined turnover cost splits
#    correctly between the closing and opening trade without
#    double-counting.
#
# 5. get_day_number regex aligned with Files 17/18
#    (day[_\s]?(\d+) instead of day[\s]?(\d+)). (unchanged)
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

THRESHOLD_SELECTION_FILE = OUTPUT_DIR / "19_threshold_selection.csv"
TRADE_FILE = OUTPUT_DIR / "19_trade_log.csv"
DAILY_FILE = OUTPUT_DIR / "19_daily_returns.csv"

TRAIN_FILE = OUTPUT_DIR / "19_train_results.csv"
VALIDATION_FILE = OUTPUT_DIR / "19_validation_results.csv"
TEST_FILE = OUTPUT_DIR / "19_test_results.csv"
SUMMARY_FILE = OUTPUT_DIR / "19_performance_summary.csv"
SIGNAL_CHECK_FILE = OUTPUT_DIR / "19_signal_direction_check.csv"

EQUITY_PLOT = RESULTS_DIR / "19_equity_curve.png"
DD_PLOT = RESULTS_DIR / "19_drawdown.png"
DAILY_PLOT = RESULTS_DIR / "19_daily_returns.png"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)

ALL_TRADE_COLS = [
    'day', 'timestamp', 'exit_timestamp', 'side', 'entry_price', 'exit_price',
    'quantity', 'gross_pnl', 'transaction_cost', 'pnl', 'pnl_pct',
]

SUMMARY_COLS = [
    'feature', 'family', 'hypothesis', 'rebalance_minutes', 'feature_horizon_minutes',
    'execution_lag_minutes', 'threshold', 'transaction_cost_bps', 'split', 'start_day',
    'end_day', 'days', 'observations', 'gross_total_return', 'transaction_cost_return',
    'net_total_return', 'annualized_volatility', 'sharpe', 'sortino', 'max_drawdown',
    'hit_rate', 'average_trade_pnl', 'average_winning_trade', 'average_losing_trade',
    'turnover', 'exposure', 'number_of_trades', 'ending_equity',
]

ANNUAL_TRADING_DAYS = 252   # standard convention; the per-day minute count is derived from data, not assumed

# Validation-only threshold selection criterion. Primary: Sharpe.
# Ties broken by total net return, then by fewer trades (prefer simplicity).
SELECTION_METRIC = 'sharpe'
TIEBREAK_METRIC = 'net_total_return'

print("\n--- FILE 19 BACKTEST (fixed) ---")


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

# --- FIX #1: read the execution lag File 18 actually froze. ---
EXECUTION_LAG = int(float(cfg('execution_lag_minutes', required=True)))

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

EXPECTED_DAYS = list(range(1, 65)) + list(range(80, 86))
ALL_DAYS = TRAIN_DAYS + VALIDATION_DAYS + TEST_DAYS


# ============================================================
# CONFIGURATION VALIDATION
# ============================================================

if not FEATURE or FEATURE == 'nan':
    raise ValueError("Invalid frozen feature")
if REBALANCE != 1:
    raise ValueError("File 19 expects frozen 1-minute execution")
if EXECUTION_LAG < 0:
    raise ValueError("execution_lag_minutes must be non-negative")
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
print("Horizon       :", f"{HORIZON} minutes (predictive target, NOT holding period)")
print("Execution lag :", f"{EXECUTION_LAG} minute(s) — signal_t executes at t+{EXECUTION_LAG}")
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
#
# FIX #2: the true final minute of each day is now RETAINED
# (previously dropped because it has no next_price). Its
# ret_1m is legitimately undefined -- there's no forward price
# to earn a return against -- but its Price/Time stay available
# for EOD-close accounting. We also compute a HORIZON-minute
# forward return here, used only by the validation-only signal-
# direction check (never by the trading logic).
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

    # Keep every minute, including the last. next_price/ret_1m are
    # legitimately NaN on the final row of the day -- that's a fact
    # about the data (no forward price exists), not something to filter.
    df['next_price'] = df['Price'].shift(-1)
    df['next_sec'] = df['sec'].shift(-1)
    df['next_time'] = df['Time'].shift(-1)
    df['ret_1m'] = df['next_price'] / df['Price'] - 1.0

    df['is_last_minute'] = df['sec'] == df['sec'].max()

    # Horizon-minute forward return, within-day only, for the
    # validation-only signal-direction check (fix #3). Not used
    # anywhere in the trading/execution logic.
    df['ret_horizon'] = df['Price'].shift(-HORIZON) / df['Price'] - 1.0

    df['z'] = ((df[FEATURE] - TRAIN_MEAN) / TRAIN_STD) * SIGNAL_DIRECTION

    # A usable feature/z is required at every row we keep; this can
    # legitimately drop the last row too if the feature itself is
    # missing there, which is fine and independent of the ret_1m fix.
    df = df[np.isfinite(df['z'])].copy()
    df['is_last_minute'] = df['sec'] == df['sec'].max()

    return df[[
        'day', 'Time', 'sec', 'Price', 'next_time', 'next_sec', FEATURE,
        'z', 'ret_1m', 'ret_horizon', 'is_last_minute',
    ]].reset_index(drop=True)


print("\n--- BUILDING MINUTE TIMELINE ---")

day_data = {}
for d in sorted(day_files):
    df = load_day(day_files[d], d)
    day_data[d] = df
    print(f"Day {d:>2}: {len(df):>5} minute observations | {df['Time'].iloc[0]} -> {df['Time'].iloc[-1]}")

print("\nTotal days loaded:", len(day_data))

# ------------------------------------------------------------
# Derive annualization from the data actually loaded, instead
# of assuming a US-equity 390-minute session.
# ------------------------------------------------------------

obs_per_day = pd.Series({d: len(df) for d, df in day_data.items()})
MINUTES_PER_DAY = int(obs_per_day.median())
ANNUAL_MINUTES = ANNUAL_TRADING_DAYS * MINUTES_PER_DAY

print(
    f"\nObservations per day — median: {MINUTES_PER_DAY}, "
    f"min: {int(obs_per_day.min())}, max: {int(obs_per_day.max())}"
)
if obs_per_day.min() != obs_per_day.max():
    print("NOTE: minute counts vary across days — annualization uses the median day length.")
print(f"Annualization basis: {ANNUAL_TRADING_DAYS} trading days x {MINUTES_PER_DAY} minutes/day = {ANNUAL_MINUTES} periods/year")


# ============================================================
# SIGNAL DIRECTION CHECK (validation days only, never test)
#
# FIX #3: checked against the HORIZON-minute forward return --
# the same target File 17/18 used to select and sign the
# feature -- instead of the 1-minute return.
# ============================================================

val_check = pd.concat([day_data[d] for d in VALIDATION_DAYS], ignore_index=True)
raw_feature = val_check['z'] * SIGNAL_DIRECTION * TRAIN_STD + TRAIN_MEAN   # undo z-scoring + direction to recover raw feature

val_check_h = val_check[['sec']].assign(raw_feature=raw_feature, ret_horizon=val_check['ret_horizon'])
val_check_h = val_check_h.dropna(subset=['raw_feature', 'ret_horizon'])

check_corr = val_check_h['raw_feature'].corr(val_check_h['ret_horizon'], method='spearman')

signal_check = pd.DataFrame([{
    'validation_days': f"{VALIDATION_DAYS[0]}-{VALIDATION_DAYS[-1]}",
    'horizon_minutes': HORIZON,
    'observations': len(val_check_h),
    'raw_feature_vs_ret_horizon_spearman': check_corr,
    'configured_signal_direction': SIGNAL_DIRECTION,
    'validation_sign_agrees_with_config': bool(np.sign(check_corr) == np.sign(SIGNAL_DIRECTION)) if np.isfinite(check_corr) else None,
}])
signal_check.to_csv(SIGNAL_CHECK_FILE, index=False)

print("\n--- SIGNAL DIRECTION CHECK (validation only, horizon-matched) ---")
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
#
# FIX #1: the raw signal formed from z_t is shifted by
# EXECUTION_LAG (per day, no cross-day leakage) before it
# becomes a tradable, cost-bearing position. Turnover/cost use
# the EXECUTED position, never the raw signal.
#
# FIX #2: the position is forced flat on the true final minute
# of the day (day-boundary reset / no overnight carry), using
# the real closing price now that it's retained. This charges
# the correct exit cost at the correct price and guarantees
# every trade closes within its own day -- no special-cased EOD
# branch needed downstream.
# ============================================================

def run_backtest(days, threshold):

    rows = []

    for d in days:
        df = day_data[d].copy()

        raw_position = np.where(
            df['z'] > threshold, MAX_EXPOSURE,
            np.where(df['z'] < -threshold, -MAX_EXPOSURE, 0.0),
        )
        df['raw_position'] = raw_position

        # feature_t -> signal_t -> execute_{t+EXECUTION_LAG}. First
        # EXECUTION_LAG rows of the day have no prior signal to execute
        # -> flat, consistent with the day-boundary reset rule.
        df['position'] = pd.Series(raw_position, index=df.index).shift(EXECUTION_LAG).fillna(0.0)

        # No overnight carry: force flat on the day's true final minute.
        df.loc[df['is_last_minute'], 'position'] = 0.0

        df['prev_position'] = df['position'].shift(1).fillna(0.0)
        df['turnover'] = (df['position'] - df['prev_position']).abs()

        ret = df['ret_1m'].fillna(0.0)   # only NaN on the forced-flat final minute, where position is 0 anyway
        df['gross_ret'] = df['position'] * ret
        df['cost_ret'] = df['turnover'] * COST
        df['net_ret'] = df['gross_ret'] - df['cost_ret']
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
    return x.mean() / sd * np.sqrt(ANNUAL_MINUTES)


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
    return x.mean() / ds * np.sqrt(ANNUAL_MINUTES)


def make_trades(df):
    """
    FIX #4: trade PnL is now derived from the same minute-level
    gross_ret series used for the equity curve, marked against the
    real running equity at entry, instead of an independent
    entry-to-exit price difference. Entry/exit transaction-cost legs
    are attributed explicitly so a reversal's combined turnover cost
    splits correctly between the closing and opening trade without
    double-counting (cost_ret at a reversal row already reflects
    BOTH legs; charging the full row cost to both trades would
    double it).

    Also folds in fix #2: because run_backtest() now forces the
    position flat on the true final minute of each day, every
    nonzero segment is guaranteed to close within its own day, so
    no separate "explicit EOD close" branch is needed.
    """

    if len(df) == 0:
        return pd.DataFrame(columns=ALL_TRADE_COLS)

    trades = []

    for d, g in df.groupby('day', sort=True):

        g = g.sort_values('sec').reset_index(drop=True)

        pos = g['position'].to_numpy()
        tm = g['Time'].to_numpy()
        px = g['Price'].to_numpy()
        gross = g['gross_ret'].to_numpy()

        # Running equity within the day, and the equity level just
        # BEFORE each row's return is applied (the correct entry/exit
        # mark for that row).
        equity_after = START_CAPITAL * np.cumprod(1.0 + g['net_ret'].to_numpy())
        equity_before = np.empty_like(equity_after)
        equity_before[0] = START_CAPITAL
        equity_before[1:] = equity_after[:-1]

        n = len(g)
        i = 0
        while i < n:
            if pos[i] == 0.0:
                i += 1
                continue

            i0 = i
            seg_val = pos[i0]
            j = i0 + 1
            while j < n and pos[j] == seg_val:
                j += 1
            # segment held over rows i0 .. j-1; position changes at row j
            # (guaranteed to exist within the day, since the last row is
            # always forced flat).

            entry_equity = equity_before[i0]
            growth = np.prod(1.0 + gross[i0:j])
            gross_pnl = entry_equity * (growth - 1.0)

            # Entry leg: this trade's own share of the turnover cost at i0.
            # (If i0 is a reversal row, the OTHER leg of that row's combined
            # turnover cost belongs to the trade that just closed, handled
            # as its own exit leg below -- so nothing is double-charged.)
            entry_leg_cost = entry_equity * abs(seg_val) * COST

            exit_equity = equity_before[j] if j < n else equity_after[j - 1]
            exit_leg_cost = exit_equity * abs(seg_val) * COST

            net_pnl = gross_pnl - entry_leg_cost - exit_leg_cost
            transaction_cost = entry_leg_cost + exit_leg_cost

            side = 'LONG' if seg_val > 0 else 'SHORT'
            entry_price = px[i0]
            exit_price = px[j] if j < n else px[-1]
            quantity = entry_equity * abs(seg_val) / entry_price

            trades.append({
                'day': d,
                'timestamp': tm[i0],
                'exit_timestamp': tm[j] if j < n else tm[-1],
                'side': side,
                'entry_price': entry_price,
                'exit_price': exit_price,
                'quantity': quantity,
                'gross_pnl': gross_pnl,
                'transaction_cost': transaction_cost,
                'pnl': net_pnl,
                'pnl_pct': net_pnl / entry_equity,
            })

            i = j

    if not trades:
        return pd.DataFrame(columns=ALL_TRADE_COLS)

    return pd.DataFrame(trades)[ALL_TRADE_COLS]


def performance(df, trades, name):

    x = df['net_ret'].replace([np.inf, -np.inf], np.nan).dropna()

    if len(x):
        gross_total = np.prod(1.0 + df['gross_ret']) - 1.0
        cost_total = np.prod(1.0 - df['cost_ret']) - 1.0
        net_total = np.prod(1.0 + df['net_ret']) - 1.0
        equity = START_CAPITAL * (1.0 + df['net_ret']).cumprod()
        peak = equity.cummax()
        dd = equity / peak - 1.0
        max_dd = dd.min()
    else:
        gross_total = cost_total = net_total = np.nan
        equity = pd.Series(dtype=float)
        max_dd = np.nan

    vol = x.std(ddof=1) * np.sqrt(ANNUAL_MINUTES) if len(x) > 1 else np.nan
    exposure = df['position'].abs().mean() if len(df) else np.nan
    turnover = df['turnover'].sum() if len(df) else 0.0

    if len(trades):
        wins = trades[trades['pnl'] > 0]
        losses = trades[trades['pnl'] < 0]
        hit = len(wins) / len(trades)
        avg_trade = trades['pnl'].mean()
        avg_win = wins['pnl'].mean() if len(wins) else np.nan
        avg_loss = losses['pnl'].mean() if len(losses) else np.nan
    else:
        hit = avg_trade = avg_win = avg_loss = np.nan

    return {
        'split': name,
        'start_day': df['day'].min() if len(df) else np.nan,
        'end_day': df['day'].max() if len(df) else np.nan,
        'days': df['day'].nunique(),
        'observations': len(df),
        'gross_total_return': gross_total,
        'transaction_cost_return': cost_total,
        'net_total_return': net_total,
        'annualized_volatility': vol,
        'sharpe': sharpe(x),
        'sortino': sortino(x),
        'max_drawdown': max_dd,
        'hit_rate': hit,
        'average_trade_pnl': avg_trade,
        'average_winning_trade': avg_win,
        'average_losing_trade': avg_loss,
        'turnover': turnover,
        'exposure': exposure,
        'number_of_trades': len(trades),
        'ending_equity': equity.iloc[-1] if len(equity) else np.nan,
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
    perf = performance(val_bt, val_trades_th, 'VALIDATION')
    perf['threshold'] = th
    threshold_rows.append(perf)

threshold_df = pd.DataFrame(threshold_rows)
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

print(threshold_df[['threshold', 'net_total_return', 'sharpe', 'sortino', 'max_drawdown', 'number_of_trades']].to_string(index=False))
print(f"\nSelected threshold (by {SELECTION_METRIC}, tie-break {TIEBREAK_METRIC}): {THRESHOLD}")
print("Test days were not used in this selection.")


# ============================================================
# FINAL FROZEN BACKTEST — LOCKED THRESHOLD
# ============================================================

print("\n--- FINAL BACKTEST (locked feature + threshold) ---")

FULL_DF = run_backtest(ALL_DAYS, THRESHOLD)
FULL_DF = FULL_DF.sort_values(['day', 'sec']).reset_index(drop=True)

FULL_DF['equity'] = START_CAPITAL * (1.0 + FULL_DF['net_ret']).cumprod()
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
# RECONCILIATION CHECK (new) — trade log vs equity curve
#
# With fix #4, sum(trade pnl) should now track the split's net
# total return in currency terms far more closely than the old
# price-difference model. This is printed as a diagnostic, not
# enforced with a hard raise, since minor drift from forced-flat
# rows with zero notional is expected to be exactly zero, not
# an error tolerance judgment call.
# ============================================================

def reconciliation(df, trades, name):
    if len(df) == 0:
        return
    net_total = np.prod(1.0 + df['net_ret']) - 1.0
    equity_pnl = START_CAPITAL * net_total
    trade_pnl_sum = trades['pnl'].sum() if len(trades) else 0.0
    diff = trade_pnl_sum - equity_pnl
    print(
        f"{name:>10} | equity net PnL: {equity_pnl:>14,.2f} | "
        f"trade log PnL sum: {trade_pnl_sum:>14,.2f} | diff: {diff:>10,.2f}"
    )


print("\n--- TRADE LOG / EQUITY RECONCILIATION ---")
reconciliation(train_df, train_trades, 'TRAIN')
reconciliation(val_df, val_trades, 'VALIDATION')
reconciliation(test_df, test_trades, 'TEST')


# ============================================================
# PERFORMANCE TABLES
# ============================================================

train_res = pd.DataFrame([performance(train_df, train_trades, 'TRAIN')])
val_res = pd.DataFrame([performance(val_df, val_trades, 'VALIDATION')])
test_res = pd.DataFrame([performance(test_df, test_trades, 'TEST')])

train_res.to_csv(TRAIN_FILE, index=False)
val_res.to_csv(VALIDATION_FILE, index=False)
test_res.to_csv(TEST_FILE, index=False)

summary = pd.concat([train_res, val_res, test_res], ignore_index=True)
summary.insert(0, 'feature', FEATURE)
summary.insert(1, 'family', FAMILY)
summary.insert(2, 'hypothesis', HYPOTHESIS)
summary.insert(3, 'rebalance_minutes', REBALANCE)
summary.insert(4, 'feature_horizon_minutes', HORIZON)
summary.insert(5, 'execution_lag_minutes', EXECUTION_LAG)
summary.insert(6, 'threshold', THRESHOLD)
summary.insert(7, 'transaction_cost_bps', COST_BPS)
summary = summary[SUMMARY_COLS]
summary.to_csv(SUMMARY_FILE, index=False)


# ============================================================
# DAILY RETURNS
# ============================================================

daily_ret = (
    FULL_DF.groupby('day')
    .agg(
        daily_gross_return=('gross_ret', lambda x: np.prod(1.0 + x) - 1.0),
        daily_cost_return=('cost_ret', lambda x: np.prod(1.0 - x) - 1.0),
        daily_net_return=('net_ret', lambda x: np.prod(1.0 + x) - 1.0),
    )
    .reset_index()
)
daily_ret.to_csv(DAILY_FILE, index=False)


# ============================================================
# OUTPUT
# ============================================================

print("\n--- PERFORMANCE (locked threshold =", THRESHOLD, ") ---")
print(summary[[
    'split', 'threshold', 'gross_total_return', 'transaction_cost_return', 'net_total_return',
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