import os
import re
import pandas as pd

# Folder containing Excel files
FOLDER_PATH = "excel_outputs"

# Output folder for cleaned files
OUTPUT_PATH = "sanitised_excel_outputs"

os.makedirs(OUTPUT_PATH, exist_ok=True)

# Regex to keep only ASCII characters
clean_pattern = re.compile(r"[^\x00-\x7F]+")


def clean_cell(value):
    """Remove non-ASCII characters (like Chinese, etc.) from a cell."""
    if isinstance(value, str):
        return clean_pattern.sub("", value)
    return value


for filename in os.listdir(FOLDER_PATH):
    if filename.endswith(".xlsx"):
        filepath = os.path.join(FOLDER_PATH, filename)
        print(f"Cleaning: {filename} ...")

        # Read all sheets
        excel = pd.ExcelFile(filepath)
        cleaned_sheets = {}

        for sheet_name in excel.sheet_names:
            df = excel.parse(sheet_name)
            cleaned_df = df.map(clean_cell)
            cleaned_sheets[sheet_name] = cleaned_df

        # Save cleaned copy
        output_file = os.path.join(OUTPUT_PATH, f"{filename}")

        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
            for sheet_name, cleaned_df in cleaned_sheets.items():
                cleaned_df.to_excel(writer, sheet_name=sheet_name, index=False)

        print(f"✅ Saved cleaned file: {output_file}")

print("All files cleaned!")
