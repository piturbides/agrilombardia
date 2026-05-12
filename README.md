# Human Health and Environment Data Science Laboratory

Statistical analysis of air pollution and health event data for the Human Health and Environment Data Science Laboratory project.

The project investigates differences in air pollution patterns between areas with different territorial and emission profiles in Lombardy, with a focus on the comparison between agricultural/rural and industrial/urban contexts.

The first part of the project focuses on environmental exposure data from ARPA Lombardia monitoring stations. The second part explores health event data and prepares population-normalized and age-specific health indicators. The third part integrates environmental indicators and health event rates into a common exploratory ecological framework.

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

## Part 3 — Environmental-health integration

The third part of the project integrates environmental pollutant indicators and health event rates into common datasets.

The aim is to move from separate environmental and health analyses to exploratory ecological comparisons between:

- seasonal or monthly pollutant concentrations;
- respiratory acute event rates;
- cardiocirculatory acute event rates;
- agricultural and industrial study areas.

This part does not aim to demonstrate individual-level causality. Instead, it investigates whether coherent temporal and territorial patterns are present in the available aggregated data.

The main output folder is:

```text
Dati/output/3-Environmental health integration/
```

The main code folder is:

```text
src/integration/
```

---

## 3.1 Seasonal environmental-health integration

The first environmental-health integration step combines seasonal pollutant indicators and seasonal health event rates.

Each row of the integrated dataset represents one combination of:

```text
SeasonYear × Season × Area
```

The integrated dataset contains:

- season year;
- meteorological season;
- study area;
- population denominator;
- seasonal respiratory acute event rate per 10,000 inhabitants;
- seasonal cardiocirculatory acute event rate per 10,000 inhabitants;
- seasonal mean NO2 concentration;
- seasonal mean PM2.5 concentration;
- readable time label for plots.

The health input is the seasonal rate table produced in Part 2.2:

```text
Dati/output/2-Health data/2.2-Health event aggregation/seasonal_health_events_rates_by_area.csv
```

The environmental inputs are the seasonal pollutant datasets produced in Part 1.3 and Part 1.4:

```text
Dati/output/1-Statistical tests/1.3-NO2_definitivo/seasonal_NO2_non_covid_dataset.csv
Dati/output/1-Statistical tests/1.4-PM25_definitivo/seasonal_PM25_non_covid_dataset.csv
```

The station-to-area mapping was defined as follows.

For NO2:

```text
Soresina → Agricultural
Rezzato  → Industrial
```

For PM2.5:

```text
Soresina                  → Agricultural
Brescia Villaggio Sereno  → Industrial
```

The final integrated seasonal dataset contains:

```text
36 rows
18 seasonal observations per study area
0 missing values after integration
```

The analysis included:

- loading seasonal health rates from Part 2.2;
- loading seasonal NO2 indicators from Part 1.3;
- loading seasonal PM2.5 indicators from Part 1.4;
- mapping monitoring stations to study areas;
- merging health and environmental indicators by season, season year and area;
- checking missing values after integration;
- producing combined-area scatter plots;
- producing area-specific scatter plots;
- producing standardized seasonal trend plots;
- computing Spearman correlations overall and separately by study area;
- exporting CSV summary tables and figures.

Spearman correlation was used because the analysis is exploratory, the number of observations is limited, and a linear relationship between pollutants and health event rates should not be assumed.

The main Spearman results were:

```text
Overall:
NO2 vs Respiratory rate: rho = 0.502, p = 0.0018
NO2 vs Cardiocirculatory rate: rho = 0.204, p = 0.2330
PM2.5 vs Respiratory rate: rho = 0.446, p = 0.0064
PM2.5 vs Cardiocirculatory rate: rho = 0.164, p = 0.3393

Industrial area:
NO2 vs Respiratory rate: rho = 0.364, p = 0.1372
NO2 vs Cardiocirculatory rate: rho = 0.383, p = 0.1168
PM2.5 vs Respiratory rate: rho = 0.280, p = 0.2610
PM2.5 vs Cardiocirculatory rate: rho = 0.428, p = 0.0762

Agricultural area:
NO2 vs Respiratory rate: rho = 0.583, p = 0.0111
NO2 vs Cardiocirculatory rate: rho = 0.119, p = 0.6390
PM2.5 vs Respiratory rate: rho = 0.569, p = 0.0138
PM2.5 vs Cardiocirculatory rate: rho = 0.148, p = 0.5590
```

**Main interpretation:**

Respiratory acute event rates showed the clearest association with seasonal pollutant indicators.

Overall, both NO2 and PM2.5 showed moderate positive and statistically significant associations with respiratory acute event rates. This suggests that seasons with higher pollutant concentrations tended to correspond to seasons with higher respiratory event rates.

The association was particularly evident in the agricultural area, where both NO2 and PM2.5 showed moderate positive and statistically significant correlations with respiratory rates.

