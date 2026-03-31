# XAUUSD Strategy Reversal Analysis: "Fading the Bounce"

## Introduction
This report evaluates the performance of the **Reversal Strategy** for XAUUSD. The strategy involves doing the exact opposite of a traditional bounce strategy: entering a trade in the direction of the breakout (continuation) immediately upon a touch of the Previous Day High (PDH) or Previous Day Low (PDL).

## The Reversal Concept
In a traditional setup, a PDH touch means "Sell the Bounce." In the **Reversal Setup**, a PDH touch means **"Buy the Continuation"** (expecting the price to break and keep going).

## Statistical Performance (2-Year Backtest)
We analyzed 610 identified touch events to see if flipping the direction increases the win rate.

### Scenario A: The "Contrarian Runner" ($10 SL / $30 TP)
This setup tries to capture a big continuation move with a tight stop.

| Session (SGT) | Trades | Wins | Losses | Win Rate | Expectancy ($) |
|:---|:---|:---|:---|:---|:---|
| **All Sessions** | 610 | 83 | 527 | **13.6%** | **-$4.56** |
| **Asian** | 333 | 54 | 279 | **16.2%** | **-$3.51** |
| **Pre-London** | 129 | 21 | 108 | **16.3%** | **-$3.49** |

### Scenario B: The "High Win Rate" Reversal ($30 SL / $10 TP)
This setup tries to maximize win rate by using a wide stop to capture a small continuation move.

| Session (SGT) | Win Rate | Expectancy ($) |
|:---|:---|:---|
| **All Sessions** | **56.6%** | **-$7.38** |
| **Pre-London** | **65.1%** | **-$3.95** |
| **Asian** | **58.6%** | **-$6.58** |

## Analysis of the Reversal Results
Your hypothesis was: **"Can I increase my win rate to 75% by reversing my trades?"**

### The Win Rate Verdict
- In the **Pre-London session**, the win rate for a continuation move reaches **65.1%** (if you use a wide $30 SL and a small $10 TP).
- However, the win rate **does not reach 75%** on a consistent basis over the 2-year sample.

### The Profitability Trap
Even with a 65% win rate, the strategy remains **net-negative (expectancy of -$3.95)**. This is because when you win, you make $10, but when you lose (the 35% of the time), you lose $30. The "Points Down" still exceed the "Points Up."

## Why the Reversal Strategy Fails on Gold
Gold is a "Mean Reverting" asset at these key levels. 
- When price touches a PDH/PDL, it often "stalls" or "chops" before deciding on a direction.
- This chop hits tight stops ($10) regardless of whether you are buying or selling.
- If you use a wide stop ($30) to survive the chop, the losses are too large to be covered by the small wins.

## Final Conclusion
Reversing the trade direction **does increase the win rate** (from ~13% to ~65%), but it **does not solve the profitability problem.** The market "noise" at these key levels is too high for a simple directional flip to work.

To reach a 75% win rate with positive profit, the data suggests you must add a secondary filter (like a volume spike or a specific 30m candle pattern) rather than just entering at the touch.

---
**Data Source:** XAUUSD 30m Candles (Apr 2024 - Mar 2026).
**Sync Status:** This analysis and the script `strategy_reversal_analysis.py` have been pushed to your GitHub repository: `salescarlingtonsc/XAUUSD-backtest`.
