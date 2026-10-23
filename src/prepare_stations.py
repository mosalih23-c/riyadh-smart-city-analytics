
from pathlib import Path
import re
import pandas as pd

# Project paths
PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "data" / "raw"
OUTPUT_DIR = PROJECT_DIR / "data" / "processed"

INPUT_FILE = RAW_DIR / "air-quality-stations-in-riyadh-2025.csv"
OUTPUT_FILE = OUTPUT_DIR / "riyadh_air_stations_clean.csv"


def extract_coordinates(value):
    """Extract latitude and longitude from a coordinate string."""
    if pd.isna(value):
        return None, None

    # Supports strings such as:
    # "24.7136, 46.6753"
    # "(24.7136, 46.6753)"
    # and coordinate pairs separated by a semicolon.
    numbers = re.findall(
        r"[-+]?\d+(?:\.\d+)?",
        str(value)
    )

    if len(numbers) < 2:
        return None, None

    first, second = float(numbers[0]), float(numbers[1])

    # Riyadh coordinates should be approximately:
    # latitude 20–28, longitude 40–50.
    # Determine order using plausible geographic ranges.
    if 20 <= first <= 28 and 40 <= second <= 50:
        return first, second

    if 40 <= first <= 50 and 20 <= second <= 28:
        return second, first

    return None, None


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Could not find input file: {INPUT_FILE}\n"
            "Make sure it is inside data/raw/."
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(INPUT_FILE)

    print("Original rows:", len(df))
    print("Original columns:", list(df.columns))

    # Find the coordinate column from known source column names.
    coordinate_candidates = [
        "Geographical coordinates",
        "geo_point_2d",
    ]

    coordinate_column = next(
        (col for col in coordinate_candidates if col in df.columns),
        None,
    )

    if coordinate_column is None:
        raise ValueError(
            "No coordinate column found. "
            "Review the printed column names and update the script."
        )

    # Extract coordinates
    coords = df[coordinate_column].apply(extract_coordinates)
    df["latitude"] = coords.apply(lambda pair: pair[0])
    df["longitude"] = coords.apply(lambda pair: pair[1])

    # Validate Riyadh-area coordinates
    valid = (
        df["latitude"].between(20, 28)
        & df["longitude"].between(40, 50)
    )

    df["coordinates_valid"] = valid

    print("\n--- Coordinate validation ---")
    print("Total stations:", len(df))
    print("Valid coordinates:", int(valid.sum()))
    print("Invalid/missing coordinates:", int((~valid).sum()))

    print("\n--- Station preview ---")
    display_columns = [
        col for col in [
            "Air quality stations",
            "Classification",
            "latitude",
            "longitude",
            "coordinates_valid",
        ]
        if col in df.columns
    ]
    print(df[display_columns].to_string(index=False))

    # Save all rows, including any that need manual review.
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print("\nCleaned station file saved to:")
    print(OUTPUT_FILE)
    print("Original source file was not modified.")


if __name__ == "__main__":
    main()