Cardiocirculatory acute event rates did not show clear same-season associations with either NO2 or PM2.5. This does not mean that cardiocirculatory outcomes are irrelevant, because previous analyses showed that cardiocirculatory rates are consistently higher in the industrial area and that this pattern is not simply explained by age structure. However, the seasonal integration suggests that cardiocirculatory outcomes may depend more on structural, demographic, long-term or lagged factors than on same-season pollutant variation alone.

The results remain exploratory and ecological. The analysis does not adjust for meteorology, socioeconomic factors, comorbidities, smoking, occupational exposure or individual-level exposure history.

**Output folder:**

```text
Dati/output/3-Environmental health integration/3.1-Seasonal integration
```

**Main script:**

```text
src/integration/environment_health_integration.py
```

---

## Repository structure

### Main folders

```text
Dati/
├── raw/
│   ├── Brescia_VillagioSereno_PM25_2016_2025.csv
│   ├── Health_events_2015_2023.csv   # local only, ignored by Git
│   ├── Rezzato_NO2_2016_2025.csv
│   ├── Soresina_2016_2025_PM25.csv
│   ├── Soresina_NO2_2016_2025.csv
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
    ├── 2-Health data/
    │   ├── 2.1-Health data exploration/
    │   ├── 2.2-Health event aggregation/
    │   └── 2.3-Health age structure check/
    │
    └── 3-Environmental health integration/
        └── 3.1-Seasonal integration/

src/
├── data_loader.py
│
├── statistical_tests/
│   ├── preliminary_no2.py
│   ├── monthly_seasonal_no2.py
│   ├── no2_definitivo_non_covid.py
│   └── pm25_definitivo_non_covid.py
│
├── health_analysis/
│   ├── health_data_exploration.py
│   ├── health_event_aggregation.py
│   └── health_age_structure_check.py
│
└── integration/
    ├── __init__.py
    └── environment_health_integration.py
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

### Run the seasonal environmental-health integration

Use this in `main.py`:

```python
from src.integration.environment_health_integration import run_environment_health_integration


if __name__ == "__main__":
    run_environment_health_integration()
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
git commit -m "Add seasonal environmental health integration"
git commit -m "Update README after seasonal integration"
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

Formal statistical testing was not added to Part 2.3 because the age-specific rates are annual and only five paired years are available. Differences were therefore interpreted through descriptive rates, mean differences, ratios and visual patterns. More formal non-parametric correlation analysis is more meaningful in the environmental-health integration phase, especially at monthly or seasonal scale.

Part 3.1 integrates pollutant indicators and health event rates at seasonal scale and uses Spearman correlation. These correlations are exploratory and ecological. They should not be interpreted as individual-level causal evidence.

The seasonal environmental-health integration uses same-season pollutant indicators and same-season health rates. Possible delayed effects are not assessed in Part 3.1 and should be explored in future lag analyses.

Important unmeasured confounders include age beyond the applied stratification, sex, socioeconomic status, smoking, occupational exposure, comorbidities, healthcare access, event coding practices, meteorology and individual exposure history.

The geographical meaning of the municipality variable should also be interpreted carefully. If the municipality refers to event location rather than patient residence, area-level health rates may not perfectly represent the resident population.

The environmental exposure side is based on monitoring station proxies, while the health outcome side is aggregated over selected municipalities. This spatial mismatch is one of the main limitations of the project.

Any future comparison between pollutant concentrations and health events should be interpreted as an exploratory ecological analysis, not as evidence of individual-level causality.

---

## Next step

Part 1 of the project, focused on statistical tests of environmental pollutant data, is completed.

Part 2 has produced:

- a general health data exploration;
- population-normalized respiratory and cardiocirculatory rates;
- age-specific health event rates for the selected study areas.

Part 3 has started with the seasonal environmental-health integration.

The main result of Part 3.1 is that respiratory acute event rates show the clearest seasonal association with pollutant indicators. Both NO2 and PM2.5 show moderate positive associations with respiratory event rates, especially in the agricultural area. Cardiocirculatory event rates do not show clear same-season associations with the pollutant indicators.

The next analytical step is to extend the environmental-health integration beyond same-season seasonal analysis.

Possible next steps include:

- monthly environmental-health integration;
- lagged monthly analysis, for example pollutant concentration in one month vs health event rate in the following month;
- lagged seasonal analysis, for example pollutant concentration in one season vs health event rate in the following season;
- separate focus on respiratory outcomes, because they show the clearest same-season associations;
- secondary focus on cardiocirculatory outcomes, especially considering lagged exposure or age-specific rates;
- possible integration of age-specific outcomes, such as respiratory `65+` rates and cardiocirculatory `<65` rates.

The most reasonable next step is Part 3.2, focused on monthly environmental-health integration or lagged seasonal/monthly associations. This would increase the number of observations and help assess whether the associations observed in Part 3.1 are stable at a finer temporal scale.

The environmental-health integration should remain clearly described as exploratory and ecological.