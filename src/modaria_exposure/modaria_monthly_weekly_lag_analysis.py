import os

import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import spearmanr


# ============================================================
# PART 4.4 - MODARIA MONTHLY AND WEEKLY LAG ANALYSIS
# ============================================================
#
# Aim:
# This script repeats the monthly and weekly lag analyses performed
# in Part 3.3 and Part 3.4, but using ModAria area-level exposure
# indicators instead of station-based exposure indicators.
#
# Current scope:
# - Monthly lag analysis using the integrated dataset from Part 4.3.
# - Weekly lag analysis using daily ModAria area-level exposure and
#   selected health events from Part 2.2.
#
# Main exposure indicator:
# - Population-weighted ModAria exposure.
#
# Main association metric:
# - Spearman correlation.
#
# Important safeguard:
# - Lagged pollutant values are kept only when the lagged month/week is
#   exactly the expected distance before the current health month/week.
# - This prevents incorrect temporal links across the 2019-2023 gap.
# ============================================================


# ============================================================
# GLOBAL SETTINGS
# ============================================================

COMMON_YEARS = [2016, 2017, 2018, 2019, 2023]

MONTHLY_LAGS = [0, 1, 2, 3]
WEEKLY_LAGS = [0, 1, 2, 3, 4]

AREA_ORDER = ["Industrial", "Agricultural"]
OUTCOME_ORDER = ["Respiratory", "Cardiocirculatory"]

RUN_MONTHLY_ANALYSIS = True
RUN_WEEKLY_ANALYSIS = True

MONTHLY_INPUT_PATH = (
    "Dati/output/4-Modaria exposure/"
    "4.3-Modaria environmental health integration/"
    "modaria_monthly_environment_health_integrated_dataset.csv"
)

DAILY_MODARIA_INPUT_PATH = (
    "Dati/output/4-Modaria exposure/"
    "4.2-Area pollutant comparison/"
    "modaria_daily_area_exposure_standardized.csv"
)

HEALTH_SELECTED_EVENTS_PATH = (
    "Dati/output/2-Health data/2.2-Health event aggregation/"
    "health_events_selected_areas_outcomes.csv"
)

ANNUAL_HEALTH_RATES_PATH = (
    "Dati/output/2-Health data/2.2-Health event aggregation/"
    "annual_health_events_rates_by_area.csv"
)

OUTPUT_DIR = (
    "Dati/output/4-Modaria exposure/"
    "4.4-Modaria monthly and weekly lag analysis"
)

PLOTS_DIR = os.path.join(OUTPUT_DIR, "plots")

POLLUTANT_COLUMNS = [
    "NO2_population_weighted_mean",
    "PM25_population_weighted_mean",
]

OUTCOME_COLUMNS = [
    "Respiratory_rate_per_10000",
    "Cardiocirculatory_rate_per_10000",
]

VARIABLE_LABELS = {
    "NO2_population_weighted_mean": "Population-weighted NO2",
    "PM25_population_weighted_mean": "Population-weighted PM2.5",
    "Respiratory_rate_per_10000": "Respiratory acute event rate",
    "Cardiocirculatory_rate_per_10000": "Cardiocirculatory acute event rate",
}

VARIABLE_UNITS = {
    "NO2_population_weighted_mean": "NO2 concentration (µg/m³)",
    "PM25_population_weighted_mean": "PM2.5 concentration (µg/m³)",
    "Respiratory_rate_per_10000": "Events per 10,000 inhabitants",
    "Cardiocirculatory_rate_per_10000": "Events per 10,000 inhabitants",
}


# ============================================================
# GENERAL UTILITY FUNCTIONS
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
        .replace("µ", "u")
        .replace("³", "3")
    )


def find_column(df, possible_names, required=True):
    """
    Find a column using a list of possible names.

    This makes the script more robust to small naming differences
    in previously generated output files.
    """

    normalized_columns = {
        str(col).strip().lower(): col
        for col in df.columns
    }

    for name in possible_names:
        key = name.strip().lower()
        if key in normalized_columns:
            return normalized_columns[key]

    if required:
        raise ValueError(
            f"None of the expected columns was found: {possible_names}\n"
            f"Available columns: {df.columns.tolist()}"
        )

    return None


def get_variable_label(variable_name, temporal_scale=None):
    """
    Return a readable label for a variable name.
    """

    label = VARIABLE_LABELS.get(variable_name, variable_name)

    if temporal_scale is None:
        return label

    if variable_name in POLLUTANT_COLUMNS:
        return f"{temporal_scale} {label}"

    return label


def get_variable_unit(variable_name):
    """
    Return a readable axis label with units.
    """

    return VARIABLE_UNITS.get(variable_name, variable_name)


def month_index(date_series):
    """
    Convert datetime values to an integer month index.
    """

    return date_series.dt.year * 12 + date_series.dt.month


