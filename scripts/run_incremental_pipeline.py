import os

from dotenv import load_dotenv

from data_pipeline.extract import extract

load_dotenv

entrypoint = os.getenv("CHROMEBROWSER_URL_ENTRY")


def run_pipeline(entrypoint, is_incremental=True, to_skip=0):
    # Extract listings from website
    extract(entrypoint, is_incremental=is_incremental, to_skip=to_skip)


if __name__ == "__main__":
    run_pipeline(entrypoint, is_incremental=True, to_skip=1000)
