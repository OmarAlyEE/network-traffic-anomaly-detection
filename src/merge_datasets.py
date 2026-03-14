
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data/raw"

files = [
    "UNSW-NB15_1.csv",
    "UNSW-NB15_2.csv",
    "UNSW-NB15_3.csv",
    "UNSW-NB15_4.csv"
]

dfs = []

print("Reading dataset files...")

for file in files:
    path = DATA_PATH / file
    print("Loading:", path)

    # IMPORTANT: no header in these files
    df = pd.read_csv(path, header=None)

    dfs.append(df)

print("Merging datasets...")

merged_df = pd.concat(dfs, ignore_index=True)

output_file = DATA_PATH / "network_logs.csv"

merged_df.to_csv(output_file, index=False, header=False)

print("Dataset merged successfully.")
print("Saved to:", output_file)
print("Final shape:", merged_df.shape)
