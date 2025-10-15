import os
import pandas as pd

# Folder paths
FOLDER_PATH = "sanitised_excel_outputs"
OUTPUT_PATH = "sanitised_formatted_excel_outputs"

os.makedirs(OUTPUT_PATH, exist_ok=True)


def sentence_case(text):
    """Convert string to sentence case."""
    if isinstance(text, str) and text.strip():
        return text.strip().capitalize()

    return text


def title_case(text):
    """Convert string to title case."""
    if isinstance(text, str) and text.strip():
        return text.strip().title()

    return text


def capitalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [col.capitalize() for col in df.columns]

    return df


def rename_columns(df: pd.DataFrame, rename_map: dict[str, str]) -> pd.DataFrame:
    df = df.rename(columns=rename_map)

    return df


def apply_title_case(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    for column in columns:
        if column in df.columns:
            df[column] = df[column].apply(title_case)

    return df


def apply_sentence_case(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    for column in columns:
        if column in df.columns:
            df[column] = df[column].apply(sentence_case)

    return df


for filename in os.listdir(FOLDER_PATH):
    if filename.endswith(".xlsx"):
        filepath = os.path.join(FOLDER_PATH, filename)
        print(f"Processing: {filename} ...")

        excel = pd.ExcelFile(filepath)
        cleaned_sheets = {}

        for sheet_name in excel.sheet_names:
            df = excel.parse(sheet_name)

            df = capitalize_column_names(df=df)

            df = rename_columns(
                df=df, rename_map={"Substrand": "SubStrand", "Theme": "Description"}
            )

            df = apply_sentence_case(
                df=df, columns=["Strand", "SubStrand", "Description", "Activity"]
            )

            df = apply_title_case(df=df, columns=["Subject"])

            if "Grade" in df.columns:
                df["Grade"] = df["Grade"].apply(
                    lambda x: f"Grade {x}" if pd.notnull(x) else x
                )

            cleaned_sheets[sheet_name] = df

        output_file = os.path.join(OUTPUT_PATH, f"{filename}")
        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
            for sheet_name, cleaned_df in cleaned_sheets.items():
                cleaned_df.to_excel(writer, sheet_name=sheet_name, index=False)

        print(f"✅ Saved cleaned file: {output_file}")

print("All Excel files processed successfully!")
