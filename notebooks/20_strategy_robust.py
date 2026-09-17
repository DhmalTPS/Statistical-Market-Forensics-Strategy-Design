
# ------------------------------------------------------------
# FILE 20 — STRATEGY ROBUSTNESS
#
# Purpose:
#   Stress the frozen File-18 / File-19 strategy without
#   redefining, re-optimizing, or refitting it.
#
# Pipeline:
#
#   18_strategy_design
#           ↓
#   frozen strategy configuration
#           ↓
#   19_strategy_backtest
#           ↓
#   validation-selected threshold
#           ↓
#   20_strategy_robustness
#
# IMPORTANT:
#   File 20 is NOT a parameter optimizer.
#
#   It only measures how the already-selected strategy behaves
#   under reasonable perturbations.
#
# Robustness axes:
#
#   20A — threshold robustness
#   20B — transaction-cost robustness
#   20C — rebalance-frequency robustness
#   20D — combined baseline / stability diagnostics
#
# Frozen strategy contract:
#
#   - Feature comes from File 18.
#   - Feature direction comes from File 18.
#   - TRAIN mean/std come from File 18.
#   - Threshold is selected by File 19 using VALIDATION only.
#   - TEST is report-only.
#   - No overnight position carry.
#   - Position resets to zero at every day boundary.
#
# Execution convention:
#
#   feature_t
#       ↓
#   signal / position_t
#       ↓
#   return over the next strategy interval
#
# This preserves File 19's existing accounting convention:
#
#   gross_ret = position_t * forward_price_return
#
# Frequency robustness changes the execution interval, NOT the
# predictive feature horizon.
#
# Accounting:
#
#   Gross wealth:
#       W_gross,t = W_{t-1} * (1 + gross_ret_t)
#
#   Transaction-cost wealth:
#       W_after_tc,t =
#           W_gross,t * (1 - transaction_cost_rate_t)
#
#   EOD liquidation:
#       W_final =
#           W_after_tc,t * (1 - eod_liquidation_rate_t)
#
# The authoritative portfolio return is therefore:
#
#   net_ret_t = W_t / W_{t-1} - 1
#
# Every cumulative performance statistic is derived from this
# same net wealth stream.
#
# No separate, incompatible "cost return" stream is used to
# define portfolio performance.
# ------------------------------------------------------------

from pathlib import Path
import re
import ast

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# HELPERS
# ============================================================

def get_day_number(file):
    res = re.search(
        r"day[_\s]?(\d+)",
        file.stem,
        re.IGNORECASE
    )
    return int(res.group(1)) if res else None


def parse_days(x):
    """
    Strictly parse a File-18 day-list configuration.

    Accepted:
        [1, 2, 3]
        (1, 2, 3)
        1,2,3

    Invalid values raise rather than being silently reinterpreted.
    """
    if pd.isna(x):
        raise ValueError("Day-list configuration is missing")

    if isinstance(x, (list, tuple, np.ndarray)):
        values = list(x)
    else:
        s = str(x).strip()

        if not s:
            raise ValueError(
                "Day-list configuration is empty"
            )

        try:
            parsed = ast.literal_eval(s)

            if isinstance(parsed, (list, tuple, np.ndarray)):
                values = list(parsed)
            elif isinstance(parsed, (int, float, np.integer, np.floating)):
                values = [parsed]
            else:
                raise ValueError
        except (ValueError, SyntaxError):
            s = s.strip("[]()")
            values = [
                v.strip()
                for v in s.split(",")
                if v.strip()
            ]

    days = []

    for v in values:
        try:
            fv = float(v)
        except (TypeError, ValueError):
            raise ValueError(
                f"Invalid day value in configuration: {v!r}"
            )

        if not np.isfinite(fv) or fv != int(fv):
            raise ValueError(
                f"Day value must be an integer: {v!r}"
            )

        days.append(int(fv))

    if not days:
        raise ValueError(
            "Day-list configuration parsed to an empty list"
        )

    if len(set(days)) != len(days):
        raise ValueError(
            f"Duplicate days in configuration: {days}"
        )

    return days


def finite_series(x):
    return (
        pd.Series(x)
        .replace([np.inf, -np.inf], np.nan)
        .dropna()
    )


def safe_total_return(x):
    x = finite_series(x)

    if len(x) == 0:
        return np.nan

    if np.any(1.0 + x <= 0):
        return np.nan

    return np.prod(1.0 + x) - 1.0


def safe_cost_return(cost_rate):
    """
    Report the cumulative wealth reduction caused by a cost stream.

    This is descriptive only.

    Portfolio performance itself is always derived from net_ret.
    """
    x = finite_series(cost_rate)

    if len(x) == 0:
        return np.nan

    if np.any((1.0 - x) <= 0):
        return np.nan

    return 1.0 - np.prod(1.0 - x)


def sharpe(x, periods_per_year):
    x = finite_series(x)

    if len(x) < 2:
        return np.nan

    sd = x.std(ddof=1)

    if not np.isfinite(sd) or sd == 0:
        return np.nan

    return (
        x.mean()
        / sd
        * np.sqrt(periods_per_year)
    )


def sortino(x, periods_per_year):
    x = finite_series(x)

    if len(x) < 2:
        return np.nan

    downside = x[x < 0]

    if len(downside) == 0:
        return (
            np.inf
            if x.mean() > 0
            else 0.0
        )

    downside_dev = np.sqrt(
        np.mean(downside ** 2)
    )

    if downside_dev == 0:
        return (
            np.inf
            if x.mean() > 0
            else 0.0
        )

    return (
        x.mean()
        / downside_dev
        * np.sqrt(periods_per_year)
    )


def max_drawdown(x):
    x = finite_series(x)

    if len(x) == 0:
        return np.nan

    if np.any(1.0 + x <= 0):
        return np.nan

    equity = (
        1.0
        * (1.0 + x).cumprod()
    )

    peak = equity.cummax()

    dd = (
        equity / peak
        - 1.0
    )

    return dd.min()


# ============================================================
# PATHS
# ============================================================

DATA_DIR = Path(r".\EBX_Dataset")
OUTPUT_DIR = Path(r".\output")
RESULTS_DIR = Path(r".\results")

CONFIG_FILE = (
    OUTPUT_DIR
    / "18_strategy_config.csv"
)

THRESHOLD_SELECTION_FILE = (
    OUTPUT_DIR
    / "19_threshold_selection.csv"
)

BASELINE_SUMMARY_FILE = (
    OUTPUT_DIR
    / "19_performance_summary.csv"
)

ROBUSTNESS_FILE = (
    OUTPUT_DIR
    / "20_robustness.csv"
)

ROBUSTNESS_SUMMARY_FILE = (
    OUTPUT_DIR
    / "20_robustness_summary.csv"
)

THRESHOLD_PLOT = (
    RESULTS_DIR
    / "20_threshold_robustness.png"
)

COST_PLOT = (
    RESULTS_DIR
    / "20_cost_robustness.png"
)

FREQUENCY_PLOT = (
    RESULTS_DIR
    / "20_frequency_robustness.png"
)

ROBUSTNESS_PLOT = (
    RESULTS_DIR
    / "20_robustness_summary.png"
)

RESULTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# ROBUSTNESS GRID
#
# These are sensitivity values, NOT optimization candidates.
# ============================================================

THRESHOLD_GRID_DEFAULT = [
    0.50,
    0.75,
    1.00,
    1.25,
    1.50,
]

COST_GRID_BPS = [
    5.0,
    7.5,
    10.0,
]

FREQUENCY_GRID = [
    1,
    5,
]


# ============================================================
# LOAD FILE-18 CONFIGURATION
# ============================================================

if not CONFIG_FILE.exists():
    raise FileNotFoundError(
        f"{CONFIG_FILE} not found. "
        "Run File 18 before File 20."
    )

config_df = pd.read_csv(CONFIG_FILE)

if not {
    "parameter",
    "value"
}.issubset(config_df.columns):

    raise ValueError(
        "Invalid 18_strategy_config.csv: expected "
        "'parameter' and 'value' columns"
    )


CONFIG = dict(
    zip(
        config_df["parameter"].astype(str),
        config_df["value"]
    )
)


def cfg(
    name,
    default=None,
    required=False
):
    if name in CONFIG:
        return CONFIG[name]

    if required:
        raise ValueError(
            "18_strategy_config.csv is missing "
            f"required key '{name}'"
        )

    return default


# ============================================================
# FROZEN STRATEGY PARAMETERS
# ============================================================

