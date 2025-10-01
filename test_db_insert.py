import sqlite3
import string
import time
from pathlib import Path

import pandas as pd

# ==============================
# 1. CREATE DEMO EXCEL FILE
# ==============================
ACTIVITIES_PER_SUBSTRAND = 100

print("📂 Creating demo Excel file...")

start_time = time.perf_counter()

strands = list(string.ascii_uppercase)
sub_strands = list(string.ascii_uppercase)
activities = [str(a) for a in range(1, ACTIVITIES_PER_SUBSTRAND)]

all_rows = []
for strand in strands:
    for sub_strand in sub_strands:
        for activity in activities:
            all_rows.append(
                {
                    "strand": f"Strand {strand}",
                    "substrand": f"Sub Strand {sub_strand}",
                    "activity": f"Activity #{activity}",
                }
            )

df = pd.DataFrame(all_rows)

output_dir = Path("demos")
output_dir.mkdir(exist_ok=True)
output_path = output_dir / "DEMO_CURRICULUM.xlsx"
df.to_excel(output_path, index=False, engine="openpyxl")

elapsed = time.perf_counter() - start_time
print(f"✅ Excel created with {len(df)} rows in {elapsed:.2f} seconds.")
print(f"   File: {output_path.resolve()}")

# ==============================
# 2. DB INSERTION
# ==============================
print("\n📂 Importing into database...")

conn = sqlite3.connect("curriculum.db")
cur = conn.cursor()

cur.executescript("""
DROP TABLE IF EXISTS Strand;
DROP TABLE IF EXISTS Substrand;
DROP TABLE IF EXISTS Activity;

CREATE TABLE Strand (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
);

CREATE TABLE Substrand (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    strand_id INTEGER,
    name TEXT,
    UNIQUE(strand_id, name),
    FOREIGN KEY (strand_id) REFERENCES Strand(id)
);

CREATE TABLE Activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    substrand_id INTEGER,
    name TEXT,
    UNIQUE(substrand_id, name),
    FOREIGN KEY (substrand_id) REFERENCES Substrand(id)
);
""")

# --- Step 1: Insert Strands ---
start_time = time.perf_counter()
unique_strands = df["strand"].unique().tolist()
cur.executemany("INSERT INTO Strand (name) VALUES (?)", [(s,) for s in unique_strands])
strand_id_map = {
    s: i for s, i in zip(unique_strands, range(1, len(unique_strands) + 1))
}
elapsed = time.perf_counter() - start_time
print(f"✅ Inserted {len(unique_strands)} strands in {elapsed:.2f} seconds.")

# --- Step 2: Insert Substrands ---
start_time = time.perf_counter()
unique_pairs = df[["strand", "substrand"]].drop_duplicates().values.tolist()
cur.executemany(
    "INSERT INTO Substrand (strand_id, name) VALUES (?, ?)",
    [(strand_id_map[strand], substrand) for strand, substrand in unique_pairs],
)
substrand_id_map = {
    (strand, substrand): i
    for i, (strand, substrand) in enumerate(unique_pairs, start=1)
}
elapsed = time.perf_counter() - start_time
print(f"✅ Inserted {len(unique_pairs)} substrands in {elapsed:.2f} seconds.")

# --- Step 3: Insert Activities ---
start_time = time.perf_counter()
unique_triples = (
    df[["strand", "substrand", "activity"]].drop_duplicates().values.tolist()
)
cur.executemany(
    "INSERT INTO Activity (substrand_id, name) VALUES (?, ?)",
    [
        (substrand_id_map[(strand, substrand)], activity)
        for strand, substrand, activity in unique_triples
    ],
)
elapsed = time.perf_counter() - start_time
print(f"✅ Inserted {len(unique_triples)} activities in {elapsed:.2f} seconds.")

# Commit
conn.commit()
conn.close()

print("\n🎉 Import complete!")