def week_index(date_series):
    """
    Convert weekly dates to an integer week index.

    If two WeekStart values are exactly one week apart,
    their week index difference is 1.
    """

    origin = pd.Timestamp("1900-01-01")

    return ((date_series - origin).dt.days // 7)


def add_week_columns(df, date_col):
    """
    Add weekly time columns.

    Weeks are defined as Monday-Sunday intervals.
    WeekStart is the Monday of the week.
    """

    df = df.copy()

    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df[df[date_col].notna()].copy()

    df["WeekStart"] = (
        df[date_col]
        .dt.to_period("W-SUN")
        .apply(lambda period: period.start_time)
    )

    df["Year"] = df["WeekStart"].dt.year
    df["Week"] = df["WeekStart"].dt.isocalendar().week.astype(int)

    df = df[df["Year"].isin(COMMON_YEARS)].copy()

    df["TimeLabel"] = df["WeekStart"].dt.strftime("%Y-%m-%d")

    return df


def parse_project_date(series):
    """
    Parse project dates.

    This handles:
    - standard ISO-like dates;
    - strings such as 01JAN2015:00:00:00.000.
    """

    parsed = pd.to_datetime(series, errors="coerce")

    if parsed.notna().sum() > 0:
        return parsed

    month_map = {
        "JAN": "01",
        "FEB": "02",
        "MAR": "03",
        "APR": "04",
        "MAY": "05",
        "JUN": "06",
        "JUL": "07",
        "AUG": "08",
        "SEP": "09",
        "OCT": "10",
        "NOV": "11",
        "DEC": "12",
    }

    def parse_single_value(value):
        if pd.isna(value):
            return pd.NaT

        text = str(value).strip().upper()

        try:
            date_part = text.split(":")[0]
            day = date_part[:2]
            month_text = date_part[2:5]
            year = date_part[5:9]
            month = month_map.get(month_text)

            if month is None:
                return pd.NaT

            return pd.to_datetime(
                f"{year}-{month}-{day}",
                errors="coerce"
            )

        except Exception:
            return pd.NaT

    return series.apply(parse_single_value)


def standardize_outcome(value):
    """
    Standardize outcome labels.
    """

    if pd.isna(value):
        return None

    text = str(value).strip().upper()

    if "RESP" in text:
        return "Respiratory"

    if "CARDIO" in text or "CIRCOL" in text:
        return "Cardiocirculatory"

    return str(value).strip()


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
# VALIDATION FUNCTIONS
# ============================================================

def validate_monthly_input_dataset(data):
    """
    Validate the monthly integrated dataset used for lag analysis.

    Expected structure:
    60 months × 2 areas = 120 rows.
    """

    errors = []

    expected_rows = 60 * len(AREA_ORDER)

    if len(data) != expected_rows:
        errors.append(
            f"Monthly input dataset: expected {expected_rows} rows, found {len(data)}."
        )

    duplicated_rows = (
        data
        .groupby(["MonthPeriod", "Area"])
        .size()
        .reset_index(name="N")
    )

    duplicated_rows = duplicated_rows[duplicated_rows["N"] > 1].copy()

    if len(duplicated_rows) > 0:
        errors.append(
            "Duplicated MonthPeriod × Area rows found:\n"
            f"{duplicated_rows.to_string(index=False)}"
        )

    expected_rows_by_area = 60

    rows_by_area = data["Area"].value_counts().to_dict()

    for area in AREA_ORDER:
        observed = rows_by_area.get(area, 0)

        if observed != expected_rows_by_area:
            errors.append(
                f"{area}: expected {expected_rows_by_area} monthly rows, found {observed}."
            )

    observed_years = sorted(data["Year"].dropna().astype(int).unique().tolist())

    if observed_years != COMMON_YEARS:
        errors.append(
            f"Monthly input dataset: expected years {COMMON_YEARS}, found {observed_years}."
        )

    required_columns = [
        "MonthPeriod",
        "Year",
        "Month",
        "Season",
        "Area",
        "Population",
    ] + POLLUTANT_COLUMNS + OUTCOME_COLUMNS

    missing_columns = [
        col for col in required_columns
        if col not in data.columns
    ]

    if missing_columns:
        errors.append(
            "Missing columns in monthly input dataset:\n"
            f"{missing_columns}"
        )

    missing_values = data[required_columns].isna().sum()
    missing_values = missing_values[missing_values > 0]

    if len(missing_values) > 0:
        errors.append(
            "Missing values found in monthly input dataset:\n"
            f"{missing_values.to_string()}"
        )

    if errors:
        raise ValueError(
            "\nMONTHLY INPUT DATASET VALIDATION FAILED\n\n"
            + "\n\n".join(errors)
        )

    print("\nMonthly input dataset validation passed.")
    print(f"Monthly rows: {len(data)} / expected {expected_rows}")
    print("Rows by area:")
    print(data["Area"].value_counts())


def validate_weekly_integrated_dataset(integrated):
    """
    Validate the weekly environmental-health integrated dataset.

    Expected structure with the current week definition:
    261 weeks × 2 areas = 522 rows.
    """

    errors = []

    expected_weeks_per_area = 261
    expected_rows = expected_weeks_per_area * len(AREA_ORDER)

    if len(integrated) != expected_rows:
        errors.append(
            f"Weekly integrated dataset: expected {expected_rows} rows "
            f"({expected_weeks_per_area} weeks × {len(AREA_ORDER)} areas), "
            f"found {len(integrated)}."
        )

    duplicated_rows = (
        integrated
        .groupby(["WeekStart", "Area"])
        .size()
        .reset_index(name="N")
    )

    duplicated_rows = duplicated_rows[duplicated_rows["N"] > 1].copy()

    if len(duplicated_rows) > 0:
        errors.append(
            "Duplicated WeekStart × Area rows found:\n"
            f"{duplicated_rows.to_string(index=False)}"
        )

    rows_by_area = integrated["Area"].value_counts().to_dict()

    for area in AREA_ORDER:
        observed = rows_by_area.get(area, 0)

        if observed != expected_weeks_per_area:
            errors.append(
                f"{area}: expected {expected_weeks_per_area} weekly rows, found {observed}."
            )

    observed_years = sorted(integrated["Year"].dropna().astype(int).unique().tolist())

    if observed_years != COMMON_YEARS:
        errors.append(
            f"Weekly integrated dataset: expected years {COMMON_YEARS}, found {observed_years}."
        )

    required_columns = [
        "WeekStart",
        "Year",
        "Week",
        "Area",
        "Population",
        "Respiratory_rate_per_10000",
        "Cardiocirculatory_rate_per_10000",
        "NO2_population_weighted_mean",
        "PM25_population_weighted_mean",
        "TimeLabel",
    ]

    missing_columns = [
        col for col in required_columns
        if col not in integrated.columns
    ]

    if missing_columns:
        errors.append(
            "Missing columns in weekly integrated dataset:\n"
            f"{missing_columns}"
        )

    missing_values = integrated[required_columns].isna().sum()
    missing_values = missing_values[missing_values > 0]

    if len(missing_values) > 0:
        errors.append(
            "Missing values found in weekly integrated dataset:\n"
            f"{missing_values.to_string()}"
        )

    if errors:
        raise ValueError(
            "\nWEEKLY INTEGRATED DATASET VALIDATION FAILED\n\n"
            + "\n\n".join(errors)
        )

    print("\nWeekly integrated dataset validation passed.")
    print(f"Weekly rows: {len(integrated)} / expected {expected_rows}")
    print("Rows by area:")
    print(integrated["Area"].value_counts())


def expected_valid_lag_count(time_values, lag, lag_unit):
    """
    Compute how many valid lagged values are expected for a given time series.

    This is based on exact temporal distance, so it respects the 2019-2023 gap.
    """

    time_series = pd.Series(
        pd.to_datetime(sorted(pd.Series(time_values).dropna().unique()))
    )

    if lag == 0:
        return len(time_series)

    if lag_unit == "months":
        time_idx = month_index(time_series)
    elif lag_unit == "weeks":
        time_idx = week_index(time_series)
    else:
        raise ValueError(f"Unknown lag unit: {lag_unit}")

    lagged_time_idx = time_idx.shift(lag)

    valid_lag = (time_idx - lagged_time_idx) == lag

    return int(valid_lag.sum())


def validate_lagged_dataset(lagged, lags, lag_unit, time_col):
    """
    Validate lagged pollutant columns.

    The check confirms that the number of non-missing lagged values matches
    the expected number after excluding invalid lags across temporal gaps.
    """

    errors = []

    for area in AREA_ORDER:
        area_data = lagged[lagged["Area"] == area].copy()

        if area_data.empty:
            errors.append(f"No lagged rows found for area: {area}.")
            continue

        for lag in lags:
            expected_count = expected_valid_lag_count(
                time_values=area_data[time_col],
                lag=lag,
                lag_unit=lag_unit
            )

            for pollutant_col in POLLUTANT_COLUMNS:
                lag_col = f"{pollutant_col}_lag{lag}"
                lag_date_col = f"{pollutant_col}_lag{lag}_{time_col}"

                if lag_col not in lagged.columns:
                    errors.append(f"Missing lag column: {lag_col}")
                    continue

                observed_count = int(area_data[lag_col].notna().sum())

                if observed_count != expected_count:
                    errors.append(
                        f"{area}, {pollutant_col}, lag {lag} {lag_unit}: "
                        f"expected {expected_count} valid lagged values, "
                        f"found {observed_count}."
                    )

                if lag_date_col in lagged.columns:
                    invalid_date_rows = area_data[
                        area_data[lag_col].notna()
                        & area_data[lag_date_col].isna()
                    ].copy()

                    if len(invalid_date_rows) > 0:
                        errors.append(
                            f"{area}, {pollutant_col}, lag {lag} {lag_unit}: "
                            f"some non-missing lagged values have missing lag dates."
                        )

    if errors:
        raise ValueError(
            f"\n{lag_unit.upper()} LAGGED DATASET VALIDATION FAILED\n\n"
            + "\n\n".join(errors)
        )

    print(f"\n{lag_unit.capitalize()} lagged dataset validation passed.")
    print("Lagged values are consistent with exact temporal-distance checks.")


# ============================================================
# MONTHLY DATA LOADING AND STANDARDIZATION
# ============================================================

def load_modaria_monthly_integrated_dataset():
    """
    Load the monthly integrated dataset produced in Part 4.3.

    Each row represents:
    MonthPeriod × Area
    """

    data = read_project_csv(MONTHLY_INPUT_PATH)

    month_period_col = find_column(
        data,
        possible_names=["MonthPeriod", "Month_Period", "Month period"],
        required=True
    )

    year_col = find_column(data, ["Year", "YEAR"], required=True)
    month_col = find_column(data, ["Month", "MONTH"], required=True)
    season_col = find_column(data, ["Season", "SEASON"], required=True)
    area_col = find_column(data, ["Area", "StudyArea", "Study_area"], required=True)
    population_col = find_column(data, ["Population", "POPULATION"], required=True)

    respiratory_col = find_column(
        data,
        ["Respiratory_rate_per_10000", "Respiratory rate per 10000", "Respiratory"],
        required=True
    )

    cardiocirculatory_col = find_column(
        data,
        [
            "Cardiocirculatory_rate_per_10000",
            "Cardiocirculatory rate per 10000",
            "Cardiocirculatory",
        ],
        required=True
    )

    no2_col = find_column(
        data,
        [
            "NO2_population_weighted_mean",
            "NO2_Population_weighted_mean",
            "NO2_population_weighted",
            "NO2_mean",
        ],
        required=True
    )

    pm25_col = find_column(
        data,
        [
            "PM25_population_weighted_mean",
            "PM2.5_population_weighted_mean",
            "PM25_Population_weighted_mean",
            "PM25_population_weighted",
            "PM25_mean",
        ],
        required=True
    )

    time_label_col = find_column(
        data,
        ["TimeLabel", "Time_label", "Label"],
        required=False
    )

    standardized = data.copy()

    standardized = standardized.rename(
        columns={
            month_period_col: "MonthPeriod",
            year_col: "Year",
            month_col: "Month",
            season_col: "Season",
            area_col: "Area",
            population_col: "Population",
            respiratory_col: "Respiratory_rate_per_10000",
            cardiocirculatory_col: "Cardiocirculatory_rate_per_10000",
            no2_col: "NO2_population_weighted_mean",
            pm25_col: "PM25_population_weighted_mean",
        }
    )

    if time_label_col is not None and time_label_col in standardized.columns:
        standardized = standardized.rename(columns={time_label_col: "TimeLabel"})

    standardized["MonthPeriod"] = pd.to_datetime(
        standardized["MonthPeriod"],
        errors="coerce"
    )

    standardized["Year"] = pd.to_numeric(standardized["Year"], errors="coerce")
    standardized["Month"] = pd.to_numeric(standardized["Month"], errors="coerce")
    standardized["Area"] = standardized["Area"].apply(clean_text)

    numeric_columns = ["Population"] + POLLUTANT_COLUMNS + OUTCOME_COLUMNS

    for col in numeric_columns:
        standardized[col] = pd.to_numeric(standardized[col], errors="coerce")

    standardized = standardized[
        standardized["Year"].isin(COMMON_YEARS)
        & standardized["Area"].isin(AREA_ORDER)
        & standardized["MonthPeriod"].notna()
    ].copy()

    if "TimeLabel" not in standardized.columns:
        standardized["TimeLabel"] = standardized["MonthPeriod"].dt.strftime("%Y-%m")

    standardized = standardized.sort_values(
        ["Area", "MonthPeriod"]
    ).reset_index(drop=True)

    required_columns = [
        "MonthPeriod",
        "Year",
        "Month",
        "Season",
        "Area",
        "Population",
        "Respiratory_rate_per_10000",
        "Cardiocirculatory_rate_per_10000",
        "NO2_population_weighted_mean",
        "PM25_population_weighted_mean",
        "TimeLabel",
    ]

    missing_columns = [col for col in required_columns if col not in standardized.columns]

    if missing_columns:
        raise ValueError(
            f"Missing columns after standardization: {missing_columns}\n"
            f"Available columns: {standardized.columns.tolist()}"
        )

    return standardized[required_columns]


# ============================================================
# MONTHLY LAG CONSTRUCTION
# ============================================================

def add_validated_monthly_lags_for_area(area_data):
    """
    Add lagged pollutant columns for one study area.

    Lagged values are kept only if the lagged month is exactly
    lag months before the current month.
    """

    area_data = area_data.sort_values("MonthPeriod").copy()
    current_month_index = month_index(area_data["MonthPeriod"])

    for lag in MONTHLY_LAGS:
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


def build_monthly_lagged_dataset(data):
    """
    Build the monthly lagged dataset.
    """

    lagged_parts = []

    for area in AREA_ORDER:
        area_data = data[data["Area"] == area].copy()

        if area_data.empty:
            raise ValueError(f"No rows found for area: {area}")

        lagged_parts.append(add_validated_monthly_lags_for_area(area_data))

    lagged = pd.concat(lagged_parts, ignore_index=True)

    lagged = lagged.sort_values(
        ["MonthPeriod", "Area"]
    ).reset_index(drop=True)

    return lagged


# ============================================================
# WEEKLY DATA LOADING AND STANDARDIZATION
# ============================================================

def load_modaria_daily_area_exposure():
    """
    Load the daily ModAria area exposure dataset produced in Part 4.2.

    Expected structure:
    Date × Area × Pollutant

    The function pivots NO2 and PM2.5 into separate population-weighted
    exposure columns.
    """

    daily = read_project_csv(DAILY_MODARIA_INPUT_PATH)

    date_col = find_column(daily, ["Date", "Data", "DATE"], required=True)
    area_col = find_column(daily, ["Area", "StudyArea", "Study_area"], required=True)
    pollutant_col = find_column(daily, ["Pollutant", "POLLUTANT"], required=True)
    exposure_col = find_column(
        daily,
        ["Population_weighted_mean", "population_weighted_mean"],
        required=True
    )

    daily = daily.copy()
    daily["Date"] = pd.to_datetime(daily[date_col], errors="coerce")
    daily["Area"] = daily[area_col].apply(clean_text)
    daily["Pollutant"] = daily[pollutant_col].apply(clean_text)
    daily["Population_weighted_mean"] = pd.to_numeric(
        daily[exposure_col],
        errors="coerce"
    )

    daily = daily[
        daily["Date"].notna()
        & daily["Area"].isin(AREA_ORDER)
        & daily["Pollutant"].isin(["NO2", "PM25", "PM2.5"])
    ].copy()

    daily["Pollutant"] = daily["Pollutant"].replace({"PM2.5": "PM25"})
    daily["Year"] = daily["Date"].dt.year
    daily = daily[daily["Year"].isin(COMMON_YEARS)].copy()

    daily_wide = daily.pivot_table(
        index=["Date", "Area"],
        columns="Pollutant",
        values="Population_weighted_mean",
        aggfunc="mean"
    ).reset_index()

    daily_wide.columns.name = None

    daily_wide = daily_wide.rename(
        columns={
            "NO2": "NO2_population_weighted_mean",
            "PM25": "PM25_population_weighted_mean",
        }
    )

    for col in POLLUTANT_COLUMNS:
        if col not in daily_wide.columns:
            raise ValueError(
                f"Missing pollutant column after daily ModAria pivot: {col}\n"
                f"Available columns: {daily_wide.columns.tolist()}"
            )

    daily_wide = daily_wide.sort_values(
        ["Date", "Area"]
    ).reset_index(drop=True)

    return daily_wide[["Date", "Area"] + POLLUTANT_COLUMNS]


def build_weekly_modaria_exposure():
    """
    Aggregate daily ModAria exposure to weekly means.

    Each row represents:
    WeekStart × Area
    """

    daily = load_modaria_daily_area_exposure()
    daily = add_week_columns(daily, date_col="Date")

    weekly = (
        daily
        .groupby(["WeekStart", "Year", "Week", "Area"], as_index=False)[POLLUTANT_COLUMNS]
        .mean()
    )

    weekly["TimeLabel"] = weekly["WeekStart"].dt.strftime("%Y-%m-%d")

    weekly = weekly.sort_values(
        ["WeekStart", "Area"]
    ).reset_index(drop=True)

    return weekly


def load_population_denominators():
    """
    Load annual population denominators by Year × Area.
    """

    population = read_project_csv(ANNUAL_HEALTH_RATES_PATH)

    year_col = find_column(population, ["Year", "YEAR"], required=True)
    area_col = find_column(population, ["Area", "StudyArea", "Study_area"], required=True)
    population_col = find_column(population, ["Population", "POPULATION"], required=True)

    population = population.copy()
    population["Year"] = pd.to_numeric(population[year_col], errors="coerce")
    population["Area"] = population[area_col].apply(clean_text)
    population["Population"] = pd.to_numeric(population[population_col], errors="coerce")

    population = (
        population[["Year", "Area", "Population"]]
        .drop_duplicates()
        .dropna()
        .copy()
    )

    population = population[
        population["Year"].isin(COMMON_YEARS)
        & population["Area"].isin(AREA_ORDER)
    ].copy()

    return population


def load_selected_health_events():
    """
    Load selected health events produced in Part 2.2.

    Expected minimum columns:
    - one date column;
    - Area;
    - Outcome.
    """

    health = read_project_csv(HEALTH_SELECTED_EVENTS_PATH)

    date_col = find_column(
        health,
        [
            "Date",
            "Data",
            "EventDate",
            "Event_Date",
            "EVENT_DATE",
            "DATE",
            "Data_evento",
            "DATA_EVENTO",
        ],
        required=True
    )

    area_col = find_column(
        health,
        ["Area", "StudyArea", "Study_area", "STUDY_AREA"],
        required=True
    )

    outcome_col = find_column(
        health,
        ["Outcome", "HealthOutcome", "Health_outcome", "TYPE_DTL", "TYPE"],
        required=True
    )

    health = health.copy()
    health["EventDate"] = parse_project_date(health[date_col])
    health["Area"] = health[area_col].apply(clean_text)
    health["Outcome"] = health[outcome_col].apply(standardize_outcome)

    health = health[
        health["Area"].isin(AREA_ORDER)
        & health["Outcome"].isin(OUTCOME_ORDER)
        & health["EventDate"].notna()
    ].copy()

    health = health[
        health["EventDate"].dt.year.isin(COMMON_YEARS)
    ].copy()

    return health[["EventDate", "Area", "Outcome"]]


def build_weekly_health_rates(weekly_time_area_grid):
    """
    Build weekly health rates by WeekStart × Area.

    Missing weekly event counts are explicitly set to zero.
    """

    health = load_selected_health_events()
    health = add_week_columns(health, date_col="EventDate")

    weekly_counts = (
        health
        .groupby(["WeekStart", "Year", "Week", "Area", "Outcome"], as_index=False)
        .size()
        .rename(columns={"size": "N_events"})
    )

    grid_rows = []

    for _, row in weekly_time_area_grid.iterrows():
        for outcome in OUTCOME_ORDER:
            grid_rows.append({
                "WeekStart": row["WeekStart"],
                "Year": row["Year"],
                "Week": row["Week"],
                "Area": row["Area"],
                "Outcome": outcome,
            })

    grid = pd.DataFrame(grid_rows)

    weekly = grid.merge(
        weekly_counts,
        on=["WeekStart", "Year", "Week", "Area", "Outcome"],
        how="left"
    )

    weekly["N_events"] = weekly["N_events"].fillna(0).astype(int)

    population = load_population_denominators()

    weekly = weekly.merge(
        population,
        on=["Year", "Area"],
        how="left"
    )

    weekly["Rate_per_10000"] = (
        weekly["N_events"] / weekly["Population"] * 10000
    )

    weekly_wide = weekly.pivot_table(
        index=["WeekStart", "Year", "Week", "Area", "Population"],
        columns="Outcome",
        values="Rate_per_10000",
        aggfunc="first"
    ).reset_index()

    weekly_wide.columns.name = None

    weekly_wide = weekly_wide.rename(
        columns={
            "Respiratory": "Respiratory_rate_per_10000",
            "Cardiocirculatory": "Cardiocirculatory_rate_per_10000",
        }
    )

    weekly_wide["TimeLabel"] = weekly_wide["WeekStart"].dt.strftime("%Y-%m-%d")

    weekly_wide = weekly_wide.sort_values(
        ["WeekStart", "Area"]
    ).reset_index(drop=True)

    return weekly_wide


def build_weekly_integrated_dataset():
    """
    Build the weekly ModAria environmental-health integrated dataset.

    Each row represents:
    WeekStart × Area
    """

    weekly_exposure = build_weekly_modaria_exposure()

    weekly_exposure.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_weekly_exposure_prepared_for_lag_analysis.csv"),
        index=False,
        sep=";"
    )

    weekly_time_area_grid = (
        weekly_exposure[["WeekStart", "Year", "Week", "Area"]]
        .drop_duplicates()
        .copy()
    )

    weekly_health = build_weekly_health_rates(weekly_time_area_grid)

    weekly_health.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_weekly_health_rates_prepared_for_lag_analysis.csv"),
        index=False,
        sep=";"
    )

    integrated = weekly_health.merge(
        weekly_exposure,
        on=["WeekStart", "Year", "Week", "Area"],
        how="left"
    )

    integrated = integrated.sort_values(
        ["WeekStart", "Area"]
    ).reset_index(drop=True)

    required_columns = [
        "WeekStart",
        "Year",
        "Week",
        "Area",
        "Population",
        "Respiratory_rate_per_10000",
        "Cardiocirculatory_rate_per_10000",
        "NO2_population_weighted_mean",
        "PM25_population_weighted_mean",
        "TimeLabel_x",
    ]

    if "TimeLabel_x" in integrated.columns:
        integrated = integrated.rename(columns={"TimeLabel_x": "TimeLabel"})

    if "TimeLabel_y" in integrated.columns:
        integrated = integrated.drop(columns=["TimeLabel_y"])

    final_columns = [
        "WeekStart",
        "Year",
        "Week",
        "Area",
        "Population",
        "Respiratory_rate_per_10000",
        "Cardiocirculatory_rate_per_10000",
        "NO2_population_weighted_mean",
        "PM25_population_weighted_mean",
        "TimeLabel",
    ]

    missing_columns = [col for col in final_columns if col not in integrated.columns]

    if missing_columns:
        raise ValueError(
            f"Missing columns in weekly integrated dataset: {missing_columns}\n"
            f"Available columns: {integrated.columns.tolist()}"
        )

    return integrated[final_columns]


