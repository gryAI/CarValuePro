import os
from dataclasses import dataclass
from datetime import datetime, timedelta

import pandas as pd
import psycopg2
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text

from utils.db_utils import create_db_engine
from utils.msc_utils import customize_logger

load_dotenv()


def extract_to_staging(
    DB_NAME: str, TBL_NAME: str, data: pd.DataFrame, is_incremental: bool
):
    # Load loggers
    if is_incremental:
        log_file, log_console, log_file_console = customize_logger(
            feature="load", subfeature="incremental"
        )
    else:
        log_file, log_console, log_file_console = customize_logger(
            feature="load", subfeature="full"
        )

    # Entry point for the extract to staging function

    log_file_console.info(f"Initiating: Loading process to {DB_NAME.upper()} DATABASE.")
    time_stamp = str(datetime.now().date()).replace("-", "")
    engine = create_db_engine(DB_NAME)

    exists = check_table_exists(engine, TBL_NAME)
    if not exists:
        create_staging_table(engine, TBL_NAME)
        log_file_console.info(
            f"Staging Database Table {TBL_NAME.upper()} has been created successfully."
        )

    load_to_staging_table(engine, data, TBL_NAME)

    if is_incremental:
        log_file_console.info(
            f"Exiting: Incremental data for {time_stamp} has been loaded to {TBL_NAME.upper()} TABLE in {DB_NAME.upper()} DATABASE successfully!"
        )
    else:
        log_file_console.info(
            f"Exiting: Full data as of {time_stamp} has been loaded to {TBL_NAME.upper()} TABLE in {DB_NAME.upper()} DATABASE successfully!"
        )


def transform_to_prod(
    DB_NAME: str, TBL_NAME: str, data: pd.DataFrame, is_incremental: bool
):
    # Load loggers
    if is_incremental:
        log_file, log_console, log_file_console = customize_logger(
            feature="load", subfeature="incremental"
        )
    else:
        log_file, log_console, log_file_console = customize_logger(
            feature="load", subfeature="full"
        )

    # Entry point for the transform to production function

    log_file_console.info(f"Initiating: Loading process to {DB_NAME.upper()} DATABASE.")
    time_stamp = str(datetime.now().date()).replace("-", "")
    engine = create_db_engine(DB_NAME)

    exists = check_table_exists(engine, TBL_NAME)

    if not exists:
        create_prod_table(engine, TBL_NAME)
        log_file_console.info(
            f"Production Database Table {TBL_NAME.upper()} has been created successfully."
        )

    if is_incremental:
        load_to_prod_table(engine, data, TBL_NAME)
        log_file_console.info(
            f"Incremental data for {time_stamp} has been loaded to {TBL_NAME.upper()} TABLE in {DB_NAME.upper()} DATABASE successfully!"
        )

    else:
        if exists:
            archive_prod_table(engine, TBL_NAME)
            log_file_console.info(
                f"Production Database Table {TBL_NAME.upper()} in {DB_NAME.upper()} DATABASE has been archived successfully!"
            )

            create_prod_table(engine, TBL_NAME)
            log_file_console.info(
                f"Production Database Table {TBL_NAME.upper()} has been created successfully."
            )

        load_to_prod_table(engine, data, TBL_NAME)
        log_file_console.info(
            f"Exiting: Full data as of {time_stamp} has been loaded to {TBL_NAME.upper()} TABLE in {DB_NAME.upper()} DATABASE successfully!"
        )


def check_table_exists(engine, TBL_NAME):
    inspector = inspect(engine)

    exists = inspector.has_table(TBL_NAME, schema="public")

    return exists


def create_staging_table(engine, TBL_NAME):
    query = f"""
    CREATE TABLE {TBL_NAME} (
        listing_id VARCHAR(10),
        dealer_id VARCHAR(6),
        listing_title VARCHAR(500),
        listing_price VARCHAR(50),
        listing_location VARCHAR(50),
        listing_url VARCHAR(500),
        detail_date_posted VARCHAR(50),
        detail_make VARCHAR(50),
        detail_model VARCHAR(50),
        detail_year VARCHAR(4),
        detail_status VARCHAR(10),
        detail_color VARCHAR(20),
        detail_transmission VARCHAR(50),
        detail_mileage VARCHAR(50),
        detail_coding VARCHAR(20),
        detail_features VARCHAR(100),
        detail_price VARCHAR(20),
        additional_services VARCHAR(100),
        negotiation_and_test_drive VARCHAR(100),
        complete_listing_description VARCHAR(1000000)

    );
    """

    with engine.connect() as connection:
        connection.execute(text(query))
        connection.commit()


def create_prod_table(engine, TBL_NAME):
    query = f"""
    CREATE TABLE {TBL_NAME} (
        listing_id VARCHAR(10),
        dealer_id VARCHAR(6),
        listing_title VARCHAR(500),
        listing_location VARCHAR(50),
        listing_url VARCHAR(500),
        detail_date_posted DATE,
        detail_make VARCHAR(50),
        detail_model VARCHAR(50),
        detail_year VARCHAR(4),
        detail_status VARCHAR(10),
        detail_color VARCHAR(20),
        detail_transmission VARCHAR(50),
        detail_mileage INT,
        detail_coding VARCHAR(20),
        detail_features VARCHAR(1000),
        detail_price INT,
        additional_services VARCHAR(1000),
        negotiation_and_test_drive VARCHAR(1000),
        complete_listing_description VARCHAR(1000000)
        
    )
    """

    with engine.connect() as connection:
        connection.execute(text(query))
        connection.commit()

    # print(f"Production Table '{TBL_NAME}' created successfully.")


def archive_prod_table(engine, TBL_NAME):
    now = datetime.now().date()
    yesterday = str(now - timedelta(days=1)).replace("-", "_")

    old_TBL_NAME = TBL_NAME
    new_TBL_NAME = f"{TBL_NAME}_as_of_{yesterday}"

    query = f"ALTER TABLE {old_TBL_NAME} RENAME TO {new_TBL_NAME};"

    with engine.connect() as connection:
        connection.execute(text(query))
        connection.commit()

    # print(f"Production data as of {yesterday} has been archived successfully!")


def load_to_staging_table(engine, data, TBL_NAME):
    time_stamp = str(datetime.now().date()).replace("-", "")
    data.to_sql(TBL_NAME, engine, if_exists="replace", index=False)

    # print(f"Incremental data for {time_stamp} has been loaded successfully!")


def load_to_prod_table(engine, data, TBL_NAME):
    time_stamp = str(datetime.now().date()).replace("-", "")
    data.to_sql(TBL_NAME, engine, if_exists="append", index=False)

    # print(f"Incremental data for {time_stamp} has been loaded successfully!")
