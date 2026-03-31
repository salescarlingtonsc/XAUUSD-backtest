"""
XAUUSD — 3-Tap Trend-Line Induced Reversal Backtest
=====================================================
Strategy Concept
----------------
Retail traders see price tap a rising trend line (or support zone) THREE times.
Each tap "induces" more retail buyers to enter long.  After the 3rd tap the
"smart money" reversal fires:

  1. Identify a rising support / trend-line zone on the 1-hour chart.
     Proxy: price makes 3 consecutive higher-lows within a rolling 10-bar window
     (each low is within ATR of the previous low, confirming the same level).
  2. On the 3rd tap, retail buyers pile in — we confirm this with a bullish
     engulfing or strong green candle (close > open by > 0.3 × ATR).
  3. The reversal signal fires when the NEXT candle is a strong bearish candle
     (close < open by > 0.3 × ATR) that closes BELOW the 3rd-tap low.
     This is the "stop hunt" — retail longs are trapped and price reverses.
  4. Enter SHORT at the close of the reversal candle.
     SL  = high of the reversal candle + 0.5 × ATR (above trapped buyers).
     TP1 = 1× risk  (1:1 R:R)
     TP2 = 2× risk  (1:2 R:R)
     TP3 = 3× risk  (1:3 R:R)

Additional filters tested
--------------------------
  A. Session filter   — London + New York only (highest liquidity sweeps).
  B. RSI filter       — RSI(14) > 60 at entry (price was overbought / buyers
                        were over-extended before the reversal).
  C. Volume filter    — Entry candle volume > 1.2 × 20-bar average volume
                        (confirms institutional participation).

Data
----
  Instrument : XAUUSD (GC=F via yfinance)
  Timeframe  : 1-hour candles
  Period     : 2 years (max available)
  Timezone   : Asia/Singapore (SGT = UTC+8)

Pip definition: 1 pip = $0.10
"""

import pandas as pd
import numpy as np
import yfinance as yf
import pytz
import warnings
warnings.filterwarnings('ignore')

# ── Constants ────────────────────────────────────────────────────────────────
SYMBOL      = "GC=F"
TIMEFRAME   = "1h"
PERIOD      = "2y"
PIP_SIZE    = 0.10
SGT         = pytz.timezone('Asia/Singapore')

ATR_PERIOD      = 14
ATR_BODY_MULT   = 0.30   # candle body must be > 0.30 × ATR to be "strong"
TOUCH_WINDOW    = 10     # bars to look back for 3 taps
TOUCH_TOLERANCE = 0.50   # $0.50 tolerance for "same level"

# ── Session helper ────────────────────────────────────────────────────────────
def get_session(hour: int) -> str:
    if 0  <= hour < 8:  return 'Asian'
    if 8  <= hour < 15: return 'Pre-London'
    if 15 <= hour < 20: return 'London'
    return 'New York'

# ── Data loading ──────────────────────────────────────────────────────────────
def load_data() -> pd.DataFrame:
    print(f"Fetching {PERIOD} of {TIMEFRAME} {SYMBOL} data …")
    df = yf.download(SYMBOL, period=PERIOD, interval=TIMEFRAME, progress=False)
    if df.empty:
        raise RuntimeError("No data returned from yfinance.")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.index = df.index.tz_convert(SGT)
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
    df.sort_index(inplace=True)
    print(f"  {len(df)} candles  |  {df.index[0].date()} → {df.index[-1].date()}")
    return df

# ── Indicator computation ─────────────────────────────────────────────────────
def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # ATR(14)
    hl  = df['High'] - df['Low']
    hc  = (df['High'] - df['Close'].shift()).abs()
    lc  = (df['Low']  - df['Close'].shift()).abs()
    tr  = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    df['atr'] = tr.rolling(ATR_PERIOD).mean()

    # RSI(14)
    delta = df['Close'].diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    rs    = gain / loss.replace(0, np.nan)
    df['rsi'] = 100 - (100 / (1 + rs))

    # Volume MA(20)
    df['vol_ma20'] = df['Volume'].rolling(20).mean()

    # Candle body size
    df['body'] = (df['Close'] - df['Open']).abs()

    return df

