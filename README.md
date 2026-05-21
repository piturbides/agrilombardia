# Human Health and Environment Data Science Laboratory

Exploratory ecological analysis of air pollution and acute health event data in Lombardy, focused on the comparison between **agricultural/rural** and **industrial/urban** territorial contexts.

The project investigates whether areas with different emission-source profiles show different environmental patterns and whether these patterns are reflected in population-normalized respiratory and cardiocirculatory health indicators.

The full analytical workflow includes:

1. station-based pollutant analysis;
2. health event exploration, aggregation and rate construction;
3. station-based environmental-health integration and lag analysis;
4. ModAria municipality-based exposure reconstruction, integration and lag analysis;
5. final synthesis comparing station-based and ModAria-based results.

The project is designed as a reproducible academic data science pipeline. Each script is organized around clear inputs, processing steps, outputs and interpretation-ready CSV/plot products.

---

## Project framework

The central comparison is between two selected study areas in Lombardy:

- **Industrial/urban area**: 16 municipalities located in the Brescia area;
- **Agricultural/rural area**: 21 municipalities located mainly in the Cremona area, with some municipalities from the Brescia province.

The project focuses on two pollutants:

- **NO2**, interpreted mainly as a combustion-related pollutant associated with traffic, heating, urbanization and industrial activity;
- **PM2.5**, interpreted as a health-relevant fine particulate pollutant influenced by both primary emissions and secondary atmospheric formation.

The selected health outcomes are:

- **Respiratory acute events**;
- **Cardiocirculatory acute events**.

Health outcomes are aggregated at area level and normalized by population:

```text
Rate per 10,000 inhabitants = (Number of events / Population) × 10,000
```

The project is explicitly exploratory and ecological. It can identify coherent area-level and temporal patterns, but it cannot demonstrate individual-level causal effects.

---

## Retained years

The definitive station-based environmental analyses exclude the COVID-related years 2020, 2021 and 2022.

```text
Station-based environmental analyses:
2016, 2017, 2018, 2019, 2023, 2024, 2025
```

The health dataset contains:

```text
2015, 2016, 2017, 2018, 2019, 2023
```

The common years used for environmental-health integration are:

```text
2016, 2017, 2018, 2019, 2023
```

The years 2020, 2021 and 2022 are not used because they are absent from the health dataset and may be affected by COVID-related changes in mobility, emissions, healthcare access and event reporting.

---

## Study areas

### Industrial area

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

### Agricultural area

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

The agricultural area is not equivalent to the province of Cremona. Some agricultural-area municipalities belong to the province of Brescia. All analyses therefore preserve the QGIS/shapefile-based area assignment instead of relying only on province boundaries.

---

## Exposure frameworks

The project uses two complementary environmental exposure frameworks.

### 1. Station-based framework

The first exposure framework uses monitoring stations as proxies for the two study areas.

```text
NO2:
Soresina → Agricultural
Rezzato  → Industrial

PM2.5:
Soresina                 → Agricultural
Brescia Villaggio Sereno → Industrial
```

This framework was useful to build and validate the complete environmental-health pipeline, but it has an important spatial limitation: one monitoring station cannot fully represent all municipalities in a study area.

### 2. ModAria municipality-based framework

The second exposure framework uses ARPA Lombardia ModAria municipal pollutant estimates for all selected municipalities.

This improves spatial coherence because both exposure indicators and health outcomes are based on the same selected municipality sets.

Two ModAria exposure indicators are computed:

```text
Arithmetic area mean =
mean of municipal pollutant values in the area
```

```text
Population-weighted area exposure =
sum(municipal pollutant value × municipal population) / total area population
```

The **population-weighted exposure** is used as the main indicator for health integration because it is conceptually aligned with population-normalized health event rates.

The **arithmetic mean** is retained as a sensitivity and descriptive territorial indicator.

---

## Repository structure

```text
.
├── README.md
├── requirements.txt
├── main.py
├── .gitignore
│
├── Dati/
│   ├── raw/
│   │   ├── Soresina_NO2_2016_2025.csv
│   │   ├── Rezzato_NO2_2016_2025.csv
│   │   ├── Soresina_2016_2025_PM25.csv
│   │   ├── Brescia_VillagioSereno_PM25_2016_2025.csv
│   │   ├── Health_events_2015_2023.csv              # local only, ignored by Git
│   │   ├── ModariaDataset/
│   │   │   ├── Agricultural/
│   │   │   └── Industrial/
│   │   └── population/
│   │       ├── Brescia_2016.csv
│   │       ├── Brescia_2017.csv
│   │       ├── Brescia_2018.csv
│   │       ├── Brescia_2019.csv
│   │       ├── Brescia_2023.csv
│   │       ├── Cremona_2016.csv
│   │       ├── Cremona_2017.csv
│   │       ├── Cremona_2018.csv
│   │       ├── Cremona_2019.csv
│   │       └── Cremona_2023.csv
│   │
│   └── output/
│       ├── 1-Statistical tests/
│       │   ├── 1.1-Preliminary/
│       │   ├── 1.2-Monthly seasonal/
│       │   ├── 1.3-NO2_definitivo/
│       │   └── 1.4-PM25_definitivo/
│       │
│       ├── 2-Health data/
│       │   ├── 2.1-Health data exploration/
│       │   ├── 2.2-Health event aggregation/
│       │   └── 2.3-Health age structure check/
│       │
│       ├── 3-Environmental health integration/
│       │   ├── 3.1-Seasonal integration/
│       │   ├── 3.2-Monthly integration/
│       │   ├── 3.3-Monthly lag analysis/
│       │   └── 3.4-Weekly lag analysis/
│       │
│       ├── 4-Modaria exposure/
│       │   ├── 4.1-Data validation and area aggregation/
│       │   ├── 4.2-Area pollutant comparison/
│       │   ├── 4.3-Modaria environmental health integration/
│       │   └── 4.4-Modaria monthly and weekly lag analysis/
│       │
│       └── 5-Final synthesis/
│           └── 5.1-Final project synthesis/
│
└── src/
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
    ├── modaria_exposure/
    │   ├── __init__.py
    │   ├── modaria_data_validation.py
    │   ├── modaria_area_pollutant_comparison.py
    │   ├── modaria_environment_health_integration.py
    │   └── modaria_monthly_weekly_lag_analysis.py
    │
    └── final_synthesis/
        ├── __init__.py
        └── final_project_synthesis.py
```

