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

- seasonal, monthly or weekly pollutant concentrations;
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

## 3.2 Monthly environmental-health integration

The second environmental-health integration step extends the seasonal integration performed in Part 3.1 to monthly scale.

Each row of the integrated dataset represents one combination of:

```text
MonthPeriod × Area
```

The integrated dataset contains:

- month period;
- calendar year;
- month;
- meteorological season;
- study area;
- population denominator;
- monthly respiratory acute event rate per 10,000 inhabitants;
- monthly cardiocirculatory acute event rate per 10,000 inhabitants;
- monthly mean NO2 concentration;
- monthly mean PM2.5 concentration;
- readable time label for plots.

The health input is the monthly rate table produced in Part 2.2:

```text
Dati/output/2-Health data/2.2-Health event aggregation/monthly_health_events_rates_by_area.csv
```

The environmental inputs are the monthly pollutant datasets produced in Part 1.3 and Part 1.4:

```text
Dati/output/1-Statistical tests/1.3-NO2_definitivo/monthly_NO2_non_covid_dataset.csv
Dati/output/1-Statistical tests/1.4-PM25_definitivo/monthly_PM25_non_covid_dataset.csv
```

The same station-to-area mapping used in Part 3.1 was retained.

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

The final integrated monthly dataset contains:

```text
120 rows
60 monthly observations per study area
0 missing values after integration
```

This corresponds exactly to:

```text
5 years × 12 months × 2 study areas = 120 observations
```

The analysis included:

- loading monthly health rates from Part 2.2;
- loading monthly NO2 indicators from Part 1.3;
- loading monthly PM2.5 indicators from Part 1.4;
- mapping monitoring stations to study areas;
- merging health and environmental indicators by month and area;
- checking missing values after integration;
- producing combined-area scatter plots;
- producing area-specific scatter plots;
- producing standardized monthly trend plots;
- computing Spearman correlations overall and separately by study area;
- computing season-stratified Spearman correlations as a sensitivity check;
- exporting CSV summary tables and figures.

Spearman correlation was used because the analysis is exploratory and ecological, the variables may not follow a normal distribution, and a strictly linear relationship between pollutant concentrations and health event rates should not be assumed.

The main overall Spearman results were:

```text
Overall:
NO2 vs Respiratory rate: rho = 0.485, p = 2.01e-08
NO2 vs Cardiocirculatory rate: rho = 0.281, p = 0.0019
PM2.5 vs Respiratory rate: rho = 0.458, p = 1.47e-07
PM2.5 vs Cardiocirculatory rate: rho = 0.259, p = 0.0043
```

The area-specific results were:

```text
Industrial area:
NO2 vs Respiratory rate: rho = 0.510, p = 3.15e-05
NO2 vs Cardiocirculatory rate: rho = 0.378, p = 0.0029
PM2.5 vs Respiratory rate: rho = 0.496, p = 5.50e-05
PM2.5 vs Cardiocirculatory rate: rho = 0.432, p = 0.00057

Agricultural area:
NO2 vs Respiratory rate: rho = 0.457, p = 0.00024
NO2 vs Cardiocirculatory rate: rho = 0.255, p = 0.0497
PM2.5 vs Respiratory rate: rho = 0.411, p = 0.0011
PM2.5 vs Cardiocirculatory rate: rho = 0.211, p = 0.1056
```

**Main interpretation:**

At monthly scale, both NO2 and PM2.5 show positive associations with acute health event rates.

The clearest and most consistent result concerns respiratory acute event rates. Both NO2 and PM2.5 show moderate positive and statistically significant associations with respiratory rates overall and within both study areas. This confirms respiratory outcomes as the most coherent endpoint for the environmental-health integration.

Cardiocirculatory acute event rates also show positive associations with pollutant indicators, but the relationships are weaker. The associations are clearer in the industrial area, especially for PM2.5, while they are weaker or not statistically significant in the agricultural area.

