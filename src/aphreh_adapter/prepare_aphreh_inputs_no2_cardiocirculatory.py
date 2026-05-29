"""
Prepare APHREH-ADSMap input files for the NO2 -> Cardiocirculatory pilot.

Pilot:
    Pollutant: NO2
    Outcome: Cardiocirculatory acute events
    Spatial unit / BSA: 37 health-aligned municipalities
    Years: 2016, 2017, 2018, 2019, 2023

Generated files:
    exposure_data.csv
    outcome_data.csv
    BSA.csv
    SRCBSA.csv
    input_validation_summary.csv

Important:
    APHREH-ADSMap reads CSV files with pandas default separator,
    therefore these files are exported with comma separator, not semicolon.

Rationale:
    This run is complementary to the PM2.5 -> Respiratory APHREH analysis.
    NO2 is the pollutant that best separated the Industrial and Agricultural areas
    in the ModAria area comparison, while NO2 -> Cardiocirculatory emerged as one
    of the strongest overall associations in the previous environmental-health
    integration and lag analyses.
"""

from pathlib import Path
import unicodedata
import pandas as pd


# =============================================================================
# Configuration
# =============================================================================

COMMON_YEARS = [2016, 2017, 2018, 2019, 2023]

PILOT_POLLUTANT = "NO2"
PILOT_OUTCOME = "Cardiocirculatory"
PILOT_LABEL = "NO2_Cardiocirculatory"

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODARIA_DAILY_LONG_PATH = (
    PROJECT_ROOT
    / "Dati/output/4-Modaria exposure/4.1-Data validation and area aggregation/modaria_daily_long_dataset.csv"
)

HEALTH_EVENTS_PATH = (
    PROJECT_ROOT
    / "Dati/output/2-Health data/2.2-Health event aggregation/health_events_selected_areas_outcomes.csv"
)

POPULATION_PATH = (
    PROJECT_ROOT
    / "Dati/output/2-Health data/2.2-Health event aggregation/population_selected_municipalities.csv"
)

STUDY_MUNICIPALITIES_PATH = (
    PROJECT_ROOT
    / "Dati/output/2-Health data/2.2-Health event aggregation/study_area_municipalities.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "Dati/output/6-APHREH ADSMap/6.1-Prepared model inputs"
    / PILOT_LABEL
)


# =============================================================================
# Helpers
# =============================================================================

def normalize_municipality_key(value: str) -> str:
    """
    Create a stable municipality key compatible with the ModAria Municipality_key.

    It removes accents, spaces, apostrophes, hyphens and punctuation.
    """
    if pd.isna(value):
        return ""

    value = str(value).strip().lower()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(char for char in value if not unicodedata.combining(char))

    chars_to_remove = [" ", "'", "’", "`", "-", ".", ",", "(", ")", "/"]
    for char in chars_to_remove:
        value = value.replace(char, "")

    return value


def build_selected_dates(years: list[int]) -> pd.DatetimeIndex:
    """
    Build a date index including only selected years.

    This avoids creating artificial dates for 2020-2022.
    """
    all_dates = []

    for year in years:
        year_dates = pd.date_range(f"{year}-01-01", f"{year}-12-31", freq="D")
        all_dates.append(year_dates)

    return all_dates[0].append(all_dates[1:])


