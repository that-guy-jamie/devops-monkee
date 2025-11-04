# Prompt for DevOps-Monkee Agent: SBEP Test Implementation

## Context

I've just completed an SBEP compliance audit and initial fixes for the Ads Monkee project. The test infrastructure is now in place, but tests need to be implemented per SBEP v2.0 requirements.

## What Was Fixed (SBEP Compliance)

### 1. Credential Defaults Documentation
**File:** `backend/config.py`
- Added SBEP warnings to all credential defaults (JWT_SECRET, DATABASE_URL, Google Ads tokens)
- Documented that defaults are for local dev convenience only
- Noted that production uses environment variables (already configured in Render)
- Status: ✅ Fixed with documentation

### 2. Test Directory Structure
**Files Created:**
- `tests/__init__.py` - Root test module with SBEP docstring
- `tests/unit/__init__.py` - Unit test directory
- `tests/integration/__init__.py` - Integration test directory  
- `tests/e2e/__init__.py` - End-to-end test directory
- `tests/conftest.py` - Shared pytest fixtures

**Status:** ✅ Infrastructure created, tests need implementation

### 3. Health Check Endpoint
**File:** `backend/main.py`
- Added database connectivity check using AsyncSessionLocal
- Added Redis connectivity check (when configured)
- Returns detailed health status with per-service checks
- Status: ✅ Implemented

### 4. SBEP Index Updates
**File:** `sds/SBEP-INDEX.yaml`
- Updated README and CHANGELOG status to "active"
- Updated test directories status to "initialized"
- Status: ✅ Updated

## What Needs to Be Done: Test Implementation

Per SBEP v2.0 Section 116-120, the following tests are **required**:

### 1. Unit Tests (`tests/unit/`)
**Required for:**
- ✅ All service classes in `backend/services/`
  - `google_ads_queries.py`
  - `llm_client.py`
  - `ghl_file_upload.py`
  - `report_generator.py`
- ✅ Integration client classes in `backend/integrations/`
  - `google_ads_client.py`
  - `ghl_client.py`
- ✅ Utility functions and data validation
- ✅ Model methods (if any business logic)

**Priority:** High - Core business logic

### 2. Integration Tests (`tests/integration/`)
**Required for:**
- ✅ API endpoint responses (`backend/routers/`, `backend/api/routes/`)
  - Health check endpoint (`/health`)
  - Analysis endpoints (`/api/analysis/*`)
  - Reports endpoints (`/api/reports/*`)
  - Clients endpoints (`/api/clients/*`)
- ✅ Celery task execution (`backend/tasks/`)
  - Analysis tasks
  - Data sync tasks
- ✅ Database operations
  - Model CRUD operations
  - Relationship queries
