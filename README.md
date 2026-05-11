# Human Health and Environment Data Science Laboratory

Statistical analysis of air pollution and health event data for the Human Health and Environment Data Science Laboratory project.

The project investigates differences in air pollution patterns between areas with different territorial and emission profiles in Lombardy, with a focus on the comparison between agricultural/rural and industrial/urban contexts.

The first part of the project focuses on environmental exposure data from ARPA Lombardia monitoring stations. The second part explores health event data and prepares population-normalized and age-specific health indicators that can later be compared with respiratory and cardiocirculatory health outcomes.

---

## Project framework

The project is based on the general idea that different emission contexts may contribute differently to air pollution levels and, potentially, to health-related outcomes.

The current environmental analysis focuses on:

- **NO2**, mainly interpreted as a combustion-related pollutant associated with traffic, heating and industrial activities;
- **PM2.5**, interpreted as a health-relevant fine particulate pollutant with both primary and secondary components.

For the definitive environmental analyses, the COVID-related years **2020, 2021 and 2022** were excluded to avoid potential bias due to abnormal changes in mobility, traffic, industrial activities and emission patterns.

The retained years for the definitive environmental analyses are:

```text
2016, 2017, 2018, 2019, 2023, 2024, 2025
```

The health dataset currently contains the following available years:

```text
2015, 2016, 2017, 2018, 2019, 2023
```

Years 2020, 2021 and 2022 are not present in the health dataset.

For the first health-environment integration steps, the retained common years are:

```text
2016, 2017, 2018, 2019, 2023
```

The project should be interpreted as an exploratory ecological analysis. Pollutant concentrations are represented by monitoring station proxies, while health outcomes are aggregated over selected municipalities. Therefore, the analysis can identify coherent territorial and temporal patterns, but it cannot demonstrate individual-level causal effects.

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

## Part 2 — Health data exploration and aggregation

The second part of the project focuses on the exploration and aggregation of health event data, with the aim of preparing respiratory and cardiocirculatory health indicators that can later be compared with the environmental pollutant patterns identified in Part 1.

The raw health dataset contains event-level records with information on:

- date;
- municipality;
- province;
- event code;
- event type;
- event detail;
- patient age.

Since the dataset may contain sensitive health-related information, the raw health file is kept local and excluded from GitHub using `.gitignore`.

The raw file is expected locally at:

```text
Dati/raw/Health_events_2015_2023.csv
```

This file is not uploaded to GitHub.

---

## 2.1 Health data exploration

The first health data exploration aims to understand the structure and quality of the available health event dataset before any integration with environmental data.

The analysis includes:

- dataset structure inspection;
- date parsing and temporal coverage check;
- missing values assessment;
- age cleaning and age distribution analysis;
- event counts by year;
- event counts by province and municipality;
- event counts by event type and event detail;
- extraction of respiratory acute events;
- extraction of cardiocirculatory acute events;
- monthly and seasonal aggregation of respiratory acute events;
- focused checks on selected municipalities: Soresina, Rezzato and Brescia;
- province-level filtering for Brescia and Cremona.

**Main interpretation:**

The health dataset is suitable for exploratory aggregated analyses. Respiratory acute events and cardiocirculatory acute events are both sufficiently represented. However, raw event counts cannot be directly interpreted as health risk because they are strongly affected by population size. Future analyses should compute population-normalized rates and interpret any comparison with pollutant data as exploratory and ecological rather than causal.

**Output folder:**

```text
Dati/output/2-Health data/2.1-Health data exploration
```

**Main script:**

```text
src/health_analysis/health_data_exploration.py
```

---

## 2.2 Health event aggregation and population-normalized rates

The second health analysis moves from raw health event counts to population-normalized health event rates for the two selected study areas.

The study areas were defined from the QGIS shapefiles used in the project:

- **Agricultural area**: 21 selected municipalities;
- **Industrial area**: 16 selected municipalities.

Population data were collected for the years:

```text
2016, 2017, 2018, 2019, 2023
```

The analysis checked that all selected municipalities were correctly matched with population data for all selected years.

The analysis included:

- loading population files for Brescia and Cremona provinces;
- filtering population data to retain only selected study-area municipalities;
- construction of annual population denominators by study area;
- assignment of each health event to the agricultural or industrial area;
- extraction of respiratory acute events;
- extraction of cardiocirculatory acute events;
- annual aggregation of health events by area and outcome;
- monthly aggregation of health events by area and outcome;
- seasonal aggregation of health events by area and outcome;
- computation of event rates per 10,000 inhabitants;
- generation of CSV outputs and graphical summaries.

The rate was computed as:

```text
Rate per 10,000 inhabitants = (Number of events / Population) × 10,000
```

**Main interpretation:**

Population normalization is essential because the industrial area has a much larger population than the agricultural area.

