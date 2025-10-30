"""Generate a ChatGPT prompt from the daily portfolio data.

This script reads the Daily Updates.csv and generates a prompt file
in the format expected by ChatGPT for portfolio management decisions.
"""

from pathlib import Path
import sys
import pandas as pd
import numpy as np

# Add parent directory to path to import trading_script
sys.path.append(str(Path(__file__).resolve().parents[1]))

from trading_script import (
    download_price_data,
    last_trading_date,
    load_benchmarks,
    PORTFOLIO_CSV_PATH,
    set_data_dir
)


def generate_chatgpt_prompt(data_dir: Path, output_file: Path | None = None, starting_equity: float | None = None) -> str:
    """Generate a ChatGPT prompt from the daily portfolio data.
    
    Args:
        data_dir: Directory containing the portfolio CSV files
        output_file: Optional path to save the prompt (defaults to prompt.md in data_dir)
        starting_equity: Starting equity for S&P 500 comparison (if None, will not include)
    
    Returns:
        The generated prompt as a string
    """
    # Set the data directory for trading_script module
    set_data_dir(data_dir)
    
    # Use the portfolio CSV from the data directory
    portfolio_csv = data_dir / "Daily Updates.csv"
    
    # Read the portfolio CSV
    if not portfolio_csv.exists():
        raise FileNotFoundError(f"Portfolio CSV not found at {portfolio_csv}")
    
    df = pd.read_csv(portfolio_csv)
    
    if df.empty:
        raise ValueError("Portfolio CSV is empty. Run ProcessPortfolio.py first.")
    
    # Get the latest date's data
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    latest_date = df["Date"].max()
    latest_data = df[df["Date"] == latest_date].copy()
    
    # Separate portfolio holdings from TOTAL row
    total_row = latest_data[latest_data["Ticker"] == "TOTAL"]
    holdings = latest_data[latest_data["Ticker"] != "TOTAL"].copy()
    
    if total_row.empty:
        raise ValueError("No TOTAL row found in the latest data")
    
    cash_balance = float(total_row["Cash Balance"].iloc[0])
    total_equity = float(total_row["Total Equity"].iloc[0])
    
    # Get price data for holdings and benchmarks
    today_str = latest_date.strftime("%Y-%m-%d")
    end_d = last_trading_date()
    start_d = (end_d - pd.Timedelta(days=4)).normalize()
    
    # Load benchmarks from config
    benchmarks = load_benchmarks()
    
    # Collect all tickers (holdings + benchmarks)
    portfolio_tickers = holdings["Ticker"].tolist()
    all_tickers = portfolio_tickers + benchmarks
    
    # Build the prompt
    lines = []

    # Add instructions
    lines.append("Here is your update for today. You can make any changes you see fit (if necessary). You do not have to ask permissions for any changes, as you have full control.")

    lines.append(f"prices and updates for {today_str}")
    
    # Get price data for each ticker
    for ticker in all_tickers:
        try:
            fetch = download_price_data(ticker, start=start_d, end=(end_d + pd.Timedelta(days=1)), progress=False)
            data = fetch.df
            
            if data.empty or len(data) < 2:
                lines.append(f"{ticker} closing price: N/A")
                lines.append(f"{ticker} volume for today: N/A")
                lines.append(f"percent change from the day before: N/A")
                continue
            
            price = float(data["Close"].iloc[-1])
            last_price = float(data["Close"].iloc[-2])
            volume = float(data["Volume"].iloc[-1])
            percent_change = ((price - last_price) / last_price) * 100
            
            lines.append(f"{ticker} closing price: {price:.2f}")
            lines.append(f"{ticker} volume for today: ${volume:,.1f}")
            lines.append(f"percent change from the day before: {percent_change:+.2f}%")
            
        except Exception as e:
            lines.append(f"{ticker} closing price: ERROR - {e}")
            lines.append(f"{ticker} volume for today: N/A")
            lines.append(f"percent change from the day before: N/A")
    
    # Calculate Sharpe and Sortino ratios
    totals = df[df["Ticker"] == "TOTAL"].copy()
    totals["Date"] = pd.to_datetime(totals["Date"], errors="coerce")
    totals = totals.sort_values("Date")
    
    if len(totals) >= 2:
        equity_series = totals.set_index("Date")["Total Equity"].astype(float).sort_index()
        r = equity_series.pct_change().dropna()
        n_days = len(r)
        
        if n_days >= 2:
            # Risk-free rate calculation
            rf_annual = 0.045
            rf_daily = (1 + rf_annual) ** (1 / 252) - 1
            rf_period = (1 + rf_daily) ** n_days - 1
            
            mean_daily = float(r.mean())
            std_daily = float(r.std(ddof=1))
            
            # Downside deviation
            downside = (r - rf_daily).clip(upper=0)
            downside_std = float((downside.pow(2).mean()) ** 0.5) if not downside.empty else np.nan
            
            # Total return
            r_numeric = pd.to_numeric(r, errors="coerce")
            r_numeric = r_numeric[~r_numeric.isna()].astype(float)
            r_numeric = r_numeric[np.isfinite(r_numeric)]
            
            if len(r_numeric) > 0:
                arr = np.asarray(r_numeric.values, dtype=float)
                period_return = float(np.prod(1 + arr) - 1) if arr.size > 0 else float('nan')
            else:
                period_return = float('nan')
            
            # Sharpe / Sortino
            sharpe_period = (period_return - rf_period) / (std_daily * np.sqrt(n_days)) if std_daily > 0 else np.nan
            sortino_period = (period_return - rf_period) / (downside_std * np.sqrt(n_days)) if downside_std and downside_std > 0 else np.nan
            
            if not np.isnan(sharpe_period):
                lines.append(f"Total Sharpe Ratio over {n_days} days: {sharpe_period:.4f}")
            if not np.isnan(sortino_period):
                lines.append(f"Total Sortino Ratio over {n_days} days: {sortino_period:.4f}")
    
    # Add equity comparison
    lines.append(f"Latest Gemini Equity: ${total_equity:.2f}")
    
    # S&P 500 comparison (if starting equity provided)
    if starting_equity is not None and len(totals) >= 2:
        try:
            equity_series = totals.set_index("Date")["Total Equity"].astype(float).sort_index()
            spx_fetch = download_price_data(
                "^GSPC",
                start=equity_series.index.min(),
                end=equity_series.index.max() + pd.Timedelta(days=1),
                progress=False,
            )
            spx = spx_fetch.df
            
            if not spx.empty:
                initial_price = float(spx["Close"].iloc[0])
                price_now = float(spx["Close"].iloc[-1])
                spx_value = (starting_equity / initial_price) * price_now
                lines.append(f"${starting_equity:.0f} Invested in the S&P 500: ${spx_value:.2f}")
        except Exception:
            pass  # Skip S&P comparison if it fails
    
    # Add portfolio holdings
    lines.append("today's portfolio: ticker shares buy_price stop_loss cost_basis")
    for idx, row in holdings.iterrows():
        ticker = row["Ticker"]
        shares = row["Shares"]
        buy_price = row["Buy Price"]
        stop_loss = row["Stop Loss"]
        cost_basis = row["Cost Basis"]
        lines.append(f"{ticker} {shares} {buy_price} {stop_loss} {cost_basis}")
    
    # Add cash balance
    lines.append(f"cash balance: {cash_balance:.2f}")
        
    # Join all lines
    prompt = "\n".join(lines)
    
    # Save to file if output path provided
    if output_file is None:
        output_file = data_dir / "prompt.md"
    
    output_file.write_text(prompt)
    print(f"Prompt saved to: {output_file}")
    
    return prompt


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate ChatGPT prompt from portfolio data")
    parser.add_argument("--data-dir", type=str, default="Start Your Own", help="Directory containing portfolio CSV files")
    parser.add_argument("--output", type=str, help="Output file path (default: prompt.md in data-dir)")
    parser.add_argument("--starting-equity", type=float, help="Starting equity for S&P 500 comparison")
    
    args = parser.parse_args()
    
    data_dir = Path(args.data_dir)
    if not data_dir.is_absolute():
        data_dir = Path(__file__).resolve().parents[1] / data_dir
    
    output_file = Path(args.output) if args.output else None
    
    prompt = generate_chatgpt_prompt(data_dir, output_file, args.starting_equity)
    print("\n" + "="*60)
    print("Generated Prompt:")
    print("="*60)
    print(prompt)
