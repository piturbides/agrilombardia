# Agricultural vs Industrial Environmental-Health Analysis in Lombardy

## Human Health and Environment Data Science Laboratory project

This repository contains an exploratory environmental-health data-science project developed for the **Human Health and Environment Data Science Laboratory** course.

The project compares two Lombardy study areas with different territorial and emission-source profiles:

- an **industrial/urban area**;
- an **agricultural/rural area**.

The objective is to investigate whether these two contexts show different air-pollution patterns and whether such patterns are reflected in population-normalized acute respiratory and cardiocirculatory health indicators.

The analysis is ecological and exploratory. It is based on aggregated environmental and health data and does **not** provide individual-level causal inference.

---

## Research question

The main research question is:

> How do different emission-source contexts, industrial/urban versus agricultural/rural, influence air-pollution patterns, and how are these differences reflected in respiratory and cardiocirculatory acute health outcomes?

The project is organized around a 2 × 2 × 2 analytical framework:

| Dimension | Categories |
|---|---|
| Pollutants | NO2, PM2.5 |
| Health outcomes | Respiratory acute events, Cardiocirculatory acute events |
| Study areas | Agricultural/rural area, Industrial/urban area |

This structure allows the analysis to compare 8 main pollutant-outcome-area combinations, together with overall results.

---

## Project status

The project pipeline is complete up to the APHREH-ADSMap modelling extension.

Completed phases:

1. **Station-based pollutant analysis**
2. **Health data exploration, aggregation and age-structure check**
3. **Station-based environmental-health integration and lag analysis**
4. **Health-aligned ModAria exposure reconstruction and integration**
5. **Station-based vs ModAria synthesis**
6. **APHREH-ADSMap modelling extension with sensitivity analysis**

---

## Study period

The common years used for the definitive environmental-health integration are:

    2016, 2017, 2018, 2019, 2023

The years 2020, 2021 and 2022 were excluded because they are absent from the health dataset and would also be affected by COVID-related disruptions in mobility, emissions, healthcare access and health-event patterns.

The code avoids artificial lag links across the 2019-2023 temporal gap.

---

## Study areas

The final health-aligned study area includes **37 municipalities**:

    21 Agricultural municipalities
    16 Industrial municipalities

The agricultural area is not equivalent to the province of Cremona. Some agricultural municipalities are located in the province of Brescia. Therefore, the project uses a QGIS/health-based municipality assignment instead of simple province boundaries.

### Industrial area

- Brescia
- Rezzato
- Castel Mella
- San Zeno Naviglio
- Gussago
- Roncadelle
- Collebeato
- Flero
- Botticino
- Castenedolo
- Borgosatollo
- Cellatica
- Torbole Casaglia
- Concesio
- Nave
- Bovezzo

### Agricultural area

- Verolavecchia
- Corte de' Cortesi con Cignone
- Castelvisconti
- Paderno Ponchielli
- Pontevico
- Pozzaglio ed Uniti
- Genivolta
- Casalmorano
- Persico Dosimo
- Casalbuttano ed Uniti
- Borgo San Giacomo
- Quinzano d'Oglio
- Villachiara
- Azzanello
- Annicco
- Robecco d'Oglio
- Olmeneta
- Castelverde
- Soresina
- Corte de' Frati
- Bordolano

---

## Data sources

### Station-based environmental data

The first exposure framework uses ARPA Lombardia monitoring-station data.

| Pollutant | Agricultural proxy | Industrial proxy |
|---|---|---|
| NO2 | Soresina | Rezzato |
| PM2.5 | Soresina | Brescia Villaggio Sereno |

Station data are measured environmental observations and were useful for the first exploratory analyses. However, a single station cannot fully represent exposure across a multi-municipality study area, especially for spatially heterogeneous pollutants such as NO2.

### ModAria environmental data

The second exposure framework uses ARPA Lombardia ModAria municipality-level pollutant estimates.

The definitive ModAria folder was rebuilt to include exactly the 37 municipalities present in the health dataset:

    Dati/raw/ModariaDataset_health_aligned/
    ├── Agricultural/
    └── Industrial/

This health-aligned ModAria reconstruction is the preferred exposure framework for area-level environmental-health interpretation.

Two exposure indicators are computed:

- arithmetic area mean;
- population-weighted area mean.

The population-weighted exposure is used as the main indicator for health integration because it better represents the exposure experienced by the population living in each area.

### Health data

The raw health dataset is an event-level dataset.

