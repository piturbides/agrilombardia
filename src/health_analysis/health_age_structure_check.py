import os
import re
from glob import glob

import pandas as pd
import matplotlib.pyplot as plt

from src.health_analysis.health_event_aggregation import (
    COMMON_YEARS,
    POPULATION_INPUT_DIR,
    OUTCOME_MAP,
    AREA_ORDER,
    OUTCOME_ORDER,
    get_study_area_municipalities,
    normalize_municipality_code,
    clean_numeric,
    clean_text,
    infer_year_from_filename,
    find_column,
    load_and_prepare_health_data,
)


# ============================================================
# GLOBAL SETTINGS
# ============================================================

OUTPUT_DIR = "Dati/output/2-Health data/2.3-Health age structure check"

AGE_GROUP_ORDER_DETAILED = ["0-44", "45-64", "65-74", "75-84", "85+"]
AGE_GROUP_ORDER_BINARY = ["<65", "65+"]


# ============================================================
# AGE GROUP FUNCTIONS
# ============================================================

def assign_age_group_detailed(age):
    """
    Assign detailed age groups.

    These age groups are used for descriptive analysis.
    They preserve clinically meaningful elderly subgroups while
    avoiding too many small categories.
    """

    if pd.isna(age):
        return None

    age = float(age)

    if age < 0 or age > 100:
        return None
    elif age <= 44:
        return "0-44"
    elif age <= 64:
        return "45-64"
    elif age <= 74:
        return "65-74"
    elif age <= 84:
        return "75-84"
    else:
        return "85+"


def assign_age_group_binary(age):
    """
    Assign binary age groups.

    This is the main sensitivity check:
    - <65: non-elderly population
    - 65+: elderly population, expected to be more vulnerable
    """

    if pd.isna(age):
        return None

    age = float(age)

    if age < 0 or age > 100:
        return None
    elif age < 65:
        return "<65"
    else:
        return "65+"


def assign_age_group_from_population_age(age_value, grouping="binary"):
    """
    Convert an age value from ISTAT population files into a project age group.

    The input may be:
    - numeric age: 0, 1, 2, ..., 99
    - text values such as '100 e più', '100+', 'Totale'

    Total rows are excluded because age-specific denominators must be
    computed by summing age-specific rows or columns.
    """

    if pd.isna(age_value):
        return None

    value = str(age_value).strip().upper()

    if value in ["TOTALE", "TOTAL", "TOTALE GENERALE"]:
        return None

    # Handle values such as "100 e più", "100+", "100 E PIÙ"
    if "100" in value and ("PI" in value or "+" in value):
        age = 100
    else:
        digits = re.findall(r"\d+", value)
        if len(digits) == 0:
            return None
        age = int(digits[0])

    if grouping == "binary":
        return assign_age_group_binary(age)
    elif grouping == "detailed":
        return assign_age_group_detailed(age)
    else:
        raise ValueError(f"Unsupported grouping: {grouping}")


# ============================================================
# POPULATION BY AGE LOADING
# ============================================================

def read_population_csv_flexible(path):
    """
    Read ISTAT population CSV files with flexible format handling.

    Supported cases:
    - comma-separated files without metadata rows
    - semicolon-separated files with a first descriptive row
    - UTF-8 or Latin-1 encoded files

    The function tests different combinations and returns the first
    dataframe in which municipality code and municipality name columns
    are correctly recognized.
    """

    encodings = ["utf-8", "latin1"]
    separators = [",", ";"]
    skiprows_options = [0, 1]

    last_error = None

    for encoding in encodings:
        for sep in separators:
            for skiprows in skiprows_options:
                try:
                    df = pd.read_csv(
                        path,
                        sep=sep,
                        encoding=encoding,
                        dtype=str,
                        skiprows=skiprows
                    )

                    df.columns = [
                        str(col).strip().replace("\ufeff", "")
                        for col in df.columns
                    ]

                    code_col = find_column(
                        df.columns,
                        ["Codice comune", "codice comune"]
                    )
                    municipality_col = find_column(
                        df.columns,
                        ["Comune", "comune"]
                    )

                    if code_col is not None and municipality_col is not None:
                        return df

                except Exception as error:
                    last_error = error

    raise ValueError(
        f"Could not read population file with supported formats: {path}. "
        f"Last error: {last_error}"
    )


