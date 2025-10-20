"""Pytest configuration and shared fixtures for TickTick link generation tests"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock, MagicMock
import sys
import os

# Set up environment variables before any imports
os.environ.setdefault('OPENROUTER_API_KEY', 'test_key')
os.environ.setdefault('TICKTICK_CLIENT_ID', 'test_client_id')
os.environ.setdefault('TICKTICK_CLIENT_SECRET', 'test_client_secret')
os.environ.setdefault('SECRET_KEY', 'test_secret_key')
os.environ.setdefault('DATABASE_URL', 'sqlite:///test.db')

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import Base, User, TaskInsight
from services.task_analyzer import TaskAnalyzer
from ticktick_client import TickTickClient


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def test_db_engine():
    """Create an in-memory SQLite database for testing"""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_db_session(test_db_engine):
    """Create a new database session for each test"""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_db_engine
    )
    session = TestingSessionLocal()
    yield session
    session.close()


# ============================================================================
# User Fixtures
# ============================================================================

@pytest.fixture
def test_user(test_db_session):
    """Create a test user in the database"""
    user = User(
        ticktick_user_id="test_user_123",
        access_token="test_access_token",
        refresh_token="test_refresh_token",
        token_expires_at=datetime.utcnow() + timedelta(hours=1)
    )
    test_db_session.add(user)
    test_db_session.commit()
    test_db_session.refresh(user)
    return user


# ============================================================================
# TickTick Client Mocks
# ============================================================================

@pytest.fixture
def mock_ticktick_client():
    """Create a mock TickTickClient"""
    client = Mock(spec=TickTickClient)
    return client


@pytest.fixture
def mock_ticktick_client_with_project_id(mock_ticktick_client):
    """Mock TickTickClient that returns tasks with projectId"""
    mock_ticktick_client.get_task.return_value = {
        "id": "task-123",
        "projectId": "project-456",
        "title": "Test Task with Project",
        "content": "This is a test task"
    }
    mock_ticktick_client.get_tasks.return_value = [
        {
            "id": "task-123",
            "projectId": "project-456",
            "title": "Test Task",
            "content": "Test content"
        },
        {
            "id": "task-vague-1",
            "projectId": "project-999",
            "title": "Research",
            "content": ""
        }
    ]
    return mock_ticktick_client


@pytest.fixture
def mock_ticktick_client_without_project_id(mock_ticktick_client):
    """Mock TickTickClient that returns tasks without projectId"""
    mock_ticktick_client.get_task.return_value = {
        "id": "task-789",
        "projectId": None,
        "title": "Test Task without Project",
        "content": "This is a legacy task"
    }
    return mock_ticktick_client


@pytest.fixture
def mock_ticktick_client_api_failure(mock_ticktick_client):
    """Mock TickTickClient that raises exceptions"""
    mock_ticktick_client.get_task.side_effect = Exception("API call failed")
    mock_ticktick_client.get_tasks.side_effect = Exception("API call failed")
    return mock_ticktick_client


# ============================================================================
# Task Data Fixtures
# ============================================================================

@pytest.fixture
def sample_task_with_project():
    """Sample task data with projectId"""
    return {
        "id": "task-123",
        "projectId": "project-456",
        "title": "Test Task with Project",
        "content": "This is a test task with description",
        "priority": 3,
        "status": 0,
        "dueDate": None,
        "items": []
    }


@pytest.fixture
def sample_task_without_project():
    """Sample task data without projectId"""
    return {
        "id": "task-789",
        "projectId": None,
        "title": "Test Task without Project",
        "content": "This is a legacy task",
        "priority": 1,
        "status": 0
    }


@pytest.fixture
def sample_vague_task():
    """Sample vague task that needs clarification"""
    return {
        "id": "task-vague-1",
        "projectId": "project-999",
        "title": "Research",
        "content": "",
        "priority": 1,
        "status": 0
    }


# ============================================================================
# TaskInsight Fixtures
# ============================================================================

@pytest.fixture
def task_insight_with_project_id(test_db_session, test_user):
    """Create a TaskInsight with projectId"""
    insight = TaskInsight(
        user_id=test_user.id,
        ticktick_task_id="task-123",
        project_id="project-456",
        task_title="Test Task with Project",
        task_description="Test description",
        energy_level="medium",
        estimated_duration_minutes=30,
        first_seen_at=datetime.utcnow() - timedelta(days=5)
    )
    test_db_session.add(insight)
    test_db_session.commit()
    test_db_session.refresh(insight)
    return insight


@pytest.fixture
def task_insight_without_project_id(test_db_session, test_user):
    """Create a TaskInsight without projectId (legacy data)"""
    insight = TaskInsight(
        user_id=test_user.id,
        ticktick_task_id="task-789",
        project_id=None,  # Legacy task without projectId
        task_title="Legacy Task",
        task_description="This is a legacy task",
        energy_level="low",
        estimated_duration_minutes=15,
        first_seen_at=datetime.utcnow() - timedelta(days=5)
    )
    test_db_session.add(insight)
    test_db_session.commit()
    test_db_session.refresh(insight)
    return insight


@pytest.fixture
def stale_task_insight(test_db_session, test_user):
    """Create a stale TaskInsight (>3 days old)"""
    insight = TaskInsight(
        user_id=test_user.id,
        ticktick_task_id="task-stale-1",
        project_id="project-stale",
        task_title="Stale Task",
        task_description="This task has been sitting for a while",
        energy_level="high",
        estimated_duration_minutes=60,
        first_seen_at=datetime.utcnow() - timedelta(days=7),
        completed=False
    )
    test_db_session.add(insight)
    test_db_session.commit()
    test_db_session.refresh(insight)
    return insight


# ============================================================================
# TaskAnalyzer Fixtures
# ============================================================================

@pytest.fixture
def task_analyzer(test_db_session, mock_ticktick_client):
    """Create a TaskAnalyzer instance with mocked dependencies"""
    analyzer = TaskAnalyzer(
        db=test_db_session,
        ticktick_client=mock_ticktick_client
    )
    # Mock the AI engine to avoid actual API calls
    analyzer.ai = Mock()
    analyzer.ai.breakdown_task.return_value = {
        "subtasks": [
            {"title": "Subtask 1", "energy": "medium", "estimated_minutes": 15},
            {"title": "Subtask 2", "energy": "low", "estimated_minutes": 10}
        ],
        "total_estimated_minutes": 30,
        "cognitive_load": "moderate"
    }
    analyzer.ai.generate_clarifying_questions.return_value = [
        {"question": "What is the specific goal?", "type": "goal"},
        {"question": "What resources do you need?", "type": "resources"}
    ]
    analyzer.ai.help_with_procrastination.return_value = {
        "likely_blockers": ["Unclear requirements", "Too complex"],
        "suggestions": ["Break it down", "Start with research"]
    }
    return analyzer


# ============================================================================
# URL Construction Test Data
# ============================================================================

@pytest.fixture
def expected_urls():
    """Expected URL formats for validation"""
    return {
        "with_project": "https://ticktick.com/webapp/#p/{project_id}/tasks/{task_id}",
        "without_project": "https://ticktick.com/webapp/#/tasks/{task_id}",
        "with_project_example": "https://ticktick.com/webapp/#p/project-456/tasks/task-123",
        "without_project_example": "https://ticktick.com/webapp/#/tasks/task-789"
    }


# ============================================================================
# Pytest Configuration
# ============================================================================

def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "regression: mark test as a regression test"
    )
    config.addinivalue_line(
        "markers", "critical: mark test as critical (must pass)"
    )


# ============================================================================
# Utility Functions
# ============================================================================

@pytest.fixture
def assert_project_id_stored():
    """Helper function to assert projectId is properly stored"""
    def _assert(task_insight, expected_project_id):
        assert task_insight is not None, "TaskInsight should exist"
        assert hasattr(task_insight, 'project_id'), "TaskInsight should have project_id field"
        assert task_insight.project_id == expected_project_id, \
            f"Expected project_id={expected_project_id}, got {task_insight.project_id}"
    return _assert


@pytest.fixture
def assert_valid_ticktick_url():
    """Helper function to validate TickTick URL format"""
    def _assert(url, task_id, project_id=None):
        assert url is not None, "URL should not be None"
        assert "ticktick.com/webapp" in url, "URL should be a TickTick webapp URL"

        if project_id:
            expected = f"https://ticktick.com/webapp/#p/{project_id}/tasks/{task_id}"
            assert url == expected, f"Expected URL: {expected}, got: {url}"
        else:
            expected = f"https://ticktick.com/webapp/#/tasks/{task_id}"
            assert url == expected, f"Expected fallback URL: {expected}, got: {url}"

    return _assert
