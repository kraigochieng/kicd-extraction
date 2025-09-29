import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List

import pandas as pd
from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_xai import ChatXAI
from pydantic import BaseModel

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.openai_api_key
os.environ["XAI_API_KEY"] = settings.xai_api_key


class CurriculumRow(BaseModel):
    subject: str
    grade: str
    strand: str
    theme: str
    substrand: str
    activity: str


class CurriculumRows(BaseModel):
    curriculum_rows: List[CurriculumRow]


# Directories
markdown_dir = Path("markdown_files")
excel_dir = Path("excel_outputs")
excel_dir.mkdir(exist_ok=True)

# LLM
# chat_model = ChatOpenAI(
#     model_name="gpt-5-nano",
#     verbosity="low",
#     reasoning_effort="low",
# )


chat_model = ChatXAI(model_name="grok-4-fast-non-reasoning", temperature=0)

parser = PydanticOutputParser(pydantic_object=CurriculumRows)


prompt = PromptTemplate(
    template="Extract subject, grade, strands, sub-strands and activities data from the following text.\n{format_instructions}\n{text}",
    input_variables=["text"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

chain = prompt | chat_model | parser


def extract_curriculum_from_md(md_file: Path, subject: str) -> List[CurriculumRow]:
    with open(md_file, "r", encoding="utf-8") as f:
        text = f.read()

    prompt_text = f"""
    You are an assistant that extracts curriculum data from text.

    The learning outcomes section is the one which has the activities.

    The file has a lot of information but focus on the strand section, extract exactly these fields:

    - subject (use '{subject}')
    - grade
    - strand
    - theme
    - substrand
    - activity

    Return the data as JSON suitable for the CurriculumRows model.
    
    Text:
    
    {text}
    """

    try:
        result: CurriculumRows = chain.invoke({"text": prompt_text})
        return result.curriculum_rows
    except Exception as e:
        print(f"Error extracting {md_file.name}: {e}")
        return []


def process_file(md_file: Path) -> None:
    subject = md_file.stem.split("GRADE")[0].strip()
    rows = extract_curriculum_from_md(md_file, subject)

    if rows:
        df = pd.DataFrame([row.model_dump() for row in rows])
        out_path = excel_dir / f"{md_file.stem}.xlsx"
        df.to_excel(out_path, index=False)
        print(f"Saved {out_path}")
    else:
        print(f"No data extracted from {md_file.name}")


md_files: List[Path] = [
    f for f in markdown_dir.glob("*.md") if "grade" in f.name.lower()
]

# Parallel processing
with ThreadPoolExecutor(max_workers=4) as executor:
    executor.map(process_file, md_files)
