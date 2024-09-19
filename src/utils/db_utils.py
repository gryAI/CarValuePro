import os
from dataclasses import dataclass

from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()


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
