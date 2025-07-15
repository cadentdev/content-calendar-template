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
from datetime import datetime, timedelta
import json

# Google Sheets API scope
SCOPES = ['https://www.googleapis.com/spreadsheets']

class ContentCalendarGenerator:
    def __init__(self, credentials_file='credentials.json', token_file='token.json'):
        """
        Initialize the Google Sheets client.
        
        Args:
            credentials_file: Path to Google API credentials JSON file
            token_file: Path to store/load OAuth token
        """
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
                    raise FileNotFoundError(f"Credentials file not found: {self.credentials_file}")
                
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
        
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
            "Notes"
        ]
        
        # Apply headers
        worksheet.update('A1:G1', [headers])
        
        # Format headers
        worksheet.format('A1:G1', {
            'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.9},
            'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
            'horizontalAlignment': 'CENTER'
        })
        
        # Set column widths
        worksheet.update_dimension_group_rows(
            start=1, end=1, pixel_size=50
        )
        
        # Adjust column widths
        dimension_updates = [
            {'range': 'A:A', 'pixelSize': 100},  # Date
            {'range': 'B:B', 'pixelSize': 80},   # Time
            {'range': 'C:C', 'pixelSize': 100},  # Platform
            {'range': 'D:D', 'pixelSize': 120},  # Content Type
            {'range': 'E:E', 'pixelSize': 400},  # Post Content
            {'range': 'F:F', 'pixelSize': 100},  # Status
            {'range': 'G:G', 'pixelSize': 200},  # Notes
        ]
        
        for update in dimension_updates:
            worksheet.columns_auto_resize(start_column_index=ord(update['range'][0]) - ord('A'))
        
        # Add sample data and data validation
        self._add_sample_data(worksheet, weeks_ahead)
        self._add_data_validation(worksheet)
        
        # Add instructions sheet
        self._create_instructions_sheet(spreadsheet)
        
        print(f"✅ Created content calendar: {sheet_title}")
        print(f"📊 Sheet URL: {spreadsheet.url}")
        
        return spreadsheet
    
    def _add_sample_data(self, worksheet, weeks_ahead):
        """Add sample data and date structure."""
        sample_data = []
        current_date = datetime.now().date()
        
        # Add sample rows for the next few weeks
        platforms = ["LinkedIn", "Facebook", "Instagram", "Twitter"]
        content_types = ["Image Post", "Video", "Carousel", "Story", "Text Post"]
        statuses = ["Draft", "In Review", "Approved", "Scheduled", "Published"]
        
        # Add a few sample entries
        sample_entries = [
            [
                current_date.strftime("%Y-%m-%d"),
                "09:00",
                "LinkedIn",
                "Image Post",
                "Share industry insights about digital marketing trends...",
                "Draft",
                "Need to add company logo"
            ],
            [
                (current_date + timedelta(days=1)).strftime("%Y-%m-%d"),
                "14:30",
                "Instagram",
                "Story",
                "Behind-the-scenes content from team meeting",
                "Planned",
                "Coordinate with design team"
            ],
            [
                (current_date + timedelta(days=2)).strftime("%Y-%m-%d"),
                "10:15",
                "Facebook",
                "Video",
                "Client testimonial video - case study feature",
                "In Review",
                "Waiting for client approval"
            ]
        ]
        
        # Add sample data starting from row 2
        if sample_entries:
            range_name = f"A2:G{1 + len(sample_entries)}"
            worksheet.update(range_name, sample_entries)
        
        # Add some empty rows with just dates for planning
        planning_rows = []
        for i in range(3, weeks_ahead * 7):  # Start after sample data
            future_date = current_date + timedelta(days=i)
            planning_rows.append([future_date.strftime("%Y-%m-%d"), "", "", "", "", "Planned", ""])
        
        if planning_rows:
            start_row = len(sample_entries) + 2
            range_name = f"A{start_row}:G{start_row + len(planning_rows) - 1}"
            worksheet.update(range_name, planning_rows)
    
    def _add_data_validation(self, worksheet):
        """Add dropdown validation for specific columns."""
        
        # Platform validation (Column C)
        platform_validation = {
            'condition': {
                'type': 'ONE_OF_LIST',
                'values': [
                    {'userEnteredValue': 'LinkedIn'},
                    {'userEnteredValue': 'Facebook'},
                    {'userEnteredValue': 'Instagram'},
                    {'userEnteredValue': 'Twitter'},
                    {'userEnteredValue': 'TikTok'},
                    {'userEnteredValue': 'YouTube'},
                    {'userEnteredValue': 'Blog'},
                    {'userEnteredValue': 'Email'},
                ]
            },
            'showCustomUi': True,
            'strict': True
        }
        
        # Content Type validation (Column D)
        content_type_validation = {
            'condition': {
                'type': 'ONE_OF_LIST',
                'values': [
                    {'userEnteredValue': 'Image Post'},
                    {'userEnteredValue': 'Video'},
                    {'userEnteredValue': 'Carousel'},
                    {'userEnteredValue': 'Story'},
                    {'userEnteredValue': 'Text Post'},
                    {'userEnteredValue': 'Reel'},
                    {'userEnteredValue': 'Live Stream'},
                    {'userEnteredValue': 'Poll'},
                ]
            },
            'showCustomUi': True,
            'strict': True
        }
        
        # Status validation (Column F)
        status_validation = {
            'condition': {
                'type': 'ONE_OF_LIST',
                'values': [
                    {'userEnteredValue': 'Planned'},
                    {'userEnteredValue': 'Draft'},
                    {'userEnteredValue': 'In Review'},
                    {'userEnteredValue': 'Approved'},
                    {'userEnteredValue': 'Scheduled'},
                    {'userEnteredValue': 'Published'},
                    {'userEnteredValue': 'Cancelled'},
                ]
            },
            'showCustomUi': True,
            'strict': True
        }
        
        # Apply validations (for rows 2-1000 to cover future entries)
        try:
            worksheet.add_validation('C2:C1000', platform_validation)
            worksheet.add_validation('D2:D1000', content_type_validation)
            worksheet.add_validation('F2:F1000', status_validation)
        except Exception as e:
            print(f"⚠️  Warning: Could not add data validation: {e}")
    
    def _create_instructions_sheet(self, spreadsheet):
        """Create a second sheet with instructions and guidelines."""
        instructions_sheet = spreadsheet.add_worksheet(title="Instructions", rows=50, cols=10)
        
        instructions_content = [
            ["Content Calendar Instructions", "", "", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", "", "", ""],
            ["How to Use This Calendar:", "", "", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", "", "", ""],
            ["1. Date & Time", "Enter the scheduled publication date and time", "", "", "", "", "", "", "", ""],
            ["2. Platform", "Select from the dropdown: LinkedIn, Facebook, Instagram, etc.", "", "", "", "", "", "", "", ""],
            ["3. Content Type", "Choose the format: Image Post, Video, Carousel, Story, etc.", "", "", "", "", "", "", "", ""],
            ["4. Post Content", "Write your post text, including hashtags and mentions", "", "", "", "", "", "", "", ""],
            ["5. Status", "Track progress: Planned → Draft → In Review → Approved → Scheduled → Published", "", "", "", "", "", "", "", ""],
            ["6. Notes", "Add any special instructions, asset needs, or reminders", "", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", "", "", ""],
            ["Tips for Success:", "", "", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", "", "", ""],
            ["• Plan content 1-2 weeks in advance", "", "", "", "", "", "", "", "", ""],
            ["• Keep post content concise but engaging", "", "", "", "", "", "", "", "", ""],
            ["• Use the Notes column for asset requirements", "", "", "", "", "", "", "", "", ""],
            ["• Update Status as content moves through workflow", "", "", "", "", "", "", "", "", ""],
            ["• Coordinate with your Cadent Creative team for approvals", "", "", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", "", "", ""],
            ["Content Guidelines:", "", "", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", "", "", ""],
            ["• Each platform has different optimal posting times", "", "", "", "", "", "", "", "", ""],
            ["• Keep Instagram captions under 2,200 characters", "", "", "", "", "", "", "", "", ""],
            ["• LinkedIn posts perform well with 150-300 words", "", "", "", "", "", "", "", "", ""],
            ["• Include relevant hashtags for discoverability", "", "", "", "", "", "", "", "", ""],
            ["• Always include a call-to-action when appropriate", "", "", "", "", "", "", "", "", ""],
        ]
        
        # Add instructions content
        instructions_sheet.update('A1:J25', instructions_content)
        
        # Format the instructions
        instructions_sheet.format('A1', {
            'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.9},
            'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}, 'fontSize': 14},
        })
        
        instructions_sheet.format('A3', {
            'textFormat': {'bold': True, 'fontSize': 12},
        })
        
        instructions_sheet.format('A12', {
            'textFormat': {'bold': True, 'fontSize': 12},
        })
        
        instructions_sheet.format('A20', {
            'textFormat': {'bold': True, 'fontSize': 12},
        })

def main():
    """Main function to create content calendar."""
    # Get client name
    client_name = input("Enter client name: ").strip()
    if not client_name:
        client_name = "Sample Client"
    
    # Get weeks ahead (optional)
    weeks_input = input("How many weeks ahead to plan? (default: 4): ").strip()
    try:
        weeks_ahead = int(weeks_input) if weeks_input else 4
    except ValueError:
        weeks_ahead = 4
    
    print(f"\n🚀 Creating content calendar for: {client_name}")
    print("📝 Make sure you have:")
    print("   1. Google API credentials file (credentials.json)")
    print("   2. Enabled Google Sheets API in your Google Cloud Console")
    print("   3. Configured OAuth consent screen\n")
    
    try:
        # Create the calendar
        generator = ContentCalendarGenerator()
        spreadsheet = generator.create_content_calendar(client_name, weeks_ahead)
        
        print(f"\n✨ Successfully created content calendar!")
        print(f"🔗 Share this URL with your client: {spreadsheet.url}")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("Please download your credentials.json file from Google Cloud Console")
    except Exception as e:
        print(f"❌ Error creating calendar: {e}")
        print("Please check your Google API setup and try again")

if __name__ == "__main__":
    main()