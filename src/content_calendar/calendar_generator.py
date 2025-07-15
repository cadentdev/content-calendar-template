#!/usr/bin/env python3
"""
Content Calendar Generator for Google Sheets
Creates a simple content calendar template for client use.
"""

import gspread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import os
import stat
from datetime import datetime, timedelta
import logging
import re

# Google Sheets API scope
SCOPES = ["https://www.googleapis.com/spreadsheets"]


class ContentCalendarGenerator:
    # Constants for dropdown options
    PLATFORMS = [
        "LinkedIn",
        "Facebook",
        "Instagram",
        "Twitter",
        "TikTok",
        "YouTube",
        "Blog",
        "Email",
    ]
    CONTENT_TYPES = [
        "Image Post",
        "Video",
        "Carousel",
        "Story",
        "Text Post",
        "Reel",
        "Live Stream",
        "Poll",
    ]
    STATUSES = [
        "Planned",
        "Draft",
        "In Review",
        "Approved",
        "Scheduled",
        "Published",
        "Cancelled",
    ]

    def __init__(self, credentials_file="credentials.json", token_file="token.json"):
        """
        Initialize the Google Sheets client.

        Args:
            credentials_file: Path to Google API credentials JSON file
            token_file: Path to store/load OAuth token
        """
        # Validate file paths for security
        if not os.path.basename(credentials_file) == credentials_file:
            raise ValueError("Credentials file must be in current directory")
        if not os.path.basename(token_file) == token_file:
            raise ValueError("Token file must be in current directory")

        self.credentials_file = credentials_file
        self.token_file = token_file
        self.client = self._authenticate()

    def _authenticate(self):
        """Authenticate with Google Sheets API."""
        creds = None

        # Load existing token if available
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)

        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"Credentials file not found: {self.credentials_file}"
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save credentials for next run with secure permissions
            with open(self.token_file, "w") as token:
                token.write(creds.to_json())
            # Set restrictive file permissions (owner read/write only)
            os.chmod(self.token_file, stat.S_IRUSR | stat.S_IWUSR)

        return gspread.authorize(creds)

    def create_content_calendar(self, client_name, weeks_ahead=4):
        """
        Create a new Google Sheet with content calendar template.

        Args:
            client_name: Name of the client (used in sheet title)
            weeks_ahead: How many weeks to pre-populate with dates

        Returns:
            The created Google Sheet object
        """
        # Create new spreadsheet
        sheet_title = f"{client_name} - Content Calendar"
        spreadsheet = self.client.create(sheet_title)
        worksheet = spreadsheet.sheet1

        # Set up headers
        headers = [
            "Date",
            "Time",
            "Platform",
            "Content Type",
            "Post Content",
            "Status",
            "Notes",
        ]

        # Apply headers
        worksheet.update("A1:G1", [headers])

        # Format headers
        worksheet.format(
            "A1:G1",
            {
                "backgroundColor": {"red": 0.2, "green": 0.6, "blue": 0.9},
                "textFormat": {
                    "bold": True,
                    "foregroundColor": {"red": 1, "green": 1, "blue": 1},
                },
                "horizontalAlignment": "CENTER",
            },
        )

        # Set column widths
        worksheet.update_dimension_group_rows(start=1, end=1, pixel_size=50)

        # Adjust column widths
        dimension_updates = [
            {"range": "A:A", "pixelSize": 100},  # Date
            {"range": "B:B", "pixelSize": 80},  # Time
            {"range": "C:C", "pixelSize": 100},  # Platform
            {"range": "D:D", "pixelSize": 120},  # Content Type
            {"range": "E:E", "pixelSize": 400},  # Post Content
            {"range": "F:F", "pixelSize": 100},  # Status
            {"range": "G:G", "pixelSize": 200},  # Notes
        ]

        for update in dimension_updates:
            worksheet.columns_auto_resize(
                start_column_index=ord(update["range"][0]) - ord("A")
            )

        # Add sample data and data validation
        self._add_sample_data(worksheet, weeks_ahead)
        self._add_data_validation(worksheet)

        # Add instructions sheet
        self._create_instructions_sheet(spreadsheet)

        logging.info(f"Created content calendar: {sheet_title}")
        logging.info(f"Sheet URL: {spreadsheet.url}")

        return spreadsheet

    def _add_sample_data(self, worksheet, weeks_ahead):
        """Add sample data and date structure."""
        current_date = datetime.now().date()

        # Add sample rows for the next few weeks
        # Use class constants for consistency

        # Add a few sample entries
        sample_entries = [
            [
                current_date.strftime("%Y-%m-%d"),
                "09:00",
                "LinkedIn",
                "Image Post",
                "Share industry insights about digital marketing trends...",
                "Draft",
                "Need to add company logo",
            ],
            [
                (current_date + timedelta(days=1)).strftime("%Y-%m-%d"),
                "14:30",
                "Instagram",
                "Story",
                "Behind-the-scenes content from team meeting",
                "Planned",
                "Coordinate with design team",
            ],
            [
                (current_date + timedelta(days=2)).strftime("%Y-%m-%d"),
                "10:15",
                "Facebook",
                "Video",
                "Client testimonial video - case study feature",
                "In Review",
                "Waiting for client approval",
            ],
        ]

        # Add sample data starting from row 2
        if sample_entries:
            range_name = f"A2:G{1 + len(sample_entries)}"
            worksheet.update(range_name, sample_entries)

        # Add some empty rows with just dates for planning
        planning_rows = []
        for i in range(3, weeks_ahead * 7):  # Start after sample data
            future_date = current_date + timedelta(days=i)
            planning_rows.append(
                [future_date.strftime("%Y-%m-%d"), "", "", "", "", "Planned", ""]
            )

        if planning_rows:
            start_row = len(sample_entries) + 2
            range_name = f"A{start_row}:G{start_row + len(planning_rows) - 1}"
            worksheet.update(range_name, planning_rows)

    def _create_dropdown_validation(self, values):
        """Create dropdown validation configuration."""
        return {
            "condition": {
                "type": "ONE_OF_LIST",
                "values": [{"userEnteredValue": val} for val in values],
            },
            "showCustomUi": True,
            "strict": True,
        }

    def _add_data_validation(self, worksheet):
        """Add dropdown validation for specific columns."""
        try:
            # Use class constants for validation
            platform_validation = self._create_dropdown_validation(self.PLATFORMS)
            content_type_validation = self._create_dropdown_validation(
                self.CONTENT_TYPES
            )
            status_validation = self._create_dropdown_validation(self.STATUSES)

            # Apply validations (for rows 2-1000 to cover future entries)
            worksheet.add_validation("C2:C1000", platform_validation)
            worksheet.add_validation("D2:D1000", content_type_validation)
            worksheet.add_validation("F2:F1000", status_validation)
        except Exception as e:
            logging.warning(f"Could not add data validation: {e}")

    def _create_instructions_sheet(self, spreadsheet):
        """Create a second sheet with instructions and guidelines."""
        instructions_sheet = spreadsheet.add_worksheet(
            title="Instructions", rows=50, cols=10
        )

        instructions_content = [
            ["Content Calendar Instructions", "", "", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", "", "", ""],
            ["How to Use This Calendar:", "", "", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", "", "", ""],
            [
                "1. Date & Time",
                "Enter the scheduled publication date and time",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ],
            [
                "2. Platform",
                "Select from the dropdown: LinkedIn, Facebook, Instagram, etc.",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ],
            [
                "3. Content Type",
                "Choose the format: Image Post, Video, Carousel, Story, etc.",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ],
            [
                "4. Post Content",
                "Write your post text, including hashtags and mentions",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ],
            [
                "5. Status",
                "Track progress: Planned → Draft → In Review → Approved → Scheduled → Published",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ],
            [
                "6. Notes",
                "Add any special instructions, asset needs, or reminders",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ],
            ["", "", "", "", "", "", "", "", "", ""],
            ["Tips for Success:", "", "", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", "", "", ""],
            ["• Plan content 1-2 weeks in advance", "", "", "", "", "", "", "", "", ""],
            [
                "• Keep post content concise but engaging",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ],
            [
                "• Use the Notes column for asset requirements",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ],
            [
                "• Update Status as content moves through workflow",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ],
            [
                "• Coordinate with your Cadent Creative team for approvals",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ],
            ["", "", "", "", "", "", "", "", "", ""],
            ["Content Guidelines:", "", "", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", "", "", ""],
            [
                "• Each platform has different optimal posting times",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ],
            [
                "• Keep Instagram captions under 2,200 characters",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ],
            [
                "• LinkedIn posts perform well with 150-300 words",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ],
            [
                "• Include relevant hashtags for discoverability",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ],
            [
                "• Always include a call-to-action when appropriate",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ],
        ]

        # Add instructions content
        instructions_sheet.update("A1:J25", instructions_content)

        # Format the instructions
        instructions_sheet.format(
            "A1",
            {
                "backgroundColor": {"red": 0.2, "green": 0.6, "blue": 0.9},
                "textFormat": {
                    "bold": True,
                    "foregroundColor": {"red": 1, "green": 1, "blue": 1},
                    "fontSize": 14,
                },
            },
        )

        instructions_sheet.format(
            "A3",
            {
                "textFormat": {"bold": True, "fontSize": 12},
            },
        )

        instructions_sheet.format(
            "A12",
            {
                "textFormat": {"bold": True, "fontSize": 12},
            },
        )

        instructions_sheet.format(
            "A20",
            {
                "textFormat": {"bold": True, "fontSize": 12},
            },
        )


def _validate_client_name(client_name):
    """Validate and sanitize client name input."""
    if not client_name:
        return "Sample Client"

    # Remove potentially harmful characters and limit length
    sanitized = re.sub(r'[<>:"/\\|?*]', "", client_name)
    sanitized = sanitized.strip()[:50]  # Limit to 50 characters

    return sanitized if sanitized else "Sample Client"


def _validate_weeks_ahead(weeks_input):
    """Validate and sanitize weeks ahead input."""
    if not weeks_input:
        return 4

    try:
        weeks = int(weeks_input)
        # Limit to reasonable range (1-52 weeks)
        return max(1, min(weeks, 52))
    except ValueError:
        return 4


def main():
    """Main function to create content calendar."""
    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    # Get and validate client name
    client_name_input = input("Enter client name: ").strip()
    client_name = _validate_client_name(client_name_input)

    # Get and validate weeks ahead
    weeks_input = input("How many weeks ahead to plan? (default: 4): ").strip()
    weeks_ahead = _validate_weeks_ahead(weeks_input)

    logging.info(f"Creating content calendar for: {client_name}")
    logging.info("Make sure you have:")
    logging.info("   1. Google API credentials file (credentials.json)")
    logging.info("   2. Enabled Google Sheets API in your Google Cloud Console")
    logging.info("   3. Configured OAuth consent screen")

    try:
        # Create the calendar
        generator = ContentCalendarGenerator()
        spreadsheet = generator.create_content_calendar(client_name, weeks_ahead)

        logging.info("Successfully created content calendar!")
        logging.info(f"Share this URL with your client: {spreadsheet.url}")

    except FileNotFoundError as e:
        logging.error(f"Error: {e}")
        logging.error(
            "Please download your credentials.json file from Google Cloud Console"
        )
    except ValueError as e:
        logging.error(f"Validation error: {e}")
    except Exception as e:
        logging.error(f"Error creating calendar: {e}")
        logging.error("Please check your Google API setup and try again")


if __name__ == "__main__":
    main()
