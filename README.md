# Human Health and Environment Data Science Laboratory

Statistical analysis of air pollution and health event data for the Human Health and Environment Data Science Laboratory project.

The project investigates differences in air pollution patterns between areas with different territorial and emission profiles in Lombardy, with a focus on the comparison between agricultural/rural and industrial/urban contexts.

The first part of the project focuses on environmental exposure data from ARPA Lombardia monitoring stations. The second part explores health event data and prepares population-normalized and age-specific health indicators. The third part integrates station-based environmental indicators and health event rates into a common exploratory ecological framework. The fourth part introduces a more robust exposure reconstruction using ARPA Lombardia ModAria municipal pollutant estimates for all selected municipalities in the two study areas, integrates these area-level exposure indicators with the health outcomes, and completes the analytical coding pipeline with ModAria monthly and weekly lag analyses.

---

## Project framework

The project is based on the general idea that different emission contexts may contribute differently to air pollution levels and, potentially, to health-related outcomes.

The current environmental analysis focuses on:

- **NO2**, mainly interpreted as a combustion-related pollutant associated with traffic, heating and industrial activities;
- **PM2.5**, interpreted as a health-relevant fine particulate pollutant with both primary and secondary components.

The central comparison of the project is between:

- an **industrial/urban area**;
- an **agricultural/rural area**.

The project should always be interpreted within this industrial-versus-agricultural framework. The objective is not only to compute pollutant-health correlations, but to understand whether two areas with different territorial and emission profiles show different environmental patterns and whether these differences are reflected in respiratory and cardiocirculatory health indicators.

For the definitive environmental analyses, the COVID-related years **2020, 2021 and 2022** were excluded to avoid potential bias due to abnormal changes in mobility, traffic, industrial activities and emission patterns.

The retained years for the definitive station-based environmental analyses are:

```text
2016, 2017, 2018, 2019, 2023, 2024, 2025
```

The health dataset currently contains the following available years:

```text
2015, 2016, 2017, 2018, 2019, 2023
```

Years 2020, 2021 and 2022 are not present in the health dataset.

For the health-environment integration steps, the retained common years are:

```text
2016, 2017, 2018, 2019, 2023
```

The first environmental-health pipeline used monitoring station proxies:

```text
NO2:
Soresina → Agricultural
Rezzato  → Industrial

PM2.5:
Soresina                  → Agricultural
Brescia Villaggio Sereno  → Industrial
```

This station-based approach was useful for developing and validating the full analytical workflow. However, it has an important limitation: health outcomes are aggregated over 37 selected municipalities, while pollutant exposure was represented by one monitoring station per pollutant and area.

For this reason, Part 4 introduces ARPA Lombardia **ModAria municipal pollutant estimates**, downloaded for all selected municipalities and for both pollutants. These data allow the project to move from single-station exposure proxies to municipality-based area exposure indicators.

The main ModAria exposure indicator for health integration is the **population-weighted area exposure**, because it weights municipal pollutant values by the population living in each municipality. The **arithmetic area mean** is retained as a secondary sensitivity and descriptive territorial indicator.

The project should always be interpreted as an exploratory ecological analysis. Pollutant concentrations are represented by monitoring stations or municipality-level estimates, while health outcomes are aggregated over selected municipalities. Therefore, the analysis can identify coherent territorial and temporal patterns, but it cannot demonstrate individual-level causal effects.

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

Soresina and Rezzato show broadly similar NO2 dynamics, strongly dominated by seasonality. Soresina tends to show slightly higher NO2 concentrations, especially in colder periods, but the magnitude of the difference is modest. This suggests that NO2 alone does not clearly separate the agricultural and industrial territorial contexts when only one monitoring station per area is used.

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

## Part 3 — Station-based environmental-health integration

The third part of the project integrates station-based environmental pollutant indicators and health event rates into common datasets.

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

The final integrated seasonal dataset contains:

```text
36 rows
18 seasonal observations per study area
0 missing values after integration
```

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

The clearest and most consistent result concerns respiratory acute event rates. Both NO2 and PM2.5 show moderate positive and statistically significant associations with respiratory rates overall and within both study areas.

Cardiocirculatory acute event rates also show positive associations with pollutant indicators, but the relationships are weaker. The associations are clearer in the industrial area, especially for PM2.5, while they are weaker or not statistically significant in the agricultural area.

A season-stratified sensitivity analysis showed that most within-season correlations are weak or very weak and not statistically significant. Therefore, the significant monthly correlations observed in the full dataset are likely influenced by the shared seasonal structure of air pollution and health events.

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

The lagged analysis used the following exposure lags:

```text
Lag 0 = pollutant concentration in the same month as the health event rate
Lag 1 = pollutant concentration one month before the health event rate
Lag 2 = pollutant concentration two months before the health event rate
Lag 3 = pollutant concentration three months before the health event rate
```

A key methodological safeguard was introduced to avoid incorrect temporal links across the 2019–2023 gap. Lagged pollutant values were retained only if the lagged month was exactly the expected number of months before the current health month.

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

**Main interpretation:**

The monthly lag analysis did not identify stronger delayed associations at lag 1, lag 2 or lag 3 months. Most pollutant-health associations were strongest at lag 0 and progressively weakened with increasing lag.

Respiratory outcomes remained the most coherent endpoint. Both NO2 and PM2.5 showed moderate positive associations with respiratory rates at lag 0, with some persistence at lag 1 and weaker associations at longer lags.

Overall, Part 3.3 suggests that the observed monthly environmental-health associations are mainly synchronous and seasonally structured rather than clearly delayed at the monthly scale.

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

The weekly lagged analysis used the following exposure lags:

```text
Lag 0 = pollutant concentration in the same week as the health event rate
Lag 1 = pollutant concentration one week before the health event rate
Lag 2 = pollutant concentration two weeks before the health event rate
Lag 3 = pollutant concentration three weeks before the health event rate
Lag 4 = pollutant concentration four weeks before the health event rate
```

As in Part 3.3, lagged pollutant values were validated to avoid incorrect temporal links across the 2019–2023 gap.

The final weekly integrated dataset contains:

```text
522 rows
261 weekly observations per study area
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
```