FEATURE = str(
    cfg(
        "feature",
        required=True
    )
).strip()

FAMILY = str(
    cfg(
        "family",
        ""
    )
).strip()

HYPOTHESIS = str(
    cfg(
        "forensic_hypothesis",
        ""
    )
).strip()

BASE_REBALANCE = int(
    float(
        cfg(
            "rebalance_minutes",
            1
        )
    )
)

HORIZON = int(
    float(
        cfg(
            "feature_horizon",
            10
        )
    )
)

SIGNAL_DIRECTION = int(
    float(
        cfg(
            "signal_direction",
            1
        )
    )
)

TRAIN_MEAN = float(
    cfg(
        "train_mean",
        required=True
    )
)

TRAIN_STD = float(
    cfg(
        "train_std",
        required=True
    )
)

MAX_EXPOSURE = float(
    cfg(
        "max_exposure",
        1.0
    )
)

BASE_COST_BPS = float(
    cfg(
        "transaction_cost_bps",
        7.5
    )
)

BASE_COST = (
    BASE_COST_BPS
    / 10000.0
)


# ============================================================
# CONTRACT VALIDATION — FILE 18
# ============================================================

if not FEATURE or FEATURE.lower() == "nan":
    raise ValueError(
        "Invalid frozen feature"
    )

if BASE_REBALANCE != 1:
    raise ValueError(
        "File 20 expects the File-18 baseline "
        "rebalance frequency to be exactly 1 minute."
    )

if not np.isfinite(TRAIN_MEAN):
    raise ValueError(
        "Invalid File-18 train_mean"
    )

if (
    not np.isfinite(TRAIN_STD)
    or TRAIN_STD <= 0
):
    raise ValueError(
        "Invalid File-18 train_std"
    )

if SIGNAL_DIRECTION not in (-1, 1):
    raise ValueError(
        "signal_direction must be either -1 or +1"
    )

if (
    not np.isfinite(MAX_EXPOSURE)
    or MAX_EXPOSURE <= 0
):
    raise ValueError(
        "max_exposure must be positive"
    )

if (
    not np.isfinite(BASE_COST_BPS)
    or BASE_COST_BPS < 0
):
    raise ValueError(
        "transaction_cost_bps must be non-negative"
    )


# ============================================================
# THRESHOLD GRID FROM FILE 18
# ============================================================

THRESHOLDS_RAW = cfg(
    "thresholds",
    ""
)

if str(THRESHOLDS_RAW).strip():

    THRESHOLDS = [
        float(t.strip())
        for t in str(
            THRESHOLDS_RAW
        ).split(",")
        if t.strip()
    ]

else:
    THRESHOLDS = (
        THRESHOLD_GRID_DEFAULT.copy()
    )


if not THRESHOLDS:
    raise ValueError(
        "File-18 threshold grid is empty"
    )

if any(
    not np.isfinite(t)
    or t < 0
    for t in THRESHOLDS
):
    raise ValueError(
        "File-18 threshold grid contains "
        "invalid values"
    )

if len(
    set(
        np.round(
            THRESHOLDS,
            12
        )
    )
) != len(THRESHOLDS):
    raise ValueError(
        "File-18 threshold grid contains duplicates"
    )


# ============================================================
# FILE-18 THRESHOLD-SELECTION CONTRACT
# ============================================================

threshold_selection_mode = str(
    cfg(
        "threshold_selection",
        ""
    )
).strip().upper()

if (
    threshold_selection_mode
    and threshold_selection_mode
    != "VALIDATION_ONLY"
):
    raise ValueError(
        "File-18 threshold_selection is not "
        "VALIDATION_ONLY."
    )


# ============================================================
# DAY SPLITS — EXACTLY FROM FILE 18
# ============================================================

TRAIN_START = int(
    float(
        cfg(
            "train_start",
            required=True
        )
    )
)

TRAIN_END = int(
    float(
        cfg(
            "train_end",
            required=True
        )
    )
)

VALIDATION_START = int(
    float(
        cfg(
            "validation_start",
            required=True
        )
    )
)

VALIDATION_END = int(
    float(
        cfg(
            "validation_end",
            required=True
        )
    )
)

TRAIN_DAYS = list(
    range(
        TRAIN_START,
        TRAIN_END + 1
    )
)

VALIDATION_DAYS = list(
    range(
        VALIDATION_START,
        VALIDATION_END + 1
    )
)

TEST_DAYS = parse_days(
    cfg(
        "test_days",
        required=True
    )
)

DISCOVERY_DAYS = parse_days(
    cfg(
        "discovery_days",
        required=True
    )
)

EXPECTED_DAYS = (
    list(range(1, 65))
    + list(range(80, 86))
)

ALL_DAYS = (
    TRAIN_DAYS
    + VALIDATION_DAYS
    + TEST_DAYS
)


# ============================================================
# SPLIT CONTRACT VALIDATION
# ============================================================

if (
    sorted(
        TRAIN_DAYS
        + VALIDATION_DAYS
    )
    !=
    sorted(DISCOVERY_DAYS)
):
    raise ValueError(
        "File-18 discovery_days does not match "
        "TRAIN_DAYS + VALIDATION_DAYS."
    )

if len(ALL_DAYS) != 70:
    raise ValueError(
        "Strategy universe must contain exactly "
        "70 days."
    )

if len(set(ALL_DAYS)) != 70:
    raise ValueError(
        "Duplicate days in strategy universe."
    )

if set(ALL_DAYS) != set(EXPECTED_DAYS):
    raise ValueError(
        "Strategy universe must be exactly "
        "Days 1-64 and 80-85."
    )

if set(TRAIN_DAYS) & set(VALIDATION_DAYS):
    raise ValueError(
        "TRAIN / VALIDATION overlap."
    )

if set(TRAIN_DAYS) & set(TEST_DAYS):
    raise ValueError(
        "TRAIN / TEST overlap."
    )

if set(VALIDATION_DAYS) & set(TEST_DAYS):
    raise ValueError(
        "VALIDATION / TEST overlap."
    )


# ============================================================
# LOAD THE ACTUAL FILE-19 SELECTED THRESHOLD
#
# IMPORTANT:
#
# File 20 does NOT reconstruct File 19's ranking rule.
#
# File 19 owns selection.
#
# We first look for an explicit selected-threshold field.
# If the existing File-19 file does not contain one, we use
# its current schema only as a compatibility bridge and verify
# that the resulting value belongs to File 18's frozen grid.
#
# This fallback is deliberately isolated here so that File 20
# does not otherwise reproduce File 19's optimization logic.
# ============================================================

if not THRESHOLD_SELECTION_FILE.exists():
    raise FileNotFoundError(
        f"{THRESHOLD_SELECTION_FILE} not found. "
        "Run File 19 before File 20."
    )

threshold_selection = pd.read_csv(
    THRESHOLD_SELECTION_FILE
)

SELECTED_THRESHOLD = None

# ------------------------------------------------------------
# Preferred explicit File-19 handoff.
# ------------------------------------------------------------

for col in [
    "selected_threshold",
    "selected_threshold_value",
]:

    if col in threshold_selection.columns:

        vals = pd.to_numeric(
            threshold_selection[col],
            errors="coerce"
        ).dropna().unique()

        if len(vals) != 1:
            raise ValueError(
                f"File 19 column '{col}' must contain "
                "exactly one unique selected threshold."
            )

        SELECTED_THRESHOLD = float(vals[0])
        break


# ------------------------------------------------------------
# Compatibility bridge for the current File-19 output.
#
# Current File 19 writes one row per candidate and does not
# explicitly persist the winner in the CSV itself. The current
# File-19 selection contract is validation-only Sharpe, then
# net return, then fewer trades. We reproduce this ONLY to
# recover the already-selected File-19 result from its existing
# output schema.
#
# This is NOT a new File-20 optimization axis.
# ------------------------------------------------------------

