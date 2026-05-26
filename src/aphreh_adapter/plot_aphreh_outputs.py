"""
Generate plots from APHREH-ADSMap summarized outputs.

This script does NOT rerun APHREH.
It reads:
    aphreh_pilot_parameter_sweep_summary.csv

and generates:
    - WMARM heatmap
    - MARM heatmap
    - WMARM ranking plot
    - WMARM 3D surface plot

Pilot:
    PM2.5 -> Respiratory acute events
"""

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401


# =============================================================================
# Configuration
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PILOT_LABEL = "PM25_Respiratory"

SUMMARY_DIR = (
    PROJECT_ROOT
    / "Dati/output/6-APHREH ADSMap/6.3-Output summaries"
    / PILOT_LABEL
)

PARAMETER_SWEEP_PATH = SUMMARY_DIR / "aphreh_pilot_parameter_sweep_summary.csv"

PLOT_DIR = SUMMARY_DIR / "plots"


# =============================================================================
# Plot helpers
# =============================================================================

def build_pivot(df: pd.DataFrame, value_column: str) -> pd.DataFrame:
    """
    Build pivot table:
        rows = exposure percentiles
        columns = lag days
        values = selected metric
    """
    pivot = (
        df.pivot(
            index="Exposure_percentile",
            columns="Lag_days",
            values=value_column,
        )
        .sort_index()
        .sort_index(axis=1)
    )
    return pivot


def save_heatmap(
    df: pd.DataFrame,
    value_column: str,
    output_filename: str,
    title: str,
) -> None:
    """
    Save a heatmap with:
        rows = exposure percentiles
        columns = lag days
        values = MARM or WMARM
    """
    pivot = build_pivot(df, value_column)

    fig, ax = plt.subplots(figsize=(8, 4.8))

    image = ax.imshow(pivot.values, aspect="auto")

    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns)

    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)

    ax.set_xlabel("Lag [days]")
    ax.set_ylabel("Exposure percentile")
    ax.set_title(title)

    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            value = pivot.iloc[i, j]
            ax.text(j, i, f"{value:.2e}", ha="center", va="center", fontsize=8)

    fig.colorbar(image, ax=ax, label=value_column)

    fig.tight_layout()
    fig.savefig(PLOT_DIR / output_filename, dpi=300)
    plt.close(fig)


def save_wmarm_ranking_plot(df: pd.DataFrame) -> None:
    """
    Save a bar plot of parameter combinations ranked by WMARM.
    """
    ranking = df.sort_values("WMARM", ascending=True).copy()
    ranking["Label"] = ranking["Parameter_folder"]

    fig, ax = plt.subplots(figsize=(8, 5.5))

    ax.barh(ranking["Label"], ranking["WMARM"])

    ax.set_xlabel("WMARM")
    ax.set_ylabel("Parameter combination")
    ax.set_title("APHREH-ADSMap mini-sweep ranking by WMARM")

    for i, value in enumerate(ranking["WMARM"]):
        ax.text(value, i, f" {value:.2e}", va="center", fontsize=8)

    fig.tight_layout()
    fig.savefig(PLOT_DIR / "aphreh_wmarm_ranking.png", dpi=300)
    plt.close(fig)


def save_wmarm_surface_3d(df: pd.DataFrame) -> None:
    """
    Save a 3D surface plot of WMARM:
        X = lag days
        Y = exposure percentile
        Z = WMARM
    """
    pivot = build_pivot(df, "WMARM")

    x = pivot.columns.to_numpy(dtype=float)      # lag days
    y = pivot.index.to_numpy(dtype=float)        # exposure percentiles
    X, Y = np.meshgrid(x, y)
    Z = pivot.to_numpy(dtype=float)

    fig = plt.figure(figsize=(9, 6.5))
    ax = fig.add_subplot(111, projection="3d")

    surface = ax.plot_surface(X, Y, Z, cmap="viridis", edgecolor="black", linewidth=0.4)

    ax.set_xlabel("Lag [days]", labelpad=10)
    ax.set_ylabel("Exposure percentile", labelpad=10)
    ax.set_zlabel("WMARM", labelpad=10)
    ax.set_title("APHREH-ADSMap WMARM 3D surface | PM2.5 → Respiratory", pad=18)

    ax.set_xticks(x)
    ax.set_yticks(y)

    fig.colorbar(surface, ax=ax, shrink=0.7, pad=0.1, label="WMARM")

    fig.tight_layout()
    fig.savefig(PLOT_DIR / "aphreh_wmarm_surface_3d.png", dpi=300)
    plt.close(fig)


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    print("=" * 100)
    print("Generating APHREH-ADSMap plots from summarized outputs")
    print(f"Pilot: {PILOT_LABEL}")
    print("=" * 100)

    if not PARAMETER_SWEEP_PATH.exists():
        raise FileNotFoundError(
            f"Missing parameter sweep summary: {PARAMETER_SWEEP_PATH}\n"
            "Run summarize_aphreh_outputs.py first."
        )

    PLOT_DIR.mkdir(parents=True, exist_ok=True)

    sweep = pd.read_csv(PARAMETER_SWEEP_PATH, sep=";")

    required_columns = [
        "Parameter_folder",
        "Exposure_percentile",
        "Lag_days",
        "MARM",
        "WMARM",
    ]

    missing = [col for col in required_columns if col not in sweep.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    save_heatmap(
        df=sweep,
        value_column="WMARM",
        output_filename="aphreh_wmarm_heatmap.png",
        title="APHREH-ADSMap WMARM heatmap | PM2.5 → Respiratory",
    )

    save_heatmap(
        df=sweep,
        value_column="MARM",
        output_filename="aphreh_marm_heatmap.png",
        title="APHREH-ADSMap MARM heatmap | PM2.5 → Respiratory",
    )

    save_wmarm_ranking_plot(sweep)
    save_wmarm_surface_3d(sweep)

    print("\nGenerated plots:")
    for path in sorted(PLOT_DIR.glob("*.png")):
        print(f"  - {path.relative_to(PROJECT_ROOT)}")

    print("\nDone.")


if __name__ == "__main__":
    main()