---

## Installation

Create and activate a virtual environment.

```bash
python -m venv .venv
```

On Windows PowerShell:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Reproducibility notes

The project is designed to be reproducible through `main.py`.

Each analysis script reads input files from `Dati/raw/` or from previous outputs in `Dati/output/`, then saves CSV tables and figures in a dedicated output folder.

Before running a script, make sure the expected input files are available in the correct folders.

The raw health event file is not uploaded to GitHub because it may contain sensitive health-related information. It is expected locally at:

```text
Dati/raw/Health_events_2015_2023.csv
```

The file is intentionally excluded from Git versioning through `.gitignore`.

Only scripts, documentation and non-sensitive aggregated outputs should be versioned.

---

## How to run

Run the analysis selected in `main.py`:

```bash
python main.py
```

To reproduce a specific part, update `main.py` with the desired function import and call.

---

## Main script examples

### Part 1.3 — Definitive non-COVID NO2 analysis

```python
from src.statistical_tests.no2_definitivo_non_covid import run_no2_definitivo_non_covid_analysis


if __name__ == "__main__":
    run_no2_definitivo_non_covid_analysis()
```

### Part 1.4 — Definitive non-COVID PM2.5 analysis

```python
from src.statistical_tests.pm25_definitivo_non_covid import run_pm25_definitivo_non_covid_analysis


if __name__ == "__main__":
    run_pm25_definitivo_non_covid_analysis()
```

### Part 2.1 — Health data exploration

```python
from src.health_analysis.health_data_exploration import run_health_data_exploration


if __name__ == "__main__":
    run_health_data_exploration()
```

### Part 2.2 — Health event aggregation

```python
from src.health_analysis.health_event_aggregation import run_health_event_aggregation


if __name__ == "__main__":
    run_health_event_aggregation()
```

### Part 2.3 — Health age-structure check

```python
from src.health_analysis.health_age_structure_check import run_health_age_structure_check


if __name__ == "__main__":
    run_health_age_structure_check()
```

### Part 3.1 — Seasonal environmental-health integration

```python
from src.integration.environment_health_integration import run_environment_health_integration


if __name__ == "__main__":
    run_environment_health_integration()
```

### Part 3.2 — Monthly environmental-health integration

```python
from src.integration.monthly_environment_health_integration import run_monthly_environment_health_integration


if __name__ == "__main__":
    run_monthly_environment_health_integration()
```

### Part 3.3 — Monthly lag analysis

```python
from src.integration.monthly_lag_analysis import run_monthly_lag_analysis


if __name__ == "__main__":
    run_monthly_lag_analysis()
```

### Part 3.4 — Weekly lag analysis

```python
from src.integration.weekly_lag_analysis import run_weekly_lag_analysis


if __name__ == "__main__":
    run_weekly_lag_analysis()
```

### Part 4.1 — ModAria data validation and exposure construction

```python
from src.modaria_exposure.modaria_data_validation import run_modaria_data_validation


if __name__ == "__main__":
    run_modaria_data_validation()
```

### Part 4.2 — ModAria area pollutant comparison

```python
from src.modaria_exposure.modaria_area_pollutant_comparison import run_modaria_area_pollutant_comparison


if __name__ == "__main__":
    run_modaria_area_pollutant_comparison()
```

### Part 4.3 — ModAria environmental-health integration

```python
from src.modaria_exposure.modaria_environment_health_integration import main as run_modaria_environment_health_integration


if __name__ == "__main__":
    run_modaria_environment_health_integration()
```

### Part 4.4 — ModAria monthly and weekly lag analysis

```python
from src.modaria_exposure.modaria_monthly_weekly_lag_analysis import main as run_modaria_lag_analysis


if __name__ == "__main__":
    run_modaria_lag_analysis()
```

### Part 5.1 — Final project synthesis

```python
from src.final_synthesis.final_project_synthesis import main as run_final_project_synthesis


if __name__ == "__main__":
    run_final_project_synthesis()
```

---

# Analytical workflow

---

## Part 1 — Station-based pollutant analysis

Output folder:

```text
Dati/output/1-Statistical tests/
```

Code folder:

```text
src/statistical_tests/
```

Part 1 compares pollutant concentrations measured at selected ARPA Lombardia monitoring stations.

The analyses include:

- data loading and cleaning;
- conversion of invalid values coded as `-999` into missing values;
- temporal aggregation at daily, monthly and seasonal scales;
- descriptive statistics;
- graphical exploration;
- normality testing;
- non-parametric statistical comparisons;
- CSV and plot export.

### Part 1.1 — Preliminary NO2 daily analysis

Script:

```text
src/statistical_tests/preliminary_no2.py
```

Output folder:

```text
Dati/output/1-Statistical tests/1.1-Preliminary/
```

Aim:

```text
Compare daily mean NO2 concentrations between Soresina and Rezzato.
```

Main operations:

- load hourly NO2 data;
- clean invalid values;
- aggregate to daily means;
- compare Soresina and Rezzato using descriptive statistics and Mann-Whitney U test.

Main interpretation:

```text
The two daily NO2 distributions are statistically different but strongly overlapping.
Soresina is slightly higher on average, but the practical difference is modest.
```

### Part 1.2 — Monthly and seasonal NO2 analysis

Script:

```text
src/statistical_tests/monthly_seasonal_no2.py
```

Output folder:

```text
Dati/output/1-Statistical tests/1.2-Monthly seasonal/
```

Aim:

```text
Evaluate whether the NO2 difference between Soresina and Rezzato is stable across months and seasons.
```