- ✅ External API mocks
  - Google Ads API (use mocks, don't hit real API)
  - GHL API (use mocks)
  - Claude API (use mocks)

**Priority:** High - Critical workflows

### 3. E2E Tests (`tests/e2e/`)
**Required for:**
- ✅ Complete workflow: Login → Run Analysis → Review → Approve → Execute
- ✅ Client dashboard access (role-based)
- ✅ GHL webhook processing
- ✅ Multi-agent AI consensus workflow

**Priority:** Medium - Full system validation

### 4. Client Size Validation Tests
**Required per SBEP:**
- ✅ Small client (~1K rows) - e.g., donaldson-educational-services
- ✅ Medium client (~6K rows) - e.g., priority-roofing
- ✅ Large client (~25K rows) - e.g., heather-murphy-group

**Success Criteria:**
- Analysis completes in <60s for large clients
- No memory leaks during multi-agent consensus
- API mutations succeed with proper error handling

**Priority:** Medium - Performance validation

## Implementation Guidelines

### Test Structure
```python
# tests/unit/test_services/test_google_ads_queries.py
import pytest
from backend.services.google_ads_queries import GoogleAdsQueries

class TestGoogleAdsQueries:
    def test_build_campaign_query(self):
        # Test query building logic
        pass
    
    def test_parse_campaign_results(self):
        # Test result parsing
        pass
```

### Mock External APIs
```python
# Use pytest fixtures and mocks
@pytest.fixture
def mock_google_ads_client():
    # Mock Google Ads API responses
    pass

@pytest.fixture
def mock_ghl_client():
    # Mock GHL API responses
    pass
```

### Database Testing
```python
# Use test database or in-memory SQLite for unit tests
# Use real PostgreSQL for integration tests (with test database)
@pytest.fixture
def test_db():
    # Setup test database
    pass
```

### Environment Setup
- Tests should NOT require real API keys
- Use `.env.test` or test fixtures for configuration
- Mock all external API calls
- Use test database (separate from dev/prod)

## Files to Create

### Unit Tests
- `tests/unit/test_services/__init__.py`
- `tests/unit/test_services/test_google_ads_queries.py`
- `tests/unit/test_services/test_llm_client.py`
- `tests/unit/test_services/test_ghl_file_upload.py`
- `tests/unit/test_services/test_report_generator.py`
- `tests/unit/test_integrations/__init__.py`
- `tests/unit/test_integrations/test_google_ads_client.py`
- `tests/unit/test_integrations/test_ghl_client.py`

### Integration Tests
- `tests/integration/test_api/__init__.py`
- `tests/integration/test_api/test_health.py`
- `tests/integration/test_api/test_analysis.py`
- `tests/integration/test_api/test_reports.py`
- `tests/integration/test_api/test_clients.py`
- `tests/integration/test_tasks/__init__.py`
- `tests/integration/test_tasks/test_analysis_tasks.py`
- `tests/integration/test_database/__init__.py`
- `tests/integration/test_database/test_models.py`

### E2E Tests
- `tests/e2e/test_workflows/__init__.py`
- `tests/e2e/test_workflows/test_analysis_workflow.py`
- `tests/e2e/test_workflows/test_approval_workflow.py`
- `tests/e2e/test_workflows/test_client_dashboard.py`

## Existing Test Infrastructure

The following is already in place:
- ✅ `tests/conftest.py` - Has basic fixtures (needs expansion)
- ✅ `pyproject.toml` - Has pytest configuration
- ✅ Test directories created with `__init__.py` files

## Dependencies Available

From `pyproject.toml`, these test dependencies are available:
- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `pytest-cov` - Coverage reporting
- `pytest-mock` - Mocking utilities
- `respx` - HTTP mocking for httpx

## Success Criteria

1. ✅ All service classes have unit tests
2. ✅ All API endpoints have integration tests
3. ✅ Critical workflows have E2E tests
4. ✅ Client size validation tests pass
5. ✅ Test coverage >70% (minimum)
6. ✅ All tests pass: `poetry run pytest`
7. ✅ Coverage report: `poetry run pytest --cov=backend --cov-report=html`

## Testing Command

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=backend --cov-report=html

# Run specific test type
poetry run pytest tests/unit/
poetry run pytest tests/integration/
poetry run pytest tests/e2e/
```

## Additional Context

- **Project:** Ads Monkee (Unified Digital Advertising Platform)
- **SBEP Version:** 2.2
- **Backend:** FastAPI (Python 3.12)
- **Database:** PostgreSQL 16
- **Task Queue:** Celery + Redis
- **Current Status:** Test infrastructure ready, tests need implementation

## Reference Files

- **SBEP Mandate:** `sds/SBEP-MANDATE.md` (Section 116-120 for testing requirements)
- **Audit Report:** `AUDIT-REPORT-2025-11-01.md` (See "Missing Test Suite" section)
- **Project Status:** `PROJECT-STATUS.md`
- **Test Config:** `pyproject.toml` (lines 119-133)

---

## Your Task

Implement comprehensive test suite per SBEP v2.0 requirements:

1. **Start with unit tests** for existing services (google_ads_queries, llm_client, etc.)
2. **Add integration tests** for API endpoints
3. **Create E2E tests** for critical workflows
4. **Ensure test coverage** meets SBEP standards (>70%)
5. **Update CHANGELOG.md** with test implementation additions
6. **Update sds/SBEP-INDEX.yaml** when tests are complete

Use the existing test infrastructure, follow pytest best practices, and ensure all external APIs are properly mocked.

