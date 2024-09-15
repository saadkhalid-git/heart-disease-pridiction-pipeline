from __future__ import annotations

import random

import numpy as np
import pandas as pd

# Load the CSV file
df = pd.read_csv("data/heart_disaease_data.csv")

# Define the percentage of the dataset to infect (40%)
infected_rows_count = int(len(df) * 0.4)
rows_to_infect = random.sample(range(len(df)), infected_rows_count)


# Helper function to introduce missing values
def introduce_missing_values(df, rows):
    for row in rows:
        col = random.choice(df.columns)
        df.loc[row, col] = np.nan
    return df


# Helper function to introduce outliers
def introduce_outliers(df, rows):
    for row in rows:
        col = random.choice(df.select_dtypes(include=[np.number]).columns)
        df.loc[row, col] = df[col].mean() * 10  # Extreme outlier
    return df


# Helper function to swap column values
def swap_values(df, rows):
    col1, col2 = random.sample(list(df.columns), 2)
    df.loc[rows, [col1, col2]] = df.loc[rows, [col2, col1]].values
    return df


# Helper function to introduce inconsistent categories
def introduce_inconsistent_categories(df, rows):
    cat_columns = df.select_dtypes(include=[object]).columns
    for row in rows:
        col = random.choice(cat_columns)
        df.loc[row, col] = "INVALID"
    return df


# Helper function to add noise to numerical columns
def add_noise_to_numerical_columns(df, rows):
    num_columns = df.select_dtypes(include=[np.number]).columns
    for row in rows:
        col = random.choice(num_columns)
        noise = np.random.normal(0, 0.1 * df[col].mean())  # Adding small noise
        df.loc[row, col] += noise
    return df


# Helper function to insert random characters into categorical columns
def insert_random_characters(df, rows):
    cat_columns = df.select_dtypes(include=[object]).columns
    for row in rows:
        col = random.choice(cat_columns)
        random_char = "".join(
            random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=3)
        )
        df.loc[row, col] = (
            df.loc[row, col] + random_char
        )  # Insert random chars
    return df


# Apply infections randomly
df_infected = introduce_missing_values(df.copy(), rows_to_infect)
df_infected = introduce_outliers(
    df_infected, random.sample(rows_to_infect, infected_rows_count // 6)
)
df_infected = swap_values(
    df_infected, random.sample(rows_to_infect, infected_rows_count // 6)
)
df_infected = introduce_inconsistent_categories(
    df_infected, random.sample(rows_to_infect, infected_rows_count // 6)
)
df_infected = add_noise_to_numerical_columns(
    df_infected, random.sample(rows_to_infect, infected_rows_count // 6)
)
df_infected = insert_random_characters(
    df_infected, random.sample(rows_to_infect, infected_rows_count // 6)
)

# Save the infected data to a CSV file
df_infected.to_csv("data/infected_data.csv", index=False)
print("Infected data saved as infected_data.csv")
