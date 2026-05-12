import os

import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import spearmanr


# ============================================================
# GLOBAL SETTINGS
# ============================================================

COMMON_YEARS = [2016, 2017, 2018, 2019, 2023]

SEASON_ORDER = ["Winter", "Spring", "Summer", "Autumn"]
AREA_ORDER = ["Industrial", "Agricultural"]

OUTPUT_DIR = "Dati/output/3-Environmental health integration/3.1-Seasonal integration"

# Health seasonal rates produced in Part 2.2
HEALTH_SEASONAL_INPUT_PATH = (
    "Dati/output/2-Health data/2.2-Health event aggregation/"
    "seasonal_health_events_rates_by_area.csv"
)

# Seasonal pollutant indicators produced in Part 1.3 and Part 1.4
NO2_SEASONAL_INPUT_PATH = (
    "Dati/output/1-Statistical tests/1.3-NO2_definitivo/"
    "seasonal_NO2_non_covid_dataset.csv"
)

PM25_SEASONAL_INPUT_PATH = (
    "Dati/output/1-Statistical tests/1.4-PM25_definitivo/"
    "seasonal_PM25_non_covid_dataset.csv"
)

# Station-to-area mapping.
# These stations are used as environmental exposure proxies.
NO2_STATION_AREA_MAP = {
    "Soresina": "Agricultural",
    "Rezzato": "Industrial",
}

PM25_STATION_AREA_MAP = {
    "Soresina": "Agricultural",
    "Brescia Villaggio Sereno": "Industrial",
}

# More readable labels for plots and summary tables.
VARIABLE_LABELS = {
    "NO2_mean": "Seasonal mean NO2",
    "PM25_mean": "Seasonal mean PM2.5",
    "Respiratory_rate_per_10000": "Respiratory acute event rate",
    "Cardiocirculatory_rate_per_10000": "Cardiocirculatory acute event rate",
}

VARIABLE_UNITS = {
    "NO2_mean": "Mean NO2 concentration",
    "PM25_mean": "Mean PM2.5 concentration",
    "Respiratory_rate_per_10000": "Events per 10,000 inhabitants",
    "Cardiocirculatory_rate_per_10000": "Events per 10,000 inhabitants",
}


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def read_project_csv(path):
    """
    Read a project CSV file.

    Most outputs in this project are saved using semicolon separators.
    This function also tries comma separation as fallback.
    """

    if not os.path.exists(path):
        raise FileNotFoundError(f"Input file not found: {path}")

    for sep in [";", ","]:
        df = pd.read_csv(path, sep=sep)

        if len(df.columns) > 1:
            df.columns = [str(col).strip() for col in df.columns]
            return df

    raise ValueError(f"Could not read file correctly: {path}")


def clean_text(value):
    """
    Standardize text values for safer matching.
    """

    if pd.isna(value):
        return None

    return str(value).strip()


def prepare_season_columns(df):
    """
    Standardize SeasonYear and Season columns.

    Season is converted to an ordered categorical variable so that
    sorting follows the meteorological order:
    Winter, Spring, Summer, Autumn.
    """

    df = df.copy()

    df["SeasonYear"] = pd.to_numeric(df["SeasonYear"], errors="coerce")

    df["Season"] = pd.Categorical(
        df["Season"],
        categories=SEASON_ORDER,
        ordered=True
    )

    df = df[df["SeasonYear"].isin(COMMON_YEARS)].copy()

    return df


def make_time_label(df):
    """
    Create a readable time label for plots.
    """

    return df["SeasonYear"].astype(str) + "-" + df["Season"].astype(str)


def get_variable_label(variable_name):
    """
    Return a readable label for a variable name.
    """

    return VARIABLE_LABELS.get(variable_name, variable_name)


def get_variable_unit(variable_name):
    """
    Return a readable axis label with units.
    """

    return VARIABLE_UNITS.get(variable_name, variable_name)


