import pandas as pd
import numpy as np

# Load full dataset
df = pd.read_csv('/home/ubuntu/backtest/touch_events.csv')
df['pb_usd'] = df['pullback_before_bo_pips'] * 0.10
df['reward_usd'] = df['reward_pips'] * 0.10

# Search for PEAK WIN RATE
# We will iterate through SL and TP combinations
sl_range = np.arange(10, 100.1, 5.0) # $10 to $100 in $5 steps
tp_range = [5.0, 10.0, 15.0, 20.0] # Small targets for high win rate
sessions = [
    ['Asian', 'Pre-London', 'London', 'New York'], 
    ['Asian', 'Pre-London'], 
    ['Pre-London', 'London'],
    ['Pre-London']
]

results = []

for sess_filter in sessions:
    sub_df = df[df['session'].isin(sess_filter)]
    total_trades = len(sub_df)
    if total_trades == 0: continue
    
    for sl in sl_range:
        for tp in tp_range:
            # Win: Broke out, didn't hit SL, reached TP
            wins = sub_df[(sub_df['broke_out'] == True) & (sub_df['pb_usd'] < sl) & (sub_df['reward_usd'] >= tp)]
            win_count = len(wins)
            win_rate = (win_count / total_trades) * 100
            
            # Loss: Hit SL or didn't break out
            losses = total_trades - win_count
            loss_rate = (losses / total_trades) * 100
            
            # Expectancy: (Win% * TP) - (Loss% * SL)
            expectancy = (win_rate/100 * tp) - (loss_rate/100 * sl)
            
            results.append({
                'sessions': "+".join(sess_filter),
                'sl': sl,
                'tp': tp,
                'win_rate': win_rate,
                'expectancy': expectancy,
                'total_trades': total_trades,
                'rr': tp/sl,
                'net_profit': (win_count * tp) - (losses * sl)
            })

res_df = pd.DataFrame(results)
# Sort by win rate descending
top_win = res_df.sort_values('win_rate', ascending=False).head(20)

print("--- Top 20 Highest Win Rate Setups ---")
print(top_win[['sessions', 'sl', 'tp', 'win_rate', 'expectancy', 'rr', 'net_profit']].to_string(index=False))
