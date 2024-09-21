from __future__ import annotations

import random

import numpy as np
import pandas as pd

# Load the CSV file
df = pd.read_csv("data/heart_disease_data.csv")

# Define the percentage of the dataset to infect (40%)
infected_rows_count = int(len(df) * 1)
rows_to_infect = random.sample(range(len(df)), infected_rows_count)


# Helper function to apply multiple types of data corruption
def apply_corruptions(df: pd.DataFrame, rows: list[int]) -> None:
    print("Original Data (First 5 Rows):")
    print(df.head())

    # Apply and show each corruption
    print("\n1. Missing Values:")
    df_missing = df.copy()
    for row in rows:
        col = random.choice(df_missing.columns)
        df_missing.loc[row, col] = np.nan
    print(df_missing.head())

    print("\n2. Outliers:")
    df_outliers = df.copy()
    num_columns = df_outliers.select_dtypes(include=[np.number]).columns
    for row in random.sample(rows, len(rows) // 5):
        col = random.choice(num_columns)
        df_outliers.loc[row, col] = df_outliers[col].mean() * 10
    print(df_outliers.head())

    print("\n3. Value Swapping:")
    df_swapping = df.copy()
    for row in random.sample(rows, len(rows) // 5):
        col1, col2 = random.sample(df_swapping.columns.tolist(), 2)
        df_swapping.loc[row, [col1, col2]] = df_swapping.loc[
            row, [col2, col1]
        ].values
    print(df_swapping.head())

    print("\n4. Inconsistent Categories:")
    df_inconsistent = df.copy()
    cat_columns = df_inconsistent.select_dtypes(include=[object]).columns
    for row in random.sample(rows, len(rows) // 5):
        col = random.choice(cat_columns)
        df_inconsistent.loc[row, col] = "INVALID"
    print(df_inconsistent.head())

    print("\n5. Noise Addition:")
    df_noise = df.copy()
    for row in random.sample(rows, len(rows) // 5):
        col = random.choice(num_columns)
        noise = np.random.normal(0, 0.1 * df_noise[col].mean())
        df_noise.loc[row, col] += noise
    print(df_noise.head())

    print("\n6. Random Characters in Categorical Columns:")
    df_random_chars = df.copy()
    for row in random.sample(rows, len(rows) // 5):
        col = random.choice(cat_columns)
        random_char = "".join(
            random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=3)
        )
        df_random_chars.loc[row, col] = (
            str(df_random_chars.loc[row, col]) + random_char
        )
    print(df_random_chars.head())

    print("\n7. Shuffling within Columns:")
    df_shuffling = df.copy()
    for row in random.sample(rows, len(rows) // 5):
        col = random.choice(df_shuffling.columns)
        df_shuffling[col] = (
            df_shuffling[col].sample(frac=1).reset_index(drop=True)
        )
    print(df_shuffling.head())


# Apply infections
df_infected = apply_corruptions(df.copy(), rows_to_infect)

# Save the infected data to a CSV file
df_infected.to_csv("data/infected_data.csv", index=False)
print("Infected data saved as infected_data.csv")
