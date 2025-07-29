"""
Tests for the uploader module.

This module tests the S3 upload functionality.
"""

import pytest
from unittest.mock import patch, MagicMock
from uploader import upload_to_s3, verify_bucket_access, setup_s3_credentials


class TestUploadToS3:
    """Test cases for upload_to_s3 function."""
    
    @patch('uploader.verify_bucket_access')
    @patch('uploader.get_config')
    def test_upload_to_s3_success(self, mock_config, mock_verify_bucket):
        """Test successful S3 upload."""
        # Mock configuration
        mock_config_instance = MagicMock()
        mock_config_instance.get.return_value = 'test-bucket'
        mock_config.return_value = mock_config_instance
        
        # Mock S3 client
        mock_s3_client = MagicMock()
        
        # Mock bucket verification
        mock_verify_bucket.return_value = True
        
        # Test data
        audio_data = b'test_audio_data'
        filename = 'test_briefing.mp3'
        
        # Mock boto3 import inside the function
        with patch('builtins.__import__') as mock_import:
            def side_effect(name, *args, **kwargs):
                if name == 'boto3':
                    mock_boto3 = MagicMock()
                    mock_boto3.client.return_value = mock_s3_client
                    return mock_boto3
                elif name == 'botocore.exceptions':
                    mock_exceptions = MagicMock()
                    mock_exceptions.ClientError = Exception
                    mock_exceptions.NoCredentialsError = Exception
                    return mock_exceptions
                return __import__(name, *args, **kwargs)
            
            mock_import.side_effect = side_effect
            
            # Call function
            result = upload_to_s3(audio_data, filename)
        
        # Verify S3 client was called correctly
        mock_s3_client.put_object.assert_called_once()
        call_args = mock_s3_client.put_object.call_args
        
        assert call_args[1]['Bucket'] == 'test-bucket'
        assert call_args[1]['Key'] == filename
        assert call_args[1]['Body'] == audio_data
        assert call_args[1]['ContentType'] == 'audio/mpeg'
        
        # Verify result is S3 URL
        assert result == f"https://test-bucket.s3.amazonaws.com/{filename}"
    
    @patch('uploader.verify_bucket_access')
    @patch('uploader.get_config')
    @patch('uploader.datetime')
    def test_upload_to_s3_auto_filename(self, mock_datetime, mock_config, mock_verify_bucket):
        """Test S3 upload with auto-generated filename."""
        # Mock datetime
        mock_datetime.now.return_value.strftime.return_value = '20250128_143000'
        
        # Mock configuration
        mock_config_instance = MagicMock()
        mock_config_instance.get.return_value = 'test-bucket'
        mock_config.return_value = mock_config_instance
        
        # Mock S3 client
        mock_s3_client = MagicMock()
        
        # Mock bucket verification
        mock_verify_bucket.return_value = True
        
        # Test data
        audio_data = b'test_audio_data'
        
        # Mock boto3 import inside the function
        with patch('builtins.__import__') as mock_import:
            def side_effect(name, *args, **kwargs):
                if name == 'boto3':
                    mock_boto3 = MagicMock()
                    mock_boto3.client.return_value = mock_s3_client
                    return mock_boto3
                elif name == 'botocore.exceptions':
                    mock_exceptions = MagicMock()
                    mock_exceptions.ClientError = Exception
                    mock_exceptions.NoCredentialsError = Exception
                    return mock_exceptions
                return __import__(name, *args, **kwargs)
            
            mock_import.side_effect = side_effect
            
            # Call function without filename
            result = upload_to_s3(audio_data)
        
        # Verify auto-generated filename was used
        expected_filename = 'daily_briefing_20250128_143000.mp3'
        call_args = mock_s3_client.put_object.call_args
        
        assert call_args[1]['Key'] == expected_filename
        assert result == f"https://test-bucket.s3.amazonaws.com/{expected_filename}"
    
    def test_upload_to_s3_empty_audio(self):
        """Test S3 upload with empty audio data."""
        with pytest.raises(Exception, match="Cannot upload empty audio data to S3"):
            upload_to_s3(None)
        
        with pytest.raises(Exception, match="Cannot upload empty audio data to S3"):
            upload_to_s3(b'')
    
    @patch('uploader.get_config')
    def test_upload_to_s3_import_error(self, mock_config):
        """Test S3 upload when boto3 is not available."""
        # Mock configuration
        mock_config_instance = MagicMock()
        mock_config_instance.get.return_value = 'test-bucket'
        mock_config.return_value = mock_config_instance
        
        # Mock import error
        with patch('builtins.__import__', side_effect=ImportError("No module named 'boto3'")):
            with pytest.raises(Exception, match="boto3 library not installed"):
                upload_to_s3(b'test_audio', 'test.mp3')
    
    @patch('uploader.verify_bucket_access')
    @patch('uploader.get_config')
    def test_upload_to_s3_bucket_access_failed(self, mock_config, mock_verify_bucket):
        """Test S3 upload when bucket access fails."""
        # Mock configuration
        mock_config_instance = MagicMock()
        mock_config_instance.get.return_value = 'test-bucket'
        mock_config.return_value = mock_config_instance
        
        # Mock bucket verification failure
        mock_verify_bucket.return_value = False
        
        with pytest.raises(Exception, match="Cannot access S3 bucket: test-bucket"):
            upload_to_s3(b'test_audio', 'test.mp3')
    
    @patch('uploader.verify_bucket_access')
    @patch('uploader.get_config')
    def test_upload_to_s3_api_error_authentication(self, mock_config, mock_verify_bucket):
        """Test S3 upload with authentication error."""
        # Mock configuration
        mock_config_instance = MagicMock()
        mock_config_instance.get.return_value = 'test-bucket'
        mock_config.return_value = mock_config_instance
        
        # Mock S3 client with authentication error
        mock_s3_client = MagicMock()
        mock_s3_client.put_object.side_effect = Exception("InvalidAccessKeyId")
        
        # Mock bucket verification
        mock_verify_bucket.return_value = True
        
        # Mock boto3 import inside the function
        with patch('builtins.__import__') as mock_import:
            def side_effect(name, *args, **kwargs):
                if name == 'boto3':
                    mock_boto3 = MagicMock()
                    mock_boto3.client.return_value = mock_s3_client
                    return mock_boto3
                elif name == 'botocore.exceptions':
                    mock_exceptions = MagicMock()
                    mock_exceptions.ClientError = Exception
                    mock_exceptions.NoCredentialsError = Exception
                    return mock_exceptions
                return __import__(name, *args, **kwargs)
            
            mock_import.side_effect = side_effect
            
            with pytest.raises(Exception, match="Invalid AWS access key"):
                upload_to_s3(b'test_audio', 'test.mp3')
    
    @patch('uploader.verify_bucket_access')
    @patch('uploader.get_config')
    def test_upload_to_s3_api_error_bucket_not_found(self, mock_config, mock_verify_bucket):
        """Test S3 upload with bucket not found error."""
        # Mock configuration
        mock_config_instance = MagicMock()
        mock_config_instance.get.return_value = 'test-bucket'
        mock_config.return_value = mock_config_instance
        
        # Mock S3 client with bucket not found error
        mock_s3_client = MagicMock()
        mock_s3_client.put_object.side_effect = Exception("NoSuchBucket")
        
        # Mock bucket verification
        mock_verify_bucket.return_value = True
        
        # Mock boto3 import inside the function
        with patch('builtins.__import__') as mock_import:
            def side_effect(name, *args, **kwargs):
                if name == 'boto3':
                    mock_boto3 = MagicMock()
                    mock_boto3.client.return_value = mock_s3_client
                    return mock_boto3
                elif name == 'botocore.exceptions':
                    mock_exceptions = MagicMock()
                    mock_exceptions.ClientError = Exception
                    mock_exceptions.NoCredentialsError = Exception
                    return mock_exceptions
                return __import__(name, *args, **kwargs)
            
            mock_import.side_effect = side_effect
            
            with pytest.raises(Exception, match="S3 bucket 'test-bucket' does not exist"):
                upload_to_s3(b'test_audio', 'test.mp3')


