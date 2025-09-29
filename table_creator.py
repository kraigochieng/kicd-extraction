from pathlib import Path
import camelot

download_dir = Path("downloads")
output_dir = Path("tables")
output_dir.mkdir(exist_ok=True)

for pdf_file in download_dir.glob("*.pdf"):
    print(f"Processing {pdf_file.name}...")
    try:
        tables = camelot.read_pdf(str(pdf_file), pages="all")
        print(f"  Found {tables.n} tables")

        for i, table in enumerate(tables):
            out_path = output_dir / f"{pdf_file.stem}_table_{i}.csv"
            table.to_csv(out_path)
            print(f"  Saved {out_path}")

    except Exception as e:
        print(f"  Error processing {pdf_file.name}: {e}")
