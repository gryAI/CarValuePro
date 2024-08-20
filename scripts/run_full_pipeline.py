import os

from dotenv import load_dotenv

from data_pipeline.full_pipeline.extract import extract

load_dotenv

entrypoint = os.getenv("CHROMEBROWSER_URL_ENTRY")


def run_pipeline(entrypoint):
    # Extract listings from website
    extract(entrypoint)


if __name__ == "__main__":
    run_pipeline(entrypoint)
