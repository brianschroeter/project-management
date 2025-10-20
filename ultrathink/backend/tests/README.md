# TickTick Link Generation - Test Suite

Comprehensive test suite for the TickTick link generation fix that ensures tasks open with correct URLs including projectId.

## Overview

This test suite validates the fix for TickTick task links that were opening to white pages. The fix ensures that `projectId` is captured and stored at all TaskInsight creation points, enabling correct URL generation in the format:

```
https://ticktick.com/webapp/#p/{projectId}/tasks/{taskId}
```

## Test Structure

```
backend/tests/
├── __init__.py                      # Package initialization
├── conftest.py                      # Pytest fixtures and configuration
├── test_models.py                   # Model validation tests (TC-001)
├── test_task_analyzer.py            # TaskAnalyzer unit tests (TC-002 to TC-008, TC-014)
├── test_main_endpoint.py            # API endpoint tests (TC-005)
├── test_integration_e2e.py          # Integration tests (TC-009, TC-010, TC-012)
├── test_migrations.py               # Database migration tests (TC-011)
├── TEST_PLAN_TICKTICK_LINKS.md     # Detailed test plan
└── README.md                        # This file
```

## Test Categories

### Unit Tests (95% coverage target)
- **test_models.py**: Database model validation
  - TC-001: Model field validation
  - Field types, constraints, and nullable behavior

- **test_task_analyzer.py**: TaskAnalyzer service tests
  - TC-002: analyze_new_task stores projectId
  - TC-003: analyze_new_task handles API failure
  - TC-004: identify_vague_tasks stores projectId
  - TC-006: detect_stale_tasks uses API projectId
  - TC-007: detect_stale_tasks fallback to stored projectId (CRITICAL)
  - TC-008: detect_stale_tasks warns about missing projectId
  - TC-014: Error logging validation

- **test_main_endpoint.py**: FastAPI endpoint tests
  - TC-005: save_clarifying_answers stores projectId
  - JSON serialization and edge cases

### Integration Tests (90% coverage target)
- **test_integration_e2e.py**: End-to-end workflows
  - TC-009: URL construction with projectId
  - TC-010: URL construction without projectId
  - TC-012: Complete task analysis flow
  - Multi-task scenarios

### Migration Tests
- **test_migrations.py**: Database migration validation
  - TC-011: Migration adds column correctly
  - Data preservation
  - Rollback simulation

## Prerequisites

### Dependencies
All required packages are in `/home/bschroeter/projects/project-management/ultrathink/requirements.txt`:

```bash
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov  # For coverage reporting (add if not present)
```

### Installation

```bash
# From project root
cd /home/bschroeter/projects/project-management/ultrathink

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Install coverage tool if needed
pip install pytest-cov
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests from project root
cd /home/bschroeter/projects/project-management/ultrathink
pytest backend/tests/ -v

# Run from backend directory
cd backend
pytest tests/ -v
```

### Run Specific Test Files

```bash
# Model tests only
pytest backend/tests/test_models.py -v

# TaskAnalyzer tests only
pytest backend/tests/test_task_analyzer.py -v

# Integration tests only
pytest backend/tests/test_integration_e2e.py -v

# Migration tests only
pytest backend/tests/test_migrations.py -v
```

### Run Specific Test Cases

```bash
# Run a specific test by name
pytest backend/tests/test_task_analyzer.py::test_analyze_new_task_stores_project_id -v

# Run critical tests only
pytest backend/tests/ -v -m critical

# Run unit tests only
pytest backend/tests/ -v -m unit

# Run integration tests only
pytest backend/tests/ -v -m integration
```

### Coverage Reports

```bash
# Run with coverage reporting
pytest backend/tests/ --cov=backend --cov-report=html --cov-report=term

# View HTML coverage report
# Open: backend/htmlcov/index.html in browser

# Coverage for specific module
pytest backend/tests/ --cov=backend.services.task_analyzer --cov-report=term

# Coverage with missing lines
pytest backend/tests/ --cov=backend --cov-report=term-missing
```

