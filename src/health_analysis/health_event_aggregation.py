import os
import re
from glob import glob

import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# GLOBAL SETTINGS
# ============================================================

COMMON_YEARS = [2016, 2017, 2018, 2019, 2023]

HEALTH_INPUT_PATH = "Dati/raw/Health_events_2015_2023.csv"
POPULATION_INPUT_DIR = "Dati/raw/population"
OUTPUT_DIR = "Dati/output/2-Health data/2.2-Health event aggregation"

OUTCOME_MAP = {
    "RESPIRATORIA": "Respiratory",
    "CARDIOCIRCOLATORIA": "Cardiocirculatory"
}

AREA_ORDER = ["Industrial", "Agricultural"]
OUTCOME_ORDER = ["Respiratory", "Cardiocirculatory"]


# ============================================================
# STUDY AREA MUNICIPALITIES
# ============================================================

def get_study_area_municipalities():
    """
    Define the municipalities included in the two study areas.

    The municipalities were obtained from the QGIS shapefiles:
    - Agricultural area: 21 municipalities
    - Industrial area: 16 municipalities

    Municipality codes are stored in 6-digit ISTAT format:
    - Brescia province codes start with 017
    - Cremona province codes start with 019

    These 6-digit codes will be used as the common key between:
    - health events
    - population data
    - study area definition
    """

    data = [
        # -------------------------
        # Agricultural study area
        # -------------------------
        {"Area": "Agricultural", "PROV": "BS", "Municipality": "VEROLAVECCHIA", "Municipality_code": "017196"},
        {"Area": "Agricultural", "PROV": "CR", "Municipality": "CORTE DE' CORTESI CON CIGNONE", "Municipality_code": "019032"},
        {"Area": "Agricultural", "PROV": "CR", "Municipality": "CASTELVISCONTI", "Municipality_code": "019027"},
        {"Area": "Agricultural", "PROV": "CR", "Municipality": "PADERNO PONCHIELLI", "Municipality_code": "019065"},
        {"Area": "Agricultural", "PROV": "BS", "Municipality": "PONTEVICO", "Municipality_code": "017149"},
        {"Area": "Agricultural", "PROV": "CR", "Municipality": "POZZAGLIO ED UNITI", "Municipality_code": "019077"},
        {"Area": "Agricultural", "PROV": "CR", "Municipality": "GENIVOLTA", "Municipality_code": "019047"},
        {"Area": "Agricultural", "PROV": "CR", "Municipality": "CASALMORANO", "Municipality_code": "019022"},
        {"Area": "Agricultural", "PROV": "CR", "Municipality": "PERSICO DOSIMO", "Municipality_code": "019068"},
        {"Area": "Agricultural", "PROV": "CR", "Municipality": "CASALBUTTANO ED UNITI", "Municipality_code": "019016"},
        {"Area": "Agricultural", "PROV": "BS", "Municipality": "BORGO SAN GIACOMO", "Municipality_code": "017020"},
        {"Area": "Agricultural", "PROV": "BS", "Municipality": "QUINZANO D'OGLIO", "Municipality_code": "017159"},
        {"Area": "Agricultural", "PROV": "BS", "Municipality": "VILLACHIARA", "Municipality_code": "017200"},
        {"Area": "Agricultural", "PROV": "CR", "Municipality": "AZZANELLO", "Municipality_code": "019004"},
        {"Area": "Agricultural", "PROV": "CR", "Municipality": "ANNICCO", "Municipality_code": "019003"},
        {"Area": "Agricultural", "PROV": "CR", "Municipality": "ROBECCO D'OGLIO", "Municipality_code": "019085"},
        {"Area": "Agricultural", "PROV": "CR", "Municipality": "OLMENETA", "Municipality_code": "019063"},
        {"Area": "Agricultural", "PROV": "CR", "Municipality": "CASTELVERDE", "Municipality_code": "019026"},
        {"Area": "Agricultural", "PROV": "CR", "Municipality": "SORESINA", "Municipality_code": "019098"},
        {"Area": "Agricultural", "PROV": "CR", "Municipality": "CORTE DE' FRATI", "Municipality_code": "019033"},
        {"Area": "Agricultural", "PROV": "CR", "Municipality": "BORDOLANO", "Municipality_code": "019007"},

        # -------------------------
        # Industrial study area
        # -------------------------
        {"Area": "Industrial", "PROV": "BS", "Municipality": "BRESCIA", "Municipality_code": "017029"},
        {"Area": "Industrial", "PROV": "BS", "Municipality": "REZZATO", "Municipality_code": "017161"},
        {"Area": "Industrial", "PROV": "BS", "Municipality": "CASTEL MELLA", "Municipality_code": "017042"},
        {"Area": "Industrial", "PROV": "BS", "Municipality": "SAN ZENO NAVIGLIO", "Municipality_code": "017173"},
        {"Area": "Industrial", "PROV": "BS", "Municipality": "GUSSAGO", "Municipality_code": "017081"},
        {"Area": "Industrial", "PROV": "BS", "Municipality": "RONCADELLE", "Municipality_code": "017165"},
        {"Area": "Industrial", "PROV": "BS", "Municipality": "COLLEBEATO", "Municipality_code": "017057"},
        {"Area": "Industrial", "PROV": "BS", "Municipality": "FLERO", "Municipality_code": "017072"},
        {"Area": "Industrial", "PROV": "BS", "Municipality": "BOTTICINO", "Municipality_code": "017023"},
        {"Area": "Industrial", "PROV": "BS", "Municipality": "CASTENEDOLO", "Municipality_code": "017043"},
        {"Area": "Industrial", "PROV": "BS", "Municipality": "BORGOSATOLLO", "Municipality_code": "017021"},
        {"Area": "Industrial", "PROV": "BS", "Municipality": "CELLATICA", "Municipality_code": "017048"},
        {"Area": "Industrial", "PROV": "BS", "Municipality": "TORBOLE CASAGLIA", "Municipality_code": "017186"},
        {"Area": "Industrial", "PROV": "BS", "Municipality": "CONCESIO", "Municipality_code": "017061"},
        {"Area": "Industrial", "PROV": "BS", "Municipality": "NAVE", "Municipality_code": "017117"},
        {"Area": "Industrial", "PROV": "BS", "Municipality": "BOVEZZO", "Municipality_code": "017025"},
    ]

    return pd.DataFrame(data)


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def normalize_municipality_code(value):
    """
    Normalize municipality ISTAT codes to 6 digits.

    Examples:
    - 03017029 -> 017029
    - 3017029  -> 017029
    - 017029   -> 017029

    This is useful because different datasets may use different
    code lengths for the same municipality.
    """

    if pd.isna(value):
        return None

    value = str(value).strip()
    value = re.sub(r"\D", "", value)

    if value == "":
        return None

    return value[-6:].zfill(6)


