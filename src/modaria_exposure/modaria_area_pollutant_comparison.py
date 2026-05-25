import os
import glob
import warnings

import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import shapiro, ttest_rel, wilcoxon


# ============================================================
# GLOBAL SETTINGS
# ============================================================

COMMON_YEARS = [2016, 2017, 2018, 2019, 2023]

AREA_ORDER = ["Industrial", "Agricultural"]
POLLUTANTS = ["NO2", "PM25"]

METHODS = {
    "Population_weighted_mean": "Population-weighted area exposure",
    "Arithmetic_mean": "Arithmetic area mean",
}

MAIN_METHOD = "Population_weighted_mean"

INPUT_DIR = (
    "Dati/output/4-Modaria exposure/"
    "4.1-Data validation and area aggregation"
)

OUTPUT_DIR = (
    "Dati/output/4-Modaria exposure/"
    "4.2-Area pollutant comparison"
)

INPUT_CANDIDATES = [
    # Updated health-aligned Part 4.1 outputs.
    # Prefer the wide summary because it has exactly one row per Date × Area
    # and contains both pollutants and both exposure indicators.
    os.path.join(INPUT_DIR, "modaria_daily_area_exposure_summary_wide.csv"),

    # Long summary is also valid and can be used as fallback.
    os.path.join(INPUT_DIR, "modaria_daily_area_exposure_summary_long.csv"),

    # Older possible names kept only for backward compatibility.
    os.path.join(INPUT_DIR, "modaria_daily_area_exposure.csv"),
    os.path.join(INPUT_DIR, "daily_area_exposure.csv"),
    os.path.join(INPUT_DIR, "modaria_area_exposure_daily.csv"),
    os.path.join(INPUT_DIR, "modaria_daily_area_exposure_dataset.csv"),
]


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


def normalize_text(value):
    """
    Normalize text for safer matching.
    """

    if pd.isna(value):
        return None

    return str(value).strip()


def normalize_column_name(col):
    """
    Normalize column names to simplify automatic column detection.
    """

    return (
        str(col)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace(".", "")
        .replace("-", "_")
    )


def find_existing_input_file():
    """
    Find the daily ModAria area exposure file produced in Part 4.1.
    """

    for candidate in INPUT_CANDIDATES:
        if os.path.exists(candidate):
            return candidate

    # Fallback: search all CSV files in the 4.1 output folder.
    csv_files = glob.glob(os.path.join(INPUT_DIR, "*.csv"))

    likely_files = [
        file for file in csv_files
        if "area" in os.path.basename(file).lower()
        and "exposure" in os.path.basename(file).lower()
        and "daily" in os.path.basename(file).lower()
    ]

    if likely_files:
        return likely_files[0]

    raise FileNotFoundError(
        "Could not find the daily ModAria area exposure file from Part 4.1.\n"
        f"Checked candidates:\n{INPUT_CANDIDATES}\n"
        f"CSV files found in {INPUT_DIR}:\n{csv_files}"
    )


def parse_dates_safely(series):
    """
    Parse date values while avoiding pandas ambiguous-format warnings.
    """

    possible_formats = [
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y %H:%M:%S",
    ]

    for fmt in possible_formats:
        parsed = pd.to_datetime(series, format=fmt, errors="coerce")

        if parsed.notna().sum() >= 0.90 * len(series):
            return parsed

    # Last fallback.
    # dayfirst=True is coherent with Italian/ARPA-style dates.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        parsed = pd.to_datetime(series, errors="coerce", dayfirst=True)

    return parsed


def get_season(month):
    """
    Assign meteorological season.
    """

    if month in [12, 1, 2]:
        return "Winter"
    if month in [3, 4, 5]:
        return "Spring"
    if month in [6, 7, 8]:
        return "Summer"
    return "Autumn"


def get_season_year(date):
    """
    Assign season year.

    December belongs to the winter of the following year.
    Example:
    December 2018 -> Winter 2019
    January 2019  -> Winter 2019
    February 2019 -> Winter 2019
    """

    if date.month == 12:
        return date.year + 1

    return date.year