A season-stratified sensitivity analysis was also performed. This analysis showed that most within-season correlations are weak or very weak and not statistically significant. Therefore, the significant monthly correlations observed in the full dataset are likely influenced by the shared seasonal structure of air pollution and health events.

The most relevant season-stratified results were observed in the industrial area during autumn:

```text
Autumn, Industrial area:
NO2 vs Cardiocirculatory rate: rho = 0.568, p = 0.027
PM2.5 vs Cardiocirculatory rate: rho = 0.536, p = 0.040
```

These autumn industrial associations are potentially interesting, but they are based on only 15 observations and should therefore be interpreted cautiously.

Overall, Part 3.2 confirms that pollutant and health patterns are temporally coherent at monthly scale, especially for respiratory outcomes. However, the season-stratified analysis suggests that these associations are largely driven by seasonality. The results remain exploratory and ecological, and they cannot be interpreted as individual-level causal evidence.

**Output folder:**

```text
Dati/output/3-Environmental health integration/3.2-Monthly integration
```

**Main script:**

```text
src/integration/monthly_environment_health_integration.py
```

---

## 3.3 Monthly lag analysis

The third environmental-health integration step explores lagged associations between monthly pollutant indicators and current-month health event rates.

This analysis uses the monthly integrated dataset produced in Part 3.2 and tests whether pollutant concentrations in previous months are more strongly associated with current-month health event rates than same-month pollutant concentrations.

Each row of the input dataset represents one combination of:

```text
MonthPeriod × Area
```

The health input is the monthly integrated dataset produced in Part 3.2:

```text
Dati/output/3-Environmental health integration/3.2-Monthly integration/monthly_environment_health_integrated_dataset.csv
```

The lagged analysis used the following exposure lags:

```text
Lag 0 = pollutant concentration in the same month as the health event rate
Lag 1 = pollutant concentration one month before the health event rate
Lag 2 = pollutant concentration two months before the health event rate
Lag 3 = pollutant concentration three months before the health event rate
```

The maximum lag was limited to 3 months to keep the analysis interpretable and to avoid excessive loss of observations.

A key methodological safeguard was introduced to avoid incorrect temporal links across the 2019–2023 gap. Lagged pollutant values were retained only if the lagged month was exactly the expected number of months before the current health month.

For example, January 2023 was not allowed to use December 2019 as lag-1 exposure. Since the actual month difference between December 2019 and January 2023 is 37 months, the lagged value was rejected and set to missing.

The lag availability check confirmed that the temporal gap was handled correctly:

```text
Overall:
Lag 0 = 120 available values
Lag 1 = 116 available values
Lag 2 = 112 available values
Lag 3 = 108 available values

Industrial area:
Lag 0 = 60 available values
Lag 1 = 58 available values
Lag 2 = 56 available values
Lag 3 = 54 available values

Agricultural area:
Lag 0 = 60 available values
Lag 1 = 58 available values
Lag 2 = 56 available values
Lag 3 = 54 available values
```

The final lagged dataset contains:

```text
120 rows
27 columns
```

The analysis included:

- loading the monthly integrated dataset from Part 3.2;
- creating lagged NO2 variables for lag 0, lag 1, lag 2 and lag 3;
- creating lagged PM2.5 variables for lag 0, lag 1, lag 2 and lag 3;
- validating lagged values to avoid crossing the 2019–2023 temporal gap;
- checking lag availability for each pollutant, lag and study area;
- computing Spearman correlations between lagged pollutant indicators and current-month health event rates;
- computing correlations overall and separately by study area;
- identifying the descriptively strongest lag for each pollutant-outcome-area combination;
- producing rho-versus-lag plots;
- producing best-lag scatter plots;
- exporting CSV summary tables and figures.

Spearman correlation was used because the analysis is exploratory and ecological, the variables may not follow a normal distribution, and a strictly linear exposure-response relationship should not be assumed.

The main overall lagged Spearman results were:

