import os
import unicodedata
import warnings

import numpy as np
import pandas as pd


# ============================================================
# GLOBAL SETTINGS
# ============================================================

COMMON_YEARS = [2016, 2017, 2018, 2019, 2023]

POLLUTANTS = ["NO2", "PM25"]

AREA_ORDER = ["Industrial", "Agricultural"]

# IMPORTANT:
# From this aligned version onward, ModAria must be read from the
# health-aligned folder, not from the old ModariaDataset folder.
MODARIA_INPUT_DIR = "Dati/raw/ModariaDataset_health_aligned"

POPULATION_INPUT_DIR = "Dati/raw/population"

OUTPUT_DIR = (
    "Dati/output/4-Modaria exposure/"
    "4.1-Data validation and area aggregation"
)

# Final health-aligned municipality list.
# This is the definitive list because it matches the 37 municipalities
# covered by the health/QGIS dataset used in Part 2.2.
EXPECTED_MUNICIPALITIES = {
    "Agricultural": [
        "Verolavecchia",
        "Corte de' Cortesi con Cignone",
        "Castelvisconti",
        "Paderno Ponchielli",
        "Pontevico",
        "Pozzaglio ed Uniti",
        "Genivolta",
        "Casalmorano",
        "Persico Dosimo",
        "Casalbuttano ed Uniti",
        "Borgo San Giacomo",
        "Quinzano d'Oglio",
        "Villachiara",
        "Azzanello",
        "Annicco",
        "Robecco d'Oglio",
        "Olmeneta",
        "Castelverde",
        "Soresina",
        "Corte de' Frati",
        "Bordolano",
    ],
    "Industrial": [
        "Brescia",
        "Rezzato",
        "Castel Mella",
        "San Zeno Naviglio",
        "Gussago",
        "Roncadelle",
        "Collebeato",
        "Flero",
        "Botticino",
        "Castenedolo",
        "Borgosatollo",
        "Cellatica",
        "Torbole Casaglia",
        "Concesio",
        "Nave",
        "Bovezzo",
    ],
}

EXPECTED_FILE_COUNTS = {
    "Agricultural": 21 * 2,
    "Industrial": 16 * 2,
}

EXPECTED_TOTAL_FILES = sum(EXPECTED_FILE_COUNTS.values())


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


def build_expected_municipalities_table():
    """
    Build the reference municipality table used throughout Part 4.1.
    """

    rows = []

    for area in AREA_ORDER:
        for municipality in EXPECTED_MUNICIPALITIES[area]:
            rows.append({
                "Area": area,
                "Municipality": municipality,
                "Municipality_key": normalize_text(municipality),
            })

    return pd.DataFrame(rows)


