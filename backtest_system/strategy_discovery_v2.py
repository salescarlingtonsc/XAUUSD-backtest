import pandas as pd
import numpy as np
import yfinance as yf
import pytz

# --- Setup ---
SYMBOL = "GC=F"
TIMEFRAME = "1h"
SGT = pytz.timezone('Asia/Singapore')

# Fetch 2 years of 1h data
print("Fetching 2 years of 1h data...")
df = yf.download(SYMBOL, period="2y", interval="1h")
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)
df.index = df.index.tz_convert(SGT)

# --- Indicators ---
# 1. EMAs for Trend
df['ema50'] = df['Close'].ewm(span=50, adjust=False).mean()
df['ema200'] = df['Close'].ewm(span=200, adjust=False).mean()

# 2. ATR for dynamic SL/TP
high_low = df['High'] - df['Low']
high_close = np.abs(df['High'] - df['Close'].shift())
low_close = np.abs(df['Low'] - df['Close'].shift())
df['atr'] = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1).rolling(window=14).mean()

# --- Strategy Simulations ---

def backtest_strategy(df, entry_signal, sl_mult=1.5, tp_mult=3):
    trades = []
    in_position = None
    
    for i in range(200, len(df)-1):
        row = df.iloc[i]
        
        if in_position is None:
            signal = entry_signal(df, i)
            if signal == 'Long':
                in_position = {'type': 'Long', 'entry_price': row['Close'], 'sl': row['Close'] - (sl_mult * row['atr']), 'tp': row['Close'] + (tp_mult * row['atr'])}
            elif signal == 'Short':
                in_position = {'type': 'Short', 'entry_price': row['Close'], 'sl': row['Close'] + (sl_mult * row['atr']), 'tp': row['Close'] - (tp_mult * row['atr'])}
        
        else:
            if in_position['type'] == 'Long':
                if row['Low'] <= in_position['sl']:
                    trades.append(0)
                    in_position = None
                elif row['High'] >= in_position['tp']:
                    trades.append(1)
                    in_position = None
            elif in_position['type'] == 'Short':
                if row['High'] >= in_position['sl']:
                    trades.append(0)
                    in_position = None
                elif row['Low'] <= in_position['tp']:
                    trades.append(1)
                    in_position = None
                    
    if not trades: return 0, 0
    return sum(trades) / len(trades), len(trades)

# Strategy 3: EMA Trend Pullback (Buy pullbacks to EMA50 in EMA200 uptrend)
def signal_ema_pullback(df, i):
    row = df.iloc[i]
    prev_row = df.iloc[i-1]
    # Uptrend: Close > EMA50 > EMA200
    if row['Close'] > row['ema50'] > row['ema200']:
        # Pullback: Touched EMA50 and bounced
        if prev_row['Low'] <= prev_row['ema50'] and row['Close'] > row['ema50']:
            return 'Long'
    # Downtrend: Close < EMA50 < EMA200
    if row['Close'] < row['ema50'] < row['ema200']:
        # Pullback: Touched EMA50 and bounced
        if prev_row['High'] >= prev_row['ema50'] and row['Close'] < row['ema50']:
            return 'Short'
    return None

# Strategy 4: High-Volatility Breakout (Price breaks 24h high with high ATR)
def signal_breakout(df, i):
    row = df.iloc[i]
    h24 = df['High'].iloc[i-24:i].max()
    l24 = df['Low'].iloc[i-24:i].min()
    if row['Close'] > h24 and row['atr'] > df['atr'].iloc[i-24:i].mean() * 1.5:
        return 'Long'
    if row['Close'] < l24 and row['atr'] > df['atr'].iloc[i-24:i].mean() * 1.5:
        return 'Short'
    return None

print("\n--- Strategy Discovery Results v2 ---")
print(f"{'Strategy':<25} | {'Win Rate':<10} | {'Trades':<10} | {'R:R':<5}")
print("-" * 60)

for tp_m in [2, 3, 4]:
    wr, count = backtest_strategy(df, signal_ema_pullback, sl_mult=1, tp_mult=tp_m)
    print(f"{'EMA Pullback':<25} | {wr*100:<9.1f}% | {count:<10} | 1:{tp_m}")

    wr, count = backtest_strategy(df, signal_breakout, sl_mult=1, tp_mult=tp_m)
    print(f"{'Breakout Momentum':<25} | {wr*100:<9.1f}% | {count:<10} | 1:{tp_m}")