The main area-specific respiratory results were:

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
```

**Main interpretation:**

The weekly lag analysis provides additional temporal detail compared with the monthly lag analysis.

At weekly scale, several associations, especially respiratory associations, reached their maximum at lag 1 or lag 2 weeks. This suggests that the same-month associations observed in Part 3.3 may partly contain shorter delayed associations occurring within the same month, especially in the industrial area.

Cardiocirculatory outcomes showed weaker and more area-dependent patterns. The industrial area showed positive short-lag associations, especially for PM2.5, but the curves were relatively flat across lag 0 to lag 2. Therefore, it would be inappropriate to identify a precise cardiovascular lag. In the agricultural area, cardiocirculatory associations were weak or very weak across all weekly lags.

Overall, Part 3.4 confirms respiratory acute event rates as the most consistent health endpoint in the project. It refines the temporal interpretation of the environmental-health association: the signal is not clearly delayed at monthly scale, but weekly analysis suggests possible short delays of approximately one to two weeks.

**Output folder:**

```text
Dati/output/3-Environmental health integration/3.4-Weekly lag analysis
```

**Main script:**

```text
src/integration/weekly_lag_analysis.py
```

---

## Part 4 — ModAria municipal exposure reconstruction

Part 4 starts a new environmental exposure phase based on ARPA Lombardia ModAria municipal pollutant estimates.

The reason for introducing Part 4 is that the previous environmental-health pipeline was based on one monitoring station per pollutant and study area. This was useful for building the analytical framework, but it created a spatial mismatch: pollutant exposure was measured at single stations, while health outcomes were aggregated over 37 selected municipalities.

The ModAria municipal datasets allow a more robust exposure reconstruction because they provide pollutant estimates for each municipality included in the agricultural and industrial study areas. These values are likely based on ARPA Lombardia modelling or interpolation procedures and are therefore more appropriate than performing a custom interpolation from a limited number of monitoring stations.

The goal of Part 4 is to replicate and improve the previous exposure and environmental-health pipeline using municipality-based area exposure indicators instead of single-station proxies.

Part 4 completes the main analytical coding pipeline of the project. A possible future Part 5 may focus on final synthesis, comparison between the station-based and ModAria-based pipelines, and preparation of final presentation/report materials.

The main output folder is:

```text
Dati/output/4-Modaria exposure/
```

The main code folder is:

```text
src/modaria_exposure/
```

---

## 4.1 ModAria data validation and area exposure construction

The first ModAria step validates the newly downloaded municipal pollutant files and constructs daily area-level exposure indicators for the agricultural and industrial study areas.

The input ModAria files are organized locally as:

```text
Dati/raw/ModariaDataset/Agricultural/
Dati/raw/ModariaDataset/Industrial/
```

Each selected municipality is expected to have one file for NO2 and one file for PM2.5.

The complete expected dataset is:

```text
37 selected municipalities × 2 pollutants = 74 files
```

The study areas are the same as those used in the health analysis.

Industrial area:

```text
Borgosatollo
Botticino
Brescia
Castenedolo
Collebeato
Flero
Gussago
Mazzano
Montirone
Nave
Nuvolento
Nuvolera
Rezzato
Roncadelle
San Zeno Naviglio
Villa Carcina
```

Agricultural area:

```text
Acquanegra Cremonese
Alfianello
Annicco
Azzanello
Barbariga
Bassano Bresciano
Bordolano
Cappella Cantone
Casalbuttano ed Uniti
Castelvisconti
Corte de' Cortesi con Cignone
Corzano
Dello
Genivolta
Longhena
Orzinuovi
Pontevico
Pralboino
Quinzano d'Oglio
San Paolo
Soresina
```

The retained years for the ModAria-health integration framework are:

```text
2016, 2017, 2018, 2019, 2023
```

The analysis included:

- automatic reading of all files in the ModAria agricultural and industrial folders;
- recognition of municipality and pollutant from the filename;
- construction of a complete file inventory;
- check that all expected municipality-pollutant files were present;
- removal of metadata rows;
- conversion of date fields into proper datetime format;
- conversion of pollutant concentration values into numeric format;
- check of missing values, duplicated dates and available years;
- filtering to the common years 2016, 2017, 2018, 2019 and 2023;
- construction of a complete long-format dataset;
- construction of wide-format datasets with municipalities as columns;
- loading and harmonization of ISTAT municipal population files;
- matching municipal population denominators to ModAria municipalities;
- construction of daily arithmetic area means;
- construction of daily population-weighted area exposure indicators;
- export of quality-control tables and reusable CSV datasets.

The file inventory confirmed that all expected files were found:

```text
Total files found = 74
Industrial municipalities = 16
Agricultural municipalities = 21
Pollutants = NO2, PM2.5
All expected municipality-pollutant files were found
```

This means that all selected municipalities have both NO2 and PM2.5 ModAria files.

The most important output of Part 4.1 is the construction of area-level exposure indicators.

Two exposure indicators were computed.

The first indicator is the arithmetic area mean:

```text
Arithmetic area mean =
mean of all available municipal pollutant values in the area
```

This indicator treats each municipality equally. It is useful as a general territorial indicator because it describes the average environmental condition across the selected municipalities.

The second indicator is the population-weighted area exposure:

```text
Population-weighted area exposure =
sum(municipal pollutant value × municipal population) / total area population
```

This indicator gives greater weight to municipalities where more people live. It is more coherent with the health-event framework because health outcomes are normalized using population denominators and represent events occurring in populations of different sizes.

For future environmental-health integration, the recommended exposure indicators are:

```text
Main indicator:
Population-weighted area exposure

Sensitivity indicator:
Arithmetic area mean
```

**Main interpretation:**

Part 4.1 does not yet perform statistical testing between agricultural and industrial areas. It is a validation and dataset-construction step.

The main result is that the ModAria municipal pollutant dataset is complete, coherent and usable for the next phase of the project.

All 74 expected files were found and successfully processed. The data were cleaned, dates were converted, pollutant values were converted into numeric format, and the analysis was restricted to the common years 2016, 2017, 2018, 2019 and 2023. The year 2023 was correctly retained, which is essential because it is part of the health-environment integration period.

This represents a major methodological improvement compared with the previous station-based exposure approach. The exposure side of the project is now spatially more coherent with the health side because both are based on the same selected municipalities.

**Output folder:**

```text
Dati/output/4-Modaria exposure/4.1-Data validation and area aggregation
```

**Main script:**

```text
src/modaria_exposure/modaria_data_validation.py
```

---

## 4.2 ModAria area pollutant comparison

The second ModAria step performs the first environmental comparison using the area-level exposure indicators constructed in Part 4.1.

The aim of Part 4.2 is to answer a purely environmental question:

```text
Do the agricultural and industrial study areas show different NO2 and PM2.5 exposure patterns when exposure is reconstructed from all selected municipalities rather than from single monitoring stations?
```

This step does not include health data. Health integration with ModAria exposure indicators is performed in Part 4.3.

The input file is the daily area exposure summary produced in Part 4.1:

```text
Dati/output/4-Modaria exposure/4.1-Data validation and area aggregation/modaria_daily_area_exposure_summary_long.csv
```

Each row of the input dataset represents one daily exposure observation for a specific combination of:

```text
Date × Area × Pollutant
```

The analysis uses the two exposure indicators produced in Part 4.1:

```text
Population_weighted_mean
Arithmetic_mean
```

The main exposure indicator is:

```text
Population_weighted_mean
```

The secondary sensitivity indicator is:

```text
Arithmetic_mean
```

The retained years are:

```text
2016, 2017, 2018, 2019, 2023
```

The final standardized daily dataset contains:

```text
7304 rows
9 columns
```

This is coherent with the expected structure:

```text
1826 days × 2 areas × 2 pollutants = 7304 rows
```

Rows by area and pollutant were perfectly balanced:

```text
Agricultural NO2  = 1826 rows
Agricultural PM25 = 1826 rows
Industrial NO2    = 1826 rows
Industrial PM25   = 1826 rows
```

The monthly dataset contains:

```text
240 rows
```

This corresponds to:

```text
5 years × 12 months × 2 areas × 2 pollutants = 240 rows
```

The seasonal dataset contains:

```text
72 rows
```

This corresponds to:

```text
18 complete seasons × 2 areas × 2 pollutants = 72 rows
```

The statistical comparison follows the paired-sample branch of the statistical-test decision framework. The two samples are:

```text
Agricultural area
Industrial area
```

The comparison is treated as paired because the two areas are compared on the same temporal units:

```text
same dates for daily comparisons
same months for monthly comparisons
same seasons for seasonal comparisons
```

The paired difference is defined as:

```text
Agricultural exposure - Industrial exposure
```

Normality is tested on the paired differences. The decision rule is:

```text
If paired differences are compatible with normality:
    use paired t-test

If paired differences are not normally distributed:
    use Wilcoxon matched-pairs signed-rank test
```

This logic was applied separately by temporal scale, pollutant and exposure indicator.

**Main interpretation:**

The ModAria-based comparison shows a clearer and more robust environmental picture than the previous station-based analysis.

The most important result is that **NO2 is higher in the industrial area than in the agricultural area** when exposure is reconstructed from all selected municipalities. This pattern is visible in the time-series plots, boxplots and paired statistical comparison summary.

This result is coherent with the interpretation of NO2 as a combustion-related pollutant associated with traffic, heating, industrial combustion and urban activity. The industrial area includes Brescia and surrounding urbanized or industrialized municipalities, so higher NO2 exposure is consistent with the territorial and emission profile of the study area.

This result also improves the previous station-based NO2 interpretation. In the station-based analysis, Soresina and Rezzato showed broadly similar NO2 dynamics and NO2 did not clearly separate the agricultural and industrial contexts. With the ModAria municipality-based exposure indicators, the area-level NO2 contrast becomes more coherent with the expected emission framework.

For **PM2.5**, the pattern is different. The agricultural and industrial areas show strongly overlapping distributions and similar temporal behavior. PM2.5 peaks often occur in both areas at the same time, suggesting that PM2.5 is strongly influenced by regional-scale dynamics, seasonal meteorology and secondary aerosol formation.

Therefore, PM2.5 should not be interpreted as a pollutant that clearly separates the two areas in the same way as NO2. Instead, it appears to behave as a regional pollutant with contributions from both agricultural and urban-industrial processes.

The main environmental interpretation of Part 4.2 is:

```text
NO2:
clearer industrial excess after ModAria area-level reconstruction

