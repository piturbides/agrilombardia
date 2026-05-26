
import os
import glob
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import spearmanr, pearsonr


# ============================================================
# GLOBAL SETTINGS
# ============================================================

COMMON_YEARS = [2016, 2017, 2018, 2019, 2023]

AREA_ORDER = ["Industrial", "Agricultural"]
SEASON_ORDER = ["Winter", "Spring", "Summer", "Autumn"]
POLLUTANTS = ["NO2", "PM25"]

OUTCOMES = {
    "Respiratory": "Respiratory_rate_per_10000",
    "Cardiocirculatory": "Cardiocirculatory_rate_per_10000",
}

METHODS = {
    "Population_weighted_mean": "Population-weighted area exposure",
    "Arithmetic_mean": "Arithmetic area mean",
}

METHOD_SUFFIX = {
    "Population_weighted_mean": "population_weighted_mean",
    "Arithmetic_mean": "arithmetic_mean",
}

MAIN_METHOD = "Population_weighted_mean"

MODARIA_INPUT_DIR = (
    "Dati/output/4-Modaria exposure/"
    "4.2-Area pollutant comparison"
)

HEALTH_INPUT_DIR = (
    "Dati/output/2-Health data/"
    "2.2-Health event aggregation"
)

OUTPUT_DIR = (
    "Dati/output/4-Modaria exposure/"
    "4.3-Modaria environmental health integration"
)

PLOTS_DIR = os.path.join(OUTPUT_DIR, "plots")


MODARIA_MONTHLY_CANDIDATES = [
    os.path.join(MODARIA_INPUT_DIR, "modaria_monthly_area_exposure_dataset.csv"),
    os.path.join(MODARIA_INPUT_DIR, "monthly_area_exposure_dataset.csv"),
    os.path.join(MODARIA_INPUT_DIR, "modaria_monthly_area_exposure.csv"),
]

MODARIA_SEASONAL_CANDIDATES = [
    os.path.join(MODARIA_INPUT_DIR, "modaria_seasonal_area_exposure_dataset.csv"),
    os.path.join(MODARIA_INPUT_DIR, "seasonal_area_exposure_dataset.csv"),
    os.path.join(MODARIA_INPUT_DIR, "modaria_seasonal_area_exposure.csv"),
]

HEALTH_MONTHLY_CANDIDATES = [
    os.path.join(HEALTH_INPUT_DIR, "monthly_health_events_rates_by_area.csv"),
    os.path.join(HEALTH_INPUT_DIR, "monthly_health_event_rates_by_area.csv"),
]

HEALTH_SEASONAL_CANDIDATES = [
    os.path.join(HEALTH_INPUT_DIR, "seasonal_health_events_rates_by_area.csv"),
    os.path.join(HEALTH_INPUT_DIR, "seasonal_health_event_rates_by_area.csv"),
]


# ============================================================
# GENERAL UTILITIES
# ============================================================

def read_project_csv(path):
    """
    Read a project CSV file.

    Most outputs in this project are saved with semicolon separators.
    The function also tries comma separation as fallback.
    """

    if not os.path.exists(path):
        raise FileNotFoundError(f"Input file not found: {path}")

    last_df = None

    for sep in [";", ","]:
        df = pd.read_csv(path, sep=sep)
        last_df = df

        if len(df.columns) > 1:
            df.columns = [str(col).strip() for col in df.columns]
            return df

    raise ValueError(
        f"Could not read file correctly: {path}\n"
        f"Columns detected in last attempt: {last_df.columns.tolist()}"
    )


def find_existing_file(candidates, description):
    """
    Return the first existing file among candidate paths.
    """

    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate

    folder = os.path.dirname(candidates[0])
    csv_files = glob.glob(os.path.join(folder, "*.csv"))

    raise FileNotFoundError(
        f"Could not find {description}.\n"
        f"Checked candidates:\n{candidates}\n"
        f"CSV files found in folder {folder}:\n{csv_files}"
    )


def normalize_column_name(col):
    """
    Normalize a column name for safer automatic detection.
    """

    return (
        str(col)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace(".", "")
        .replace("-", "_")
        .replace("/", "_")
        .replace("(", "")
        .replace(")", "")
    )


def normalize_text(value):
    """
    Normalize text values while preserving the actual labels.
    """

    if pd.isna(value):
        return None

    return str(value).strip()


def parse_dates_safely(series):
    """
    Parse dates while avoiding ambiguous-format warnings when possible.
    """

    possible_formats = [
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y %H:%M:%S",
        "%Y/%m/%d",
        "%d-%m-%Y",
    ]

    for fmt in possible_formats:
        parsed = pd.to_datetime(series, format=fmt, errors="coerce")

        if parsed.notna().sum() >= 0.90 * len(series):
            return parsed

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


def get_season_year_from_date(date):
    """
    Assign season-year.

    December belongs to the winter of the following year.
    """

    if pd.isna(date):
        return pd.NA

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
        .replace("\\", "_")
        .replace("(", "")
        .replace(")", "")
        .replace(",", "")
        .replace(":", "")
        .replace("<", "lt")
        .replace(">", "gt")
    )


def standardize_pollutant_name(value):
    """
    Standardize pollutant names used across the project.
    """

    if pd.isna(value):
        return None

    text = str(value).strip().upper()
    text = text.replace("PM2.5", "PM25").replace("PM2_5", "PM25")
    text = text.replace("PM 2.5", "PM25")

    if text in ["NO2", "NO₂"]:
        return "NO2"

    if text in ["PM25", "PM_25", "PM2,5"]:
        return "PM25"

    return text


def pollutant_label(pollutant):
    """
    Pretty label for plots.
    """

    if pollutant == "PM25":
        return "PM2.5"

    return pollutant


def standardize_area(value):
    """
    Standardize area labels.
    """

    if pd.isna(value):
        return None

    text = str(value).strip().lower()

    if text.startswith("ind"):
        return "Industrial"

    if text.startswith("agr"):
        return "Agricultural"

    return str(value).strip()


def standardize_season(value):
    """
    Standardize season labels.
    """

    if pd.isna(value):
        return None

    text = str(value).strip().lower()

    if text.startswith("win") or text.startswith("inv"):
        return "Winter"
    if text.startswith("spr") or text.startswith("pri"):
        return "Spring"
    if text.startswith("sum") or text.startswith("est"):
        return "Summer"
    if text.startswith("aut") or text.startswith("fal"):
        return "Autumn"

    return str(value).strip()


def standardize_outcome(value):
    """
    Standardize health outcome names.
    """

    if pd.isna(value):
        return None

    text = str(value).strip().upper()

    if "RESP" in text:
        return "Respiratory"

    if "CARDIO" in text or "CIRCOL" in text:
        return "Cardiocirculatory"

    return str(value).strip()


def find_column(columns, exact_names=None, contains=None):
    """
    Find a column using normalized exact matching first and partial matching second.
    """

    exact_names = exact_names or []
    contains = contains or []

    normalized = {
        col: normalize_column_name(col)
        for col in columns
    }

    exact_normalized = [
        normalize_column_name(name)
        for name in exact_names
    ]

    for col, norm_col in normalized.items():
        if norm_col in exact_normalized:
            return col

    for col, norm_col in normalized.items():
        for pattern in contains:
            if normalize_column_name(pattern) in norm_col:
                return col

    return None


def ensure_output_folders():
    """
    Create output folders.
    """

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(PLOTS_DIR, exist_ok=True)


# ============================================================
# HEALTH DATA PREPARATION
# ============================================================

def detect_population_column(df):
    """
    Detect the population denominator column.
    """

    population_col = find_column(
        df.columns,
        exact_names=["Population", "Total_population", "Area_population"],
        contains=["population"]
    )

    if population_col is None:
        raise ValueError(
            "Could not detect population column in health dataset.\n"
            f"Available columns: {df.columns.tolist()}"
        )

    return population_col


def detect_rate_column(df):
    """
    Detect the health-rate column in long-format health datasets.
    """

    rate_col = find_column(
        df.columns,
        exact_names=[
            "Rate_per_10000",
            "Health_rate_per_10000",
            "Event_rate_per_10000",
        ],
        contains=["rate_per_10000"]
    )

    if rate_col is None:
        raise ValueError(
            "Could not detect rate-per-10000 column in long-format health dataset.\n"
            f"Available columns: {df.columns.tolist()}"
        )

    return rate_col


