# EBX Market Forensics and Strategy Backtest

**Quant Data Challenge — Prepathon 2026: Statistical & Strategy Design Exercise** · August 2026 · solo submission

Full write-up: [`report/EBX_Quant_Report.pdf`](report/EBX_Quant_Report.pdf) (15 pages). Problem statement: [`report/Quant_Data_Challenge_Prepathon_2026.pdf`](report/Quant_Data_Challenge_Prepathon_2026.pdf). Consolidated tables: [`results/results.md`](results/results.md).

## Problem

The data is 1-second price data for a masked equity, "EBX", together with several hundred anonymised features. The challenge has five graded parts:

1. data hygiene
2. return distribution and tails
3. regime classification
4. reverse-engineering the masked features
5. designing and backtesting a strategy with costs

Only Days 1–85 may be used.

## Data

- 70 usable sessions in the Day 1–85 range: Days 1–64 and 80–85. Days 65–79 are absent. In total there are 1,596,012 one-second rows, with 0 missing and 0 duplicate timestamps.
- Each file has 693 columns: Time, Price and 691 masked columns. This project analyses the 288 PB/VB features (216 PB and 72 VB). The other masked families were not analysed.
- The dataset was supplied by the organisers and is **not redistributed** here (`EBX_Dataset/` is gitignored). Some large intermediate CSVs in `output/` are also excluded.

## Method

| Stage | Scripts | What it does |
|---|---|---|
| Hygiene | `01`–`03` | Audits each file, classifies missing values (no blind forward-fill) and computes within-day log returns at 1 s, 1 m and 5 m. |
| Distribution | `04`–`09` | Computes ACFs and intraday seasonality, runs Jarque–Bera and D'Agostino K² tests, counts sigma-event exceedances against a Gaussian, measures volatility clustering and catalogues extreme moves. |
| Regimes | `10`–`14` | Applies a variance ratio (q = 2, 5, 30), the R/S Hurst exponent and lag-k ACF to each day, then a 2-of-3 consensus rule and a transition matrix. |
| Feature forensics | `15`–`16` | Uses first-valid-index fingerprints to infer the window ladder (5 s to 3600 s). Each feature is matched against a library of rolling statistics using Pearson, Spearman, affine fits and lag-correlation. |
| Feature alpha | `17` | Scores each feature as AlphaScore = 0.40·\|ρ_P\| + 0.35·\|ρ_S\| + 0.25·MI against forward returns at 60, 300 and 600 s. Also runs PCA on the 288 features. |
| Strategy | `18`–`19` | Selects a feature using discovery days only (Days 1–54) with a redundancy penalty. The signal is a z-score using train-only mean and std. The threshold is chosen on validation. Max exposure is 1.0, costs are 7.5 bps per unit of turnover, execution lags by 1 minute and the position is reset to flat each day. |
| Robustness | `20` | Sweeps the threshold, costs (5, 7.5 and 10 bps) and rebalance interval (1 and 5 min), each run on train, validation and test. |

**Split.** The split is by day index: train is Days 1–43, validation is Days 44–54 and test is Days 55–64 plus 80–85 (16 days). The day number is a file index, not a confirmed calendar date, so the ordering is assumed to be chronological.

**Leakage fixes made during the project:**

- The first version of the feature ranking used all 70 days, including test days. It was rewritten to use Days 1–54 only. This lowered the selected feature's alpha score from 0.2102 to 0.1999.
- An earlier backtest executed trades at time t on a signal formed at t. This was replaced with a 1-minute execution lag.

## Results

**Statistical findings**

- Returns are far from normal. 425 of 426 normality tests reject at 5%. The pooled 1-minute kurtosis is 16.23.
- At 1 minute there are 6.21× more 3σ moves than a Gaussian predicts (26,674 actual vs 4,298 expected). Day 36 alone accounts for 34.0% of them.
- Hurst at 1 m is about 0.25–0.29 on all 70 days, and VR(5) at 1 m is about 4.83–4.88.
- At 1 m, the regime vote is MIXED_INCONCLUSIVE on all 70 days. At 1 s it gives 47 random-walk, 18 mixed and 5 mean-reverting days.
- **Caveat:** the 1 m and 5 m series are k-second returns sampled on the 1-second grid, so they overlap (n = 1,591,812 at 1 m). Overlap mechanically inflates the ACF (the |r| ACF at lag 1 is 0.963) and pushes the variance ratio towards q. The 1 m and 5 m regime results and tail counts should therefore be read as partly an artefact of how the returns were built, not as a property of the market.

**Feature forensics**

- Of the 288 identity hypotheses, 62 are HIGH confidence, 172 MEDIUM and 54 LOW.
- VB5_Tj matches a rolling range (ρ > 0.9999), and PB10 and PB11 match a rolling max and min (ρ > 0.9998).
- PCA: PC1 explains 26.3% and PC2 15.9% of the variance. 20 PCs explain 88.2%.

**Strategy (VB5_T12, threshold 1.25, 7.5 bps):** a negative out-of-sample result.

| Split | Days | Net return | Sharpe | Sortino | Max DD | Trades |
|---|---|---|---|---|---|---|
| Train | 1–43 | −2.70% | −2.22 | −1.60 | −5.03% | 32 |
| Validation | 44–54 | +1.27% | 5.66 | 6.32 | −0.67% | 6 |
| Test | 55–64, 80–85 | **−0.47%** | **−3.17** | −1.94 | −0.92% | 12 |

- The validation Sharpe of 5.66 came from 11 days and 6 trades, and it did not hold out of sample. The test hit rate was 41.7%, with exposure of 5.9%.
- Robustness on the test split:
  - None of the 5 thresholds gives a positive Sharpe.
  - Neither rebalance interval (1 or 5 min) gives a positive Sharpe.
  - The only positive test scenario is the 5 bps cost case (net +0.063%, Sharpe +0.34).
- The robustness engine's baseline (net −0.536%, Sharpe −2.63) differs from the backtest engine's figures (`19_*`). The two accounting streams have not been reconciled.
- Table 6 of the submitted report prints −1.94 as the test Sharpe. That figure is the Sortino ratio. The source CSV (`output/19_test_results.csv`) gives a Sharpe of −3.17.

**Limitations**

- The test set is small: 16 days and 12 trades.
- Sharpe is annualised from 1-minute returns, with no confidence intervals.
- 864 feature × horizon combinations and 5 thresholds were screened with no multiple-testing correction.
- There is no buy-and-hold or random-signal baseline.

## How to run

The `notebooks/` folder holds plain Python scripts. Run them from the repository root in numeric order. Where a script has several versions, the highest-numbered one is the latest (`16.02`, `17.02`, `18.04`, `19.02.1`).

```bash
pip install pandas numpy scipy statsmodels scikit-learn matplotlib torch
# place day1.csv ... day85.csv in ./EBX_Dataset/ (not included)
python notebooks/01_data_audit.py
python notebooks/02_cleaning_policy.py
# ... through
python notebooks/20_strategy_robust.py
```

`00_dataset_download.py` is the original download helper. It writes to a hard-coded local path, so edit that path before using it. The scripts are self-contained and do not import any local package.

## Repository layout

```
notebooks/   00–20 analysis scripts (hygiene -> distribution -> regimes -> features -> strategy -> robustness)
output/      CSV outputs per stage (audit, tests, regime tables, feature dossier, backtest, robustness)
results/     figures (ACF, QQ, volatility clustering, PCA, equity curve, drawdown, robustness) and results.md
report/      submitted report (EBX_Quant_Report.pdf) and challenge statement
```