def clean_numeric(value):
    """
    Convert population values to numeric format.

    This function removes possible thousand separators and handles
    values imported as strings.
    """

    if pd.isna(value):
        return None

    value = str(value).strip()
    value = value.replace(".", "")
    value = value.replace(" ", "")
    value = value.replace(",", ".")

    return pd.to_numeric(value, errors="coerce")


def clean_text(value):
    """
    Standardize text values for safer filtering.
    """

    if pd.isna(value):
        return None

    return str(value).strip().upper()


def parse_health_date(date_series):
    """
    Parse dates in the format used in the health dataset, for example:
    01JAN2015:00:00:00.000
    31DEC2023:00:00:00.000
    """

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

    def convert_single_date(value):
        if pd.isna(value):
            return None

        value = str(value).strip().upper()

        pattern = r"(\d{2})([A-Z]{3})(\d{4}):(.*)"
        match = re.match(pattern, value)

        if not match:
            return None

        day = match.group(1)
        month_text = match.group(2)
        year = match.group(3)
        time_part = match.group(4)

        month_number = month_map.get(month_text)

        if month_number is None:
            return None

        return f"{day}-{month_number}-{year} {time_part}"

    converted = date_series.apply(convert_single_date)

    return pd.to_datetime(
        converted,
        format="%d-%m-%Y %H:%M:%S.%f",
        errors="coerce"
    )