if SELECTED_THRESHOLD is None:

    required_cols = {
        "threshold",
        "sharpe",
        "net_total_return",
        "number_of_trades",
    }

    if not required_cols.issubset(
        threshold_selection.columns
    ):
        raise ValueError(
            "19_threshold_selection.csv does not contain "
            "an explicit selected threshold and does not "
            "contain the current File-19 selection output "
            "columns."
        )

    selection_df = (
        threshold_selection.copy()
    )

    for c in [
        "threshold",
        "sharpe",
        "net_total_return",
        "number_of_trades",
    ]:
        selection_df[c] = pd.to_numeric(
            selection_df[c],
            errors="coerce"
        )

    selection_df = selection_df[
        selection_df["threshold"].notna()
    ].copy()

    if len(selection_df) == 0:
        raise ValueError(
            "File-19 threshold selection file contains "
            "no usable threshold rows."
        )

    # Current File-19 contract:
    #   Sharpe
    #   → net total return
    #   → fewer trades
    selection_df["_rank_sharpe"] = (
        selection_df["sharpe"]
        .fillna(-np.inf)
    )

    selection_df["_rank_return"] = (
        selection_df["net_total_return"]
        .fillna(-np.inf)
    )

    selection_df["_rank_trades"] = (
        selection_df["number_of_trades"]
        .fillna(np.inf)
    )

    selection_df = selection_df.sort_values(
        [
            "_rank_sharpe",
            "_rank_return",
            "_rank_trades",
        ],
        ascending=[
            False,
            False,
            True,
        ]
    ).reset_index(drop=True)

    SELECTED_THRESHOLD = float(
        selection_df.iloc[0]["threshold"]
    )


if (
    SELECTED_THRESHOLD is None
    or not np.isfinite(SELECTED_THRESHOLD)
):
    raise ValueError(
        "File 19 did not provide a valid selected threshold."
    )


# ============================================================
# SELECTED THRESHOLD MUST BELONG TO FILE-18 GRID
# ============================================================

if not any(
    np.isclose(
        SELECTED_THRESHOLD,
        t,
        rtol=0.0,
        atol=1e-10
    )
    for t in THRESHOLDS
):
    raise ValueError(
        "File-19 selected threshold "
        f"{SELECTED_THRESHOLD} is not present in the "
        "frozen File-18 threshold grid."
    )


# ============================================================
# ROBUSTNESS GRID MUST CONTAIN BASELINE
# ============================================================

def contains_close(values, target):
    return any(
        np.isclose(
            float(v),
            float(target),
            rtol=0.0,
            atol=1e-10
        )
        for v in values
    )


if not contains_close(
    THRESHOLDS,
    SELECTED_THRESHOLD
):
    raise ValueError(
        "Robustness threshold grid does not contain "
        "the selected File-19 threshold."
    )

if not contains_close(
    COST_GRID_BPS,
    BASE_COST_BPS
):
    raise ValueError(
        "Cost robustness grid does not contain "
        "the frozen File-18 baseline cost."
    )

if BASE_REBALANCE not in FREQUENCY_GRID:
    raise ValueError(
        "Frequency robustness grid does not contain "
        "the frozen File-18 baseline frequency."
    )


# ============================================================
# REPORT CONFIGURATION
# ============================================================

print(
    "\n--- FILE 20: STRATEGY ROBUSTNESS ---"
)

print("\nFrozen strategy")
print("Feature       :", FEATURE)
print("Family        :", FAMILY)
print("Hypothesis    :", HYPOTHESIS)
print(
    "Baseline freq :",
    f"{BASE_REBALANCE} minute"
)
print(
    "Horizon       :",
    f"{HORIZON} predictive minutes"
)
print(
    "Direction     :",
    SIGNAL_DIRECTION
)
print(
    "Train mean    :",
    TRAIN_MEAN
)
print(
    "Train std     :",
    TRAIN_STD
)
print(
    "Baseline cost :",
    BASE_COST_BPS,
    "bps"
)
print(
    "Selected th   :",
    SELECTED_THRESHOLD
)
print(
    "Thresholds    :",
    THRESHOLDS
)

print(
    "\nTrain         :",
    TRAIN_DAYS[0],
    "-",
    TRAIN_DAYS[-1]
)

print(
    "Validation    :",
    VALIDATION_DAYS[0],
    "-",
    VALIDATION_DAYS[-1]
)

print(
    "Test          :",
    TEST_DAYS
)

print("\nRobustness grids")
print(
    "Thresholds    :",
    THRESHOLDS
)
print(
    "Costs         :",
    COST_GRID_BPS
)
print(
    "Frequencies   :",
    FREQUENCY_GRID
)


# ============================================================
# DATA FILES
# ============================================================

if not DATA_DIR.exists():
    raise FileNotFoundError(
        DATA_DIR
    )

csv_files = sorted(
    DATA_DIR.glob("*.csv"),
    key=lambda f:
        get_day_number(f)
        if get_day_number(f) is not None
        else 10**9
)

day_files = {
    get_day_number(f): f
    for f in csv_files
    if get_day_number(f) in ALL_DAYS
}

if len(day_files) != 70:
    raise ValueError(
        f"Expected 70 usable files, "
        f"found {len(day_files)}."
    )

missing_days = sorted(
    set(ALL_DAYS)
    - set(day_files)
)

if missing_days:
    raise ValueError(
        "Missing dataset files for days: "
        f"{missing_days}"
    )


# ============================================================
# LOAD ONE DAY
#
# Only raw feature + price + time are required.
#
# Normalization:
#
#   z_t =
#       direction *
#       (feature_t - TRAIN_MEAN)
#       / TRAIN_STD
#
# TRAIN statistics are never recomputed.
# ============================================================

def load_day(file, day):

    head = pd.read_csv(
        file,
        nrows=1
    )

    cols = head.columns.tolist()

    required = {
        "Time",
        "Price",
        FEATURE,
    }

    missing = required - set(cols)

    if missing:
        raise ValueError(
            f"Day {day}: missing required columns "
            f"{sorted(missing)}"
        )

    df = pd.read_csv(
        file,
        usecols=[
            "Time",
            "Price",
            FEATURE,
        ]
    )

    df["Price"] = pd.to_numeric(
        df["Price"],
        errors="coerce"
    )

    df[FEATURE] = pd.to_numeric(
        df[FEATURE],
        errors="coerce"
    )

    df = df.replace(
        [np.inf, -np.inf],
        np.nan
    )

    df["Time"] = (
        df["Time"]
        .astype(str)
        .str.strip()
    )

    td = pd.to_timedelta(
        df["Time"],
        errors="coerce"
    )

    df["sec"] = (
        td.dt.total_seconds()
        .astype("float64")
    )

    df = df[
        df["Price"].notna()
        & df[FEATURE].notna()
        & df["Price"].gt(0)
        & df["sec"].notna()
    ].copy()

    if len(df) == 0:
        raise ValueError(
            f"Day {day}: no valid observations."
        )

    if (
        df["sec"]
        .duplicated()
        .any()
    ):
        dup = int(
            df["sec"].duplicated().sum()
        )

        raise ValueError(
            f"Day {day}: {dup} duplicate timestamps."
        )

    df = (
        df
        .sort_values("sec")
        .reset_index(drop=True)
    )

    if not df["sec"].is_monotonic_increasing:
        raise ValueError(
            f"Day {day}: timestamps are not strictly increasing."
        )

    df["day"] = day

    # --------------------------------------------------------
    # Frozen TRAIN-only normalization.
    # --------------------------------------------------------

    df["z"] = (
        (
            df[FEATURE]
            - TRAIN_MEAN
        )
        / TRAIN_STD
    ) * SIGNAL_DIRECTION

    df = df[
        np.isfinite(df["z"])
    ].copy()

    if len(df) < 2:
        raise ValueError(
            f"Day {day}: insufficient valid observations "
            "after normalization."
        )

    # --------------------------------------------------------
    # Timestamp diagnostics.
    #
    # The dataset is expected to be approximately 1-second
    # sampled, but File 20 does not fabricate missing seconds.
    # --------------------------------------------------------

    diffs = (
        df["sec"]
        .diff()
        .dropna()
        .to_numpy()
    )

    if len(diffs):
        if np.any(diffs <= 0):
            raise ValueError(
                f"Day {day}: non-positive timestamp gap detected."
            )

    df["minute_index"] = (
        np.floor(
            df["sec"] / 60.0
        ).astype(np.int64)
    )

    return df[
        [
            "day",
            "Time",
            "sec",
            "Price",
            FEATURE,
            "z",
            "minute_index",
        ]
    ].reset_index(drop=True)


# ============================================================
# LOAD ALL DAYS
# ============================================================

print(
    "\n--- LOADING DATA ---"
)

day_data = {}

for d in sorted(day_files):

    df = load_day(
        day_files[d],
        d
    )

    day_data[d] = df

    print(
        f"Day {d:>2}: "
        f"{len(df):>5} observations | "
        f"{df['Time'].iloc[0]} -> "
        f"{df['Time'].iloc[-1]}"
    )

print(
    "\nTotal days loaded:",
    len(day_data)
)


