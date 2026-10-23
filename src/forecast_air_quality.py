
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.ensemble import RandomForestRegressor

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "raw" / "air_quality_historical.csv"
OUTPUT_DIR = BASE_DIR / "data" / "processed"
REPORTS_DIR = BASE_DIR / "reports"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

TARGET = "pm2_5"
TEST_DAYS = 180


def create_features(df):
    data = df.copy()
    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    data = data.dropna(subset=["date"]).sort_values("date")

    # Calendar features
    data["day_of_week"] = data["date"].dt.dayofweek
    data["month"] = data["date"].dt.month
    data["day_of_year"] = data["date"].dt.dayofyear

    # Past observations only
    for lag in [1, 2, 3, 7, 14]:
        data[f"lag_{lag}"] = data[TARGET].shift(lag)

    # Rolling averages use only previous days
    data["rolling_mean_7"] = (
        data[TARGET].shift(1).rolling(7).mean()
    )
    data["rolling_mean_14"] = (
        data[TARGET].shift(1).rolling(14).mean()
    )

    return data


def main():
    df = pd.read_csv(INPUT_FILE)
    data = create_features(df)

    feature_cols = [
        "day_of_week",
        "month",
        "day_of_year",
        "lag_1",
        "lag_2",
        "lag_3",
        "lag_7",
        "lag_14",
        "rolling_mean_7",
        "rolling_mean_14",
    ]

    # Drop missing target/features; do not interpolate test targets
    model_data = data.dropna(
        subset=[TARGET] + feature_cols
    ).copy()

    if len(model_data) <= TEST_DAYS:
        raise ValueError("Not enough observations for the selected test window.")

    # Chronological split
    split_index = len(model_data) - TEST_DAYS
    train = model_data.iloc[:split_index].copy()
    test = model_data.iloc[split_index:].copy()

    X_train = train[feature_cols]
    y_train = train[TARGET]
    X_test = test[feature_cols]
    y_test = test[TARGET]

    model = RandomForestRegressor(
        n_estimators=300,
        min_samples_leaf=3,
        random_state=42,
        n_jobs=-1,
    )

    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    # Simple baseline: tomorrow's value equals the previous day's value
    baseline = test["lag_1"].to_numpy()

    results = pd.DataFrame({
        "date": test["date"].dt.strftime("%Y-%m-%d"),
        "actual_pm2_5": y_test.to_numpy(),
        "predicted_pm2_5": predictions,
        "baseline_lag1": baseline,
    })

    results.to_csv(
        REPORTS_DIR / "pm25_forecast_test_results.csv",
        index=False,
    )

    def calculate_metrics(actual, predicted):
        return {
            "MAE": mean_absolute_error(actual, predicted),
            "RMSE": np.sqrt(mean_squared_error(actual, predicted)),
        }

    model_metrics = calculate_metrics(y_test, predictions)
    baseline_metrics = calculate_metrics(y_test, baseline)

    metrics = pd.DataFrame([
        {"model": "Random Forest", **model_metrics},
        {"model": "Previous-day baseline", **baseline_metrics},
    ])

    metrics = metrics.round(3)
    metrics.to_csv(
        REPORTS_DIR / "pm25_forecast_metrics.csv",
        index=False,
    )

    print("PM2.5 forecast evaluation completed.")
    print(f"Training observations: {len(train)}")
    print(f"Test observations: {len(test)}")
    print(f"Test period: {test['date'].min().date()} to {test['date'].max().date()}")
    print("\nMetrics (lower is better):")
    print(metrics.to_string(index=False))
    print("\nSaved:")
    print(REPORTS_DIR / "pm25_forecast_test_results.csv")
    print(REPORTS_DIR / "pm25_forecast_metrics.csv")


if __name__ == "__main__":
    main()