Main operations:

- monthly aggregation;
- seasonal aggregation;
- removal of incomplete seasons;
- paired monthly and seasonal comparisons;
- monthly and seasonal climatology.

Main interpretation:

```text
NO2 shows a strong seasonal cycle, with higher concentrations in colder periods.
Soresina is slightly higher than Rezzato in many months, especially in winter and autumn, but the difference remains modest.
```

### Part 1.3 — Definitive non-COVID NO2 analysis

Script:

```text
src/statistical_tests/no2_definitivo_non_covid.py
```

Output folder:

```text
Dati/output/1-Statistical tests/1.3-NO2_definitivo/
```

Aim:

```text
Repeat the NO2 comparison after excluding 2020, 2021 and 2022.
```

Retained years:

```text
2016, 2017, 2018, 2019, 2023, 2024, 2025
```

Main operations:

- daily, monthly and seasonal NO2 aggregation;
- COVID-year exclusion;
- graphical outputs with correct temporal gaps;
- Shapiro-Wilk normality tests;
- Mann-Whitney U tests;
- paired Wilcoxon signed-rank tests;
- CSV summary tables.

Main interpretation:

```text
Soresina and Rezzato show broadly similar NO2 dynamics dominated by seasonality.
Soresina tends to be slightly higher, but the magnitude is modest.
NO2 does not clearly separate agricultural and industrial contexts when using one monitoring station per area.
```

### Part 1.4 — Definitive non-COVID PM2.5 analysis

Script:

```text
src/statistical_tests/pm25_definitivo_non_covid.py
```

Output folder:

```text
Dati/output/1-Statistical tests/1.4-PM25_definitivo/
```

Aim:

```text
Compare PM2.5 concentrations between Soresina and Brescia Villaggio Sereno after excluding 2020, 2021 and 2022.
```

Retained years:

```text
2016, 2017, 2018, 2019, 2023, 2024, 2025
```

Main operations:

- daily, monthly and seasonal PM2.5 aggregation;
- COVID-year exclusion;
- normality tests;
- paired and unpaired statistical comparisons;
- month-specific and season-specific paired comparisons;
- CSV and plot export.

Main interpretation:

```text
Soresina generally shows higher PM2.5 concentrations than Brescia Villaggio Sereno.
The difference is especially visible outside winter.
This suggests that PM2.5 is not only an industrial/urban pollutant and may reflect regional secondary aerosol formation and agricultural precursor contributions.
```

This interpretation remains exploratory because NH3, meteorology and PM chemical speciation are not included.

---

## Part 2 — Health data exploration and aggregation

Output folder:

```text
Dati/output/2-Health data/
```

Code folder:

```text
src/health_analysis/
```

Part 2 prepares the health outcome side of the project.

The raw health dataset contains event-level records with information on:

- date;
- municipality;
- province;
- event code;
- event type;
- event detail;
- age.

The selected outcomes are:

```text
TYPE = MEDICO ACUTO and TYPE_DTL = RESPIRATORIA
TYPE = MEDICO ACUTO and TYPE_DTL = CARDIOCIRCOLATORIA
```

### Part 2.1 — Health data exploration

Script:

```text
src/health_analysis/health_data_exploration.py
```

Output folder:

```text
Dati/output/2-Health data/2.1-Health data exploration/
```

Aim:

```text
Inspect the structure, quality and coverage of the health event dataset.
```

Main operations:

- load health event data;
- parse non-standard date format;
- clean age values;
- inspect missing values;
- explore event categories;
- extract respiratory and cardiocirculatory acute events;
- produce preliminary temporal and geographical summaries.

Main interpretation:

```text
The dataset is suitable for exploratory aggregated analysis.
Respiratory and cardiocirculatory acute events are sufficiently represented.
Raw event counts cannot be interpreted directly as risk because they are strongly affected by population size.
```

### Part 2.2 — Health event aggregation and population-normalized rates

Script:

```text
src/health_analysis/health_event_aggregation.py
```

Output folder:

```text
Dati/output/2-Health data/2.2-Health event aggregation/
```

Aim:

```text
Compute population-normalized respiratory and cardiocirculatory event rates for the agricultural and industrial study areas.
```

Main operations:

- load ISTAT population files;
- match all selected municipalities to population denominators;
- assign each health event to Agricultural or Industrial area;
- aggregate events annually, monthly and seasonally;
- compute rates per 10,000 inhabitants;
- export health rate tables.

Main population check:

```text
Expected municipality-year combinations = 185
Found municipality-year combinations    = 185
```

Main interpretation:

```text
Population normalization is essential because the industrial area has a much larger population than the agricultural area.

Respiratory rates are broadly comparable between areas.
Cardiocirculatory rates are consistently higher in the industrial area.
```

### Part 2.3 — Health age-structure check and age-specific rates

Script:

```text
src/health_analysis/health_age_structure_check.py
```

Output folder:

```text
Dati/output/2-Health data/2.3-Health age structure check/
```

Aim:

```text
Check whether differences in health event rates may be influenced by age structure.
```

Age groups:

```text
Binary:
<65
65+

Detailed:
0-44
45-64
65-74
75-84
85+
```

Main operations:

- classify selected events by age group;
- load age-specific municipal population denominators;
- compute age-specific annual rates;
- compare age-specific rates between areas.

Main interpretation:

```text
Acute events are concentrated among older subjects, especially respiratory events.

The agricultural area has an older event-age profile than the industrial area.

The industrial area still shows higher cardiocirculatory rates in the <65 group, suggesting that its higher cardiocirculatory burden is not simply explained by an older population structure.
```

Key result:

```text
Mean <65 cardiocirculatory rate:
Industrial area   = 103.5 events per 10,000 inhabitants
Agricultural area = 77.6 events per 10,000 inhabitants

Industrial/Agricultural ratio ≈ 1.33
```

---

## Part 3 — Station-based environmental-health integration

Output folder:

```text
Dati/output/3-Environmental health integration/
```

