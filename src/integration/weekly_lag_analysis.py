import os

import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

from src.data_loader import load_pollution_data


# ============================================================
# GLOBAL SETTINGS
# ============================================================

COMMON_YEARS = [2016, 2017, 2018, 2019, 2023]

LAGS = [0, 1, 2, 3, 4]

AREA_ORDER = ["Industrial", "Agricultural"]

OUTPUT_DIR = (
    "Dati/output/3-Environmental health integration/"
    "3.4-Weekly lag analysis"
)

# ------------------------------------------------------------
# Pollution raw input files
# ------------------------------------------------------------

NO2_RAW_FILES = {
    "Soresina": "Dati/raw/Soresina_NO2_2016_2025.csv",
    "Rezzato": "Dati/raw/Rezzato_NO2_2016_2025.csv",
}

PM25_RAW_FILES = {
    "Soresina": "Dati/raw/Soresina_2016_2025_PM25.csv",
    "Brescia Villaggio Sereno": "Dati/raw/Brescia_VillagioSereno_PM25_2016_2025.csv",
}

NO2_STATION_AREA_MAP = {
    "Soresina": "Agricultural",
    "Rezzato": "Industrial",
}

PM25_STATION_AREA_MAP = {
    "Soresina": "Agricultural",
    "Brescia Villaggio Sereno": "Industrial",
}

# ------------------------------------------------------------
# Health and population input files
# ------------------------------------------------------------

# This file was produced locally in Part 2.2.
# It contains selected health events already assigned to study area and outcome.
HEALTH_SELECTED_EVENTS_PATH = (
    "Dati/output/2-Health data/2.2-Health event aggregation/"
    "health_events_selected_areas_outcomes.csv"
)

# This file is not sensitive and contains annual population denominators.
ANNUAL_HEALTH_RATES_PATH = (
    "Dati/output/2-Health data/2.2-Health event aggregation/"
    "annual_health_events_rates_by_area.csv"
)

POLLUTANT_COLUMNS = ["NO2_mean", "PM25_mean"]

OUTCOME_COLUMNS = [
    "Respiratory_rate_per_10000",
    "Cardiocirculatory_rate_per_10000",
]

OUTCOME_ORDER = ["Respiratory", "Cardiocirculatory"]

VARIABLE_LABELS = {
    "NO2_mean": "Weekly mean NO2",
    "PM25_mean": "Weekly mean PM2.5",
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

    Most project outputs are saved using semicolon separators.
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
    )


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


