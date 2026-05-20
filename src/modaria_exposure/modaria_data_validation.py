import os
import unicodedata

import numpy as np
import pandas as pd

import warnings


# ============================================================
# GLOBAL SETTINGS
# ============================================================

COMMON_YEARS = [2016, 2017, 2018, 2019, 2023]

POLLUTANTS = ["NO2", "PM25"]

AREA_ORDER = ["Industrial", "Agricultural"]

MODARIA_INPUT_DIR = "Dati/raw/ModariaDataset"

POPULATION_INPUT_DIR = "Dati/raw/population"

OUTPUT_DIR = (
    "Dati/output/4-Modaria exposure/"
    "4.1-Data validation and area aggregation"
)

# Expected municipalities based on the two project areas.
# These names are used only for consistency checks and population matching.
EXPECTED_MUNICIPALITIES = {
    "Industrial": [
        "Borgosatollo",
        "Botticino",
        "Brescia",
        "Castenedolo",
        "Collebeato",
        "Flero",
        "Gussago",
        "Mazzano",
        "Montirone",
        "Nave",
        "Nuvolento",
        "Nuvolera",
        "Rezzato",
        "Roncadelle",
        "San Zeno Naviglio",
        "Villa Carcina",
    ],
    "Agricultural": [
        "Acquanegra Cremonese",
        "Alfianello",
        "Annicco",
        "Azzanello",
        "Barbariga",
        "Bassano Bresciano",
        "Bordolano",
        "Cappella Cantone",
        "Casalbuttano ed Uniti",
        "Castelvisconti",
        "Corte de' Cortesi con Cignone",
        "Corzano",
        "Dello",
        "Genivolta",
        "Longhena",
        "Orzinuovi",
        "Pontevico",
        "Pralboino",
        "Quinzano d'Oglio",
        "San Paolo",
        "Soresina",
    ],
}


# ============================================================
# TEXT AND DATE UTILITIES
# ============================================================

def normalize_text(value):
    """
    Normalize municipality names for safer matching.

    The function:
    - removes accents;
    - removes apostrophes and punctuation;
    - removes spaces;
    - converts everything to lowercase.

    Example:
    "Corte de' Cortesi con Cignone" -> "cortedecortesiconcignone"
    """

    if pd.isna(value):
        return None

    text = str(value).strip().lower()

    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("utf-8")

    for char in ["'", "’", "`", " ", "-", "_", ".", ",", "(", ")"]:
        text = text.replace(char, "")

    return text


def build_expected_municipality_lookup():
    """
    Build a lookup table from normalized municipality names to official names.
    """

    rows = []

    for area, municipalities in EXPECTED_MUNICIPALITIES.items():
        for municipality in municipalities:
            rows.append({
                "Area": area,
                "Municipality": municipality,
                "Municipality_key": normalize_text(municipality),
            })

    return pd.DataFrame(rows)


def selected_date_index():
    """
    Build the complete daily date index for the selected non-COVID years.

    This avoids accidentally including 2020, 2021 or 2022.
    """

    date_ranges = []

    for year in COMMON_YEARS:
        date_ranges.append(
            pd.date_range(
                start=f"{year}-01-01",
                end=f"{year}-12-31",
                freq="D"
            )
        )

    return date_ranges[0].append(date_ranges[1:])


def parse_date_series(series):
    """
    Parse date values in a robust and controlled way.

    This version avoids the pandas warning:
    'Could not infer format, so each element will be parsed individually...'

    It first tries several explicit formats. If some dates remain unparsed,
    it uses format='mixed' when available. If the installed pandas version
    does not support format='mixed', the fallback is executed with the warning
    suppressed because it is intentional and controlled.
    """

    series_as_string = (
        series
        .astype(str)
        .str.strip()
        .str.replace('"', "", regex=False)
        .str.replace("\ufeff", "", regex=False)
    )

    series_as_string = series_as_string.replace(
        ["", "nan", "NaN", "NaT", "None", "null"],
        np.nan
    )

    parsed = pd.Series(
        pd.NaT,
        index=series.index,
        dtype="datetime64[ns]"
    )

    date_formats = [
        "%d/%m/%Y",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H.%M",
        "%d/%m/%Y %H.%M.%S",
        "%d-%m-%Y",
        "%d-%m-%Y %H:%M",
        "%d-%m-%Y %H:%M:%S",
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d",
        "%Y/%m/%d %H:%M",
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
    ]

    for fmt in date_formats:
        missing_mask = parsed.isna() & series_as_string.notna()

        if not missing_mask.any():
            break

        parsed_attempt = pd.to_datetime(
            series_as_string[missing_mask],
            format=fmt,
            errors="coerce"
        )

        parsed.loc[missing_mask] = parsed_attempt

    missing_mask = parsed.isna() & series_as_string.notna()

    if missing_mask.any():
        try:
            parsed_fallback = pd.to_datetime(
                series_as_string[missing_mask],
                format="mixed",
                errors="coerce",
                dayfirst=True
            )

        except TypeError:
            # Compatibility fallback for older pandas versions.
            # The warning is suppressed because this fallback is intentional.
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore",
                    message="Could not infer format.*",
                    category=UserWarning
                )

                parsed_fallback = pd.to_datetime(
                    series_as_string[missing_mask],
                    errors="coerce",
                    dayfirst=True
                )

        parsed.loc[missing_mask] = parsed_fallback

    return parsed


