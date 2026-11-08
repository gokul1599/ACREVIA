# ACREVIA — Scheduled Processing & Bounded Worker Architecture
## Operational Guide for Automated Daily Agrometeorological & Risk Evaluations

---

## 1. Architectural Philosophy: Bounded Execution vs. Long-Running Daemons

In cloud serverless environments (e.g., Vercel Functions + Neon PostgreSQL), running unconstrained, infinite-loop background daemons is an anti-pattern that leads to memory leaks, connection starvation, and unexpected billing spikes.

ACREVIA adopts a **bounded, idempotent batch processing model**.

```
+-----------------------------------------------------------------------------------+
|                           CRON / SCHEDULER DISPATCH                               |
|   - Triggered every 6 hours (e.g. 00:00, 06:00, 12:00, 18:00 IST)                 |
|   - Invokes Bounded CLI Task: `python -m backend.app.tasks.scheduled_riskcast`    |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                         IDEMPOTENT BATCH RUNNER                                   |
|   1. Query all active farms with unarchived plots                                 |
|   2. Group plots by district centroid to batch Open-Meteo fetches                 |
|   3. Ingest fresh WeatherData (observation + 72h forecast)                        |
|   4. Evaluate active RiskRules for each active CropSeason                         |
|   5. Compute SHA-256 deduplication key for potential alerts                       |
|   6. Commit batch transaction and gracefully exit                                 |
+-----------------------------------------------------------------------------------+
```

---

## 2. Command-Line Batch Task Script

To enable standalone automated cron execution, ACREVIA provides a dedicated task script:
`backend/app/tasks/run_riskcast_batch.py`

```python
"""
ACREVIA - Standalone Bounded Batch Script for Daily RiskCast Evaluations.
"""
import asyncio
from backend.app.database.session import SessionLocal
from backend.app.models.farm import Farm, Plot
from backend.app.models.crop import CropSeason
from backend.app.services.riskcast.risk_service import RiskCastService
from backend.app.core.logging import logger

async def run_batch():
    logger.info("Starting bounded RiskCast daily batch evaluation...")
    with SessionLocal() as db:
        farms = db.query(Farm).filter_by(is_archived=False).all()
        for farm in farms:
            for plot in farm.plots:
                if plot.is_archived:
                    continue
                try:
                    await RiskCastService.evaluate_plot(plot_id=plot.id, current_user=farm.owner, db=db)
                except Exception as e:
                    logger.error(f"Error evaluating plot {plot.id}: {e}")
    logger.info("RiskCast batch completed successfully.")

if __name__ == "__main__":
    asyncio.run(run_batch())
```

---

## 3. Recommended Production Schedule (Telangana Local Time - IST)

| Time (IST) | Scheduled Purpose | Execution Timeout |
|:---|:---|:---|
| **05:30 AM** | Morning Dew & Overnight Leaf Wetness Accumulation Evaluation | 60 seconds |
| **11:30 AM** | Midday Temperature Spike & Sucking Pest (Thrips/Whitefly) Evaluation | 60 seconds |
| **05:30 PM** | Evening Humidity Recovery & Fungal Spore Inoculation Window Check | 60 seconds |
| **11:30 PM** | Night-time Rainfall & Water Stagnation Aggregation | 60 seconds |