def safe_filename(text):
    """
    Create a safe filename from a text string.
    """

    return (
        str(text)
        .replace(" ", "_")
        .replace(".", "")
        .replace("/", "_")
        .replace("(", "")
        .replace(")", "")
        .replace(",", "")
        .replace(":", "")
    )


def interpret_spearman_result(rho, p_value):
    """
    Add a simple qualitative interpretation to Spearman results.

    This interpretation is descriptive and should not be treated as
    causal evidence.
    """

    if rho is None or pd.isna(rho):
        return "Not enough data"

    abs_rho = abs(rho)

    if abs_rho < 0.20:
        strength = "very weak"
    elif abs_rho < 0.40:
        strength = "weak"
    elif abs_rho < 0.60:
        strength = "moderate"
    elif abs_rho < 0.80:
        strength = "strong"
    else:
        strength = "very strong"

    direction = "positive" if rho > 0 else "negative"

    if p_value is None or pd.isna(p_value):
        significance = "statistical significance not available"
    elif p_value < 0.05:
        significance = "statistically significant at p < 0.05"
    else:
        significance = "not statistically significant"

    return f"{strength} {direction} association; {significance}"


# ============================================================
# HEALTH DATA
# ============================================================

def load_seasonal_health_rates():
    """
    Load seasonal health rates produced in Part 2.2.

    Input format:
    SeasonYear | Season | Area | Outcome | N_events | Population | Rate_per_10000

    Output format:
    SeasonYear | Season | Area | Population |
    Respiratory_rate_per_10000 | Cardiocirculatory_rate_per_10000
    """

    health = read_project_csv(HEALTH_SEASONAL_INPUT_PATH)

    required_columns = [
        "SeasonYear",
        "Season",
        "Area",
        "Outcome",
        "Population",
        "Rate_per_10000",
    ]

    missing_columns = [
        col for col in required_columns
        if col not in health.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns in health seasonal file: {missing_columns}\n"
            f"Available columns: {health.columns.tolist()}"
        )

    health = prepare_season_columns(health)

    # Convert outcome rows into separate columns.
    health_wide = health.pivot_table(
        index=["SeasonYear", "Season", "Area", "Population"],
        columns="Outcome",
        values="Rate_per_10000",
        aggfunc="first",
        observed=True
    ).reset_index()

    health_wide.columns.name = None

    health_wide = health_wide.rename(
        columns={
            "Respiratory": "Respiratory_rate_per_10000",
            "Cardiocirculatory": "Cardiocirculatory_rate_per_10000",
        }
    )

    health_wide = health_wide.sort_values(
        ["SeasonYear", "Season", "Area"]
    )

    return health_wide


# ============================================================
# POLLUTION DATA
# ============================================================

def load_seasonal_pollutant(path, pollutant_column, station_area_map):
    """
    Load seasonal pollutant data and map monitoring stations to study areas.

    Input format from Part 1.3 / 1.4:
    SeasonYear | Season | Station | NO2 or PM25

    Output format:
    SeasonYear | Season | Area | NO2_mean or PM25_mean
    """

    pollutant = read_project_csv(path)

    required_columns = [
        "SeasonYear",
        "Season",
        "Station",
        pollutant_column,
    ]

    missing_columns = [
        col for col in required_columns
        if col not in pollutant.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns in pollutant file: {missing_columns}\n"
            f"File: {path}\n"
            f"Available columns: {pollutant.columns.tolist()}"
        )

    pollutant = prepare_season_columns(pollutant)

    pollutant["Station"] = pollutant["Station"].apply(clean_text)

    pollutant["Area"] = pollutant["Station"].map(station_area_map)

    pollutant = pollutant[pollutant["Area"].notna()].copy()

    pollutant[pollutant_column] = pd.to_numeric(
        pollutant[pollutant_column],
        errors="coerce"
    )

    pollutant = pollutant.rename(
        columns={
            pollutant_column: f"{pollutant_column}_mean"
        }
    )

    pollutant = pollutant[
        ["SeasonYear", "Season", "Area", f"{pollutant_column}_mean"]
    ].copy()

    pollutant = pollutant.sort_values(
        ["SeasonYear", "Season", "Area"]
    )

    return pollutant


