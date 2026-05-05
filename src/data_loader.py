import pandas as pd


def load_pollution_data(path, station_name, pollutant_name):
    """
    Load and clean pollution data from Regione Lombardia CSV format.

    Parameters
    ----------
    path : str
        Path to the raw CSV file.
    station_name : str
        Name of the monitoring station.
    pollutant_name : str
        Name of the pollutant column, e.g. 'NO2' or 'PM25'.

    Returns
    -------
    pandas.DataFrame
        Cleaned dataframe with columns: Data, pollutant_name, Station.
    """

    df = pd.read_csv(
        path,
        sep=",",
        skiprows=2,
        encoding="latin1",
        na_values="-999"
    )

    df.columns = ["Data", pollutant_name]

    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    df[pollutant_name] = pd.to_numeric(df[pollutant_name], errors="coerce")

    df = df.dropna(subset=["Data", pollutant_name])
    df["Station"] = station_name

    return df