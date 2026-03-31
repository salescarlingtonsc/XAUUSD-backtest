import pandas as pd
import numpy as np

# Load the events
df = pd.read_csv('/home/ubuntu/backtest/ha_touch_events.csv')

# Since we don't have exit prices (we'd need a target), let's calculate 
# how far it went in the right direction after entry
# To do this accurately, we'd need to go back to the original OHLCV data.

# For now, let's provide clear stats on:
# 1. Distribution of pullbacks ($) before the HA reversal happens
# 2. Session breakdown

stats = []
for sess in ['Asian', 'Pre-London', 'London', 'New York']:
    sub = df[df['session'] == sess]
    if len(sub) > 0:
        stats.append({
            'Session': sess,
            'Count': len(sub),
            'Med Pullback ($)': sub['pullback_usd'].median(),
            'P25 Pullback ($)': sub['pullback_usd'].quantile(0.25),
            'P75 Pullback ($)': sub['pullback_usd'].quantile(0.75),
            'Avg Pullback ($)': sub['pullback_usd'].mean()
        })

stats_df = pd.DataFrame(stats)
stats_df.to_csv('/home/ubuntu/backtest/ha_stats_by_session.csv', index=False)
print("Heikin-Ashi Stats Summary:")
print(stats_df.to_string())
