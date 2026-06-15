import datetime
import numpy as np
import pandas as pd
import yfinance as yf


def get_market_options_data(ticker_symbol):
    print(f"Fetching market data for {ticker_symbol}...")
    ticker = yf.Ticker(ticker_symbol)

    # Fetch underlying asset price
    ticker_history = ticker.history(period="1d")
    if ticker_history.empty:
        raise ValueError(
            f"Could not fetch underlying price for {ticker_symbol}."
        )
    S = ticker_history["Close"].iloc[-1]
    print(f"Current Stock Price (S): ${S:.2f}")

    all_options = []
    today = datetime.date.today()

    # Iterate through all available expiration dates
    for exp_date_str in ticker.options:
        exp_date = datetime.datetime.strptime(exp_date_str, "%Y-%m-%d").date()

        # Calculate Time to Maturity (T) in years
        T = (exp_date - today).days / 365.0

        # Skip options expiring today or in the past to avoid math errors
        if T <= 0:
            continue

        opt_chain = ticker.option_chain(exp_date_str)
        calls = opt_chain.calls.copy()

        # Step 4 Data Cleaning & Filtering:
        # 1. Compute mid-price as proxy for market price
        calls["market_price"] = (calls["bid"] + calls["ask"]) / 2

        # 2. Filter out illiquid options
        calls = calls[
            (calls["bid"] > 0) & (calls["ask"] > 0) & (calls["volume"] > 0)
        ]

        # 3. Filter for intrinsic value boundary
        intrinsic_value = np.maximum(S - calls["strike"], 0)
        calls = calls[calls["market_price"] > intrinsic_value]

        # Structure final features
        calls["T"] = T
        calls["S"] = S
        calls["yahoo_IV"] = calls["impliedVolatility"]
        
        # Keep both metrics for verification
        calls_cleaned = calls[["S", "strike", "T", "market_price", "volume", "yahoo_IV"]]
        all_options.append(calls_cleaned)

    if not all_options:
        raise ValueError("No valid options data found after filtering.")

    options_df = pd.concat(all_options, ignore_index=True)
    return options_df, S