PM2.5:
more regional and seasonally shared pattern, with weaker area separation
```

The comparison between arithmetic mean and population-weighted mean showed very strong agreement. The method-comparison scatter plots were close to a diagonal pattern for both pollutants and both areas. This indicates that population weighting adjusts the exposure indicator according to population distribution but does not distort the overall temporal behavior.

This supports the decision to use population-weighted exposure as the main indicator for future health integration, while retaining the arithmetic mean as a sensitivity indicator.

**Output folder:**

```text
Dati/output/4-Modaria exposure/4.2-Area pollutant comparison
```

**Main script:**

```text
src/modaria_exposure/modaria_area_pollutant_comparison.py
```

**Main CSV outputs:**

```text
modaria_daily_area_exposure_standardized.csv
modaria_monthly_area_exposure_dataset.csv
modaria_seasonal_area_exposure_dataset.csv
modaria_area_pollutant_paired_test_summary.csv
modaria_method_comparison_summary.csv
modaria_area_pollutant_comparison_summary.csv
```

---

## 4.3 ModAria environmental-health integration

The third ModAria step integrates the ModAria area-level exposure indicators with population-normalized health event rates.

This step repeats and improves the environmental-health integration performed in Part 3.1 and Part 3.2. The main difference is that exposure is no longer represented by one monitoring station per pollutant and area. Instead, exposure is reconstructed from municipality-level ModAria estimates for all selected municipalities in the agricultural and industrial study areas.

The aim of Part 4.3 is to answer the following environmental-health question:

```text
When pollutant exposure is reconstructed using ModAria municipality-level estimates, do the agricultural and industrial study areas show coherent associations between NO2/PM2.5 exposure and respiratory or cardiocirculatory health event rates?
```

This step is still exploratory and ecological. It does not demonstrate individual-level causality. Instead, it investigates whether area-level exposure patterns and area-level health event rates show coherent temporal associations.

The environmental inputs are the monthly and seasonal ModAria exposure datasets produced in Part 4.2:

```text
Dati/output/4-Modaria exposure/4.2-Area pollutant comparison/modaria_monthly_area_exposure_dataset.csv
Dati/output/4-Modaria exposure/4.2-Area pollutant comparison/modaria_seasonal_area_exposure_dataset.csv
```

The health inputs are the monthly and seasonal health event rate tables produced in Part 2.2:

```text
Dati/output/2-Health data/2.2-Health event aggregation/monthly_health_events_rates_by_area.csv
Dati/output/2-Health data/2.2-Health event aggregation/seasonal_health_events_rates_by_area.csv
```

The retained years are:

```text
2016, 2017, 2018, 2019, 2023
```

The analysis included:

- loading monthly and seasonal ModAria exposure datasets;
- loading monthly and seasonal health rate datasets;
- preparing exposure variables for NO2 and PM2.5;
- preparing health outcome variables for respiratory and cardiocirculatory rates;
- constructing monthly and seasonal integrated datasets;
- checking missing values after integration;
- using population-weighted exposure as the main exposure indicator;
- retaining arithmetic mean exposure as a sensitivity indicator;
- computing Spearman correlations as the main association metric;
- computing Pearson correlations as a secondary linear sensitivity check;
- computing correlations overall and separately within the industrial and agricultural areas;
- performing a season-stratified monthly Spearman sensitivity analysis;
- producing scatter plots, standardized trend plots and correlation summary plots;
- exporting integrated datasets and CSV summary tables.

The main exposure indicator was:

```text
Population_weighted_mean
```

The secondary sensitivity exposure indicator was:

```text
Arithmetic_mean
```

The main correlation method was:

```text
Spearman correlation
```

Spearman correlation was selected because the analysis is exploratory, ecological and does not assume a linear exposure-response relationship. Spearman evaluates monotonic associations using ranks.

Pearson correlation was also computed, but only as a secondary sensitivity check:

```text
Pearson correlation = linear sensitivity check
```

Pearson was not used as the main metric because it assumes linear association and is more sensitive to outliers and non-normality.

The monthly integrated dataset contains:

```text
120 rows
60 monthly observations per study area
0 missing values after integration
```

This corresponds to:

```text
5 years × 12 months × 2 areas = 120 observations
```

The seasonal integrated dataset contains:

```text
36 rows
18 seasonal observations per study area
0 missing values after integration
```

This corresponds to:

```text
18 complete seasons × 2 areas = 36 observations
```

Therefore, the integration was complete and successful.

### Main monthly Spearman results using population-weighted exposure

```text
Overall:
NO2 vs Respiratory rate: rho = 0.373, p = 2.79e-05
NO2 vs Cardiocirculatory rate: rho = 0.431, p = 8.94e-07
PM2.5 vs Respiratory rate: rho = 0.450, p = 2.52e-07
PM2.5 vs Cardiocirculatory rate: rho = 0.218, p = 0.0166

Industrial area:
NO2 vs Respiratory rate: rho = 0.307, p = 0.0170
NO2 vs Cardiocirculatory rate: rho = 0.380, p = 0.00275
PM2.5 vs Respiratory rate: rho = 0.430, p = 0.000603
PM2.5 vs Cardiocirculatory rate: rho = 0.385, p = 0.00236

Agricultural area:
NO2 vs Respiratory rate: rho = 0.465, p = 0.000184
NO2 vs Cardiocirculatory rate: rho = 0.277, p = 0.0318
PM2.5 vs Respiratory rate: rho = 0.432, p = 0.000573
PM2.5 vs Cardiocirculatory rate: rho = 0.126, p = 0.337
```

### Main seasonal Spearman results using population-weighted exposure

```text
Overall:
NO2 vs Respiratory rate: rho = 0.318, p = 0.0588
NO2 vs Cardiocirculatory rate: rho = 0.508, p = 0.00155
PM2.5 vs Respiratory rate: rho = 0.433, p = 0.00827
PM2.5 vs Cardiocirculatory rate: rho = 0.124, p = 0.470

Industrial area:
NO2 vs Respiratory rate: rho = 0.146, p = 0.565
NO2 vs Cardiocirculatory rate: rho = 0.379, p = 0.121
PM2.5 vs Respiratory rate: rho = 0.284, p = 0.254
PM2.5 vs Cardiocirculatory rate: rho = 0.445, p = 0.0644

Agricultural area:
NO2 vs Respiratory rate: rho = 0.600, p = 0.00854
NO2 vs Cardiocirculatory rate: rho = 0.137, p = 0.587
PM2.5 vs Respiratory rate: rho = 0.589, p = 0.0101
PM2.5 vs Cardiocirculatory rate: rho = 0.123, p = 0.627
```

**Main monthly interpretation:**

At monthly scale, all overall associations were positive. Respiratory outcomes remained strongly coherent with pollutant variation, especially for PM2.5. The strongest overall monthly association was:

```text
PM2.5 vs Respiratory rate:
rho = 0.450
```

NO2 also showed a relevant positive association with cardiocirculatory rates:

```text
NO2 vs Cardiocirculatory rate:
rho = 0.431
```

This is important because Part 4.2 showed that ModAria NO2 is the pollutant that best characterizes the industrial/urban exposure contrast. At the same time, Part 2.2 and Part 2.3 showed that cardiocirculatory burden is higher in the industrial area and that this pattern is not simply explained by an older event-age profile.

Within the industrial area, all monthly associations were positive and statistically significant. This suggests that both respiratory and cardiocirculatory rates vary in temporal coherence with ModAria exposure indicators.

Within the agricultural area, respiratory outcomes were again the clearest result:

```text
Agricultural NO2 vs Respiratory rate:
rho = 0.465

Agricultural PM2.5 vs Respiratory rate:
rho = 0.432
```

The agricultural cardiocirculatory pattern was weaker, especially for PM2.5, which was not statistically significant.

Therefore, the monthly ModAria integration suggests:

```text
Respiratory outcomes:
coherent positive associations in both areas.

Cardiocirculatory outcomes:
more visible in the industrial area, especially with ModAria NO2 and PM2.5.
```

**Main seasonal interpretation:**

At seasonal scale, results must be interpreted more cautiously because the sample size is smaller:

```text
Overall: N = 36
Area-specific: N = 18
```

The strongest overall seasonal result was:

```text
NO2 vs Cardiocirculatory rate:
rho = 0.508, p = 0.00155
```

This result is interesting because NO2 is the pollutant that most clearly separates the industrial and agricultural areas in the ModAria framework. However, it should be interpreted carefully because the overall association may partly reflect structural differences between areas: the industrial area tends to have both higher NO2 exposure and higher cardiocirculatory rates.

The most coherent seasonal area-specific pattern was observed in the agricultural area for respiratory outcomes:

```text
Agricultural NO2 vs Respiratory rate:
rho = 0.600, p = 0.00854