# ============================================================
# WEEKLY LAG CONSTRUCTION
# ============================================================

def add_validated_weekly_lags_for_area(area_data):
    """
    Add lagged pollutant columns for one study area.

    Lagged values are kept only if the lagged week is exactly
    lag weeks before the current week.
    """

    area_data = area_data.sort_values("WeekStart").copy()
    current_week_index = week_index(area_data["WeekStart"])

    for lag in WEEKLY_LAGS:
        for pollutant_col in POLLUTANT_COLUMNS:
            lag_col = f"{pollutant_col}_lag{lag}"
            lag_date_col = f"{pollutant_col}_lag{lag}_WeekStart"

            if lag == 0:
                area_data[lag_col] = area_data[pollutant_col]
                area_data[lag_date_col] = area_data["WeekStart"]
            else:
                area_data[lag_col] = area_data[pollutant_col].shift(lag)
                area_data[lag_date_col] = area_data["WeekStart"].shift(lag)

                lagged_week_index = week_index(area_data[lag_date_col])
                week_difference = current_week_index - lagged_week_index
                valid_lag = week_difference == lag

                area_data.loc[~valid_lag, lag_col] = pd.NA
                area_data.loc[~valid_lag, lag_date_col] = pd.NaT

    return area_data


def build_weekly_lagged_dataset(integrated):
    """
    Build the weekly lagged dataset.
    """

    lagged_parts = []

    for area in AREA_ORDER:
        area_data = integrated[integrated["Area"] == area].copy()

        if area_data.empty:
            raise ValueError(f"No rows found for area: {area}")

        lagged_parts.append(add_validated_weekly_lags_for_area(area_data))

    lagged = pd.concat(lagged_parts, ignore_index=True)

    lagged = lagged.sort_values(
        ["WeekStart", "Area"]
    ).reset_index(drop=True)

    return lagged