Local path:

    Dati/raw/Health_events_2015_2023.csv

Selected outcomes:

    TYPE = MEDICO ACUTO and TYPE_DTL = RESPIRATORIA
    TYPE = MEDICO ACUTO and TYPE_DTL = CARDIOCIRCOLATORIA

Important note:

The health dataset is event-level, not patient-level. Therefore, repeated events from the same individual cannot be identified.

### Population data

ISTAT municipality-level population files are used for:

- health-rate denominators;
- age-structure analysis;
- population-weighted ModAria exposure;
- APHREH-ADSMap BSA population columns.

Population files are stored in:

    Dati/raw/population/

---

## Sensitive data and Git tracking

Some files are intentionally ignored by Git because they contain raw or intermediate health-related information.

Ignored files/folders:

    Dati/raw/Health_events_2015_2023.csv
    Dati/output/2-Health data/2.2-Health event aggregation/health_events_selected_areas_outcomes.csv
    Dati/output/6-APHREH ADSMap/6.1-Prepared model inputs/
    Dati/output/6-APHREH ADSMap/6.2-Model outputs/
    Dati/output/6-APHREH ADSMap/_runtime/

Reason:

These files may contain raw health-event records, daily municipality-level health counts, or model inputs/outputs derived from sensitive health data.

The following APHREH folder is versioned:

    Dati/output/6-APHREH ADSMap/6.3-Output summaries/

Reason:

This folder contains only aggregated summary CSV files and plots, not raw sensitive health-event records.

---

## Repository structure

    .
    ├── README.md
    ├── requirements.txt
    ├── main.py
    ├── .gitignore
    │
    ├── Dati/
    │   ├── raw/
    │   │   ├── ModariaDataset_health_aligned/
    │   │   │   ├── Agricultural/
    │   │   │   └── Industrial/
    │   │   ├── population/
    │   │   │   ├── Brescia_2016.csv
    │   │   │   ├── Brescia_2017.csv
    │   │   │   ├── Brescia_2018.csv
    │   │   │   ├── Brescia_2019.csv
    │   │   │   ├── Brescia_2023.csv
    │   │   │   ├── Cremona_2016.csv
    │   │   │   ├── Cremona_2017.csv
    │   │   │   ├── Cremona_2018.csv
    │   │   │   ├── Cremona_2019.csv
    │   │   │   └── Cremona_2023.csv
    │   │   ├── Brescia_VillagioSereno_PM25_2016_2025.csv
    │   │   ├── Health_events_2015_2023.csv              # ignored by Git
    │   │   ├── Rezzato_NO2_2016_2025.csv
    │   │   ├── Soresina_2016_2025_PM25.csv
    │   │   └── Soresina_NO2_2016_2025.csv
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
    │       ├── 5-Preliminary synthesis/
    │       │   └── 5.1-Station vs ModAria synthesis/
    │       │
    │       └── 6-APHREH ADSMap/
    │           ├── 6.1-Prepared model inputs/       # ignored by Git
    │           ├── 6.2-Model outputs/               # ignored by Git
    │           ├── 6.3-Output summaries/            # versioned aggregated outputs
    │           └── _runtime/                        # ignored by Git
    │
    ├── external_models/
    │   └── APHREH-ADSMap_1.0.0/
    │
    └── src/
        ├── data_loader.py
        │
        ├── statistical_tests/
        │   ├── monthly_seasonal_no2.py
        │   ├── no2_definitivo_non_covid.py
        │   ├── pm25_definitivo_non_covid.py
        │   └── preliminary_no2.py
        │
        ├── health_analysis/
        │   ├── health_age_structure_check.py
        │   ├── health_data_exploration.py
        │   └── health_event_aggregation.py
        │
        ├── integration/
        │   ├── environment_health_integration.py
        │   ├── monthly_environment_health_integration.py
        │   ├── monthly_lag_analysis.py
        │   └── weekly_lag_analysis.py
        │
        ├── modaria_exposure/
        │   ├── modaria_area_pollutant_comparison.py
        │   ├── modaria_data_validation.py
        │   ├── modaria_environment_health_integration.py
        │   └── modaria_monthly_weekly_lag_analysis.py
        │
        ├── preliminary_synthesis/
        │   └── preliminary_station_modaria_synthesis.py
        │
        └── aphreh_adapter/
            ├── inspect_aphreh_outputs.py
            ├── plot_aphreh_outputs.py
            ├── plot_aphreh_sensitivity_outputs.py
            ├── prepare_aphreh_inputs.py
            ├── prepare_aphreh_inputs_no2_cardiocirculatory.py
            ├── run_aphreh_no2_cardiocirculatory_sensitivity.py
            ├── run_aphreh_pilot.py
            ├── run_aphreh_sensitivity.py
            ├── summarize_aphreh_outputs.py
            ├── summarize_aphreh_sensitivity_outputs.py
            └── summarize_plot_aphreh_no2_cardiocirculatory.py

