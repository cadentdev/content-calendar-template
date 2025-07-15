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

## Future enhancement possibilities

- Bulk creation for multiple clients
- Custom branding per client
- Integration with scheduling tools
- Performance tracking columns
- Media asset management
