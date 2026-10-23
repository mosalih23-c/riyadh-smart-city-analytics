
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_FILE = PROJECT_DIR / "data" / "raw" / "air_quality_historical.csv"
REPORT_DIR = PROJECT_DIR / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(RAW_FILE, parse_dates=["date"])
df = df.sort_values("date").set_index("date")

# Monthly averages; missing values are excluded from each mean.
columns = [
    "pm2_5",
    "pm10",
    "us_aqi",
    "european_aqi",
]

monthly = df[columns].resample("MS").mean()

# Save monthly data
monthly.to_csv(REPORT_DIR / "monthly_air_quality.csv")

# Plot each indicator separately to preserve its own scale.
for column in columns:
    series = monthly[column].dropna()

    if series.empty:
        print(f"Skipping {column}: no valid observations.")
        continue

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(series.index, series.values, marker="o")
    ax.set_title(f"Monthly Average: {column}")
    ax.set_xlabel("Month")
    ax.set_ylabel(column)
    ax.grid(True, alpha=0.3)
    fig.autofmt_xdate()
    fig.tight_layout()

    output_file = REPORT_DIR / f"monthly_{column}.png"
    fig.savefig(output_file, dpi=150)
    plt.close(fig)

# Highest and lowest monthly averages
print("\n--- Highest Monthly Averages ---")
for column in columns:
    valid = monthly[column].dropna()
    if not valid.empty:
        date = valid.idxmax()
        print(f"{column}: {valid.loc[date]:.2f} ({date:%Y-%m})")

print("\n--- Lowest Monthly Averages ---")
for column in columns:
    valid = monthly[column].dropna()
    if not valid.empty:
        date = valid.idxmin()
        print(f"{column}: {valid.loc[date]:.2f} ({date:%Y-%m})")

# Correlation is descriptive, not proof of causation.
print("\n--- Correlation Matrix ---")
print(df[columns].corr().round(3).to_string())

print(f"\nMonthly table and charts saved in: {REPORT_DIR}")