Agricultural PM2.5 vs Respiratory rate:
rho = 0.589, p = 0.0101
```

This confirms that the agricultural area should not be interpreted as a clean reference area. It is affected by regional and seasonal air pollution dynamics, and respiratory health indicators show clear temporal coherence with pollutant exposure at seasonal scale.

Cardiocirculatory seasonal associations in the agricultural area remained weak and not statistically significant.

**Pearson sensitivity interpretation:**

Pearson correlations were computed as a secondary linear sensitivity check. In general, Pearson results were similar to Spearman results, especially at monthly scale.

For example, the overall monthly Pearson correlations were:

```text
NO2 vs Respiratory rate: r = 0.400
NO2 vs Cardiocirculatory rate: r = 0.430
PM2.5 vs Respiratory rate: r = 0.482
PM2.5 vs Cardiocirculatory rate: r = 0.226
```

These values do not contradict the Spearman results. This suggests that many of the observed monotonic associations are also approximately compatible with a linear pattern.

However, Spearman remains the main metric because the project does not assume linear exposure-response relationships.

**Arithmetic exposure sensitivity interpretation:**

The arithmetic mean exposure was used as a sensitivity indicator.

The comparison between population-weighted and arithmetic exposure correlations showed very similar results. The largest absolute difference between Spearman correlations was approximately:

```text
0.061
```

Most differences were smaller.

This confirms that the main environmental-health patterns are not driven by the choice of population weighting. Population-weighted exposure remains the main indicator because it is conceptually more coherent with population-normalized health rates, while arithmetic exposure confirms the robustness of the results.

**Season-stratified monthly sensitivity interpretation:**

A season-stratified monthly Spearman analysis was performed to check whether the monthly associations were mainly driven by shared seasonality.

The analysis produced:

```text
4 seasons × 3 groups × 2 pollutants × 2 outcomes = 48 correlations
```

Only 2 out of 48 correlations were statistically significant at p < 0.05:

```text
Summer, Industrial area:
NO2 vs Respiratory rate:
rho = -0.582, p = 0.0228

Autumn, Overall:
NO2 vs Cardiocirculatory rate:
rho = 0.366, p = 0.0470
```

The fact that most within-season correlations were weak or not statistically significant suggests that the full monthly associations are strongly influenced by broad seasonal dynamics. This is coherent with the station-based monthly integration in Part 3.2.

Therefore, Part 4.3 should be interpreted as evidence of temporal ecological coherence, largely structured by seasonality, rather than as evidence of direct short-term causal exposure-response effects.

**Interpretation in relation to the industrial-versus-agricultural comparison:**

Part 4.3 is important because it connects the improved ModAria environmental contrast with the health outcome patterns.

The key interpretation is:

```text
NO2:
better characterizes the industrial/urban exposure profile in the ModAria framework.

PM2.5:
behaves more as a shared regional hazard affecting both areas.

Respiratory outcomes:
show the most consistent temporal coherence with pollutant variation.

Cardiocirculatory outcomes:
show a stronger structural burden in the industrial area and become more visible in the ModAria NO2 integration.
```

This means that the two areas do not differ in a simple way for all pollutants and all health outcomes. Instead, the results are pollutant-specific and outcome-specific.

The industrial area is more clearly characterized by higher NO2 exposure and higher cardiocirculatory burden.

The agricultural area does not behave as a clean control area. Respiratory rates show coherent associations with both NO2 and PM2.5, especially at seasonal scale, suggesting that the agricultural/rural context is still affected by regional air pollution dynamics.

Therefore, Part 4.3 supports the central project narrative:

```text
Industrial and agricultural areas show different environmental-health profiles.

NO2 is the clearest pollutant for distinguishing the industrial/urban context.

PM2.5 is a regional and health-relevant pollutant shared by both areas.

Respiratory outcomes are more temporally coherent with pollutant variation.

Cardiocirculatory outcomes are more structurally connected to the industrial area and become more evident when using ModAria NO2 exposure.
```

**Output folder:**

```text
Dati/output/4-Modaria exposure/4.3-Modaria environmental health integration
```

**Main script:**

```text
src/modaria_exposure/modaria_environment_health_integration.py
```

**Main CSV outputs:**

```text
modaria_monthly_environment_health_integrated_dataset.csv
modaria_seasonal_environment_health_integrated_dataset.csv
missing_values_check.csv

spearman_population_weighted_correlation_summary_monthly.csv
spearman_population_weighted_correlation_summary_seasonal.csv
pearson_population_weighted_correlation_summary_monthly.csv
pearson_population_weighted_correlation_summary_seasonal.csv

spearman_arithmetic_mean_sensitivity_summary_monthly.csv
spearman_arithmetic_mean_sensitivity_summary_seasonal.csv
pearson_arithmetic_mean_sensitivity_summary_monthly.csv
pearson_arithmetic_mean_sensitivity_summary_seasonal.csv

modaria_environment_health_correlation_summary_all_methods.csv
modaria_exposure_method_correlation_comparison.csv
spearman_population_weighted_season_stratified_monthly.csv
modaria_environment_health_integration_summary.csv
```

**Main graphical outputs:**

```text
Monthly scatter plots for:
NO2 vs Respiratory
NO2 vs Cardiocirculatory
PM2.5 vs Respiratory
PM2.5 vs Cardiocirculatory

Seasonal scatter plots for:
NO2 vs Respiratory
NO2 vs Cardiocirculatory
PM2.5 vs Respiratory
PM2.5 vs Cardiocirculatory

Monthly standardized trend plots
Seasonal standardized trend plots
Monthly Spearman vs Pearson correlation summary plot
Seasonal Spearman vs Pearson correlation summary plot
```

---

## 4.4 ModAria monthly and weekly lag analysis

The fourth ModAria step investigates whether the ModAria environmental-health associations observed in Part 4.3 are mainly same-period associations or whether they persist at previous temporal lags.

Part 4.3 showed positive associations between ModAria population-weighted exposure indicators and population-normalized health event rates. However, those associations were same-period correlations. Part 4.4 adds a temporal lag dimension.

The aim of Part 4.4 is to answer the following questions:

```text
Are monthly health event rates more strongly associated with pollutant exposure in the same month or in previous months?

If the strongest monthly association is observed at lag 0 months, does this same-month signal contain shorter delays at weekly scale?

Are lag patterns different between respiratory and cardiocirculatory outcomes?

Are lag patterns different between the industrial and agricultural areas?

