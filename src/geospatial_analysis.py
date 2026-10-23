
from pathlib import Path

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "riyadh_air_stations_clean.csv"
)

OUTPUT_DIR = BASE_DIR / "data" / "processed"
REPORTS_DIR = BASE_DIR / "reports"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def main():
    print("=" * 55)
    print("RIYADH AIR QUALITY - GEOSPATIAL ANALYSIS")
    print("=" * 55)

    # 1. Load station data
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Station file not found: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    print(f"\nInput rows: {len(df)}")
    print("Available columns:")
    print(df.columns.tolist())

    # 2. Identify coordinate columns
    lat_candidates = ["latitude", "lat"]
    lon_candidates = ["longitude", "lon", "lng"]

    lat_col = next(
        (c for c in lat_candidates if c in df.columns),
        None,
    )
    lon_col = next(
        (c for c in lon_candidates if c in df.columns),
        None,
    )

    if lat_col is None or lon_col is None:
        raise ValueError(
            "Latitude/longitude columns were not found. "
            "Check the column names printed above."
        )

    # 3. Clean coordinates
    df[lat_col] = pd.to_numeric(df[lat_col], errors="coerce")
    df[lon_col] = pd.to_numeric(df[lon_col], errors="coerce")

    df = df.dropna(subset=[lat_col, lon_col]).copy()

    # Keep only coordinates within the approximate Riyadh region
    df = df[
        df[lat_col].between(20, 28)
        & df[lon_col].between(40, 50)
    ].copy()

    if df.empty:
        raise ValueError(
            "No valid Riyadh coordinates remain after cleaning."
        )

    # 4. Create a GeoDataFrame using WGS84
    stations = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(
            df[lon_col],
            df[lat_col],
        ),
        crs="EPSG:4326",
    )

    # 5. Export geospatial station data
    geo_csv = OUTPUT_DIR / "riyadh_air_stations_geospatial.csv"
    stations.to_csv(geo_csv, index=False)

    geojson_file = OUTPUT_DIR / "riyadh_air_stations.geojson"
    stations.to_file(geojson_file, driver="GeoJSON")

    # 6. Summarize station classifications
    category_col = next(
        (
            c for c in ["Classification", "classification"]
            if c in stations.columns
        ),
        None,
    )

    if category_col:
        summary = (
            stations[category_col]
            .fillna("Unknown")
            .value_counts()
            .rename_axis("classification")
            .reset_index(name="station_count")
        )
    else:
        summary = pd.DataFrame({
            "classification": ["All stations"],
            "station_count": [len(stations)],
        })

    summary_file = REPORTS_DIR / "station_classification_summary.csv"
    summary.to_csv(summary_file, index=False)

    # 7. Plot station locations
    fig, ax = plt.subplots(figsize=(10, 8))

    if category_col:
        stations.plot(
            ax=ax,
            column=category_col,
            legend=True,
            markersize=65,
            alpha=0.85,
        )
    else:
        stations.plot(
            ax=ax,
            markersize=65,
            alpha=0.85,
        )

    ax.set_title(
        "Air Quality Monitoring Stations — Riyadh",
        fontsize=14,
    )
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.grid(True, linestyle="--", alpha=0.35)

    plt.tight_layout()

    plot_file = REPORTS_DIR / "riyadh_stations_geospatial.png"
    plt.savefig(plot_file, dpi=200, bbox_inches="tight")
    plt.close(fig)

    # 8. Print results
    print(f"\nValid stations: {len(stations)}")
    print(f"Coordinate system: {stations.crs}")

    print("\nStation classification summary:")
    print(summary.to_string(index=False))

    print("\nFiles created:")
    print(geo_csv)
    print(geojson_file)
    print(summary_file)
    print(plot_file)

    print("\nGeospatial analysis completed successfully.")


if __name__ == "__main__":
    main()
