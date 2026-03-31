import pandas as pd
import numpy as np

# Load full dataset of 610 touch events
df = pd.read_csv('/home/ubuntu/backtest/touch_events.csv')

# Convert pips to USD ($0.10 per pip)
df['pb_usd'] = df['pullback_before_bo_pips'] * 0.10
df['reward_usd'] = df['reward_pips'] * 0.10

# Strategy Parameters
SL_USD = 2.50
TP_USD = 5.00

total_touches = len(df)

def run_scalp_analysis(data, label):
    # A win is: Broke out AND pullback was less than SL AND reward reached TP
    wins = data[(data['broke_out'] == True) & (data['pb_usd'] < SL_USD) & (data['reward_usd'] >= TP_USD)]
    win_count = len(wins)
    win_rate = (win_count / len(data)) * 100
    
    # A loss is: Anything else (never broke out OR hit SL first)
    loss_count = len(data) - win_count
    loss_rate = (loss_count / len(data)) * 100
    
    # Expectancy: (Win% * TP) - (Loss% * SL)
    expectancy = (win_rate/100 * TP_USD) - (loss_rate/100 * SL_USD)
    
    # Points analysis (requested by user)
    points_up = win_count * 2 # Each win is 2 units of risk (1:2)
    points_down = loss_count * 1 # Each loss is 1 unit of risk
    net_points = points_up - points_down
    
    # Pullback probability: What % of trades pull back less than SL?
    pb_less_than_sl = len(data[data['pb_usd'] < SL_USD]) / len(data) * 100
    
    return {
        'Label': label,
        'Trades': len(data),
        'Wins': win_count,
        'Losses': loss_count,
        'Win Rate': f"{win_rate:.1f}%",
        'PB < $2.5 (%)': f"{pb_less_than_sl:.1f}%",
        'Expectancy ($)': f"${expectancy:.2f}",
        'Net Points (R)': net_points
    }

results = []
results.append(run_scalp_analysis(df, "All Sessions"))

for sess in ['Asian', 'Pre-London', 'London', 'New York']:
    sess_df = df[df['session'] == sess]
    if len(sess_df) > 0:
        results.append(run_scalp_analysis(sess_df, sess))

res_df = pd.DataFrame(results)
print("--- Micro-Scalp Performance Analysis ($2.50 SL / $5.00 TP) ---")
print(res_df.to_string(index=False))

# Pullback Distribution for the User
print("\n--- Probability of Pullback Depth ($) ---")
pb_levels = [1.0, 2.5, 5.0, 7.5, 10.0]
for pb in pb_levels:
    prob = len(df[df['pb_usd'] < pb]) / len(df) * 100
    print(f"Price pulls back LESS than ${pb:<4}: {prob:>5.1f}%")

# Save for reference
res_df.to_csv('/home/ubuntu/backtest/micro_scalp_stats.csv', index=False)
