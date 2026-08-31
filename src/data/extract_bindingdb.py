from pathlib import Path
import requests
from urllib3.util import response

BINDINDGDB_RELEASE = "202608"

OUTPUT_DIR = Path("data/raw/BINDINGDB")

BASE_URL = "https://www.bindingdb.org/rwd/bind/downloads"

FILE_NAME = f"BindingDB_BindingDB_Articles_{BINDINDGDB_RELEASE}_tsv.zip"

DOWNLOAD_URL = f"{BASE_URL}/{FILE_NAME}"
OUTPUT_FILE = OUTPUT_DIR / FILE_NAME

# Requests hacia la base de datos


def download_DB() -> Path:

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if OUTPUT_FILE.exists():
        print("File already exists")
        return OUTPUT_FILE

    with requests.get(
        DOWNLOAD_URL,
        stream=True,
        timeout=60,
    ) as response:
        response.raise_for_status()

        with OUTPUT_FILE.open("wb") as file:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    file.write(chunk)
    print(f"Saved to: {OUTPUT_DIR}")

    return OUTPUT_FILE


download_DB()
