import pandas as pd
import json

# Load the data
df = pd.read_csv('/home/ubuntu/backtest/ha_touch_events.csv')
stats = pd.read_csv('/home/ubuntu/backtest/ha_stats_by_session.csv')

# Prepare HTML report
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XAUUSD Heikin-Ashi Reversal Backtest</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: sans-serif; background: #0d1117; color: #c9d1d9; padding: 20px; }}
        h1 {{ color: #58a6ff; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
        th, td {{ padding: 10px; border: 1px solid #30363d; text-align: left; }}
        th {{ background: #161b22; }}
        .card {{ background: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 6px; margin-bottom: 20px; }}
        .summary {{ display: flex; gap: 20px; }}
        .stat {{ flex: 1; text-align: center; }}
        .stat-val {{ font-size: 24px; font-weight: bold; color: #238636; }}
    </style>
</head>
<body>
    <h1>XAUUSD Heikin-Ashi Reversal Backtest</h1>
    <p>Strategy: Wait for touch of Previous Day H/L on 30m TF, wait for pullback, enter on first Heikin-Ashi color change.</p>
    
    <div class="summary">
        <div class="card stat">
            <div>Total Reversal Events</div>
            <div class="stat-val">{len(df)}</div>
        </div>
        <div class="card stat">
            <div>Median Pullback (All)</div>
            <div class="stat-val">${df['pullback_usd'].median():.2f}</div>
        </div>
        <div class="card stat">
            <div>Avg Pullback (All)</div>
            <div class="stat-val">${df['pullback_usd'].mean():.2f}</div>
        </div>
    </div>

    <div class="card">
        <h3>Session Performance (USD)</h3>
        {stats.to_html(index=False)}
    </div>

    <div class="card">
        <h3>All 109 Reversal Events</h3>
        {df.to_html(index=False)}
    </div>
</body>
</html>
"""

with open('/home/ubuntu/backtest/ha_xauusd_report.html', 'w') as f:
    f.write(html_content)
print("Heikin-Ashi report generated.")
