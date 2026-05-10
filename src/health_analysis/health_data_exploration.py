import os
import re

import pandas as pd
import matplotlib.pyplot as plt


COVID_YEARS = [2020, 2021, 2022]

SELECTED_MUNICIPALITIES = ["SORESINA", "REZZATO", "BRESCIA"]
SELECTED_PROVINCES = ["BS", "CR"]


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
    Winter = December, January, February.
    Spring = March, April, May.
    Summer = June, July, August.
    Autumn = September, October, November.
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


def clean_text_columns(df, columns):
    """
    Standardize text columns by stripping spaces and converting to uppercase.
    """
    for column in columns:
        if column in df.columns:
            df[column] = df[column].astype(str).str.strip().str.upper()

    return df


def save_count_table(series, output_path, index_name, count_name):
    """
    Save a value_counts table as CSV.
    """
    table = (
        series.value_counts(dropna=False)
        .rename_axis(index_name)
        .reset_index(name=count_name)
    )

    table.to_csv(output_path, index=False, sep=";")
    return table


def run_health_data_exploration():
    """
    Exploratory analysis of health event data.

    The goal is to understand:
    - dataset structure
    - available years
    - available municipalities/provinces
    - event types
    - age distribution
    - respiratory acute event counts
    - cardiocirculatory acute event counts
    """

    # =========================
    # 1. PATHS
    # =========================

    input_path = "Dati/raw/Health_events_2015_2023.csv"
    output_dir = "Dati/output/2-Health data/2.1-Health data exploration"

    os.makedirs(output_dir, exist_ok=True)

    # =========================
    # 2. LOAD DATA
    # =========================

    df = pd.read_csv(
        input_path,
        sep=",",
        encoding="latin1",
        dtype=str
    )

    df.columns = df.columns.str.strip().str.upper()

    print("\n==============================")
    print("HEALTH DATA EXPLORATION")
    print("==============================")

    print("\nColumns found:")
    print(df.columns.tolist())

    print("\nRaw dataset shape:")
    print(df.shape)

    # =========================
    # 3. BASIC CLEANING
    # =========================

    text_columns = [
        "MUNICIPALITY",
        "PROV",
        "CODE",
        "TYPE",
        "TYPE_DTL",
        "NOME_PRO"
    ]

    df = clean_text_columns(df, text_columns)

    df["DATE_PARSED"] = parse_health_date(df["DATE"])
    df["YEAR_PARSED"] = df["DATE_PARSED"].dt.year
    df["MONTH"] = df["DATE_PARSED"].dt.month
    df["MONTH_PERIOD"] = df["DATE_PARSED"].dt.to_period("M").dt.to_timestamp()

    df["AGE"] = pd.to_numeric(df["AGE"], errors="coerce")

    print("\nParsed date range:")
    print(f"Min date: {df['DATE_PARSED'].min()}")
    print(f"Max date: {df['DATE_PARSED'].max()}")

    # =========================
    # 4. MISSING VALUES SUMMARY
    # =========================

    missing_summary = pd.DataFrame({
        "Column": df.columns,
        "Missing values": df.isna().sum().values,
        "Missing percentage": (df.isna().mean().values * 100).round(2)
    })

    missing_summary.to_csv(
        f"{output_dir}/missing_values_summary.csv",
        index=False,
        sep=";"
    )

    print("\nMissing values summary:")
    print(missing_summary)

    # =========================
    # 5. DATASET OVERVIEW
    # =========================

    available_years = sorted(df["YEAR_PARSED"].dropna().astype(int).unique())

    overview = pd.DataFrame({
        "Indicator": [
            "Total raw records",
            "Valid parsed dates",
            "Minimum date",
            "Maximum date",
            "Available years",
            "Available provinces",
            "Available municipalities",
            "Records with missing age",
            "Records with age > 100"
        ],
        "Value": [
            len(df),
            df["DATE_PARSED"].notna().sum(),
            df["DATE_PARSED"].min(),
            df["DATE_PARSED"].max(),
            ", ".join(map(str, available_years)),
            df["PROV"].nunique(dropna=True),
            df["MUNICIPALITY"].nunique(dropna=True),
            df["AGE"].isna().sum(),
            (df["AGE"] > 100).sum()
        ]
    })

    overview.to_csv(
        f"{output_dir}/health_dataset_overview.csv",
        index=False,
        sep=";"
    )

    print("\nDataset overview:")
    print(overview)

    # =========================
    # 6. GENERAL COUNT TABLES
    # =========================

    events_by_year = (
        df.groupby("YEAR_PARSED")
        .size()
        .reset_index(name="N_events")
        .sort_values("YEAR_PARSED")
    )

    events_by_year.to_csv(
        f"{output_dir}/events_by_year_all.csv",
        index=False,
        sep=";"
    )

    save_count_table(
        df["PROV"],
        f"{output_dir}/events_by_province_all.csv",
        index_name="Province",
        count_name="N_events"
    )

    events_by_municipality = save_count_table(
        df["MUNICIPALITY"],
        f"{output_dir}/events_by_municipality_all.csv",
        index_name="Municipality",
        count_name="N_events"
    )

    events_by_municipality.head(50).to_csv(
        f"{output_dir}/events_by_municipality_top50_all.csv",
        index=False,
        sep=";"
    )

    save_count_table(
        df["TYPE"],
        f"{output_dir}/events_by_type_all.csv",
        index_name="Type",
        count_name="N_events"
    )

    events_by_type_detail = save_count_table(
        df["TYPE_DTL"],
        f"{output_dir}/events_by_type_detail_all.csv",
        index_name="Type_detail",
        count_name="N_events"
    )

    print("\nEvents by year:")
    print(events_by_year)

    print("\nTop event details:")
    print(events_by_type_detail.head(20))

    # =========================
    # 7. AGE CLEANING
    # =========================

    df_age_clean = df[
        df["AGE"].notna()
        & df["AGE"].between(0, 100)
        & df["DATE_PARSED"].notna()
    ].copy()

    print("\nDataset after age/date cleaning:")
    print(df_age_clean.shape)

    age_stats = df_age_clean["AGE"].describe().round(2)

    age_stats.to_csv(
        f"{output_dir}/age_descriptive_statistics.csv",
        sep=";"
    )

    plt.figure(figsize=(8, 5))
    plt.hist(df_age_clean["AGE"], bins=40, alpha=0.8)
    plt.title("Age distribution of health events")
    plt.xlabel("Age")
    plt.ylabel("Number of events")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/age_distribution_all_events.png", dpi=300)
    plt.show()

    # =========================
    # 8. REMOVE COVID YEARS
    # =========================

    df_non_covid = df_age_clean[
        ~df_age_clean["YEAR_PARSED"].isin(COVID_YEARS)
    ].copy()

    print("\nDataset after excluding COVID years 2020-2022:")
    print(df_non_covid.shape)

    included_years = sorted(df_non_covid["YEAR_PARSED"].dropna().astype(int).unique())
    print(f"Included years: {included_years}")

    # Keep only selected valid provinces for province-level comparisons.
    # This removes anomalous or non-informative province codes such as "0".
    df_non_covid_selected_provinces = df_non_covid[
        df_non_covid["PROV"].isin(SELECTED_PROVINCES)
    ].copy()

    print("\nDataset after keeping only selected provinces BS and CR:")
    print(df_non_covid_selected_provinces.shape)
    print(df_non_covid_selected_provinces["PROV"].value_counts())

    events_by_year_non_covid = (
        df_non_covid.groupby("YEAR_PARSED")
        .size()
        .reset_index(name="N_events")
        .sort_values("YEAR_PARSED")
    )

    events_by_year_non_covid.to_csv(
        f"{output_dir}/events_by_year_non_covid.csv",
        index=False,
        sep=";"
    )

    plt.figure(figsize=(8, 5))
    plt.bar(
        events_by_year_non_covid["YEAR_PARSED"],
        events_by_year_non_covid["N_events"]
    )
    plt.title("Health events by year, excluding COVID years")
    plt.xlabel("Year")
    plt.ylabel("Number of events")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/events_by_year_non_covid.png", dpi=300)
    plt.show()

    # =========================
    # 9. RESPIRATORY ACUTE EVENTS
    # =========================

    respiratory = df_non_covid_selected_provinces[
        (df_non_covid_selected_provinces["TYPE"] == "MEDICO ACUTO")
        & (df_non_covid_selected_provinces["TYPE_DTL"] == "RESPIRATORIA")
    ].copy()

    print("\nRespiratory acute events:")
    print(respiratory.shape)

    respiratory_by_year = (
        respiratory.groupby("YEAR_PARSED")
        .size()
        .reset_index(name="N_respiratory_events")
        .sort_values("YEAR_PARSED")
    )

    respiratory_by_year.to_csv(
        f"{output_dir}/respiratory_acute_events_by_year.csv",
        index=False,
        sep=";"
    )

    respiratory_by_province = (
        respiratory.groupby("PROV")
        .size()
        .reset_index(name="N_respiratory_events")
        .sort_values("N_respiratory_events", ascending=False)
    )

    respiratory_by_province.to_csv(
        f"{output_dir}/respiratory_acute_events_by_province.csv",
        index=False,
        sep=";"
    )

    respiratory_by_municipality = (
        respiratory.groupby(["PROV", "MUNICIPALITY"])
        .size()
        .reset_index(name="N_respiratory_events")
        .sort_values("N_respiratory_events", ascending=False)
    )

    respiratory_by_municipality.to_csv(
        f"{output_dir}/respiratory_acute_events_by_municipality.csv",
        index=False,
        sep=";"
    )

    respiratory_by_municipality.head(50).to_csv(
        f"{output_dir}/respiratory_acute_events_by_municipality_top50.csv",
        index=False,
        sep=";"
    )

    respiratory_monthly_by_province = (
        respiratory.groupby(["MONTH_PERIOD", "YEAR_PARSED", "MONTH", "PROV"])
        .size()
        .reset_index(name="N_respiratory_events")
        .sort_values(["MONTH_PERIOD", "PROV"])
    )

    respiratory_monthly_by_province.to_csv(
        f"{output_dir}/respiratory_acute_monthly_by_province.csv",
        index=False,
        sep=";"
    )

    respiratory_selected_municipalities = respiratory[
        respiratory["MUNICIPALITY"].isin(SELECTED_MUNICIPALITIES)
    ].copy()

    respiratory_monthly_selected_municipalities = (
        respiratory_selected_municipalities
        .groupby(["MONTH_PERIOD", "YEAR_PARSED", "MONTH", "PROV", "MUNICIPALITY"])
        .size()
        .reset_index(name="N_respiratory_events")
        .sort_values(["MONTH_PERIOD", "MUNICIPALITY"])
    )

    respiratory_monthly_selected_municipalities.to_csv(
        f"{output_dir}/respiratory_acute_monthly_selected_municipalities.csv",
        index=False,
        sep=";"
    )

    respiratory_year_province_pivot = respiratory.pivot_table(
        index="YEAR_PARSED",
        columns="PROV",
        values="UID",
        aggfunc="count",
        fill_value=0
    )
    respiratory_year_province_pivot = respiratory_year_province_pivot[SELECTED_PROVINCES]

    respiratory_year_province_pivot.to_csv(
        f"{output_dir}/respiratory_acute_events_by_year_and_province.csv",
        sep=";"
    )

    respiratory_year_province_pivot.plot(kind="bar", figsize=(9, 5))
    plt.title("Respiratory acute events by year and province")
    plt.xlabel("Year")
    plt.ylabel("Number of respiratory acute events")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/respiratory_acute_events_by_year_and_province.png", dpi=300)
    plt.show()

    # =========================
    # 10. SEASONAL RESPIRATORY EVENTS
    # =========================

    respiratory["SEASON"] = respiratory["DATE_PARSED"].dt.month.apply(assign_season)
    respiratory["SEASON_YEAR"] = respiratory["DATE_PARSED"].apply(assign_season_year)

    respiratory_seasonal_by_province = (
        respiratory.groupby(["SEASON_YEAR", "SEASON", "PROV"])
        .size()
        .reset_index(name="N_respiratory_events")
        .sort_values(["SEASON_YEAR", "SEASON", "PROV"])
    )

    respiratory_seasonal_by_province.to_csv(
        f"{output_dir}/respiratory_acute_seasonal_by_province.csv",
        index=False,
        sep=";"
    )

    # =========================
    # 11. CARDIOCIRCULATORY EVENTS
    # =========================

    cardiocirculatory = df_non_covid_selected_provinces[
        (df_non_covid_selected_provinces["TYPE"] == "MEDICO ACUTO")
        & (df_non_covid_selected_provinces["TYPE_DTL"] == "CARDIOCIRCOLATORIA")
    ].copy()

    print("\nCardiocirculatory acute events:")
    print(cardiocirculatory.shape)

    cardiocirculatory_by_year = (
        cardiocirculatory.groupby("YEAR_PARSED")
        .size()
        .reset_index(name="N_cardiocirculatory_events")
        .sort_values("YEAR_PARSED")
    )

    cardiocirculatory_by_year.to_csv(
        f"{output_dir}/cardiocirculatory_acute_events_by_year.csv",
        index=False,
        sep=";"
    )

    cardiocirculatory_by_province = (
        cardiocirculatory.groupby("PROV")
        .size()
        .reset_index(name="N_cardiocirculatory_events")
        .sort_values("N_cardiocirculatory_events", ascending=False)
    )

    cardiocirculatory_by_province.to_csv(
        f"{output_dir}/cardiocirculatory_acute_events_by_province.csv",
        index=False,
        sep=";"
    )

    # =========================
    # 12. FINAL SUMMARY
    # =========================

    final_summary = pd.DataFrame({
        "Indicator": [
            "Records after age/date cleaning",
            "Records after excluding COVID years",
            "Records after excluding COVID years and keeping only BS/CR",
            "Respiratory acute events, non-COVID, BS/CR only",
            "Cardiocirculatory acute events, non-COVID, BS/CR only",
            "Selected municipalities used for focused checks",
            "Selected provinces used for focused checks"
        ],
        "Value": [
            len(df_age_clean),
            len(df_non_covid),
            len(df_non_covid_selected_provinces),
            len(respiratory),
            len(cardiocirculatory),
            ", ".join(SELECTED_MUNICIPALITIES),
            ", ".join(SELECTED_PROVINCES)
        ]
    })

    final_summary.to_csv(
        f"{output_dir}/health_exploration_final_summary.csv",
        index=False,
        sep=";"
    )

    print("\n==============================")
    print("HEALTH DATA EXPLORATION COMPLETED")
    print("==============================")
    print(f"Results saved in: {output_dir}")