def identify_age_columns_wide_format(df):
    """
    Identify age-specific columns in a wide-format ISTAT population file.

    Wide files may contain one column per age, plus a 'Totale' column.
    This function selects columns that look like ages:
    - '0', '1', ..., '99'
    - '100 e più', '100+'
    """

    age_columns = []

    for col in df.columns:
        col_text = str(col).strip().upper()

        if col_text in ["TOTALE", "TOTAL"]:
            continue

        if re.fullmatch(r"\d{1,3}", col_text):
            age = int(col_text)
            if 0 <= age <= 100:
                age_columns.append(col)

        elif "100" in col_text and ("PI" in col_text or "+" in col_text):
            age_columns.append(col)

    return age_columns


def load_single_population_file_by_age(path, grouping="binary"):
    """
    Load one ISTAT population CSV file and return population by:
    Year, Municipality_code, Municipality, Age_group

    Supported input formats:

    1. Long format:
       Codice comune | Comune | Età | Sesso | Popolazione

    2. Long POSAS format:
       Codice comune | Comune | Età | ... | Totale

       This is the format used by ISTAT POSAS files, for example:
       POSAS_2023_it_017_Brescia.csv

    3. Wide format:
       Codice comune | Comune | one column per age | Totale

    The function keeps only total sex when a sex column is present.
    """

    year = infer_year_from_filename(path)

    df = read_population_csv_flexible(path)

    code_col = find_column(df.columns, ["Codice comune", "codice comune"])
    municipality_col = find_column(df.columns, ["Comune", "comune"])
    sex_col = find_column(df.columns, ["Sesso", "sesso"])
    population_col = find_column(df.columns, ["Popolazione", "popolazione"])
    total_col = find_column(df.columns, ["Totale", "totale"])

    age_col = find_column(
        df.columns,
        [
            "Età", "Eta", "età", "eta",
            "EtÃ", "EtÃ\xa0", "etÃ", "etÃ\xa0"
        ]
    )

    if code_col is None or municipality_col is None:
        raise ValueError(
            f"Missing municipality code or municipality name column in {path}"
        )

    # ------------------------------------------------------------
    # Case 1: long format with explicit age and population columns
    # Example:
    # Codice comune | Comune | Età | Sesso | Popolazione
    # ------------------------------------------------------------
    if age_col is not None and population_col is not None:
        temp = df.copy()

        if sex_col is not None:
            temp["Sesso_clean"] = temp[sex_col].apply(clean_text)
            temp = temp[temp["Sesso_clean"] == "TOTALE"].copy()

        temp["Population"] = temp[population_col].apply(clean_numeric)
        temp["Age_group"] = temp[age_col].apply(
            lambda x: assign_age_group_from_population_age(x, grouping=grouping)
        )

        temp = temp[temp["Age_group"].notna()].copy()

        pop_age = (
            temp.groupby([code_col, municipality_col, "Age_group"])["Population"]
            .sum()
            .reset_index()
        )

        pop_age.columns = [
            "Municipality_code",
            "Municipality",
            "Age_group",
            "Population"
        ]

    # ------------------------------------------------------------
    # Case 1B: long POSAS format with explicit age and total columns
    # Example:
    # Codice comune | Comune | Età | ... | Totale
    # ------------------------------------------------------------
    elif age_col is not None and total_col is not None:
        temp = df.copy()

        temp["Population"] = temp[total_col].apply(clean_numeric)
        temp["Age_group"] = temp[age_col].apply(
            lambda x: assign_age_group_from_population_age(x, grouping=grouping)
        )

        temp = temp[temp["Age_group"].notna()].copy()

        pop_age = (
            temp.groupby([code_col, municipality_col, "Age_group"])["Population"]
            .sum()
            .reset_index()
        )

        pop_age.columns = [
            "Municipality_code",
            "Municipality",
            "Age_group",
            "Population"
        ]

    # ------------------------------------------------------------
    # Case 2: wide format with one age column per age
    # ------------------------------------------------------------
    else:
        age_columns = identify_age_columns_wide_format(df)

        if len(age_columns) == 0:
            raise ValueError(
                f"Could not identify age-specific columns in {path}. "
                f"Columns found: {df.columns.tolist()}"
            )

        id_columns = [code_col, municipality_col]

        temp = df[id_columns + age_columns].copy()

        long_df = temp.melt(
            id_vars=id_columns,
            value_vars=age_columns,
            var_name="Age",
            value_name="Population"
        )

        long_df["Population"] = long_df["Population"].apply(clean_numeric)
        long_df["Age_group"] = long_df["Age"].apply(
            lambda x: assign_age_group_from_population_age(x, grouping=grouping)
        )

        long_df = long_df[long_df["Age_group"].notna()].copy()

        pop_age = (
            long_df.groupby([code_col, municipality_col, "Age_group"])["Population"]
            .sum()
            .reset_index()
        )

        pop_age.columns = [
            "Municipality_code",
            "Municipality",
            "Age_group",
            "Population"
        ]

    pop_age["Year"] = year
    pop_age["Municipality_code"] = pop_age["Municipality_code"].apply(
        normalize_municipality_code
    )
    pop_age["Municipality"] = pop_age["Municipality"].apply(clean_text)

    pop_age = pop_age[
        ["Year", "Municipality_code", "Municipality", "Age_group", "Population"]
    ]

    return pop_age