def convert_to_numeric(series):
    """
    Convert concentration values to numeric.

    Handles:
    - decimal comma;
    - invalid values coded as -999;
    - empty strings.
    """

    cleaned = (
        series
        .astype(str)
        .str.strip()
        .str.replace(",", ".", regex=False)
    )

    cleaned = cleaned.replace(
        ["", "nan", "NaN", "None", "null"],
        np.nan
    )

    numeric = pd.to_numeric(cleaned, errors="coerce")

    numeric = numeric.replace(-999, np.nan)

    return numeric


# ============================================================
# MODARIA FILE SCAN
# ============================================================

def parse_modaria_filename(filename):
    """
    Extract municipality and pollutant from file name.

    Expected examples:
    - Brescia_NO2.csv
    - Brescia_PM25.csv
    - AcquanegraCremonese_NO2.csv
    - San Zeno Naviglio_PM25.csv
    """

    stem = os.path.splitext(filename)[0]

    if stem.endswith("_NO2"):
        pollutant = "NO2"
        municipality_raw = stem.replace("_NO2", "")
    elif stem.endswith("_PM25"):
        pollutant = "PM25"
        municipality_raw = stem.replace("_PM25", "")
    else:
        pollutant = None
        municipality_raw = stem

    municipality_key = normalize_text(municipality_raw)

    return municipality_raw, municipality_key, pollutant


def scan_modaria_files():
    """
    Scan ModAria input folders and create a file inventory.
    """

    expected_lookup = build_expected_municipality_lookup()

    rows = []

    for area in AREA_ORDER:
        area_dir = os.path.join(MODARIA_INPUT_DIR, area)

        if not os.path.exists(area_dir):
            raise FileNotFoundError(f"Missing input folder: {area_dir}")

        for filename in os.listdir(area_dir):
            if not filename.lower().endswith(".csv"):
                continue

            municipality_raw, municipality_key, pollutant = parse_modaria_filename(filename)

            matched = expected_lookup[
                (expected_lookup["Area"] == area)
                & (expected_lookup["Municipality_key"] == municipality_key)
            ]

            if len(matched) == 1:
                municipality = matched.iloc[0]["Municipality"]
            else:
                municipality = municipality_raw

            rows.append({
                "Area": area,
                "Municipality": municipality,
                "Municipality_key": municipality_key,
                "Pollutant": pollutant,
                "Filename": filename,
                "Path": os.path.join(area_dir, filename),
            })

    inventory = pd.DataFrame(rows)

    inventory = inventory.sort_values(
        ["Area", "Municipality", "Pollutant"]
    ).reset_index(drop=True)

    return inventory


def check_file_inventory(inventory):
    """
    Check whether all expected municipality-pollutant files are present.
    """

    expected_rows = []

    for area, municipalities in EXPECTED_MUNICIPALITIES.items():
        for municipality in municipalities:
            for pollutant in POLLUTANTS:
                expected_rows.append({
                    "Area": area,
                    "Municipality": municipality,
                    "Municipality_key": normalize_text(municipality),
                    "Pollutant": pollutant,
                })

    expected = pd.DataFrame(expected_rows)

    observed = inventory[
        ["Area", "Municipality_key", "Pollutant", "Filename"]
    ].copy()

    check = expected.merge(
        observed,
        on=["Area", "Municipality_key", "Pollutant"],
        how="left"
    )

    check["File_found"] = check["Filename"].notna()

    return check