def add_datestr_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add DATE_STR as first column, formatted as %y%m%d.

    APHREH expects DATE_STR in this format.
    """
    out = df.copy()
    out.insert(0, "DATE_STR", out.index.strftime("%y%m%d"))
    out = out.reset_index(drop=True)

    return out


def assert_no_missing_columns(
    df: pd.DataFrame,
    required_columns: list[str],
    table_name: str,
) -> None:
    """
    Raise an error if required columns are missing.
    """
    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        raise ValueError(f"{table_name}: missing required columns: {missing}")


# =============================================================================
# Load reference tables
# =============================================================================

def load_study_municipalities() -> pd.DataFrame:
    """
    Load the 37 health-aligned study municipalities.
    """
    study = pd.read_csv(STUDY_MUNICIPALITIES_PATH, sep=";", low_memory=False)

    assert_no_missing_columns(
        study,
        ["Area", "PROV", "Municipality", "Municipality_code"],
        "study_area_municipalities.csv",
    )

    study = study.copy()
    study["Municipality_code"] = study["Municipality_code"].astype(int)
    study["Municipality_key"] = study["Municipality"].apply(normalize_municipality_key)

    if study["Municipality_code"].nunique() != 37:
        raise ValueError(
            f"Expected 37 study municipalities, "
            f"found {study['Municipality_code'].nunique()}."
        )

    if study["Municipality_key"].duplicated().any():
        duplicated = study.loc[
            study["Municipality_key"].duplicated(),
            "Municipality",
        ].tolist()

        raise ValueError(f"Duplicated Municipality_key in study municipalities: {duplicated}")

    return study


# =============================================================================
# Build exposure_data.csv
# =============================================================================

def build_exposure_data(
    study: pd.DataFrame,
    selected_dates: pd.DatetimeIndex,
) -> pd.DataFrame:
    """
    Build wide daily NO2 exposure table.

    Output structure:
        DATE_STR, one column per municipality/BSA.
    """
    modaria = pd.read_csv(MODARIA_DAILY_LONG_PATH, sep=";", low_memory=False)

    assert_no_missing_columns(
        modaria,
        ["Date", "Area", "Municipality", "Municipality_key", "Pollutant", "Value", "Year"],
        "modaria_daily_long_dataset.csv",
    )

    modaria = modaria.copy()
    modaria["Date"] = pd.to_datetime(modaria["Date"])
    modaria["Year"] = modaria["Date"].dt.year
    modaria["Municipality_key"] = modaria["Municipality_key"].astype(str)

    modaria = modaria.loc[
        (modaria["Pollutant"] == PILOT_POLLUTANT)
        & (modaria["Year"].isin(COMMON_YEARS))
    ].copy()

    if modaria.empty:
        raise ValueError(
            f"No ModAria records found for pollutant {PILOT_POLLUTANT} "
            f"and years {COMMON_YEARS}."
        )

    # Map ModAria municipality keys to official study-area municipality codes.
    mapper = study[["Area", "Municipality_key", "Municipality_code"]].copy()

    exposure_long = modaria.merge(
        mapper,
        on=["Area", "Municipality_key"],
        how="left",
        validate="many_to_one",
    )

    unmatched = exposure_long.loc[
        exposure_long["Municipality_code"].isna(),
        ["Area", "Municipality", "Municipality_key"],
    ]

    if not unmatched.empty:
        unmatched_unique = unmatched.drop_duplicates()

        raise ValueError(
            "Some ModAria municipalities could not be matched to study municipalities:\n"
            + unmatched_unique.to_string(index=False)
        )

    exposure_long["Municipality_code"] = exposure_long["Municipality_code"].astype(int)
    exposure_long["Value"] = pd.to_numeric(exposure_long["Value"], errors="coerce")

    exposure_daily = (
        exposure_long
        .groupby(["Date", "Municipality_code"], as_index=False)["Value"]
        .mean()
    )

    exposure_wide = exposure_daily.pivot(
        index="Date",
        columns="Municipality_code",
        values="Value",
    )

    expected_codes = sorted(study["Municipality_code"].unique())
    exposure_wide = exposure_wide.reindex(index=selected_dates, columns=expected_codes)

    missing_values = int(exposure_wide.isna().sum().sum())

    if missing_values > 0:
        missing_by_code = exposure_wide.isna().sum()
        missing_by_code = missing_by_code[missing_by_code > 0]

        raise ValueError(
            f"Exposure data contain {missing_values} missing values. "
            "Missing by municipality:\n"
            + missing_by_code.to_string()
        )

    exposure_wide = exposure_wide.sort_index()
    exposure_out = add_datestr_column(exposure_wide)

    # Column names must be numeric strings for APHREH.
    exposure_out.columns = ["DATE_STR"] + [str(int(col)) for col in exposure_wide.columns]

    return exposure_out


# =============================================================================
# Build outcome_data.csv
# =============================================================================

def build_outcome_data(
    study: pd.DataFrame,
    selected_dates: pd.DatetimeIndex,
) -> pd.DataFrame:
    """
    Build wide daily cardiocirculatory event-count table.

    Output structure:
        DATE_STR, one column per municipality/BSA.

    Values are event counts, not rates.
    """
    health = pd.read_csv(HEALTH_EVENTS_PATH, sep=";", low_memory=False)

    assert_no_missing_columns(
        health,
        ["DATE_PARSED", "Year", "Municipality_code", "Outcome"],
        "health_events_selected_areas_outcomes.csv",
    )

    health = health.copy()
    health["DATE_PARSED"] = pd.to_datetime(health["DATE_PARSED"])
    health["Year"] = health["DATE_PARSED"].dt.year
    health["Municipality_code"] = health["Municipality_code"].astype(int)

    study_codes = set(study["Municipality_code"].astype(int))

    health = health.loc[
        (health["Year"].isin(COMMON_YEARS))
        & (health["Municipality_code"].isin(study_codes))
        & (health["Outcome"] == PILOT_OUTCOME)
    ].copy()

    if health.empty:
        raise ValueError(
            f"No health records found for outcome {PILOT_OUTCOME} "
            f"and years {COMMON_YEARS}."
        )

    outcome_daily = (
        health
        .groupby(["DATE_PARSED", "Municipality_code"])
        .size()
        .reset_index(name="N_events")
    )

    outcome_wide = outcome_daily.pivot(
        index="DATE_PARSED",
        columns="Municipality_code",
        values="N_events",
    )

    expected_codes = sorted(study["Municipality_code"].unique())
    outcome_wide = outcome_wide.reindex(index=selected_dates, columns=expected_codes)

    # No event on a municipality-day means zero, not missing.
    outcome_wide = outcome_wide.fillna(0).astype(int)
    outcome_wide = outcome_wide.sort_index()

    outcome_out = add_datestr_column(outcome_wide)
    outcome_out.columns = ["DATE_STR"] + [str(int(col)) for col in outcome_wide.columns]

    return outcome_out


# =============================================================================
# Build BSA.csv
# =============================================================================

def build_bsa_data(study: pd.DataFrame) -> pd.DataFrame:
    """
    Build APHREH BSA reference grid.

    BSA = municipality.
    """
    population = pd.read_csv(POPULATION_PATH, sep=";", low_memory=False)

    assert_no_missing_columns(
        population,
        ["Year", "Municipality_code", "Municipality_population", "Population", "Area", "PROV"],
        "population_selected_municipalities.csv",
    )

    population = population.copy()
    population["Year"] = population["Year"].astype(int)
    population["Municipality_code"] = population["Municipality_code"].astype(int)
    population["Population"] = population["Population"].astype(int)

    population = population.loc[population["Year"].isin(COMMON_YEARS)].copy()

    pop_wide = population.pivot_table(
        index="Municipality_code",
        columns="Year",
        values="Population",
        aggfunc="first",
    )

    expected_codes = sorted(study["Municipality_code"].unique())
    pop_wide = pop_wide.reindex(expected_codes)

    missing_pop = int(pop_wide.isna().sum().sum())

    if missing_pop > 0:
        raise ValueError(
            f"BSA population table contains {missing_pop} missing POP_YYYY values:\n"
            + pop_wide.isna().sum().to_string()
        )

    pop_wide.columns = [f"POP_{int(year)}" for year in pop_wide.columns]
    pop_wide = pop_wide.astype(int).reset_index()

    bsa = study[["Municipality_code", "Municipality", "Area", "PROV"]].copy()

    bsa = bsa.rename(
        columns={
            "Municipality_code": "BSA",
            "PROV": "Province",
        }
    )

    bsa = bsa.merge(
        pop_wide.rename(columns={"Municipality_code": "BSA"}),
        on="BSA",
        how="left",
        validate="one_to_one",
    )

    # Identity geometry for the pilot.
    # Each municipality has artificial area = 1.
    # This works together with SRCBSA.csv where intersection area is also 1.
    bsa.insert(1, "BSA_AREA", 1.0)

    bsa = bsa.sort_values("BSA").reset_index(drop=True)

    return bsa


# =============================================================================
# Build SRCBSA.csv
# =============================================================================

def build_srcbsa_data(study: pd.DataFrame) -> pd.DataFrame:
    """
    Build identity cross-grid mapping.

    In this pilot:
        source exposure unit = municipality
        BSA analysis unit = municipality

    Therefore each source municipality maps onto itself.
    """
    srcbsa = pd.DataFrame(
        {
            "SRC": study["Municipality_code"].astype(int),
            "BSA": study["Municipality_code"].astype(int),
            "Area": 1.0,
            "BSA_AREA": 1.0,
        }
    )

    srcbsa = srcbsa.sort_values("BSA").reset_index(drop=True)

    return srcbsa


# =============================================================================
# Validation summary
# =============================================================================

def build_validation_summary(
    exposure: pd.DataFrame,
    outcome: pd.DataFrame,
    bsa: pd.DataFrame,
    srcbsa: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build compact validation summary for APHREH input consistency.
    """
    exposure_codes = set(map(int, exposure.columns[1:]))
    outcome_codes = set(map(int, outcome.columns[1:]))
    bsa_codes = set(bsa["BSA"].astype(int))
    src_codes = set(srcbsa["SRC"].astype(int))
    srcbsa_bsa_codes = set(srcbsa["BSA"].astype(int))

    summary = {
        "pilot_label": PILOT_LABEL,
        "pollutant": PILOT_POLLUTANT,
        "outcome": PILOT_OUTCOME,
        "years": ",".join(map(str, COMMON_YEARS)),
        "n_dates_exposure": exposure.shape[0],
        "n_dates_outcome": outcome.shape[0],
        "n_bsa": len(bsa_codes),
        "n_exposure_municipalities": len(exposure_codes),
        "n_outcome_municipalities": len(outcome_codes),
        "n_srcbsa_rows": srcbsa.shape[0],
        "exposure_outcome_same_dates": exposure["DATE_STR"].equals(outcome["DATE_STR"]),
        "exposure_outcome_same_municipalities": exposure_codes == outcome_codes,
        "exposure_bsa_same_municipalities": exposure_codes == bsa_codes,
        "outcome_bsa_same_municipalities": outcome_codes == bsa_codes,
        "src_codes_same_as_bsa": src_codes == bsa_codes,
        "srcbsa_bsa_codes_same_as_bsa": srcbsa_bsa_codes == bsa_codes,
        "srcbsa_has_area": "Area" in srcbsa.columns,
        "srcbsa_has_bsa_area": "BSA_AREA" in srcbsa.columns,
        "exposure_missing_values": int(exposure.drop(columns=["DATE_STR"]).isna().sum().sum()),
        "outcome_missing_values": int(outcome.drop(columns=["DATE_STR"]).isna().sum().sum()),
        "outcome_total_events": int(outcome.drop(columns=["DATE_STR"]).sum().sum()),
    }

    return pd.DataFrame([summary])


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 100)
    print("Preparing APHREH-ADSMap inputs")
    print(f"Pilot: {PILOT_LABEL}")
    print("=" * 100)

    selected_dates = build_selected_dates(COMMON_YEARS)
    study = load_study_municipalities()

    exposure = build_exposure_data(study, selected_dates)
    outcome = build_outcome_data(study, selected_dates)
    bsa = build_bsa_data(study)
    srcbsa = build_srcbsa_data(study)
    validation = build_validation_summary(exposure, outcome, bsa, srcbsa)

    # APHREH expects comma-separated CSV files.
    exposure.to_csv(OUTPUT_DIR / "exposure_data.csv", index=False)
    outcome.to_csv(OUTPUT_DIR / "outcome_data.csv", index=False)
    bsa.to_csv(OUTPUT_DIR / "BSA.csv", index=False)
    srcbsa.to_csv(OUTPUT_DIR / "SRCBSA.csv", index=False)
    validation.to_csv(OUTPUT_DIR / "input_validation_summary.csv", index=False)

    print("\nGenerated files:")
    for path in [
        OUTPUT_DIR / "exposure_data.csv",
        OUTPUT_DIR / "outcome_data.csv",
        OUTPUT_DIR / "BSA.csv",
        OUTPUT_DIR / "SRCBSA.csv",
        OUTPUT_DIR / "input_validation_summary.csv",
    ]:
        print(f"  - {path.relative_to(PROJECT_ROOT)}")

    print("\nValidation summary:")
    print(validation.T.to_string(header=False))

    print("\nDone.")


if __name__ == "__main__":
    main()