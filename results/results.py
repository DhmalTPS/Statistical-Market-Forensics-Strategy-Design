"""
Quant Data Challenge - Final Report Generator
=============================================

This script reads the EXISTING project outputs and generates:

    results/results.md

It is deliberately a REPORT GENERATOR, not an analysis notebook.

Design principles
-----------------
1. Do not rerun the research pipeline.
2. Do not dump large dataframes into the report.
3. Use complete CSVs for calculations where necessary.
4. Use small CSVs directly for report tables.
5. Never require pandas.to_markdown()/tabulate.
6. Reference existing PNG figures rather than recreating them.
7. Keep the report concise enough for a 6-10 page submission.
8. Preserve train / validation / test separation for Task 5.
"""

from pathlib import Path
import math
import warnings

import numpy as np
import pandas as pd


# ============================================================
# 0. PATHS
# ============================================================

ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = Path(__file__).resolve().parent
OUTPUT = ROOT / "output"
RESULTS = ROOT / "results"

REPORT_FILE = REPORT_DIR / "results.md"

warnings.filterwarnings("ignore")


# ============================================================
# 1. GENERAL HELPERS
# ============================================================

def read_csv(name, subdir=None, **kwargs):
    """Read an output CSV safely."""
    path = OUTPUT / subdir / name if subdir else OUTPUT / name

    if not path.exists():
        print(f"[WARN] Missing: {path}")
        return None

    try:
        return pd.read_csv(path, **kwargs)
    except Exception as exc:
        print(f"[WARN] Could not read {path}: {exc}")
        return None


def read_csv_path(path, **kwargs):
    """Read an arbitrary CSV safely."""
    path = Path(path)

    if not path.exists():
        print(f"[WARN] Missing: {path}")
        return None

    try:
        return pd.read_csv(path, **kwargs)
    except Exception as exc:
        print(f"[WARN] Could not read {path}: {exc}")
        return None


def clean_value(x):
    """Convert numpy/pandas values into report-friendly values."""
    if pd.isna(x):
        return "—"

    if isinstance(x, (np.integer,)):
        return int(x)

    if isinstance(x, (np.floating, float)):
        if not np.isfinite(x):
            return "—"
        return float(x)

    return x


def fmt(x, digits=4):
    """Compact numerical formatting."""
    x = clean_value(x)

    if x == "—":
        return "—"

    if isinstance(x, (int, np.integer)):
        return f"{int(x):,}"

    if isinstance(x, (float, np.floating)):
        if abs(x) >= 1000:
            return f"{x:,.2f}"
        if abs(x) >= 1:
            return f"{x:.{digits}f}"
        return f"{x:.{digits}g}"

    return str(x)


def pct(x, digits=2):
    """Format decimal as percentage."""
    if x is None or pd.isna(x):
        return "—"

    return f"{100 * float(x):.{digits}f}%"


def md_escape(x):
    """Escape Markdown table characters."""
    x = clean_value(x)
    return str(x).replace("|", "\\|").replace("\n", " ")