class TestVerifyBucketAccess:
    """Test cases for verify_bucket_access function."""
    
    def test_verify_bucket_access_success(self):
        """Test successful bucket access verification."""
        # Mock S3 client
        mock_s3_client = MagicMock()
        mock_s3_client.get_bucket_location.return_value = {'LocationConstraint': 'us-west-2'}
        
        # Mock boto3 import inside the function
        with patch('builtins.__import__') as mock_import:
            def side_effect(name, *args, **kwargs):
                if name == 'boto3':
                    mock_boto3 = MagicMock()
                    mock_boto3.client.return_value = mock_s3_client
                    return mock_boto3
                elif name == 'botocore.exceptions':
                    mock_exceptions = MagicMock()
                    mock_exceptions.ClientError = Exception
                    mock_exceptions.NoCredentialsError = Exception
                    return mock_exceptions
                return __import__(name, *args, **kwargs)
            
            mock_import.side_effect = side_effect
            
            result = verify_bucket_access('test-bucket')
        
        assert result is True
        mock_s3_client.get_bucket_location.assert_called_once_with(Bucket='test-bucket')
    
    def test_verify_bucket_access_no_bucket_name(self):
        """Test bucket access verification with no bucket name."""
        result = verify_bucket_access(None)
        assert result is False
        
        result = verify_bucket_access('')
        assert result is False
    
    def test_verify_bucket_access_bucket_not_found(self):
        """Test bucket access verification with bucket not found."""
        # Mock S3 client with bucket not found error
        mock_s3_client = MagicMock()
        mock_s3_client.get_bucket_location.side_effect = Exception("NoSuchBucket")
        
        # Mock boto3 import inside the function
        with patch('builtins.__import__') as mock_import:
            def side_effect(name, *args, **kwargs):
                if name == 'boto3':
                    mock_boto3 = MagicMock()
                    mock_boto3.client.return_value = mock_s3_client
                    return mock_boto3
                elif name == 'botocore.exceptions':
                    mock_exceptions = MagicMock()
                    mock_exceptions.ClientError = Exception
                    mock_exceptions.NoCredentialsError = Exception
                    return mock_exceptions
                return __import__(name, *args, **kwargs)
            
            mock_import.side_effect = side_effect
            
            with pytest.raises(Exception, match="S3 bucket 'test-bucket' does not exist"):
                verify_bucket_access('test-bucket')
    
    def test_verify_bucket_access_access_denied(self):
        """Test bucket access verification with access denied."""
        # Mock S3 client with access denied error
        mock_s3_client = MagicMock()
        mock_s3_client.get_bucket_location.side_effect = Exception("AccessDenied")
        
        # Mock boto3 import inside the function
        with patch('builtins.__import__') as mock_import:
            def side_effect(name, *args, **kwargs):
                if name == 'boto3':
                    mock_boto3 = MagicMock()
                    mock_boto3.client.return_value = mock_s3_client
                    return mock_boto3
                elif name == 'botocore.exceptions':
                    mock_exceptions = MagicMock()
                    mock_exceptions.ClientError = Exception
                    mock_exceptions.NoCredentialsError = Exception
                    return mock_exceptions
                return __import__(name, *args, **kwargs)
            
            mock_import.side_effect = side_effect
            
            with pytest.raises(Exception, match="No permission to access S3 bucket 'test-bucket'"):
                verify_bucket_access('test-bucket')


