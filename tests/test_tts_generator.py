"""
Unit tests for tts_generator module.

Tests the TTS provider switching and both ElevenLabs and Google TTS integrations.
"""

import pytest
from unittest.mock import MagicMock, patch
from tts_generator import generate_audio, generate_audio_elevenlabs, save_audio_locally


class TestGenerateAudio:
    """Test cases for generate_audio function with provider switching."""
    
    @patch('google_tts_generator.generate_audio_google')
    @patch('tts_generator.get_config')
    def test_generate_audio_google_provider(self, mock_config, mock_google_audio):
        """Test audio generation with Google TTS provider."""
        # Mock configuration for Google TTS
        mock_config_instance = MagicMock()
        mock_config_instance.get.side_effect = lambda key, default=None: {
            'TTS_PROVIDER': 'google'
        }.get(key, default)
        mock_config.return_value = mock_config_instance
        
        # Mock Google TTS response
        mock_google_audio.return_value = b'google_audio_data'
        
        # Test
        result = generate_audio("Test script for Google")
        
        # Verify
        assert result == b'google_audio_data'
        mock_google_audio.assert_called_once_with("Test script for Google", mock_config_instance)
    
    @patch('elevenlabs.client.ElevenLabs')
    @patch('tts_generator.get_config')
    def test_generate_audio_elevenlabs_provider(self, mock_config, mock_elevenlabs_class):
        """Test audio generation with ElevenLabs provider."""
        # Mock configuration for ElevenLabs
        mock_config_instance = MagicMock()
        mock_config_instance.get.side_effect = lambda key, default=None: {
            'TTS_PROVIDER': 'elevenlabs',
            'ELEVENLABS_API_KEY': 'test-elevenlabs-key',
            'ELEVENLABS_VOICE_ID': 'test-voice-id'
        }.get(key, default)
        mock_config_instance.get_voice_speed.return_value = 1.0
        mock_config.return_value = mock_config_instance
        
        # Mock ElevenLabs client and response
        mock_client = MagicMock()
        mock_elevenlabs_class.return_value = mock_client
        mock_client.text_to_speech.convert.return_value = b'elevenlabs_audio_data'
        
        # Test
        result = generate_audio("Test script for ElevenLabs")
        
        # Verify
        assert result == b'elevenlabs_audio_data'
        mock_elevenlabs_class.assert_called_once_with(api_key='test-elevenlabs-key')
    
    @patch('tts_generator.get_config')
    def test_generate_audio_unknown_provider(self, mock_config):
        """Test error handling for unknown TTS provider."""
        # Mock configuration with unknown provider
        mock_config_instance = MagicMock()
        mock_config_instance.get.side_effect = lambda key, default=None: {
            'TTS_PROVIDER': 'unknown_provider'
        }.get(key, default)
        mock_config.return_value = mock_config_instance
        
        # Test
        with pytest.raises(Exception) as exc_info:
            generate_audio("Test script")
        
        assert "Unknown TTS provider: unknown_provider" in str(exc_info.value)
    
    @patch('google_tts_generator.generate_audio_google')
    def test_generate_audio_with_custom_config(self, mock_google_audio):
        """Test audio generation with custom config object."""
        # Create custom config
        custom_config = MagicMock()
        custom_config.get.side_effect = lambda key, default=None: {
            'TTS_PROVIDER': 'google'
        }.get(key, default)
        
        # Mock Google TTS response
        mock_google_audio.return_value = b'custom_config_audio'
        
        # Test
        result = generate_audio("Test with custom config", config=custom_config)
        
        # Verify
        assert result == b'custom_config_audio'
        mock_google_audio.assert_called_once_with("Test with custom config", custom_config)