Does the ModAria-based lag analysis confirm or modify the previous station-based lag interpretation?
```

This analysis remains exploratory and ecological. It does not demonstrate causal delayed effects.

### Meaning of lag analysis in this project

Lag analysis does not mean selecting isolated pollution peaks and then checking what happens in the following periods.

Instead, lagged exposure variables are created by shifting the complete pollutant time series relative to the health event time series.

For each health period, the health outcome always refers to the current period, while pollutant exposure is taken from the same period or from previous periods.

For the monthly lag analysis:

```text
Lag 0 = pollutant concentration in the same month as the health event rate
Lag 1 = pollutant concentration one month before the health event rate
Lag 2 = pollutant concentration two months before the health event rate
Lag 3 = pollutant concentration three months before the health event rate
```

For example, the respiratory rate in March 2017 is compared with:

```text
Lag 0: pollutant mean in March 2017
Lag 1: pollutant mean in February 2017
Lag 2: pollutant mean in January 2017
Lag 3: pollutant mean in December 2016
```

For the weekly lag analysis:

```text
Lag 0 = pollutant concentration in the same week as the health event rate
Lag 1 = pollutant concentration one week before the health event rate
Lag 2 = pollutant concentration two weeks before the health event rate
Lag 3 = pollutant concentration three weeks before the health event rate
Lag 4 = pollutant concentration four weeks before the health event rate
```

This means that all available periods contribute to the analysis. The lag analysis is not a peak-based analysis.

### Methodological choices

The exposure variables used in Part 4.4 were:

```text
NO2_population_weighted_mean
PM25_population_weighted_mean
```

Only the population-weighted exposure indicator was used, because Part 4.3 had already shown that arithmetic and population-weighted exposure produced very similar correlation patterns.

The main association metric was:

```text
Spearman correlation
```

Spearman correlation was used because the analysis is exploratory, ecological and does not assume a linear exposure-response relationship.

Pearson correlation was not included in Part 4.4. Pearson had already been used as a sensitivity check in Part 4.3, but adding it to the lag analysis would have doubled the number of outputs and made interpretation less clear.

### Temporal safeguard

A key methodological safeguard was applied in both the monthly and weekly lag analyses.

Lagged pollutant values were retained only when the lagged period was exactly the expected distance from the current health period.

This was necessary because the project excludes 2020, 2021 and 2022. Without this control, the script could incorrectly connect December 2019 to January 2023 as if they were consecutive periods.

For example:

```text
Current month = January 2023
Previous available month = December 2019
```

This is not a valid lag 1 month. Therefore, the lagged value is set to missing.

The same logic was applied at weekly scale. A lag 1 week value was retained only if the lagged week was exactly 7 days before the current week.

### Monthly lag analysis

The monthly analysis used the monthly ModAria environmental-health integrated dataset produced in Part 4.3:

```text
Dati/output/4-Modaria exposure/4.3-Modaria environmental health integration/modaria_monthly_environment_health_integrated_dataset.csv
```

Each row represents:

```text
MonthPeriod × Area
```

The monthly input dataset contained:

```text
120 rows
60 monthly observations for the industrial area
60 monthly observations for the agricultural area
0 missing values in the input dataset
```

This corresponds to:

```text
5 years × 12 months × 2 areas = 120 observations
```

After lag construction, the monthly lagged dataset still contained:

```text
120 rows
```

The expected number of available values by lag was:

```text
Overall:
Lag 0 = 120
Lag 1 = 116
Lag 2 = 112
Lag 3 = 108

By area:
Lag 0 = 60
Lag 1 = 58
Lag 2 = 56
Lag 3 = 54
```

This confirms that lagged values were handled correctly and that the 2019–2023 gap was not incorrectly bridged.

### Main monthly lag results

The main overall monthly Spearman results were:

```text
Overall NO2 vs Respiratory rate:
Lag 0 = 0.373
Lag 1 = 0.333
Lag 2 = 0.175
Lag 3 = 0.024

Overall NO2 vs Cardiocirculatory rate:
Lag 0 = 0.431
Lag 1 = 0.333
Lag 2 = 0.208
Lag 3 = 0.136

Overall PM2.5 vs Respiratory rate:
Lag 0 = 0.450
Lag 1 = 0.413
Lag 2 = 0.300
Lag 3 = 0.056

Overall PM2.5 vs Cardiocirculatory rate:
Lag 0 = 0.218
Lag 1 = 0.120
Lag 2 = 0.065
Lag 3 = -0.008
```

The monthly best-lag summary showed:

```text
Number of pollutant-outcome-group combinations = 12
Combinations where lag 0 is strongest positive rho = 12
Percentage = 100%
```

Therefore, at monthly scale, lag 0 dominated all pollutant-outcome-group combinations.

This means that the ModAria monthly lag analysis did not identify a clear delayed association at lag 1, lag 2 or lag 3 months.

The main monthly interpretation is:

```text
At monthly scale, ModAria pollutant-health associations are mainly same-month and seasonally structured.
The associations are strongest at lag 0 months and generally weaken at longer monthly lags.
No clear 1–3 month delayed pattern emerges.
```

### Area-specific monthly lag interpretation

In the industrial area, all four pollutant-outcome combinations showed their highest monthly correlation at lag 0.

The strongest industrial monthly associations were:

```text
Industrial PM2.5 vs Respiratory:
Lag 0 = 0.430

Industrial PM2.5 vs Cardiocirculatory:
Lag 0 = 0.385

Industrial NO2 vs Cardiocirculatory:
Lag 0 = 0.380
```

This suggests positive same-month ModAria-health associations in the industrial area, but without evidence of stronger delayed monthly associations.

In the agricultural area, respiratory outcomes again showed the clearest monthly pattern:

```text
Agricultural NO2 vs Respiratory:
Lag 0 = 0.465

Agricultural PM2.5 vs Respiratory:
Lag 0 = 0.432
Lag 1 = 0.424
```

The PM2.5-respiratory association remained very similar between lag 0 and lag 1, suggesting some persistence, but lag 0 remained the maximum.

Cardiocirculatory associations in the agricultural area were much weaker, especially for PM2.5.

### Weekly lag analysis

The weekly lag analysis was introduced because monthly lag 0 dominated all combinations. A lag 0 monthly association does not necessarily mean that there is no delay. It may contain shorter delays occurring within the same month.

The weekly analysis used ModAria daily area-level exposure data and selected health events.

The environmental input was:

```text
Dati/output/4-Modaria exposure/4.2-Area pollutant comparison/modaria_daily_area_exposure_standardized.csv
```

The health event input was:

```text
Dati/output/2-Health data/2.2-Health event aggregation/health_events_selected_areas_outcomes.csv
```

The annual population denominator input was:

```text
Dati/output/2-Health data/2.2-Health event aggregation/annual_health_events_rates_by_area.csv
```

Weekly aggregation was performed using Monday-to-Sunday weeks, consistently with the previous station-based weekly lag analysis in Part 3.4.

Each row of the weekly integrated dataset represents:

```text
WeekStart × Area
```

The weekly integrated dataset contained:

```text
522 rows
261 weekly observations for the industrial area
261 weekly observations for the agricultural area
0 missing values in the integrated weekly dataset
```

The expected number of available values by weekly lag was:

```text
Overall:
Lag 0 = 522
Lag 1 = 518
Lag 2 = 514
Lag 3 = 510
Lag 4 = 506

By area:
Lag 0 = 261
Lag 1 = 259
Lag 2 = 257
Lag 3 = 255
Lag 4 = 253
```

This confirms that weekly lags were validated correctly and that the 2019–2023 gap was not incorrectly bridged.

### Main weekly lag results

The main overall weekly Spearman results were:

```text
Overall NO2 vs Respiratory rate:
Lag 0 = 0.249
Lag 1 = 0.268
Lag 2 = 0.259
Lag 3 = 0.239
Lag 4 = 0.230

Overall NO2 vs Cardiocirculatory rate:
Lag 0 = 0.288
Lag 1 = 0.296
Lag 2 = 0.296
Lag 3 = 0.258
Lag 4 = 0.253

Overall PM2.5 vs Respiratory rate:
Lag 0 = 0.297
Lag 1 = 0.331
Lag 2 = 0.277
Lag 3 = 0.250
Lag 4 = 0.266

Overall PM2.5 vs Cardiocirculatory rate:
Lag 0 = 0.179
Lag 1 = 0.185
Lag 2 = 0.135
Lag 3 = 0.117
Lag 4 = 0.128
```

The best overall weekly lags were:

```text
NO2 vs Respiratory:
best lag = 1 week
rho = 0.268

NO2 vs Cardiocirculatory:
best lag = 2 weeks
rho = 0.296

PM2.5 vs Respiratory:
best lag = 1 week
rho = 0.331

PM2.5 vs Cardiocirculatory:
best lag = 1 week
rho = 0.185
```

The weekly best-lag summary showed:

```text
Number of pollutant-outcome-group combinations = 12
Combinations where lag 0 is strongest positive rho = 1
Percentage = 8.33%
```

This result is very different from the monthly analysis. At weekly scale, lag 0 was rarely the strongest association. Most best lags occurred at lag 1 or lag 2 weeks.

The main weekly interpretation is:

```text
The monthly lag 0 signal appears to contain shorter temporal delays that become visible only at weekly scale.
Many same-month associations are compatible with short delays of approximately 1–2 weeks.
```

### Area-specific weekly lag interpretation

The industrial area showed the clearest weekly lag structure.

The best industrial weekly lags were:

```text
Industrial NO2 vs Respiratory:
best lag = 2 weeks
rho = 0.249

Industrial NO2 vs Cardiocirculatory:
best lag = 2 weeks
rho = 0.336

Industrial PM2.5 vs Respiratory:
best lag = 1 week
rho = 0.364

Industrial PM2.5 vs Cardiocirculatory:
best lag = 2 weeks
rho = 0.354
```

This suggests that, in the industrial area, ModAria weekly associations tend to peak around lag 1–2 weeks, especially for PM2.5 respiratory and for cardiocirculatory outcomes.

The agricultural area also showed positive respiratory associations, especially at lag 1 week:

```text
Agricultural NO2 vs Respiratory:
best lag = 1 week
rho = 0.304