# ============================================================
# MINUTE-TIMELINE CONSTRUCTION
#
# We do NOT use:
#
#     iloc[::frequency]
#
# because that means "every N rows", not "every N minutes".
#
# Instead:
#
#   1. identify actual minute timestamps;
#   2. use elapsed time in seconds;
#   3. construct the strategy timeline from timestamps.
#
# The actual last observation of the day is retained separately
# so EOD liquidation is charged at the true EOD boundary.
# ============================================================

def build_minute_timeline(df, frequency_minutes):

    if frequency_minutes < 1:
        raise ValueError(
            "frequency_minutes must be >= 1"
        )

    raw = df.sort_values(
        "sec"
    ).reset_index(drop=True)

    # --------------------------------------------------------
    # Minute observations.
    #
    # We identify the first available observation in each
    # elapsed-minute bucket rather than requiring perfect
    # second-level completeness.
    #
    # This avoids inventing prices when seconds are missing.
    # --------------------------------------------------------

    minute_bucket = (
        np.floor(
            raw["sec"].to_numpy()
            / 60.0
        ).astype(np.int64)
    )

    raw = raw.copy()

    raw["_minute_bucket"] = (
        minute_bucket
    )

    minute = (
        raw
        .sort_values(
            [
                "_minute_bucket",
                "sec",
            ]
        )
        .drop_duplicates(
            "_minute_bucket",
            keep="first"
        )
        .drop(columns="_minute_bucket")
        .reset_index(drop=True)
    )

    if len(minute) < 2:
        return (
            pd.DataFrame(),
            raw.iloc[-1:].copy()
        )

    # --------------------------------------------------------
    # Actual elapsed minute spacing.
    #
    # The first minute observation becomes the strategy anchor.
    #
    # frequency = 1:
    #     every available minute
    #
    # frequency = 5:
    #     timestamps approximately 5 minutes apart according
    #     to elapsed time, not row count.
    #
    # A timestamp is accepted only when its elapsed time from
    # the previous accepted strategy point reaches the requested
    # frequency.
    # --------------------------------------------------------

    selected_idx = [0]

    last_sec = float(
        minute.loc[0, "sec"]
    )

    target_gap = (
        frequency_minutes
        * 60.0
    )

    for i in range(
        1,
        len(minute)
    ):

        current_sec = float(
            minute.loc[i, "sec"]
        )

        if (
            current_sec
            - last_sec
            >= target_gap
        ):

            selected_idx.append(i)

            last_sec = current_sec

    strategy = (
        minute
        .iloc[selected_idx]
        .copy()
        .reset_index(drop=True)
    )

    return (
        strategy,
        raw.iloc[-1:].copy()
    )


# ============================================================
# POSITION RULE
# ============================================================

def make_position(
    z,
    threshold
):

    return np.where(
        z > threshold,
        MAX_EXPOSURE,
        np.where(
            z < -threshold,
            -MAX_EXPOSURE,
            0.0
        )
    )


# ============================================================
# CENTRAL SCENARIO ENGINE
#
# Accounting convention:
#
#   position_t
#       *
#   price return from strategy timestamp t
#       to next strategy timestamp
#
# This is consistent with File 19's actual backtest convention.
#
# EOD:
#
#   The last strategy position is carried from its last sampled
#   timestamp to the actual final market observation.
#
#   Then the position is liquidated at EOD.
#
#   No additional EOD holding-period return is created after the
#   final market observation.
# ============================================================

