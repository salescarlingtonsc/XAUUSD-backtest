import pandas as pd
import numpy as np

df = pd.read_csv('/home/ubuntu/backtest/touch_events.csv')
bo_df = df[df['broke_out'] == True].copy()
bo_df['reward_usd'] = bo_df['reward_pips'] * 0.10
bo_df['pb_usd'] = bo_df['pullback_before_bo_pips'] * 0.10

tp_target = 20.00 # Target $20 move
print(f"--- Optimizing SL for Fixed TP of ${tp_target:.2f} ---")
print(f"{'SL ($)':<10} | {'Win Rate (%)':<15} | {'R:R':<10} | {'Expectancy ($)':<15}")
print("-" * 60)

for sl in [5, 7.5, 10, 12.5, 15, 17.5, 20]:
    # A win is when reward >= TP target AND price never hit SL during pullback
    wins = len(bo_df[(bo_df['reward_usd'] >= tp_target) & (bo_df['pb_usd'] < sl)])
    win_rate = (wins / len(bo_df)) * 100
    rr = tp_target / sl
    expectancy = (win_rate/100 * tp_target) - ((100-win_rate)/100 * sl)
    print(f"${sl:<9.2f} | {win_rate:<14.1f}% | {rr:<9.2f} | ${expectancy:<14.2f}")

# Check $10 target as well
tp_target = 10.00
print(f"\n--- Optimizing SL for Fixed TP of ${tp_target:.2f} ---")
print(f"{'SL ($)':<10} | {'Win Rate (%)':<15} | {'R:R':<10} | {'Expectancy ($)':<15}")
print("-" * 60)

for sl in [5, 7.5, 10, 12.5, 15]:
    wins = len(bo_df[(bo_df['reward_usd'] >= tp_target) & (bo_df['pb_usd'] < sl)])
    win_rate = (wins / len(bo_df)) * 100
    rr = tp_target / sl
    expectancy = (win_rate/100 * tp_target) - ((100-win_rate)/100 * sl)
    print(f"${sl:<9.2f} | {win_rate:<14.1f}% | {rr:<9.2f} | ${expectancy:<14.2f}")
