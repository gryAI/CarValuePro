import os
import schedule
import time
from datetime import datetime
from dotenv import load_dotenv

from data_pipeline.extract import extract
from data_pipeline.transform import transform
from data_pipeline.load import extract_to_staging, transform_to_prod

load_dotenv()

entrypoint = os.getenv("CHROMEBROWSER_URL_ENTRY")


def run_pipeline(entrypoint, is_incremental=True, to_skip=500):
    # Define Static Inputs
    ui_time_stamp = str(datetime.now().date()).replace("-", "")
    ui_DB_NAME_STG = "staging"
    ui_DB_NAME_PRD = "production"
    ui_TBL_NAME_STG = f"raw_incremental_load_{ui_time_stamp}"
    ui_TBL_NAME_PRD = f"vehicle_data_prd"

    # Extract listings from website
    data = extract(entrypoint, is_incremental=is_incremental, to_skip=to_skip)

    # Load extracted data to the staging table in PostgreSQL
    extract_to_staging(
        DB_NAME=ui_DB_NAME_STG,
        TBL_NAME=ui_TBL_NAME_STG,
        data=data,
        is_incremental=is_incremental,
    )

    # Transform the data loaded into the staging table
    data = transform(
        DB_NAME=ui_DB_NAME_STG, TBL_NAME=ui_TBL_NAME_STG, is_incremental=is_incremental
    )

    # Load to production table
    transform_to_prod(
        DB_NAME=ui_DB_NAME_PRD,
        TBL_NAME=ui_TBL_NAME_PRD,
        data=data,
        is_incremental=is_incremental,
    )


# Schedule the pipeline to run every day at 12:01 AM
schedule.every().day.at("00:01").do(
    run_pipeline, entrypoint=entrypoint, is_incremental=True, to_skip=500
)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)

# if __name__ == "__main__":
#     run_pipeline(entrypoint=entrypoint, is_incremental=True, to_skip=500)
