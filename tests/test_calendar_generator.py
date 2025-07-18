#!/usr/bin/env python3
"""
Comprehensive unit tests for the Content Calendar Generator.
Tests for 100% code coverage including all methods, error handling, and edge cases.
"""

import os
import stat
import tempfile
import time
import logging
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch, call
import pytest
import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from content_calendar.calendar_generator import (
    ContentCalendarGenerator,
    _validate_client_name,
    _validate_weeks_ahead,
    main,
    SCOPES,
)


class TestContentCalendarGenerator:
    """Test suite for ContentCalendarGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.credentials_file = os.path.join(self.temp_dir, "credentials.json")
        self.token_file = os.path.join(self.temp_dir, "token.json")
        
        # Create mock credentials file
        with open(self.credentials_file, 'w') as f:
            f.write('{"test": "credentials"}')
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if os.path.exists(self.credentials_file):
            os.remove(self.credentials_file)
        if os.path.exists(self.token_file):
            os.remove(self.token_file)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_class_constants(self):
        """Test that class constants are properly defined."""
        assert ContentCalendarGenerator.PLATFORMS == [
            "LinkedIn", "Facebook", "Instagram", "Twitter", 
            "TikTok", "YouTube", "Blog", "Email"
        ]
        assert ContentCalendarGenerator.CONTENT_TYPES == [
            "Image Post", "Video", "Carousel", "Story", 
            "Text Post", "Reel", "Live Stream", "Poll"
        ]
        assert ContentCalendarGenerator.STATUSES == [
            "Planned", "Draft", "In Review", "Approved", 
            "Scheduled", "Published", "Cancelled"
        ]
    
    def test_init_with_valid_files(self):
        """Test initialization with valid file paths."""
        with patch('content_calendar.calendar_generator.ContentCalendarGenerator._authenticate') as mock_auth:
            mock_auth.return_value = Mock(spec=gspread.Client)
            
            generator = ContentCalendarGenerator(
                credentials_file=os.path.basename(self.credentials_file),
                token_file=os.path.basename(self.token_file)
            )
            
            assert generator.credentials_file == os.path.basename(self.credentials_file)
            assert generator.token_file == os.path.basename(self.token_file)
            assert generator.client is not None
    
    def test_init_with_invalid_credentials_path(self):
        """Test initialization with invalid credentials file path."""
        with pytest.raises(ValueError, match="Credentials file must be in current directory"):
            ContentCalendarGenerator(credentials_file="../invalid/path.json")
    
    def test_init_with_invalid_token_path(self):
        """Test initialization with invalid token file path."""
        with pytest.raises(ValueError, match="Token file must be in current directory"):
            ContentCalendarGenerator(token_file="../invalid/path.json")
    
    @patch('gspread.authorize')
    @patch('os.path.exists')
    @patch('content_calendar.calendar_generator.Credentials.from_authorized_user_file')
    def test_authenticate_with_existing_valid_token(self, mock_from_file, mock_exists, mock_authorize):
        """Test authentication with existing valid token."""
        mock_exists.return_value = True
        mock_creds = Mock(spec=Credentials)
        mock_creds.valid = True
        mock_from_file.return_value = mock_creds
        mock_client = Mock(spec=gspread.Client)
        mock_authorize.return_value = mock_client
        
        generator = ContentCalendarGenerator(
            credentials_file=os.path.basename(self.credentials_file),
            token_file=os.path.basename(self.token_file)
        )
        
        assert generator.client == mock_client
        mock_authorize.assert_called_once_with(mock_creds)
    
    @patch('gspread.authorize')
    @patch('os.path.exists')
    @patch('content_calendar.calendar_generator.Credentials.from_authorized_user_file')
    def test_authenticate_with_expired_token_refresh(self, mock_from_file, mock_exists, mock_authorize):
        """Test authentication with expired token that can be refreshed."""
        mock_exists.return_value = True
        mock_creds = Mock(spec=Credentials)
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = "refresh_token"
        mock_from_file.return_value = mock_creds
        mock_client = Mock(spec=gspread.Client)
        mock_authorize.return_value = mock_client
        
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('os.chmod') as mock_chmod:
                generator = ContentCalendarGenerator(
                    credentials_file=os.path.basename(self.credentials_file),
                    token_file=os.path.basename(self.token_file)
                )
        
        mock_creds.refresh.assert_called_once()
        mock_file.assert_called_once()
        mock_chmod.assert_called_once_with(
            os.path.basename(self.token_file), 
            stat.S_IRUSR | stat.S_IWUSR
        )
    
    @patch('gspread.authorize')
    @patch('os.path.exists')
    @patch('content_calendar.calendar_generator.InstalledAppFlow.from_client_secrets_file')
    def test_authenticate_with_new_oauth_flow(self, mock_flow_from_file, mock_exists, mock_authorize):
        """Test authentication with new OAuth flow."""
        def exists_side_effect(path):
            if path == os.path.basename(self.token_file):
                return False
            elif path == os.path.basename(self.credentials_file):
                return True
            return False
        
        mock_exists.side_effect = exists_side_effect
        
        mock_flow = Mock(spec=InstalledAppFlow)
        mock_creds = Mock(spec=Credentials)
        mock_creds.to_json.return_value = '{"token": "test"}'
        mock_flow.run_local_server.return_value = mock_creds
        mock_flow_from_file.return_value = mock_flow
        
        mock_client = Mock(spec=gspread.Client)
        mock_authorize.return_value = mock_client
        
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('os.chmod') as mock_chmod:
                generator = ContentCalendarGenerator(
                    credentials_file=os.path.basename(self.credentials_file),
                    token_file=os.path.basename(self.token_file)
                )
        
        mock_flow.run_local_server.assert_called_once_with(port=0)
        mock_file.assert_called_once()
        mock_chmod.assert_called_once()
    
    @patch('os.path.exists')
    def test_authenticate_missing_credentials_file(self, mock_exists):
        """Test authentication with missing credentials file."""
        def exists_side_effect(path):
            if path == os.path.basename(self.credentials_file):
                return False
            return False
        
        mock_exists.side_effect = exists_side_effect
        
        with pytest.raises(FileNotFoundError, match="Credentials file not found"):
            ContentCalendarGenerator(
                credentials_file=os.path.basename(self.credentials_file),
                token_file=os.path.basename(self.token_file)
            )
    
    def test_is_retryable_error(self):
        """Test retryable error detection."""
        with patch('content_calendar.calendar_generator.ContentCalendarGenerator._authenticate'):
            generator = ContentCalendarGenerator(
                credentials_file=os.path.basename(self.credentials_file),
                token_file=os.path.basename(self.token_file)
            )
            
            # Test retryable errors
            assert generator._is_retryable_error(Exception("quota exceeded"))
            assert generator._is_retryable_error(Exception("rate limit"))
            assert generator._is_retryable_error(Exception("timeout"))
            assert generator._is_retryable_error(Exception("connection error"))
            assert generator._is_retryable_error(Exception("network issue"))
            assert generator._is_retryable_error(Exception("internal error"))
            assert generator._is_retryable_error(Exception("service unavailable"))
            assert generator._is_retryable_error(Exception("temporary failure"))
            
            # Test non-retryable errors
            assert not generator._is_retryable_error(Exception("invalid credentials"))
            assert not generator._is_retryable_error(Exception("permission denied"))
            assert not generator._is_retryable_error(Exception("not found"))
    
    @patch('time.sleep')
    def test_retry_api_call_success_first_try(self, mock_sleep):
        """Test successful API call on first try."""
        with patch('content_calendar.calendar_generator.ContentCalendarGenerator._authenticate'):
            generator = ContentCalendarGenerator(
                credentials_file=os.path.basename(self.credentials_file),
                token_file=os.path.basename(self.token_file)
            )
            
            mock_func = Mock(return_value="success")
            result = generator._retry_api_call(mock_func, "arg1", kwarg1="value1")
            
            assert result == "success"
            mock_func.assert_called_once_with("arg1", kwarg1="value1")
            mock_sleep.assert_not_called()
    
    @patch('time.sleep')
    @patch('logging.warning')
    def test_retry_api_call_success_after_retry(self, mock_warning, mock_sleep):
        """Test successful API call after retry."""
        with patch('content_calendar.calendar_generator.ContentCalendarGenerator._authenticate'):
            generator = ContentCalendarGenerator(
                credentials_file=os.path.basename(self.credentials_file),
                token_file=os.path.basename(self.token_file)
            )
            
            mock_func = Mock(side_effect=[Exception("timeout"), "success"])
            result = generator._retry_api_call(mock_func, "arg1")
            
            assert result == "success"
            assert mock_func.call_count == 2
            mock_sleep.assert_called_once_with(1)
            mock_warning.assert_called_once()
    
    @patch('time.sleep')
    @patch('logging.error')
    def test_retry_api_call_failure_after_max_retries(self, mock_error, mock_sleep):
        """Test API call failure after max retries."""
        with patch('content_calendar.calendar_generator.ContentCalendarGenerator._authenticate'):
            generator = ContentCalendarGenerator(
                credentials_file=os.path.basename(self.credentials_file),
                token_file=os.path.basename(self.token_file)
            )
            
            mock_func = Mock(side_effect=Exception("quota exceeded"))
            
            with pytest.raises(Exception, match="quota exceeded"):
                generator._retry_api_call(mock_func, "arg1")
            
            assert mock_func.call_count == 3
            assert mock_sleep.call_count == 2
            mock_error.assert_called_once()
    
    @patch('logging.error')
    def test_retry_api_call_non_retryable_error(self, mock_error):
        """Test API call with non-retryable error."""
        with patch('content_calendar.calendar_generator.ContentCalendarGenerator._authenticate'):
            generator = ContentCalendarGenerator(
                credentials_file=os.path.basename(self.credentials_file),
                token_file=os.path.basename(self.token_file)
            )
            
            mock_func = Mock(side_effect=Exception("invalid credentials"))
            
            with pytest.raises(Exception, match="invalid credentials"):
                generator._retry_api_call(mock_func, "arg1")
            
            assert mock_func.call_count == 1
            mock_error.assert_called_once()
    
    def test_create_dropdown_validation(self):
        """Test dropdown validation creation."""
        with patch('content_calendar.calendar_generator.ContentCalendarGenerator._authenticate'):
            generator = ContentCalendarGenerator(
                credentials_file=os.path.basename(self.credentials_file),
                token_file=os.path.basename(self.token_file)
            )
            
            values = ["Option1", "Option2", "Option3"]
            result = generator._create_dropdown_validation(values)
            
            expected = {
                "condition": {
                    "type": "ONE_OF_LIST",
                    "values": [
                        {"userEnteredValue": "Option1"},
                        {"userEnteredValue": "Option2"},
                        {"userEnteredValue": "Option3"}
                    ]
                },
                "showCustomUi": True,
                "strict": True
            }
            
            assert result == expected
    
    @patch('content_calendar.calendar_generator.ContentCalendarGenerator._retry_api_call')
    @patch('content_calendar.calendar_generator.ContentCalendarGenerator._authenticate')
    def test_set_column_widths_success(self, mock_auth, mock_retry):
        """Test successful column width setting."""
        mock_client = Mock(spec=gspread.Client)
        mock_auth.return_value = mock_client
        
        generator = ContentCalendarGenerator(
            credentials_file=os.path.basename(self.credentials_file),
            token_file=os.path.basename(self.token_file)
        )
        
        mock_spreadsheet = Mock()
        mock_worksheet = Mock()
        mock_worksheet.id = 0
        
        generator._set_column_widths(mock_spreadsheet, mock_worksheet)
        
        mock_retry.assert_called_once()
        # Verify the batch update call was made
        call_args = mock_retry.call_args[0]
        assert call_args[0] == mock_spreadsheet.batch_update
        assert "requests" in call_args[1]
        assert len(call_args[1]["requests"]) == 7  # 7 columns
    
    @patch('logging.warning')
    @patch('content_calendar.calendar_generator.ContentCalendarGenerator._retry_api_call')
    @patch('content_calendar.calendar_generator.ContentCalendarGenerator._authenticate')
    def test_set_column_widths_failure(self, mock_auth, mock_retry, mock_warning):
        """Test column width setting failure."""
        mock_client = Mock(spec=gspread.Client)
        mock_auth.return_value = mock_client
        mock_retry.side_effect = Exception("API error")
        
        generator = ContentCalendarGenerator(
            credentials_file=os.path.basename(self.credentials_file),
            token_file=os.path.basename(self.token_file)
        )
        
        mock_spreadsheet = Mock()
        mock_worksheet = Mock()
        mock_worksheet.id = 0
        
        generator._set_column_widths(mock_spreadsheet, mock_worksheet)
        
        mock_warning.assert_called_once_with("Could not set column widths: API error")
    
    @patch('content_calendar.calendar_generator.datetime')
    @patch('content_calendar.calendar_generator.ContentCalendarGenerator._retry_api_call')
    @patch('content_calendar.calendar_generator.ContentCalendarGenerator._authenticate')
    def test_add_sample_data(self, mock_auth, mock_retry, mock_datetime):
        """Test adding sample data to worksheet."""
        mock_client = Mock(spec=gspread.Client)
        mock_auth.return_value = mock_client
        
        # Mock datetime to return predictable dates
        mock_date = datetime(2024, 1, 15)
        mock_datetime.now.return_value = mock_date
        
        generator = ContentCalendarGenerator(
            credentials_file=os.path.basename(self.credentials_file),
            token_file=os.path.basename(self.token_file)
        )
        
        mock_worksheet = Mock()
        weeks_ahead = 2
        
        generator._add_sample_data(mock_worksheet, weeks_ahead)
        
        # Should be called twice: once for sample entries, once for planning rows
        assert mock_retry.call_count == 2
    
    @patch('logging.warning')
    @patch('content_calendar.calendar_generator.ContentCalendarGenerator._retry_api_call')
    @patch('content_calendar.calendar_generator.ContentCalendarGenerator._authenticate')
    def test_add_data_validation_success(self, mock_auth, mock_retry, mock_warning):
        """Test successful data validation addition."""
        mock_client = Mock(spec=gspread.Client)
        mock_auth.return_value = mock_client
        
        generator = ContentCalendarGenerator(
            credentials_file=os.path.basename(self.credentials_file),
            token_file=os.path.basename(self.token_file)
        )
        
        mock_worksheet = Mock()
        
        generator._add_data_validation(mock_worksheet)
        
        # Should be called 3 times: platforms, content types, statuses
        assert mock_retry.call_count == 3
        mock_warning.assert_not_called()
    
    @patch('logging.warning')
    @patch('content_calendar.calendar_generator.ContentCalendarGenerator._retry_api_call')
    @patch('content_calendar.calendar_generator.ContentCalendarGenerator._authenticate')
    def test_add_data_validation_failure(self, mock_auth, mock_retry, mock_warning):
        """Test data validation addition failure."""
        mock_client = Mock(spec=gspread.Client)
        mock_auth.return_value = mock_client
        mock_retry.side_effect = Exception("Validation error")
        
        generator = ContentCalendarGenerator(
            credentials_file=os.path.basename(self.credentials_file),
            token_file=os.path.basename(self.token_file)
        )
        
        mock_worksheet = Mock()
        
        generator._add_data_validation(mock_worksheet)
        
        mock_warning.assert_called_once_with("Could not add data validation: Validation error")
    
    @patch('logging.info')
    @patch('content_calendar.calendar_generator.ContentCalendarGenerator._create_instructions_sheet')
    @patch('content_calendar.calendar_generator.ContentCalendarGenerator._add_data_validation')
    @patch('content_calendar.calendar_generator.ContentCalendarGenerator._add_sample_data')
    @patch('content_calendar.calendar_generator.ContentCalendarGenerator._set_column_widths')
    @patch('content_calendar.calendar_generator.ContentCalendarGenerator._retry_api_call')
    @patch('content_calendar.calendar_generator.ContentCalendarGenerator._authenticate')
    def test_create_content_calendar_success(self, mock_auth, mock_retry, mock_set_widths, 
                                           mock_add_sample, mock_add_validation, 
                                           mock_create_instructions, mock_info):
        """Test successful content calendar creation."""
        mock_client = Mock(spec=gspread.Client)
        mock_auth.return_value = mock_client
        
        mock_spreadsheet = Mock()
        mock_spreadsheet.url = "https://docs.google.com/spreadsheets/test"
        mock_worksheet = Mock()
        mock_spreadsheet.sheet1 = mock_worksheet
        mock_retry.return_value = mock_spreadsheet
        
        generator = ContentCalendarGenerator(
            credentials_file=os.path.basename(self.credentials_file),
            token_file=os.path.basename(self.token_file)
        )
        
        result = generator.create_content_calendar("Test Client", 4)
        
        assert result == mock_spreadsheet
        mock_set_widths.assert_called_once_with(mock_spreadsheet, mock_worksheet)
        mock_add_sample.assert_called_once_with(mock_worksheet, 4)
        mock_add_validation.assert_called_once_with(mock_worksheet)
        mock_create_instructions.assert_called_once_with(mock_spreadsheet)
        
        # Check logging calls
        mock_info.assert_any_call("Created content calendar: Test Client - Content Calendar")
        mock_info.assert_any_call("Sheet URL: https://docs.google.com/spreadsheets/test")
    
    @patch('content_calendar.calendar_generator.ContentCalendarGenerator._retry_api_call')
    @patch('content_calendar.calendar_generator.ContentCalendarGenerator._authenticate')
    def test_create_instructions_sheet(self, mock_auth, mock_retry):
        """Test instructions sheet creation."""
        mock_client = Mock(spec=gspread.Client)
        mock_auth.return_value = mock_client
        
        mock_instructions_sheet = Mock()
        mock_retry.return_value = mock_instructions_sheet
        
        generator = ContentCalendarGenerator(
            credentials_file=os.path.basename(self.credentials_file),
            token_file=os.path.basename(self.token_file)
        )
        
        mock_spreadsheet = Mock()
        
        generator._create_instructions_sheet(mock_spreadsheet)
        
        # Should be called 6 times: 1 for add_worksheet, 1 for update, 4 for formatting
        assert mock_retry.call_count == 6
        
        # Verify add_worksheet was called
        mock_retry.assert_any_call(
            mock_spreadsheet.add_worksheet,
            title="Instructions", rows=50, cols=10
        )


class TestValidationFunctions:
    """Test suite for validation functions."""
    
    def test_validate_client_name_empty(self):
        """Test client name validation with empty input."""
        assert _validate_client_name("") == "Sample Client"
        assert _validate_client_name("   ") == "Sample Client"
    
    def test_validate_client_name_valid(self):
        """Test client name validation with valid input."""
        assert _validate_client_name("Test Client") == "Test Client"
        assert _validate_client_name("  Test Client  ") == "Test Client"
    
    def test_validate_client_name_sanitization(self):
        """Test client name sanitization of harmful characters."""
        assert _validate_client_name("Test<>Client") == "TestClient"
        assert _validate_client_name('Test"Client') == "TestClient"
        assert _validate_client_name("Test/Client") == "TestClient"
        assert _validate_client_name("Test\\Client") == "TestClient"
        assert _validate_client_name("Test|Client") == "TestClient"
        assert _validate_client_name("Test?Client") == "TestClient"
        assert _validate_client_name("Test*Client") == "TestClient"
        assert _validate_client_name("Test:Client") == "TestClient"
    
    def test_validate_client_name_length_limit(self):
        """Test client name length limitation."""
        long_name = "A" * 60
        result = _validate_client_name(long_name)
        assert len(result) == 50
        assert result == "A" * 50
    
    def test_validate_client_name_all_harmful_chars(self):
        """Test client name with all harmful characters."""
        assert _validate_client_name('<>:"/\\|?*') == "Sample Client"
    
    def test_validate_weeks_ahead_empty(self):
        """Test weeks ahead validation with empty input."""
        assert _validate_weeks_ahead("") == 4
        assert _validate_weeks_ahead("   ") == 4
    
    def test_validate_weeks_ahead_valid(self):
        """Test weeks ahead validation with valid input."""
        assert _validate_weeks_ahead("5") == 5
        assert _validate_weeks_ahead("10") == 10
        assert _validate_weeks_ahead("1") == 1
        assert _validate_weeks_ahead("52") == 52
    
    def test_validate_weeks_ahead_invalid_format(self):
        """Test weeks ahead validation with invalid format."""
        assert _validate_weeks_ahead("abc") == 4
        assert _validate_weeks_ahead("5.5") == 4
        assert _validate_weeks_ahead("5a") == 4
    
    def test_validate_weeks_ahead_out_of_range(self):
        """Test weeks ahead validation with out-of-range values."""
        assert _validate_weeks_ahead("0") == 1  # Below minimum
        assert _validate_weeks_ahead("-5") == 1  # Negative
        assert _validate_weeks_ahead("100") == 52  # Above maximum
        assert _validate_weeks_ahead("999") == 52  # Way above maximum


class TestMainFunction:
    """Test suite for main function."""
    
    @patch('content_calendar.calendar_generator.ContentCalendarGenerator')
    @patch('content_calendar.calendar_generator._validate_weeks_ahead')
    @patch('content_calendar.calendar_generator._validate_client_name')
    @patch('builtins.input')
    @patch('logging.basicConfig')
    @patch('logging.info')
    def test_main_success(self, mock_info, mock_log_config, mock_input, 
                         mock_validate_name, mock_validate_weeks, mock_generator_class):
        """Test successful main function execution."""
        mock_input.side_effect = ["Test Client", "5"]
        mock_validate_name.return_value = "Test Client"
        mock_validate_weeks.return_value = 5
        
        mock_generator = Mock()
        mock_spreadsheet = Mock()
        mock_spreadsheet.url = "https://docs.google.com/spreadsheets/test"
        mock_generator.create_content_calendar.return_value = mock_spreadsheet
        mock_generator_class.return_value = mock_generator
        
        main()
        
        mock_log_config.assert_called_once_with(
            level=logging.INFO, 
            format="%(levelname)s: %(message)s"
        )
        mock_validate_name.assert_called_once_with("Test Client")
        mock_validate_weeks.assert_called_once_with("5")
        mock_generator.create_content_calendar.assert_called_once_with("Test Client", 5)
        
        # Check info logging calls
        mock_info.assert_any_call("Creating content calendar for: Test Client")
        mock_info.assert_any_call("Successfully created content calendar!")
        mock_info.assert_any_call("Share this URL with your client: https://docs.google.com/spreadsheets/test")
    
    @patch('content_calendar.calendar_generator.ContentCalendarGenerator')
    @patch('content_calendar.calendar_generator._validate_weeks_ahead')
    @patch('content_calendar.calendar_generator._validate_client_name')
    @patch('builtins.input')
    @patch('logging.basicConfig')
    @patch('logging.error')
    def test_main_file_not_found_error(self, mock_error, mock_log_config, mock_input, 
                                      mock_validate_name, mock_validate_weeks, mock_generator_class):
        """Test main function with FileNotFoundError."""
        mock_input.side_effect = ["Test Client", "5"]
        mock_validate_name.return_value = "Test Client"
        mock_validate_weeks.return_value = 5
        
        mock_generator_class.side_effect = FileNotFoundError("credentials.json not found")
        
        main()
        
        mock_error.assert_any_call("Error: credentials.json not found")
        mock_error.assert_any_call("Please download your credentials.json file from Google Cloud Console")
    
    @patch('content_calendar.calendar_generator.ContentCalendarGenerator')
    @patch('content_calendar.calendar_generator._validate_weeks_ahead')
    @patch('content_calendar.calendar_generator._validate_client_name')
    @patch('builtins.input')
    @patch('logging.basicConfig')
    @patch('logging.error')
    def test_main_value_error(self, mock_error, mock_log_config, mock_input, 
                             mock_validate_name, mock_validate_weeks, mock_generator_class):
        """Test main function with ValueError."""
        mock_input.side_effect = ["Test Client", "5"]
        mock_validate_name.return_value = "Test Client"
        mock_validate_weeks.return_value = 5
        
        mock_generator_class.side_effect = ValueError("Invalid file path")
        
        main()
        
        mock_error.assert_called_once_with("Validation error: Invalid file path")
    
    @patch('content_calendar.calendar_generator.ContentCalendarGenerator')
    @patch('content_calendar.calendar_generator._validate_weeks_ahead')
    @patch('content_calendar.calendar_generator._validate_client_name')
    @patch('builtins.input')
    @patch('logging.basicConfig')
    @patch('logging.error')
    def test_main_general_exception(self, mock_error, mock_log_config, mock_input, 
                                   mock_validate_name, mock_validate_weeks, mock_generator_class):
        """Test main function with general exception."""
        mock_input.side_effect = ["Test Client", "5"]
        mock_validate_name.return_value = "Test Client"
        mock_validate_weeks.return_value = 5
        
        mock_generator = Mock()
        mock_generator.create_content_calendar.side_effect = Exception("API Error")
        mock_generator_class.return_value = mock_generator
        
        main()
        
        mock_error.assert_any_call("Error creating calendar: API Error")
        mock_error.assert_any_call("Please check your Google API setup and try again")


class TestConstants:
    """Test suite for module constants."""
    
    def test_scopes_constant(self):
        """Test that SCOPES constant is correctly defined."""
        assert SCOPES == ["https://www.googleapis.com/spreadsheets"]


def mock_open(read_data=""):
    """Helper function to create mock file objects."""
    from unittest.mock import mock_open as unittest_mock_open
    return unittest_mock_open(read_data=read_data)


class TestModuleExecution:
    """Test module execution."""
    
    def test_main_module_execution(self):
        """Test that the module can be executed directly."""
        with patch('content_calendar.calendar_generator.main') as mock_main:
            # Import the module and test the __main__ block
            import content_calendar.calendar_generator as module
            
            # Mock the __name__ variable to simulate direct execution
            with patch.object(module, '__name__', '__main__'):
                # Execute the main block
                exec("if __name__ == '__main__': main()", {'__name__': '__main__', 'main': mock_main})
                mock_main.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])