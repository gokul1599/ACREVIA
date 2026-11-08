"""
ACREVIA Backend - Test Suite Fixtures & Test Database Configuration.
"""

import io
import pytest
from typing import Generator
from PIL import Image
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.database.base import Base
from backend.app.database.session import get_db
from backend.app.database.init_db import init_db
from backend.app.models.user import User, Role
from backend.app.models.farm import Farm, FarmMembership, Plot
from backend.app.models.crop import CropSeason
from backend.app.core.security import hash_password, create_access_token

# In-memory SQLite for high-speed, fully isolated automated testing
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Creates all tables and seeds base taxonomy before test execution."""
    Base.metadata.create_all(bind=test_engine)
    with TestingSessionLocal() as db:
        init_db(db)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Provides a fresh transactional session for each test function."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """TestClient with overridden get_db dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def farmer_user(db_session: Session) -> User:
    """Primary smallholder farmer user (User A)."""
    user = User(
        phone="+919876543210",
        full_name="Ramesh Goud",
        email="ramesh@acrevia.test",
        hashed_password=hash_password("Acrevia@2026"),
        language_preference="te",
        is_active=True,
        is_verified=True
    )
    role = db_session.get(Role, "FARMER")
    if role:
        user.roles.append(role)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def farmer_token(farmer_user: User) -> str:
    """JWT bearer token for farmer_user."""
    return create_access_token(
        subject=farmer_user.id,
        roles=[r.id for r in farmer_user.roles]
    )


@pytest.fixture
def second_farmer_user(db_session: Session) -> User:
    """Secondary farmer user (User B) for testing cross-farm tenant isolation."""
    user = User(
        phone="+919123456789",
        full_name="Suresh Reddy",
        email="suresh@acrevia.test",
        hashed_password=hash_password("Acrevia@2026"),
        language_preference="te",
        is_active=True,
        is_verified=True
    )
    role = db_session.get(Role, "FARMER")
    if role:
        user.roles.append(role)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def second_farmer_token(second_farmer_user: User) -> str:
    """JWT bearer token for second_farmer_user."""
    return create_access_token(
        subject=second_farmer_user.id,
        roles=[r.id for r in second_farmer_user.roles]
    )


@pytest.fixture
def expert_user(db_session: Session) -> User:
    """Certified agricultural expert / agronomist user."""
    user = User(
        phone="+919988776655",
        full_name="Dr. K. Srinivas Rao (Agronomist)",
        email="srinivas.kvk@acrevia.test",
        hashed_password=hash_password("ExpertPass@2026"),
        language_preference="te",
        is_active=True,
        is_verified=True
    )
    role = db_session.get(Role, "AGRICULTURAL_EXPERT")
    if role:
        user.roles.append(role)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def expert_token(expert_user: User) -> str:
    """JWT bearer token for expert_user."""
    return create_access_token(
        subject=expert_user.id,
        roles=[r.id for r in expert_user.roles]
    )


@pytest.fixture
def admin_user(db_session: Session) -> User:
    """Platform administrator user."""
    user = User(
        phone="+919000000001",
        full_name="ACREVIA Admin",
        email="admin@acrevia.test",
        hashed_password=hash_password("AdminPass@2026"),
        language_preference="en",
        is_active=True,
        is_verified=True
    )
    role = db_session.get(Role, "ADMIN")
    if role:
        user.roles.append(role)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_token(admin_user: User) -> str:
    """JWT bearer token for admin_user."""
    return create_access_token(
        subject=admin_user.id,
        roles=[r.id for r in admin_user.roles]
    )


@pytest.fixture
def sample_farm(db_session: Session, farmer_user: User) -> Farm:
    """Sample farm owned by farmer_user."""
    farm = Farm(
        owner_id=farmer_user.id,
        name="Ramesh Warangal Farm",
        state="Telangana",
        district="Warangal",
        mandal="Geesugonda",
        village="Dharmaram",
        total_acreage=3.5
    )
    db_session.add(farm)
    db_session.flush()

    membership = FarmMembership(
        farm_id=farm.id,
        user_id=farmer_user.id,
        role_in_farm="OWNER"
    )
    db_session.add(membership)
    db_session.commit()
    db_session.refresh(farm)
    return farm


@pytest.fixture
def sample_plot(db_session: Session, sample_farm: Farm) -> Plot:
    """Sample plot in sample_farm."""
    plot = Plot(
        farm_id=sample_farm.id,
        name="North Plot - Cotton",
        soil_type="BLACK_COTTON",
        irrigation_source="BOREWELL",
        acreage=2.0
    )
    db_session.add(plot)
    db_session.commit()
    db_session.refresh(plot)
    return plot


@pytest.fixture
def sample_season(db_session: Session, sample_plot: Plot) -> CropSeason:
    """Sample Kharif cotton crop season."""
    from datetime import date
    season = CropSeason(
        plot_id=sample_plot.id,
        crop_id="cotton",
        season_type="KHARIF",
        sowing_date=date(2026, 6, 15),
        current_stage="VEGETATIVE",
        status="ACTIVE"
    )
    db_session.add(season)
    db_session.commit()
    db_session.refresh(season)
    return season


@pytest.fixture
def sample_image_bytes() -> bytes:
    """Generates valid 256x256 JPEG foliar image bytes for test uploads."""
    img = Image.new("RGB", (256, 256), color=(34, 139, 34))  # Forest green leaf color
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()