# ============================================================
# INTEGRATED DATASET
# ============================================================

def build_integrated_dataset():
    """
    Build the seasonal environmental-health integrated dataset.

    Each row represents:
    SeasonYear × Season × Area
    """

    health = load_seasonal_health_rates()

    no2 = load_seasonal_pollutant(
        path=NO2_SEASONAL_INPUT_PATH,
        pollutant_column="NO2",
        station_area_map=NO2_STATION_AREA_MAP
    )

    pm25 = load_seasonal_pollutant(
        path=PM25_SEASONAL_INPUT_PATH,
        pollutant_column="PM25",
        station_area_map=PM25_STATION_AREA_MAP
    )

    integrated = health.merge(
        no2,
        on=["SeasonYear", "Season", "Area"],
        how="left"
    )

    integrated = integrated.merge(
        pm25,
        on=["SeasonYear", "Season", "Area"],
        how="left"
    )

    integrated["TimeLabel"] = make_time_label(integrated)

    integrated = integrated.sort_values(
        ["SeasonYear", "Season", "Area"]
    )

    return integrated


# ============================================================
# PLOTTING FUNCTIONS
# ============================================================

def plot_scatter_by_area(integrated, pollutant_col, outcome_col):
    """
    Create a scatter plot between one pollutant and one health outcome.

    Points are separated by study area in the same plot.
    """

    plt.figure(figsize=(8, 5))

    for area in AREA_ORDER:
        subset = integrated[integrated["Area"] == area].copy()

        plt.scatter(
            subset[pollutant_col],
            subset[outcome_col],
            label=area,
            alpha=0.8
        )

    pollutant_label = get_variable_label(pollutant_col)
    outcome_label = get_variable_label(outcome_col)

    plt.title(f"{pollutant_label} vs {outcome_label}")
    plt.xlabel(get_variable_unit(pollutant_col))
    plt.ylabel(get_variable_unit(outcome_col))
    plt.grid(True, alpha=0.3)
    plt.legend(title="Study area")
    plt.tight_layout()

    filename = (
        f"scatter_combined_areas_"
        f"{safe_filename(pollutant_col)}_vs_{safe_filename(outcome_col)}.png"
    )

    plt.savefig(
        os.path.join(OUTPUT_DIR, filename),
        dpi=300
    )

    plt.show()


def plot_scatter_single_area(integrated, pollutant_col, outcome_col):
    """
    Create one scatter plot per study area.

    This helps distinguish whether the apparent association is driven by:
    - within-area temporal variation;
    - or by differences between areas.
    """

    pollutant_label = get_variable_label(pollutant_col)
    outcome_label = get_variable_label(outcome_col)

    for area in AREA_ORDER:
        subset = integrated[integrated["Area"] == area].copy()

        plt.figure(figsize=(7, 5))

        plt.scatter(
            subset[pollutant_col],
            subset[outcome_col],
            alpha=0.8
        )

        plt.title(f"{pollutant_label} vs {outcome_label} - {area}")
        plt.xlabel(get_variable_unit(pollutant_col))
        plt.ylabel(get_variable_unit(outcome_col))
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        filename = (
            f"scatter_{safe_filename(area)}_"
            f"{safe_filename(pollutant_col)}_vs_{safe_filename(outcome_col)}.png"
        )

        plt.savefig(
            os.path.join(OUTPUT_DIR, filename),
            dpi=300
        )

        plt.show()


