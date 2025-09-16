# src/run_capm.py
# src/run_capm.py
from __future__ import annotations
from pathlib import Path
import sys

import yaml
import pandas as pd


# Ensure project root is importable when running as a script
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.metrics import to_returns
from src.capm import (
    load_close_prices,
    rf_daily_from_annual,
    build_excess_returns,
    estimate_betas,
    summarize_capm,
)


def _load_config() -> dict:
    with open(ROOT / "config.yaml", "r", encoding="utf-8") as cfg_file:
        return yaml.safe_load(cfg_file)


def main() -> None:
    cfg = _load_config()

    data_dir = ROOT / cfg.get("DATA_PATH", "data")
    tickers = list(cfg["DOWNLOAD_STOCK_TICKER_LIST"])
    market_proxy = cfg.get("MARKET_PROXY", "SPY")
    rf_annual = float(cfg.get("RF_ANNUAL", 0.02))
    mkt_erp_annual = float(cfg.get("MKT_ERP_ANNUAL", 0.05))

    # ---------- Load prices ----------
    # Expect CSVs created by your fetch_data.py: data/{TICKER}_daily.csv
    seen = dict.fromkeys(tickers + [market_proxy])
    tickers_all = list(seen)
    prices = load_close_prices(data_dir, tickers_all)

    # ---------- Daily returns (log by default) ----------
    R = to_returns(prices, method="log")  # use "simple" if you prefer simple returns
    R_assets = R[tickers]
    R_mkt = R[market_proxy]
    if isinstance(R_mkt, pd.DataFrame):
        R_mkt = R_mkt.iloc[:, 0]
    R_mkt = R_mkt.rename("MKT")

    # ---------- Excess returns ----------
    rf_daily = rf_daily_from_annual(rf_annual)
    Rx_assets, Rx_mkt = build_excess_returns(R_assets, R_mkt, rf_daily)

    # ---------- Betas ----------
    betas = estimate_betas(Rx_assets, Rx_mkt)

    # ---------- Summary vs CAPM ----------
    summary = summarize_capm(
        R_assets_daily=R_assets if isinstance(R_assets, pd.DataFrame) else R_assets.to_frame(),
        betas_df=betas,
        rf_annual=rf_annual,
        mkt_erp_annual=mkt_erp_annual,
    )

    # ---------- Output ----------
    pd.set_option("display.width", 120)
    pd.set_option("display.max_columns", 20)

    print("\n=== Betas (daily regression on excess returns) ===")
    print(betas.round(4))

    print("\n=== CAPM vs Historical (annualized) ===")
    print(summary.round(4))

    # Optional: save results
    out_dir = ROOT / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    betas.round(6).to_csv(out_dir / "betas.csv")
    summary.round(6).to_csv(out_dir / "capm_summary.csv")

    print(f"\nSaved: {out_dir/'betas.csv'}")
    print(f"Saved: {out_dir/'capm_summary.csv'}")


if __name__ == "__main__":
    main()
