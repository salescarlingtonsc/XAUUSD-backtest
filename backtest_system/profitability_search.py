import pandas as pd
import numpy as np

# Load full dataset
df = pd.read_csv('/home/ubuntu/backtest/touch_events.csv')
df['pb_usd'] = df['pullback_before_bo_pips'] * 0.10
df['reward_usd'] = df['reward_pips'] * 0.10

# Search for POSITIVE expectancy
# We will iterate through SL and TP combinations
sl_range = np.arange(15, 60.1, 2.5) # Wider SL to survive pullbacks
tp_range = np.arange(20, 150.1, 5.0) # Larger TP targets
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
            
            if expectancy > 0:
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
if res_df.empty:
    print("No positive expectancy setup found in this search range.")
else:
    top_profitable = res_df.sort_values('expectancy', ascending=False).head(15)
    print("--- Top 15 PROFITABLE Setups (Expectancy > 0) ---")
    print(top_profitable[['sessions', 'sl', 'tp', 'win_rate', 'expectancy', 'rr', 'net_profit']].to_string(index=False))

    # Let's pick the one with the best balance of Win Rate and Expectancy
    # Usually higher Win Rate is better for psychology
    best_balanced = res_df[res_df['win_rate'] > 30].sort_values('expectancy', ascending=False).head(1)
    if not best_balanced.empty:
        print("\n--- Best Balanced Profitable Setup (Win Rate > 30%) ---")
        print(best_balanced[['sessions', 'sl', 'tp', 'win_rate', 'expectancy', 'rr', 'net_profit']].to_string(index=False))
