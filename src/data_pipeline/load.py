import os
from dataclasses import dataclass

import pandas as pd
import psycopg2
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text


load_dotenv()


def extract_to_staging(
    DB_NAME: str, TBL_NAME: str, data: pd.DataFrame, is_incremental: bool
):
    engine = create_db_engine(DB_NAME)

    exists = check_table_exists(engine, TBL_NAME)
    if not exists:
        create_staging_table(engine, TBL_NAME)

    load_to_staging_table(engine, data, TBL_NAME)

    time_stamp = str(datetime.now().date()).replace("-", "")
    print(f"Incremental data for {time_stamp} has been loaded successfully!")


def transform_to_prod():
    pass


@dataclass
class DBSecrets:
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: str


def get_db_creds():
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")

    return DBSecrets(DB_USER, DB_PASS, DB_HOST, DB_PORT)


def create_db_engine(DB_NAME: str):
    secrets = get_db_creds()

    engine = create_engine(
        f"postgresql+psycopg2://{secrets.DB_USER}:{secrets.DB_PASS}@{secrets.DB_HOST}:{secrets.DB_PORT}/{DB_NAME}"
    )

    return engine


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

    print(f"Staging Table '{TBL_NAME}' created successfully.")


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
        detail_status VARCHAR(10),
        detail_color VARCHAR(20),
        detail_transmission VARCHAR(50),
        detail_mileage INT,
        detail_coding VARCHAR(20),
        detail_features VARCHAR(100),
        detail_price INT,
        additional_services VARCHAR(100),
        negotiation_and_test_drive VARCHAR(100),
        complete_listing_description VARCHAR(1000000)
        
    )
    """

    with engine.connect() as connection:
        connection.execute(text(query))
        connection.commit()

    print(f"Production Table '{TBL_NAME}' created successfully.")


def archive_prod_table(engine):
    now = datetime.now().date()
    yesterday = str(now - timedelta(days=1)).replace("-", "_")

    old_TBL_NAME = "car_data_production"
    new_TBL_NAME = "car_data_production_as_of_{yesterday}"

    query = f"ALTER TABLE {old_TBL_NAME} RENAME TO {new_TBL_NAME};"

    print(f"Production data as of {yesterday} has been archive successfully!")


def load_to_staging_table(engine, data, TBL_NAME):
    time_stamp = str(datetime.now().date()).replace("-", "")
    data.to_sql(TBL_NAME, engine, if_exists="replace", index=False)

    print(f"Incremental data for {time_stamp} has been loaded successfully!")