def prepare_health_common(raw):
    """
    Apply common standardization to health datasets.
    """

    data = raw.copy()
    data.columns = [str(col).strip() for col in data.columns]

    area_col = find_column(data.columns, exact_names=["Area"], contains=["area"])

    if area_col is None:
        raise ValueError(
            "Could not detect Area column in health dataset.\n"
            f"Available columns: {data.columns.tolist()}"
        )

    data[area_col] = data[area_col].apply(standardize_area)

    return data, area_col


def pivot_health_outcomes(data, index_columns):
    """
    Convert health data to wide outcome format.

    Supported input structures:
    1. Wide format already containing:
       Respiratory_rate_per_10000
       Cardiocirculatory_rate_per_10000

    2. Long format containing:
       Outcome
       Rate_per_10000
    """

    existing_outcome_cols = [
        col for col in OUTCOMES.values()
        if col in data.columns
    ]

    if len(existing_outcome_cols) == len(OUTCOMES):
        keep_cols = index_columns + list(OUTCOMES.values())

        wide = data[keep_cols].drop_duplicates(subset=index_columns).copy()
        return wide

    outcome_col = find_column(
        data.columns,
        exact_names=["Outcome", "Health_outcome", "Event_outcome"],
        contains=["outcome", "type_dtl"]
    )

    if outcome_col is None:
        raise ValueError(
            "Could not detect health outcome column.\n"
            "Expected either wide outcome columns or a long-format Outcome column.\n"
            f"Available columns: {data.columns.tolist()}"
        )

    rate_col = detect_rate_column(data)

    data = data.copy()
    data[outcome_col] = data[outcome_col].apply(standardize_outcome)

    data = data[data[outcome_col].isin(OUTCOMES.keys())].copy()

    wide = data.pivot_table(
        index=index_columns,
        columns=outcome_col,
        values=rate_col,
        aggfunc="mean"
    ).reset_index()

    wide.columns.name = None

    rename_dict = {
        "Respiratory": OUTCOMES["Respiratory"],
        "Cardiocirculatory": OUTCOMES["Cardiocirculatory"],
    }

    wide = wide.rename(columns=rename_dict)

    for outcome_col_name in OUTCOMES.values():
        if outcome_col_name not in wide.columns:
            wide[outcome_col_name] = np.nan

    return wide


def prepare_monthly_health(path):
    """
    Prepare monthly health rate dataset from Part 2.2.

    Final output columns:
    MonthPeriod | Year | Month | Season | Area | Population
    Respiratory_rate_per_10000 | Cardiocirculatory_rate_per_10000 | TimeLabel
    """

    raw = read_project_csv(path)
    data, area_col = prepare_health_common(raw)

    month_period_col = find_column(
        data.columns,
        exact_names=["MonthPeriod", "Month_period"],
        contains=["monthperiod", "month_period"]
    )

    year_col = find_column(data.columns, exact_names=["Year"], contains=["year"])
    month_col = find_column(data.columns, exact_names=["Month"], contains=["month"])
    season_col = find_column(data.columns, exact_names=["Season"], contains=["season"])
    population_col = detect_population_column(data)

    if month_period_col is not None:
        data["MonthPeriod"] = parse_dates_safely(data[month_period_col])
        data["Year"] = data["MonthPeriod"].dt.year
        data["Month"] = data["MonthPeriod"].dt.month

    else:
        if year_col is None or month_col is None:
            raise ValueError(
                "Could not build MonthPeriod. Need either MonthPeriod column "
                "or both Year and Month columns."
            )

        data["Year"] = pd.to_numeric(data[year_col], errors="coerce").astype("Int64")
        data["Month"] = pd.to_numeric(data[month_col], errors="coerce").astype("Int64")

        data["MonthPeriod"] = pd.to_datetime(
            data["Year"].astype(str) + "-" + data["Month"].astype(str).str.zfill(2) + "-01",
            errors="coerce"
        )

    if season_col is not None:
        data["Season"] = data[season_col].apply(standardize_season)
    else:
        data["Season"] = data["Month"].apply(get_season)

    data["Area"] = data[area_col].apply(standardize_area)
    data["Population"] = pd.to_numeric(data[population_col], errors="coerce")

    data = data[
        data["Year"].isin(COMMON_YEARS)
        & data["Area"].isin(AREA_ORDER)
        & data["MonthPeriod"].notna()
    ].copy()

    index_columns = [
        "MonthPeriod",
        "Year",
        "Month",
        "Season",
        "Area",
        "Population",
    ]

    monthly_health = pivot_health_outcomes(data, index_columns)

    monthly_health["TimeLabel"] = monthly_health["MonthPeriod"].dt.strftime("%Y-%m")

    monthly_health = monthly_health.sort_values(
        ["Area", "MonthPeriod"]
    ).reset_index(drop=True)

    return monthly_health


def prepare_seasonal_health(path):
    """
    Prepare seasonal health rate dataset from Part 2.2.

    Final output columns:
    SeasonYear | Season | Area | Population
    Respiratory_rate_per_10000 | Cardiocirculatory_rate_per_10000 | TimeLabel
    """

    raw = read_project_csv(path)
    data, area_col = prepare_health_common(raw)

    season_year_col = find_column(
        data.columns,
        exact_names=["SeasonYear", "Season_year"],
        contains=["seasonyear", "season_year"]
    )

    season_col = find_column(data.columns, exact_names=["Season"], contains=["season"])
    population_col = detect_population_column(data)

    if season_year_col is None:
        year_col = find_column(data.columns, exact_names=["Year"], contains=["year"])

        if year_col is None:
            raise ValueError(
                "Could not detect SeasonYear or Year column in seasonal health dataset."
            )

        data["SeasonYear"] = pd.to_numeric(data[year_col], errors="coerce").astype("Int64")
    else:
        data["SeasonYear"] = pd.to_numeric(
            data[season_year_col],
            errors="coerce"
        ).astype("Int64")

    if season_col is None:
        raise ValueError(
            "Could not detect Season column in seasonal health dataset."
        )

    data["Season"] = data[season_col].apply(standardize_season)
    data["Area"] = data[area_col].apply(standardize_area)
    data["Population"] = pd.to_numeric(data[population_col], errors="coerce")

    data = data[
        data["SeasonYear"].isin(COMMON_YEARS)
        & data["Area"].isin(AREA_ORDER)
        & data["Season"].isin(SEASON_ORDER)
    ].copy()

    index_columns = [
        "SeasonYear",
        "Season",
        "Area",
        "Population",
    ]

    seasonal_health = pivot_health_outcomes(data, index_columns)

    seasonal_health["Season"] = pd.Categorical(
        seasonal_health["Season"],
        categories=SEASON_ORDER,
        ordered=True
    )

    seasonal_health["TimeLabel"] = (
        seasonal_health["SeasonYear"].astype(str)
        + "-"
        + seasonal_health["Season"].astype(str)
    )

    seasonal_health = seasonal_health.sort_values(
        ["Area", "SeasonYear", "Season"]
    ).reset_index(drop=True)

    seasonal_health["Season"] = seasonal_health["Season"].astype(str)

    return seasonal_health


# ============================================================
# MODARIA EXPOSURE PREPARATION
# ============================================================

def detect_method_columns(df):
    """
    Detect arithmetic and population-weighted exposure columns.
    """

    method_columns = {}

    for method in METHODS.keys():
        exact = find_column(df.columns, exact_names=[method])

        if exact is not None:
            method_columns[method] = exact
            continue

        if method == "Population_weighted_mean":
            col = find_column(
                df.columns,
                contains=["population_weighted", "pop_weighted"]
            )
        else:
            col = find_column(
                df.columns,
                contains=["arithmetic_mean", "arithmetic"]
            )

        if col is None:
            raise ValueError(
                f"Could not detect exposure column for method {method}.\n"
                f"Available columns: {df.columns.tolist()}"
            )

        method_columns[method] = col

    return method_columns


