import os

from dotenv import load_dotenv

from data_pipeline.extract import extract

load_dotenv

entrypoint = os.getenv("CHROMEBROWSER_URL_ENTRY")


def run_pipeline(entrypoint, is_incremental=False):
    # Extract listings from website
    extract(entrypoint, is_incremental=is_incremental)


if __name__ == "__main__":
    run_pipeline(entrypoint, is_incremental=False)
