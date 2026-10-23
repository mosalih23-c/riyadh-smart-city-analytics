
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "data" / "raw"
REPORT_DIR = PROJECT_DIR / "reports"

FILE = RAW_DIR / "air_quality_historical.csv"


def main():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(FILE)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # 1. Completeness of each column
    quality = pd.DataFrame({
        "column": df.columns,
        "missing_count": [df[c].isna().sum() for c in df.columns],
        "missing_pct": [
            round(df[c].isna().mean() * 100, 2)
            for c in df.columns
        ],
        "unique_values": [df[c].nunique() for c in df.columns],
    })

    # 2. Check chronological gaps
    dates = df["date"].dropna().sort_values()
    expected_dates = pd.date_range(
        start=dates.min(),
        end=dates.max(),
        freq="D"
    )
    missing_dates = expected_dates.difference(dates)

    # 3. Check negative values in numeric indicators
    numeric_cols = df.select_dtypes(include="number").columns
    negative_counts = df[numeric_cols].lt(0).sum()
    negative_counts = negative_counts[negative_counts > 0]

    # 4. Flag statistical outliers using the IQR rule.
    # These are candidates for review, not automatic errors.
    outlier_rows = []

    for col in numeric_cols:
        values = df[col].dropna()

        if values.empty:
            continue

        q1 = values.quantile(0.25)
        q3 = values.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        count = ((values < lower) | (values > upper)).sum()

        outlier_rows.append({
            "column": col,
            "lower_bound": round(lower, 3),
            "upper_bound": round(upper, 3),
            "candidate_count": int(count),
        })

    outliers = pd.DataFrame(outlier_rows)

    # 5. Print results
    print("\n--- COLUMN COMPLETENESS ---")
    print(quality.to_string(index=False))

    print("\n--- DATE COVERAGE ---")
    print(f"First date: {dates.min().date()}")
    print(f"Last date:  {dates.max().date()}")
    print(f"Expected daily records: {len(expected_dates)}")
    print(f"Unique valid dates: {dates.nunique()}")
    print(f"Missing dates in calendar: {len(missing_dates)}")
    print("First missing dates:", list(missing_dates[:10].date))

    print("\n--- NEGATIVE VALUES ---")
    if negative_counts.empty:
        print("No negative numeric values found.")
    else:
        print(negative_counts.to_string())

    print("\n--- POTENTIAL OUTLIERS (IQR) ---")
    print(outliers.to_string(index=False))

    # 6. Save audit outputs
    quality.to_csv(
        REPORT_DIR / "data_completeness.csv",
        index=False
    )
    outliers.to_csv(
        REPORT_DIR / "potential_outliers.csv",
        index=False
    )
    pd.DataFrame({"missing_date": missing_dates}).to_csv(
        REPORT_DIR / "missing_dates.csv",
        index=False
    )

    print("\nReports saved to:", REPORT_DIR)
    print("Original data was not modified.")


if __name__ == "__main__":
    main()
