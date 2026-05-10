# Human Health and Environment Data Science Laboratory

Statistical analysis of air pollution data for the Human Health and Environment Data Science Laboratory project.

The project investigates differences in air pollution patterns between areas with different territorial and emission profiles in Lombardy, with a focus on the comparison between agricultural/rural and industrial/urban contexts.

The first part of the project focuses on environmental exposure data from ARPA Lombardia monitoring stations. The aim is to characterize and compare pollutant concentration patterns before moving to the integration of health outcome data.

---

## Project framework

The project is based on the general idea that different emission contexts may contribute differently to air pollution levels and, potentially, to health-related outcomes.

The current environmental analysis focuses on:

- **NO2**, mainly interpreted as a combustion-related pollutant associated with traffic, heating and industrial activities;
- **PM2.5**, interpreted as a health-relevant fine particulate pollutant with both primary and secondary components.

For all definitive analyses, the COVID-related years **2020, 2021 and 2022** were excluded to avoid potential bias due to abnormal changes in mobility, traffic, industrial activities and emission patterns.

The retained years are:

```text
2016, 2017, 2018, 2019, 2023, 2024, 2025
```

---

## Part 1 — Statistical tests on air pollution data

The first part of the project is organized in:

```text
Dati/output/1-Statistical tests/
```

This section contains exploratory and statistical comparisons of pollutant concentration data at different temporal aggregation scales.

---

## 1.1 Preliminary NO2 daily analysis

The first exploratory analysis compared daily mean NO2 concentrations between:

- **Soresina**, used as a proxy for an agricultural/rural context;
- **Rezzato**, used as a proxy for a more industrialized context in the Brescia area.

The analysis included:

- loading and cleaning of ARPA Lombardia CSV files;
- conversion of invalid values coded as `-999` into missing values;
- aggregation of hourly NO2 data into daily mean concentrations;
- descriptive statistics;
- graphical exploratory analysis;
- Shapiro-Wilk normality test;
- Mann-Whitney U test.

**Output folder:**

```text
Dati/output/1-Statistical tests/1.1-Preliminary
```

---

## 1.2 Monthly and seasonal NO2 analysis

The second analysis extended the NO2 comparison between Soresina and Rezzato by considering monthly and seasonal aggregation.

The analysis included:

- monthly mean NO2 concentrations;
- seasonal mean NO2 concentrations;
- meteorological seasons:
  - Winter: December, January, February;
  - Spring: March, April, May;
  - Summer: June, July, August;
  - Autumn: September, October, November;
- removal of incomplete seasons;
- monthly and seasonal climatology;
- Mann-Whitney U test;
- paired Wilcoxon signed-rank test;
- month-specific and season-specific paired comparisons.

**Output folder:**

```text
Dati/output/1-Statistical tests/1.2-Monthly seasonal
```

---

## 1.3 Definitive non-COVID NO2 analysis

The definitive NO2 analysis repeated the daily, monthly and seasonal comparison after excluding the COVID-related years 2020, 2021 and 2022.

**Comparison:**

- **Soresina**: agricultural/rural proxy;
- **Rezzato**: industrial proxy.

The analysis included:

- daily mean NO2 comparison;
- monthly mean NO2 comparison;
- seasonal mean NO2 comparison;
- exclusion of 2020, 2021 and 2022;
- graphical outputs with consistent station colors;
- Shapiro-Wilk normality tests;
- Mann-Whitney U tests;
- paired Wilcoxon signed-rank tests;
- CSV summary tables.

**Main interpretation:**

Soresina and Rezzato show broadly similar NO2 dynamics, strongly dominated by seasonality. Soresina tends to show slightly higher NO2 concentrations, especially in colder periods, but the magnitude of the difference is modest. This suggests that NO2 alone does not clearly separate the agricultural and industrial territorial contexts.

**Output folder:**

```text
Dati/output/1-Statistical tests/1.3-NO2_definitivo
```

**Main script:**

```text
src/statistical_tests/no2_definitivo_non_covid.py
```

---

## 1.4 Definitive non-COVID PM2.5 analysis

