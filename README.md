# content-calendar-template

A Python tool to generate a Google Sheet content calendar. Requires Google API credentials.

The Python script creates a simple, client-friendly content calendar in Google Sheets with these MVP features:

## Core Functionality

- **Essential columns**: Date, Time, Platform, Content Type, Post Content, Status, Notes
- **Dropdown validation** for platforms, content types, and status tracking
- **Sample data** to show clients how to use it
- **Instructions sheet** with guidelines and tips

## Client-Friendly Features

- Clean, professional formatting with branded header colors
- Pre-populated sample entries to demonstrate usage
- Built-in data validation to prevent errors
- Separate instructions sheet for onboarding

## Setup

1. **Install Poetry:**
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. **Install dependencies:**
```bash
poetry install
```

3. **Run the script:**
```bash
poetry run python src/content_calendar/calendar_generator.py
```

4. **Get Google API credentials:**
   - Go to Google Cloud Console
   - Enable Google Sheets API
   - Create credentials (OAuth 2.0) and download as `credentials.json`

3. **Run the script:**
```bash
poetry run python src/content_calendar/calendar_generator.py
```

The script will:
- Authenticate with Google (first time only)
- Create a branded spreadsheet for your client
- Add sample data and validation rules
- Generate a shareable URL

## Architecture

### Security Features
- **Input validation** and sanitization for all user inputs
- **Path validation** to prevent directory traversal attacks
- **Secure credential storage** with 600 file permissions
- **Error handling** that doesn't expose sensitive information

### Reliability Features
- **Retry logic** with exponential backoff for API calls
- **Comprehensive error handling** for network and quota issues
- **Graceful degradation** when optional features fail
- **Logging** throughout the application for debugging

### Code Quality
- **Type hints** throughout codebase for better IDE support
- **Comprehensive unit tests** with 99% coverage
- **Modular design** with clear separation of concerns
- **Configuration management** through class constants

## Contributing

This project follows modern Python development practices:

1. **Code Style**: Uses Black for formatting, isort for imports, flake8 for linting
2. **Testing**: Comprehensive test suite with pytest and high coverage requirements
3. **Security**: Security-first approach with input validation and secure defaults
4. **Documentation**: Clear docstrings and type hints throughout
5. **Error Handling**: Robust error handling with proper logging

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

For issues and questions, please see the [CLAUDE.md](CLAUDE.md) file for development guidance.

## Repository Configuration

For detailed information about branch protection, workflows, and repository settings, see [GitHub Configuration](docs/github_config.md).

## Future Enhancement Possibilities

- Bulk creation for multiple clients
- Custom branding per client
- Integration with scheduling tools
- Performance tracking columns
- Media asset management
- Configuration file support
- CLI argument parsing
- Docker containerization
- API quota monitoring
- Database integration for client management