Agricultural PM2.5 vs Respiratory:
best lag = 1 week
rho = 0.295
```

However, the agricultural respiratory pattern was less sharply defined because lag 0 and lag 1 values were very similar.

Agricultural cardiocirculatory associations remained weak:

```text
Agricultural NO2 vs Cardiocirculatory:
best lag = 1 week
rho = 0.136

Agricultural PM2.5 vs Cardiocirculatory:
best lag = 0 weeks
rho = 0.118
```

This confirms that cardiocirculatory outcomes are more informative in the industrial area than in the agricultural area.

### Monthly versus weekly synthesis

The key result of Part 4.4 is the contrast between monthly and weekly lag patterns.

At monthly scale:

```text
Lag 0 months was the strongest positive association in 12 out of 12 combinations.
```

At weekly scale:

```text
Lag 0 weeks was the strongest positive association in only 1 out of 12 combinations.
```

Therefore, the same-month signal should not be interpreted as evidence that exposure and health outcomes occur with no delay. Rather, the monthly time resolution is too coarse to detect shorter delays.

The combined interpretation is:

```text
Monthly analysis:
associations are mainly same-month and do not show clear 1–3 month delays.

Weekly analysis:
same-month associations may contain short delays, mostly around 1–2 weeks.
```

This result is coherent with the previous station-based lag analyses. The ModAria framework confirms the same general temporal pattern, but with a more spatially representative exposure assessment.

### Interpretation in relation to the industrial-versus-agricultural comparison

Part 4.4 adds an important temporal component to the industrial-versus-agricultural comparison.

The industrial area shows the clearest weekly short-lag structure. Several industrial associations reach their maximum at lag 1 or lag 2 weeks, including:

```text
Industrial PM2.5 vs Respiratory:
best lag = 1 week

Industrial NO2 vs Cardiocirculatory:
best lag = 2 weeks

Industrial PM2.5 vs Cardiocirculatory:
best lag = 2 weeks
```

This suggests that the industrial area is the context where short-lag temporal coherence between ModAria exposure and health outcomes is most visible.

The agricultural area also shows positive respiratory associations, especially at lag 1 week, but the pattern is less sharply defined. Cardiocirculatory outcomes remain weak in the agricultural area.

Therefore, the industrial-versus-agricultural interpretation after Part 4.4 is:

```text
Industrial area:
clearer short-lag structure, especially at lag 1–2 weeks.

Agricultural area:
positive respiratory associations, but weaker or less sharply lagged structure.

Respiratory outcomes:
most coherent temporal endpoint in both areas.

Cardiocirculatory outcomes:
more visible in the industrial area, weak in the agricultural area.
```

### Final interpretation of Part 4.4

Part 4.4 completes the ModAria-based environmental-health temporal analysis.

The final interpretation is:

```text
At monthly scale:
ModAria pollutant-health associations are mainly same-month and seasonally structured.

At weekly scale:
the same-month signal may contain short delays, mostly around 1–2 weeks.

Respiratory outcomes:
remain the most temporally coherent health endpoint.

Cardiocirculatory outcomes:
remain more area-dependent and are more visible in the industrial area.

Industrial area:
shows the clearest weekly short-lag structure.

Agricultural area:
shows coherent respiratory associations but weaker cardiocirculatory patterns.
```

Overall, Part 4.4 strengthens the main project narrative. The ModAria framework confirms that the environmental-health patterns are not random, but temporally coherent. At the same time, the results remain exploratory and ecological. They should be interpreted as evidence of temporal consistency between area-level pollutant exposure and area-level health event rates, not as proof of causal delayed effects.

With Part 4.4 completed, the main analytical coding pipeline of the project is essentially complete.

**Output folder:**

```text
Dati/output/4-Modaria exposure/4.4-Modaria monthly and weekly lag analysis
```

**Main script:**

```text
src/modaria_exposure/modaria_monthly_weekly_lag_analysis.py
```

**Main monthly CSV outputs:**

```text
modaria_monthly_dataset_prepared_for_lag_analysis.csv
modaria_monthly_lag_integrated_dataset.csv
modaria_monthly_lag_availability_check.csv
modaria_monthly_lag_spearman_summary.csv
modaria_monthly_lag_best_lag_summary.csv
modaria_monthly_lag0_dominance_check.csv
modaria_monthly_lag_analysis_summary.csv
```

**Main weekly CSV outputs:**

```text
modaria_weekly_environment_health_integrated_dataset.csv
modaria_weekly_lag_integrated_dataset.csv
modaria_weekly_lag_availability_check.csv
modaria_weekly_lag_spearman_summary.csv
modaria_weekly_lag_best_lag_summary.csv
modaria_weekly_lag0_dominance_check.csv
modaria_weekly_lag_analysis_summary.csv
```

**Combined CSV output:**

```text
modaria_monthly_weekly_lag_spearman_summary.csv
```

**Main graphical outputs:**

```text
modaria_monthly_lag_summary_overall.png
modaria_monthly_best_positive_lag_summary.png
modaria_weekly_lag_summary_overall.png
modaria_weekly_best_positive_lag_summary.png
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
│   ├── ModariaDataset/
│   │   ├── Agricultural/
│   │   │   ├── AcquanegraCremonese_NO2.csv
│   │   │   ├── AcquanegraCremonese_PM25.csv
│   │   │   └── ...
│   │   └── Industrial/
│   │       ├── Borgosatollo_NO2.csv
│   │       ├── Borgosatollo_PM25.csv
│   │       └── ...
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
    ├── 3-Environmental health integration/
    │   ├── 3.1-Seasonal integration/
    │   ├── 3.2-Monthly integration/
    │   ├── 3.3-Monthly lag analysis/
    │   └── 3.4-Weekly lag analysis/
    │
    └── 4-Modaria exposure/
        ├── 4.1-Data validation and area aggregation/
        ├── 4.2-Area pollutant comparison/
        ├── 4.3-Modaria environmental health integration/
        └── 4.4-Modaria monthly and weekly lag analysis/

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
├── integration/
│   ├── __init__.py
│   ├── environment_health_integration.py
│   ├── monthly_environment_health_integration.py
│   ├── monthly_lag_analysis.py
│   └── weekly_lag_analysis.py
│
└── modaria_exposure/
    ├── __init__.py
    ├── modaria_data_validation.py
    ├── modaria_area_pollutant_comparison.py
    ├── modaria_environment_health_integration.py
    └── modaria_monthly_weekly_lag_analysis.py
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

### Run the ModAria data validation and area exposure construction

Use this in `main.py`:

```python
from src.modaria_exposure.modaria_data_validation import run_modaria_data_validation


if __name__ == "__main__":
    run_modaria_data_validation()
```

### Run the ModAria area pollutant comparison

Use this in `main.py`:

```python
from src.modaria_exposure.modaria_area_pollutant_comparison import run_modaria_area_pollutant_comparison


if __name__ == "__main__":
    run_modaria_area_pollutant_comparison()
```

### Run the ModAria environmental-health integration

Use this in `main.py`:

```python
from src.modaria_exposure.modaria_environment_health_integration import main as run_modaria_environment_health_integration


if __name__ == "__main__":
    run_modaria_environment_health_integration()
```

### Run the ModAria monthly and weekly lag analysis

Use this in `main.py`:

```python
from src.modaria_exposure.modaria_monthly_weekly_lag_analysis import main as run_modaria_lag_analysis


if __name__ == "__main__":
    run_modaria_lag_analysis()
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
git commit -m "Add ModAria data validation and area exposure construction"
git commit -m "Add ModAria area pollutant comparison"
git commit -m "Add ModAria environmental health integration"
git commit -m "Add ModAria monthly and weekly lag analysis"
git commit -m "Update README after seasonal integration"
git commit -m "Update README after monthly integration"
git commit -m "Update README after monthly lag analysis"
git commit -m "Update README after weekly lag analysis"
git commit -m "Update README after ModAria data validation"
git commit -m "Update README after ModAria area pollutant comparison"
git commit -m "Update README after ModAria environmental health integration"
git commit -m "Update README after ModAria monthly and weekly lag analysis"
git commit -m "Fix README formatting"
```