```text
Overall NO2 vs Respiratory rate:
Lag 0: rho = 0.485, p = 2.01e-08
Lag 1: rho = 0.445, p = 5.64e-07
Lag 2: rho = 0.320, p = 0.00057
Lag 3: rho = 0.109, p = 0.261

Overall PM2.5 vs Respiratory rate:
Lag 0: rho = 0.458, p = 1.47e-07
Lag 1: rho = 0.427, p = 1.78e-06
Lag 2: rho = 0.304, p = 0.0011
Lag 3: rho = 0.065, p = 0.502

Overall NO2 vs Cardiocirculatory rate:
Lag 0: rho = 0.281, p = 0.0019
Lag 1: rho = 0.190, p = 0.0409
Lag 2: rho = 0.101, p = 0.291
Lag 3: rho = 0.022, p = 0.822

Overall PM2.5 vs Cardiocirculatory rate:
Lag 0: rho = 0.259, p = 0.0043
Lag 1: rho = 0.163, p = 0.0806
Lag 2: rho = 0.124, p = 0.191
Lag 3: rho = 0.016, p = 0.871
```

The main area-specific results were:

```text
Industrial area, NO2 vs Respiratory rate:
Lag 0: rho = 0.510, p = 3.15e-05
Lag 1: rho = 0.458, p = 0.00030
Lag 2: rho = 0.305, p = 0.0221
Lag 3: rho = 0.091, p = 0.513

Industrial area, PM2.5 vs Respiratory rate:
Lag 0: rho = 0.496, p = 5.50e-05
Lag 1: rho = 0.447, p = 0.00043
Lag 2: rho = 0.323, p = 0.0152
Lag 3: rho = 0.115, p = 0.407

Industrial area, NO2 vs Cardiocirculatory rate:
Lag 0: rho = 0.378, p = 0.0029
Lag 1: rho = 0.294, p = 0.0251
Lag 2: rho = 0.204, p = 0.1310
Lag 3: rho = 0.074, p = 0.5966

Industrial area, PM2.5 vs Cardiocirculatory rate:
Lag 0: rho = 0.432, p = 0.00057
Lag 1: rho = 0.394, p = 0.0022
Lag 2: rho = 0.250, p = 0.0626
Lag 3: rho = 0.085, p = 0.5396

Agricultural area, NO2 vs Respiratory rate:
Lag 0: rho = 0.457, p = 0.00024
Lag 1: rho = 0.424, p = 0.00091
Lag 2: rho = 0.315, p = 0.0179
Lag 3: rho = 0.114, p = 0.413

Agricultural area, PM2.5 vs Respiratory rate:
Lag 0: rho = 0.411, p = 0.0011
Lag 1: rho = 0.420, p = 0.0010
Lag 2: rho = 0.295, p = 0.0271
Lag 3: rho = 0.043, p = 0.760

Agricultural area, NO2 vs Cardiocirculatory rate:
Lag 0: rho = 0.255, p = 0.0497
Lag 1: rho = 0.146, p = 0.276
Lag 2: rho = 0.047, p = 0.733
Lag 3: rho = 0.021, p = 0.881

Agricultural area, PM2.5 vs Cardiocirculatory rate:
Lag 0: rho = 0.211, p = 0.106
Lag 1: rho = 0.085, p = 0.524
Lag 2: rho = 0.093, p = 0.497
Lag 3: rho = 0.046, p = 0.740
```

**Main interpretation:**

The monthly lag analysis did not identify stronger delayed associations at lag 1, lag 2 or lag 3 months. Most pollutant-health associations were strongest at lag 0 and progressively weakened with increasing lag.

Respiratory outcomes remained the most coherent endpoint. Both NO2 and PM2.5 showed moderate positive associations with respiratory rates at lag 0, with some persistence at lag 1 and weaker associations at longer lags.

The only small exception was PM2.5 versus respiratory rates in the agricultural area, where lag 1 had a slightly higher rho than lag 0:

```text
Lag 0: rho = 0.411
Lag 1: rho = 0.420
```

However, the difference was minimal and should not be interpreted as strong evidence of a delayed effect.

