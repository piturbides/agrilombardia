import os

import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import spearmanr


# ============================================================
# GLOBAL SETTINGS
# ============================================================

COMMON_YEARS = [2016, 2017, 2018, 2019, 2023]

MONTH_ORDER = list(range(1, 13))
AREA_ORDER = ["Industrial", "Agricultural"]

OUTPUT_DIR = "Dati/output/3-Environmental health integration/3.2-Monthly integration"

# Health monthly rates produced in Part 2.2
HEALTH_MONTHLY_INPUT_PATH = (
    "Dati/output/2-Health data/2.2-Health event aggregation/"
    "monthly_health_events_rates_by_area.csv"
)

# Monthly pollutant indicators produced in Part 1.3 and Part 1.4
NO2_MONTHLY_INPUT_PATH = (
    "Dati/output/1-Statistical tests/1.3-NO2_definitivo/"
    "monthly_NO2_non_covid_dataset.csv"
)

PM25_MONTHLY_INPUT_PATH = (
    "Dati/output/1-Statistical tests/1.4-PM25_definitivo/"
    "monthly_PM25_non_covid_dataset.csv"
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
    "NO2_mean": "Monthly mean NO2",
    "PM25_mean": "Monthly mean PM2.5",
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


def assign_season(month):
    """
    Assign meteorological season from month number.

    This is useful for optional interpretation and for checking whether
    monthly associations are mainly driven by broad seasonal patterns.
    """

    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    else:
        return "Autumn"


def prepare_month_columns(df):
    """
    Standardize MonthPeriod, Year and Month columns.

    The function accepts two possible input formats:

    1. MonthPeriod already present
    2. Year and Month already present

    Output:
    MonthPeriod is converted to the first day of the month.
    Year and Month are numeric.
    Only common years are retained.
    """

    df = df.copy()

    if "MonthPeriod" in df.columns:
        df["MonthPeriod"] = pd.to_datetime(
            df["MonthPeriod"],
            errors="coerce"
        )

        df["MonthPeriod"] = (
            df["MonthPeriod"]
            .dt.to_period("M")
            .dt.to_timestamp()
        )

        df["Year"] = df["MonthPeriod"].dt.year
        df["Month"] = df["MonthPeriod"].dt.month

    elif "Year" in df.columns and "Month" in df.columns:
        df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
        df["Month"] = pd.to_numeric(df["Month"], errors="coerce")

        df["MonthPeriod"] = pd.to_datetime(
            df["Year"].astype("Int64").astype(str)
            + "-"
            + df["Month"].astype("Int64").astype(str).str.zfill(2)
            + "-01",
            errors="coerce"
        )

    else:
        raise ValueError(
            "Monthly dataframe must contain either MonthPeriod "
            "or both Year and Month columns."
        )

    df = df[df["Year"].isin(COMMON_YEARS)].copy()

    df["Month"] = pd.Categorical(
        df["Month"],
        categories=MONTH_ORDER,
        ordered=True
    )

    df["Season"] = df["Month"].astype(int).apply(assign_season)

    return df


def make_time_label(df):
    """
    Create a readable time label for plots.
    """

    return df["MonthPeriod"].dt.strftime("%Y-%m")


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


def add_monthly_gaps_for_plot(data, date_column, value_columns, max_gap_days=45):
    """
    Add NaN rows after large temporal gaps.

    This prevents line plots from artificially connecting 2019 and 2023.
    """

    data = data.sort_values(date_column).copy()

    rows = []
    previous_date = None

    for _, row in data.iterrows():
        current_date = row[date_column]

        if previous_date is not None:
            gap_days = (current_date - previous_date).days

            if gap_days > max_gap_days:
                gap_row = row.copy()
                gap_row[date_column] = previous_date + pd.Timedelta(days=31)

                for col in value_columns:
                    gap_row[col] = float("nan")

                rows.append(gap_row)

        rows.append(row)
        previous_date = current_date

    return pd.DataFrame(rows)


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

def load_monthly_health_rates():
    """
    Load monthly health rates produced in Part 2.2.

    Input format:
    MonthPeriod | Year | Month | Area | Outcome | N_events | Population | Rate_per_10000

    Output format:
    MonthPeriod | Year | Month | Season | Area | Population |
    Respiratory_rate_per_10000 | Cardiocirculatory_rate_per_10000
    """

    health = read_project_csv(HEALTH_MONTHLY_INPUT_PATH)

    required_columns = [
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
            f"Missing columns in health monthly file: {missing_columns}\n"
            f"Available columns: {health.columns.tolist()}"
        )

    health = prepare_month_columns(health)

    health["Area"] = health["Area"].apply(clean_text)
    health["Outcome"] = health["Outcome"].apply(clean_text)

    health["Population"] = pd.to_numeric(
        health["Population"],
        errors="coerce"
    )

    health["Rate_per_10000"] = pd.to_numeric(
        health["Rate_per_10000"],
        errors="coerce"
    )

    # Convert outcome rows into separate columns.
    health_wide = health.pivot_table(
        index=["MonthPeriod", "Year", "Month", "Season", "Area", "Population"],
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
        ["MonthPeriod", "Area"]
    )

    return health_wide


# ============================================================
# POLLUTION DATA
# ============================================================

def load_monthly_pollutant(path, pollutant_column, station_area_map):
    """
    Load monthly pollutant data and map monitoring stations to study areas.

    Input format from Part 1.3 / 1.4:
    MonthPeriod | Station | NO2 or PM25

    Output format:
    MonthPeriod | Year | Month | Area | NO2_mean or PM25_mean
    """

    pollutant = read_project_csv(path)

    required_columns = [
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

    pollutant = prepare_month_columns(pollutant)

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
        ["MonthPeriod", "Year", "Month", "Area", f"{pollutant_column}_mean"]
    ].copy()

    pollutant = pollutant.sort_values(
        ["MonthPeriod", "Area"]
    )

    return pollutant


# ============================================================
# INTEGRATED DATASET
# ============================================================

def build_monthly_integrated_dataset():
    """
    Build the monthly environmental-health integrated dataset.

    Each row represents:
    MonthPeriod × Area
    """

    health = load_monthly_health_rates()

    no2 = load_monthly_pollutant(
        path=NO2_MONTHLY_INPUT_PATH,
        pollutant_column="NO2",
        station_area_map=NO2_STATION_AREA_MAP
    )

    pm25 = load_monthly_pollutant(
        path=PM25_MONTHLY_INPUT_PATH,
        pollutant_column="PM25",
        station_area_map=PM25_STATION_AREA_MAP
    )

    integrated = health.merge(
        no2[["MonthPeriod", "Area", "NO2_mean"]],
        on=["MonthPeriod", "Area"],
        how="left"
    )

    integrated = integrated.merge(
        pm25[["MonthPeriod", "Area", "PM25_mean"]],
        on=["MonthPeriod", "Area"],
        how="left"
    )

    integrated["TimeLabel"] = make_time_label(integrated)

    integrated = integrated.sort_values(
        ["MonthPeriod", "Area"]
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
    - within-area monthly temporal variation;
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


def plot_standardized_monthly_time_series(integrated, pollutant_col, outcome_col):
    """
    Plot standardized monthly trends for one pollutant and one health outcome.

    Standardization is performed within each area:
    z = (value - mean) / standard deviation

    This allows visual comparison between variables with different units.
    """

    pollutant_label = get_variable_label(pollutant_col)
    outcome_label = get_variable_label(outcome_col)

    for area in AREA_ORDER:
        subset = integrated[integrated["Area"] == area].copy()
        subset = subset.sort_values("MonthPeriod")

        plot_df = subset[
            ["MonthPeriod", "TimeLabel", pollutant_col, outcome_col]
        ].copy()

        for col in [pollutant_col, outcome_col]:
            mean_value = plot_df[col].mean()
            std_value = plot_df[col].std()

            if pd.isna(std_value) or std_value == 0:
                plot_df[f"{col}_z"] = 0
            else:
                plot_df[f"{col}_z"] = (
                    (plot_df[col] - mean_value) / std_value
                )

        plot_df = add_monthly_gaps_for_plot(
            data=plot_df,
            date_column="MonthPeriod",
            value_columns=[
                f"{pollutant_col}_z",
                f"{outcome_col}_z"
            ],
            max_gap_days=45
        )

        plt.figure(figsize=(12, 5))

        plt.plot(
            plot_df["MonthPeriod"],
            plot_df[f"{pollutant_col}_z"],
            marker="o",
            label=pollutant_label
        )

        plt.plot(
            plot_df["MonthPeriod"],
            plot_df[f"{outcome_col}_z"],
            marker="o",
            label=outcome_label
        )

        plt.title(
            f"Standardized monthly trends - {area}: "
            f"{pollutant_label} vs {outcome_label}"
        )
        plt.xlabel("Month")
        plt.ylabel("Standardized value")
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()

        filename = (
            f"standardized_monthly_trend_{safe_filename(area)}_"
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


def compute_spearman_correlations_by_season(integrated):
    """
    Optional sensitivity analysis.

    Compute Spearman correlations by meteorological season.

    This helps check whether monthly correlations are mainly driven by
    the broad annual seasonal cycle.

    Results should be interpreted very cautiously because each season
    has fewer observations.
    """

    pollutant_columns = ["NO2_mean", "PM25_mean"]

    outcome_columns = [
        "Respiratory_rate_per_10000",
        "Cardiocirculatory_rate_per_10000",
    ]

    rows = []

    groups = ["Overall"] + AREA_ORDER

    for season in ["Winter", "Spring", "Summer", "Autumn"]:
        season_df = integrated[integrated["Season"] == season].copy()

        for group in groups:
            if group == "Overall":
                subset = season_df.copy()
            else:
                subset = season_df[season_df["Area"] == group].copy()

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
                        "Season": season,
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
            "Monthly",
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

def run_monthly_environment_health_integration():
    """
    Run Part 3.2: monthly environmental-health integration.

    The analysis:
    - loads monthly health rates from Part 2.2;
    - loads monthly NO2 indicators from Part 1.3;
    - loads monthly PM2.5 indicators from Part 1.4;
    - maps pollutant stations to study areas;
    - builds a monthly integrated dataset;
    - produces combined-area scatter plots;
    - produces area-specific scatter plots;
    - produces standardized monthly time-series plots;
    - computes Spearman correlations;
    - computes season-stratified Spearman correlations as sensitivity check.
    """

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("\n========================================")
    print("MONTHLY ENVIRONMENTAL-HEALTH INTEGRATION")
    print("========================================")

    # ------------------------------------------------------------
    # 1. Build integrated dataset
    # ------------------------------------------------------------

    integrated = build_monthly_integrated_dataset()

    integrated_output_path = os.path.join(
        OUTPUT_DIR,
        "monthly_environment_health_integrated_dataset.csv"
    )

    integrated.to_csv(
        integrated_output_path,
        index=False,
        sep=";"
    )

    print("\nIntegrated monthly dataset:")
    print(integrated.head(30))

    print("\nIntegrated dataset shape:")
    print(integrated.shape)

    print("\nRows by area:")
    print(integrated["Area"].value_counts())

    print("\nYears included:")
    print(sorted(integrated["Year"].dropna().unique()))

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
    # 3. Standardized monthly trend plots
    # ------------------------------------------------------------

    for pollutant_col in pollutant_columns:
        for outcome_col in outcome_columns:
            plot_standardized_monthly_time_series(
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
    # 5. Season-stratified Spearman correlations
    # ------------------------------------------------------------

    seasonal_correlation_summary = compute_spearman_correlations_by_season(
        integrated
    )

    seasonal_correlation_summary.to_csv(
        os.path.join(OUTPUT_DIR, "spearman_correlation_summary_by_season.csv"),
        index=False,
        sep=";"
    )

    print("\nSeason-stratified Spearman correlation summary:")
    print(seasonal_correlation_summary)

    # ------------------------------------------------------------
    # 6. Summary output
    # ------------------------------------------------------------

    summary = summarize_integrated_dataset(integrated)

    summary.to_csv(
        os.path.join(OUTPUT_DIR, "monthly_integration_summary.csv"),
        index=False,
        sep=";"
    )

    print("\n========================================")
    print("MONTHLY ENVIRONMENTAL-HEALTH INTEGRATION COMPLETED")
    print("========================================")
    print(f"Results saved in: {OUTPUT_DIR}")


if __name__ == "__main__":
    run_monthly_environment_health_integration()