Recommended commit for the current project status:

```bash
git add -A
git commit -m "Add ModAria monthly and weekly lag analysis"
git push
```

---

## Notes and limitations

The current analyses are exploratory and descriptive. Statistical significance is interpreted together with the magnitude of the observed differences and with the methodological limitations of using monitoring stations or municipality-level estimates as proxies for broader territorial exposure.

Due to pollutant-specific monitoring availability, the industrial/urban proxy station differs between the NO2 and PM2.5 station-based analyses. Therefore, Part 1 and Part 3 station-based results should be interpreted pollutant by pollutant and not as a perfectly matched multi-pollutant comparison on the same station pair.

The statistical tests on pollutant data do not explicitly model temporal autocorrelation or meteorological confounding. Future analyses may include meteorological variables, health outcome data and additional pollutants such as NH3, if available.

The raw health event dataset is not uploaded to GitHub because it may contain sensitive health-related information. Only aggregated outputs and analysis scripts are versioned.

The health dataset does not contain a patient identifier. Therefore, records should be interpreted as health events, not unique individuals. The same person may appear more than once.

Raw health event counts cannot be directly interpreted as health risk because they are strongly affected by population size. For this reason, Part 2.2 computes population-normalized rates per 10,000 inhabitants.

Part 2.3 introduces age-specific rates using age-specific municipal population denominators. This improves the interpretation of the health outcome comparison, but it is still not a full age-standardized epidemiological analysis based on a common reference population.

The age-specific analysis suggests that the higher cardiocirculatory burden in the industrial area is not simply explained by age structure alone, especially because the excess is visible in the `<65` group. However, this result remains ecological and descriptive.

Part 3.1 integrates station-based pollutant indicators and health event rates at seasonal scale and uses Spearman correlation. These correlations are exploratory and ecological. They should not be interpreted as individual-level causal evidence.

The seasonal environmental-health integration uses same-season pollutant indicators and same-season health rates. Possible delayed effects are not assessed in Part 3.1 and are explored in later lag analyses.

Part 3.2 extends the station-based environmental-health integration to monthly scale and increases the number of observations from 36 seasonal rows to 120 monthly rows. This improves temporal detail and prepares the dataset for lag analysis.

The monthly integration shows positive associations between pollutant indicators and health event rates, especially for respiratory outcomes. However, the season-stratified sensitivity analysis suggests that most of the significant monthly correlations are largely driven by the shared annual seasonal cycle of air pollution and health events.

Therefore, Part 3.2 should be interpreted as evidence of coherent temporal ecological patterns, not as evidence of independent within-season or individual-level exposure-response effects.

Part 3.3 explores monthly lagged associations using lag 0, lag 1, lag 2 and lag 3 months. Lagged pollutant values are validated so that they are retained only when the lagged month is exactly the expected number of months before the current health month. This prevents incorrect temporal links across the 2019–2023 gap.

The monthly lag analysis shows that most pollutant-health associations are strongest at lag 0 and progressively weaken at longer monthly lags. Therefore, the observed monthly associations appear mainly synchronous and seasonally structured rather than clearly delayed at the monthly scale.

Part 3.4 refines the lag analysis at weekly scale using lag 0, lag 1, lag 2, lag 3 and lag 4 weeks. Lagged pollutant values are validated so that they are retained only when the lagged week is exactly the expected number of weeks before the current health week. This prevents incorrect temporal links across the 2019–2023 gap.

The weekly lag analysis suggests that some same-month associations observed in Part 3.3 may include shorter delayed patterns of approximately 1–2 weeks, especially for respiratory outcomes in the industrial area. However, these associations remain exploratory and ecological.

Weekly health event rates can be noisier than monthly or seasonal rates because weekly event counts are smaller. For this reason, the weekly lag analysis should be interpreted together with the broader seasonal and monthly results rather than as a standalone causal model.

Part 4 introduces ModAria municipal pollutant estimates. This improves the environmental exposure side of the project because exposure indicators are now reconstructed from all selected municipalities rather than from one monitoring station per pollutant and area.

The ModAria-based exposure indicators are still ecological exposure estimates. They do not represent individual exposure and they do not account for within-municipality variability.

The population-weighted ModAria exposure indicator should be considered the main exposure indicator for health integration, because it weights municipal pollutant values by the number of inhabitants. The arithmetic area mean should be retained as a secondary sensitivity indicator where needed.

The ModAria values are treated as official ARPA-derived municipal estimates. However, the internal modelling or interpolation uncertainty of the ModAria system is not quantified within this project.

Part 4.2 shows that NO2 is higher in the industrial area when exposure is reconstructed from all selected municipalities. This is coherent with the interpretation of NO2 as a combustion-related pollutant related to traffic, heating, industrial activity and urban emissions.

Part 4.2 also shows that PM2.5 has a more regional and seasonally shared pattern, with stronger overlap between agricultural and industrial areas. Therefore, PM2.5 should not be interpreted as a simple industrial-versus-agricultural discriminator.

Part 4.3 integrates ModAria exposure indicators with population-normalized health rates at monthly and seasonal scale. This improves the spatial coherence of the environmental-health analysis because both exposure and health outcomes are now based on the same selected municipality sets.

Part 4.3 uses Spearman correlation as the main association metric because the analysis is exploratory and does not assume linear exposure-response relationships. Pearson correlation is included only as a secondary linear sensitivity check.

Part 4.3 shows positive monthly associations between ModAria exposure and health event rates. Respiratory outcomes remain coherent with pollutant variation in both areas, while cardiocirculatory outcomes become more visible in the industrial area, especially with NO2.

Part 4.3 also shows that seasonal agricultural respiratory rates have strong positive associations with both NO2 and PM2.5. This supports the interpretation that the agricultural area is not a clean reference area, but is affected by regional and seasonal air pollution dynamics.

The overall seasonal NO2-cardiocirculatory association is strong, but it must be interpreted carefully because it may partly reflect structural differences between the two areas: the industrial area tends to have both higher NO2 exposure and higher cardiocirculatory rates.

The season-stratified monthly sensitivity analysis in Part 4.3 shows that most within-season correlations are weak or not statistically significant. This suggests that monthly associations are strongly influenced by broad seasonal dynamics shared by pollutant concentrations and health event rates.

The arithmetic exposure sensitivity in Part 4.3 shows that population-weighted and arithmetic exposure indicators produce very similar correlation patterns. Therefore, the results are not strongly driven by the population-weighting method.

Part 4.4 uses only population-weighted ModAria exposure because Part 4.3 showed that arithmetic and population-weighted exposure produced very similar correlation patterns.

Part 4.4 shows that ModAria monthly lag associations are strongest at lag 0 months in all pollutant-outcome-area combinations. Therefore, no clear 1–3 month delayed pattern emerges from the monthly ModAria lag analysis.

Part 4.4 also shows that, at weekly scale, most strongest associations occur at lag 1 or lag 2 weeks. This suggests that the same-month signal observed at monthly scale may contain shorter delayed associations within the same month.

Part 4.4 should not be interpreted as evidence of causal delayed effects. Lagged correlations may still be influenced by seasonality, temporal autocorrelation, meteorology and unmeasured confounding.

The strongest weekly short-lag structure is observed in the industrial area, especially for PM2.5 versus respiratory rates and for NO2/PM2.5 versus cardiocirculatory rates. However, adjacent weekly lags often have similar correlation values, so the result should be interpreted as a short-lag window rather than as a precise biological delay.

Daily statistical tests can become statistically significant even when differences are small, because the number of paired daily observations is large. For this reason, interpretation should consider effect magnitude, temporal consistency and graphical evidence, not p-values alone.

Important unmeasured confounders include age beyond the applied stratification, sex, socioeconomic status, smoking, occupational exposure, comorbidities, healthcare access, event coding practices, meteorology, respiratory infections, influenza circulation and individual exposure history.

The geographical meaning of the municipality variable should also be interpreted carefully. If the municipality refers to event location rather than patient residence, area-level health rates may not perfectly represent the resident population.

Any future comparison between pollutant concentrations and health events should be interpreted as an exploratory ecological analysis, not as evidence of individual-level causality.

---

## Current project status and possible next steps

Part 1 of the project, focused on statistical tests of station-based environmental pollutant data, is completed.

Part 2 has produced:

- a general health data exploration;
- population-normalized respiratory and cardiocirculatory rates;
- age-specific health event rates for the selected study areas.

