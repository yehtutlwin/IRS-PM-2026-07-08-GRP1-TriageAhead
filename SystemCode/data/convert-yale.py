"""Task F day-1: convert the Yale .rdata download to Parquet once (columnar; the
experiments read only the columns they touch). Types are normalised here so no
experiment repeats the pd.to_numeric dance: esi -> Int8 (NaN kept), cc_* and PMH
flags -> Int8 0/1, meds_* -> Int16 counts, vitals -> float. Run after
data/download-yale.sh; needs pip install pyreadr pandas pyarrow."""
import os, sys, time
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
SRC, OUT = os.path.join(HERE, "yale_ed_visits.rdata"), os.path.join(HERE, "yale_ed_visits.parquet")
t = time.time()
import pyreadr
df = next(iter(pyreadr.read_r(SRC).values()))
print(f"loaded {df.shape} in {time.time()-t:.0f}s")
df["esi"] = pd.to_numeric(df["esi"], errors="coerce").astype("Int8")
for c in df.columns:
    if c.startswith("cc_") or c.startswith("meds_"):
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype("Int16" if c.startswith("meds_") else "Int8")
    elif c.startswith("triage_vital_"):
        df[c] = pd.to_numeric(df[c], errors="coerce").astype("float32")
    elif df[c].dtype == object and df[c].dropna().isin(["0", "1", 0, 1]).all():
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype("Int8")
df.to_parquet(OUT, index=False)
print(f"wrote {OUT} ({os.path.getsize(OUT)//1_000_000} MB) in {time.time()-t:.0f}s")
