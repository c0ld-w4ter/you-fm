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
        'NEWSAPI_KEY': 'test_newsapi_key',
        'OPENWEATHER_API_KEY': 'test_openweather_key',
        'TADDY_API_KEY': 'test_taddy_key',
        'TADDY_USER_ID': 'test_taddy_user',
        'GEMINI_API_KEY': 'test_gemini_key',
        'ELEVENLABS_API_KEY': 'test_elevenlabs_key',
        'ELEVENLABS_VOICE_ID': 'EXAVITQu4vr4xnSDxMaL'  # Will be overridden in specific tests
    }


@pytest.fixture
def form_data():
    """Provide form data with lowercase field names for WebConfig.create_config_from_form."""
    return {
        'newsapi_key': 'test_newsapi_key',
        'openweather_api_key': 'test_openweather_key',
        'taddy_api_key': 'test_taddy_key',
        'taddy_user_id': 'test_taddy_user',
        'gemini_api_key': 'test_gemini_key',
        'elevenlabs_api_key': 'test_elevenlabs_key',
        'elevenlabs_voice_id': 'EXAVITQu4vr4xnSDxMaL'  # Will be overridden in specific tests
    }


class TestVoiceSelectionFlow:
    """Test voice selection from form to TTS generation."""
    
    def test_form_voice_choices_consistent(self, app):
        """Test that both forms have the same voice choices."""
        with app.app_context():
            settings_form = SettingsForm()
            briefing_form = BriefingConfigForm()
            
            settings_choices = settings_form.elevenlabs_voice_id.choices
            briefing_choices = briefing_form.elevenlabs_voice_id.choices
            
            assert settings_choices == briefing_choices, "Voice choices should be identical in both forms"
            
            # Verify we have more than the original 5 voices
            assert len(settings_choices) > 5, "Should have expanded voice selection"
            
            # Verify default voice is first choice
            assert settings_choices[0][0] == 'default', "First choice should be 'default'"
            
            # Verify all voice IDs are valid (non-empty)
            for voice_id, description in settings_choices:
                assert voice_id, f"Voice ID should not be empty for {description}"
                assert description, f"Description should not be empty for {voice_id}"
    
    def test_config_creation_preserves_voice_id(self, form_data):
        """Test that voice ID is properly preserved when creating Config from form data."""
        test_form_data = form_data.copy()
        test_form_data['elevenlabs_voice_id'] = 'EXAVITQu4vr4xnSDxMaL'
        
        config = WebConfig.create_config_from_form(test_form_data)
        
        assert config.get('ELEVENLABS_VOICE_ID') == 'EXAVITQu4vr4xnSDxMaL'
        assert config.get('ELEVENLABS_API_KEY') == 'test_elevenlabs_key'
    
    def test_default_voice_handling(self, form_data):
        """Test that default voice is handled correctly."""
        # Test with 'default' value
        form_data_default = form_data.copy()
        form_data_default['elevenlabs_voice_id'] = 'default'
        
        config = WebConfig.create_config_from_form(form_data_default)
        assert config.get('ELEVENLABS_VOICE_ID') == 'default'
        
        # Test with no voice ID (should default)
        form_data_empty = form_data_default.copy()
        del form_data_empty['elevenlabs_voice_id']
        
        config = WebConfig.create_config_from_form(form_data_empty)
        assert config.get('ELEVENLABS_VOICE_ID') == 'default'


class TestVoicePreview:
    """Test voice preview functionality."""
    
    @patch('tts_generator.generate_audio')
    def test_preview_voice_endpoint(self, mock_generate_audio, client):
        """Test the voice preview endpoint."""
        mock_generate_audio.return_value = b'fake_audio_data'
        
        # Set up session with API keys
        with client.session_transaction() as sess:
            sess['api_keys'] = {
                'elevenlabs_api_key': 'test_api_key'
            }
        
        # Test voice preview request
        response = client.post('/preview-voice', 
                              json={'voice_id': 'EXAVITQu4vr4xnSDxMaL'},
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] is True
        assert 'audio_data' in data
        assert data['voice_id'] == 'EXAVITQu4vr4xnSDxMaL'
        
        # Verify generate_audio was called with correct parameters
        mock_generate_audio.assert_called_once()
        call_args = mock_generate_audio.call_args
        # generate_audio is called as generate_audio(script_text, config)
        config_used = call_args[0][1]  # Second positional argument is the config
        
        assert config_used.get('ELEVENLABS_VOICE_ID') == 'EXAVITQu4vr4xnSDxMaL'
        assert config_used.get('ELEVENLABS_API_KEY') == 'test_api_key'
    
    def test_preview_voice_no_api_key(self, client):
        """Test voice preview fails without API key."""
        response = client.post('/preview-voice',
                              json={'voice_id': 'EXAVITQu4vr4xnSDxMaL'},
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] is False
        assert 'API key not configured' in data['error']
    
    def test_preview_voice_no_voice_id(self, client):
        """Test voice preview fails without voice ID."""
        with client.session_transaction() as sess:
            sess['api_keys'] = {'elevenlabs_api_key': 'test_key'}
        
        response = client.post('/preview-voice',
                              json={},
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] is False
        assert 'No voice ID provided' in data['error']


class TestTTSVoiceGeneration:
    """Test TTS generation with voice selection."""
    
    @patch('elevenlabs.client.ElevenLabs')
    def test_generate_audio_uses_correct_voice_id(self, mock_elevenlabs_class, full_config_data):
        """Test that generate_audio uses the correct voice ID."""
        # Setup mock
        mock_client = MagicMock()
        mock_elevenlabs_class.return_value = mock_client
        mock_client.text_to_speech.convert.return_value = b'fake_audio'
        
        # Test with specific voice ID
        config_data = full_config_data.copy()
        config_data['ELEVENLABS_VOICE_ID'] = 'EXAVITQu4vr4xnSDxMaL'  # Bella
        config = Config(config_data)
        
        generate_audio("Test script", config)
        
        # Verify correct voice ID was used
        mock_client.text_to_speech.convert.assert_called_once()
        call_kwargs = mock_client.text_to_speech.convert.call_args[1]
        assert call_kwargs['voice_id'] == 'EXAVITQu4vr4xnSDxMaL'
    
    @patch('elevenlabs.client.ElevenLabs')
    def test_generate_audio_default_voice_resolution(self, mock_elevenlabs_class, full_config_data):
        """Test that 'default' voice ID is resolved to correct ElevenLabs ID."""
        # Setup mock
        mock_client = MagicMock()
        mock_elevenlabs_class.return_value = mock_client
        mock_client.text_to_speech.convert.return_value = b'fake_audio'
        
        # Test with 'default' voice ID
        config_data = full_config_data.copy()
        config_data['ELEVENLABS_VOICE_ID'] = 'default'
        config = Config(config_data)
        
        generate_audio("Test script", config)
        
        # Verify default resolves to the expected voice ID
        mock_client.text_to_speech.convert.assert_called_once()
        call_kwargs = mock_client.text_to_speech.convert.call_args[1]
        
        # Should resolve to a specific ElevenLabs voice ID, not 'default'
        assert call_kwargs['voice_id'] != 'default'
        assert isinstance(call_kwargs['voice_id'], str)
        assert len(call_kwargs['voice_id']) > 10  # ElevenLabs IDs are long strings 