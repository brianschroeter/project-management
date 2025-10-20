"""
Unit tests for TaskAnalyzer - TickTick Link Generation with Project ID

Tests verify that projectId is properly stored and used in TaskInsight records
to generate correct TickTick task URLs.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, call
from models import TaskInsight


# ============================================================================
# TC-002: TaskInsight Creation - analyze_new_task
# ============================================================================

@pytest.mark.unit
@pytest.mark.critical
def test_analyze_new_task_stores_project_id(
    task_analyzer,
    test_user,
    test_db_session,
    sample_task_with_project,
    assert_project_id_stored
):
    """
    TC-002: Verify analyze_new_task stores projectId when creating TaskInsight

    CRITICAL: This ensures new task analysis captures projectId for correct URLs
    """
    # Arrange
    task_analyzer.ticktick.get_task.return_value = sample_task_with_project
    task_analyzer.ticktick.add_subtask.return_value = {"id": "subtask-1"}

    # Act
    result = task_analyzer.analyze_new_task(
        user_id=test_user.id,
        task_id=sample_task_with_project["id"],
        task_title=sample_task_with_project["title"],
        task_description=sample_task_with_project["content"],
        auto_create_subtasks=True
    )

    # Assert
    # Verify the API was called to get full task details
    task_analyzer.ticktick.get_task.assert_called_once_with(sample_task_with_project["id"])

    # Verify TaskInsight was created with projectId
    insight = test_db_session.query(TaskInsight).filter(
        TaskInsight.ticktick_task_id == sample_task_with_project["id"]
    ).first()

    assert_project_id_stored(insight, sample_task_with_project["projectId"])

    # Verify other fields are also correct
    assert insight.task_title == sample_task_with_project["title"]
    assert insight.user_id == test_user.id


@pytest.mark.unit
@pytest.mark.critical
def test_analyze_new_task_handles_api_failure(
    task_analyzer,
    test_user,
    test_db_session,
    capsys
):
    """
    TC-003: Verify analyze_new_task handles API failure gracefully

    CRITICAL: Even if get_task fails, analysis should continue with projectId=None
    """
    # Arrange
    task_analyzer.ticktick.get_task.side_effect = Exception("TickTick API unavailable")

    # Act
    result = task_analyzer.analyze_new_task(
        user_id=test_user.id,
        task_id="task-123",
        task_title="Test Task",
        task_description="Test description",
        auto_create_subtasks=False
    )

    # Assert
    # Verify TaskInsight was still created (with projectId=None)
    insight = test_db_session.query(TaskInsight).filter(
        TaskInsight.ticktick_task_id == "task-123"
    ).first()

    assert insight is not None, "TaskInsight should be created even if API fails"
    assert insight.project_id is None, "projectId should be None when API fails"
    assert insight.task_title == "Test Task"

    # Verify warning was printed
    captured = capsys.readouterr()
    assert "Warning: Could not fetch projectId" in captured.out
    assert "task-123" in captured.out


@pytest.mark.unit
def test_analyze_new_task_updates_existing_insight(
    task_analyzer,
    test_user,
    test_db_session,
    task_insight_with_project_id,
    sample_task_with_project
):
    """
    Verify analyze_new_task updates existing TaskInsight instead of creating duplicate
    """
    # Arrange
    task_analyzer.ticktick.get_task.return_value = sample_task_with_project
    existing_insight_id = task_insight_with_project_id.id

    # Act
    result = task_analyzer.analyze_new_task(
        user_id=test_user.id,
        task_id=task_insight_with_project_id.ticktick_task_id,
        task_title="Updated Title",
        task_description="Updated description",
        auto_create_subtasks=False
    )

    # Assert
    # Should only have one insight for this task
    insights = test_db_session.query(TaskInsight).filter(
        TaskInsight.ticktick_task_id == task_insight_with_project_id.ticktick_task_id
    ).all()

    assert len(insights) == 1, "Should not create duplicate TaskInsight"
    assert insights[0].id == existing_insight_id, "Should update existing insight"

    # Verify projectId is preserved
    assert insights[0].project_id == "project-456"


# ============================================================================
# TC-004: TaskInsight Creation - identify_vague_tasks
# ============================================================================

@pytest.mark.unit
@pytest.mark.critical
def test_identify_vague_tasks_stores_project_id(
    task_analyzer,
    test_user,
    test_db_session,
    sample_vague_task,
    assert_project_id_stored
):
    """
    TC-004: Verify identify_vague_tasks extracts and stores projectId from task object

    CRITICAL: Vague tasks must also have projectId for correct URLs
    """
    # Arrange
    task_analyzer.ticktick.get_tasks.return_value = [sample_vague_task]

    # Act
    vague_tasks = task_analyzer.identify_vague_tasks(user_id=test_user.id)

    # Assert
    assert len(vague_tasks) > 0, "Should identify at least one vague task"

    # Verify TaskInsight was created with projectId
    insight = test_db_session.query(TaskInsight).filter(
        TaskInsight.ticktick_task_id == sample_vague_task["id"]
    ).first()

    assert_project_id_stored(insight, sample_vague_task["projectId"])
    assert insight.clarifying_questions is not None, "Should have clarifying questions"


@pytest.mark.unit
def test_identify_vague_tasks_handles_missing_project_id(
    task_analyzer,
    test_user,
    test_db_session
):
    """
    Verify identify_vague_tasks handles tasks without projectId gracefully
    """
    # Arrange
    task_without_project = {
        "id": "task-no-project",
        "projectId": None,
        "title": "Research",
        "content": ""
    }
    task_analyzer.ticktick.get_tasks.return_value = [task_without_project]

    # Act
    vague_tasks = task_analyzer.identify_vague_tasks(user_id=test_user.id)

    # Assert
    insight = test_db_session.query(TaskInsight).filter(
        TaskInsight.ticktick_task_id == task_without_project["id"]
    ).first()

    assert insight is not None, "TaskInsight should be created"
    assert insight.project_id is None, "projectId should be None"


@pytest.mark.unit
def test_identify_vague_tasks_skips_non_vague_tasks(
    task_analyzer,
    test_user,
    test_db_session
):
    """
    Verify identify_vague_tasks correctly filters out clear, detailed tasks
    """
    # Arrange
    clear_task = {
        "id": "task-clear",
        "projectId": "project-123",
        "title": "Write comprehensive documentation for API endpoints",
        "content": "Detailed description with all requirements"
    }
    task_analyzer.ticktick.get_tasks.return_value = [clear_task]

    # Act
    vague_tasks = task_analyzer.identify_vague_tasks(user_id=test_user.id)

    # Assert
    assert len(vague_tasks) == 0, "Should not identify clear task as vague"


# ============================================================================
# TC-006: Stale Tasks Detection - Successful API Call
# ============================================================================

@pytest.mark.unit
@pytest.mark.critical
def test_detect_stale_tasks_uses_api_project_id(
    task_analyzer,
    test_user,
    test_db_session,
    stale_task_insight,
    sample_task_with_project
):
    """
    TC-006: Verify detect_stale_tasks uses fresh projectId from API call

    CRITICAL: Should prefer fresh data from API over stored data
    """
    # Arrange
    task_analyzer.ticktick.get_task.return_value = sample_task_with_project

    # Act
    stale_tasks = task_analyzer.detect_stale_tasks(
        user_id=test_user.id,
        stale_threshold_days=3
    )

    # Assert
    assert len(stale_tasks) > 0, "Should detect stale task"

    # Verify API was called to get fresh task data
    task_analyzer.ticktick.get_task.assert_called()

    # Verify returned data includes projectId from API
    stale_task = stale_tasks[0]
    assert stale_task.get("projectId") == sample_task_with_project["projectId"]


# ============================================================================
# TC-007: Stale Tasks Detection - API Failure with Stored projectId
# ============================================================================

@pytest.mark.unit
@pytest.mark.critical
def test_detect_stale_tasks_fallback_to_stored_project_id(
    task_analyzer,
    test_user,
    test_db_session,
    stale_task_insight,
    capsys
):
    """
    TC-007: Verify detect_stale_tasks falls back to stored projectId when API fails

    CRITICAL: This is the key fallback mechanism for reliable link generation
    """
    # Arrange
    task_analyzer.ticktick.get_task.side_effect = Exception("API unavailable")
    original_project_id = stale_task_insight.project_id

    # Act
    stale_tasks = task_analyzer.detect_stale_tasks(
        user_id=test_user.id,
        stale_threshold_days=3
    )

    # Assert
    assert len(stale_tasks) > 0, "Should still return stale tasks even if API fails"

    # Verify fallback used stored projectId
    stale_task = stale_tasks[0]
    assert stale_task.get("projectId") == original_project_id, \
        "Should use stored projectId as fallback"

    # Verify appropriate warning was logged
    captured = capsys.readouterr()
    assert "Error fetching full task data" in captured.out
    assert "Using stored projectId" in captured.out
    assert stale_task_insight.ticktick_task_id in captured.out


# ============================================================================
# TC-008: Stale Tasks Detection - API Failure without Stored projectId
# ============================================================================

@pytest.mark.unit
@pytest.mark.critical
def test_detect_stale_tasks_no_project_id_warning(
    task_analyzer,
    test_user,
    test_db_session,
    task_insight_without_project_id,
    capsys
):
    """
    TC-008: Verify detect_stale_tasks warns when no projectId is available

    CRITICAL: User should be warned that link may not work
    """
    # Arrange
    # Make the insight stale
    task_insight_without_project_id.first_seen_at = datetime.utcnow() - timedelta(days=5)
    test_db_session.commit()

    task_analyzer.ticktick.get_task.side_effect = Exception("API unavailable")

    # Act
    stale_tasks = task_analyzer.detect_stale_tasks(
        user_id=test_user.id,
        stale_threshold_days=3
    )

    # Assert
    assert len(stale_tasks) > 0, "Should still return task"

    stale_task = stale_tasks[0]
    assert stale_task.get("projectId") is None, "projectId should be None"

    # Verify WARNING was logged
    captured = capsys.readouterr()
    assert "WARNING: No projectId available" in captured.out
    assert "link may not work" in captured.out


# ============================================================================
# TC-014: Error Logging Validation
# ============================================================================

@pytest.mark.unit
def test_error_logging_scenarios(
    task_analyzer,
    test_user,
    test_db_session,
    capsys
):
    """
    TC-014: Verify appropriate error logging in various scenarios
    """
    # Scenario 1: API failure during analyze_new_task
    task_analyzer.ticktick.get_task.side_effect = Exception("Network error")

    task_analyzer.analyze_new_task(
        user_id=test_user.id,
        task_id="task-error-1",
        task_title="Test Task",
        auto_create_subtasks=False
    )

    captured = capsys.readouterr()
    assert "Warning: Could not fetch projectId" in captured.out

    # Scenario 2: API failure during detect_stale_tasks with stored projectId
    insight_with_project = TaskInsight(
        user_id=test_user.id,
        ticktick_task_id="task-error-2",
        project_id="project-123",
        task_title="Stale Task",
        first_seen_at=datetime.utcnow() - timedelta(days=5),
        completed=False
    )
    test_db_session.add(insight_with_project)
    test_db_session.commit()

    stale_tasks = task_analyzer.detect_stale_tasks(
        user_id=test_user.id,
        stale_threshold_days=3
    )

    captured = capsys.readouterr()
    assert "Using stored projectId" in captured.out


# ============================================================================
# Additional Edge Cases
# ============================================================================

@pytest.mark.unit
def test_analyze_new_task_with_empty_project_id(
    task_analyzer,
    test_user,
    test_db_session
):
    """
    Verify behavior when API returns empty string for projectId
    """
    # Arrange
    task_analyzer.ticktick.get_task.return_value = {
        "id": "task-empty",
        "projectId": "",  # Empty string instead of None
        "title": "Task with empty projectId",
        "content": "Test"
    }

    # Act
    result = task_analyzer.analyze_new_task(
        user_id=test_user.id,
        task_id="task-empty",
        task_title="Task with empty projectId",
        auto_create_subtasks=False
    )

    # Assert
    insight = test_db_session.query(TaskInsight).filter(
        TaskInsight.ticktick_task_id == "task-empty"
    ).first()

    # Empty string should be stored as-is (frontend can handle it)
    assert insight.project_id == ""


@pytest.mark.unit
def test_detect_stale_tasks_threshold(
    task_analyzer,
    test_user,
    test_db_session
):
    """
    Verify stale task detection respects the threshold parameter
    """
    # Arrange - Create tasks with different ages
    recent_task = TaskInsight(
        user_id=test_user.id,
        ticktick_task_id="task-recent",
        project_id="project-123",
        task_title="Recent Task",
        first_seen_at=datetime.utcnow() - timedelta(days=2),
        completed=False
    )

    old_task = TaskInsight(
        user_id=test_user.id,
        ticktick_task_id="task-old",
        project_id="project-456",
        task_title="Old Task",
        first_seen_at=datetime.utcnow() - timedelta(days=10),
        completed=False
    )

    test_db_session.add_all([recent_task, old_task])
    test_db_session.commit()

    task_analyzer.ticktick.get_task.return_value = {
        "id": "task-old",
        "projectId": "project-456",
        "title": "Old Task",
        "content": "Test"
    }

    # Act - Use 5 day threshold
    stale_tasks = task_analyzer.detect_stale_tasks(
        user_id=test_user.id,
        stale_threshold_days=5
    )

    # Assert - Only old_task should be returned
    assert len(stale_tasks) == 1, "Should only detect tasks older than threshold"
    assert stale_tasks[0]["task_id"] == "task-old"


@pytest.mark.unit
def test_analyze_new_task_preserves_project_id_on_update(
    task_analyzer,
    test_user,
    test_db_session,
    task_insight_with_project_id
):
    """
    Verify that re-analyzing a task doesn't lose the projectId
    """
    # Arrange
    original_project_id = task_insight_with_project_id.project_id
    task_id = task_insight_with_project_id.ticktick_task_id

    # Don't mock get_task - testing update path where API isn't called
    task_analyzer.ticktick.get_task.return_value = {
        "id": task_id,
        "projectId": original_project_id,
        "title": "Updated Task",
        "content": "Updated content"
    }

    # Act - Re-analyze the same task
    result = task_analyzer.analyze_new_task(
        user_id=test_user.id,
        task_id=task_id,
        task_title="Updated Task",
        task_description="Updated content",
        auto_create_subtasks=False
    )

    # Assert
    insight = test_db_session.query(TaskInsight).filter(
        TaskInsight.ticktick_task_id == task_id
    ).first()

    assert insight.project_id == original_project_id, \
        "projectId should be preserved on update"
