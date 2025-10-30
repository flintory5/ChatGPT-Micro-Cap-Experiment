# How to Use Your ChatGPT Portfolio Tracker

This guide explains how to use the portfolio tracking system for your own micro-cap investing with ChatGPT.

## Quick Start

### Daily Workflow

1. **Record Your Trades and Update Portfolio**
   ```bash
   source ../venv/bin/activate  # Activate virtual environment
   python ProcessPortfolio.py
   ```
   This will:
   - Prompt you to enter any trades (buy/sell)
   - Fetch current market prices
   - Update your portfolio value
   - Save results to `Daily Updates.csv` and `Trade Log.csv`

2. **Generate ChatGPT Prompt**
   ```bash
   python GeneratePrompt.py
   ```
   This will create a `prompt.md` file with today's market data formatted for ChatGPT.
   
   Or use the command-line version:
   ```bash
   python generate_prompt.py --data-dir "." --starting-equity 700 --output prompt.md
   ```

3. **Copy Prompt to ChatGPT**
   - Open `prompt.md`
   - Copy the entire contents
   - Paste into ChatGPT
   - ChatGPT will analyze and make trading recommendations

4. **Execute Trades**
   - Follow ChatGPT's recommendations (or not!)
   - Place trades with your broker
   - Run step 1 again to record the trades

5. **Generate Performance Graph**
   ```bash
   python Generate Graph.py --start-equity 700 --output Results.png
   ```
   This creates a chart comparing your portfolio vs S&P 500.

## Files Explained

### Your Data Files
- **Daily Updates.csv** - Daily snapshots of your portfolio value (used for graphs)
- **Trade Log.csv** - Permanent record of all buy/sell transactions
- **prompt.md** - Generated ChatGPT prompt (created by generate_prompt.py)
- **Results.png** - Performance chart (created by Generate Graph.py)

### Scripts
- **ProcessPortfolio.py** - Main script to record trades and update portfolio
- **generate_prompt.py** - Creates the ChatGPT prompt from your data
- **GeneratePrompt.py** - Simplified wrapper for generate_prompt.py
- **Generate Graph.py** - Creates performance charts

## Important Notes

### File Synchronization Issue (FIXED!)
Previously, there was a bug where:
- `Generate Graph.py` was reading from `chatgpt_portfolio_update.csv`
- `ProcessPortfolio.py` was writing to `Daily Updates.csv`

This has been **fixed**. Both scripts now use `Daily Updates.csv`.

### Daily Updates Behavior
The `Daily Updates.csv` file:
- Stores one snapshot per day
- **Overwrites** entries for the current date each time you run ProcessPortfolio.py
- **Preserves** entries from previous dates
- This is **correct behavior** - you should only have one entry per day

### Trade Log Behavior
The `Trade Log.csv` file:
- Permanently records every buy/sell transaction
- **Never** overwrites or deletes entries
- Grows over time as you make trades

### Performance Metrics
Some metrics require multiple days of data:
- **Sharpe Ratio** - Needs at least 2 days
- **Sortino Ratio** - Needs at least 2 days  
- **S&P 500 Comparison** - Needs at least 2 days

These will appear in your prompt once you have accumulated enough daily snapshots.

## Troubleshooting

### "Portfolio CSV not found" error
Make sure you've run `ProcessPortfolio.py` at least once to create the CSV files.

### No Sharpe/Sortino ratios in prompt
You need at least 2 days of data. Run the workflow daily to accumulate history.

### Graph shows only one point
You need multiple days of data. Keep running daily to build up your performance history.

### Module not found errors
Make sure you activate the virtual environment:
```bash
source ../venv/bin/activate
```

## Example Prompt Output

Your generated prompt will look like this:

```
prices and updates for 2025-10-30
MIST closing price: 1.84
MIST volume for today: $1,503,000.0
percent change from the day before: +0.55%
ATRA closing price: 14.06
ATRA volume for today: $37,700.0
percent change from the day before: -7.56%
...
Total Sharpe Ratio over 5 days: 0.9362
Total Sortino Ratio over 5 days: 1.9217
Latest ChatGPT Equity: $686.18
$700 Invested in the S&P 500: $702.04
today's portfolio: ticker shares buy_price stop_loss cost_basis
MIST 184.0 1.865 0.0 343.16
ATRA 22.0 14.57 0.0 320.54
cash balance: 38.30
Here is your update for today. You can make any changes you see fit (if necessary). 
You do not have to ask permissions for any changes, as you have full control.
```

## Tips

1. **Run daily** - The more data you accumulate, the better your performance metrics
2. **Be consistent** - Try to run at the same time each day (e.g., after market close)
3. **Keep backups** - Your CSV files contain your entire trading history
4. **Starting equity** - Remember your starting equity amount for S&P 500 comparisons

## Questions?

If you run into issues, check:
1. Are you in the virtual environment?
2. Do your CSV files exist?
3. Have you run ProcessPortfolio.py at least once?