---

## Installation

Create a virtual environment:

    python -m venv .venv

Activate the virtual environment.

On Windows PowerShell:

    .venv\Scripts\activate

Install dependencies:

    pip install -r requirements.txt

---

## How to run the project

The project is executed through `main.py`.

The workflow is:

1. open `main.py`;
2. uncomment the function corresponding to the desired analysis;
3. keep the other function calls commented;
4. run:

    python main.py

Example:

    from src.modaria_exposure.modaria_area_pollutant_comparison import run_modaria_area_pollutant_comparison

    if __name__ == "__main__":
        run_modaria_area_pollutant_comparison()

The same logic is used for all scripts.

---

## Recommended reproduction order

To reproduce the complete analytical workflow from scratch, use the following order:

    1. Station-based pollutant analysis
       src/statistical_tests/

    2. Health data exploration and aggregation
       src/health_analysis/

    3. Station-based environmental-health integration and lag analysis
       src/integration/

    4. Health-aligned ModAria exposure reconstruction and integration
       src/modaria_exposure/

    5. Station-based vs ModAria synthesis
       src/preliminary_synthesis/

    6. APHREH-ADSMap modelling extension
       src/aphreh_adapter/

Important:

Part 6 depends on the health-aligned ModAria outputs and on the health-event aggregation outputs.

Because some health-derived files are ignored by Git, full reproduction requires local access to the raw health dataset.

---

# Analytical workflow

---

## Part 1 — Station-based pollutant analysis

Code folder:

    src/statistical_tests/

Output folder:

    Dati/output/1-Statistical tests/

Main scripts:

    preliminary_no2.py
    monthly_seasonal_no2.py
    no2_definitivo_non_covid.py
    pm25_definitivo_non_covid.py

Main operations:

- load station-based pollutant data;
- clean invalid values;
- aggregate data at daily, monthly and seasonal scales;
- exclude COVID-related years in definitive analyses;
- compute descriptive statistics;
- test normality;
- perform non-parametric station comparisons;
- export CSV tables and plots.

Main interpretation:

Station-based NO2 does not clearly separate agricultural and industrial contexts. Soresina is slightly higher than Rezzato, but the difference is modest and strongly affected by seasonality.

Station-based PM2.5 is generally higher in Soresina than in Brescia Villaggio Sereno. This suggests that PM2.5 is not only an industrial/urban pollutant and may reflect regional secondary aerosol formation and agricultural precursor contributions.

---

## Part 2 — Health data exploration, aggregation and age-structure check

Code folder:

    src/health_analysis/

Output folder:

    Dati/output/2-Health data/

Main scripts:

    health_data_exploration.py
    health_event_aggregation.py
    health_age_structure_check.py

Main operations:

- load and inspect event-level health records;
- parse dates;
- clean age values;
- select respiratory and cardiocirculatory acute events;
- assign events to agricultural and industrial areas;
- load ISTAT population denominators;
- compute annual, monthly and seasonal rates per 10,000 inhabitants;
- perform age-structure and age-specific rate checks.

Health-rate formula:

    Rate per 10,000 inhabitants = (Number of events / Population) × 10,000

Main interpretation:

Population normalization is essential because the industrial area has a much larger population than the agricultural area.

Respiratory rates are broadly comparable between the two areas.

Cardiocirculatory rates are consistently higher in the industrial area.

The higher industrial cardiocirculatory burden is not fully explained by older age structure, because it remains visible in the <65 group.

Key age-specific result:

    Mean <65 cardiocirculatory rate:
    Industrial area   ≈ 103.5 events per 10,000 inhabitants
    Agricultural area ≈ 77.6 events per 10,000 inhabitants

    Industrial/Agricultural ratio ≈ 1.33

---

## Part 3 — Station-based environmental-health integration and lag analysis

Code folder:

    src/integration/

Output folder:

    Dati/output/3-Environmental health integration/

Main scripts:

    environment_health_integration.py
    monthly_environment_health_integration.py
    monthly_lag_analysis.py
    weekly_lag_analysis.py

