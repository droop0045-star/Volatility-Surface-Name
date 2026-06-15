# Volatility Surface Project

A Python application that builds an implied volatility surface from real-time market options data using the Black-Scholes model and Radial Basis Function (RBF) interpolation.

## Features

- **Real-time Data Fetching**: Pulls live options data from Yahoo Finance using `yfinance`
- **Implied Volatility Calculation**: Uses Newton-Raphson root-finding method to compute IV from market prices via inverse Black-Scholes formula with dividend yield support
- **3D Volatility Surface**: Constructs and visualizes a smooth 3D surface using RBF interpolation (thin-plate splines)
- **Volatility Smile**: Plots the 2D volatility smile cross-section at a fixed maturity (~3 months)
- **Interactive Plots**: Generates interactive HTML plots using Plotly and static visualizations with Matplotlib

## Project Structure

```
Volatility_Surface_Project/
├── main.py                      # Entry point
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── src/
│   ├── __init__.py             # Package initialization
│   ├── bs_engine.py            # Black-Scholes pricing and IV solver
│   ├── data_fetcher.py         # Market data retrieval and cleaning
│   └── visualizer.py           # 3D surface and 2D slices plotting
├── notebooks/                  # Jupyter notebooks (optional)
├── volatility_surface.html     # Generated interactive 3D surface plot
└── volatility_curves.png       # Generated volatility smile plot
```

## Installation

1. Clone or download the project

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the main script:
```bash
python3 main.py
```

### What it does:
1. Fetches live SPY options data from Yahoo Finance
2. Calculates implied volatility for each option using the inverse Black-Scholes formula
3. Builds a 3D volatility surface via RBF interpolation
4. Generates plots:
   - **volatility_surface.html**: Interactive 3D surface (open in browser)
   - **volatility_curves.png**: 2D volatility smile cross-section

## Configuration

Edit `main.py` to change:
- **Ticker Symbol**: `ticker_target = "SPY"` (default)
- **Risk-Free Rate**: `risk_free_rate = 0.040` (4% default)
- **Dividend Yield**: `dividend_yield = 0.005` (0.5% default)

## Core Modules

### `bs_engine.py`
- `black_scholes_call()`: Calculates European call option price
- `black_scholes_vega()`: Computes option sensitivity to volatility
- `find_implied_volatility()`: Solves for IV using Newton-Raphson method

### `data_fetcher.py`
- `get_market_options_data()`: Fetches and cleans options data from Yahoo Finance

### `visualizer.py`
- `build_and_plot_volatility_surface()`: Creates 3D surface via RBF interpolation
- `plot_volatility_slices()`: Plots 2D volatility smile

## Mathematical Foundation

### Black-Scholes Formula
The project uses the Black-Scholes-Merton model with continuous dividend yield:

```
C = S*e^(-q*T)*N(d1) - K*e^(-r*T)*N(d2)

where:
  d1 = [ln(S/K) + (r - q + 0.5*σ²)*T] / (σ*√T)
  d2 = d1 - σ*√T
```

### Implied Volatility
IV is extracted using Newton-Raphson iteration:
```
σ_{n+1} = σ_n - (C_model(σ_n) - C_market) / vega(σ_n)
```

### RBF Interpolation
A thin-plate spline RBF interpolates IV across the (Strike, Maturity) grid to create a smooth surface.

## Requirements

- Python 3.8+
- numpy: Numerical computations
- pandas: Data manipulation
- scipy: Scientific computing (norm CDF, RBF interpolation)
- yfinance: Market data fetching
- matplotlib: Static plotting
- plotly: Interactive 3D plotting

## Notes

- Data is filtered for liquidity (positive bid/ask spreads, non-zero volume)
- Implied volatility is clipped to [0.01, 2.0] to avoid numerical artifacts
- The project uses SPY (S&P 500 ETF) by default due to high liquidity
- Longer maturities have fewer data points, leading to RBF extrapolation

## License

Open source - feel free to use and modify.
