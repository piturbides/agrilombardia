"""
Summarize APHREH-ADSMap pilot outputs into project-readable tables.

Input:
    Dati/output/6-APHREH ADSMap/6.2-Model outputs/PM25_Respiratory/v01/

Output:
    Dati/output/6-APHREH ADSMap/6.3-Output summaries/PM25_Respiratory/

Generated files:
    aphreh_pilot_municipality_summary.csv
    aphreh_pilot_area_summary.csv
    aphreh_pilot_model_summary.csv
    aphreh_pilot_exposure_thresholds.csv

Pilot:
    PM2.5 -> Respiratory acute events
    Single-combination test: P75_L0
"""

from pathlib import Path
import pandas as pd


# =============================================================================
# Configuration
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PILOT_LABEL = "PM25_Respiratory"
PARAMETER_FOLDER = "MAX_WMARM_P75_L0"

APHREH_OUTPUT_ROOT = (
    PROJECT_ROOT
    / "Dati/output/6-APHREH ADSMap/6.2-Model outputs"
    / PILOT_LABEL
    / "v01"
)

APHREH_BEST_PARAM_DIR = APHREH_OUTPUT_ROOT / PARAMETER_FOLDER

STUDY_MUNICIPALITIES_PATH = (
    PROJECT_ROOT
    / "Dati/output/2-Health data/2.2-Health event aggregation/study_area_municipalities.csv"
)

SUMMARY_OUTPUT_DIR = (
    PROJECT_ROOT
    / "Dati/output/6-APHREH ADSMap/6.3-Output summaries"
    / PILOT_LABEL
)


# =============================================================================
# Helpers
# =============================================================================

def read_scalar_txt(path: Path, label: str) -> float:
    """
    Read files like:
        MARM: 2.29e-05
        WMARM: 1.98e-05
    """
    text = path.read_text(encoding="utf-8").strip()
    value = text.replace(label, "").replace(":", "").strip()
    return float(value)


def load_study_municipalities() -> pd.DataFrame:
    study = pd.read_csv(STUDY_MUNICIPALITIES_PATH, sep=";", low_memory=False)

    required = ["Area", "PROV", "Municipality", "Municipality_code"]
    missing = [col for col in required if col not in study.columns]
    if missing:
        raise ValueError(f"Missing columns in study municipalities file: {missing}")

    study = study.copy()
    study["BSA"] = study["Municipality_code"].astype(int)

    study = study[["BSA", "Municipality", "Area", "PROV"]].copy()
    study = study.rename(columns={"PROV": "Province"})

    return study


def load_aphreh_results() -> tuple[pd.DataFrame, pd.DataFrame]:
    index_raw_path = APHREH_BEST_PARAM_DIR / "index_raw.csv"
    index_cumulated_path = APHREH_BEST_PARAM_DIR / "index_cumulated_raw.csv"

    if not index_raw_path.exists():
        raise FileNotFoundError(f"Missing file: {index_raw_path}")

    if not index_cumulated_path.exists():
        raise FileNotFoundError(f"Missing file: {index_cumulated_path}")

    index_raw = pd.read_csv(index_raw_path)
    index_cumulated = pd.read_csv(index_cumulated_path)

    index_raw["BSA"] = index_raw["BSA"].astype(int)
    index_cumulated["BSA"] = index_cumulated["BSA"].astype(int)

    return index_raw, index_cumulated