Respiratory acute event rates are broadly comparable between the two areas and do not show a stable area-specific separation. In contrast, cardiocirculatory acute event rates are consistently higher in the industrial area than in the agricultural area.

These results are descriptive and exploratory. They do not demonstrate a causal relationship with air pollution, but they provide the normalized health indicators needed for future environmental-health integration.

**Output folder:**

```text
Dati/output/2-Health data/2.2-Health event aggregation
```

**Main script:**

```text
src/health_analysis/health_event_aggregation.py
```

---

## 2.3 Health age-structure check and age-specific rates

The third health analysis refines the interpretation of the population-normalized health event rates by explicitly considering age structure.

This step was introduced because respiratory and cardiocirculatory acute events are strongly age-dependent. Therefore, differences between the agricultural and industrial areas may be influenced by different age structures, especially if one area has a larger elderly population.

The analysis used the same selected study areas and the same selected acute outcomes as Part 2.2:

- **Respiratory acute events**;
- **Cardiocirculatory acute events**.

Events were stratified into two main age groups:

```text
<65
65+
```

and into five detailed age classes:

```text
0-44
45-64
65-74
75-84
85+
```

Age-specific municipal population denominators were collected from ISTAT population files and used to compute annual age-specific event rates per 10,000 inhabitants.

The analysis included:

- assignment of each selected health event to an age group;
- comparison of event-age distributions between the two study areas;
- loading and harmonization of age-specific ISTAT population files;
- construction of age-specific population denominators by year, area and age group;
- computation of annual age-specific rates per 10,000 inhabitants;
- comparison of binary age-specific rates (`<65` and `65+`);
- comparison of detailed age-specific rates;
- graphical outputs and CSV summary tables.

The age-specific rate was computed as:

```text
Age-specific rate per 10,000 inhabitants =
(Number of events in the age group / Population in the same age group) × 10,000
```

Population denominator coverage was complete:

```text
Binary age groups: 0 missing denominators
Detailed age groups: 0 missing denominators
```

**Main interpretation:**

The event-age distribution showed that acute events were mainly concentrated among elderly subjects, especially respiratory events. The agricultural area showed an older event-age profile than the industrial area for both outcomes.

The share of events in subjects aged 65 or older was:

```text
Cardiocirculatory events:
Agricultural = 66.5%
Industrial = 59.7%

Respiratory events:
Agricultural = 76.4%
Industrial = 70.1%
```

After age stratification, the cardiocirculatory outcome showed the most relevant pattern. In the `<65` group, the industrial area had consistently higher annual cardiocirculatory rates than the agricultural area across all available years.

Mean `<65` cardiocirculatory rates were:

```text
Industrial area = 103.5 events per 10,000 inhabitants
Agricultural area = 77.6 events per 10,000 inhabitants
```

This corresponds to an industrial/agricultural ratio of approximately:

```text
1.33
```

Therefore, the higher crude cardiocirculatory burden previously observed in the industrial area does not appear to be simply explained by an older population structure. The excess is particularly visible in younger and middle-aged groups.

In the `65+` group, cardiocirculatory rates were high in both areas and showed a mixed pattern, with no stable dominance of either area.

For respiratory events, the industrial area showed higher rates in the `<65` group, while the agricultural area showed higher rates among subjects aged 65 or older. This suggests that respiratory outcomes may be more strongly influenced by elderly vulnerability, frailty and demographic structure.

No additional formal statistical testing was performed in this step. The age-specific rates are annual rates and only five paired years are available. With this sample size, normality testing and paired hypothesis testing would have limited interpretability. Therefore, Part 2.3 is interpreted descriptively through rates, differences, ratios and visual comparison.

The results remain ecological and descriptive. They do not demonstrate individual-level causal effects, but they strengthen the interpretation of cardiocirculatory outcomes as a relevant indicator for the next environmental-health integration phase.

**Output folder:**

```text
Dati/output/2-Health data/2.3-Health age structure check
```

**Main script:**

```text
src/health_analysis/health_age_structure_check.py
```

---

## Repository structure

### Main folders

```text
Dati/
├── raw/
│   ├── Raw ARPA monitoring station data
│   ├── Health_events_2015_2023.csv   # local only, ignored by Git
│   └── population/
│       ├── Brescia_2016.csv
│       ├── Brescia_2017.csv
│       ├── Brescia_2018.csv
│       ├── Brescia_2019.csv
│       ├── Brescia_2023.csv
│       ├── Cremona_2016.csv
│       ├── Cremona_2017.csv
│       ├── Cremona_2018.csv
│       ├── Cremona_2019.csv
│       └── Cremona_2023.csv
│
└── output/
    ├── 1-Statistical tests/
    │   ├── 1.1-Preliminary/
    │   ├── 1.2-Monthly seasonal/
    │   ├── 1.3-NO2_definitivo/
    │   └── 1.4-PM25_definitivo/
    │
    └── 2-Health data/
        ├── 2.1-Health data exploration/
        ├── 2.2-Health event aggregation/
        └── 2.3-Health age structure check/

src/
├── data_loader.py
│
├── statistical_tests/
│   ├── preliminary_no2.py
│   ├── monthly_seasonal_no2.py
│   ├── no2_definitivo_non_covid.py
│   └── pm25_definitivo_non_covid.py
│
└── health_analysis/
    ├── health_data_exploration.py
    ├── health_event_aggregation.py
    └── health_age_structure_check.py
```

