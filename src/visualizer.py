import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from scipy.interpolate import RBFInterpolator


def build_and_plot_volatility_surface(df):
    print("Interpolating data arrays onto dense mesh grid...")

    if df.empty or df["strike"].empty or df["T"].empty or df["IV"].empty:
        print("Error: DataFrame or required columns are empty. Cannot plot volatility surface.")
        return None

    strikes = df["strike"].values
    maturities = df["T"].values
    ivs = df["IV"].values

    if len(strikes) == 0 or len(maturities) == 0 or len(ivs) == 0:
        print("Error: No data points available for plotting.")
        return None

    X_scatter = np.column_stack((strikes, maturities))

    # Create uniform evaluation grid
    strike_grid = np.linspace(strikes.min(), strikes.max(), 100)
    maturity_grid = np.linspace(maturities.min(), maturities.max(), 100)
    Strike_Mesh, Maturity_Mesh = np.meshgrid(strike_grid, maturity_grid)

    X_grid = np.column_stack((Strike_Mesh.ravel(), Maturity_Mesh.ravel()))

    # Apply Radial Basis Function interpolation with thin plate splines (Step 5)
    rbf = RBFInterpolator(X_scatter, ivs, kernel="thin_plate_spline", epsilon=1.0)
    IV_grid_flat = rbf(X_grid)
    IV_Surface = IV_grid_flat.reshape(Strike_Mesh.shape)

    # Bound extreme mathematical extrapolation edges
    IV_Surface = np.clip(IV_Surface, 0.01, 2.0)

    print("Rendering 3D viewport canvas...")
    fig = go.Figure()

    # Add smooth interpolated mesh
    fig.add_trace(
        go.Surface(
            x=Strike_Mesh,
            y=Maturity_Mesh,
            z=IV_Surface,
            colorscale="Viridis",
            colorbar_title="Implied Vol (σ)",
            name="Smoothed Surface",
        )
    )

    # Overlay actual market data markers
    fig.add_trace(
        go.Scatter3d(
            x=strikes,
            y=maturities,
            z=ivs,
            mode="markers",
            marker=dict(size=2.5, color="red", opacity=0.7),
            name="Market Data Points",
        )
    )

    fig.update_layout(
        title="Real-Time 3D Implied Volatility Surface",
        scene=dict(
            xaxis_title="Strike Price ($)",
            yaxis_title="Time to Maturity (Years)",
            zaxis_title="Implied Volatility (IV)",
        ),
        margin=dict(l=0, r=0, b=0, t=40),
        width=900,
        height=700,
    )

    # Export an interactive HTML copy for your GitHub Portfolio link
    fig.write_html("volatility_surface.html")
    print("✓ Interactive file successfully saved as 'volatility_surface.html'")
    fig.show()

    # Return the fitted interpolator object to extract 2D cross sections
    return rbf


def plot_volatility_slices(df, rbf_interpolator):
    """Extracts and plots the 2D Volatility Smile."""
    print("Extracting 2D analytical curve slices...")
    strikes = df["strike"].values
    maturities = df["T"].values
    current_S = df["S"].iloc[0]

    fig, ax = plt.subplots(figsize=(10, 6))

    # VOLATILITY SMILE (Slice at a fixed maturity)
    # Target maturity close to 3 months (0.25 years)
    target_T = maturities[np.abs(maturities - 0.25).argmin()]
    smile_strikes = np.linspace(strikes.min(), strikes.max(), 200)
    smile_maturities = np.full(shape=smile_strikes.shape, fill_value=target_T)
    smile_coords = np.column_stack((smile_strikes, smile_maturities))

    predicted_smile_ivs = rbf_interpolator(smile_coords)

    ax.plot(
        smile_strikes,
        predicted_smile_ivs * 100,
        color="dodgerblue",
        lw=2.5,
        label=f"Maturity: {target_T:.2f} Yrs",
    )
    ax.axvline(
        x=current_S,
        color="red",
        linestyle="--",
        label=f"Spot Price (${current_S:.2f})",
    )
    ax.set_title("Volatility Smile / Skew Cross-Section", fontsize=11, fontweight="bold")
    ax.set_xlabel("Strike Price ($)")
    ax.set_ylabel("Implied Volatility (%)")
    ax.grid(True, alpha=0.3)
    ax.legend()

    plt.tight_layout()
    plt.savefig("volatility_curves.png", dpi=300)
    print("✓ Static 2D plots successfully saved as 'volatility_curves.png'")
    plt.show()


