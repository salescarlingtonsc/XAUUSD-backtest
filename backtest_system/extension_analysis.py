import pandas as pd
import numpy as np

df = pd.read_csv('/home/ubuntu/backtest/touch_events.csv')
bo_df = df[df['broke_out'] == True].copy()
bo_df['reward_usd'] = bo_df['reward_pips'] * 0.10

print("--- Breakout Extension Potential (USD) ---")
print(f"{'Target ($)':<12} | {'Probability (%)':<15}")
print("-" * 30)

targets = [5, 10, 15, 20, 25, 30, 40, 50]
for t in targets:
    prob = (len(bo_df[bo_df['reward_usd'] >= t]) / len(bo_df)) * 100
    print(f"${t:<11.2f} | {prob:<14.1f}%")

print("\n--- Best Session for Extension ($20+) ---")
for sess in ['Asian', 'Pre-London', 'London', 'New York']:
    sub = bo_df[bo_df['session'] == sess]
    if len(sub) > 0:
        prob = (len(sub[sub['reward_usd'] >= 20]) / len(sub)) * 100
        print(f"{sess:12} | {prob:5.1f}%")