def assign_season(month):
    """
    Assign meteorological season based on month number.
    """

    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    else:
        return "Autumn"


def assign_season_year(date):
    """
    Assign season year.

    December is assigned to the following year,
    so Dec 2016 belongs to Winter 2017.
    """

    if date.month == 12:
        return date.year + 1

    return date.year


def infer_year_from_filename(path):
    """
    Extract the year from a filename such as:
    brescia_2016.csv
    cremona_2023.csv
    """

    filename = os.path.basename(path)
    match = re.search(r"(2016|2017|2018|2019|2023)", filename)

    if match:
        return int(match.group(1))

    raise ValueError(f"Could not infer year from filename: {filename}")


def find_column(columns, possible_names):
    """
    Find the first column matching one of the possible names.
    Matching is case-insensitive and ignores leading/trailing spaces.
    """

    normalized = {str(col).strip().lower(): col for col in columns}

    for name in possible_names:
        key = name.strip().lower()
        if key in normalized:
            return normalized[key]

    return None


# ============================================================
# POPULATION DATA LOADING
# ============================================================

def load_single_population_file(path):
    """
    Load one ISTAT population CSV file and return population by municipality.

    Two input formats are supported:

    1. Long format, used for 2016-2018:
       Codice comune | Comune | Età | Sesso | Popolazione

       In this case, population is obtained by summing population values
       where Sesso = Totale.

    2. Wide format, used for 2019 and 2023:
       Codice comune | Comune | ... | Totale

       In this case, the column Totale is used directly.
    """

    year = infer_year_from_filename(path)

    df = pd.read_csv(
        path,
        sep=",",
        encoding="latin1",
        dtype=str
    )

    df.columns = [str(col).strip().replace("\ufeff", "") for col in df.columns]

    code_col = find_column(df.columns, ["Codice comune", "codice comune"])
    municipality_col = find_column(df.columns, ["Comune", "comune"])
    total_col = find_column(df.columns, ["Totale", "totale"])
    sex_col = find_column(df.columns, ["Sesso", "sesso"])
    population_col = find_column(df.columns, ["Popolazione", "popolazione"])
    age_col = find_column(df.columns, ["Età", "Eta", "età", "eta"])

    if code_col is None or municipality_col is None:
        raise ValueError(f"Missing municipality code or municipality name column in {path}")

    # ------------------------------------------------------------
    # Wide format: direct total population column
    # ------------------------------------------------------------
    if total_col is not None:
        pop = df[[code_col, municipality_col, total_col]].copy()
        pop.columns = ["Municipality_code", "Municipality", "Population"]
        pop["Population"] = pop["Population"].apply(clean_numeric)

    # ------------------------------------------------------------
    # Long format: sum across ages for Sesso = Totale
    # ------------------------------------------------------------
    elif sex_col is not None and population_col is not None:
        temp = df.copy()
        temp["Sesso_clean"] = temp[sex_col].apply(clean_text)
        temp["Population"] = temp[population_col].apply(clean_numeric)

        temp = temp[temp["Sesso_clean"] == "TOTALE"].copy()

        # If the file contains an explicit total age row, use it.
        # Otherwise, sum all age-specific rows.
        if age_col is not None:
            temp["Age_clean"] = temp[age_col].apply(clean_text)

            total_age_rows = temp[
                temp["Age_clean"].isin(["TOTALE", "TOTAL", "999", "100 E PIÙ", "100+"])
            ].copy()

            if len(total_age_rows) > 0:
                temp = total_age_rows

        pop = (
            temp.groupby([code_col, municipality_col])["Population"]
            .sum()
            .reset_index()
        )

        pop.columns = ["Municipality_code", "Municipality", "Population"]

    else:
        raise ValueError(
            f"Unsupported population file format for {path}. "
            f"Columns found: {df.columns.tolist()}"
        )

    pop["Year"] = year
    pop["Municipality_code"] = pop["Municipality_code"].apply(normalize_municipality_code)
    pop["Municipality"] = pop["Municipality"].apply(clean_text)

    pop = pop[["Year", "Municipality_code", "Municipality", "Population"]]

    return pop


