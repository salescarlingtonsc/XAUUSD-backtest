import pandas as pd
import numpy as np

# Load full dataset of 610 touch events
df = pd.read_csv('/home/ubuntu/backtest/touch_events.csv')

# Convert pips to USD ($0.10 per pip)
df['pb_usd'] = df['pullback_before_bo_pips'] * 0.10
df['reward_usd'] = df['reward_pips'] * 0.10

# Strategy Parameters
SL_USD = 10.0
TP_USD = 30.0

total_touches = len(df)

def run_analysis(data, label):
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
    points_up = win_count * 3 # Each win is 3 units of risk (1:3)
    points_down = loss_count * 1 # Each loss is 1 unit of risk
    net_points = points_up - points_down
    
    return {
        'Label': label,
        'Trades': len(data),
        'Wins': win_count,
        'Losses': loss_count,
        'Win Rate': f"{win_rate:.1f}%",
        'Expectancy ($)': f"${expectancy:.2f}",
        'Net Points (R)': net_points
    }

results = []
results.append(run_analysis(df, "All Sessions"))

for sess in ['Asian', 'Pre-London', 'London', 'New York']:
    sess_df = df[df['session'] == sess]
    if len(sess_df) > 0:
        results.append(run_analysis(sess_df, sess))

res_df = pd.DataFrame(results)
print("--- Strategy 10/30 Performance Analysis ---")
print(res_df.to_string(index=False))

# Save for reference
res_df.to_csv('/home/ubuntu/backtest/strategy_10_30_stats.csv', index=False)