class TestGenerateAudioElevenLabs:
    """Test cases for generate_audio_elevenlabs function."""
    
    @patch('elevenlabs.client.ElevenLabs')
    @patch('tts_generator.get_config')
    def test_generate_audio_success(self, mock_config, mock_elevenlabs_class):
        """Test successful audio generation."""
        # Mock configuration
        mock_config_instance = MagicMock()
        mock_config_instance.get.side_effect = lambda key, default=None: {
            'ELEVENLABS_API_KEY': 'test-elevenlabs-key',
            'ELEVENLABS_VOICE_ID': 'test-voice-id'
        }.get(key, default)
        mock_config_instance.get_voice_speed.return_value = 1.0
        mock_config.return_value = mock_config_instance
        
        # Mock ElevenLabs client and response
        mock_client = MagicMock()
        mock_elevenlabs_class.return_value = mock_client
        
        # Mock audio response
        test_audio_data = b'fake_audio_data_mp3_content'
        mock_client.text_to_speech.convert.return_value = test_audio_data
        
        # Test script
        script_text = "Good morning! This is your daily briefing for today."
        
        # Call function
        result = generate_audio_elevenlabs(script_text)
        
        # Verify results
        assert result == test_audio_data
        assert len(result) > 0
        
        # Verify API calls
        mock_elevenlabs_class.assert_called_once_with(api_key='test-elevenlabs-key')
        mock_client.text_to_speech.convert.assert_called_once_with(
            text=script_text,
            voice_id='test-voice-id',
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
            voice_settings={
                "stability": 0.75,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            }
        )
        
    @patch('elevenlabs.client.ElevenLabs')
    @patch('tts_generator.get_config')
    def test_generate_audio_default_voice(self, mock_config, mock_elevenlabs_class):
        """Test audio generation with default voice when voice_id is 'default'."""
        # Mock configuration
        mock_config_instance = MagicMock()
        mock_config_instance.get.side_effect = lambda key, default=None: {
            'ELEVENLABS_API_KEY': 'test-elevenlabs-key',
            'ELEVENLABS_VOICE_ID': 'default'  # Should use Rachel voice
        }.get(key, default)
        mock_config_instance.get_voice_speed.return_value = 1.0
        mock_config.return_value = mock_config_instance
        
        # Mock ElevenLabs client and response
        mock_client = MagicMock()
        mock_elevenlabs_class.return_value = mock_client
        mock_client.text_to_speech.convert.return_value = b'audio_data'
        
        # Call function
        result = generate_audio_elevenlabs("Test script")
        
        # Verify Rachel voice is used when 'default' is specified
        mock_client.text_to_speech.convert.assert_called_once_with(
            text="Test script",
            voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel voice
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
            voice_settings={
                "stability": 0.75,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            }
        )
        
    @patch('elevenlabs.client.ElevenLabs')
    @patch('tts_generator.get_config')
    def test_generate_audio_streaming_response(self, mock_config, mock_elevenlabs_class):
        """Test audio generation with streaming response (generator)."""
        # Mock configuration
        mock_config_instance = MagicMock()
        mock_config_instance.get.side_effect = lambda key, default=None: {
            'ELEVENLABS_API_KEY': 'test-elevenlabs-key',
            'ELEVENLABS_VOICE_ID': 'test-voice-id'
        }.get(key, default)
        mock_config_instance.get_voice_speed.return_value = 1.0
        mock_config.return_value = mock_config_instance
        
        # Mock ElevenLabs client
        mock_client = MagicMock()
        mock_elevenlabs_class.return_value = mock_client
        
        # Mock streaming response (generator-like object)
        audio_chunks = [b'chunk1', b'chunk2', b'chunk3']
        mock_client.text_to_speech.convert.return_value = iter(audio_chunks)
        
        # Call function
        result = generate_audio_elevenlabs("Test streaming script")
        
        # Verify chunks are joined correctly
        expected_audio = b'chunk1chunk2chunk3'
        assert result == expected_audio
        
    def test_generate_audio_empty_script(self):
        """Test audio generation with empty script."""
        # Test with None
        with pytest.raises(Exception) as exc_info:
            generate_audio_elevenlabs(None)
        assert "Cannot generate audio from empty script text" in str(exc_info.value)
        
        # Test with empty string
        with pytest.raises(Exception) as exc_info:
            generate_audio_elevenlabs("")
        assert "Cannot generate audio from empty script text" in str(exc_info.value)
        
        # Test with whitespace only
        with pytest.raises(Exception) as exc_info:
            generate_audio_elevenlabs("   \n\t  ")
        assert "Cannot generate audio from empty script text" in str(exc_info.value)
        
    @patch('tts_generator.get_config')
    def test_generate_audio_import_error(self, mock_config):
        """Test handling of missing ElevenLabs library."""
        # Mock configuration
        mock_config_instance = MagicMock()
        mock_config_instance.get.return_value = 'test-key'
        mock_config.return_value = mock_config_instance
        
        # Mock import error by patching the import inside the function
        with patch('builtins.__import__', side_effect=ImportError("No module named 'elevenlabs'")):
            with pytest.raises(Exception) as exc_info:
                generate_audio_elevenlabs("Test script")
            
            assert "ElevenLabs library not installed" in str(exc_info.value)
            
    @patch('elevenlabs.client.ElevenLabs')
    @patch('tts_generator.get_config')
    def test_generate_audio_api_authentication_error(self, mock_config, mock_elevenlabs_class):
        """Test handling of API authentication errors."""
        # Mock configuration
        mock_config_instance = MagicMock()
        mock_config_instance.get.side_effect = lambda key, default=None: {
            'ELEVENLABS_API_KEY': 'invalid-key',
            'ELEVENLABS_VOICE_ID': 'test-voice'
        }.get(key, default)
        mock_config_instance.get_voice_speed.return_value = 1.0
        mock_config.return_value = mock_config_instance
        
        # Mock ElevenLabs client that raises authentication error
        mock_client = MagicMock()
        mock_elevenlabs_class.return_value = mock_client
        mock_client.text_to_speech.convert.side_effect = Exception("Unauthorized: Invalid API key")
        
        # Call function and verify error handling
        with pytest.raises(Exception) as exc_info:
            generate_audio_elevenlabs("Test script")
            
        assert "ElevenLabs API authentication failed" in str(exc_info.value)
        
    @patch('elevenlabs.client.ElevenLabs')
    @patch('tts_generator.get_config')
    def test_generate_audio_voice_not_found_error(self, mock_config, mock_elevenlabs_class):
        """Test handling of voice not found errors."""
        # Mock configuration
        mock_config_instance = MagicMock()
        mock_config_instance.get.side_effect = lambda key, default=None: {
            'ELEVENLABS_API_KEY': 'test-key',
            'ELEVENLABS_VOICE_ID': 'invalid-voice-id'
        }.get(key, default)
        mock_config_instance.get_voice_speed.return_value = 1.0
        mock_config.return_value = mock_config_instance
        
        # Mock ElevenLabs client that raises voice error
        mock_client = MagicMock()
        mock_elevenlabs_class.return_value = mock_client
        mock_client.text_to_speech.convert.side_effect = Exception("Voice ID not found")
        
        # Call function and verify error handling
        with pytest.raises(Exception) as exc_info:
            generate_audio_elevenlabs("Test script")
            
        assert "Voice ID 'invalid-voice-id' not found" in str(exc_info.value)
        
    @patch('elevenlabs.client.ElevenLabs')
    @patch('tts_generator.get_config')
    def test_generate_audio_quota_exceeded_error(self, mock_config, mock_elevenlabs_class):
        """Test handling of quota exceeded errors."""
        # Mock configuration  
        mock_config_instance = MagicMock()
        mock_config_instance.get.side_effect = lambda key, default=None: {
            'ELEVENLABS_API_KEY': 'test-key',
            'ELEVENLABS_VOICE_ID': 'test-voice'
        }.get(key, default)
        mock_config_instance.get_voice_speed.return_value = 1.0
        mock_config.return_value = mock_config_instance
        
        # Mock ElevenLabs client that raises quota error
        mock_client = MagicMock()
        mock_elevenlabs_class.return_value = mock_client
        mock_client.text_to_speech.convert.side_effect = Exception("API quota exceeded")
        
        # Call function and verify error handling
        with pytest.raises(Exception) as exc_info:
            generate_audio_elevenlabs("Test script")
            
        assert "ElevenLabs API quota exceeded" in str(exc_info.value)
        
    @patch('elevenlabs.client.ElevenLabs')
    @patch('tts_generator.get_config')
    def test_generate_audio_network_error(self, mock_config, mock_elevenlabs_class):
        """Test handling of network connection errors."""
        # Mock configuration
        mock_config_instance = MagicMock()
        mock_config_instance.get.side_effect = lambda key, default=None: {
            'ELEVENLABS_API_KEY': 'test-key',
            'ELEVENLABS_VOICE_ID': 'test-voice'
        }.get(key, default)
        mock_config_instance.get_voice_speed.return_value = 1.0
        mock_config.return_value = mock_config_instance
        
        # Mock ElevenLabs client that raises network error
        mock_client = MagicMock()
        mock_elevenlabs_class.return_value = mock_client
        mock_client.text_to_speech.convert.side_effect = Exception("Network connection failed")
        
        # Call function and verify error handling
        with pytest.raises(Exception) as exc_info:
            generate_audio_elevenlabs("Test script")
            
        assert "Network error connecting to ElevenLabs API" in str(exc_info.value)