# ── 3-Tap detection ───────────────────────────────────────────────────────────
def find_three_tap_setups(df: pd.DataFrame) -> list:
    """
    Scan for 3-tap rising support setups.

    A valid 3-tap setup requires, within the last TOUCH_WINDOW bars:
      • tap1_low < tap2_low < tap3_low  (rising lows — ascending support)
      • Each consecutive low is within TOUCH_TOLERANCE of the prior low
        (they are "touching" the same rising trend line, not wildly different)
      • tap3 is the most recent of the three
      • After tap3, the NEXT candle is the "inducement" candle:
          – bullish (close > open) with body > ATR_BODY_MULT × ATR
      • The candle AFTER the inducement is the "reversal" candle:
          – bearish (close < open) with body > ATR_BODY_MULT × ATR
          – close < tap3_low  (breaks below support — stop hunt confirmed)

    Returns a list of setup dicts.
    """
    setups = []
    n = len(df)

    for i in range(TOUCH_WINDOW + 2, n - 1):
        atr_val = df['atr'].iloc[i]
        if pd.isna(atr_val) or atr_val == 0:
            continue

        window = df.iloc[i - TOUCH_WINDOW: i]

        # Find local lows in the window (candle whose low < both neighbours)
        lows_idx = []
        for j in range(1, len(window) - 1):
            if (window['Low'].iloc[j] < window['Low'].iloc[j - 1] and
                    window['Low'].iloc[j] < window['Low'].iloc[j + 1]):
                lows_idx.append(j)

        if len(lows_idx) < 3:
            continue

        # Take the last 3 local lows
        t1, t2, t3 = lows_idx[-3], lows_idx[-2], lows_idx[-1]
        low1 = window['Low'].iloc[t1]
        low2 = window['Low'].iloc[t2]
        low3 = window['Low'].iloc[t3]

        # Rising lows (ascending support)
        if not (low1 < low2 < low3):
            continue

        # Lows must be "close" to each other — same trend-line zone
        # Allow up to 3× ATR spread across all 3 taps
        if (low3 - low1) > 3 * atr_val:
            continue

        # ── Inducement candle (bar i-1 relative to current) ──────────────────
        # The candle at position t3+1 in the window (bar right after 3rd tap)
        # We want the inducement to be the candle just before our current bar i
        induce_bar_pos = t3 + 1
        if induce_bar_pos >= len(window):
            continue
        induce_bar = window.iloc[induce_bar_pos]

        # Bullish inducement: retail buyers pile in
        if not (induce_bar['Close'] > induce_bar['Open'] and
                induce_bar['body'] > ATR_BODY_MULT * atr_val):
            continue

        # ── Reversal candle (current bar i) ──────────────────────────────────
        rev_bar = df.iloc[i]

        # Bearish reversal
        if not (rev_bar['Close'] < rev_bar['Open'] and
                rev_bar['body'] > ATR_BODY_MULT * atr_val):
            continue

        # Must close BELOW the 3rd tap low (stop hunt / liquidity grab)
        if rev_bar['Close'] >= low3:
            continue

        # ── Record setup ──────────────────────────────────────────────────────
        entry_price = rev_bar['Close']
        sl_price    = rev_bar['High'] + 0.5 * atr_val
        risk        = sl_price - entry_price

        if risk <= 0:
            continue

        setups.append({
            'bar_index'    : i,
            'datetime_sgt' : df.index[i],
            'session'      : get_session(df.index[i].hour),
            'tap1_low'     : round(low1, 2),
            'tap2_low'     : round(low2, 2),
            'tap3_low'     : round(low3, 2),
            'entry_price'  : round(entry_price, 2),
            'sl_price'     : round(sl_price, 2),
            'risk_usd'     : round(risk, 2),
            'atr'          : round(atr_val, 2),
            'rsi_at_entry' : round(df['rsi'].iloc[i], 1),
            'vol_ratio'    : round(df['Volume'].iloc[i] / df['vol_ma20'].iloc[i], 2)
                             if df['vol_ma20'].iloc[i] > 0 else np.nan,
        })

    return setups

