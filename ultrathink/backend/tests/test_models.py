"""
Unit tests for database models - TickTick Link Generation

Tests verify that the TaskInsight model has the correct project_id field
with proper constraints and behavior.
"""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy import inspect
from datetime import datetime

from models import TaskInsight, User


# ============================================================================
# TC-001: Model Field Validation
# ============================================================================

@pytest.mark.unit
@pytest.mark.critical
def test_task_insight_project_id_field(test_db_engine):
    """
    TC-001: Verify TaskInsight model has project_id field with correct properties

    CRITICAL: This is the foundation for storing projectId for correct URLs
    """
    # Get the TaskInsight table metadata
    inspector = inspect(test_db_engine)
    columns = {col['name']: col for col in inspector.get_columns('task_insights')}

    # Assert project_id column exists
    assert 'project_id' in columns, "project_id column should exist in task_insights table"

    # Get column details
    project_id_col = columns['project_id']

    # Assert column type is String
    assert 'VARCHAR' in str(project_id_col['type']).upper() or \
           'TEXT' in str(project_id_col['type']).upper() or \
           'STRING' in str(project_id_col['type']).upper(), \
           f"project_id should be String type, got {project_id_col['type']}"

    # Assert column is nullable
    assert project_id_col['nullable'] == True, \
        "project_id should be nullable for backward compatibility"


@pytest.mark.unit
@pytest.mark.critical
def test_task_insight_can_store_project_id(test_db_session, test_user):
    """
    Verify TaskInsight can store and retrieve project_id values
    """
    # Arrange & Act - Create TaskInsight with project_id
    insight = TaskInsight(
        user_id=test_user.id,
        ticktick_task_id="task-123",
        project_id="project-456",
        task_title="Test Task"
    )
    test_db_session.add(insight)
    test_db_session.commit()
    test_db_session.refresh(insight)

    # Assert
    assert insight.project_id == "project-456", \
        "Should store and retrieve project_id correctly"


@pytest.mark.unit
@pytest.mark.critical
def test_task_insight_allows_null_project_id(test_db_session, test_user):
    """
    Verify TaskInsight allows NULL project_id (for backward compatibility)

    CRITICAL: Legacy tasks may not have projectId
    """
    # Arrange & Act - Create TaskInsight without project_id
    insight = TaskInsight(
        user_id=test_user.id,
        ticktick_task_id="task-legacy",
        project_id=None,  # Explicitly set to None
        task_title="Legacy Task"
    )
    test_db_session.add(insight)
    test_db_session.commit()
    test_db_session.refresh(insight)

    # Assert
    assert insight.project_id is None, \
        "Should allow NULL project_id for legacy tasks"


@pytest.mark.unit
def test_task_insight_all_required_fields(test_db_session, test_user):
    """
    Verify TaskInsight model has all expected fields including project_id
    """
    # Arrange & Act
    insight = TaskInsight(
        user_id=test_user.id,
        ticktick_task_id="task-full",
        project_id="project-789",
        task_title="Full Task",
        task_description="Complete description",
        energy_level="high",
        estimated_duration_minutes=60,
        cognitive_load="heavy"
    )
    test_db_session.add(insight)
    test_db_session.commit()
    test_db_session.refresh(insight)

    # Assert all fields are accessible
    assert hasattr(insight, 'project_id'), "Should have project_id attribute"
    assert hasattr(insight, 'ticktick_task_id'), "Should have ticktick_task_id attribute"
    assert hasattr(insight, 'task_title'), "Should have task_title attribute"
    assert hasattr(insight, 'energy_level'), "Should have energy_level attribute"

    # Verify values
    assert insight.project_id == "project-789"
    assert insight.ticktick_task_id == "task-full"
    assert insight.task_title == "Full Task"


