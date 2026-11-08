"""
ACREVIA - Crop Season Economics & Loss Evidence Service.
Pillar F: Cost of cultivation, gross revenues, unit margins, and cryptographically verified crop loss packages.
"""

from datetime import date, datetime, timezone
from decimal import Decimal
import hashlib
import json
from typing import Dict, Any, List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from backend.app.models.farm import Farm, Plot
from backend.app.models.crop import CropSeason
from backend.app.models.financial_ledger import FarmExpense, SaleTransaction
from backend.app.models.harvest_operations import HarvestSession, HarvestPlan
from backend.app.models.crop_economics import CropSeasonEconomics
from backend.app.models.evidence_package import CropLossEvidencePackage
from backend.app.models.weather_data import WeatherData
from backend.app.schemas.crop_economics import (
    CropSeasonEconomicsResponse,
    ExpenseCategoryBreakdown,
    EconomicsSummaryResponse,
)
from backend.app.schemas.evidence_package import (
    CropLossEvidencePackageCreate,
    CropLossEvidencePackageResponse,
)

CORE_EXPENSE_CATEGORIES = ["SEEDS", "FERTILIZERS", "PESTICIDES", "LABOUR", "MACHINERY"]


class EconomicsService:
    @staticmethod
    def calculate_crop_season_economics(db: Session, crop_season_id: str) -> EconomicsSummaryResponse:
        season = db.get(CropSeason, crop_season_id)
        if not season:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"CropSeason '{crop_season_id}' not found.",
            )

        crop_name = season.crop.name_en if season.crop else season.crop_id

        # 1. Aggregate Expenses
        expenses = list(db.scalars(select(FarmExpense).where(FarmExpense.crop_season_id == crop_season_id)).all())
        total_expenses = Decimal("0.00")
        category_totals: Dict[str, Decimal] = {}

        for exp in expenses:
            total_expenses += exp.amount
            cat = exp.category.upper()
            category_totals[cat] = category_totals.get(cat, Decimal("0.00")) + exp.amount

        # Calculate category percentages
        category_breakdown: List[ExpenseCategoryBreakdown] = []
        for cat, amt in category_totals.items():
            pct = ((amt / total_expenses) * Decimal("100.00")).quantize(Decimal("0.1")) if total_expenses > Decimal("0.00") else Decimal("0.0")
            category_breakdown.append(
                ExpenseCategoryBreakdown(
                    category=cat,
                    total_amount=amt,
                    percentage_of_total=pct,
                )
            )

        # Check completeness against core agricultural buckets
        recorded_core = set(category_totals.keys()).intersection(CORE_EXPENSE_CATEGORIES)
        missing_categories = [c for c in CORE_EXPENSE_CATEGORIES if c not in category_totals]
        completeness_pct = (Decimal(len(recorded_core)) / Decimal(len(CORE_EXPENSE_CATEGORIES)) * Decimal("100.00")).quantize(Decimal("0.01"))

        if completeness_pct >= Decimal("80.00"):
            completeness_badge = "COMPLETE"
        elif completeness_pct >= Decimal("40.00"):
            completeness_badge = "PARTIAL_DATA"
        else:
            completeness_badge = "MINIMAL_DATA"

        # 2. Aggregate Sales Transactions
        sales = list(db.scalars(select(SaleTransaction).where(SaleTransaction.crop_season_id == crop_season_id)).all())
        gross_revenue = Decimal("0.00")
        total_sold_quantity = Decimal("0.00")
        for s in sales:
            gross_revenue += s.net_amount  # Farmer's actual net realization after deductions
            total_sold_quantity += s.quantity_sold

        # 3. Aggregate Harvested Quantities
        harvest_sessions = list(db.scalars(select(HarvestSession).where(HarvestSession.crop_season_id == crop_season_id)).all())
        total_harvest_quantity = Decimal("0.00")
        unit = "QUINTAL"
        for h in harvest_sessions:
            total_harvest_quantity += h.harvested_quantity
            unit = h.unit

        # 4. Economic Metrics
        net_realization = (gross_revenue - total_expenses).quantize(Decimal("0.01"))

        cost_per_unit = Decimal("0.00")
        if total_harvest_quantity > Decimal("0.00"):
            cost_per_unit = (total_expenses / total_harvest_quantity).quantize(Decimal("0.01"))

        margin_denominator = total_sold_quantity if total_sold_quantity > Decimal("0.00") else total_harvest_quantity
        net_margin_per_unit = Decimal("0.00")
        if margin_denominator > Decimal("0.00"):
            net_margin_per_unit = (net_realization / margin_denominator).quantize(Decimal("0.01"))

        # 5. Upsert CropSeasonEconomics record
        econ_record = db.scalar(select(CropSeasonEconomics).where(CropSeasonEconomics.crop_season_id == crop_season_id))
        if not econ_record:
            econ_record = CropSeasonEconomics(
                crop_season_id=crop_season_id,
                total_expenses=total_expenses,
                gross_revenue=gross_revenue,
                net_realization=net_realization,
                total_harvest_quantity=total_harvest_quantity,
                total_sold_quantity=total_sold_quantity,
                unit=unit,
                cost_per_unit=cost_per_unit,
                net_margin_per_unit=net_margin_per_unit,
                data_completeness_pct=completeness_pct,
            )
            db.add(econ_record)
        else:
            econ_record.total_expenses = total_expenses
            econ_record.gross_revenue = gross_revenue
            econ_record.net_realization = net_realization
            econ_record.total_harvest_quantity = total_harvest_quantity
            econ_record.total_sold_quantity = total_sold_quantity
            econ_record.unit = unit
            econ_record.cost_per_unit = cost_per_unit
            econ_record.net_margin_per_unit = net_margin_per_unit
            econ_record.data_completeness_pct = completeness_pct
            econ_record.calculated_at = datetime.now(timezone.utc)

        db.commit()

        economic_disclaimers = [
            "Economic analyses reflect recorded cash expenses and realized transactions.",
            "Family labour and owned land rental values are excluded from basic A1 cash accounting.",
        ]
        if completeness_badge != "COMPLETE":
            economic_disclaimers.append(f"Incomplete records: Missing core categories {', '.join(missing_categories)}.")

        return EconomicsSummaryResponse(
            crop_season_id=crop_season_id,
            crop_name=crop_name,
            total_expenses=total_expenses,
            gross_revenue=gross_revenue,
            net_realization=net_realization,
            total_harvest_quantity=total_harvest_quantity,
            total_sold_quantity=total_sold_quantity,
            unit=unit,
            cost_per_unit=cost_per_unit,
            net_margin_per_unit=net_margin_per_unit,
            data_completeness_pct=completeness_pct,
            completeness_badge=completeness_badge,
            category_breakdown=category_breakdown,
            missing_categories=missing_categories,
            economic_disclaimers=economic_disclaimers,
        )

    @staticmethod
    def generate_crop_loss_evidence_package(
        db: Session,
        data: CropLossEvidencePackageCreate,
    ) -> CropLossEvidencePackageResponse:
        farm = db.get(Farm, data.farm_id)
        if not farm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Farm '{data.farm_id}' not found.",
            )

        plot = db.get(Plot, data.plot_id)
        if not plot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plot '{data.plot_id}' not found.",
            )

        season = db.get(CropSeason, data.crop_season_id)
        if not season:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"CropSeason '{data.crop_season_id}' not found.",
            )

        # Harvest plan vs actual
        plan = db.scalar(select(HarvestPlan).where(HarvestPlan.crop_season_id == data.crop_season_id))
        harvest_sessions = list(db.scalars(select(HarvestSession).where(HarvestSession.crop_season_id == data.crop_season_id)).all())
        actual_harvested = sum(h.harvested_quantity for h in harvest_sessions) if harvest_sessions else Decimal("0.00")
        planned_yield = plan.estimated_quantity_quintals if plan else Decimal("0.00")
        estimated_yield_loss = max(Decimal("0.00"), planned_yield - actual_harvested)

        # Build payload bundle
        payload = {
            "farm": {
                "id": farm.id,
                "name": farm.name,
                "district": farm.district,
                "state": farm.state,
                "total_acreage": float(farm.total_acreage),
            },
            "plot": {
                "id": plot.id,
                "name": plot.name,
                "acreage": float(plot.acreage),
            },
            "season": {
                "id": season.id,
                "crop_id": season.crop_id,
                "crop_name": season.crop.name_en if season.crop else season.crop_id,
                "sowing_date": str(season.sowing_date),
                "growth_stage": season.current_stage,
            },
            "incident": {
                "date": str(data.incident_date),
                "type": data.incident_type,
                "notes": data.notes,
            },
            "loss_assessment": {
                "planned_yield_quintals": float(planned_yield),
                "actual_realized_quintals": float(actual_harvested),
                "estimated_loss_quintals": float(estimated_yield_loss),
                "loss_percentage": round(float((estimated_yield_loss / planned_yield) * 100), 2) if planned_yield > 0 else 0.0,
            },
            "attestation": {
                "compliance_standard": "PMFBY_GOI_DISASTER_RELIEF_EVIDENCE",
                "authority": "ACREVIA Agricultural Risk & Climate Intelligence System",
                "issued_at": datetime.now(timezone.utc).isoformat(),
            },
        }

        # Compute SHA-256 integrity hash
        serialized_payload = json.dumps(payload, sort_keys=True)
        package_hash = hashlib.sha256(serialized_payload.encode("utf-8")).hexdigest()

        package = CropLossEvidencePackage(
            farm_id=data.farm_id,
            plot_id=data.plot_id,
            crop_season_id=data.crop_season_id,
            incident_date=data.incident_date,
            incident_type=data.incident_type,
            package_payload_json=serialized_payload,
            package_hash=package_hash,
        )
        db.add(package)
        db.commit()
        db.refresh(package)

        return CropLossEvidencePackageResponse(
            id=package.id,
            farm_id=package.farm_id,
            plot_id=package.plot_id,
            crop_season_id=package.crop_season_id,
            incident_date=package.incident_date,
            incident_type=package.incident_type,
            package_payload=payload,
            package_hash=package.package_hash,
            generated_at=package.generated_at,
        )
