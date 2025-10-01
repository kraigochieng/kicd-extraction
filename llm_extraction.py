import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List

import pandas as pd
from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_xai import ChatXAI
from pydantic import BaseModel, Field

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.openai_api_key
os.environ["XAI_API_KEY"] = settings.xai_api_key

GROK_MODEL = "grok-4-fast-non-reasoning"


class CurriculumRow(BaseModel):
    """
    Defines the structure for a single row of curriculum data.
    """

    subject: str = Field(
        description="The main subject area, e.g., 'AGRICULTURE AND NUTRITION'"
    )
    grade: str = Field(description="The grade level, e.g., '4'")
    strand: str = Field(description="The high-level topic within the subject")
    theme: str = Field(description="The overarching theme for the strand/substrand")
    substrand: str = Field(description="A more specific topic within the strand")
    activity: str = Field(
        description="A single, distinct suggested learning experience or activity"
    )


class CurriculumRows(BaseModel):
    """
    A container for a list of curriculum rows.
    """

    curriculum_rows: List[CurriculumRow]


# Directories
markdown_dir = Path("markdown_files")
excel_dir = Path("excel_outputs")
markdown_dir.mkdir(exist_ok=True)
excel_dir.mkdir(exist_ok=True)

# LLM
# chat_model = ChatOpenAI(
#     model_name="gpt-5-nano",
#     verbosity="low",
#     reasoning_effort="low",
# )


chat_model = ChatXAI(model_name=GROK_MODEL, temperature=0)

parser = PydanticOutputParser(pydantic_object=CurriculumRows)


prompt_template = PromptTemplate(
    template="{text}\n\n{format_instructions}",
    input_variables=["text"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)


chain = prompt_template | chat_model | parser


def extract_curriculum_from_md(md_file: Path, subject: str) -> List[CurriculumRow]:
    """
    Reads a markdown file and uses an LLM to extract curriculum data.

    Args:
        md_file: Path to the input markdown file.
        subject: The subject name to be used in the output.

    Returns:
        A list of CurriculumRow objects, or an empty list if an error occurs.
    """
    print(f"Processing {md_file.name} for subject '{subject}'...")
    with open(md_file, "r", encoding="utf-8") as f:
        text = f.read()

    prompt_with_instructions = f"""
        You are an expert assistant specializing in extracting curriculum data from educational documents.
        Your task is to parse the provided text and generate a structured JSON output.

        Follow these rules meticulously:
        1.  **Activity Source**: The activities are found under the heading 'SUGGESTED LEARNING EXPERIENCES'.
        2.  **One Activity Per Row**: For each substrand, there are multiple learning experiences. You MUST create a separate, distinct JSON object for EACH individual activity. Never group multiple activities into a single "activity" field.
        3.  **Clean Text**: When extracting 'strand' and 'substrand' names, you MUST omit any leading numbers, letters, or bullet points. For example, '1. Conservation of Resources' should become 'Conservation of Resources', and '1.1 Soil Conservation' should become 'Soil Conservation'.
        4.  **Field Extraction**: Extract exactly these fields for each activity:
            - subject: Use the provided value '{subject}'.
            - grade: The grade level specified in the text.
            - strand: The cleaned strand name.
            - theme: The theme associated with the strand/substrand.
            - substrand: The cleaned substrand name.
            - activity: The single learning experience.

        Return the data as a JSON object that strictly follows the format of the `CurriculumRows` model.

        Text to be processed:
        ---
        {text}
    """

    try:
        result: CurriculumRows = chain.invoke({"text": prompt_with_instructions})
        return result.curriculum_rows
    except Exception as e:
        print(f"Error extracting {md_file.name}: {e}")
        return []


def process_file(md_file: Path) -> None:
    """
    Orchestrates the processing of a single markdown file: extraction and saving to Excel.
    """
    subject = md_file.stem.split("GRADE")[0].strip()
    rows = extract_curriculum_from_md(md_file, subject)

    if rows:
        df = pd.DataFrame([row.model_dump() for row in rows])
        out_path = excel_dir / f"{md_file.stem}.xlsx"
        df.to_excel(out_path, index=False)
        print(f"✅ Successfully saved {len(df.index)} rows to {out_path}")
    else:
        print(f"No data extracted from {md_file.name}")


def main():
    """
    Main function to find markdown files and process them in parallel.
    """
    # Create a dummy markdown file if the directory is empty, for demonstration.
    if not any(markdown_dir.iterdir()):
        print("Markdown directory is empty. Exiting...")
        return

    md_files: List[Path] = [
        f for f in markdown_dir.glob("*.md") if "grade" in f.name.lower()
    ]

    if not md_files:
        print("No markdown files containing 'grade' in their name were found.")
        return

    print(f"Found {len(md_files)} files to process.")
    # Using ThreadPoolExecutor to process files concurrently for better performance.
    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(process_file, md_files)

    print("\nProcessing complete.")


if __name__ == "__main__":
    main()
