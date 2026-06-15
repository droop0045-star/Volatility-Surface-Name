# src/bs_engine.py
import numpy as np
import scipy.stats as si


def black_scholes_call(S, K, T, r, sigma, q=0.013):
    """Calculates the theoretical Black-Scholes-Merton price for a European Call

    accounting for continuous dividend yield (q).
    """
    if T <= 0 or sigma <= 0:
        return max(S * np.exp(-q * T) - K * np.exp(-r * T), 0.0)

    # Note the (r - q) term here
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    call_price = S * np.exp(-q * T) * si.norm.cdf(d1) - K * np.exp(-r * T) * si.norm.cdf(d2)
    return call_price


def black_scholes_vega(S, K, T, r, sigma, q=0.013):
    """Calculates the option's sensitivity to volatility (Vega) with dividends."""
    if T <= 0 or sigma <= 0:
        return 0.0

    d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    vega = S * np.exp(-q * T) * np.sqrt(T) * si.norm.pdf(d1)
    return vega


def find_implied_volatility(
    market_price, S, K, T, r=0.040, q=0.013, max_iter=100, precision=1e-5
):
    """Backs out Implied Volatility using Newton-Raphson root-finding with dividend logic."""
    sigma = 0.22  # Shifted starting guess slightly closer to baseline index vol

    for _ in range(max_iter):
        price = black_scholes_call(S, K, T, r, sigma, q)
        vega = black_scholes_vega(S, K, T, r, sigma, q)

        if abs(vega) < 1e-4:
            break

        diff = price - market_price

        if abs(diff) < precision:
            return sigma

        sigma = sigma - diff / vega

        if sigma <= 0:
            sigma = 0.001

    return np.nan