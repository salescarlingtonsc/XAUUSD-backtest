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

# REVERSAL LOGIC:
# Traditional: PDH Touch -> SELL (expect bounce), PDL Touch -> BUY (expect bounce)
# REVERSAL: PDH Touch -> BUY (expect continuation), PDL Touch -> SELL (expect continuation)

# In our dataset:
# 'pb_usd' is the adverse movement against the BO direction (i.e., the "bounce")
# 'reward_usd' is the movement in the BO direction (i.e., the "continuation")

# So for a REVERSAL trade:
# A WIN is when price continues (reward_usd >= TP_USD) without bouncing first (pb_usd < SL_USD)
# A LOSS is when price bounces (pb_usd >= SL_USD) before continuing (reward_usd reached TP)

total_touches = len(df)

def run_reversal_analysis(data, label):
    # For a REVERSAL trade:
    # We enter in the direction of the breakout immediately at the touch.
    # Win: Reward (continuation) reaches TP before Pullback (bounce) reaches SL.
    wins = data[(data['broke_out'] == True) & (data['pb_usd'] < SL_USD) & (data['reward_usd'] >= TP_USD)]
    win_count = len(wins)
    win_rate = (win_count / len(data)) * 100
    
    # Loss: Pullback (bounce) reaches SL before Reward (continuation) reaches TP.
    losses = len(data) - win_count
    loss_rate = (losses / len(data)) * 100
    
    # Expectancy
    expectancy = (win_rate/100 * TP_USD) - (loss_rate/100 * SL_USD)
    
    return {
        'Label': label,
        'Trades': len(data),
        'Wins': win_count,
        'Losses': losses,
        'Win Rate': f"{win_rate:.1f}%",
        'Expectancy ($)': f"${expectancy:.2f}"
    }

results = []
results.append(run_reversal_analysis(df, "All Sessions"))

for sess in ['Asian', 'Pre-London', 'London', 'New York']:
    sess_df = df[df['session'] == sess]
    if len(sess_df) > 0:
        results.append(run_reversal_analysis(sess_df, sess))

res_df = pd.DataFrame(results)
print("--- REVERSAL Strategy Performance Analysis (10/30) ---")
print(res_df.to_string(index=False))

# Now let's try a high win rate reversal (Wide SL, Small TP)
# Win: Continue $10 without bouncing $30
SL_REVERSE = 30.0
TP_REVERSE = 10.0

def run_high_wr_reversal(data, label):
    wins = data[(data['broke_out'] == True) & (data['pb_usd'] < SL_REVERSE) & (data['reward_usd'] >= TP_REVERSE)]
    win_count = len(wins)
    win_rate = (win_count / len(data)) * 100
    losses = len(data) - win_count
    expectancy = (win_rate/100 * TP_REVERSE) - ((1-win_rate/100) * SL_REVERSE)
    return {
        'Label': label,
        'Win Rate': f"{win_rate:.1f}%",
        'Expectancy ($)': f"${expectancy:.2f}"
    }

print("\n--- HIGH WIN RATE REVERSAL Analysis ($30 SL / $10 TP) ---")
results_high = [run_high_wr_reversal(df, "All Sessions")]
for sess in ['Asian', 'Pre-London', 'London', 'New York']:
    sess_df = df[df['session'] == sess]
    if len(sess_df) > 0:
        results_high.append(run_high_wr_reversal(sess_df, sess))
print(pd.DataFrame(results_high).to_string(index=False))