### Test Output Verbosity

```bash
# Verbose output with test names
pytest backend/tests/ -v

# Very verbose with full output
pytest backend/tests/ -vv

# Show print statements and logs
pytest backend/tests/ -v -s

# Show logs at specific level
pytest backend/tests/ -v --log-cli-level=INFO
pytest backend/tests/ -v --log-cli-level=DEBUG
```

### Performance and Debugging

```bash
# Show slowest tests
pytest backend/tests/ --durations=10

# Run tests in parallel (requires pytest-xdist)
# pip install pytest-xdist
pytest backend/tests/ -n auto

# Stop on first failure
pytest backend/tests/ -x

# Drop into debugger on failure
pytest backend/tests/ --pdb

# Run last failed tests only
pytest backend/tests/ --lf
```

## Test Markers

Tests are marked with custom markers for selective execution:

- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.regression`: Regression tests
- `@pytest.mark.critical`: Critical tests (must pass)

### Using Markers

```bash
# Run only critical tests
pytest backend/tests/ -m critical

# Run unit tests only
pytest backend/tests/ -m unit

# Run all except integration tests
pytest backend/tests/ -m "not integration"

# Run critical unit tests
pytest backend/tests/ -m "critical and unit"
```

## Expected Test Results

### Success Criteria

All tests should pass with the following outcomes:

1. **Model Tests** (test_models.py)
   - ✓ project_id field exists and is nullable
   - ✓ Can store and retrieve projectId values
   - ✓ Handles NULL and empty string values

2. **TaskAnalyzer Tests** (test_task_analyzer.py)
   - ✓ analyze_new_task captures projectId from API
   - ✓ analyze_new_task handles API failures gracefully
   - ✓ identify_vague_tasks extracts projectId from task object
   - ✓ detect_stale_tasks uses API projectId when available
   - ✓ detect_stale_tasks falls back to stored projectId on API failure
   - ✓ Appropriate warnings logged in error scenarios

3. **Endpoint Tests** (test_main_endpoint.py)
   - ✓ save_clarifying_answers endpoint stores projectId
   - ✓ Handles tasks with and without projectId

4. **Integration Tests** (test_integration_e2e.py)
   - ✓ Frontend constructs correct URLs with projectId
   - ✓ Frontend falls back to simple URL without projectId
   - ✓ End-to-end flow from task creation to URL generation works

5. **Migration Tests** (test_migrations.py)
   - ✓ Migration adds project_id column
   - ✓ Existing data is preserved
   - ✓ Both NULL and non-NULL values work

### Coverage Targets

- Unit Tests: >= 95%
- Integration Tests: >= 90%
- Critical Path: 100%

## Test Fixtures

Key fixtures available in `conftest.py`:

### Database Fixtures
- `test_db_engine`: In-memory SQLite database
- `test_db_session`: Database session for each test
- `test_user`: Test user with credentials

### Mock Fixtures
- `mock_ticktick_client`: Basic mock TickTickClient
- `mock_ticktick_client_with_project_id`: Returns tasks with projectId
- `mock_ticktick_client_without_project_id`: Returns tasks without projectId
- `mock_ticktick_client_api_failure`: Simulates API failures

### Data Fixtures
- `sample_task_with_project`: Task data with projectId
- `sample_task_without_project`: Task data without projectId
- `sample_vague_task`: Vague task needing clarification
- `task_insight_with_project_id`: Pre-created TaskInsight with projectId
- `task_insight_without_project_id`: Pre-created TaskInsight without projectId
- `stale_task_insight`: Pre-created stale TaskInsight

### Utility Fixtures
- `assert_project_id_stored`: Helper to assert projectId storage
- `assert_valid_ticktick_url`: Helper to validate URL format
- `expected_urls`: Expected URL formats for validation
- `task_analyzer`: TaskAnalyzer instance with mocked dependencies

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# If you get import errors, ensure you're running from correct directory
cd /home/bschroeter/projects/project-management/ultrathink
export PYTHONPATH="${PYTHONPATH}:/home/bschroeter/projects/project-management/ultrathink/backend"
pytest backend/tests/ -v
```

