# LEVEL 1 — Data
# Pandas
# NumPy
# data cleaning
# datetime
# multi-file ingestion
# missing values
# duplicates
# outlier detection
# rolling windows
# resampling
# groupby

# LEVEL 2 — EDA
# mean
# median
# variance
# std
# skew
# kurtosis
# histograms
# boxplots
# QQ plots
# correlation
# ACF
# intraday seasonality

# LEVEL 3 — Statistics
# Normal distribution
# CLT intuition
# hypothesis testing
# p-values
# confidence intervals
# Jarque-Bera
# Shapiro-Wilk
# Anderson-Darling
# D'Agostino
# fat tails
# kurtosis
# empirical distributions
# tail index
# Hill estimator

# LEVEL 4 — Time Series
# returns
# stationarity
# autocorrelation
# random walk
# mean reversion
# momentum
# Variance Ratio
# Hurst exponent
# ADF
# regimes
# transition probabilities
# volatility clustering

# LEVEL 5 — Feature Engineering
# rolling return
# rolling mean
# rolling std
# EMA
# momentum
# z-score
# volume features
# lagged features
# forward returns
# correlation
# mutual information
# PCA
# Granger causality

# LEVEL 6 — Quant
# signal construction
# long/short/flat
# position sizing
# transaction costs
# turnover
# slippage assumptions
# backtesting
# look-ahead bias
# train/test split
# Sharpe
# Sortino
# drawdown
# hit rate
# PnL

# LEVEL 7 — Optional ML
# Linear Regression
# Ridge/Lasso
# Random Forest
# Gradient Boosting
# XGBoost
# classification/regression
# walk-forward validation
# feature importance

#____________________________________#
########## DATASET DOWNLOAD ##########

import kagglehub
path = kagglehub.dataset_download("hawkwild/ebx-20-days",output_dir="EBX_Dataset",force_download=True)
print(path)