Code folder:

```text
src/integration/
```

Part 3 integrates station-based pollutant indicators with population-normalized health event rates.

The aim is to evaluate whether pollutant concentrations and acute health event rates show coherent temporal patterns.

The analysis uses Spearman correlation as the main association metric because the data are aggregated, exploratory and not assumed to be normally distributed or linearly related.

### Part 3.1 — Seasonal environmental-health integration

Script:

```text
src/integration/environment_health_integration.py
```

Output folder:

```text
Dati/output/3-Environmental health integration/3.1-Seasonal integration/
```

Integrated dataset:

```text
36 rows
18 seasonal observations per study area
0 missing values after integration
```

Each row represents:

```text
SeasonYear × Season × Area
```

Main overall Spearman results:

```text
NO2 vs Respiratory rate:          rho = 0.502, p = 0.0018
NO2 vs Cardiocirculatory rate:    rho = 0.204, p = 0.2330
PM2.5 vs Respiratory rate:        rho = 0.446, p = 0.0064
PM2.5 vs Cardiocirculatory rate:  rho = 0.164, p = 0.3393
```

Main interpretation:

```text
Respiratory acute event rates show the clearest seasonal association with pollutant indicators.

Cardiocirculatory rates do not show clear same-season associations with station-based pollutant indicators.
```

### Part 3.2 — Monthly environmental-health integration

Script:

```text
src/integration/monthly_environment_health_integration.py
```

Output folder:

```text
Dati/output/3-Environmental health integration/3.2-Monthly integration/
```

Integrated dataset:

```text
120 rows
60 monthly observations per study area
0 missing values after integration
```

Each row represents:

```text
MonthPeriod × Area
```

Main overall Spearman results:

```text
NO2 vs Respiratory rate:          rho = 0.485, p = 2.01e-08
NO2 vs Cardiocirculatory rate:    rho = 0.281, p = 0.0019
PM2.5 vs Respiratory rate:        rho = 0.458, p = 1.47e-07
PM2.5 vs Cardiocirculatory rate:  rho = 0.259, p = 0.0043
```

Main interpretation:

```text
Monthly pollutant indicators show positive associations with health event rates.
Respiratory outcomes are the most consistent endpoint.
Cardiocirculatory associations are weaker and more visible in the industrial area.
```

A season-stratified sensitivity analysis showed that most within-season correlations were weak or not significant. This suggests that the full monthly associations are strongly influenced by shared seasonality.

### Part 3.3 — Monthly lag analysis

Script:

```text
src/integration/monthly_lag_analysis.py
```

Output folder:

```text
Dati/output/3-Environmental health integration/3.3-Monthly lag analysis/
```

Tested lags:

```text
Lag 0 = same month
Lag 1 = previous month
Lag 2 = two months before
Lag 3 = three months before
```

Temporal safeguard:

```text
Lagged values are retained only when the lagged month is exactly the expected number of months before the current health month.
This prevents invalid links across the 2019-2023 gap.
```

Main interpretation:

```text
Most monthly associations are strongest at lag 0 and weaken at longer monthly lags.
No clear 1-3 month delayed pattern emerges.
Monthly associations are mainly same-month and seasonally structured.
```

### Part 3.4 — Weekly lag analysis

Script:

```text
src/integration/weekly_lag_analysis.py
```

Output folder:

```text
Dati/output/3-Environmental health integration/3.4-Weekly lag analysis/
```

Integrated dataset:

```text
522 rows
261 weekly observations per study area
```

Tested lags:

```text
Lag 0 = same week
Lag 1 = one week before
Lag 2 = two weeks before
Lag 3 = three weeks before
Lag 4 = four weeks before
```

Main interpretation:

```text
At weekly scale, several associations peak around lag 1 or lag 2 weeks.
This suggests that same-month associations may contain shorter delayed patterns within the same month.

The clearest weekly signal concerns respiratory outcomes, especially in the industrial area.
```

---

## Part 4 — ModAria municipality-based exposure analysis

Output folder:

```text
Dati/output/4-Modaria exposure/
```

Code folder:

```text
src/modaria_exposure/
```

Part 4 replaces the station-based exposure proxies with municipality-level ModAria exposure estimates.

This improves spatial coherence because exposure indicators are reconstructed from all selected municipalities, while health outcomes are aggregated over the same municipality sets.

### Part 4.1 — ModAria data validation and area exposure construction

Script:

```text
src/modaria_exposure/modaria_data_validation.py
```

Output folder:

```text
Dati/output/4-Modaria exposure/4.1-Data validation and area aggregation/
```

Expected input structure:

```text
37 selected municipalities × 2 pollutants = 74 files
```

Input folders:

```text
Dati/raw/ModariaDataset/Agricultural/
Dati/raw/ModariaDataset/Industrial/
```

Main operations:

- scan ModAria folders;
- build file inventory;
- check expected municipality-pollutant combinations;
- clean files;
- convert dates and pollutant values;
- filter to 2016, 2017, 2018, 2019 and 2023;
- build long-format municipality-level dataset;
- build wide-format municipality-level datasets;
- load municipal population denominators;
- compute daily arithmetic area means;
- compute daily population-weighted area exposure indicators.

Main validation result:

```text
Total files found = 74
Industrial municipalities = 16
Agricultural municipalities = 21
All expected municipality-pollutant files were found
```

Main interpretation:

```text
The ModAria dataset is complete and suitable for area-level exposure reconstruction.
This step provides a stronger exposure basis than the previous single-station proxy approach.
```

### Part 4.2 — ModAria area pollutant comparison

Script:

```text
src/modaria_exposure/modaria_area_pollutant_comparison.py
```

Output folder:

```text
Dati/output/4-Modaria exposure/4.2-Area pollutant comparison/
```

Input:

```text
Dati/output/4-Modaria exposure/4.1-Data validation and area aggregation/modaria_daily_area_exposure_summary_long.csv
```

Main datasets:

```text
Daily dataset:
7304 rows = 1826 days × 2 areas × 2 pollutants

Monthly dataset:
240 rows = 5 years × 12 months × 2 areas × 2 pollutants

Seasonal dataset:
72 rows = 18 complete seasons × 2 areas × 2 pollutants
```

Main statistical approach:

```text
Paired comparison between Agricultural and Industrial areas on the same temporal units.
If paired differences are normally distributed: paired t-test.
If paired differences are not normally distributed: Wilcoxon signed-rank test.
```

Main interpretation:

```text
NO2 is higher in the industrial area when exposure is reconstructed from all selected municipalities.
This is coherent with NO2 as a combustion-related pollutant linked to urban and industrial activity.

PM2.5 shows stronger overlap between areas and behaves more as a regional, seasonally shared pollutant.
```

This result improves the previous station-based interpretation. In the station-based framework, NO2 did not clearly separate the two contexts. In the ModAria framework, NO2 becomes a clearer industrial/urban marker.

Main CSV outputs:

```text
modaria_daily_area_exposure_standardized.csv
modaria_monthly_area_exposure_dataset.csv
modaria_seasonal_area_exposure_dataset.csv
modaria_area_pollutant_paired_test_summary.csv
modaria_method_comparison_summary.csv
modaria_area_pollutant_comparison_summary.csv
```

### Part 4.3 — ModAria environmental-health integration

Script:

```text
src/modaria_exposure/modaria_environment_health_integration.py
```

Output folder:

```text
Dati/output/4-Modaria exposure/4.3-Modaria environmental health integration/
```

Aim:

```text
Integrate ModAria area-level exposure indicators with population-normalized health event rates.
```

Inputs:

```text
Dati/output/4-Modaria exposure/4.2-Area pollutant comparison/modaria_monthly_area_exposure_dataset.csv
Dati/output/4-Modaria exposure/4.2-Area pollutant comparison/modaria_seasonal_area_exposure_dataset.csv

Dati/output/2-Health data/2.2-Health event aggregation/monthly_health_events_rates_by_area.csv
Dati/output/2-Health data/2.2-Health event aggregation/seasonal_health_events_rates_by_area.csv
```

Integrated datasets:

```text
Monthly:
120 rows
60 monthly observations per study area
0 missing values after integration

Seasonal:
36 rows
18 seasonal observations per study area
0 missing values after integration
```

Main monthly Spearman results using population-weighted exposure:

```text
Overall:
NO2 vs Respiratory rate:          rho = 0.373, p = 2.79e-05
NO2 vs Cardiocirculatory rate:    rho = 0.431, p = 8.94e-07
PM2.5 vs Respiratory rate:        rho = 0.450, p = 2.52e-07
PM2.5 vs Cardiocirculatory rate:  rho = 0.218, p = 0.0166

Industrial:
NO2 vs Respiratory rate:          rho = 0.307, p = 0.0170
NO2 vs Cardiocirculatory rate:    rho = 0.380, p = 0.00275
PM2.5 vs Respiratory rate:        rho = 0.430, p = 0.000603
PM2.5 vs Cardiocirculatory rate:  rho = 0.385, p = 0.00236

Agricultural:
NO2 vs Respiratory rate:          rho = 0.465, p = 0.000184
NO2 vs Cardiocirculatory rate:    rho = 0.277, p = 0.0318
PM2.5 vs Respiratory rate:        rho = 0.432, p = 0.000573
PM2.5 vs Cardiocirculatory rate:  rho = 0.126, p = 0.337
```

Main seasonal Spearman results using population-weighted exposure:

```text
Overall:
NO2 vs Respiratory rate:          rho = 0.318, p = 0.0588
NO2 vs Cardiocirculatory rate:    rho = 0.508, p = 0.00155
PM2.5 vs Respiratory rate:        rho = 0.433, p = 0.00827
PM2.5 vs Cardiocirculatory rate:  rho = 0.124, p = 0.470

Agricultural:
NO2 vs Respiratory rate:          rho = 0.600, p = 0.00854
PM2.5 vs Respiratory rate:        rho = 0.589, p = 0.0101
```

Main interpretation:

```text
Respiratory outcomes remain the most consistent endpoint.
They show positive associations with pollutant variation in both study areas.

Cardiocirculatory outcomes become more visible in the industrial area, especially with ModAria NO2 and PM2.5.

The agricultural area is not a clean reference area: respiratory rates show coherent associations with both NO2 and PM2.5, especially at seasonal scale.
```

Pearson correlation was computed as a secondary linear sensitivity check. The results generally supported the Spearman interpretation.

The arithmetic exposure sensitivity showed that population-weighted and arithmetic exposure produced very similar correlation patterns. Therefore, the main conclusions are not driven by the population-weighting method.

Main CSV outputs:

```text
modaria_monthly_environment_health_integrated_dataset.csv
modaria_seasonal_environment_health_integrated_dataset.csv
spearman_population_weighted_correlation_summary_monthly.csv
spearman_population_weighted_correlation_summary_seasonal.csv
pearson_population_weighted_correlation_summary_monthly.csv
pearson_population_weighted_correlation_summary_seasonal.csv
spearman_arithmetic_mean_sensitivity_summary_monthly.csv
spearman_arithmetic_mean_sensitivity_summary_seasonal.csv
modaria_environment_health_correlation_summary_all_methods.csv
modaria_exposure_method_correlation_comparison.csv
spearman_population_weighted_season_stratified_monthly.csv
modaria_environment_health_integration_summary.csv
```

### Part 4.4 — ModAria monthly and weekly lag analysis

Script:

```text
src/modaria_exposure/modaria_monthly_weekly_lag_analysis.py
```

Output folder:

```text
Dati/output/4-Modaria exposure/4.4-Modaria monthly and weekly lag analysis/
```

Aim:

```text
Evaluate whether ModAria exposure-health associations are mainly same-period associations or whether they persist at previous temporal lags.
```

Lag analysis meaning:

