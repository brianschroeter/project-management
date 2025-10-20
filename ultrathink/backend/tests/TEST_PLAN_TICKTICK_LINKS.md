# Test Plan: TickTick Link Generation Fix

## Executive Summary

**Feature**: TickTick Task Link Generation with Project ID
**Priority**: HIGH
**Risk Level**: MEDIUM (affects user navigation to tasks)
**Test Type**: Unit, Integration, End-to-End

## Problem Statement

Tasks were opening to incorrect URLs:
- **Before**: `https://ticktick.com/webapp/#tasks/{taskId}` (white page)
- **After**: `https://ticktick.com/webapp/#p/{projectId}/tasks/{taskId}` (correct)

## Scope

### In Scope
1. Verification that `project_id` field is stored in TaskInsight model
2. Verification that all three TaskInsight creation points capture projectId
3. Verification that fallback logic uses stored projectId when API calls fail
4. Verification that frontend constructs correct URLs
5. Database migration validation
6. Error handling and logging

### Out of Scope
- TickTick API reliability testing
- Frontend UI/UX testing beyond link generation
- Performance testing of link generation
- Cross-browser compatibility testing

## Test Strategy

### 1. Unit Tests
**Objective**: Verify individual components work correctly in isolation

**Coverage Areas**:
- Model field presence and constraints
- TaskInsight creation with projectId in all three locations
- URL construction logic
- Fallback behavior when projectId is missing
- Error handling

**Tools**: pytest, unittest.mock
**Target Coverage**: 95%+

### 2. Integration Tests
**Objective**: Verify components work together correctly

**Coverage Areas**:
- End-to-end flow from task creation to link generation
- Database operations with projectId
- API interactions with TickTickClient
- Error propagation and recovery

**Tools**: pytest, pytest-asyncio, test database
**Target Coverage**: 90%+

### 3. Regression Tests
**Objective**: Ensure existing functionality remains intact

**Coverage Areas**:
- Tasks without projectId (legacy behavior)
- Existing task insights are not broken
- Other TaskInsight fields function normally

### 4. Migration Tests
**Objective**: Verify database migration adds column correctly

**Coverage Areas**:
- Column addition
- Nullable constraint
- Existing data preservation
- Migration rollback

## Test Cases

### TC-001: Model Field Validation
**Priority**: HIGH
**Type**: Unit Test

**Preconditions**: None
**Steps**:
1. Verify TaskInsight model has `project_id` field
2. Verify field is String type
3. Verify field is nullable
4. Verify field has correct column name

**Expected Results**:
- Field exists with correct type and constraints

**Test File**: `test_models.py::test_task_insight_project_id_field`

---

### TC-002: TaskInsight Creation - analyze_new_task
**Priority**: CRITICAL
**Type**: Unit Test

**Preconditions**: Mock TickTickClient
**Steps**:
1. Call analyze_new_task with task_id and user_id
2. Mock get_task to return task with projectId
3. Verify TaskInsight is created with projectId

**Expected Results**:
- TaskInsight record has correct projectId from API

**Test File**: `test_task_analyzer.py::test_analyze_new_task_stores_project_id`

---

### TC-003: TaskInsight Creation - analyze_new_task (API Failure)
**Priority**: HIGH
**Type**: Unit Test

**Preconditions**: Mock TickTickClient to fail
**Steps**:
1. Call analyze_new_task with task_id and user_id
2. Mock get_task to raise exception
3. Verify TaskInsight is created with projectId=None
4. Verify warning is logged

**Expected Results**:
- TaskInsight created successfully with null projectId
- Error logged but doesn't crash
- Task analysis continues

**Test File**: `test_task_analyzer.py::test_analyze_new_task_handles_api_failure`

---

### TC-004: TaskInsight Creation - identify_vague_tasks
**Priority**: CRITICAL
**Type**: Unit Test

**Preconditions**: Mock get_tasks response
**Steps**:
1. Call identify_vague_tasks with vague task
2. Verify TaskInsight extracts projectId from task object
3. Verify projectId is stored correctly

**Expected Results**:
- TaskInsight has projectId from task.get("projectId")

**Test File**: `test_task_analyzer.py::test_identify_vague_tasks_stores_project_id`

---

### TC-005: TaskInsight Creation - Save Clarifying Answers (main.py)
**Priority**: CRITICAL
**Type**: Unit Test

**Preconditions**: Mock TickTickClient
**Steps**:
1. Call save clarifying answers endpoint
2. Mock get_task to return task with projectId
3. Verify TaskInsight stores projectId

**Expected Results**:
- TaskInsight has correct projectId

**Test File**: `test_main.py::test_save_clarifying_answers_stores_project_id`

---

### TC-006: Stale Tasks Detection - Successful API Call
**Priority**: HIGH
**Type**: Unit Test

**Preconditions**: TaskInsight with stored projectId, mock API success
**Steps**:
1. Create TaskInsight with stored projectId
2. Mock get_task to return full task
3. Call detect_stale_tasks
4. Verify returned data includes projectId from API

