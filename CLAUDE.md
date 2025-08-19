# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development Setup
```bash
# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Run the main script (interactive mode)
poetry run python src/content_calendar/calendar_generator.py

# Run with command line arguments (non-interactive)
poetry run python src/content_calendar/calendar_generator.py --client-name "Acme Corp" --weeks 6

# Show help for command line options
poetry run python src/content_calendar/calendar_generator.py --help
```

### Development Tools
```bash
# Code formatting
poetry run black src/ tests/

# Import sorting
poetry run isort src/ tests/

# Linting
poetry run flake8 src/ tests/

# Run all tools together (recommended before committing)
poetry run black src/ tests/ && poetry run isort src/ tests/ && poetry run flake8 src/ tests/ && poetry run pytest --cov=src --cov-report=term-missing
```

## Testing

### Running Tests
```bash
# Run all tests
poetry run pytest

# Run tests with coverage report (matches CI)
poetry run pytest -v --cov=src --cov-report=term-missing --cov-report=xml

# Run a specific test file
poetry run pytest tests/test_calendar_generator.py -v

# Run tests with detailed output
poetry run pytest -v --tb=short
```

### Writing Tests
- Tests are located in the `tests/` directory
- Follow the `test_*.py` naming convention
- Use descriptive test function names starting with `test_`
- Group related tests in classes when appropriate
- Use fixtures for common test data and setup

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

**SECURITY-FIRST SETUP**: This application uses OAuth 2.0 for user authentication, which is the recommended approach for client applications that access user data.

#### Initial Setup (One-time)
1. **Google Cloud Console Setup**:
   - Create a Google Cloud Console project
   - Enable the Google Sheets API
   - Configure OAuth consent screen
   - Create OAuth 2.0 credentials (Desktop application type)
   - Download credentials as `credentials.json`

2. **Secure File Placement**:
   ```bash
   # Place credentials.json in project root (gitignored for security)
   mv ~/Downloads/credentials.json ./credentials.json
   chmod 600 credentials.json  # Restrict to owner-only access
   ```

#### Security Features
- **Git Protection**: `credentials.json` and `token.json` are automatically excluded from git commits
- **Path Validation**: Application validates credential files are in current directory (prevents path traversal)
- **File Permissions**: Token files stored with 600 permissions (owner-only access)
- **OAuth Flow**: First run opens browser for secure OAuth consent (creates `token.json`)
- **Token Refresh**: Automatic token refresh handling for long-running sessions

#### Alternative: Service Account (For Server Applications)
For production server environments, consider using service accounts instead:
```bash
# Download service account key (for server-to-server applications only)
# Place as service-account-key.json and update code to use ServiceAccountCredentials
```

**Important**: Never commit credential files to version control. The `.gitignore` is configured to protect these files.

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

### Development Workflow

This project follows GitHub Flow with branch protection:
- `main` branch: Production-ready code (protected)
- `develop` branch: Integration branch for features
- Create feature branches from `develop`
- Pull requests require passing tests and review

### Development Notes

- Always run full test suite before committing: `poetry run pytest -v --cov=src --cov-report=term-missing`
- Use type hints for all new functions and methods
- Follow the existing error handling patterns with proper logging
- Security-first approach: validate all inputs and use secure defaults
- The main script is interactive and prompts for client name and planning duration, then creates a shareable Google Sheet with the generated calendar

### Authentication Setup

Before running the script for the first time:
1. Create a Google Cloud Console project
2. Enable the Google Sheets API
3. Create OAuth 2.0 credentials (Desktop application)
4. Download `credentials.json` to the project root
5. First run will open browser for OAuth consent