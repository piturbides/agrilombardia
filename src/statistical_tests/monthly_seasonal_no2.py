import os
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import shapiro, mannwhitneyu, wilcoxon

from src.data_loader import load_pollution_data


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


def run_monthly_seasonal_no2_analysis():
    """
    Monthly and seasonal statistical comparison of NO2 concentrations
    between Soresina and Rezzato.
    """

    # =========================
    # 1. PATHS
    # =========================

    soresina_path = "Dati/raw/Soresina_NO2_2016_2025.csv"
    rezzato_path = "Dati/raw/Rezzato_NO2_2016_2025.csv"

    output_dir = "Dati/output/1-Statistical tests/1.2-Monthly seasonal"
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

    print("Dataset combined:")
    print(df.head())
    print(df.info())

    # =========================
    # 3. MONTHLY AGGREGATION
    # =========================

    df["Year"] = df["Data"].dt.year
    df["Month"] = df["Data"].dt.month
    df["MonthPeriod"] = df["Data"].dt.to_period("M").dt.to_timestamp()

    monthly = (
        df.groupby(["MonthPeriod", "Year", "Month", "Station"])["NO2"]
        .mean()
        .reset_index()
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

    # =========================
    # 4. MONTHLY TIME SERIES PLOT
    # =========================

    plt.figure(figsize=(12, 5))

    for station in monthly["Station"].unique():
        subset = monthly[monthly["Station"] == station]
        plt.plot(
            subset["MonthPeriod"],
            subset["NO2"],
            marker="o",
            markersize=3,
            label=station,
            alpha=0.8
        )

    plt.title("Monthly mean NO2 concentration: Soresina vs Rezzato")
    plt.xlabel("Date")
    plt.ylabel("Monthly mean NO2 concentration")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{output_dir}/monthly_mean_NO2_time_series.png", dpi=300)
    plt.show()

    # =========================
    # 5. MONTHLY CLIMATOLOGY
    # =========================

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
    plt.title("Average monthly NO2 pattern")
    plt.xlabel("Month")
    plt.ylabel("Mean NO2 concentration")
    plt.xticks(range(1, 13))
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/monthly_climatology_NO2.png", dpi=300)
    plt.show()

    # =========================
    # 6. MONTHLY DISTRIBUTION PLOTS
    # =========================

    plt.figure(figsize=(7, 5))
    monthly.boxplot(column="NO2", by="Station")
    plt.title("Monthly NO2 distribution by station")
    plt.suptitle("")
    plt.xlabel("Station")
    plt.ylabel("Monthly mean NO2 concentration")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/monthly_NO2_boxplot_by_station.png", dpi=300)
    plt.show()

    plt.figure(figsize=(8, 5))

    soresina_monthly = monthly[monthly["Station"] == "Soresina"]["NO2"].dropna()
    rezzato_monthly = monthly[monthly["Station"] == "Rezzato"]["NO2"].dropna()

    plt.hist(soresina_monthly, bins=25, alpha=0.5, label="Soresina")
    plt.hist(rezzato_monthly, bins=25, alpha=0.5, label="Rezzato")
    plt.title("Distribution of monthly mean NO2 concentration")
    plt.xlabel("Monthly mean NO2 concentration")
    plt.ylabel("Frequency")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{output_dir}/monthly_NO2_distribution_histogram.png", dpi=300)
    plt.show()

    # =========================
    # 7. MONTHLY NORMALITY TEST
    # =========================

    shapiro_soresina_monthly = shapiro(soresina_monthly)
    shapiro_rezzato_monthly = shapiro(rezzato_monthly)

    print("\n--- Shapiro-Wilk normality test: monthly values ---")
    print(
        f"Soresina: statistic = {shapiro_soresina_monthly.statistic:.4f}, "
        f"p-value = {shapiro_soresina_monthly.pvalue:.4e}"
    )
    print(
        f"Rezzato: statistic = {shapiro_rezzato_monthly.statistic:.4f}, "
        f"p-value = {shapiro_rezzato_monthly.pvalue:.4e}"
    )

    # =========================
    # 8. MONTHLY STATISTICAL TESTS
    # =========================

    print("\n--- Monthly Mann-Whitney U test ---")

    monthly_u_stat, monthly_p_value = mannwhitneyu(
        soresina_monthly,
        rezzato_monthly,
        alternative="two-sided"
    )

    print(f"U statistic: {monthly_u_stat:.2f}")
    print(f"p-value: {monthly_p_value:.4e}")

    # Paired comparison by same month-year
    monthly_pivot = monthly.pivot(
        index="MonthPeriod",
        columns="Station",
        values="NO2"
    ).dropna()

    print("\n--- Monthly paired dataset ---")
    print(monthly_pivot.head())
    print(f"Number of paired months: {len(monthly_pivot)}")

    monthly_wilcoxon_stat, monthly_wilcoxon_p = safe_wilcoxon(
        monthly_pivot["Soresina"],
        monthly_pivot["Rezzato"]
    )

    print("\n--- Monthly Wilcoxon signed-rank test ---")
    print(f"Statistic: {monthly_wilcoxon_stat}")
    print(f"p-value: {monthly_wilcoxon_p:.4e}")

    monthly_difference = monthly_pivot["Soresina"] - monthly_pivot["Rezzato"]

    print("\n--- Monthly difference summary: Soresina - Rezzato ---")
    print(monthly_difference.describe().round(2))

    # =========================
    # 9. MONTH-SPECIFIC TESTS
    # =========================

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

    # =========================
    # 10. SEASONAL AGGREGATION
    # =========================

    df["Season"] = df["Data"].dt.month.apply(assign_season)
    df["SeasonYear"] = df["Data"].apply(assign_season_year)

    # First compute monthly means with season information
    monthly_for_season = (
        df.groupby(["Year", "Month", "MonthPeriod", "SeasonYear", "Season", "Station"])["NO2"]
        .mean()
        .reset_index()
    )

    # Count how many months are available for each season-year and station
    season_month_count = (
        monthly_for_season.groupby(["SeasonYear", "Season", "Station"])["Month"]
        .nunique()
        .reset_index(name="N_months")
    )

    # Keep only complete seasons, i.e. seasons with 3 months available
    complete_seasons = season_month_count[season_month_count["N_months"] == 3]

    # Merge back to keep only complete season-year-station combinations
    monthly_complete_seasons = monthly_for_season.merge(
        complete_seasons[["SeasonYear", "Season", "Station"]],
        on=["SeasonYear", "Season", "Station"],
        how="inner"
    )

    # Compute seasonal mean only on complete seasons
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

    print("\nSeasonal dataset:")
    print(seasonal.head())

    seasonal_stats = seasonal.groupby("Station")["NO2"].describe().round(2)

    print("\n--- Seasonal descriptive statistics ---")
    print(seasonal_stats)

    seasonal_stats.to_csv(
        f"{output_dir}/seasonal_descriptive_statistics.csv",
        sep=";"
    )

    # =========================
    # 11. SEASONAL CLIMATOLOGY
    # =========================

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
    plt.title("Average seasonal NO2 concentration")
    plt.xlabel("Season")
    plt.ylabel("Mean NO2 concentration")
    plt.xticks(rotation=0)
    plt.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/seasonal_climatology_NO2.png", dpi=300)
    plt.show()

    # =========================
    # 12. SEASONAL BOXPLOT
    # =========================

    plt.figure(figsize=(8, 5))

    seasonal.boxplot(column="NO2", by="Station")
    plt.title("Seasonal NO2 distribution by station")
    plt.suptitle("")
    plt.xlabel("Station")
    plt.ylabel("Seasonal mean NO2 concentration")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/seasonal_NO2_boxplot_by_station.png", dpi=300)
    plt.show()

    # =========================
    # 13. SEASONAL STATISTICAL TESTS
    # =========================

    seasonal_pivot = seasonal.pivot_table(
        index=["SeasonYear", "Season"],
        columns="Station",
        values="NO2",
        observed=True
    ).dropna()

    print("\n--- Seasonal paired dataset ---")
    print(seasonal_pivot.head())
    print(f"Number of paired seasons: {len(seasonal_pivot)}")

    seasonal_wilcoxon_stat, seasonal_wilcoxon_p = safe_wilcoxon(
        seasonal_pivot["Soresina"],
        seasonal_pivot["Rezzato"]
    )

    print("\n--- Seasonal Wilcoxon signed-rank test ---")
    print(f"Statistic: {seasonal_wilcoxon_stat}")
    print(f"p-value: {seasonal_wilcoxon_p:.4e}")

    seasonal_difference = seasonal_pivot["Soresina"] - seasonal_pivot["Rezzato"]

    print("\n--- Seasonal difference summary: Soresina - Rezzato ---")
    print(seasonal_difference.describe().round(2))

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

    # =========================
    # 14. SAVE GLOBAL RESULTS
    # =========================

    global_results = pd.DataFrame({
        "Analysis": [
            "Monthly Shapiro-Wilk Soresina",
            "Monthly Shapiro-Wilk Rezzato",
            "Monthly Mann-Whitney U test",
            "Monthly Wilcoxon paired test",
            "Seasonal Wilcoxon paired test"
        ],
        "Statistic / Value": [
            round(shapiro_soresina_monthly.statistic, 4),
            round(shapiro_rezzato_monthly.statistic, 4),
            round(monthly_u_stat, 2),
            round(monthly_wilcoxon_stat, 2) if monthly_wilcoxon_stat is not None else "",
            round(seasonal_wilcoxon_stat, 2) if seasonal_wilcoxon_stat is not None else ""
        ],
        "p-value": [
            f"{shapiro_soresina_monthly.pvalue:.2e}",
            f"{shapiro_rezzato_monthly.pvalue:.2e}",
            f"{monthly_p_value:.2e}",
            f"{monthly_wilcoxon_p:.2e}" if monthly_wilcoxon_p is not None else "",
            f"{seasonal_wilcoxon_p:.2e}" if seasonal_wilcoxon_p is not None else ""
        ]
    })

    global_results.to_csv(
        f"{output_dir}/monthly_seasonal_global_results.csv",
        index=False,
        sep=";"
    )

    print(f"\nMonthly and seasonal analysis completed.")
    print(f"Results saved in: {output_dir}")