**Expected Results**:
- Returned task data includes fresh projectId from API
- Stored projectId is used in fallback if needed

**Test File**: `test_task_analyzer.py::test_detect_stale_tasks_uses_api_project_id`

---

### TC-007: Stale Tasks Detection - API Failure with Stored projectId
**Priority**: CRITICAL
**Type**: Unit Test

**Preconditions**: TaskInsight with stored projectId, mock API failure
**Steps**:
1. Create TaskInsight with stored projectId
2. Mock get_task to raise exception
3. Call detect_stale_tasks
4. Verify fallback uses stored projectId
5. Verify appropriate warning is logged

**Expected Results**:
- Fallback uses stored projectId successfully
- Warning logged about using stored projectId
- No exceptions raised

**Test File**: `test_task_analyzer.py::test_detect_stale_tasks_fallback_to_stored_project_id`

---

### TC-008: Stale Tasks Detection - API Failure without Stored projectId
**Priority**: HIGH
**Type**: Unit Test

**Preconditions**: TaskInsight without projectId, mock API failure
**Steps**:
1. Create TaskInsight with projectId=None
2. Mock get_task to raise exception
3. Call detect_stale_tasks
4. Verify WARNING about missing projectId is logged

**Expected Results**:
- Task data returned with projectId=None
- WARNING logged indicating link may not work
- No exceptions raised

**Test File**: `test_task_analyzer.py::test_detect_stale_tasks_no_project_id_warning`

---

### TC-009: Frontend URL Construction - With projectId
**Priority**: CRITICAL
**Type**: Integration Test

**Preconditions**: Task object with projectId
**Steps**:
1. Create task object with id and projectId
2. Verify URL format: `https://ticktick.com/webapp/#p/{projectId}/tasks/{taskId}`

**Expected Results**:
- Correct URL with projectId in path

**Test File**: `test_frontend_integration.py::test_url_construction_with_project_id`

---

### TC-010: Frontend URL Construction - Without projectId
**Priority**: HIGH
**Type**: Integration Test

**Preconditions**: Task object without projectId
**Steps**:
1. Create task object with id but no projectId
2. Verify fallback URL format: `https://ticktick.com/webapp/#/tasks/{taskId}`

**Expected Results**:
- Fallback URL without projectId segment

**Test File**: `test_frontend_integration.py::test_url_construction_without_project_id`

---

### TC-011: Database Migration Validation
**Priority**: CRITICAL
**Type**: Migration Test

**Preconditions**: Test database without migration
**Steps**:
1. Apply migration
2. Verify project_id column exists
3. Verify column is nullable
4. Verify column type is String
5. Create TaskInsight with and without projectId
6. Verify both scenarios work

**Expected Results**:
- Column added successfully
- No data loss
- Both null and non-null values work

**Test File**: `test_migrations.py::test_add_project_id_column`

---

### TC-012: End-to-End Task Analysis Flow
**Priority**: HIGH
**Type**: Integration Test

**Preconditions**: Real database, mock TickTick API
**Steps**:
1. Create new task via analyze_new_task
2. Verify projectId is stored
3. Call detect_stale_tasks
4. Verify projectId is returned in task data
5. Verify URL can be constructed correctly

**Expected Results**:
- Complete flow works with projectId propagation
- URLs are correct at all stages

**Test File**: `test_integration_e2e.py::test_task_analysis_project_id_flow`

---

### TC-013: Regression - Tasks Without projectId
**Priority**: MEDIUM
**Type**: Regression Test

**Preconditions**: Existing TaskInsights without projectId
**Steps**:
1. Query TaskInsights with projectId=None
2. Call detect_stale_tasks
3. Verify no exceptions
4. Verify fallback URLs work

**Expected Results**:
- System handles legacy data gracefully
- No crashes or errors
- Appropriate warnings logged

**Test File**: `test_regression.py::test_legacy_tasks_without_project_id`

---

### TC-014: Error Logging Validation
**Priority**: MEDIUM
**Type**: Unit Test

**Preconditions**: Mock logger
**Steps**:
1. Simulate various error scenarios
2. Verify appropriate logs are generated:
   - Warning when API call fails
   - Warning when using stored projectId as fallback
   - Warning when no projectId available

**Expected Results**:
- All error paths log appropriately
- Log messages are clear and actionable

**Test File**: `test_logging.py::test_error_logging_scenarios`

---

## Test Data Requirements

### Test Users
- User ID: 1 (primary test user)
- TickTick User ID: "test_user_123"

### Test Tasks
```json
{
  "task_with_project": {
    "id": "task-123",
    "projectId": "project-456",
    "title": "Test Task with Project",
    "content": "This is a test task"
  },
  "task_without_project": {
    "id": "task-789",
    "projectId": null,
    "title": "Test Task without Project",
    "content": "This is a legacy task"
  },
  "vague_task": {
    "id": "task-vague-1",
    "projectId": "project-999",
    "title": "Research",
    "content": ""
  }
}
```

