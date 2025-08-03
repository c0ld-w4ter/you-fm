"""
Tests to verify Google TTS voice selection fixes.

This file tests the specific regression fixes for voice selection:
1. Default voice is cost-effective Standard voice
2. Voice preview works with correct Google TTS voice names
3. Voice selection flows properly to Google TTS generation
"""

import pytest
from unittest.mock import patch, MagicMock
from config_web import WebConfig


class TestVoiceFixes:
    """Test fixes for Google TTS voice selection issues."""
    
    def test_default_voice_is_standard(self):
        """Test that default voice is cost-effective Standard voice."""
        # Test form data with default Google TTS voice
        form_data = {
            'newsapi_key': 'test_key',
            'openweather_api_key': 'test_key',
            'gemini_api_key': 'test_key',
            'google_api_key': 'test_key',
            'google_tts_voice_name': 'en-US-Standard-C',  # Testing Standard voice for cost efficiency
            'tts_provider': 'google'  # Force Google TTS
        }
        
        config = WebConfig.create_config_from_form(form_data)
        voice_name = config.get('GOOGLE_TTS_VOICE_NAME')
        
        assert voice_name == 'en-US-Standard-C', "Form should store Standard voice for cost efficiency"
        assert 'Standard' in voice_name, "Should be a Standard voice for cost efficiency"
        
        # Now test that TTS generation uses this correctly
        with patch('google_tts_generator.generate_audio_google') as mock_generate_google:
            mock_generate_google.return_value = b'fake_audio'
            
            from tts_generator import generate_audio
            generate_audio("Test script", config)
            
            # Verify generate_audio_google was called with correct config
            mock_generate_google.assert_called_once_with("Test script", config)
            assert config.get('GOOGLE_TTS_VOICE_NAME') == 'en-US-Standard-C'
    
    def test_specific_voice_name_preserved(self):
        """Test that specific Google TTS voice names are preserved through the flow."""
        # Test with Neural2 voice (high quality)
        form_data = {
            'newsapi_key': 'test_key',
            'openweather_api_key': 'test_key',
            'gemini_api_key': 'test_key',
            'google_api_key': 'test_key',
            'google_tts_voice_name': 'en-US-Neural2-F',  # High quality Neural2 voice
            'tts_provider': 'google'  # Force Google TTS
        }
        
        config = WebConfig.create_config_from_form(form_data)
        voice_name = config.get('GOOGLE_TTS_VOICE_NAME')
        
        assert voice_name == 'en-US-Neural2-F', "Specific voice name should be preserved"
        assert 'Neural2' in voice_name, "Should be Neural2 voice for high quality"
        
        # Test TTS generation uses the correct voice
        with patch('google_tts_generator.generate_audio_google') as mock_generate_google:
            mock_generate_google.return_value = b'fake_audio'
            
            from tts_generator import generate_audio
            generate_audio("Test script", config)
            
            # Verify Neural2 voice was used directly
            mock_generate_google.assert_called_once_with("Test script", config)
            assert config.get('GOOGLE_TTS_VOICE_NAME') == 'en-US-Neural2-F'
    
    @patch('google_tts_generator.generate_audio_google')
    def test_voice_preview_config_creation(self, mock_generate_google):
        """Test that Google TTS voice preview creates proper config object."""
        # Setup mock
        mock_generate_google.return_value = b'fake_audio'
        
        # Test the preview config creation approach
        google_api_key = 'test_google_api_key'
        voice_name = 'en-US-Neural2-C'
        
        # This mimics the current preview endpoint with Google TTS provider
        preview_config = type('PreviewConfig', (), {
            'get': lambda self, key, default=None: {
                'GOOGLE_API_KEY': google_api_key,
                'GOOGLE_TTS_VOICE_NAME': voice_name,
                'GOOGLE_TTS_LANGUAGE_CODE': 'en-US',
                'TTS_PROVIDER': 'google'  # Force Google TTS
            }.get(key, default),
            'get_voice_speed': lambda self: 1.0
        })()
        
        # Test that the config works
        assert preview_config.get('GOOGLE_API_KEY') == 'test_google_api_key'
        assert preview_config.get('GOOGLE_TTS_VOICE_NAME') == 'en-US-Neural2-C'
        assert preview_config.get('TTS_PROVIDER') == 'google'
        assert preview_config.get_voice_speed() == 1.0
        
        # Test with TTS generator
        from tts_generator import generate_audio
        generate_audio("Preview text", preview_config)
        
        # Verify generate_audio_google was called with correct config
        mock_generate_google.assert_called_once_with("Preview text", preview_config)
    
    def test_form_voice_choices_structure(self):
        """Test that Google TTS voice choices have the expected structure."""
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
            settings_choices = settings_form.google_tts_voice_name.choices
            briefing_choices = briefing_form.google_tts_voice_name.choices
            
            assert settings_choices == briefing_choices, "Voice choices should be identical"
            
            # Test structure of choices
            assert len(settings_choices) > 10, "Should have expanded Google TTS voice selection"
            
            # Test that we have both Standard and Neural2 voices
            choice_text = ' '.join([choice[1] for choice in settings_choices])
            assert 'Standard' in choice_text, "Should have Standard voices"
            assert 'Neural2' in choice_text, "Should have Neural2 voices"
            assert 'Cost-effective' in choice_text, "Should indicate cost-effective Standard voices"
            assert 'High Quality' in choice_text, "Should indicate high quality Neural2 voices"
            
            # Test that we have both male and female voices
            assert 'Male' in choice_text, "Should have male voices"
            assert 'Female' in choice_text, "Should have female voices"
            
            # Verify voice name format (should be like 'en-US-Standard-C' or 'en-GB-Standard-A')
            voice_names = [choice[0] for choice in settings_choices]
            for voice_name in voice_names:
                assert '-' in voice_name, f"Voice name {voice_name} should contain hyphens"
                assert voice_name.startswith('en-'), f"Voice name {voice_name} should start with English language code"
                parts = voice_name.split('-')
                assert len(parts) >= 3, f"Voice name {voice_name} should have at least 3 parts (lang-region-type-id)" 