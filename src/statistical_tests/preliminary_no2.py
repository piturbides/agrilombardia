import os
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu, shapiro

from src.data_loader import load_pollution_data


def run_preliminary_no2_analysis():
    """
    Preliminary statistical comparison of daily NO2 concentrations
    between Soresina and Rezzato.
    """

    # =========================
    # 1. PATHS
    # =========================

    soresina_path = "Dati/raw/Soresina_NO2_2016_2025.csv"
    rezzato_path = "Dati/raw/Rezzato_NO2_2016_2025.csv"

    output_dir = "Dati/output/1-Statistical tests/1.1-Preliminary"
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
    # 3. DAILY AGGREGATION
    # =========================

    df["Date"] = df["Data"].dt.date
    df["Date"] = pd.to_datetime(df["Date"])

    daily = (
        df.groupby(["Date", "Station"])["NO2"]
        .mean()
        .reset_index()
    )

    print("\nDaily dataset:")
    print(daily.head())

    print("\n--- Daily descriptive statistics ---")
    descriptive_stats = daily.groupby("Station")["NO2"].describe().round(2)
    print(descriptive_stats)

    descriptive_stats.to_csv(
        f"{output_dir}/daily_descriptive_statistics.csv",
        sep=";"
    )

    # =========================
    # 4. TIME SERIES PLOT
    # =========================

    plt.figure(figsize=(12, 5))

    for station in daily["Station"].unique():
        subset = daily[daily["Station"] == station]
        plt.plot(subset["Date"], subset["NO2"], label=station, alpha=0.7)

    plt.title("Daily mean NO2 concentration: Soresina vs Rezzato")
    plt.xlabel("Date")
    plt.ylabel("NO2 concentration")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{output_dir}/daily_mean_NO2.png", dpi=300)
    plt.show()

    # =========================
    # 5. DISTRIBUTION CHECK
    # =========================

    soresina_daily = daily[daily["Station"] == "Soresina"]["NO2"].dropna()
    rezzato_daily = daily[daily["Station"] == "Rezzato"]["NO2"].dropna()

    print("\n--- Sample sizes ---")
    print(f"Soresina daily observations: {len(soresina_daily)}")
    print(f"Rezzato daily observations: {len(rezzato_daily)}")

    # Histograms
    plt.figure(figsize=(8, 5))
    plt.hist(soresina_daily, bins=40, alpha=0.5, label="Soresina")
    plt.hist(rezzato_daily, bins=40, alpha=0.5, label="Rezzato")
    plt.title("Distribution of daily mean NO2 concentration")
    plt.xlabel("NO2 concentration")
    plt.ylabel("Frequency")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{output_dir}/no2_distribution_histogram.png", dpi=300)
    plt.show()

    # Boxplot
    plt.figure(figsize=(7, 5))
    daily.boxplot(column="NO2", by="Station")
    plt.title("Daily NO2 distribution by station")
    plt.suptitle("")
    plt.xlabel("Station")
    plt.ylabel("NO2 concentration")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/no2_boxplot_by_station.png", dpi=300)
    plt.show()

    # Shapiro-Wilk normality test
    soresina_sample = soresina_daily.sample(
        min(500, len(soresina_daily)),
        random_state=1
    )

    rezzato_sample = rezzato_daily.sample(
        min(500, len(rezzato_daily)),
        random_state=1
    )

    shapiro_soresina = shapiro(soresina_sample)
    shapiro_rezzato = shapiro(rezzato_sample)

    print("\n--- Shapiro-Wilk normality test ---")
    print(
        f"Soresina: statistic = {shapiro_soresina.statistic:.4f}, "
        f"p-value = {shapiro_soresina.pvalue:.4e}"
    )
    print(
        f"Rezzato: statistic = {shapiro_rezzato.statistic:.4f}, "
        f"p-value = {shapiro_rezzato.pvalue:.4e}"
    )

    if shapiro_soresina.pvalue < 0.05 or shapiro_rezzato.pvalue < 0.05:
        print("At least one distribution is not normal → use a non-parametric test.")
    else:
        print("Both distributions are compatible with normality → parametric test could be used.")

    # =========================
    # 6. MAIN STATISTICAL TEST
    # =========================

    print("\n--- Mann-Whitney U test ---")

    u_stat, p_value = mannwhitneyu(
        soresina_daily,
        rezzato_daily,
        alternative="two-sided"
    )

    print(f"U statistic: {u_stat:.2f}")
    print(f"p-value: {p_value:.4e}")

    alpha = 0.05

    if p_value < alpha:
        print("Result: statistically significant difference between Soresina and Rezzato daily NO2 distributions.")
    else:
        print("Result: no statistically significant difference between Soresina and Rezzato daily NO2 distributions.")

    # =========================
    # 7. DIFFERENCE SUMMARY
    # =========================

    mean_soresina = soresina_daily.mean()
    mean_rezzato = rezzato_daily.mean()

    median_soresina = soresina_daily.median()
    median_rezzato = rezzato_daily.median()

    print("\n--- Difference summary ---")
    print(f"Soresina mean NO2: {mean_soresina:.2f}")
    print(f"Rezzato mean NO2: {mean_rezzato:.2f}")
    print(f"Mean difference (Soresina - Rezzato): {mean_soresina - mean_rezzato:.2f}")

    print(f"Soresina median NO2: {median_soresina:.2f}")
    print(f"Rezzato median NO2: {median_rezzato:.2f}")
    print(f"Median difference (Soresina - Rezzato): {median_soresina - median_rezzato:.2f}")

    # Save statistical results in a readable format for Excel
    results = pd.DataFrame({
        "Analysis": [
            "Shapiro-Wilk Soresina",
            "Shapiro-Wilk Rezzato",
            "Mann-Whitney U test",
            "Mean Soresina",
            "Mean Rezzato",
            "Mean difference Soresina-Rezzato",
            "Median Soresina",
            "Median Rezzato",
            "Median difference Soresina-Rezzato"
        ],
        "Statistic / Value": [
            round(shapiro_soresina.statistic, 4),
            round(shapiro_rezzato.statistic, 4),
            round(u_stat, 2),
            round(mean_soresina, 2),
            round(mean_rezzato, 2),
            round(mean_soresina - mean_rezzato, 2),
            round(median_soresina, 2),
            round(median_rezzato, 2),
            round(median_soresina - median_rezzato, 2)
        ],
        "p-value": [
            f"{shapiro_soresina.pvalue:.2e}",
            f"{shapiro_rezzato.pvalue:.2e}",
            f"{p_value:.2e}",
            "",
            "",
            "",
            "",
            "",
            ""
        ]
    })

    results.to_csv(
        f"{output_dir}/preliminary_no2_statistical_results.csv",
        index=False,
        sep=";"
    )

    print(f"\nResults saved in: {output_dir}")