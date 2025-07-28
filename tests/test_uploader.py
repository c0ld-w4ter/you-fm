"""
Unit tests for uploader module.

Tests the Google Drive API integration for file uploads.
"""

import pytest
from unittest.mock import MagicMock, patch, mock_open
from uploader import upload_to_drive, setup_drive_credentials, verify_folder_access


class TestUploadToDrive:
    """Test cases for upload_to_drive function."""
    
    @patch('uploader.verify_folder_access')
    @patch('uploader.setup_drive_credentials')
    @patch('uploader.get_config')
    def test_upload_to_drive_success(self, mock_config, mock_setup_creds, mock_verify_folder):
        """Test successful file upload to Google Drive."""
        # Mock configuration
        mock_config_instance = MagicMock()
        mock_config_instance.get.return_value = 'test-folder-id'
        mock_config.return_value = mock_config_instance
        
        # Mock Google Drive service
        mock_service = MagicMock()
        mock_setup_creds.return_value = mock_service
        mock_verify_folder.return_value = True
        
        # Mock upload response
        mock_request = MagicMock()
        mock_service.files().create.return_value = mock_request
        mock_request.execute.return_value = {
            'id': 'uploaded-file-id-12345',
            'name': 'daily_briefing_20250128_140000.mp3',
            'size': '1024',
            'webViewLink': 'https://drive.google.com/file/d/uploaded-file-id-12345/view'
        }
        
        # Test data
        audio_data = b'fake_mp3_audio_data_content'
        filename = 'test_briefing.mp3'
        
        # Call function
        result = upload_to_drive(audio_data, filename)
        
        # Verify results
        assert result == 'uploaded-file-id-12345'
        
        # Verify service calls
        mock_setup_creds.assert_called_once()
        mock_verify_folder.assert_called_once_with('test-folder-id')
        mock_service.files().create.assert_called_once()
        
        # Verify file metadata
        call_args = mock_service.files().create.call_args
        file_metadata = call_args[1]['body']
        assert file_metadata['name'] == filename
        assert file_metadata['parents'] == ['test-folder-id']
        
    @patch('uploader.verify_folder_access')
    @patch('uploader.setup_drive_credentials')
    @patch('uploader.get_config')
    @patch('uploader.datetime')
    def test_upload_to_drive_auto_filename(self, mock_datetime, mock_config, mock_setup_creds, mock_verify_folder):
        """Test upload with auto-generated filename."""
        # Mock datetime for consistent filename
        mock_datetime.now.return_value.strftime.return_value = '20250128_140000'
        
        # Mock configuration
        mock_config_instance = MagicMock()
        mock_config_instance.get.return_value = 'test-folder-id'
        mock_config.return_value = mock_config_instance
        
        # Mock Google Drive service
        mock_service = MagicMock()
        mock_setup_creds.return_value = mock_service
        mock_verify_folder.return_value = True
        
        # Mock upload response
        mock_request = MagicMock()
        mock_service.files().create.return_value = mock_request
        mock_request.execute.return_value = {
            'id': 'uploaded-file-id-12345',
            'name': 'daily_briefing_20250128_140000.mp3',
            'size': '1024'
        }
        
        # Test data - no filename provided
        audio_data = b'fake_mp3_audio_data_content'
        
        # Call function without filename
        result = upload_to_drive(audio_data)
        
        # Verify results
        assert result == 'uploaded-file-id-12345'
        
        # Verify auto-generated filename was used
        call_args = mock_service.files().create.call_args
        file_metadata = call_args[1]['body']
        assert file_metadata['name'] == 'daily_briefing_20250128_140000.mp3'
        
    def test_upload_to_drive_empty_audio(self):
        """Test upload with empty audio data."""
        # Test with None
        with pytest.raises(Exception) as exc_info:
            upload_to_drive(None)
        assert "Cannot upload empty audio data" in str(exc_info.value)
        
        # Test with empty bytes
        with pytest.raises(Exception) as exc_info:
            upload_to_drive(b'')
        assert "Cannot upload empty audio data" in str(exc_info.value)
        
    @patch('uploader.get_config')
    def test_upload_to_drive_import_error(self, mock_config):
        """Test handling of missing Google API libraries."""
        # Mock configuration
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        
        # Mock import error by patching the import inside the function
        with patch('builtins.__import__', side_effect=ImportError("No module named 'googleapiclient'")):
            with pytest.raises(Exception) as exc_info:
                upload_to_drive(b'test_audio', 'test.mp3')
            
            assert "Google API libraries not installed" in str(exc_info.value)
            
    @patch('uploader.verify_folder_access')
    @patch('uploader.setup_drive_credentials')
    @patch('uploader.get_config')
    def test_upload_to_drive_folder_access_failed(self, mock_config, mock_setup_creds, mock_verify_folder):
        """Test upload when folder access verification fails."""
        # Mock configuration
        mock_config_instance = MagicMock()
        mock_config_instance.get.return_value = 'invalid-folder-id'
        mock_config.return_value = mock_config_instance
        
        # Mock services
        mock_service = MagicMock()
        mock_setup_creds.return_value = mock_service
        mock_verify_folder.return_value = False  # Folder access failed
        
        # Call function and verify error
        with pytest.raises(Exception) as exc_info:
            upload_to_drive(b'test_audio', 'test.mp3')
            
        assert "Cannot access Google Drive folder 'invalid-folder-id'" in str(exc_info.value)
        
    @patch('uploader.verify_folder_access')  
    @patch('uploader.setup_drive_credentials')
    @patch('uploader.get_config')
    def test_upload_to_drive_api_error_authentication(self, mock_config, mock_setup_creds, mock_verify_folder):
        """Test handling of authentication errors during upload."""
        # Mock configuration
        mock_config_instance = MagicMock()
        mock_config_instance.get.return_value = 'test-folder-id'
        mock_config.return_value = mock_config_instance
        
        # Mock services
        mock_service = MagicMock()
        mock_setup_creds.return_value = mock_service
        mock_verify_folder.return_value = True
        
        # Mock API authentication error
        mock_request = MagicMock()
        mock_service.files().create.return_value = mock_request
        mock_request.execute.side_effect = Exception("Authentication failed: Invalid credentials")
        
        # Call function and verify error handling
        with pytest.raises(Exception) as exc_info:
            upload_to_drive(b'test_audio', 'test.mp3')
            
        assert "Google Drive authentication failed" in str(exc_info.value)
        
    @patch('uploader.verify_folder_access')
    @patch('uploader.setup_drive_credentials') 
    @patch('uploader.get_config')
    def test_upload_to_drive_api_error_quota(self, mock_config, mock_setup_creds, mock_verify_folder):
        """Test handling of quota exceeded errors."""
        # Mock configuration
        mock_config_instance = MagicMock()
        mock_config_instance.get.return_value = 'test-folder-id'
        mock_config.return_value = mock_config_instance
        
        # Mock services
        mock_service = MagicMock()
        mock_setup_creds.return_value = mock_service
        mock_verify_folder.return_value = True
        
        # Mock API quota error
        mock_request = MagicMock()
        mock_service.files().create.return_value = mock_request
        mock_request.execute.side_effect = Exception("Storage quota exceeded")
        
        # Call function and verify error handling
        with pytest.raises(Exception) as exc_info:
            upload_to_drive(b'test_audio', 'test.mp3')
            
        assert "Google Drive storage quota exceeded" in str(exc_info.value)