# ============================================================
# MODARIA CSV READING
# ============================================================

def find_column_by_name(columns, patterns):
    """
    Find a column whose name contains one of the requested patterns.
    """

    for col in columns:
        col_clean = str(col).strip().lower()

        for pattern in patterns:
            if pattern in col_clean:
                return col

    return None


def read_modaria_csv(path, area, municipality, municipality_key, pollutant):
    """
    Read one ModAria CSV file.

    The function is intentionally robust because ARPA files may contain
    metadata rows before the actual table.

    Output columns:
    Date | Area | Municipality | Municipality_key | Pollutant | Value
    """

    encodings = ["utf-8-sig", "latin1"]
    separators = [";", ",", "\t"]

    best_error = None

    for encoding in encodings:
        for sep in separators:
            for skiprows in range(0, 15):
                try:
                    df = pd.read_csv(
                        path,
                        sep=sep,
                        encoding=encoding,
                        skiprows=skiprows
                    )

                    if df.shape[1] < 2:
                        continue

                    df.columns = [str(col).strip() for col in df.columns]

                    date_col = find_column_by_name(
                        df.columns,
                        patterns=["data", "date", "giorno"]
                    )

                    if date_col is None:
                        # Fallback: try the first column as date column.
                        candidate = df.columns[0]
                        parsed_dates = parse_date_series(df[candidate])

                        if parsed_dates.notna().mean() > 0.7:
                            date_col = candidate

                    if date_col is None:
                        continue

                    value_col = find_column_by_name(
                        df.columns,
                        patterns=["valore", pollutant.lower(), "media", "concentrazione"]
                    )

                    if value_col is None or value_col == date_col:
                        numeric_candidates = []

                        for col in df.columns:
                            if col == date_col:
                                continue

                            col_lower = str(col).lower()

                            if any(excluded in col_lower for excluded in ["id", "codice", "stato"]):
                                continue

                            numeric_values = convert_to_numeric(df[col])
                            n_valid = numeric_values.notna().sum()

                            if n_valid > 0:
                                numeric_candidates.append((col, n_valid))

                        if not numeric_candidates:
                            continue

                        value_col = sorted(
                            numeric_candidates,
                            key=lambda item: item[1],
                            reverse=True
                        )[0][0]

                    parsed = pd.DataFrame({
                        "Date": parse_date_series(df[date_col]),
                        "Value": convert_to_numeric(df[value_col]),
                    })

                    parsed = parsed.dropna(subset=["Date"])

                    parsed["Date"] = parsed["Date"].dt.floor("D")

                    duplicate_dates_before_aggregation = parsed["Date"].duplicated().sum()

                    parsed = (
                        parsed
                        .groupby("Date", as_index=False)["Value"]
                        .mean()
                    )

                    parsed = parsed.dropna(subset=["Value"])

                    parsed["Area"] = area
                    parsed["Municipality"] = municipality
                    parsed["Municipality_key"] = municipality_key
                    parsed["Pollutant"] = pollutant
                    parsed["Source_file"] = os.path.basename(path)
                    parsed["Duplicate_dates_before_daily_aggregation"] = duplicate_dates_before_aggregation

                    parsed = parsed[
                        [
                            "Date",
                            "Area",
                            "Municipality",
                            "Municipality_key",
                            "Pollutant",
                            "Value",
                            "Source_file",
                            "Duplicate_dates_before_daily_aggregation",
                        ]
                    ].copy()

                    return parsed

                except Exception as error:
                    best_error = error
                    continue

    raise ValueError(
        f"Could not correctly read ModAria file: {path}\n"
        f"Last error: {best_error}"
    )


def load_all_modaria_data(inventory):
    """
    Load all ModAria files into one long dataset.
    """

    parts = []

    for _, row in inventory.iterrows():
        if row["Pollutant"] not in POLLUTANTS:
            continue

        data = read_modaria_csv(
            path=row["Path"],
            area=row["Area"],
            municipality=row["Municipality"],
            municipality_key=row["Municipality_key"],
            pollutant=row["Pollutant"]
        )

        parts.append(data)

    if not parts:
        raise ValueError("No ModAria data files were loaded.")

    data = pd.concat(parts, ignore_index=True)

    data["Year"] = data["Date"].dt.year
    data["Month"] = data["Date"].dt.month

    data = data[data["Year"].isin(COMMON_YEARS)].copy()

    data = data.sort_values(
        ["Area", "Municipality", "Pollutant", "Date"]
    ).reset_index(drop=True)

    return data