def load_population_data():
    """
    Load all population CSV files stored in Dati/raw/population.

    The function reads both Brescia and Cremona files for all common years
    and combines them into a single dataframe.
    """

    population_files = sorted(glob(os.path.join(POPULATION_INPUT_DIR, "*.csv")))

    if len(population_files) == 0:
        raise FileNotFoundError(
            f"No population CSV files found in: {POPULATION_INPUT_DIR}"
        )

    all_population = []

    for path in population_files:
        print(f"Loading population file: {os.path.basename(path)}")
        pop = load_single_population_file(path)
        all_population.append(pop)

    population = pd.concat(all_population, ignore_index=True)

    population = population[
        population["Year"].isin(COMMON_YEARS)
    ].copy()

    return population


# ============================================================
# HEALTH DATA LOADING
# ============================================================

def load_and_prepare_health_data():
    """
    Load and clean health event data.

    The function:
    - parses dates
    - normalizes municipality codes
    - keeps common years only
    - keeps valid age values only
    - standardizes event type columns
    """

    df = pd.read_csv(
        HEALTH_INPUT_PATH,
        sep=",",
        encoding="latin1",
        dtype=str
    )

    df.columns = df.columns.str.strip().str.upper()

    required_columns = [
        "UID",
        "MUNICIPALITY",
        "PROV",
        "DATE",
        "TYPE",
        "TYPE_DTL",
        "AGE",
        "COD_ISTATN"
    ]

    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(f"Missing required columns in health dataset: {missing_columns}")

    df["DATE_PARSED"] = parse_health_date(df["DATE"])
    df["Year"] = df["DATE_PARSED"].dt.year
    df["Month"] = df["DATE_PARSED"].dt.month
    df["MonthPeriod"] = df["DATE_PARSED"].dt.to_period("M").dt.to_timestamp()

    df["AGE"] = pd.to_numeric(df["AGE"], errors="coerce")

    df["Municipality_code"] = df["COD_ISTATN"].apply(normalize_municipality_code)
    df["Municipality"] = df["MUNICIPALITY"].apply(clean_text)
    df["PROV"] = df["PROV"].apply(clean_text)
    df["TYPE"] = df["TYPE"].apply(clean_text)
    df["TYPE_DTL"] = df["TYPE_DTL"].apply(clean_text)

    df = df[
        df["DATE_PARSED"].notna()
        & df["Year"].isin(COMMON_YEARS)
        & df["AGE"].notna()
        & df["AGE"].between(0, 100)
    ].copy()

    return df


# ============================================================
# AGGREGATION FUNCTIONS
# ============================================================

def complete_monthly_grid(monthly):
    """
    Complete the monthly dataset with zero-event combinations.

    This ensures that missing combinations of:
    MonthPeriod × Area × Outcome
    are represented with N_events = 0.
    """

    month_periods = pd.date_range(
        start=f"{min(COMMON_YEARS)}-01-01",
        end=f"{max(COMMON_YEARS)}-12-01",
        freq="MS"
    )

    # Keep only months belonging to the selected common years.
    month_periods = [
        period for period in month_periods
        if period.year in COMMON_YEARS
    ]

    full_index = pd.MultiIndex.from_product(
        [month_periods, AREA_ORDER, OUTCOME_ORDER],
        names=["MonthPeriod", "Area", "Outcome"]
    )

    monthly = (
        monthly.set_index(["MonthPeriod", "Area", "Outcome"])
        .reindex(full_index, fill_value=0)
        .reset_index()
    )

    monthly["Year"] = monthly["MonthPeriod"].dt.year
    monthly["Month"] = monthly["MonthPeriod"].dt.month

    return monthly


def complete_annual_grid(annual):
    """
    Complete the annual dataset with zero-event combinations.
    """

    full_index = pd.MultiIndex.from_product(
        [COMMON_YEARS, AREA_ORDER, OUTCOME_ORDER],
        names=["Year", "Area", "Outcome"]
    )

    annual = (
        annual.set_index(["Year", "Area", "Outcome"])
        .reindex(full_index, fill_value=0)
        .reset_index()
    )

    return annual


