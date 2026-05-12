import os

import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import spearmanr


# ============================================================
# GLOBAL SETTINGS
# ============================================================

LAGS = [0, 1, 2, 3]

AREA_ORDER = ["Industrial", "Agricultural"]

INPUT_PATH = (
    "Dati/output/3-Environmental health integration/"
    "3.2-Monthly integration/"
    "monthly_environment_health_integrated_dataset.csv"
)

OUTPUT_DIR = (
    "Dati/output/3-Environmental health integration/"
    "3.3-Monthly lag analysis"
)

POLLUTANT_COLUMNS = ["NO2_mean", "PM25_mean"]

OUTCOME_COLUMNS = [
    "Respiratory_rate_per_10000",
    "Cardiocirculatory_rate_per_10000",
]

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


def month_index(date_series):
    """
    Convert datetime values to an integer month index.

    This allows exact month-distance calculations.

    Example:
    January 2016  -> 2016 * 12 + 1
    February 2016 -> 2016 * 12 + 2

    The difference between these values gives the number of months
    between two dates.
    """

    return date_series.dt.year * 12 + date_series.dt.month


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
# DATA LOADING
# ============================================================

def load_monthly_integrated_dataset():
    """
    Load the monthly integrated dataset produced in Part 3.2.

    Expected input:
    monthly_environment_health_integrated_dataset.csv

    Each row represents:
    MonthPeriod × Area
    """

    data = read_project_csv(INPUT_PATH)

    required_columns = [
        "MonthPeriod",
        "Year",
        "Month",
        "Season",
        "Area",
        "Population",
        "Respiratory_rate_per_10000",
        "Cardiocirculatory_rate_per_10000",
        "NO2_mean",
        "PM25_mean",
        "TimeLabel",
    ]

    missing_columns = [
        col for col in required_columns
        if col not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns in monthly integrated dataset: {missing_columns}\n"
            f"Available columns: {data.columns.tolist()}"
        )

    data["MonthPeriod"] = pd.to_datetime(
        data["MonthPeriod"],
        errors="coerce"
    )

    data["Year"] = pd.to_numeric(
        data["Year"],
        errors="coerce"
    )

    data["Month"] = pd.to_numeric(
        data["Month"],
        errors="coerce"
    )

    data["Area"] = data["Area"].apply(clean_text)

    for col in POLLUTANT_COLUMNS + OUTCOME_COLUMNS + ["Population"]:
        data[col] = pd.to_numeric(
            data[col],
            errors="coerce"
        )

    data = data.sort_values(["Area", "MonthPeriod"]).reset_index(drop=True)

    return data


# ============================================================
# LAG CONSTRUCTION
# ============================================================

def add_validated_lags_for_area(area_data):
    """
    Add lagged pollutant columns for one study area.

    Very important:
    lagged values are kept only if the lagged month is exactly
    lag months before the current month.

    This prevents wrong links across the 2019-2023 temporal gap.

    Example:
    current month = 2023-01
    shifted previous row = 2019-12
    month difference = 37 months

    For lag 1, expected difference = 1 month.
    Since 37 != 1, the lagged value is set to NaN.
    """

    area_data = area_data.sort_values("MonthPeriod").copy()

    current_month_index = month_index(area_data["MonthPeriod"])

    for lag in LAGS:
        for pollutant_col in POLLUTANT_COLUMNS:
            lag_col = f"{pollutant_col}_lag{lag}"
            lag_date_col = f"{pollutant_col}_lag{lag}_MonthPeriod"

            if lag == 0:
                area_data[lag_col] = area_data[pollutant_col]
                area_data[lag_date_col] = area_data["MonthPeriod"]

            else:
                area_data[lag_col] = area_data[pollutant_col].shift(lag)
                area_data[lag_date_col] = area_data["MonthPeriod"].shift(lag)

                lagged_month_index = month_index(area_data[lag_date_col])

                month_difference = current_month_index - lagged_month_index

                valid_lag = month_difference == lag

                area_data.loc[~valid_lag, lag_col] = pd.NA
                area_data.loc[~valid_lag, lag_date_col] = pd.NaT

    return area_data


def build_lagged_dataset(data):
    """
    Build the monthly lagged dataset.

    Lags are computed separately for each study area.
    """

    lagged_parts = []

    for area in AREA_ORDER:
        area_data = data[data["Area"] == area].copy()

        area_lagged = add_validated_lags_for_area(area_data)

        lagged_parts.append(area_lagged)

    lagged = pd.concat(lagged_parts, ignore_index=True)

    lagged = lagged.sort_values(["MonthPeriod", "Area"]).reset_index(drop=True)

    return lagged