@pytest.mark.unit
def test_task_insight_project_id_can_be_updated(test_db_session, test_user):
    """
    Verify project_id can be updated after creation
    """
    # Arrange - Create with project_id
    insight = TaskInsight(
        user_id=test_user.id,
        ticktick_task_id="task-update",
        project_id="project-old",
        task_title="Test Task"
    )
    test_db_session.add(insight)
    test_db_session.commit()

    # Act - Update project_id
    insight.project_id = "project-new"
    test_db_session.commit()
    test_db_session.refresh(insight)

    # Assert
    assert insight.project_id == "project-new", \
        "Should be able to update project_id"


@pytest.mark.unit
def test_task_insight_project_id_string_length(test_db_session, test_user):
    """
    Verify project_id can store typical TickTick project ID lengths
    """
    # Arrange - Create with long project_id
    long_project_id = "project-" + "x" * 100  # Long but realistic ID

    insight = TaskInsight(
        user_id=test_user.id,
        ticktick_task_id="task-long-id",
        project_id=long_project_id,
        task_title="Test Task"
    )

    # Act
    test_db_session.add(insight)
    test_db_session.commit()
    test_db_session.refresh(insight)

    # Assert
    assert insight.project_id == long_project_id, \
        "Should handle longer project IDs"


@pytest.mark.unit
def test_task_insight_with_empty_string_project_id(test_db_session, test_user):
    """
    Verify TaskInsight handles empty string project_id
    """
    # Arrange & Act
    insight = TaskInsight(
        user_id=test_user.id,
        ticktick_task_id="task-empty",
        project_id="",  # Empty string
        task_title="Test Task"
    )
    test_db_session.add(insight)
    test_db_session.commit()
    test_db_session.refresh(insight)

    # Assert
    assert insight.project_id == "", \
        "Should store empty string (different from NULL)"


@pytest.mark.unit
def test_task_insight_query_by_project_id(test_db_session, test_user):
    """
    Verify we can query TaskInsights by project_id
    """
    # Arrange - Create multiple insights with different project_ids
    insights = [
        TaskInsight(
            user_id=test_user.id,
            ticktick_task_id=f"task-{i}",
            project_id="project-123",
            task_title=f"Task {i}"
        )
        for i in range(3)
    ]

    insight_different_project = TaskInsight(
        user_id=test_user.id,
        ticktick_task_id="task-different",
        project_id="project-456",
        task_title="Different Project Task"
    )

    test_db_session.add_all(insights + [insight_different_project])
    test_db_session.commit()

    # Act - Query by project_id
    results = test_db_session.query(TaskInsight).filter(
        TaskInsight.project_id == "project-123"
    ).all()

    # Assert
    assert len(results) == 3, "Should find all tasks with matching project_id"
    assert all(r.project_id == "project-123" for r in results), \
        "All results should have correct project_id"


@pytest.mark.unit
def test_task_insight_relationships_preserved(test_db_session, test_user):
    """
    Verify adding project_id doesn't break existing relationships
    """
    # Arrange & Act
    insight = TaskInsight(
        user_id=test_user.id,
        ticktick_task_id="task-rel",
        project_id="project-123",
        task_title="Test Task"
    )
    test_db_session.add(insight)
    test_db_session.commit()
    test_db_session.refresh(insight)

    # Assert - Verify user relationship works
    assert insight.user is not None, "Should have user relationship"
    assert insight.user.id == test_user.id, "User relationship should be correct"
    assert insight in test_user.task_insights, \
        "Bidirectional relationship should work"


@pytest.mark.unit
def test_task_insight_timestamps_unaffected(test_db_session, test_user):
    """
    Verify timestamp fields still work correctly with project_id addition
    """
    # Arrange
    before_creation = datetime.utcnow()

    # Act
    insight = TaskInsight(
        user_id=test_user.id,
        ticktick_task_id="task-time",
        project_id="project-123",
        task_title="Test Task"
    )
    test_db_session.add(insight)
    test_db_session.commit()
    test_db_session.refresh(insight)

    after_creation = datetime.utcnow()

    # Assert
    assert insight.first_seen_at is not None, "Should have first_seen_at timestamp"
    assert before_creation <= insight.first_seen_at <= after_creation, \
        "Timestamp should be within expected range"

    assert insight.last_updated_at is not None, "Should have last_updated_at timestamp"