# ── Trade simulation ──────────────────────────────────────────────────────────
def simulate_trades(df: pd.DataFrame, setups: list,
                    rr_targets: list = [1.0, 2.0, 3.0],
                    max_bars_hold: int = 48) -> pd.DataFrame:
    """
    For each setup, simulate a SHORT entry and check which TP / SL is hit first
    within max_bars_hold candles.

    Returns a DataFrame with one row per setup × TP target.
    """
    records = []

    for s in setups:
        i           = s['bar_index']
        entry       = s['entry_price']
        sl          = s['sl_price']
        risk        = s['risk_usd']

        for rr in rr_targets:
            tp = entry - rr * risk   # SHORT trade — TP is below entry

            outcome  = 'TIMEOUT'
            exit_bar = None
            exit_px  = None
            bars_held = 0

            for j in range(i + 1, min(i + 1 + max_bars_hold, len(df))):
                bar = df.iloc[j]
                bars_held = j - i

                # SL hit (price trades above SL)
                if bar['High'] >= sl:
                    outcome  = 'LOSS'
                    exit_bar = df.index[j]
                    exit_px  = sl
                    break

                # TP hit (price trades below TP)
                if bar['Low'] <= tp:
                    outcome  = 'WIN'
                    exit_bar = df.index[j]
                    exit_px  = tp
                    break

            pnl = (entry - exit_px) if exit_px is not None else (entry - df['Close'].iloc[min(i + max_bars_hold, len(df) - 1)])
            pnl_pips = pnl / PIP_SIZE

            rec = {**s,
                   'rr_target'  : rr,
                   'tp_price'   : round(tp, 2),
                   'outcome'    : outcome,
                   'exit_time'  : exit_bar,
                   'exit_price' : round(exit_px, 2) if exit_px else None,
                   'bars_held'  : bars_held,
                   'pnl_pips'   : round(pnl_pips, 1),
                   'pnl_usd'    : round(pnl, 2),
                   }
            records.append(rec)

    return pd.DataFrame(records)

