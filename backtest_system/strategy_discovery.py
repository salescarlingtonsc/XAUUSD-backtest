import pandas as pd
import numpy as np
import yfinance as yf
import pytz

# --- Setup ---
SYMBOL = "GC=F"
TIMEFRAME = "1h" # Using 1h for longer history (2 years)
SGT = pytz.timezone('Asia/Singapore')

# Fetch 2 years of 1h data
print("Fetching 2 years of 1h data...")
df = yf.download(SYMBOL, period="2y", interval="1h")
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)
df.index = df.index.tz_convert(SGT)

# --- Indicators ---
# 1. Bollinger Bands (for Mean Reversion)
df['ma20'] = df['Close'].rolling(window=20).mean()
df['std20'] = df['Close'].rolling(window=20).std()
df['upper_bb'] = df['ma20'] + (2.5 * df['std20'])
df['lower_bb'] = df['ma20'] - (2.5 * df['std20'])

# 2. RSI (for Divergence/Overbought)
delta = df['Close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
df['rsi'] = 100 - (100 / (1 + rs))

# 3. ATR (for dynamic SL/TP)
high_low = df['High'] - df['Low']
high_close = np.abs(df['High'] - df['Close'].shift())
low_close = np.abs(df['Low'] - df['Close'].shift())
df['atr'] = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1).rolling(window=14).mean()

# --- Strategy Simulations ---

def backtest_strategy(df, entry_signal, exit_long, exit_short, sl_mult=2, tp_mult=4):
    """Generic backtester to find win rate and R:R."""
    trades = []
    in_position = None
    
    for i in range(20, len(df)-1):
        row = df.iloc[i]
        
        if in_position is None:
            # Check for Long Entry
            if entry_signal(df, i) == 'Long':
                in_position = {'type': 'Long', 'entry_price': row['Close'], 'sl': row['Close'] - (sl_mult * row['atr']), 'tp': row['Close'] + (tp_mult * row['atr'])}
            # Check for Short Entry
            elif entry_signal(df, i) == 'Short':
                in_position = {'type': 'Short', 'entry_price': row['Close'], 'sl': row['Close'] + (sl_mult * row['atr']), 'tp': row['Close'] - (tp_mult * row['atr'])}
        
        else:
            # Check Exit
            if in_position['type'] == 'Long':
                if row['Low'] <= in_position['sl']:
                    trades.append(0) # Loss
                    in_position = None
                elif row['High'] >= in_position['tp']:
                    trades.append(1) # Win
                    in_position = None
            elif in_position['type'] == 'Short':
                if row['High'] >= in_position['sl']:
                    trades.append(0) # Loss
                    in_position = None
                elif row['Low'] <= in_position['tp']:
                    trades.append(1) # Win
                    in_position = None
                    
    if not trades: return 0, 0
    win_rate = sum(trades) / len(trades)
    return win_rate, len(trades)

# Strategy 1: BB 2.5 Reversion + RSI Filter
def signal_bb_rsi(df, i):
    row = df.iloc[i]
    if row['Close'] < row['lower_bb'] and row['rsi'] < 30: return 'Long'
    if row['Close'] > row['upper_bb'] and row['rsi'] > 70: return 'Short'
    return None

# Strategy 2: Asian Session Sweep (Simplified)
# Logic: Sweep Asian High/Low, then reversal
def signal_sweep(df, i):
    row = df.iloc[i]
    # Simplified: If price is at a 24h high/low and RSI is extreme
    if row['Close'] == df['Close'].iloc[i-24:i].min() and row['rsi'] < 25: return 'Long'
    if row['Close'] == df['Close'].iloc[i-24:i].max() and row['rsi'] > 75: return 'Short'
    return None

print("\n--- Strategy Discovery Results ---")
print(f"{'Strategy':<25} | {'Win Rate':<10} | {'Trades':<10} | {'R:R':<5}")
print("-" * 60)

for tp_m in [2, 3, 4]:
    wr, count = backtest_strategy(df, signal_bb_rsi, None, None, sl_mult=1, tp_mult=tp_m)
    print(f"{'BB Reversion':<25} | {wr*100:<9.1f}% | {count:<10} | 1:{tp_m}")

    wr, count = backtest_strategy(df, signal_sweep, None, None, sl_mult=1, tp_mult=tp_m)
    print(f"{'Liquidity Sweep':<25} | {wr*100:<9.1f}% | {count:<10} | 1:{tp_m}")
