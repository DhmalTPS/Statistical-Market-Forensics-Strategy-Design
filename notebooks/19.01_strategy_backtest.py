from pathlib import Path
import re
import ast
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def get_day_number(file):
    res = re.search(r'day[\s]?(\d+)',file.stem,re.IGNORECASE)
    return int(res.group(1)) if res else None


def parse_days(x):
    if pd.isna(x):
        return []

    s = str(x).strip()

    try:
        y = ast.literal_eval(s)

        if isinstance(y,(list,tuple,np.ndarray)):
            return [int(v) for v in y]

    except (ValueError,SyntaxError):
        pass

    return [
        int(v.strip())
        for v in s.strip('[]').split(',')
        if str(v).strip()
    ]


DATA_DIR = Path(r'.\EBX_Dataset')
OUTPUT_DIR = Path(r'.\output')
RESULTS_DIR = Path(r'.\results')

CONFIG_FILE = OUTPUT_DIR / "18_strategy_config.csv"

TRADE_FILE = OUTPUT_DIR / "19_trade_log.csv"
DAILY_FILE = OUTPUT_DIR / "19_daily_returns.csv"

TRAIN_FILE = OUTPUT_DIR / "19_train_results.csv"
VALIDATION_FILE = OUTPUT_DIR / "19_validation_results.csv"
TEST_FILE = OUTPUT_DIR / "19_test_results.csv"
SUMMARY_FILE = OUTPUT_DIR / "19_performance_summary.csv"

EQUITY_PLOT = RESULTS_DIR / "19_equity_curve.png"
DD_PLOT = RESULTS_DIR / "19_drawdown.png"
DAILY_PLOT = RESULTS_DIR / "19_daily_returns.png"

RESULTS_DIR.mkdir(parents=True,exist_ok=True)

ALL_TRADE_COLS = [
    'day',
    'timestamp',
    'exit_timestamp',
    'side',
    'entry_price',
    'exit_price',
    'quantity',
    'gross_pnl',
    'transaction_cost',
    'pnl',
    'pnl_pct'
]

SUMMARY_COLS = [
    'feature',
    'family',
    'hypothesis',
    'rebalance_minutes',
    'feature_horizon_minutes',
    'threshold',
    'transaction_cost_bps',
    'split',
    'start_day',
    'end_day',
    'days',
    'observations',
    'gross_total_return',
    'transaction_cost_return',
    'net_total_return',
    'annualized_volatility',
    'sharpe',
    'sortino',
    'max_drawdown',
    'hit_rate',
    'average_trade_pnl',
    'average_winning_trade',
    'average_losing_trade',
    'turnover',
    'exposure',
    'number_of_trades',
    'ending_equity'
]

print("\n--- TASK 5 BACKTEST ---")


# ============================================================
# FROZEN STRATEGY CONFIGURATION
# ============================================================

config_df = pd.read_csv(CONFIG_FILE)

if not {'parameter','value'}.issubset(config_df.columns):
    raise ValueError(
        "Invalid 18_strategy_config.csv: expected "
        "'parameter' and 'value' columns"
    )

CONFIG = dict(
    zip(
        config_df['parameter'].astype(str),
        config_df['value']
    )
)


def cfg(name,default=None):
    return CONFIG[name] if name in CONFIG else default


FEATURE = str(cfg('feature')).strip()
FAMILY = str(cfg('family')).strip()
HYPOTHESIS = str(cfg('forensic_hypothesis')).strip()

REBALANCE = int(float(cfg('rebalance_minutes',1)))
HORIZON = int(float(cfg('feature_horizon',10)))

SIGNAL_DIRECTION = int(float(cfg('signal_direction',1)))

TRAIN_MEAN = float(cfg('train_mean'))
TRAIN_STD = float(cfg('train_std'))

# File 19 executes the threshold frozen by File 18.
# No threshold selection happens here.
THRESHOLD_RAW = cfg(
    'selected_threshold',
    cfg('threshold',None)
)

if THRESHOLD_RAW is None:
    raise ValueError(
        "File 18 must provide a frozen "
        "'selected_threshold' (or 'threshold')"
    )

THRESHOLD = float(THRESHOLD_RAW)

MAX_EXPOSURE = float(cfg('max_exposure',1.0))

COST_BPS = float(
    cfg('transaction_cost_bps',7.5)
)