Part 3 integrates station-based pollutant indicators with population-normalized health event rates.

Main analyses:

- seasonal environmental-health integration;
- monthly environmental-health integration;
- monthly lag analysis;
- weekly lag analysis.

Main monthly overall Spearman results:

    NO2 vs Respiratory rate:          rho ≈ 0.485
    NO2 vs Cardiocirculatory rate:    rho ≈ 0.281
    PM2.5 vs Respiratory rate:        rho ≈ 0.458
    PM2.5 vs Cardiocirculatory rate:  rho ≈ 0.259

Main interpretation:

Station-based pollutant-health associations are mostly positive.

Respiratory outcomes show the clearest temporal coherence with pollutant variation.

Cardiocirculatory associations are weaker and more heterogeneous.

Monthly lag analyses are mainly strongest at lag 0 months.

Weekly lag analyses suggest short-lag structures around 1-2 weeks, especially for respiratory outcomes and in the industrial area.

Main limitation:

The exposure framework is spatially limited because one station cannot represent all municipalities in a multi-municipality area.

---

## Part 4 — Health-aligned ModAria exposure reconstruction and environmental-health integration

Code folder:

    src/modaria_exposure/

Output folder:

    Dati/output/4-Modaria exposure/

Main scripts:

    modaria_data_validation.py
    modaria_area_pollutant_comparison.py
    modaria_environment_health_integration.py
    modaria_monthly_weekly_lag_analysis.py

Part 4 introduces the health-aligned ModAria framework.

This is a key methodological improvement because exposure is reconstructed on the same 37 municipalities used in the health dataset.

---

### Part 4.1 — ModAria data validation and exposure construction

Expected input structure:

    37 selected municipalities × 2 pollutants = 74 files

Main validation result:

    Total files found = 74
    Industrial municipalities = 16
    Agricultural municipalities = 21
    All expected municipality-pollutant files found
    No missing daily records in selected years
    Population rows = 185
    Expected population rows = 185

Main interpretation:

The health-aligned ModAria dataset is complete and suitable for area-level exposure reconstruction.

---

### Part 4.2 — ModAria area pollutant comparison

Main interpretation:

NO2 is higher in the industrial area when exposure is reconstructed from all selected health-aligned municipalities.

This is coherent with NO2 as a combustion-related pollutant linked to traffic, heating, urbanization and industrial activity.

PM2.5 shows stronger overlap between areas and behaves more as a regional, seasonally shared pollutant.

This result improves the previous station-based interpretation, where NO2 did not clearly separate the two contexts.

---

### Part 4.3 — ModAria environmental-health integration

Main monthly Spearman results using population-weighted exposure:

    Overall:
    NO2 vs Respiratory rate:          rho ≈ 0.324
    NO2 vs Cardiocirculatory rate:    rho ≈ 0.433
    PM2.5 vs Respiratory rate:        rho ≈ 0.450
    PM2.5 vs Cardiocirculatory rate:  rho ≈ 0.221

    Industrial:
    NO2 vs Respiratory rate:          rho ≈ 0.293
    NO2 vs Cardiocirculatory rate:    rho ≈ 0.375
    PM2.5 vs Respiratory rate:        rho ≈ 0.425
    PM2.5 vs Cardiocirculatory rate:  rho ≈ 0.387

    Agricultural:
    NO2 vs Respiratory rate:          rho ≈ 0.396
    NO2 vs Cardiocirculatory rate:    rho ≈ 0.281
    PM2.5 vs Respiratory rate:        rho ≈ 0.444
    PM2.5 vs Cardiocirculatory rate:  rho ≈ 0.125

Main interpretation:

Respiratory outcomes remain the most consistent endpoint.

PM2.5-respiratory remains one of the most stable pollutant-outcome associations.

NO2-cardiocirculatory becomes stronger in the ModAria framework, especially in the industrial context.

The agricultural area is not a clean reference area: respiratory associations remain visible.

---

### Part 4.4 — ModAria monthly and weekly lag analysis

Monthly lag interpretation:

Lag 0 months is the strongest positive association in all tested pollutant-outcome-group combinations.

No clear 1-3 month delayed pattern emerges.

Monthly associations are mainly same-month and seasonally structured.

Weekly lag interpretation:

Several best lags occur around lag 1 or lag 2 weeks.

The industrial area shows the clearest short-lag structure.

NO2-cardiocirculatory becomes one of the strongest weekly associations.

Weekly results should be interpreted as broad short-lag coherence, not as precise causal delay estimates.