# ============================================================
# QUALITY CHECKS
# ============================================================

def summarize_modaria_quality(data, inventory_check):
    """
    Build quality-control tables for ModAria data.
    """

    full_date_index = selected_date_index()
    expected_days = len(full_date_index)

    rows = []

    grouped = data.groupby(
        ["Area", "Municipality", "Municipality_key", "Pollutant"],
        observed=True
    )

    for keys, subset in grouped:
        area, municipality, municipality_key, pollutant = keys

        available_dates = pd.DatetimeIndex(subset["Date"].drop_duplicates())
        missing_dates = full_date_index.difference(available_dates)

        rows.append({
            "Area": area,
            "Municipality": municipality,
            "Municipality_key": municipality_key,
            "Pollutant": pollutant,
            "First_date": subset["Date"].min(),
            "Last_date": subset["Date"].max(),
            "Years_present": ", ".join(map(str, sorted(subset["Year"].unique()))),
            "Expected_days_selected_years": expected_days,
            "Available_days": len(available_dates),
            "Missing_days": len(missing_dates),
            "Missing_percentage": round(100 * len(missing_dates) / expected_days, 2),
            "Mean_value": round(subset["Value"].mean(), 3),
            "Median_value": round(subset["Value"].median(), 3),
            "Min_value": round(subset["Value"].min(), 3),
            "Max_value": round(subset["Value"].max(), 3),
            "Duplicate_dates_before_daily_aggregation": int(
                subset["Duplicate_dates_before_daily_aggregation"].max()
            ),
        })

    quality = pd.DataFrame(rows)

    quality = quality.sort_values(
        ["Area", "Municipality", "Pollutant"]
    ).reset_index(drop=True)

    return quality


def build_missing_dates_table(data):
    """
    Build a table with missing dates for each municipality and pollutant.

    This can be useful for debugging if some files have incomplete coverage.
    """

    full_date_index = selected_date_index()

    rows = []

    grouped = data.groupby(
        ["Area", "Municipality", "Municipality_key", "Pollutant"],
        observed=True
    )

    for keys, subset in grouped:
        area, municipality, municipality_key, pollutant = keys

        available_dates = pd.DatetimeIndex(subset["Date"].drop_duplicates())
        missing_dates = full_date_index.difference(available_dates)

        for date in missing_dates:
            rows.append({
                "Area": area,
                "Municipality": municipality,
                "Municipality_key": municipality_key,
                "Pollutant": pollutant,
                "Missing_date": date,
            })

    return pd.DataFrame(rows)


# ============================================================
# WIDE DATASETS
# ============================================================

def build_wide_datasets(data):
    """
    Build wide daily datasets.

    One CSV is produced for each:
    Area × Pollutant

    Columns:
    Date | Year | Month | municipality_1 | municipality_2 | ...
    """

    full_date_index = selected_date_index()

    wide_outputs = {}

    for area in AREA_ORDER:
        for pollutant in POLLUTANTS:
            subset = data[
                (data["Area"] == area)
                & (data["Pollutant"] == pollutant)
            ].copy()

            wide = subset.pivot_table(
                index="Date",
                columns="Municipality",
                values="Value",
                aggfunc="mean",
                observed=True
            )

            wide = wide.reindex(full_date_index)

            wide.index.name = "Date"
            wide = wide.reset_index()

            wide["Year"] = wide["Date"].dt.year
            wide["Month"] = wide["Date"].dt.month

            first_columns = ["Date", "Year", "Month"]
            municipality_columns = [
                col for col in wide.columns
                if col not in first_columns
            ]

            wide = wide[first_columns + sorted(municipality_columns)]

            wide_outputs[(area, pollutant)] = wide

    return wide_outputs


# ============================================================
# POPULATION DATA
# ============================================================

