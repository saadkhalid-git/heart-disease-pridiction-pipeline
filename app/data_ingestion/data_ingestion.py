from __future__ import annotations

import numpy as np
import pandas as pd


def split_csv(file_path, num_files):
    # Read the CSV file
    data = pd.read_csv(file_path)

    # Limit the number of files if there are fewer rows than requested files
    num_files = min(num_files, len(data))

    # Split the data into chunks
    chunks = np.array_split(data, num_files)

    # Save each chunk as a separate CSV
    for i, chunk in enumerate(chunks):
        chunk.to_csv(f"output_file_{i+1}.csv", index=False)
        print(f"Created output_file_{i+1}.csv")


file_path = "large_data.csv"  # Path to your large CSV file
num_files = 2  # Set how many files you want
split_csv(file_path, num_files)