Main overall weekly best lags:

    NO2 vs Respiratory:
    best lag = 2 weeks

    NO2 vs Cardiocirculatory:
    best lag = 2 weeks

    PM2.5 vs Respiratory:
    best lag = 1 week

    PM2.5 vs Cardiocirculatory:
    best lag = 1 week

---

## Part 5 — Station-based vs ModAria synthesis

Code folder:

    src/preliminary_synthesis/

Output folder:

    Dati/output/5-Preliminary synthesis/5.1-Station vs ModAria synthesis/

Main script:

    preliminary_station_modaria_synthesis.py

Part 5 compares the station-based and health-aligned ModAria pipelines.

Main goals:

- standardize correlation outputs from both pipelines;
- compare station-based and ModAria-based correlations;
- compare station-based and ModAria-based lag patterns;
- identify robust conclusions;
- identify method-dependent findings;
- produce compact summary tables and presentation-ready plots.

Main synthesis:

The direction of environmental-health associations is generally positive in both pipelines.

Monthly associations are more stable than seasonal associations.

Both pipelines show monthly lag 0 dominance.

Both pipelines suggest weekly short-lag structures around 1-2 weeks.

ModAria improves spatial coherence and provides the preferred exposure framework for final interpretation.

Main robust conclusions:

NO2 is the clearest industrial/urban exposure marker after ModAria reconstruction.

PM2.5 behaves as a regional/shared pollutant with strong respiratory relevance.

Respiratory outcomes are the most temporally coherent health endpoint.

Cardiocirculatory outcomes are structurally higher in the industrial area and become more visible in the ModAria framework, especially with NO2.

---

## Part 6 — APHREH-ADSMap modelling extension

Code folder:

    src/aphreh_adapter/

Output folders:

    Dati/output/6-APHREH ADSMap/6.1-Prepared model inputs/    # ignored by Git
    Dati/output/6-APHREH ADSMap/6.2-Model outputs/            # ignored by Git
    Dati/output/6-APHREH ADSMap/6.3-Output summaries/         # versioned aggregated summaries
    Dati/output/6-APHREH ADSMap/_runtime/                     # ignored by Git

External model folder:

    external_models/APHREH-ADSMap_1.0.0/

Part 6 adapts the APHREH-ADSMap model to the project data.

The original professor model is not modified directly. Each run creates a local runtime copy, patches only the runtime configuration and writes outputs to dedicated folders.

---

### APHREH-ADSMap input structure

Each APHREH run uses:

    exposure_data.csv
    outcome_data.csv
    BSA.csv
    SRCBSA.csv

In this project:

    BSA = municipality
    SRC = municipality
    SRCBSA = identity municipality-to-municipality mapping

This allows daily ModAria exposure and daily health-event counts to be used at municipality level.

---

### APHREH parameter grid

The final focused sweep uses:

    Exposure percentiles:
    P75, P85, P95

    Lags:
    0, 3, 7, 14 days

    Total combinations:
    3 × 4 = 12

Bootstrap and sensitivity settings:

    bootstrap_iterations = 100
    sensitivity_analysis = ON
    sensitivity range = -40% to +100%, step 20%

The focused 12-combination grid was selected to balance:

- computational feasibility;
- interpretability;
- consistency with previous weekly lag findings;
- project scope.

---

### APHREH metrics

    MARM:
    model-derived relevance score averaged across municipalities.

    WMARM:
    population-weighted version of MARM.

WMARM is used to select the best parameter combination.

Important interpretation note:

WMARM is not a Spearman correlation.

WMARM is not a causal effect size.

WMARM identifies the APHREH parameter configuration producing the strongest population-weighted model signal.

---

### Part 6.1 — PM2.5 -> Respiratory

Main scripts:

    prepare_aphreh_inputs.py
    run_aphreh_sensitivity.py
    summarize_aphreh_sensitivity_outputs.py
    plot_aphreh_sensitivity_outputs.py

Final output summary folder:

    Dati/output/6-APHREH ADSMap/6.3-Output summaries/PM25_Respiratory_sensitivity_bs100/

Input characteristics:

    Pollutant: PM2.5
    Outcome: Respiratory acute events
    Municipalities: 37
    Dates: 1826
    Respiratory events: 13,655

Selected APHREH parameter:

    P75_L0

Main model values:

    MARM  ≈ 5.01e-05
    WMARM ≈ 4.17e-05

Main interpretation:

The strongest population-weighted APHREH signal for PM2.5-respiratory was obtained with moderately high PM2.5 exposure days, defined by the 75th percentile.