The definitive PM2.5 analysis compared PM2.5 concentrations between:

- **Soresina**, used as a proxy for an agricultural/rural context;
- **Brescia Villaggio Sereno**, used as an urban/industrial proxy in the Brescia area.

The analysis was performed after excluding the COVID-related years 2020, 2021 and 2022.

The analysis included:

- daily PM2.5 comparison;
- monthly mean PM2.5 comparison;
- seasonal mean PM2.5 comparison;
- exclusion of 2020, 2021 and 2022;
- graphical outputs with consistent station colors;
- Shapiro-Wilk normality tests;
- Mann-Whitney U tests;
- paired Wilcoxon signed-rank tests;
- month-specific and season-specific paired comparisons;
- CSV summary tables.

**Main interpretation:**

Soresina shows systematically higher PM2.5 concentrations than Brescia Villaggio Sereno, especially outside winter. The difference is statistically significant at daily, monthly and seasonal scales. This suggests that PM2.5 patterns are not exclusively driven by urban or industrial sources and may reflect regional secondary aerosol formation and agricultural precursor contributions.

However, this interpretation remains exploratory because the current analysis does not include NH3 concentrations, meteorological covariates or PM chemical speciation.

**Output folder:**

```text
Dati/output/1-Statistical tests/1.4-PM25_definitivo
```

**Main script:**

```text
src/statistical_tests/pm25_definitivo_non_covid.py
```

---

## Repository structure

### Main folders

```text
Dati/
├── raw/
│   └── Raw ARPA monitoring station data
│
└── output/
    └── 1-Statistical tests/
        ├── 1.1-Preliminary/
        ├── 1.2-Monthly seasonal/
        ├── 1.3-NO2_definitivo/
        └── 1.4-PM25_definitivo/

src/
├── data_loader.py
│
└── statistical_tests/
    ├── preliminary_no2.py
    ├── monthly_seasonal_no2.py
    ├── no2_definitivo_non_covid.py
    └── pm25_definitivo_non_covid.py
```

### Main files

```text
main.py
requirements.txt
README.md
```

---

## How to run

Install the required libraries:

```bash
pip install -r requirements.txt
```

Run the current analysis:

```bash
python main.py
```

The script executed by `main.py` can be changed depending on the analysis to run.

### Run the definitive PM2.5 analysis

Use this in `main.py`:

```python
from src.statistical_tests.pm25_definitivo_non_covid import run_pm25_definitivo_non_covid_analysis


if __name__ == "__main__":
    run_pm25_definitivo_non_covid_analysis()
```

### Run the definitive NO2 analysis

Use this in `main.py`:

```python
from src.statistical_tests.no2_definitivo_non_covid import run_no2_definitivo_non_covid_analysis


if __name__ == "__main__":
    run_no2_definitivo_non_covid_analysis()
```

---

## GitHub workflow

Before starting new work:

```bash
git pull
```

After modifying and testing the code:

```bash
python main.py
git status
git add -A
git commit -m "Clear commit message"
git push
```

Useful commit message examples:

```bash
git commit -m "Add definitive non-covid NO2 analysis"
git commit -m "Add definitive non-covid PM25 analysis"
git commit -m "Update README after statistical tests"
git commit -m "Fix README formatting"
```

---

## Notes and limitations

The current analyses are exploratory and descriptive. Statistical significance is interpreted together with the magnitude of the observed differences and with the methodological limitations of using monitoring stations as proxies for broader territorial contexts.

Due to pollutant-specific monitoring availability, the industrial/urban proxy station differs between the NO2 and PM2.5 analyses. Therefore, results should be interpreted pollutant by pollutant and not as a perfectly matched multi-pollutant comparison on the same station pair.

The statistical tests do not explicitly model temporal autocorrelation or meteorological confounding. Future analyses may include meteorological variables, health outcome data and additional pollutants such as NH3, if available.

---

## Next step

Part 1 of the project, focused on statistical tests of environmental pollutant data, is now completed.

The next part of the project will focus on the exploration and possible integration of health outcome data, in order to investigate whether the environmental differences observed in air pollution data can be related to respiratory and cardiovascular health indicators.