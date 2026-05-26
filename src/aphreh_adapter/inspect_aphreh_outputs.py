"""
Inspect APHREH-ADSMap pilot outputs.

This script does not modify any file.
It prints:
    - output folder structure
    - available CSV/TXT files
    - preview of key output tables

Pilot:
    PM2.5 -> Respiratory
"""

from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PILOT_LABEL = "PM25_Respiratory"

OUTPUT_ROOT = (
    PROJECT_ROOT
    / "Dati/output/6-APHREH ADSMap/6.2-Model outputs"
    / PILOT_LABEL
    / "v01"
)

KEY_FILES = [
    "Parametric/P75_L0/index_raw.csv",
    "Parametric/P75_L0/index_formatted.csv",
    "Parametric/P75_L0/index_cumulated_raw.csv",
    "Parametric/P75_L0/index_cumulated_formatted.csv",
    "Parametric/P75_L0/marm_value.txt",
    "Parametric/P75_L0/wmarm_value.txt",
    "MAX_WMARM_P75_L0/index_raw.csv",
    "MAX_WMARM_P75_L0/index_cumulated_raw.csv",
    "PLOT/WMARM.csv",
    "Years/exposure_thresholds.csv",
]


def print_header(title: str) -> None:
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def preview_csv(path: Path) -> None:
    try:
        df = pd.read_csv(path)
        print(f"Shape: {df.shape}")
        print("Columns:")
        print(list(df.columns))
        print("\nHead:")
        print(df.head(10).to_string(index=False))
    except Exception as exc:
        print(f"Could not read CSV: {exc}")


def preview_text(path: Path) -> None:
    try:
        print(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError:
        print(path.read_text(encoding="latin1"))
    except Exception as exc:
        print(f"Could not read text file: {exc}")


def main() -> None:
    print_header("Inspecting APHREH-ADSMap outputs")
    print(f"Output root: {OUTPUT_ROOT.relative_to(PROJECT_ROOT)}")

    if not OUTPUT_ROOT.exists():
        raise FileNotFoundError(f"Output folder not found: {OUTPUT_ROOT}")

    print_header("Available files")
    files = sorted([p for p in OUTPUT_ROOT.rglob("*") if p.is_file()])

    for file in files:
        print(file.relative_to(OUTPUT_ROOT))

    print_header("Key file previews")

    for relative_file in KEY_FILES:
        path = OUTPUT_ROOT / relative_file

        print_header(relative_file)

        if not path.exists():
            print("File not found.")
            continue

        if path.suffix.lower() == ".csv":
            preview_csv(path)
        elif path.suffix.lower() == ".txt":
            preview_text(path)
        else:
            print("Unsupported preview type.")


if __name__ == "__main__":
    main()