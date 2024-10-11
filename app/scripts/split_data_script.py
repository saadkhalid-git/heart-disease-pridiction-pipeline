from __future__ import annotations

import numpy as np
import pandas as pd


def split_csv(file_path, num_files):
    data = pd.read_csv(file_path)

    num_files = min(num_files, len(data))

    chunks = np.array_split(data, num_files)

    for i, chunk in enumerate(chunks):
        chunk.to_csv(f"data/raw_data/output_file_{i+1}.csv", index=False)
        print(f"Created output_file_{i+1}.csv")


file_path = "data/heart_disease_data.csv"  # Path to your large CSV file
num_files = 25  # Set how many files you want
split_csv(file_path, num_files)
