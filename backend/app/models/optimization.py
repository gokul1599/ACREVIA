"""
ACREVIA - Agricultural Resource Optimization Models (Pillar C: ACREVIA Optimize).
Stores constrained resource optimization formulations and mathematical solver outputs.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin


class OptimizationProblem(Base, TimestampMixin):
    __tablename__ = "optimization_problems"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farm_id: Mapped[str] = mapped_column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), index=True, nullable=False)
    plot_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("plots.id", ondelete="SET NULL"), nullable=True, index=True)

    problem_type: Mapped[str] = mapped_column(String(50), nullable=False)  # WATER_ALLOCATION, INPUT_BUDGET_ALLOCATION, IRRIGATION_WINDOW
    objective_type: Mapped[str] = mapped_column(String(50), nullable=False)  # MAXIMIZE_WATER_PRODUCTIVITY, MINIMIZE_STRESS, MINIMIZE_COST

    decision_variables_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    hard_constraints_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    soft_constraints_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="PENDING", nullable=False)  # PENDING, SOLVED, INFEASIBLE, FAILED

    # Relationships
    farm: Mapped["Farm"] = relationship("Farm")
    result: Mapped[Optional["OptimizationResult"]] = relationship("OptimizationResult", back_populates="problem", uselist=False, cascade="all, delete-orphan")


class OptimizationResult(Base, TimestampMixin):
    __tablename__ = "optimization_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    problem_id: Mapped[str] = mapped_column(String(36), ForeignKey("optimization_problems.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)

    feasibility_status: Mapped[str] = mapped_column(String(30), nullable=False)  # FEASIBLE, INFEASIBLE
    selected_solution_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    alternative_solutions_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    conflicting_constraints_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    trade_off_analysis_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    solver_name: Mapped[str] = mapped_column(String(100), nullable=False)  # SIMPLEX_BOUNDED_LP, PRIORITY_QUEUE_ALLOCATOR
    solved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    problem: Mapped["OptimizationProblem"] = relationship("OptimizationProblem", back_populates="result")