# ============================================================
# SHARED LAG ANALYSIS FUNCTIONS
# ============================================================

def summarize_lag_availability(lagged, lags, lag_unit):
    """
    Count available non-missing lagged values for each lag, pollutant and area.
    """

    rows = []
    groups = ["Overall"] + AREA_ORDER

    lag_column_name = f"Lag_{lag_unit}"

    for group in groups:
        if group == "Overall":
            subset = lagged.copy()
        else:
            subset = lagged[lagged["Area"] == group].copy()

        for pollutant_col in POLLUTANT_COLUMNS:
            for lag in lags:
                lag_col = f"{pollutant_col}_lag{lag}"

                rows.append({
                    "Group": group,
                    "Pollutant": pollutant_col,
                    "Pollutant_label": get_variable_label(pollutant_col),
                    lag_column_name: lag,
                    "Available_values": int(subset[lag_col].notna().sum()),
                    "Missing_values": int(subset[lag_col].isna().sum()),
                })

    return pd.DataFrame(rows)


def compute_lagged_spearman_correlations(lagged, lags, lag_unit):
    """
    Compute Spearman correlations between lagged pollutant indicators
    and current health event rates.
    """

    rows = []
    groups = ["Overall"] + AREA_ORDER
    lag_column_name = f"Lag_{lag_unit}"

    for group in groups:
        if group == "Overall":
            subset = lagged.copy()
        else:
            subset = lagged[lagged["Area"] == group].copy()

        for pollutant_col in POLLUTANT_COLUMNS:
            for outcome_col in OUTCOME_COLUMNS:
                for lag in lags:
                    lag_col = f"{pollutant_col}_lag{lag}"

                    temp = subset[[lag_col, outcome_col]].dropna()
                    n = len(temp)

                    if n < 3:
                        rho = None
                        p_value = None
                    else:
                        rho, p_value = spearmanr(temp[lag_col], temp[outcome_col])

                    rows.append({
                        "Group": group,
                        "Pollutant": pollutant_col,
                        "Pollutant_label": get_variable_label(pollutant_col),
                        "Outcome": outcome_col,
                        "Outcome_label": get_variable_label(outcome_col),
                        lag_column_name: lag,
                        "N": n,
                        "Spearman_rho": rho,
                        "p_value": p_value,
                        "Interpretation": interpret_spearman_result(rho, p_value),
                    })

    return pd.DataFrame(rows)