Cardiocirculatory associations were weaker. They were more visible in the industrial area, especially for PM2.5, but they were still strongest at lag 0 and did not show evidence of stronger delayed associations at lag 1–3 months.

Overall, Part 3.3 suggests that the observed monthly environmental-health associations are mainly synchronous and seasonally structured rather than clearly delayed. The results remain exploratory and ecological. They do not demonstrate individual-level causal effects, but they clarify the temporal structure of the monthly pollutant-health associations.

**Output folder:**

```text
Dati/output/3-Environmental health integration/3.3-Monthly lag analysis
```

**Main script:**

```text
src/integration/monthly_lag_analysis.py
```

---

## 3.4 Weekly lag analysis

The fourth environmental-health integration step refines the monthly lag analysis by exploring lagged associations at weekly scale.

This analysis was introduced because the monthly lag analysis showed that most pollutant-health associations were strongest at lag 0 months. However, a same-month association may still include shorter delayed effects occurring within the same month. Weekly aggregation allows the project to investigate whether pollutant concentrations in the previous 1–4 weeks are more strongly associated with current-week health event rates than same-week pollutant concentrations.

Each row of the weekly integrated dataset represents one combination of:

```text
WeekStart × Area
```

The weekly integrated dataset contains:

- week start date;
- calendar year;
- ISO week number;
- study area;
- population denominator;
- weekly respiratory acute event rate per 10,000 inhabitants;
- weekly cardiocirculatory acute event rate per 10,000 inhabitants;
- weekly mean NO2 concentration;
- weekly mean PM2.5 concentration;
- readable time label for plots.

The environmental inputs are the raw pollutant datasets used in Part 1.3 and Part 1.4:

```text
Dati/raw/Soresina_NO2_2016_2025.csv
Dati/raw/Rezzato_NO2_2016_2025.csv
Dati/raw/Soresina_2016_2025_PM25.csv
Dati/raw/Brescia_VillagioSereno_PM25_2016_2025.csv
```

The health input is the selected health event table produced in Part 2.2:

```text
Dati/output/2-Health data/2.2-Health event aggregation/health_events_selected_areas_outcomes.csv
```

The annual population denominators were derived from:

```text
Dati/output/2-Health data/2.2-Health event aggregation/annual_health_events_rates_by_area.csv
```

The same station-to-area mapping used in the previous integration steps was retained.

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

The final weekly integrated dataset contains:

```text
522 rows
261 weekly observations per study area
```

The included years are:

```text
2016, 2017, 2018, 2019, 2023
```

The missing value check showed:

```text
WeekStart: 0 missing values
Year: 0 missing values
Week: 0 missing values
Area: 0 missing values
Population: 0 missing values
Cardiocirculatory_rate_per_10000: 0 missing values
Respiratory_rate_per_10000: 0 missing values
TimeLabel: 0 missing values
NO2_mean: 0 missing values
PM25_mean: 2 missing values
```

The weekly lagged analysis used the following exposure lags:

```text
Lag 0 = pollutant concentration in the same week as the health event rate
Lag 1 = pollutant concentration one week before the health event rate
Lag 2 = pollutant concentration two weeks before the health event rate
Lag 3 = pollutant concentration three weeks before the health event rate
Lag 4 = pollutant concentration four weeks before the health event rate
```

The maximum lag was limited to 4 weeks because four weeks approximately correspond to one month. This makes the weekly analysis directly comparable with the monthly lag analysis while preserving a finer temporal resolution.

As in Part 3.3, a key methodological safeguard was introduced to avoid incorrect temporal links across the 2019–2023 gap. Lagged pollutant values were retained only if the lagged week was exactly the expected number of weeks before the current health week.

For example, the first weeks of 2023 were not allowed to use the last weeks of 2019 as lagged exposure values. Since the actual temporal difference is much larger than the expected weekly lag, those lagged values were rejected and set to missing.

The lag availability check confirmed that the temporal gap was handled correctly.

For NO2:

```text
Overall:
Lag 0 = 522 available values
Lag 1 = 518 available values
Lag 2 = 514 available values
Lag 3 = 510 available values
Lag 4 = 506 available values

Industrial area:
Lag 0 = 261 available values
Lag 1 = 259 available values
Lag 2 = 257 available values
Lag 3 = 255 available values
Lag 4 = 253 available values

Agricultural area:
Lag 0 = 261 available values
Lag 1 = 259 available values
Lag 2 = 257 available values
Lag 3 = 255 available values
Lag 4 = 253 available values
```

For PM2.5:

```text
Overall:
Lag 0 = 520 available values
Lag 1 = 516 available values
Lag 2 = 512 available values
Lag 3 = 508 available values
Lag 4 = 504 available values

Industrial area:
Lag 0 = 260 available values
Lag 1 = 258 available values
Lag 2 = 256 available values
Lag 3 = 254 available values
Lag 4 = 252 available values

Agricultural area:
Lag 0 = 260 available values
Lag 1 = 258 available values
Lag 2 = 256 available values
Lag 3 = 254 available values
Lag 4 = 252 available values
```

The final weekly lagged dataset contains:

```text
522 rows
30 columns
```

The analysis included:

- loading raw NO2 and PM2.5 pollutant datasets;
- aggregating pollutant data to weekly mean concentrations;
- loading selected health event records from Part 2.2;
- aggregating health events to weekly counts by area and outcome;
- computing weekly event rates per 10,000 inhabitants using annual area-level population denominators;
- mapping monitoring stations to study areas;
- merging weekly health and environmental indicators by week and area;
- creating lagged NO2 variables for lag 0, lag 1, lag 2, lag 3 and lag 4 weeks;
- creating lagged PM2.5 variables for lag 0, lag 1, lag 2, lag 3 and lag 4 weeks;
- validating lagged values to avoid crossing the 2019–2023 temporal gap;
- checking lag availability for each pollutant, lag and study area;
- computing Spearman correlations between lagged pollutant indicators and current-week health event rates;
- computing correlations overall and separately by study area;
- identifying the descriptively strongest weekly lag for each pollutant-outcome-area combination;
- producing rho-versus-lag plots;
- producing best-lag scatter plots;
- exporting CSV summary tables and figures.

Spearman correlation was used because the analysis is exploratory and ecological, the variables may not follow a normal distribution, and a strictly linear exposure-response relationship should not be assumed.

The weekly lag analysis produced 60 Spearman correlation results:

```text
3 groups × 2 pollutants × 2 outcomes × 5 weekly lags = 60 correlations
```

The main overall weekly lagged results were:

```text
Overall NO2 vs Respiratory rate:
Lag 0: rho ≈ 0.336
Lag 1: rho ≈ 0.356
Lag 2: rho ≈ 0.351
Lag 3: rho ≈ 0.327
Lag 4: rho ≈ 0.318

Overall PM2.5 vs Respiratory rate:
Lag 0: rho ≈ 0.306
Lag 1: rho ≈ 0.342
Lag 2: rho ≈ 0.297
Lag 3: rho ≈ 0.284
Lag 4: rho ≈ 0.279

Overall NO2 vs Cardiocirculatory rate:
Lag 0: rho ≈ 0.203
Lag 1: rho ≈ 0.209
Lag 2: rho ≈ 0.209
Lag 3: rho ≈ 0.178
Lag 4: rho ≈ 0.168

Overall PM2.5 vs Cardiocirculatory rate:
Lag 0: rho ≈ 0.199
Lag 1: rho ≈ 0.212
Lag 2: rho ≈ 0.164
Lag 3: rho ≈ 0.147
Lag 4: rho ≈ 0.151
```

The main area-specific results were:

