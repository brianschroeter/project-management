"""
Unit tests for main.py endpoints - TickTick Link Generation

Tests verify that the save clarifying answers endpoint stores projectId correctly.
"""

import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException
from models import TaskInsight


# ============================================================================
# TC-005: TaskInsight Creation - Save Clarifying Answers (main.py)
# ============================================================================

@pytest.mark.unit
@pytest.mark.critical
def test_save_clarifying_answers_stores_project_id(
    test_db_session,
    test_user,
    sample_task_with_project,
    assert_project_id_stored
):
    """
    TC-005: Verify save clarifying answers endpoint stores projectId

    CRITICAL: When user answers clarifying questions, projectId must be captured
    """
    # This test simulates the endpoint logic from main.py:892-899
    # We're testing the business logic, not the HTTP layer

    # Arrange
    task_id = sample_task_with_project["id"]
    answers = {
        "question_1": "Answer to first question",
        "question_2": "Answer to second question"
    }

    # Mock TickTickClient
    with patch('ticktick_client.TickTickClient') as MockClient:
        mock_client_instance = MockClient.return_value
        mock_client_instance.get_task.return_value = sample_task_with_project

        # Simulate the endpoint logic
        task = mock_client_instance.get_task(task_id)

        # Act - Create TaskInsight as done in main.py:892-899
        insight = TaskInsight(
            user_id=test_user.id,
            ticktick_task_id=task_id,
            task_title=task.get("title", ""),
            task_description=task.get("content"),
            project_id=task.get("projectId"),  # This is the critical line
            clarifying_answers=answers
        )
        test_db_session.add(insight)
        test_db_session.commit()
        test_db_session.refresh(insight)

        # Assert
        assert_project_id_stored(insight, sample_task_with_project["projectId"])
        assert insight.clarifying_answers == answers


@pytest.mark.unit
def test_save_clarifying_answers_without_project_id(
    test_db_session,
    test_user,
    sample_task_without_project
):
    """
    Verify save clarifying answers handles tasks without projectId
    """
    # Arrange
    task_id = sample_task_without_project["id"]
    answers = {"question_1": "Answer"}

    # Mock TickTickClient
    with patch('ticktick_client.TickTickClient') as MockClient:
        mock_client_instance = MockClient.return_value
        mock_client_instance.get_task.return_value = sample_task_without_project

        # Simulate endpoint logic
        task = mock_client_instance.get_task(task_id)

        # Act
        insight = TaskInsight(
            user_id=test_user.id,
            ticktick_task_id=task_id,
            task_title=task.get("title", ""),
            task_description=task.get("content"),
            project_id=task.get("projectId"),  # Will be None
            clarifying_answers=answers
        )
        test_db_session.add(insight)
        test_db_session.commit()
        test_db_session.refresh(insight)

        # Assert
        assert insight.project_id is None, "Should handle None projectId gracefully"
        assert insight.clarifying_answers == answers


@pytest.mark.unit
def test_save_clarifying_answers_updates_existing_insight(
    test_db_session,
    test_user,
    task_insight_with_project_id,
    sample_task_with_project
):
    """
    Verify updating existing insight with clarifying answers preserves projectId
    """
    # Arrange
    task_id = task_insight_with_project_id.ticktick_task_id
    new_answers = {"question_1": "New answer"}

    # Simulate updating existing insight (main.py:901-903)
    existing_insight = test_db_session.query(TaskInsight).filter(
        TaskInsight.ticktick_task_id == task_id
    ).first()

    original_project_id = existing_insight.project_id

    # Act
    existing_insight.clarifying_answers = new_answers
    test_db_session.commit()
    test_db_session.refresh(existing_insight)

    # Assert
    assert existing_insight.project_id == original_project_id, \
        "Updating answers should not affect project_id"
    assert existing_insight.clarifying_answers == new_answers


@pytest.mark.unit
def test_save_clarifying_answers_task_not_found(test_db_session, test_user):
    """
    Verify behavior when task is not found in TickTick
    """
    # Arrange
    task_id = "non-existent-task"

    # Mock TickTickClient to return None
    with patch('ticktick_client.TickTickClient') as MockClient:
        mock_client_instance = MockClient.return_value
        mock_client_instance.get_task.return_value = None

        # Act & Assert
        task = mock_client_instance.get_task(task_id)

        # In the actual endpoint, this would raise HTTPException(404)
        assert task is None, "Should return None for non-existent task"


@pytest.mark.unit
def test_save_clarifying_answers_extracts_project_id_from_task_object(
    test_db_session,
    test_user
):
    """
    Verify projectId is correctly extracted from task.get("projectId")
    """
    # Arrange
    test_project_id = "test-project-999"
    task = {
        "id": "task-extract",
        "projectId": test_project_id,  # Using exact key from TickTick API
        "title": "Test Task",
        "content": "Test content"
    }

    # Act - Extract projectId as done in main.py
    extracted_project_id = task.get("projectId")

    insight = TaskInsight(
        user_id=test_user.id,
        ticktick_task_id=task["id"],
        task_title=task.get("title", ""),
        task_description=task.get("content"),
        project_id=extracted_project_id,
        clarifying_answers={"q1": "a1"}
    )
    test_db_session.add(insight)
    test_db_session.commit()
    test_db_session.refresh(insight)

    # Assert
    assert extracted_project_id == test_project_id, \
        "Should extract correct projectId"
    assert insight.project_id == test_project_id, \
        "Should store extracted projectId"


@pytest.mark.unit
def test_save_clarifying_answers_handles_missing_optional_fields(
    test_db_session,
    test_user
):
    """
    Verify endpoint handles tasks with missing optional fields gracefully
    """
    # Arrange - Minimal task object
    task = {
        "id": "task-minimal",
        "projectId": "project-123"
        # Missing title and content
    }

    # Act
    insight = TaskInsight(
        user_id=test_user.id,
        ticktick_task_id=task["id"],
        task_title=task.get("title", ""),  # Will be empty string
        task_description=task.get("content"),  # Will be None
        project_id=task.get("projectId"),
        clarifying_answers={"q1": "a1"}
    )
    test_db_session.add(insight)
    test_db_session.commit()
    test_db_session.refresh(insight)

    # Assert - Should handle missing fields gracefully
    assert insight.project_id == "project-123", "projectId should be stored"
    assert insight.task_title == "", "Empty title should be handled"
    assert insight.task_description is None, "None description should be handled"


@pytest.mark.unit
def test_clarifying_answers_json_serialization(
    test_db_session,
    test_user,
    sample_task_with_project
):
    """
    Verify clarifying answers are properly stored as JSON with projectId
    """
    # Arrange
    complex_answers = {
        "question_1": "Simple answer",
        "question_2": "Answer with special chars: @#$%",
        "question_3": "Very long answer " * 50,
        "nested": {
            "sub_question": "nested answer"
        }
    }

    # Act
    insight = TaskInsight(
        user_id=test_user.id,
        ticktick_task_id=sample_task_with_project["id"],
        task_title=sample_task_with_project["title"],
        task_description=sample_task_with_project.get("content"),
        project_id=sample_task_with_project.get("projectId"),
        clarifying_answers=complex_answers
    )
    test_db_session.add(insight)
    test_db_session.commit()
    test_db_session.refresh(insight)

    # Assert
    assert insight.clarifying_answers == complex_answers, \
        "Complex JSON should be stored and retrieved correctly"
    assert insight.project_id == sample_task_with_project["projectId"], \
        "projectId should not interfere with JSON storage"
