# CAPM Portfolio Project

This project implements a full workflow for building and analyzing a portfolio using the Capital Asset Pricing Model (CAPM).

## Features
- Download historical price data from Alpha Vantage or other sources
- Calculate log or simple returns
- Estimate stock betas relative to a benchmark
- Compute required returns using CAPM
- Screen and select stocks for a portfolio
- Generate a report of results

## Project Structure

CAPM_Portfolio/
├─ README.md
├─ requirements.txt
├─ config.yaml
├─ data/              # CSVs saved here
├─ reports/           # charts/tables
└─ src/
   ├─ download_data.py   # fetch raw data (Alpha Vantage, etc.)
   ├─ metrics.py         # returns, annualization, cumulative returns
   ├─ capm.py            # betas, CAPM expected return, summary
   └─ run_capm.py        # the driver script that ties it all together



## License
MIT
