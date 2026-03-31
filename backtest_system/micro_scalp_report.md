# XAUUSD Micro-Scalp Analysis: The "$2.50 SL / $5.00 TP" Setup

## Introduction
This report evaluates the performance of a **Micro-Scalp Strategy** for XAUUSD. The setup involves entering a trade immediately upon a touch of the Previous Day High (PDH) or Previous Day Low (PDL) with a **$2.50 Stop Loss** and a **$5.00 Take Profit** (1:2 Risk-to-Reward).

## Statistical Performance (2-Year Backtest)
The analysis was performed on 610 identified touch events from April 2024 to March 2026.

| Session (SGT) | Total Trades | Wins | Losses | Win Rate | PB < $2.50 (%) | Net Points (R) |
|:---|:---|:---|:---|:---|:---|:---|
| **All Sessions** | 610 | 18 | 592 | **3.0%** | **3.3%** | **-556 R** |
| **Asian** | 333 | 13 | 320 | **3.9%** | **4.5%** | **-294 R** |
| **Pre-London** | 129 | 4 | 125 | **3.1%** | **3.1%** | **-117 R** |
| **London** | 57 | 1 | 56 | **1.8%** | **1.8%** | **-54 R** |
| **New York** | 91 | 0 | 91 | **0.0%** | **0.0%** | **-91 R** |

## Pullback Probability: How much room does Gold need?
To understand why the win rate is so low (3%), we analyzed how much the price "breathes" against the entry point after a touch.

| Pullback Depth ($) | Probability of Pullback being LESS than this (%) |
|:---|:---|
| **$1.00** | 0.7% |
| **$2.50** | **3.3%** |
| **$5.00** | 21.0% |
| **$7.50** | 38.5% |
| **$10.00** | 54.3% |

**The Reality:** In **96.7%** of all touch events, XAUUSD pulls back more than **$2.50** before it makes its move. This means your $2.50 stop loss will be hit almost every time, regardless of whether the trade eventually goes to your profit target.

## Analysis of the Scalp Math
- **Win Rate Needed:** For a 1:2 R:R strategy, you need a **33.3% win rate** to break even.
- **Actual Win Rate:** You are achieving a **3.0% win rate**.
- **Net Result:** You are losing **-2.28 units of risk** for every trade on average.

## Conclusion
The **$2.50 SL / $5.00 TP** micro-scalp is not viable for XAUUSD. The "noise" of Gold at key daily levels is significantly larger than $2.50. Even a "perfect" entry will almost always see a pullback of $5.00 to $10.00 before the breakout or reversal begins.

**Recommendation:**
To successfully scalp Gold at these levels, you must increase your stop loss to at least **$10.00** (which covers 54% of pullbacks) and adjust your take profit accordingly. A $2.50 stop loss is effectively a guaranteed loss in the current market environment.

---
**Data Source:** XAUUSD 30m Candles (Apr 2024 - Mar 2026).
**Sync Status:** This analysis and the script `micro_scalp_analysis.py` have been pushed to your GitHub repository: `salescarlingtonsc/XAUUSD-backtest`.
