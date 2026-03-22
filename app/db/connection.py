import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from app.utils.paths import repo_root


def get_engine() -> Engine:
    load_dotenv(repo_root() / ".env")
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set. Copy .env.example to .env and set DATABASE_URL."
        )
    return create_engine(url, future=True)