def prepare_exposure_long_format(data, temporal_scale):
    """
    Prepare exposure data when the dataset is in long pollutant format.

    Expected conceptual columns:
    temporal columns | Area | Pollutant | Arithmetic_mean | Population_weighted_mean
    """

    pollutant_col = find_column(
        data.columns,
        exact_names=["Pollutant", "Inquinante"],
        contains=["pollutant", "inquinante"]
    )

    if pollutant_col is None:
        return None

    area_col = find_column(data.columns, exact_names=["Area"], contains=["area"])

    if area_col is None:
        raise ValueError(
            "Could not detect Area column in exposure dataset."
        )

    method_columns = detect_method_columns(data)

    prepared = data.copy()

    prepared["Area"] = prepared[area_col].apply(standardize_area)
    prepared["Pollutant"] = prepared[pollutant_col].apply(standardize_pollutant_name)

    for method, col in method_columns.items():
        prepared[method] = pd.to_numeric(prepared[col], errors="coerce")

    if temporal_scale == "monthly":
        month_period_col = find_column(
            prepared.columns,
            exact_names=["MonthPeriod", "Month_period"],
            contains=["monthperiod", "month_period"]
        )

        year_col = find_column(prepared.columns, exact_names=["Year"], contains=["year"])
        month_col = find_column(prepared.columns, exact_names=["Month"], contains=["month"])
        season_col = find_column(prepared.columns, exact_names=["Season"], contains=["season"])

        if month_period_col is not None:
            prepared["MonthPeriod"] = parse_dates_safely(prepared[month_period_col])
            prepared["Year"] = prepared["MonthPeriod"].dt.year
            prepared["Month"] = prepared["MonthPeriod"].dt.month
        else:
            if year_col is None or month_col is None:
                raise ValueError(
                    "Could not build MonthPeriod in monthly exposure dataset."
                )

            prepared["Year"] = pd.to_numeric(prepared[year_col], errors="coerce").astype("Int64")
            prepared["Month"] = pd.to_numeric(prepared[month_col], errors="coerce").astype("Int64")
            prepared["MonthPeriod"] = pd.to_datetime(
                prepared["Year"].astype(str)
                + "-"
                + prepared["Month"].astype(str).str.zfill(2)
                + "-01",
                errors="coerce"
            )

        if season_col is not None:
            prepared["Season"] = prepared[season_col].apply(standardize_season)
        else:
            prepared["Season"] = prepared["Month"].apply(get_season)

        prepared = prepared[
            prepared["Year"].isin(COMMON_YEARS)
            & prepared["Area"].isin(AREA_ORDER)
            & prepared["Pollutant"].isin(POLLUTANTS)
            & prepared["MonthPeriod"].notna()
        ].copy()

        index_columns = ["MonthPeriod", "Year", "Month", "Season", "Area"]

    else:
        season_year_col = find_column(
            prepared.columns,
            exact_names=["SeasonYear", "Season_year"],
            contains=["seasonyear", "season_year"]
        )

        season_col = find_column(prepared.columns, exact_names=["Season"], contains=["season"])

        if season_year_col is None or season_col is None:
            raise ValueError(
                "Could not detect SeasonYear and Season columns "
                "in seasonal exposure dataset."
            )

        prepared["SeasonYear"] = pd.to_numeric(
            prepared[season_year_col],
            errors="coerce"
        ).astype("Int64")

        prepared["Season"] = prepared[season_col].apply(standardize_season)

        prepared = prepared[
            prepared["SeasonYear"].isin(COMMON_YEARS)
            & prepared["Area"].isin(AREA_ORDER)
            & prepared["Season"].isin(SEASON_ORDER)
            & prepared["Pollutant"].isin(POLLUTANTS)
        ].copy()

        index_columns = ["SeasonYear", "Season", "Area"]

    # Pivot pollutant and method columns to wide format.
    wide = prepared[index_columns].drop_duplicates().copy()

    for pollutant in POLLUTANTS:
        pollutant_subset = prepared[prepared["Pollutant"] == pollutant].copy()

        for method in METHODS.keys():
            suffix = METHOD_SUFFIX[method]
            output_col = f"{pollutant}_{suffix}"

            pivoted = pollutant_subset.pivot_table(
                index=index_columns,
                values=method,
                aggfunc="mean"
            ).reset_index()

            pivoted = pivoted.rename(columns={method: output_col})

            wide = wide.merge(
                pivoted,
                on=index_columns,
                how="left"
            )

    if temporal_scale == "monthly":
        wide["TimeLabel"] = wide["MonthPeriod"].dt.strftime("%Y-%m")
        wide = wide.sort_values(["Area", "MonthPeriod"]).reset_index(drop=True)
    else:
        wide["Season"] = pd.Categorical(
            wide["Season"],
            categories=SEASON_ORDER,
            ordered=True
        )
        wide["TimeLabel"] = wide["SeasonYear"].astype(str) + "-" + wide["Season"].astype(str)
        wide = wide.sort_values(["Area", "SeasonYear", "Season"]).reset_index(drop=True)
        wide["Season"] = wide["Season"].astype(str)

    return wide


def prepare_exposure_wide_format(data, temporal_scale):
    """
    Prepare exposure data if the 4.2 output is already in wide format.

    The function searches for columns containing:
    pollutant name + exposure method name.
    """

    prepared = data.copy()
    prepared.columns = [str(col).strip() for col in prepared.columns]

    area_col = find_column(prepared.columns, exact_names=["Area"], contains=["area"])

    if area_col is None:
        raise ValueError(
            "Could not detect Area column in wide-format exposure dataset."
        )

    prepared["Area"] = prepared[area_col].apply(standardize_area)

    if temporal_scale == "monthly":
        month_period_col = find_column(
            prepared.columns,
            exact_names=["MonthPeriod", "Month_period"],
            contains=["monthperiod", "month_period"]
        )

        year_col = find_column(prepared.columns, exact_names=["Year"], contains=["year"])
        month_col = find_column(prepared.columns, exact_names=["Month"], contains=["month"])
        season_col = find_column(prepared.columns, exact_names=["Season"], contains=["season"])

        if month_period_col is not None:
            prepared["MonthPeriod"] = parse_dates_safely(prepared[month_period_col])
            prepared["Year"] = prepared["MonthPeriod"].dt.year
            prepared["Month"] = prepared["MonthPeriod"].dt.month
        else:
            if year_col is None or month_col is None:
                raise ValueError(
                    "Could not build MonthPeriod in wide-format monthly exposure dataset."
                )

            prepared["Year"] = pd.to_numeric(prepared[year_col], errors="coerce").astype("Int64")
            prepared["Month"] = pd.to_numeric(prepared[month_col], errors="coerce").astype("Int64")
            prepared["MonthPeriod"] = pd.to_datetime(
                prepared["Year"].astype(str)
                + "-"
                + prepared["Month"].astype(str).str.zfill(2)
                + "-01",
                errors="coerce"
            )

        if season_col is not None:
            prepared["Season"] = prepared[season_col].apply(standardize_season)
        else:
            prepared["Season"] = prepared["Month"].apply(get_season)

        base_columns = ["MonthPeriod", "Year", "Month", "Season", "Area"]

    else:
        season_year_col = find_column(
            prepared.columns,
            exact_names=["SeasonYear", "Season_year"],
            contains=["seasonyear", "season_year"]
        )

        season_col = find_column(prepared.columns, exact_names=["Season"], contains=["season"])

        if season_year_col is None or season_col is None:
            raise ValueError(
                "Could not detect SeasonYear and Season columns in seasonal exposure dataset."
            )

        prepared["SeasonYear"] = pd.to_numeric(
            prepared[season_year_col],
            errors="coerce"
        ).astype("Int64")

        prepared["Season"] = prepared[season_col].apply(standardize_season)

        base_columns = ["SeasonYear", "Season", "Area"]

    output = prepared[base_columns].copy()

    normalized_columns = {
        col: normalize_column_name(col)
        for col in prepared.columns
    }

    for pollutant in POLLUTANTS:
        pollutant_keys = [pollutant.lower()]

        if pollutant == "PM25":
            pollutant_keys += ["pm25", "pm2_5", "pm25", "pm2"]

        for method, suffix in METHOD_SUFFIX.items():
            target_col = f"{pollutant}_{suffix}"

            found_col = None

            for col, norm_col in normalized_columns.items():
                has_pollutant = any(key in norm_col for key in pollutant_keys)

                if not has_pollutant:
                    continue

                if method == "Population_weighted_mean":
                    has_method = (
                        "population_weighted" in norm_col
                        or "pop_weighted" in norm_col
                        or ("population" in norm_col and "weighted" in norm_col)
                    )
                else:
                    has_method = (
                        "arithmetic" in norm_col
                        or "arith" in norm_col
                    )

                if has_method:
                    found_col = col
                    break

            if found_col is None:
                raise ValueError(
                    f"Could not detect exposure column for {pollutant} / {method} "
                    f"in wide-format exposure dataset.\n"
                    f"Available columns: {prepared.columns.tolist()}"
                )

            output[target_col] = pd.to_numeric(prepared[found_col], errors="coerce")

    if temporal_scale == "monthly":
        output = output[
            output["Year"].isin(COMMON_YEARS)
            & output["Area"].isin(AREA_ORDER)
            & output["MonthPeriod"].notna()
        ].copy()

        output["TimeLabel"] = output["MonthPeriod"].dt.strftime("%Y-%m")
        output = output.sort_values(["Area", "MonthPeriod"]).reset_index(drop=True)

    else:
        output = output[
            output["SeasonYear"].isin(COMMON_YEARS)
            & output["Area"].isin(AREA_ORDER)
            & output["Season"].isin(SEASON_ORDER)
        ].copy()

        output["Season"] = pd.Categorical(
            output["Season"],
            categories=SEASON_ORDER,
            ordered=True
        )

        output["TimeLabel"] = output["SeasonYear"].astype(str) + "-" + output["Season"].astype(str)
        output = output.sort_values(["Area", "SeasonYear", "Season"]).reset_index(drop=True)
        output["Season"] = output["Season"].astype(str)

    return output


