import os
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import shapiro, mannwhitneyu, wilcoxon

from src.data_loader import load_pollution_data


COVID_YEARS = [2020, 2021, 2022]


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


def safe_wilcoxon(x, y):
    """
    Run Wilcoxon signed-rank test safely.
    Returns statistic and p-value.
    """
    try:
        stat, p_value = wilcoxon(x, y)
        return stat, p_value
    except ValueError:
        return None, None


def filter_non_covid_years(df):
    """
    Remove years affected by COVID-related bias.

    Excluded years:
    2020, 2021, 2022.
    """
    return df[~df["Data"].dt.year.isin(COVID_YEARS)].copy()

def add_time_gaps_for_plot(data, date_column, value_column, max_gap_days):
    """
    Add NaN values after large temporal gaps so that line plots
    do not connect separate time periods.

    Parameters
    ----------
    data : pandas.DataFrame
        Dataframe containing the time series.
    date_column : str
        Name of the date column.
    value_column : str
        Name of the pollutant/value column.
    max_gap_days : int
        Maximum allowed gap between consecutive observations.
        Larger gaps are interrupted in the plot.

    Returns
    -------
    pandas.DataFrame
        Dataframe with additional NaN rows used to break plot lines.
    """

    data = data.sort_values(date_column).copy()
    rows = []

    previous_date = None

    for _, row in data.iterrows():
        current_date = row[date_column]

        if previous_date is not None:
            gap_days = (current_date - previous_date).days

            if gap_days > max_gap_days:
                gap_row = row.copy()
                gap_row[date_column] = previous_date + pd.Timedelta(days=1)
                gap_row[value_column] = float("nan")
                rows.append(gap_row)

        rows.append(row)
        previous_date = current_date

    return pd.DataFrame(rows)


def save_series_description(series, output_path):
    """
    Save descriptive statistics of a pandas Series.
    """
    series.describe().round(2).to_csv(output_path, sep=";")