def run_scenario(
    days,
    threshold,
    cost_bps,
    frequency_minutes
):

    scenario_rows = []

    cost_rate = (
        float(cost_bps)
        / 10000.0
    )

    for d in days:

        raw = day_data[d]

        strategy, eod_row = (
            build_minute_timeline(
                raw,
                frequency_minutes
            )
        )

        if len(strategy) == 0:
            continue

        if len(strategy) < 1:
            continue

        # ----------------------------------------------------
        # Signals / positions at strategy timestamps.
        # ----------------------------------------------------

        strategy["position"] = (
            make_position(
                strategy["z"].to_numpy(),
                threshold
            )
        )

        # ----------------------------------------------------
        # Turnover:
        #
        # Day starts flat.
        #
        # Therefore first strategy position is traded from zero.
        # ----------------------------------------------------

        strategy["prev_position"] = (
            strategy["position"]
            .shift(1)
            .fillna(0.0)
        )

        strategy["turnover"] = (
            strategy["position"]
            - strategy["prev_position"]
        ).abs()

        # ----------------------------------------------------
        # Every ordinary strategy interval ends at the next
        # strategy timestamp.
        # ----------------------------------------------------

        strategy["next_sec"] = (
            strategy["sec"]
            .shift(-1)
        )

        strategy["next_time"] = (
            strategy["Time"]
            .shift(-1)
        )

        strategy["next_price"] = (
            strategy["Price"]
            .shift(-1)
        )

        # ----------------------------------------------------
        # Only observations with a real next strategy point
        # create ordinary portfolio intervals.
        # ----------------------------------------------------

        ordinary = strategy[
            strategy["next_sec"].notna()
            & strategy["next_price"].notna()
        ].copy()

        # ----------------------------------------------------
        # Actual EOD row.
        #
        # The last strategy timestamp may be earlier than the
        # actual final market observation, especially for 5m.
        #
        # Therefore the last position must earn the actual
        # last-segment return before EOD liquidation.
        # ----------------------------------------------------

        actual_eod_sec = float(
            eod_row["sec"].iloc[0]
        )

        actual_eod_price = float(
            eod_row["Price"].iloc[0]
        )

        actual_eod_time = str(
            eod_row["Time"].iloc[0]
        )

        # ----------------------------------------------------
        # Build the authoritative interval stream.
        # ----------------------------------------------------

        rows = []

        # ----------------------------------------------------
        # Ordinary strategy intervals.
        # ----------------------------------------------------

        for _, r in ordinary.iterrows():

            p0 = float(
                r["Price"]
            )

            p1 = float(
                r["next_price"]
            )

            if (
                not np.isfinite(p0)
                or not np.isfinite(p1)
                or p0 <= 0
                or p1 <= 0
            ):
                continue

            future_return = (
                p1 / p0
                - 1.0
            )

            position = float(
                r["position"]
            )

            turnover = float(
                r["turnover"]
            )

            transaction_cost_rate = (
                turnover
                * cost_rate
            )

            gross_growth = (
                1.0
                + position
                * future_return
            )

            if gross_growth <= 0:
                raise ValueError(
                    f"Day {d}: non-positive gross wealth "
                    "factor encountered."
                )

            # ------------------------------------------------
            # AUTHORITATIVE PORTFOLIO ACCOUNTING
            #
            # Gross wealth factor:
            #       1 + gross_ret
            #
            # Transaction-cost factor:
            #       1 - cost
            #
            # Net wealth factor:
            #       gross_factor * cost_factor
            # ------------------------------------------------

            net_growth = (
                gross_growth
                * (
                    1.0
                    - transaction_cost_rate
                )
            )

            if net_growth <= 0:
                raise ValueError(
                    f"Day {d}: non-positive net wealth factor."
                )

            net_ret = (
                net_growth
                - 1.0
            )

            rows.append({
                "day": d,
                "Time": r["Time"],
                "sec": float(r["sec"]),
                "Price": p0,
                "next_time": r["next_time"],
                "next_sec": float(r["next_sec"]),
                "next_price": p1,
                "future_return": future_return,
                FEATURE: float(r[FEATURE]),
                "z": float(r["z"]),
                "position": position,
                "prev_position": float(
                    r["prev_position"]
                ),
                "turnover": turnover,
                "gross_ret": (
                    position
                    * future_return
                ),
                "transaction_cost_rate": (
                    transaction_cost_rate
                ),
                "transaction_cost_ret": (
                    transaction_cost_rate
                ),
                "eod_liquidation_cost_rate": 0.0,
                "net_ret": net_ret,
                "interval_type": "STRATEGY",
            })

        # ----------------------------------------------------
        # EOD completion.
        #
        # If the final strategy point is before actual EOD,
        # carry its frozen position to the final observed price.
        #
        # If it is already the final observation, no extra
        # holding-period return is created.
        # ----------------------------------------------------

        if len(strategy) > 0:

            last_strategy = strategy.iloc[-1]

            last_strategy_sec = float(
                last_strategy["sec"]
            )

            last_strategy_price = float(
                last_strategy["Price"]
            )

            last_position = float(
                last_strategy["position"]
            )

            last_turnover = 0.0

            # ------------------------------------------------
            # The last strategy point has already had its
            # entry/rebalance cost represented by its turnover
            # on the ordinary interval stream.
            #
            # Therefore EOD itself is only the liquidation leg.
            # ------------------------------------------------

            if (
                actual_eod_sec
                > last_strategy_sec
                and last_strategy_price > 0
                and actual_eod_price > 0
            ):

                eod_future_return = (
                    actual_eod_price
                    / last_strategy_price
                    - 1.0
                )

                gross_ret = (
                    last_position
                    * eod_future_return
                )

                # No new rebalance cost here.
                #
                # The position remains unchanged until EOD.
                transaction_cost_rate = 0.0

                eod_liquidation_rate = (
                    abs(last_position)
                    * cost_rate
                )

                gross_growth = (
                    1.0
                    + gross_ret
                )

                if gross_growth <= 0:
                    raise ValueError(
                        f"Day {d}: non-positive EOD gross "
                        "wealth factor."
                    )

                net_growth = (
                    gross_growth
                    * (
                        1.0
                        - eod_liquidation_rate
                    )
                )

                if net_growth <= 0:
                    raise ValueError(
                        f"Day {d}: non-positive EOD net "
                        "wealth factor."
                    )

                net_ret = (
                    net_growth
                    - 1.0
                )

                rows.append({
                    "day": d,
                    "Time": last_strategy["Time"],
                    "sec": last_strategy_sec,
                    "Price": last_strategy_price,
                    "next_time": actual_eod_time,
                    "next_sec": actual_eod_sec,
                    "next_price": actual_eod_price,
                    "future_return": eod_future_return,
                    FEATURE: float(
                        last_strategy[FEATURE]
                    ),
                    "z": float(
                        last_strategy["z"]
                    ),
                    "position": last_position,
                    "prev_position": float(
                        last_strategy["prev_position"]
                    ),
                    "turnover": last_turnover,
                    "gross_ret": gross_ret,
                    "transaction_cost_rate": (
                        transaction_cost_rate
                    ),
                    "transaction_cost_ret": (
                        transaction_cost_rate
                    ),
                    "eod_liquidation_cost_rate": (
                        eod_liquidation_rate
                    ),
                    "net_ret": net_ret,
                    "interval_type": "EOD",
                })

            elif (
                np.isclose(
                    actual_eod_sec,
                    last_strategy_sec,
                    rtol=0.0,
                    atol=1e-9
                )
            ):

                # ------------------------------------------------
                # The final strategy timestamp IS the actual EOD.
                #
                # No additional return exists.
                #
                # But the position must still be liquidated.
                # ------------------------------------------------

                eod_liquidation_rate = (
                    abs(last_position)
                    * cost_rate
                )

                if eod_liquidation_rate > 0:

                    # Apply the EOD liquidation cost to the
                    # final strategy interval.
                    #
                    # We modify only the final row because the
                    # liquidation occurs at this timestamp.
                    if rows:

                        final_row = rows[-1]

                        if (
                            final_row["day"] == d
                            and np.isclose(
                                final_row["next_sec"],
                                actual_eod_sec,
                                rtol=0.0,
                                atol=1e-9
                            )
                        ):
                            # Already reaches EOD.
                            final_row[
                                "eod_liquidation_cost_rate"
                            ] = (
                                eod_liquidation_rate
                            )

                            gross_growth = (
                                1.0
                                + final_row["gross_ret"]
                            )

                            net_growth = (
                                gross_growth
                                * (
                                    1.0
                                    - final_row[
                                        "transaction_cost_rate"
                                    ]
                                )
                                * (
                                    1.0
                                    - eod_liquidation_rate
                                )
                            )

                            if net_growth <= 0:
                                raise ValueError(
                                    f"Day {d}: non-positive "
                                    "final EOD wealth factor."
                                )

                            final_row["net_ret"] = (
                                net_growth
                                - 1.0
                            )

                        else:
                            # This case should be extremely rare,
                            # but if the final strategy point does
                            # not correspond to a generated row,
                            # create an explicit zero-return EOD
                            # liquidation event.
                            rows.append({
                                "day": d,
                                "Time": last_strategy["Time"],
                                "sec": last_strategy_sec,
                                "Price": last_strategy_price,
                                "next_time": actual_eod_time,
                                "next_sec": actual_eod_sec,
                                "next_price": actual_eod_price,
                                "future_return": 0.0,
                                FEATURE: float(
                                    last_strategy[FEATURE]
                                ),
                                "z": float(
                                    last_strategy["z"]
                                ),
                                "position": last_position,
                                "prev_position": float(
                                    last_strategy[
                                        "prev_position"
                                    ]
                                ),
                                "turnover": 0.0,
                                "gross_ret": 0.0,
                                "transaction_cost_rate": 0.0,
                                "transaction_cost_ret": 0.0,
                                "eod_liquidation_cost_rate": (
                                    eod_liquidation_rate
                                ),
                                "net_ret": (
                                    -eod_liquidation_rate
                                ),
                                "interval_type": "EOD",
                            })

        # ----------------------------------------------------
        # If the day contains no active position, no EOD
        # liquidation cost exists.
        # ----------------------------------------------------

        if not rows:
            continue

        day_result = pd.DataFrame(rows)

        # ----------------------------------------------------
        # Defensive validation.
        # ----------------------------------------------------

        if not day_result["sec"].is_monotonic_increasing:
            raise ValueError(
                f"Day {d}: scenario timestamps are not monotonic."
            )

        if (
            day_result["day"]
            != d
        ).any():
            raise ValueError(
                f"Day {d}: internal day-label corruption."
            )

        # ----------------------------------------------------
        # Authoritative wealth reconstruction.
        #
        # This verifies that net_ret is exactly the same stream
        # used for cumulative portfolio performance.
        # ----------------------------------------------------

        growth = (
            1.0
            + day_result["net_ret"]
        )

        if np.any(
            ~np.isfinite(growth)
            | (growth <= 0)
        ):
            raise ValueError(
                f"Day {d}: invalid net wealth factor."
            )

        scenario_rows.append(
            day_result
        )

    if not scenario_rows:
        return pd.DataFrame()

    result = (
        pd.concat(
            scenario_rows,
            ignore_index=True
        )
        .sort_values(
            [
                "day",
                "sec",
            ]
        )
        .reset_index(drop=True)
    )

    result["threshold"] = (
        float(threshold)
    )

    result["transaction_cost_bps"] = (
        float(cost_bps)
    )

    result["rebalance_minutes"] = (
        int(frequency_minutes)
    )

    return result


# ============================================================
# SCENARIO PERFORMANCE
# ============================================================