```text
The health outcome always refers to the current period.
The pollutant exposure refers to the same period or to a previous period.
The analysis is based on shifted time series, not on isolated pollution peaks.
```

Monthly lags:

```text
Lag 0 = same month
Lag 1 = previous month
Lag 2 = two months before
Lag 3 = three months before
```

Weekly lags:

```text
Lag 0 = same week
Lag 1 = one week before
Lag 2 = two weeks before
Lag 3 = three weeks before
Lag 4 = four weeks before
```

The same temporal safeguard used in Part 3 is applied:

```text
Lagged values are retained only if the lagged period is exactly the expected distance from the current health period.
This avoids invalid links across the 2019-2023 gap.
```

Monthly lag input:

```text
Dati/output/4-Modaria exposure/4.3-Modaria environmental health integration/modaria_monthly_environment_health_integrated_dataset.csv
```

Monthly dataset:

```text
120 rows
60 monthly observations per study area
0 missing values
```

Monthly lag availability:

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

Main monthly result:

```text
Lag 0 months is the strongest positive association in 12 out of 12 pollutant-outcome-group combinations.
```

Main monthly interpretation:

```text
No clear 1-3 month delayed pattern emerges.
At monthly scale, ModAria pollutant-health associations are mainly same-month and seasonally structured.
```

Weekly input files:

```text
Dati/output/4-Modaria exposure/4.2-Area pollutant comparison/modaria_daily_area_exposure_standardized.csv
Dati/output/2-Health data/2.2-Health event aggregation/health_events_selected_areas_outcomes.csv
Dati/output/2-Health data/2.2-Health event aggregation/annual_health_events_rates_by_area.csv
```

Weekly dataset:

```text
522 rows
261 weekly observations per study area
0 missing values after integration
```

Weekly lag availability:

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

Main overall weekly best lags:

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

Main weekly result:

```text
Lag 0 weeks is the strongest positive association in only 1 out of 12 pollutant-outcome-group combinations.
Most best lags occur at lag 1 or lag 2 weeks.
```

Main interpretation:

```text
The same-month signal observed in monthly analysis may contain shorter delayed associations within the month.
Weekly analysis suggests a short-lag window of approximately 1-2 weeks, especially in the industrial area.
```

Industrial weekly best lags:

```text
NO2 vs Respiratory:
best lag = 2 weeks
rho = 0.249

NO2 vs Cardiocirculatory:
best lag = 2 weeks
rho = 0.336

PM2.5 vs Respiratory:
best lag = 1 week
rho = 0.364

PM2.5 vs Cardiocirculatory:
best lag = 2 weeks
rho = 0.354
```

Agricultural weekly best lags:

```text
NO2 vs Respiratory:
best lag = 1 week
rho = 0.304

PM2.5 vs Respiratory:
best lag = 1 week
rho = 0.295

NO2 vs Cardiocirculatory:
best lag = 1 week
rho = 0.136

PM2.5 vs Cardiocirculatory:
best lag = 0 weeks
rho = 0.118
```

Main interpretation by area:

```text
Industrial area:
clearest short-lag structure, especially around lag 1-2 weeks.

Agricultural area:
coherent respiratory associations, but weaker and less sharply lagged.

Respiratory outcomes:
most consistent temporal endpoint.

Cardiocirculatory outcomes:
more visible in the industrial area and weak in the agricultural area.
```

Main CSV outputs:

```text
modaria_monthly_dataset_prepared_for_lag_analysis.csv
modaria_monthly_lag_integrated_dataset.csv
modaria_monthly_lag_availability_check.csv
modaria_monthly_lag_spearman_summary.csv
modaria_monthly_lag_best_lag_summary.csv
modaria_monthly_lag0_dominance_check.csv
modaria_monthly_lag_analysis_summary.csv

modaria_weekly_environment_health_integrated_dataset.csv
modaria_weekly_lag_integrated_dataset.csv
modaria_weekly_lag_availability_check.csv
modaria_weekly_lag_spearman_summary.csv
modaria_weekly_lag_best_lag_summary.csv
modaria_weekly_lag0_dominance_check.csv
modaria_weekly_lag_analysis_summary.csv

modaria_monthly_weekly_lag_spearman_summary.csv
```

Main plots:

```text
modaria_monthly_lag_summary_overall.png
modaria_monthly_best_positive_lag_summary.png
modaria_weekly_lag_summary_overall.png
modaria_weekly_best_positive_lag_summary.png
```

---

## Part 5 — Final project synthesis

Output folder:

```text
Dati/output/5-Final synthesis/5.1-Final project synthesis/
```

Code folder:

```text
src/final_synthesis/
```

Script:

```text
src/final_synthesis/final_project_synthesis.py
```

Aim:

```text
Summarize and compare the station-based pipeline and the ModAria-based pipeline.
```

Part 5 is not a new exposure or health analysis. It is a final synthesis step designed to make the project easier to interpret, present and reproduce.

The analysis compares:

```text
Station-based pipeline:
Part 3 seasonal/monthly integration and lag analysis

ModAria-based pipeline:
Part 4.3 integration and Part 4.4 lag analysis
```

Main goals:

- standardize correlation outputs from both pipelines;
- compare station-based and ModAria-based correlations;
- compare station-based and ModAria-based lag patterns;
- identify which conclusions are robust to the change in exposure assessment;
- produce compact summary tables;
- produce final presentation-ready plots;
- build a qualitative evidence strength table;
- summarize the whole analytical workflow.

Main standardized correlation table:

```text
48 rows
```

Structure:

```text
Temporal_scale
Pipeline
Group
Pollutant
Outcome
Rho
P_value
N
Interpretation
```

Main correlation comparison table:

```text
24 rows
```

Main standardized best-lag table:

```text
48 rows
```

Main full lag table:

```text
216 rows
```

Main lag comparison table:

```text
24 rows
```

### Final correlation synthesis

The final synthesis showed that all station-based and ModAria correlations had the same positive direction.

Summary:

```text
Station-based, Seasonal:
Positive correlations = 12/12
Significant correlations = 4/12
Mean absolute rho = 0.349

Station-based, Monthly:
Positive correlations = 12/12
Significant correlations = 11/12
Mean absolute rho = 0.386

ModAria, Seasonal:
Positive correlations = 12/12
Significant correlations = 4/12
Mean absolute rho = 0.340

ModAria, Monthly:
Positive correlations = 12/12
Significant correlations = 11/12
Mean absolute rho = 0.356
```

Interpretation:

```text
The direction of the environmental-health associations is robust to the change from station-based exposure to ModAria area-level exposure.

Monthly associations are more robust than seasonal associations in both pipelines, mainly because the monthly datasets contain more observations.
```

### Final lag synthesis

Summary:

```text
Station-based monthly lag:
Lag 0 best = 11/12
Median best lag = 0 months

ModAria monthly lag:
Lag 0 best = 12/12
Median best lag = 0 months

Station-based weekly lag:
Lag 0 best = 1/12
Median best lag = 1 week

ModAria weekly lag:
Lag 0 best = 1/12
Median best lag = 1 week
```

Interpretation:

```text
Both pipelines agree that monthly associations are mainly strongest at lag 0 months.

Both pipelines also agree that weekly associations often peak around lag 1 week.

This suggests that the same-month signal observed at monthly scale may contain shorter lagged structures visible only at weekly scale.
```

### Final qualitative synthesis

The final qualitative evidence summary supports the following conclusions:

```text
NO2 industrial contrast:
stronger in the ModAria framework than in the station-based framework.

PM2.5 regional/shared behavior:
supported by both pipelines, especially after ModAria reconstruction.

Respiratory temporal coherence:
one of the most robust findings across the project.

Cardiocirculatory industrial relevance:
supported mainly by health rates and ModAria integration, especially in the industrial area.

Monthly lag 0 dominance:
robust across both exposure frameworks.

Weekly short-lag signal:
supported by both station-based and ModAria pipelines.
```

### Main Part 5 outputs

Main CSV outputs:

```text
final_standardized_correlation_results.csv
final_station_vs_modaria_correlation_comparison.csv
final_standardized_lag_best_results.csv
final_standardized_lag_full_results.csv
final_station_vs_modaria_lag_comparison.csv
final_methodological_comparison_station_vs_modaria.csv
final_robust_conclusions_summary.csv
final_quantitative_synthesis_summary.csv
final_project_synthesis_summary.csv
```

Main plot outputs:

```text
final_project_pipeline_overview.png
final_monthly_station_vs_modaria_correlations.png
final_seasonal_station_vs_modaria_correlations.png
final_monthly_delta_rho_modaria_minus_station.png
final_seasonal_delta_rho_modaria_minus_station.png
final_monthly_best_lag_station_vs_modaria.png
final_weekly_best_lag_station_vs_modaria.png
final_overall_monthly_rho_vs_lag_station_vs_modaria.png
final_overall_weekly_rho_vs_lag_station_vs_modaria.png
final_evidence_strength_heatmap.png
```

Main interpretation:

```text
The analytical coding pipeline is complete.

The station-based pipeline was useful to develop the complete workflow.

The ModAria pipeline improves spatial coherence and provides the strongest final exposure framework.

The main conclusions are robust when interpreted cautiously:
NO2 better characterizes the industrial/urban context.
PM2.5 behaves as a more regional/shared pollutant.
Respiratory outcomes are the most temporally coherent health endpoint.
Cardiocirculatory burden is structurally higher in the industrial area and becomes more visible in the ModAria framework.
Monthly lag analyses do not show clear 1-3 month delayed patterns.
Weekly lag analyses suggest short-lag windows around 1-2 weeks.
```

---

# Main results

## Environmental results

### NO2

```text
Station-based framework:
NO2 does not clearly separate agricultural and industrial contexts.
Soresina is slightly higher than Rezzato, but the difference is modest and strongly affected by seasonality.

ModAria framework:
NO2 is higher in the industrial area.
This is coherent with its interpretation as a combustion-related pollutant associated with traffic, heating, urbanization and industrial activity.
```

Final interpretation:

```text
NO2 is the clearest pollutant for identifying the industrial/urban exposure profile when exposure is reconstructed at area level using ModAria municipal estimates.
```

### PM2.5

```text
Station-based framework:
Soresina shows higher PM2.5 than Brescia Villaggio Sereno, especially outside winter.

ModAria framework:
Agricultural and industrial PM2.5 exposure patterns are strongly overlapping and temporally similar.
```

Final interpretation:

```text
PM2.5 behaves more as a regional/shared pollutant than as a simple agricultural-versus-industrial discriminator.
This is coherent with secondary aerosol formation, atmospheric stagnation and regional pollution dynamics in the Po Valley.
```

---

## Health results

### Respiratory outcomes

```text
Respiratory rates are broadly comparable between the two areas.
They show the clearest temporal coherence with pollutant variation.
Associations are positive in both station-based and ModAria frameworks.
```

Final interpretation:

```text
Respiratory acute event rates are the most consistent environmental-health endpoint in the project.
```

### Cardiocirculatory outcomes

```text
Cardiocirculatory rates are consistently higher in the industrial area after population normalization.
The higher industrial cardiocirculatory burden is not fully explained by age structure, especially because it is visible in the <65 group.

Pollutant-health correlations for cardiocirculatory outcomes are more heterogeneous than respiratory correlations.
They are more visible in the industrial area and in the ModAria framework.
```

Final interpretation:

```text
Cardiocirculatory outcomes are relevant for the industrial context, but their association with pollutant variation is more complex and more likely influenced by structural, demographic and unmeasured factors.
```

---

## Lag results

### Monthly lag

```text
Station-based monthly lag:
Lag 0 dominates most combinations.

ModAria monthly lag:
Lag 0 dominates all combinations.
```

Interpretation:

```text
No clear 1-3 month delayed pattern emerges.
Monthly associations are mainly same-month and seasonally structured.
```