def summarize_best_lags(correlation_summary, lag_unit):
    """
    Create a compact best-lag summary.

    Two descriptive criteria are reported:
    - best lag by absolute rho;
    - best lag by positive rho.
    """

    rows = []
    lag_column_name = f"Lag_{lag_unit}"

    grouping_columns = [
        "Group",
        "Pollutant",
        "Pollutant_label",
        "Outcome",
        "Outcome_label",
    ]

    for _, subset in correlation_summary.groupby(grouping_columns):
        subset = subset.dropna(subset=["Spearman_rho"]).copy()

        if subset.empty:
            continue

        subset["abs_rho"] = subset["Spearman_rho"].abs()

        best_abs = subset.sort_values(
            ["abs_rho", lag_column_name],
            ascending=[False, True]
        ).iloc[0]

        best_positive = subset.sort_values(
            ["Spearman_rho", lag_column_name],
            ascending=[False, True]
        ).iloc[0]

        lag0 = subset[subset[lag_column_name] == 0].copy()

        if lag0.empty:
            lag0_rho = None
            lag0_p_value = None
        else:
            lag0_rho = lag0.iloc[0]["Spearman_rho"]
            lag0_p_value = lag0.iloc[0]["p_value"]

        lag0_is_best_abs = bool(best_abs[lag_column_name] == 0)
        lag0_is_best_positive = bool(best_positive[lag_column_name] == 0)

        rows.append({
            "Group": best_abs["Group"],
            "Pollutant": best_abs["Pollutant"],
            "Pollutant_label": best_abs["Pollutant_label"],
            "Outcome": best_abs["Outcome"],
            "Outcome_label": best_abs["Outcome_label"],
            "Lag0_Spearman_rho": lag0_rho,
            "Lag0_p_value": lag0_p_value,
            f"Best_lag_by_abs_rho_{lag_unit}": int(best_abs[lag_column_name]),
            "Best_abs_Spearman_rho": best_abs["Spearman_rho"],
            "Best_abs_p_value": best_abs["p_value"],
            f"Best_lag_by_positive_rho_{lag_unit}": int(best_positive[lag_column_name]),
            "Best_positive_Spearman_rho": best_positive["Spearman_rho"],
            "Best_positive_p_value": best_positive["p_value"],
            "Lag0_is_best_abs_rho": lag0_is_best_abs,
            "Lag0_is_best_positive_rho": lag0_is_best_positive,
            "N_at_best_abs_lag": int(best_abs["N"]),
            "N_at_best_positive_lag": int(best_positive["N"]),
            "Caution": (
                "Best lags are selected descriptively from Spearman correlations. "
                "They should not be interpreted as causal delays."
            ),
        })

    return pd.DataFrame(rows)


def summarize_lag0_dominance(best_lag_summary, temporal_scale):
    """
    Summarize how often lag 0 is the strongest association.
    """

    total_comparisons = len(best_lag_summary)

    if total_comparisons == 0:
        lag0_positive_count = 0
        lag0_abs_count = 0
        lag0_positive_percentage = None
        lag0_abs_percentage = None
    else:
        lag0_positive_count = int(best_lag_summary["Lag0_is_best_positive_rho"].sum())
        lag0_abs_count = int(best_lag_summary["Lag0_is_best_abs_rho"].sum())
        lag0_positive_percentage = lag0_positive_count / total_comparisons * 100
        lag0_abs_percentage = lag0_abs_count / total_comparisons * 100

    if temporal_scale == "Monthly":
        decision_rule = (
            "If most relevant positive associations peak at lag 0 months, "
            "a weekly refinement can be useful to check whether the same-month "
            "signal hides shorter delays of 1-2 weeks."
        )
    else:
        decision_rule = (
            "Weekly lag results refine the interpretation of same-month patterns. "
            "They remain exploratory and should not be interpreted as causal delays."
        )

    return pd.DataFrame({
        "Indicator": [
            "Temporal scale",
            "Number of pollutant-outcome-group combinations",
            "Combinations where lag 0 is strongest positive rho",
            "Percentage where lag 0 is strongest positive rho",
            "Combinations where lag 0 is strongest absolute rho",
            "Percentage where lag 0 is strongest absolute rho",
            "Suggested decision rule",
        ],
        "Value": [
            temporal_scale,
            total_comparisons,
            lag0_positive_count,
            lag0_positive_percentage,
            lag0_abs_count,
            lag0_abs_percentage,
            decision_rule,
        ]
    })


# ============================================================
# PLOTTING FUNCTIONS
# ============================================================