def md_table(df, index=False, max_rows=None, digits=4):
    """
    Local Markdown table formatter.

    IMPORTANT:
    Does NOT use DataFrame.to_markdown().
    Therefore no 'tabulate' dependency is required.
    """

    if df is None or len(df) == 0:
        return "_No data available._"

    work = df.copy()

    if not index:
        work = work.reset_index(drop=True)

    if max_rows is not None:
        work = work.head(max_rows)

    headers = list(work.columns)

    lines = [
        "| " + " | ".join(md_escape(h) for h in headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]

    for _, row in work.iterrows():
        vals = []

        for value in row:
            value = clean_value(value)

            if isinstance(value, (float, np.floating)):
                value = fmt(value, digits)

            vals.append(md_escape(value))

        lines.append("| " + " | ".join(vals) + " |")

    return "\n".join(lines)


def section(title, level=2):
    return f"\n{'#' * level} {title}\n"


def image(name, caption=None):
    """Reference an existing PNG in the results directory."""
    path = RESULTS / name

    if not path.exists():
        return ""

    text = f"![{caption or name}]({name})"

    if caption:
        text += f"\n\n*Figure: {caption}*"

    return text


def first_existing(*paths):
    for p in paths:
        p = Path(p)
        if p.exists():
            return p
    return None


def numeric_columns(df):
    if df is None:
        return []

    return list(df.select_dtypes(include=[np.number]).columns)


def find_col(df, candidates):
    """Find first matching column, case-insensitively."""
    if df is None:
        return None

    lookup = {str(c).lower(): c for c in df.columns}

    for candidate in candidates:
        if candidate.lower() in lookup:
            return lookup[candidate.lower()]

    return None


def safe_mean(df, col):
    if df is None or col is None or col not in df.columns:
        return np.nan

    return pd.to_numeric(df[col], errors="coerce").mean()


def safe_median(df, col):
    if df is None or col is None or col not in df.columns:
        return np.nan

    return pd.to_numeric(df[col], errors="coerce").median()


def safe_sum(df, col):
    if df is None or col is None or col not in df.columns:
        return np.nan

    return pd.to_numeric(df[col], errors="coerce").sum()


# ============================================================
# 2. TASK 1
#    DATA HYGIENE & DESCRIPTIVE STATISTICS
# ============================================================

def task1():
    report = []

    report.append(section("Task 1 — Data Hygiene & Descriptive Statistics"))

    audit = read_csv("01_audit_days.csv")
    extreme = read_csv("01_extreme_moves.csv")
    feature_missing = read_csv("01_feature_missing.csv")
    missing_classify = read_csv("02_missing_classify.csv")
    pooled_stats = read_csv("03_pooled_statistics.csv")
    pooled_direction = read_csv("03_pooled_direction.csv")
    pooled_extremes = read_csv("03_pooled_extremes.csv")

    # --------------------------------------------------------
    # Dataset coverage
    # --------------------------------------------------------

    report.append("### 1.1 Dataset coverage\n")

    if audit is not None:
        day_col = find_col(audit, ["Day", "day"])

        if day_col:
            days = pd.to_numeric(audit[day_col], errors="coerce").dropna()

            if len(days):
                report.append(
                    f"The analysis is restricted to the competition's eligible "
                    f"Day 1–85 universe. The audit output contains "
                    f"**{int(days.min())}–{int(days.max())}** day identifiers "
                    f"across **{len(days)}** audited files."
                )
            else:
                report.append(
                    "The audit file is available, but its day identifiers "
                    "could not be interpreted numerically."
                )
        else:
            report.append(
                "The audit file is available but does not expose a standard "
                "`Day` column."
            )

    # --------------------------------------------------------
    # Audit summary
    # --------------------------------------------------------

    report.append("\n### 1.2 Ingestion and sanity checks\n")

    if audit is not None:
        cols = {str(c).lower(): c for c in audit.columns}

        candidate_cols = [
            ("Rows", ["rows", "row_count", "n_rows"]),
            ("Missing timestamps", ["missing_timestamps", "missing_timestamp"]),
            ("Duplicate timestamps", ["duplicate_timestamps", "duplicate_timestamp"]),
            ("NaN values", ["nan_count", "nans", "missing_values"]),
            ("Non-positive prices", ["nonpositive_prices", "non_positive_prices"]),
            ("Flat-line count", ["flatline", "flatlined", "flat_line"]),
            ("Extreme jumps", ["extreme_moves", "extreme_jumps"]),
        ]

        rows = []

        for label, names in candidate_cols:
            found = None

            for n in names:
                if n.lower() in cols:
                    found = cols[n.lower()]
                    break

            if found:
                rows.append({
                    "Check": label,
                    "Total": pd.to_numeric(
                        audit[found], errors="coerce"
                    ).sum()
                })

        if rows:
            audit_summary = pd.DataFrame(rows)
            audit_summary["Total"] = audit_summary["Total"].apply(
                lambda x: fmt(x, 0)
            )

            report.append(md_table(audit_summary))
        else:
            report.append(
                "The audit CSV is present. Its full per-day structure was "
                "used by the upstream audit notebook; no generic summary "
                "mapping was imposed here because column names do not match "
                "the expected audit labels."
            )

    # --------------------------------------------------------
    # Missing-data / cleaning policy
    # --------------------------------------------------------

    report.append("\n### 1.3 Cleaning policy\n")

    if missing_classify is not None:
        report.append(
            "The missing-data classification output was generated before "
            "downstream return analysis. The report therefore treats the "
            "cleaning decision as an explicit preprocessing step rather than "
            "silently modifying observations during later calculations."
        )

        # Give only category totals if possible.
        possible_cat = find_col(
            missing_classify,
            ["classification", "class", "missing_class", "category", "type"]
        )

        if possible_cat:
            counts = (
                missing_classify[possible_cat]
                .value_counts(dropna=False)
                .rename_axis("Classification")
                .reset_index(name="Count")
            )

            report.append("\n**Missing-data classifications:**\n")
            report.append(md_table(counts))

    else:
        report.append(
            "The missing-data classification output was not available at "
            "report-generation time."
        )

    # --------------------------------------------------------
    # Return representation
    # --------------------------------------------------------

    report.append("\n### 1.4 Return representation\n")

    report.append(
        "Returns are analysed rather than raw price levels for the dynamic "
        "time-series analysis. The primary representation is the "
        "**1-minute log return**, with 1-second and 5-minute returns retained "
        "for microstructure and horizon comparisons. Returns are calculated "
        "within individual days, avoiding artificial overnight/day-boundary "
        "returns."
    )

    if pooled_stats is not None:
        report.append("\n#### Pooled return statistics\n")

        # Keep this small: only return-related numeric columns.
        cols = [
            c for c in pooled_stats.columns
            if any(k in str(c).lower()
                   for k in ["return", "mean", "median", "std", "skew", "kurt"])
        ]

        if cols:
            show = pooled_stats[cols].copy()
            report.append(md_table(show, max_rows=15))
        else:
            report.append(md_table(pooled_stats, max_rows=15))

    # --------------------------------------------------------
    # ACF / microstructure
    # --------------------------------------------------------

    report.append("\n### 1.5 Short-lag autocorrelation and microstructure\n")

    acf1 = read_csv("acf_log_ret_1s.csv", subdir="04_day_acf")
    acf1m = read_csv("acf_log_ret_1m.csv", subdir="04_day_acf")
    acf5m = read_csv("acf_log_ret_5m.csv", subdir="04_day_acf")

    acf_rows = []

    for label, df in [
        ("1-second", acf1),
        ("1-minute", acf1m),
        ("5-minute", acf5m),
    ]:
        if df is None or len(df) == 0:
            continue

        num = numeric_columns(df)

        if not num:
            continue

        first_numeric = num[0]

        vals = pd.to_numeric(df[first_numeric], errors="coerce").dropna()

        if len(vals):
            acf_rows.append({
                "Return horizon": label,
                "First reported ACF": vals.iloc[0],
                "Maximum |ACF|": vals.abs().max(),
            })

    if acf_rows:
        acf_summary = pd.DataFrame(acf_rows)
        acf_summary["First reported ACF"] = acf_summary[
            "First reported ACF"
        ].map(lambda x: fmt(x, 5))
        acf_summary["Maximum |ACF|"] = acf_summary[
            "Maximum |ACF|"
        ].map(lambda x: fmt(x, 5))

        report.append(md_table(acf_summary))

    report.append(
        "\nThe interpretation should focus on whether short-horizon return "
        "autocorrelation is materially stronger at the 1-second frequency "
        "than at the 1-minute/5-minute frequencies. Stronger very-short-lag "
        "dependence is consistent with microstructure effects and supports "
        "using the 1-minute horizon as the main statistical representation."
    )

    # --------------------------------------------------------
    # Intraday seasonality
    # --------------------------------------------------------

    report.append("\n### 1.6 Intraday seasonality\n")

    intraday = read_csv(
        "intraday_log_ret_1m.csv",
        subdir="05_intraday_season"
    )

    if intraday is not None and len(intraday):
        numeric = numeric_columns(intraday)

        if numeric:
            vol_col = None

            for c in numeric:
                if "abs" in str(c).lower() or "vol" in str(c).lower():
                    vol_col = c
                    break

            if vol_col is None:
                vol_col = numeric[-1]

            values = pd.to_numeric(
                intraday[vol_col], errors="coerce"
            ).dropna()

            if len(values):
                report.append(
                    f"The intraday 1-minute seasonality output contains "
                    f"**{len(values):,}** usable observations. The cross-session "
                    f"pattern is evaluated from the existing intraday output "
                    f"rather than from individual raw-day files."
                )

    fig = image(
        "05_intra_abs_log_ret_1m.png",
        "Intraday absolute 1-minute log-return profile."
    )

    if fig:
        report.append("\n" + fig)

    report.append(
        "\nThe figure is used to assess whether volatility follows a "
        "U-shaped/open-close pattern or another systematic intraday shape. "
        "This matters for strategy design because a signal with identical "
        "raw strength at every clock time need not have identical risk."
    )

    # --------------------------------------------------------
    # Useful raw extreme evidence
    # --------------------------------------------------------

    if extreme is not None and len(extreme):
        report.append("\n### 1.7 Data-quality extremes\n")

        report.append(
            "The extreme-move audit is retained as supporting evidence for "
            "distinguishing genuine large moves from possible bad ticks. "
            "Only the most relevant summary is reported rather than dumping "
            "the full CSV."
        )

        num = numeric_columns(extreme)

        if num:
            summary = extreme[num].describe().T.reset_index()
            summary.columns = ["Variable", "Count", "Mean", "Std",
                               "Min", "25%", "50%", "75%", "Max"]

            report.append(md_table(summary, max_rows=10))

    return "\n".join(report)


# ============================================================
# 3. TASK 2
#    DISTRIBUTIONAL & TAIL ANALYSIS
# ============================================================

def task2():
    report = []

    report.append(section("Task 2 — Distributional & Tail Analysis"))

    stats = read_csv("06_distribution_stats.csv")
    normality = read_csv("06_normality_test.csv")
    sigma_pool = read_csv("sigma_pool_log_ret_1m.csv",
                          subdir="07_sigma_events")
    sigma_daily = read_csv("sigma_daily_log_ret_1m.csv",
                           subdir="07_sigma_events")
    vol_acf = read_csv("vol_acf_log_ret_1m.csv",
                       subdir="08_vol_cluster")
    extreme20 = read_csv("log_ret_1m_top20.csv",
                         subdir="09_extreme_events")

    # --------------------------------------------------------
    # Distribution
    # --------------------------------------------------------

    report.append("### 2.1 Return distribution\n")

    if stats is not None:
        report.append(
            "The distribution summary is based on the pooled and/or "
            "per-horizon return statistics produced by the distribution "
            "analysis."
        )

        report.append(md_table(stats, max_rows=20))

    # --------------------------------------------------------
    # Normality
    # --------------------------------------------------------

    report.append("\n### 2.2 Normality testing\n")

    if normality is not None:
        show = normality.copy()

        # Report only the columns useful for inference.
        keep = []

        for c in show.columns:
            name = str(c).lower()

            if (
                "horizon" in name
                or "return" in name
                or "test" in name
                or "stat" in name
                or "p" == name
                or "pvalue" in name
                or "p_value" in name
                or "sample" in name
                or "day" in name
            ):
                keep.append(c)

        if keep:
            show = show[keep]

        report.append(md_table(show, max_rows=30))

        # Count rejected tests if a p-value column exists.
        pcol = None

        for c in normality.columns:
            if str(c).lower() in {
                "p", "pvalue", "p_value", "p-value"
            }:
                pcol = c
                break

        if pcol:
            pvals = pd.to_numeric(
                normality[pcol], errors="coerce"
            ).dropna()

            if len(pvals):
                rejected = int((pvals < 0.05).sum())

                report.append(
                    f"\nAt the conventional 5% level, **{rejected} of "
                    f"{len(pvals)} reported tests reject normality**."
                )

    report.append(
        "\nA statistically significant normality test does not merely mean "
        "\"the p-value is small\": it means the Gaussian distribution is "
        "inconsistent with the observed sample at the chosen significance "
        "level. For a Gaussian VaR model, the practical implication is that "
        "tail probabilities inferred from a normal distribution may be "
        "miscalibrated, particularly when skewness, excess kurtosis and "
        "volatility clustering are present."
    )

    # --------------------------------------------------------
    # Sigma events
    # --------------------------------------------------------

    report.append("\n### 2.3 Sigma-event analysis\n")

    if sigma_pool is not None:
        report.append("#### Pooled sigma events\n")
        report.append(md_table(sigma_pool, max_rows=20))

    if sigma_daily is not None:
        report.append("\n#### Daily sigma-event extremes\n")

        # Instead of all 85 rows, identify days with largest 3-sigma counts.
        numeric = numeric_columns(sigma_daily)

        if numeric:
            count_col = None

            for c in numeric:
                if "3" in str(c) and (
                    "sigma" in str(c).lower()
                    or "std" in str(c).lower()
                    or "count" in str(c).lower()
                ):
                    count_col = c
                    break

            if count_col is None:
                # fallback to the last numeric field
                count_col = numeric[-1]

            show_cols = [
                c for c in sigma_daily.columns
                if c == count_col
                or str(c).lower() in {"day", "date"}
            ]

            if len(show_cols) == 1:
                show_cols = [count_col]

            show = sigma_daily[show_cols].copy()

            show[count_col] = pd.to_numeric(
                show[count_col], errors="coerce"
            )

            show = show.sort_values(
                count_col, ascending=False
            ).head(10)

            report.append(md_table(show))

    # --------------------------------------------------------
    # Volatility clustering
    # --------------------------------------------------------

    report.append("\n### 2.4 Volatility clustering\n")

    if vol_acf is not None:
        report.append(
            "Autocorrelation of absolute returns is used as the direct "
            "diagnostic for volatility persistence."
        )

        report.append(md_table(vol_acf, max_rows=15))

    fig = image(
        "08_vol_cluster_log_ret_1m.png",
        "Rolling/clustered 1-minute volatility behaviour."
    )

    if fig:
        report.append("\n" + fig)

    report.append(
        "\nPersistence in absolute-return dependence indicates that large "
        "moves are not necessarily independent events. This is the key "
        "reason a static Gaussian model can underestimate risk during "
        "volatile regimes."
    )

    # --------------------------------------------------------
    # Extreme-event catalogue
    # --------------------------------------------------------

    report.append("\n### 2.5 Rare-event catalogue — largest 1-minute moves\n")

    if extreme20 is not None:
        report.append(
            "The following table is intentionally limited to the requested "
            "top extreme events rather than reproducing the entire return "
            "dataset."
        )

        report.append(md_table(extreme20, max_rows=20))

    report.append(
        "\nThe extreme-event catalogue provides a concrete sanity check on "
        "the tail analysis and identifies the observations that dominate "
        "risk metrics."
    )

    # --------------------------------------------------------
    # Figures
    # --------------------------------------------------------

    for filename, caption in [
        (
            "06_norm_hist_log_ret_1m.png",
            "Histogram of pooled 1-minute log returns with normal reference."
        ),
        (
            "06_norm_qq_log_ret_1m.png",
            "Normal Q-Q plot for pooled 1-minute log returns."
        ),
    ]:
        fig = image(filename, caption)
        if fig:
            report.append("\n" + fig)

    return "\n".join(report)


# ============================================================
# 4. TASK 3
#    REGIME CLASSIFICATION
# ============================================================

def task3():
    report = []

    report.append(section("Task 3 — Regime Classification"))

    vr = read_csv("10_variance_ratio.csv")
    hurst = read_csv(
        "log_ret_1m_hurst_exp.csv",
        subdir="11_hurst_expo"
    )
    acf = read_csv(
        "log_ret_1m_reg_acf.csv",
        subdir="12_regime_acf"
    )
    reg_table = read_csv(
        "reg_tab_log_ret_1m.csv",
        subdir="13_regime_classify"
    )
    reg_summary = read_csv(
        "reg_sum_log_ret_1m.csv",
        subdir="13_regime_classify"
    )
    transition = read_csv("14_transition_matrix.csv")

    # --------------------------------------------------------
    # Methodology
    # --------------------------------------------------------

    report.append("### 3.1 Classification methodology\n")

    report.append(
        "Each eligible day is classified independently using multiple "
        "quantitative diagnostics. The primary evidence combines the "
        "**variance-ratio test, Hurst exponent and lagged-return "
        "autocorrelation**, rather than relying on a single statistic."
    )

    report.append(
        "\nThe interpretation follows the pre-declared direction of the "
        "tests: variance ratio materially below one and Hurst exponent "
        "below 0.5 support mean reversion; values above the corresponding "
        "thresholds support momentum/trending behaviour; values close to "
        "the random-walk benchmark are treated as approximately random."
    )

    # --------------------------------------------------------
    # Regime summary
    # --------------------------------------------------------

    report.append("\n### 3.2 Regime breakdown across 85 days\n")

    if reg_summary is not None:
        report.append(md_table(reg_summary, max_rows=15))

    # If no summary, derive counts from table.
    elif reg_table is not None:
        possible = [
            c for c in reg_table.columns
            if "regime" in str(c).lower()
        ]

        if possible:
            c = possible[0]

            counts = (
                reg_table[c]
                .value_counts(dropna=False)
                .rename_axis("Regime")
                .reset_index(name="Days")
            )

            report.append(md_table(counts))

    # --------------------------------------------------------
    # Per-day table
    # --------------------------------------------------------

    report.append("\n### 3.3 Per-day regime evidence\n")

    if reg_table is not None:
        report.append(
            "The complete 85-day regime table is a required deliverable. "
            "It is retained in the project output rather than reproducing "
            "all 85 rows inside the narrative report."
        )

        # Show only first 10 rows as a compact representative preview.
        report.append("\n**Representative rows:**\n")
        report.append(md_table(reg_table, max_rows=10))

    # --------------------------------------------------------
    # Test agreement
    # --------------------------------------------------------

    report.append("\n### 3.4 Agreement between tests\n")

    evidence = []

    if vr is not None:
        evidence.append(
            f"Variance-ratio output: **{len(vr):,}** rows."
        )

    if hurst is not None:
        evidence.append(
            f"Hurst output: **{len(hurst):,}** rows."
        )

    if acf is not None:
        evidence.append(
            f"Regime-ACF output: **{len(acf):,}** rows."
        )

    if evidence:
        report.append(" ".join(evidence))

    report.append(
        "\nDisagreement between the tests should not be interpreted as a "
        "failure of the analysis. The statistics answer different questions: "
        "variance ratio compares multi-step variance with the random-walk "
        "benchmark, Hurst measures persistence over scales, and lagged "
        "autocorrelation measures dependence at specified horizons."
    )

    # --------------------------------------------------------
    # Transition probabilities
    # --------------------------------------------------------

    report.append("\n### 3.5 Sequential regime behaviour\n")

    if transition is not None:
        report.append(md_table(transition, max_rows=20))

        report.append(
            "\nThe transition matrix is the direct test of whether regimes "
            "cluster sequentially rather than appearing independently."
        )

    # --------------------------------------------------------
    # Figures
    # --------------------------------------------------------

    for filename, caption in [
        (
            "log_ret_1m_vr_dist.png",
            "Distribution of daily variance-ratio statistics."
        ),
        (
            "log_ret_1m_hur_dist.png",
            "Distribution of daily Hurst exponents."
        ),
        (
            "log_ret_1m_reg_count.png",
            "Daily regime classification counts."
        ),
    ]:
        fig = image(filename, caption)
        if fig:
            report.append("\n" + fig)

    return "\n".join(report)


# ============================================================
# 5. TASK 4
#    FEATURE FORENSICS
# ============================================================

def task4():
    report = []

    report.append(section("Task 4 — Feature Forensics"))

    inventory = read_csv("15_feature_inventory.csv")
    hypotheses = read_csv("16_feature_hypotheses.csv")
    matching = read_csv("16_feature_matching.csv")
    lag_matching = read_csv("16_feature_lag_matching.csv")
    t_structure = read_csv("16_T_structure.csv")

    alpha_summary = read_csv("17_feature_alpha_summary.csv")
    alpha_rank = read_csv("17_feature_alpha_rank.csv")
    correlation = read_csv("17_feature_correlation.csv")
    pca = read_csv("17_pca_results.csv")

    dossier_path = OUTPUT / "16_FEATURE_DOSSIER.md"

    # --------------------------------------------------------
    # Feature inventory
    # --------------------------------------------------------

    report.append("### 4.1 Feature inventory and structure\n")

    if inventory is not None:
        report.append(
            f"The feature inventory contains **{len(inventory):,}** "
            f"reported feature records."
        )

        report.append(
            "\nA compact preview of the inventory is included only to "
            "establish the observed feature families:"
        )

        report.append(md_table(inventory, max_rows=12))

    # --------------------------------------------------------
    # Feature hypotheses
    # --------------------------------------------------------

    report.append("\n### 4.2 Reverse-engineering hypotheses\n")

    if hypotheses is not None:
        report.append(
            "The masked features are not assigned an interpretation merely "
            "from their names. The hypotheses are supported by matching "
            "against hand-built rolling statistics and their observed "
            "relationships."
        )

        # Select useful columns.
        cols = []

        for c in hypotheses.columns:
            n = str(c).lower()

            if (
                "feature" in n
                or "hypoth" in n
                or "family" in n
                or "confidence" in n
                or "match" in n
                or "description" in n
            ):
                cols.append(c)

        show = hypotheses[cols] if cols else hypotheses

        report.append(md_table(show, max_rows=25))

    # --------------------------------------------------------
    # Matching
    # --------------------------------------------------------

    report.append("\n### 4.3 PB/VB structural matching\n")

    if matching is not None:
        report.append(
            "The feature-matching output provides the quantitative evidence "
            "for the proposed construction of the masked price-based and "
            "volume-based features."
        )

        report.append(md_table(matching, max_rows=25))

    if lag_matching is not None:
        report.append(
            "\nLag-aware matching was also evaluated to avoid mistaking "
            "similar shapes at different effective windows for exact "
            "contemporaneous matches."
        )

        report.append(md_table(lag_matching, max_rows=20))

    # --------------------------------------------------------
    # Feature dossier
    # --------------------------------------------------------

    report.append("\n### 4.4 Feature dossier\n")

    if dossier_path.exists():
        try:
            dossier = dossier_path.read_text(
                encoding="utf-8",
                errors="replace"
            ).strip()

            if dossier:
                report.append(dossier)
        except Exception as exc:
            report.append(
                f"_Feature dossier could not be read: {exc}_"
            )
    else:
        report.append(
            "The generated feature dossier is not present."
        )

    # --------------------------------------------------------
    # Predictive content
    # --------------------------------------------------------

    report.append("\n### 4.5 Predictive content\n")

    if alpha_rank is not None:
        report.append(
            "Feature alpha is ranked using the forward-return analysis. "
            "Only the leading candidates are reported here; the complete "
            "rank file remains in the project output."
        )

        report.append(md_table(alpha_rank, max_rows=15))

    elif alpha_summary is not None:
        report.append(md_table(alpha_summary, max_rows=15))

    # --------------------------------------------------------
    # Correlation / redundancy
    # --------------------------------------------------------

    report.append("\n### 4.6 Redundancy and effective dimensions\n")

    if correlation is not None:
        report.append(
            "The feature correlation matrix is used to assess redundancy "
            "before interpreting individual features as independent sources "
            "of alpha."
        )

        # Do not print the enormous full matrix.
        numeric = correlation.select_dtypes(include=[np.number])

        if not numeric.empty:
            corr_abs = numeric.abs()

            # Remove diagonal where possible.
            arr = corr_abs.to_numpy()

            if arr.shape[0] == arr.shape[1]:
                np.fill_diagonal(arr, np.nan)

            max_corr = np.nanmax(arr)

            report.append(
                f"The largest off-diagonal absolute correlation represented "
                f"in the matrix is approximately **{max_corr:.4f}**."
            )

    if pca is not None:
        report.append("\n#### PCA evidence\n")
        report.append(md_table(pca, max_rows=20))

    # --------------------------------------------------------
    # Figures
    # --------------------------------------------------------

    for filename, caption in [
        (
            "16_pb_T_correlation.png",
            "PB feature correlation / structural matching evidence."
        ),
        (
            "16_vb_T_correlation.png",
            "VB feature correlation / structural matching evidence."
        ),
        (
            "16_feature_confidence.png",
            "Confidence assigned to feature reconstruction hypotheses."
        ),
        (
            "17_feature_correlation.png",
            "Feature correlation structure."
        ),
        (
            "17_pca_scree.png",
            "PCA scree plot showing effective feature dimensions."
        ),
    ]:
        fig = image(filename, caption)
        if fig:
            report.append("\n" + fig)

    return "\n".join(report)


# ============================================================
# 6. TASK 5
#    STRATEGY DESIGN & BACKTEST
# ============================================================

def task5():
    report = []

    report.append(section("Task 5 — Strategy Design & Backtest"))

    family = read_csv("18_family_summary.csv")
    availability = read_csv("18_feature_availability.csv")
    config = read_csv("18_strategy_config.csv")
    finalists = read_csv("18_strategy_finalists.csv")
    selection = read_csv("18_strategy_selection.csv")
    thresholds = read_csv("18_validation_thresholds.csv")

    performance = read_csv("19_performance_summary.csv")
    daily = read_csv("19_daily_returns.csv")
    train = read_csv("19_train_results.csv")
    validation = read_csv("19_validation_results.csv")
    test = read_csv("19_test_results.csv")
    trade_log = read_csv("19_trade_log.csv")
    threshold_selection = read_csv("19_threshold_selection.csv")

    robustness = read_csv("20_robustness.csv")
    robustness_summary = read_csv("20_robustness_summary.csv")

    # --------------------------------------------------------
    # Strategy construction
    # --------------------------------------------------------

    report.append("### 5.1 Strategy construction\n")

    if selection is not None:
        report.append(
            "The strategy-selection output records the candidate signal "
            "screening and final selection process."
        )

        report.append(md_table(selection, max_rows=15))

    if config is not None:
        report.append("\n#### Final strategy configuration\n")
        report.append(md_table(config, max_rows=20))

    if finalists is not None:
        report.append("\n#### Candidate finalists\n")
        report.append(md_table(finalists, max_rows=15))

    # --------------------------------------------------------
    # Feature availability
    # --------------------------------------------------------

    if availability is not None:
        report.append("\n### 5.2 Feature availability\n")
        report.append(md_table(availability, max_rows=15))

    # --------------------------------------------------------
    # Validation thresholds
    # --------------------------------------------------------

    if thresholds is not None:
        report.append("\n### 5.3 Threshold selection\n")
        report.append(md_table(thresholds, max_rows=20))

    if threshold_selection is not None:
        report.append(
            "\nThe threshold-selection output is kept separate from the "
            "held-out test results to make the parameter-selection boundary "
            "explicit."
        )

    # --------------------------------------------------------
    # No look-ahead / implementation
    # --------------------------------------------------------

    report.append("\n### 5.4 Backtest implementation\n")

    report.append(
        "The strategy is evaluated at a fixed intraday rebalance frequency. "
        "The signal at time *t* is applied to the subsequent execution "
        "interval rather than allowing information from the future bar to "
        "determine the same-bar trade. Transaction costs are explicitly "
        "included rather than using a frictionless return series."
    )

    report.append(
        "\nThe project split separates parameter discovery from held-out "
        "evaluation. In the current strategy pipeline the train/validation "
        "stage is used for selection and calibration, while the final test "
        "period remains untouched until the strategy is fixed."
    )

    # --------------------------------------------------------
    # Performance
    # --------------------------------------------------------

    report.append("\n### 5.5 Performance\n")

    if performance is not None:
        report.append(md_table(performance, max_rows=20))

    # --------------------------------------------------------
    # Train / validation / test
    # --------------------------------------------------------

    report.append("\n### 5.6 Train, validation and test results\n")

    split_tables = []

    for label, df in [
        ("TRAIN", train),
        ("VALIDATION", validation),
        ("TEST", test),
    ]:
        if df is not None and len(df):
            temp = df.copy()

            # If the table already has a split column, keep it.
            if not any(str(c).lower() == "split" for c in temp.columns):
                temp.insert(0, "Split", label)

            split_tables.append(temp)

    if split_tables:
        combined = pd.concat(
            split_tables,
            ignore_index=True,
            sort=False
        )

        report.append(md_table(combined, max_rows=30))

    # --------------------------------------------------------
    # Trade log
    # --------------------------------------------------------

    report.append("\n### 5.7 Trade log\n")

    if trade_log is not None:
        report.append(
            f"The generated trade log contains **{len(trade_log):,}** "
            f"trade records."
        )

        required = [
            "timestamp",
            "side",
            "entry_price",
            "exit_price",
            "quantity",
            "pnl",
            "pnl_pct",
        ]

        available_required = [
            c for c in required if c in trade_log.columns
        ]

        if available_required:
            report.append(
                "\nThe required trade-log fields present in the output are: "
                + ", ".join(f"`{c}`" for c in available_required)
                + "."
            )

        # Report aggregate trade information, NOT the whole trade log.
        pnl_col = find_col(trade_log, ["pnl", "PnL"])
        side_col = find_col(trade_log, ["side", "Side"])

        if pnl_col:
            pnl = pd.to_numeric(
                trade_log[pnl_col], errors="coerce"
            ).dropna()

            if len(pnl):
                report.append(
                    f"\nAggregate logged PnL: **{pnl.sum():.4f}**; "
                    f"mean trade PnL: **{pnl.mean():.4f}**; "
                    f"winning trades: **{(pnl > 0).sum():,}**; "
                    f"losing trades: **{(pnl < 0).sum():,}**."
                )

        if side_col:
            sides = trade_log[side_col].value_counts(dropna=False)

            side_table = (
                sides.rename_axis("Side")
                .reset_index(name="Trades")
            )

            report.append("\nTrade direction breakdown:\n")
            report.append(md_table(side_table))

    # --------------------------------------------------------
    # Robustness
    # --------------------------------------------------------

    report.append("\n### 5.8 Robustness analysis\n")

    if robustness_summary is not None:
        report.append(
            "The robustness summary evaluates whether the observed strategy "
            "performance survives reasonable perturbations of the key "
            "implementation assumptions."
        )

        report.append(md_table(robustness_summary, max_rows=30))

    if robustness is not None:
        # Summarise rather than dumping every scenario.
        report.append(
            f"\nThe detailed robustness grid contains "
            f"**{len(robustness):,} scenario rows**."
        )

        numeric = robustness.select_dtypes(include=[np.number])

        if not numeric.empty:
            rows = []

            for c in numeric.columns:
                vals = pd.to_numeric(
                    robustness[c], errors="coerce"
                ).dropna()

                if len(vals):
                    rows.append({
                        "Metric": c,
                        "Minimum": vals.min(),
                        "Median": vals.median(),
                        "Maximum": vals.max(),
                    })

            if rows:
                summary = pd.DataFrame(rows)
                report.append(md_table(summary, max_rows=20))

    # --------------------------------------------------------
    # Strategy figures
    # --------------------------------------------------------

    for filename, caption in [
        (
            "19_equity_curve.png",
            "Strategy equity curve."
        ),
        (
            "19_drawdown.png",
            "Strategy drawdown."
        ),
        (
            "19_daily_returns.png",
            "Daily strategy returns."
        ),
        (
            "20_cost_robustness.png",
            "Sensitivity of performance to transaction costs."
        ),
        (
            "20_frequency_robustness.png",
            "Sensitivity to rebalancing frequency."
        ),
        (
            "20_threshold_robustness.png",
            "Sensitivity to signal threshold."
        ),
        (
            "20_robustness_summary.png",
            "Overall strategy robustness summary."
        ),
    ]:
        fig = image(filename, caption)
        if fig:
            report.append("\n" + fig)

    report.append(
        "\n### 5.9 Strategy conclusion\n\n"
        "The final strategy should be judged primarily on the held-out "
        "performance and robustness outputs, not on the best in-sample "
        "candidate. The key acceptance criteria are: explicit transaction "
        "costs, a fixed signal/rebalance rule, correct position sizing, "
        "strict information timing, separation of parameter selection from "
        "final testing, and stability under reasonable perturbations."
    )

    return "\n".join(report)


# ============================================================
# 7. FINAL REPORT
# ============================================================

def build_report():
    report = []

    report.append("# Quant Data Challenge — EBX")
    report.append("")
    report.append("## Statistical & Strategy Design Exercise")
    report.append("")
    report.append(
        "> **Final consolidated report generated from the completed "
        "project outputs.**"
    )

    report.append(
        "\nThis report uses only the eligible **Day 1–85** dataset universe "
        "and consolidates the outputs generated by the numbered analysis "
        "notebooks. Large intermediate datasets are not reproduced in the "
        "report; only statistics, conclusions, required tables and the most "
        "informative figures are retained."
    )

    # --------------------------------------------------------
    # Executive summary
    # --------------------------------------------------------

    report.append(section("Executive Summary"))

    report.append(
        "The analysis proceeds from data validation to return "
        "characterisation, distributional and tail analysis, dynamic regime "
        "classification, masked-feature reconstruction, and finally "
        "systematic strategy evaluation. This ordering is intentional: "
        "strategy conclusions are only interpreted after establishing the "
        "statistical properties and information content of the data."
    )

    report.append(
        "\nThe central methodological principles are: use returns rather "
        "than raw price levels for stationarity-sensitive analysis; avoid "
        "cross-day return contamination; distinguish microstructure effects "
        "from economically meaningful dynamics; test rather than assume "
        "Gaussianity; require multiple independent regime diagnostics; "
        "reverse-engineer masked features using empirical evidence; and "
        "evaluate trading performance with costs and out-of-sample controls."
    )

    # --------------------------------------------------------
    # Tasks
    # --------------------------------------------------------

    report.append(task1())
    report.append(task2())
    report.append(task3())
    report.append(task4())
    report.append(task5())

    # --------------------------------------------------------
    # Final methodology / reproducibility
    # --------------------------------------------------------

    report.append(section("Reproducibility & Evidence Map"))

    evidence = pd.DataFrame([
        ["Task 1", "00–04", "Audit, cleaning, returns, ACF, descriptive evidence"],
        ["Task 2", "05–09", "Intraday/distribution/tails/volatility/extremes"],
        ["Task 3", "10–14", "Variance ratio, Hurst, ACF, regimes, transitions"],
        ["Task 4", "15–17", "Feature inventory, forensic matching, alpha, PCA"],
        ["Task 5", "18–20", "Strategy selection, backtest, trade log, robustness"],
    ], columns=["Task", "Notebook range", "Primary evidence"])

    report.append(md_table(evidence))

    report.append(
        "\nThe final submission should include this written report together "
        "with the required supporting deliverables specified by the "
        "competition, especially the **85-row regime table**, the "
        "**feature dossier**, and the **trade log** for Level 2."
    )

    report.append(
        "\nThe report intentionally does **not** reproduce every CSV row. "
        "Intermediate files remain the computational record, while this "
        "document contains the evidence needed to communicate the findings "
        "clearly within the requested report length."
    )

    return "\n\n".join(report)


# ============================================================
# 8. MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("QUANT DATA CHALLENGE — FINAL REPORT GENERATOR")
    print("=" * 70)

    print(f"Project root : {ROOT}")
    print(f"Output dir   : {OUTPUT}")
    print(f"Results dir  : {RESULTS}")
    print(f"Report file  : {REPORT_FILE}")
    print()

    final_report = build_report()

    REPORT_FILE.write_text(
        final_report,
        encoding="utf-8"
    )

    print("=" * 70)
    print("REPORT GENERATED SUCCESSFULLY")
    print("=" * 70)
    print(f"Saved to: {REPORT_FILE}")
    print(f"Characters: {len(final_report):,}")
    print(f"Lines: {final_report.count(chr(10)) + 1:,}")

