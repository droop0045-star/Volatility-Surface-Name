# main.py
import src

if __name__ == "__main__":
    ticker_target = "SPY"
    risk_free_rate = 0.040   # Set closer to current macro yield expectations
    dividend_yield = 0.005   # SPY continuous dividend yield proxy (~1.3%)

    # 1. Pull data arrays
    cleaned_data, current_S = src.get_market_options_data(ticker_target)

    # 2. Run your custom Newton-Raphson math solver with q included
    print("Running custom numerical pricing solver with dividend adjustments...")
    cleaned_data["IV"] = cleaned_data.apply(
        lambda row: src.find_implied_volatility(
            market_price=row["market_price"],
            S=row["S"],
            K=row["strike"],
            T=row["T"],
            r=risk_free_rate,
            q=dividend_yield, # Passed down to the equation
        ),
        axis=1,
    )

    cleaned_data = cleaned_data.dropna(subset=["IV"])
    cleaned_data = cleaned_data[cleaned_data["yahoo_IV"] > 0]

    if cleaned_data.empty:
        print("Error: No valid options data available after filtering. Cannot plot volatility surface.")
        exit(1)

    # 3. Build your 3D Plotly Surface sheet
    custom_rbf = src.build_and_plot_volatility_surface(cleaned_data)
    
    # 4. Plot 2D slices (smile and term structure)
    src.plot_volatility_slices(cleaned_data, custom_rbf)