def prepare_modaria_exposure(path, temporal_scale):
    """
    Prepare ModAria exposure dataset from Part 4.2.

    The function first tries the expected long format.
    If no Pollutant column is detected, it switches to wide-format detection.
    """

    raw = read_project_csv(path)

    long_format = prepare_exposure_long_format(raw, temporal_scale)

    if long_format is not None:
        return long_format

    return prepare_exposure_wide_format(raw, temporal_scale)


# ============================================================
# DATA INTEGRATION
# ============================================================

def integrate_monthly(monthly_exposure, monthly_health):
    """
    Merge monthly ModAria exposure with monthly health rates.
    """

    integrated = monthly_health.merge(
        monthly_exposure,
        on=["MonthPeriod", "Year", "Month", "Season", "Area"],
        how="inner",
        suffixes=("_health", "_exposure")
    )

    # Keep one TimeLabel column.
    if "TimeLabel_health" in integrated.columns:
        integrated["TimeLabel"] = integrated["TimeLabel_health"]

    elif "TimeLabel_exposure" in integrated.columns:
        integrated["TimeLabel"] = integrated["TimeLabel_exposure"]

    integrated = integrated.drop(
        columns=[
            col for col in ["TimeLabel_health", "TimeLabel_exposure"]
            if col in integrated.columns
        ]
    )

    first_cols = [
        "MonthPeriod",
        "Year",
        "Month",
        "Season",
        "Area",
        "Population",
        OUTCOMES["Respiratory"],
        OUTCOMES["Cardiocirculatory"],
    ]

    exposure_cols = [
        f"{pollutant}_{METHOD_SUFFIX[method]}"
        for pollutant in POLLUTANTS
        for method in METHODS.keys()
    ]

    final_cols = first_cols + exposure_cols + ["TimeLabel"]

    integrated = integrated[final_cols].sort_values(
        ["Area", "MonthPeriod"]
    ).reset_index(drop=True)

    return integrated


def integrate_seasonal(seasonal_exposure, seasonal_health):
    """
    Merge seasonal ModAria exposure with seasonal health rates.
    """

    integrated = seasonal_health.merge(
        seasonal_exposure,
        on=["SeasonYear", "Season", "Area"],
        how="inner",
        suffixes=("_health", "_exposure")
    )

    if "TimeLabel_health" in integrated.columns:
        integrated["TimeLabel"] = integrated["TimeLabel_health"]

    elif "TimeLabel_exposure" in integrated.columns:
        integrated["TimeLabel"] = integrated["TimeLabel_exposure"]

    integrated = integrated.drop(
        columns=[
            col for col in ["TimeLabel_health", "TimeLabel_exposure"]
            if col in integrated.columns
        ]
    )

    first_cols = [
        "SeasonYear",
        "Season",
        "Area",
        "Population",
        OUTCOMES["Respiratory"],
        OUTCOMES["Cardiocirculatory"],
    ]

    exposure_cols = [
        f"{pollutant}_{METHOD_SUFFIX[method]}"
        for pollutant in POLLUTANTS
        for method in METHODS.keys()
    ]

    final_cols = first_cols + exposure_cols + ["TimeLabel"]

    integrated["Season"] = pd.Categorical(
        integrated["Season"],
        categories=SEASON_ORDER,
        ordered=True
    )

    integrated = integrated[final_cols].sort_values(
        ["Area", "SeasonYear", "Season"]
    ).reset_index(drop=True)

    integrated["Season"] = integrated["Season"].astype(str)

    return integrated


def build_missing_values_check(monthly_integrated, seasonal_integrated):
    """
    Build a compact missing-value check for integrated datasets.
    """

    rows = []

    for temporal_scale, dataset in [
        ("Monthly", monthly_integrated),
        ("Seasonal", seasonal_integrated),
    ]:
        for col in dataset.columns:
            rows.append({
                "Temporal_scale": temporal_scale,
                "Column": col,
                "Missing_values": int(dataset[col].isna().sum()),
                "Total_rows": len(dataset),
                "Missing_percentage": round(
                    100 * dataset[col].isna().sum() / len(dataset),
                    3
                ) if len(dataset) > 0 else np.nan,
            })

    return pd.DataFrame(rows)

