from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from storage.models.base import Base
import storage.models  # noqa: F401

_ENGINE = None
_SESSION_FACTORY = None

def init_db(force: bool = False, database_url: str | None = None) -> None:
    global _ENGINE, _SESSION_FACTORY
    if _ENGINE is not None and not force:
        return
    url = database_url or os.getenv("AWE_DATABASE_URL", "sqlite:///./awe.db")
    _ENGINE = create_engine(url, future=True)
    _SESSION_FACTORY = sessionmaker(bind=_ENGINE, class_=Session, expire_on_commit=False)
    if force:
        Base.metadata.drop_all(_ENGINE)
    Base.metadata.create_all(_ENGINE)


def get_session() -> Session:
    if _SESSION_FACTORY is None:
        init_db()
    return _SESSION_FACTORY()
