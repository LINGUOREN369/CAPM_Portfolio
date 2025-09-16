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
    return ANNUALIZE_MAP.get(interval, 252)

# --- Returns ---
def to_returns(prices: SeriesOrDF, method: str = "log") -> SeriesOrDF:
    """Convert price series/dataframe to returns."""
    if method == "log":
        rets = np.log(prices / prices.shift(1))
    else:
        rets = prices.pct_change()
    return rets.dropna(how="all")

# --- Annualization ---
def annualize_mean_arith(mean_periodic: SeriesOrDF | Number, interval: str = "1d") -> SeriesOrDF | Number:
    """Arithmetic scaling (expected return per period * k)."""
    return mean_periodic * ann_factor(interval)

def annualize_mean_geom(mean_periodic: SeriesOrDF | Number, interval: str = "1d") -> SeriesOrDF | Number:
    """Geometric compounding (CAGR)."""
    k = ann_factor(interval)
    return (1 + mean_periodic) ** k - 1

def annualize_vol(vol_periodic: SeriesOrDF | Number, interval: str = "1d") -> SeriesOrDF | Number:
    """Volatility scales with sqrt(k)."""
    return vol_periodic * np.sqrt(ann_factor(interval))

# --- Equity curves ---
def cumret_simple(returns: SeriesOrDF) -> SeriesOrDF:
    """Cumulative return from simple returns: (1+r).cumprod() - 1."""
    r = returns.fillna(0)
    return (1 + r).cumprod() - 1

def cumret_log(returns: SeriesOrDF) -> SeriesOrDF:
    """Cumulative return from log returns: exp(cumsum) - 1."""
    r = returns.fillna(0)
    return np.exp(r.cumsum()) - 1