### Test TaskInsights
- TaskInsight with projectId
- TaskInsight without projectId (legacy)
- Stale TaskInsight (>3 days old)

## Test Environment

### Database
- SQLite in-memory database for unit tests
- Test database instance for integration tests

### Mocks
- TickTickClient.get_task()
- TickTickClient.get_tasks()
- AIEngine (where needed)

### Dependencies
- pytest
- pytest-asyncio
- unittest.mock
- pytest-cov (for coverage)

## Success Criteria

### Coverage Requirements
- Unit Test Coverage: >= 95%
- Integration Test Coverage: >= 90%
- Critical Path Coverage: 100%

### Functional Requirements
- All three TaskInsight creation points store projectId
- Fallback logic works when API fails
- Frontend constructs correct URLs
- Migration runs without errors
- No regression in existing functionality

### Non-Functional Requirements
- Tests run in < 30 seconds
- Tests are isolated and can run in any order
- Tests are maintainable and well-documented
- Mock dependencies don't require external services

## Test Execution Plan

### Phase 1: Unit Tests (Priority: CRITICAL)
1. Run model tests
2. Run task_analyzer tests
3. Run main.py endpoint tests
4. Target: 100% pass rate

### Phase 2: Integration Tests
1. Run end-to-end flow tests
2. Run frontend integration tests
3. Target: 100% pass rate

### Phase 3: Migration Tests
1. Run migration up/down tests
2. Verify data integrity
3. Target: 100% pass rate

### Phase 4: Regression Tests
1. Run legacy data tests
2. Verify backward compatibility
3. Target: 100% pass rate

## Risk Assessment

### High Risk Areas
1. **API Failure Scenarios**: If API calls fail and no projectId is stored, links won't work
   - **Mitigation**: Comprehensive fallback testing, clear warning logs

2. **Migration Failures**: Adding column to production could fail
   - **Mitigation**: Test migration thoroughly, ensure rollback works

3. **Legacy Data**: Existing TaskInsights without projectId
   - **Mitigation**: Regression tests for null projectId scenarios

### Medium Risk Areas
1. **Frontend URL Construction**: JavaScript logic could have edge cases
   - **Mitigation**: Integration tests with various data scenarios

2. **Concurrent Updates**: Race conditions during TaskInsight creation
   - **Mitigation**: Database transaction tests

## Test Deliverables

1. **Test Files**:
   - `conftest.py` - Pytest fixtures and configuration
   - `test_models.py` - Model validation tests
   - `test_task_analyzer.py` - TaskAnalyzer unit tests
   - `test_main.py` - API endpoint tests
   - `test_integration_e2e.py` - End-to-end integration tests
   - `test_migrations.py` - Database migration tests
   - `test_regression.py` - Regression tests

2. **Documentation**:
   - This test plan
   - Test execution guide (README.md)
   - Coverage report

3. **Test Data**:
   - Fixtures in conftest.py
   - Mock data files (if needed)

## Continuous Integration

### Pre-commit Hooks
- Run unit tests
- Run code formatting (black)
- Run linting (ruff)

### CI Pipeline
- Run all tests on PR
- Generate coverage report
- Block merge if coverage < 90%
- Block merge if critical tests fail

## Sign-off Criteria

- [ ] All critical tests pass
- [ ] Coverage >= 95% for unit tests
- [ ] Coverage >= 90% for integration tests
- [ ] No P0/P1 bugs found
- [ ] Test documentation complete
- [ ] Code review approved
- [ ] Migration tested on staging

## Appendix

### Related Files
- `/home/bschroeter/projects/project-management/ultrathink/backend/models.py:44`
- `/home/bschroeter/projects/project-management/ultrathink/backend/services/task_analyzer.py:45-61`
- `/home/bschroeter/projects/project-management/ultrathink/backend/services/task_analyzer.py:118-126`
- `/home/bschroeter/projects/project-management/ultrathink/backend/services/task_analyzer.py:179-191`
- `/home/bschroeter/projects/project-management/ultrathink/backend/main.py:892-899`
- `/home/bschroeter/projects/project-management/ultrathink/web/src/components/TaskCard.jsx:125-127`
- `/home/bschroeter/projects/project-management/ultrathink/web/src/components/TaskCard.jsx:158-160`

### Test Execution Commands
```bash
# Run all tests
pytest backend/tests/ -v

# Run with coverage
pytest backend/tests/ --cov=backend --cov-report=html --cov-report=term

# Run specific test file
pytest backend/tests/test_task_analyzer.py -v

# Run specific test
pytest backend/tests/test_task_analyzer.py::test_analyze_new_task_stores_project_id -v

# Run tests with logging
pytest backend/tests/ -v --log-cli-level=INFO
```

### Change Log
- 2025-10-20: Initial test plan created
