"""
ACREVIA - Database Initialization & Seed Scripts.
Ensures core roles and supported crops are present upon deployment.
"""

from typing import Optional
from sqlalchemy.orm import Session
from backend.app.database.base import Base
from backend.app.database.session import engine as default_engine, SessionLocal as default_session_factory
from backend.app.models.user import Role
from backend.app.models.crop import Crop


def _seed_data(session: Session):
    """Seeds baseline roles and target crops if not present."""
    # 1. Seed System Roles
    roles_data = [
        ("FARMER", "Smallholder farmer or cultivator managing farms and plots"),
        ("AGRICULTURAL_EXPERT", "KVK or university agronomist reviewing foliar diagnoses"),
        ("RESEARCHER", "Agricultural research scientist studying pathology patterns"),
        ("ADMIN", "Platform administrator managing system security and operations")
    ]
    for role_id, desc in roles_data:
        existing = session.get(Role, role_id)
        if not existing:
            session.add(Role(id=role_id, description=desc))

    # 2. Seed Telangana Target Crops
    crops_data = [
        ("cotton", "Cotton", "పత్తి", "कपास", "Gossypium hirsutum"),
        ("rice", "Rice / Paddy", "వరి", "चावल / धान", "Oryza sativa"),
        ("chilli", "Chilli", "మిరప", "मिर्च", "Capsicum annuum")
    ]
    for cid, en, te, hi, sci in crops_data:
        existing = session.get(Crop, cid)
        if not existing:
            session.add(Crop(
                id=cid,
                name_en=en,
                name_te=te,
                name_hi=hi,
                scientific_name=sci
            ))

    session.commit()


def init_db(engine_or_session=None, session_factory=None):
    """Creates tables if not existing and seeds baseline roles and crops."""
    if isinstance(engine_or_session, Session):
        _seed_data(engine_or_session)
    else:
        eng = engine_or_session or default_engine
        Base.metadata.create_all(bind=eng)
        factory = session_factory or default_session_factory
        with factory() as session:
            _seed_data(session)