def validate_integrated_datasets(monthly_integrated, seasonal_integrated):
    """
    Validate the ModAria-health integrated datasets.

    Expected structure:
    - Monthly: 60 months × 2 areas = 120 rows
    - Seasonal: 18 complete seasons × 2 areas = 36 rows

    The exposure dataset contains both pollutants and both exposure indicators
    as columns, while the health dataset contains both outcomes as columns.
    """

    errors = []

    expected_monthly_rows = 60 * len(AREA_ORDER)
    expected_seasonal_rows = 18 * len(AREA_ORDER)

    if len(monthly_integrated) != expected_monthly_rows:
        errors.append(
            f"Monthly integrated dataset: expected {expected_monthly_rows} rows, "
            f"found {len(monthly_integrated)}."
        )

    if len(seasonal_integrated) != expected_seasonal_rows:
        errors.append(
            f"Seasonal integrated dataset: expected {expected_seasonal_rows} rows, "
            f"found {len(seasonal_integrated)}."
        )

    monthly_duplicates = (
        monthly_integrated
        .groupby(["MonthPeriod", "Area"])
        .size()
        .reset_index(name="N")
    )

    monthly_duplicates = monthly_duplicates[monthly_duplicates["N"] > 1].copy()

    if len(monthly_duplicates) > 0:
        errors.append(
            "Duplicated MonthPeriod × Area rows found in monthly integrated dataset:\n"
            f"{monthly_duplicates.to_string(index=False)}"
        )

    seasonal_duplicates = (
        seasonal_integrated
        .groupby(["SeasonYear", "Season", "Area"])
        .size()
        .reset_index(name="N")
    )

    seasonal_duplicates = seasonal_duplicates[seasonal_duplicates["N"] > 1].copy()

    if len(seasonal_duplicates) > 0:
        errors.append(
            "Duplicated SeasonYear × Season × Area rows found in seasonal integrated dataset:\n"
            f"{seasonal_duplicates.to_string(index=False)}"
        )

    required_exposure_cols = [
        f"{pollutant}_{METHOD_SUFFIX[method]}"
        for pollutant in POLLUTANTS
        for method in METHODS.keys()
    ]

    required_health_cols = list(OUTCOMES.values())

    required_monthly_cols = [
        "MonthPeriod",
        "Year",
        "Month",
        "Season",
        "Area",
        "Population",
    ] + required_health_cols + required_exposure_cols

    required_seasonal_cols = [
        "SeasonYear",
        "Season",
        "Area",
        "Population",
    ] + required_health_cols + required_exposure_cols

    missing_monthly_cols = [
        col for col in required_monthly_cols
        if col not in monthly_integrated.columns
    ]

    missing_seasonal_cols = [
        col for col in required_seasonal_cols
        if col not in seasonal_integrated.columns
    ]

    if missing_monthly_cols:
        errors.append(
            "Missing columns in monthly integrated dataset:\n"
            f"{missing_monthly_cols}"
        )

    if missing_seasonal_cols:
        errors.append(
            "Missing columns in seasonal integrated dataset:\n"
            f"{missing_seasonal_cols}"
        )

    monthly_missing = monthly_integrated.isna().sum()
    monthly_missing = monthly_missing[monthly_missing > 0]

    seasonal_missing = seasonal_integrated.isna().sum()
    seasonal_missing = seasonal_missing[seasonal_missing > 0]

    if len(monthly_missing) > 0:
        errors.append(
            "Missing values found in monthly integrated dataset:\n"
            f"{monthly_missing.to_string()}"
        )

    if len(seasonal_missing) > 0:
        errors.append(
            "Missing values found in seasonal integrated dataset:\n"
            f"{seasonal_missing.to_string()}"
        )

    if errors:
        raise ValueError(
            "\nPART 4.3 INTEGRATED DATASET VALIDATION FAILED\n\n"
            + "\n\n".join(errors)
        )

    print("\nIntegrated dataset validation passed.")
    print(f"Monthly integrated rows: {len(monthly_integrated)} / expected {expected_monthly_rows}")
    print(f"Seasonal integrated rows: {len(seasonal_integrated)} / expected {expected_seasonal_rows}")


# ============================================================
# CORRELATION ANALYSIS
# ============================================================

def interpret_strength(value):
    """
    Qualitative interpretation of absolute correlation strength.
    """

    if pd.isna(value):
        return "not available"

    abs_value = abs(value)

    if abs_value < 0.10:
        return "very weak"
    if abs_value < 0.30:
        return "weak"
    if abs_value < 0.50:
        return "moderate"
    if abs_value < 0.70:
        return "strong"

    return "very strong"


def interpret_direction(value):
    """
    Interpret correlation direction.
    """

    if pd.isna(value):
        return "not available"

    if value > 0:
        return "positive"

    if value < 0:
        return "negative"

    return "zero"


def interpret_significance(p_value):
    """
    Interpret p-value using p < 0.05 as descriptive threshold.
    """

    if pd.isna(p_value):
        return "not available"

    if p_value < 0.05:
        return "statistically significant at p < 0.05"

    return "not statistically significant at p < 0.05"


def build_interpretation(correlation, p_value):
    """
    Build a compact correlation interpretation string.
    """

    if pd.isna(correlation):
        return "Correlation not available"

    strength = interpret_strength(correlation)
    direction = interpret_direction(correlation)

    if pd.isna(p_value):
        significance = "p-value not available"
    elif p_value < 0.05:
        significance = "statistically significant"
    else:
        significance = "not statistically significant"

    return f"{strength.capitalize()} {direction}, {significance}"


def run_correlation(x, y, method):
    """
    Run Spearman or Pearson correlation safely.
    """

    pair = pd.DataFrame({
        "x": x,
        "y": y,
    }).dropna()

    n = len(pair)

    if n < 3:
        return n, np.nan, np.nan

    if pair["x"].nunique() < 2 or pair["y"].nunique() < 2:
        return n, np.nan, np.nan

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        if method == "Spearman":
            result = spearmanr(pair["x"], pair["y"])
        elif method == "Pearson":
            result = pearsonr(pair["x"], pair["y"])
        else:
            raise ValueError(f"Unknown correlation method: {method}")

    return n, result.statistic, result.pvalue


def compute_correlations(dataset, temporal_scale):
    """
    Compute Spearman and Pearson correlations.

    Correlations are computed:
    - overall;
    - separately for Industrial and Agricultural areas;
    - for both pollutants;
    - for both outcomes;
    - for both exposure indicators.
    """

    rows = []

    groups = {
        "Overall": dataset,
        "Industrial": dataset[dataset["Area"] == "Industrial"],
        "Agricultural": dataset[dataset["Area"] == "Agricultural"],
    }

    for exposure_method, exposure_label in METHODS.items():
        exposure_suffix = METHOD_SUFFIX[exposure_method]

        for correlation_method in ["Spearman", "Pearson"]:
            for group_name, group_data in groups.items():
                for pollutant in POLLUTANTS:
                    pollutant_col = f"{pollutant}_{exposure_suffix}"

                    for outcome_name, outcome_col in OUTCOMES.items():
                        n, corr, p_value = run_correlation(
                            x=group_data[pollutant_col],
                            y=group_data[outcome_col],
                            method=correlation_method
                        )

                        rows.append({
                            "Temporal_scale": temporal_scale,
                            "Exposure_method": exposure_method,
                            "Exposure_method_label": exposure_label,
                            "Correlation_method": correlation_method,
                            "Group": group_name,
                            "Pollutant": pollutant,
                            "Outcome": outcome_name,
                            "Pollutant_column": pollutant_col,
                            "Outcome_column": outcome_col,
                            "N": n,
                            "Correlation": corr,
                            "P_value": p_value,
                            "Strength": interpret_strength(corr),
                            "Direction": interpret_direction(corr),
                            "Significance": interpret_significance(p_value),
                            "Interpretation": build_interpretation(corr, p_value),
                        })

    return pd.DataFrame(rows)


def compute_monthly_season_stratified_spearman(monthly_integrated):
    """
    Season-stratified monthly Spearman correlation.

    This is a sensitivity check using only the main exposure indicator.
    It helps evaluate whether monthly correlations are mainly driven by
    broad seasonal cycles.
    """

    rows = []
    exposure_method = MAIN_METHOD
    exposure_suffix = METHOD_SUFFIX[exposure_method]

    for season in SEASON_ORDER:
        season_data = monthly_integrated[
            monthly_integrated["Season"] == season
        ].copy()

        groups = {
            "Overall": season_data,
            "Industrial": season_data[season_data["Area"] == "Industrial"],
            "Agricultural": season_data[season_data["Area"] == "Agricultural"],
        }

        for group_name, group_data in groups.items():
            for pollutant in POLLUTANTS:
                pollutant_col = f"{pollutant}_{exposure_suffix}"

                for outcome_name, outcome_col in OUTCOMES.items():
                    n, corr, p_value = run_correlation(
                        x=group_data[pollutant_col],
                        y=group_data[outcome_col],
                        method="Spearman"
                    )

                    rows.append({
                        "Temporal_scale": "Monthly season-stratified",
                        "Season": season,
                        "Exposure_method": exposure_method,
                        "Exposure_method_label": METHODS[exposure_method],
                        "Correlation_method": "Spearman",
                        "Group": group_name,
                        "Pollutant": pollutant,
                        "Outcome": outcome_name,
                        "Pollutant_column": pollutant_col,
                        "Outcome_column": outcome_col,
                        "N": n,
                        "Correlation": corr,
                        "P_value": p_value,
                        "Strength": interpret_strength(corr),
                        "Direction": interpret_direction(corr),
                        "Significance": interpret_significance(p_value),
                        "Interpretation": build_interpretation(corr, p_value),
                    })

    return pd.DataFrame(rows)


# ============================================================
# PLOTTING UTILITIES
# ============================================================

