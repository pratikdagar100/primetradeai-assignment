# Bitcoin Market Sentiment vs. Hyperliquid Trader Performance

Analysis of how trader behavior and profitability on Hyperliquid shift across
Bitcoin Fear/Greed sentiment regimes.

## Files

| File | Description |
|---|---|
| `Sentiment_Trader_Performance_Analysis.docx` | Full write-up: executive summary, methodology, findings, strategic recommendations, limitations |
| `sentiment_vs_trader_performance.py` | Reproducible analysis script (pandas + matplotlib) |
| `sentiment_performance_overview.png` | 4-panel summary chart (win rate, avg PnL, long/short bias, total PnL by sentiment) |

## Data

- **`fear_greed_index.csv`** — daily Bitcoin sentiment classification (Extreme Fear → Extreme Greed), 2018–2025
- **`historical_data.csv`** — 211,224 Hyperliquid trades across 32 accounts and 246 tokens, May 2023–May 2025

These two source files are not included here; place them in the same folder as
the script before running.

## How to run

```bash
pip install pandas numpy matplotlib
python sentiment_vs_trader_performance.py
```

This regenerates `merged.csv` (trade-level data joined to daily sentiment),
prints the key summary tables to console, and saves the chart PNG.

## Methodology

1. Trades are joined to sentiment by calendar date (99.997% match rate).
2. A trade is "realized" if `Closed PnL != 0`.
3. Win rate = share of realized trades with positive PnL.
4. Directional bias is measured from `Open Long` / `Open Short` events only,
   independent of position-closing activity.

## Key findings

- **Win rate is non-linear across sentiment**: highest in Extreme Greed
  (89.2%) and Fear (87.3%), lowest in Extreme Fear (76.2%) and Greed (76.9%).
- **Positioning is contrarian**: 68.8% of new positions opened during Extreme
  Fear are long; only 45.1% are long during Extreme Greed (54.9% short) —
  traders buy dips and fade euphoria rather than following the crowd.
- **Performance is concentrated**: the top 5 of 32 accounts hold over 60% of
  all positive PnL.
- **Coin-level sensitivity varies widely**: BTC and HYPE stayed profitable in
  every sentiment regime; smaller-cap tokens (e.g. `@107`) swung from a loss
  in Extreme Fear to the single largest PnL figure in the dataset during
  Extreme Greed.

## Limitations

- Small account sample (32 unique accounts) — not necessarily representative.
- No leverage column was present in the trade data, despite being referenced
  in the task brief, so leverage effects could not be analyzed directly.
- The Fear/Greed Index reflects BTC-wide sentiment but is applied here across
  246 tokens with varying correlation to BTC.