def run_no2_definitivo_non_covid_analysis():
    """
    Definitive statistical comparison of NO2 concentrations between
    Soresina and Rezzato, excluding COVID-related years 2020-2022.

    The analysis includes:
    - daily aggregation and statistical comparison
    - monthly aggregation and statistical comparison
    - seasonal aggregation and statistical comparison
    """

    # =========================
    # 1. PATHS
    # =========================

    soresina_path = "Dati/raw/Soresina_NO2_2016_2025.csv"
    rezzato_path = "Dati/raw/Rezzato_NO2_2016_2025.csv"

    output_dir = "Dati/output/1-Statistical tests/1.3-NO2_definitivo"
    os.makedirs(output_dir, exist_ok=True)

    # =========================
    # 2. LOAD DATA
    # =========================

    soresina = load_pollution_data(
        path=soresina_path,
        station_name="Soresina",
        pollutant_name="NO2"
    )

    rezzato = load_pollution_data(
        path=rezzato_path,
        station_name="Rezzato",
        pollutant_name="NO2"
    )

    df = pd.concat([soresina, rezzato], ignore_index=True)

    print("\n==============================")
    print("NO2 DEFINITIVE NON-COVID ANALYSIS")
    print("==============================")

    print("\nDataset before COVID-years exclusion:")
    print(df.info())
    print(df.groupby("Station")["NO2"].count())

    # =========================
    # 3. REMOVE COVID YEARS
    # =========================

    df = filter_non_covid_years(df)

    print("\nExcluded years: 2020, 2021, 2022")
    print("Dataset after COVID-years exclusion:")
    print(df.info())
    print(df.groupby("Station")["NO2"].count())

    included_years = sorted(df["Data"].dt.year.unique())
    print(f"\nIncluded years: {included_years}")

    pd.DataFrame({
        "Excluded years": COVID_YEARS,
        "Reason": ["COVID-related bias"] * len(COVID_YEARS)
    }).to_csv(
        f"{output_dir}/excluded_years.csv",
        index=False,
        sep=";"
    )

    # ============================================================
    # DAILY ANALYSIS
    # ============================================================

    print("\n\n==============================")
    print("1. DAILY ANALYSIS")
    print("==============================")

    df["Date"] = df["Data"].dt.date
    df["Date"] = pd.to_datetime(df["Date"])

    daily = (
        df.groupby(["Date", "Station"])["NO2"]
        .mean()
        .reset_index()
    )

    daily.to_csv(
        f"{output_dir}/daily_NO2_non_covid_dataset.csv",
        index=False,
        sep=";"
    )

    print("\nDaily dataset:")
    print(daily.head())

    daily_stats = daily.groupby("Station")["NO2"].describe().round(2)

    print("\n--- Daily descriptive statistics ---")
    print(daily_stats)

    daily_stats.to_csv(
        f"{output_dir}/daily_descriptive_statistics.csv",
        sep=";"
    )

    # Daily time series plot
    plt.figure(figsize=(12, 5))

    for station in daily["Station"].unique():
        subset = daily[daily["Station"] == station]

        subset_with_gaps = add_time_gaps_for_plot(
            data=subset,
            date_column="Date",
            value_column="NO2",
            max_gap_days=7
        )

        plt.plot(
            subset_with_gaps["Date"],
            subset_with_gaps["NO2"],
            label=station,
            alpha=0.7
        )

    plt.title("Daily mean NO2 concentration: Soresina vs Rezzato (non-COVID years)")
    plt.xlabel("Date")
    plt.ylabel("Daily mean NO2 concentration")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{output_dir}/daily_mean_NO2_non_covid_time_series.png", dpi=300)
    plt.show()

    # Daily histogram
    soresina_daily = daily[daily["Station"] == "Soresina"]["NO2"].dropna()
    rezzato_daily = daily[daily["Station"] == "Rezzato"]["NO2"].dropna()

    plt.figure(figsize=(8, 5))
    plt.hist(soresina_daily, bins=40, alpha=0.5, label="Soresina")
    plt.hist(rezzato_daily, bins=40, alpha=0.5, label="Rezzato")
    plt.title("Distribution of daily mean NO2 concentration (non-COVID years)")
    plt.xlabel("Daily mean NO2 concentration")
    plt.ylabel("Frequency")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{output_dir}/daily_NO2_distribution_histogram.png", dpi=300)
    plt.show()

    # Daily boxplot
    plt.figure(figsize=(7, 5))
    daily.boxplot(column="NO2", by="Station")
    plt.title("Daily NO2 distribution by station (non-COVID years)")
    plt.suptitle("")
    plt.xlabel("Station")
    plt.ylabel("Daily mean NO2 concentration")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/daily_NO2_boxplot_by_station.png", dpi=300)
    plt.show()

    # Daily normality test
    soresina_daily_sample = soresina_daily.sample(
        min(500, len(soresina_daily)),
        random_state=1
    )

    rezzato_daily_sample = rezzato_daily.sample(
        min(500, len(rezzato_daily)),
        random_state=1
    )

    shapiro_soresina_daily = shapiro(soresina_daily_sample)
    shapiro_rezzato_daily = shapiro(rezzato_daily_sample)

    print("\n--- Daily Shapiro-Wilk normality test ---")
    print(
        f"Soresina: statistic = {shapiro_soresina_daily.statistic:.4f}, "
        f"p-value = {shapiro_soresina_daily.pvalue:.4e}"
    )
    print(
        f"Rezzato: statistic = {shapiro_rezzato_daily.statistic:.4f}, "
        f"p-value = {shapiro_rezzato_daily.pvalue:.4e}"
    )

    # Daily Mann-Whitney U test
    daily_u_stat, daily_p_value = mannwhitneyu(
        soresina_daily,
        rezzato_daily,
        alternative="two-sided"
    )

    print("\n--- Daily Mann-Whitney U test ---")
    print(f"U statistic: {daily_u_stat:.2f}")
    print(f"p-value: {daily_p_value:.4e}")

    daily_summary = pd.DataFrame({
        "Analysis": [
            "Daily Shapiro-Wilk Soresina",
            "Daily Shapiro-Wilk Rezzato",
            "Daily Mann-Whitney U test",
            "Daily mean Soresina",
            "Daily mean Rezzato",
            "Daily mean difference Soresina-Rezzato",
            "Daily median Soresina",
            "Daily median Rezzato",
            "Daily median difference Soresina-Rezzato"
        ],
        "Statistic / Value": [
            round(shapiro_soresina_daily.statistic, 4),
            round(shapiro_rezzato_daily.statistic, 4),
            round(daily_u_stat, 2),
            round(soresina_daily.mean(), 2),
            round(rezzato_daily.mean(), 2),
            round(soresina_daily.mean() - rezzato_daily.mean(), 2),
            round(soresina_daily.median(), 2),
            round(rezzato_daily.median(), 2),
            round(soresina_daily.median() - rezzato_daily.median(), 2)
        ],
        "p-value": [
            f"{shapiro_soresina_daily.pvalue:.2e}",
            f"{shapiro_rezzato_daily.pvalue:.2e}",
            f"{daily_p_value:.2e}",
            "",
            "",
            "",
            "",
            "",
            ""
        ]
    })

    daily_summary.to_csv(
        f"{output_dir}/daily_statistical_results.csv",
        index=False,
        sep=";"
    )

    # ============================================================
    # MONTHLY ANALYSIS
    # ============================================================

    print("\n\n==============================")
    print("2. MONTHLY ANALYSIS")
    print("==============================")

    df["Year"] = df["Data"].dt.year
    df["Month"] = df["Data"].dt.month
    df["MonthPeriod"] = df["Data"].dt.to_period("M").dt.to_timestamp()

    monthly = (
        df.groupby(["MonthPeriod", "Year", "Month", "Station"])["NO2"]
        .mean()
        .reset_index()
    )

    monthly.to_csv(
        f"{output_dir}/monthly_NO2_non_covid_dataset.csv",
        index=False,
        sep=";"
    )

    print("\nMonthly dataset:")
    print(monthly.head())

    monthly_stats = monthly.groupby("Station")["NO2"].describe().round(2)

    print("\n--- Monthly descriptive statistics ---")
    print(monthly_stats)

    monthly_stats.to_csv(
        f"{output_dir}/monthly_descriptive_statistics.csv",
        sep=";"
    )

    # Monthly time series plot
    plt.figure(figsize=(12, 5))

    for station in monthly["Station"].unique():
        subset = monthly[monthly["Station"] == station]

        subset_with_gaps = add_time_gaps_for_plot(
            data=subset,
            date_column="MonthPeriod",
            value_column="NO2",
            max_gap_days=45
        )

        plt.plot(
            subset_with_gaps["MonthPeriod"],
            subset_with_gaps["NO2"],
            marker="o",
            markersize=3,
            label=station,
            alpha=0.8
        )

    plt.title("Monthly mean NO2 concentration: Soresina vs Rezzato (non-COVID years)")
    plt.xlabel("Date")
    plt.ylabel("Monthly mean NO2 concentration")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{output_dir}/monthly_mean_NO2_non_covid_time_series.png", dpi=300)
    plt.show()

    # Monthly climatology
    monthly_climatology = (
        monthly.groupby(["Month", "Station"])["NO2"]
        .mean()
        .reset_index()
    )

    monthly_climatology_pivot = monthly_climatology.pivot(
        index="Month",
        columns="Station",
        values="NO2"
    )

    print("\n--- Monthly climatology ---")
    print(monthly_climatology_pivot.round(2))

    monthly_climatology_pivot.round(2).to_csv(
        f"{output_dir}/monthly_climatology.csv",
        sep=";"
    )

    monthly_climatology_pivot.plot(marker="o", figsize=(9, 5))
    plt.title("Average monthly NO2 pattern (non-COVID years)")
    plt.xlabel("Month")
    plt.ylabel("Mean NO2 concentration")
    plt.xticks(range(1, 13))
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/monthly_climatology_NO2.png", dpi=300)
    plt.show()

    # Monthly boxplot
    plt.figure(figsize=(7, 5))
    monthly.boxplot(column="NO2", by="Station")
    plt.title("Monthly NO2 distribution by station (non-COVID years)")
    plt.suptitle("")
    plt.xlabel("Station")
    plt.ylabel("Monthly mean NO2 concentration")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/monthly_NO2_boxplot_by_station.png", dpi=300)
    plt.show()

    # Monthly histogram
    soresina_monthly = monthly[monthly["Station"] == "Soresina"]["NO2"].dropna()
    rezzato_monthly = monthly[monthly["Station"] == "Rezzato"]["NO2"].dropna()

    plt.figure(figsize=(8, 5))
    plt.hist(soresina_monthly, bins=25, alpha=0.5, label="Soresina")
    plt.hist(rezzato_monthly, bins=25, alpha=0.5, label="Rezzato")
    plt.title("Distribution of monthly mean NO2 concentration (non-COVID years)")
    plt.xlabel("Monthly mean NO2 concentration")
    plt.ylabel("Frequency")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{output_dir}/monthly_NO2_distribution_histogram.png", dpi=300)
    plt.show()

    # Monthly normality
    shapiro_soresina_monthly = shapiro(soresina_monthly)
    shapiro_rezzato_monthly = shapiro(rezzato_monthly)

    print("\n--- Monthly Shapiro-Wilk normality test ---")
    print(
        f"Soresina: statistic = {shapiro_soresina_monthly.statistic:.4f}, "
        f"p-value = {shapiro_soresina_monthly.pvalue:.4e}"
    )
    print(
        f"Rezzato: statistic = {shapiro_rezzato_monthly.statistic:.4f}, "
        f"p-value = {shapiro_rezzato_monthly.pvalue:.4e}"
    )

    # Monthly Mann-Whitney
    monthly_u_stat, monthly_p_value = mannwhitneyu(
        soresina_monthly,
        rezzato_monthly,
        alternative="two-sided"
    )

    print("\n--- Monthly Mann-Whitney U test ---")
    print(f"U statistic: {monthly_u_stat:.2f}")
    print(f"p-value: {monthly_p_value:.4e}")

    # Monthly paired Wilcoxon
    monthly_pivot = monthly.pivot(
        index="MonthPeriod",
        columns="Station",
        values="NO2"
    ).dropna()

    monthly_wilcoxon_stat, monthly_wilcoxon_p = safe_wilcoxon(
        monthly_pivot["Soresina"],
        monthly_pivot["Rezzato"]
    )

    print("\n--- Monthly Wilcoxon signed-rank test ---")
    print(f"Number of paired months: {len(monthly_pivot)}")
    print(f"Statistic: {monthly_wilcoxon_stat}")
    print(f"p-value: {monthly_wilcoxon_p:.4e}")

    monthly_difference = monthly_pivot["Soresina"] - monthly_pivot["Rezzato"]

    print("\n--- Monthly difference summary: Soresina - Rezzato ---")
    print(monthly_difference.describe().round(2))

    monthly_difference.describe().round(2).to_csv(
        f"{output_dir}/monthly_difference_summary.csv",
        sep=";"
    )

    # Month-specific paired tests
    month_specific_results = []

    for month in range(1, 13):
        month_data = monthly[monthly["Month"] == month]

        month_pivot = month_data.pivot(
            index="Year",
            columns="Station",
            values="NO2"
        ).dropna()

        if len(month_pivot) >= 3:
            stat, p_value = safe_wilcoxon(
                month_pivot["Soresina"],
                month_pivot["Rezzato"]
            )

            mean_soresina = month_pivot["Soresina"].mean()
            mean_rezzato = month_pivot["Rezzato"].mean()

            month_specific_results.append({
                "Month": month,
                "N paired years": len(month_pivot),
                "Mean Soresina": round(mean_soresina, 2),
                "Mean Rezzato": round(mean_rezzato, 2),
                "Mean difference Soresina-Rezzato": round(mean_soresina - mean_rezzato, 2),
                "Wilcoxon statistic": stat,
                "p-value": f"{p_value:.2e}" if p_value is not None else ""
            })

    month_specific_results = pd.DataFrame(month_specific_results)

    print("\n--- Month-specific paired tests ---")
    print(month_specific_results)

    month_specific_results.to_csv(
        f"{output_dir}/month_specific_wilcoxon_tests.csv",
        index=False,
        sep=";"
    )

    monthly_summary = pd.DataFrame({
        "Analysis": [
            "Monthly Shapiro-Wilk Soresina",
            "Monthly Shapiro-Wilk Rezzato",
            "Monthly Mann-Whitney U test",
            "Monthly Wilcoxon paired test",
            "Monthly mean Soresina",
            "Monthly mean Rezzato",
            "Monthly mean difference Soresina-Rezzato",
            "Monthly median Soresina",
            "Monthly median Rezzato",
            "Monthly median difference Soresina-Rezzato"
        ],
        "Statistic / Value": [
            round(shapiro_soresina_monthly.statistic, 4),
            round(shapiro_rezzato_monthly.statistic, 4),
            round(monthly_u_stat, 2),
            round(monthly_wilcoxon_stat, 2) if monthly_wilcoxon_stat is not None else "",
            round(soresina_monthly.mean(), 2),
            round(rezzato_monthly.mean(), 2),
            round(soresina_monthly.mean() - rezzato_monthly.mean(), 2),
            round(soresina_monthly.median(), 2),
            round(rezzato_monthly.median(), 2),
            round(soresina_monthly.median() - rezzato_monthly.median(), 2)
        ],
        "p-value": [
            f"{shapiro_soresina_monthly.pvalue:.2e}",
            f"{shapiro_rezzato_monthly.pvalue:.2e}",
            f"{monthly_p_value:.2e}",
            f"{monthly_wilcoxon_p:.2e}" if monthly_wilcoxon_p is not None else "",
            "",
            "",
            "",
            "",
            "",
            ""
        ]
    })

    monthly_summary.to_csv(
        f"{output_dir}/monthly_statistical_results.csv",
        index=False,
        sep=";"
    )

    # ============================================================
    # SEASONAL ANALYSIS
    # ============================================================

    print("\n\n==============================")
    print("3. SEASONAL ANALYSIS")
    print("==============================")

    df["Season"] = df["Data"].dt.month.apply(assign_season)
    df["SeasonYear"] = df["Data"].apply(assign_season_year)

    monthly_for_season = (
        df.groupby(["Year", "Month", "MonthPeriod", "SeasonYear", "Season", "Station"])["NO2"]
        .mean()
        .reset_index()
    )

    season_month_count = (
        monthly_for_season.groupby(["SeasonYear", "Season", "Station"])["Month"]
        .nunique()
        .reset_index(name="N_months")
    )

    complete_seasons = season_month_count[season_month_count["N_months"] == 3]

    monthly_complete_seasons = monthly_for_season.merge(
        complete_seasons[["SeasonYear", "Season", "Station"]],
        on=["SeasonYear", "Season", "Station"],
        how="inner"
    )

    seasonal = (
        monthly_complete_seasons.groupby(["SeasonYear", "Season", "Station"])["NO2"]
        .mean()
        .reset_index()
    )

    season_order = ["Winter", "Spring", "Summer", "Autumn"]

    seasonal["Season"] = pd.Categorical(
        seasonal["Season"],
        categories=season_order,
        ordered=True
    )

    seasonal = seasonal.sort_values(["SeasonYear", "Season", "Station"])

    seasonal.to_csv(
        f"{output_dir}/seasonal_NO2_non_covid_dataset.csv",
        index=False,
        sep=";"
    )

    print("\nSeasonal dataset:")
    print(seasonal.head())

    seasonal_stats = seasonal.groupby("Station")["NO2"].describe().round(2)

    print("\n--- Seasonal descriptive statistics ---")
    print(seasonal_stats)

    seasonal_stats.to_csv(
        f"{output_dir}/seasonal_descriptive_statistics.csv",
        sep=";"
    )

    # Seasonal climatology
    seasonal_climatology = (
        seasonal.groupby(["Season", "Station"], observed=True)["NO2"]
        .mean()
        .reset_index()
    )

    seasonal_climatology_pivot = seasonal_climatology.pivot(
        index="Season",
        columns="Station",
        values="NO2"
    ).reindex(season_order)

    print("\n--- Seasonal climatology ---")
    print(seasonal_climatology_pivot.round(2))

    seasonal_climatology_pivot.round(2).to_csv(
        f"{output_dir}/seasonal_climatology.csv",
        sep=";"
    )

    seasonal_climatology_pivot.plot(kind="bar", figsize=(8, 5))
    plt.title("Average seasonal NO2 concentration (non-COVID years)")
    plt.xlabel("Season")
    plt.ylabel("Mean NO2 concentration")
    plt.xticks(rotation=0)
    plt.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/seasonal_climatology_NO2.png", dpi=300)
    plt.show()

    # Seasonal boxplot
    plt.figure(figsize=(8, 5))
    seasonal.boxplot(column="NO2", by="Station")
    plt.title("Seasonal NO2 distribution by station (non-COVID years)")
    plt.suptitle("")
    plt.xlabel("Station")
    plt.ylabel("Seasonal mean NO2 concentration")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/seasonal_NO2_boxplot_by_station.png", dpi=300)
    plt.show()

    # Seasonal paired Wilcoxon
    seasonal_pivot = seasonal.pivot_table(
        index=["SeasonYear", "Season"],
        columns="Station",
        values="NO2",
        observed=True
    ).dropna()

    seasonal_wilcoxon_stat, seasonal_wilcoxon_p = safe_wilcoxon(
        seasonal_pivot["Soresina"],
        seasonal_pivot["Rezzato"]
    )

    print("\n--- Seasonal Wilcoxon signed-rank test ---")
    print(f"Number of paired seasons: {len(seasonal_pivot)}")
    print(f"Statistic: {seasonal_wilcoxon_stat}")
    print(f"p-value: {seasonal_wilcoxon_p:.4e}")

    seasonal_difference = seasonal_pivot["Soresina"] - seasonal_pivot["Rezzato"]

    print("\n--- Seasonal difference summary: Soresina - Rezzato ---")
    print(seasonal_difference.describe().round(2))

    seasonal_difference.describe().round(2).to_csv(
        f"{output_dir}/seasonal_difference_summary.csv",
        sep=";"
    )

    # Season-specific paired tests
    season_specific_results = []

    for season in season_order:
        season_data = seasonal[seasonal["Season"] == season]

        season_pivot = season_data.pivot(
            index="SeasonYear",
            columns="Station",
            values="NO2"
        ).dropna()

        if len(season_pivot) >= 3:
            stat, p_value = safe_wilcoxon(
                season_pivot["Soresina"],
                season_pivot["Rezzato"]
            )

            mean_soresina = season_pivot["Soresina"].mean()
            mean_rezzato = season_pivot["Rezzato"].mean()

            season_specific_results.append({
                "Season": season,
                "N paired years": len(season_pivot),
                "Mean Soresina": round(mean_soresina, 2),
                "Mean Rezzato": round(mean_rezzato, 2),
                "Mean difference Soresina-Rezzato": round(mean_soresina - mean_rezzato, 2),
                "Wilcoxon statistic": stat,
                "p-value": f"{p_value:.2e}" if p_value is not None else ""
            })

    season_specific_results = pd.DataFrame(season_specific_results)

    print("\n--- Season-specific paired tests ---")
    print(season_specific_results)

    season_specific_results.to_csv(
        f"{output_dir}/season_specific_wilcoxon_tests.csv",
        index=False,
        sep=";"
    )

    seasonal_summary = pd.DataFrame({
        "Analysis": [
            "Seasonal Wilcoxon paired test",
            "Seasonal mean Soresina",
            "Seasonal mean Rezzato",
            "Seasonal mean difference Soresina-Rezzato",
            "Seasonal median Soresina",
            "Seasonal median Rezzato",
            "Seasonal median difference Soresina-Rezzato"
        ],
        "Statistic / Value": [
            round(seasonal_wilcoxon_stat, 2) if seasonal_wilcoxon_stat is not None else "",
            round(seasonal_pivot["Soresina"].mean(), 2),
            round(seasonal_pivot["Rezzato"].mean(), 2),
            round(seasonal_pivot["Soresina"].mean() - seasonal_pivot["Rezzato"].mean(), 2),
            round(seasonal_pivot["Soresina"].median(), 2),
            round(seasonal_pivot["Rezzato"].median(), 2),
            round(seasonal_pivot["Soresina"].median() - seasonal_pivot["Rezzato"].median(), 2)
        ],
        "p-value": [
            f"{seasonal_wilcoxon_p:.2e}" if seasonal_wilcoxon_p is not None else "",
            "",
            "",
            "",
            "",
            "",
            ""
        ]
    })

    seasonal_summary.to_csv(
        f"{output_dir}/seasonal_statistical_results.csv",
        index=False,
        sep=";"
    )

    # ============================================================
    # GLOBAL SUMMARY
    # ============================================================

    global_results = pd.concat(
        [daily_summary, monthly_summary, seasonal_summary],
        ignore_index=True
    )

    global_results.to_csv(
        f"{output_dir}/global_NO2_non_covid_statistical_results.csv",
        index=False,
        sep=";"
    )

    print("\n==============================")
    print("ANALYSIS COMPLETED")
    print("==============================")
    print(f"Results saved in: {output_dir}")