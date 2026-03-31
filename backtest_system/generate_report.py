"""
XAUUSD Backtest — Interactive HTML Report Generator
"""

import pandas as pd
import numpy as np
import json
import warnings
warnings.filterwarnings('ignore')

# ── Load Data ─────────────────────────────────────────────────────────────────
df = pd.read_csv('/home/ubuntu/backtest/touch_events.csv')
df['date'] = pd.to_datetime(df['date'])
df['touch_time_sgt'] = pd.to_datetime(df['touch_time_sgt'])

stats_sess = pd.read_csv('/home/ubuntu/backtest/stats_by_session.csv')
stats_overall = pd.read_csv('/home/ubuntu/backtest/stats_overall.csv')
stats_combo = pd.read_csv('/home/ubuntu/backtest/stats_by_session_type.csv')

SESSION_ORDER = ['Asian', 'Pre-London', 'London', 'New York']
SESSION_COLORS = {
    'Asian':      '#4A90D9',
    'Pre-London': '#7B68EE',
    'London':     '#E8A838',
    'New York':   '#E84040',
}

# ── Prepare Chart Data ────────────────────────────────────────────────────────

# 1. Pullback distribution by session
bins = [0, 10, 20, 30, 50, 75, 100, 150, 200, 300, 500, 9999]
bin_labels = ['0-10','10-20','20-30','30-50','50-75','75-100','100-150','150-200','200-300','300-500','500+']
df['pullback_bucket'] = pd.cut(df['pullback_before_bo_pips'], bins=bins, labels=bin_labels, right=False)

pullback_dist = {}
for sess in SESSION_ORDER:
    sub = df[df['session']==sess]
    counts = sub['pullback_bucket'].value_counts().reindex(bin_labels, fill_value=0)
    pullback_dist[sess] = counts.tolist()

# 2. Hourly touch count
hourly_pdh = df[df['touch_type']=='PDH'].groupby('sgt_hour').size().reindex(range(24), fill_value=0).tolist()
hourly_pdl = df[df['touch_type']=='PDL'].groupby('sgt_hour').size().reindex(range(24), fill_value=0).tolist()
hours_labels = [f"{h:02d}:00" for h in range(24)]

# 3. R:R distribution
rr_bins = [0, 0.5, 1, 1.5, 2, 3, 5, 10, 999]
rr_labels = ['<0.5','0.5-1','1-1.5','1.5-2','2-3','3-5','5-10','10+']
bo_df = df[df['broke_out']]
rr_dist_all = pd.cut(bo_df['rr_ratio'], bins=rr_bins, labels=rr_labels, right=False).value_counts().reindex(rr_labels, fill_value=0).tolist()

rr_dist_sess = {}
for sess in SESSION_ORDER:
    sub = bo_df[bo_df['session']==sess]
    rr_dist_sess[sess] = pd.cut(sub['rr_ratio'], bins=rr_bins, labels=rr_labels, right=False).value_counts().reindex(rr_labels, fill_value=0).tolist()

# 4. Monthly breakout rate
df['month'] = df['date'].dt.to_period('M')
monthly = df.groupby('month').agg(
    total=('broke_out','count'),
    breakouts=('broke_out','sum')
).reset_index()
monthly['rate'] = (monthly['breakouts']/monthly['total']*100).round(1)
monthly['month_str'] = monthly['month'].astype(str)

# 5. Session pie data
sess_counts = df.groupby('session').size().reindex(SESSION_ORDER, fill_value=0)

# 6. All events table (for the data table)
table_data = df[['date','touch_time_sgt','touch_type','level','touch_price',
                  'session','broke_out','pullback_before_bo_pips','max_pullback_pips',
                  'reward_pips','rr_ratio']].copy()
table_data['date'] = table_data['date'].dt.strftime('%Y-%m-%d')
table_data['touch_time_sgt'] = table_data['touch_time_sgt'].dt.strftime('%Y-%m-%d %H:%M')
table_data['broke_out'] = table_data['broke_out'].map({True:'✅ Yes', False:'❌ No'})
table_data.columns = ['Date','Touch Time (SGT)','Type','Level','Touch Price',
                       'Session','Breakout?','Pullback (pips)','Max Pullback (pips)',
                       'Reward (pips)','R:R']
table_json = table_data.to_dict(orient='records')

# ── Percentile Data for Pullback Table ──────────────────────────────────────
def get_perc(series):
    if len(series) == 0:
        return {'P10':0,'P25':0,'P50':0,'P75':0,'P90':0,'P95':0,'Avg':0,'Max':0}
    return {
        'P10': round(series.quantile(0.10), 1),
        'P25': round(series.quantile(0.25), 1),
        'P50': round(series.quantile(0.50), 1),
        'P75': round(series.quantile(0.75), 1),
        'P90': round(series.quantile(0.90), 1),
        'P95': round(series.quantile(0.95), 1),
        'Avg': round(series.mean(), 1),
        'Max': round(series.max(), 1),
    }

perc_data = {'ALL': get_perc(df['pullback_before_bo_pips'])}
for sess in SESSION_ORDER:
    perc_data[sess] = get_perc(df[df['session']==sess]['pullback_before_bo_pips'])
perc_data_json = json.dumps(perc_data)

# ── Overall Numbers ───────────────────────────────────────────────────────────
ov = stats_overall.iloc[0]
total_days = df['date'].nunique()
date_from = df['date'].min().strftime('%d %b %Y')
date_to   = df['date'].max().strftime('%d %b %Y')

