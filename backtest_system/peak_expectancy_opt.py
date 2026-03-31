import pandas as pd
import numpy as np

# Load full dataset
df = pd.read_csv('/home/ubuntu/backtest/touch_events.csv')
df['pb_usd'] = df['pullback_before_bo_pips'] * 0.10
df['reward_usd'] = df['reward_pips'] * 0.10

# Optimization ranges
sl_range = np.arange(5, 40.1, 2.5) # $5 to $40 in $2.5 steps
tp_range = np.arange(5, 60.1, 5.0) # $5 to $60 in $5 steps
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
            
            expectancy = (win_rate/100 * tp) - (loss_rate/100 * sl)
            
            results.append({
                'sessions': "+".join(sess_filter),
                'sl': sl,
                'tp': tp,
                'win_rate': win_rate,
                'expectancy': expectancy,
                'trades': total_trades,
                'rr': tp/sl
            })

res_df = pd.DataFrame(results)
top_10 = res_df.sort_values('expectancy', ascending=False).head(10)

print("--- Top 10 Optimized Setups by Expectancy ---")
print(top_10[['sessions', 'sl', 'tp', 'win_rate', 'expectancy', 'rr']].to_string(index=False))

# Let's check a specific high-expectancy candidate
best = res_df.iloc[res_df['expectancy'].idxmax()]
print("\n--- Absolute Best Setup Found ---")
print(f"Sessions: {best['sessions']}")
print(f"Stop Loss: ${best['sl']:.2f}")
print(f"Take Profit: ${best['tp']:.2f}")
print(f"Win Rate: {best['win_rate']:.1f}%")
print(f"Expectancy: ${best['expectancy']:.2f} per trade")
print(f"R:R Ratio: {best['rr']:.2f}")
