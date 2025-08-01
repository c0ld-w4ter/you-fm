"""
Integration tests for TTS provider switching and end-to-end functionality.

Tests the complete TTS pipeline with both Google Cloud Text-to-Speech and ElevenLabs,
including provider switching, configuration validation, and error handling.
"""

import pytest
from unittest.mock import MagicMock, patch, Mock
from config import Config
from tts_generator import generate_audio
from google_tts_generator import generate_audio_google
import os


class TestTTSProviderSwitching:
    """Test cases for TTS provider switching functionality."""
    
    @patch('google_tts_generator.GoogleTTSClient')
    @patch('tts_generator.get_config')
    def test_google_provider_integration(self, mock_get_config, mock_google_client):
        """Test complete integration with Google TTS provider."""
        # Mock configuration for Google TTS
        mock_config = MagicMock()
        mock_config.get.side_effect = lambda key, default=None: {
            'TTS_PROVIDER': 'google',
            'GOOGLE_TTS_VOICE_NAME': 'en-US-Journey-D',
            'GOOGLE_TTS_LANGUAGE_CODE': 'en-US',
            'GOOGLE_CLOUD_CREDENTIALS_PATH': ''
        }.get(key, default)
        mock_config.get_voice_speed.return_value = 1.0
        mock_get_config.return_value = mock_config
        
        # Mock Google TTS client
        mock_client_instance = MagicMock()
        mock_client_instance.synthesize_speech.return_value = b'google_audio_data'
        mock_google_client.return_value = mock_client_instance
        
        # Test audio generation
        script_text = "This is a test script for Google TTS integration."
        result = generate_audio(script_text)
        
        # Verify Google TTS was used
        assert result == b'google_audio_data'
        mock_google_client.assert_called_once_with(api_key=None, credentials_path=None)
        mock_client_instance.synthesize_speech.assert_called_once_with(
            text=script_text,
            voice_name='en-US-Journey-D',
            language_code='en-US',
            speaking_rate=1.0
        )
    
    @patch('tts_generator.generate_audio_elevenlabs')
    @patch('tts_generator.get_config')
    def test_elevenlabs_provider_integration(self, mock_get_config, mock_elevenlabs):
        """Test complete integration with ElevenLabs provider."""
        # Mock configuration for ElevenLabs
        mock_config = MagicMock()
        mock_config.get.side_effect = lambda key, default=None: {
            'TTS_PROVIDER': 'elevenlabs',
            'ELEVENLABS_API_KEY': 'test-elevenlabs-key',
            'ELEVENLABS_VOICE_ID': 'test-voice-id'
        }.get(key, default)
        mock_config.get_voice_speed.return_value = 1.2
        mock_get_config.return_value = mock_config
        
        # Mock ElevenLabs audio generation
        mock_elevenlabs.return_value = b'elevenlabs_audio_data'
        
        # Test audio generation
        script_text = "This is a test script for ElevenLabs integration."
        result = generate_audio(script_text)
        
        # Verify ElevenLabs was used
        assert result == b'elevenlabs_audio_data'
        mock_elevenlabs.assert_called_once_with(script_text, mock_config)
    
    @patch('tts_generator.get_config')
    def test_provider_switching_configuration(self, mock_get_config):
        """Test that provider switching works based on configuration."""
        # Test configurations for both providers
        test_configs = [
            ('google', 'Google TTS should be selected'),
            ('elevenlabs', 'ElevenLabs should be selected'),
            ('GOOGLE', 'Case insensitive Google selection'),
            ('ElevenLabs', 'Case insensitive ElevenLabs selection')
        ]
        
        for provider, description in test_configs:
            mock_config = MagicMock()
            mock_config.get.return_value = provider
            mock_get_config.return_value = mock_config
            
            with patch('google_tts_generator.generate_audio_google') as mock_google:
                with patch('tts_generator.generate_audio_elevenlabs') as mock_elevenlabs:
                    mock_google.return_value = b'google_data'
                    mock_elevenlabs.return_value = b'elevenlabs_data'
                    
                    try:
                        result = generate_audio("Test script")
                        
                        if provider.lower() == 'google':
                            mock_google.assert_called_once()
                            mock_elevenlabs.assert_not_called()
                            assert result == b'google_data', f"Failed: {description}"
                        elif provider.lower() == 'elevenlabs':
                            mock_elevenlabs.assert_called_once()
                            mock_google.assert_not_called()
                            assert result == b'elevenlabs_data', f"Failed: {description}"
                    except Exception as e:
                        pytest.fail(f"Provider switching failed for {provider}: {e}")