```text
Industrial area, NO2 vs Respiratory rate:
Lag 0: rho ≈ 0.383
Lag 1: rho ≈ 0.441
Lag 2: rho ≈ 0.444
Lag 3: rho ≈ 0.387
Lag 4: rho ≈ 0.365

Industrial area, PM2.5 vs Respiratory rate:
Lag 0: rho ≈ 0.350
Lag 1: rho ≈ 0.412
Lag 2: rho ≈ 0.364
Lag 3: rho ≈ 0.346
Lag 4: rho ≈ 0.337

Industrial area, NO2 vs Cardiocirculatory rate:
Lag 0: rho ≈ 0.325
Lag 1: rho ≈ 0.324
Lag 2: rho ≈ 0.346
Lag 3: rho ≈ 0.326
Lag 4: rho ≈ 0.270

Industrial area, PM2.5 vs Cardiocirculatory rate:
Lag 0: rho ≈ 0.360
Lag 1: rho ≈ 0.368
Lag 2: rho ≈ 0.354
Lag 3: rho ≈ 0.320
Lag 4: rho ≈ 0.278

Agricultural area, NO2 vs Respiratory rate:
Lag 0: rho ≈ 0.300
Lag 1: rho ≈ 0.298
Lag 2: rho ≈ 0.288
Lag 3: rho ≈ 0.283
Lag 4: rho ≈ 0.282

Agricultural area, PM2.5 vs Respiratory rate:
Lag 0: rho ≈ 0.259
Lag 1: rho ≈ 0.284
Lag 2: rho ≈ 0.238
Lag 3: rho ≈ 0.228
Lag 4: rho ≈ 0.223

Agricultural area, NO2 vs Cardiocirculatory rate:
Lag 0: rho ≈ 0.139
Lag 1: rho ≈ 0.149
Lag 2: rho ≈ 0.134
Lag 3: rho ≈ 0.100
Lag 4: rho ≈ 0.129

Agricultural area, PM2.5 vs Cardiocirculatory rate:
Lag 0: rho ≈ 0.118
Lag 1: rho ≈ 0.150
Lag 2: rho ≈ 0.057
Lag 3: rho ≈ 0.059
Lag 4: rho ≈ 0.109
```

**Main interpretation:**

The weekly lag analysis provides additional temporal detail compared with the monthly lag analysis.

In Part 3.3, most pollutant-health associations were strongest at lag 0 months. Part 3.4 shows that this does not necessarily mean that there is no delay. At weekly scale, several associations, especially respiratory associations, reached their maximum at lag 1 or lag 2 weeks.

The clearest pattern was observed for respiratory acute event rates.

Overall, both NO2 and PM2.5 showed positive associations with respiratory rates across all weekly lags, with the highest correlations generally observed at lag 1 week.

In the industrial area, the respiratory signal was particularly coherent:

```text
Industrial NO2 vs Respiratory rate:
highest rho at lag 2 weeks

Industrial PM2.5 vs Respiratory rate:
highest rho at lag 1 week
```

This suggests that the same-month associations observed in Part 3.3 may partly contain shorter delayed associations occurring within the same month, especially in the industrial area.

Cardiocirculatory outcomes showed weaker and more area-dependent patterns. The industrial area showed positive short-lag associations, especially for PM2.5, but the curves were relatively flat across lag 0 to lag 2. Therefore, it would be inappropriate to identify a precise cardiovascular lag. In the agricultural area, cardiocirculatory associations were weak or very weak across all weekly lags.

Overall, Part 3.4 confirms respiratory acute event rates as the most consistent health endpoint in the project. It refines the temporal interpretation of the environmental-health association: the signal is not clearly delayed at monthly scale, but weekly analysis suggests possible short delays of approximately one to two weeks.

The results remain exploratory and ecological. They do not demonstrate individual-level causal effects. Weekly rates can be noisier than monthly or seasonal rates, and the analysis does not adjust for meteorology, respiratory infections, temporal autocorrelation, socioeconomic factors or individual exposure history.

**Output folder:**

```text
Dati/output/3-Environmental health integration/3.4-Weekly lag analysis
```

**Main script:**

