# XAUUSD Strategy Expectancy Report: "True Win Rate" Analysis

## Introduction
This report calculates the **True Win Rate** for the XAUUSD Previous Day High/Low touch strategy. A "True Win" is defined as hitting the Take Profit (TP) target **without** first hitting the $18.40 Stop Loss (SL). This analysis is based on 610 identified touch events over the last two years.

## Global Strategy Performance Summary
The table below shows the probability of each outcome for every touch of the previous day's high or low.

| Outcome                   | Probability (%) | Description                                     |
|:--------------------------|:----------------|:------------------------------------------------|
| **Stopped Out ($18.40 SL)** | **26.1%**       | Price hits $18.40 SL before hitting TP or never breaks out. |
| **Hit TP1 ($10.00)**      | **47.7%**       | Hits $10.00 profit *without* hitting the SL first. |
| **Hit TP2 ($20.00)**      | **29.8%**       | Hits $20.00 profit *without* hitting the SL first. |

## Risk Coverage Analysis
To answer your question: **"Can my risk be covered?"**

Mathematically, yes. While you have a **26.1% chance** of losing $18.40, your **combined chance of hitting at least TP1 ($10.00)** is **47.7%**. 

### 1. Mathematical Expectancy (Per Trade)
Expectancy is the average amount you can expect to win or lose per trade over a large sample.

- **Targeting TP1 ($10.00):** Expectancy is **-$0.03**. (Nearly break-even).
- **Targeting TP2 ($20.00):** Expectancy is **+$1.17**. (Profitable over time).

### 2. Session-Specific "True Win Rate" (Targeting TP1)
Your win rate varies significantly depending on the Singapore Time session:

| Session (SGT)   | True Win Rate (%) | Analysis                                      |
|:----------------|:------------------|:----------------------------------------------|
| **Pre-London**  | **55.0%**         | **Best Performance.** Most consistent breakout extension. |
| **Asian**       | **49.8%**         | **High Frequency.** Most trades occur here with solid win rates. |
| **London**      | **43.9%**         | Moderate win rate; breakouts can be more volatile. |
| **New York**    | **31.9%**         | **Highest Risk.** Price often reverses aggressively in NY. |

## Final Conclusion and Strategy Recommendation

1.  **Risk is Covered:** The strategy is mathematically profitable if you target **TP2 ($20.00)** or use a split-exit strategy (taking half profit at TP1 and letting the rest run to TP2).
2.  **The "Pre-London" Edge:** You should prioritize trades during the **08:00–14:59 SGT** window. This session has the highest "True Win Rate" (55%), meaning your risk is most effectively covered during these hours.
3.  **New York Caution:** Avoid or reduce risk during the New York session (after 20:00 SGT), as the "True Win Rate" drops significantly to 31.9%.

**Final Recommendation:**
- **Entry:** Touch of PDH/PDL.
- **Stop Loss:** $18.40.
- **Take Profit:** Target **$20.00** for the best long-term profitability.
- **Focus:** Asian and Pre-London sessions for the highest probability of success.
