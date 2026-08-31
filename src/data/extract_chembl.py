# from pathlib import Path
import pandas as pd
from chembl_webresource_client.new_client import new_client
from pathlib import Path


TARGET_ID_CHEMBL = "CHEMBL214"
ACTIVITY_TYPES = ["Ki", "IC50"]


OUTPUT_DIR = Path("data/raw/chembl")
OUTPUT_FILE = OUTPUT_DIR / "chembl214_ki_ic50.parquet"


def find_activities() -> pd.DataFrame:
    activity = new_client.activity.filter(
        target_chembl_id=TARGET_ID_CHEMBL,
        standard_type__in=ACTIVITY_TYPES,
    )
    return pd.DataFrame(activity)


def data_save_to_raw(df: pd.DataFrame) -> None:
    df.to_parquet(
        OUTPUT_FILE,
        index=False,
    )


df = find_activities()
print(df.shape)
print(df.columns)

data_save_to_raw(df)
