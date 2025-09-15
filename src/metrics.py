# src/metrics.py
from __future__ import annotations
from typing import Union
import numpy as np
import pandas as pd

Number = Union[float, int]
SeriesOrDF = Union[pd.Series, pd.DataFrame]

# --- Periods per year ---
ANNUALIZE_MAP = {
    "1d": 252,  # trading days
    "D":  252,  # pandas daily freq
    "1wk": 52,
    "W":   52,
    "1mo": 12,
    "M":   12,
}

def ann_factor(interval: str = "1d") -> int:
    """Return periods-per-year for the given interval key."""
    return ANNUALIZE_MAP.get(interval, 252)

# --- Returns ---
def to_returns(prices: SeriesOrDF, method: str = "log") -> SeriesOrDF:
    """
    Convert price series/dataframe to returns.
    method: "log" (default) or "simple"
    """
    if method == "log":
        rets = np.log(prices / prices.shift(1))
    else:
        rets = prices.pct_change()
    return rets.dropna(how="all")

# --- Annualization ---
def annualize_mean_arith(mean_periodic: SeriesOrDF | Number, interval: str = "1d") -> SeriesOrDF | Number:
    """Arithmetic scaling (expected return per period * k). Good for CAPM-style reporting."""
    k = ann_factor(interval)
    return mean_periodic * k

def annualize_mean_geom(mean_periodic: SeriesOrDF | Number, interval: str = "1d") -> SeriesOrDF | Number:
    """Geometric compounding (CAGR-style). Good for performance reporting."""
    k = ann_factor(interval)
    return (1 + mean_periodic) ** k - 1

def annualize_vol(vol_periodic: SeriesOrDF | Number, interval: str = "1d") -> SeriesOrDF | Number:
    """Volatility scales with sqrt(k)."""
    k = ann_factor(interval)
    return vol_periodic * np.sqrt(k)

# --- Equity curves ---
def cumret_simple(returns: SeriesOrDF) -> SeriesOrDF:
    """Cumulative return from simple returns: (1+r).cumprod() - 1."""
    r = returns.fillna(0)
    return (1 + r).cumprod() - 1

def cumret_log(returns: SeriesOrDF) -> SeriesOrDF:
    """Cumulative return from log returns: exp(cumsum) - 1."""
    r = returns.fillna(0)
    return np.exp(r.cumsum()) - 1

# --- Risk metrics ---
def sharpe_ratio(
    returns: SeriesOrDF,
    rf_periodic: Union[Number, pd.Series] = 0.0,
    interval: str = "1d",
    use_sample: bool = True,
) -> SeriesOrDF | Number:
    """
    Annualized Sharpe using periodic returns:
      Sharpe = (mean(R - Rf) * k) / (std(R - Rf) * sqrt(k))
    If rf_periodic is a scalar, it’s applied to all periods; or pass a Series aligned to index.
    """
    if isinstance(returns, pd.DataFrame):
        # Broadcast rf to each column
        if (rf_periodic, pd.Series):
            isinstanceexcess = returns.sub(rf_periodic, axis=0)
        else:
            excess = returns - rf_periodic
        mean_p = excess.mean()
        std_p  = excess.std(ddof=1 if use_sample else 0)
    else:
        if isinstance(rf_periodic, pd.Series):
            excess = returns - rf_periodic.reindex(returns.index).fillna(0)
        else:
            excess = returns - rf_periodic
        mean_p = excess.mean()
        std_p  = excess.std(ddof=1 if use_sample else 0)

    k = ann_factor(interval)
    mean_ann = mean_p * k
    vol_ann  = std_p * np.sqrt(k)
    return mean_ann / vol_ann.replace(0, np.nan) if isinstance(vol_ann, pd.Series) else (mean_ann / vol_ann if vol_ann != 0 else np.nan)

def max_drawdown(curve_or_returns: SeriesOrDF, from_returns: bool = False, log: bool = False) -> SeriesOrDF | Number:
    """
    Maximum drawdown. If from_returns=True, builds an equity curve first.
      - If log=True, treats returns as log returns.
    Returns a single number for Series, or per-column values for DataFrame.
    """
    if from_returns:
        curve = cumret_log(curve_or_returns) if log else cumret_simple(curve_or_returns)
    else:
        curve = curve_or_returns  # expected to be cumulative return (starts near 0)

    def _mdd(s: pd.Series) -> float:
        wealth = 1 + s.fillna(0)
        peak = wealth.cummax()
        dd = (wealth / peak) - 1
        return dd.min()

    if isinstance(curve, pd.DataFrame):
        return curve.apply(_mdd, axis=0)
    return _mdd(curve)