def add_week_columns(df, date_col):
    """
    Add weekly time columns.

    Weeks are defined as Monday-Sunday intervals.

    WeekStart is the Monday of the week.

    To avoid duplicated cross-year partial weeks, the analysis keeps only
    weeks whose WeekStart year is included in COMMON_YEARS.
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


def week_index(date_series):
    """
    Convert weekly dates to an integer week index.

    This is used to validate lagged values.

    If two WeekStart values are exactly one week apart,
    their week index difference is 1.
    """

    origin = pd.Timestamp("1900-01-01")

    return ((date_series - origin).dt.days // 7)


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
# WEEKLY POLLUTION DATA
# ============================================================

def load_weekly_pollutant(raw_files, pollutant_name, station_area_map):
    """
    Load raw pollutant files and aggregate them to weekly mean values.

    Weekly aggregation:
    - first daily means are computed;
    - then weekly means are computed from daily means.

    Each row of the output represents:
    WeekStart × Area
    """

    all_daily = []

    for station_name, path in raw_files.items():
        pollutant = load_pollution_data(
            path=path,
            station_name=station_name,
            pollutant_name=pollutant_name
        )

        required_columns = ["Data", pollutant_name, "Station"]

        missing_columns = [
            col for col in required_columns
            if col not in pollutant.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Missing columns in pollutant data: {missing_columns}\n"
                f"File: {path}\n"
                f"Available columns: {pollutant.columns.tolist()}"
            )

        pollutant["Data"] = pd.to_datetime(
            pollutant["Data"],
            errors="coerce"
        )

        pollutant[pollutant_name] = pd.to_numeric(
            pollutant[pollutant_name],
            errors="coerce"
        )

        pollutant = pollutant[
            pollutant["Data"].dt.year.isin(COMMON_YEARS)
        ].copy()

        pollutant = pollutant.dropna(
            subset=["Data", pollutant_name]
        ).copy()

        # Daily mean first, to avoid weighting weeks by the number
        # of hourly observations if the raw file is hourly.
        pollutant["Date"] = pollutant["Data"].dt.floor("D")

        daily = (
            pollutant
            .groupby(["Date", "Station"], as_index=False)[pollutant_name]
            .mean()
        )

        daily["Area"] = daily["Station"].map(station_area_map)

        daily = daily[daily["Area"].notna()].copy()

        all_daily.append(daily)

    combined_daily = pd.concat(all_daily, ignore_index=True)

    combined_daily = add_week_columns(
        combined_daily,
        date_col="Date"
    )

    weekly = (
        combined_daily
        .groupby(["WeekStart", "Year", "Week", "Area"], as_index=False)[pollutant_name]
        .mean()
    )

    weekly = weekly.rename(
        columns={
            pollutant_name: f"{pollutant_name}_mean"
        }
    )

    weekly = weekly.sort_values(
        ["WeekStart", "Area"]
    ).reset_index(drop=True)

    return weekly


def load_weekly_pollution_data():
    """
    Load and merge weekly NO2 and PM2.5 datasets.
    """

    no2_weekly = load_weekly_pollutant(
        raw_files=NO2_RAW_FILES,
        pollutant_name="NO2",
        station_area_map=NO2_STATION_AREA_MAP
    )

    pm25_weekly = load_weekly_pollutant(
        raw_files=PM25_RAW_FILES,
        pollutant_name="PM25",
        station_area_map=PM25_STATION_AREA_MAP
    )

    weekly_pollution = no2_weekly.merge(
        pm25_weekly,
        on=["WeekStart", "Year", "Week", "Area"],
        how="outer"
    )

    weekly_pollution = weekly_pollution.sort_values(
        ["WeekStart", "Area"]
    ).reset_index(drop=True)

    return weekly_pollution


# ============================================================
# WEEKLY HEALTH DATA
# ============================================================

def load_population_denominators():
    """
    Load annual population denominators by area.

    The annual health rates file produced in Part 2.2 contains
    population values by Year × Area × Outcome. Since population is
    the same for both outcomes, we keep one unique value per Year × Area.
    """

    population = read_project_csv(ANNUAL_HEALTH_RATES_PATH)

    required_columns = ["Year", "Area", "Population"]

    missing_columns = [
        col for col in required_columns
        if col not in population.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns in annual health rates file: {missing_columns}\n"
            f"Available columns: {population.columns.tolist()}"
        )

    population["Year"] = pd.to_numeric(
        population["Year"],
        errors="coerce"
    )

    population["Area"] = population["Area"].apply(clean_text)

    population["Population"] = pd.to_numeric(
        population["Population"],
        errors="coerce"
    )

    population = (
        population[["Year", "Area", "Population"]]
        .drop_duplicates()
        .dropna()
        .copy()
    )

    population = population[
        population["Year"].isin(COMMON_YEARS)
    ].copy()

    return population


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


def load_selected_health_events():
    """
    Load selected health events produced in Part 2.2.

    Expected minimum columns:
    - one date column;
    - Area;
    - Outcome.

    The function is robust to small differences in date column names.
    """

    health = read_project_csv(HEALTH_SELECTED_EVENTS_PATH)

    date_col = find_column(
        health,
        possible_names=[
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
        possible_names=[
            "Area",
            "StudyArea",
            "Study_area",
            "STUDY_AREA",
        ],
        required=True
    )

    outcome_col = find_column(
        health,
        possible_names=[
            "Outcome",
            "HealthOutcome",
            "Health_outcome",
            "TYPE_DTL",
            "TYPE",
        ],
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
    Build weekly health rates by Area × Outcome.

    Missing weekly event counts are explicitly set to zero.
    """

    health = load_selected_health_events()

    health = add_week_columns(
        health,
        date_col="EventDate"
    )

    weekly_counts = (
        health
        .groupby(["WeekStart", "Year", "Week", "Area", "Outcome"], as_index=False)
        .size()
        .rename(columns={"size": "N_events"})
    )

    # Build complete grid using the weeks available in the integrated pollution timeline.
    grid = []

    for _, row in weekly_time_area_grid.iterrows():
        for outcome in OUTCOME_ORDER:
            grid.append({
                "WeekStart": row["WeekStart"],
                "Year": row["Year"],
                "Week": row["Week"],
                "Area": row["Area"],
                "Outcome": outcome,
            })

    grid = pd.DataFrame(grid)

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