class TestTTSConfigurationValidation:
    """Test cases for TTS configuration validation."""
    
    def test_google_tts_config_validation(self):
        """Test Google TTS configuration validation."""
        # Test valid Google TTS configuration
        config_data = {
            'NEWSAPI_AI_KEY': 'test-news-key',
            'OPENWEATHER_API_KEY': 'test-weather-key', 
            'GEMINI_API_KEY': 'test-gemini-key',
            'TTS_PROVIDER': 'google',
            'GOOGLE_TTS_VOICE_NAME': 'en-US-Journey-D',
            'GOOGLE_TTS_LANGUAGE_CODE': 'en-US'
        }
        
        config = Config(config_data)
        # Should not raise any exceptions
        config._validate_tts_config()
    
    def test_elevenlabs_config_validation_with_api_key(self):
        """Test ElevenLabs configuration validation with API key."""
        config_data = {
            'NEWSAPI_AI_KEY': 'test-news-key',
            'OPENWEATHER_API_KEY': 'test-weather-key',
            'GEMINI_API_KEY': 'test-gemini-key',
            'TTS_PROVIDER': 'elevenlabs',
            'ELEVENLABS_API_KEY': 'test-api-key'
        }
        
        config = Config(config_data)
        # Should not raise any exceptions
        config._validate_tts_config()
    
    def test_elevenlabs_config_validation_missing_api_key(self):
        """Test ElevenLabs configuration validation without API key."""
        config_data = {
            'NEWSAPI_AI_KEY': 'test-news-key',
            'OPENWEATHER_API_KEY': 'test-weather-key',
            'GEMINI_API_KEY': 'test-gemini-key',
            'TTS_PROVIDER': 'elevenlabs'
            # Missing ELEVENLABS_API_KEY
        }
        
        with pytest.raises(Exception) as exc_info:
            config = Config(config_data)
            config._validate_tts_config()
        
        assert "ELEVENLABS_API_KEY is required" in str(exc_info.value)
    
    def test_invalid_tts_provider(self):
        """Test validation with invalid TTS provider."""
        config_data = {
            'NEWSAPI_AI_KEY': 'test-news-key',
            'OPENWEATHER_API_KEY': 'test-weather-key',
            'GEMINI_API_KEY': 'test-gemini-key',
            'TTS_PROVIDER': 'invalid_provider'
        }
        
        with pytest.raises(Exception) as exc_info:
            config = Config(config_data)
            config._validate_tts_config()
        
        assert "must be either 'google' or 'elevenlabs'" in str(exc_info.value)


class TestTTSErrorHandling:
    """Test cases for TTS error handling across providers."""
    
    @patch('google_tts_generator.GoogleTTSClient')
    @patch('tts_generator.get_config')
    def test_google_tts_authentication_error_handling(self, mock_get_config, mock_google_client):
        """Test Google TTS authentication error handling."""
        mock_config = MagicMock()
        mock_config.get.side_effect = lambda key, default=None: {
            'TTS_PROVIDER': 'google',
            'GOOGLE_TTS_VOICE_NAME': 'en-US-Journey-D',
            'GOOGLE_TTS_LANGUAGE_CODE': 'en-US'
        }.get(key, default)
        mock_config.get_voice_speed.return_value = 1.0
        mock_get_config.return_value = mock_config
        
        # Mock authentication error
        mock_client_instance = MagicMock()
        mock_client_instance.synthesize_speech.side_effect = Exception("authentication failed")
        mock_google_client.return_value = mock_client_instance
        
        with pytest.raises(Exception) as exc_info:
            generate_audio("Test script")
        
        assert "Google Cloud authentication failed" in str(exc_info.value)
    
    @patch('tts_generator.generate_audio_elevenlabs')
    @patch('tts_generator.get_config')
    def test_elevenlabs_api_error_handling(self, mock_get_config, mock_elevenlabs):
        """Test ElevenLabs API error handling."""
        mock_config = MagicMock()
        mock_config.get.side_effect = lambda key, default=None: {
            'TTS_PROVIDER': 'elevenlabs',
            'ELEVENLABS_API_KEY': 'invalid-key',
            'ELEVENLABS_VOICE_ID': 'test-voice-id'
        }.get(key, default)
        mock_config.get_voice_speed.return_value = 1.0
        mock_get_config.return_value = mock_config
        
        # Mock API authentication error
        mock_elevenlabs.side_effect = Exception("Invalid API key")
        
        with pytest.raises(Exception) as exc_info:
            generate_audio("Test script")
        
        assert "Invalid API key" in str(exc_info.value)