def summarize_lag_availability(lagged):
    """
    Count available non-missing lagged values for each lag, pollutant and area.

    This is a quality-control table to verify that the temporal gap was handled correctly.
    """

    rows = []

    groups = ["Overall"] + AREA_ORDER

    for group in groups:
        if group == "Overall":
            subset = lagged.copy()
        else:
            subset = lagged[lagged["Area"] == group].copy()

        for pollutant_col in POLLUTANT_COLUMNS:
            for lag in LAGS:
                lag_col = f"{pollutant_col}_lag{lag}"

                rows.append({
                    "Group": group,
                    "Pollutant": pollutant_col,
                    "Lag_months": lag,
                    "Available_values": subset[lag_col].notna().sum(),
                    "Missing_values": subset[lag_col].isna().sum(),
                })

    return pd.DataFrame(rows)


# ============================================================
# CORRELATION ANALYSIS
# ============================================================

def compute_lagged_spearman_correlations(lagged):
    """
    Compute Spearman correlations between lagged pollutant indicators
    and current-month health event rates.

    For each combination:
    - group;
    - pollutant;
    - outcome;
    - lag.

    The health outcome always refers to the current month.
    The pollutant indicator refers to the same month or previous months,
    depending on lag.
    """

    rows = []

    groups = ["Overall"] + AREA_ORDER

    for group in groups:
        if group == "Overall":
            subset = lagged.copy()
        else:
            subset = lagged[lagged["Area"] == group].copy()

        for pollutant_col in POLLUTANT_COLUMNS:
            for outcome_col in OUTCOME_COLUMNS:
                for lag in LAGS:
                    lag_col = f"{pollutant_col}_lag{lag}"

                    temp = subset[
                        [lag_col, outcome_col]
                    ].dropna()

                    n = len(temp)

                    if n < 3:
                        rho = None
                        p_value = None
                    else:
                        rho, p_value = spearmanr(
                            temp[lag_col],
                            temp[outcome_col]
                        )

                    rows.append({
                        "Group": group,
                        "Pollutant": pollutant_col,
                        "Pollutant_label": get_variable_label(pollutant_col),
                        "Outcome": outcome_col,
                        "Outcome_label": get_variable_label(outcome_col),
                        "Lag_months": lag,
                        "N": n,
                        "Spearman_rho": rho,
                        "p_value": p_value,
                        "Interpretation": interpret_spearman_result(rho, p_value),
                    })

    return pd.DataFrame(rows)


def summarize_best_lags(correlation_summary):
    """
    Identify the lag with the strongest absolute Spearman correlation
    for each group, pollutant and outcome.

    This is only a descriptive summary.
    It does not imply that the selected lag is a causal delay.
    """

    rows = []

    grouping_columns = [
        "Group",
        "Pollutant",
        "Pollutant_label",
        "Outcome",
        "Outcome_label",
    ]

    for keys, subset in correlation_summary.groupby(grouping_columns):
        subset = subset.dropna(subset=["Spearman_rho"]).copy()

        if subset.empty:
            continue

        subset["abs_rho"] = subset["Spearman_rho"].abs()

        best_row = subset.sort_values(
            ["abs_rho", "Lag_months"],
            ascending=[False, True]
        ).iloc[0]

        rows.append({
            "Group": best_row["Group"],
            "Pollutant": best_row["Pollutant"],
            "Pollutant_label": best_row["Pollutant_label"],
            "Outcome": best_row["Outcome"],
            "Outcome_label": best_row["Outcome_label"],
            "Best_lag_months": best_row["Lag_months"],
            "Best_Spearman_rho": best_row["Spearman_rho"],
            "Best_p_value": best_row["p_value"],
            "N": best_row["N"],
            "Interpretation": best_row["Interpretation"],
            "Caution": (
                "Best lag is selected descriptively using the strongest absolute "
                "Spearman correlation. It should not be interpreted as a causal delay."
            ),
        })

    return pd.DataFrame(rows)


# ============================================================
# PLOTTING FUNCTIONS
# ============================================================