# ============================================================
# WEEKLY INTEGRATED DATASET
# ============================================================

def build_weekly_integrated_dataset():
    """
    Build the weekly environmental-health integrated dataset.

    Each row represents:
    WeekStart × Area
    """

    weekly_pollution = load_weekly_pollution_data()

    weekly_time_area_grid = (
        weekly_pollution[["WeekStart", "Year", "Week", "Area"]]
        .drop_duplicates()
        .copy()
    )

    weekly_health = build_weekly_health_rates(
        weekly_time_area_grid=weekly_time_area_grid
    )

    integrated = weekly_health.merge(
        weekly_pollution,
        on=["WeekStart", "Year", "Week", "Area"],
        how="left"
    )

    integrated = integrated.sort_values(
        ["WeekStart", "Area"]
    ).reset_index(drop=True)

    return integrated


# ============================================================
# WEEKLY LAG CONSTRUCTION
# ============================================================

def add_validated_weekly_lags_for_area(area_data):
    """
    Add lagged pollutant columns for one study area.

    Lagged values are kept only if the lagged week is exactly
    lag weeks before the current week.

    This prevents incorrect links across the 2019-2023 temporal gap.
    """

    area_data = area_data.sort_values("WeekStart").copy()

    current_week_index = week_index(area_data["WeekStart"])

    for lag in LAGS:
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

    Lags are computed separately for each study area.
    """

    lagged_parts = []

    for area in AREA_ORDER:
        area_data = integrated[integrated["Area"] == area].copy()

        area_lagged = add_validated_weekly_lags_for_area(area_data)

        lagged_parts.append(area_lagged)

    lagged = pd.concat(lagged_parts, ignore_index=True)

    lagged = lagged.sort_values(
        ["WeekStart", "Area"]
    ).reset_index(drop=True)

    return lagged


def summarize_lag_availability(lagged):
    """
    Count available non-missing lagged values for each lag, pollutant and area.
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
                    "Lag_weeks": lag,
                    "Available_values": subset[lag_col].notna().sum(),
                    "Missing_values": subset[lag_col].isna().sum(),
                })

    return pd.DataFrame(rows)


# ============================================================
# CORRELATION ANALYSIS
# ============================================================

