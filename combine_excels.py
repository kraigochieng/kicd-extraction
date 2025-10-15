from pathlib import Path

import pandas as pd

# === SETTINGS ===
folder_path = Path("sanitised_excel_outputs")
output_file = folder_path.parent / "sanitised_excel_outputs_combined.xlsx"

# === READ & COMBINE ===
all_dfs = []

for file in folder_path.glob("*.xlsx"):
    print(f"Reading {file.name}...")
    df = pd.read_excel(file)
    all_dfs.append(df)

# Combine all dataframes
combined_df = pd.concat(all_dfs, ignore_index=True)

# === SAVE ===
combined_df.to_excel(output_file, index=False)
print(f"\n✅ Combined file saved as: {output_file}")
