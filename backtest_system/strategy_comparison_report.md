# XAUUSD Backtest Strategy Comparison: Blind Touch vs. Heikin-Ashi Reversal

## Introduction
This report compares two distinct entry strategies for trading XAUUSD (Gold) based on touches of the Previous Day High (PDH) or Previous Day Low (PDL) on a 30-minute timeframe. The objective is to evaluate their performance, particularly concerning the depth of price pullback (risk) and the number of identified trading opportunities.

**Strategy 1: Blind Touch Entry**
This strategy involves entering a trade immediately upon the price wick touching the PDH or PDL. For a PDH touch, a short position is considered, and for a PDL touch, a long position is considered. The pullback is measured from the touch point to the lowest point before a breakout (for PDH) or highest point before a breakout (for PDL).

**Strategy 2: Heikin-Ashi Reversal Entry**
This strategy refines the entry by waiting for a confirmation of reversal using Heikin-Ashi (HA) candles. After a PDH/PDL touch, the trader waits for a pullback and enters only when the Heikin-Ashi candle changes color in the direction of the expected reversal (e.g., a green HA candle after a PDH touch pullback for a long entry, or a red HA candle after a PDL touch pullback for a short entry). The pullback is measured from the touch point to the entry point (close of the first reversal HA candle).

## Global Comparison of Pullback Characteristics (USD)
This table summarizes the key pullback statistics for both strategies across all trading sessions, measured in USD ($0.10 per pip).

| Metric            | Blind Touch Entry | Heikin-Ashi Reversal Entry |
|:------------------|:------------------|:---------------------------|
| **Total Events**  | 610               | 109                        |
| **Median Pullback ($)** | $9.35             | $24.50                     |
| **P25 Pullback ($)**    | $5.60             | $0.00                      |
| **P75 Pullback ($)**    | $18.40            | $50.50                     |
| **Average Pullback ($)**| $14.59            | $39.64                     |
| **Maximum Pullback ($)**| $279.40           | $425.30                    |

## Session-Specific Median Pullback Comparison (USD)
This table breaks down the median pullback for each strategy by trading session (Singapore Time).

| Session (SGT)   | Blind Touch Median PB ($) | HA Reversal Median PB ($) |
|:----------------|:--------------------------|:--------------------------|
| **Asian**       | $7.90                     | $44.80                    |
| **Pre-London**  | $9.10                     | $29.70                    |
| **London**      | $9.20                     | $3.20                     |
| **New York**    | $15.20                    | $0.00                     |

## Analysis and Recommendations

### Number of Opportunities
The **Blind Touch Entry** strategy identifies significantly more trading opportunities (610 events) compared to the **Heikin-Ashi Reversal Entry** (109 events). This is expected, as the HA reversal strategy adds a filtering condition, reducing the frequency of entries but potentially increasing their quality.

### Pullback Depth (Risk)
- **Blind Touch:** The median pullback is **$9.35**, with 75% of pullbacks being less than **$18.40**. This suggests that a stop loss placed around $18.40 from the entry level would cover most initial adverse movements.
- **Heikin-Ashi Reversal:** The median pullback for this strategy is **$24.50**, which is considerably higher than the blind touch. This indicates that by waiting for the HA reversal, you are often entering *after* a larger initial move against the touch level has already occurred. The P75 pullback is **$50.50**, implying a larger required stop loss for this strategy to be effective.

### Session-Specific Insights
- **Asian Session:** The HA Reversal strategy shows a much larger median pullback ($44.80) compared to the Blind Touch ($7.90). This suggests that in the Asian session, waiting for an HA reversal means enduring a more significant initial adverse movement.
- **London Session:** The HA Reversal strategy has a very small median pullback ($3.20), indicating that when an HA reversal occurs in London, it tends to happen very close to the initial touch point, offering potentially tighter stop losses.
- **New York Session:** The HA Reversal strategy shows a $0.00 median pullback, suggesting that if an HA reversal signal appears, it's often right at the touch level or with minimal adverse movement. However, the overall R:R for New York was lower in the previous analysis, so this needs to be considered.

### Conclusion

- If your priority is **frequency of trades** and you are comfortable with a **tighter, more consistent stop loss** (around $18.40), the **Blind Touch Entry** strategy provides more opportunities with a predictable pullback range.

- If your priority is **higher quality entries with confirmation** and you are willing to accept **fewer trades and potentially larger initial pullbacks** (requiring a stop loss around $50.50), the **Heikin-Ashi Reversal Entry** strategy might be suitable. However, the larger median pullback for HA reversal (especially in Asian session) implies that while you wait for confirmation, the price might have already moved significantly against the initial touch, potentially reducing your overall R:R if your target remains fixed.

**Recommendation:** For a more robust R:R profile, the **Blind Touch Entry** with a well-defined stop loss based on the $18.40 (75th percentile) pullback seems to offer a better balance of opportunity and risk management. The Heikin-Ashi Reversal strategy, while providing confirmation, appears to lead to entries after a larger adverse move has already occurred, which could negatively impact the risk-to-reward ratio unless targets are also adjusted significantly.

## Methodology

Both strategies were backtested on XAUUSD using 30-minute historical data from April 2024 to March 2026. Previous Day High/Low levels were calculated based on the daily OHLCV data. Pullbacks were measured in USD, assuming a pip size of $0.10 for XAUUSD. The Heikin-Ashi candles were calculated from the standard OHLC data. All times are in Singapore Time (SGT, UTC+8).