def add_population_and_rates(df, population_by_area_year, year_column):
    """
    Add population denominators and event rates per 10,000 inhabitants.

    Parameters
    ----------
    df : pandas.DataFrame
        Event count dataframe.
    population_by_area_year : pandas.DataFrame
        Population aggregated by Area and Year.
    year_column : str
        Name of the year column to use for the merge.
        For monthly and annual data this is 'Year'.
        For seasonal data this is 'SeasonYear'.
    """

    population = population_by_area_year.rename(
        columns={"Year": year_column}
    )

    merged = df.merge(
        population,
        on=[year_column, "Area"],
        how="left"
    )

    merged["Rate_per_10000"] = (
        merged["N_events"] / merged["Population"] * 10000
    )

    return merged


# ============================================================
# PLOTTING FUNCTIONS
# ============================================================

def plot_annual_rates(annual_rates, output_dir):
    """
    Plot annual health event rates by area and outcome.

    Missing COVID years are explicitly inserted as NaN values
    so that the line is interrupted between 2019 and 2023.
    """

    full_years = list(range(min(COMMON_YEARS), max(COMMON_YEARS) + 1))

    for outcome in OUTCOME_ORDER:
        subset = annual_rates[annual_rates["Outcome"] == outcome]

        pivot = subset.pivot(
            index="Year",
            columns="Area",
            values="Rate_per_10000"
        )

        pivot = pivot.reindex(full_years)
        pivot = pivot[AREA_ORDER]

        pivot.plot(marker="o", figsize=(9, 5))
        plt.title(f"Annual {outcome.lower()} acute event rate by study area")
        plt.xlabel("Year")
        plt.ylabel("Events per 10,000 inhabitants")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(
            f"{output_dir}/annual_{outcome.lower()}_rate_by_area.png",
            dpi=300
        )
        plt.show()


def plot_monthly_rates(monthly_rates, output_dir):
    """
    Plot monthly health event rates by area and outcome.

    Missing COVID months are explicitly inserted as NaN values
    so that the line is interrupted between 2019 and 2023.
    """

    full_months = pd.date_range(
        start=f"{min(COMMON_YEARS)}-01-01",
        end=f"{max(COMMON_YEARS)}-12-01",
        freq="MS"
    )

    for outcome in OUTCOME_ORDER:
        subset = monthly_rates[monthly_rates["Outcome"] == outcome]

        pivot = subset.pivot(
            index="MonthPeriod",
            columns="Area",
            values="Rate_per_10000"
        )

        pivot = pivot.reindex(full_months)
        pivot = pivot[AREA_ORDER]

        pivot.plot(figsize=(12, 5))
        plt.title(f"Monthly {outcome.lower()} acute event rate by study area")
        plt.xlabel("Date")
        plt.ylabel("Events per 10,000 inhabitants")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(
            f"{output_dir}/monthly_{outcome.lower()}_rate_by_area.png",
            dpi=300
        )
        plt.show()


def plot_population_by_area(population_by_area_year, output_dir):
    """
    Plot population denominators by study area and year.
    """

    pivot = population_by_area_year.pivot(
        index="Year",
        columns="Area",
        values="Population"
    )

    pivot = pivot[AREA_ORDER]

    pivot.plot(kind="bar", figsize=(9, 5))
    plt.title("Population denominator by study area")
    plt.xlabel("Year")
    plt.ylabel("Population")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/population_by_area_year.png", dpi=300)
    plt.show()


# ============================================================
# MAIN ANALYSIS FUNCTION
# ============================================================

