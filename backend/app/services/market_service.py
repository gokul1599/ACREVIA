"""
ACREVIA - Agricultural Market Intelligence Service.
Pillar B: Ingestion normalization, Agmarknet/e-NAM adapters, and comparative net realization across Telangana mandis.
"""

from datetime import date, datetime, timezone, timedelta
from decimal import Decimal
import math
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy import select, desc
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.app.models.farm import Plot
from backend.app.models.geo_spatial import PlotGeometry
from backend.app.models.market_intelligence import MarketLocation, MarketCommodity, MarketPriceObservation
from backend.app.schemas.market_intelligence import (
    MarketComparisonItem,
    MarketCompareResponse,
)

# Reference Mandi Coordinates in Telangana
DEFAULT_MANDIS = [
    {
        "market_code": "TEL_WGL_ENUMAMULA",
        "market_name": "Warangal (Enumamula)",
        "district": "Warangal",
        "state": "Telangana",
        "latitude": Decimal("17.968900"),
        "longitude": Decimal("79.594100"),
    },
    {
        "market_code": "TEL_KHM_KHAMMAM",
        "market_name": "Khammam Mandi",
        "district": "Khammam",
        "state": "Telangana",
        "latitude": Decimal("17.247300"),
        "longitude": Decimal("80.151400"),
    },
    {
        "market_code": "TEL_NLG_SURYAPET",
        "market_name": "Suryapet Market Yard",
        "district": "Suryapet",
        "state": "Telangana",
        "latitude": Decimal("17.140800"),
        "longitude": Decimal("79.623600"),
    },
    {
        "market_code": "TEL_KRM_KARIMNAGAR",
        "market_name": "Karimnagar APMC",
        "district": "Karimnagar",
        "state": "Telangana",
        "latitude": Decimal("18.438600"),
        "longitude": Decimal("79.128800"),
    },
    {
        "market_code": "TEL_ADB_ADILABAD",
        "market_name": "Adilabad Cotton Yard",
        "district": "Adilabad",
        "state": "Telangana",
        "latitude": Decimal("19.664100"),
        "longitude": Decimal("78.532000"),
    },
]

# Canonical Telangana Commodities and Benchmark Baseline Rates
DEFAULT_COMMODITIES = [
    {"commodity_name": "Cotton (Kapas)", "canonical_crop_id": "cotton", "variety_name": "Medium/Long Staple", "grade": "FAQ"},
    {"commodity_name": "Paddy (Dhan) - Common", "canonical_crop_id": "rice", "variety_name": "Grade A / BPT", "grade": "FAQ"},
    {"commodity_name": "Red Chilli - Teja", "canonical_crop_id": "chilli", "variety_name": "Teja / Deluxe", "grade": "Premium"},
]

DEFAULT_BENCHMARKS = {
    "cotton": {"min": Decimal("7100.00"), "max": Decimal("7750.00"), "modal": Decimal("7450.00")},
    "rice": {"min": Decimal("2203.00"), "max": Decimal("2350.00"), "modal": Decimal("2280.00")},
    "chilli": {"min": Decimal("14500.00"), "max": Decimal("21000.00"), "modal": Decimal("18200.00")},
}


