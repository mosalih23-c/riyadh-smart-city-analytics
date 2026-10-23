
from pathlib import Path

import geopandas as gpd
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "riyadh_air_stations_geospatial.csv"
)

OUTPUT_DIR = BASE_DIR / "reports"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    # Read the CSV file
    df = pd.read_csv(INPUT_FILE)

    # Recreate geometry from longitude and latitude
    df["latitude"] = pd.to_numeric(
        df["latitude"], errors="coerce"
    )
    df["longitude"] = pd.to_numeric(
        df["longitude"], errors="coerce"
    )

    df = df.dropna(
        subset=["latitude", "longitude"]
    ).copy()

    # Convert DataFrame into GeoDataFrame
    stations = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(
            df["longitude"],
            df["latitude"],
        ),
        crs="EPSG:4326",
    )

    # Project to a coordinate system measured in meters
    stations_metric = stations.to_crs("EPSG:32638")

    # Calculate center of station distribution
    center = stations_metric.geometry.union_all().centroid

    # Calculate distance from the center in kilometers
    stations_metric["distance_from_center_km"] = (
        stations_metric.geometry.distance(center) / 1000
    ).round(3)

    # Summarize station categories
    category_col = "Classification"

    summary = (
        stations_metric.groupby(category_col, dropna=False)
        .agg(
            station_count=("geometry", "count"),
            mean_distance_km=(
                "distance_from_center_km", "mean"
            ),
            max_distance_km=(
                "distance_from_center_km", "max"
            ),
        )
        .reset_index()
        .round(3)
    )

    # Save summary
    summary.to_csv(
        OUTPUT_DIR / "station_spatial_summary.csv",
        index=False,
    )

    # Save station distances
    stations_metric.drop(
        columns="geometry"
    ).to_csv(
        OUTPUT_DIR / "station_distances.csv",
        index=False,
    )

    print("Spatial summary completed successfully.")
    print(f"Stations analyzed: {len(stations_metric)}")
    print(f"CRS used for distances: {stations_metric.crs}")

    print("\nClassification summary:")
    print(summary.to_string(index=False))

    print("\nCreated files:")
    print(OUTPUT_DIR / "station_spatial_summary.csv")
    print(OUTPUT_DIR / "station_distances.csv")


if __name__ == "__main__":
    main()