COST = COST_BPS / 10000.0

TRAIN_DAYS = parse_days(
    cfg('train_days')
)

VALIDATION_DAYS = parse_days(
    cfg('validation_days')
)

TEST_DAYS = parse_days(
    cfg('test_days')
)

START_CAPITAL = 1_000_000.0

# EBX one-minute convention used for annualized statistics.
ANNUAL_MINUTES = 252 * 390

EXPECTED_DAYS = (
    list(range(1,65))
    +
    list(range(80,86))
)

ALL_DAYS = (
    TRAIN_DAYS
    +
    VALIDATION_DAYS
    +
    TEST_DAYS
)


# ============================================================
# CONFIGURATION VALIDATION
# ============================================================

if not FEATURE or FEATURE == 'nan':
    raise ValueError("Invalid frozen feature")

if REBALANCE != 1:
    raise ValueError(
        "File 19 expects frozen 1-minute execution"
    )

if TRAIN_STD <= 0 or not np.isfinite(TRAIN_STD):
    raise ValueError(
        "Invalid frozen training standard deviation"
    )

if not np.isfinite(THRESHOLD) or THRESHOLD < 0:
    raise ValueError(
        "Invalid frozen threshold"
    )

if SIGNAL_DIRECTION not in (-1,1):
    raise ValueError(
        "signal_direction must be either -1 or 1"
    )

if MAX_EXPOSURE <= 0:
    raise ValueError(
        "max_exposure must be positive"
    )

if COST_BPS < 0:
    raise ValueError(
        "transaction cost cannot be negative"
    )

if (
    len(ALL_DAYS) != 70
    or len(set(ALL_DAYS)) != 70
):
    raise ValueError(
        "Invalid 70-day strategy universe"
    )

if set(ALL_DAYS) != set(EXPECTED_DAYS):
    raise ValueError(
        "Strategy universe must be "
        "Days 1-64 and 80-85"
    )

if set(TRAIN_DAYS) & set(VALIDATION_DAYS):
    raise ValueError(
        "Train/validation overlap"
    )

if set(TRAIN_DAYS) & set(TEST_DAYS):
    raise ValueError(
        "Train/test overlap"
    )

if set(VALIDATION_DAYS) & set(TEST_DAYS):
    raise ValueError(
        "Validation/test overlap"
    )

if (
    len(TRAIN_DAYS)
    + len(VALIDATION_DAYS)
    + len(TEST_DAYS)
) != 70:
    raise ValueError(
        "Train/validation/test days do not "
        "cover all 70 strategy days"
    )


print("\nFrozen strategy:")

print("Feature       :",FEATURE)
print("Family        :",FAMILY)
print("Hypothesis    :",HYPOTHESIS)
print("Rebalance     :",f"{REBALANCE} minute")
print("Horizon       :",f"{HORIZON} minutes")
print("Direction     :",SIGNAL_DIRECTION)
print("Train mean    :",TRAIN_MEAN)
print("Train std     :",TRAIN_STD)
print("Threshold     :",THRESHOLD)
print("Cost          :",COST_BPS,"bps")
print("Max exposure  :",MAX_EXPOSURE)
print("Start capital :",START_CAPITAL)

print("\nTrain       :",TRAIN_DAYS)
print("Validation  :",VALIDATION_DAYS)
print("Test        :",TEST_DAYS)


# ============================================================
# DATA FILES
# ============================================================

csv_files = sorted(
    DATA_DIR.glob("*.csv"),
    key=lambda f: (
        get_day_number(f)
        if get_day_number(f) is not None
        else 10**9
    )
)

day_files = {
    get_day_number(f): f
    for f in csv_files
    if get_day_number(f) in ALL_DAYS
}

if len(day_files) != 70:
    raise ValueError(
        f"Expected 70 usable files, "
        f"found {len(day_files)}"
    )

missing_days = sorted(
    set(ALL_DAYS) - set(day_files)
)

if missing_days:
    raise ValueError(
        f"Missing dataset files for days: "
        f"{missing_days}"
    )


# ============================================================
# FEATURE / TIMELINE
# ============================================================

