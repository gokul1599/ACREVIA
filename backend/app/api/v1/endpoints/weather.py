"""
ACREVIA - Weather & Agrometeorological Risk Endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.models.farm import Farm
from backend.app.schemas.weather import FarmWeatherReportResponse
from backend.app.security.dependencies import get_current_user, verify_farm_access
from backend.app.integrations.weather_client import weather_client

router = APIRouter(tags=["Weather & Agro-Risk"])


@router.get("/farms/{farm_id}/weather", response_model=FarmWeatherReportResponse)
async def get_farm_weather(
    farm_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves real-time agrometeorological indicators and agro-climatic disease risk for a farm holding.
    """
    farm = verify_farm_access(farm_id=farm_id, user=current_user, db=db)
    weather_data = await weather_client.get_district_weather(farm.district)

    temp = weather_data.get("temperature", 28.0)
    humidity = weather_data.get("humidity", 65.0)
    precip = weather_data.get("precipitation", 0.0)
    wind = weather_data.get("wind_speed", 8.0)

    # Compute rule-based agronomic risk
    if humidity >= 80.0 and 22.0 <= temp <= 32.0:
        pest_risk = "HIGH"
        advisory = "High relative humidity combined with moderate temperature elevates risk of foliar fungal pathogens (e.g., Rice Blast, Cotton Cercospora Leaf Spot). Maintain field drainage and monitor lower canopy."
    elif humidity >= 65.0:
        pest_risk = "MODERATE"
        advisory = "Favorable conditions for sucking pests (Thrips, Aphids) and mild foliar spot incidence. Periodic scouting recommended."
    else:
        pest_risk = "LOW"
        advisory = "Low disease pressure observed under current ambient humidity levels."

    weather_risk = "HIGH" if precip > 25.0 else ("MODERATE" if precip > 5.0 else "LOW")

    return FarmWeatherReportResponse(
        farm_id=farm.id,
        district=farm.district,
        temperature=temp,
        humidity=humidity,
        precipitation=precip,
        wind_speed=wind,
        source=weather_data.get("source", "Open-Meteo"),
        pest_risk_level=pest_risk,
        weather_risk_level=weather_risk,
        advisory=advisory
    )
