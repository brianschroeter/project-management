"""
Integration tests for TickTick Link Generation end-to-end flows

Tests verify complete workflows from task creation to URL generation.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from models import TaskInsight


# ============================================================================
# TC-009 & TC-010: Frontend URL Construction
# ============================================================================

@pytest.mark.integration
@pytest.mark.critical
def test_url_construction_with_project_id(expected_urls):
    """
    TC-009: Verify frontend constructs correct URL with projectId

    CRITICAL: This is what users actually see
    """
    # Simulate frontend TaskCard.jsx logic (lines 125-127, 158-160)
    task = {
        "id": "task-123",
        "projectId": "project-456"
    }

    # Frontend URL construction logic
    ticktick_link = (
        f"https://ticktick.com/webapp/#p/{task['projectId']}/tasks/{task['id']}"
        if task.get('projectId')
        else f"https://ticktick.com/webapp/#/tasks/{task['id']}"
    )

    # Assert
    expected = expected_urls["with_project_example"]
    assert ticktick_link == expected, \
        f"Expected: {expected}, Got: {ticktick_link}"

    # Verify URL components
    assert "/p/project-456/tasks/task-123" in ticktick_link, \
        "URL should contain project path segment"


@pytest.mark.integration
@pytest.mark.critical
def test_url_construction_without_project_id(expected_urls):
    """
    TC-010: Verify frontend falls back to simple URL without projectId

    CRITICAL: Backward compatibility for legacy tasks
    """
    # Simulate frontend logic for task without projectId
    task = {
        "id": "task-789",
        "projectId": None
    }

    # Frontend URL construction logic
    ticktick_link = (
        f"https://ticktick.com/webapp/#p/{task['projectId']}/tasks/{task['id']}"
        if task.get('projectId')
        else f"https://ticktick.com/webapp/#/tasks/{task['id']}"
    )

    # Assert
    expected = expected_urls["without_project_example"]
    assert ticktick_link == expected, \
        f"Expected: {expected}, Got: {ticktick_link}"

    # Verify fallback format
    assert "/p/" not in ticktick_link, \
        "Fallback URL should not contain project path segment"


@pytest.mark.integration
def test_url_construction_with_empty_project_id(expected_urls):
    """
    Verify frontend handles empty string projectId (edge case)
    """
    task = {
        "id": "task-empty",
        "projectId": ""  # Empty string
    }

    # Frontend logic treats empty string as falsy
    ticktick_link = (
        f"https://ticktick.com/webapp/#p/{task['projectId']}/tasks/{task['id']}"
        if task.get('projectId')
        else f"https://ticktick.com/webapp/#/tasks/{task['id']}"
    )

    # Assert - Empty string is falsy in JavaScript
    expected = f"https://ticktick.com/webapp/#/tasks/task-empty"
    assert ticktick_link == expected, \
        "Empty projectId should use fallback URL"


# ============================================================================
# TC-012: End-to-End Task Analysis Flow
# ============================================================================

@pytest.mark.integration
@pytest.mark.critical
def test_task_analysis_project_id_flow(
    task_analyzer,
    test_user,
    test_db_session,
    sample_task_with_project,
    expected_urls
):
    """
    TC-012: Verify complete flow from task creation to URL generation

    CRITICAL: This is the complete user journey
    """
    # Setup
    task_analyzer.ticktick.get_task.return_value = sample_task_with_project
    task_analyzer.ticktick.add_subtask.return_value = {"id": "subtask-1"}

    # Step 1: User creates/analyzes a new task
    result = task_analyzer.analyze_new_task(
        user_id=test_user.id,
        task_id=sample_task_with_project["id"],
        task_title=sample_task_with_project["title"],
        task_description=sample_task_with_project["content"],
        auto_create_subtasks=True
    )

    # Verify projectId is stored
    insight = test_db_session.query(TaskInsight).filter(
        TaskInsight.ticktick_task_id == sample_task_with_project["id"]
    ).first()

    assert insight is not None, "TaskInsight should be created"
    assert insight.project_id == sample_task_with_project["projectId"], \
        "projectId should be stored"

    # Step 2: Task becomes stale
    insight.first_seen_at = datetime.utcnow() - timedelta(days=5)
    test_db_session.commit()

    # Step 3: System detects stale task
    stale_tasks = task_analyzer.detect_stale_tasks(
        user_id=test_user.id,
        stale_threshold_days=3
    )

    assert len(stale_tasks) > 0, "Should detect stale task"
    stale_task = stale_tasks[0]

    # Verify projectId is in returned data
    assert stale_task.get("projectId") == sample_task_with_project["projectId"], \
        "Stale task should include projectId"

    # Step 4: Frontend constructs URL
    task_data = {
        "id": stale_task.get("id"),
        "projectId": stale_task.get("projectId")
    }

    ticktick_link = (
        f"https://ticktick.com/webapp/#p/{task_data['projectId']}/tasks/{task_data['id']}"
        if task_data.get('projectId')
        else f"https://ticktick.com/webapp/#/tasks/{task_data['id']}"
    )

    # Assert final URL is correct
    expected = expected_urls["with_project"].format(
        project_id=sample_task_with_project["projectId"],
        task_id=sample_task_with_project["id"]
    )
    assert ticktick_link == expected, \
        "End-to-end flow should produce correct URL"


@pytest.mark.integration
def test_vague_task_to_url_flow(
    task_analyzer,
    test_user,
    test_db_session,
    sample_vague_task,
    expected_urls
):
    """
    Verify flow from vague task identification to URL generation
    """
    # Step 1: System identifies vague task
    task_analyzer.ticktick.get_tasks.return_value = [sample_vague_task]

    vague_tasks = task_analyzer.identify_vague_tasks(user_id=test_user.id)

    assert len(vague_tasks) > 0, "Should identify vague task"

    # Verify TaskInsight has projectId
    insight = test_db_session.query(TaskInsight).filter(
        TaskInsight.ticktick_task_id == sample_vague_task["id"]
    ).first()

    assert insight.project_id == sample_vague_task["projectId"], \
        "Vague task should have projectId stored"

    # Step 2: User answers clarifying questions (simulate main.py endpoint)
    insight.clarifying_answers = {
        "question_1": "Specific goal",
        "question_2": "Required resources"
    }
    test_db_session.commit()

    # Step 3: Frontend gets task data and constructs URL
    task_data = {
        "id": insight.ticktick_task_id,
        "projectId": insight.project_id
    }

    ticktick_link = (
        f"https://ticktick.com/webapp/#p/{task_data['projectId']}/tasks/{task_data['id']}"
        if task_data.get('projectId')
        else f"https://ticktick.com/webapp/#/tasks/{task_data['id']}"
    )

    # Assert
    expected = expected_urls["with_project"].format(
        project_id=sample_vague_task["projectId"],
        task_id=sample_vague_task["id"]
    )
    assert ticktick_link == expected, \
        "Vague task flow should produce correct URL"


@pytest.mark.integration
def test_api_failure_recovery_flow(
    task_analyzer,
    test_user,
    test_db_session,
    task_insight_with_project_id,
    capsys
):
    """
    Verify system recovers gracefully when API fails but projectId is stored
    """
    # Step 1: Task exists with stored projectId
    original_project_id = task_insight_with_project_id.project_id

    # Step 2: API call fails during stale task detection
    task_analyzer.ticktick.get_task.side_effect = Exception("Network error")

    # Make task stale
    task_insight_with_project_id.first_seen_at = datetime.utcnow() - timedelta(days=5)
    test_db_session.commit()

    # Step 3: System detects stale tasks with fallback
    stale_tasks = task_analyzer.detect_stale_tasks(
        user_id=test_user.id,
        stale_threshold_days=3
    )

    # Assert recovery
    assert len(stale_tasks) > 0, "Should recover and return stale tasks"

    stale_task = stale_tasks[0]
    assert stale_task.get("projectId") == original_project_id, \
        "Should use stored projectId as fallback"

    # Step 4: Verify frontend can still construct URL
    ticktick_link = (
        f"https://ticktick.com/webapp/#p/{stale_task['projectId']}/tasks/{stale_task['id']}"
        if stale_task.get('projectId')
        else f"https://ticktick.com/webapp/#/tasks/{stale_task['id']}"
    )

    assert "/p/" in ticktick_link, "URL should have project path with fallback data"

    # Verify warning was logged
    captured = capsys.readouterr()
    assert "Using stored projectId" in captured.out


# ============================================================================
# Multi-Step Integration Tests
# ============================================================================

@pytest.mark.integration
def test_multiple_tasks_different_projects(
    task_analyzer,
    test_user,
    test_db_session
):
    """
    Verify system handles multiple tasks from different projects correctly
    """
    # Arrange - Create tasks from different projects
    tasks = [
        {
            "id": f"task-{i}",
            "projectId": f"project-{i % 3}",  # 3 different projects
            "title": f"Task {i}",
            "content": f"Content {i}"
        }
        for i in range(6)
    ]

    # Create TaskInsights for all tasks
    for task in tasks:
        task_analyzer.ticktick.get_task.return_value = task

        task_analyzer.analyze_new_task(
            user_id=test_user.id,
            task_id=task["id"],
            task_title=task["title"],
            task_description=task["content"],
            auto_create_subtasks=False
        )

    # Verify all projectIds are stored correctly
    insights = test_db_session.query(TaskInsight).filter(
        TaskInsight.user_id == test_user.id
    ).all()

    assert len(insights) == 6, "Should have 6 TaskInsights"

    # Group by project and verify
    project_groups = {}
    for insight in insights:
        project_id = insight.project_id
        if project_id not in project_groups:
            project_groups[project_id] = []
        project_groups[project_id].append(insight)

    assert len(project_groups) == 3, "Should have tasks from 3 projects"

    # Verify each group has correct count
    for project_id, group_insights in project_groups.items():
        assert len(group_insights) == 2, f"Project {project_id} should have 2 tasks"


@pytest.mark.integration
def test_concurrent_task_analysis(
    task_analyzer,
    test_user,
    test_db_session,
    sample_task_with_project
):
    """
    Verify system handles rapid successive task analyses correctly
    """
    # Simulate multiple rapid analyses of same task
    task_analyzer.ticktick.get_task.return_value = sample_task_with_project

    # Run analysis multiple times
    for _ in range(3):
        task_analyzer.analyze_new_task(
            user_id=test_user.id,
            task_id=sample_task_with_project["id"],
            task_title=sample_task_with_project["title"],
            auto_create_subtasks=False
        )

    # Should only have one TaskInsight (no duplicates)
    insights = test_db_session.query(TaskInsight).filter(
        TaskInsight.ticktick_task_id == sample_task_with_project["id"]
    ).all()

    assert len(insights) == 1, "Should not create duplicate TaskInsights"
    assert insights[0].project_id == sample_task_with_project["projectId"], \
        "projectId should be correct"


@pytest.mark.integration
def test_mixed_tasks_with_and_without_project_ids(
    task_analyzer,
    test_user,
    test_db_session,
    expected_urls
):
    """
    Verify system handles mix of tasks with and without projectIds
    """
    # Create tasks with different projectId scenarios
    task_with_project = {
        "id": "task-with",
        "projectId": "project-123",
        "title": "Task with Project",
        "content": "Test"
    }

    task_without_project = {
        "id": "task-without",
        "projectId": None,
        "title": "Task without Project",
        "content": "Test"
    }

    # Analyze both tasks
    for task in [task_with_project, task_without_project]:
        task_analyzer.ticktick.get_task.return_value = task
        task_analyzer.analyze_new_task(
            user_id=test_user.id,
            task_id=task["id"],
            task_title=task["title"],
            auto_create_subtasks=False
        )

    # Retrieve and verify URLs can be constructed for both
    insights = test_db_session.query(TaskInsight).filter(
        TaskInsight.user_id == test_user.id
    ).all()

    assert len(insights) == 2, "Should have both tasks"

    for insight in insights:
        # Construct URL as frontend would
        ticktick_link = (
            f"https://ticktick.com/webapp/#p/{insight.project_id}/tasks/{insight.ticktick_task_id}"
            if insight.project_id
            else f"https://ticktick.com/webapp/#/tasks/{insight.ticktick_task_id}"
        )

        # Verify URL format is valid
        assert "ticktick.com/webapp" in ticktick_link
        assert insight.ticktick_task_id in ticktick_link

        if insight.project_id:
            assert "/p/" in ticktick_link
        else:
            assert "/p/" not in ticktick_link
