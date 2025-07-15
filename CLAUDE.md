# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development Setup
```bash
# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Run the main script
poetry run python src/content_calendar/calendar_generator.py
```

### Development Tools
```bash
# Code formatting
poetry run black src/ tests/

# Import sorting
poetry run isort src/ tests/

# Linting
poetry run flake8 src/ tests/

# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=src/content_calendar --cov-report=term-missing

# Run tests with HTML coverage report
poetry run pytest --cov=src/content_calendar --cov-report=html
```

## Architecture

This is a production-ready Python CLI tool that generates Google Sheets content calendars for clients. The project uses Poetry for dependency management and follows enterprise-grade development practices with comprehensive error handling, security features, and 99% test coverage.

### Core Components

- **ContentCalendarGenerator** (`src/content_calendar/calendar_generator.py`): Main class with robust error handling, retry logic, and comprehensive API integration
- **Google Sheets Integration**: Uses `gspread` library with OAuth2 authentication, automatic retry on failures, and proper error handling
- **Authentication Flow**: Secure authentication with proper file permissions, token refresh, and comprehensive error handling
- **Input Validation**: Security-first validation functions with sanitization and boundary checking
- **Retry Logic**: Exponential backoff retry mechanism for handling transient API failures

### Key Features

The tool creates professional content calendars with:
- Pre-configured columns (Date, Time, Platform, Content Type, Post Content, Status, Notes)
- Smart data validation dropdowns for platforms, content types, and status values
- Sample data to demonstrate usage with realistic examples
- Separate instructions sheet with comprehensive guidelines
- Branded formatting with company colors and proper column sizing
- Automatic retry on Google API failures with exponential backoff
- Secure credential storage with proper file permissions
- Comprehensive logging for debugging and monitoring
- Input sanitization and validation for security

### Dependencies

- **Runtime**: `gspread`, `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`
- **Development**: `pytest`, `pytest-cov`, `black`, `isort`, `flake8`
- **Type Safety**: Full type hints using `typing` module for better IDE support and code clarity

### Authentication Requirements

The script requires:
1. Google Cloud Console project with Sheets API enabled
2. OAuth 2.0 credentials downloaded as `credentials.json` (must be in project root)
3. Configured OAuth consent screen
4. Proper file permissions (credentials.json should be in current directory only)

**Security Note**: The application validates that credential files are in the current directory to prevent path traversal attacks.

### File Structure

```
src/
├── __init__.py                    # Package initialization
└── content_calendar/
    ├── __init__.py               # Module initialization with exports
    └── calendar_generator.py     # Main application logic

tests/
├── conftest.py                   # Test configuration and setup
└── test_calendar_generator.py    # Comprehensive test suite (36 tests)
```

### Code Quality

- **Test Coverage**: 99% (161/163 statements) with comprehensive test suite
- **Security**: Input validation, path sanitization, secure file permissions
- **Error Handling**: Comprehensive error handling with retry logic and proper logging
- **Type Safety**: Full type hints throughout codebase
- **Code Style**: Consistent formatting with Black, isort, and flake8

### Security Features

- **Input Validation**: All user inputs are validated and sanitized
- **Path Security**: File path validation prevents directory traversal attacks
- **Credential Security**: Token files stored with 600 permissions (owner-only)
- **Error Handling**: Errors logged without exposing sensitive information

### Testing

The comprehensive test suite includes:
- **Unit Tests**: All methods and functions thoroughly tested
- **Integration Tests**: End-to-end workflow testing with proper mocking
- **Edge Cases**: Boundary conditions, error scenarios, and input validation
- **Security Tests**: Input sanitization and path validation testing
- **Error Handling**: Retry logic, timeout handling, and graceful degradation

### Development Notes

- Always run tests before committing: `poetry run pytest --cov=src/content_calendar`
- Use type hints for all new functions and methods
- Follow the existing error handling patterns with proper logging
- Security-first approach: validate all inputs and use secure defaults
- The main script is interactive and prompts for client name and planning duration, then creates a shareable Google Sheet with the generated calendar