def plot_volatility_verification(df, custom_rbf_model):
    """Fits an independent RBF model to Yahoo Finance's built-in IV column

    and plots it alongside your custom model for verification.
    """
    print("Generating cross-sectional verification plots...")
    strikes = df["strike"].values
    maturities = df["T"].values
    current_S = df["S"].iloc[0]

    # 1. Fit an independent RBF model to Yahoo's pre-calculated data
    X_scatter = np.column_stack((strikes, maturities))
    yahoo_ivs = df["yahoo_IV"].values
    
    yahoo_rbf_model = RBFInterpolator(X_scatter, yahoo_ivs, kernel="thin_plate_spline", epsilon=1.0)

    # 2. Initialize dual axes plotting grid
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5.5))

    # ---------------------------------------------------------
    # VERIFICATION 1: THE VOLATILITY SMILE (Slice at T ~ 3 Months)
    # ---------------------------------------------------------
    target_T = maturities[np.abs(maturities - 0.25).argmin()]
    smile_strikes = np.linspace(strikes.min(), strikes.max(), 200)
    smile_maturities = np.full(shape=smile_strikes.shape, fill_value=target_T)
    smile_coords = np.column_stack((smile_strikes, smile_maturities))

    # Predict both models across the strike line
    custom_smile = custom_rbf_model(smile_coords) * 100
    yahoo_smile = yahoo_rbf_model(smile_coords) * 100

    # Plot Comparison Curves
    ax1.plot(smile_strikes, custom_smile, color="dodgerblue", lw=2.5, label="Custom Solver IV")
    ax1.plot(smile_strikes, yahoo_smile, color="orange", lw=2, linestyle="--", label="Yahoo Built-in IV")
    ax1.axvline(x=current_S, color="red", linestyle=":", label=f"Spot Price (${current_S:.2f})")
    
    ax1.set_title(f"Volatility Smile Verification (Maturity: {target_T:.2f} Yrs)", fontsize=11, fontweight="bold")
    ax1.set_xlabel("Strike Price ($)")
    ax1.set_ylabel("Implied Volatility (%)")
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    # ---------------------------------------------------------
    # VERIFICATION 2: THE TERM STRUCTURE (Slice at At-the-Money Strike)
    # ---------------------------------------------------------
    target_K = strikes[np.abs(strikes - current_S).argmin()]
    term_maturities = np.linspace(maturities.min(), maturities.max(), 200)
    term_strikes = np.full(shape=term_maturities.shape, fill_value=target_K)
    term_coords = np.column_stack((term_strikes, term_maturities))

    # Predict both models across the time horizon
    custom_term = custom_rbf_model(term_coords) * 100
    yahoo_term = yahoo_rbf_model(term_coords) * 100

    # Plot Comparison Curves
    ax2.plot(term_maturities, custom_term, color="darkorchid", lw=2.5, label="Custom Solver IV")
    ax2.plot(term_maturities, yahoo_term, color="limegreen", lw=2, linestyle="--", label="Yahoo Built-in IV")
    
    ax2.set_title(f"Term Structure Verification (ATM Strike: ${target_K:.2f})", fontsize=11, fontweight="bold")
    ax2.set_xlabel("Time to Maturity (Years)")
    ax2.set_ylabel("Implied Volatility (%)")
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    plt.tight_layout()
    plt.savefig("verification_output.png", dpi=300)
    print("✓ Verification charts successfully saved to 'verification_output.png'")
    plt.show()