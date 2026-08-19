# from pathlib import Path
import pandas as pd
from chembl_webresource_client.new_client import new_client

# Extracción del conjunto de datos

TARGET_ID_CHEMBL = "CHEMBL214"
ACTIVITY_TYPES = ["Ki", "IC50"]


def find_activities() -> pd.DataFrame:
    activity = new_client.activity.filter(
        target_chembl_id=TARGET_ID_CHEMBL,
        standard_type__in=ACTIVITY_TYPES,
    )
    return pd.DataFrame(activity)


df = find_activities()
print(df.info())

print(df.shape)
print(df.columns)
print(df["standard_type"].value_counts())
