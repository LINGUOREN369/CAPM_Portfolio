# CAPM Portfolio Project

This project implements a full workflow for building and analyzing a portfolio using the Capital Asset Pricing Model (CAPM).

---

## Features
- Download historical price data from Alpha Vantage (or load from local CSVs).
- Compute **simple returns** or **log returns**.
- Estimate stock **betas** relative to a market benchmark (e.g. S&P 500 / SPY).
- Compute **required returns** using CAPM.
- Screen and select stocks for portfolio construction.
- Generate summary tables, charts, and reports.

---

## Data → Metrics → Report

```text
┌────────────────────────────────────────────────────────────────────────────┐
│                          DATA → METRICS → REPORT                           │
└────────────────────────────────────────────────────────────────────────────┘

[1] PRICES
    P_t  (e.g., close prices per day)

        │
        ├───────────────────────────────────────────────────────────┐
        │                                                           │
        ▼                                                           ▼
[2A] SIMPLE RETURNS r_t                                   [2B] LOG RETURNS ℓ_t
     r_t = (P_t / P_{t-1}) - 1                                 ℓ_t = ln(P_t / P_{t-1})

        │                                                           │
        │  (periodic stats)                                         │
        │                                                           │
        ├───────────────┐                                           ├───────────────┐
        │               │                                           │               │
        ▼               ▼                                           ▼               ▼
[3] MEAN           [4] VOL (σ)                                [3] MEAN         [4] VOL (σ)
    μ_simple = avg(r_t)       σ_daily = stdev(r_t)                μ_log = avg(ℓ_t)      σ_daily = stdev(ℓ_t)

        │               │                                           │               │
        │               └─ Annualize volatility:                     │               └─ Annualize volatility:
        │                      σ_ann = σ_daily * √252                │                      σ_ann = σ_daily * √252
        │
        ├─ Annualize mean (expected, arithmetic):                    ├─ Annualize mean (log space):
        │      μ_ann^arith = μ_simple * 252                          │      μ_ann^log = μ_log * 252
        │                                                             │
        └─ CAGR (geometric, performance):                            └─ Convert to simple (CAGR):
               CAGR = (∏(1+r_t))^(1/T) - 1                                CAGR = exp(μ_ann^log) - 1

        │                                                           │
        ├─────────────────────┐                                     ├─────────────────────┐
        │                     │                                     │                     │
        ▼                     ▼                                     ▼                     ▼
[5A] CUMULATIVE / EQUITY CURVE (simple)                   [5B] CUMULATIVE / EQUITY CURVE (log)
     Curve_simple(t) = (1 + r).cumprod() - 1                   Curve_log(t) = exp(ℓ.cumsum()) - 1
     (multiply factors)                                        (sum logs, then exp)

        │                                                           │
        └───────────── both yield the same wealth path if inputs match ────────────────┘


⸻

CAPM Workflow

┌────────────────────────────────────────────────────────────────────────────┐
│                         CAPM (run in either space)                         │
└────────────────────────────────────────────────────────────────────────────┘
Inputs:
  Asset returns (R_i,t), Market returns (R_m,t), Risk-free rate (R_f,t)

Excess returns:
  SIMPLE:  X_t = (R_m,t - R_f,t),  y_t = (R_i,t - R_f,t)
  LOG   :  X_t = (ℓ_m,t - ℓ_f,t),  y_t = (ℓ_i,t - ℓ_f,t)

Regression (OLS):
  y_t = α + β X_t + ε_t

Reporting:
  • Scale α, β as needed (e.g. α × 252 for daily → annual).
  • Expected annual return (reported in simple space):
        CAPM:  E[R_i] ≈ R_f(annual) + β · (E[R_m] - R_f)(annual)
  • If regression is in log space, convert with exp(·) − 1 for presentation.


⸻

📂 Project Structure

CAPM_Portfolio/
├─ README.md
├─ environment.yaml   # optional conda environment
├─ config.yaml        # configuration for data fetch + CAPM run
├─ data/              # CSVs saved here
├─ reports/           # charts/tables
└─ src/
   ├─ fetch_data.py      # fetch raw data (Alpha Vantage, etc.)
   ├─ metrics.py         # returns, annualization, cumulative returns
   ├─ capm.py            # betas, CAPM expected return, summary
   └─ run_capm.py        # the driver script that ties it all together


⸻

Notes on Annualization
	•	Mean returns
	•	Arithmetic mean × 252 → expected annual return (CAPM style).
	•	Log mean × 252, then exp(·) − 1 → CAGR (performance reporting).
	•	Volatility
	•	Always scale by √252 when going from daily → annual.
	•	Annualized metrics are projections: they assume daily return behavior continues in the future.

⸻

⚡ Quick Start

# 1. Install dependencies
## Conda (recommended)
conda env create -f environment.yaml
conda activate atr_sigma_rvol

## Pip (minimal example)
pip install numpy "pandas<2" scipy statsmodels matplotlib pyyaml pillow alpha_vantage

# 2. Set your API key (bash/zsh)
export ALPHA_VANTAGE_API_KEY="your_api_key_here"

# 3. Download data
python src/fetch_data.py

# 4. Run CAPM analysis
python src/run_capm.py


⸻

⚖️ License

MIT

---
