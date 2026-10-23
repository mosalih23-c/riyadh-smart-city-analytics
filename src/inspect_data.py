
from pathlib import Path
import pandas as pd

# تحديد مسار المشروع تلقائياً
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data" / "raw"

DATA_FILE = DATA_DIR / "air_quality_historical.csv"
DICTIONARY_FILE = DATA_DIR / "data_dictionary.csv"

def main():
    if not DATA_FILE.exists():
        print(f"ERROR: File not found: {DATA_FILE}")
        print("Check that the CSV file is inside data/raw/")
        return

    # قراءة البيانات الأصلية دون تعديلها
    df = pd.read_csv(DATA_FILE)

    print("\n" + "=" * 60)
    print("RIYADH SMART CITY - AIR QUALITY DATA AUDIT")
    print("=" * 60)

    print(f"\nFile: {DATA_FILE.name}")
    print(f"Rows: {df.shape[0]:,}")
    print(f"Columns: {df.shape[1]}")

    print("\n--- Column Names ---")
    for column in df.columns:
        print(f"- {column}")

    print("\n--- Data Types ---")
    print(df.dtypes.to_string())

    print("\n--- First 5 Rows ---")
    print(df.head().to_string())

    print("\n--- Missing Values ---")
    missing = df.isna().sum()
    missing = missing[missing > 0]

    if missing.empty:
        print("No missing values detected.")
    else:
        print(missing.to_string())

    print("\n--- Duplicate Rows ---")
    print(f"Exact duplicate rows: {df.duplicated().sum():,}")

    print("\n--- Date Column Candidates ---")
    date_columns = [
        col for col in df.columns
        if any(word in col.lower()
               for word in ["date", "time", "timestamp"])
    ]

    if not date_columns:
        print("No obvious date/time columns found.")
    else:
        for column in date_columns:
            print(f"\nColumn: {column}")
            parsed = pd.to_datetime(df[column], errors="coerce")
            valid = parsed.dropna()

            print(f"Valid date values: {len(valid):,}")
            print(f"Invalid or missing dates: {parsed.isna().sum():,}")

            if not valid.empty:
                print(f"Earliest: {valid.min()}")
                print(f"Latest:   {valid.max()}")

    print("\n--- Numeric Summary ---")
    numeric = df.select_dtypes(include="number")

    if numeric.empty:
        print("No numeric columns detected.")
    else:
        print(numeric.describe().round(2).to_string())

    if DICTIONARY_FILE.exists():
        print("\n--- Data Dictionary ---")
        dictionary = pd.read_csv(DICTIONARY_FILE)
        print(f"Dictionary rows: {len(dictionary)}")
        print(dictionary.head(20).to_string(index=False))

    print("\n--- Audit Complete ---")
    print("Original dataset has not been modified.")

if __name__ == "__main__":
    main()