class TestSetupDriveCredentials:
    """Test cases for setup_drive_credentials function."""
    
    @patch('googleapiclient.discovery.build')
    @patch('google.oauth2.service_account.Credentials.from_service_account_info')
    @patch('os.getenv')
    @patch('uploader.get_config')
    def test_setup_drive_credentials_from_env_json(self, mock_config, mock_getenv, mock_from_service_account, mock_build):
        """Test credential setup from environment JSON."""
        # Mock configuration
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        
        # Mock environment variable with JSON content
        test_service_account_json = '{"type": "service_account", "project_id": "test-project"}'
        mock_getenv.side_effect = lambda key: {
            'GOOGLE_SERVICE_ACCOUNT_JSON': test_service_account_json,
            'GOOGLE_SERVICE_ACCOUNT_FILE': None
        }.get(key)
        
        # Mock service account credentials
        mock_credentials = MagicMock()
        mock_from_service_account.return_value = mock_credentials
        
        # Mock Google Drive service
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        # Call function
        result = setup_drive_credentials()
        
        # Verify results
        assert result == mock_service
        
        # Verify credentials were created from JSON
        mock_from_service_account.assert_called_once()
        service_account_info = mock_from_service_account.call_args[0][0]
        assert service_account_info['type'] == 'service_account'
        assert service_account_info['project_id'] == 'test-project'
        
        # Verify service was built with correct parameters
        mock_build.assert_called_once_with('drive', 'v3', credentials=mock_credentials)
        
    @patch('googleapiclient.discovery.build')
    @patch('google.oauth2.service_account.Credentials.from_service_account_info')
    @patch('os.path.exists')
    @patch('os.getenv')
    @patch('builtins.open', new_callable=mock_open)
    @patch('uploader.get_config')
    def test_setup_drive_credentials_from_file(self, mock_config, mock_file, mock_getenv, mock_exists, mock_from_service_account, mock_build):
        """Test credential setup from service account file."""
        # Mock configuration
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        
        # Mock environment - no JSON, but file path exists
        mock_getenv.side_effect = lambda key: {
            'GOOGLE_SERVICE_ACCOUNT_JSON': None,
            'GOOGLE_SERVICE_ACCOUNT_FILE': '/path/to/service_account.json'
        }.get(key)
        mock_exists.return_value = True
        
        # Mock file content
        test_service_account_data = '{"type": "service_account", "project_id": "test-project-file"}'
        mock_file.return_value.read.return_value = test_service_account_data
        
        # Mock service account credentials
        mock_credentials = MagicMock()
        mock_from_service_account.return_value = mock_credentials
        
        # Mock Google Drive service
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        # Call function
        result = setup_drive_credentials()
        
        # Verify results
        assert result == mock_service
        
        # Verify file was opened and read
        mock_file.assert_called_once_with('/path/to/service_account.json', 'r')
        
    @patch('os.path.exists')
    @patch('os.getenv')
    @patch('uploader.get_config')
    def test_setup_drive_credentials_no_credentials(self, mock_config, mock_getenv, mock_exists):
        """Test error when no credentials are found."""
        # Mock configuration
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        
        # Mock no credentials available
        mock_getenv.return_value = None
        mock_exists.return_value = False
        
        # Call function and verify error
        with pytest.raises(Exception) as exc_info:
            setup_drive_credentials()
            
        assert "Google service account credentials not found" in str(exc_info.value)
        assert "GOOGLE_SERVICE_ACCOUNT_JSON" in str(exc_info.value)
        assert "GOOGLE_SERVICE_ACCOUNT_FILE" in str(exc_info.value)
        
    @patch('uploader.get_config')
    def test_setup_drive_credentials_import_error(self, mock_config):
        """Test handling of missing Google API libraries."""
        # Mock configuration
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        
        # Mock import error by patching the import inside the function
        with patch('builtins.__import__', side_effect=ImportError("No module named 'googleapiclient'")):
            with pytest.raises(Exception) as exc_info:
                setup_drive_credentials()
            
            assert "Required Google API libraries not installed" in str(exc_info.value)
            
    @patch('os.getenv')
    @patch('uploader.get_config')
    def test_setup_drive_credentials_invalid_json(self, mock_config, mock_getenv):
        """Test handling of invalid JSON in environment variable."""
        # Mock configuration
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        
        # Mock environment variable with invalid JSON
        mock_getenv.side_effect = lambda key: {
            'GOOGLE_SERVICE_ACCOUNT_JSON': 'invalid-json-content',
            'GOOGLE_SERVICE_ACCOUNT_FILE': None
        }.get(key)
        
        # Call function and verify error
        with pytest.raises(Exception) as exc_info:
            setup_drive_credentials()
            
        assert "Google service account credentials not found" in str(exc_info.value)


