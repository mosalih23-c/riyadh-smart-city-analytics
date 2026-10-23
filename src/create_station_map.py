
from pathlib import Path
import pandas as pd
import folium

ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = ROOT / "data" / "processed" / "riyadh_air_stations_clean.csv"
OUTPUT_DIR = ROOT / "reports"
OUTPUT_FILE = OUTPUT_DIR / "riyadh_air_quality_stations_map.html"

def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"File not found: {INPUT_FILE}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(INPUT_FILE)

    # Use only stations with valid coordinates
    df = df[
        df["coordinates_valid"].astype(str).str.lower().eq("true")
    ].copy()

    if df.empty:
        raise ValueError("No stations with valid coordinates.")

    # Center the map around the station network
    center = [df["latitude"].mean(), df["longitude"].mean()]

    station_map = folium.Map(
        location=center,
        zoom_start=11,
        tiles="OpenStreetMap",
        control_scale=True,
    )

    colors = {
        "Traffic": "red",
        "Suburban": "green",
        "Background stations": "blue",
        "Mobile": "purple",
    }

    for _, station in df.iterrows():
        name = station.get("Air quality stations", "Unknown station")
        classification = station.get("Classification", "Unknown")
        lat = station["latitude"]
        lon = station["longitude"]

        popup_html = f"""
        <b>{name}</b><br>
        Classification: {classification}<br>
        Latitude: {lat:.6f}<br>
        Longitude: {lon:.6f}
        """

        folium.CircleMarker(
            location=[lat, lon],
            radius=7,
            color=colors.get(classification, "gray"),
            fill=True,
            fill_opacity=0.85,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=name,
        ).add_to(station_map)

    # Legend
    legend = """
    <div style="
        position: fixed; bottom: 25px; left: 25px; z-index: 9999;
        background: white; padding: 12px; border: 1px solid #999;
        border-radius: 6px; font-size: 13px;">
        <b>Station Classification</b><br>
        <span style="color:red;">●</span> Traffic<br>
        <span style="color:green;">●</span> Suburban<br>
        <span style="color:blue;">●</span> Background stations<br>
        <span style="color:purple;">●</span> Mobile
    </div>
    """
    station_map.get_root().html.add_child(folium.Element(legend))

    station_map.save(str(OUTPUT_FILE))

    print(f"Stations displayed: {len(df)}")
    print(f"Map saved to: {OUTPUT_FILE}")
    print("Open the HTML file in your browser to explore the map.")

if __name__ == "__main__":
    main()
