"""
Bitcoin Market Sentiment vs. Hyperliquid Trader Performance
=============================================================
Merges the Fear/Greed Index with historical Hyperliquid trade data to explore
how trader behavior and profitability shift across sentiment regimes.

Inputs:
    fear_greed_index.csv   - daily sentiment classification (Fear/Greed etc.)
    historical_data.csv    - per-trade execution data from Hyperliquid

Output:
    merged.csv                              - trade-level data joined with sentiment
    sentiment_performance_overview.png      - 4-panel summary chart
    Console output                          - key summary tables
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

FG_PATH = "fear_greed_index.csv"
HIST_PATH = "historical_data.csv"
SENTIMENT_ORDER = ["Extreme Fear", "Fear", "Neutral", "Greed", "Extreme Greed"]


def load_and_merge():
    hist = pd.read_csv(HIST_PATH)
    fg = pd.read_csv(FG_PATH)

    # Normalize dates so trades can be joined to a daily sentiment reading
    hist["dt"] = pd.to_datetime(hist["Timestamp IST"], format="%d-%m-%Y %H:%M")
    hist["date"] = hist["dt"].dt.date
    fg["date"] = pd.to_datetime(fg["date"]).dt.date

    merged = hist.merge(fg[["date", "value", "classification"]], on="date", how="left")
    merged = merged.dropna(subset=["classification"])
    merged["classification"] = pd.Categorical(
        merged["classification"], categories=SENTIMENT_ORDER, ordered=True
    )
    return merged


def realized_trades(merged):
    """Trades with a non-zero Closed PnL represent an actual realized gain/loss."""
    return merged[merged["Closed PnL"] != 0].copy()


def win_rate(pnl_series):
    return (pnl_series > 0).mean()


def summarize(merged):
    realized = realized_trades(merged)

    print("=== Win rate & PnL by sentiment ===")
    summary = realized.groupby("classification", observed=True)["Closed PnL"].agg(
        trades="size", win_rate=win_rate, avg_pnl="mean", total_pnl="sum"
    )
    print(summary, "\n")

    print("=== Long vs. short bias in newly opened positions ===")
    opens = merged[merged["Direction"].isin(["Open Long", "Open Short"])]
    dir_counts = opens.groupby(["classification", "Direction"], observed=True).size().unstack()
    dir_counts["pct_long"] = dir_counts["Open Long"] / (
        dir_counts["Open Long"] + dir_counts["Open Short"]
    ) * 100
    print(dir_counts, "\n")

    print("=== Account concentration ===")
    acct_pnl = realized.groupby("Account")["Closed PnL"].sum().sort_values(ascending=False)
    top5_share = acct_pnl.head(5).sum() / acct_pnl[acct_pnl > 0].sum()
    print(f"Top 5 of {len(acct_pnl)} accounts hold {top5_share:.1%} of total positive PnL\n")

    print("=== Top coins by volume, PnL by sentiment ===")
    top_coins = merged.groupby("Coin")["Size USD"].sum().sort_values(ascending=False).head(5).index
    for coin in top_coins:
        sub = realized[realized["Coin"] == coin]
        print(f"--- {coin} ---")
        print(sub.groupby("classification", observed=True)["Closed PnL"].agg(
            n="size", win_rate=win_rate, total="sum"
        ))
        print()

    return summary, dir_counts


def plot_overview(merged, out_path="sentiment_performance_overview.png"):
    realized = realized_trades(merged)
    colors = ["#8B0000", "#D2691E", "#808080", "#228B22", "#006400"]

    fig, axes = plt.subplots(2, 2, figsize=(13, 10))

    wr = realized.groupby("classification", observed=True)["Closed PnL"].apply(win_rate)
    axes[0, 0].bar(SENTIMENT_ORDER, wr.reindex(SENTIMENT_ORDER) * 100, color=colors)
    axes[0, 0].set_title("Win Rate by Market Sentiment")
    axes[0, 0].set_ylabel("Win Rate (%)")
    axes[0, 0].set_ylim(0, 100)

    avgp = realized.groupby("classification", observed=True)["Closed PnL"].mean()
    axes[0, 1].bar(SENTIMENT_ORDER, avgp.reindex(SENTIMENT_ORDER), color=colors)
    axes[0, 1].set_title("Average PnL per Trade by Sentiment")
    axes[0, 1].set_ylabel("Avg Closed PnL (USD)")

    opens = merged[merged["Direction"].isin(["Open Long", "Open Short"])]
    dir_counts = opens.groupby(["classification", "Direction"], observed=True).size().unstack()
    pct_long = (dir_counts["Open Long"] / (dir_counts["Open Long"] + dir_counts["Open Short"]) * 100)
    axes[1, 0].bar(SENTIMENT_ORDER, pct_long.reindex(SENTIMENT_ORDER), color=colors)
    axes[1, 0].axhline(50, color="black", linestyle="--", linewidth=1)
    axes[1, 0].set_title("% of New Positions that are LONG, by Sentiment")
    axes[1, 0].set_ylabel("% Long")

    totp = realized.groupby("classification", observed=True)["Closed PnL"].sum()
    axes[1, 1].bar(SENTIMENT_ORDER, totp.reindex(SENTIMENT_ORDER) / 1e6, color=colors)
    axes[1, 1].set_title("Total Realized PnL by Sentiment")
    axes[1, 1].set_ylabel("Total PnL (Million USD)")

    for ax in axes.flat:
        ax.tick_params(axis="x", rotation=20)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    print(f"Saved chart to {out_path}")


if __name__ == "__main__":
    merged = load_and_merge()
    merged.to_csv("merged.csv", index=False)
    summarize(merged)
    plot_overview(merged)