def build_expected_file_table():
    """
    Build the complete expected Area × Municipality × Pollutant table.

    Expected total:
    37 municipalities × 2 pollutants = 74 files.
    """

    rows = []

    for area in AREA_ORDER:
        for municipality in EXPECTED_MUNICIPALITIES[area]:
            for pollutant in POLLUTANTS:
                rows.append({
                    "Area": area,
                    "Municipality": municipality,
                    "Municipality_key": normalize_text(municipality),
                    "Pollutant": pollutant,
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
    - BorgoSanGiacomo_NO2.csv
    - San Zeno Naviglio_PM25.csv
    """

    stem = os.path.splitext(filename)[0]

    if stem.endswith("_NO2"):
        pollutant = "NO2"
        municipality_raw = stem[:-len("_NO2")]
    elif stem.endswith("_PM25"):
        pollutant = "PM25"
        municipality_raw = stem[:-len("_PM25")]
    else:
        pollutant = None
        municipality_raw = stem

    municipality_key = normalize_text(municipality_raw)

    return municipality_raw, municipality_key, pollutant


def scan_modaria_files():
    """
    Scan ModAria health-aligned input folders and create a file inventory.
    """

    if not os.path.exists(MODARIA_INPUT_DIR):
        raise FileNotFoundError(
            f"Missing ModAria input folder: {MODARIA_INPUT_DIR}"
        )

    expected_lookup = build_expected_municipalities_table()

    rows = []

    for area in AREA_ORDER:
        area_dir = os.path.join(MODARIA_INPUT_DIR, area)

        if not os.path.exists(area_dir):
            raise FileNotFoundError(f"Missing input folder: {area_dir}")

        for filename in os.listdir(area_dir):
            if not filename.lower().endswith(".csv"):
                continue

            municipality_raw, municipality_key_raw, pollutant = parse_modaria_filename(filename)

            matched = expected_lookup[
                (expected_lookup["Area"] == area)
                & (expected_lookup["Municipality_key"] == municipality_key_raw)
            ]

            if len(matched) == 1:
                municipality = matched.iloc[0]["Municipality"]
                municipality_key = matched.iloc[0]["Municipality_key"]
                matched_expected = True
            else:
                municipality = municipality_raw
                municipality_key = municipality_key_raw
                matched_expected = False

            rows.append({
                "Area": area,
                "Municipality": municipality,
                "Municipality_key": municipality_key,
                "Raw_municipality_from_filename": municipality_raw,
                "Raw_municipality_key_from_filename": municipality_key_raw,
                "Pollutant": pollutant,
                "Filename": filename,
                "Path": os.path.join(area_dir, filename),
                "Matched_expected_municipality": matched_expected,
            })

    inventory = pd.DataFrame(rows)

    if inventory.empty:
        raise ValueError(
            f"No CSV files were found in {MODARIA_INPUT_DIR}."
        )

    inventory = inventory.sort_values(
        ["Area", "Municipality", "Pollutant", "Filename"]
    ).reset_index(drop=True)

    return inventory


def check_file_inventory(inventory):
    """
    Check whether all expected Area × Municipality × Pollutant files are present.
    """

    expected = build_expected_file_table()

    observed = inventory[
        inventory["Pollutant"].isin(POLLUTANTS)
    ].copy()

    observed_summary = (
        observed
        .groupby(["Area", "Municipality_key", "Pollutant"], as_index=False)
        .agg(
            File_count=("Filename", "count"),
            Filename=("Filename", lambda x: " | ".join(sorted(x))),
            Path=("Path", lambda x: " | ".join(sorted(x))),
        )
    )

    check = expected.merge(
        observed_summary,
        on=["Area", "Municipality_key", "Pollutant"],
        how="left"
    )

    check["File_count"] = check["File_count"].fillna(0).astype(int)
    check["File_found"] = check["File_count"] > 0
    check["Duplicated_file_pair"] = check["File_count"] > 1

    check = check.sort_values(
        ["Area", "Municipality", "Pollutant"]
    ).reset_index(drop=True)

    return check


def validate_file_inventory(inventory, inventory_check):
    """
    Strictly validate the ModAria health-aligned file inventory.

    The script must stop if:
    - the number of CSV files is not 74;
    - one area has the wrong number of files;
    - at least one expected municipality-pollutant file is missing;
    - at least one extra municipality is present;
    - at least one file has an invalid pollutant suffix;
    - duplicates exist for the same Area × Municipality × Pollutant.
    """

    errors = []

    # ------------------------------------------------------------
    # 1. Total number of files
    # ------------------------------------------------------------

    if len(inventory) != EXPECTED_TOTAL_FILES:
        errors.append(
            f"Expected {EXPECTED_TOTAL_FILES} CSV files, but found {len(inventory)}."
        )

    # ------------------------------------------------------------
    # 2. Files per area
    # ------------------------------------------------------------

    area_counts = (
        inventory
        .groupby("Area")
        .size()
        .to_dict()
    )

    for area, expected_count in EXPECTED_FILE_COUNTS.items():
        observed_count = area_counts.get(area, 0)

        if observed_count != expected_count:
            errors.append(
                f"{area}: expected {expected_count} files, found {observed_count}."
            )

    # ------------------------------------------------------------
    # 3. Invalid pollutant suffix
    # ------------------------------------------------------------

    invalid_pollutant = inventory[
        ~inventory["Pollutant"].isin(POLLUTANTS)
    ].copy()

    if len(invalid_pollutant) > 0:
        errors.append(
            "Some files do not end with a valid pollutant suffix "
            "(_NO2.csv or _PM25.csv):\n"
            f"{invalid_pollutant[['Area', 'Filename']].to_string(index=False)}"
        )

    # ------------------------------------------------------------
    # 4. Extra/unmatched municipalities
    # ------------------------------------------------------------

    unmatched = inventory[
        inventory["Matched_expected_municipality"] == False
    ].copy()

    if len(unmatched) > 0:
        errors.append(
            "Some files refer to municipalities that are not in the "
            "health-aligned list:\n"
            f"{unmatched[['Area', 'Filename', 'Raw_municipality_from_filename']].to_string(index=False)}"
        )

    # ------------------------------------------------------------
    # 5. Missing expected files
    # ------------------------------------------------------------

    missing_files = inventory_check[
        inventory_check["File_found"] == False
    ].copy()

    if len(missing_files) > 0:
        errors.append(
            "Some expected Area × Municipality × Pollutant files are missing:\n"
            f"{missing_files[['Area', 'Municipality', 'Pollutant']].to_string(index=False)}"
        )

    # ------------------------------------------------------------
    # 6. Duplicated expected pairs
    # ------------------------------------------------------------

    duplicated_pairs = inventory_check[
        inventory_check["Duplicated_file_pair"] == True
    ].copy()

    if len(duplicated_pairs) > 0:
        errors.append(
            "Some Area × Municipality × Pollutant pairs have duplicated files:\n"
            f"{duplicated_pairs[['Area', 'Municipality', 'Pollutant', 'Filename']].to_string(index=False)}"
        )

    # ------------------------------------------------------------
    # 7. Unique municipality counts
    # ------------------------------------------------------------

    valid_inventory = inventory[
        inventory["Pollutant"].isin(POLLUTANTS)
        & (inventory["Matched_expected_municipality"] == True)
    ].copy()

    municipality_counts = (
        valid_inventory
        .drop_duplicates(["Area", "Municipality_key"])
        .groupby("Area")
        .size()
        .to_dict()
    )

    expected_municipality_counts = {
        area: len(municipalities)
        for area, municipalities in EXPECTED_MUNICIPALITIES.items()
    }

    for area, expected_count in expected_municipality_counts.items():
        observed_count = municipality_counts.get(area, 0)

        if observed_count != expected_count:
            errors.append(
                f"{area}: expected {expected_count} unique municipalities, "
                f"found {observed_count}."
            )

    if errors:
        message = (
            "\nMODARIA HEALTH-ALIGNED FILE VALIDATION FAILED\n"
            "Fix the input folder before running Part 4.1.\n\n"
            + "\n\n".join(errors)
        )

        raise ValueError(message)

    print("\nFile inventory validation passed.")
    print(f"Total CSV files found: {len(inventory)}")
    print("Files by area:")
    print(inventory.groupby("Area").size())
    print("Unique municipalities by area:")
    print(
        valid_inventory
        .drop_duplicates(["Area", "Municipality_key"])
        .groupby("Area")
        .size()
    )


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

    The function is intentionally robust because ARPA/ModAria files may contain
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
                        candidate = df.columns[0]
                        parsed_dates = parse_date_series(df[candidate])

                        if parsed_dates.notna().mean() > 0.7:
                            date_col = candidate

                    if date_col is None:
                        continue

                    value_col = find_column_by_name(
                        df.columns,
                        patterns=[
                            "valore",
                            pollutant.lower(),
                            "media",
                            "concentrazione",
                            "value",
                        ]
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

                    if parsed.empty:
                        continue

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

    valid_inventory = inventory[
        inventory["Pollutant"].isin(POLLUTANTS)
        & (inventory["Matched_expected_municipality"] == True)
    ].copy()

    for _, row in valid_inventory.iterrows():
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


def validate_loaded_modaria_data(data):
    """
    Validate loaded ModAria data after filtering to COMMON_YEARS.
    """

    errors = []

    if data.empty:
        errors.append("Loaded ModAria dataset is empty after filtering to COMMON_YEARS.")

    observed_years = sorted(data["Year"].dropna().unique().tolist())

    if observed_years != COMMON_YEARS:
        errors.append(
            f"Expected years {COMMON_YEARS}, but loaded years are {observed_years}."
        )

    expected = build_expected_file_table()

    observed = (
        data
        .groupby(["Area", "Municipality_key", "Pollutant"], as_index=False)
        .agg(
            Loaded_rows=("Value", "count"),
            First_date=("Date", "min"),
            Last_date=("Date", "max"),
        )
    )

    loaded_check = expected.merge(
        observed,
        on=["Area", "Municipality_key", "Pollutant"],
        how="left"
    )

    loaded_check["Loaded_rows"] = loaded_check["Loaded_rows"].fillna(0).astype(int)

    missing_loaded_groups = loaded_check[
        loaded_check["Loaded_rows"] == 0
    ].copy()

    if len(missing_loaded_groups) > 0:
        errors.append(
            "Some expected Area × Municipality × Pollutant groups have no loaded data "
            "after filtering to COMMON_YEARS:\n"
            f"{missing_loaded_groups[['Area', 'Municipality', 'Pollutant']].to_string(index=False)}"
        )

    if errors:
        message = (
            "\nMODARIA LOADED DATA VALIDATION FAILED\n\n"
            + "\n\n".join(errors)
        )

        raise ValueError(message)

    print("\nLoaded ModAria data validation passed.")
    print("Rows by area and pollutant:")
    print(data.groupby(["Area", "Pollutant"]).size())

    return loaded_check


# ============================================================
# QUALITY CHECKS
# ============================================================

def summarize_modaria_quality(data):
    """
    Build quality-control table for ModAria data.
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

    columns = [
        "Area",
        "Municipality",
        "Municipality_key",
        "Pollutant",
        "Missing_date",
    ]

    return pd.DataFrame(rows, columns=columns)


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

            if sex_col is not None and sex_col in temp.columns:
                total_sex_mask = find_total_sex_mask(temp[sex_col])

                if total_sex_mask.any():
                    temp = temp[total_sex_mask].copy()

            if age_col is not None and age_col in temp.columns:
                total_age_mask = find_total_age_mask(temp[age_col])

                if total_age_mask.any():
                    temp = temp[total_age_mask].copy()

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


def build_population_weights():
    """
    Build population denominators for each health-aligned study municipality and year.

    Output:
    one row for each Area × Municipality × Year.
    """

    population_data = load_population_data()

    municipalities = build_expected_municipalities_table()

    year_table = pd.DataFrame({"Year": COMMON_YEARS})

    municipalities["merge_key"] = 1
    year_table["merge_key"] = 1

    expected_population = municipalities.merge(
        year_table,
        on="merge_key",
        how="outer"
    ).drop(columns="merge_key")

    selected_keys = expected_population["Municipality_key"].drop_duplicates()

    selected_population_data = population_data[
        population_data["Municipality_key"].isin(selected_keys)
    ].copy()

    duplicated_population_keys = (
        selected_population_data
        .groupby(["Year", "Municipality_key"])
        .size()
        .reset_index(name="N_matches")
    )

    duplicated_population_keys = duplicated_population_keys[
        duplicated_population_keys["N_matches"] > 1
    ].copy()

    if len(duplicated_population_keys) > 0:
        raise ValueError(
            "Duplicated population matches were found for some "
            "Year × Municipality_key pairs. Check population input files:\n"
            f"{duplicated_population_keys.to_string(index=False)}"
        )

    population_weights = expected_population.merge(
        population_data,
        on=["Year", "Municipality_key"],
        how="left"
    )

    population_weights = population_weights.sort_values(
        ["Area", "Municipality", "Year"]
    ).reset_index(drop=True)

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


def validate_population_weights(population_weights):
    """
    Validate that all selected municipalities have population values
    for all selected years.
    """

    missing_population = population_weights[
        population_weights["Population"].isna()
    ].copy()

    if len(missing_population) > 0:
        raise ValueError(
            "Some selected municipalities have missing population values:\n"
            f"{missing_population[['Area', 'Municipality', 'Year']].to_string(index=False)}"
        )

    duplicated_rows = (
        population_weights
        .groupby(["Area", "Municipality_key", "Year"])
        .size()
        .reset_index(name="N")
    )

    duplicated_rows = duplicated_rows[duplicated_rows["N"] > 1].copy()

    if len(duplicated_rows) > 0:
        raise ValueError(
            "Duplicated rows found in population weights:\n"
            f"{duplicated_rows.to_string(index=False)}"
        )

    print("\nPopulation weights validation passed.")
    print("Population rows:", len(population_weights))
    print("Expected population rows:", 37 * len(COMMON_YEARS))


# ============================================================
# AREA-LEVEL EXPOSURE INDICATORS
# ============================================================

def build_arithmetic_area_mean(data):
    """
    Build daily area-level arithmetic mean exposure.

    For each Date × Area × Pollutant:
    arithmetic mean = mean of available municipal values.

    This is kept as descriptive/sensitivity indicator.
    """

    grouped = (
        data
        .groupby(["Date", "Year", "Month", "Area", "Pollutant"], as_index=False)
        .agg(
            Arithmetic_mean=("Value", "mean"),
            Available_municipalities=("Municipality", "nunique"),
        )
    )

    expected_counts = (
        build_expected_municipalities_table()
        .groupby("Area", as_index=False)["Municipality"]
        .nunique()
        .rename(columns={"Municipality": "Total_municipalities"})
    )

    grouped = grouped.merge(
        expected_counts,
        on="Area",
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

    This remains the main exposure indicator.
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

    missing_population_after_merge = data_with_population[
        data_with_population["Population"].isna()
    ].copy()

    if len(missing_population_after_merge) > 0:
        raise ValueError(
            "Population is missing after merging ModAria data with population weights:\n"
            f"{missing_population_after_merge[['Area', 'Municipality', 'Year']].drop_duplicates().to_string(index=False)}"
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

    This health-aligned version:
    - reads only Dati/raw/ModariaDataset_health_aligned;
    - uses the 37 municipalities covered by the health dataset;
    - checks that exactly 74 ModAria CSV files are present;
    - stops if extra/missing/duplicated municipality-pollutant files exist;
    - filters to selected non-COVID years;
    - builds long and wide daily municipal datasets;
    - builds arithmetic and population-weighted area exposure indicators.
    """

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("\n========================================")
    print("MODARIA DATA VALIDATION AND AREA EXPOSURE")
    print("HEALTH-ALIGNED VERSION")
    print("========================================")

    print(f"\nInput folder: {MODARIA_INPUT_DIR}")
    print(f"Expected total files: {EXPECTED_TOTAL_FILES}")
    print(f"Expected files by area: {EXPECTED_FILE_COUNTS}")

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

    validate_file_inventory(
        inventory=inventory,
        inventory_check=inventory_check
    )

    # ------------------------------------------------------------
    # 2. Load and clean all ModAria files
    # ------------------------------------------------------------

    data = load_all_modaria_data(inventory)

    loaded_check = validate_loaded_modaria_data(data)

    loaded_check.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_loaded_data_check.csv"),
        index=False,
        sep=";"
    )

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

    quality = summarize_modaria_quality(data)

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

    population_weights = build_population_weights()

    validate_population_weights(population_weights)

    population_weights.to_csv(
        os.path.join(OUTPUT_DIR, "modaria_population_weights.csv"),
        index=False,
        sep=";"
    )

    print("\nPopulation weights:")
    print(population_weights.head(40))

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