# Test Suite for Demo Protection

This test suite has been created to prevent demo breakage by testing critical functionality that is most likely to fail during a live demonstration.

## Overview

The test suite consists of three main test files:

1. **test_authentication.py** - Tests user registration, login, and authentication systems
2. **test_core_api.py** - Tests database health, API endpoint availability, and core functionality
3. **test_basic_functionality.py** - Additional basic tests (can be expanded)

## What These Tests Protect Against

### Authentication Tests Prevent:
- Broken registration/login flows during demo
- Token generation/verification issues
- Password hashing problems
- Missing or malformed auth endpoints
- Validation errors in auth requests

### Core API/Database Tests Prevent:
- Database connectivity issues
- Missing API endpoints
- Health check failures
- Model import/instantiation errors
- Configuration loading problems
- Standard response format violations

## How to Run the Tests

### Prerequisites
- Python 3.8+ 
- All backend dependencies installed (should already be available in the virtual environment)
- Test database configured (or tests will use mocks where needed)

### Running All Tests
```bash
# From the backend directory
cd /home/vishalvignesh12/oil-spill-platform/backend
python -m pytest tests/ -v
```

### Running Specific Test Files
```bash
# Run only authentication tests
python -m pytest tests/test_authentication.py -v

# Run only core API tests  
python -m pytest tests/test_core_api.py -v

# Run only basic functionality tests
python -m pytest tests/test_basic_functionality.py -v
```

### Running with Coverage (if coverage is installed)
```bash
python -m pytest tests/ --cov=app --cov-report=term-missing
```

## Test Design Principles

### Mocking Strategy
- Tests use mocking extensively for database dependencies to avoid requiring a real database
- External service integrations (satellite, GFW, OpenDrift) are mocked where appropriate
- Auth service tests mock password hashing/verification to focus on business logic

### Test Coverage
- **Authentication**: Registration, login, token handling, password security
- **Core API**: Endpoint availability, health checks, CORS, error handling
- **Models**: Import capability, basic instantiation
- **Configuration**: Settings loading, validation

### Demo-Specific Focus
These tests target the "simple things that break demos":
1. Forgot to add auth middleware to a route
2. Database connection string typo in environment
3. Missing import causing 500 error on startup
4. Validation error in request/response models
5. Health check endpoint not implemented
6. CORS blocking frontend requests
7. Token expiration/secret key issues
8. Password hashing failures
9. Endpoint returning wrong content type
10. Missing error handling leading to unhandled exceptions

## Adding More Tests

To add additional demo protection tests:

1. **Identify critical demo paths**: What will you definitely show in the demo?
2. **Test the happy path**: Does the basic workflow work?
3. **Test error conditions**: What happens with bad input?
4. **Test edge cases**: Boundary conditions, empty data, etc.
5. **Use mocks**: Avoid requiring external services or complex setup
6. **Keep tests fast**: Demo protection tests should run in seconds

## Suggested Additional Tests

For even more demo protection, consider adding:

1. **Integration tests**: Test actual API calls with test database
2. **Service layer tests**: Test detection, drift, attribution services with mocks
3. **Endpoint-specific tests**: Test each API route with valid/invalid data
4. **Performance tests**: Ensure endpoints respond quickly enough for demo
5. **Frontend-backend contract tests**: Verify API responses match frontend expectations

## Maintenance

Run these tests regularly during development:
- Before each demo/practice run
- After making changes to auth, database, or core API code
- When preparing the final demo presentation

If a test fails, fix the underlying issue rather than skipping or modifying the test (unless the test itself is incorrect).

## Notes on Test Environment

Some tests may return 500 errors in the test environment if:
- Database is not configured
- Required environment variables are missing
- External services are not available

This is expected - the tests are designed to verify that:
1. Endpoints exist (not 404)
2. Validation works correctly (422 for bad input)
3. Auth protections are in place (401 for missing tokens)
4. Error responses are properly formatted
5. The application starts and loads configurations correctly

A test passing means the basic infrastructure is working - actual functionality would require proper test fixtures or database setup.