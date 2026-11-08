"""
ACREVIA - Standalone Bounded Batch Script for Daily RiskCast Evaluations.
Can be triggered via external cron or scheduled CI/CD job.
"""

import asyncio
from backend.app.database.session import SessionLocal
from backend.app.models.farm import Farm, Plot
from backend.app.models.user import User
from backend.app.services.riskcast.risk_service import RiskCastService
from backend.app.core.logging import logger


async def run_batch():
    logger.info("Starting bounded RiskCast daily batch evaluation...")
    with SessionLocal() as db:
        farms = db.query(Farm).filter_by(is_archived=False).all()
        evaluated_count = 0
        for farm in farms:
            owner = db.get(User, farm.owner_id)
            if not owner:
                continue
            for plot in farm.plots:
                if plot.is_archived:
                    continue
                try:
                    await RiskCastService.evaluate_plot(plot_id=plot.id, current_user=owner, db=db)
                    evaluated_count += 1
                except Exception as e:
                    logger.error(f"Error evaluating plot {plot.id}: {e}")
        logger.info(f"RiskCast batch completed. Successfully evaluated {evaluated_count} active plots.")


if __name__ == "__main__":
    asyncio.run(run_batch())