def plot_rho_vs_lag(correlation_summary, lags, lag_unit, temporal_scale):
    """
    Plot Spearman rho as a function of lag.
    """

    lag_column_name = f"Lag_{lag_unit}"

    for group in ["Overall"] + AREA_ORDER:
        for pollutant_col in POLLUTANT_COLUMNS:
            for outcome_col in OUTCOME_COLUMNS:
                subset = correlation_summary[
                    (correlation_summary["Group"] == group)
                    & (correlation_summary["Pollutant"] == pollutant_col)
                    & (correlation_summary["Outcome"] == outcome_col)
                ].copy()

                subset = subset.sort_values(lag_column_name)

                pollutant_label = get_variable_label(pollutant_col, temporal_scale)
                outcome_label = get_variable_label(outcome_col)

                plt.figure(figsize=(7, 5))

                plt.plot(
                    subset[lag_column_name],
                    subset["Spearman_rho"],
                    marker="o"
                )

                plt.axhline(y=0, linestyle="--", linewidth=1)
                plt.xticks(lags)

                plt.title(
                    f"ModAria {temporal_scale.lower()} lag analysis - {group}\n"
                    f"{pollutant_label} vs {outcome_label}"
                )

                plt.xlabel(f"Lag in {lag_unit}")
                plt.ylabel("Spearman rho")
                plt.grid(True, alpha=0.3)
                plt.tight_layout()

                filename = (
                    f"modaria_{temporal_scale.lower()}_rho_vs_lag_"
                    f"{safe_filename(group)}_"
                    f"{safe_filename(pollutant_col)}_vs_"
                    f"{safe_filename(outcome_col)}.png"
                )

                plt.savefig(os.path.join(PLOTS_DIR, filename), dpi=300)
                plt.close()


def plot_best_lag_scatter(lagged, best_lag_summary, lag_unit, temporal_scale, time_col):
    """
    Create scatter plots for the descriptively strongest positive lag
    of each group, pollutant and outcome.
    """

    best_lag_col = f"Best_lag_by_positive_rho_{lag_unit}"

    for _, row in best_lag_summary.iterrows():
        group = row["Group"]
        pollutant_col = row["Pollutant"]
        outcome_col = row["Outcome"]
        lag = int(row[best_lag_col])
        lag_col = f"{pollutant_col}_lag{lag}"

        if group == "Overall":
            subset = lagged.copy()
        else:
            subset = lagged[lagged["Area"] == group].copy()

        subset = subset[[lag_col, outcome_col, "Area"]].dropna().copy()

        if subset.empty:
            continue

        pollutant_label = get_variable_label(pollutant_col, temporal_scale)
        outcome_label = get_variable_label(outcome_col)
        rho = row["Best_positive_Spearman_rho"]
        p_value = row["Best_positive_p_value"]

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
            f"Best positive {temporal_scale.lower()} lag scatter - {group}\n"
            f"{pollutant_label} lag {lag} vs {outcome_label}\n"
            f"Spearman rho = {rho:.3f}, p = {p_value:.3g}"
        )

        plt.xlabel(f"{get_variable_unit(pollutant_col)} - lag {lag} {lag_unit}")
        plt.ylabel(get_variable_unit(outcome_col))
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        filename = (
            f"modaria_{temporal_scale.lower()}_best_positive_lag_scatter_"
            f"{safe_filename(group)}_"
            f"{safe_filename(pollutant_col)}_lag{lag}_vs_"
            f"{safe_filename(outcome_col)}.png"
        )

        plt.savefig(os.path.join(PLOTS_DIR, filename), dpi=300)
        plt.close()


def plot_overall_lag_summary(correlation_summary, lags, lag_unit, temporal_scale):
    """
    Produce a compact summary plot for the overall lag results.
    """

    subset = correlation_summary[correlation_summary["Group"] == "Overall"].copy()
    subset = subset.sort_values(f"Lag_{lag_unit}")
    lag_column_name = f"Lag_{lag_unit}"

    plt.figure(figsize=(9, 6))

    for pollutant_col in POLLUTANT_COLUMNS:
        for outcome_col in OUTCOME_COLUMNS:
            temp = subset[
                (subset["Pollutant"] == pollutant_col)
                & (subset["Outcome"] == outcome_col)
            ].copy()

            label = (
                f"{get_variable_label(pollutant_col)} vs "
                f"{get_variable_label(outcome_col)}"
            )

            plt.plot(
                temp[lag_column_name],
                temp["Spearman_rho"],
                marker="o",
                label=label
            )

    plt.axhline(y=0, linestyle="--", linewidth=1)
    plt.xticks(lags)
    plt.xlabel(f"Lag in {lag_unit}")
    plt.ylabel("Spearman rho")
    plt.title(f"ModAria {temporal_scale.lower()} lag summary - Overall")
    plt.legend(fontsize=8)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        os.path.join(PLOTS_DIR, f"modaria_{temporal_scale.lower()}_lag_summary_overall.png"),
        dpi=300
    )

    plt.close()


def plot_best_lag_summary(best_lag_summary, lag_unit, temporal_scale):
    """
    Produce a compact plot showing the strongest positive lagged association
    for each pollutant-outcome-group combination.
    """

    plot_data = best_lag_summary.copy()

    if plot_data.empty:
        return

    best_lag_col = f"Best_lag_by_positive_rho_{lag_unit}"

    plot_data["Combination"] = (
        plot_data["Group"]
        + " | "
        + plot_data["Pollutant_label"].str.replace("Population-weighted ", "", regex=False)
        + " | "
        + plot_data["Outcome_label"].str.replace(" acute event rate", "", regex=False)
    )

    plot_data = plot_data.sort_values(
        ["Group", "Pollutant", "Outcome"]
    ).reset_index(drop=True)

    x_positions = range(len(plot_data))

    plt.figure(figsize=(12, 6))

    plt.scatter(x_positions, plot_data["Best_positive_Spearman_rho"])
    plt.axhline(y=0, linestyle="--", linewidth=1)

    for x, (_, row) in zip(x_positions, plot_data.iterrows()):
        plt.text(
            x,
            row["Best_positive_Spearman_rho"],
            f"L{int(row[best_lag_col])}",
            ha="center",
            va="bottom",
            fontsize=8
        )

    plt.xticks(
        ticks=list(x_positions),
        labels=plot_data["Combination"],
        rotation=75,
        ha="right"
    )

    plt.ylabel("Best positive Spearman rho")
    plt.title(f"ModAria {temporal_scale.lower()} lag analysis - Best positive lag summary")
    plt.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        os.path.join(PLOTS_DIR, f"modaria_{temporal_scale.lower()}_best_positive_lag_summary.png"),
        dpi=300
    )

    plt.close()


def plot_monthly_vs_weekly_overall_summary(monthly_summary, weekly_summary):
    """
    Produce a compact comparison plot between overall monthly and weekly lag curves.

    This is a descriptive visual aid only. Monthly and weekly lags are shown on
    different x-axis labels because they are different temporal units.
    """

    if monthly_summary is None or weekly_summary is None:
        return

    monthly = monthly_summary[monthly_summary["Group"] == "Overall"].copy()
    weekly = weekly_summary[weekly_summary["Group"] == "Overall"].copy()

    rows = []

    for _, row in monthly.iterrows():
        rows.append({
            "Temporal_scale": "Monthly",
            "Lag_label": f"M{int(row['Lag_months'])}",
            "Combination": f"{row['Pollutant_label']} vs {row['Outcome_label']}",
            "Spearman_rho": row["Spearman_rho"],
        })

    for _, row in weekly.iterrows():
        rows.append({
            "Temporal_scale": "Weekly",
            "Lag_label": f"W{int(row['Lag_weeks'])}",
            "Combination": f"{row['Pollutant_label']} vs {row['Outcome_label']}",
            "Spearman_rho": row["Spearman_rho"],
        })

    plot_data = pd.DataFrame(rows)

    if plot_data.empty:
        return

    for combination in sorted(plot_data["Combination"].unique()):
        subset = plot_data[plot_data["Combination"] == combination].copy()

        plt.figure(figsize=(9, 5))

        for scale in ["Monthly", "Weekly"]:
            temp = subset[subset["Temporal_scale"] == scale].copy()
            x_positions = range(len(temp))
            plt.plot(
                list(x_positions),
                temp["Spearman_rho"],
                marker="o",
                label=scale
            )

            for x, (_, row) in zip(x_positions, temp.iterrows()):
                plt.text(
                    x,
                    row["Spearman_rho"],
                    row["Lag_label"],
                    ha="center",
                    va="bottom",
                    fontsize=8
                )

        plt.axhline(y=0, linestyle="--", linewidth=1)
        plt.ylabel("Spearman rho")
        plt.xlabel("Lag order within each temporal scale")
        plt.title(f"Monthly vs weekly lag comparison - Overall\n{combination}")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        filename = (
            "modaria_monthly_vs_weekly_overall_"
            f"{safe_filename(combination)}.png"
        )

        plt.savefig(os.path.join(PLOTS_DIR, filename), dpi=300)
        plt.close()


