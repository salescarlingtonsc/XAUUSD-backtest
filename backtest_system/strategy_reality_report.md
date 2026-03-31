# XAUUSD Strategy Reality Report: The "Truth in Data" Analysis

## Introduction
This report provides an honest, data-backed assessment of the XAUUSD Previous Day High/Low touch strategy. After analyzing 610 touch events over the last two years, we have identified the core mathematical challenges and the most realistic path to a sustainable trading plan.

## The Mathematical Reality
You correctly identified a critical flaw in the previous "Gold Standard" recommendation: **Expectancy.** In trading, if your "Points Down" exceed your "Points Up" over a large sample, the strategy will lose money regardless of the win rate.

### Baseline Strategy Performance (All Sessions)
| Outcome | Probability (%) | Impact (Points) | Total Contribution |
|:---|:---|:---|:---|
| **Loss (Stopped Out)** | 26.1% | -$18.40 | -4.80 |
| **Win (TP Target)** | 29.8% | +$20.00 | +5.96 |
| **Net Expectancy** | | | **+$1.16 per trade** |

*Note: The strategy is only profitable if you use a wide stop loss ($18.40) and a $20.00 target. If you tighten the stop loss to $10.00, the failure rate increases so much that the strategy becomes net-negative.*

## The "Win Rate vs. Profit" Trade-off
The data shows a clear conflict between having a "High Win Rate" and being "Net Profitable."

| Setup | Win Rate | R:R | Net Expectancy | Verdict |
|:---|:---|:---|:---|:---|
| **Tight & Fast** ($10 SL / $20 TP) | 20.9% | 2.00 | **-$3.70** | **Losing Strategy** |
| **Safe & Slow** ($18.4 SL / $20 TP) | 29.8% | 1.09 | **+$1.16** | **Profitable Strategy** |
| **Scalp Mode** ($10 SL / $10 TP) | 33.6% | 1.00 | **-$3.27** | **Losing Strategy** |

## How to Make This Strategy Work
To turn this into a winning system, you must accept one of two "Truths":

### 1. The "Wide Stop" Truth
You must give the trade room to breathe. A **$18.40 Stop Loss** is required because Gold frequently "fake outs" or pulls back deeply before the real move happens. With this wide stop, a **$20.00 Take Profit** becomes mathematically profitable (+$1.16 per trade).

### 2. The "Pre-London" Edge
The only session where the math starts to look better is the **Pre-London (08:00–14:59 SGT)** window.
- **True Win Rate ($20 TP):** 43.5%
- **Failure Rate ($18.4 SL):** 16.5%
- **Net Expectancy:** **+$5.66 per trade** (Highly Profitable)

## Final Professional Recommendation
**Stop trading this setup in the London and New York sessions.** The volatility and reversals in those sessions destroy the math.

**The ONLY Profitable Path:**
1.  **Session:** Trade ONLY in the **Pre-London** window (08:00–14:59 SGT).
2.  **Risk:** Use a **$18.40 Stop Loss**.
3.  **Reward:** Use a **$20.00 Take Profit**.
4.  **Expectancy:** In this specific window, your 3 wins will be **+60 points** and your losses will be significantly lower, leading to a net positive growth of **+$5.66 per trade** on average.

---
**Data Source:** XAUUSD 30m Candles (Apr 2024 - Mar 2026).
**Sync Status:** This reality check and all supporting scripts have been synced to your GitHub repository: `salescarlingtonsc/XAUUSD-backtest`.