def scenario_performance(
    df,
    split,
    threshold,
    cost_bps,
    frequency_minutes
):

    if len(df) == 0:

        return {
            "split": split,
            "threshold": threshold,
            "transaction_cost_bps": cost_bps,
            "rebalance_minutes": frequency_minutes,
            "start_day": np.nan,
            "end_day": np.nan,
            "days": 0,
            "observations": 0,
            "strategy_intervals": 0,
            "eod_intervals": 0,
            "gross_total_return": np.nan,
            "transaction_cost_return": np.nan,
            "eod_liquidation_cost_return": np.nan,
            "net_total_return": np.nan,
            "annualized_volatility": np.nan,
            "sharpe": np.nan,
            "sortino": np.nan,
            "max_drawdown": np.nan,
            "positive_net_period_fraction": np.nan,
            "turnover": np.nan,
            "exposure": np.nan,
            "long_fraction": np.nan,
            "short_fraction": np.nan,
            "flat_fraction": np.nan,
            "active_fraction": np.nan,
            "mean_abs_position": np.nan,
            "number_of_rebalances": 0,
            "eod_liquidations": 0,
            "avg_periods_per_day": np.nan,
            "periods_per_year": np.nan,
        }

    x = finite_series(
        df["net_ret"]
    )

    gross = finite_series(
        df["gross_ret"]
    )

    tc = finite_series(
        df["transaction_cost_rate"]
    )

    eod_cost = finite_series(
        df[
            "eod_liquidation_cost_rate"
        ]
    )

    # --------------------------------------------------------
    # Authoritative portfolio return.
    # --------------------------------------------------------

    net_total = safe_total_return(
        x
    )

    gross_total = safe_total_return(
        gross
    )

    transaction_cost_total = (
        safe_cost_return(tc)
    )

    eod_cost_total = (
        safe_cost_return(eod_cost)
    )

    # --------------------------------------------------------
    # Actual scenario periods/day.
    #
    # This is deliberately derived from the generated scenario
    # stream rather than median raw observations / frequency.
    # --------------------------------------------------------

    periods_by_day = (
        df.groupby("day")
        .size()
    )

    avg_periods_per_day = (
        periods_by_day.mean()
        if len(periods_by_day)
        else np.nan
    )

    periods_per_year = (
        252.0
        * avg_periods_per_day
        if np.isfinite(avg_periods_per_day)
        else np.nan
    )

    if (
        not np.isfinite(periods_per_year)
        or periods_per_year <= 0
    ):
        periods_per_year = np.nan

    volatility = (
        x.std(ddof=1)
        * np.sqrt(periods_per_year)
        if (
            len(x) > 1
            and np.isfinite(periods_per_year)
        )
        else np.nan
    )

    sharpe_value = (
        sharpe(
            x,
            periods_per_year
        )
        if np.isfinite(periods_per_year)
        else np.nan
    )

    sortino_value = (
        sortino(
            x,
            periods_per_year
        )
        if np.isfinite(periods_per_year)
        else np.nan
    )

    long_fraction = (
        (df["position"] > 0).mean()
    )

    short_fraction = (
        (df["position"] < 0).mean()
    )

    flat_fraction = (
        (df["position"] == 0).mean()
    )

    active_fraction = (
        df["position"].ne(0).mean()
    )

    mean_abs_position = (
        df["position"]
        .abs()
        .mean()
    )

    turnover = (
        df["turnover"]
        .sum()
    )

    positive_net_period_fraction = (
        (x > 0).mean()
        if len(x)
        else np.nan
    )

    number_of_rebalances = int(
        (
            df["turnover"]
            > 0
        ).sum()
    )

    eod_liquidations = int(
        (
            df[
                "eod_liquidation_cost_rate"
            ]
            > 0
        ).sum()
    )

    strategy_intervals = int(
        (
            df["interval_type"]
            == "STRATEGY"
        ).sum()
    )

    eod_intervals = int(
        (
            df["interval_type"]
            == "EOD"
        ).sum()
    )

    return {
        "split": split,
        "threshold": threshold,
        "transaction_cost_bps": cost_bps,
        "rebalance_minutes": frequency_minutes,
        "start_day": int(df["day"].min()),
        "end_day": int(df["day"].max()),
        "days": int(df["day"].nunique()),
        "observations": int(len(df)),
        "strategy_intervals": strategy_intervals,
        "eod_intervals": eod_intervals,
        "gross_total_return": gross_total,
        "transaction_cost_return": (
            transaction_cost_total
        ),
        "eod_liquidation_cost_return": (
            eod_cost_total
        ),
        "net_total_return": net_total,
        "annualized_volatility": volatility,
        "sharpe": sharpe_value,
        "sortino": sortino_value,
        "max_drawdown": max_drawdown(x),
        "positive_net_period_fraction": (
            positive_net_period_fraction
        ),
        "turnover": turnover,
        "exposure": active_fraction,
        "long_fraction": long_fraction,
        "short_fraction": short_fraction,
        "flat_fraction": flat_fraction,
        "active_fraction": active_fraction,
        "mean_abs_position": mean_abs_position,
        "number_of_rebalances": (
            number_of_rebalances
        ),
        "eod_liquidations": (
            eod_liquidations
        ),
        "avg_periods_per_day": (
            avg_periods_per_day
        ),
        "periods_per_year": (
            periods_per_year
        ),
    }


# ============================================================
# SPLIT MAP
# ============================================================

SPLITS = {
    "TRAIN": TRAIN_DAYS,
    "VALIDATION": VALIDATION_DAYS,
    "TEST": TEST_DAYS,
}


# ============================================================
# EVALUATE ONE SCENARIO
#
# No scenario can modify the frozen strategy.
# ============================================================

def evaluate_scenario(
    threshold,
    cost_bps,
    frequency_minutes,
    scenario_type
):

    rows = []

    for split_name, split_days in SPLITS.items():

        bt = run_scenario(
            split_days,
            threshold,
            cost_bps,
            frequency_minutes
        )

        perf = scenario_performance(
            bt,
            split_name,
            threshold,
            cost_bps,
            frequency_minutes
        )

        perf["scenario"] = (
            scenario_type
        )

        perf["feature"] = (
            FEATURE
        )

        perf["family"] = (
            FAMILY
        )

        perf["selected_threshold"] = (
            SELECTED_THRESHOLD
        )

        perf["baseline_cost_bps"] = (
            BASE_COST_BPS
        )

        perf[
            "baseline_frequency_minutes"
        ] = BASE_REBALANCE

        # TEST is always report-only.
        perf[
            "test_used_for_selection"
        ] = False

        rows.append(perf)

    return rows


# ============================================================
# 20A — THRESHOLD ROBUSTNESS
#
# Frozen:
#   cost = baseline
#   frequency = baseline
#
# Varied:
#   threshold
# ============================================================

print(
    "\n--- 20A: THRESHOLD ROBUSTNESS ---"
)

threshold_rows = []

for threshold in THRESHOLDS:

    threshold_rows.extend(
        evaluate_scenario(
            threshold=threshold,
            cost_bps=BASE_COST_BPS,
            frequency_minutes=BASE_REBALANCE,
            scenario_type="threshold"
        )
    )


# ============================================================
# 20B — TRANSACTION-COST ROBUSTNESS
#
# Frozen:
#   threshold = File-19 selected threshold
#   frequency = baseline
#
# Varied:
#   transaction cost
# ============================================================

print(
    "\n--- 20B: TRANSACTION-COST ROBUSTNESS ---"
)

cost_rows = []

for cost_bps in COST_GRID_BPS:

    cost_rows.extend(
        evaluate_scenario(
            threshold=SELECTED_THRESHOLD,
            cost_bps=cost_bps,
            frequency_minutes=BASE_REBALANCE,
            scenario_type="transaction_cost"
        )
    )


# ============================================================
# 20C — REBALANCE-FREQUENCY ROBUSTNESS
#
# Frozen:
#   threshold = File-19 selected threshold
#   cost = baseline
#
# Varied:
#   frequency
#
# This changes execution frequency only.
#
# HORIZON remains the frozen predictive horizon.
# ============================================================

print(
    "\n--- 20C: REBALANCE-FREQUENCY ROBUSTNESS ---"
)

frequency_rows = []

for frequency in FREQUENCY_GRID:

    frequency_rows.extend(
        evaluate_scenario(
            threshold=SELECTED_THRESHOLD,
            cost_bps=BASE_COST_BPS,
            frequency_minutes=frequency,
            scenario_type="frequency"
        )
    )


# ============================================================
# COMBINE
# ============================================================

robustness_df = pd.DataFrame(
    threshold_rows
    + cost_rows
    + frequency_rows
)

if len(robustness_df) == 0:
    raise ValueError(
        "No robustness scenarios were produced."
    )


# ============================================================
# SCENARIO LABELS
# ============================================================

robustness_df["is_baseline"] = (
    np.isclose(
        robustness_df[
            "threshold"
        ].astype(float),
        SELECTED_THRESHOLD,
        rtol=0.0,
        atol=1e-10
    )
    &
    np.isclose(
        robustness_df[
            "transaction_cost_bps"
        ].astype(float),
        BASE_COST_BPS,
        rtol=0.0,
        atol=1e-10
    )
    &
    (
        robustness_df[
            "rebalance_minutes"
        ].astype(int)
        == BASE_REBALANCE
    )
)

robustness_df[
    "threshold_deviation"
] = (
    robustness_df["threshold"]
    - SELECTED_THRESHOLD
)

robustness_df[
    "cost_deviation_bps"
] = (
    robustness_df[
        "transaction_cost_bps"
    ]
    - BASE_COST_BPS
)

robustness_df[
    "frequency_change"
] = (
    robustness_df[
        "rebalance_minutes"
    ]
    / BASE_REBALANCE
)


# ============================================================
# BASELINE VALIDATION
# ============================================================

# baseline_rows = robustness_df[
#     robustness_df["is_baseline"]
# ].copy()

# if len(baseline_rows) != 3:
#     raise ValueError(
#         "Expected exactly one baseline row per split "
#         "(TRAIN, VALIDATION, TEST)."
#     )

baseline_rows = robustness_df[
    robustness_df['is_baseline']
    & (robustness_df['scenario'] == 'threshold')
].copy()