### Main files

```text
main.py
requirements.txt
README.md
.gitignore
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

### Run the health data exploration

Use this in `main.py`:

```python
from src.health_analysis.health_data_exploration import run_health_data_exploration


if __name__ == "__main__":
    run_health_data_exploration()
```

### Run the health event aggregation

Use this in `main.py`:

```python
from src.health_analysis.health_event_aggregation import run_health_event_aggregation


if __name__ == "__main__":
    run_health_event_aggregation()
```

### Run the health age-structure check

Use this in `main.py`:

```python
from src.health_analysis.health_age_structure_check import run_health_age_structure_check


if __name__ == "__main__":
    run_health_age_structure_check()
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
git commit -m "Add health data exploration"
git commit -m "Add health event aggregation and rates"
git commit -m "Add health age structure check"
git commit -m "Update README after age-specific health analysis"
git commit -m "Fix README formatting"
```

---

## Notes and limitations

The current analyses are exploratory and descriptive. Statistical significance is interpreted together with the magnitude of the observed differences and with the methodological limitations of using monitoring stations as proxies for broader territorial contexts.

Due to pollutant-specific monitoring availability, the industrial/urban proxy station differs between the NO2 and PM2.5 analyses. Therefore, results should be interpreted pollutant by pollutant and not as a perfectly matched multi-pollutant comparison on the same station pair.

The statistical tests on pollutant data do not explicitly model temporal autocorrelation or meteorological confounding. Future analyses may include meteorological variables, health outcome data and additional pollutants such as NH3, if available.

The raw health event dataset is not uploaded to GitHub because it may contain sensitive health-related information. Only aggregated outputs and analysis scripts are versioned.

The health dataset does not contain a patient identifier. Therefore, records should be interpreted as health events, not unique individuals. The same person may appear more than once.

Raw health event counts cannot be directly interpreted as health risk because they are strongly affected by population size. For this reason, Part 2.2 computes population-normalized rates per 10,000 inhabitants.

Part 2.3 introduces age-specific rates using age-specific municipal population denominators. This improves the interpretation of the health outcome comparison, but it is still not a full age-standardized epidemiological analysis based on a common reference population.

The age-specific analysis suggests that the higher cardiocirculatory burden in the industrial area is not simply explained by age structure alone, especially because the excess is visible in the `<65` group. However, this result remains ecological and descriptive.

Formal statistical testing was not added to Part 2.3 because the age-specific rates are annual and only five paired years are available. Differences were therefore interpreted through descriptive rates, mean differences, ratios and visual patterns. More formal non-parametric correlation analysis may be more meaningful in the environmental-health integration phase, especially at monthly or seasonal scale.

Any future comparison between pollutant concentrations and health events should be interpreted as an exploratory ecological analysis, not as evidence of individual-level causality.

Important unmeasured confounders include age beyond the applied stratification, sex, socioeconomic status, smoking, occupational exposure, comorbidities, healthcare access, event coding practices and individual exposure history.

The geographical meaning of the municipality variable should also be interpreted carefully. If the municipality refers to event location rather than patient residence, area-level health rates may not perfectly represent the resident population.

---

## Next step

Part 1 of the project, focused on statistical tests of environmental pollutant data, is completed.

Part 2 has now produced:

- a general health data exploration;
- population-normalized respiratory and cardiocirculatory rates;
- age-specific health event rates for the selected study areas.

The next analytical step is to integrate environmental indicators and health event rates into a common dataset, starting from seasonal or monthly aggregation.

The most promising starting point is seasonal integration because it provides a compromise between annual aggregation, which gives too few observations, and monthly aggregation, which may be noisier.

The future integrated dataset may include:

```text
SeasonYear
Season
Area
NO2_mean
PM25_mean
Respiratory_rate_per_10000
Cardiocirculatory_rate_per_10000
Population
```

Possible analyses include:

- visual comparison of pollutant trends and health event rates;
- scatter plots between pollutant concentrations and health event rates;
- Spearman correlation analysis;
- separate analyses for PM2.5 and NO2;
- separate analyses for respiratory and cardiocirculatory outcomes;
- possible exploration of lagged associations.

The environmental-health integration should remain clearly described as exploratory and ecological.