def load_day(f,d):

    head = pd.read_csv(
        f,
        nrows=1
    )

    cols = head.columns.tolist()

    if FEATURE not in cols:
        raise ValueError(
            f"Day {d}: frozen feature '{FEATURE}' "
            f"is not a raw dataset column.\n"
            f"File 19 cannot safely reconstruct this "
            f"feature without the exact feature definition "
            f"used by File 18."
        )

    df = pd.read_csv(
        f,
        usecols=['Time','Price',FEATURE]
    )

    df['Price'] = pd.to_numeric(
        df['Price'],
        errors='coerce'
    )

    df[FEATURE] = pd.to_numeric(
        df[FEATURE],
        errors='coerce'
    )

    df = df.replace(
        [np.inf,-np.inf],
        np.nan
    )

    df['Time'] = (
        df['Time']
        .astype(str)
        .str.strip()
    )

    # Parse HH:MM:SS without depending on
    # string slicing for continuity checks.
    td = pd.to_timedelta(
        df['Time'],
        errors='coerce'
    )

    df['sec'] = (
        td.dt.total_seconds()
        .astype('float64')
    )

    df = df[
        df['Price'].notna()
        &
        df[FEATURE].notna()
        &
        df['Price'].gt(0)
        &
        df['sec'].notna()
        &
        ((df['sec'] % 60) == 0)
    ].copy()

    if len(df) == 0:
        raise ValueError(
            f"Day {d}: no valid 1-minute observations"
        )

    # One row per minute is required.
    dup = df['sec'].duplicated().sum()

    if dup:
        raise ValueError(
            f"Day {d}: {dup} duplicate minute timestamps"
        )

    df = df.sort_values(
        'sec'
    ).reset_index(drop=True)

    # Verify that the minute series is actually consecutive.
    diff = np.diff(
        df['sec'].to_numpy()
    )

    bad = diff[
        ~np.isclose(diff,60.0)
    ]

    if len(bad):
        raise ValueError(
            f"Day {d}: non-contiguous minute timeline "
            f"detected ({len(bad)} gaps)"
        )

    df['day'] = d

    df['next_price'] = (
        df['Price'].shift(-1)
    )

    df['next_sec'] = (
        df['sec'].shift(-1)
    )

    df['next_time'] = (
        df['Time'].shift(-1)
    )

    df['ret_1m'] = (
        df['next_price']
        /
        df['Price']
        - 1.0
    )

    # The final minute has no t -> t+1 observation.
    df = df[
        df['next_price'].notna()
        &
        df['next_sec'].notna()
        &
        np.isfinite(df['ret_1m'])
    ].copy()

    df['z'] = (
        (
            df[FEATURE]
            -
            TRAIN_MEAN
        )
        /
        TRAIN_STD
    ) * SIGNAL_DIRECTION

    df = df[
        np.isfinite(df['z'])
    ].copy()

    return df[
        [
            'day',
            'Time',
            'sec',
            'Price',
            'next_time',
            'next_sec',
            FEATURE,
            'z',
            'ret_1m'
        ]
    ].reset_index(drop=True)


print("\n--- BUILDING MINUTE TIMELINE ---")

day_data = {}

for d in sorted(day_files):

    df = load_day(
        day_files[d],
        d
    )

    day_data[d] = df

    print(
        f"Day {d:>2}: "
        f"{len(df):>5} minute observations | "
        f"{df['Time'].iloc[0]} -> "
        f"{df['next_time'].iloc[-1]}"
    )

print("\nTotal days loaded:",len(day_data))


# ============================================================
# SIGNAL / POSITION
# ============================================================

def run_backtest(days):

    rows = []

    for d in days:

        df = day_data[d].copy()

        df['position'] = np.where(
            df['z'] > THRESHOLD,
            MAX_EXPOSURE,
            np.where(
                df['z'] < -THRESHOLD,
                -MAX_EXPOSURE,
                0.0
            )
        )

        df['prev_position'] = (
            df['position']
            .shift(1)
            .fillna(0.0)
        )

        df['turnover'] = (
            df['position']
            -
            df['prev_position']
        ).abs()

        df['gross_ret'] = (
            df['position']
            *
            df['ret_1m']
        )

        df['cost_ret'] = (
            df['turnover']
            *
            COST
        )

        df['net_ret'] = (
            df['gross_ret']
            -
            df['cost_ret']
        )

        df['threshold'] = THRESHOLD

        rows.append(df)

    return pd.concat(
        rows,
        ignore_index=True
    )


# ============================================================
# PERFORMANCE
# ============================================================

