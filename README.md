# Human Health and Environment Data Science Laboratory

Preliminary and statistical analysis of air pollution data for the Human Health and Environment Data Science Laboratory project.

## Project context

The project investigates differences in air pollution patterns between areas with different territorial and emission profiles in Lombardy, with a focus on the comparison between agricultural/rural and industrial/urban contexts.

The current environmental analysis focuses on measured air pollutant concentrations from ARPA Lombardia monitoring stations.

## Current analyses

### NO2 analysis: Soresina vs Rezzato

NO2 concentrations were compared between:

- Soresina, used as a proxy for an agricultural/rural context;
- Rezzato, used as a proxy for a more industrialized context in the Brescia area.

The analysis includes:

- daily mean NO2 comparison;
- monthly mean NO2 comparison;
- seasonal mean NO2 comparison;
- exclusion of COVID-related years 2020, 2021 and 2022;
- statistical tests: Shapiro-Wilk, Mann-Whitney U, Wilcoxon signed-rank;
- graphical outputs and CSV summary tables.

The definitive NO2 non-COVID analysis is saved in:

```text
Dati/output/1-Statistical tests/1.3-NO2_definitivo