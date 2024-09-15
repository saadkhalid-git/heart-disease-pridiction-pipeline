from __future__ import annotations

import random

import numpy as np
import pandas as pd

# Load the CSV file
df = pd.read_csv("data/heart_disease_data.csv")

# Define the percentage of the dataset to infect (40%)
infected_rows_count = int(len(df) * 0.4)
rows_to_infect = random.sample(range(len(df)), infected_rows_count)


# Helper function to apply multiple types of data corruption
def apply_corruptions(df: pd.DataFrame, rows: list[int]) -> pd.DataFrame:
    # Introduce missing values
    for row in rows:
        col = random.choice(df.columns)
        df.loc[row, col] = np.nan

    # Introduce outliers in numerical columns
    num_columns = df.select_dtypes(include=[np.number]).columns
    for row in random.sample(rows, infected_rows_count // 5):
        col = random.choice(num_columns)
        df.loc[row, col] = df[col].mean() * 10

    # Swap values between columns
    for row in random.sample(rows, infected_rows_count // 5):
        col1, col2 = random.sample(df.columns.tolist(), 2)
        # Ensure values can be swapped
        df.loc[row, [col1, col2]] = df.loc[row, [col2, col1]].values

    # Introduce inconsistent categories
    cat_columns = df.select_dtypes(include=[object]).columns
    for row in random.sample(rows, infected_rows_count // 5):
        col = random.choice(cat_columns)
        df.loc[row, col] = "INVALID"

    # Add noise to numerical columns
    for row in random.sample(rows, infected_rows_count // 5):
        col = random.choice(num_columns)
        if pd.api.types.is_numeric_dtype(df[col]):
            noise = np.random.normal(0, 0.1 * df[col].mean())
            df.loc[row, col] = df.loc[row, col] + noise

    # Insert random characters into categorical columns
    for row in random.sample(rows, infected_rows_count // 5):
        col = random.choice(cat_columns)
        random_char = "".join(
            random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=3)
        )
        df.loc[row, col] = (
            str(df.loc[row, col]) + random_char
        )  # Ensure value is string

    return df


# Apply infections
df_infected = apply_corruptions(df.copy(), rows_to_infect)

# Save the infected data to a CSV file
df_infected.to_csv("data/infected_data.csv", index=False)
print("Infected data saved as infected_data.csv")
