import pandas as pd
df = pd.read_csv('/home/ubuntu/backtest/touch_events.csv')
df['pb_usd'] = df['pullback_before_bo_pips'] * 0.1
df['reward_usd'] = df['reward_pips'] * 0.1

# Strategy: SL $10, TP $20
sl = 10
tp = 20

for sess in ['Asian', 'Pre-London', 'London', 'New York']:
    sub = df[df['session'] == sess]
    wins = sub[(sub['broke_out'] == True) & (sub['pb_usd'] < sl) & (sub['reward_usd'] >= tp)]
    win_rate = len(wins) / len(sub) * 100
    exp = (win_rate/100 * tp) - ((100-win_rate)/100 * sl)
    print(f"{sess:12} | Win Rate: {win_rate:5.1f}% | Expectancy: ${exp:6.2f}")
