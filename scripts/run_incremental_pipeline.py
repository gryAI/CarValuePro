import os

from dotenv import load_dotenv
from datetime import datetime, timedelta

from data_pipeline.extract import extract
from data_pipeline.transform import transform
from data_pipeline.load import (
    get_db_creds,
    create_db_engine,
    check_table_exists,
    create_staging_table,
    extract_to_staging,
)

load_dotenv()


entrypoint = os.getenv("CHROMEBROWSER_URL_ENTRY")


def run_pipeline(entrypoint, is_incremental=True, to_skip=500):

    # Define Static Inputs
    ui_time_stamp = str(datetime.now().date()).replace("-", "")
    ui_DB_NAME_STG = "staging"
    ui_TBL_NAME = f"raw_incremental_load_{ui_time_stamp}"

    # Extract listings from website
    data = extract(entrypoint, is_incremental=is_incremental, to_skip=to_skip)

    # Load extracted data to the staging table in PostgreSQL
    extract_to_staging(
        DB_NAME=ui_DB_NAME_STG,
        TBL_NAME=ui_TBL_NAME,
        data=data,
        is_incremental=is_incremental,
    )

    # Transform the data loaded into the staging table
    transform(
        DB_NAME=ui_DB_NAME_STG, TBL_NAME=ui_TBL_NAME, is_incremental=is_incremental
    )


if __name__ == "__main__":
    # data = extract(entrypoint, is_incremental=True, to_skip=200)
    # time_stamp = str(datetime.now().date()).replace("-", "")
    # TBL_NAME = f"raw_incremental_load_{time_stamp}"
    # extract_to_staging(
    #     DB_NAME="CVP_FINAL", TBL_NAME=TBL_NAME, data=data, is_incremental=True
    # )

    run_pipeline(entrypoint=entrypoint, is_incremental=True, to_skip=500)
