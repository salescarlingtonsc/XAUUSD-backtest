"""
XAUUSD Previous Day High/Low Touch Backtest Engine
===================================================
Timeframe  : 1-hour candles (resampled to 30-min equivalent logic)
Instrument : XAUUSD (Gold Futures GC=F)
Timezone   : Singapore Time (SGT = UTC+8)
Logic      :
  1. For each trading day (SGT), compute the previous day's High and Low.
  2. On each 1h candle of the current day, check if the candle's wick
     (High or Low) touches the previous day's High or Low level.
  3. When a touch occurs, record:
       - Touch type  : PDH (Previous Day High) or PDL (Previous Day Low)
       - Touch candle: datetime (SGT), session label
       - Pullback    : max adverse excursion (pips) before price breaks
                       above PDH (for PDH touch) or below PDL (for PDL touch)
       - Breakout    : did price eventually break out? (within same day)
       - Max pullback: worst-case pips retraced from the touch level
       - Session     : Asian / London / New York (based on SGT hour)
  4. Aggregate statistics per session and overall.

Pip definition for XAUUSD: 1 pip = $0.10 (i.e., price / 0.1)
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ── Constants ────────────────────────────────────────────────────────────────
PIP_SIZE = 0.10          # 1 pip = $0.10 for XAUUSD
TOUCH_TOLERANCE = 0.50   # within $0.50 (~5 pips) counts as a touch
SGT_OFFSET = 8           # UTC+8

# Session boundaries in SGT (hour, inclusive start – exclusive end)
SESSIONS = {
    'Asian':  (0,  8),   # 00:00 – 07:59 SGT
    'London': (15, 21),  # 15:00 – 20:59 SGT  (London 07:00–13:00 UTC)
    'New York': (20, 24) # 20:00 – 23:59 SGT  (NY 12:00–17:00 UTC) — overlap ok
}
# Note: 08:00–14:59 SGT is pre-London; we'll label it "Pre-London"

def get_session(sgt_hour: int) -> str:
    if 0 <= sgt_hour < 8:
        return 'Asian'
    elif 8 <= sgt_hour < 15:
        return 'Pre-London'
    elif 15 <= sgt_hour < 20:
        return 'London'
    else:
        return 'New York'

def price_to_pips(price_diff: float) -> float:
    return round(abs(price_diff) / PIP_SIZE, 1)

# ── Data Loading ─────────────────────────────────────────────────────────────
def load_data():
    print("Loading 1h XAUUSD data...")
    df = pd.read_csv('/home/ubuntu/xauusd_1h_raw.csv', header=[0,1], index_col=0)
    # Flatten multi-level columns
    df.columns = [col[0] if col[1] == 'GC=F' else '_'.join(col) for col in df.columns]
    df.index = pd.to_datetime(df.index, utc=True)
    df = df[['Open','High','Low','Close','Volume']].copy()
    df.columns = ['Open','High','Low','Close','Volume']
    df = df.sort_index()
    
    # Convert to SGT
    df.index = df.index.tz_convert('Asia/Singapore')
    print(f"  Loaded {len(df)} hourly candles from {df.index[0].date()} to {df.index[-1].date()}")
    return df

def compute_previous_day_levels(df: pd.DataFrame) -> pd.DataFrame:
    """Add PDH and PDL columns based on previous calendar day (SGT)."""
    df = df.copy()
    df['date_sgt'] = df.index.date
    
    # Daily OHLC in SGT
    daily = df.groupby('date_sgt').agg(
        day_high=('High', 'max'),
        day_low=('Low', 'min')
    ).reset_index()
    daily = daily.sort_values('date_sgt').reset_index(drop=True)
    daily['PDH'] = daily['day_high'].shift(1)
    daily['PDL'] = daily['day_low'].shift(1)
    
    # Merge back
    daily_map = daily.set_index('date_sgt')[['PDH','PDL']]
    df = df.join(daily_map, on='date_sgt')
    df = df.dropna(subset=['PDH','PDL'])
    return df

# ── Touch Detection ──────────────────────────────────────────────────────────
def detect_touches(df: pd.DataFrame) -> list:
    """
    For each candle, check if it touches PDH or PDL.
    Returns a list of touch events with full metadata.
    """
    events = []
    dates = sorted(df['date_sgt'].unique())
    
    for trade_date in dates:
        day_df = df[df['date_sgt'] == trade_date].copy()
        if len(day_df) < 2:
            continue
        
        pdh = day_df['PDH'].iloc[0]
        pdl = day_df['PDL'].iloc[0]
        
        # Track which levels have been touched today (avoid double-counting same touch)
        touched_pdh = False
        touched_pdl = False
        
        for i, (idx, row) in enumerate(day_df.iterrows()):
            candle_high = row['High']
            candle_low  = row['Low']
            sgt_hour    = idx.hour
            session     = get_session(sgt_hour)
            
            # ── PDH Touch ────────────────────────────────────────────────
            if not touched_pdh and candle_high >= (pdh - TOUCH_TOLERANCE):
                touched_pdh = True
                # Measure pullback: from touch candle forward, find max low before
                # price closes above PDH (breakout)
                future = day_df.iloc[i:]
                
                # Max adverse move = how far price dipped below PDH after touch
                max_pullback_price = future['Low'].min()
                max_pullback_pips  = price_to_pips(pdh - max_pullback_price)
                
                # Did price break above PDH? (any candle close or high > PDH)
                breakout_candles = future[future['High'] > pdh + TOUCH_TOLERANCE]
                broke_out = len(breakout_candles) > 0
                
                if broke_out:
                    # Pullback before breakout: from touch to first breakout candle
                    first_bo_idx = breakout_candles.index[0]
                    pre_bo = future.loc[:first_bo_idx]
                    pullback_before_bo = price_to_pips(pdh - pre_bo['Low'].min())
                    # Reward: how far above PDH did price go after breakout
                    post_bo = future.loc[first_bo_idx:]
                    reward_pips = price_to_pips(post_bo['High'].max() - pdh)
                else:
                    pullback_before_bo = max_pullback_pips
                    reward_pips = 0.0
                
                events.append({
                    'date': trade_date,
                    'touch_time_sgt': idx.strftime('%Y-%m-%d %H:%M'),
                    'touch_type': 'PDH',
                    'level': round(pdh, 2),
                    'touch_price': round(candle_high, 2),
                    'session': session,
                    'sgt_hour': sgt_hour,
                    'broke_out': broke_out,
                    'pullback_before_bo_pips': pullback_before_bo,
                    'max_pullback_pips': max_pullback_pips,
                    'reward_pips': reward_pips,
                    'rr_ratio': round(reward_pips / max(pullback_before_bo, 1), 2) if broke_out else 0.0,
                })
            
            # ── PDL Touch ────────────────────────────────────────────────
            if not touched_pdl and candle_low <= (pdl + TOUCH_TOLERANCE):
                touched_pdl = True
                future = day_df.iloc[i:]
                
                max_pullback_price = future['High'].max()
                max_pullback_pips  = price_to_pips(max_pullback_price - pdl)
                
                breakout_candles = future[future['Low'] < pdl - TOUCH_TOLERANCE]
                broke_out = len(breakout_candles) > 0
                
                if broke_out:
                    first_bo_idx = breakout_candles.index[0]
                    pre_bo = future.loc[:first_bo_idx]
                    pullback_before_bo = price_to_pips(pre_bo['High'].max() - pdl)
                    post_bo = future.loc[first_bo_idx:]
                    reward_pips = price_to_pips(pdl - post_bo['Low'].min())
                else:
                    pullback_before_bo = max_pullback_pips
                    reward_pips = 0.0
                
                events.append({
                    'date': trade_date,
                    'touch_time_sgt': idx.strftime('%Y-%m-%d %H:%M'),
                    'touch_type': 'PDL',
                    'level': round(pdl, 2),
                    'touch_price': round(candle_low, 2),
                    'session': session,
                    'sgt_hour': sgt_hour,
                    'broke_out': broke_out,
                    'pullback_before_bo_pips': pullback_before_bo,
                    'max_pullback_pips': max_pullback_pips,
                    'reward_pips': reward_pips,
                    'rr_ratio': round(reward_pips / max(pullback_before_bo, 1), 2) if broke_out else 0.0,
                })
    
    return events

# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    df = load_data()
    df = compute_previous_day_levels(df)
    
    print(f"\nRunning touch detection on {len(df)} candles...")
    events = detect_touches(df)
    
    results = pd.DataFrame(events)
    results.to_csv('/home/ubuntu/backtest/touch_events.csv', index=False)
    print(f"\nDetected {len(results)} touch events.")
    print(f"  PDH touches: {len(results[results['touch_type']=='PDH'])}")
    print(f"  PDL touches: {len(results[results['touch_type']=='PDL'])}")
    print(f"\nBreakout rate: {results['broke_out'].mean()*100:.1f}%")
    print(f"\nSample events:")
    print(results.head(10).to_string())
    
    # Save raw df for further analysis
    df.to_csv('/home/ubuntu/backtest/ohlcv_with_levels.csv')
    print("\nDone. Files saved.")
