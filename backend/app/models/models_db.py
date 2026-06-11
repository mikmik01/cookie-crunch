from sqlalchemy import String, Integer, Float, Text, ForeignKey, Date, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.db import Base
from datetime import datetime, date
from uuid import uuid4

def uuid() -> str:
    return str(uuid4())


class ScrapeRun(Base):
    __tablename__ = "scrape_runs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=uuid)
    source: Mapped[str] = mapped_column(String, nullable=False)
    scraped_for_date: Mapped[date] = mapped_column(Date, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now() , nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String, nullable=False)
    hero_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    issue_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    hero_stats: Mapped[list["HeroStatRow"]] = relationship(back_populates="scrape_run", cascade="all, delete-orphan")


class HeroStatRow(Base):
    __tablename__ = "hero_stats"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=uuid)
    scrape_run_id: Mapped[str] = mapped_column(ForeignKey("scrape_runs.id", ondelete="CASCADE"), nullable=False) 
    hero: Mapped[str] = mapped_column(String, nullable=False)
    rank_filter: Mapped[str] = mapped_column(String, nullable=False, index=True)
    rank: Mapped[int | None] = mapped_column(Integer)
    lane: Mapped[str | None] = mapped_column(String)
    tier: Mapped[str | None] = mapped_column(String)
    win_rate: Mapped[float | None] = mapped_column(Float)
    ban_rate: Mapped[float | None] = mapped_column(Float)
    pick_rate: Mapped[float | None] = mapped_column(Float)
    roles: Mapped[str | None] = mapped_column(Text)
    scrape_run: Mapped["ScrapeRun"] = relationship(back_populates="hero_stats")

