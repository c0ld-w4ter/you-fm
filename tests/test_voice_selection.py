"""
Tests for voice selection functionality in the AI Daily Briefing Agent.

Tests the flow from form submission to TTS generation, voice preview,
and proper voice ID handling.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from flask import session

from config import Config
from config_web import WebConfig
from web.forms import SettingsForm, BriefingConfigForm
from tts_generator import generate_audio


# Flask app fixture for testing
@pytest.fixture
def app():
    """Create a Flask app for testing."""
    import os
    from flask import Flask
    from web.routes import web_bp
    
    # Get the project root directory (parent of tests directory)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Create Flask app with proper template and static directories
    app = Flask(__name__, 
                template_folder=os.path.join(project_root, 'templates'),
                static_folder=os.path.join(project_root, 'static'))
    
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    
    # Register the web blueprint so routes are available
    app.register_blueprint(web_bp)
    
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def full_config_data():
    """Provide full configuration data with all required keys for Config class."""
    return {
        'NEWSAPI_AI_KEY': 'test_newsapi_key',
        'OPENWEATHER_API_KEY': 'test_openweather_key',
        'GEMINI_API_KEY': 'test_gemini_key',
        'GOOGLE_API_KEY': 'test_google_key',
        'GOOGLE_TTS_VOICE_NAME': 'en-US-Standard-C'  # Will be overridden in specific tests
    }


@pytest.fixture
def form_data():
    """Provide form data with lowercase field names for WebConfig.create_config_from_form."""
    return {
        'newsapi_key': 'test_newsapi_key',
        'openweather_api_key': 'test_openweather_key',
        'gemini_api_key': 'test_gemini_key',
        'google_api_key': 'test_google_key',
        'google_tts_voice_name': 'en-US-Neural2-C',  # Neural2 voice for testing
        'listener_name': 'Test User',
        'location_city': 'Denver',
        'location_country': 'US',
        'briefing_duration_minutes': 5,
        'news_topics': ['technology', 'business'],
        'max_articles_per_topic': 3
    }


class TestVoiceSelectionFlow:
    """Test voice selection from form to TTS generation."""
    
    def test_form_voice_choices_consistent(self, app):
        """Test that both forms have the same Google TTS voice choices."""
        with app.app_context():
            settings_form = SettingsForm()
            briefing_form = BriefingConfigForm()
            
            settings_choices = settings_form.google_tts_voice_name.choices
            briefing_choices = briefing_form.google_tts_voice_name.choices
            
            assert settings_choices == briefing_choices, "Voice choices should be identical in both forms"
            
            # Verify we have a good selection of voices (both Standard and Neural2)
            assert len(settings_choices) > 10, "Should have good selection of Google TTS voices"
            
            # Verify default voice is a Standard voice for cost efficiency
            assert settings_choices[0][0] == 'en-US-Standard-A', "First choice should be a Standard voice"
            
            # Verify all voice names are valid (non-empty)
            for voice_name, description in settings_choices:
                assert voice_name, f"Voice name should not be empty for {description}"
                assert description, f"Description should not be empty for {voice_name}"
                
            # Verify we have both Standard and Neural2 voices
            voice_names = [choice[0] for choice in settings_choices]
            has_standard = any('Standard' in name for name in voice_names)
            has_neural2 = any('Neural2' in name for name in voice_names)
            assert has_standard, "Should have Standard voices for cost efficiency"
            assert has_neural2, "Should have Neural2 voices for quality"
    
    def test_config_creation_preserves_voice_name(self, form_data):
        """Test that Google TTS voice name is properly preserved when creating Config from form data."""
        test_form_data = form_data.copy()
        test_form_data['google_tts_voice_name'] = 'en-US-Neural2-F'
        
        config = WebConfig.create_config_from_form(test_form_data)
        
        assert config.get('GOOGLE_TTS_VOICE_NAME') == 'en-US-Neural2-F'
        assert config.get('GOOGLE_API_KEY') == 'test_google_key'
        assert config.get('GOOGLE_TTS_LANGUAGE_CODE') == 'en-US'  # Should be extracted from voice name
    
    def test_default_voice_handling(self, form_data):
        """Test that default Google TTS voice is handled correctly."""
        # Test with Standard voice (cost-effective default)
        form_data_default = form_data.copy()
        form_data_default['google_tts_voice_name'] = 'en-US-Standard-C'
        
        config = WebConfig.create_config_from_form(form_data_default)
        assert config.get('GOOGLE_TTS_VOICE_NAME') == 'en-US-Standard-C'
        
        # Test with no voice name (should default to Standard voice)
        form_data_empty = form_data_default.copy()
        del form_data_empty['google_tts_voice_name']
        
        config = WebConfig.create_config_from_form(form_data_empty)
        assert config.get('GOOGLE_TTS_VOICE_NAME') == 'en-US-Standard-C'  # Should default to cost-effective voice


class TestVoicePreview:
    """Test voice preview functionality."""
    
    @patch('tts_generator.generate_audio')
    def test_preview_voice_endpoint(self, mock_generate_audio, client):
        """Test the Google TTS voice preview endpoint."""
        mock_generate_audio.return_value = b'fake_audio_data'
        
        # Set up session with API keys
        with client.session_transaction() as sess:
            sess['api_keys'] = {
                'google_api_key': 'test_google_api_key'
            }
        
        # Test voice preview request
        response = client.post('/preview-voice', 
                              json={'voice_id': 'en-US-Neural2-C'},
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] is True
        assert 'audio_data' in data
        assert data['voice_name'] == 'en-US-Neural2-C'
        
        # Verify generate_audio was called with correct parameters
        mock_generate_audio.assert_called_once()
        call_args = mock_generate_audio.call_args
        # generate_audio is called as generate_audio(script_text, config)
        config_used = call_args[0][1]  # Second positional argument is the config
        
        assert config_used.get('GOOGLE_TTS_VOICE_NAME') == 'en-US-Neural2-C'
        assert config_used.get('GOOGLE_API_KEY') == 'test_google_api_key'
        assert config_used.get('TTS_PROVIDER') == 'google'
    
    def test_preview_voice_no_api_key(self, client):
        """Test voice preview fails without Google API key."""
        response = client.post('/preview-voice',
                              json={'voice_id': 'en-US-Neural2-C'},
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] is False
        assert 'Google API key not configured' in data['error']
    
    def test_preview_voice_no_voice_id(self, client):
        """Test voice preview fails without voice name."""
        with client.session_transaction() as sess:
            sess['api_keys'] = {'google_api_key': 'test_key'}
        
        response = client.post('/preview-voice',
                              json={},
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] is False
        assert 'No voice name provided' in data['error']


class TestTTSVoiceGeneration:
    """Test Google TTS generation with voice selection."""
    
    @patch('google_tts_generator.generate_audio_google')
    def test_generate_audio_uses_correct_voice_name(self, mock_generate_google, full_config_data):
        """Test that generate_audio uses the correct Google TTS voice name."""
        # Setup mock
        mock_generate_google.return_value = b'fake_audio'
        
        # Test with specific voice name
        config_data = full_config_data.copy()
        config_data['GOOGLE_TTS_VOICE_NAME'] = 'en-US-Neural2-F'  # High quality Neural2 voice
        config_data['TTS_PROVIDER'] = 'google'  # Force Google TTS
        config = Config(config_data)
        
        generate_audio("Test script", config)
        
        # Verify generate_audio_google was called with correct config
        mock_generate_google.assert_called_once_with("Test script", config)
        
        # Verify config has correct voice settings
        assert config.get('GOOGLE_TTS_VOICE_NAME') == 'en-US-Neural2-F'
        assert config.get('TTS_PROVIDER') == 'google'
    
    @patch('google_tts_generator.generate_audio_google')
    def test_generate_audio_standard_voice_cost_efficiency(self, mock_generate_google, full_config_data):
        """Test that Standard voices are used for cost efficiency."""
        # Setup mock
        mock_generate_google.return_value = b'fake_audio'
        
        # Test with Standard voice (cost-effective)
        config_data = full_config_data.copy()
        config_data['GOOGLE_TTS_VOICE_NAME'] = 'en-US-Standard-C'
        config_data['TTS_PROVIDER'] = 'google'
        config = Config(config_data)
        
        generate_audio("Test script", config)
        
        # Verify generate_audio_google was called with correct config
        mock_generate_google.assert_called_once_with("Test script", config)
        
        # Verify config has correct Standard voice settings for cost efficiency
        assert config.get('GOOGLE_TTS_VOICE_NAME') == 'en-US-Standard-C'
        assert config.get('TTS_PROVIDER') == 'google'
        
        # Verify it's a Standard voice (cost-effective)
        voice_name = config.get('GOOGLE_TTS_VOICE_NAME')
        assert 'Standard' in voice_name, "Should use Standard voice for cost efficiency" 