def load_population_data_by_age(grouping="binary"):
    """
    Load all ISTAT population files and aggregate population by age group.
    """

    population_files = sorted(glob(os.path.join(POPULATION_INPUT_DIR, "*.csv")))

    if len(population_files) == 0:
        raise FileNotFoundError(
            f"No population CSV files found in: {POPULATION_INPUT_DIR}"
        )

    all_population = []

    for path in population_files:
        print(f"Loading age-specific population file: {os.path.basename(path)}")
        pop = load_single_population_file_by_age(path, grouping=grouping)
        all_population.append(pop)

    population = pd.concat(all_population, ignore_index=True)

    population = population[
        population["Year"].isin(COMMON_YEARS)
    ].copy()

    return population


# ============================================================
# GRID COMPLETION AND RATES
# ============================================================

def complete_age_annual_grid(annual, age_group_order):
    """
    Complete annual event counts with zero-event combinations.

    This ensures that all combinations of:
    Year × Area × Outcome × Age_group
    are represented.
    """

    full_index = pd.MultiIndex.from_product(
        [COMMON_YEARS, AREA_ORDER, OUTCOME_ORDER, age_group_order],
        names=["Year", "Area", "Outcome", "Age_group"]
    )

    annual = (
        annual.set_index(["Year", "Area", "Outcome", "Age_group"])
        .reindex(full_index, fill_value=0)
        .reset_index()
    )

    return annual


def add_age_specific_population_and_rates(event_counts, population_by_area_year_age):
    """
    Add age-specific population denominators and compute rates.

    Rate per 10,000 inhabitants =
    N_events / age-specific population * 10,000
    """

    merged = event_counts.merge(
        population_by_area_year_age,
        on=["Year", "Area", "Age_group"],
        how="left"
    )

    merged["Rate_per_10000"] = (
        merged["N_events"] / merged["Population"] * 10000
    )

    return merged


def print_population_rate_coverage_check(rates, grouping_name):
    """
    Print a simple check for missing population denominators after the merge.
    """

    missing_population = rates[rates["Population"].isna()].copy()

    print(f"\nPopulation denominator coverage check ({grouping_name}):")
    print(f"Rows in rate table: {len(rates)}")
    print(f"Rows with missing population denominator: {len(missing_population)}")

    if len(missing_population) > 0:
        print("\nWARNING: Missing population denominators found.")
        print(missing_population[["Year", "Area", "Outcome", "Age_group"]].head(20))
    else:
        print("All rate rows have a population denominator.")


# ============================================================
# PLOTTING FUNCTIONS
# ============================================================

def plot_age_distribution_bar(age_summary, output_dir, grouping_name):
    """
    Plot percentage distribution of selected health events by age group and area.
    """

    for outcome in OUTCOME_ORDER:
        subset = age_summary[age_summary["Outcome"] == outcome].copy()

        pivot = subset.pivot(
            index="Age_group",
            columns="Area",
            values="Percentage"
        )

        age_order = (
            AGE_GROUP_ORDER_BINARY
            if grouping_name == "binary"
            else AGE_GROUP_ORDER_DETAILED
        )

        pivot = pivot.reindex(age_order)
        pivot = pivot[AREA_ORDER]

        pivot.plot(kind="bar", figsize=(9, 5))
        plt.title(f"{outcome} acute events: age distribution by study area")
        plt.xlabel("Age group")
        plt.ylabel("Percentage of events (%)")
        plt.xticks(rotation=0)
        plt.grid(axis="y", alpha=0.3)
        plt.tight_layout()
        plt.savefig(
            f"{output_dir}/{grouping_name}_{outcome.lower()}_event_age_distribution_by_area.png",
            dpi=300
        )
        plt.show()