Part 3 has produced:

- a seasonal station-based environmental-health integration;
- a monthly station-based environmental-health integration;
- a monthly lag analysis;
- a weekly lag analysis.

Part 4 has produced:

- a complete ModAria file inventory;
- validation of all 74 expected municipality-pollutant files;
- cleaned long-format ModAria dataset;
- wide-format municipality-level datasets;
- municipal population matching;
- daily arithmetic area exposure indicators;
- daily population-weighted area exposure indicators;
- daily, monthly and seasonal ModAria area exposure datasets;
- statistical comparison of ModAria area-level NO2 and PM2.5 exposure between agricultural and industrial areas;
- method comparison between arithmetic and population-weighted exposure indicators;
- monthly ModAria environmental-health integrated dataset;
- seasonal ModAria environmental-health integrated dataset;
- Spearman correlation summaries for population-weighted ModAria exposure;
- Pearson correlation summaries as linear sensitivity checks;
- arithmetic exposure sensitivity correlation summaries;
- season-stratified monthly sensitivity analysis;
- ModAria environmental-health scatter plots and standardized trend plots;
- ModAria monthly lag analysis;
- ModAria weekly lag analysis;
- monthly and weekly lag summary plots;
- monthly and weekly best-lag summary tables.

The main result of Part 3.1 is that respiratory acute event rates show the clearest seasonal association with station-based pollutant indicators. Both NO2 and PM2.5 show moderate positive associations with respiratory event rates, especially in the agricultural area. Cardiocirculatory event rates do not show clear same-season seasonal associations with the pollutant indicators.

Part 3.2 confirms the relevance of respiratory outcomes at monthly scale. Both NO2 and PM2.5 show moderate positive and statistically significant associations with respiratory acute event rates overall and within both study areas. Cardiocirculatory associations are weaker, but they are more visible in the industrial area, especially for PM2.5.

However, the season-stratified sensitivity analysis in Part 3.2 shows that most within-season correlations are weak or not statistically significant. This suggests that the overall monthly associations are largely influenced by the shared seasonal structure of pollutant concentrations and acute health event rates.

Part 3.3 shows that lagged pollutant indicators at 1–3 months do not generally improve the strength of the associations compared with same-month pollutant indicators. Most associations are strongest at lag 0 and progressively weaken with increasing monthly lag. This suggests that the observed monthly environmental-health associations are mainly synchronous and seasonally structured rather than clearly delayed at the monthly scale.

Part 3.4 refines this conclusion. At weekly scale, some associations, especially respiratory associations in the industrial area, are strongest at lag 1 or lag 2 weeks. This suggests that the same-month associations observed in Part 3.3 may partly contain shorter delayed patterns within the month. The most coherent weekly lag signal concerns respiratory acute event rates, while cardiocirculatory outcomes remain weaker and more area-dependent.

Part 4.1 addresses the main limitation of the first station-based pipeline. Instead of representing each area with one station per pollutant, the ModAria dataset provides pollutant estimates for all 37 municipalities included in the study areas. This makes the exposure side of the project more spatially coherent with the health side.

Part 4.2 confirms that the ModAria exposure framework is usable and informative. NO2 is higher in the industrial area when reconstructed from all selected municipalities, which is coherent with its combustion-related interpretation. PM2.5 shows stronger overlap between agricultural and industrial areas and appears more regionally and seasonally structured.

Part 4.3 extends the ModAria framework to health integration. The monthly integrated dataset contains 120 rows and the seasonal integrated dataset contains 36 rows, with no missing values after integration. Spearman correlations show positive associations between ModAria exposure and health event rates.

At monthly scale, respiratory outcomes remain coherent with pollutant variation in both study areas. PM2.5 versus respiratory rate is one of the strongest overall monthly associations. NO2 versus cardiocirculatory rate also becomes more visible in the ModAria framework, especially because NO2 now better represents the industrial/urban exposure profile.

At seasonal scale, the agricultural area shows strong positive associations between both pollutants and respiratory rates. This confirms that the agricultural area is not a clean reference area and that respiratory burden in this context may follow regional and seasonal air pollution dynamics.

Cardiocirculatory outcomes remain more complex. The industrial area has a higher structural cardiocirculatory burden, and ModAria NO2 integration makes the NO2-cardiocirculatory pattern more visible. However, these results remain ecological and may reflect both exposure differences and other structural area-level factors.

Part 4.4 completes the ModAria temporal analysis. The monthly lag analysis shows that all pollutant-outcome-area combinations have their strongest positive association at lag 0 months. Therefore, no clear delayed pattern emerges at 1–3 months.

The weekly lag analysis refines this conclusion. At weekly scale, lag 0 is the strongest association in only 1 out of 12 combinations, while most strongest associations occur at lag 1 or lag 2 weeks. This suggests that the same-month signal observed in monthly analysis may contain shorter delayed associations within the same month.

The main interpretation after Part 4.4 is:

```text
NO2:
best pollutant for distinguishing the industrial/urban exposure profile in the ModAria framework.

PM2.5:
regional and shared health-relevant pollutant, less able to separate agricultural and industrial areas.

Respiratory outcomes:
most consistent temporal association with pollutant variation.

Cardiocirculatory outcomes:
more structurally elevated in the industrial area and more visible in the ModAria NO2 framework.

Monthly lag:
no clear 1–3 month delayed pattern; strongest associations occur at lag 0 months.

Weekly lag:
the monthly lag 0 signal may contain short delays of approximately 1–2 weeks.

Industrial area:
clearest weekly short-lag structure.

Agricultural area:
coherent respiratory associations but weaker cardiocirculatory lag patterns.
```

At the current stage, the project provides two complementary environmental frameworks:

```text
Station-based framework:
useful for the first complete environmental-health pipeline.

ModAria municipality-based framework:
more spatially coherent with the selected study areas and better suited for final environmental-health integration.
```

The strongest and most defensible message from the project is that industrial and agricultural areas differ in their environmental-health profiles, but the difference is pollutant-specific, outcome-specific and scale-dependent.

The ModAria framework improves the environmental interpretation. NO2 becomes more clearly associated with the industrial/urban context, while PM2.5 appears more regional and shared. Respiratory outcomes show the most consistent temporal coherence with pollutant variation, while cardiocirculatory outcomes remain relevant because they are structurally higher in the industrial area and become more visible when ModAria NO2 exposure is used.

The analytical coding phase of the project is now essentially complete.

A possible future Part 5 may be dedicated to final synthesis rather than to a new analytical pipeline. It could include:

- a concise comparison between the station-based pipeline and the ModAria-based pipeline;
- summary tables comparing Part 3 and Part 4 results;
- summary plots comparing station-based and ModAria-based correlations;
- final interpretation of which conclusions are robust to the change in exposure assessment;
- preparation of final presentation figures and report text.

The likely final synthesis should emphasize that:

```text
The station-based pipeline was useful to develop and validate the complete environmental-health workflow.

The ModAria pipeline improves spatial coherence because exposure is reconstructed from all selected municipalities.

NO2 becomes a clearer industrial/urban marker in the ModAria framework.

PM2.5 remains a more regional and shared pollutant.

Respiratory outcomes are the most temporally coherent health endpoint.

Cardiocirculatory outcomes are more area-dependent and more visible in the industrial area.

Monthly lag analyses do not show clear 1–3 month delays.

Weekly lag analyses suggest possible short delays of approximately 1–2 weeks, especially in the industrial area.
```

Possible future non-code or external extensions include:

- comparing station-based results with ModAria-based results in a final synthesis section;
- preparing final presentation-ready tables and plots;
- adding QGIS-based spatial visualizations or heatmaps;
- exploring spatial modelling or map-based analysis if needed by the group;
- adding meteorological variables such as temperature, humidity, precipitation, wind speed or atmospheric stability;
- exploring emission inventory data or additional pollutants such as NH3;
- testing more formal statistical models with adjustment for seasonality and temporal autocorrelation;
- considering moving-average exposure indicators rather than simple single-lag indicators;
- exploring cumulative weekly exposure indicators;
- exploring age-specific environmental-health integration as a secondary sensitivity analysis;
- focusing more specifically on respiratory outcomes, which currently show the clearest environmental-health temporal pattern;
- considering more advanced distributed lag approaches only if additional data and modelling time are available.

Any future extension should remain clearly framed as ecological unless individual-level exposure and health data become available.