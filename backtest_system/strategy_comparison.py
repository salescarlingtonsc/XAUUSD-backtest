import pandas as pd
import numpy as np

# Load Blind Touch Strategy data
df_blind = pd.read_csv('/home/ubuntu/backtest/touch_events.csv')
df_blind['pb_usd'] = df_blind['pullback_before_bo_pips'] * 0.10

# Load Heikin-Ashi Reversal Strategy data
df_ha = pd.read_csv('/home/ubuntu/backtest/ha_touch_events.csv')
# ha_touch_events already has 'pullback_usd'

def get_stats(df, col):
    return {
        'Count': len(df),
        'Median PB ($)': df[col].median(),
        'P25 PB ($)': df[col].quantile(0.25),
        'P75 PB ($)': df[col].quantile(0.75),
        'Avg PB ($)': df[col].mean(),
        'Max PB ($)': df[col].max()
    }

blind_stats = get_stats(df_blind, 'pb_usd')
ha_stats = get_stats(df_ha, 'pullback_usd')

print("--- GLOBAL COMPARISON (USD) ---")
print(f"{'Metric':<15} | {'Blind Touch':<15} | {'HA Reversal':<15}")
print("-" * 50)
for key in blind_stats.keys():
    b_val = blind_stats[key]
    h_val = ha_stats[key]
    if isinstance(b_val, float):
        print(f"{key:<15} | ${b_val:<14.2f} | ${h_val:<14.2f}")
    else:
        print(f"{key:<15} | {b_val:<15} | {h_val:<15}")

print("\n--- SESSION COMPARISON (MEDIAN PULLBACK $) ---")
print(f"{'Session':<15} | {'Blind Touch':<15} | {'HA Reversal':<15}")
print("-" * 50)
for sess in ['Asian', 'Pre-London', 'London', 'New York']:
    b_med = df_blind[df_blind['session']==sess]['pb_usd'].median()
    h_med = df_ha[df_ha['session']==sess]['pullback_usd'].median()
    print(f"{sess:<15} | ${b_med:<14.2f} | ${h_med:<14.2f}")