### Weekly lag

```text
Station-based weekly lag:
Best lags often occur around 1-2 weeks.

ModAria weekly lag:
Best lags often occur around 1-2 weeks.
```

Interpretation:

```text
The same-month signal observed at monthly scale may contain shorter delayed associations within the month.
Weekly results should be interpreted as a short-lag window, not as a precise causal delay.
```

---

# Final interpretation

The final project interpretation is:

```text
Industrial and agricultural areas show different environmental-health profiles, but the difference is pollutant-specific, outcome-specific and scale-dependent.

NO2 is the clearest pollutant for the industrial/urban exposure profile when using ModAria area-level exposure.

PM2.5 behaves as a regional/shared pollutant affecting both areas.

Respiratory outcomes show the most consistent temporal coherence with pollutant variation.

Cardiocirculatory outcomes are structurally higher in the industrial area and become more visible in the ModAria framework, but their association with pollutant variation is more heterogeneous.

Monthly lag analysis does not show clear delayed patterns at 1-3 months.

Weekly lag analysis suggests short-lag windows around 1-2 weeks.

The ModAria framework provides the most spatially coherent final exposure assessment.
```

---

# Limitations

The project has several important limitations.

## Ecological design

All analyses are based on aggregated area-level data.

```text
The results cannot be interpreted as individual-level causal effects.
```

A correlation between area-level pollutant exposure and area-level health event rates does not prove that the individuals experiencing higher exposure are the same individuals experiencing the health events.

## Health event data

The health dataset contains event-level records, not individual patient histories.

This means that:

- repeated events from the same person cannot be identified;
- individual risk factors are not available;
- smoking status, occupation, comorbidities and medication use are not available;
- the municipality variable may not perfectly represent the patient residential exposure location.

## Population and age

Part 2.2 uses population-normalized rates, and Part 2.3 checks age-specific rates.

However:

```text
The environmental-health integration is not a full age-standardized epidemiological model.
```

Age remains an important potential confounder.

## Exposure assessment

The station-based framework uses one monitoring station per pollutant and area. This is useful but spatially limited.

The ModAria framework improves spatial coherence but still provides area-level ecological exposure estimates. It does not represent individual exposure and does not account for within-municipality variability.

## Meteorology and seasonality

Meteorological variables are not included.

Important omitted factors include:

- temperature;
- humidity;
- wind speed;
- precipitation;
- atmospheric stability;
- boundary-layer height;
- respiratory infections;
- influenza circulation.

Because both pollutants and health outcomes vary seasonally, some observed associations may be driven by shared seasonal dynamics.

## Temporal autocorrelation

Pollutant concentrations and health event rates are time series.

The current analysis uses Spearman correlations and paired tests but does not explicitly model temporal autocorrelation.

## Multiple comparisons

Many comparisons are performed across:

- pollutants;
- outcomes;
- areas;
- temporal scales;
- exposure frameworks;
- lags.

For this reason, p-values are interpreted as descriptive evidence, not as definitive proof.

## Missing COVID years

The years 2020, 2021 and 2022 are excluded.

The code prevents invalid lag links across the 2019-2023 gap, but the missing years still limit temporal continuity.

## Missing additional pollutants and source information

The project does not include:

- NH3;
- PM chemical speciation;
- emission inventories;
- source apportionment;
- meteorological adjustment.

This limits the ability to directly attribute PM2.5 patterns to agricultural or industrial sources.

---

# Current project status

The Python analytical pipeline is complete.

Completed parts:

```text
Part 1:
Station-based NO2 and PM2.5 statistical analyses.

Part 2:
Health data exploration, population-normalized rates and age-specific rate checks.

Part 3:
Station-based seasonal/monthly environmental-health integration and lag analysis.

Part 4:
ModAria exposure reconstruction, area pollutant comparison, environmental-health integration and lag analysis.

Part 5:
Final synthesis comparing station-based and ModAria-based pipelines.
```

The project is ready for:

- final report preparation;
- final presentation figure selection;
- final GitHub commit;
- optional QGIS-based spatial visualization by the group.

---

# Possible future extensions

The following extensions could build on this project, but they are beyond the current analytical coding scope.

Possible future work:

- include meteorological variables;
- include NH3 if reliable data become available;
- add PM chemical speciation or source apportionment;
- validate ModAria estimates against monitoring station measurements;
- perform age-stratified environmental-health integration;
- use generalized additive models;
- use distributed lag models;
- explore moving-average or cumulative exposure indicators;
- add QGIS maps of exposure, health rates and municipality-level patterns;
- extend the analysis if additional post-2023 health data become available.

These extensions would increase robustness and complexity, but the current project already provides a complete reproducible exploratory pipeline.

---

# GitHub workflow

Recommended standard workflow for each coding session:

```bash
git pull
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
git commit -m "Add final project synthesis"
git commit -m "Update README with final project documentation"
```

Recommended final commit:

```bash
git add -A
git commit -m "Finalize project synthesis and README"
git push
```

---

# Final conclusion

This repository contains a complete exploratory data science workflow for comparing agricultural/rural and industrial/urban environmental-health patterns in Lombardy.

The project progressively moves from station-based pollutant comparisons to a more spatially coherent ModAria municipality-based exposure framework.

The final results suggest that:

```text
NO2 is the clearest marker of the industrial/urban exposure profile in the ModAria framework.

PM2.5 behaves as a regional/shared pollutant affecting both agricultural and industrial areas.

Respiratory acute event rates show the most consistent temporal coherence with pollutant variation.

Cardiocirculatory rates are structurally higher in the industrial area and are more visible in the ModAria integration, but their interpretation is more complex.

Monthly associations are mainly same-month and seasonally structured.

Weekly analyses suggest possible short-lag windows of approximately 1-2 weeks.
```

All conclusions should be interpreted as ecological and exploratory, not as individual-level causal evidence.

The analytical Python part of the project is complete and provides a reproducible foundation for final reporting, presentation and optional spatial visualization.