def plot_rho_vs_lag(correlation_summary):
    """
    Plot Spearman rho as a function of lag.

    One plot is produced for each:
    - group;
    - pollutant;
    - outcome.
    """

    for group in ["Overall"] + AREA_ORDER:
        for pollutant_col in POLLUTANT_COLUMNS:
            for outcome_col in OUTCOME_COLUMNS:
                subset = correlation_summary[
                    (correlation_summary["Group"] == group)
                    & (correlation_summary["Pollutant"] == pollutant_col)
                    & (correlation_summary["Outcome"] == outcome_col)
                ].copy()

                subset = subset.sort_values("Lag_months")

                pollutant_label = get_variable_label(pollutant_col)
                outcome_label = get_variable_label(outcome_col)

                plt.figure(figsize=(7, 5))

                plt.plot(
                    subset["Lag_months"],
                    subset["Spearman_rho"],
                    marker="o"
                )

                plt.axhline(
                    y=0,
                    linestyle="--",
                    linewidth=1
                )

                plt.xticks(LAGS)

                plt.title(
                    f"Spearman rho vs lag - {group}\n"
                    f"{pollutant_label} vs {outcome_label}"
                )

                plt.xlabel("Lag in months")
                plt.ylabel("Spearman rho")
                plt.grid(True, alpha=0.3)
                plt.tight_layout()

                filename = (
                    f"rho_vs_lag_{safe_filename(group)}_"
                    f"{safe_filename(pollutant_col)}_vs_"
                    f"{safe_filename(outcome_col)}.png"
                )

                plt.savefig(
                    os.path.join(OUTPUT_DIR, filename),
                    dpi=300
                )

                plt.show()


def plot_lagged_scatter_for_best_lags(lagged, best_lag_summary):
    """
    Create scatter plots only for the descriptively strongest lag
    of each group, pollutant and outcome.

    These plots are useful for interpreting the main lag summary
    without generating too many figures.
    """

    for _, row in best_lag_summary.iterrows():
        group = row["Group"]
        pollutant_col = row["Pollutant"]
        outcome_col = row["Outcome"]
        lag = int(row["Best_lag_months"])

        lag_col = f"{pollutant_col}_lag{lag}"

        if group == "Overall":
            subset = lagged.copy()
        else:
            subset = lagged[lagged["Area"] == group].copy()

        subset = subset[[lag_col, outcome_col, "Area"]].dropna().copy()

        if subset.empty:
            continue

        pollutant_label = get_variable_label(pollutant_col)
        outcome_label = get_variable_label(outcome_col)

        plt.figure(figsize=(7, 5))

        if group == "Overall":
            for area in AREA_ORDER:
                area_subset = subset[subset["Area"] == area].copy()

                plt.scatter(
                    area_subset[lag_col],
                    area_subset[outcome_col],
                    label=area,
                    alpha=0.8
                )

            plt.legend(title="Study area")

        else:
            plt.scatter(
                subset[lag_col],
                subset[outcome_col],
                alpha=0.8
            )

        plt.title(
            f"Best lag scatter - {group}\n"
            f"{pollutant_label} lag {lag} vs {outcome_label}"
        )

        plt.xlabel(f"{get_variable_unit(pollutant_col)} - lag {lag} month(s)")
        plt.ylabel(get_variable_unit(outcome_col))
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        filename = (
            f"best_lag_scatter_{safe_filename(group)}_"
            f"{safe_filename(pollutant_col)}_lag{lag}_vs_"
            f"{safe_filename(outcome_col)}.png"
        )

        plt.savefig(
            os.path.join(OUTPUT_DIR, filename),
            dpi=300
        )

        plt.show()


# ============================================================
# SUMMARY TABLE
# ============================================================

def summarize_lag_analysis(lagged, correlation_summary):
    """
    Create a compact descriptive summary of the monthly lag analysis.
    """

    summary = pd.DataFrame({
        "Indicator": [
            "Input dataset",
            "Temporal scale",
            "Lag values tested",
            "Number of rows in lagged dataset",
            "Number of areas",
            "Areas",
            "Pollutants",
            "Health outcomes",
            "Maximum N at lag 0",
            "Maximum N at lag 1",
            "Maximum N at lag 2",
            "Maximum N at lag 3",
            "Main methodological safeguard",
            "Main interpretation rule",
        ],
        "Value": [
            INPUT_PATH,
            "Monthly",
            ", ".join(map(str, LAGS)),
            len(lagged),
            lagged["Area"].nunique(),
            ", ".join(AREA_ORDER),
            "NO2, PM2.5",
            "Respiratory and cardiocirculatory event rates",
            int(correlation_summary[correlation_summary["Lag_months"] == 0]["N"].max()),
            int(correlation_summary[correlation_summary["Lag_months"] == 1]["N"].max()),
            int(correlation_summary[correlation_summary["Lag_months"] == 2]["N"].max()),
            int(correlation_summary[correlation_summary["Lag_months"] == 3]["N"].max()),
            (
                "Lagged pollutant values are kept only when the lagged month is "
                "exactly the expected number of months before the current health month. "
                "This prevents linking December 2019 to January 2023."
            ),
            (
                "Lagged correlations are exploratory ecological associations. "
                "They should not be interpreted as causal delayed effects."
            ),
        ]
    })

    return summary