def sharpe(x):

    x = pd.Series(x).replace(
        [np.inf,-np.inf],
        np.nan
    ).dropna()

    if len(x) < 2:
        return np.nan

    sd = x.std(ddof=1)

    if not np.isfinite(sd) or sd == 0:
        return np.nan

    return (
        x.mean()
        /
        sd
        *
        np.sqrt(ANNUAL_MINUTES)
    )


def sortino(x):

    x = pd.Series(x).replace(
        [np.inf,-np.inf],
        np.nan
    ).dropna()

    if len(x) < 2:
        return np.nan

    dn = x[x < 0]

    if len(dn) == 0:
        return (
            np.inf
            if x.mean() > 0
            else 0.0
        )

    ds = np.sqrt(
        np.mean(dn ** 2)
    )

    if ds == 0:
        return (
            np.inf
            if x.mean() > 0
            else 0.0
        )

    return (
        x.mean()
        /
        ds
        *
        np.sqrt(ANNUAL_MINUTES)
    )


def make_trades(df):

    if len(df) == 0:
        return pd.DataFrame(
            columns=ALL_TRADE_COLS
        )

    trades = []

    for d,g in df.groupby(
        'day',
        sort=True
    ):

        g = (
            g.sort_values('sec')
            .reset_index(drop=True)
        )

        pos = g['position'].to_numpy()
        tm = g['Time'].to_numpy()
        px = g['Price'].to_numpy()

        active = 0.0
        et = None
        ep = None

        # Equity before each minute's return.
        eq = START_CAPITAL

        for i in range(len(g)):

            cur = pos[i]

            if active == 0 and cur != 0:

                active = cur
                et = tm[i]
                ep = px[i]
                entry_equity = eq

            elif active != 0 and cur != active:

                xt = tm[i]
                xp = px[i]

                side = (
                    'LONG'
                    if active > 0
                    else 'SHORT'
                )

                qty = (
                    entry_equity
                    *
                    abs(active)
                    /
                    ep
                )

                gpnl = qty * (
                    xp - ep
                )

                if active < 0:
                    gpnl = -gpnl

                # Entry + exit costs.
                tc = (
                    entry_equity
                    *
                    abs(active)
                    *
                    COST
                    +
                    entry_equity
                    *
                    abs(active)
                    *
                    COST
                )

                # For a reversal, the current signal is
                # both the exit and the new entry.
                if cur != 0:
                    tc = (
                        entry_equity
                        *
                        abs(active)
                        *
                        COST
                        +
                        entry_equity
                        *
                        abs(cur)
                        *
                        COST
                    )

                pnl = gpnl - tc

                trades.append({
                    'day':d,
                    'timestamp':et,
                    'exit_timestamp':xt,
                    'side':side,
                    'entry_price':ep,
                    'exit_price':xp,
                    'quantity':qty,
                    'gross_pnl':gpnl,
                    'transaction_cost':tc,
                    'pnl':pnl,
                    'pnl_pct':(
                        gpnl / entry_equity
                        -
                        tc / entry_equity
                    )
                })

                active = 0.0
                et = None
                ep = None

                if cur != 0:
                    active = cur
                    et = tm[i]
                    ep = px[i]
                    entry_equity = eq

            # Apply this minute's portfolio return
            # after the signal has been established.
            eq *= (
                1.0
                +
                g['net_ret'].iloc[i]
            )

        # Explicit EOD close.
        if active != 0 and ep is not None:

            xt = tm[-1]
            xp = px[-1]

            side = (
                'LONG'
                if active > 0
                else 'SHORT'
            )

            qty = (
                entry_equity
                *
                abs(active)
                /
                ep
            )

            gpnl = qty * (
                xp - ep
            )

            if active < 0:
                gpnl = -gpnl

            tc = (
                entry_equity
                *
                abs(active)
                *
                COST
                +
                entry_equity
                *
                abs(active)
                *
                COST
            )

            pnl = gpnl - tc

            trades.append({
                'day':d,
                'timestamp':et,
                'exit_timestamp':xt,
                'side':side,
                'entry_price':ep,
                'exit_price':xp,
                'quantity':qty,
                'gross_pnl':gpnl,
                'transaction_cost':tc,
                'pnl':pnl,
                'pnl_pct':(
                    gpnl / entry_equity
                    -
                    tc / entry_equity
                )
            })

    if not trades:
        return pd.DataFrame(
            columns=ALL_TRADE_COLS
        )

    return pd.DataFrame(
        trades
    )[
        ALL_TRADE_COLS
    ]