def build_municipality_summary(
    study: pd.DataFrame,
    index_raw: pd.DataFrame,
    index_cumulated: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build one row per municipality.

    Main APHREH fields:
        INDEX_MEDIAN:
            multi-year median vulnerability/risk index.

        INDEX_Q25 / INDEX_Q75:
            interquartile range across selected years.

        CI_LOW_MEDIAN / CI_HIGH_MEDIAN:
            median lower/upper confidence bounds.

        AVG_STDEFF:
            averaged standardized effect used by MARM/WMARM computations.

    Important:
        AVG_STDEFF exists both in index_raw.csv and index_cumulated_raw.csv.
        To avoid pandas suffixes such as AVG_STDEFF_x / AVG_STDEFF_y, we keep
        AVG_STDEFF only from index_cumulated_raw.csv.
    """
    keep_cumulated = [
        "BSA",
        "INDEX_MEDIAN",
        "INDEX_Q25",
        "INDEX_Q75",
        "INDEX_IQR",
        "CI_LOW_MEDIAN",
        "CI_HIGH_MEDIAN",
        "AVG_STDEFF",
    ]

    missing = [col for col in keep_cumulated if col not in index_cumulated.columns]
    if missing:
        raise ValueError(f"Missing columns in index_cumulated_raw.csv: {missing}")

    municipality_summary = study.merge(
        index_cumulated[keep_cumulated],
        on="BSA",
        how="left",
        validate="one_to_one",
    )

    # Add year-specific APHREH index and standardized-effect values.
    # Exclude AVG_STDEFF here because it is already taken from index_cumulated_raw.csv.
    year_index_columns = [
        col for col in index_raw.columns
        if (col.endswith("INDEX") or col.endswith("STDEFF"))
        and col != "AVG_STDEFF"
    ]

    year_values = index_raw[["BSA"] + year_index_columns].copy()

    municipality_summary = municipality_summary.merge(
        year_values,
        on="BSA",
        how="left",
        validate="one_to_one",
    )

    if "AVG_STDEFF" not in municipality_summary.columns:
        raise ValueError(
            "AVG_STDEFF column not found after merging APHREH outputs. "
            f"Available columns are: {list(municipality_summary.columns)}"
        )

    municipality_summary = municipality_summary.sort_values(
        by="AVG_STDEFF",
        ascending=False,
    ).reset_index(drop=True)

    return municipality_summary


def build_area_summary(municipality_summary: pd.DataFrame) -> pd.DataFrame:
    """
    Summarize APHREH outputs by Agricultural/Industrial area.
    """
    area_summary = (
        municipality_summary
        .groupby("Area")
        .agg(
            n_municipalities=("BSA", "count"),
            mean_index_median=("INDEX_MEDIAN", "mean"),
            median_index_median=("INDEX_MEDIAN", "median"),
            min_index_median=("INDEX_MEDIAN", "min"),
            max_index_median=("INDEX_MEDIAN", "max"),
            mean_avg_stdeff=("AVG_STDEFF", "mean"),
            median_avg_stdeff=("AVG_STDEFF", "median"),
            min_avg_stdeff=("AVG_STDEFF", "min"),
            max_avg_stdeff=("AVG_STDEFF", "max"),
        )
        .reset_index()
    )

    return area_summary


def build_model_summary() -> pd.DataFrame:
    marm_path = APHREH_BEST_PARAM_DIR / "marm_value.txt"
    wmarm_path = APHREH_BEST_PARAM_DIR / "wmarm_value.txt"
    wmarm_csv_path = APHREH_OUTPUT_ROOT / "PLOT/WMARM.csv"

    if not marm_path.exists():
        raise FileNotFoundError(f"Missing file: {marm_path}")

    if not wmarm_path.exists():
        raise FileNotFoundError(f"Missing file: {wmarm_path}")

    marm = read_scalar_txt(marm_path, "MARM")
    wmarm = read_scalar_txt(wmarm_path, "WMARM")

    model_summary = pd.DataFrame(
        [
            {
                "Pilot": PILOT_LABEL,
                "Selected_parameter_folder": PARAMETER_FOLDER,
                "Pollutant": "PM2.5",
                "Outcome": "Respiratory",
                "Exposure_percentile": 75,
                "Lag_days": 0,
                "MARM": marm,
                "WMARM": wmarm,
                "WMARM_csv_exists": wmarm_csv_path.exists(),
                "Interpretation_note": (
                    "Single-combination technical test. "
                    "Do not interpret this as optimized until the full percentile-lag sweep is run."
                ),
            }
        ]
    )

    return model_summary


def load_exposure_thresholds() -> pd.DataFrame:
    path = APHREH_OUTPUT_ROOT / "Years/exposure_thresholds.csv"

    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    thresholds = pd.read_csv(path)
    return thresholds


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    print("=" * 100)
    print("Summarizing APHREH-ADSMap pilot outputs")
    print(f"Pilot: {PILOT_LABEL}")
    print("=" * 100)

    SUMMARY_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    study = load_study_municipalities()
    index_raw, index_cumulated = load_aphreh_results()

    municipality_summary = build_municipality_summary(
        study=study,
        index_raw=index_raw,
        index_cumulated=index_cumulated,
    )

    area_summary = build_area_summary(municipality_summary)
    model_summary = build_model_summary()
    exposure_thresholds = load_exposure_thresholds()

    municipality_summary_path = SUMMARY_OUTPUT_DIR / "aphreh_pilot_municipality_summary.csv"
    area_summary_path = SUMMARY_OUTPUT_DIR / "aphreh_pilot_area_summary.csv"
    model_summary_path = SUMMARY_OUTPUT_DIR / "aphreh_pilot_model_summary.csv"
    thresholds_path = SUMMARY_OUTPUT_DIR / "aphreh_pilot_exposure_thresholds.csv"

    # Use semicolon for project-level readable outputs.
    municipality_summary.to_csv(municipality_summary_path, sep=";", index=False)
    area_summary.to_csv(area_summary_path, sep=";", index=False)
    model_summary.to_csv(model_summary_path, sep=";", index=False)
    exposure_thresholds.to_csv(thresholds_path, sep=";", index=False)

    print("\nGenerated summary files:")
    for path in [
        municipality_summary_path,
        area_summary_path,
        model_summary_path,
        thresholds_path,
    ]:
        print(f"  - {path.relative_to(PROJECT_ROOT)}")

    print("\nModel summary:")
    print(model_summary.to_string(index=False))

    print("\nArea summary:")
    print(area_summary.to_string(index=False))

    print("\nTop 10 municipalities by AVG_STDEFF:")
    print(
        municipality_summary[
            [
                "BSA",
                "Municipality",
                "Area",
                "Province",
                "INDEX_MEDIAN",
                "CI_LOW_MEDIAN",
                "CI_HIGH_MEDIAN",
                "AVG_STDEFF",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )

    print("\nBottom 10 municipalities by AVG_STDEFF:")
    print(
        municipality_summary[
            [
                "BSA",
                "Municipality",
                "Area",
                "Province",
                "INDEX_MEDIAN",
                "CI_LOW_MEDIAN",
                "CI_HIGH_MEDIAN",
                "AVG_STDEFF",
            ]
        ]
        .tail(10)
        .to_string(index=False)
    )

    print("\nDone.")


if __name__ == "__main__":
    main()