# ============================================================
# SUMMARY TABLES
# ============================================================

def summarize_lag_analysis(lagged, correlation_summary, best_lag_summary, lags, lag_unit, temporal_scale, input_description):
    """
    Create a compact descriptive summary of a lag analysis.
    """

    lag_column_name = f"Lag_{lag_unit}"
    lag0_count = int(best_lag_summary["Lag0_is_best_positive_rho"].sum())
    total_count = len(best_lag_summary)

    if total_count > 0:
        lag0_percentage = lag0_count / total_count * 100
    else:
        lag0_percentage = None

    max_n_by_lag = []

    for lag in lags:
        max_n = int(correlation_summary[correlation_summary[lag_column_name] == lag]["N"].max())
        max_n_by_lag.append(f"Lag {lag}: {max_n}")

    summary = pd.DataFrame({
        "Indicator": [
            "Input dataset/source",
            "Temporal scale",
            "Exposure source",
            "Exposure indicator",
            "Lag values tested",
            "Number of rows in lagged dataset",
            "Number of areas",
            "Areas",
            "Pollutants",
            "Health outcomes",
            "Correlation method",
            "Maximum N by lag",
            "Combinations where lag 0 is strongest positive rho",
            "Percentage where lag 0 is strongest positive rho",
            "Main methodological safeguard",
            "Main interpretation rule",
        ],
        "Value": [
            input_description,
            temporal_scale,
            "ModAria municipality-level area exposure",
            "Population-weighted mean",
            ", ".join(map(str, lags)),
            len(lagged),
            lagged["Area"].nunique(),
            ", ".join(AREA_ORDER),
            "NO2, PM2.5",
            "Respiratory and cardiocirculatory event rates",
            "Spearman correlation",
            "; ".join(max_n_by_lag),
            lag0_count,
            lag0_percentage,
            (
                f"Lagged pollutant values are kept only when the lagged {lag_unit[:-1]} "
                f"is exactly the expected number of {lag_unit} before the current health "
                f"{lag_unit[:-1]}. This prevents incorrect links across the 2019-2023 gap."
            ),
            (
                "Lagged correlations are exploratory ecological associations. "
                "They should not be interpreted as causal delayed effects."
            ),
        ]
    })

    return summary


def create_combined_monthly_weekly_summary(monthly_corr, monthly_best, weekly_corr, weekly_best):
    """
    Create one compact CSV that combines monthly and weekly lag outputs.
    """

    outputs = []

    if monthly_corr is not None:
        temp = monthly_corr.copy()
        temp = temp.rename(columns={"Lag_months": "Lag"})
        temp["Temporal_scale"] = "Monthly"
        temp["Lag_unit"] = "months"
        outputs.append(temp)

    if weekly_corr is not None:
        temp = weekly_corr.copy()
        temp = temp.rename(columns={"Lag_weeks": "Lag"})
        temp["Temporal_scale"] = "Weekly"
        temp["Lag_unit"] = "weeks"
        outputs.append(temp)

    if not outputs:
        return pd.DataFrame()

    combined = pd.concat(outputs, ignore_index=True)

    columns = [
        "Temporal_scale",
        "Lag_unit",
        "Group",
        "Pollutant",
        "Pollutant_label",
        "Outcome",
        "Outcome_label",
        "Lag",
        "N",
        "Spearman_rho",
        "p_value",
        "Interpretation",
    ]

    return combined[columns]


# ============================================================
# MONTHLY ANALYSIS RUNNER
# ============================================================

def run_monthly_lag_analysis():
    """
    Run ModAria monthly lag analysis.
    """

    print("\n========================================")
    print("PART 4.4A - MODARIA MONTHLY LAG ANALYSIS")
    print("========================================")

    print("\nInput file:")
    print(MONTHLY_INPUT_PATH)

    data = load_modaria_monthly_integrated_dataset()
    validate_monthly_input_dataset(data)

    data.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_monthly_dataset_prepared_for_lag_analysis.csv"),
        index=False,
        sep=";"
    )

    print("\nInput monthly integrated dataset preview:")
    print(data.head(20))

    print("\nInput dataset shape:")
    print(data.shape)

    print("\nRows by area:")
    print(data["Area"].value_counts())

    print("\nYears included:")
    print(sorted(data["Year"].dropna().unique()))

    print("\nInput missing values check:")
    print(data.isna().sum())

    lagged = build_monthly_lagged_dataset(data)
    validate_lagged_dataset(
        lagged=lagged,
        lags=MONTHLY_LAGS,
        lag_unit="months",
        time_col="MonthPeriod"
    )

    lagged.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_monthly_lag_integrated_dataset.csv"),
        index=False,
        sep=";"
    )

    print("\nLagged monthly dataset preview:")
    print(lagged.head(30))

    print("\nLagged dataset shape:")
    print(lagged.shape)

    print("\nLagged missing values check:")
    print(lagged.isna().sum())

    lag_availability = summarize_lag_availability(
        lagged=lagged,
        lags=MONTHLY_LAGS,
        lag_unit="months"
    )

    lag_availability.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_monthly_lag_availability_check.csv"),
        index=False,
        sep=";"
    )

    print("\nMonthly lag availability check:")
    print(lag_availability)

    correlation_summary = compute_lagged_spearman_correlations(
        lagged=lagged,
        lags=MONTHLY_LAGS,
        lag_unit="months"
    )

    correlation_summary.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_monthly_lag_spearman_summary.csv"),
        index=False,
        sep=";"
    )

    print("\nMonthly lag Spearman correlation summary:")
    print(correlation_summary)

    best_lag_summary = summarize_best_lags(
        correlation_summary=correlation_summary,
        lag_unit="months"
    )

    best_lag_summary.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_monthly_lag_best_lag_summary.csv"),
        index=False,
        sep=";"
    )

    print("\nBest monthly lag summary:")
    print(best_lag_summary)

    lag0_dominance = summarize_lag0_dominance(
        best_lag_summary=best_lag_summary,
        temporal_scale="Monthly"
    )

    lag0_dominance.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_monthly_lag0_dominance_check.csv"),
        index=False,
        sep=";"
    )

    print("\nMonthly lag 0 dominance check:")
    print(lag0_dominance)

    plot_rho_vs_lag(
        correlation_summary=correlation_summary,
        lags=MONTHLY_LAGS,
        lag_unit="months",
        temporal_scale="Monthly"
    )

    plot_best_lag_scatter(
        lagged=lagged,
        best_lag_summary=best_lag_summary,
        lag_unit="months",
        temporal_scale="Monthly",
        time_col="MonthPeriod"
    )

    plot_overall_lag_summary(
        correlation_summary=correlation_summary,
        lags=MONTHLY_LAGS,
        lag_unit="months",
        temporal_scale="Monthly"
    )

    plot_best_lag_summary(
        best_lag_summary=best_lag_summary,
        lag_unit="months",
        temporal_scale="Monthly"
    )

    summary = summarize_lag_analysis(
        lagged=lagged,
        correlation_summary=correlation_summary,
        best_lag_summary=best_lag_summary,
        lags=MONTHLY_LAGS,
        lag_unit="months",
        temporal_scale="Monthly",
        input_description=MONTHLY_INPUT_PATH
    )

    summary.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_monthly_lag_analysis_summary.csv"),
        index=False,
        sep=";"
    )

    print("\nMODARIA MONTHLY LAG ANALYSIS COMPLETED")

    return correlation_summary, best_lag_summary