```text
src/integration/weekly_lag_analysis.py
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
        ├── 3.1-Seasonal integration/
        ├── 3.2-Monthly integration/
        ├── 3.3-Monthly lag analysis/
        └── 3.4-Weekly lag analysis/

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
    ├── environment_health_integration.py
    ├── monthly_environment_health_integration.py
    ├── monthly_lag_analysis.py
    └── weekly_lag_analysis.py
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

### Run the monthly environmental-health integration

Use this in `main.py`:

```python
from src.integration.monthly_environment_health_integration import run_monthly_environment_health_integration


if __name__ == "__main__":
    run_monthly_environment_health_integration()
```

### Run the monthly lag analysis

Use this in `main.py`:

```python
from src.integration.monthly_lag_analysis import run_monthly_lag_analysis


if __name__ == "__main__":
    run_monthly_lag_analysis()
```

### Run the weekly lag analysis

Use this in `main.py`:

```python
from src.integration.weekly_lag_analysis import run_weekly_lag_analysis


if __name__ == "__main__":
    run_weekly_lag_analysis()
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
git commit -m "Add monthly environmental health integration"
git commit -m "Add monthly lag analysis"
git commit -m "Add weekly lag analysis"
git commit -m "Update README after seasonal integration"
git commit -m "Update README after monthly integration"
git commit -m "Update README after monthly lag analysis"
git commit -m "Update README after weekly lag analysis"
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

Formal statistical testing was not added to Part 2.3 because the age-specific rates are annual and only five paired years are available. Differences were therefore interpreted through descriptive rates, mean differences, ratios and visual patterns. More formal non-parametric correlation analysis is more meaningful in the environmental-health integration phase, especially at monthly, seasonal or weekly scale.

Part 3.1 integrates pollutant indicators and health event rates at seasonal scale and uses Spearman correlation. These correlations are exploratory and ecological. They should not be interpreted as individual-level causal evidence.

The seasonal environmental-health integration uses same-season pollutant indicators and same-season health rates. Possible delayed effects are not assessed in Part 3.1 and are explored in later lag analyses.

Part 3.2 extends the environmental-health integration to monthly scale and increases the number of observations from 36 seasonal rows to 120 monthly rows. This improves temporal detail and prepares the dataset for lag analysis.

The monthly integration shows positive associations between pollutant indicators and health event rates, especially for respiratory outcomes. However, the season-stratified sensitivity analysis suggests that most of the significant monthly correlations are largely driven by the shared annual seasonal cycle of air pollution and health events.

Therefore, Part 3.2 should be interpreted as evidence of coherent temporal ecological patterns, not as evidence of independent within-season or individual-level exposure-response effects.

Part 3.3 explores monthly lagged associations using lag 0, lag 1, lag 2 and lag 3 months. Lagged pollutant values are validated so that they are retained only when the lagged month is exactly the expected number of months before the current health month. This prevents incorrect temporal links across the 2019–2023 gap.

The monthly lag analysis shows that most pollutant-health associations are strongest at lag 0 and progressively weaken at longer monthly lags. Therefore, the observed monthly associations appear mainly synchronous and seasonally structured rather than clearly delayed at the monthly scale.

Part 3.4 refines the lag analysis at weekly scale using lag 0, lag 1, lag 2, lag 3 and lag 4 weeks. Lagged pollutant values are validated so that they are retained only when the lagged week is exactly the expected number of weeks before the current health week. This prevents incorrect temporal links across the 2019–2023 gap.

The weekly lag analysis suggests that some same-month associations observed in Part 3.3 may include shorter delayed patterns of approximately 1–2 weeks, especially for respiratory outcomes in the industrial area. However, these associations remain exploratory and ecological.

Weekly health event rates can be noisier than monthly or seasonal rates because weekly event counts are smaller. For this reason, the weekly lag analysis should be interpreted together with the broader seasonal and monthly results rather than as a standalone causal model.

Lag analyses should not be interpreted as evidence of causal delayed effects. Lagged correlations may still be influenced by seasonality, temporal autocorrelation, meteorology and unmeasured confounding.