def plot_standardized_time_series(integrated, pollutant_col, outcome_col):
    """
    Plot standardized seasonal trends for one pollutant and one health outcome.

    Standardization is performed within each area:
    z = (value - mean) / standard deviation

    This allows visual comparison between variables with different units.
    """

    pollutant_label = get_variable_label(pollutant_col)
    outcome_label = get_variable_label(outcome_col)

    for area in AREA_ORDER:
        subset = integrated[integrated["Area"] == area].copy()
        subset = subset.sort_values(["SeasonYear", "Season"])

        plot_df = subset[["TimeLabel", pollutant_col, outcome_col]].copy()

        for col in [pollutant_col, outcome_col]:
            mean_value = plot_df[col].mean()
            std_value = plot_df[col].std()

            if pd.isna(std_value) or std_value == 0:
                plot_df[f"{col}_z"] = 0
            else:
                plot_df[f"{col}_z"] = (
                    (plot_df[col] - mean_value) / std_value
                )

        plt.figure(figsize=(11, 5))

        plt.plot(
            plot_df["TimeLabel"],
            plot_df[f"{pollutant_col}_z"],
            marker="o",
            label=pollutant_label
        )

        plt.plot(
            plot_df["TimeLabel"],
            plot_df[f"{outcome_col}_z"],
            marker="o",
            label=outcome_label
        )

        plt.title(
            f"Standardized seasonal trends - {area}: "
            f"{pollutant_label} vs {outcome_label}"
        )
        plt.xlabel("Season")
        plt.ylabel("Standardized value")
        plt.xticks(rotation=90)
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()

        filename = (
            f"standardized_trend_{safe_filename(area)}_"
            f"{safe_filename(pollutant_col)}_vs_{safe_filename(outcome_col)}.png"
        )

        plt.savefig(
            os.path.join(OUTPUT_DIR, filename),
            dpi=300
        )

        plt.show()


# ============================================================
# CORRELATION ANALYSIS
# ============================================================

def compute_spearman_correlations(integrated):
    """
    Compute Spearman correlations between pollutant indicators and health rates.

    Correlations are computed:
    - overall, using both areas together;
    - separately for each study area.

    These correlations are exploratory and ecological.
    """

    pollutant_columns = ["NO2_mean", "PM25_mean"]

    outcome_columns = [
        "Respiratory_rate_per_10000",
        "Cardiocirculatory_rate_per_10000",
    ]

    rows = []

    groups = ["Overall"] + AREA_ORDER

    for group in groups:
        if group == "Overall":
            subset = integrated.copy()
        else:
            subset = integrated[integrated["Area"] == group].copy()

        for pollutant_col in pollutant_columns:
            for outcome_col in outcome_columns:
                temp = subset[
                    [pollutant_col, outcome_col]
                ].dropna()

                n = len(temp)

                if n < 3:
                    rho = None
                    p_value = None
                else:
                    rho, p_value = spearmanr(
                        temp[pollutant_col],
                        temp[outcome_col]
                    )

                rows.append({
                    "Group": group,
                    "Pollutant": pollutant_col,
                    "Pollutant_label": get_variable_label(pollutant_col),
                    "Outcome": outcome_col,
                    "Outcome_label": get_variable_label(outcome_col),
                    "N": n,
                    "Spearman_rho": rho,
                    "p_value": p_value,
                    "Interpretation": interpret_spearman_result(rho, p_value),
                })

    return pd.DataFrame(rows)


# ============================================================
# SUMMARY TABLES
# ============================================================

def summarize_integrated_dataset(integrated):
    """
    Create a compact descriptive summary of the integrated dataset.
    """

    summary = pd.DataFrame({
        "Indicator": [
            "Common years used",
            "Temporal scale",
            "Number of rows",
            "Number of areas",
            "Areas",
            "Pollutants",
            "Health outcomes",
            "Main exposure limitation",
            "Main interpretation rule"
        ],
        "Value": [
            ", ".join(map(str, COMMON_YEARS)),
            "Seasonal",
            len(integrated),
            integrated["Area"].nunique(),
            ", ".join(AREA_ORDER),
            "NO2, PM2.5",
            "Respiratory and cardiocirculatory event rates",
            (
                "Pollutant concentrations are represented by monitoring-station "
                "proxies and not by exact area-level exposure estimates."
            ),
            (
                "Results must be interpreted as exploratory ecological patterns, "
                "not as individual-level causal evidence."
            )
        ]
    })

    return summary


