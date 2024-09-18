import os

from dotenv import load_dotenv

from data_pipeline.extract import extract
from data_pipeline.load import (
    get_db_creds,
    create_db_engine,
    create_db_connection,
    check_table_exists,
    create_staging_table,
)

load_dotenv()

entrypoint = os.getenv("CHROMEBROWSER_URL_ENTRY")


def run_pipeline(entrypoint, is_incremental=False):
    # Extract listings from website
    extract(entrypoint, is_incremental=is_incremental)


if __name__ == "__main__":
    run_pipeline(entrypoint, is_incremental=False)
