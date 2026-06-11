import os
import time

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker


def build_database_url():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    db_host = os.getenv("DB_HOST", "db")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "appdb")
    db_user = os.getenv("DB_USER", "devops")
    db_password = os.getenv("DB_PASSWORD", "secret123")

    return (
        "postgresql://"
        f"{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )


SQLALCHEMY_DATABASE_URL = build_database_url()

connect_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def wait_for_database():
    for attempt in range(5):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return True
        except OperationalError:
            print(f"DB not ready (attempt {attempt + 1}/5), waiting 2s...")
            time.sleep(2)
    return False


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