def compute_weekly_lagged_spearman_correlations(lagged):
    """
    Compute Spearman correlations between weekly lagged pollutant indicators
    and current-week health event rates.
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
                        "Lag_weeks": lag,
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
            ["abs_rho", "Lag_weeks"],
            ascending=[False, True]
        ).iloc[0]

        rows.append({
            "Group": best_row["Group"],
            "Pollutant": best_row["Pollutant"],
            "Pollutant_label": best_row["Pollutant_label"],
            "Outcome": best_row["Outcome"],
            "Outcome_label": best_row["Outcome_label"],
            "Best_lag_weeks": best_row["Lag_weeks"],
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

def plot_rho_vs_weekly_lag(correlation_summary):
    """
    Plot Spearman rho as a function of weekly lag.
    """

    for group in ["Overall"] + AREA_ORDER:
        for pollutant_col in POLLUTANT_COLUMNS:
            for outcome_col in OUTCOME_COLUMNS:
                subset = correlation_summary[
                    (correlation_summary["Group"] == group)
                    & (correlation_summary["Pollutant"] == pollutant_col)
                    & (correlation_summary["Outcome"] == outcome_col)
                ].copy()

                subset = subset.sort_values("Lag_weeks")

                pollutant_label = get_variable_label(pollutant_col)
                outcome_label = get_variable_label(outcome_col)

                plt.figure(figsize=(7, 5))

                plt.plot(
                    subset["Lag_weeks"],
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
                    f"Spearman rho vs weekly lag - {group}\n"
                    f"{pollutant_label} vs {outcome_label}"
                )

                plt.xlabel("Lag in weeks")
                plt.ylabel("Spearman rho")
                plt.grid(True, alpha=0.3)
                plt.tight_layout()

                filename = (
                    f"rho_vs_weekly_lag_{safe_filename(group)}_"
                    f"{safe_filename(pollutant_col)}_vs_"
                    f"{safe_filename(outcome_col)}.png"
                )

                plt.savefig(
                    os.path.join(OUTPUT_DIR, filename),
                    dpi=300
                )

                plt.show()


def plot_weekly_best_lag_scatter(lagged, best_lag_summary):
    """
    Create scatter plots for descriptively strongest weekly lags.
    """

    for _, row in best_lag_summary.iterrows():
        group = row["Group"]
        pollutant_col = row["Pollutant"]
        outcome_col = row["Outcome"]
        lag = int(row["Best_lag_weeks"])

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
            f"Best weekly lag scatter - {group}\n"
            f"{pollutant_label} lag {lag} vs {outcome_label}"
        )

        plt.xlabel(f"{get_variable_unit(pollutant_col)} - lag {lag} week(s)")
        plt.ylabel(get_variable_unit(outcome_col))
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        filename = (
            f"best_weekly_lag_scatter_{safe_filename(group)}_"
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

def summarize_weekly_lag_analysis(integrated, lagged, correlation_summary):
    """
    Create a compact descriptive summary of the weekly lag analysis.
    """

    summary = pd.DataFrame({
        "Indicator": [
            "Temporal scale",
            "Lag values tested",
            "Number of rows in weekly integrated dataset",
            "Number of rows in weekly lagged dataset",
            "Number of areas",
            "Areas",
            "Pollutants",
            "Health outcomes",
            "Maximum N at lag 0",
            "Maximum N at lag 1",
            "Maximum N at lag 2",
            "Maximum N at lag 3",
            "Maximum N at lag 4",
            "Main methodological safeguard",
            "Main interpretation rule",
        ],
        "Value": [
            "Weekly",
            ", ".join(map(str, LAGS)),
            len(integrated),
            len(lagged),
            integrated["Area"].nunique(),
            ", ".join(AREA_ORDER),
            "NO2, PM2.5",
            "Respiratory and cardiocirculatory event rates",
            int(correlation_summary[correlation_summary["Lag_weeks"] == 0]["N"].max()),
            int(correlation_summary[correlation_summary["Lag_weeks"] == 1]["N"].max()),
            int(correlation_summary[correlation_summary["Lag_weeks"] == 2]["N"].max()),
            int(correlation_summary[correlation_summary["Lag_weeks"] == 3]["N"].max()),
            int(correlation_summary[correlation_summary["Lag_weeks"] == 4]["N"].max()),
            (
                "Lagged pollutant values are kept only when the lagged week is "
                "exactly the expected number of weeks before the current health week. "
                "This prevents linking the end of 2019 to the beginning of 2023."
            ),
            (
                "Weekly lagged correlations are exploratory ecological associations. "
                "They should not be interpreted as causal delayed effects."
            ),
        ]
    })

    return summary


# ============================================================
# MAIN FUNCTION
# ============================================================

def run_weekly_lag_analysis():
    """
    Run Part 3.4: weekly lag refinement.

    This analysis:
    - builds weekly pollutant indicators from raw pollution data;
    - builds weekly health event rates from selected health events;
    - integrates weekly pollution and weekly health rates;
    - creates validated weekly lags from lag 0 to lag 4;
    - avoids incorrect temporal links across the 2019-2023 gap;
    - computes Spearman correlations overall and by area;
    - produces rho-vs-lag plots and best-lag scatter plots.
    """

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("\n========================================")
    print("WEEKLY LAG ANALYSIS")
    print("========================================")

    # ------------------------------------------------------------
    # 1. Build weekly integrated dataset
    # ------------------------------------------------------------

    integrated = build_weekly_integrated_dataset()

    integrated_output_path = os.path.join(
        OUTPUT_DIR,
        "weekly_environment_health_integrated_dataset.csv"
    )

    integrated.to_csv(
        integrated_output_path,
        index=False,
        sep=";"
    )

    print("\nWeekly integrated dataset:")
    print(integrated.head(30))

    print("\nWeekly integrated dataset shape:")
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
        os.path.join(OUTPUT_DIR, "weekly_missing_values_check.csv"),
        index=False,
        sep=";"
    )

    # ------------------------------------------------------------
    # 2. Build weekly lagged dataset
    # ------------------------------------------------------------

    lagged = build_weekly_lagged_dataset(integrated)

    lagged_output_path = os.path.join(
        OUTPUT_DIR,
        "weekly_lag_integrated_dataset.csv"
    )

    lagged.to_csv(
        lagged_output_path,
        index=False,
        sep=";"
    )

    print("\nWeekly lagged dataset:")
    print(lagged.head(30))

    print("\nWeekly lagged dataset shape:")
    print(lagged.shape)

    print("\nWeekly lagged missing values check:")
    print(lagged.isna().sum())

    # ------------------------------------------------------------
    # 3. Lag availability check
    # ------------------------------------------------------------

    lag_availability = summarize_lag_availability(lagged)

    lag_availability.to_csv(
        os.path.join(OUTPUT_DIR, "weekly_lag_availability_check.csv"),
        index=False,
        sep=";"
    )

    print("\nWeekly lag availability check:")
    print(lag_availability)

    # ------------------------------------------------------------
    # 4. Spearman correlations
    # ------------------------------------------------------------

    correlation_summary = compute_weekly_lagged_spearman_correlations(lagged)

    correlation_summary.to_csv(
        os.path.join(OUTPUT_DIR, "weekly_lag_spearman_summary.csv"),
        index=False,
        sep=";"
    )

    print("\nWeekly lag Spearman correlation summary:")
    print(correlation_summary)

    # ------------------------------------------------------------
    # 5. Best lag summary
    # ------------------------------------------------------------

    best_lag_summary = summarize_best_lags(correlation_summary)

    best_lag_summary.to_csv(
        os.path.join(OUTPUT_DIR, "weekly_lag_best_lag_summary.csv"),
        index=False,
        sep=";"
    )

    print("\nWeekly best lag summary:")
    print(best_lag_summary)

    # ------------------------------------------------------------
    # 6. Plots
    # ------------------------------------------------------------

    plot_rho_vs_weekly_lag(correlation_summary)

    plot_weekly_best_lag_scatter(
        lagged=lagged,
        best_lag_summary=best_lag_summary
    )

    # ------------------------------------------------------------
    # 7. General summary
    # ------------------------------------------------------------

    summary = summarize_weekly_lag_analysis(
        integrated=integrated,
        lagged=lagged,
        correlation_summary=correlation_summary
    )

    summary.to_csv(
        os.path.join(OUTPUT_DIR, "weekly_lag_analysis_summary.csv"),
        index=False,
        sep=";"
    )

    print("\n========================================")
    print("WEEKLY LAG ANALYSIS COMPLETED")
    print("========================================")
    print(f"Results saved in: {OUTPUT_DIR}")


if __name__ == "__main__":
    run_weekly_lag_analysis()