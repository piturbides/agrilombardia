from src.statistical_tests.preliminary_no2 import run_preliminary_no2_analysis
from src.statistical_tests.monthly_seasonal_no2 import run_monthly_seasonal_no2_analysis
from src.statistical_tests.no2_definitivo_non_covid import run_no2_definitivo_non_covid_analysis
from src.statistical_tests.pm25_definitivo_non_covid import run_pm25_definitivo_non_covid_analysis
from src.health_analysis.health_data_exploration import run_health_data_exploration
from src.health_analysis.health_event_aggregation import run_health_event_aggregation
from src.health_analysis.health_age_structure_check import run_health_age_structure_check
from src.integration.environment_health_integration import run_environment_health_integration
from src.integration.monthly_environment_health_integration import run_monthly_environment_health_integration
from src.integration.monthly_lag_analysis import run_monthly_lag_analysis



if __name__ == "__main__":
    #run_preliminary_no2_analysis()
    #run_monthly_seasonal_no2_analysis()
    #run_no2_definitivo_non_covid_analysis()
    #run_pm25_definitivo_non_covid_analysis()
    #run_health_data_exploration()
    #run_health_event_aggregation()
    #run_health_age_structure_check()
    #run_environment_health_integration()
    #run_monthly_environment_health_integration()
    run_monthly_lag_analysis()
