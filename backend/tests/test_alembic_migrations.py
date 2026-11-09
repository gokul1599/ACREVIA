"""
Tests for ACREVIA Database Migrations & Alembic Architecture.
Stage 04 Remediation (TASK-S04-01).
"""

import os
import re
import pytest
from pathlib import Path
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

from backend.app.database.base import Base
from backend.app.database.init_db import check_db_readiness, init_db


def test_alembic_config_and_structure():
    """Verifies that alembic.ini and migration directory exist and are valid."""
    root_dir = Path(__file__).resolve().parent.parent.parent
    alembic_ini = root_dir / "backend" / "alembic.ini"
    assert alembic_ini.exists(), "backend/alembic.ini must exist"

    with open(alembic_ini, "r", encoding="utf-8") as f:
        content = f.read()

    assert "script_location = backend/app/database/migrations" in content


def test_alembic_revision_graph_integrity():
    """Validates the linear revision chain across all Alembic versions."""
    root_dir = Path(__file__).resolve().parent.parent.parent
    versions_dir = root_dir / "backend" / "app" / "database" / "migrations" / "versions"
    assert versions_dir.exists(), "versions directory must exist"

    version_files = list(versions_dir.glob("*.py"))
    assert len(version_files) >= 5, "Must have all version files in versions directory"

    revisions = {}
    down_revisions = {}

    for v_file in version_files:
        content = v_file.read_text(encoding="utf-8")
        rev_match = re.search(r"revision:\s*str\s*=\s*['\"]([^'\"]+)['\"]", content)
        down_match = re.search(r"down_revision:\s*Union\[str,\s*None\]\s*=\s*(['\"][^'\"]+['\"]|None)", content)

        if rev_match and down_match:
            rev_id = rev_match.group(1)
            down_raw = down_match.group(1).strip("'\"")
            down_id = None if down_raw == "None" else down_raw

            assert rev_id not in revisions, f"Duplicate revision ID: {rev_id}"
            revisions[rev_id] = v_file.name
            down_revisions[rev_id] = down_id

    # Base revision must have down_revision = None
    assert "f043516098f8" in revisions
    assert down_revisions["f043516098f8"] is None

    # Target head revision must be a1089411c87d (PostgreSQL RLS tenant isolation)
    assert "a1089411c87d" in revisions
    assert down_revisions["a1089411c87d"] == "f4894a11c87d"

    # Verify linear chain from head back to base
    curr = "a1089411c87d"
    visited = []
    while curr is not None:
        visited.append(curr)
        curr = down_revisions.get(curr)

    assert visited[-1] == "f043516098f8"
    assert len(visited) == len(revisions), "Revision graph must form a single unbroken linear chain"


def test_check_db_readiness_probe():
    """Tests the database readiness probe on blank and migrated databases."""
    engine = create_engine("sqlite:///:memory:")

    # 1. Blank database
    readiness1 = check_db_readiness(engine)
    assert readiness1["connected"] is True
    assert readiness1["is_ready"] is False
    assert readiness1["alembic_version"] is None
    assert "alembic_version table not found" in readiness1["error"]

    # 2. Database with alembic_version table
    with engine.connect() as conn:
        conn.execute(text("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL PRIMARY KEY)"))
        conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('f4894a11c87d')"))
        conn.commit()

    readiness2 = check_db_readiness(engine)
    assert readiness2["connected"] is True
    assert readiness2["is_ready"] is True
    assert readiness2["alembic_version"] == "f4894a11c87d"
    assert readiness2["error"] is None


def test_init_db_create_tables_flag():
    """Verifies that init_db does not execute create_all when create_tables=False."""
    engine = create_engine("sqlite:///:memory:")

    # Calling init_db with create_tables=False on a blank database should not create tables
    with pytest.raises(Exception):
        # Seeding into non-existent tables will raise OperationalError
        init_db(engine_or_session=engine, create_tables=False)

    insp = inspect(engine)
    assert len(insp.get_table_names()) == 0

    # Calling with create_tables=True creates tables and seeds successfully
    init_db(engine_or_session=engine, create_tables=True)
    insp2 = inspect(engine)
    assert len(insp2.get_table_names()) > 10