# ============================================================
# MAIN FUNCTION
# ============================================================

def run_monthly_lag_analysis():
    """
    Run Part 3.3: monthly lag analysis.

    The analysis:
    - loads the monthly integrated dataset from Part 3.2;
    - creates lagged pollutant indicators for lag 0, 1, 2 and 3 months;
    - validates lagged values to avoid crossing the 2019-2023 gap;
    - computes Spearman correlations between lagged pollutants and
      current-month health event rates;
    - summarizes the best lag for each pollutant-outcome-group combination;
    - produces rho-vs-lag plots;
    - produces scatter plots for descriptively strongest lags;
    - exports CSV summary tables and figures.
    """

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("\n========================================")
    print("MONTHLY LAG ANALYSIS")
    print("========================================")

    # ------------------------------------------------------------
    # 1. Load monthly integrated dataset
    # ------------------------------------------------------------

    data = load_monthly_integrated_dataset()

    print("\nInput monthly integrated dataset:")
    print(data.head(20))

    print("\nInput dataset shape:")
    print(data.shape)

    print("\nRows by area:")
    print(data["Area"].value_counts())

    print("\nYears included:")
    print(sorted(data["Year"].dropna().unique()))

    print("\nInput missing values check:")
    print(data.isna().sum())

    # ------------------------------------------------------------
    # 2. Build lagged dataset
    # ------------------------------------------------------------

    lagged = build_lagged_dataset(data)

    lagged_output_path = os.path.join(
        OUTPUT_DIR,
        "monthly_lag_integrated_dataset.csv"
    )

    lagged.to_csv(
        lagged_output_path,
        index=False,
        sep=";"
    )

    print("\nLagged monthly dataset:")
    print(lagged.head(30))

    print("\nLagged dataset shape:")
    print(lagged.shape)

    print("\nLagged missing values check:")
    print(lagged.isna().sum())

    # ------------------------------------------------------------
    # 3. Lag availability check
    # ------------------------------------------------------------

    lag_availability = summarize_lag_availability(lagged)

    lag_availability.to_csv(
        os.path.join(OUTPUT_DIR, "lag_availability_check.csv"),
        index=False,
        sep=";"
    )

    print("\nLag availability check:")
    print(lag_availability)

    # ------------------------------------------------------------
    # 4. Spearman correlations by lag
    # ------------------------------------------------------------

    correlation_summary = compute_lagged_spearman_correlations(lagged)

    correlation_summary.to_csv(
        os.path.join(OUTPUT_DIR, "monthly_lag_spearman_summary.csv"),
        index=False,
        sep=";"
    )

    print("\nMonthly lag Spearman correlation summary:")
    print(correlation_summary)

    # ------------------------------------------------------------
    # 5. Best lag summary
    # ------------------------------------------------------------

    best_lag_summary = summarize_best_lags(correlation_summary)

    best_lag_summary.to_csv(
        os.path.join(OUTPUT_DIR, "monthly_lag_best_lag_summary.csv"),
        index=False,
        sep=";"
    )

    print("\nBest lag summary:")
    print(best_lag_summary)

    # ------------------------------------------------------------
    # 6. Plots
    # ------------------------------------------------------------

    plot_rho_vs_lag(correlation_summary)

    plot_lagged_scatter_for_best_lags(
        lagged=lagged,
        best_lag_summary=best_lag_summary
    )

    # ------------------------------------------------------------
    # 7. General summary
    # ------------------------------------------------------------

    summary = summarize_lag_analysis(
        lagged=lagged,
        correlation_summary=correlation_summary
    )

    summary.to_csv(
        os.path.join(OUTPUT_DIR, "monthly_lag_analysis_summary.csv"),
        index=False,
        sep=";"
    )

    print("\n========================================")
    print("MONTHLY LAG ANALYSIS COMPLETED")
    print("========================================")
    print(f"Results saved in: {OUTPUT_DIR}")


if __name__ == "__main__":
    run_monthly_lag_analysis()