def safe_filename(text):
    """
    Create safe filenames for output figures.
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


def interpret_test_result(p_value):
    """
    Simple statistical-significance interpretation.
    """

    if pd.isna(p_value):
        return "Statistical test not available"

    if p_value < 0.05:
        return "Statistically significant difference at p < 0.05"

    return "No statistically significant difference at p < 0.05"


def interpret_direction(mean_difference):
    """
    Interpret the direction of the area difference.

    Difference is computed as:
    Agricultural - Industrial
    """

    if pd.isna(mean_difference):
        return "Direction not available"

    if mean_difference > 0:
        return "Agricultural area higher on average"

    if mean_difference < 0:
        return "Industrial area higher on average"

    return "Same average value"


# ============================================================
# DATA LOADING AND STANDARDIZATION
# ============================================================

def load_and_standardize_daily_area_exposure():
    """
    Load the area-level daily exposure dataset produced in Part 4.1.

    The function supports two possible structures:

    1. Long format:
       Date | Area | Pollutant | Arithmetic_mean | Population_weighted_mean

    2. Wide format:
       Date | Area | NO2_arithmetic_mean | NO2_population_weighted_mean
                   | PM25_arithmetic_mean | PM25_population_weighted_mean

    The output is standardized as:

       Date | Year | Month | Season | SeasonYear | Area | Pollutant
            | Arithmetic_mean | Population_weighted_mean
    """

    input_path = find_existing_input_file()

    print("\nInput file used for Part 4.2:")
    print(input_path)

    raw = read_project_csv(input_path)

    print("\nInput columns:")
    print(raw.columns.tolist())

    normalized_columns = {
        col: normalize_column_name(col)
        for col in raw.columns
    }

    # ------------------------------------------------------------
    # Detect date column
    # ------------------------------------------------------------

    date_col = None

    for col, norm_col in normalized_columns.items():
        if norm_col in ["date", "data", "day", "giorno"]:
            date_col = col
            break

    if date_col is None:
        raise ValueError(
            "Could not detect date column in the 4.1 area exposure dataset."
        )

    # ------------------------------------------------------------
    # Detect area column
    # ------------------------------------------------------------

    area_col = None

    for col, norm_col in normalized_columns.items():
        if norm_col == "area":
            area_col = col
            break

    if area_col is None:
        raise ValueError(
            "Could not detect Area column in the 4.1 area exposure dataset."
        )

    raw[date_col] = parse_dates_safely(raw[date_col])
    raw[area_col] = raw[area_col].apply(normalize_text)

    # ------------------------------------------------------------
    # Case 1: long format with Pollutant column
    # ------------------------------------------------------------

    # ------------------------------------------------------------
    # Case 1: long format with Pollutant column
    # ------------------------------------------------------------

    pollutant_col = None

    for col, norm_col in normalized_columns.items():
        if norm_col in ["pollutant", "inquinante", "contaminant"]:
            pollutant_col = col
            break

    if pollutant_col is not None:
        raw[pollutant_col] = (
            raw[pollutant_col]
            .astype(str)
            .str.strip()
            .str.replace("PM2.5", "PM25", regex=False)
            .str.replace("pm2.5", "PM25", regex=False)
            .str.upper()
        )

        # IMPORTANT:
        # Use exact column-name matching first.
        # This avoids confusing Arithmetic_mean with Arithmetic_coverage_percentage.
        arithmetic_col = None
        population_weighted_col = None

        for col, norm_col in normalized_columns.items():
            if norm_col == "arithmetic_mean":
                arithmetic_col = col

            if norm_col == "population_weighted_mean":
                population_weighted_col = col

        # Fallback only if exact names are not found
        if arithmetic_col is None:
            for col, norm_col in normalized_columns.items():
                if (
                        "arith" in norm_col
                        and "coverage" not in norm_col
                        and "percentage" not in norm_col
                ):
                    arithmetic_col = col
                    break

        if population_weighted_col is None:
            for col, norm_col in normalized_columns.items():
                if (
                        "population_weighted" in norm_col
                        or "pop_weighted" in norm_col
                        or ("weighted" in norm_col and "population" in norm_col)
                ):
                    population_weighted_col = col
                    break

        if arithmetic_col is None:
            raise ValueError(
                "Could not detect arithmetic mean column in long-format input."
            )

        if population_weighted_col is None:
            raise ValueError(
                "Could not detect population-weighted mean column in long-format input."
            )

        data = raw[
            [date_col, area_col, pollutant_col, arithmetic_col, population_weighted_col]
        ].copy()

        data.columns = [
            "Date",
            "Area",
            "Pollutant",
            "Arithmetic_mean",
            "Population_weighted_mean",
        ]

    # ------------------------------------------------------------
    # Case 2: wide format with pollutant-specific columns
    # ------------------------------------------------------------

    else:
        records = []

        for _, row in raw.iterrows():
            for pollutant in POLLUTANTS:
                pollutant_keys = [pollutant.lower()]

                if pollutant == "PM25":
                    pollutant_keys += ["pm25", "pm2_5", "pm2.5"]

                arithmetic_col = None
                population_weighted_col = None

                for col, norm_col in normalized_columns.items():
                    col_is_pollutant = any(key in norm_col for key in pollutant_keys)

                    if not col_is_pollutant:
                        continue

                    if "arith" in norm_col:
                        arithmetic_col = col

                    if (
                        "population_weighted" in norm_col
                        or "pop_weighted" in norm_col
                        or ("weighted" in norm_col and "population" in norm_col)
                    ):
                        population_weighted_col = col

                if arithmetic_col is None or population_weighted_col is None:
                    raise ValueError(
                        f"Could not detect both arithmetic and population-weighted "
                        f"columns for pollutant {pollutant} in wide-format input."
                    )

                records.append({
                    "Date": row[date_col],
                    "Area": row[area_col],
                    "Pollutant": pollutant,
                    "Arithmetic_mean": row[arithmetic_col],
                    "Population_weighted_mean": row[population_weighted_col],
                })

        data = pd.DataFrame(records)

    # ------------------------------------------------------------
    # Final cleaning
    # ------------------------------------------------------------

    data["Pollutant"] = (
        data["Pollutant"]
        .astype(str)
        .str.strip()
        .str.replace("PM2.5", "PM25", regex=False)
        .str.replace("pm2.5", "PM25", regex=False)
        .str.upper()
    )

    data["Area"] = data["Area"].apply(normalize_text)

    data["Arithmetic_mean"] = pd.to_numeric(
        data["Arithmetic_mean"],
        errors="coerce"
    )

    data["Population_weighted_mean"] = pd.to_numeric(
        data["Population_weighted_mean"],
        errors="coerce"
    )

    data = data[
        data["Date"].notna()
        & data["Area"].isin(AREA_ORDER)
        & data["Pollutant"].isin(POLLUTANTS)
    ].copy()

    data["Year"] = data["Date"].dt.year
    data["Month"] = data["Date"].dt.month
    data["Season"] = data["Month"].apply(get_season)
    data["SeasonYear"] = data["Date"].apply(get_season_year)

    data = data[data["Year"].isin(COMMON_YEARS)].copy()

    data = data[
        [
            "Date",
            "Year",
            "Month",
            "Season",
            "SeasonYear",
            "Area",
            "Pollutant",
            "Arithmetic_mean",
            "Population_weighted_mean",
        ]
    ].sort_values(["Pollutant", "Area", "Date"]).reset_index(drop=True)

    return data


def validate_daily_standardized_dataset(daily):
    """
    Validate the standardized daily area exposure dataset produced for Part 4.2.

    Expected structure:
    1826 selected days × 2 areas × 2 pollutants = 7304 rows.
    """

    expected_days = 1826
    expected_rows = expected_days * len(AREA_ORDER) * len(POLLUTANTS)

    errors = []

    if len(daily) != expected_rows:
        errors.append(
            f"Expected {expected_rows} daily rows "
            f"({expected_days} days × {len(AREA_ORDER)} areas × {len(POLLUTANTS)} pollutants), "
            f"but found {len(daily)}."
        )

    observed_years = sorted(daily["Year"].dropna().unique().tolist())

    if observed_years != COMMON_YEARS:
        errors.append(
            f"Expected years {COMMON_YEARS}, but found {observed_years}."
        )

    row_counts = (
        daily
        .groupby(["Area", "Pollutant"])
        .size()
        .reset_index(name="N_rows")
    )

    wrong_counts = row_counts[row_counts["N_rows"] != expected_days].copy()

    if len(wrong_counts) > 0:
        errors.append(
            "Unexpected number of daily rows for some Area × Pollutant groups:\n"
            f"{wrong_counts.to_string(index=False)}"
        )

    missing_values = daily[
        [
            "Date",
            "Area",
            "Pollutant",
            "Arithmetic_mean",
            "Population_weighted_mean",
        ]
    ].isna().sum()

    if missing_values.sum() > 0:
        errors.append(
            "Missing values found in standardized daily dataset:\n"
            f"{missing_values.to_string()}"
        )

    duplicated_rows = (
        daily
        .groupby(["Date", "Area", "Pollutant"])
        .size()
        .reset_index(name="N")
    )

    duplicated_rows = duplicated_rows[duplicated_rows["N"] > 1].copy()

    if len(duplicated_rows) > 0:
        errors.append(
            "Duplicated Date × Area × Pollutant rows found:\n"
            f"{duplicated_rows.to_string(index=False)}"
        )

    if errors:
        raise ValueError(
            "\nPART 4.2 DAILY STANDARDIZED DATASET VALIDATION FAILED\n\n"
            + "\n\n".join(errors)
        )

    print("\nDaily standardized dataset validation passed.")
    print(f"Expected rows: {expected_rows}")
    print(f"Observed rows: {len(daily)}")
    print("Rows by Area × Pollutant:")
    print(row_counts)

# ============================================================
# TEMPORAL AGGREGATION
# ============================================================

def build_monthly_dataset(daily):
    """
    Aggregate daily area exposure to monthly means.
    """

    monthly = daily.copy()

    monthly["MonthPeriod"] = monthly["Date"].dt.to_period("M").dt.to_timestamp()

    monthly = (
        monthly
        .groupby(
            ["MonthPeriod", "Year", "Month", "Season", "Area", "Pollutant"],
            as_index=False
        )
        [["Arithmetic_mean", "Population_weighted_mean"]]
        .mean()
    )

    monthly["TimeLabel"] = monthly["MonthPeriod"].dt.strftime("%Y-%m")

    return monthly


def build_seasonal_dataset(daily):
    """
    Aggregate daily area exposure to seasonal means.

    Incomplete seasons are removed.
    This is important because:
    - Winter 2016 misses December 2015;
    - Winter 2020 misses January-February 2020 because COVID years are excluded;
    - Winter 2023 misses December 2022;
    - Winter 2024 only contains December 2023.
    """

    seasonal_base = daily.copy()

    seasonal_base["MonthPeriod"] = seasonal_base["Date"].dt.to_period("M").dt.to_timestamp()

    seasonal = (
        seasonal_base
        .groupby(
            ["SeasonYear", "Season", "Area", "Pollutant"],
            as_index=False
        )
        .agg(
            Arithmetic_mean=("Arithmetic_mean", "mean"),
            Population_weighted_mean=("Population_weighted_mean", "mean"),
            Number_of_days=("Date", "nunique"),
            Number_of_months=("Month", "nunique"),
        )
    )

    # Complete meteorological seasons require 3 months.
    seasonal = seasonal[seasonal["Number_of_months"] == 3].copy()

    seasonal["TimeLabel"] = (
        seasonal["SeasonYear"].astype(str)
        + "-"
        + seasonal["Season"].astype(str)
    )

    return seasonal


# ============================================================
# STATISTICAL TEST DECISION TREE
# ============================================================

def choose_and_run_paired_test(values_agricultural, values_industrial):
    """
    Compare Agricultural and Industrial paired values.

    Decision logic:
    - Two samples;
    - Paired samples, because the two areas are compared on the same dates/months/seasons;
    - Normality is checked on paired differences;
    - If paired differences are compatible with normality: paired t-test;
    - Otherwise: Wilcoxon matched-pairs signed-rank test.
    """

    paired = pd.DataFrame({
        "Agricultural": values_agricultural,
        "Industrial": values_industrial,
    }).dropna()

    n = len(paired)

    if n < 3:
        return {
            "N_pairs": n,
            "Shapiro_statistic": pd.NA,
            "Shapiro_p_value": pd.NA,
            "Normality_result": "Not enough pairs for normality test",
            "Selected_test": "Not available",
            "Test_statistic": pd.NA,
            "p_value": pd.NA,
            "Test_interpretation": "Not enough paired observations",
        }

    paired["Difference_Agricultural_minus_Industrial"] = (
        paired["Agricultural"] - paired["Industrial"]
    )

    differences = paired["Difference_Agricultural_minus_Industrial"].dropna()

    if len(differences) < 3:
        return {
            "N_pairs": n,
            "Shapiro_statistic": pd.NA,
            "Shapiro_p_value": pd.NA,
            "Normality_result": "Not enough valid differences",
            "Selected_test": "Not available",
            "Test_statistic": pd.NA,
            "p_value": pd.NA,
            "Test_interpretation": "Not enough valid differences",
        }

    # Shapiro-Wilk is very sensitive for large samples.
    # We use a fixed random subsample for daily data, as already done in previous scripts.
    shapiro_sample = differences.sample(
        n=min(500, len(differences)),
        random_state=1
    )

    shapiro_result = shapiro(shapiro_sample)

    shapiro_stat = shapiro_result.statistic
    shapiro_p = shapiro_result.pvalue

    if shapiro_p >= 0.05:
        normality_result = "Paired differences compatible with normality"
        selected_test = "Paired t-test"

        test = ttest_rel(
            paired["Agricultural"],
            paired["Industrial"],
            nan_policy="omit"
        )

        test_stat = test.statistic
        test_p = test.pvalue

    else:
        normality_result = "Paired differences not normally distributed"
        selected_test = "Wilcoxon matched-pairs signed-rank test"

        try:
            test = wilcoxon(
                paired["Agricultural"],
                paired["Industrial"],
                zero_method="wilcox",
                alternative="two-sided"
            )

            test_stat = test.statistic
            test_p = test.pvalue

        except ValueError:
            test_stat = pd.NA
            test_p = pd.NA
            selected_test = "Wilcoxon test not available"
            normality_result += "; all paired differences may be zero"

    return {
        "N_pairs": n,
        "Shapiro_statistic": shapiro_stat,
        "Shapiro_p_value": shapiro_p,
        "Normality_result": normality_result,
        "Selected_test": selected_test,
        "Test_statistic": test_stat,
        "p_value": test_p,
        "Test_interpretation": interpret_test_result(test_p),
    }


def run_paired_area_comparison(dataset, temporal_scale, time_column):
    """
    Run paired Agricultural vs Industrial comparisons.

    Difference is always computed as:
    Agricultural - Industrial
    """

    rows = []

    for method_col, method_label in METHODS.items():
        for pollutant in POLLUTANTS:
            subset = dataset[
                (dataset["Pollutant"] == pollutant)
            ].copy()

            wide = subset.pivot_table(
                index=time_column,
                columns="Area",
                values=method_col,
                aggfunc="mean"
            )

            if "Agricultural" not in wide.columns or "Industrial" not in wide.columns:
                continue

            wide = wide[["Agricultural", "Industrial"]].dropna().copy()

            test_result = choose_and_run_paired_test(
                values_agricultural=wide["Agricultural"],
                values_industrial=wide["Industrial"]
            )

            mean_agricultural = wide["Agricultural"].mean()
            mean_industrial = wide["Industrial"].mean()
            median_agricultural = wide["Agricultural"].median()
            median_industrial = wide["Industrial"].median()

            mean_difference = mean_agricultural - mean_industrial
            median_difference = median_agricultural - median_industrial

            rows.append({
                "Temporal_scale": temporal_scale,
                "Pollutant": pollutant,
                "Exposure_indicator": method_col,
                "Exposure_indicator_label": method_label,
                "N_pairs": test_result["N_pairs"],
                "Mean_Agricultural": mean_agricultural,
                "Mean_Industrial": mean_industrial,
                "Mean_difference_Agricultural_minus_Industrial": mean_difference,
                "Median_Agricultural": median_agricultural,
                "Median_Industrial": median_industrial,
                "Median_difference_Agricultural_minus_Industrial": median_difference,
                "Direction": interpret_direction(mean_difference),
                "Shapiro_statistic_on_paired_differences": test_result["Shapiro_statistic"],
                "Shapiro_p_value_on_paired_differences": test_result["Shapiro_p_value"],
                "Normality_result": test_result["Normality_result"],
                "Selected_test": test_result["Selected_test"],
                "Test_statistic": test_result["Test_statistic"],
                "p_value": test_result["p_value"],
                "Test_interpretation": test_result["Test_interpretation"],
            })

    return pd.DataFrame(rows)


# ============================================================
# METHOD COMPARISON
# ============================================================

def summarize_method_comparison(daily):
    """
    Compare arithmetic mean and population-weighted mean.

    This does not replace the main analysis.
    It is used as a sensitivity check.
    """

    rows = []

    for area in AREA_ORDER:
        for pollutant in POLLUTANTS:
            subset = daily[
                (daily["Area"] == area)
                & (daily["Pollutant"] == pollutant)
            ].dropna(
                subset=["Arithmetic_mean", "Population_weighted_mean"]
            ).copy()

            if subset.empty:
                continue

            subset["Difference_population_weighted_minus_arithmetic"] = (
                subset["Population_weighted_mean"] - subset["Arithmetic_mean"]
            )

            rows.append({
                "Area": area,
                "Pollutant": pollutant,
                "N_days": len(subset),
                "Mean_arithmetic": subset["Arithmetic_mean"].mean(),
                "Mean_population_weighted": subset["Population_weighted_mean"].mean(),
                "Mean_difference_population_weighted_minus_arithmetic": (
                    subset["Difference_population_weighted_minus_arithmetic"].mean()
                ),
                "Median_difference_population_weighted_minus_arithmetic": (
                    subset["Difference_population_weighted_minus_arithmetic"].median()
                ),
                "Correlation_arithmetic_vs_population_weighted": (
                    subset["Arithmetic_mean"].corr(subset["Population_weighted_mean"])
                ),
            })

    return pd.DataFrame(rows)


# ============================================================
# PLOTTING FUNCTIONS
# ============================================================

def pollutant_label(pollutant):
    """
    Return a readable pollutant label for plots.
    """

    if pollutant == "PM25":
        return "PM2.5"

    return pollutant


def concentration_label(pollutant):
    """
    Return the y-axis label with measurement unit.
    """

    if pollutant == "PM25":
        return "PM2.5 concentration (µg/m³)"

    if pollutant == "NO2":
        return "NO2 concentration (µg/m³)"

    return f"{pollutant} concentration (µg/m³)"


def plot_daily_time_series(daily):
    """
    Plot daily area-level exposure time series.

    Main plots are focused on the population-weighted exposure indicator.

    Important:
    Data are plotted year by year to avoid connecting the last available day
    of 2019 with the first available day of 2023.
    """

    area_colors = {
        "Industrial": "tab:blue",
        "Agricultural": "tab:orange",
    }

    for pollutant in POLLUTANTS:
        subset = daily[daily["Pollutant"] == pollutant].copy()

        plt.figure(figsize=(12, 5))

        for area in AREA_ORDER:
            area_subset = subset[subset["Area"] == area].copy()
            area_subset = area_subset.sort_values("Date")

            first_label = True

            # Plot separately by year to break the 2019-2023 gap
            for year in COMMON_YEARS:
                year_subset = area_subset[area_subset["Year"] == year].copy()

                if year_subset.empty:
                    continue

                plt.plot(
                    year_subset["Date"],
                    year_subset[MAIN_METHOD],
                    label=area if first_label else None,
                    color=area_colors.get(area),
                    alpha=0.8
                )

                first_label = False

        plt.title(
            f"Daily {pollutant_label(pollutant)} "
            "population-weighted exposure by area"
        )
        plt.xlabel("Date")
        plt.ylabel(concentration_label(pollutant))
        plt.legend()
        plt.tight_layout()

        filename = f"daily_{pollutant}_population_weighted_time_series.png"

        plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=300)
        plt.close()


def plot_monthly_time_series(monthly):
    """
    Plot monthly area-level exposure time series.

    Important:
    Data are plotted year by year to avoid connecting the last available month
    of 2019 with the first available month of 2023.
    """

    area_colors = {
        "Industrial": "tab:blue",
        "Agricultural": "tab:orange",
    }

    for pollutant in POLLUTANTS:
        subset = monthly[monthly["Pollutant"] == pollutant].copy()

        plt.figure(figsize=(12, 5))

        for area in AREA_ORDER:
            area_subset = subset[subset["Area"] == area].copy()
            area_subset = area_subset.sort_values("MonthPeriod")

            first_label = True

            # Plot separately by year to break the 2019-2023 gap
            for year in COMMON_YEARS:
                year_subset = area_subset[area_subset["Year"] == year].copy()

                if year_subset.empty:
                    continue

                plt.plot(
                    year_subset["MonthPeriod"],
                    year_subset[MAIN_METHOD],
                    marker="o",
                    label=area if first_label else None,
                    color=area_colors.get(area),
                    alpha=0.8
                )

                first_label = False

        plt.title(
            f"Monthly {pollutant_label(pollutant)} "
            "population-weighted exposure by area"
        )
        plt.xlabel("Month")
        plt.ylabel(concentration_label(pollutant))
        plt.legend()
        plt.tight_layout()

        filename = f"monthly_{pollutant}_population_weighted_time_series.png"

        plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=300)
        plt.close()


def plot_distribution_boxplots(daily):
    """
    Plot daily population-weighted exposure distributions by area.
    """

    for pollutant in POLLUTANTS:
        subset = daily[daily["Pollutant"] == pollutant].copy()

        plot_data = subset[["Area", MAIN_METHOD]].dropna().copy()

        plt.figure(figsize=(7, 5))

        plot_data.boxplot(
            column=MAIN_METHOD,
            by="Area"
        )

        plt.title(
            f"Daily {pollutant_label(pollutant)} "
            "population-weighted exposure by area"
        )
        plt.suptitle("")
        plt.xlabel("Area")
        plt.ylabel(concentration_label(pollutant))
        plt.tight_layout()

        filename = f"daily_{pollutant}_population_weighted_boxplot.png"

        plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=300)
        plt.close()


def concentration_unit():
    """
    Return concentration unit used for NO2 and PM2.5.
    """

    return "µg/m³"


def plot_method_comparison(daily):
    """
    Plot arithmetic mean vs population-weighted mean.

    These plots are used as a sensitivity check.
    """

    for area in AREA_ORDER:
        for pollutant in POLLUTANTS:
            subset = daily[
                (daily["Area"] == area)
                & (daily["Pollutant"] == pollutant)
            ].dropna(
                subset=["Arithmetic_mean", "Population_weighted_mean"]
            ).copy()

            if subset.empty:
                continue

            plt.figure(figsize=(6, 6))

            plt.scatter(
                subset["Arithmetic_mean"],
                subset["Population_weighted_mean"],
                alpha=0.6
            )

            plt.title(
                f"{pollutant_label(pollutant)} method comparison - {area}\n"
                "Arithmetic mean vs population-weighted mean"
            )

            plt.xlabel(f"Arithmetic area mean ({concentration_unit()})")
            plt.ylabel(f"Population-weighted area exposure ({concentration_unit()})")
            plt.grid(True, alpha=0.3)
            plt.tight_layout()

            filename = (
                f"method_comparison_{safe_filename(area)}_"
                f"{pollutant}_scatter.png"
            )

            plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=300)
            plt.close()


# ============================================================
# SUMMARY TABLE
# ============================================================

def build_analysis_summary(daily, monthly, seasonal, comparison_summary):
    """
    Build a compact summary of Part 4.2.
    """

    summary = pd.DataFrame({
        "Indicator": [
            "Input folder",
            "Output folder",
            "Temporal scales",
            "Pollutants",
            "Areas",
            "Main exposure indicator",
            "Sensitivity exposure indicator",
            "Daily rows",
            "Monthly rows",
            "Seasonal rows after incomplete-season removal",
            "Common years",
            "Main statistical comparison",
            "Test selection rule",
            "Interpretation rule",
        ],
        "Value": [
            INPUT_DIR,
            OUTPUT_DIR,
            "Daily, monthly, seasonal",
            ", ".join(POLLUTANTS),
            ", ".join(AREA_ORDER),
            "Population-weighted area exposure",
            "Arithmetic area mean",
            len(daily),
            len(monthly),
            len(seasonal),
            ", ".join(map(str, COMMON_YEARS)),
            "Agricultural vs Industrial paired comparison",
            (
                "Normality is tested on paired differences. "
                "If differences are compatible with normality, paired t-test is used; "
                "otherwise Wilcoxon matched-pairs signed-rank test is used."
            ),
            (
                "Results are environmental area-level comparisons. "
                "They do not include health data and should not be interpreted "
                "as health-effect evidence."
            ),
        ],
    })

    return summary


# ============================================================
# MAIN FUNCTION
# ============================================================

def run_modaria_area_pollutant_comparison():
    """
    Run Part 4.2: ModAria area-level pollutant comparison.

    This script:
    - loads the daily area exposure dataset produced in Part 4.1;
    - checks and standardizes the dataset;
    - builds daily, monthly and seasonal area-level exposure datasets;
    - compares Agricultural vs Industrial exposure values;
    - selects the statistical test according to the paired-samples decision tree;
    - uses population-weighted exposure as the main indicator;
    - keeps arithmetic mean as sensitivity indicator;
    - exports CSV tables and figures.
    """

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("\n========================================")
    print("MODARIA AREA POLLUTANT COMPARISON")
    print("========================================")

    # ------------------------------------------------------------
    # 1. Load and standardize daily area exposure
    # ------------------------------------------------------------

    daily = load_and_standardize_daily_area_exposure()
    validate_daily_standardized_dataset(daily)

    daily_output_path = os.path.join(
        OUTPUT_DIR,
        "modaria_daily_area_exposure_standardized.csv"
    )

    daily.to_csv(
        daily_output_path,
        index=False,
        sep=";"
    )

    print("\nDaily standardized dataset:")
    print(daily.head(20))

    print("\nDaily standardized dataset shape:")
    print(daily.shape)

    print("\nRows by area and pollutant:")
    print(daily.groupby(["Area", "Pollutant"]).size())

    print("\nMissing values check:")
    print(daily.isna().sum())

    # ------------------------------------------------------------
    # 2. Monthly and seasonal aggregation
    # ------------------------------------------------------------

    monthly = build_monthly_dataset(daily)

    monthly.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_monthly_area_exposure_dataset.csv"),
        index=False,
        sep=";"
    )

    print("\nMonthly area exposure dataset:")
    print(monthly.head(20))

    print("\nMonthly dataset shape:")
    print(monthly.shape)

    seasonal = build_seasonal_dataset(daily)

    seasonal.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_seasonal_area_exposure_dataset.csv"),
        index=False,
        sep=";"
    )

    print("\nSeasonal area exposure dataset:")
    print(seasonal.head(20))

    print("\nSeasonal dataset shape:")
    print(seasonal.shape)

    # ------------------------------------------------------------
    # 3. Paired statistical comparisons
    # ------------------------------------------------------------

    daily_comparison = run_paired_area_comparison(
        dataset=daily,
        temporal_scale="Daily",
        time_column="Date"
    )

    monthly_comparison = run_paired_area_comparison(
        dataset=monthly,
        temporal_scale="Monthly",
        time_column="MonthPeriod"
    )

    seasonal_for_test = seasonal.copy()
    seasonal_for_test["SeasonKey"] = (
        seasonal_for_test["SeasonYear"].astype(str)
        + "_"
        + seasonal_for_test["Season"].astype(str)
    )

    seasonal_comparison = run_paired_area_comparison(
        dataset=seasonal_for_test,
        temporal_scale="Seasonal",
        time_column="SeasonKey"
    )

    comparison_summary = pd.concat(
        [daily_comparison, monthly_comparison, seasonal_comparison],
        ignore_index=True
    )

    comparison_summary.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_area_pollutant_paired_test_summary.csv"),
        index=False,
        sep=";"
    )

    print("\nPaired statistical comparison summary:")
    print(comparison_summary)

    # ------------------------------------------------------------
    # 4. Method comparison: arithmetic vs population-weighted
    # ------------------------------------------------------------

    method_comparison = summarize_method_comparison(daily)

    method_comparison.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_method_comparison_summary.csv"),
        index=False,
        sep=";"
    )

    print("\nArithmetic vs population-weighted method comparison:")
    print(method_comparison)

    # ------------------------------------------------------------
    # 5. Plots
    # ------------------------------------------------------------

    plot_daily_time_series(daily)
    plot_monthly_time_series(monthly)
    plot_distribution_boxplots(daily)
    plot_method_comparison(daily)

    # ------------------------------------------------------------
    # 6. General summary
    # ------------------------------------------------------------

    analysis_summary = build_analysis_summary(
        daily=daily,
        monthly=monthly,
        seasonal=seasonal,
        comparison_summary=comparison_summary
    )

    analysis_summary.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_area_pollutant_comparison_summary.csv"),
        index=False,
        sep=";"
    )

    print("\n========================================")
    print("MODARIA AREA POLLUTANT COMPARISON COMPLETED")
    print("========================================")
    print(f"Results saved in: {OUTPUT_DIR}")


if __name__ == "__main__":
    run_modaria_area_pollutant_comparison()