import pandas as pd
import numpy as np

# Load the main touch events data
df = pd.read_csv('/home/ubuntu/backtest/touch_events.csv')

# Filter only for events that actually broke out (96.6% of them)
bo_df = df[df['broke_out'] == True].copy()

# Convert reward pips to USD ($0.10 per pip)
bo_df['reward_usd'] = bo_df['reward_pips'] * 0.10

# Define TP targets in USD
tp_targets = [5, 10, 15, 20, 30, 40, 50, 75, 100]

print("--- Take Profit (TP) Probability Analysis (USD) ---")
print(f"Total Breakout Events Analyzed: {len(bo_df)}")
print("-" * 50)
print(f"{'Target ($)':<12} | {'Hit Rate (%)':<15} | {'Occurrences':<12}")
print("-" * 50)

results = []
for target in tp_targets:
    hits = len(bo_df[bo_df['reward_usd'] >= target])
    hit_rate = (hits / len(bo_df)) * 100
    print(f"${target:<11.2f} | {hit_rate:<14.1f}% | {hits:<12}")
    results.append({'target_usd': target, 'hit_rate': hit_rate, 'hits': hits})

# Session-specific analysis for $20 target
print("\n--- $20 TP Hit Rate by Session ---")
for sess in ['Asian', 'Pre-London', 'London', 'New York']:
    sess_df = bo_df[bo_df['session'] == sess]
    if len(sess_df) > 0:
        hits = len(sess_df[sess_df['reward_usd'] >= 20])
        rate = (hits / len(sess_df)) * 100
        print(f"{sess:12} | {rate:6.1f}% hit rate ({hits}/{len(sess_df)})")

# Optimal R:R calculation based on $18.40 SL
sl_usd = 18.40
print(f"\n--- R:R Scenarios (based on $18.40 SL) ---")
for target in [20, 30, 40, 50]:
    rr = target / sl_usd
    hit_rate = (len(bo_df[bo_df['reward_usd'] >= target]) / len(bo_df)) * 100
    expectancy = (hit_rate/100 * target) - ((100-hit_rate)/100 * sl_usd)
    print(f"Target ${target}: R:R {rr:.2f} | Hit Rate {hit_rate:.1f}% | Expectancy: ${expectancy:.2f} per trade")

# Save stats
pd.DataFrame(results).to_csv('/home/ubuntu/backtest/tp_stats.csv', index=False)