if len(baseline_rows) != 3:
    raise ValueError(
        "Expected exactly one baseline row per split"
    )

if set(
    baseline_rows["split"]
) != {
    "TRAIN",
    "VALIDATION",
    "TEST",
}:
    raise ValueError(
        "Baseline rows do not contain exactly "
        "TRAIN / VALIDATION / TEST."
    )

baseline_lookup = (
    baseline_rows
    .set_index("split")
    .to_dict("index")
)


def baseline_delta(
    row,
    metric
):

    base = (
        baseline_lookup
        .get(
            row["split"],
            {}
        )
        .get(
            metric,
            np.nan
        )
    )

    value = row.get(
        metric,
        np.nan
    )

    if (
        pd.isna(base)
        or pd.isna(value)
    ):
        return np.nan

    return (
        float(value)
        - float(base)
    )


robustness_df[
    "sharpe_delta_vs_baseline"
] = robustness_df.apply(
    lambda r:
        baseline_delta(
            r,
            "sharpe"
        ),
    axis=1
)

robustness_df[
    "net_return_delta_vs_baseline"
] = robustness_df.apply(
    lambda r:
        baseline_delta(
            r,
            "net_total_return"
        ),
    axis=1
)

robustness_df[
    "drawdown_delta_vs_baseline"
] = robustness_df.apply(
    lambda r:
        baseline_delta(
            r,
            "max_drawdown"
        ),
    axis=1
)


# ============================================================
# ROBUSTNESS DIAGNOSTICS
#
# Descriptive only.
#
# None of these metrics selects a strategy parameter.
# ============================================================

def robustness_stats(
    group,
    axis_name
):

    sharpe_values = (
        pd.to_numeric(
            group["sharpe"],
            errors="coerce"
        )
        .replace(
            [np.inf, -np.inf],
            np.nan
        )
        .dropna()
    )

    return {
        "axis": axis_name,
        "split": (
            group["split"].iloc[0]
            if len(group)
            else None
        ),
        "scenarios": int(
            len(group)
        ),
        "sharpe_min": (
            sharpe_values.min()
            if len(sharpe_values)
            else np.nan
        ),
        "sharpe_max": (
            sharpe_values.max()
            if len(sharpe_values)
            else np.nan
        ),
        "sharpe_median": (
            sharpe_values.median()
            if len(sharpe_values)
            else np.nan
        ),
        "sharpe_std": (
            sharpe_values.std(ddof=1)
            if len(sharpe_values) > 1
            else 0.0
            if len(sharpe_values) == 1
            else np.nan
        ),
        "positive_sharpe_fraction": (
            (sharpe_values > 0).mean()
            if len(sharpe_values)
            else np.nan
        ),
        "positive_return_fraction": (
            (
                pd.to_numeric(
                    group[
                        "net_total_return"
                    ],
                    errors="coerce"
                )
                > 0
            ).mean()
            if len(group)
            else np.nan
        ),
        "worst_net_return": (
            pd.to_numeric(
                group[
                    "net_total_return"
                ],
                errors="coerce"
            ).min()
            if len(group)
            else np.nan
        ),
        "best_net_return": (
            pd.to_numeric(
                group[
                    "net_total_return"
                ],
                errors="coerce"
            ).max()
            if len(group)
            else np.nan
        ),
        "worst_drawdown": (
            pd.to_numeric(
                group[
                    "max_drawdown"
                ],
                errors="coerce"
            ).min()
            if len(group)
            else np.nan
        ),
    }


summary_rows = []

for axis_name, axis_df in [
    (
        "threshold",
        threshold_rows
    ),
    (
        "transaction_cost",
        cost_rows
    ),
    (
        "frequency",
        frequency_rows
    ),
]:

    axis_df = pd.DataFrame(
        axis_df
    )

    if len(axis_df) == 0:
        continue

    for split_name in [
        "TRAIN",
        "VALIDATION",
        "TEST",
    ]:

        q = axis_df[
            axis_df["split"]
            == split_name
        ].copy()

        if len(q):
            summary_rows.append(
                robustness_stats(
                    q,
                    axis_name
                )
            )

robustness_summary_df = pd.DataFrame(
    summary_rows
)


# ============================================================
# TEST-ONLY DESCRIPTIVE FLAGS
#
# These are NOT optimization criteria.
# ============================================================

threshold_test = robustness_df[
    robustness_df["scenario"]
    == "threshold"
]

cost_test = robustness_df[
    robustness_df["scenario"]
    == "transaction_cost"
]

frequency_test = robustness_df[
    robustness_df["scenario"]
    == "frequency"
]

test_threshold = threshold_test[
    threshold_test["split"]
    == "TEST"
].copy()

test_cost = cost_test[
    cost_test["split"]
    == "TEST"
].copy()

test_frequency = frequency_test[
    frequency_test["split"]
    == "TEST"
].copy()


def positive_fraction(
    df,
    metric
):

    x = (
        pd.to_numeric(
            df[metric],
            errors="coerce"
        )
        .replace(
            [np.inf, -np.inf],
            np.nan
        )
        .dropna()
    )

    if len(x) == 0:
        return np.nan

    return (
        x > 0
    ).mean()


threshold_test_positive_sharpe = (
    positive_fraction(
        test_threshold,
        "sharpe"
    )
)

cost_test_positive_sharpe = (
    positive_fraction(
        test_cost,
        "sharpe"
    )
)

frequency_test_positive_sharpe = (
    positive_fraction(
        test_frequency,
        "sharpe"
    )
)


# ============================================================
# BASELINE TEST RESULT
# ============================================================

# baseline_test = robustness_df[
#     (
#         robustness_df["split"]
#         == "TEST"
#     )
#     &
#     (
#         robustness_df["is_baseline"]
#     )
# ].copy()

baseline_test = robustness_df[
    (
        robustness_df['split']
        == 'TEST'
    )
    & (
        robustness_df['is_baseline']
    )
    & (
        robustness_df['scenario']
        == 'threshold'
    )
].copy()

if len(baseline_test) != 1:
    raise ValueError(
        "Exactly one baseline TEST scenario is required."
    )

baseline_test = (
    baseline_test.iloc[0]
)


# ============================================================
# SAVE MAIN ROBUSTNESS TABLE
# ============================================================

COLUMN_ORDER = [

    "scenario",

    "feature",
    "family",

    "split",

    "threshold",
    "selected_threshold",

    "transaction_cost_bps",
    "baseline_cost_bps",

    "rebalance_minutes",
    "baseline_frequency_minutes",

    "is_baseline",

    "threshold_deviation",
    "cost_deviation_bps",
    "frequency_change",

    "start_day",
    "end_day",
    "days",
    "observations",

    "strategy_intervals",
    "eod_intervals",

    "gross_total_return",
    "transaction_cost_return",
    "eod_liquidation_cost_return",
    "net_total_return",

    "annualized_volatility",
    "sharpe",
    "sortino",
    "max_drawdown",

    "positive_net_period_fraction",

    "turnover",
    "exposure",

    "long_fraction",
    "short_fraction",
    "flat_fraction",
    "active_fraction",
    "mean_abs_position",

    "number_of_rebalances",
    "eod_liquidations",

    "avg_periods_per_day",
    "periods_per_year",

    "sharpe_delta_vs_baseline",
    "net_return_delta_vs_baseline",
    "drawdown_delta_vs_baseline",

    "test_used_for_selection",
]

COLUMN_ORDER = [
    c
    for c in COLUMN_ORDER
    if c in robustness_df.columns
]

robustness_df = (
    robustness_df[
        COLUMN_ORDER
    ]
)

robustness_df.to_csv(
    ROBUSTNESS_FILE,
    index=False
)


# ============================================================
# SAVE ROBUSTNESS SUMMARY
# ============================================================

robustness_summary_df.to_csv(
    ROBUSTNESS_SUMMARY_FILE,
    index=False
)


# ============================================================
# 20D — HUMAN-READABLE ROBUSTNESS SUMMARY
#
# Descriptive only.
#
# No "best parameter" is selected.
# ============================================================

print(
    "\n--- 20D: ROBUSTNESS SUMMARY ---"
)

print(
    "\nThreshold robustness — TEST"
)

print(
    test_threshold[
        [
            "threshold",
            "sharpe",
            "sortino",
            "net_total_return",
            "max_drawdown",
            "number_of_rebalances",
        ]
    ].sort_values(
        "threshold"
    ).to_string(
        index=False
    )
)

print(
    "\nTransaction-cost robustness — TEST"
)