#### Database Errors
```bash
# Clear any stale database connections
rm -f backend/test.db backend/test.db-journal

# Run tests with fresh database
pytest backend/tests/ -v
```

#### Mock Errors
```bash
# If mocks aren't working, check conftest.py is being loaded
pytest backend/tests/ -v --fixtures

# Run with more verbosity to see mock calls
pytest backend/tests/test_task_analyzer.py -vv -s
```

### Debugging Failed Tests

```bash
# Run failed test with debugging
pytest backend/tests/test_task_analyzer.py::test_analyze_new_task_stores_project_id -vv -s --pdb

# Show full diff on assertion failures
pytest backend/tests/ -vv --tb=long

# Capture and show warnings
pytest backend/tests/ -v -W all
```

## Continuous Integration

### Pre-commit Checks

Add to `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: pytest
      name: pytest
      entry: pytest
      args: [backend/tests/, -v, --tb=short]
      language: system
      pass_filenames: false
      always_run: true
```

### CI Pipeline

Example GitHub Actions workflow:

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest backend/tests/ --cov=backend --cov-report=xml
      - uses: codecov/codecov-action@v2
```

## Test Data

### Sample TickTick Task Structure

```json
{
  "id": "task-123",
  "projectId": "project-456",
  "title": "Test Task",
  "content": "Task description",
  "priority": 3,
  "status": 0,
  "dueDate": null,
  "items": []
}
```

### Expected URL Formats

**With projectId:**
```
https://ticktick.com/webapp/#p/project-456/tasks/task-123
```

**Without projectId (fallback):**
```
https://ticktick.com/webapp/#/tasks/task-123
```

## Verification Checklist

After running tests, verify:

- [ ] All tests pass (0 failures)
- [ ] Coverage >= 95% for unit tests
- [ ] Coverage >= 90% for integration tests
- [ ] No warnings about missing projectId in normal scenarios
- [ ] Appropriate warnings logged when API fails
- [ ] All critical tests pass
- [ ] Migration tests pass
- [ ] URL construction tests pass

## Additional Resources

- **Test Plan**: `TEST_PLAN_TICKTICK_LINKS.md` - Detailed test strategy
- **Models**: `/home/bschroeter/projects/project-management/ultrathink/backend/models.py`
- **TaskAnalyzer**: `/home/bschroeter/projects/project-management/ultrathink/backend/services/task_analyzer.py`
- **Main Endpoint**: `/home/bschroeter/projects/project-management/ultrathink/backend/main.py`
- **Frontend Component**: `/home/bschroeter/projects/project-management/ultrathink/web/src/components/TaskCard.jsx`

## Contributing

When adding new tests:

1. Follow existing test naming conventions: `test_<functionality>_<scenario>`
2. Add appropriate markers: `@pytest.mark.unit`, `@pytest.mark.critical`
3. Use fixtures from conftest.py
4. Include clear docstrings with TC numbers
5. Ensure tests are isolated and can run in any order
6. Update this README with new test descriptions

## Quick Reference

### Most Common Commands

```bash
# Run all tests with coverage
pytest backend/tests/ --cov=backend --cov-report=term-missing

# Run critical tests only
pytest backend/tests/ -m critical -v

# Run specific test file
pytest backend/tests/test_task_analyzer.py -v

# Debug a failing test
pytest backend/tests/test_task_analyzer.py::test_name -vv -s --pdb

# Check test discovery
pytest backend/tests/ --collect-only
```

## Support

For issues or questions about these tests:

1. Review the test plan: `TEST_PLAN_TICKTICK_LINKS.md`
2. Check the implementation files listed above
3. Review test fixtures in `conftest.py`
4. Run tests with `-vv -s` for detailed output

## Change Log

- 2025-10-20: Initial test suite created for TickTick link generation fix
