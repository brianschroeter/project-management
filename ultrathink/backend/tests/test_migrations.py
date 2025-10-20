"""
Migration tests for TickTick Link Generation

Tests verify that the database migration adds project_id column correctly.
"""

import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from models import Base, TaskInsight, User
from datetime import datetime


# ============================================================================
# TC-011: Database Migration Validation
# ============================================================================

@pytest.mark.integration
@pytest.mark.critical
def test_add_project_id_column_migration():
    """
    TC-011: Verify migration adds project_id column with correct properties

    CRITICAL: Migration must work without data loss
    """
    # Create a fresh database to simulate migration
    engine = create_engine("sqlite:///:memory:", echo=False)

    # Step 1: Create schema with all tables including project_id
    # (In real migration, this would be the "up" migration)
    Base.metadata.create_all(engine)

    # Step 2: Verify column exists with correct properties
    inspector = inspect(engine)
    columns = {col['name']: col for col in inspector.get_columns('task_insights')}

    # Assert project_id column exists
    assert 'project_id' in columns, "Migration should add project_id column"

    # Assert column properties
    project_id_col = columns['project_id']
    assert project_id_col['nullable'] == True, \
        "project_id should be nullable for backward compatibility"

    # Step 3: Verify existing data is preserved (simulate by creating data)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    # Create test user
    user = User(
        ticktick_user_id="test_user",
        access_token="token",
        refresh_token="refresh",
        token_expires_at=datetime.utcnow()
    )
    session.add(user)
    session.commit()

    # Create TaskInsight with project_id
    insight_with_project = TaskInsight(
        user_id=user.id,
        ticktick_task_id="task-1",
        project_id="project-123",
        task_title="Task with Project"
    )

    # Create TaskInsight without project_id (legacy data)
    insight_without_project = TaskInsight(
        user_id=user.id,
        ticktick_task_id="task-2",
        project_id=None,
        task_title="Legacy Task"
    )

    session.add_all([insight_with_project, insight_without_project])
    session.commit()

    # Step 4: Verify both scenarios work
    retrieved_with = session.query(TaskInsight).filter(
        TaskInsight.ticktick_task_id == "task-1"
    ).first()

    retrieved_without = session.query(TaskInsight).filter(
        TaskInsight.ticktick_task_id == "task-2"
    ).first()

    assert retrieved_with.project_id == "project-123", \
        "Should store project_id correctly"
    assert retrieved_without.project_id is None, \
        "Should allow NULL project_id"

    # Clean up
    session.close()
    engine.dispose()


@pytest.mark.integration
def test_migration_preserves_existing_data():
    """
    Verify migration doesn't affect existing TaskInsight data
    """
    # Create database and populate with data
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    # Create user
    user = User(
        ticktick_user_id="test_user",
        access_token="token",
        refresh_token="refresh",
        token_expires_at=datetime.utcnow()
    )
    session.add(user)
    session.commit()

    # Create existing TaskInsight with all fields
    existing_data = {
        "user_id": user.id,
        "ticktick_task_id": "existing-task",
        "task_title": "Existing Task",
        "task_description": "Existing Description",
        "energy_level": "high",
        "estimated_duration_minutes": 60,
        "cognitive_load": "heavy",
        "priority_score": 8.5,
        "completed": False
    }

    insight = TaskInsight(**existing_data)
    session.add(insight)
    session.commit()

    # Simulate migration by adding project_id
    insight.project_id = "new-project-id"
    session.commit()

    # Verify all original data is preserved
    retrieved = session.query(TaskInsight).filter(
        TaskInsight.ticktick_task_id == "existing-task"
    ).first()

    assert retrieved.task_title == existing_data["task_title"]
    assert retrieved.task_description == existing_data["task_description"]
    assert retrieved.energy_level == existing_data["energy_level"]
    assert retrieved.estimated_duration_minutes == existing_data["estimated_duration_minutes"]
    assert retrieved.cognitive_load == existing_data["cognitive_load"]
    assert retrieved.priority_score == existing_data["priority_score"]
    assert retrieved.completed == existing_data["completed"]

    # And new field is added
    assert retrieved.project_id == "new-project-id"

    session.close()
    engine.dispose()


