"""
Generate charts for the 3-Tap Induced Reversal Backtest
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

OUT = '/home/ubuntu/XAUUSD-backtest/backtest_system'

trades  = pd.read_csv(f'{OUT}/three_tap_trades.csv')
setups  = pd.read_csv(f'{OUT}/three_tap_setups.csv')

# ── Colour palette ────────────────────────────────────────────────────────────
WIN_COL  = '#00C896'
LOSS_COL = '#FF4C4C'
TO_COL   = '#FFA500'
BG       = '#0D1117'
GRID_C   = '#21262D'
TEXT_C   = '#E6EDF3'
ACCENT   = '#58A6FF'

plt.rcParams.update({
    'figure.facecolor' : BG,
    'axes.facecolor'   : BG,
    'axes.edgecolor'   : GRID_C,
    'axes.labelcolor'  : TEXT_C,
    'xtick.color'      : TEXT_C,
    'ytick.color'      : TEXT_C,
    'text.color'       : TEXT_C,
    'grid.color'       : GRID_C,
    'grid.linestyle'   : '--',
    'grid.alpha'       : 0.5,
    'font.family'      : 'DejaVu Sans',
    'font.size'        : 11,
})

# ─────────────────────────────────────────────────────────────────────────────
# CHART 1 — Win / Loss / Timeout breakdown by R:R
# ─────────────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle('3-Tap Induced Reversal  |  XAUUSD 1H  |  2-Year Backtest\nOutcome Breakdown by R:R Target',
             fontsize=15, fontweight='bold', color=TEXT_C, y=1.02)

for ax, rr in zip(axes, [1.0, 2.0, 3.0]):
    sub = trades[trades['rr_target'] == rr]
    counts = sub['outcome'].value_counts()
    labels = []
    sizes  = []
    colors = []
    for outcome, col in [('WIN', WIN_COL), ('LOSS', LOSS_COL), ('TIMEOUT', TO_COL)]:
        v = counts.get(outcome, 0)
        labels.append(f'{outcome}\n{v} ({v/len(sub)*100:.0f}%)')
        sizes.append(v)
        colors.append(col)

    wedges, texts = ax.pie(sizes, labels=labels, colors=colors,
                           startangle=90, wedgeprops=dict(width=0.55, edgecolor=BG))
    for t in texts:
        t.set_color(TEXT_C)
        t.set_fontsize(10)
    ax.set_title(f'R:R  {rr}:1', color=TEXT_C, fontsize=13, pad=10)

plt.tight_layout()
plt.savefig(f'{OUT}/chart1_outcome_breakdown.png', dpi=150, bbox_inches='tight',
            facecolor=BG)
plt.close()
print("Chart 1 saved.")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 2 — Win Rate & Expectancy by Session (R:R = 2:1)
# ─────────────────────────────────────────────────────────────────────────────
rr2 = trades[trades['rr_target'] == 2.0]
sessions = ['Asian', 'Pre-London', 'London', 'New York']
win_rates = []
expectancies = []
trade_counts = []

for sess in sessions:
    sub = rr2[rr2['session'] == sess]
    n = len(sub)
    trade_counts.append(n)
    if n == 0:
        win_rates.append(0)
        expectancies.append(0)
        continue
    wr = (sub['outcome'] == 'WIN').sum() / n * 100
    win_rates.append(wr)
    avg_win  = sub[sub['outcome']=='WIN']['pnl_pips'].mean() if (sub['outcome']=='WIN').any() else 0
    avg_loss = sub[sub['outcome']=='LOSS']['pnl_pips'].mean() if (sub['outcome']=='LOSS').any() else 0
    avg_to   = sub[sub['outcome']=='TIMEOUT']['pnl_pips'].mean() if (sub['outcome']=='TIMEOUT').any() else 0
    exp = (wr/100*avg_win + (sub['outcome']=='LOSS').sum()/n*avg_loss +
           (sub['outcome']=='TIMEOUT').sum()/n*avg_to)
    expectancies.append(round(exp, 1))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle('3-Tap Reversal  |  Session Analysis  (R:R = 2:1)',
             fontsize=14, fontweight='bold', color=TEXT_C)

x = np.arange(len(sessions))
bar_colors = [WIN_COL if wr >= 50 else LOSS_COL for wr in win_rates]
bars = ax1.bar(x, win_rates, color=bar_colors, width=0.5, edgecolor=BG)
ax1.axhline(50, color=ACCENT, linestyle='--', linewidth=1.5, label='50% break-even')
ax1.set_xticks(x)
ax1.set_xticklabels([f'{s}\n(n={c})' for s, c in zip(sessions, trade_counts)], fontsize=10)
ax1.set_ylabel('Win Rate (%)', color=TEXT_C)
ax1.set_ylim(0, 115)
ax1.set_title('Win Rate by Session', color=TEXT_C, fontsize=12)
ax1.legend(facecolor=GRID_C, edgecolor=GRID_C, labelcolor=TEXT_C)
ax1.grid(axis='y')
for bar, wr in zip(bars, win_rates):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
             f'{wr:.0f}%', ha='center', va='bottom', color=TEXT_C, fontsize=11, fontweight='bold')

exp_colors = [WIN_COL if e > 0 else LOSS_COL for e in expectancies]
bars2 = ax2.bar(x, expectancies, color=exp_colors, width=0.5, edgecolor=BG)
ax2.axhline(0, color=ACCENT, linestyle='--', linewidth=1.5)
ax2.set_xticks(x)
ax2.set_xticklabels([f'{s}\n(n={c})' for s, c in zip(sessions, trade_counts)], fontsize=10)
ax2.set_ylabel('Expectancy (pips per trade)', color=TEXT_C)
ax2.set_title('Expectancy by Session', color=TEXT_C, fontsize=12)
ax2.grid(axis='y')
for bar, exp in zip(bars2, expectancies):
    ypos = bar.get_height() + (5 if exp >= 0 else -20)
    ax2.text(bar.get_x() + bar.get_width()/2, ypos,
             f'{exp:+.0f}', ha='center', va='bottom', color=TEXT_C, fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig(f'{OUT}/chart2_session_analysis.png', dpi=150, bbox_inches='tight',
            facecolor=BG)
plt.close()
print("Chart 2 saved.")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 3 — Cumulative P&L (pips) across all trades (R:R = 2:1)
# ─────────────────────────────────────────────────────────────────────────────
rr2_sorted = rr2.copy()
rr2_sorted['datetime_sgt'] = pd.to_datetime(rr2_sorted['datetime_sgt'])
rr2_sorted = rr2_sorted.sort_values('datetime_sgt').reset_index(drop=True)
rr2_sorted['cum_pips'] = rr2_sorted['pnl_pips'].cumsum()

fig, ax = plt.subplots(figsize=(16, 6))
fig.suptitle('3-Tap Reversal  |  Cumulative P&L in Pips  (R:R = 2:1)',
             fontsize=14, fontweight='bold', color=TEXT_C)

colors_line = [WIN_COL if p >= 0 else LOSS_COL for p in rr2_sorted['pnl_pips']]
ax.plot(range(len(rr2_sorted)), rr2_sorted['cum_pips'], color=ACCENT, linewidth=2.5, zorder=3)
ax.fill_between(range(len(rr2_sorted)), rr2_sorted['cum_pips'], 0,
                where=(rr2_sorted['cum_pips'] >= 0), alpha=0.15, color=WIN_COL)
ax.fill_between(range(len(rr2_sorted)), rr2_sorted['cum_pips'], 0,
                where=(rr2_sorted['cum_pips'] < 0), alpha=0.15, color=LOSS_COL)
ax.axhline(0, color=TEXT_C, linestyle='--', linewidth=1, alpha=0.5)

# Mark individual trades
for i, row in rr2_sorted.iterrows():
    c = WIN_COL if row['outcome'] == 'WIN' else (TO_COL if row['outcome'] == 'TIMEOUT' else LOSS_COL)
    ax.scatter(i, row['cum_pips'], color=c, s=60, zorder=5)

ax.set_xlabel('Trade Number', color=TEXT_C)
ax.set_ylabel('Cumulative Pips', color=TEXT_C)
ax.grid(True)

win_p = mpatches.Patch(color=WIN_COL, label='WIN')
loss_p = mpatches.Patch(color=LOSS_COL, label='LOSS')
to_p = mpatches.Patch(color=TO_COL, label='TIMEOUT')
ax.legend(handles=[win_p, loss_p, to_p], facecolor=GRID_C, edgecolor=GRID_C, labelcolor=TEXT_C)

plt.tight_layout()
plt.savefig(f'{OUT}/chart3_cumulative_pnl.png', dpi=150, bbox_inches='tight',
            facecolor=BG)
plt.close()
print("Chart 3 saved.")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 4 — Filtered variants comparison (bar chart)
# ─────────────────────────────────────────────────────────────────────────────
variants = {
    'All Sessions\n(unfiltered)': rr2,
    'London +\nNew York': rr2[rr2['session'].isin(['London','New York'])],
    'RSI > 60\n(overbought)': rr2[rr2['rsi_at_entry'] > 60],
    'London/NY +\nRSI > 60': rr2[(rr2['rsi_at_entry'] > 60) & rr2['session'].isin(['London','New York'])],
}

v_labels = list(variants.keys())
v_wr     = []
v_exp    = []
v_n      = []

for label, sub in variants.items():
    n = len(sub)
    v_n.append(n)
    if n == 0:
        v_wr.append(0); v_exp.append(0); continue
    wr = (sub['outcome']=='WIN').sum() / n * 100
    v_wr.append(wr)
    avg_win  = sub[sub['outcome']=='WIN']['pnl_pips'].mean()  if (sub['outcome']=='WIN').any()  else 0
    avg_loss = sub[sub['outcome']=='LOSS']['pnl_pips'].mean() if (sub['outcome']=='LOSS').any() else 0
    avg_to   = sub[sub['outcome']=='TIMEOUT']['pnl_pips'].mean() if (sub['outcome']=='TIMEOUT').any() else 0
    exp = (wr/100*avg_win + (sub['outcome']=='LOSS').sum()/n*avg_loss +
           (sub['outcome']=='TIMEOUT').sum()/n*avg_to)
    v_exp.append(round(exp, 1))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle('3-Tap Reversal  |  Filter Comparison  (R:R = 2:1)',
             fontsize=14, fontweight='bold', color=TEXT_C)

x = np.arange(len(v_labels))
bar_colors = [WIN_COL if wr >= 50 else LOSS_COL for wr in v_wr]
bars = ax1.bar(x, v_wr, color=bar_colors, width=0.5, edgecolor=BG)
ax1.axhline(50, color=ACCENT, linestyle='--', linewidth=1.5, label='50% line')
ax1.set_xticks(x); ax1.set_xticklabels([f'{l}\n(n={c})' for l, c in zip(v_labels, v_n)], fontsize=9)
ax1.set_ylabel('Win Rate (%)', color=TEXT_C); ax1.set_ylim(0, 115)
ax1.set_title('Win Rate by Filter', color=TEXT_C, fontsize=12)
ax1.legend(facecolor=GRID_C, edgecolor=GRID_C, labelcolor=TEXT_C); ax1.grid(axis='y')
for bar, wr in zip(bars, v_wr):
    ax1.text(bar.get_x()+bar.get_width()/2, bar.get_height()+2,
             f'{wr:.0f}%', ha='center', va='bottom', color=TEXT_C, fontsize=11, fontweight='bold')

exp_colors = [WIN_COL if e > 0 else LOSS_COL for e in v_exp]
bars2 = ax2.bar(x, v_exp, color=exp_colors, width=0.5, edgecolor=BG)
ax2.axhline(0, color=ACCENT, linestyle='--', linewidth=1.5)
ax2.set_xticks(x); ax2.set_xticklabels([f'{l}\n(n={c})' for l, c in zip(v_labels, v_n)], fontsize=9)
ax2.set_ylabel('Expectancy (pips per trade)', color=TEXT_C)
ax2.set_title('Expectancy by Filter', color=TEXT_C, fontsize=12); ax2.grid(axis='y')
for bar, exp in zip(bars2, v_exp):
    ypos = bar.get_height() + (5 if exp >= 0 else -25)
    ax2.text(bar.get_x()+bar.get_width()/2, ypos,
             f'{exp:+.0f}', ha='center', va='bottom', color=TEXT_C, fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig(f'{OUT}/chart4_filter_comparison.png', dpi=150, bbox_inches='tight',
            facecolor=BG)
plt.close()
print("Chart 4 saved.")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 5 — Strategy concept diagram (annotated trade example)
# ─────────────────────────────────────────────────────────────────────────────
# Use the London WIN trade from Dec 2024 as the example
import yfinance as yf, pytz
SGT = pytz.timezone('Asia/Singapore')
raw = yf.download("GC=F", start="2024-12-14", end="2024-12-20", interval="1h", progress=False)
if isinstance(raw.columns, pd.MultiIndex):
    raw.columns = raw.columns.get_level_values(0)
raw.index = raw.index.tz_convert(SGT)

fig, ax = plt.subplots(figsize=(18, 8))
fig.suptitle('3-Tap Induced Reversal  |  Example Trade  |  XAUUSD 1H  |  Dec 2024',
             fontsize=14, fontweight='bold', color=TEXT_C)

# Draw candles
for i, (ts, row) in enumerate(raw.iterrows()):
    color = WIN_COL if row['Close'] >= row['Open'] else LOSS_COL
    ax.plot([i, i], [row['Low'], row['High']], color=color, linewidth=1)
    body_bot = min(row['Open'], row['Close'])
    body_top = max(row['Open'], row['Close'])
    ax.add_patch(mpatches.FancyBboxPatch((i-0.3, body_bot), 0.6, max(body_top-body_bot, 0.1),
                                          boxstyle='square,pad=0', facecolor=color, edgecolor=color))

# Mark the 3 taps (approximate positions)
tap_positions = [10, 14, 19]   # approximate bar indices for the Dec 17 setup
for tp_i, tp_pos in enumerate(tap_positions, 1):
    if tp_pos < len(raw):
        low_val = raw.iloc[tp_pos]['Low']
        ax.annotate(f'Tap {tp_i}', xy=(tp_pos, low_val),
                    xytext=(tp_pos, low_val - 8),
                    arrowprops=dict(arrowstyle='->', color=ACCENT, lw=1.5),
                    color=ACCENT, fontsize=9, ha='center')

# Entry annotation
entry_bar = 20
if entry_bar < len(raw):
    entry_px = raw.iloc[entry_bar]['Close']
    ax.axhline(entry_px, color=LOSS_COL, linestyle='--', linewidth=1.5, alpha=0.8, label=f'Entry SHORT ~{entry_px:.0f}')
    ax.text(len(raw)-1, entry_px+1, 'ENTRY SHORT', color=LOSS_COL, fontsize=9, ha='right')

ax.set_xlabel('Candle (1H)', color=TEXT_C)
ax.set_ylabel('Price (USD)', color=TEXT_C)
ax.grid(True, alpha=0.3)

# Trend line (rising support)
if tap_positions[0] < len(raw) and tap_positions[-1] < len(raw):
    x1, y1 = tap_positions[0], raw.iloc[tap_positions[0]]['Low']
    x2, y2 = tap_positions[-1], raw.iloc[tap_positions[-1]]['Low']
    ax.plot([x1, x2+3], [y1, y2 + (y2-y1)/(x2-x1)*3], color=ACCENT,
            linestyle='-', linewidth=2, label='Rising Support (Trend Line)')

ax.legend(facecolor=GRID_C, edgecolor=GRID_C, labelcolor=TEXT_C, fontsize=9)
plt.tight_layout()
plt.savefig(f'{OUT}/chart5_example_trade.png', dpi=150, bbox_inches='tight',
            facecolor=BG)
plt.close()
print("Chart 5 saved.")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 6 — Risk distribution (risk_usd per setup)
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 5))
fig.suptitle('3-Tap Reversal  |  Risk Per Trade Distribution',
             fontsize=13, fontweight='bold', color=TEXT_C)
ax.hist(setups['risk_usd'], bins=12, color=ACCENT, edgecolor=BG, alpha=0.85)
ax.axvline(setups['risk_usd'].median(), color=WIN_COL, linestyle='--', linewidth=2,
           label=f'Median risk = ${setups["risk_usd"].median():.1f}')
ax.set_xlabel('Risk per trade (USD)', color=TEXT_C)
ax.set_ylabel('Frequency', color=TEXT_C)
ax.legend(facecolor=GRID_C, edgecolor=GRID_C, labelcolor=TEXT_C)
ax.grid(axis='y')
plt.tight_layout()
plt.savefig(f'{OUT}/chart6_risk_distribution.png', dpi=150, bbox_inches='tight',
            facecolor=BG)
plt.close()
print("Chart 6 saved.")

print("\nAll charts generated successfully.")