# ============================================================
# MAIN FUNCTION
# ============================================================

def run_environment_health_integration():
    """
    Run Part 3.1: seasonal environmental-health integration.

    The analysis:
    - loads seasonal health rates from Part 2.2;
    - loads seasonal NO2 indicators from Part 1.3;
    - loads seasonal PM2.5 indicators from Part 1.4;
    - maps pollutant stations to study areas;
    - builds a seasonal integrated dataset;
    - produces combined-area scatter plots;
    - produces area-specific scatter plots;
    - produces standardized time-series plots;
    - computes Spearman correlations.
    """

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("\n========================================")
    print("SEASONAL ENVIRONMENTAL-HEALTH INTEGRATION")
    print("========================================")

    # ------------------------------------------------------------
    # 1. Build integrated dataset
    # ------------------------------------------------------------

    integrated = build_integrated_dataset()

    integrated_output_path = os.path.join(
        OUTPUT_DIR,
        "seasonal_environment_health_integrated_dataset.csv"
    )

    integrated.to_csv(
        integrated_output_path,
        index=False,
        sep=";"
    )

    print("\nIntegrated seasonal dataset:")
    print(integrated.head(20))

    print("\nIntegrated dataset shape:")
    print(integrated.shape)

    print("\nMissing values check:")
    print(integrated.isna().sum())

    missing_values_summary = (
        integrated
        .isna()
        .sum()
        .reset_index()
    )

    missing_values_summary.columns = ["Column", "Missing_values"]

    missing_values_summary.to_csv(
        os.path.join(OUTPUT_DIR, "missing_values_check.csv"),
        index=False,
        sep=";"
    )

    # ------------------------------------------------------------
    # 2. Scatter plots
    # ------------------------------------------------------------

    pollutant_columns = ["NO2_mean", "PM25_mean"]

    outcome_columns = [
        "Respiratory_rate_per_10000",
        "Cardiocirculatory_rate_per_10000",
    ]

    for pollutant_col in pollutant_columns:
        for outcome_col in outcome_columns:
            # Combined scatter plot with both areas.
            plot_scatter_by_area(
                integrated=integrated,
                pollutant_col=pollutant_col,
                outcome_col=outcome_col
            )

            # Area-specific scatter plots.
            plot_scatter_single_area(
                integrated=integrated,
                pollutant_col=pollutant_col,
                outcome_col=outcome_col
            )

    # ------------------------------------------------------------
    # 3. Standardized seasonal trend plots
    # ------------------------------------------------------------

    # Standardized trend plots for both pollutants.
    # PM2.5 is especially relevant, but NO2 is also useful as a
    # combustion-related comparison marker.
    for pollutant_col in pollutant_columns:
        for outcome_col in outcome_columns:
            plot_standardized_time_series(
                integrated=integrated,
                pollutant_col=pollutant_col,
                outcome_col=outcome_col
            )

    # ------------------------------------------------------------
    # 4. Spearman correlations
    # ------------------------------------------------------------

    correlation_summary = compute_spearman_correlations(integrated)

    correlation_summary.to_csv(
        os.path.join(OUTPUT_DIR, "spearman_correlation_summary.csv"),
        index=False,
        sep=";"
    )

    print("\nSpearman correlation summary:")
    print(correlation_summary)

    # ------------------------------------------------------------
    # 5. Summary output
    # ------------------------------------------------------------

    summary = summarize_integrated_dataset(integrated)

    summary.to_csv(
        os.path.join(OUTPUT_DIR, "seasonal_integration_summary.csv"),
        index=False,
        sep=";"
    )

    print("\n========================================")
    print("SEASONAL ENVIRONMENTAL-HEALTH INTEGRATION COMPLETED")
    print("========================================")
    print(f"Results saved in: {OUTPUT_DIR}")


if __name__ == "__main__":
    run_environment_health_integration()