Important unmeasured confounders include age beyond the applied stratification, sex, socioeconomic status, smoking, occupational exposure, comorbidities, healthcare access, event coding practices, meteorology, respiratory infections, influenza circulation and individual exposure history.

The geographical meaning of the municipality variable should also be interpreted carefully. If the municipality refers to event location rather than patient residence, area-level health rates may not perfectly represent the resident population.

The environmental exposure side is based on monitoring station proxies, while the health outcome side is aggregated over selected municipalities. This spatial mismatch is one of the main limitations of the project.

Any future comparison between pollutant concentrations and health events should be interpreted as an exploratory ecological analysis, not as evidence of individual-level causality.

---

## Current project status and possible next steps

Part 1 of the project, focused on statistical tests of environmental pollutant data, is completed.

Part 2 has produced:

- a general health data exploration;
- population-normalized respiratory and cardiocirculatory rates;
- age-specific health event rates for the selected study areas.

Part 3 has produced:

- a seasonal environmental-health integration;
- a monthly environmental-health integration;
- a monthly lag analysis;
- a weekly lag analysis.

The main result of Part 3.1 is that respiratory acute event rates show the clearest seasonal association with pollutant indicators. Both NO2 and PM2.5 show moderate positive associations with respiratory event rates, especially in the agricultural area. Cardiocirculatory event rates do not show clear same-season seasonal associations with the pollutant indicators.

Part 3.2 confirms the relevance of respiratory outcomes at monthly scale. Both NO2 and PM2.5 show moderate positive and statistically significant associations with respiratory acute event rates overall and within both study areas. Cardiocirculatory associations are weaker, but they are more visible in the industrial area, especially for PM2.5.

However, the season-stratified sensitivity analysis in Part 3.2 shows that most within-season correlations are weak or not statistically significant. This suggests that the overall monthly associations are largely influenced by the shared seasonal structure of pollutant concentrations and acute health event rates.

Part 3.3 shows that lagged pollutant indicators at 1–3 months do not generally improve the strength of the associations compared with same-month pollutant indicators. Most associations are strongest at lag 0 and progressively weaken with increasing monthly lag. This suggests that the observed monthly environmental-health associations are mainly synchronous and seasonally structured rather than clearly delayed at the monthly scale.

Part 3.4 refines this conclusion. At weekly scale, some associations, especially respiratory associations in the industrial area, are strongest at lag 1 or lag 2 weeks. This suggests that the same-month associations observed in Part 3.3 may partly contain shorter delayed patterns within the month. The most coherent weekly lag signal concerns respiratory acute event rates, while cardiocirculatory outcomes remain weaker and more area-dependent.

At the current stage, the project provides a coherent exploratory ecological framework linking pollutant indicators and health event rates at different temporal scales. The strongest and most defensible message is that respiratory acute event rates show the most consistent temporal coherence with NO2 and PM2.5 indicators across seasonal, monthly and weekly scales. Cardiocirculatory outcomes show weaker associations, but they remain relevant because previous health analyses showed a stable higher burden in the industrial area, especially in the `<65` age group.

This represents a reasonable stopping point for the current phase of the project. Future developments can be decided based on course requirements and feedback from the instructor.

Possible future extensions include:

- adding meteorological variables such as temperature, humidity, precipitation, wind speed or atmospheric stability;
- exploring emission inventory data or additional pollutants such as NH3;
- testing more formal statistical models with adjustment for seasonality and temporal autocorrelation;
- considering moving-average exposure indicators rather than simple single-lag indicators;
- exploring cumulative weekly exposure indicators;
- exploring age-specific environmental-health integration as a secondary sensitivity analysis;
- focusing more specifically on respiratory outcomes, which currently show the clearest environmental-health temporal pattern;
- refining exposure assessment by adding more monitoring stations or spatially averaged pollutant indicators;
- considering more advanced distributed lag approaches only if additional data and modelling time are available.

Any future extension should remain clearly framed as ecological unless individual-level exposure and health data become available.