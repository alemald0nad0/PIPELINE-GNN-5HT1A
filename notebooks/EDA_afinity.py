# %%
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path

# %%
DATA_DIR = Path("data/raw")

DATA_CHEMBL = DATA_DIR / "chembl" / "chembl214_ki_ic50.parquet"

BINDINGDB_DIR = DATA_DIR / "BINDINGDB"
PDSP_DIR = DATA_DIR / "PDSP"

# %%
data_chembl = pd.read_parquet(DATA_CHEMBL)
data_chembl
data_chembl.info()

# %%
# ¿Cuántas moléculas hay?

print(data_chembl["canonical_smiles"].value_counts())

print(data_chembl["canonical_smiles"].duplicated)
# %%
