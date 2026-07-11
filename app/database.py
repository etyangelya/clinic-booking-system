from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool

from app.config import settings

_is_postgres = bool(settings.database_url and settings.database_url.startswith("postgresql"))
_is_sqlite = bool(settings.database_url and settings.database_url.startswith("sqlite"))

engine = create_engine(
    settings.database_url,
    poolclass=NullPool if _is_postgres else None,
    connect_args=(
        {"check_same_thread": False, "timeout": 30}
        if _is_sqlite
        else {"sslmode": "require"}
        if _is_postgres
        else {}
    ),
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
