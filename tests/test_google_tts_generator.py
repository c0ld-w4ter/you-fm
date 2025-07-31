"""
Unit tests for google_tts_generator module.

Tests the Google Cloud Text-to-Speech API integration.
"""

import pytest
from unittest.mock import MagicMock, patch, Mock
from google_tts_generator import generate_audio_google, GoogleTTSClient, get_available_voices


class TestGoogleTTSClient:
    """Test cases for GoogleTTSClient class."""
    
    @patch('google_tts_generator.service_account.Credentials')
    @patch('google_tts_generator.texttospeech.TextToSpeechClient')
    @patch('os.path.exists')
    def test_client_init_with_credentials_file(self, mock_exists, mock_tts_client, mock_credentials):
        """Test client initialization with credentials file."""
        mock_exists.return_value = True
        mock_creds_instance = MagicMock()
        mock_credentials.from_service_account_file.return_value = mock_creds_instance
        
        client = GoogleTTSClient('/path/to/credentials.json')
        
        mock_exists.assert_called_once_with('/path/to/credentials.json')
        mock_credentials.from_service_account_file.assert_called_once_with('/path/to/credentials.json')
        mock_tts_client.assert_called_once_with(credentials=mock_creds_instance)
    
    @patch('google_tts_generator.texttospeech.TextToSpeechClient')
    def test_client_init_default_credentials(self, mock_tts_client):
        """Test client initialization with default credentials."""
        client = GoogleTTSClient()
        
        mock_tts_client.assert_called_once_with()
    
    @patch('google_tts_generator.texttospeech')
    def test_synthesize_speech(self, mock_texttospeech):
        """Test speech synthesis with various parameters."""
        # Mock the client and response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.audio_content = b'fake_audio_data'
        mock_client.synthesize_speech.return_value = mock_response
        
        # Create client instance
        with patch('google_tts_generator.texttospeech.TextToSpeechClient', return_value=mock_client):
            client = GoogleTTSClient()
            
            # Test synthesis
            result = client.synthesize_speech(
                text="Hello, world!",
                voice_name="en-US-Journey-D",
                language_code="en-US",
                speaking_rate=1.2,
                pitch=2.0,
                volume_gain_db=3.0
            )
            
            # Verify result
            assert result == b'fake_audio_data'
            
            # Verify API call
            mock_client.synthesize_speech.assert_called_once()
            call_args = mock_client.synthesize_speech.call_args[1]
            
            # Check synthesis input
            assert call_args['input'].text == "Hello, world!"
            
            # Check voice selection
            assert call_args['voice'].language_code == "en-US"
            assert call_args['voice'].name == "en-US-Journey-D"
            
            # Check audio config
            assert call_args['audio_config'].audio_encoding == mock_texttospeech.AudioEncoding.MP3
            assert call_args['audio_config'].speaking_rate == 1.2
            assert call_args['audio_config'].pitch == 2.0
            assert call_args['audio_config'].volume_gain_db == 3.0