# ============================================================
# WEEKLY ANALYSIS RUNNER
# ============================================================

def run_weekly_lag_analysis():
    """
    Run ModAria weekly lag analysis.
    """

    print("\n=======================================")
    print("PART 4.4B - MODARIA WEEKLY LAG ANALYSIS")
    print("=======================================")

    print("\nInput daily ModAria file:")
    print(DAILY_MODARIA_INPUT_PATH)

    print("\nInput selected health events file:")
    print(HEALTH_SELECTED_EVENTS_PATH)

    integrated = build_weekly_integrated_dataset()
    validate_weekly_integrated_dataset(integrated)

    integrated.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_weekly_environment_health_integrated_dataset.csv"),
        index=False,
        sep=";"
    )

    print("\nWeekly integrated dataset preview:")
    print(integrated.head(30))

    print("\nWeekly integrated dataset shape:")
    print(integrated.shape)

    print("\nRows by area:")
    print(integrated["Area"].value_counts())

    print("\nYears included:")
    print(sorted(integrated["Year"].dropna().unique()))

    print("\nWeekly integrated missing values check:")
    print(integrated.isna().sum())

    missing_values_summary = integrated.isna().sum().reset_index()
    missing_values_summary.columns = ["Column", "Missing_values"]

    missing_values_summary.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_weekly_missing_values_check.csv"),
        index=False,
        sep=";"
    )

    lagged = build_weekly_lagged_dataset(integrated)
    validate_lagged_dataset(
        lagged=lagged,
        lags=WEEKLY_LAGS,
        lag_unit="weeks",
        time_col="WeekStart"
    )

    lagged.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_weekly_lag_integrated_dataset.csv"),
        index=False,
        sep=";"
    )

    print("\nWeekly lagged dataset preview:")
    print(lagged.head(30))

    print("\nWeekly lagged dataset shape:")
    print(lagged.shape)

    print("\nWeekly lagged missing values check:")
    print(lagged.isna().sum())

    lag_availability = summarize_lag_availability(
        lagged=lagged,
        lags=WEEKLY_LAGS,
        lag_unit="weeks"
    )

    lag_availability.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_weekly_lag_availability_check.csv"),
        index=False,
        sep=";"
    )

    print("\nWeekly lag availability check:")
    print(lag_availability)

    correlation_summary = compute_lagged_spearman_correlations(
        lagged=lagged,
        lags=WEEKLY_LAGS,
        lag_unit="weeks"
    )

    correlation_summary.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_weekly_lag_spearman_summary.csv"),
        index=False,
        sep=";"
    )

    print("\nWeekly lag Spearman correlation summary:")
    print(correlation_summary)

    best_lag_summary = summarize_best_lags(
        correlation_summary=correlation_summary,
        lag_unit="weeks"
    )

    best_lag_summary.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_weekly_lag_best_lag_summary.csv"),
        index=False,
        sep=";"
    )

    print("\nBest weekly lag summary:")
    print(best_lag_summary)

    lag0_dominance = summarize_lag0_dominance(
        best_lag_summary=best_lag_summary,
        temporal_scale="Weekly"
    )

    lag0_dominance.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_weekly_lag0_dominance_check.csv"),
        index=False,
        sep=";"
    )

    print("\nWeekly lag 0 dominance check:")
    print(lag0_dominance)

    plot_rho_vs_lag(
        correlation_summary=correlation_summary,
        lags=WEEKLY_LAGS,
        lag_unit="weeks",
        temporal_scale="Weekly"
    )

    plot_best_lag_scatter(
        lagged=lagged,
        best_lag_summary=best_lag_summary,
        lag_unit="weeks",
        temporal_scale="Weekly",
        time_col="WeekStart"
    )

    plot_overall_lag_summary(
        correlation_summary=correlation_summary,
        lags=WEEKLY_LAGS,
        lag_unit="weeks",
        temporal_scale="Weekly"
    )

    plot_best_lag_summary(
        best_lag_summary=best_lag_summary,
        lag_unit="weeks",
        temporal_scale="Weekly"
    )

    summary = summarize_lag_analysis(
        lagged=lagged,
        correlation_summary=correlation_summary,
        best_lag_summary=best_lag_summary,
        lags=WEEKLY_LAGS,
        lag_unit="weeks",
        temporal_scale="Weekly",
        input_description=(
            DAILY_MODARIA_INPUT_PATH
            + " + "
            + HEALTH_SELECTED_EVENTS_PATH
        )
    )

    summary.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_weekly_lag_analysis_summary.csv"),
        index=False,
        sep=";"
    )

    print("\nMODARIA WEEKLY LAG ANALYSIS COMPLETED")

    return correlation_summary, best_lag_summary


# ============================================================
# MAIN FUNCTION
# ============================================================

def main():
    """
    Run Part 4.4: ModAria monthly and weekly lag analysis.
    """

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(PLOTS_DIR, exist_ok=True)

    print("\n===================================================")
    print("PART 4.4 - MODARIA MONTHLY AND WEEKLY LAG ANALYSIS")
    print("===================================================")

    print("\nOutput folder:")
    print(OUTPUT_DIR)

    monthly_correlation_summary = None
    monthly_best_lag_summary = None
    weekly_correlation_summary = None
    weekly_best_lag_summary = None

    if RUN_MONTHLY_ANALYSIS:
        monthly_correlation_summary, monthly_best_lag_summary = run_monthly_lag_analysis()

    if RUN_WEEKLY_ANALYSIS:
        weekly_correlation_summary, weekly_best_lag_summary = run_weekly_lag_analysis()

    combined_summary = create_combined_monthly_weekly_summary(
        monthly_corr=monthly_correlation_summary,
        monthly_best=monthly_best_lag_summary,
        weekly_corr=weekly_correlation_summary,
        weekly_best=weekly_best_lag_summary
    )

    if not combined_summary.empty:
        combined_summary.to_csv(
            os.path.join(OUTPUT_DIR, "modaria_monthly_weekly_lag_spearman_summary.csv"),
            index=False,
            sep=";"
        )

    if monthly_correlation_summary is not None and weekly_correlation_summary is not None:
        plot_monthly_vs_weekly_overall_summary(
            monthly_summary=monthly_correlation_summary,
            weekly_summary=weekly_correlation_summary
        )

    general_summary = pd.DataFrame({
        "Indicator": [
            "Section",
            "Monthly analysis executed",
            "Weekly analysis executed",
            "Exposure source",
            "Exposure indicator",
            "Correlation method",
            "Main methodological safeguard",
            "Main interpretation rule",
        ],
        "Value": [
            "Part 4.4 - ModAria monthly and weekly lag analysis",
            RUN_MONTHLY_ANALYSIS,
            RUN_WEEKLY_ANALYSIS,
            "ModAria municipality-level area exposure",
            "Population-weighted mean",
            "Spearman correlation",
            "Lagged exposure values are validated to avoid incorrect links across the 2019-2023 temporal gap.",
            "Lagged associations are exploratory ecological correlations and should not be interpreted as causal delays.",
        ]
    })

    general_summary.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_monthly_weekly_lag_analysis_summary.csv"),
        index=False,
        sep=";"
    )

    print("\n===================================================")
    print("MODARIA MONTHLY AND WEEKLY LAG ANALYSIS COMPLETED")
    print("===================================================")
    print(f"Results saved in: {OUTPUT_DIR}")
    print(f"Plots saved in:   {PLOTS_DIR}")


# Alias for consistency with the previous project scripts.
run_modaria_monthly_weekly_lag_analysis = main


if __name__ == "__main__":
    main()
