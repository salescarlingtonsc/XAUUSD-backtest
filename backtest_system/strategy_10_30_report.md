# XAUUSD Strategy Analysis: The "10/30" Setup ($10 SL / $30 TP)

## Introduction
This report evaluates the performance of the **10/30 Strategy** for XAUUSD. The strategy involves entering a trade immediately upon a touch of the Previous Day High (PDH) or Previous Day Low (PDL) with a fixed **$10.00 Stop Loss** and a **$30.00 Take Profit** (1:3 Risk-to-Reward).

## Statistical Performance (2-Year Backtest)
The analysis was performed on 610 identified touch events from April 2024 to March 2026.

| Session (SGT) | Total Trades | Wins | Losses | Win Rate | Net Points (R) | Expectancy ($) |
|:---|:---|:---|:---|:---|:---|:---|
| **All Sessions** | 610 | 83 | 527 | **13.6%** | **-278 R** | **-$4.56** |
| **Asian** | 333 | 54 | 279 | **16.2%** | **-117 R** | **-$3.51** |
| **Pre-London** | 129 | 21 | 108 | **16.3%** | **-45 R** | **-$3.49** |
| **London** | 57 | 4 | 53 | **7.0%** | **-41 R** | **-$7.19** |
| **New York** | 91 | 4 | 87 | **4.4%** | **-75 R** | **-$8.24** |

## Analysis of the "Points"
You were correct to question the "Points Up" vs. "Points Down" math. Here is the breakdown for the 10/30 setup:

1.  **Points Up:** For every 10 trades, you win ~1.4 times. (1.4 wins x 3 points = **4.2 points up**).
2.  **Points Down:** For every 10 trades, you lose ~8.6 times. (8.6 losses x 1 point = **8.6 points down**).
3.  **Net Result:** You are down **-4.4 points** for every 10 trades.

## Why the Win Rate is Low (13.6%)
The data reveals two main reasons why the $10/$30 setup struggle on XAUUSD:
- **Stop Loss is Too Tight:** 50% of all breakout pullbacks on Gold exceed $9.35. A $10.00 SL is hit by the "noise" of the market before the price has a chance to move in your direction.
- **Target is Too Far:** Only 30.9% of all breakouts ever reach a $30.00 extension. When you combine this with the high failure rate of a tight stop, the "True Win Rate" drops to 13.6%.

## Conclusion
The **10/30 Strategy** is mathematically a losing system for XAUUSD. To make a 1:3 R:R strategy work, you would need a win rate of at least **25%** just to break even. Currently, the market only provides a **16.3%** win rate in the best-performing session (Pre-London).

**Final Recommendation:**
The data suggests that the "10/30" setup is not viable for Gold. To survive the volatility, you must either widen the stop loss (accepting a lower R:R) or identify a more powerful entry signal than a simple PDH/PDL touch.

---
**Data Source:** XAUUSD 30m Candles (Apr 2024 - Mar 2026).
**Sync Status:** This analysis and the script `strategy_10_30_analysis.py` have been pushed to your GitHub repository: `salescarlingtonsc/XAUUSD-backtest`.