The selected lag was 0 days, but this should not be interpreted as proof of an immediate causal effect.

The spatial pattern is not completely separated between agricultural and industrial municipalities, supporting the interpretation of PM2.5 as a shared regional pollutant with respiratory relevance.

Sensitivity analysis interpretation:

When respiratory events during exposed days are artificially increased, WMARM increases.

This supports the internal consistency of the adapted APHREH pipeline, but it does not prove causal effects.

---

### Part 6.2 — NO2 -> Cardiocirculatory

Main scripts:

    prepare_aphreh_inputs_no2_cardiocirculatory.py
    run_aphreh_no2_cardiocirculatory_sensitivity.py
    summarize_plot_aphreh_no2_cardiocirculatory.py

Final output summary folder:

    Dati/output/6-APHREH ADSMap/6.3-Output summaries/NO2_Cardiocirculatory_sensitivity_bs100/

Input characteristics:

    Pollutant: NO2
    Outcome: Cardiocirculatory acute events
    Municipalities: 37
    Dates: 1826
    Cardiocirculatory events: 33,495

Selected APHREH parameter:

    P95_L14

Main model values:

    MARM  ≈ 5.7e-05
    WMARM ≈ 5.9e-05

Important caution:

P95_L0 was very close to P95_L14.

Therefore, the robust interpretation is the importance of high NO2 exposure days, not a definitive biological 14-day lag.

Main interpretation:

The NO2-cardiocirculatory APHREH signal is driven by high or extreme NO2 exposure days.

The highest positive municipality-level values are concentrated in industrial municipalities.

Most agricultural municipalities show lower or negative model indices.

This supports the interpretation of NO2 as the clearest industrial/urban exposure marker and of cardiocirculatory outcomes as more relevant in the industrial framework.

Sensitivity analysis interpretation:

When cardiocirculatory events during exposed days are artificially increased, WMARM increases.

This confirms a coherent internal model response to strengthened exposure-day outcome contrast.

---

## APHREH summary outputs

Tracked APHREH summary folders:

    Dati/output/6-APHREH ADSMap/6.3-Output summaries/
    ├── PM25_Respiratory_sensitivity_bs100/
    │   ├── plots/
    │   ├── aphreh_sensitivity_area_summary.csv
    │   ├── aphreh_sensitivity_exposure_thresholds.csv
    │   ├── aphreh_sensitivity_model_summary.csv
    │   ├── aphreh_sensitivity_municipality_summary.csv
    │   └── aphreh_sensitivity_parameter_sweep_summary.csv
    │
    └── NO2_Cardiocirculatory_sensitivity_bs100/
        ├── plots/
        ├── aphreh_no2_cardio_area_summary.csv
        ├── aphreh_no2_cardio_exposure_thresholds.csv
        ├── aphreh_no2_cardio_model_summary.csv
        ├── aphreh_no2_cardio_municipality_summary.csv
        └── aphreh_no2_cardio_parameter_sweep_summary.csv

Main APHREH plot types:

- MARM heatmap;
- WMARM heatmap;
- WMARM ranking plot;
- WMARM 3D surface plot;
- sensitivity analysis plot;
- interpolated sensitivity analysis plot.

---

# Main results

## Environmental results

### NO2

Station-based framework:

NO2 does not clearly separate agricultural and industrial contexts. Soresina is slightly higher than Rezzato, but the difference is modest and strongly affected by seasonality.

Health-aligned ModAria framework:

NO2 is higher in the industrial area. This is coherent with its interpretation as a combustion-related pollutant associated with traffic, heating, urbanization and industrial activity.

APHREH-ADSMap:

NO2-cardiocirculatory outputs show clearer positive indices in industrial municipalities.

Final interpretation:

NO2 is the clearest pollutant for identifying the industrial/urban exposure profile when exposure is reconstructed at area level using health-aligned ModAria municipal estimates.

---

### PM2.5

Station-based framework:

Soresina shows higher PM2.5 than Brescia Villaggio Sereno, especially outside winter.

Health-aligned ModAria framework:

Agricultural and industrial PM2.5 exposure patterns are strongly overlapping and temporally similar.

APHREH-ADSMap:

PM2.5-respiratory produces a diffuse health-relevant signal without complete industrial/agricultural separation.

Final interpretation:

PM2.5 behaves more as a regional/shared pollutant than as a simple agricultural-versus-industrial discriminator.

It remains strongly relevant for respiratory health interpretation.

