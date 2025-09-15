import pandas as pd
from metrics import to_returns, annualize_mean_geom, annualize_vol, cumret_log, sharpe_ratio, max_drawdown
import yaml

# Load config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

ticker = config["STOCK_CALCULATION_LIST"][1]
start_date = config.get("CALCULATION_START_DATE", "2020-01-01")
end_date = config.get("CALCULATION_END_DATE", None)

# Load prices
prices = (
    pd.read_csv(f"data/{ticker}_daily.csv", index_col=0, parse_dates=True)[["4. close"]]
      .rename(columns={"4. close": ticker})
)

prices = prices.loc[start_date:end_date].copy().dropna()

# 1) Daily returns (log, for analysis)
r = to_returns(prices[ticker], method="log")

# 2) Annualized stats (CAGR for reporting)
mean_ann = annualize_mean_geom(r.mean(), "1d")
vol_ann  = annualize_vol(r.std(ddof=1), "1d")

# 3) Equity curve
curve = cumret_log(r)

# 4) Risk metrics
sr  = sharpe_ratio(r, rf_periodic=0.0, interval="1d")
mdd = max_drawdown(curve, from_returns=False)

## Beatiful print
print(f"Ticker: {ticker} from {prices.index.min().date()} to {prices.index.max().date()} ({len(prices)} days)")
print(f"CAGR: {mean_ann:.2%}")
print(f"Volatility: {vol_ann:.2%}")
print(f"Sharpe Ratio: {sr:.2f}")
print(f"Max Drawdown: {mdd:.2%}")