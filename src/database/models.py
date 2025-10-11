from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
	Boolean,
	CheckConstraint,
	Column,
	DateTime,
	Enum,
	ForeignKey,
	Integer,
	BigInteger,
	String,
	UniqueConstraint,
	Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


UserRole = Enum(
	"participant", "organizer", "admin",
	name="user_role",
)

CompetitionStatus = Enum(
	"draft", "active", "completed", "cancelled",
	name="competition_status",
)


class User(Base):
	__tablename__ = "users"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
	username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
	first_name: Mapped[str] = mapped_column(String(100), nullable=False)
	last_name: Mapped[str] = mapped_column(String(100), nullable=False)
	role: Mapped[str] = mapped_column(UserRole, nullable=False, default="participant")
	created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
	updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

	organized_competitions: Mapped[list["Competition"]] = relationship(back_populates="organizer", cascade="all, delete-orphan")
	participants: Mapped[list["Participant"]] = relationship(back_populates="user")


class Competition(Base):
	__tablename__ = "competitions"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	name: Mapped[str] = mapped_column(String(255), nullable=False)
	competition_code: Mapped[str] = mapped_column(String(16), unique=True, nullable=False, index=True)
	organizer_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
	status: Mapped[str] = mapped_column(CompetitionStatus, nullable=False, default="draft")
	created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
	start_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
	end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

	organizer: Mapped["User"] = relationship(back_populates="organized_competitions")
	competition_disciplines: Mapped[list["CompetitionDiscipline"]] = relationship(back_populates="competition", cascade="all, delete-orphan")
	scrambles: Mapped[list["Scramble"]] = relationship(back_populates="competition", cascade="all, delete-orphan")
	participants: Mapped[list["Participant"]] = relationship(back_populates="competition", cascade="all, delete-orphan")
	leaderboards: Mapped[list["Leaderboard"]] = relationship(back_populates="competition", cascade="all, delete-orphan")
	overall: Mapped[list["OverallLeaderboard"]] = relationship(back_populates="competition", cascade="all, delete-orphan")


class Discipline(Base):
	__tablename__ = "disciplines"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
	code: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
	attempts_count: Mapped[int] = mapped_column(Integer, nullable=False)
	average_calculation_type: Mapped[str] = mapped_column(String(32), nullable=False)
	dnf_threshold: Mapped[int] = mapped_column(Integer, nullable=False)
	max_time_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=10)

	competition_disciplines: Mapped[list["CompetitionDiscipline"]] = relationship(back_populates="discipline", cascade="all, delete-orphan")
	scrambles: Mapped[list["Scramble"]] = relationship(back_populates="discipline", cascade="all, delete-orphan")
	results: Mapped[list["Result"]] = relationship(back_populates="discipline")
	leaderboards: Mapped[list["Leaderboard"]] = relationship(back_populates="discipline")


class CompetitionDiscipline(Base):
	__tablename__ = "competition_disciplines"
	__table_args__ = (
		UniqueConstraint("competition_id", "discipline_id", name="uq_competition_discipline"),
	)

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	competition_id: Mapped[int] = mapped_column(ForeignKey("competitions.id", ondelete="CASCADE"), nullable=False)
	discipline_id: Mapped[int] = mapped_column(ForeignKey("disciplines.id", ondelete="CASCADE"), nullable=False)
	is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

	competition: Mapped["Competition"] = relationship(back_populates="competition_disciplines")
	discipline: Mapped["Discipline"] = relationship(back_populates="competition_disciplines")


class Scramble(Base):
	__tablename__ = "scrambles"
	__table_args__ = (
		UniqueConstraint("competition_id", "discipline_id", "attempt_number", name="uq_scramble_attempt"),
		Index("ix_scrambles_comp_disc", "competition_id", "discipline_id"),
	)

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	competition_id: Mapped[int] = mapped_column(ForeignKey("competitions.id", ondelete="CASCADE"), nullable=False)
	discipline_id: Mapped[int] = mapped_column(ForeignKey("disciplines.id", ondelete="CASCADE"), nullable=False)
	attempt_number: Mapped[int] = mapped_column(Integer, nullable=False)
	file_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
	file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
	uploaded_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

	competition: Mapped["Competition"] = relationship(back_populates="scrambles")
	discipline: Mapped["Discipline"] = relationship(back_populates="scrambles")


class Participant(Base):
	__tablename__ = "participants"
	__table_args__ = (
		UniqueConstraint("competition_id", "user_id", name="uq_participant_unique"),
		Index("ix_participants_comp_user", "competition_id", "user_id"),
	)

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	competition_id: Mapped[int] = mapped_column(ForeignKey("competitions.id", ondelete="CASCADE"), nullable=False)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
	registration_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

	competition: Mapped["Competition"] = relationship(back_populates="participants")
	user: Mapped["User"] = relationship(back_populates="participants")
	results: Mapped[list["Result"]] = relationship(back_populates="participant", cascade="all, delete-orphan")


class Result(Base):
	__tablename__ = "results"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	participant_id: Mapped[int] = mapped_column(ForeignKey("participants.id", ondelete="CASCADE"), nullable=False)
	discipline_id: Mapped[int] = mapped_column(ForeignKey("disciplines.id", ondelete="CASCADE"), nullable=False)

	attempt_1_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
	attempt_1_dnf: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
	attempt_2_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
	attempt_2_dnf: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
	attempt_3_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
	attempt_3_dnf: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
	attempt_4_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
	attempt_4_dnf: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
	attempt_5_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
	attempt_5_dnf: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

	average_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
	average_dnf: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
	best_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
	submitted_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
	updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

	participant: Mapped["Participant"] = relationship(back_populates="results")
	discipline: Mapped["Discipline"] = relationship(back_populates="results")

	__table_args__ = (
		UniqueConstraint("participant_id", "discipline_id", name="uq_results_participant_discipline"),
		Index("ix_results_participant_discipline", "participant_id", "discipline_id"),
		CheckConstraint(
			"attempt_1_time >= 0 OR attempt_1_time IS NULL",
			name="ck_result_attempt_1_time_non_negative",
		),
	)


class Leaderboard(Base):
	__tablename__ = "leaderboards"
	__table_args__ = (
		UniqueConstraint("competition_id", "discipline_id", "user_id", name="uq_leaderboard_unique"),
		Index("ix_leaderboards_comp_disc", "competition_id", "discipline_id"),
	)

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	competition_id: Mapped[int] = mapped_column(ForeignKey("competitions.id", ondelete="CASCADE"), nullable=False)
	discipline_id: Mapped[int] = mapped_column(ForeignKey("disciplines.id", ondelete="CASCADE"), nullable=False)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
	position: Mapped[int] = mapped_column(Integer, nullable=False)
	average_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
	average_dnf: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
	best_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
	points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
	calculated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

	competition: Mapped["Competition"] = relationship(back_populates="leaderboards")
	discipline: Mapped["Discipline"] = relationship(back_populates="leaderboards")
	user: Mapped["User"] = relationship()


class OverallLeaderboard(Base):
	__tablename__ = "overall_leaderboard"
	__table_args__ = (
		UniqueConstraint("competition_id", "user_id", name="uq_overall_unique"),
		Index("ix_overall_competition", "competition_id"),
	)

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	competition_id: Mapped[int] = mapped_column(ForeignKey("competitions.id", ondelete="CASCADE"), nullable=False)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
	total_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
	disciplines_participated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
	position: Mapped[int] = mapped_column(Integer, nullable=False)
	calculated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

	competition: Mapped["Competition"] = relationship(back_populates="overall")
	user: Mapped["User"] = relationship()