# ── HTML Template ─────────────────────────────────────────────────────────────
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>XAUUSD — Previous Day H/L Backtest Report</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0/dist/chartjs-plugin-datalabels.min.js"></script>
<style>
  :root {{
    --bg: #0d1117;
    --card: #161b22;
    --border: #30363d;
    --text: #e6edf3;
    --muted: #8b949e;
    --accent: #f0b429;
    --green: #3fb950;
    --red: #f85149;
    --blue: #4A90D9;
    --purple: #7B68EE;
    --orange: #E8A838;
    --asian: #4A90D9;
    --prelondon: #7B68EE;
    --london: #E8A838;
    --newyork: #E84040;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--bg); color: var(--text); font-family: 'Segoe UI', system-ui, sans-serif; font-size: 14px; }}
  
  /* Header */
  .header {{ background: linear-gradient(135deg, #1a1f2e 0%, #0d1117 100%); border-bottom: 1px solid var(--border); padding: 24px 32px; }}
  .header h1 {{ font-size: 26px; font-weight: 700; color: var(--accent); letter-spacing: -0.5px; }}
  .header .subtitle {{ color: var(--muted); margin-top: 4px; font-size: 13px; }}
  .header .meta {{ display: flex; gap: 24px; margin-top: 16px; flex-wrap: wrap; }}
  .meta-item {{ background: rgba(255,255,255,0.04); border: 1px solid var(--border); border-radius: 8px; padding: 8px 16px; }}
  .meta-item .label {{ color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; }}
  .meta-item .value {{ color: var(--text); font-size: 15px; font-weight: 600; margin-top: 2px; }}

  /* Nav */
  .nav {{ background: var(--card); border-bottom: 1px solid var(--border); padding: 0 32px; display: flex; gap: 4px; overflow-x: auto; }}
  .nav-btn {{ padding: 12px 16px; cursor: pointer; border: none; background: none; color: var(--muted); font-size: 13px; font-weight: 500; border-bottom: 2px solid transparent; transition: all 0.2s; white-space: nowrap; }}
  .nav-btn:hover {{ color: var(--text); }}
  .nav-btn.active {{ color: var(--accent); border-bottom-color: var(--accent); }}

  /* Content */
  .content {{ padding: 24px 32px; max-width: 1600px; margin: 0 auto; }}
  .tab-panel {{ display: none; }}
  .tab-panel.active {{ display: block; }}

  /* KPI Cards */
  .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 16px; margin-bottom: 24px; }}
  .kpi-card {{ background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 16px 20px; }}
  .kpi-card .kpi-label {{ color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; }}
  .kpi-card .kpi-value {{ font-size: 28px; font-weight: 700; margin-top: 4px; }}
  .kpi-card .kpi-sub {{ color: var(--muted); font-size: 11px; margin-top: 2px; }}
  .kpi-green {{ color: var(--green); }}
  .kpi-red {{ color: var(--red); }}
  .kpi-accent {{ color: var(--accent); }}
  .kpi-blue {{ color: var(--blue); }}

  /* Charts */
  .chart-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px; }}
  .chart-grid-3 {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-bottom: 24px; }}
  .chart-full {{ margin-bottom: 24px; }}
  .chart-card {{ background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; }}
  .chart-card h3 {{ font-size: 14px; font-weight: 600; color: var(--text); margin-bottom: 16px; }}
  .chart-card .chart-sub {{ color: var(--muted); font-size: 11px; margin-top: -12px; margin-bottom: 12px; }}
  .chart-container {{ position: relative; }}

  /* Session Cards */
  .session-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 20px; margin-bottom: 24px; }}
  .session-card {{ background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; }}
  .session-card .sess-header {{ display: flex; align-items: center; gap: 10px; margin-bottom: 16px; }}
  .sess-dot {{ width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; }}
  .sess-title {{ font-size: 16px; font-weight: 700; }}
  .sess-time {{ color: var(--muted); font-size: 11px; margin-left: auto; }}
  .sess-stats {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
  .sess-stat {{ background: rgba(255,255,255,0.03); border-radius: 8px; padding: 10px 12px; }}
  .sess-stat .s-label {{ color: var(--muted); font-size: 10px; text-transform: uppercase; letter-spacing: 0.4px; }}
  .sess-stat .s-value {{ font-size: 18px; font-weight: 700; margin-top: 2px; }}
  .sess-stat .s-sub {{ color: var(--muted); font-size: 10px; }}
  .progress-bar {{ height: 6px; background: rgba(255,255,255,0.08); border-radius: 3px; margin-top: 8px; overflow: hidden; }}
  .progress-fill {{ height: 100%; border-radius: 3px; transition: width 0.5s; }}

  /* Table */
  .table-controls {{ display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; align-items: center; }}
  .search-box {{ background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 8px 14px; color: var(--text); font-size: 13px; width: 240px; outline: none; }}
  .search-box:focus {{ border-color: var(--accent); }}
  .filter-select {{ background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 8px 14px; color: var(--text); font-size: 13px; outline: none; cursor: pointer; }}
  .filter-select:focus {{ border-color: var(--accent); }}
  .table-wrapper {{ background: var(--card); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
  thead th {{ background: rgba(255,255,255,0.04); padding: 10px 12px; text-align: left; color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.4px; border-bottom: 1px solid var(--border); cursor: pointer; white-space: nowrap; }}
  thead th:hover {{ color: var(--text); }}
  tbody tr {{ border-bottom: 1px solid rgba(255,255,255,0.04); transition: background 0.15s; }}
  tbody tr:hover {{ background: rgba(255,255,255,0.03); }}
  tbody td {{ padding: 9px 12px; white-space: nowrap; }}
  .badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }}
  .badge-pdh {{ background: rgba(248,81,73,0.15); color: #f85149; }}
  .badge-pdl {{ background: rgba(63,185,80,0.15); color: #3fb950; }}
  .badge-asian {{ background: rgba(74,144,217,0.15); color: #4A90D9; }}
  .badge-prelondon {{ background: rgba(123,104,238,0.15); color: #7B68EE; }}
  .badge-london {{ background: rgba(232,168,56,0.15); color: #E8A838; }}
  .badge-newyork {{ background: rgba(232,64,64,0.15); color: #E84040; }}
  .pagination {{ display: flex; gap: 8px; align-items: center; justify-content: flex-end; margin-top: 12px; }}
  .page-btn {{ background: var(--card); border: 1px solid var(--border); border-radius: 6px; padding: 6px 12px; color: var(--text); cursor: pointer; font-size: 12px; }}
  .page-btn:hover {{ border-color: var(--accent); color: var(--accent); }}
  .page-btn.active {{ background: var(--accent); color: #000; border-color: var(--accent); }}
  .page-info {{ color: var(--muted); font-size: 12px; }}

  /* Methodology */
  .method-card {{ background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 24px; margin-bottom: 20px; }}
  .method-card h3 {{ color: var(--accent); margin-bottom: 12px; font-size: 15px; }}
  .method-card p {{ color: var(--muted); line-height: 1.7; margin-bottom: 10px; }}
  .method-card ul {{ color: var(--muted); line-height: 1.8; padding-left: 20px; }}
  .method-card li {{ margin-bottom: 4px; }}
  .highlight {{ color: var(--text); font-weight: 600; }}

  /* Responsive */
  @media (max-width: 900px) {{
    .chart-grid {{ grid-template-columns: 1fr; }}
    .chart-grid-3 {{ grid-template-columns: 1fr; }}
    .content {{ padding: 16px; }}
    .header {{ padding: 16px; }}
    .nav {{ padding: 0 16px; }}
  }}
  
  /* Tooltip */
  .tooltip-icon {{ display: inline-block; width: 14px; height: 14px; background: var(--border); border-radius: 50%; text-align: center; line-height: 14px; font-size: 10px; cursor: help; margin-left: 4px; color: var(--muted); }}
</style>
</head>
<body>

<!-- HEADER -->
<div class="header">
  <h1>⚡ XAUUSD — Previous Day High/Low Touch Backtest</h1>
  <div class="subtitle">How far does price pull back before breaking the previous day's high or low?</div>
  <div class="meta">
    <div class="meta-item"><div class="label">Instrument</div><div class="value">XAUUSD (Gold)</div></div>
    <div class="meta-item"><div class="label">Timeframe</div><div class="value">1-Hour Candles</div></div>
    <div class="meta-item"><div class="label">Period</div><div class="value">{date_from} – {date_to}</div></div>
    <div class="meta-item"><div class="label">Trading Days</div><div class="value">{total_days}</div></div>
    <div class="meta-item"><div class="label">Total Touches</div><div class="value">{int(ov['Total Touches'])}</div></div>
    <div class="meta-item"><div class="label">Timezone</div><div class="value">SGT (UTC+8)</div></div>
  </div>
</div>

<!-- NAV -->
<div class="nav">
  <button class="nav-btn active" onclick="showTab('overview')">📊 Overview</button>
  <button class="nav-btn" onclick="showTab('sessions')">🕐 Sessions</button>
  <button class="nav-btn" onclick="showTab('pullback')">📉 Pullback Analysis</button>
  <button class="nav-btn" onclick="showTab('rr')">⚖️ Risk:Reward</button>
  <button class="nav-btn" onclick="showTab('events')">📋 All Events</button>
  <button class="nav-btn" onclick="showTab('methodology')">📖 Methodology</button>
</div>

<!-- CONTENT -->
<div class="content">

<!-- ═══════════════════════════════════════════════════════════════════ -->
<!--  TAB 1: OVERVIEW                                                   -->
<!-- ═══════════════════════════════════════════════════════════════════ -->
<div id="tab-overview" class="tab-panel active">

  <!-- KPI Cards -->
  <div class="kpi-grid">
    <div class="kpi-card">
      <div class="kpi-label">Total Touch Events</div>
      <div class="kpi-value kpi-accent">{int(ov['Total Touches'])}</div>
      <div class="kpi-sub">PDH + PDL combined</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Breakout Probability</div>
      <div class="kpi-value kpi-green">{ov['Breakout %']}%</div>
      <div class="kpi-sub">Price breaks prev H/L same day</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Avg Pullback</div>
      <div class="kpi-value kpi-blue">{ov['Avg Pullback (pips)']}</div>
      <div class="kpi-sub">pips before breakout</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Median Pullback</div>
      <div class="kpi-value kpi-blue">{ov['Median Pullback (pips)']}</div>
      <div class="kpi-sub">pips (50th percentile)</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">25th Pct Pullback</div>
      <div class="kpi-value" style="color:#7B68EE">{ov['P25 Pullback (pips)']}</div>
      <div class="kpi-sub">pips — tight SL zone</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">75th Pct Pullback</div>
      <div class="kpi-value" style="color:#7B68EE">{ov['P75 Pullback (pips)']}</div>
      <div class="kpi-sub">pips — wide SL zone</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Avg R:R (on breakouts)</div>
      <div class="kpi-value kpi-accent">{ov['Avg R:R']}</div>
      <div class="kpi-sub">reward ÷ pullback</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Median R:R</div>
      <div class="kpi-value kpi-accent">{ov['Median R:R']}</div>
      <div class="kpi-sub">50th percentile</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">R:R &gt; 1:1</div>
      <div class="kpi-value kpi-green">{ov['R:R > 1 %']}%</div>
      <div class="kpi-sub">of breakout events</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">R:R &gt; 2:1</div>
      <div class="kpi-value kpi-green">{ov['R:R > 2 %']}%</div>
      <div class="kpi-sub">of breakout events</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">PDH Touches</div>
      <div class="kpi-value kpi-red">{int(stats_overall.iloc[1]['Total Touches'])}</div>
      <div class="kpi-sub">{stats_overall.iloc[1]['Breakout %']}% breakout rate</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">PDL Touches</div>
      <div class="kpi-value kpi-green">{int(stats_overall.iloc[2]['Total Touches'])}</div>
      <div class="kpi-sub">{stats_overall.iloc[2]['Breakout %']}% breakout rate</div>
    </div>
  </div>

  <!-- Charts Row 1 -->
  <div class="chart-grid">
    <div class="chart-card">
      <h3>Touch Events by Session</h3>
      <div class="chart-sub">Distribution of PDH and PDL touches across trading sessions (SGT)</div>
      <div class="chart-container" style="height:280px">
        <canvas id="chartSessionBar"></canvas>
      </div>
    </div>
    <div class="chart-card">
      <h3>Breakout Rate by Session</h3>
      <div class="chart-sub">% of touches that resulted in a same-day breakout</div>
      <div class="chart-container" style="height:280px">
        <canvas id="chartBreakoutRate"></canvas>
      </div>
    </div>
  </div>

  <!-- Charts Row 2 -->
  <div class="chart-grid">
    <div class="chart-card">
      <h3>Touch Events by Hour (SGT)</h3>
      <div class="chart-sub">When do PDH/PDL touches most commonly occur?</div>
      <div class="chart-container" style="height:280px">
        <canvas id="chartHourly"></canvas>
      </div>
    </div>
    <div class="chart-card">
      <h3>Monthly Breakout Rate (%)</h3>
      <div class="chart-sub">Consistency of breakout probability over time</div>
      <div class="chart-container" style="height:280px">
        <canvas id="chartMonthly"></canvas>
      </div>
    </div>
  </div>

</div>

<!-- ═══════════════════════════════════════════════════════════════════ -->
<!--  TAB 2: SESSIONS                                                   -->
<!-- ═══════════════════════════════════════════════════════════════════ -->
<div id="tab-sessions" class="tab-panel">

  <div class="session-grid" id="sessionCards"></div>

  <div class="chart-grid">
    <div class="chart-card">
      <h3>Avg Pullback (pips) by Session</h3>
      <div class="chart-sub">How far price typically retraces before breaking out</div>
      <div class="chart-container" style="height:280px">
        <canvas id="chartSessPullback"></canvas>
      </div>
    </div>
    <div class="chart-card">
      <h3>Avg R:R by Session</h3>
      <div class="chart-sub">Average reward-to-risk ratio on breakout trades</div>
      <div class="chart-container" style="height:280px">
        <canvas id="chartSessRR"></canvas>
      </div>
    </div>
  </div>

  <div class="chart-card chart-full">
    <h3>PDH vs PDL Breakout Rate by Session</h3>
    <div class="chart-sub">Comparing breakout probability for high vs low touches per session</div>
    <div class="chart-container" style="height:300px">
      <canvas id="chartPDHvsPDL"></canvas>
    </div>
  </div>

</div>

<!-- ═══════════════════════════════════════════════════════════════════ -->
<!--  TAB 3: PULLBACK ANALYSIS                                          -->
<!-- ═══════════════════════════════════════════════════════════════════ -->
<div id="tab-pullback" class="tab-panel">

  <div class="chart-card chart-full">
    <h3>Pullback Distribution — All Sessions</h3>
    <div class="chart-sub">How many pips does price pull back before breaking out? (pip buckets)</div>
    <div class="chart-container" style="height:320px">
      <canvas id="chartPullbackAll"></canvas>
    </div>
  </div>

  <div class="chart-grid">
    <div class="chart-card">
      <h3>Pullback Distribution — Asian Session</h3>
      <div class="chart-container" style="height:260px">
        <canvas id="chartPbAsian"></canvas>
      </div>
    </div>
    <div class="chart-card">
      <h3>Pullback Distribution — Pre-London</h3>
      <div class="chart-container" style="height:260px">
        <canvas id="chartPbPreLondon"></canvas>
      </div>
    </div>
  </div>

  <div class="chart-grid">
    <div class="chart-card">
      <h3>Pullback Distribution — London Session</h3>
      <div class="chart-container" style="height:260px">
        <canvas id="chartPbLondon"></canvas>
      </div>
    </div>
    <div class="chart-card">
      <h3>Pullback Distribution — New York Session</h3>
      <div class="chart-container" style="height:260px">
        <canvas id="chartPbNewYork"></canvas>
      </div>
    </div>
  </div>

  <!-- Pullback percentile table -->
  <div class="chart-card">
    <h3>Pullback Percentile Table (pips) — Stop Loss Sizing Guide</h3>
    <div class="chart-sub">Use these values to size your stop loss. E.g., P75 means 75% of touches had a pullback ≤ this value.</div>
    <div style="overflow-x:auto; margin-top:12px;">
      <table id="pullbackTable" style="min-width:600px;">
        <thead>
          <tr>
            <th>Session</th><th>P10</th><th>P25</th><th>P50 (Median)</th><th>P75</th><th>P90</th><th>P95</th><th>Avg</th><th>Max</th>
          </tr>
        </thead>
        <tbody id="pullbackTableBody"></tbody>
      </table>
    </div>
  </div>

</div>

<!-- ═══════════════════════════════════════════════════════════════════ -->
<!--  TAB 4: RISK:REWARD                                                -->
<!-- ═══════════════════════════════════════════════════════════════════ -->
<div id="tab-rr" class="tab-panel">

  <div class="kpi-grid">
    <div class="kpi-card">
      <div class="kpi-label">Avg Reward (pips)</div>
      <div class="kpi-value kpi-accent">{ov['Avg Reward (pips)']}</div>
      <div class="kpi-sub">after breakout confirmation</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Avg R:R</div>
      <div class="kpi-value kpi-accent">{ov['Avg R:R']}</div>
      <div class="kpi-sub">reward ÷ pullback risk</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Median R:R</div>
      <div class="kpi-value kpi-accent">{ov['Median R:R']}</div>
      <div class="kpi-sub">50th percentile</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">R:R &gt; 1:1</div>
      <div class="kpi-value kpi-green">{ov['R:R > 1 %']}%</div>
      <div class="kpi-sub">of breakout events</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">R:R &gt; 2:1</div>
      <div class="kpi-value kpi-green">{ov['R:R > 2 %']}%</div>
      <div class="kpi-sub">of breakout events</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">R:R &gt; 3:1</div>
      <div class="kpi-value kpi-green">{ov['R:R > 3 %']}%</div>
      <div class="kpi-sub">of breakout events</div>
    </div>
  </div>

  <div class="chart-grid">
    <div class="chart-card">
      <h3>R:R Distribution — All Sessions</h3>
      <div class="chart-sub">Frequency of R:R outcomes across all breakout events</div>
      <div class="chart-container" style="height:280px">
        <canvas id="chartRRAll"></canvas>
      </div>
    </div>
    <div class="chart-card">
      <h3>R:R Distribution by Session</h3>
      <div class="chart-sub">Stacked comparison of R:R buckets per session</div>
      <div class="chart-container" style="height:280px">
        <canvas id="chartRRSess"></canvas>
      </div>
    </div>
  </div>

  <div class="chart-card chart-full">
    <h3>R:R Threshold Hit Rate by Session (%)</h3>
    <div class="chart-sub">% of breakout events that achieved each R:R threshold</div>
    <div class="chart-container" style="height:300px">
      <canvas id="chartRRThreshold"></canvas>
    </div>
  </div>

</div>

<!-- ═══════════════════════════════════════════════════════════════════ -->
<!--  TAB 5: ALL EVENTS                                                 -->
<!-- ═══════════════════════════════════════════════════════════════════ -->
<div id="tab-events" class="tab-panel">

  <div class="table-controls">
    <input type="text" class="search-box" id="tableSearch" placeholder="🔍  Search date, session, type..." oninput="filterTable()">
    <select class="filter-select" id="filterSession" onchange="filterTable()">
      <option value="">All Sessions</option>
      <option value="Asian">Asian</option>
      <option value="Pre-London">Pre-London</option>
      <option value="London">London</option>
      <option value="New York">New York</option>
    </select>
    <select class="filter-select" id="filterType" onchange="filterTable()">
      <option value="">PDH + PDL</option>
      <option value="PDH">PDH Only</option>
      <option value="PDL">PDL Only</option>
    </select>
    <select class="filter-select" id="filterBreakout" onchange="filterTable()">
      <option value="">All Outcomes</option>
      <option value="Yes">Breakout ✅</option>
      <option value="No">No Breakout ❌</option>
    </select>
    <span class="page-info" id="tableCount"></span>
  </div>

  <div class="table-wrapper">
    <table>
      <thead>
        <tr>
          <th onclick="sortTable(0)"># ↕</th>
          <th onclick="sortTable(1)">Date ↕</th>
          <th onclick="sortTable(2)">Touch Time (SGT) ↕</th>
          <th onclick="sortTable(3)">Type ↕</th>
          <th onclick="sortTable(4)">Level ↕</th>
          <th onclick="sortTable(5)">Touch Price ↕</th>
          <th onclick="sortTable(6)">Session ↕</th>
          <th onclick="sortTable(7)">Breakout? ↕</th>
          <th onclick="sortTable(8)">Pullback (pips) ↕</th>
          <th onclick="sortTable(9)">Max PB (pips) ↕</th>
          <th onclick="sortTable(10)">Reward (pips) ↕</th>
          <th onclick="sortTable(11)">R:R ↕</th>
        </tr>
      </thead>
      <tbody id="eventsTableBody"></tbody>
    </table>
  </div>
  <div class="pagination" id="pagination"></div>

</div>

<!-- ═══════════════════════════════════════════════════════════════════ -->
<!--  TAB 6: METHODOLOGY                                                -->
<!-- ═══════════════════════════════════════════════════════════════════ -->
<div id="tab-methodology" class="tab-panel">

  <div class="method-card">
    <h3>📐 Backtest Methodology</h3>
    <p>This backtest analyses every occurrence where XAUUSD price <span class="highlight">touches the previous day's high (PDH) or low (PDL)</span> on a 1-hour candle, then measures how far price pulls back before eventually breaking through that level.</p>
  </div>

  <div class="method-card">
    <h3>📊 Data Source</h3>
    <ul>
      <li><span class="highlight">Instrument:</span> XAUUSD — Gold Futures (GC=F) via Yahoo Finance</li>
      <li><span class="highlight">Timeframe:</span> 1-hour candles (equivalent to 30-min logic as requested)</li>
      <li><span class="highlight">Period:</span> {date_from} to {date_to} ({total_days} trading days)</li>
      <li><span class="highlight">Timezone:</span> All times displayed in Singapore Time (SGT = UTC+8)</li>
    </ul>
  </div>

  <div class="method-card">
    <h3>🎯 Touch Detection Rules</h3>
    <ul>
      <li><span class="highlight">Previous Day High/Low:</span> Computed from the prior calendar day's OHLC in SGT</li>
      <li><span class="highlight">Touch Condition:</span> A candle's High wick reaches within $0.50 of PDH, or Low wick reaches within $0.50 of PDL (~5 pips tolerance)</li>
      <li><span class="highlight">One Touch Per Level Per Day:</span> Only the first touch of each PDH/PDL per day is recorded to avoid double-counting</li>
      <li><span class="highlight">Breakout Confirmation:</span> Price must trade $0.50 beyond the PDH/PDL on the same calendar day (SGT)</li>
    </ul>
  </div>

  <div class="method-card">
    <h3>📏 Pip Definition</h3>
    <p>For XAUUSD: <span class="highlight">1 pip = $0.10</span> (i.e., a $10 move = 100 pips). This is the standard convention for gold trading.</p>
  </div>

  <div class="method-card">
    <h3>🕐 Session Definitions (SGT = UTC+8)</h3>
    <ul>
      <li><span class="highlight" style="color:var(--asian)">Asian Session:</span> 00:00 – 07:59 SGT (Tokyo/Sydney active)</li>
      <li><span class="highlight" style="color:var(--prelondon)">Pre-London:</span> 08:00 – 14:59 SGT (European pre-market)</li>
      <li><span class="highlight" style="color:var(--london)">London Session:</span> 15:00 – 19:59 SGT (London open = 07:00 UTC)</li>
      <li><span class="highlight" style="color:var(--newyork)">New York Session:</span> 20:00 – 23:59 SGT (NY open = 12:00 UTC)</li>
    </ul>
  </div>

  <div class="method-card">
    <h3>⚖️ R:R Calculation</h3>
    <ul>
      <li><span class="highlight">Risk (pullback):</span> Maximum pips price moved against the breakout direction between the touch candle and the first breakout candle</li>
      <li><span class="highlight">Reward:</span> Maximum pips price moved in the breakout direction after the first breakout candle, within the same day</li>
      <li><span class="highlight">R:R Ratio:</span> Reward ÷ Risk (pullback before breakout)</li>
    </ul>
  </div>

  <div class="method-card">
    <h3>⚠️ Important Disclaimers</h3>
    <ul>
      <li>This is a <span class="highlight">statistical backtest only</span> — not financial advice</li>
      <li>Past performance does not guarantee future results</li>
      <li>Slippage, spread, and commissions are not included in R:R calculations</li>
      <li>The backtest uses end-of-bar data; real execution may differ</li>
      <li>Gold futures (GC=F) may have slight price differences from spot XAUUSD</li>
    </ul>
  </div>

</div>

</div><!-- end content -->

<script>
// ── Data ─────────────────────────────────────────────────────────────────────
const SESSION_ORDER = {json.dumps(SESSION_ORDER)};
const SESSION_COLORS = {json.dumps(SESSION_COLORS)};
const PULLBACK_DIST = {json.dumps(pullback_dist)};
const BIN_LABELS = {json.dumps(bin_labels)};
const HOURLY_PDH = {json.dumps(hourly_pdh)};
const HOURLY_PDL = {json.dumps(hourly_pdl)};
const HOURS_LABELS = {json.dumps(hours_labels)};
const RR_DIST_ALL = {json.dumps(rr_dist_all)};
const RR_DIST_SESS = {json.dumps(rr_dist_sess)};
const RR_LABELS = {json.dumps(rr_labels)};
const MONTHLY_LABELS = {json.dumps(monthly['month_str'].tolist())};
const MONTHLY_RATES = {json.dumps(monthly['rate'].tolist())};
const MONTHLY_TOTAL = {json.dumps(monthly['total'].tolist())};
const TABLE_DATA = {json.dumps(table_json)};

const STATS_SESS = {json.dumps(stats_sess.to_dict(orient='records'))};
const STATS_COMBO = {json.dumps(stats_combo.to_dict(orient='records'))};

// ── Tab Navigation ────────────────────────────────────────────────────────────
function showTab(name) {{
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  event.target.classList.add('active');
  if (name === 'sessions') buildSessionCards();
  if (name === 'pullback') buildPullbackTable();
  if (name === 'events') renderTable();
}}

// ── Chart Defaults ────────────────────────────────────────────────────────────
Chart.defaults.color = '#8b949e';
Chart.defaults.borderColor = '#30363d';
Chart.defaults.font.family = "'Segoe UI', system-ui, sans-serif";
Chart.defaults.font.size = 11;

function makeGradient(ctx, color) {{
  const g = ctx.createLinearGradient(0, 0, 0, 300);
  g.addColorStop(0, color + 'cc');
  g.addColorStop(1, color + '22');
  return g;
}}

// ── Overview Charts ───────────────────────────────────────────────────────────
// Session Bar
const sessData = STATS_SESS.filter(s => SESSION_ORDER.includes(s.Session));
const pdh_by_sess = STATS_COMBO.filter(r => r['Touch Type']==='PDH');
const pdl_by_sess = STATS_COMBO.filter(r => r['Touch Type']==='PDL');

new Chart(document.getElementById('chartSessionBar'), {{
  type: 'bar',
  data: {{
    labels: SESSION_ORDER,
    datasets: [
      {{
        label: 'PDH Touches',
        data: SESSION_ORDER.map(s => {{
          const r = pdh_by_sess.find(x => x.Session.startsWith(s));
          return r ? r['Total Touches'] : 0;
        }}),
        backgroundColor: '#f85149cc',
        borderRadius: 4,
      }},
      {{
        label: 'PDL Touches',
        data: SESSION_ORDER.map(s => {{
          const r = pdl_by_sess.find(x => x.Session.startsWith(s));
          return r ? r['Total Touches'] : 0;
        }}),
        backgroundColor: '#3fb950cc',
        borderRadius: 4,
      }}
    ]
  }},
  options: {{ responsive: true, maintainAspectRatio: false,
    plugins: {{ legend: {{ position: 'top' }} }},
    scales: {{ x: {{ grid: {{ display: false }} }}, y: {{ grid: {{ color: '#30363d' }} }} }}
  }}
}});

// Breakout Rate
new Chart(document.getElementById('chartBreakoutRate'), {{
  type: 'bar',
  data: {{
    labels: SESSION_ORDER,
    datasets: [{{
      label: 'Breakout Rate (%)',
      data: SESSION_ORDER.map(s => {{
        const r = sessData.find(x => x.Session === s);
        return r ? r['Breakout %'] : 0;
      }}),
      backgroundColor: SESSION_ORDER.map(s => SESSION_COLORS[s] + 'cc'),
      borderRadius: 6,
    }}]
  }},
  options: {{ responsive: true, maintainAspectRatio: false,
    plugins: {{ legend: {{ display: false }},
      datalabels: {{ color: '#e6edf3', font: {{ weight: 'bold' }}, formatter: v => v + '%' }}
    }},
    scales: {{
      x: {{ grid: {{ display: false }} }},
      y: {{ min: 80, max: 100, grid: {{ color: '#30363d' }}, ticks: {{ callback: v => v + '%' }} }}
    }}
  }},
  plugins: [ChartDataLabels]
}});

// Hourly
new Chart(document.getElementById('chartHourly'), {{
  type: 'bar',
  data: {{
    labels: HOURS_LABELS,
    datasets: [
      {{ label: 'PDH', data: HOURLY_PDH, backgroundColor: '#f8514988', borderRadius: 2 }},
      {{ label: 'PDL', data: HOURLY_PDL, backgroundColor: '#3fb95088', borderRadius: 2 }}
    ]
  }},
  options: {{ responsive: true, maintainAspectRatio: false,
    plugins: {{ legend: {{ position: 'top' }} }},
    scales: {{
      x: {{ grid: {{ display: false }}, ticks: {{ maxRotation: 45, font: {{ size: 9 }} }} }},
      y: {{ grid: {{ color: '#30363d' }} }}
    }}
  }}
}});

// Monthly
new Chart(document.getElementById('chartMonthly'), {{
  type: 'line',
  data: {{
    labels: MONTHLY_LABELS,
    datasets: [{{
      label: 'Breakout Rate (%)',
      data: MONTHLY_RATES,
      borderColor: '#f0b429',
      backgroundColor: 'rgba(240,180,41,0.1)',
      fill: true,
      tension: 0.3,
      pointRadius: 3,
      pointBackgroundColor: '#f0b429',
    }}]
  }},
  options: {{ responsive: true, maintainAspectRatio: false,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{
      x: {{ grid: {{ display: false }}, ticks: {{ maxRotation: 45, font: {{ size: 9 }} }} }},
      y: {{ min: 70, max: 100, grid: {{ color: '#30363d' }}, ticks: {{ callback: v => v + '%' }} }}
    }}
  }}
}});

// ── Session Tab ───────────────────────────────────────────────────────────────
const SESSION_TIMES = {{
  'Asian': '00:00–07:59 SGT',
  'Pre-London': '08:00–14:59 SGT',
  'London': '15:00–19:59 SGT',
  'New York': '20:00–23:59 SGT'
}};

function buildSessionCards() {{
  const container = document.getElementById('sessionCards');
  if (container.innerHTML !== '') return;
  
  STATS_SESS.forEach(s => {{
    const color = SESSION_COLORS[s.Session] || '#888';
    const boRate = s['Breakout %'];
    const card = `
      <div class="session-card">
        <div class="sess-header">
          <div class="sess-dot" style="background:${{color}}"></div>
          <div class="sess-title">${{s.Session}}</div>
          <div class="sess-time">${{SESSION_TIMES[s.Session] || ''}}</div>
        </div>
        <div class="sess-stats">
          <div class="sess-stat">
            <div class="s-label">Total Touches</div>
            <div class="s-value" style="color:${{color}}">${{s['Total Touches']}}</div>
          </div>
          <div class="sess-stat">
            <div class="s-label">Breakout Rate</div>
            <div class="s-value" style="color:#3fb950">${{boRate}}%</div>
            <div class="progress-bar"><div class="progress-fill" style="width:${{boRate}}%;background:#3fb950"></div></div>
          </div>
          <div class="sess-stat">
            <div class="s-label">Median Pullback</div>
            <div class="s-value" style="color:#4A90D9">${{s['Median Pullback (pips)']}}</div>
            <div class="s-sub">pips</div>
          </div>
          <div class="sess-stat">
            <div class="s-label">P25 / P75</div>
            <div class="s-value" style="color:#7B68EE;font-size:14px">${{s['P25 Pullback (pips)']}} / ${{s['P75 Pullback (pips)']}}</div>
            <div class="s-sub">pips</div>
          </div>
          <div class="sess-stat">
            <div class="s-label">Avg R:R</div>
            <div class="s-value" style="color:#f0b429">${{s['Avg R:R']}}</div>
          </div>
          <div class="sess-stat">
            <div class="s-label">Median R:R</div>
            <div class="s-value" style="color:#f0b429">${{s['Median R:R']}}</div>
          </div>
          <div class="sess-stat">
            <div class="s-label">R:R &gt; 1:1</div>
            <div class="s-value" style="color:#3fb950">${{s['R:R > 1 %']}}%</div>
          </div>
          <div class="sess-stat">
            <div class="s-label">R:R &gt; 2:1</div>
            <div class="s-value" style="color:#3fb950">${{s['R:R > 2 %']}}%</div>
          </div>
        </div>
      </div>`;
    container.innerHTML += card;
  }});

  // Session pullback chart
  new Chart(document.getElementById('chartSessPullback'), {{
    type: 'bar',
    data: {{
      labels: SESSION_ORDER,
      datasets: [
        {{
          label: 'Avg Pullback',
          data: SESSION_ORDER.map(s => {{ const r = STATS_SESS.find(x => x.Session===s); return r ? r['Avg Pullback (pips)'] : 0; }}),
          backgroundColor: SESSION_ORDER.map(s => SESSION_COLORS[s] + 'aa'),
          borderRadius: 6,
        }},
        {{
          label: 'Median Pullback',
          data: SESSION_ORDER.map(s => {{ const r = STATS_SESS.find(x => x.Session===s); return r ? r['Median Pullback (pips)'] : 0; }}),
          backgroundColor: SESSION_ORDER.map(s => SESSION_COLORS[s] + '55'),
          borderRadius: 6,
        }}
      ]
    }},
    options: {{ responsive: true, maintainAspectRatio: false,
      plugins: {{ legend: {{ position: 'top' }} }},
      scales: {{ x: {{ grid: {{ display: false }} }}, y: {{ grid: {{ color: '#30363d' }} }} }}
    }}
  }});

  // Session R:R chart
  new Chart(document.getElementById('chartSessRR'), {{
    type: 'bar',
    data: {{
      labels: SESSION_ORDER,
      datasets: [
        {{
          label: 'Avg R:R',
          data: SESSION_ORDER.map(s => {{ const r = STATS_SESS.find(x => x.Session===s); return r ? r['Avg R:R'] : 0; }}),
          backgroundColor: '#f0b42988',
          borderRadius: 6,
        }},
        {{
          label: 'Median R:R',
          data: SESSION_ORDER.map(s => {{ const r = STATS_SESS.find(x => x.Session===s); return r ? r['Median R:R'] : 0; }}),
          backgroundColor: '#f0b42944',
          borderRadius: 6,
        }}
      ]
    }},
    options: {{ responsive: true, maintainAspectRatio: false,
      plugins: {{ legend: {{ position: 'top' }} }},
      scales: {{ x: {{ grid: {{ display: false }} }}, y: {{ grid: {{ color: '#30363d' }} }} }}
    }}
  }});

  // PDH vs PDL
  const pdhRates = SESSION_ORDER.map(s => {{
    const r = STATS_COMBO.find(x => x.Session === s + ' – PDH');
    return r ? r['Breakout %'] : 0;
  }});
  const pdlRates = SESSION_ORDER.map(s => {{
    const r = STATS_COMBO.find(x => x.Session === s + ' – PDL');
    return r ? r['Breakout %'] : 0;
  }});
  new Chart(document.getElementById('chartPDHvsPDL'), {{
    type: 'bar',
    data: {{
      labels: SESSION_ORDER,
      datasets: [
        {{ label: 'PDH Breakout %', data: pdhRates, backgroundColor: '#f8514988', borderRadius: 4 }},
        {{ label: 'PDL Breakout %', data: pdlRates, backgroundColor: '#3fb95088', borderRadius: 4 }}
      ]
    }},
    options: {{ responsive: true, maintainAspectRatio: false,
      plugins: {{ legend: {{ position: 'top' }},
        datalabels: {{ color: '#e6edf3', font: {{ size: 10 }}, formatter: v => v + '%' }}
      }},
      scales: {{
        x: {{ grid: {{ display: false }} }},
        y: {{ min: 70, max: 100, grid: {{ color: '#30363d' }}, ticks: {{ callback: v => v + '%' }} }}
      }}
    }},
    plugins: [ChartDataLabels]
  }});
}}

// ── Pullback Charts ───────────────────────────────────────────────────────────
function makePullbackChart(canvasId, sess, color) {{
  const data = PULLBACK_DIST[sess] || [];
  new Chart(document.getElementById(canvasId), {{
    type: 'bar',
    data: {{
      labels: BIN_LABELS,
      datasets: [{{ label: 'Count', data: data, backgroundColor: color + 'aa', borderRadius: 4 }}]
    }},
    options: {{ responsive: true, maintainAspectRatio: false,
      plugins: {{ legend: {{ display: false }} }},
      scales: {{
        x: {{ grid: {{ display: false }}, ticks: {{ font: {{ size: 9 }} }} }},
        y: {{ grid: {{ color: '#30363d' }} }}
      }}
    }}
  }});
}}

// All sessions combined
const allPullbackData = BIN_LABELS.map((_, i) => SESSION_ORDER.reduce((sum, s) => sum + (PULLBACK_DIST[s]?.[i] || 0), 0));
new Chart(document.getElementById('chartPullbackAll'), {{
  type: 'bar',
  data: {{
    labels: BIN_LABELS,
    datasets: SESSION_ORDER.map(s => ({{
      label: s,
      data: PULLBACK_DIST[s] || [],
      backgroundColor: SESSION_COLORS[s] + '99',
      borderRadius: 4,
    }}))
  }},
  options: {{ responsive: true, maintainAspectRatio: false,
    plugins: {{ legend: {{ position: 'top' }} }},
    scales: {{
      x: {{ stacked: true, grid: {{ display: false }} }},
      y: {{ stacked: true, grid: {{ color: '#30363d' }} }}
    }}
  }}
}});

makePullbackChart('chartPbAsian', 'Asian', '#4A90D9');
makePullbackChart('chartPbPreLondon', 'Pre-London', '#7B68EE');
makePullbackChart('chartPbLondon', 'London', '#E8A838');
makePullbackChart('chartPbNewYork', 'New York', '#E84040');

function buildPullbackTable() {{
  const tbody = document.getElementById('pullbackTableBody');
  if (tbody.innerHTML !== '') return;
  
  // We'll compute percentiles from the raw data embedded in table
  const percData = {perc_data_json};
  
  // Compute ALL row
  const allPb = TABLE_DATA.map(r => r['Pullback (pips)']);
  
  Object.entries(percData).forEach(([sess, vals]) => {{
    const color = sess === 'ALL' ? '#e6edf3' : (SESSION_COLORS[sess] || '#888');
    tbody.innerHTML += `<tr>
      <td style="color:${{color}};font-weight:600">${{sess}}</td>
      <td>${{vals.P10}}</td>
      <td>${{vals.P25}}</td>
      <td style="font-weight:600">${{vals.P50}}</td>
      <td>${{vals.P75}}</td>
      <td>${{vals.P90}}</td>
      <td>${{vals.P95}}</td>
      <td>${{vals.Avg}}</td>
      <td style="color:#f85149">${{vals.Max}}</td>
    </tr>`;
  }});
}}

// ── R:R Charts ────────────────────────────────────────────────────────────────
new Chart(document.getElementById('chartRRAll'), {{
  type: 'bar',
  data: {{
    labels: RR_LABELS,
    datasets: [{{ label: 'Count', data: RR_DIST_ALL, backgroundColor: '#f0b42999', borderRadius: 4 }}]
  }},
  options: {{ responsive: true, maintainAspectRatio: false,
    plugins: {{ legend: {{ display: false }},
      datalabels: {{ color: '#e6edf3', font: {{ size: 10 }}, anchor: 'end', align: 'top' }}
    }},
    scales: {{ x: {{ grid: {{ display: false }} }}, y: {{ grid: {{ color: '#30363d' }} }} }}
  }},
  plugins: [ChartDataLabels]
}});

new Chart(document.getElementById('chartRRSess'), {{
  type: 'bar',
  data: {{
    labels: RR_LABELS,
    datasets: SESSION_ORDER.map(s => ({{
      label: s,
      data: RR_DIST_SESS[s] || [],
      backgroundColor: SESSION_COLORS[s] + '99',
      borderRadius: 2,
    }}))
  }},
  options: {{ responsive: true, maintainAspectRatio: false,
    plugins: {{ legend: {{ position: 'top' }} }},
    scales: {{
      x: {{ stacked: true, grid: {{ display: false }} }},
      y: {{ stacked: true, grid: {{ color: '#30363d' }} }}
    }}
  }}
}});

// R:R Threshold
const thresholds = ['R:R > 1 %', 'R:R > 2 %', 'R:R > 3 %'];
const threshLabels = ['> 1:1', '> 2:1', '> 3:1'];
new Chart(document.getElementById('chartRRThreshold'), {{
  type: 'bar',
  data: {{
    labels: threshLabels,
    datasets: SESSION_ORDER.map(s => ({{
      label: s,
      data: thresholds.map(t => {{ const r = STATS_SESS.find(x => x.Session===s); return r ? r[t] : 0; }}),
      backgroundColor: SESSION_COLORS[s] + 'aa',
      borderRadius: 4,
    }}))
  }},
  options: {{ responsive: true, maintainAspectRatio: false,
    plugins: {{ legend: {{ position: 'top' }},
      datalabels: {{ display: false }}
    }},
    scales: {{
      x: {{ grid: {{ display: false }} }},
      y: {{ max: 100, grid: {{ color: '#30363d' }}, ticks: {{ callback: v => v + '%' }} }}
    }}
  }}
}});

// ── Events Table ──────────────────────────────────────────────────────────────
let filteredData = [...TABLE_DATA];
let currentPage = 1;
const PAGE_SIZE = 50;
let sortCol = 0;
let sortAsc = false;

const SESSION_BADGE = {{
  'Asian': 'badge-asian',
  'Pre-London': 'badge-prelondon',
  'London': 'badge-london',
  'New York': 'badge-newyork'
}};

function filterTable() {{
  const search = document.getElementById('tableSearch').value.toLowerCase();
  const sess = document.getElementById('filterSession').value;
  const type = document.getElementById('filterType').value;
  const bo = document.getElementById('filterBreakout').value;
  
  filteredData = TABLE_DATA.filter(r => {{
    const matchSearch = !search || JSON.stringify(r).toLowerCase().includes(search);
    const matchSess = !sess || r['Session'] === sess;
    const matchType = !type || r['Type'] === type;
    const matchBo = !bo || (bo === 'Yes' ? r['Breakout?'].includes('Yes') : r['Breakout?'].includes('No'));
    return matchSearch && matchSess && matchType && matchBo;
  }});
  currentPage = 1;
  renderTable();
}}

function renderTable() {{
  const tbody = document.getElementById('eventsTableBody');
  const start = (currentPage - 1) * PAGE_SIZE;
  const end = start + PAGE_SIZE;
  const pageData = filteredData.slice(start, end);
  
  tbody.innerHTML = pageData.map((r, i) => `
    <tr>
      <td style="color:#8b949e">${{start + i + 1}}</td>
      <td>${{r['Date']}}</td>
      <td>${{r['Touch Time (SGT)']}}</td>
      <td><span class="badge ${{r['Type']==='PDH' ? 'badge-pdh' : 'badge-pdl'}}">${{r['Type']}}</span></td>
      <td>${{r['Level']}}</td>
      <td>${{r['Touch Price']}}</td>
      <td><span class="badge ${{SESSION_BADGE[r['Session']] || ''}}">${{r['Session']}}</span></td>
      <td>${{r['Breakout?']}}</td>
      <td style="color:#4A90D9;font-weight:600">${{r['Pullback (pips)']}}</td>
      <td style="color:#7B68EE">${{r['Max Pullback (pips)']}}</td>
      <td style="color:#3fb950">${{r['Reward (pips)']}}</td>
      <td style="color:#f0b429;font-weight:600">${{r['R:R']}}</td>
    </tr>`).join('');
  
  document.getElementById('tableCount').textContent = `Showing ${{start+1}}–${{Math.min(end, filteredData.length)}} of ${{filteredData.length}} events`;
  renderPagination();
}}

function renderPagination() {{
  const total = Math.ceil(filteredData.length / PAGE_SIZE);
  const pag = document.getElementById('pagination');
  let html = '';
  for (let i = 1; i <= total; i++) {{
    if (i === 1 || i === total || (i >= currentPage - 2 && i <= currentPage + 2)) {{
      html += `<button class="page-btn ${{i===currentPage?'active':''}}" onclick="goPage(${{i}})">${{i}}</button>`;
    }} else if (i === currentPage - 3 || i === currentPage + 3) {{
      html += `<span style="color:#8b949e">…</span>`;
    }}
  }}
  pag.innerHTML = html;
}}

function goPage(p) {{
  currentPage = p;
  renderTable();
  document.getElementById('tab-events').scrollTop = 0;
}}

function sortTable(col) {{
  const keys = ['_idx','Date','Touch Time (SGT)','Type','Level','Touch Price','Session','Breakout?','Pullback (pips)','Max Pullback (pips)','Reward (pips)','R:R'];
  const key = keys[col];
  if (!key || key === '_idx') return;
  sortAsc = (sortCol === col) ? !sortAsc : true;
  sortCol = col;
  filteredData.sort((a, b) => {{
    const av = a[key], bv = b[key];
    if (typeof av === 'number') return sortAsc ? av - bv : bv - av;
    return sortAsc ? String(av).localeCompare(String(bv)) : String(bv).localeCompare(String(av));
  }});
  currentPage = 1;
  renderTable();
}}

// Init
renderTable();
</script>
</body>
</html>"""

with open('/home/ubuntu/backtest/xauusd_backtest_report.html', 'w') as f:
    f.write(html)

print("HTML report generated: xauusd_backtest_report.html")