class TestGenerateAudioGoogle:
    """Test cases for generate_audio_google function."""
    
    @patch('google_tts_generator.GoogleTTSClient')
    @patch('google_tts_generator.get_config')
    def test_generate_audio_success(self, mock_get_config, mock_client_class):
        """Test successful audio generation with Google TTS."""
        # Mock configuration
        mock_config = MagicMock()
        mock_config.get.side_effect = lambda key, default=None: {
            'GOOGLE_CLOUD_CREDENTIALS_PATH': '/path/to/creds.json',
            'GOOGLE_TTS_VOICE_NAME': 'en-US-Journey-F',
            'GOOGLE_TTS_LANGUAGE_CODE': 'en-US'
        }.get(key, default)
        mock_config.get_voice_speed.return_value = 1.0
        mock_get_config.return_value = mock_config
        
        # Mock client
        mock_client_instance = MagicMock()
        mock_client_instance.synthesize_speech.return_value = b'fake_google_audio'
        mock_client_class.return_value = mock_client_instance
        
        # Test
        result = generate_audio_google("Test script for Google TTS")
        
        # Verify
        assert result == b'fake_google_audio'
        mock_client_class.assert_called_once_with('/path/to/creds.json')
        mock_client_instance.synthesize_speech.assert_called_once_with(
            text="Test script for Google TTS",
            voice_name='en-US-Journey-F',
            language_code='en-US',
            speaking_rate=1.0
        )
    
    @patch('google_tts_generator.GoogleTTSClient')
    @patch('google_tts_generator.get_config')
    def test_generate_audio_with_custom_speed(self, mock_get_config, mock_client_class):
        """Test audio generation with custom voice speed."""
        # Mock configuration
        mock_config = MagicMock()
        mock_config.get.side_effect = lambda key, default=None: {
            'GOOGLE_CLOUD_CREDENTIALS_PATH': '',
            'GOOGLE_TTS_VOICE_NAME': 'en-US-Journey-D',
            'GOOGLE_TTS_LANGUAGE_CODE': 'en-US'
        }.get(key, default)
        mock_config.get_voice_speed.return_value = 1.2  # Fast speed
        mock_get_config.return_value = mock_config
        
        # Mock client
        mock_client_instance = MagicMock()
        mock_client_instance.synthesize_speech.return_value = b'fake_audio_fast'
        mock_client_class.return_value = mock_client_instance
        
        # Test
        result = generate_audio_google("Fast speech test")
        
        # Verify speed parameter
        mock_client_instance.synthesize_speech.assert_called_once()
        call_args = mock_client_instance.synthesize_speech.call_args[1]
        assert call_args['speaking_rate'] == 1.2
    
    def test_generate_audio_empty_script(self):
        """Test audio generation with empty script."""
        # Test with None
        with pytest.raises(Exception) as exc_info:
            generate_audio_google(None)
        assert "Cannot generate audio from empty script text" in str(exc_info.value)
        
        # Test with empty string
        with pytest.raises(Exception) as exc_info:
            generate_audio_google("")
        assert "Cannot generate audio from empty script text" in str(exc_info.value)
        
        # Test with whitespace only
        with pytest.raises(Exception) as exc_info:
            generate_audio_google("   \n\t  ")
        assert "Cannot generate audio from empty script text" in str(exc_info.value)
    
    @patch('google_tts_generator.get_config')
    def test_generate_audio_import_error(self, mock_get_config):
        """Test handling of missing Google Cloud library."""
        mock_config = MagicMock()
        mock_get_config.return_value = mock_config
        
        with patch('google_tts_generator.texttospeech', side_effect=ImportError("No module")):
            with pytest.raises(Exception) as exc_info:
                generate_audio_google("Test script")
            
            assert "Google Cloud Text-to-Speech library not installed" in str(exc_info.value)
    
    @patch('google_tts_generator.GoogleTTSClient')
    @patch('google_tts_generator.get_config')
    def test_generate_audio_authentication_error(self, mock_get_config, mock_client_class):
        """Test handling of authentication errors."""
        # Mock configuration
        mock_config = MagicMock()
        mock_config.get.return_value = ''
        mock_config.get_voice_speed.return_value = 1.0
        mock_get_config.return_value = mock_config
        
        # Mock client that raises auth error
        mock_client_class.side_effect = Exception("Could not authenticate credentials")
        
        with pytest.raises(Exception) as exc_info:
            generate_audio_google("Test script")
        
        assert "Google Cloud authentication failed" in str(exc_info.value)
    
    @patch('google_tts_generator.GoogleTTSClient')
    @patch('google_tts_generator.get_config')
    def test_generate_audio_quota_error(self, mock_get_config, mock_client_class):
        """Test handling of quota exceeded errors."""
        # Mock configuration
        mock_config = MagicMock()
        mock_config.get.return_value = ''
        mock_config.get_voice_speed.return_value = 1.0
        mock_get_config.return_value = mock_config
        
        # Mock client
        mock_client_instance = MagicMock()
        mock_client_instance.synthesize_speech.side_effect = Exception("Quota exceeded")
        mock_client_class.return_value = mock_client_instance
        
        with pytest.raises(Exception) as exc_info:
            generate_audio_google("Test script")
        
        assert "Google Cloud quota exceeded" in str(exc_info.value)
    
    @patch('google_tts_generator.GoogleTTSClient')
    @patch('google_tts_generator.get_config')
    def test_generate_audio_with_config_object(self, mock_get_config, mock_client_class):
        """Test audio generation with provided config object."""
        # Create custom config
        custom_config = MagicMock()
        custom_config.get.side_effect = lambda key, default=None: {
            'GOOGLE_CLOUD_CREDENTIALS_PATH': '/custom/path.json',
            'GOOGLE_TTS_VOICE_NAME': 'en-GB-News-G',
            'GOOGLE_TTS_LANGUAGE_CODE': 'en-GB'
        }.get(key, default)
        custom_config.get_voice_speed.return_value = 0.8
        
        # Mock client
        mock_client_instance = MagicMock()
        mock_client_instance.synthesize_speech.return_value = b'custom_audio'
        mock_client_class.return_value = mock_client_instance
        
        # Test - should use provided config, not call get_config
        result = generate_audio_google("Test with custom config", config=custom_config)
        
        # Verify
        assert result == b'custom_audio'
        mock_get_config.assert_not_called()
        mock_client_instance.synthesize_speech.assert_called_once_with(
            text="Test with custom config",
            voice_name='en-GB-News-G',
            language_code='en-GB',
            speaking_rate=0.8
        )


class TestGetAvailableVoices:
    """Test cases for get_available_voices function."""
    
    @patch('google_tts_generator.GoogleTTSClient')
    def test_get_available_voices_success(self, mock_client_class):
        """Test successful retrieval of available voices."""
        # Mock voice objects
        mock_voice1 = MagicMock()
        mock_voice1.name = "en-US-Journey-D"
        mock_voice1.language_codes = ["en-US"]
        mock_voice1.ssml_gender.name = "MALE"
        
        mock_voice2 = MagicMock()
        mock_voice2.name = "en-US-Journey-F"
        mock_voice2.language_codes = ["en-US"]
        mock_voice2.ssml_gender.name = "FEMALE"
        
        # Mock response
        mock_response = MagicMock()
        mock_response.voices = [mock_voice1, mock_voice2]
        
        # Mock client
        mock_client_instance = MagicMock()
        mock_client_instance.client.list_voices.return_value = mock_response
        mock_client_class.return_value = mock_client_instance
        
        # Test
        voices = get_available_voices("en-US")
        
        # Verify
        assert len(voices) == 2
        assert voices[0] == {
            "name": "en-US-Journey-D",
            "language": "en-US",
            "gender": "MALE"
        }
        assert voices[1] == {
            "name": "en-US-Journey-F",
            "language": "en-US",
            "gender": "FEMALE"
        }
    
    @patch('google_tts_generator.GoogleTTSClient')
    def test_get_available_voices_error(self, mock_client_class):
        """Test error handling in voice listing."""
        # Mock client that raises error
        mock_client_class.side_effect = Exception("API error")
        
        # Test - should return empty list on error
        voices = get_available_voices("en-US")
        
        assert voices == []