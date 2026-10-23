
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "reports" / "pm25_forecast_test_results.csv"
REPORTS_DIR = BASE_DIR / "reports"


def main():
    df = pd.read_csv(INPUT_FILE, parse_dates=["date"])
    df["error"] = df["actual_pm2_5"] - df["predicted_pm2_5"]

    # Actual vs predicted
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.plot(
        df["date"], df["actual_pm2_5"],
        label="Actual PM2.5", linewidth=1.3
    )
    ax.plot(
        df["date"], df["predicted_pm2_5"],
        label="Random Forest prediction", linewidth=1.3
    )
    ax.set_title("PM2.5: Actual vs Predicted (Test Period)")
    ax.set_xlabel("Date")
    ax.set_ylabel("PM2.5")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.3)
    fig.tight_layout()
    fig.savefig(
        REPORTS_DIR / "pm25_actual_vs_predicted.png",
        dpi=200
    )
    plt.close(fig)

    # Prediction error distribution
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(df["error"].dropna(), bins=30)
    ax.axvline(0, linestyle="--")
    ax.set_title("PM2.5 Prediction Error Distribution")
    ax.set_xlabel("Actual - Predicted")
    ax.set_ylabel("Number of observations")
    ax.grid(True, linestyle="--", alpha=0.3)
    fig.tight_layout()
    fig.savefig(
        REPORTS_DIR / "pm25_prediction_error_distribution.png",
        dpi=200
    )
    plt.close(fig)

    print("Forecast plots created successfully:")
    print(REPORTS_DIR / "pm25_actual_vs_predicted.png")
    print(REPORTS_DIR / "pm25_prediction_error_distribution.png")


if __name__ == "__main__":
    main()