def run_health_event_aggregation():
    """
    Aggregate health events by study area and compute rates.

    This script represents Part 2.2 of the project.

    The analysis:
    - uses study areas derived from QGIS shapefiles
    - loads ISTAT municipal population data
    - assigns each health event to Agricultural or Industrial area
    - filters respiratory and cardiocirculatory acute events
    - aggregates events at annual, monthly and seasonal scale
    - computes rates per 10,000 inhabitants
    """

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("\n==============================")
    print("HEALTH EVENT AGGREGATION")
    print("==============================")

    # ------------------------------------------------------------
    # 1. Study area definition
    # ------------------------------------------------------------

    study_areas = get_study_area_municipalities()

    study_areas.to_csv(
        f"{OUTPUT_DIR}/study_area_municipalities.csv",
        index=False,
        sep=";"
    )

    print("\nStudy area municipalities:")
    print(study_areas.groupby("Area")["Municipality_code"].count())

    # ------------------------------------------------------------
    # 2. Population data
    # ------------------------------------------------------------

    population = load_population_data()

    population_selected = population.merge(
        study_areas[["Area", "PROV", "Municipality_code", "Municipality"]],
        on="Municipality_code",
        how="inner",
        suffixes=("_population", "_study_area")
    )

    population_selected.to_csv(
        f"{OUTPUT_DIR}/population_selected_municipalities.csv",
        index=False,
        sep=";"
    )

    population_by_area_year = (
        population_selected
        .groupby(["Year", "Area"])["Population"]
        .sum()
        .reset_index()
        .sort_values(["Year", "Area"])
    )

    population_by_area_year.to_csv(
        f"{OUTPUT_DIR}/population_by_area_year.csv",
        index=False,
        sep=";"
    )

    print("\nPopulation by study area and year:")
    print(population_by_area_year)

    # Check whether all study area municipalities were found
    expected_combinations = len(study_areas) * len(COMMON_YEARS)
    actual_combinations = len(population_selected)

    print("\nPopulation coverage check:")
    print(f"Expected municipality-year combinations: {expected_combinations}")
    print(f"Found municipality-year combinations: {actual_combinations}")

    if actual_combinations != expected_combinations:
        found_codes = set(population_selected["Municipality_code"].unique())
        expected_codes = set(study_areas["Municipality_code"].unique())
        missing_codes = sorted(expected_codes - found_codes)

        print("\nWARNING: Some municipalities may be missing from population data.")
        print(f"Missing municipality codes: {missing_codes}")

    plot_population_by_area(population_by_area_year, OUTPUT_DIR)

    # ------------------------------------------------------------
    # 3. Health event data
    # ------------------------------------------------------------

    health = load_and_prepare_health_data()

    health_area = health.merge(
        study_areas[["Area", "Municipality_code"]],
        on="Municipality_code",
        how="inner"
    )

    print("\nHealth records after assigning study area:")
    print(health_area.shape)
    print(health_area["Area"].value_counts())

    health_area["Outcome"] = health_area["TYPE_DTL"].map(OUTCOME_MAP)

    health_area = health_area[
        (health_area["TYPE"] == "MEDICO ACUTO")
        & (health_area["Outcome"].notna())
    ].copy()

    print("\nSelected acute health events:")
    print(health_area.groupby(["Area", "Outcome"]).size())

    health_area.to_csv(
        f"{OUTPUT_DIR}/health_events_selected_areas_outcomes.csv",
        index=False,
        sep=";"
    )

    # ------------------------------------------------------------
    # 4. Annual aggregation
    # ------------------------------------------------------------

    annual_counts = (
        health_area
        .groupby(["Year", "Area", "Outcome"])
        .size()
        .reset_index(name="N_events")
    )

    annual_counts = complete_annual_grid(annual_counts)

    annual_rates = add_population_and_rates(
        df=annual_counts,
        population_by_area_year=population_by_area_year,
        year_column="Year"
    )

    annual_rates.to_csv(
        f"{OUTPUT_DIR}/annual_health_events_rates_by_area.csv",
        index=False,
        sep=";"
    )

    print("\nAnnual health event rates:")
    print(annual_rates.head())

    # ------------------------------------------------------------
    # 5. Monthly aggregation
    # ------------------------------------------------------------

    monthly_counts = (
        health_area
        .groupby(["MonthPeriod", "Area", "Outcome"])
        .size()
        .reset_index(name="N_events")
    )

    monthly_counts = complete_monthly_grid(monthly_counts)

    monthly_rates = add_population_and_rates(
        df=monthly_counts,
        population_by_area_year=population_by_area_year,
        year_column="Year"
    )

    monthly_rates.to_csv(
        f"{OUTPUT_DIR}/monthly_health_events_rates_by_area.csv",
        index=False,
        sep=";"
    )

    print("\nMonthly health event rates:")
    print(monthly_rates.head())

    # ------------------------------------------------------------
    # 6. Seasonal aggregation
    # ------------------------------------------------------------

    health_area["Season"] = health_area["DATE_PARSED"].dt.month.apply(assign_season)
    health_area["SeasonYear"] = health_area["DATE_PARSED"].apply(assign_season_year)

    # Count available months for each season-year, area and outcome.
    # Complete seasons are required to avoid biased seasonal counts.
    monthly_for_season = (
        health_area
        .groupby(["SeasonYear", "Season", "Month", "Area", "Outcome"])
        .size()
        .reset_index(name="N_events_month")
    )

    season_month_count = (
        monthly_for_season
        .groupby(["SeasonYear", "Season", "Area", "Outcome"])["Month"]
        .nunique()
        .reset_index(name="N_months")
    )

    complete_seasons = season_month_count[
        season_month_count["N_months"] == 3
    ].copy()

    monthly_complete_seasons = monthly_for_season.merge(
        complete_seasons[["SeasonYear", "Season", "Area", "Outcome"]],
        on=["SeasonYear", "Season", "Area", "Outcome"],
        how="inner"
    )

    seasonal_counts = (
        monthly_complete_seasons
        .groupby(["SeasonYear", "Season", "Area", "Outcome"])["N_events_month"]
        .sum()
        .reset_index(name="N_events")
    )

    seasonal_counts = seasonal_counts[
        seasonal_counts["SeasonYear"].isin(COMMON_YEARS)
    ].copy()

    season_order = ["Winter", "Spring", "Summer", "Autumn"]

    seasonal_counts["Season"] = pd.Categorical(
        seasonal_counts["Season"],
        categories=season_order,
        ordered=True
    )

    seasonal_counts = seasonal_counts.sort_values(
        ["SeasonYear", "Season", "Area", "Outcome"]
    )

    seasonal_rates = add_population_and_rates(
        df=seasonal_counts,
        population_by_area_year=population_by_area_year,
        year_column="SeasonYear"
    )

    seasonal_rates.to_csv(
        f"{OUTPUT_DIR}/seasonal_health_events_rates_by_area.csv",
        index=False,
        sep=";"
    )

    print("\nSeasonal health event rates:")
    print(seasonal_rates.head())

    # ------------------------------------------------------------
    # 7. Plot outputs
    # ------------------------------------------------------------

    plot_annual_rates(annual_rates, OUTPUT_DIR)
    plot_monthly_rates(monthly_rates, OUTPUT_DIR)

    # ------------------------------------------------------------
    # 8. Final summary
    # ------------------------------------------------------------

    summary = pd.DataFrame({
        "Indicator": [
            "Common years used",
            "Agricultural municipalities",
            "Industrial municipalities",
            "Population municipality-year combinations expected",
            "Population municipality-year combinations found",
            "Selected health records after area assignment",
            "Selected acute respiratory/cardiocirculatory events",
            "Annual rows",
            "Monthly rows",
            "Seasonal rows"
        ],
        "Value": [
            ", ".join(map(str, COMMON_YEARS)),
            len(study_areas[study_areas["Area"] == "Agricultural"]),
            len(study_areas[study_areas["Area"] == "Industrial"]),
            expected_combinations,
            actual_combinations,
            len(health_area),
            len(health_area),
            len(annual_rates),
            len(monthly_rates),
            len(seasonal_rates)
        ]
    })

    summary.to_csv(
        f"{OUTPUT_DIR}/health_event_aggregation_summary.csv",
        index=False,
        sep=";"
    )

    print("\n==============================")
    print("HEALTH EVENT AGGREGATION COMPLETED")
    print("==============================")
    print(f"Results saved in: {OUTPUT_DIR}")