def performance(df,trades,name):

    x = df['net_ret'].replace(
        [np.inf,-np.inf],
        np.nan
    ).dropna()

    if len(x):

        gross_total = (
            np.prod(
                1.0
                +
                df['gross_ret']
            )
            - 1.0
        )

        cost_total = (
            np.prod(
                1.0
                -
                df['cost_ret']
            )
            - 1.0
        )

        net_total = (
            np.prod(
                1.0
                +
                df['net_ret']
            )
            - 1.0
        )

        equity = (
            START_CAPITAL
            *
            (
                1.0
                +
                df['net_ret']
            ).cumprod()
        )

        peak = equity.cummax()

        dd = (
            equity
            /
            peak
            - 1.0
        )

        max_dd = dd.min()

    else:

        gross_total = np.nan
        cost_total = np.nan
        net_total = np.nan

        equity = pd.Series(
            dtype=float
        )

        max_dd = np.nan

    if len(x) > 1:

        vol = (
            x.std(ddof=1)
            *
            np.sqrt(ANNUAL_MINUTES)
        )

    else:
        vol = np.nan

    exposure = (
        df['position'].abs().mean()
        if len(df)
        else np.nan
    )

    turnover = (
        df['turnover'].sum()
        if len(df)
        else 0.0
    )

    if len(trades):

        wins = trades[
            trades['pnl'] > 0
        ]

        losses = trades[
            trades['pnl'] < 0
        ]

        hit = (
            len(wins)
            /
            len(trades)
        )

        avg_trade = trades['pnl'].mean()

        avg_win = (
            wins['pnl'].mean()
            if len(wins)
            else np.nan
        )

        avg_loss = (
            losses['pnl'].mean()
            if len(losses)
            else np.nan
        )

    else:

        hit = np.nan
        avg_trade = np.nan
        avg_win = np.nan
        avg_loss = np.nan

    return {
        'split':name,
        'start_day':(
            df['day'].min()
            if len(df)
            else np.nan
        ),
        'end_day':(
            df['day'].max()
            if len(df)
            else np.nan
        ),
        'days':df['day'].nunique(),
        'observations':len(df),
        'gross_total_return':gross_total,
        'transaction_cost_return':cost_total,
        'net_total_return':net_total,
        'annualized_volatility':vol,
        'sharpe':sharpe(x),
        'sortino':sortino(x),
        'max_drawdown':max_dd,
        'hit_rate':hit,
        'average_trade_pnl':avg_trade,
        'average_winning_trade':avg_win,
        'average_losing_trade':avg_loss,
        'turnover':turnover,
        'exposure':exposure,
        'number_of_trades':len(trades),
        'ending_equity':(
            equity.iloc[-1]
            if len(equity)
            else np.nan
        )
    }


# ============================================================
# FINAL FROZEN BACKTEST
# ============================================================

print("\n--- FINAL BACKTEST ---")

FULL_DF = run_backtest(
    ALL_DAYS
)

FULL_DF = (
    FULL_DF
    .sort_values(['day','sec'])
    .reset_index(drop=True)
)

FULL_DF['equity'] = (
    START_CAPITAL
    *
    (
        1.0
        +
        FULL_DF['net_ret']
    ).cumprod()
)

FULL_DF['peak'] = (
    FULL_DF['equity']
    .cummax()
)

FULL_DF['drawdown'] = (
    FULL_DF['equity']
    /
    FULL_DF['peak']
    -
    1.0
)


# ============================================================
# SPLITS
# ============================================================

train_df = FULL_DF[
    FULL_DF['day'].isin(TRAIN_DAYS)
].copy()

val_df = FULL_DF[
    FULL_DF['day'].isin(VALIDATION_DAYS)
].copy()

test_df = FULL_DF[
    FULL_DF['day'].isin(TEST_DAYS)
].copy()

train_trades = make_trades(
    train_df
)

val_trades = make_trades(
    val_df
)

test_trades = make_trades(
    test_df
)

all_trades = pd.concat(
    [
        train_trades,
        val_trades,
        test_trades
    ],
    ignore_index=True
)

if len(all_trades):

    all_trades = (
        all_trades
        .sort_values(
            ['day','timestamp']
        )
        .reset_index(drop=True)
    )

