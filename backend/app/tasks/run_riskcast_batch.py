"""
ACREVIA - Standalone Bounded Batch Script for Daily RiskCast Evaluations.
Option A Implementation: Validated per-tenant worker processing with isolated
transaction-local sessions and fail-closed context lifecycle.
"""

import asyncio
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.database.session import SessionLocal
from backend.app.database.rls import set_tenant_context, clear_tenant_context
from backend.app.models.farm import Farm, Plot
from backend.app.models.user import User
from backend.app.services.riskcast.risk_service import RiskCastService
from backend.app.core.logging import logger


async def evaluate_single_farm(farm_id: str) -> int:
    """
    Evaluates plots for a single farm within an isolated, tenant-scoped session.
    Enforces strict RLS boundaries and guarantees connection-pool context reset.
    """
    with SessionLocal() as db:
        try:
            # 1. Establish initial candidate tenant context
            set_tenant_context(db, tenant_id=farm_id, is_admin=False)
            farm = db.get(Farm, farm_id)
            if not farm or farm.is_archived:
                return 0

            owner = db.get(User, farm.owner_id)
            if not owner or not owner.is_active:
                return 0

            # 2. Establish fully authenticated tenant & owner context
            set_tenant_context(db, tenant_id=farm_id, user_id=owner.id, is_admin=False)

            evaluated_count = 0
            for plot in farm.plots:
                if plot.is_archived:
                    continue
                try:
                    await RiskCastService.evaluate_plot(plot_id=plot.id, current_user=owner, db=db)
                    evaluated_count += 1
                except Exception as e:
                    logger.error(f"Error evaluating plot {plot.id} for farm {farm_id}: {e}")
            db.commit()
            return evaluated_count
        except Exception as exc:
            db.rollback()
            logger.error(f"Batch evaluation failed for farm {farm_id}: {exc}")
            return 0
        finally:
            # 3. Non-negotiable teardown: Clear tenant context before returning connection to pool
            clear_tenant_context(db)


async def run_batch(target_farm_ids: Optional[List[str]] = None) -> int:
    """
    Executes bounded daily RiskCast evaluations across active farms.
    When target_farm_ids is provided, evaluates each farm in an isolated per-tenant session.
    When not provided, safely inspects registered farms under an isolated administrative dispatch query.
    """
    logger.info("Starting bounded RiskCast daily batch evaluation (Option A: Per-Tenant Isolation)...")
    farm_ids = target_farm_ids or []

    if not farm_ids:
        with SessionLocal() as db:
            try:
                farms = db.query(Farm.id).filter_by(is_archived=False).all()
                farm_ids = [f[0] for f in farms]
            finally:
                clear_tenant_context(db)

    total_evaluated = 0
    for fid in farm_ids:
        plots_evaluated = await evaluate_single_farm(fid)
        total_evaluated += plots_evaluated

    logger.info(f"RiskCast batch completed. Successfully evaluated {total_evaluated} active plots across {len(farm_ids)} farms.")
    return total_evaluated


if __name__ == "__main__":
    asyncio.run(run_batch())