class TestSetupS3Credentials:
    """Test cases for setup_s3_credentials function."""
    
    def test_setup_s3_credentials_success(self):
        """Test successful S3 credentials setup."""
        mock_s3_client = MagicMock()
        mock_s3_client.list_buckets.return_value = {'Buckets': []}
        
        # Mock boto3 import inside the function
        with patch('builtins.__import__') as mock_import:
            def side_effect(name, *args, **kwargs):
                if name == 'boto3':
                    mock_boto3 = MagicMock()
                    mock_boto3.client.return_value = mock_s3_client
                    return mock_boto3
                elif name == 'botocore.exceptions':
                    mock_exceptions = MagicMock()
                    mock_exceptions.NoCredentialsError = Exception
                    return mock_exceptions
                return __import__(name, *args, **kwargs)
            
            mock_import.side_effect = side_effect
            
            result = setup_s3_credentials()
        
        assert result == mock_s3_client
        mock_s3_client.list_buckets.assert_called_once()
    
    def test_setup_s3_credentials_import_error(self):
        """Test S3 credentials setup with import error."""
        with patch('builtins.__import__', side_effect=ImportError("No module named 'boto3'")):
            with pytest.raises(Exception, match="Required boto3 library not installed"):
                setup_s3_credentials()
    
    def test_setup_s3_credentials_no_credentials(self):
        """Test S3 credentials setup with no credentials."""
        mock_s3_client = MagicMock()
        mock_s3_client.list_buckets.side_effect = Exception("NoCredentialsError")
        
        # Mock boto3 import inside the function
        with patch('builtins.__import__') as mock_import:
            def side_effect(name, *args, **kwargs):
                if name == 'boto3':
                    mock_boto3 = MagicMock()
                    mock_boto3.client.return_value = mock_s3_client
                    return mock_boto3
                elif name == 'botocore.exceptions':
                    mock_exceptions = MagicMock()
                    mock_exceptions.NoCredentialsError = Exception
                    return mock_exceptions
                return __import__(name, *args, **kwargs)
            
            mock_import.side_effect = side_effect
            
            with pytest.raises(Exception, match="AWS credentials not found"):
                setup_s3_credentials() 