else:

    all_trades = pd.DataFrame(
        columns=ALL_TRADE_COLS
    )

all_trades.to_csv(
    TRADE_FILE,
    index=False
)


# ============================================================
# PERFORMANCE TABLES
# ============================================================

train_res = pd.DataFrame([
    performance(
        train_df,
        train_trades,
        'TRAIN'
    )
])

val_res = pd.DataFrame([
    performance(
        val_df,
        val_trades,
        'VALIDATION'
    )
])

test_res = pd.DataFrame([
    performance(
        test_df,
        test_trades,
        'TEST'
    )
])

train_res.to_csv(
    TRAIN_FILE,
    index=False
)

val_res.to_csv(
    VALIDATION_FILE,
    index=False
)

test_res.to_csv(
    TEST_FILE,
    index=False
)

summary = pd.concat(
    [
        train_res,
        val_res,
        test_res
    ],
    ignore_index=True
)

summary.insert(
    0,
    'feature',
    FEATURE
)

summary.insert(
    1,
    'family',
    FAMILY
)

summary.insert(
    2,
    'hypothesis',
    HYPOTHESIS
)

summary.insert(
    3,
    'rebalance_minutes',
    REBALANCE
)

summary.insert(
    4,
    'feature_horizon_minutes',
    HORIZON
)

summary.insert(
    5,
    'threshold',
    THRESHOLD
)

summary.insert(
    6,
    'transaction_cost_bps',
    COST_BPS
)

summary = summary[
    SUMMARY_COLS
]

summary.to_csv(
    SUMMARY_FILE,
    index=False
)


# ============================================================
# DAILY RETURNS
# ============================================================

daily_ret = (
    FULL_DF
    .groupby('day')
    .agg(
        daily_gross_return=(
            'gross_ret',
            lambda x:
            np.prod(1.0+x)-1.0
        ),
        daily_cost_return=(
            'cost_ret',
            lambda x:
            np.prod(1.0-x)-1.0
        ),
        daily_net_return=(
            'net_ret',
            lambda x:
            np.prod(1.0+x)-1.0
        )
    )
    .reset_index()
)

daily_ret.to_csv(
    DAILY_FILE,
    index=False
)


# ============================================================
# OUTPUT
# ============================================================

print("\n--- PERFORMANCE ---")

print(
    summary[
        [
            'split',
            'threshold',
            'gross_total_return',
            'transaction_cost_return',
            'net_total_return',
            'annualized_volatility',
            'sharpe',
            'sortino',
            'max_drawdown',
            'hit_rate',
            'turnover',
            'exposure',
            'number_of_trades',
            'ending_equity'
        ]
    ].to_string(index=False)
)


# ============================================================
# EQUITY CURVE
# ============================================================

print("\n--- EQUITY CURVE ---")

plt.figure(figsize=(11,5))

plt.plot(
    FULL_DF['equity'].to_numpy()
)

plt.xlabel("Minute")
plt.ylabel("Equity")

plt.title(
    f"EBX Strategy Equity Curve — {FEATURE}"
)

plt.grid(alpha=0.3)

plt.tight_layout()

plt.savefig(
    EQUITY_PLOT,
    dpi=150
)

plt.show()


# ============================================================
# DRAWDOWN
# ============================================================

print("\n--- DRAWDOWN ---")

plt.figure(figsize=(11,5))

plt.plot(
    FULL_DF['drawdown'].to_numpy()
)

plt.xlabel("Minute")
plt.ylabel("Drawdown")

plt.title(
    f"EBX Strategy Drawdown — {FEATURE}"
)

plt.grid(alpha=0.3)

plt.tight_layout()

plt.savefig(
    DD_PLOT,
    dpi=150
)

plt.show()


# ============================================================
# DAILY RETURNS
# ============================================================

print("\n--- DAILY RETURNS ---")

plt.figure(figsize=(11,5))

plt.bar(
    daily_ret['day'],
    daily_ret['daily_net_return']
)

plt.xlabel("Day")
plt.ylabel("Daily Return")

plt.title(
    f"EBX Strategy Daily Returns — {FEATURE}"
)

plt.grid(
    axis='y',
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    DAILY_PLOT,
    dpi=150
)

plt.show()


# ============================================================
# FILES
# ============================================================

print("\n--- FILES WRITTEN ---")

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