print(
    test_cost[
        [
            "transaction_cost_bps",
            "sharpe",
            "sortino",
            "net_total_return",
            "max_drawdown",
            "number_of_rebalances",
        ]
    ].sort_values(
        "transaction_cost_bps"
    ).to_string(
        index=False
    )
)

print(
    "\nFrequency robustness — TEST"
)

print(
    test_frequency[
        [
            "rebalance_minutes",
            "sharpe",
            "sortino",
            "net_total_return",
            "max_drawdown",
            "number_of_rebalances",
        ]
    ].sort_values(
        "rebalance_minutes"
    ).to_string(
        index=False
    )
)


# ============================================================
# BASELINE TEST REPORT
# ============================================================

print(
    "\n--- BASELINE TEST ---"
)

print(
    "Threshold       :",
    baseline_test[
        "threshold"
    ]
)

print(
    "Cost            :",
    baseline_test[
        "transaction_cost_bps"
    ],
    "bps"
)

print(
    "Frequency       :",
    baseline_test[
        "rebalance_minutes"
    ],
    "minute"
)

print(
    "Net return      :",
    baseline_test[
        "net_total_return"
    ]
)

print(
    "Sharpe          :",
    baseline_test[
        "sharpe"
    ]
)

print(
    "Sortino         :",
    baseline_test[
        "sortino"
    ]
)

print(
    "Max drawdown    :",
    baseline_test[
        "max_drawdown"
    ]
)

print(
    "Transaction cost:",
    baseline_test[
        "transaction_cost_return"
    ]
)

print(
    "EOD liquidation :",
    baseline_test[
        "eod_liquidation_cost_return"
    ]
)


# ============================================================
# ROBUSTNESS FLAGS
#
# These are descriptive diagnostics only.
# ============================================================

print(
    "\n--- ROBUSTNESS FLAGS ---"
)

print(
    "Threshold grid — positive TEST Sharpe fraction:",
    threshold_test_positive_sharpe
)

print(
    "Cost grid      — positive TEST Sharpe fraction:",
    cost_test_positive_sharpe
)

print(
    "Frequency grid — positive TEST Sharpe fraction:",
    frequency_test_positive_sharpe
)

print(
    "\nIMPORTANT:"
)

print(
    "These are descriptive diagnostics only."
)

print(
    "No TEST scenario was used to select "
    "threshold, transaction cost, or frequency."
)


# ============================================================
# PLOT 1 — THRESHOLD vs TEST SHARPE
#
# TEST is shown only after all parameters are frozen.
# ============================================================

plot_df = (
    test_threshold
    .sort_values("threshold")
)

plt.figure(
    figsize=(10, 5)
)

plt.plot(
    plot_df["threshold"],
    plot_df["sharpe"],
    marker="o"
)

plt.axvline(
    SELECTED_THRESHOLD,
    linestyle="--",
    alpha=0.7
)

plt.xlabel(
    "Threshold"
)

plt.ylabel(
    "Test Sharpe"
)

plt.title(
    f"Threshold Robustness — {FEATURE}"
)

plt.grid(
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    THRESHOLD_PLOT,
    dpi=150
)

plt.close()


# ============================================================
# PLOT 2 — COST vs TEST NET RETURN
# ============================================================

plot_df = (
    test_cost
    .sort_values(
        "transaction_cost_bps"
    )
)

plt.figure(
    figsize=(10, 5)
)

plt.plot(
    plot_df[
        "transaction_cost_bps"
    ],
    plot_df[
        "net_total_return"
    ],
    marker="o"
)

plt.axvline(
    BASE_COST_BPS,
    linestyle="--",
    alpha=0.7
)

plt.xlabel(
    "Transaction Cost (bps)"
)

plt.ylabel(
    "Test Net Return"
)

plt.title(
    f"Transaction-Cost Robustness — {FEATURE}"
)

plt.grid(
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    COST_PLOT,
    dpi=150
)

plt.close()


# ============================================================
# PLOT 3 — FREQUENCY vs TEST SHARPE
# ============================================================

plot_df = (
    test_frequency
    .sort_values(
        "rebalance_minutes"
    )
)

plt.figure(
    figsize=(10, 5)
)

plt.plot(
    plot_df[
        "rebalance_minutes"
    ],
    plot_df[
        "sharpe"
    ],
    marker="o"
)

plt.axvline(
    BASE_REBALANCE,
    linestyle="--",
    alpha=0.7
)

plt.xlabel(
    "Rebalance Frequency (minutes)"
)

plt.ylabel(
    "Test Sharpe"
)

plt.title(
    f"Rebalance-Frequency Robustness — {FEATURE}"
)

plt.grid(
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    FREQUENCY_PLOT,
    dpi=150
)

plt.close()


# ============================================================
# PLOT 4 — NORMALIZED TEST SHARPE
#
# Visualization only.
#
# Baseline = 1.0.
# ============================================================

summary_plot_rows = []

for scenario_name, q in [
    (
        "threshold",
        test_threshold
    ),
    (
        "transaction_cost",
        test_cost
    ),
    (
        "frequency",
        test_frequency
    ),
]:

    for _, r in q.iterrows():

        base_sharpe = float(
            baseline_test[
                "sharpe"
            ]
        )

        current_sharpe = float(
            r["sharpe"]
        ) if pd.notna(
            r["sharpe"]
        ) else np.nan

        if (
            not np.isfinite(
                base_sharpe
            )
            or base_sharpe == 0
            or not np.isfinite(
                current_sharpe
            )
        ):
            normalized = np.nan

        else:
            normalized = (
                current_sharpe
                / base_sharpe
            )

        if (
            scenario_name
            == "threshold"
        ):
            label = (
                f"th={r['threshold']}"
            )

        elif (
            scenario_name
            == "transaction_cost"
        ):
            label = (
                f"cost={r['transaction_cost_bps']}"
            )

        else:
            label = (
                f"freq={r['rebalance_minutes']}m"
            )

        summary_plot_rows.append({
            "scenario": scenario_name,
            "label": label,
            "normalized_sharpe": normalized,
        })


summary_plot = pd.DataFrame(
    summary_plot_rows
)

plt.figure(
    figsize=(12, 5)
)

positions = np.arange(
    len(summary_plot)
)

plt.bar(
    positions,
    summary_plot[
        "normalized_sharpe"
    ]
)

plt.axhline(
    1.0,
    linestyle="--",
    alpha=0.7
)

plt.xticks(
    positions,
    summary_plot["label"],
    rotation=45,
    ha="right"
)

plt.ylabel(
    "Test Sharpe / Baseline Test Sharpe"
)

plt.title(
    f"Strategy Robustness Relative to Baseline — {FEATURE}"
)

plt.grid(
    axis="y",
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    ROBUSTNESS_PLOT,
    dpi=150
)

plt.close()


# ============================================================
# FINAL REPORT
# ============================================================

print(
    "\n--- FILES WRITTEN ---"
)

print(
    ROBUSTNESS_FILE
)

print(
    ROBUSTNESS_SUMMARY_FILE
)

print(
    THRESHOLD_PLOT
)

print(
    COST_PLOT
)

print(
    FREQUENCY_PLOT
)

print(
    ROBUSTNESS_PLOT
)


# ============================================================
# FINAL CONTRACT LOCK
# ============================================================

print(
    "\n--- TEST LOCK ---"
)

print(
    "Feature remained frozen from File 18."
)

print(
    "TRAIN normalization remained frozen."
)

print(
    "Signal direction remained frozen from File 18."
)

print(
    "Selected threshold came from File 19."
)

print(
    "File 20 did not optimize TEST."
)

print(
    "Transaction cost was not selected using TEST."
)

print(
    "Rebalance frequency was not selected using TEST."
)

print(
    "Threshold stress is sensitivity analysis."
)

print(
    "Transaction-cost stress is sensitivity analysis."
)

print(
    "Frequency stress is sensitivity analysis."
)

print(
    "No overnight position carry."
)

print(
    "Position resets to zero at every day boundary."
)

print(
    "Frequency is interpreted using elapsed timestamps, "
    "not row count."
)

print(
    "Actual EOD observation is used for EOD completion."
)

print(
    "Explicit EOD liquidation cost is included."
)

print(
    "Net portfolio wealth is the authoritative accounting stream."
)

print(
    "All cumulative performance metrics derive from net_ret."
)

print(
    "Annualization is derived from actual generated "
    "scenario periods/day."
)

print(
    "TEST results are report-only."
)

print(
    "\nDone."
)

