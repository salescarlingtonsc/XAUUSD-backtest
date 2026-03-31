"""
XAUUSD Backtest Statistics Computation
=======================================
Computes probability, pip distribution, and R:R stats from touch events.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.ticker import FuncFormatter
import warnings
warnings.filterwarnings('ignore')

# ── Load Data ────────────────────────────────────────────────────────────────
df = pd.read_csv('/home/ubuntu/backtest/touch_events.csv')
df['date'] = pd.to_datetime(df['date'])

SESSION_ORDER = ['Asian', 'Pre-London', 'London', 'New York']
SESSION_COLORS = {
    'Asian':      '#4A90D9',
    'Pre-London': '#7B68EE',
    'London':     '#E8A838',
    'New York':   '#E84040',
}

# ── Helper ───────────────────────────────────────────────────────────────────
def pct(x): return f"{x*100:.1f}%"
def fmt(x): return f"{x:.1f}"

def session_stats(sub: pd.DataFrame, label: str) -> dict:
    n = len(sub)
    if n == 0:
        return {}
    bo = sub[sub['broke_out']]
    nbo = sub[~sub['broke_out']]
    
    pb = sub['pullback_before_bo_pips']
    pb_bo = bo['pullback_before_bo_pips'] if len(bo) > 0 else pd.Series(dtype=float)
    rr = bo['rr_ratio'] if len(bo) > 0 else pd.Series(dtype=float)
    rew = bo['reward_pips'] if len(bo) > 0 else pd.Series(dtype=float)
    
    return {
        'Session': label,
        'Total Touches': n,
        'Breakouts': len(bo),
        'No Breakout': len(nbo),
        'Breakout %': round(len(bo)/n*100, 1),
        'Avg Pullback (pips)': round(pb.mean(), 1),
        'Median Pullback (pips)': round(pb.median(), 1),
        'Min Pullback (pips)': round(pb.min(), 1),
        'Max Pullback (pips)': round(pb.max(), 1),
        'P25 Pullback (pips)': round(pb.quantile(0.25), 1),
        'P75 Pullback (pips)': round(pb.quantile(0.75), 1),
        'Avg Pullback on BO (pips)': round(pb_bo.mean(), 1) if len(pb_bo) > 0 else 0,
        'Avg Reward (pips)': round(rew.mean(), 1) if len(rew) > 0 else 0,
        'Avg R:R': round(rr.mean(), 2) if len(rr) > 0 else 0,
        'Median R:R': round(rr.median(), 2) if len(rr) > 0 else 0,
        'R:R > 1 %': round((rr > 1).mean()*100, 1) if len(rr) > 0 else 0,
        'R:R > 2 %': round((rr > 2).mean()*100, 1) if len(rr) > 0 else 0,
        'R:R > 3 %': round((rr > 3).mean()*100, 1) if len(rr) > 0 else 0,
    }

# ── Overall Stats ─────────────────────────────────────────────────────────────
print("=" * 70)
print("XAUUSD PREVIOUS DAY HIGH/LOW TOUCH — BACKTEST STATISTICS")
print("=" * 70)

overall = session_stats(df, 'ALL')
pdh_stats = session_stats(df[df['touch_type']=='PDH'], 'PDH Only')
pdl_stats = session_stats(df[df['touch_type']=='PDL'], 'PDL Only')

for k, v in overall.items():
    print(f"  {k:<35}: {v}")

# ── Per-Session Stats ─────────────────────────────────────────────────────────
session_rows = []
for sess in SESSION_ORDER:
    sub = df[df['session'] == sess]
    if len(sub) > 0:
        session_rows.append(session_stats(sub, sess))

session_df = pd.DataFrame(session_rows)
print("\nPer-Session Summary:")
print(session_df.to_string(index=False))

# ── PDH vs PDL per Session ────────────────────────────────────────────────────
combo_rows = []
for sess in SESSION_ORDER:
    for ttype in ['PDH', 'PDL']:
        sub = df[(df['session']==sess) & (df['touch_type']==ttype)]
        if len(sub) > 0:
            r = session_stats(sub, f"{sess} – {ttype}")
            r['Touch Type'] = ttype
            combo_rows.append(r)

combo_df = pd.DataFrame(combo_rows)

# ── Save Stats ────────────────────────────────────────────────────────────────
session_df.to_csv('/home/ubuntu/backtest/stats_by_session.csv', index=False)
combo_df.to_csv('/home/ubuntu/backtest/stats_by_session_type.csv', index=False)

# Save overall summary
overall_df = pd.DataFrame([overall, pdh_stats, pdl_stats])
overall_df.to_csv('/home/ubuntu/backtest/stats_overall.csv', index=False)

print("\nStats saved.")

# ── Pullback Distribution Buckets ─────────────────────────────────────────────
bins = [0, 10, 20, 30, 50, 75, 100, 150, 200, 300, 500, 9999]
labels = ['0-10','10-20','20-30','30-50','50-75','75-100','100-150','150-200','200-300','300-500','500+']

df['pullback_bucket'] = pd.cut(df['pullback_before_bo_pips'], bins=bins, labels=labels, right=False)
bucket_counts = df.groupby(['pullback_bucket','session'], observed=True).size().unstack(fill_value=0)
bucket_counts.to_csv('/home/ubuntu/backtest/pullback_distribution.csv')

# ── Hourly Touch Distribution ─────────────────────────────────────────────────
hourly = df.groupby(['sgt_hour','touch_type']).size().unstack(fill_value=0)
hourly.to_csv('/home/ubuntu/backtest/hourly_distribution.csv')

print("Distribution data saved.")
print(f"\nTotal events: {len(df)}")
print(f"Date range: {df['date'].min().date()} to {df['date'].max().date()}")
print(f"Trading days: {df['date'].nunique()}")