class TestTTSPerformanceAndCompatibility:
    """Test cases for TTS performance and compatibility features."""
    
    @patch('google_tts_generator.GoogleTTSClient')
    @patch('tts_generator.get_config')
    def test_google_tts_voice_speed_configuration(self, mock_get_config, mock_google_client):
        """Test Google TTS voice speed configuration."""
        test_speeds = [0.8, 1.0, 1.2]
        
        for speed in test_speeds:
            mock_config = MagicMock()
            mock_config.get.side_effect = lambda key, default=None: {
                'TTS_PROVIDER': 'google',
                'GOOGLE_TTS_VOICE_NAME': 'en-US-Journey-D',
                'GOOGLE_TTS_LANGUAGE_CODE': 'en-US'
            }.get(key, default)
            mock_config.get_voice_speed.return_value = speed
            mock_get_config.return_value = mock_config
            
            mock_client_instance = MagicMock()
            mock_client_instance.synthesize_speech.return_value = b'audio_data'
            mock_google_client.return_value = mock_client_instance
            
            generate_audio("Test script")
            
            # Verify speed was passed correctly
            mock_client_instance.synthesize_speech.assert_called_with(
                text="Test script",
                voice_name='en-US-Journey-D',
                language_code='en-US',
                speaking_rate=speed
            )
    
    @patch('tts_generator.get_config')
    def test_tts_empty_script_handling(self, mock_get_config):
        """Test handling of empty script across providers."""
        mock_config = MagicMock()
        mock_config.get.return_value = 'google'
        mock_get_config.return_value = mock_config
        
        # Test empty string
        with pytest.raises(Exception) as exc_info:
            generate_audio("")
        assert "Cannot generate audio from empty script" in str(exc_info.value)
        
        # Test whitespace-only string
        with pytest.raises(Exception) as exc_info:
            generate_audio("   ")
        assert "Cannot generate audio from empty script" in str(exc_info.value)
    
    @patch('google_tts_generator.GoogleTTSClient')
    @patch('tts_generator.get_config')
    def test_google_tts_large_script_handling(self, mock_get_config, mock_google_client):
        """Test Google TTS handling of large scripts."""
        mock_config = MagicMock()
        mock_config.get.side_effect = lambda key, default=None: {
            'TTS_PROVIDER': 'google',
            'GOOGLE_TTS_VOICE_NAME': 'en-US-Journey-D',
            'GOOGLE_TTS_LANGUAGE_CODE': 'en-US'
        }.get(key, default)
        mock_config.get_voice_speed.return_value = 1.0
        mock_get_config.return_value = mock_config
        
        mock_client_instance = MagicMock()
        mock_client_instance.synthesize_speech.return_value = b'large_audio_data'
        mock_google_client.return_value = mock_client_instance
        
        # Test with large script (5000+ characters)
        large_script = "This is a test script. " * 250  # ~5750 characters
        result = generate_audio(large_script)
        
        assert result == b'large_audio_data'
        mock_client_instance.synthesize_speech.assert_called_once_with(
            text=large_script,
            voice_name='en-US-Journey-D',
            language_code='en-US',
            speaking_rate=1.0
        )


class TestTTSMigrationCompatibility:
    """Test cases for ensuring compatibility during the ElevenLabs to Google TTS migration."""
    
    def test_default_provider_is_google(self):
        """Test that Google is the default TTS provider after migration."""
        config_data = {
            'NEWSAPI_AI_KEY': 'test-news-key',
            'OPENWEATHER_API_KEY': 'test-weather-key',
            'GEMINI_API_KEY': 'test-gemini-key'
        }
        config = Config(config_data)
        assert config.get('TTS_PROVIDER', 'google').lower() == 'google'
    
    @patch('tts_generator.get_config')
    def test_backward_compatibility_with_elevenlabs(self, mock_get_config):
        """Test that ElevenLabs still works for existing configurations."""
        mock_config = MagicMock()
        mock_config.get.return_value = 'elevenlabs'
        mock_get_config.return_value = mock_config
        
        with patch('tts_generator.generate_audio_elevenlabs') as mock_elevenlabs:
            mock_elevenlabs.return_value = b'elevenlabs_audio'
            
            result = generate_audio("Test backward compatibility")
            
            assert result == b'elevenlabs_audio'
            mock_elevenlabs.assert_called_once_with("Test backward compatibility", mock_config)
    
    @patch('google_tts_generator.generate_audio_google')
    @patch('tts_generator.get_config')
    def test_migration_fallback_behavior(self, mock_get_config, mock_google):
        """Test fallback behavior during migration."""
        mock_config = MagicMock()
        # Return the default value when TTS_PROVIDER is not set
        mock_config.get.side_effect = lambda key, default=None: default if key == 'TTS_PROVIDER' else None
        mock_get_config.return_value = mock_config
        
        mock_google.return_value = b'google_fallback_audio'
        
        result = generate_audio("Test migration fallback")
        
        # Should default to Google TTS
        assert result == b'google_fallback_audio'
        mock_google.assert_called_once_with("Test migration fallback", mock_config)