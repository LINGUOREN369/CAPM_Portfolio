# src/capm.py
from __future__ import annotations
import numpy as np
import pandas as pd
import statsmodels.api as sm
from pathlib import Path
from typing import List, Tuple
from .metrics import to_returns, annualize_mean_arith

# -------- I/O helpers --------
def load_close_prices(data_dir: Path, tickers: List[str]) -> pd.DataFrame:
    """
    Load 'Close' column for each ticker from data/{TICKER}_daily.csv (Alpha Vantage format).
    Returns a DataFrame with columns named by ticker.
    """
    frames = []
    for t in tickers:
        fp = data_dir / f"{t}_daily.csv"
        df = pd.read_csv(fp, index_col=0, parse_dates=True)
        # Alpha Vantage daily CSV columns are '1. open','2. high','3. low','4. close','5. volume'
        col = "4. close" if "4. close" in df.columns else "Close"
        frames.append(df[[col]].rename(columns={col: t}))
    out = pd.concat(frames, axis=1).sort_index()
    return out.dropna(how="all")

# -------- Excess returns + RF --------
def rf_daily_from_annual(rf_annual: float) -> float:
    """
    Convert constant annual risk-free rate to effective daily rate (~252 trading days).
    """
    return (1 + rf_annual) ** (1/252) - 1

def build_excess_returns(
    R_assets: pd.DataFrame, R_mkt: pd.Series, rf_daily: float | pd.Series
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Subtract risk-free (per-period) from asset and market returns.
    rf_daily can be a scalar or a Series aligned to the index.
    """
    if isinstance(rf_daily, pd.Series):
        rf_series = rf_daily.reindex(R_assets.index).fillna(method="ffill").fillna(0)
    else:
        rf_series = pd.Series(rf_daily, index=R_assets.index)

    Rx_assets = R_assets.sub(rf_series, axis=0)
    Rx_mkt    = R_mkt.sub(rf_series, axis=0)
    return Rx_assets, Rx_mkt

# -------- Beta estimation --------
def estimate_betas(Rx_assets: pd.DataFrame, Rx_mkt: pd.Series) -> pd.DataFrame:
    """
    OLS per asset: (R_i - R_f) = alpha + beta*(R_m - R_f) + eps
    Returns a DataFrame with alpha, beta, R2.
    """
    X = sm.add_constant(Rx_mkt.rename("MKT"))
    alphas, betas, r2 = {}, {}, {}
    for col in Rx_assets.columns:
        y = Rx_assets[col].dropna()
        Xy = X.loc[y.index]
        res = sm.OLS(y, Xy).fit()
        alphas[col] = res.params.get("const", np.nan)
        betas[col]  = res.params.get("MKT",  np.nan)
        r2[col]     = res.rsquared
    out = pd.DataFrame({"alpha": alphas, "beta": betas, "R2": r2})
    return out[["alpha", "beta", "R2"]].sort_index()

# -------- CAPM expected return + summary --------
def capm_expected_return(beta: float, rf_annual: float, mkt_erp_annual: float) -> float:
    """
    E[R_i] = R_f + beta * (E[R_m] - R_f) = R_f + beta * ERP
    """
    return rf_annual + beta * mkt_erp_annual

def summarize_capm(
    R_assets_daily: pd.DataFrame,
    betas_df: pd.DataFrame,
    rf_annual: float = 0.02,
    mkt_erp_annual: float = 0.05,
) -> pd.DataFrame:
    """
    Compare historical annualized mean (arithmetic) vs CAPM expected (annual).
    Also reports annualized alpha (alpha * 252 for daily data).
    """
    hist_mean_daily   = R_assets_daily.mean()
    hist_mean_annual  = annualize_mean_arith(hist_mean_daily, "1d")

    exp_ret_capm = betas_df["beta"].apply(lambda b: capm_expected_return(b, rf_annual, mkt_erp_annual))
    alpha_ann    = betas_df["alpha"] * 252  # scale daily alpha to annual

    out = pd.DataFrame({
        "beta": betas_df["beta"],
        "alpha_ann": alpha_ann,
        "hist_ann_mean": hist_mean_annual,
        "capm_ann_exp": exp_ret_capm,
    }).reindex(betas_df.index)
    out["gap_hist_minus_capm"] = out["hist_ann_mean"] - out["capm_ann_exp"]
    return out.sort_values("gap_hist_minus_capm", ascending=False)