---

## Health results

### Respiratory outcomes

Respiratory rates are broadly comparable between the two areas.

They show the clearest temporal coherence with pollutant variation.

Associations are positive in both station-based and ModAria frameworks.

PM2.5-respiratory is the most robust general pollutant-outcome pair across the project.

Final interpretation:

Respiratory acute event rates are the most consistent environmental-health endpoint in the project.

---

### Cardiocirculatory outcomes

Cardiocirculatory rates are consistently higher in the industrial area after population normalization.

The higher industrial cardiocirculatory burden is not fully explained by age structure, especially because it is visible in the <65 group.

Pollutant-health correlations for cardiocirculatory outcomes are more heterogeneous than respiratory correlations.

They are more visible in the industrial area and in the ModAria framework, especially with NO2.

APHREH-ADSMap confirms a clearer NO2-cardiocirculatory spatial signal in industrial municipalities.

Final interpretation:

Cardiocirculatory outcomes are relevant for the industrial context, but their interpretation is more complex and likely influenced by structural, demographic and unmeasured factors.

---

## Lag results

### Monthly lag

Station-based monthly lag:

Lag 0 dominates most combinations.

Health-aligned ModAria monthly lag:

Lag 0 dominates all combinations.

Interpretation:

No clear 1-3 month delayed pattern emerges.

Monthly associations are mainly same-month and seasonally structured.

---

### Weekly lag

Station-based weekly lag:

Best lags often occur around 1-2 weeks.

Health-aligned ModAria weekly lag:

Best lags often occur around 1-2 weeks overall and in the industrial area.

APHREH-ADSMap:

NO2-cardiocirculatory selected P95_L14, while PM2.5-respiratory had P75_L14 among high-ranking configurations.

Interpretation:

The same-month signal observed at monthly scale may contain shorter delayed associations within the month.

Weekly and APHREH results suggest that short-lag windows may be relevant, but they should not be interpreted as precise causal biological delays.

---

# Integrated interpretation

The final interpretation of the project is:

Industrial and agricultural areas show different environmental-health profiles, but the difference is pollutant-specific, outcome-specific and scale-dependent.

NO2 is the clearest pollutant for the industrial/urban exposure profile when using health-aligned ModAria area-level exposure.

PM2.5 behaves as a regional/shared pollutant affecting both agricultural and industrial areas.

Respiratory outcomes show the most consistent temporal coherence with pollutant variation.

Cardiocirculatory outcomes are structurally higher in the industrial area and become more visible in the ModAria and APHREH frameworks, especially with NO2.

Monthly lag analysis does not show clear delayed patterns at 1-3 months.

Weekly analyses suggest possible short-lag windows of approximately 1-2 weeks, especially in the industrial area.

APHREH-ADSMap confirms the feasibility of municipality-level vulnerability-style modelling and provides complementary evidence:

- PM2.5-respiratory as a diffuse health-relevant signal;
- NO2-cardiocirculatory as a clearer industrial/territorial signal.

---

# Strengths

Main strengths of the project:

1. **Progressive workflow**  
   The project moves from station-based analysis to health-aligned ModAria reconstruction and APHREH modelling.

2. **Spatial health alignment**  
   The final ModAria and APHREH analyses use the same 37 municipalities covered by the health dataset.

3. **Multiple temporal scales**  
   The project includes daily exposure, seasonal/monthly integration, monthly/weekly lag analysis and APHREH daily model inputs.

4. **Multiple exposure frameworks**  
   The project compares measured station data, ModAria municipality-level estimates and APHREH-ADSMap model outputs.

5. **Multiple health outcomes**  
   The project analyzes respiratory and cardiocirculatory events, with population normalization and age-structure checks.

6. **Explicit comparison of robust and method-dependent results**  
   The project distinguishes robust conclusions from exposure-framework-specific signals.

7. **Reproducible code organization**  
   Each analysis step has a dedicated script and output folder.

---

# Limitations

## Ecological design

All analyses are based on aggregated area-level or municipality-level data.

The results cannot be interpreted as individual-level causal effects.

A correlation between area-level pollutant exposure and area-level health event rates does not prove that the individuals experiencing higher exposure are the same individuals experiencing the health events.

---

## Health event data

The health dataset contains event-level records, not individual patient histories.

This means that:

- repeated events from the same person cannot be identified;
- individual risk factors are not available;
- smoking status is not available;
- occupation is not available;
- comorbidities are not available;
- medication use is not available;
- healthcare access is not modelled.