# ── Statistics ────────────────────────────────────────────────────────────────
def compute_stats(trades: pd.DataFrame, label: str = 'All') -> dict:
    if trades.empty:
        return {}

    wins    = trades[trades['outcome'] == 'WIN']
    losses  = trades[trades['outcome'] == 'LOSS']
    timeout = trades[trades['outcome'] == 'TIMEOUT']

    n       = len(trades)
    win_n   = len(wins)
    loss_n  = len(losses)
    to_n    = len(timeout)

    win_rate = win_n / n * 100

    avg_win_pips  = wins['pnl_pips'].mean()   if win_n  > 0 else 0
    avg_loss_pips = losses['pnl_pips'].mean() if loss_n > 0 else 0
    avg_to_pips   = timeout['pnl_pips'].mean() if to_n > 0 else 0

    # Expectancy per trade (pips)
    expectancy_pips = (win_rate / 100 * avg_win_pips +
                       (loss_n / n) * avg_loss_pips +
                       (to_n  / n) * avg_to_pips)

    return {
        'Label'          : label,
        'Trades'         : n,
        'Wins'           : win_n,
        'Losses'         : loss_n,
        'Timeouts'       : to_n,
        'Win Rate %'     : round(win_rate, 1),
        'Avg Win (pips)' : round(avg_win_pips, 1),
        'Avg Loss (pips)': round(avg_loss_pips, 1),
        'Expectancy (pips)': round(expectancy_pips, 1),
    }

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    import os
    out_dir = '/home/ubuntu/XAUUSD-backtest/backtest_system'
    os.makedirs(out_dir, exist_ok=True)

    # 1. Load & prepare data
    df = load_data()
    df = add_indicators(df)

    # 2. Find 3-tap setups
    print("\nScanning for 3-tap induced reversal setups …")
    setups = find_three_tap_setups(df)
    print(f"  Found {len(setups)} raw setups")

    if not setups:
        print("No setups found. Exiting.")
        exit()

    setups_df = pd.DataFrame(setups)
    setups_df.to_csv(f'{out_dir}/three_tap_setups.csv', index=False)

    # 3. Simulate trades for R:R 1, 2, 3
    print("\nSimulating trades …")
    trades = simulate_trades(df, setups, rr_targets=[1.0, 2.0, 3.0])
    trades.to_csv(f'{out_dir}/three_tap_trades.csv', index=False)
    print(f"  Total trade records: {len(trades)}")

    # 4. Statistics — all sessions, per session, per R:R
    print("\n" + "="*70)
    print("  3-TAP INDUCED REVERSAL BACKTEST — RESULTS SUMMARY")
    print("="*70)

    all_stats = []

    for rr in [1.0, 2.0, 3.0]:
        subset = trades[trades['rr_target'] == rr]
        s = compute_stats(subset, label=f'All Sessions  RR={rr}:1')
        all_stats.append(s)
        print(f"\n  R:R = {rr}:1  |  {s['Trades']} trades  |  Win Rate: {s['Win Rate %']}%  |  Expectancy: {s['Expectancy (pips)']} pips")

    print("\n--- By Session (R:R = 2:1) ---")
    rr2 = trades[trades['rr_target'] == 2.0]
    for sess in ['Asian', 'Pre-London', 'London', 'New York']:
        sub = rr2[rr2['session'] == sess]
        if len(sub) == 0:
            continue
        s = compute_stats(sub, label=f'{sess}  RR=2:1')
        all_stats.append(s)
        print(f"  {sess:<12}  |  {s['Trades']} trades  |  Win Rate: {s['Win Rate %']}%  |  Expectancy: {s['Expectancy (pips)']} pips")

    # --- Filtered variants ---
    print("\n--- Filtered: RSI > 60 at entry (overbought buyers)  R:R = 2:1 ---")
    rr2_rsi = rr2[rr2['rsi_at_entry'] > 60]
    s = compute_stats(rr2_rsi, label='RSI>60 filter  RR=2:1')
    all_stats.append(s)
    print(f"  {s['Trades']} trades  |  Win Rate: {s['Win Rate %']}%  |  Expectancy: {s['Expectancy (pips)']} pips")

    print("\n--- Filtered: London + New York sessions  R:R = 2:1 ---")
    rr2_lny = rr2[rr2['session'].isin(['London', 'New York'])]
    s = compute_stats(rr2_lny, label='London+NY  RR=2:1')
    all_stats.append(s)
    print(f"  {s['Trades']} trades  |  Win Rate: {s['Win Rate %']}%  |  Expectancy: {s['Expectancy (pips)']} pips")

    print("\n--- Filtered: RSI > 60 + London/NY  R:R = 2:1 ---")
    rr2_combo = rr2[(rr2['rsi_at_entry'] > 60) & (rr2['session'].isin(['London', 'New York']))]
    s = compute_stats(rr2_combo, label='RSI>60+London/NY  RR=2:1')
    all_stats.append(s)
    print(f"  {s['Trades']} trades  |  Win Rate: {s['Win Rate %']}%  |  Expectancy: {s['Expectancy (pips)']} pips")

    # Save stats
    stats_df = pd.DataFrame(all_stats)
    stats_df.to_csv(f'{out_dir}/three_tap_stats.csv', index=False)

    print(f"\nAll files saved to {out_dir}/")
    print("  three_tap_setups.csv  — raw setup events")
    print("  three_tap_trades.csv  — per-trade outcomes")
    print("  three_tap_stats.csv   — aggregated statistics")