def add_correlation_annotation(ax, corr_summary, temporal_scale, pollutant, outcome):
    """
    Add main Spearman annotation to scatter plots.
    """

    rows = corr_summary[
        (corr_summary["Temporal_scale"] == temporal_scale)
        & (corr_summary["Exposure_method"] == MAIN_METHOD)
        & (corr_summary["Correlation_method"] == "Spearman")
        & (corr_summary["Group"] == "Overall")
        & (corr_summary["Pollutant"] == pollutant)
        & (corr_summary["Outcome"] == outcome)
    ]

    if rows.empty:
        return

    row = rows.iloc[0]

    if pd.isna(row["Correlation"]):
        text = "Spearman ρ = n/a"
    else:
        text = (
            f"Overall Spearman ρ = {row['Correlation']:.3f}\n"
            f"p = {row['P_value']:.3g}\n"
            f"N = {int(row['N'])}"
        )

    ax.text(
        0.03,
        0.97,
        text,
        transform=ax.transAxes,
        va="top",
        ha="left",
        bbox=dict(boxstyle="round", alpha=0.15)
    )


def plot_main_scatter(dataset, temporal_scale, corr_summary):
    """
    Create main scatter plots using:
    - Population-weighted exposure;
    - Spearman annotation only.
    """

    exposure_suffix = METHOD_SUFFIX[MAIN_METHOD]

    for pollutant in POLLUTANTS:
        pollutant_col = f"{pollutant}_{exposure_suffix}"

        for outcome_name, outcome_col in OUTCOMES.items():
            fig, ax = plt.subplots(figsize=(8, 6))

            for area in AREA_ORDER:
                subset = dataset[dataset["Area"] == area].copy()

                ax.scatter(
                    subset[pollutant_col],
                    subset[outcome_col],
                    label=area,
                    alpha=0.75
                )

            ax.set_title(
                f"{temporal_scale} ModAria {pollutant_label(pollutant)} vs {outcome_name} rate"
            )

            ax.set_xlabel(f"{pollutant_label(pollutant)} concentration (µg/m³) - population-weighted")
            ax.set_ylabel(f"{outcome_name} rate per 10,000 inhabitants")

            add_correlation_annotation(
                ax=ax,
                corr_summary=corr_summary,
                temporal_scale=temporal_scale,
                pollutant=pollutant,
                outcome=outcome_name
            )

            ax.legend()
            ax.grid(alpha=0.3)

            filename = (
                f"{temporal_scale.lower()}_scatter_"
                f"{pollutant}_{outcome_name}_population_weighted_spearman.png"
            )

            plt.tight_layout()
            plt.savefig(
                os.path.join(PLOTS_DIR, safe_filename(filename)),
                dpi=300
            )
            plt.close()


def add_continuous_block(dataset, temporal_scale):
    """
    Add a block variable to avoid plotting lines across the 2019-2023 gap.
    """

    data = dataset.copy()

    if temporal_scale == "Monthly":
        year_col = "Year"
    else:
        year_col = "SeasonYear"

    data["ContinuousBlock"] = np.where(
        data[year_col] <= 2019,
        "2016-2019",
        "2023"
    )

    return data


def zscore(series):
    """
    Compute z-score safely.
    """

    if series.std(ddof=0) == 0 or pd.isna(series.std(ddof=0)):
        return series * np.nan

    return (series - series.mean()) / series.std(ddof=0)


def plot_standardized_trends(dataset, temporal_scale):
    """
    Create standardized trend plots.

    For each pollutant-outcome pair, the pollutant and health rate are
    standardized within each area. Lines are split by continuous block,
    so the 2019-2023 gap is not connected.
    """

    exposure_suffix = METHOD_SUFFIX[MAIN_METHOD]
    data = add_continuous_block(dataset, temporal_scale)

    if temporal_scale == "Monthly":
        x_col = "MonthPeriod"
    else:
        # Build an approximate date only for plotting seasonal order.
        season_to_month = {
            "Winter": 1,
            "Spring": 4,
            "Summer": 7,
            "Autumn": 10,
        }

        data["PlotDate"] = pd.to_datetime(
            data["SeasonYear"].astype(str)
            + "-"
            + data["Season"].map(season_to_month).astype(str).str.zfill(2)
            + "-01",
            errors="coerce"
        )

        x_col = "PlotDate"

    for pollutant in POLLUTANTS:
        pollutant_col = f"{pollutant}_{exposure_suffix}"

        for outcome_name, outcome_col in OUTCOMES.items():
            plot_data = data.copy()

            plot_data[f"{pollutant_col}_z"] = (
                plot_data
                .groupby("Area", observed=True)[pollutant_col]
                .transform(zscore)
            )

            plot_data[f"{outcome_col}_z"] = (
                plot_data
                .groupby("Area", observed=True)[outcome_col]
                .transform(zscore)
            )

            fig, ax = plt.subplots(figsize=(10, 6))

            for area in AREA_ORDER:
                for block in sorted(plot_data["ContinuousBlock"].dropna().unique()):
                    subset = plot_data[
                        (plot_data["Area"] == area)
                        & (plot_data["ContinuousBlock"] == block)
                    ].copy()

                    subset = subset.sort_values(x_col)

                    if subset.empty:
                        continue

                    ax.plot(
                        subset[x_col],
                        subset[f"{pollutant_col}_z"],
                        marker="o",
                        linestyle="-",
                        label=f"{area} - {pollutant_label(pollutant)}"
                        if block == sorted(plot_data["ContinuousBlock"].dropna().unique())[0]
                        else None
                    )

                    ax.plot(
                        subset[x_col],
                        subset[f"{outcome_col}_z"],
                        marker="s",
                        linestyle="--",
                        label=f"{area} - {outcome_name}"
                        if block == sorted(plot_data["ContinuousBlock"].dropna().unique())[0]
                        else None
                    )

            ax.set_title(
                f"{temporal_scale} standardized trends: {pollutant_label(pollutant)} and {outcome_name}"
            )

            ax.set_xlabel("Time")
            ax.set_ylabel("Within-area z-score")
            ax.axhline(0, linewidth=1, alpha=0.5)
            ax.grid(alpha=0.3)
            ax.legend(fontsize=8)

            filename = (
                f"{temporal_scale.lower()}_standardized_trends_"
                f"{pollutant}_{outcome_name}_population_weighted.png"
            )

            plt.tight_layout()
            plt.savefig(
                os.path.join(PLOTS_DIR, safe_filename(filename)),
                dpi=300
            )
            plt.close()


def plot_correlation_summary(correlation_summary, temporal_scale):
    """
    Plot final summary comparing Spearman and Pearson for the main exposure method.

    This plot is intentionally placed as a final/sensitivity figure.
    Main scatter plots remain Spearman-only.
    """

    subset = correlation_summary[
        (correlation_summary["Temporal_scale"] == temporal_scale)
        & (correlation_summary["Exposure_method"] == MAIN_METHOD)
    ].copy()

    subset["Label"] = (
        subset["Group"].astype(str)
        + " | "
        + subset["Pollutant"].astype(str)
        + " | "
        + subset["Outcome"].astype(str)
    )

    # Keep a readable order.
    order_df = subset[
        subset["Correlation_method"] == "Spearman"
    ][["Label", "Correlation"]].copy()

    order_df["AbsCorrelation"] = order_df["Correlation"].abs()
    ordered_labels = order_df.sort_values("AbsCorrelation")["Label"].tolist()

    fig, ax = plt.subplots(figsize=(10, 9))

    y_positions = np.arange(len(ordered_labels))
    bar_height = 0.35

    for offset, method in [(-bar_height / 2, "Spearman"), (bar_height / 2, "Pearson")]:
        method_data = subset[subset["Correlation_method"] == method].copy()
        method_data = method_data.set_index("Label").reindex(ordered_labels)

        ax.barh(
            y_positions + offset,
            method_data["Correlation"],
            height=bar_height,
            label=method
        )

    ax.set_yticks(y_positions)
    ax.set_yticklabels(ordered_labels, fontsize=8)
    ax.axvline(0, linewidth=1)
    ax.set_xlabel("Correlation coefficient")
    ax.set_title(
        f"{temporal_scale} correlation summary - population-weighted exposure"
    )
    ax.legend()
    ax.grid(axis="x", alpha=0.3)

    filename = (
        f"{temporal_scale.lower()}_correlation_summary_"
        f"population_weighted_spearman_vs_pearson.png"
    )

    plt.tight_layout()
    plt.savefig(
        os.path.join(PLOTS_DIR, safe_filename(filename)),
        dpi=300
    )
    plt.close()


