from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List

from markitdown import MarkItDown

download_dir = Path("downloads")
output_dir = Path("markdown_files")
output_dir.mkdir(exist_ok=True)

md = MarkItDown(enable_plugins=False)


def convert_pdf_to_md(pdf_file: Path) -> None:
    try:
        result = md.convert(str(pdf_file))  # Ignores "no extraction" metadata
        out_path = output_dir / f"{pdf_file.stem}.md"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(result.text_content)
        print(f"Saved {out_path}")
    except Exception as e:
        print(f"Error processing {pdf_file.name}: {e}")


pdf_files: List[Path] = []

# Loop through all PDF files in the downloads directory
for f in download_dir.glob("*.pdf"):
    # Check if 'grade' appears in the filename (case-insensitive)
    if "grade" in f.name.lower():
        pdf_files.append(f)

with ThreadPoolExecutor(max_workers=2) as executor:  # Adjust workers as needed
    executor.map(convert_pdf_to_md, pdf_files)
