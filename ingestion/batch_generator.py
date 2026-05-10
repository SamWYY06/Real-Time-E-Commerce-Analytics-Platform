import pandas as pd
import os
from ingestion.data_generator import generate_event

# ---------------- CONFIG ----------------
N = 10000

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "raw", "synthetic_data.csv")


def generate_data():
    data = []

    for _ in range(N):
        event = generate_event(messy=True)
        data.append(event)

    df = pd.DataFrame(data)

    # ---------------- DUPLICATES ----------------
    df = pd.concat([df, df.sample(frac=0.02)], ignore_index=True)

    # ---------------- SAVE ----------------
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print("=======================================")
    print("✅ Batch Data Generated")
    print(f"📦 Rows: {len(df)}")
    print(f"📁 Path: {OUTPUT_PATH}")
    print("=======================================")


if __name__ == "__main__":
    generate_data()