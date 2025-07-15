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
poetry run black .

# Import sorting
poetry run isort .

# Linting
poetry run flake8

# Run tests
poetry run pytest
```

## Architecture

This is a Python CLI tool that generates Google Sheets content calendars for clients. The project uses Poetry for dependency management and follows a simple single-module structure.

### Core Components

- **ContentCalendarGenerator** (`src/content_calendar/calendar_generator.py`): Main class that handles Google Sheets API authentication and calendar creation
- **Google Sheets Integration**: Uses `gspread` library with OAuth2 authentication for Google Sheets API access
- **Authentication Flow**: Supports both initial OAuth setup and token refresh using `credentials.json` and `token.json`

### Key Features

The tool creates professional content calendars with:
- Pre-configured columns (Date, Time, Platform, Content Type, Post Content, Status, Notes)
- Data validation dropdowns for platforms, content types, and status values
- Sample data to demonstrate usage
- Separate instructions sheet with guidelines
- Branded formatting with company colors

### Dependencies

- **Runtime**: `gspread`, `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`
- **Development**: `pytest`, `black`, `isort`, `flake8`

### Authentication Requirements

The script requires:
1. Google Cloud Console project with Sheets API enabled
2. OAuth 2.0 credentials downloaded as `credentials.json`
3. Configured OAuth consent screen

### File Structure

```
src/content_calendar/
├── __init__.py
└── calendar_generator.py  # Main application logic
```

The main script is interactive and prompts for client name and planning duration, then creates a shareable Google Sheet with the generated calendar.