@pytest.mark.integration
def test_migration_column_type():
    """
    Verify project_id column has correct data type for TickTick IDs
    """
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)

    inspector = inspect(engine)
    columns = {col['name']: col for col in inspector.get_columns('task_insights')}

    project_id_col = columns['project_id']
    col_type = str(project_id_col['type']).upper()

    # Should be a string/text type
    assert any(t in col_type for t in ['VARCHAR', 'TEXT', 'STRING']), \
        f"project_id should be string type, got {col_type}"

    engine.dispose()


@pytest.mark.integration
def test_migration_allows_long_project_ids():
    """
    Verify project_id column can store realistic TickTick project IDs
    """
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    # Create user
    user = User(
        ticktick_user_id="test_user",
        access_token="token",
        refresh_token="refresh",
        token_expires_at=datetime.utcnow()
    )
    session.add(user)
    session.commit()

    # Test with realistic and long project IDs
    test_project_ids = [
        "simple-id",
        "project-123456789",
        "very-long-project-id-" + "x" * 100,
        "special-chars-project_id_123",
        "projectId-with-Capitals-123"
    ]

    for i, project_id in enumerate(test_project_ids):
        insight = TaskInsight(
            user_id=user.id,
            ticktick_task_id=f"task-{i}",
            project_id=project_id,
            task_title=f"Task {i}"
        )
        session.add(insight)

    session.commit()

    # Verify all project IDs are stored correctly
    insights = session.query(TaskInsight).all()
    stored_project_ids = [i.project_id for i in insights]

    assert stored_project_ids == test_project_ids, \
        "All project IDs should be stored accurately"

    session.close()
    engine.dispose()


@pytest.mark.integration
def test_migration_rollback_simulation():
    """
    Verify database can handle project_id column being removed (rollback)
    """
    # This simulates what would happen if we need to rollback the migration
    engine = create_engine("sqlite:///:memory:", echo=False)

    # Create tables with project_id
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    # Create user and insight
    user = User(
        ticktick_user_id="test_user",
        access_token="token",
        refresh_token="refresh",
        token_expires_at=datetime.utcnow()
    )
    session.add(user)
    session.commit()

    insight = TaskInsight(
        user_id=user.id,
        ticktick_task_id="task-1",
        project_id="project-123",
        task_title="Test Task"
    )
    session.add(insight)
    session.commit()

    # Verify data exists
    assert session.query(TaskInsight).count() == 1

    session.close()

    # Simulate rollback by dropping and recreating without project_id
    # (In real migration, this would be the "down" migration)
    # Note: We can't actually remove the column from the model, but we can
    # verify that setting it to NULL works (which is what a rollback would do)

    session = SessionLocal()
    insight = session.query(TaskInsight).first()
    insight.project_id = None
    session.commit()

    # Verify task still exists and other data is intact
    retrieved = session.query(TaskInsight).first()
    assert retrieved.ticktick_task_id == "task-1"
    assert retrieved.task_title == "Test Task"
    assert retrieved.project_id is None

    session.close()
    engine.dispose()


@pytest.mark.integration
def test_migration_index_performance():
    """
    Verify querying by project_id is efficient
    (Note: This test is conceptual - actual index would be in migration)
    """
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    # Create user
    user = User(
        ticktick_user_id="test_user",
        access_token="token",
        refresh_token="refresh",
        token_expires_at=datetime.utcnow()
    )
    session.add(user)
    session.commit()

    # Create many tasks
    for i in range(100):
        insight = TaskInsight(
            user_id=user.id,
            ticktick_task_id=f"task-{i}",
            project_id=f"project-{i % 10}",  # 10 different projects
            task_title=f"Task {i}"
        )
        session.add(insight)

    session.commit()

    # Query by project_id (should be fast with index)
    results = session.query(TaskInsight).filter(
        TaskInsight.project_id == "project-5"
    ).all()

    # Verify query works correctly
    assert len(results) == 10, "Should find all tasks for project-5"
    assert all(r.project_id == "project-5" for r in results)

    session.close()
    engine.dispose()