---

## Population and age

Population-normalized rates and age-specific checks were computed.

However, the environmental-health integration is not a full age-standardized epidemiological model.

Age remains an important potential confounder.

---

## Exposure assessment

The station-based framework uses one monitoring station per pollutant and area. This is useful but spatially limited.

The ModAria framework improves spatial coherence because it uses all 37 health-aligned municipalities, but it still provides ecological exposure estimates. It does not represent individual exposure and does not account for within-municipality variability.

---

## Meteorology and seasonality

Meteorological variables are not included.

Important omitted factors include:

- temperature;
- humidity;
- wind speed;
- precipitation;
- atmospheric stability;
- boundary-layer height;
- influenza circulation;
- respiratory infection waves.

Because both pollutants and health outcomes vary seasonally, some observed associations may be driven by shared seasonal dynamics.

---

## Temporal autocorrelation

Pollutant concentrations and health event rates are time series.

The current analysis uses Spearman correlations and paired tests but does not explicitly model temporal autocorrelation.

---

## Multiple comparisons

Many comparisons are performed across:

- pollutants;
- outcomes;
- areas;
- temporal scales;
- exposure frameworks;
- lags;
- APHREH parameter combinations.

For this reason, p-values and ranking metrics are interpreted as exploratory evidence, not as definitive proof.

---

## APHREH-ADSMap limitations

APHREH-ADSMap is used as a modelling extension, but:

- BSA is simplified as municipality;
- SRC-BSA mapping is an identity mapping;
- small municipalities may introduce random instability;
- the parameter grid is focused, not exhaustive;
- WMARM is model-specific and not a causal effect size;
- sensitivity analysis tests internal model response, not real-world counterfactual causality.

---

## Missing pollutants and source information

The project does not include:

- NH3;
- PM chemical speciation;
- emission inventories;
- source apportionment;
- meteorological adjustment.

This limits the ability to directly attribute PM2.5 patterns to agricultural or industrial sources.

---

# Possible future extensions

Possible future developments include:

1. **QGIS integration**  
   Map ModAria exposure, health rates and APHREH municipality-level indices.

2. **NH3 inclusion**  
   NH3 would be important for agricultural interpretation and secondary PM2.5 formation.

3. **Meteorological adjustment**  
   Temperature, humidity, wind, precipitation and stagnation indicators could be added.

4. **Age-standardized environmental-health analysis**  
   This would allow more robust handling of age-related vulnerability.

5. **Larger APHREH spatial units**  
   Small municipalities could be aggregated into larger zones to reduce random instability.

6. **Expanded APHREH parameter search**  
   More percentiles, more lags, more bootstrap iterations and additional pollutant-outcome pairs could be tested.

7. **Advanced epidemiological modelling**  
   Distributed lag models, mixed models, panel models or regression models with meteorological covariates could be implemented.

8. **Integration with additional environmental platforms**  
   ModAria results could be compared with Airscreen or other exposure sources, if available.

---

# Git workflow

Recommended standard workflow:

    git pull
    python main.py
    git status
    git add -A
    git commit -m "Clear commit message"
    git push

Useful commands:

    git status
    git diff
    git add -A
    git commit -m "Update README with complete phase 6 workflow"
    git push

---

# Final conclusion

This repository contains a complete exploratory data-science workflow for comparing agricultural/rural and industrial/urban environmental-health patterns in Lombardy.

The project progressively moves from station-based pollutant comparisons to a more spatially coherent health-aligned ModAria municipality-level exposure framework and finally to an APHREH-ADSMap modelling extension.

The current results suggest that:

- NO2 is the clearest marker of the industrial/urban exposure profile in the health-aligned ModAria framework.
- PM2.5 behaves as a regional/shared pollutant affecting both agricultural and industrial areas.
- Respiratory acute event rates show the most consistent temporal coherence with pollutant variation.
- Cardiocirculatory rates are structurally higher in the industrial area and become more visible in the ModAria and APHREH frameworks, especially with NO2.
- Monthly associations are mainly same-month and seasonally structured.
- Weekly analyses suggest possible short-lag windows of approximately 1-2 weeks, especially in the industrial area.
- APHREH-ADSMap confirms the feasibility of municipality-level vulnerability-style modelling and provides complementary evidence:
  - PM2.5-respiratory as a diffuse health-relevant signal;
  - NO2-cardiocirculatory as a clearer industrial/territorial signal.

All conclusions should be interpreted as ecological and exploratory, not as individual-level causal evidence.