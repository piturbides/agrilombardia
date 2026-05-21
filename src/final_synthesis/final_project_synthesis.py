"""
Final project synthesis for the Human Health and Environment Data Science Laboratory project.

Part 5 is not a new environmental-health analysis.
It is a final synthesis layer that compares the previous station-based pipeline
with the newer ModAria-based pipeline and produces compact tables and plots
for final reporting and presentation.

Recommended location:
    src/final_synthesis/final_project_synthesis.py

Run from main.py:
    from src.final_synthesis.final_project_synthesis import main as run_final_synthesis

    if __name__ == "__main__":
        run_final_synthesis()
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# 1. CONFIGURATION AND PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_DIR = PROJECT_ROOT / "Dati" / "output" / "5-Final synthesis" / "5.1-Final project synthesis"
PLOTS_DIR = OUTPUT_DIR / "plots"

STATION_CORRELATION_FILES = {
    "Seasonal": PROJECT_ROOT / "Dati" / "output" / "3-Environmental health integration" / "3.1-Seasonal integration" / "spearman_correlation_summary.csv",
    "Monthly": PROJECT_ROOT / "Dati" / "output" / "3-Environmental health integration" / "3.2-Monthly integration" / "spearman_correlation_summary.csv",
}

MODARIA_CORRELATION_FILES = {
    "Seasonal": PROJECT_ROOT / "Dati" / "output" / "4-Modaria exposure" / "4.3-Modaria environmental health integration" / "spearman_population_weighted_correlation_summary_seasonal.csv",
    "Monthly": PROJECT_ROOT / "Dati" / "output" / "4-Modaria exposure" / "4.3-Modaria environmental health integration" / "spearman_population_weighted_correlation_summary_monthly.csv",
}

STATION_LAG_BEST_FILES = {
    "Monthly": PROJECT_ROOT / "Dati" / "output" / "3-Environmental health integration" / "3.3-Monthly lag analysis" / "monthly_lag_best_lag_summary.csv",
    "Weekly": PROJECT_ROOT / "Dati" / "output" / "3-Environmental health integration" / "3.4-Weekly lag analysis" / "weekly_lag_best_lag_summary.csv",
}

STATION_LAG_FULL_FILES = {
    "Monthly": PROJECT_ROOT / "Dati" / "output" / "3-Environmental health integration" / "3.3-Monthly lag analysis" / "monthly_lag_spearman_summary.csv",
    "Weekly": PROJECT_ROOT / "Dati" / "output" / "3-Environmental health integration" / "3.4-Weekly lag analysis" / "weekly_lag_spearman_summary.csv",
}

MODARIA_LAG_BEST_FILES = {
    "Monthly": PROJECT_ROOT / "Dati" / "output" / "4-Modaria exposure" / "4.4-Modaria monthly and weekly lag analysis" / "modaria_monthly_lag_best_lag_summary.csv",
    "Weekly": PROJECT_ROOT / "Dati" / "output" / "4-Modaria exposure" / "4.4-Modaria monthly and weekly lag analysis" / "modaria_weekly_lag_best_lag_summary.csv",
}

MODARIA_LAG_FULL_FILES = {
    "Monthly": PROJECT_ROOT / "Dati" / "output" / "4-Modaria exposure" / "4.4-Modaria monthly and weekly lag analysis" / "modaria_monthly_lag_spearman_summary.csv",
    "Weekly": PROJECT_ROOT / "Dati" / "output" / "4-Modaria exposure" / "4.4-Modaria monthly and weekly lag analysis" / "modaria_weekly_lag_spearman_summary.csv",
}

GROUP_ORDER = ["Overall", "Industrial", "Agricultural"]
POLLUTANT_ORDER = ["NO2", "PM25"]
OUTCOME_ORDER = ["Respiratory", "Cardiocirculatory"]


# ============================================================
# 2. UTILITY FUNCTIONS
# ============================================================

def ensure_output_dirs() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def read_csv_robust(path: Path) -> Optional[pd.DataFrame]:
    if not path.exists():
        print(f"[WARNING] Missing file: {path}")
        return None

    attempts = [
        {"sep": ";", "encoding": "utf-8-sig"},
        {"sep": ";", "encoding": "latin1"},
        {"sep": ",", "encoding": "utf-8-sig"},
        {"sep": ",", "encoding": "latin1"},
    ]

    last_error = None

    for kwargs in attempts:
        try:
            df = pd.read_csv(path, engine="python", **kwargs)
            df = df.dropna(how="all")
            df.columns = [str(c).strip() for c in df.columns]

            if len(df.columns) > 1:
                return df

        except Exception as exc:
            last_error = exc

    print(f"[ERROR] Could not read file: {path}")
    print(f"        Last error: {last_error}")
    return None


def save_csv(df: pd.DataFrame, filename: str) -> Path:
    path = OUTPUT_DIR / filename
    df.to_csv(path, sep=";", index=False, encoding="utf-8-sig")
    return path


def save_plot(filename: str) -> None:
    path = PLOTS_DIR / filename
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()


def find_column(df: pd.DataFrame, candidates: Iterable[str]) -> Optional[str]:
    if df is None or df.empty:
        return None

    lower_map = {str(c).lower(): c for c in df.columns}

    for candidate in candidates:
        key = candidate.lower()
        if key in lower_map:
            return lower_map[key]

    return None


def to_numeric_safe(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def normalize_pollutant(value: object) -> str:
    text = str(value).upper().replace(".", "").replace("_", "").replace("-", "").replace(" ", "")

    if "NO2" in text:
        return "NO2"

    if "PM25" in text or "PM2,5" in text or "PM2" in text:
        return "PM25"

    return str(value)


def normalize_outcome(value: object) -> str:
    text = str(value).lower()

    if "resp" in text:
        return "Respiratory"

    if "cardio" in text or "circul" in text:
        return "Cardiocirculatory"

    return str(value)


def normalize_group(value: object) -> str:
    text = str(value).strip().lower()

    if "overall" in text:
        return "Overall"

    if "industr" in text:
        return "Industrial"

    if "agric" in text:
        return "Agricultural"

    return str(value).strip()


def direction_label(rho: object) -> str:
    try:
        r = float(rho)
    except Exception:
        return "not available"

    if r > 0:
        return "positive"
    if r < 0:
        return "negative"
    return "zero"


def strength_label(rho: object) -> str:
    try:
        r = abs(float(rho))
    except Exception:
        return "not available"

    if r < 0.10:
        return "very weak"
    if r < 0.30:
        return "weak"
    if r < 0.50:
        return "moderate"
    if r < 0.70:
        return "strong"
    return "very strong"


def significance_label(p_value: object) -> str:
    try:
        p = float(p_value)
    except Exception:
        return "not available"

    if p < 0.05:
        return "statistically significant"

    return "not statistically significant"


def build_interpretation(rho: object, p_value: object) -> str:
    return f"{strength_label(rho)} {direction_label(rho)} association; {significance_label(p_value)}"


def sort_summary_table(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    result = df.copy()

    if "Temporal_scale" in result.columns:
        result["Temporal_order"] = result["Temporal_scale"].map({"Seasonal": 0, "Monthly": 1, "Weekly": 2})

    if "Pipeline" in result.columns:
        result["Pipeline_order"] = result["Pipeline"].map({"Station-based": 0, "ModAria": 1})

    if "Group" in result.columns:
        result["Group_order"] = result["Group"].map({g: i for i, g in enumerate(GROUP_ORDER)})

    if "Pollutant" in result.columns:
        result["Pollutant_order"] = result["Pollutant"].map({p: i for i, p in enumerate(POLLUTANT_ORDER)})

    if "Outcome" in result.columns:
        result["Outcome_order"] = result["Outcome"].map({o: i for i, o in enumerate(OUTCOME_ORDER)})

    sort_cols = [
        c for c in [
            "Temporal_order",
            "Pipeline_order",
            "Group_order",
            "Pollutant_order",
            "Outcome_order",
            "Lag",
            "Best_lag",
        ]
        if c in result.columns
    ]

    if sort_cols:
        result = result.sort_values(sort_cols)

    drop_cols = [
        "Temporal_order",
        "Pipeline_order",
        "Group_order",
        "Pollutant_order",
        "Outcome_order",
    ]

    return result.drop(columns=[c for c in drop_cols if c in result.columns])


def make_short_label(row: pd.Series) -> str:
    return f"{row['Group']}\n{row['Pollutant']} - {row['Outcome']}"


# ============================================================
# 3. STANDARDIZE CORRELATION TABLES
# ============================================================

def standardize_correlation_table(
    df: Optional[pd.DataFrame],
    temporal_scale: str,
    pipeline: str,
) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    group_col = find_column(df, ["Group", "Area_group", "Aggregation"])
    pollutant_col = find_column(df, ["Pollutant", "Pollutant_column", "Exposure", "Exposure_variable"])
    outcome_col = find_column(df, ["Outcome", "Outcome_column", "Health_outcome", "Outcome_variable"])
    rho_col = find_column(df, ["Spearman_rho", "Rho", "rho", "Correlation"])
    p_col = find_column(df, ["p_value", "P_value", "p", "P"])
    n_col = find_column(df, ["N", "n"])
    interpretation_col = find_column(df, ["Interpretation"])

    required = [group_col, pollutant_col, outcome_col, rho_col, p_col]

    if any(col is None for col in required):
        print("[WARNING] Could not standardize correlation table because required columns are missing.")
        print(f"          Temporal scale: {temporal_scale}")
        print(f"          Pipeline: {pipeline}")
        print(f"          Available columns: {list(df.columns)}")
        return pd.DataFrame()

    # IMPORTANT FIX:
    # DataFrame is initialized with df.index so scalar metadata are correctly broadcast.
    out = pd.DataFrame(index=df.index)

    out["Temporal_scale"] = temporal_scale
    out["Pipeline"] = pipeline
    out["Group"] = df[group_col].apply(normalize_group)
    out["Pollutant"] = df[pollutant_col].apply(normalize_pollutant)
    out["Outcome"] = df[outcome_col].apply(normalize_outcome)
    out["Rho"] = to_numeric_safe(df[rho_col])
    out["P_value"] = to_numeric_safe(df[p_col])
    out["N"] = to_numeric_safe(df[n_col]) if n_col else np.nan

    if interpretation_col:
        out["Interpretation"] = df[interpretation_col].astype(str)
    else:
        out["Interpretation"] = [
            build_interpretation(rho, p)
            for rho, p in zip(out["Rho"], out["P_value"])
        ]

    out["Direction"] = out["Rho"].apply(direction_label)
    out["Strength"] = out["Rho"].apply(strength_label)
    out["Significance"] = out["P_value"].apply(significance_label)

    return sort_summary_table(out.reset_index(drop=True))


def load_station_based_correlations() -> pd.DataFrame:
    frames = []

    for temporal_scale, path in STATION_CORRELATION_FILES.items():
        df = read_csv_robust(path)
        standardized = standardize_correlation_table(
            df=df,
            temporal_scale=temporal_scale,
            pipeline="Station-based",
        )

        if not standardized.empty:
            frames.append(standardized)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)


def load_modaria_correlations() -> pd.DataFrame:
    frames = []

    for temporal_scale, path in MODARIA_CORRELATION_FILES.items():
        df = read_csv_robust(path)
        standardized = standardize_correlation_table(
            df=df,
            temporal_scale=temporal_scale,
            pipeline="ModAria",
        )

        if not standardized.empty:
            frames.append(standardized)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)


# ============================================================
# 4. STANDARDIZE LAG TABLES
# ============================================================

def standardize_lag_best_table(
    df: Optional[pd.DataFrame],
    temporal_scale: str,
    lag_unit: str,
    pipeline: str,
) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    group_col = find_column(df, ["Group", "Area_group", "Aggregation"])
    pollutant_col = find_column(df, ["Pollutant", "Pollutant_column", "Exposure", "Exposure_variable"])
    outcome_col = find_column(df, ["Outcome", "Outcome_column", "Health_outcome", "Outcome_variable"])

    best_lag_col = find_column(
        df,
        [
            f"Best_lag_by_positive_rho_{lag_unit}",
            f"Best_lag_by_abs_rho_{lag_unit}",
            f"Best_lag_{lag_unit}",
            "Best_lag_months",
            "Best_lag_weeks",
            "Best_lag",
        ],
    )

    best_rho_col = find_column(
        df,
        [
            "Best_positive_Spearman_rho",
            "Best_abs_Spearman_rho",
            "Best_Spearman_rho",
            "Best_Rho",
            "Spearman_rho",
            "Rho",
        ],
    )

    best_p_col = find_column(
        df,
        [
            "Best_positive_p_value",
            "Best_abs_p_value",
            "Best_p_value",
            "Best_P_value",
            "p_value",
            "P_value",
        ],
    )

    n_col = find_column(df, ["N_at_best_positive_lag", "N_at_best_abs_lag", "N_at_best_lag", "N"])

    lag0_rho_col = find_column(df, ["Lag0_Spearman_rho", "Lag0_Rho"])
    lag0_p_col = find_column(df, ["Lag0_p_value", "Lag0_P_value"])
    lag0_best_col = find_column(df, ["Lag0_is_best_positive_rho", "Lag0_is_best_abs_rho", "Lag0_is_best"])
    interpretation_col = find_column(df, ["Interpretation"])

    required = [group_col, pollutant_col, outcome_col, best_lag_col, best_rho_col, best_p_col]

    if any(col is None for col in required):
        print("[WARNING] Could not standardize best-lag table because required columns are missing.")
        print(f"          Temporal scale: {temporal_scale}")
        print(f"          Pipeline: {pipeline}")
        print(f"          Available columns: {list(df.columns)}")
        return pd.DataFrame()

    # IMPORTANT FIX:
    # DataFrame is initialized with df.index so scalar metadata are correctly broadcast.
    out = pd.DataFrame(index=df.index)

    out["Temporal_scale"] = temporal_scale
    out["Lag_unit"] = lag_unit
    out["Pipeline"] = pipeline
    out["Group"] = df[group_col].apply(normalize_group)
    out["Pollutant"] = df[pollutant_col].apply(normalize_pollutant)
    out["Outcome"] = df[outcome_col].apply(normalize_outcome)
    out["Best_lag"] = to_numeric_safe(df[best_lag_col])
    out["Best_Rho"] = to_numeric_safe(df[best_rho_col])
    out["Best_P_value"] = to_numeric_safe(df[best_p_col])
    out["N_at_best_lag"] = to_numeric_safe(df[n_col]) if n_col else np.nan

    out["Lag0_Rho"] = to_numeric_safe(df[lag0_rho_col]) if lag0_rho_col else np.nan
    out["Lag0_P_value"] = to_numeric_safe(df[lag0_p_col]) if lag0_p_col else np.nan

    if lag0_best_col:
        out["Lag0_is_best"] = (
            df[lag0_best_col]
            .astype(str)
            .str.lower()
            .isin(["true", "1", "yes", "y"])
        )
    else:
        out["Lag0_is_best"] = out["Best_lag"].eq(0)

    if interpretation_col:
        out["Interpretation"] = df[interpretation_col].astype(str)
    else:
        out["Interpretation"] = [
            build_interpretation(rho, p)
            for rho, p in zip(out["Best_Rho"], out["Best_P_value"])
        ]

    return sort_summary_table(out.reset_index(drop=True))


def standardize_lag_full_table(
    df: Optional[pd.DataFrame],
    temporal_scale: str,
    lag_unit: str,
    pipeline: str,
) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    group_col = find_column(df, ["Group", "Area_group", "Aggregation"])
    pollutant_col = find_column(df, ["Pollutant", "Pollutant_column", "Exposure", "Exposure_variable"])
    outcome_col = find_column(df, ["Outcome", "Outcome_column", "Health_outcome", "Outcome_variable"])
    lag_col = find_column(df, [f"Lag_{lag_unit}", "Lag_months", "Lag_weeks", "Lag"])
    rho_col = find_column(df, ["Spearman_rho", "Rho", "rho", "Correlation"])
    p_col = find_column(df, ["p_value", "P_value", "p", "P"])
    n_col = find_column(df, ["N", "n"])
    interpretation_col = find_column(df, ["Interpretation"])

    required = [group_col, pollutant_col, outcome_col, lag_col, rho_col, p_col]

    if any(col is None for col in required):
        print("[WARNING] Could not standardize full lag table because required columns are missing.")
        print(f"          Temporal scale: {temporal_scale}")
        print(f"          Pipeline: {pipeline}")
        print(f"          Available columns: {list(df.columns)}")
        return pd.DataFrame()

    # IMPORTANT FIX:
    # DataFrame is initialized with df.index so scalar metadata are correctly broadcast.
    out = pd.DataFrame(index=df.index)

    out["Temporal_scale"] = temporal_scale
    out["Lag_unit"] = lag_unit
    out["Pipeline"] = pipeline
    out["Group"] = df[group_col].apply(normalize_group)
    out["Pollutant"] = df[pollutant_col].apply(normalize_pollutant)
    out["Outcome"] = df[outcome_col].apply(normalize_outcome)
    out["Lag"] = to_numeric_safe(df[lag_col])
    out["Rho"] = to_numeric_safe(df[rho_col])
    out["P_value"] = to_numeric_safe(df[p_col])
    out["N"] = to_numeric_safe(df[n_col]) if n_col else np.nan

    if interpretation_col:
        out["Interpretation"] = df[interpretation_col].astype(str)
    else:
        out["Interpretation"] = [
            build_interpretation(rho, p)
            for rho, p in zip(out["Rho"], out["P_value"])
        ]

    return sort_summary_table(out.reset_index(drop=True))


def load_lag_summaries() -> Tuple[pd.DataFrame, pd.DataFrame]:
    best_frames = []
    full_frames = []

    for temporal_scale, path in STATION_LAG_BEST_FILES.items():
        lag_unit = "months" if temporal_scale == "Monthly" else "weeks"
        df = read_csv_robust(path)
        standardized = standardize_lag_best_table(df, temporal_scale, lag_unit, "Station-based")

        if not standardized.empty:
            best_frames.append(standardized)

    for temporal_scale, path in MODARIA_LAG_BEST_FILES.items():
        lag_unit = "months" if temporal_scale == "Monthly" else "weeks"
        df = read_csv_robust(path)
        standardized = standardize_lag_best_table(df, temporal_scale, lag_unit, "ModAria")

        if not standardized.empty:
            best_frames.append(standardized)

    for temporal_scale, path in STATION_LAG_FULL_FILES.items():
        lag_unit = "months" if temporal_scale == "Monthly" else "weeks"
        df = read_csv_robust(path)
        standardized = standardize_lag_full_table(df, temporal_scale, lag_unit, "Station-based")

        if not standardized.empty:
            full_frames.append(standardized)

    for temporal_scale, path in MODARIA_LAG_FULL_FILES.items():
        lag_unit = "months" if temporal_scale == "Monthly" else "weeks"
        df = read_csv_robust(path)
        standardized = standardize_lag_full_table(df, temporal_scale, lag_unit, "ModAria")

        if not standardized.empty:
            full_frames.append(standardized)

    best = pd.concat(best_frames, ignore_index=True) if best_frames else pd.DataFrame()
    full = pd.concat(full_frames, ignore_index=True) if full_frames else pd.DataFrame()

    return best, full


# ============================================================
# 5. BUILD COMPARISON TABLES
# ============================================================

def build_correlation_comparison(corr: pd.DataFrame) -> pd.DataFrame:
    if corr.empty:
        return pd.DataFrame()

    required_cols = ["Temporal_scale", "Pipeline", "Group", "Pollutant", "Outcome", "Rho", "P_value", "N"]

    missing = [c for c in required_cols if c not in corr.columns]
    if missing:
        print(f"[WARNING] Correlation comparison missing columns: {missing}")
        return pd.DataFrame()

    key_cols = ["Temporal_scale", "Group", "Pollutant", "Outcome"]

    station = corr[corr["Pipeline"] == "Station-based"].copy()
    modaria = corr[corr["Pipeline"] == "ModAria"].copy()

    if station.empty or modaria.empty:
        print("[WARNING] Correlation comparison cannot be created because one pipeline is missing.")
        print(f"          Station rows: {len(station)}")
        print(f"          ModAria rows: {len(modaria)}")
        return pd.DataFrame()

    station = station.rename(
        columns={
            "Rho": "Station_Rho",
            "P_value": "Station_P_value",
            "N": "Station_N",
            "Interpretation": "Station_Interpretation",
            "Direction": "Station_Direction",
            "Strength": "Station_Strength",
            "Significance": "Station_Significance",
        }
    )

    modaria = modaria.rename(
        columns={
            "Rho": "ModAria_Rho",
            "P_value": "ModAria_P_value",
            "N": "ModAria_N",
            "Interpretation": "ModAria_Interpretation",
            "Direction": "ModAria_Direction",
            "Strength": "ModAria_Strength",
            "Significance": "ModAria_Significance",
        }
    )

    keep_station = key_cols + [
        "Station_Rho",
        "Station_P_value",
        "Station_N",
        "Station_Direction",
        "Station_Strength",
        "Station_Significance",
        "Station_Interpretation",
    ]

    keep_modaria = key_cols + [
        "ModAria_Rho",
        "ModAria_P_value",
        "ModAria_N",
        "ModAria_Direction",
        "ModAria_Strength",
        "ModAria_Significance",
        "ModAria_Interpretation",
    ]

    comparison = pd.merge(
        station[keep_station],
        modaria[keep_modaria],
        on=key_cols,
        how="outer",
    )

    comparison["Delta_Rho_ModAria_minus_Station"] = comparison["ModAria_Rho"] - comparison["Station_Rho"]

    def direction_agreement(row: pd.Series) -> str:
        s = row.get("Station_Rho")
        m = row.get("ModAria_Rho")

        if pd.isna(s) or pd.isna(m):
            return "not available"

        if s == 0 or m == 0:
            return "one zero correlation"

        if np.sign(s) == np.sign(m):
            return "same direction"

        return "opposite direction"

    def magnitude_change(row: pd.Series) -> str:
        s = row.get("Station_Rho")
        m = row.get("ModAria_Rho")

        if pd.isna(s) or pd.isna(m):
            return "not available"

        diff = abs(m) - abs(s)

        if diff > 0.05:
            return "stronger in ModAria"

        if diff < -0.05:
            return "weaker in ModAria"

        return "similar magnitude"

    def final_interpretation(row: pd.Series) -> str:
        direction = direction_agreement(row)
        change = magnitude_change(row)

        if direction == "same direction" and change == "similar magnitude":
            return "Robust pattern with similar direction and magnitude across exposure frameworks."

        if direction == "same direction" and change == "stronger in ModAria":
            return "Same direction, strengthened by the ModAria exposure reconstruction."

        if direction == "same direction" and change == "weaker in ModAria":
            return "Same direction, but weaker after ModAria exposure reconstruction."

        if direction == "opposite direction":
            return "Different direction across exposure frameworks; interpret with caution."

        return "Comparison incomplete because one pipeline result is missing."

    comparison["Direction_agreement"] = comparison.apply(direction_agreement, axis=1)
    comparison["Magnitude_change"] = comparison.apply(magnitude_change, axis=1)
    comparison["Final_interpretation"] = comparison.apply(final_interpretation, axis=1)

    return sort_summary_table(comparison)


def build_lag_comparison(best_lags: pd.DataFrame) -> pd.DataFrame:
    if best_lags.empty:
        return pd.DataFrame()

    required_cols = [
        "Temporal_scale",
        "Lag_unit",
        "Pipeline",
        "Group",
        "Pollutant",
        "Outcome",
        "Best_lag",
        "Best_Rho",
        "Best_P_value",
    ]

    missing = [c for c in required_cols if c not in best_lags.columns]
    if missing:
        print(f"[WARNING] Lag comparison missing columns: {missing}")
        return pd.DataFrame()

    key_cols = ["Temporal_scale", "Group", "Pollutant", "Outcome"]

    station = best_lags[best_lags["Pipeline"] == "Station-based"].copy()
    modaria = best_lags[best_lags["Pipeline"] == "ModAria"].copy()

    if station.empty or modaria.empty:
        print("[WARNING] Lag comparison cannot be created because one pipeline is missing.")
        print(f"          Station rows: {len(station)}")
        print(f"          ModAria rows: {len(modaria)}")
        return pd.DataFrame()

    station = station.rename(
        columns={
            "Lag_unit": "Station_Lag_unit",
            "Best_lag": "Station_Best_lag",
            "Best_Rho": "Station_Best_Rho",
            "Best_P_value": "Station_Best_P_value",
            "N_at_best_lag": "Station_N_at_best_lag",
            "Lag0_Rho": "Station_Lag0_Rho",
            "Lag0_P_value": "Station_Lag0_P_value",
            "Lag0_is_best": "Station_Lag0_is_best",
            "Interpretation": "Station_Interpretation",
        }
    )

    modaria = modaria.rename(
        columns={
            "Lag_unit": "ModAria_Lag_unit",
            "Best_lag": "ModAria_Best_lag",
            "Best_Rho": "ModAria_Best_Rho",
            "Best_P_value": "ModAria_Best_P_value",
            "N_at_best_lag": "ModAria_N_at_best_lag",
            "Lag0_Rho": "ModAria_Lag0_Rho",
            "Lag0_P_value": "ModAria_Lag0_P_value",
            "Lag0_is_best": "ModAria_Lag0_is_best",
            "Interpretation": "ModAria_Interpretation",
        }
    )

    keep_station = key_cols + [
        "Station_Lag_unit",
        "Station_Best_lag",
        "Station_Best_Rho",
        "Station_Best_P_value",
        "Station_N_at_best_lag",
        "Station_Lag0_Rho",
        "Station_Lag0_P_value",
        "Station_Lag0_is_best",
        "Station_Interpretation",
    ]

    keep_modaria = key_cols + [
        "ModAria_Lag_unit",
        "ModAria_Best_lag",
        "ModAria_Best_Rho",
        "ModAria_Best_P_value",
        "ModAria_N_at_best_lag",
        "ModAria_Lag0_Rho",
        "ModAria_Lag0_P_value",
        "ModAria_Lag0_is_best",
        "ModAria_Interpretation",
    ]

    comparison = pd.merge(
        station[keep_station],
        modaria[keep_modaria],
        on=key_cols,
        how="outer",
    )

    comparison["Delta_best_lag_ModAria_minus_Station"] = comparison["ModAria_Best_lag"] - comparison["Station_Best_lag"]
    comparison["Delta_best_rho_ModAria_minus_Station"] = comparison["ModAria_Best_Rho"] - comparison["Station_Best_Rho"]

    def lag_agreement(row: pd.Series) -> str:
        s = row.get("Station_Best_lag")
        m = row.get("ModAria_Best_lag")

        if pd.isna(s) or pd.isna(m):
            return "not available"

        if s == m:
            return "same best lag"

        if abs(s - m) <= 1:
            return "similar short-lag structure"

        return "different lag structure"

    def final_interpretation(row: pd.Series) -> str:
        agreement = lag_agreement(row)

        if agreement == "same best lag":
            return "Best lag is consistent across station-based and ModAria exposure frameworks."

        if agreement == "similar short-lag structure":
            return "Best lag differs slightly but remains within a similar short-lag window."

        if agreement == "different lag structure":
            return "Best lag differs across exposure frameworks; interpret temporal delay cautiously."

        return "Comparison incomplete because one pipeline result is missing."

    comparison["Best_lag_agreement"] = comparison.apply(lag_agreement, axis=1)
    comparison["Final_interpretation"] = comparison.apply(final_interpretation, axis=1)

    return sort_summary_table(comparison)


# ============================================================
# 6. QUALITATIVE AND QUANTITATIVE SUMMARY TABLES
# ============================================================

def build_methodological_comparison_table() -> pd.DataFrame:
    rows = [
        {
            "Aspect": "Exposure spatial representation",
            "Station_based_pipeline": "One monitoring station per pollutant and study area.",
            "ModAria_based_pipeline": "Municipality-level exposure estimates for all selected municipalities.",
            "Final_interpretation": "ModAria improves spatial coherence with the health-event aggregation.",
        },
        {
            "Aspect": "Exposure-health spatial coherence",
            "Station_based_pipeline": "Health data are aggregated over many municipalities, while exposure is represented by one station.",
            "ModAria_based_pipeline": "Both health and exposure are aligned to the same selected municipality sets.",
            "Final_interpretation": "ModAria reduces the spatial mismatch of the first pipeline.",
        },
        {
            "Aspect": "Industrial vs agricultural comparison",
            "Station_based_pipeline": "Useful first comparison, but strongly dependent on station representativeness.",
            "ModAria_based_pipeline": "More coherent area-level comparison between industrial and agricultural municipalities.",
            "Final_interpretation": "Final interpretation should rely mainly on ModAria, using station results as exploratory support.",
        },
        {
            "Aspect": "NO2 interpretation",
            "Station_based_pipeline": "NO2 reflects local traffic/industrial signal only at selected stations.",
            "ModAria_based_pipeline": "NO2 is reconstructed over all selected municipalities.",
            "Final_interpretation": "The ModAria framework gives stronger evidence for the industrial NO2 contrast.",
        },
        {
            "Aspect": "PM2.5 interpretation",
            "Station_based_pipeline": "PM2.5 may appear station-specific and sensitive to local measurement context.",
            "ModAria_based_pipeline": "PM2.5 shows broader regional/shared behavior across the selected territory.",
            "Final_interpretation": "PM2.5 should be interpreted as a regional pollutant rather than a simple industrial/agricultural discriminator.",
        },
        {
            "Aspect": "Temporal lag interpretation",
            "Station_based_pipeline": "Exploratory lag structure based on station exposure.",
            "ModAria_based_pipeline": "Lag structure based on population-weighted area exposure.",
            "Final_interpretation": "Lag results are descriptive and useful for temporal coherence, not causal inference.",
        },
        {
            "Aspect": "Main limitation",
            "Station_based_pipeline": "Potential exposure misclassification due to station representativeness.",
            "ModAria_based_pipeline": "Modelled exposure may smooth local peaks and depends on ModAria reconstruction quality.",
            "Final_interpretation": "The two pipelines are complementary and should be compared rather than treated as interchangeable.",
        },
        {
            "Aspect": "Final role in project",
            "Station_based_pipeline": "Exploratory baseline analysis.",
            "ModAria_based_pipeline": "Final spatially coherent exposure-health analysis.",
            "Final_interpretation": "The project conclusions are stronger when robust patterns are consistent across both pipelines.",
        },
    ]

    return pd.DataFrame(rows)


def build_robust_conclusions_table() -> pd.DataFrame:
    rows = [
        {
            "Conclusion": "The two study areas differ in environmental-health profile, but not in a simple pollutant-independent way.",
            "Supported_by_station_pipeline": "Partly",
            "Supported_by_ModAria_pipeline": "Yes",
            "Strength": "Strong",
            "Final_interpretation": "Differences are pollutant-specific, outcome-specific and scale-dependent.",
        },
        {
            "Conclusion": "NO2 is the clearest pollutant for characterizing the industrial/urban exposure profile.",
            "Supported_by_station_pipeline": "Weakly",
            "Supported_by_ModAria_pipeline": "Yes",
            "Strength": "Strengthened by ModAria",
            "Final_interpretation": "The ModAria framework makes the industrial NO2 contrast much clearer.",
        },
        {
            "Conclusion": "PM2.5 behaves more as a shared/regional pollutant than as a simple area discriminator.",
            "Supported_by_station_pipeline": "Partly",
            "Supported_by_ModAria_pipeline": "Yes",
            "Strength": "Moderate",
            "Final_interpretation": "PM2.5 should be interpreted with attention to regional background and secondary formation.",
        },
        {
            "Conclusion": "Respiratory outcomes show the most temporally coherent environmental-health associations.",
            "Supported_by_station_pipeline": "Yes",
            "Supported_by_ModAria_pipeline": "Yes",
            "Strength": "Strong",
            "Final_interpretation": "Respiratory rates are the most consistent health outcome across the project.",
        },
        {
            "Conclusion": "Cardiocirculatory associations are present but more heterogeneous.",
            "Supported_by_station_pipeline": "Partly",
            "Supported_by_ModAria_pipeline": "Partly",
            "Strength": "Moderate",
            "Final_interpretation": "Cardiocirculatory results should be interpreted more cautiously than respiratory ones.",
        },
        {
            "Conclusion": "Monthly lag analysis mainly supports same-month association structure.",
            "Supported_by_station_pipeline": "Yes",
            "Supported_by_ModAria_pipeline": "Yes",
            "Strength": "Strong",
            "Final_interpretation": "The monthly signal does not strongly support delayed multi-month effects.",
        },
        {
            "Conclusion": "Weekly lag analysis suggests short-lag temporal structure.",
            "Supported_by_station_pipeline": "Partly",
            "Supported_by_ModAria_pipeline": "Yes",
            "Strength": "Moderate",
            "Final_interpretation": "Weekly results are useful as a more granular temporal sensitivity check.",
        },
        {
            "Conclusion": "The project remains exploratory and ecological.",
            "Supported_by_station_pipeline": "Yes",
            "Supported_by_ModAria_pipeline": "Yes",
            "Strength": "Important limitation",
            "Final_interpretation": "Results describe population-level associations and should not be interpreted as individual-level causality.",
        },
    ]

    return pd.DataFrame(rows)


def build_quantitative_synthesis_summary(
    corr: pd.DataFrame,
    lag_best: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    if not corr.empty:
        for pipeline in ["Station-based", "ModAria"]:
            for scale in ["Seasonal", "Monthly"]:
                sub = corr[(corr["Pipeline"] == pipeline) & (corr["Temporal_scale"] == scale)]

                if sub.empty:
                    continue

                positive = (sub["Rho"] > 0).sum()
                significant = (sub["P_value"] < 0.05).sum()
                total = len(sub)
                mean_abs_rho = sub["Rho"].abs().mean()

                rows.append(
                    {
                        "Section": "Correlation summary",
                        "Pipeline": pipeline,
                        "Temporal_scale": scale,
                        "Metric": "positive/significant correlations",
                        "Value": f"{positive}/{total} positive; {significant}/{total} significant; mean |rho| = {mean_abs_rho:.3f}",
                        "Interpretation": "Descriptive count of monotonic environmental-health associations.",
                    }
                )

    if not lag_best.empty:
        for pipeline in ["Station-based", "ModAria"]:
            for scale in ["Monthly", "Weekly"]:
                sub = lag_best[(lag_best["Pipeline"] == pipeline) & (lag_best["Temporal_scale"] == scale)]

                if sub.empty:
                    continue

                lag0_best = sub["Lag0_is_best"].sum()
                total = len(sub)
                median_best_lag = sub["Best_lag"].median()

                rows.append(
                    {
                        "Section": "Lag summary",
                        "Pipeline": pipeline,
                        "Temporal_scale": scale,
                        "Metric": "lag 0 dominance",
                        "Value": f"{lag0_best}/{total} lag-0 best; median best lag = {median_best_lag}",
                        "Interpretation": "Monthly lag 0 dominance suggests same-period structure; weekly results describe short-lag sensitivity.",
                    }
                )

    return pd.DataFrame(rows)


def build_final_project_summary() -> pd.DataFrame:
    rows = [
        {
            "Item": "Output folder",
            "Value": str(OUTPUT_DIR),
        },
        {
            "Item": "Main interpretation",
            "Value": "ModAria improves spatial exposure coherence and strengthens the final interpretation of the industrial-versus-agricultural comparison.",
        },
        {
            "Item": "Role of station-based pipeline",
            "Value": "Exploratory baseline based on selected monitoring stations.",
        },
        {
            "Item": "Role of ModAria pipeline",
            "Value": "Final spatially coherent exposure reconstruction based on municipality-level population-weighted pollutant estimates.",
        },
        {
            "Item": "Main robust result",
            "Value": "NO2 is the clearest pollutant for the industrial contrast, while PM2.5 behaves more as a regional/shared pollutant.",
        },
        {
            "Item": "Main limitation",
            "Value": "The project remains exploratory and ecological; correlations and lag patterns should not be interpreted as individual-level causal effects.",
        },
    ]

    return pd.DataFrame(rows)


# ============================================================
# 7. PLOTS
# ============================================================

def plot_pipeline_overview() -> None:
    labels = [
        "Station data\nPart 1",
        "Health rates\nPart 2",
        "Station-based\nintegration\nPart 3",
        "ModAria exposure\nPart 4.1-4.2",
        "ModAria integration\nPart 4.3",
        "ModAria lags\nPart 4.4",
        "Final synthesis\nPart 5",
    ]

    x = np.arange(len(labels))
    y = np.zeros(len(labels))

    plt.figure(figsize=(15, 3))

    for i, label in enumerate(labels):
        plt.text(
            x[i],
            y[i],
            label,
            ha="center",
            va="center",
            bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="black"),
        )

        if i < len(labels) - 1:
            plt.annotate(
                "",
                xy=(x[i + 1] - 0.35, y[i]),
                xytext=(x[i] + 0.35, y[i]),
                arrowprops=dict(arrowstyle="->"),
            )

    plt.axis("off")
    plt.title("Final project pipeline overview")
    save_plot("final_project_pipeline_overview.png")


def plot_correlation_comparison(corr_comparison: pd.DataFrame, temporal_scale: str) -> None:
    if corr_comparison.empty:
        return

    sub = corr_comparison[corr_comparison["Temporal_scale"] == temporal_scale].copy()

    if sub.empty:
        return

    sub["Label"] = sub.apply(make_short_label, axis=1)
    x = np.arange(len(sub))
    width = 0.35

    plt.figure(figsize=(max(12, len(sub) * 0.7), 5))
    plt.bar(x - width / 2, sub["Station_Rho"], width, label="Station-based")
    plt.bar(x + width / 2, sub["ModAria_Rho"], width, label="ModAria")
    plt.axhline(0, linestyle="--", linewidth=1)
    plt.xticks(x, sub["Label"], rotation=75, ha="right")
    plt.ylabel("Spearman rho")
    plt.title(f"{temporal_scale} station-based vs ModAria correlations")
    plt.legend()

    save_plot(f"final_{temporal_scale.lower()}_station_vs_modaria_correlations.png")


def plot_correlation_delta(corr_comparison: pd.DataFrame, temporal_scale: str) -> None:
    if corr_comparison.empty:
        return

    sub = corr_comparison[corr_comparison["Temporal_scale"] == temporal_scale].copy()

    if sub.empty:
        return

    sub["Label"] = sub.apply(make_short_label, axis=1)
    x = np.arange(len(sub))

    plt.figure(figsize=(max(12, len(sub) * 0.7), 5))
    plt.bar(x, sub["Delta_Rho_ModAria_minus_Station"])
    plt.axhline(0, linestyle="--", linewidth=1)
    plt.xticks(x, sub["Label"], rotation=75, ha="right")
    plt.ylabel("Delta rho: ModAria - station-based")
    plt.title(f"{temporal_scale} change in correlation after ModAria exposure reconstruction")

    save_plot(f"final_{temporal_scale.lower()}_delta_rho_modaria_minus_station.png")


def plot_lag_best_comparison(lag_comparison: pd.DataFrame, temporal_scale: str) -> None:
    if lag_comparison.empty:
        return

    sub = lag_comparison[lag_comparison["Temporal_scale"] == temporal_scale].copy()

    if sub.empty:
        return

    sub["Label"] = sub.apply(make_short_label, axis=1)
    x = np.arange(len(sub))
    width = 0.35

    plt.figure(figsize=(max(12, len(sub) * 0.7), 5))
    plt.bar(x - width / 2, sub["Station_Best_lag"], width, label="Station-based")
    plt.bar(x + width / 2, sub["ModAria_Best_lag"], width, label="ModAria")
    plt.xticks(x, sub["Label"], rotation=75, ha="right")
    plt.ylabel(f"Best lag ({'months' if temporal_scale == 'Monthly' else 'weeks'})")
    plt.title(f"{temporal_scale} best lag comparison")
    plt.legend()

    save_plot(f"final_{temporal_scale.lower()}_best_lag_station_vs_modaria.png")


def plot_lag_rho_overall(lag_full: pd.DataFrame, temporal_scale: str) -> None:
    if lag_full.empty:
        return

    sub = lag_full[
        (lag_full["Temporal_scale"] == temporal_scale)
        & (lag_full["Group"] == "Overall")
    ].copy()

    if sub.empty:
        return

    plt.figure(figsize=(10, 6))

    for pipeline in ["Station-based", "ModAria"]:
        for pollutant in POLLUTANT_ORDER:
            for outcome in OUTCOME_ORDER:
                line = sub[
                    (sub["Pipeline"] == pipeline)
                    & (sub["Pollutant"] == pollutant)
                    & (sub["Outcome"] == outcome)
                ].sort_values("Lag")

                if line.empty:
                    continue

                label = f"{pipeline} | {pollutant} | {outcome}"
                plt.plot(line["Lag"], line["Rho"], marker="o", label=label)

    plt.axhline(0, linestyle="--", linewidth=1)
    plt.xlabel(f"Lag ({'months' if temporal_scale == 'Monthly' else 'weeks'})")
    plt.ylabel("Spearman rho")
    plt.title(f"{temporal_scale} overall rho vs lag: station-based vs ModAria")
    plt.legend(fontsize=8)

    save_plot(f"final_{temporal_scale.lower()}_overall_rho_vs_lag_station_vs_modaria.png")


def plot_evidence_strength_heatmap() -> None:
    rows = [
        "NO2 industrial contrast",
        "PM2.5 regional/shared behavior",
        "Respiratory temporal coherence",
        "Cardiocirculatory industrial relevance",
        "Monthly lag 0 dominance",
        "Weekly short-lag signal",
    ]

    cols = ["Station-based", "ModAria", "Final confidence"]

    values = np.array(
        [
            [1, 3, 3],
            [1, 3, 2],
            [3, 3, 3],
            [2, 3, 2],
            [3, 3, 3],
            [2, 3, 2],
        ],
        dtype=float,
    )

    plt.figure(figsize=(9, 5))
    plt.imshow(values)
    plt.xticks(np.arange(len(cols)), cols, rotation=30, ha="right")
    plt.yticks(np.arange(len(rows)), rows)
    plt.colorbar(label="Qualitative evidence score")
    plt.title("Final qualitative evidence strength summary")

    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            plt.text(j, i, int(values[i, j]), ha="center", va="center")

    save_plot("final_evidence_strength_heatmap.png")


def generate_all_plots(
    corr_comparison: pd.DataFrame,
    lag_comparison: pd.DataFrame,
    lag_full: pd.DataFrame,
) -> None:
    plot_pipeline_overview()

    for scale in ["Seasonal", "Monthly"]:
        plot_correlation_comparison(corr_comparison, scale)
        plot_correlation_delta(corr_comparison, scale)

    for scale in ["Monthly", "Weekly"]:
        plot_lag_best_comparison(lag_comparison, scale)
        plot_lag_rho_overall(lag_full, scale)

    plot_evidence_strength_heatmap()


# ============================================================
# 8. MAIN
# ============================================================

def main() -> None:
    ensure_output_dirs()

    print("\n========================================")
    print("PART 5 - FINAL PROJECT SYNTHESIS")
    print("Station-based vs ModAria comparison")
    print("========================================\n")

    print("Loading station-based correlation summaries...")
    station_corr = load_station_based_correlations()

    print("Loading ModAria correlation summaries...")
    modaria_corr = load_modaria_correlations()

    corr_frames = [
        df for df in [station_corr, modaria_corr]
        if df is not None and not df.empty
    ]

    all_corr = pd.concat(corr_frames, ignore_index=True) if corr_frames else pd.DataFrame()

    if not all_corr.empty:
        all_corr = sort_summary_table(all_corr)
        save_csv(all_corr, "final_standardized_correlation_results.csv")
        print(f"Standardized correlation results: {len(all_corr)} rows")
        print(all_corr[["Temporal_scale", "Pipeline"]].drop_duplicates().to_string(index=False))
    else:
        print("[WARNING] No standardized correlation results were created.")

    print("Building station-based vs ModAria correlation comparison...")
    corr_comparison = build_correlation_comparison(all_corr)

    if not corr_comparison.empty:
        save_csv(corr_comparison, "final_station_vs_modaria_correlation_comparison.csv")
        print(f"Correlation comparison: {len(corr_comparison)} rows")
    else:
        print("[WARNING] Correlation comparison could not be created.")

    print("Loading lag summaries...")
    lag_best, lag_full = load_lag_summaries()

    if not lag_best.empty:
        lag_best = sort_summary_table(lag_best)
        save_csv(lag_best, "final_standardized_lag_best_results.csv")
        print(f"Standardized best-lag results: {len(lag_best)} rows")
        print(lag_best[["Temporal_scale", "Lag_unit", "Pipeline"]].drop_duplicates().to_string(index=False))
    else:
        print("[WARNING] No standardized best-lag results were created.")

    if not lag_full.empty:
        lag_full = sort_summary_table(lag_full)
        save_csv(lag_full, "final_standardized_lag_full_results.csv")
        print(f"Standardized full lag results: {len(lag_full)} rows")
        print(lag_full[["Temporal_scale", "Lag_unit", "Pipeline"]].drop_duplicates().to_string(index=False))
    else:
        print("[WARNING] No standardized full lag results were created.")

    print("Building station-based vs ModAria lag comparison...")
    lag_comparison = build_lag_comparison(lag_best)

    if not lag_comparison.empty:
        save_csv(lag_comparison, "final_station_vs_modaria_lag_comparison.csv")
        print(f"Lag comparison: {len(lag_comparison)} rows")
    else:
        print("[WARNING] Lag comparison could not be created.")

    print("Building qualitative methodological comparison table...")
    methodological_comparison = build_methodological_comparison_table()
    save_csv(methodological_comparison, "final_methodological_comparison_station_vs_modaria.csv")

    print("Building robust conclusions table...")
    robust_conclusions = build_robust_conclusions_table()
    save_csv(robust_conclusions, "final_robust_conclusions_summary.csv")

    print("Building compact quantitative synthesis summary...")
    quantitative_summary = build_quantitative_synthesis_summary(all_corr, lag_best)
    save_csv(quantitative_summary, "final_quantitative_synthesis_summary.csv")

    print("Building final project synthesis summary...")
    final_summary = build_final_project_summary()
    save_csv(final_summary, "final_project_synthesis_summary.csv")

    print("Generating final synthesis plots...")
    generate_all_plots(
        corr_comparison=corr_comparison,
        lag_comparison=lag_comparison,
        lag_full=lag_full,
    )

    print("\n========================================")
    print("FINAL PROJECT SYNTHESIS COMPLETED")
    print("========================================")
    print(f"Results saved in: {OUTPUT_DIR}")
    print(f"Plots saved in:   {PLOTS_DIR}")

    if corr_comparison.empty or lag_comparison.empty:
        print("\n[CHECK REQUIRED]")
        print("Some comparison tables were not created. Check the warnings above.")
    else:
        print("\n[OK]")
        print("Station-based vs ModAria comparison tables were successfully created.")


if __name__ == "__main__":
    main()