# ============================================================
# SUMMARY TABLES
# ============================================================

def build_exposure_method_comparison(correlation_summary):
    """
    Compare population-weighted and arithmetic Spearman results.

    This tells whether the exposure aggregation method materially changes
    the correlation pattern.
    """

    spearman = correlation_summary[
        correlation_summary["Correlation_method"] == "Spearman"
    ].copy()

    population = spearman[
        spearman["Exposure_method"] == "Population_weighted_mean"
    ].copy()

    arithmetic = spearman[
        spearman["Exposure_method"] == "Arithmetic_mean"
    ].copy()

    merge_keys = [
        "Temporal_scale",
        "Group",
        "Pollutant",
        "Outcome",
        "Correlation_method",
    ]

    comparison = population.merge(
        arithmetic,
        on=merge_keys,
        how="inner",
        suffixes=("_population_weighted", "_arithmetic")
    )

    comparison["Correlation_difference_population_weighted_minus_arithmetic"] = (
        comparison["Correlation_population_weighted"]
        - comparison["Correlation_arithmetic"]
    )

    comparison["Absolute_correlation_difference"] = (
        comparison["Correlation_difference_population_weighted_minus_arithmetic"].abs()
    )

    comparison["Sensitivity_interpretation"] = np.where(
        comparison["Absolute_correlation_difference"] < 0.10,
        "Very similar correlation pattern",
        np.where(
            comparison["Absolute_correlation_difference"] < 0.20,
            "Moderately different correlation pattern",
            "Substantially different correlation pattern"
        )
    )

    keep_cols = merge_keys + [
        "N_population_weighted",
        "Correlation_population_weighted",
        "P_value_population_weighted",
        "N_arithmetic",
        "Correlation_arithmetic",
        "P_value_arithmetic",
        "Correlation_difference_population_weighted_minus_arithmetic",
        "Absolute_correlation_difference",
        "Sensitivity_interpretation",
    ]

    return comparison[keep_cols].copy()


def build_analysis_summary(monthly_integrated, seasonal_integrated, correlation_summary):
    """
    Build a compact key-value summary for the whole Part 4.3.
    """

    rows = []

    rows.append({
        "Item": "Monthly integrated rows",
        "Value": len(monthly_integrated),
        "Comment": "Expected value is 120 if all 5 years, 12 months and 2 areas are matched."
    })

    rows.append({
        "Item": "Seasonal integrated rows",
        "Value": len(seasonal_integrated),
        "Comment": "Expected value is 36 if the same complete seasons used in station-based integration are matched."
    })

    rows.append({
        "Item": "Main exposure indicator",
        "Value": MAIN_METHOD,
        "Comment": "Population-weighted exposure is conceptually aligned with population-normalized health rates."
    })

    rows.append({
        "Item": "Secondary exposure indicator",
        "Value": "Arithmetic_mean",
        "Comment": "Used as sensitivity check, not as main exposure indicator."
    })

    rows.append({
        "Item": "Main correlation method",
        "Value": "Spearman",
        "Comment": "Main ecological association metric because no linear exposure-response relationship is assumed."
    })

    rows.append({
        "Item": "Secondary correlation method",
        "Value": "Pearson",
        "Comment": "Computed as linear sensitivity check and saved in separate files."
    })

    main_spearman = correlation_summary[
        (correlation_summary["Exposure_method"] == MAIN_METHOD)
        & (correlation_summary["Correlation_method"] == "Spearman")
    ].copy()

    for temporal_scale in ["Monthly", "Seasonal"]:
        subset = main_spearman[
            main_spearman["Temporal_scale"] == temporal_scale
        ].copy()

        subset = subset.dropna(subset=["Correlation"])

        if subset.empty:
            continue

        strongest = subset.loc[subset["Correlation"].abs().idxmax()]

        rows.append({
            "Item": f"Strongest {temporal_scale.lower()} main Spearman association",
            "Value": (
                f"{strongest['Group']} | {strongest['Pollutant']} | "
                f"{strongest['Outcome']} | rho={strongest['Correlation']:.3f} | "
                f"p={strongest['P_value']:.3g}"
            ),
            "Comment": strongest["Interpretation"],
        })

    rows.append({
        "Item": "Brief station-based comparison note",
        "Value": "Qualitative comparison only in Part 4.3",
        "Comment": (
            "Use Part 4.3 to check whether the ModAria-based direction is broadly similar "
            "or different from the previous station-based integration. A complete station-based "
            "vs ModAria synthesis is better placed after monthly and weekly lag analyses."
        )
    })

    rows.append({
        "Item": "Causal interpretation warning",
        "Value": "Ecological association only",
        "Comment": (
            "Rows represent area-time aggregates, not individual exposure-response observations. "
            "No adjustment for meteorology, autocorrelation, demographic structure or socioeconomic factors is included."
        )
    })

    return pd.DataFrame(rows)


# ============================================================
# OUTPUT WRITING
# ============================================================

def save_correlation_outputs(
    monthly_corr,
    seasonal_corr,
    season_stratified_corr,
    exposure_method_comparison,
    all_corr
):
    """
    Save correlation outputs in separate and combined files.
    """

    # Main population-weighted Spearman files.
    monthly_corr[
        (monthly_corr["Exposure_method"] == "Population_weighted_mean")
        & (monthly_corr["Correlation_method"] == "Spearman")
    ].to_csv(
        os.path.join(OUTPUT_DIR, "spearman_population_weighted_correlation_summary_monthly.csv"),
        index=False,
        sep=";"
    )

    seasonal_corr[
        (seasonal_corr["Exposure_method"] == "Population_weighted_mean")
        & (seasonal_corr["Correlation_method"] == "Spearman")
    ].to_csv(
        os.path.join(OUTPUT_DIR, "spearman_population_weighted_correlation_summary_seasonal.csv"),
        index=False,
        sep=";"
    )

    # Pearson sensitivity on population-weighted exposure.
    monthly_corr[
        (monthly_corr["Exposure_method"] == "Population_weighted_mean")
        & (monthly_corr["Correlation_method"] == "Pearson")
    ].to_csv(
        os.path.join(OUTPUT_DIR, "pearson_population_weighted_correlation_summary_monthly.csv"),
        index=False,
        sep=";"
    )

    seasonal_corr[
        (seasonal_corr["Exposure_method"] == "Population_weighted_mean")
        & (seasonal_corr["Correlation_method"] == "Pearson")
    ].to_csv(
        os.path.join(OUTPUT_DIR, "pearson_population_weighted_correlation_summary_seasonal.csv"),
        index=False,
        sep=";"
    )

    # Arithmetic exposure sensitivity.
    monthly_corr[
        (monthly_corr["Exposure_method"] == "Arithmetic_mean")
        & (monthly_corr["Correlation_method"] == "Spearman")
    ].to_csv(
        os.path.join(OUTPUT_DIR, "spearman_arithmetic_mean_sensitivity_summary_monthly.csv"),
        index=False,
        sep=";"
    )

    seasonal_corr[
        (seasonal_corr["Exposure_method"] == "Arithmetic_mean")
        & (seasonal_corr["Correlation_method"] == "Spearman")
    ].to_csv(
        os.path.join(OUTPUT_DIR, "spearman_arithmetic_mean_sensitivity_summary_seasonal.csv"),
        index=False,
        sep=";"
    )

    monthly_corr[
        (monthly_corr["Exposure_method"] == "Arithmetic_mean")
        & (monthly_corr["Correlation_method"] == "Pearson")
    ].to_csv(
        os.path.join(OUTPUT_DIR, "pearson_arithmetic_mean_sensitivity_summary_monthly.csv"),
        index=False,
        sep=";"
    )

    seasonal_corr[
        (seasonal_corr["Exposure_method"] == "Arithmetic_mean")
        & (seasonal_corr["Correlation_method"] == "Pearson")
    ].to_csv(
        os.path.join(OUTPUT_DIR, "pearson_arithmetic_mean_sensitivity_summary_seasonal.csv"),
        index=False,
        sep=";"
    )

    # Combined files.
    all_corr.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_environment_health_correlation_summary_all_methods.csv"),
        index=False,
        sep=";"
    )

    season_stratified_corr.to_csv(
        os.path.join(OUTPUT_DIR, "spearman_population_weighted_season_stratified_monthly.csv"),
        index=False,
        sep=";"
    )

    exposure_method_comparison.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_exposure_method_correlation_comparison.csv"),
        index=False,
        sep=";"
    )


