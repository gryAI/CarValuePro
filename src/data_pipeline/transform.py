import ast
import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta

import pandas as pd
from cleantext import clean
from dotenv import load_dotenv

from utils.utils import get_logger, customize_logger
from data_pipeline.load import get_db_creds, create_db_engine

load_dotenv()


def transform(DB_NAME, TBL_NAME: str, is_incremental: bool):

    # Load loggers
    if is_incremental:
        log_file, log_console, log_file_console = customize_logger(
            feature="transform", subfeature="incremental"
        )
    else:
        log_file, log_console, log_file_console = customize_logger(
            feature="transform", subfeature="full"
        )

    # Load data
    engine = create_db_engine(DB_NAME)
    query = f"SELECT * FROM {TBL_NAME};"
    data = pd.read_sql(query, engine)

    # Load the list of words to be removed from the listing title from the `.env` file.
    words_to_remove = os.getenv("WORDS_TO_REMOVE").split(",")

    # Entry point for transformation
    data = transform_listing_title(data, "listing_title", words_to_remove)

    data = transform_listing_location(data, "listing_location")

    pattern = r"Posted on "
    data = transform_date_posted(data, "detail_date_posted", pattern)

    pattern = r"km|,"
    data = transform_mileage(data, "detail_mileage", pattern)

    pattern = r"₱ |,"
    data = transform_price(data, "detail_price", pattern)

    pattern = r"[\r\n\t]+|\s{2,}"
    data = transform_complete_desc(data, "complete_listing_description", pattern)

    pattern = pattern = r'[{}"]'
    list_cols = ["negotiation_and_test_drive", "detail_features", "additional_services"]
    data = transform_list_cols(data, list_cols, pattern)

    drop_cols = ["listing_price"]
    data = drop_columns(data, drop_cols)

    # Save data
    save_data(data)


def remove_words(text: str, words: list):
    tokens = text.split()
    filtered_tokens = [word for word in tokens if word.lower() not in words]

    return " ".join(filtered_tokens)


def transform_listing_title(df: pd.DataFrame, col: str, words: list):
    df[col] = df[col].apply(lambda x: clean(x, no_emoji=True))
    df[col] = df[col].apply(lambda x: remove_words(x, words))

    return df


def transform_listing_location(df: pd.DataFrame, col: str):
    df[col] = df[col].apply(lambda x: x.strip())

    return df


# pattern = r"Posted on "
def transform_date_posted(df: pd.DataFrame, col: str, pattern: str):
    df[col] = df[col].apply(lambda x: re.sub(pattern, "", x))
    df[col] = pd.to_datetime(df[col], dayfirst=True)

    return df


# pattern = r"km|,"
def transform_mileage(df: pd.DataFrame, col: str, pattern: str):
    df[col] = df[col].apply(lambda x: -1 if pd.isna(x) else re.sub(pattern, "", x))
    df[col] = df[col].apply(lambda x: -2 if x == "N/A" else int(x))

    return df


# pattern = r"₱ |,"
def transform_price(df: pd.DataFrame, col: str, pattern: str):
    df[col] = df[col].apply(lambda x: int(re.sub(pattern, "", x)))
    df[col] = df[col].astype("int")

    return df


# pattern = r"[\r\n\t]+|\s{2,}"
def transform_complete_desc(df: pd.DataFrame, col: str, pattern: str):
    df[col] = df[col].apply(
        lambda x: "" if pd.isna(x) else re.sub(pattern, "", x).strip()
    )

    return df


# pattern = r'{|}|"'
def transform_list_cols(df: pd.DataFrame, cols: list, pattern: str):
    for col in cols:
        # Step 1: Remove unwanted characters using regex
        df[col] = df[col].apply(
            lambda x: re.sub(pattern, "", x) if isinstance(x, str) else x
        )
        # Step 2: Convert string representation to actual lists
        df[col] = df[col].apply(
            lambda x: x.strip("[]").split(",") if isinstance(x, str) else x
        )
        # Step 3: Clean empty items from lists
        df[col] = df[col].apply(lambda x: [item for item in x if item])

    return df


def drop_columns(df: pd.DataFrame, cols: list):
    df.drop(columns=cols, inplace=True)

    return df


def save_data(df):
    time_stamp = str(datetime.now().date())
    file_path = f"data/processed_data/full_load_processed_data-{time_stamp}.csv"
    df.to_csv(file_path, index=False)


if __name__ == "__main__":
    print("|==============================|")
    print("|           pipeline           |")
    print("|              |               |")
    print("|         transform.py         |")
    print("|==============================|")

    transform(is_incremental=True)
