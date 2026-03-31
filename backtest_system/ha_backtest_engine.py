import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import pytz

# --- Configuration ---
SYMBOL = "GC=F"  # Gold Futures for best 30m data
TIMEFRAME = "30m"
PERIOD = "60d"   # Yahoo Finance max for 30m
PIP_SIZE = 0.10  # 1 pip = $0.10 for XAUUSD
SGT = pytz.timezone('Asia/Singapore')

def calculate_heikin_ashi(df):
    """Calculates Heikin-Ashi candles from OHLC data."""
    ha_df = df.copy()
    ha_df['ha_close'] = (df['Open'] + df['High'] + df['Low'] + df['Close']) / 4
    
    # Initialize ha_open
    ha_open = np.zeros(len(df))
    ha_open[0] = (df['Open'].iloc[0] + df['Close'].iloc[0]) / 2
    for i in range(1, len(df)):
        ha_open[i] = (ha_open[i-1] + ha_df['ha_close'].iloc[i-1]) / 2
    ha_df['ha_open'] = ha_open
    
    ha_df['ha_high'] = ha_df[['High', 'ha_open', 'ha_close']].max(axis=1)
    ha_df['ha_low'] = ha_df[['Low', 'ha_open', 'ha_close']].min(axis=1)
    
    # Color: Green (Close > Open), Red (Close < Open)
    ha_df['ha_color'] = np.where(ha_df['ha_close'] >= ha_df['ha_open'], 'Green', 'Red')
    return ha_df

def get_session(dt):
    """Classifies SGT time into sessions."""
    hour = dt.hour
    if 0 <= hour < 8: return 'Asian'
    if 8 <= hour < 15: return 'Pre-London'
    if 15 <= hour < 20: return 'London'
    return 'New York'

# 1. Fetch Data
print(f"Fetching {TIMEFRAME} data for {SYMBOL}...")
df = yf.download(SYMBOL, period=PERIOD, interval=TIMEFRAME)
if df.empty:
    print("Error: No data found.")
    exit()

# Flatten columns if MultiIndex
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

# 2. Calculate Daily Levels (Previous Day High/Low)
df.index = df.index.tz_convert(SGT)
df['date'] = pd.to_datetime(df.index.date)
daily = df.resample('D').agg({'High': 'max', 'Low': 'min'}).shift(1)
daily.index = pd.to_datetime(daily.index.date)
daily.columns = ['pdh', 'pdl']

df = df.join(daily, on='date')
df = df.dropna(subset=['pdh', 'pdl'])

# 3. Calculate Heikin-Ashi
df = calculate_heikin_ashi(df)

# 4. Backtest Logic: HA Reversal after Touch
events = []
current_touch = None # Track if we are in a "wait for reversal" state

for i in range(1, len(df)):
    row = df.iloc[i]
    prev_row = df.iloc[i-1]
    
    # A. Detect Touch (Price wick touches PDH or PDL)
    # If not already waiting for a reversal, check for a new touch
    if current_touch is None:
        if row['High'] >= row['pdh']:
            current_touch = {'type': 'PDH', 'level': row['pdh'], 'touch_time': df.index[i], 'max_pullback': 0}
        elif row['Low'] <= row['pdl']:
            current_touch = {'type': 'PDL', 'level': row['pdl'], 'touch_time': df.index[i], 'max_pullback': 0}
    
    # B. If we have a touch, wait for HA reversal
    if current_touch:
        # Update max pullback (how far price went against the reversal direction)
        if current_touch['type'] == 'PDH':
            # After touching high, we wait for pullback (price goes down) and then reversal (Green HA)
            # Actually, user said: "PDH touched, wait for pullback, buy at first green"
            # This implies a MEAN REVERSION or a BREAKOUT RETEST?
            # User example: "previous day high touched, i wait for price to pull back and i buy at the first green candle"
            # This is a BREAKOUT RETEST logic.
            
            pullback = row['pdh'] - row['Low']
            current_touch['max_pullback'] = max(current_touch['max_pullback'], pullback)
            
            # Check for Reversal: First Green HA candle after some pullback? 
            # Or just first Green HA candle after the touch?
            if row['ha_color'] == 'Green' and prev_row['ha_color'] == 'Red':
                entry_price = row['ha_close']
                # Success criteria: Does it go higher than the touch high?
                # We will just record the event and the outcome
                events.append({
                    'date': row['date'],
                    'touch_time': current_touch['touch_time'],
                    'entry_time': df.index[i],
                    'type': current_touch['type'],
                    'level': current_touch['level'],
                    'entry_price': entry_price,
                    'pullback_usd': current_touch['max_pullback'],
                    'session': get_session(df.index[i])
                })
                current_touch = None # Reset
                
        elif current_touch['type'] == 'PDL':
            # PDL touched, wait for pullback (price goes up), sell at first red?
            # User didn't specify PDL but logic should be symmetric.
            pullback = row['High'] - row['pdl']
            current_touch['max_pullback'] = max(current_touch['max_pullback'], pullback)
            
            if row['ha_color'] == 'Red' and prev_row['ha_color'] == 'Green':
                entry_price = row['ha_close']
                events.append({
                    'date': row['date'],
                    'touch_time': current_touch['touch_time'],
                    'entry_time': df.index[i],
                    'type': current_touch['type'],
                    'level': current_touch['level'],
                    'entry_price': entry_price,
                    'pullback_usd': current_touch['max_pullback'],
                    'session': get_session(df.index[i])
                })
                current_touch = None

# 5. Save Results
events_df = pd.DataFrame(events)
events_df.to_csv('/home/ubuntu/backtest/ha_touch_events.csv', index=False)
print(f"Backtest complete. Found {len(events_df)} Heikin-Ashi reversal events.")