def plot_age_specific_rates(annual_rates, output_dir, grouping_name):
    """
    Plot annual age-specific rates by area, outcome and age group.

    Missing COVID years are explicitly inserted as NaN values so the
    line is interrupted between 2019 and 2023.
    """

    full_years = list(range(min(COMMON_YEARS), max(COMMON_YEARS) + 1))
    age_order = (
        AGE_GROUP_ORDER_BINARY
        if grouping_name == "binary"
        else AGE_GROUP_ORDER_DETAILED
    )

    for outcome in OUTCOME_ORDER:
        for age_group in age_order:
            subset = annual_rates[
                (annual_rates["Outcome"] == outcome)
                & (annual_rates["Age_group"] == age_group)
            ].copy()

            if subset.empty:
                print(
                    f"Skipping plot: no data for {outcome}, "
                    f"age group {age_group}, grouping {grouping_name}"
                )
                continue

            pivot = subset.pivot(
                index="Year",
                columns="Area",
                values="Rate_per_10000"
            )

            pivot = pivot.reindex(full_years)
            pivot = pivot[AREA_ORDER]

            pivot.plot(marker="o", figsize=(9, 5))
            plt.title(
                f"Annual {outcome.lower()} acute event rate, age group {age_group}"
            )
            plt.xlabel("Year")
            plt.ylabel("Events per 10,000 inhabitants")
            plt.grid(True, alpha=0.3)
            plt.tight_layout()

            safe_age_group = (
                age_group
                .replace("+", "plus")
                .replace("<", "under")
            )

            plt.savefig(
                f"{output_dir}/{grouping_name}_{outcome.lower()}_annual_rate_age_{safe_age_group}.png",
                dpi=300
            )
            plt.show()


def plot_mean_age_by_area_outcome(health_area, output_dir):
    """
    Plot mean event age by area and outcome.
    """

    summary = (
        health_area
        .groupby(["Area", "Outcome"])["AGE"]
        .mean()
        .reset_index(name="Mean_age")
    )

    pivot = summary.pivot(
        index="Outcome",
        columns="Area",
        values="Mean_age"
    )

    pivot = pivot.reindex(OUTCOME_ORDER)
    pivot = pivot[AREA_ORDER]

    pivot.plot(kind="bar", figsize=(8, 5))
    plt.title("Mean age of selected acute events by study area")
    plt.xlabel("Outcome")
    plt.ylabel("Mean age")
    plt.xticks(rotation=0)
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/mean_event_age_by_area_outcome.png", dpi=300)
    plt.show()


# ============================================================
# MAIN ANALYSIS FUNCTION
# ============================================================

