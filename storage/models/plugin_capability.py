from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from storage.models.base import Base


class PluginCapabilityRecord(Base):
    __tablename__ = "plugin_capabilities"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    plugin_name: Mapped[str] = mapped_column(String(64), ForeignKey("plugins.name"))
    capability: Mapped[str] = mapped_column(String(128))
