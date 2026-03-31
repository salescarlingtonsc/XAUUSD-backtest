import pandas as pd
import numpy as np
import yfinance as yf
import pytz

# Setup
SYMBOL = "GC=F"
df = yf.download(SYMBOL, period="2y", interval="1h")
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)
SGT = pytz.timezone('Asia/Singapore')
df.index = df.index.tz_convert(SGT)

# Indicators
df['ma20'] = df['Close'].rolling(window=20).mean()
df['std20'] = df['Close'].rolling(window=20).std()
df['upper_bb'] = df['ma20'] + (3.0 * df['std20']) # Extreme 3.0 SD
df['lower_bb'] = df['ma20'] - (3.0 * df['std20'])

delta = df['Close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
df['rsi'] = 100 - (100 / (1 + rs))

high_low = df['High'] - df['Low']
high_close = np.abs(df['High'] - df['Close'].shift())
low_close = np.abs(df['Low'] - df['Close'].shift())
df['atr'] = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1).rolling(window=14).mean()

def backtest_fixed_risk(df, signal_func, sl_usd, tp_usd):
    trades = []
    for i in range(30, len(df)-1):
        row = df.iloc[i]
        sig = signal_func(df, i)
        if sig == 'Long':
            # Check outcome
            entry = row['Close']
            sl = entry - sl_usd
            tp = entry + tp_usd
            for j in range(i+1, min(i+100, len(df))):
                future_row = df.iloc[j]
                if future_row['Low'] <= sl:
                    trades.append(0)
                    break
                if future_row['High'] >= tp:
                    trades.append(1)
                    break
        elif sig == 'Short':
            entry = row['Close']
            sl = entry + sl_usd
            tp = entry - tp_usd
            for j in range(i+1, min(i+100, len(df))):
                future_row = df.iloc[j]
                if future_row['High'] >= sl:
                    trades.append(0)
                    break
                if future_row['Low'] <= tp:
                    trades.append(1)
                    break
    if not trades: return 0, 0
    return sum(trades) / len(trades), len(trades)

# Extreme Mean Reversion: 3.0 SD + RSI < 20 or > 80
def signal_extreme(df, i):
    row = df.iloc[i]
    if row['Close'] < row['lower_bb'] and row['rsi'] < 20: return 'Long'
    if row['Close'] > row['upper_bb'] and row['rsi'] > 80: return 'Short'
    return None

print("--- Testing Extreme Mean Reversion (3.0 SD) ---")
for sl in [5, 10, 15]:
    for tp_mult in [2, 3]:
        wr, count = backtest_fixed_risk(df, signal_extreme, sl, sl * tp_mult)
        print(f"SL: ${sl:<2} | TP: ${sl*tp_mult:<2} | Win Rate: {wr*100:<5.1f}% | Trades: {count}")