class MarketService:
    @staticmethod
    def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Computes great-circle distance between two GPS coordinates in kilometers."""
        r = 6371.0
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return round(r * c, 1)

    @classmethod
    def seed_reference_data_if_empty(cls, db: Session):
        """Ensures reference mandis and commodities are available in the database."""
        existing_markets = db.scalars(select(MarketLocation)).all()
        if not existing_markets:
            for m in DEFAULT_MANDIS:
                db.add(MarketLocation(**m))
            db.commit()

        existing_commodities = db.scalars(select(MarketCommodity)).all()
        if not existing_commodities:
            for c in DEFAULT_COMMODITIES:
                db.add(MarketCommodity(**c))
            db.commit()

        # Seed initial price observations if none exist for today
        today = date.today()
        existing_obs = db.scalars(select(MarketPriceObservation)).first()
        if not existing_obs:
            markets = db.scalars(select(MarketLocation)).all()
            commodities = db.scalars(select(MarketCommodity)).all()
            for m in markets:
                for c in commodities:
                    rates = DEFAULT_BENCHMARKS.get(c.canonical_crop_id, {"min": Decimal("2000.00"), "max": Decimal("3000.00"), "modal": Decimal("2500.00")})
                    # Adjust slightly by market district
                    dist_offset = Decimal(str(len(m.district) % 5 * 10))
                    obs = MarketPriceObservation(
                        market_id=m.id,
                        commodity_id=c.id,
                        min_price=rates["min"] + dist_offset,
                        max_price=rates["max"] + dist_offset,
                        modal_price=rates["modal"] + dist_offset,
                        price_unit="INR_PER_QUINTAL",
                        arrival_quantity_quintals=Decimal("450.00"),
                        observation_date=today,
                        source_provider="AGMARKNET",
                    )
                    db.add(obs)
            db.commit()

    @classmethod
    def get_market_prices(
        cls,
        db: Session,
        canonical_crop_id: Optional[str] = None,
        district: Optional[str] = None,
        limit: int = 50,
    ) -> List[MarketPriceObservation]:
        cls.seed_reference_data_if_empty(db)

        query = (
            select(MarketPriceObservation)
            .join(MarketLocation, MarketPriceObservation.market_id == MarketLocation.id)
            .join(MarketCommodity, MarketPriceObservation.commodity_id == MarketCommodity.id)
        )
        if canonical_crop_id:
            query = query.where(MarketCommodity.canonical_crop_id == canonical_crop_id.lower())
        if district:
            query = query.where(MarketLocation.district.ilike(f"%{district}%"))

        query = query.order_by(desc(MarketPriceObservation.observation_date), desc(MarketPriceObservation.modal_price)).limit(limit)
        return list(db.scalars(query).all())

    @classmethod
    def compare_market_realizations(
        cls,
        db: Session,
        canonical_crop_id: str,
        quantity_quintals: Decimal,
        plot_id: Optional[str] = None,
    ) -> MarketCompareResponse:
        cls.seed_reference_data_if_empty(db)

        if quantity_quintals <= Decimal("0.00"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity must be strictly greater than zero quintals.",
            )

        # Determine origin coordinates (from plot geometry or Warangal default)
        origin_lat = 17.9689
        origin_lon = 79.5941

        if plot_id:
            geom = db.scalar(select(PlotGeometry).where(PlotGeometry.plot_id == plot_id))
            if geom and geom.centroid_latitude and geom.centroid_longitude:
                origin_lat = float(geom.centroid_latitude)
                origin_lon = float(geom.centroid_longitude)

        # Query all latest observations for this canonical crop
        commodities = list(db.scalars(select(MarketCommodity).where(MarketCommodity.canonical_crop_id == canonical_crop_id.lower())).all())
        if not commodities:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Commodity '{canonical_crop_id}' not found in market catalogue.",
            )

        commodity_ids = [c.id for c in commodities]
        observations = list(
            db.scalars(
                select(MarketPriceObservation)
                .where(MarketPriceObservation.commodity_id.in_(commodity_ids))
                .order_by(desc(MarketPriceObservation.observation_date))
            ).all()
        )

        comparisons: List[MarketComparisonItem] = []
        seen_markets = set()

        for obs in observations:
            if obs.market_id in seen_markets:
                continue
            seen_markets.add(obs.market_id)
            market = obs.market

            dist = cls.haversine_distance_km(
                origin_lat, origin_lon, float(market.latitude), float(market.longitude)
            )

            # Economic cost modeling:
            # Transport cost: ₹30 base loading per quintal + ₹1.5 per km per quintal
            rate_per_km_qtl = Decimal("1.50")
            base_loading_qtl = Decimal("30.00")
            transport_per_qtl = base_loading_qtl + (Decimal(str(dist)) * rate_per_km_qtl)
            total_transport = (transport_per_qtl * quantity_quintals).quantize(Decimal("0.01"))

            # Mandi cess: standard 1% of gross value
            gross_value = (obs.modal_price * quantity_quintals).quantize(Decimal("0.01"))
            mandi_cess = (gross_value * Decimal("0.01")).quantize(Decimal("0.01"))

            # Handling charges (hamali, weighing): ~₹15 per quintal
            handling_charges = (Decimal("15.00") * quantity_quintals).quantize(Decimal("0.01"))

            total_deductions = total_transport + mandi_cess + handling_charges
            net_realization = (gross_value - total_deductions).quantize(Decimal("0.01"))
            effective_rate = (net_realization / quantity_quintals).quantize(Decimal("0.01"))

            comparisons.append(
                MarketComparisonItem(
                    market_id=market.id,
                    market_name=market.market_name,
                    district=market.district,
                    distance_km=dist,
                    modal_price_per_quintal=obs.modal_price,
                    min_price_per_quintal=obs.min_price,
                    max_price_per_quintal=obs.max_price,
                    gross_value=gross_value,
                    estimated_transport_cost=total_transport,
                    estimated_mandi_cess=mandi_cess,
                    estimated_handling_charges=handling_charges,
                    estimated_net_realization=net_realization,
                    effective_rate_per_quintal=effective_rate,
                    observation_date=obs.observation_date,
                )
            )

        # Sort comparisons by estimated net realization descending
        comparisons.sort(key=lambda x: x.estimated_net_realization, reverse=True)

        return MarketCompareResponse(
            canonical_crop_id=canonical_crop_id.lower(),
            quantity_quintals=quantity_quintals,
            plot_id=plot_id,
            comparisons=comparisons,
        )

    @classmethod
    async def sync_datagov_prices(
        cls,
        commodity: Optional[str] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Ingests live official Agmarknet mandi arrivals and modal prices from data.gov.in."""
        from backend.app.integrations.datagov_client import datagov_client
        return await datagov_client.fetch_telangana_mandi_prices(commodity=commodity, limit=limit)
