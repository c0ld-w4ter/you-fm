"""
Tests to verify voice selection fixes.

This file tests the specific regression fixes for voice selection:
1. Default voice ID is correct (Rachel, female)
2. Voice preview works with correct voice IDs
3. Voice selection flows properly to TTS generation
"""

import pytest
from unittest.mock import patch, MagicMock
from config_web import WebConfig


class TestVoiceFixes:
    """Test fixes for voice selection issues."""
    
    def test_default_voice_is_rachel(self):
        """Test that default voice resolves to correct Rachel voice ID."""
        # Test form data with default voice
        form_data = {
            'newsapi_key': 'test_key',
            'openweather_api_key': 'test_key',
            'taddy_api_key': 'test_key', 
            'taddy_user_id': 'test_id',
            'gemini_api_key': 'test_key',
            'elevenlabs_api_key': 'test_key',
            'elevenlabs_voice_id': 'default',
            'listener_name': 'Test User',
            'location_city': 'Denver',
            'location_country': 'US',
        }
        
        config = WebConfig.create_config_from_form(form_data)
        voice_id = config.get('ELEVENLABS_VOICE_ID')
        
        assert voice_id == 'default', "Form should store 'default' value"
        
        # Now test that TTS generation resolves this correctly
        with patch('elevenlabs.client.ElevenLabs') as mock_elevenlabs_class:
            mock_client = MagicMock()
            mock_elevenlabs_class.return_value = mock_client
            mock_client.text_to_speech.convert.return_value = b'fake_audio'
            
            from tts_generator import generate_audio
            generate_audio("Test script", config)
            
            # Verify correct Rachel voice ID was used
            mock_client.text_to_speech.convert.assert_called_once()
            call_kwargs = mock_client.text_to_speech.convert.call_args[1]
            assert call_kwargs['voice_id'] == '21m00Tcm4TlvDq8ikWAM', "Should resolve to Rachel voice ID"
    
    def test_specific_voice_id_preserved(self):
        """Test that specific voice IDs are preserved through the flow."""
        # Test with Bella voice
        form_data = {
            'newsapi_key': 'test_key',
            'openweather_api_key': 'test_key',
            'taddy_api_key': 'test_key',
            'taddy_user_id': 'test_id', 
            'gemini_api_key': 'test_key',
            'elevenlabs_api_key': 'test_key',
            'elevenlabs_voice_id': 'EXAVITQu4vr4xnSDxMaL',  # Bella
            'listener_name': 'Test User',
            'location_city': 'Denver',
            'location_country': 'US',
        }
        
        config = WebConfig.create_config_from_form(form_data)
        voice_id = config.get('ELEVENLABS_VOICE_ID')
        
        assert voice_id == 'EXAVITQu4vr4xnSDxMaL', "Specific voice ID should be preserved"
        
        # Test TTS generation uses the correct voice
        with patch('elevenlabs.client.ElevenLabs') as mock_elevenlabs_class:
            mock_client = MagicMock()
            mock_elevenlabs_class.return_value = mock_client
            mock_client.text_to_speech.convert.return_value = b'fake_audio'
            
            from tts_generator import generate_audio
            generate_audio("Test script", config)
            
            # Verify Bella voice ID was used directly (no substitution)
            mock_client.text_to_speech.convert.assert_called_once()
            call_kwargs = mock_client.text_to_speech.convert.call_args[1]
            assert call_kwargs['voice_id'] == 'EXAVITQu4vr4xnSDxMaL', "Should use Bella voice ID directly"
    
    @patch('elevenlabs.client.ElevenLabs')
    def test_voice_preview_config_creation(self, mock_elevenlabs_class):
        """Test that voice preview creates proper config object."""
        # Setup mock
        mock_client = MagicMock()
        mock_elevenlabs_class.return_value = mock_client
        mock_client.text_to_speech.convert.return_value = b'fake_audio'
        
        # Test the preview config creation approach
        elevenlabs_api_key = 'test_api_key'
        voice_id = 'EXAVITQu4vr4xnSDxMaL'
        
        # This mimics the current preview endpoint
        preview_config = type('PreviewConfig', (), {
            'get': lambda self, key, default=None: {
                'ELEVENLABS_API_KEY': elevenlabs_api_key,
                'ELEVENLABS_VOICE_ID': voice_id
            }.get(key, default),
            'get_voice_speed': lambda self: 1.0
        })()
        
        # Test that the config works
        assert preview_config.get('ELEVENLABS_API_KEY') == 'test_api_key'
        assert preview_config.get('ELEVENLABS_VOICE_ID') == 'EXAVITQu4vr4xnSDxMaL'
        assert preview_config.get_voice_speed() == 1.0
        
        # Test with TTS generator
        from tts_generator import generate_audio
        generate_audio("Preview text", preview_config)
        
        # Verify correct voice was used
        mock_client.text_to_speech.convert.assert_called_once()
        call_kwargs = mock_client.text_to_speech.convert.call_args[1]
        assert call_kwargs['voice_id'] == 'EXAVITQu4vr4xnSDxMaL'
    
    def test_form_voice_choices_structure(self):
        """Test that voice choices have the expected structure."""
        from web.forms import SettingsForm, BriefingConfigForm
        
        # Create simple mock app context
        from flask import Flask
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'
        app.config['WTF_CSRF_ENABLED'] = False
        
        with app.app_context():
            settings_form = SettingsForm()
            briefing_form = BriefingConfigForm()
            
            # Test that forms have same choices
            settings_choices = settings_form.elevenlabs_voice_id.choices
            briefing_choices = briefing_form.elevenlabs_voice_id.choices
            
            assert settings_choices == briefing_choices, "Voice choices should be identical"
            
            # Test structure of choices
            assert len(settings_choices) > 5, "Should have expanded voice selection"
            
            # First choice should be default (Rachel)
            default_choice = settings_choices[0]
            assert default_choice[0] == 'default', "First choice value should be 'default'"
            assert 'Rachel' in default_choice[1], "First choice should mention Rachel"
            assert 'Female' in default_choice[1], "First choice should indicate Female"
            
            # Test that we have both male and female voices
            choice_text = ' '.join([choice[1] for choice in settings_choices])
            assert 'Male' in choice_text, "Should have male voices"
            assert 'Female' in choice_text, "Should have female voices" 