class TestSaveAudioLocally:
    """Test cases for save_audio_locally function."""
    
    @patch('builtins.open', create=True)
    def test_save_audio_locally_success(self, mock_open):
        """Test successful local audio file saving."""
        # Mock file operations
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Test data
        audio_data = b'test_audio_content'
        filename = 'test_briefing.mp3'
        
        # Call function
        result = save_audio_locally(audio_data, filename)
        
        # Verify results
        assert result == filename
        
        # Verify file operations
        mock_open.assert_called_once_with(filename, 'wb')
        mock_file.write.assert_called_once_with(audio_data)
        
    @patch('builtins.open', create=True)
    def test_save_audio_locally_default_filename(self, mock_open):
        """Test saving with default filename."""
        # Mock file operations
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Test data
        audio_data = b'test_audio_content'
        
        # Call function without filename
        result = save_audio_locally(audio_data)
        
        # Verify default filename is used
        assert result == "briefing.mp3"
        mock_open.assert_called_once_with("briefing.mp3", 'wb')
        mock_file.write.assert_called_once_with(audio_data)
        
    @patch('builtins.open', create=True)
    def test_save_audio_locally_file_error(self, mock_open):
        """Test handling of file write errors."""
        # Mock file operations that raise an error
        mock_open.side_effect = IOError("Permission denied")
        
        # Test data
        audio_data = b'test_audio_content'
        
        # Call function and verify error is propagated
        with pytest.raises(IOError):
            save_audio_locally(audio_data, 'test.mp3') 