# ============================================================
# MAIN WORKFLOW
# ============================================================

def run_modaria_environment_health_integration():
    """
    Run Part 4.3 ModAria environmental-health integration.

    Main analysis:
    - monthly + seasonal integration;
    - Population_weighted_mean exposure;
    - Spearman correlation.

    Sensitivity:
    - Pearson correlation on population-weighted exposure;
    - Spearman/Pearson on arithmetic exposure;
    - season-stratified monthly Spearman check using population-weighted exposure.
    """

    ensure_output_folders()

    print("\n========================================")
    print("PART 4.3 - MODARIA ENVIRONMENTAL-HEALTH INTEGRATION")
    print("========================================")

    # ------------------------------------------------------------
    # Locate input files
    # ------------------------------------------------------------

    modaria_monthly_path = find_existing_file(
        MODARIA_MONTHLY_CANDIDATES,
        "ModAria monthly exposure dataset from Part 4.2"
    )

    modaria_seasonal_path = find_existing_file(
        MODARIA_SEASONAL_CANDIDATES,
        "ModAria seasonal exposure dataset from Part 4.2"
    )

    health_monthly_path = find_existing_file(
        HEALTH_MONTHLY_CANDIDATES,
        "monthly health-event rate dataset from Part 2.2"
    )

    health_seasonal_path = find_existing_file(
        HEALTH_SEASONAL_CANDIDATES,
        "seasonal health-event rate dataset from Part 2.2"
    )

    print("\nInput files:")
    print(f"ModAria monthly:  {modaria_monthly_path}")
    print(f"ModAria seasonal: {modaria_seasonal_path}")
    print(f"Health monthly:   {health_monthly_path}")
    print(f"Health seasonal:  {health_seasonal_path}")

    # ------------------------------------------------------------
    # Load and prepare input datasets
    # ------------------------------------------------------------

    monthly_exposure = prepare_modaria_exposure(
        modaria_monthly_path,
        temporal_scale="monthly"
    )

    seasonal_exposure = prepare_modaria_exposure(
        modaria_seasonal_path,
        temporal_scale="seasonal"
    )

    monthly_health = prepare_monthly_health(health_monthly_path)
    seasonal_health = prepare_seasonal_health(health_seasonal_path)

    # Save prepared inputs for quality control.
    monthly_exposure.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_monthly_exposure_prepared_for_integration.csv"),
        index=False,
        sep=";"
    )

    seasonal_exposure.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_seasonal_exposure_prepared_for_integration.csv"),
        index=False,
        sep=";"
    )

    monthly_health.to_csv(
        os.path.join(OUTPUT_DIR, "monthly_health_rates_prepared_for_integration.csv"),
        index=False,
        sep=";"
    )

    seasonal_health.to_csv(
        os.path.join(OUTPUT_DIR, "seasonal_health_rates_prepared_for_integration.csv"),
        index=False,
        sep=";"
    )

    print("\nPrepared dataset sizes:")
    print(f"Monthly exposure rows:  {len(monthly_exposure)}")
    print(f"Seasonal exposure rows: {len(seasonal_exposure)}")
    print(f"Monthly health rows:    {len(monthly_health)}")
    print(f"Seasonal health rows:   {len(seasonal_health)}")

    # ------------------------------------------------------------
    # Integrate exposure and health
    # ------------------------------------------------------------

    monthly_integrated = integrate_monthly(
        monthly_exposure=monthly_exposure,
        monthly_health=monthly_health
    )

    seasonal_integrated = integrate_seasonal(
        seasonal_exposure=seasonal_exposure,
        seasonal_health=seasonal_health
    )

    validate_integrated_datasets(
        monthly_integrated=monthly_integrated,
        seasonal_integrated=seasonal_integrated
    )

    monthly_integrated.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_monthly_environment_health_integrated_dataset.csv"),
        index=False,
        sep=";"
    )

    seasonal_integrated.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_seasonal_environment_health_integrated_dataset.csv"),
        index=False,
        sep=";"
    )

    missing_values_check = build_missing_values_check(
        monthly_integrated=monthly_integrated,
        seasonal_integrated=seasonal_integrated
    )

    missing_values_check.to_csv(
        os.path.join(OUTPUT_DIR, "missing_values_check.csv"),
        index=False,
        sep=";"
    )

    print("\nIntegrated dataset sizes:")
    print(f"Monthly integrated rows:  {len(monthly_integrated)}")
    print(f"Seasonal integrated rows: {len(seasonal_integrated)}")

    print("\nMissing values check:")
    print(missing_values_check)

    # ------------------------------------------------------------
    # Correlation analysis
    # ------------------------------------------------------------

    monthly_corr = compute_correlations(
        dataset=monthly_integrated,
        temporal_scale="Monthly"
    )

    seasonal_corr = compute_correlations(
        dataset=seasonal_integrated,
        temporal_scale="Seasonal"
    )

    all_corr = pd.concat(
        [monthly_corr, seasonal_corr],
        ignore_index=True
    )

    season_stratified_corr = compute_monthly_season_stratified_spearman(
        monthly_integrated=monthly_integrated
    )

    exposure_method_comparison = build_exposure_method_comparison(all_corr)

    save_correlation_outputs(
        monthly_corr=monthly_corr,
        seasonal_corr=seasonal_corr,
        season_stratified_corr=season_stratified_corr,
        exposure_method_comparison=exposure_method_comparison,
        all_corr=all_corr
    )

    # ------------------------------------------------------------
    # Plots
    # ------------------------------------------------------------

    plot_main_scatter(
        dataset=monthly_integrated,
        temporal_scale="Monthly",
        corr_summary=all_corr
    )

    plot_main_scatter(
        dataset=seasonal_integrated,
        temporal_scale="Seasonal",
        corr_summary=all_corr
    )

    plot_standardized_trends(
        dataset=monthly_integrated,
        temporal_scale="Monthly"
    )

    plot_standardized_trends(
        dataset=seasonal_integrated,
        temporal_scale="Seasonal"
    )

    plot_correlation_summary(
        correlation_summary=all_corr,
        temporal_scale="Monthly"
    )

    plot_correlation_summary(
        correlation_summary=all_corr,
        temporal_scale="Seasonal"
    )

    # ------------------------------------------------------------
    # Compact summary
    # ------------------------------------------------------------

    analysis_summary = build_analysis_summary(
        monthly_integrated=monthly_integrated,
        seasonal_integrated=seasonal_integrated,
        correlation_summary=all_corr
    )

    analysis_summary.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_environment_health_integration_summary.csv"),
        index=False,
        sep=";"
    )

    print("\nMain monthly Spearman results - population-weighted exposure:")
    print(
        monthly_corr[
            (monthly_corr["Exposure_method"] == "Population_weighted_mean")
            & (monthly_corr["Correlation_method"] == "Spearman")
        ][
            [
                "Group",
                "Pollutant",
                "Outcome",
                "N",
                "Correlation",
                "P_value",
                "Interpretation",
            ]
        ]
    )

    print("\nMain seasonal Spearman results - population-weighted exposure:")
    print(
        seasonal_corr[
            (seasonal_corr["Exposure_method"] == "Population_weighted_mean")
            & (seasonal_corr["Correlation_method"] == "Spearman")
        ][
            [
                "Group",
                "Pollutant",
                "Outcome",
                "N",
                "Correlation",
                "P_value",
                "Interpretation",
            ]
        ]
    )

    print("\n========================================")
    print("MODARIA ENVIRONMENTAL-HEALTH INTEGRATION COMPLETED")
    print("========================================")
    print(f"Results saved in: {OUTPUT_DIR}")


if __name__ == "__main__":
    run_modaria_environment_health_integration()