def run_health_age_structure_check():
    """
    Run Part 2.3: health age structure check.

    This analysis is a sensitivity/refinement step after Part 2.2.

    The goal is to assess whether the different health event rates
    observed between Industrial and Agricultural areas may be influenced
    by age structure.

    Main outputs:
    - age distribution of selected events
    - elderly share of selected events
    - annual age-specific event counts
    - annual age-specific rates using ISTAT age-specific population
      denominators
    """

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("\n==============================")
    print("HEALTH AGE STRUCTURE CHECK")
    print("==============================")

    # ------------------------------------------------------------
    # 1. Load study areas and health data
    # ------------------------------------------------------------

    study_areas = get_study_area_municipalities()

    health = load_and_prepare_health_data()

    health_area = health.merge(
        study_areas[["Area", "Municipality_code"]],
        on="Municipality_code",
        how="inner"
    )

    health_area["Outcome"] = health_area["TYPE_DTL"].map(OUTCOME_MAP)

    health_area = health_area[
        (health_area["TYPE"] == "MEDICO ACUTO")
        & (health_area["Outcome"].notna())
    ].copy()

    health_area["Age_group_binary"] = health_area["AGE"].apply(
        assign_age_group_binary
    )
    health_area["Age_group_detailed"] = health_area["AGE"].apply(
        assign_age_group_detailed
    )

    print("\nSelected acute health events after area assignment:")
    print(health_area.groupby(["Area", "Outcome"]).size())

    # ------------------------------------------------------------
    # 2. Event-level age summaries
    # ------------------------------------------------------------

    age_descriptive_summary = (
        health_area
        .groupby(["Area", "Outcome"])["AGE"]
        .agg(
            N_events="count",
            Mean_age="mean",
            Median_age="median",
            Min_age="min",
            Max_age="max"
        )
        .reset_index()
    )

    age_descriptive_summary.to_csv(
        f"{OUTPUT_DIR}/event_age_descriptive_summary.csv",
        index=False,
        sep=";"
    )

    print("\nEvent age descriptive summary:")
    print(age_descriptive_summary)

    plot_mean_age_by_area_outcome(health_area, OUTPUT_DIR)

    # ------------------------------------------------------------
    # 3. Binary age group event distribution
    # ------------------------------------------------------------

    binary_counts = (
        health_area
        .groupby(["Area", "Outcome", "Age_group_binary"])
        .size()
        .reset_index(name="N_events")
        .rename(columns={"Age_group_binary": "Age_group"})
    )

    binary_totals = (
        binary_counts
        .groupby(["Area", "Outcome"])["N_events"]
        .sum()
        .reset_index(name="Total_events")
    )

    binary_distribution = binary_counts.merge(
        binary_totals,
        on=["Area", "Outcome"],
        how="left"
    )

    binary_distribution["Percentage"] = (
        binary_distribution["N_events"]
        / binary_distribution["Total_events"]
        * 100
    )

    binary_distribution.to_csv(
        f"{OUTPUT_DIR}/binary_age_group_event_distribution.csv",
        index=False,
        sep=";"
    )

    print("\nBinary age group event distribution:")
    print(binary_distribution)

    plot_age_distribution_bar(
        binary_distribution,
        OUTPUT_DIR,
        grouping_name="binary"
    )

    # ------------------------------------------------------------
    # 4. Detailed age group event distribution
    # ------------------------------------------------------------

    detailed_counts = (
        health_area
        .groupby(["Area", "Outcome", "Age_group_detailed"])
        .size()
        .reset_index(name="N_events")
        .rename(columns={"Age_group_detailed": "Age_group"})
    )

    detailed_totals = (
        detailed_counts
        .groupby(["Area", "Outcome"])["N_events"]
        .sum()
        .reset_index(name="Total_events")
    )

    detailed_distribution = detailed_counts.merge(
        detailed_totals,
        on=["Area", "Outcome"],
        how="left"
    )

    detailed_distribution["Percentage"] = (
        detailed_distribution["N_events"]
        / detailed_distribution["Total_events"]
        * 100
    )

    detailed_distribution.to_csv(
        f"{OUTPUT_DIR}/detailed_age_group_event_distribution.csv",
        index=False,
        sep=";"
    )

    print("\nDetailed age group event distribution:")
    print(detailed_distribution)

    plot_age_distribution_bar(
        detailed_distribution,
        OUTPUT_DIR,
        grouping_name="detailed"
    )

    # ------------------------------------------------------------
    # 5. Annual event counts by binary age group
    # ------------------------------------------------------------

    annual_binary_counts = (
        health_area
        .groupby(["Year", "Area", "Outcome", "Age_group_binary"])
        .size()
        .reset_index(name="N_events")
        .rename(columns={"Age_group_binary": "Age_group"})
    )

    annual_binary_counts = complete_age_annual_grid(
        annual_binary_counts,
        AGE_GROUP_ORDER_BINARY
    )

    annual_binary_counts.to_csv(
        f"{OUTPUT_DIR}/annual_health_events_by_binary_age_group.csv",
        index=False,
        sep=";"
    )

    # ------------------------------------------------------------
    # 6. Annual event counts by detailed age group
    # ------------------------------------------------------------

    annual_detailed_counts = (
        health_area
        .groupby(["Year", "Area", "Outcome", "Age_group_detailed"])
        .size()
        .reset_index(name="N_events")
        .rename(columns={"Age_group_detailed": "Age_group"})
    )

    annual_detailed_counts = complete_age_annual_grid(
        annual_detailed_counts,
        AGE_GROUP_ORDER_DETAILED
    )

    annual_detailed_counts.to_csv(
        f"{OUTPUT_DIR}/annual_health_events_by_detailed_age_group.csv",
        index=False,
        sep=";"
    )

    # ------------------------------------------------------------
    # 7. Load age-specific population and compute binary rates
    # ------------------------------------------------------------

    annual_binary_rates = None
    annual_detailed_rates = None

    try:
        population_binary = load_population_data_by_age(grouping="binary")

        population_binary_selected = population_binary.merge(
            study_areas[["Area", "Municipality_code"]],
            on="Municipality_code",
            how="inner"
        )

        population_binary_by_area = (
            population_binary_selected
            .groupby(["Year", "Area", "Age_group"])["Population"]
            .sum()
            .reset_index()
        )

        population_binary_by_area.to_csv(
            f"{OUTPUT_DIR}/population_by_area_year_binary_age_group.csv",
            index=False,
            sep=";"
        )

        annual_binary_rates = add_age_specific_population_and_rates(
            annual_binary_counts,
            population_binary_by_area
        )

        print_population_rate_coverage_check(
            annual_binary_rates,
            grouping_name="binary"
        )

        annual_binary_rates.to_csv(
            f"{OUTPUT_DIR}/annual_health_event_rates_by_binary_age_group.csv",
            index=False,
            sep=";"
        )

        print("\nAnnual age-specific rates, binary age groups:")
        print(annual_binary_rates.head(20))

        plot_age_specific_rates(
            annual_binary_rates,
            OUTPUT_DIR,
            grouping_name="binary"
        )

    except Exception as error:
        print("\nWARNING: Could not compute binary age-specific rates.")
        print("Reason:")
        print(error)
        annual_binary_rates = None

    # ------------------------------------------------------------
    # 8. Load age-specific population and compute detailed rates
    # ------------------------------------------------------------

    try:
        population_detailed = load_population_data_by_age(grouping="detailed")

        population_detailed_selected = population_detailed.merge(
            study_areas[["Area", "Municipality_code"]],
            on="Municipality_code",
            how="inner"
        )

        population_detailed_by_area = (
            population_detailed_selected
            .groupby(["Year", "Area", "Age_group"])["Population"]
            .sum()
            .reset_index()
        )

        population_detailed_by_area.to_csv(
            f"{OUTPUT_DIR}/population_by_area_year_detailed_age_group.csv",
            index=False,
            sep=";"
        )

        annual_detailed_rates = add_age_specific_population_and_rates(
            annual_detailed_counts,
            population_detailed_by_area
        )

        print_population_rate_coverage_check(
            annual_detailed_rates,
            grouping_name="detailed"
        )

        annual_detailed_rates.to_csv(
            f"{OUTPUT_DIR}/annual_health_event_rates_by_detailed_age_group.csv",
            index=False,
            sep=";"
        )

        print("\nAnnual age-specific rates, detailed age groups:")
        print(annual_detailed_rates.head(30))

        plot_age_specific_rates(
            annual_detailed_rates,
            OUTPUT_DIR,
            grouping_name="detailed"
        )

    except Exception as error:
        print("\nWARNING: Could not compute detailed age-specific rates.")
        print("Reason:")
        print(error)
        annual_detailed_rates = None

    # ------------------------------------------------------------
    # 9. Final summary
    # ------------------------------------------------------------

    elderly_share = binary_distribution[
        binary_distribution["Age_group"] == "65+"
    ][["Area", "Outcome", "N_events", "Total_events", "Percentage"]].copy()

    elderly_share = elderly_share.rename(
        columns={
            "N_events": "Events_65plus",
            "Percentage": "Events_65plus_percentage"
        }
    )

    elderly_share.to_csv(
        f"{OUTPUT_DIR}/elderly_event_share_summary.csv",
        index=False,
        sep=";"
    )

    summary = pd.DataFrame({
        "Indicator": [
            "Common years used",
            "Selected health events",
            "Age groups used - main",
            "Age groups used - detailed",
            "Binary age-specific rates computed",
            "Detailed age-specific rates computed",
            "Main interpretation",
            "Main limitation"
        ],
        "Value": [
            ", ".join(map(str, COMMON_YEARS)),
            len(health_area),
            ", ".join(AGE_GROUP_ORDER_BINARY),
            ", ".join(AGE_GROUP_ORDER_DETAILED),
            annual_binary_rates is not None,
            annual_detailed_rates is not None,
            (
                "The Agricultural area showed an older event-age profile than "
                "the Industrial area for both respiratory and cardiocirculatory outcomes."
            ),
            (
                "Age-specific rates are computed using available ISTAT age-specific "
                "municipal population denominators. Results remain ecological and "
                "should not be interpreted as individual-level causal effects."
            )
        ]
    })

    summary.to_csv(
        f"{OUTPUT_DIR}/health_age_structure_check_summary.csv",
        index=False,
        sep=";"
    )

    print("\nElderly event share summary:")
    print(elderly_share)

    print("\n==============================")
    print("HEALTH AGE STRUCTURE CHECK COMPLETED")
    print("==============================")
    print(f"Results saved in: {OUTPUT_DIR}")


if __name__ == "__main__":
    run_health_age_structure_check()