class TestVerifyFolderAccess:
    """Test cases for verify_folder_access function."""
    
    @patch('uploader.setup_drive_credentials')
    def test_verify_folder_access_success(self, mock_setup_creds):
        """Test successful folder access verification."""
        # Mock Google Drive service
        mock_service = MagicMock()
        mock_setup_creds.return_value = mock_service
        
        # Mock folder response with write permissions
        mock_service.files().get.return_value.execute.return_value = {
            'id': 'test-folder-id',
            'name': 'Test Folder',
            'capabilities': {
                'canAddChildren': True
            }
        }
        
        # Call function
        result = verify_folder_access('test-folder-id')
        
        # Verify results
        assert result == True
        
        # Verify API call
        mock_service.files().get.assert_called_once_with(
            fileId='test-folder-id',
            fields='id,name,parents,capabilities'
        )
        
    @patch('uploader.setup_drive_credentials')
    def test_verify_folder_access_no_write_permission(self, mock_setup_creds):
        """Test folder access verification when write permission denied."""
        # Mock Google Drive service
        mock_service = MagicMock()
        mock_setup_creds.return_value = mock_service
        
        # Mock folder response without write permissions
        mock_service.files().get.return_value.execute.return_value = {
            'id': 'test-folder-id',
            'name': 'Read Only Folder',
            'capabilities': {
                'canAddChildren': False
            }
        }
        
        # Call function
        result = verify_folder_access('test-folder-id')
        
        # Verify results
        assert result == False
        
    def test_verify_folder_access_no_folder_id(self):
        """Test folder access verification with no folder ID provided."""
        # Call function with None
        result = verify_folder_access(None)
        
        # Should return True (uploads to root directory)
        assert result == True
        
        # Test with empty string
        result = verify_folder_access('')
        assert result == True
        
    @patch('uploader.setup_drive_credentials')
    def test_verify_folder_access_folder_not_found(self, mock_setup_creds):
        """Test folder access verification when folder not found."""
        # Mock Google Drive service
        mock_service = MagicMock()
        mock_setup_creds.return_value = mock_service
        
        # Mock API error - folder not found
        mock_service.files().get.return_value.execute.side_effect = Exception("File not found (404)")
        
        # Call function and verify error
        with pytest.raises(Exception) as exc_info:
            verify_folder_access('invalid-folder-id')
            
        assert "Google Drive folder 'invalid-folder-id' not found" in str(exc_info.value)
        
    @patch('uploader.setup_drive_credentials')
    def test_verify_folder_access_permission_denied(self, mock_setup_creds):
        """Test folder access verification when permission denied."""
        # Mock Google Drive service
        mock_service = MagicMock()
        mock_setup_creds.return_value = mock_service
        
        # Mock API error - permission denied
        mock_service.files().get.return_value.execute.side_effect = Exception("Forbidden: Insufficient permissions")
        
        # Call function and verify error
        with pytest.raises(Exception) as exc_info:
            verify_folder_access('restricted-folder-id')
            
        assert "No permission to access Google Drive folder" in str(exc_info.value)
        
    @patch('uploader.setup_drive_credentials')
    def test_verify_folder_access_generic_error(self, mock_setup_creds):
        """Test folder access verification with generic error."""
        # Mock Google Drive service
        mock_service = MagicMock()
        mock_setup_creds.return_value = mock_service
        
        # Mock generic API error
        mock_service.files().get.return_value.execute.side_effect = Exception("Network timeout")
        
        # Call function and verify error
        with pytest.raises(Exception) as exc_info:
            verify_folder_access('test-folder-id')
            
        assert "Failed to verify Google Drive folder access" in str(exc_info.value) 