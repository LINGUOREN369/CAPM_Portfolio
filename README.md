# CAPM Portfolio Project

A complete, reproducible workflow for sourcing market data, estimating risk, and constructing portfolios with the Capital Asset Pricing Model (CAPM). The repository packages data acquisition, factor calculations, and reporting so you can move from raw quotes to an investment-ready summary in a single run.

## Table of Contents
- [Capabilities](#capabilities)
- [Project Structure](#project-structure)
- [Workflow Overview](#workflow-overview)
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Configuration](#configuration)
- [Running the Pipeline](#running-the-pipeline)
- [Outputs](#outputs)
- [License](#license)

## Capabilities
- Retrieve daily price history from Alpha Vantage or load existing CSV files.
- Calculate simple and log returns, annualized statistics, and cumulative performance curves.
- Estimate asset betas against a configurable market benchmark and compute CAPM expected returns.
- Screen and rank securities using configurable rules before portfolio construction.
- Produce tabular and visual reports that summarize market assumptions, betas, and projected performance.

## Project Structure
```
CAPM_Portfolio/
├─ README.md
├─ config.yaml            # Runtime configuration for data sources and portfolio settings
├─ environment.yaml       # Optional Conda environment specification
├─ data/                  # Cached price history and intermediate CSV files
├─ reports/               # Generated charts, tables, and documentation
└─ src/
   ├─ fetch_data.py       # Data ingestion from Alpha Vantage or local files
   ├─ metrics.py          # Return calculations, annualization, cumulative curves
   ├─ capm.py             # Beta estimation, CAPM projections, summarization
   └─ run_capm.py         # Orchestrates the full workflow end to end
```

## Workflow Overview
1. **Data acquisition**: Pull daily close prices for target equities and the market benchmark.
2. **Return engineering**: Compute simple and log returns, then annualize mean and volatility.
3. **Risk modeling**: Estimate alpha and beta via ordinary least squares on excess returns.
4. **Portfolio insights**: Derive expected returns with CAPM, apply filters, and confirm allocations.
5. **Reporting**: Assemble charts and tables for both exploratory review and presentation.

## Prerequisites
- Python 3.9 or later
- An Alpha Vantage API key (only required when fetching fresh market data)
- Optional: Conda for managing the provided environment specification

## Environment Setup
Using Conda (recommended):
```bash
conda env create -f environment.yaml
conda activate atr_sigma_rvol
```

Using pip and `venv`:
```bash
python -m venv .venv
source .venv/bin/activate
pip install numpy "pandas<2" scipy statsmodels matplotlib pyyaml pillow alpha_vantage
```

## Configuration
- Copy `config.yaml` and update the tickers, benchmark symbol, and data handling preferences.
- Set the Alpha Vantage API key in your shell before fetching data:
  ```bash
  export ALPHA_VANTAGE_API_KEY="your_api_key_here"
  ```
- Place any pre-downloaded CSV files inside `data/` and set the configuration to use local data.

## Running the Pipeline
Fetch data (skipped automatically if cached files are up to date):
```bash
python src/fetch_data.py
```
Run the CAPM analysis and generate reports:
```bash
python src/run_capm.py
```
Both scripts accept command line arguments for overrides such as start and end dates. Use the `--help` flag on each command to view the available options.

## Outputs
- `data/`: Stores raw prices, engineered returns, and any cached artifacts for reproducibility.
- `reports/`: Contains generated plots (PNG) and tables (CSV, HTML) summarizing CAPM metrics and portfolio performance.
- Console logs document progress, decisions (for example, skipped downloads), and any validation warnings.

## License
Released under the MIT License. See the `LICENSE` file for full terms.