def clean_population_numeric(series):
    """
    Convert ISTAT population values to numeric.

    Handles:
    - thousands separators;
    - decimal comma;
    - empty strings.
    """

    cleaned = (
        series
        .astype(str)
        .str.strip()
        .str.replace('"', "", regex=False)
        .str.replace("\ufeff", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )

    cleaned = cleaned.replace(
        ["", "nan", "NaN", "None", "null"],
        np.nan
    )

    return pd.to_numeric(cleaned, errors="coerce")


def find_total_sex_mask(series):
    """
    Identify rows corresponding to total sex.

    Depending on the ISTAT file, total sex may be coded as:
    - Totale
    - T
    - Total
    """

    normalized = series.apply(normalize_text)

    return normalized.isin([
        "totale",
        "total",
        "t",
        "tot",
    ])


def find_total_age_mask(series):
    """
    Identify rows corresponding to total age.

    Depending on the ISTAT file, total age may be coded as:
    - 999
    - Totale
    - Total
    - TOTALE
    """

    text = series.astype(str).str.strip()

    normalized = text.apply(normalize_text)

    numeric_age = pd.to_numeric(
        text.str.replace("+", "", regex=False),
        errors="coerce"
    )

    return (
        numeric_age.eq(999)
        | normalized.isin([
            "totale",
            "total",
            "t",
            "tot",
            "tutteeta",
            "tutteleeta",
            "allages",
        ])
    )


def get_column_by_possible_names(columns, possible_names):
    """
    Find a column using normalized exact matching first,
    then partial matching.
    """

    normalized_columns = {
        normalize_text(col): col
        for col in columns
    }

    normalized_possible_names = [
        normalize_text(name)
        for name in possible_names
    ]

    for name in normalized_possible_names:
        if name in normalized_columns:
            return normalized_columns[name]

    for normalized_col, original_col in normalized_columns.items():
        for name in normalized_possible_names:
            if name in normalized_col:
                return original_col

    return None


def read_population_file(path, year, province):
    """
    Read one ISTAT population file.

    This function handles the different formats used in the project.

    Key safeguard:
    If a total-age row exists, it is used directly.
    This prevents double counting in 2023 files, where the file may contain
    both single-age rows and an additional total row.
    """

    attempts = [
        {"sep": ",", "skiprows": 0},
        {"sep": ";", "skiprows": 0},
        {"sep": ";", "skiprows": 1},
        {"sep": ",", "skiprows": 1},
    ]

    last_error = None

    for attempt in attempts:
        try:
            df = pd.read_csv(
                path,
                sep=attempt["sep"],
                skiprows=attempt["skiprows"],
                encoding="latin1"
            )

            df.columns = [
                str(col).strip().replace('"', "")
                for col in df.columns
            ]

            municipality_col = get_column_by_possible_names(
                df.columns,
                ["Comune", "Denominazione comune", "Territorio"]
            )

            if municipality_col is None:
                continue

            age_col = get_column_by_possible_names(
                df.columns,
                ["Età", "Eta", "Age"]
            )

            sex_col = get_column_by_possible_names(
                df.columns,
                ["Sesso", "Sex"]
            )

            population_col = get_column_by_possible_names(
                df.columns,
                ["Popolazione", "Totale", "Population"]
            )

            if population_col is None:
                continue

            temp = df.copy()

            temp = temp.rename(
                columns={
                    municipality_col: "Comune",
                    population_col: "Population_raw",
                }
            )

            temp["Population"] = clean_population_numeric(
                temp["Population_raw"]
            )

            temp = temp.dropna(subset=["Comune", "Population"]).copy()

            # --------------------------------------------------------
            # 1. If a sex column exists, keep only total-sex rows.
            #    This avoids summing male + female + total together.
            # --------------------------------------------------------

            if sex_col is not None and sex_col in temp.columns:
                total_sex_mask = find_total_sex_mask(temp[sex_col])

                if total_sex_mask.any():
                    temp = temp[total_sex_mask].copy()

            # --------------------------------------------------------
            # 2. If a total-age row exists, keep only that row.
            #    This is the key correction for 2023 double counting.
            # --------------------------------------------------------

            if age_col is not None and age_col in temp.columns:
                total_age_mask = find_total_age_mask(temp[age_col])

                if total_age_mask.any():
                    temp = temp[total_age_mask].copy()

            # --------------------------------------------------------
            # 3. Aggregate by municipality.
            #    If total-age row was available, this simply keeps the
            #    municipal total.
            #    If not, it sums age classes after total-sex filtering.
            # --------------------------------------------------------

            population = (
                temp
                .groupby("Comune", as_index=False)["Population"]
                .sum()
            )

            population["Year"] = year
            population["Province"] = province
            population["Municipality_key"] = population["Comune"].apply(
                normalize_text
            )

            population = population.rename(
                columns={"Comune": "Population_file_municipality"}
            )

            population = population[
                [
                    "Year",
                    "Province",
                    "Population_file_municipality",
                    "Municipality_key",
                    "Population",
                ]
            ].copy()

            return population

        except Exception as error:
            last_error = error
            continue

    raise ValueError(
        f"Could not read population file: {path}\n"
        f"Last error: {last_error}"
    )


def load_population_data():
    """
    Load all ISTAT population files from Dati/raw/population.
    """

    rows = []

    for filename in os.listdir(POPULATION_INPUT_DIR):
        if not filename.lower().endswith(".csv"):
            continue

        filename_no_ext = os.path.splitext(filename)[0]
        parts = filename_no_ext.split("_")

        if len(parts) != 2:
            continue

        province = parts[0]
        year = int(parts[1])

        if year not in COMMON_YEARS:
            continue

        path = os.path.join(POPULATION_INPUT_DIR, filename)

        population = read_population_file(
            path=path,
            year=year,
            province=province
        )

        rows.append(population)

    if not rows:
        raise ValueError("No population files were loaded.")

    population_data = pd.concat(rows, ignore_index=True)

    return population_data


def build_population_weights(inventory):
    """
    Build population denominators for each study municipality and year.

    Output:
    one row for each Area × Municipality × Year.
    """

    population_data = load_population_data()

    municipalities = inventory[
        ["Area", "Municipality", "Municipality_key"]
    ].drop_duplicates().copy()

    year_table = pd.DataFrame({"Year": COMMON_YEARS})

    municipalities["merge_key"] = 1
    year_table["merge_key"] = 1

    expected_population = municipalities.merge(
        year_table,
        on="merge_key",
        how="outer"
    ).drop(columns="merge_key")

    population_weights = expected_population.merge(
        population_data,
        on=["Year", "Municipality_key"],
        how="left"
    )

    population_weights = population_weights.sort_values(
        ["Area", "Municipality", "Year"]
    ).reset_index(drop=True)

    # ------------------------------------------------------------
    # Internal consistency check.
    # This does not stop the script, but it prints a clear warning
    # if one year is suspiciously larger than the previous years.
    # ------------------------------------------------------------

    area_year_totals = (
        population_weights
        .groupby(["Area", "Year"], as_index=False)["Population"]
        .sum()
    )

    print("\nArea population totals used for weights:")
    print(area_year_totals)

    for area in AREA_ORDER:
        subset = area_year_totals[area_year_totals["Area"] == area].copy()

        if 2019 in subset["Year"].values and 2023 in subset["Year"].values:
            pop_2019 = subset.loc[subset["Year"] == 2019, "Population"].iloc[0]
            pop_2023 = subset.loc[subset["Year"] == 2023, "Population"].iloc[0]

            if pd.notna(pop_2019) and pd.notna(pop_2023):
                ratio = pop_2023 / pop_2019

                if ratio > 1.25:
                    print(
                        f"\nWARNING: suspicious 2023 population for {area}. "
                        f"2023/2019 ratio = {ratio:.2f}. "
                        "This may indicate double counting in the ISTAT file."
                    )

    return population_weights


# ============================================================
# AREA-LEVEL EXPOSURE INDICATORS
# ============================================================

def build_arithmetic_area_mean(data):
    """
    Build daily area-level arithmetic mean exposure.

    For each Date × Area × Pollutant:
    arithmetic mean = mean of available municipal values.
    """

    grouped = (
        data
        .groupby(["Date", "Year", "Month", "Area", "Pollutant"], as_index=False)
        .agg(
            Arithmetic_mean=("Value", "mean"),
            Available_municipalities=("Municipality", "nunique"),
        )
    )

    total_municipalities = (
        data
        .groupby(["Area", "Pollutant"], as_index=False)["Municipality"]
        .nunique()
        .rename(columns={"Municipality": "Total_municipalities"})
    )

    grouped = grouped.merge(
        total_municipalities,
        on=["Area", "Pollutant"],
        how="left"
    )

    grouped["Arithmetic_coverage_percentage"] = (
        grouped["Available_municipalities"]
        / grouped["Total_municipalities"]
        * 100
    ).round(2)

    return grouped


def build_population_weighted_area_mean(data, population_weights):
    """
    Build daily population-weighted area-level exposure.

    For each Date × Area × Pollutant:
    weighted mean = sum(value × municipal population) / sum(municipal population)

    Missing pollutant values are excluded from both numerator and denominator.
    """

    data_with_population = data.merge(
        population_weights[
            [
                "Year",
                "Area",
                "Municipality",
                "Municipality_key",
                "Population",
            ]
        ],
        on=["Year", "Area", "Municipality", "Municipality_key"],
        how="left"
    )

    data_with_population["Weighted_value"] = (
        data_with_population["Value"]
        * data_with_population["Population"]
    )

    grouped = (
        data_with_population
        .dropna(subset=["Value", "Population"])
        .groupby(["Date", "Year", "Month", "Area", "Pollutant"], as_index=False)
        .agg(
            Weighted_sum=("Weighted_value", "sum"),
            Population_available=("Population", "sum"),
            Available_municipalities_pop_weighted=("Municipality", "nunique"),
        )
    )

    grouped["Population_weighted_mean"] = (
        grouped["Weighted_sum"]
        / grouped["Population_available"]
    )

    grouped = grouped.drop(columns=["Weighted_sum"])

    return grouped


def build_daily_area_exposure_summary(arithmetic_mean, population_weighted_mean):
    """
    Merge arithmetic and population-weighted exposure indicators.
    """

    exposure = arithmetic_mean.merge(
        population_weighted_mean,
        on=["Date", "Year", "Month", "Area", "Pollutant"],
        how="left"
    )

    exposure = exposure.sort_values(
        ["Date", "Area", "Pollutant"]
    ).reset_index(drop=True)

    return exposure


def build_daily_area_exposure_wide(exposure):
    """
    Build a compact wide exposure dataset.

    Columns:
    Date | Year | Month | Area |
    NO2_arithmetic_mean | PM25_arithmetic_mean |
    NO2_population_weighted_mean | PM25_population_weighted_mean
    """

    arithmetic = exposure.pivot_table(
        index=["Date", "Year", "Month", "Area"],
        columns="Pollutant",
        values="Arithmetic_mean",
        aggfunc="first",
        observed=True
    ).reset_index()

    arithmetic.columns.name = None

    arithmetic = arithmetic.rename(
        columns={
            "NO2": "NO2_arithmetic_mean",
            "PM25": "PM25_arithmetic_mean",
        }
    )

    weighted = exposure.pivot_table(
        index=["Date", "Year", "Month", "Area"],
        columns="Pollutant",
        values="Population_weighted_mean",
        aggfunc="first",
        observed=True
    ).reset_index()

    weighted.columns.name = None

    weighted = weighted.rename(
        columns={
            "NO2": "NO2_population_weighted_mean",
            "PM25": "PM25_population_weighted_mean",
        }
    )

    wide = arithmetic.merge(
        weighted,
        on=["Date", "Year", "Month", "Area"],
        how="left"
    )

    wide = wide.sort_values(["Date", "Area"]).reset_index(drop=True)

    return wide


# ============================================================
# MAIN FUNCTION
# ============================================================

def run_modaria_data_validation():
    """
    Run Part 4.1: ModAria data validation and area exposure construction.

    This script:
    - reads all ModAria municipal CSV files;
    - identifies area, municipality and pollutant from file names;
    - cleans metadata rows, dates and concentration values;
    - filters the selected non-COVID years;
    - builds a long daily dataset;
    - builds wide daily datasets by area and pollutant;
    - checks data availability and missing dates;
    - loads ISTAT population files;
    - builds arithmetic area mean exposure;
    - builds population-weighted area mean exposure.
    """

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("\n========================================")
    print("MODARIA DATA VALIDATION AND AREA EXPOSURE")
    print("========================================")

    # ------------------------------------------------------------
    # 1. File inventory
    # ------------------------------------------------------------

    inventory = scan_modaria_files()

    inventory.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_file_inventory.csv"),
        index=False,
        sep=";"
    )

    print("\nModAria file inventory:")
    print(inventory)

    print("\nNumber of files found:")
    print(len(inventory))

    inventory_check = check_file_inventory(inventory)

    inventory_check.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_expected_file_check.csv"),
        index=False,
        sep=";"
    )

    print("\nExpected file check:")
    print(inventory_check)

    missing_files = inventory_check[inventory_check["File_found"] == False].copy()

    if len(missing_files) > 0:
        print("\nWARNING: Some expected files are missing:")
        print(missing_files)
    else:
        print("\nAll expected municipality-pollutant files were found.")

    # ------------------------------------------------------------
    # 2. Load and clean all ModAria files
    # ------------------------------------------------------------

    data = load_all_modaria_data(inventory)

    data_output_path = os.path.join(
        OUTPUT_DIR,
        "modaria_daily_long_dataset.csv"
    )

    data.to_csv(
        data_output_path,
        index=False,
        sep=";"
    )

    print("\nLong daily ModAria dataset:")
    print(data.head(30))

    print("\nLong dataset shape:")
    print(data.shape)

    print("\nRows by area and pollutant:")
    print(data.groupby(["Area", "Pollutant"]).size())

    print("\nYears included:")
    print(sorted(data["Year"].unique()))

    print("\nMissing values check:")
    print(data.isna().sum())

    # ------------------------------------------------------------
    # 3. Quality checks
    # ------------------------------------------------------------

    quality = summarize_modaria_quality(
        data=data,
        inventory_check=inventory_check
    )

    quality.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_data_quality_summary.csv"),
        index=False,
        sep=";"
    )

    print("\nModAria data quality summary:")
    print(quality)

    missing_dates = build_missing_dates_table(data)

    missing_dates.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_missing_dates_by_municipality.csv"),
        index=False,
        sep=";"
    )

    print("\nNumber of missing daily records in selected years:")
    print(len(missing_dates))

    # ------------------------------------------------------------
    # 4. Wide datasets by area and pollutant
    # ------------------------------------------------------------

    wide_outputs = build_wide_datasets(data)

    for (area, pollutant), wide in wide_outputs.items():
        filename = f"modaria_daily_wide_{area}_{pollutant}.csv"

        wide.to_csv(
            os.path.join(OUTPUT_DIR, filename),
            index=False,
            sep=";"
        )

    print("\nWide datasets saved for each Area × Pollutant.")

    # ------------------------------------------------------------
    # 5. Population weights
    # ------------------------------------------------------------

    population_weights = build_population_weights(inventory)

    population_weights.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_population_weights.csv"),
        index=False,
        sep=";"
    )

    print("\nPopulation weights:")
    print(population_weights.head(40))

    print("\nMissing population values:")
    print(population_weights["Population"].isna().sum())

    missing_population = population_weights[
        population_weights["Population"].isna()
    ].copy()

    if len(missing_population) > 0:
        print("\nWARNING: Some municipalities have missing population values:")
        print(missing_population)
    else:
        print("\nAll selected municipalities were matched with population data.")

    # ------------------------------------------------------------
    # 6. Area-level arithmetic mean exposure
    # ------------------------------------------------------------

    arithmetic_mean = build_arithmetic_area_mean(data)

    arithmetic_mean.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_daily_area_arithmetic_mean.csv"),
        index=False,
        sep=";"
    )

    print("\nDaily area arithmetic mean exposure:")
    print(arithmetic_mean.head(20))

    # ------------------------------------------------------------
    # 7. Area-level population-weighted exposure
    # ------------------------------------------------------------

    population_weighted_mean = build_population_weighted_area_mean(
        data=data,
        population_weights=population_weights
    )

    population_weighted_mean.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_daily_area_population_weighted_mean.csv"),
        index=False,
        sep=";"
    )

    print("\nDaily area population-weighted exposure:")
    print(population_weighted_mean.head(20))

    # ------------------------------------------------------------
    # 8. Final daily area exposure summary
    # ------------------------------------------------------------

    exposure_summary = build_daily_area_exposure_summary(
        arithmetic_mean=arithmetic_mean,
        population_weighted_mean=population_weighted_mean
    )

    exposure_summary.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_daily_area_exposure_summary_long.csv"),
        index=False,
        sep=";"
    )

    exposure_summary_wide = build_daily_area_exposure_wide(exposure_summary)

    exposure_summary_wide.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_daily_area_exposure_summary_wide.csv"),
        index=False,
        sep=";"
    )

    print("\nFinal daily area exposure summary - long format:")
    print(exposure_summary.head(20))

    print("\nFinal daily area exposure summary - wide format:")
    print(exposure_summary_wide.head(20))

    print("\n========================================")
    print("MODARIA DATA VALIDATION COMPLETED")
    print("========================================")
    print(f"Results saved in: {OUTPUT_DIR}")


if __name__ == "__main__":
    run_modaria_data_validation()