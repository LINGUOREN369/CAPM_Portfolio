import pandas as pd
from metrics import to_returns, annualize_mean_arith, annualize_vol, cumret_log, sharpe_ratio, max_drawdown

# prices: DataFrame with columns per ticker
prices = pd.read_csv("data/AAPL_daily.csv", index_col=0, parse_dates=True)[["4. close"]].rename(columns={"4. close":"AAPL"})

# 1) Returns
r = to_returns(prices["AAPL"], method="log")          # daily log returns

# 2) Annualized stats (CAPM-style)
mean_ann = annualize_mean_arith(r.mean(), "1d")       # arithmetic annualized mean
vol_ann  = annualize_vol(r.std(ddof=1), "1d")         # annualized vol

# 3) Equity curve
curve = cumret_log(r)                                  # growth of $1 - 1

# 4) Risk metrics
sr = sharpe_ratio(r, rf_periodic=0.0, interval="1d")  # annualized Sharpe
mdd = max_drawdown(curve, from_returns=False)



print(f"Mean (ann): {mean_ann:.2%}, Vol (ann): {vol_ann:.2%}, Sharpe: {sr:.2f}, Max Drawdown: {mdd:.2%}")
