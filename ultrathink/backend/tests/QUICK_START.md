# Quick Start - TickTick Link Generation Tests

## TL;DR - Run Tests Now

```bash
# From project root
cd /home/bschroeter/projects/project-management/ultrathink/backend

# Set test environment variables
export OPENROUTER_API_KEY=test_key
export TICKTICK_CLIENT_ID=test_client_id
export TICKTICK_CLIENT_SECRET=test_client_secret
export SECRET_KEY=test_secret_key
export DATABASE_URL=sqlite:///test.db

# Run tests
python3 -m pytest tests/ -v

# Or with coverage
python3 -m pytest tests/ --cov=. --cov-report=term
```

## Installation (One-Time Setup)

```bash
# Ensure pytest is installed
pip install pytest pytest-asyncio pytest-cov

# Or from requirements.txt
cd /home/bschroeter/projects/project-management/ultrathink
pip install -r requirements.txt
```

## Common Commands

### Run All Tests
```bash
cd /home/bschroeter/projects/project-management/ultrathink/backend
python3 -m pytest tests/ -v
```

### Run Critical Tests Only
```bash
python3 -m pytest tests/ -v -m critical
```

### Run Specific Test File
```bash
python3 -m pytest tests/test_models.py -v
python3 -m pytest tests/test_task_analyzer.py -v
python3 -m pytest tests/test_integration_e2e.py -v
```

### Run Single Test
```bash
python3 -m pytest tests/test_task_analyzer.py::test_analyze_new_task_stores_project_id -v
```

### With Coverage
```bash
python3 -m pytest tests/ --cov=. --cov-report=html --cov-report=term
# Open htmlcov/index.html for detailed report
```

## Test Structure Overview

The test suite covers:

1. **Model Tests** (`test_models.py`)
   - ✓ project_id field exists and is nullable
   - ✓ Can store/retrieve projectId values

2. **TaskAnalyzer Tests** (`test_task_analyzer.py`)
   - ✓ All 3 TaskInsight creation points store projectId
   - ✓ API failure handling and fallback logic
   - ✓ Error logging validation

3. **Endpoint Tests** (`test_main_endpoint.py`)
   - ✓ save_clarifying_answers stores projectId
   - ✓ Handles edge cases

4. **Integration Tests** (`test_integration_e2e.py`)
   - ✓ URL construction with/without projectId
   - ✓ End-to-end task analysis flow

5. **Migration Tests** (`test_migrations.py`)
   - ✓ Database migration validation
   - ✓ Data preservation

## Expected Output

```
========================= test session starts ==========================
collected 45 items

tests/test_models.py::test_task_insight_project_id_field PASSED   [  2%]
tests/test_models.py::test_task_insight_can_store_project_id PASSED [  4%]
tests/test_task_analyzer.py::test_analyze_new_task_stores_project_id PASSED [  6%]
...

========================= 45 passed in 2.34s ===========================
```

## Troubleshooting

### Import Errors

If you see import errors, ensure you're in the backend directory:
```bash
cd /home/bschroeter/projects/project-management/ultrathink/backend
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python3 -m pytest tests/ -v
```

### Environment Variable Errors

Make sure test environment variables are set:
```bash
export OPENROUTER_API_KEY=test_key
export TICKTICK_CLIENT_ID=test_client_id
export TICKTICK_CLIENT_SECRET=test_client_secret
export SECRET_KEY=test_secret_key
export DATABASE_URL=sqlite:///test.db
```

Or create a `.env` file in the backend directory:
```bash
cat > .env << EOF
OPENROUTER_API_KEY=test_key
TICKTICK_CLIENT_ID=test_client_id
TICKTICK_CLIENT_SECRET=test_client_secret
SECRET_KEY=test_secret_key
DATABASE_URL=sqlite:///test.db
EOF
```

### Module Not Found

```bash
# Install missing dependencies
pip install pytest pytest-asyncio

# Or install all
pip install -r ../requirements.txt
```

## Verification Checklist

After running tests, verify:

- [ ] All tests passed (0 failures)
- [ ] No import errors
- [ ] Coverage report generated (if using --cov)
- [ ] All critical tests passed
- [ ] URL construction tests passed

## What Tests Cover

### 1. Model Validation (TC-001)
Verifies `TaskInsight.project_id` field exists with correct properties:
- String type, nullable
- Can store/retrieve values
- Handles NULL and empty string

### 2. TaskAnalyzer - analyze_new_task (TC-002, TC-003)
Verifies new task analysis stores projectId:
- ✓ Fetches projectId from TickTick API
- ✓ Handles API failures gracefully
- ✓ Logs appropriate warnings

### 3. TaskAnalyzer - identify_vague_tasks (TC-004)
Verifies vague task identification stores projectId:
- ✓ Extracts projectId from task object
- ✓ Handles missing projectId

### 4. TaskAnalyzer - detect_stale_tasks (TC-006, TC-007, TC-008)
Verifies stale task detection with projectId:
- ✓ Uses fresh projectId from API when available
- ✓ **Falls back to stored projectId when API fails (CRITICAL)**
- ✓ Warns when no projectId available

### 5. Main Endpoint - save_clarifying_answers (TC-005)
Verifies clarifying answers endpoint stores projectId:
- ✓ Captures projectId from task object
- ✓ Handles missing projectId

### 6. Frontend Integration (TC-009, TC-010)
Verifies URL construction logic:
- ✓ With projectId: `https://ticktick.com/webapp/#p/{projectId}/tasks/{taskId}`
- ✓ Without projectId: `https://ticktick.com/webapp/#/tasks/{taskId}`

### 7. End-to-End Flow (TC-012)
Verifies complete workflow:
- Task creation → projectId storage → stale detection → URL generation
- API failure recovery with stored projectId

### 8. Database Migration (TC-011)
Verifies migration:
- Adds project_id column
- Preserves existing data
- Handles NULL and non-NULL values

## Success Metrics

- **Coverage**: >= 95% for unit tests, >= 90% for integration
- **Pass Rate**: 100% of all tests
- **Critical Tests**: 100% pass rate
- **Performance**: Tests complete in < 30 seconds

## Next Steps

1. Run the tests: `python3 -m pytest tests/ -v`
2. Check coverage: `python3 -m pytest tests/ --cov=. --cov-report=html`
3. Review results in `htmlcov/index.html`
4. Verify all critical tests pass
5. Check that fallback logic works (TC-007)

## Links

- Detailed Test Plan: `TEST_PLAN_TICKTICK_LINKS.md`
- Full Documentation: `README.md`
- Test Fixtures: `conftest.py`

## Support

For issues:
1. Check environment variables are set
2. Verify you're in the backend directory
3. Review error messages for missing imports
4. Check Python version (requires 3.10+)
5. Ensure all dependencies are installed

## One-Liner Test Commands

```bash
# Critical tests only
python3 -m pytest tests/ -v -m critical

# With detailed output
python3 -m pytest tests/ -vv -s

# Stop on first failure
python3 -m pytest tests/ -x

# Show slowest tests
python3 -m pytest tests/ --durations=5

# Re-run failed tests
python3 -m pytest tests/ --lf
```
