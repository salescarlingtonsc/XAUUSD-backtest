import pandas as pd
import numpy as np

# Load the full dataset (all 610 events)
df = pd.read_csv('/home/ubuntu/backtest/touch_events.csv')

# Convert pips to USD
df['pb_usd'] = df['pullback_before_bo_pips'] * 0.10
df['reward_usd'] = df['reward_pips'] * 0.10

# Fixed Strategy Parameters
SL_USD = 18.40
TP1_USD = 10.00
TP2_USD = 20.00

# Total trades to consider (those that broke out + those that didn't)
# Actually, we should consider all 610 touches.
total_touches = len(df)

print(f"--- Strategy Expectancy Analysis (Total Touches: {total_touches}) ---")
print(f"Fixed SL: ${SL_USD:.2f} | TP1: ${TP1_USD:.2f} | TP2: ${TP2_USD:.2f}")
print("-" * 60)

# 1. Failure Case: Price pulls back >= $18.40 before breakout or never breaks out
# Note: 'broke_out' is False if it didn't break out same day.
failures = df[(df['pb_usd'] >= SL_USD) | (df['broke_out'] == False)]
failure_count = len(failures)
failure_rate = (failure_count / total_touches) * 100

# 2. Success Case for TP1: Price hits $10.00 WITHOUT hitting $18.40 SL first
tp1_success = df[(df['broke_out'] == True) & (df['pb_usd'] < SL_USD) & (df['reward_usd'] >= TP1_USD)]
tp1_count = len(tp1_success)
tp1_win_rate = (tp1_count / total_touches) * 100

# 3. Success Case for TP2: Price hits $20.00 WITHOUT hitting $18.40 SL first
tp2_success = df[(df['broke_out'] == True) & (df['pb_usd'] < SL_USD) & (df['reward_usd'] >= TP2_USD)]
tp2_count = len(tp2_success)
tp2_win_rate = (tp2_count / total_touches) * 100

print(f"{'Outcome':<25} | {'Count':<10} | {'True Prob (%)':<15}")
print("-" * 60)
print(f"{'Stopped Out ($18.40 SL)':<25} | {failure_count:<10} | {failure_rate:<15.1f}%")
print(f"{'Hit TP1 ($10.00)':<25} | {tp1_count:<10} | {tp1_win_rate:<15.1f}%")
print(f"{'Hit TP2 ($20.00)':<25} | {tp2_count:<10} | {tp2_win_rate:<15.1f}%")

# 4. Expectancy Calculation
# If we split the trade 50/50 between TP1 and TP2:
# Outcome A: Lose $18.40 (Failure Rate)
# Outcome B: Win avg of ($10 + $20)/2 = $15 (TP2 Win Rate)
# Outcome C: Win $10 on half and lose $18.40 on half (TP1 Win Rate - TP2 Win Rate)

# Simpler expectancy: 
# If TP1 is target: (TP1_Win_Rate * $10) - (Failure_Rate * $18.40)
exp_tp1 = (tp1_win_rate/100 * TP1_USD) - (failure_rate/100 * SL_USD)
exp_tp2 = (tp2_win_rate/100 * TP2_USD) - (failure_rate/100 * SL_USD)

print(f"\n--- Mathematical Expectancy (per trade) ---")
print(f"Targeting only TP1 ($10): ${exp_tp1:.2f}")
print(f"Targeting only TP2 ($20): ${exp_tp2:.2f}")

# 5. Session Breakdown for True Win Rate
print(f"\n--- True Win Rate (TP1) by Session ---")
for sess in ['Asian', 'Pre-London', 'London', 'New York']:
    sess_all = df[df['session'] == sess]
    sess_tp1 = sess_all[(sess_all['broke_out'] == True) & (sess_all['pb_usd'] < SL_USD) & (sess_all['reward_usd'] >= TP1_USD)]
    rate = (len(sess_tp1) / len(sess_all)) * 100
    print(f"{sess:12} | {rate:5.1f}% ({len(sess_tp1)}/{len(sess_all)})")
