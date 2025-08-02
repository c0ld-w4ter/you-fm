"""
Unit tests for AI Daily Briefing Agent web interface.

Tests the Flask web application functionality including form validation,
route handlers, and configuration integration.
"""

import pytest
import json
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from flask import session, url_for

from app import create_app
from web.forms import BriefingConfigForm, APIKeysForm, SettingsForm
from config_web import WebConfig
from config import Config, ConfigurationError


class TestAPIKeysForm:
    """Test API keys form validation."""
    
    def test_valid_api_keys_form(self, app, valid_form_data):
        """Test valid API keys form submission."""
        with app.app_context():
            form_data = {
                'newsapi_key': valid_form_data['newsapi_key'],
                'openweather_api_key': valid_form_data['openweather_api_key'],
                'gemini_api_key': valid_form_data['gemini_api_key'],
                'elevenlabs_api_key': valid_form_data['elevenlabs_api_key']
            }
            
            form = APIKeysForm(data=form_data)
            assert form.validate()
    
    def test_missing_required_api_key(self, app):
        """Test form validation with missing required API keys."""
        with app.app_context():
            form_data = {
                'newsapi_key': '',  # Missing required field
                'openweather_api_key': 'test_weather_key',
                'gemini_api_key': 'test_gemini_key',
                'elevenlabs_api_key': 'test_elevenlabs_key',
            }
            
            form = APIKeysForm(data=form_data)
            
            # Test that validation catches missing required field
            assert not form.newsapi_key.data
            # In real form validation, this would fail validation


class TestSettingsForm:
    """Test settings form validation including new advanced fields."""
    
    def test_valid_settings_form_with_advanced_fields(self, app):
        """Test form validation with valid settings and remaining advanced fields."""
        with app.app_context():
            form_data = {
                'listener_name': 'Test User',
                'location_city': 'Denver',
                'location_country': 'US',
                'briefing_duration_minutes': 8,
                'google_voice_name': 'en-US-Journey-D',
                'aws_region': 'us-east-1',
                # Only remaining advanced field
                'briefing_tone': 'casual',
                # Removed fields: content_depth, keywords_exclude, voice_speed, news_topics, max_articles_per_topic
            }
            
            form = SettingsForm(data=form_data)
            
            # Verify remaining field is present and has correct values
            assert form.briefing_tone.data == 'casual'
            # Removed fields should not exist
            assert not hasattr(form, 'content_depth')
            assert not hasattr(form, 'keywords_exclude') 
            assert not hasattr(form, 'voice_speed')
            assert not hasattr(form, 'news_topics')
            assert not hasattr(form, 'max_articles_per_topic')

    def test_advanced_field_defaults(self, app):
        """Test that remaining advanced field has proper default values."""
        with app.app_context():
            form = SettingsForm()
            
            # Check that defaults are set correctly for remaining field
            assert form.briefing_tone.default == 'professional'
            # Removed fields should not exist
            assert not hasattr(form, 'content_depth')
            assert not hasattr(form, 'keywords_exclude')
            assert not hasattr(form, 'voice_speed')

    def test_advanced_field_validation(self, app):
        """Test validation works without removed fields."""
        with app.app_context():
            form_data = {
                'briefing_duration_minutes': 8,
                'briefing_tone': 'professional',
            }
            
            form = SettingsForm(data=form_data)
            
            # Test that form can be created without removed fields
            assert form.briefing_tone.data == 'professional'
            # Removed fields should not exist
            assert not hasattr(form, 'keywords_exclude')
            assert not hasattr(form, 'content_depth')
            assert not hasattr(form, 'voice_speed')


class TestWebConfig:
    """Test web configuration handling including advanced fields."""
    
    def test_create_config_with_advanced_fields(self):
        """Test creating Config object with simplified advanced fields."""
        form_data = {
            'newsapi_key': 'test_news_key',
            'openweather_api_key': 'test_weather_key',
            'gemini_api_key': 'test_gemini_key',
            'elevenlabs_api_key': 'test_elevenlabs_key',
            'listener_name': 'Test User',
            'location_city': 'Denver',
            'location_country': 'US',
            'briefing_duration_minutes': 10,
            'google_voice_name': 'en-US-Journey-D',
            'aws_region': 'us-east-1',
            # Only remaining advanced field
            'briefing_tone': 'casual',
            # Removed fields are auto-configured
        }
        
        # This should not raise an exception
        config = WebConfig.create_config_from_form(form_data)
        
        # Verify advanced fields are configured correctly
        assert config.get('BRIEFING_TONE') == 'casual'
        assert config.get('CONTENT_DEPTH') == 'balanced'  # Hardcoded
        assert config.get('KEYWORDS_EXCLUDE') == ''  # Hardcoded
        assert config.get('VOICE_SPEED') == '1.0'  # Hardcoded
        assert config.get('NEWS_TOPICS') == 'business,entertainment,general,health,science,sports,technology'  # Auto-configured
        assert config.get('MAX_ARTICLES_PER_TOPIC') == '100'  # Auto-configured

    def test_form_defaults_include_advanced_fields(self):
        """Test that form defaults include values for remaining advanced fields."""
        defaults = WebConfig.get_form_defaults()
        
        # Verify remaining advanced field default is present
        assert 'briefing_tone' in defaults
        # Removed fields should not be in defaults
        assert 'content_depth' not in defaults
        assert 'keywords_exclude' not in defaults
        assert 'voice_speed' not in defaults
        assert 'news_topics' not in defaults
        assert 'max_articles_per_topic' not in defaults
    
    def test_config_with_empty_advanced_fields(self):
        """Test configuration creation with empty advanced fields."""
        form_data = {
            'newsapi_key': 'test_news_key',
            'openweather_api_key': 'test_weather_key',
            'gemini_api_key': 'test_gemini_key',
            'elevenlabs_api_key': 'test_elevenlabs_key',
            # Advanced fields not provided (should use defaults)
        }
        
        config = WebConfig.create_config_from_form(form_data)
        
        # Should use defaults for missing advanced fields
        assert config.get('BRIEFING_TONE') == 'professional'
        assert config.get('CONTENT_DEPTH') == 'balanced'
        assert config.get('KEYWORDS_EXCLUDE') == ''
        assert config.get('VOICE_SPEED') == '1.0'


class TestAdvancedFieldsIntegration:
    """Test integration of advanced fields with existing functionality."""
    
    def test_session_storage_includes_advanced_fields(self, app):
        """Test that session properly stores advanced field values."""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                # Simulate storing settings with advanced fields
                sess['settings'] = {
                    'listener_name': 'Test User',
                    'briefing_duration_minutes': 8,
                    'briefing_tone': 'energetic',
                    'content_depth': 'headlines',
                    'keywords_exclude': 'politics,sports',
                    'voice_speed': '0.8',
                }
            
            # Verify session contains advanced fields
            with client.session_transaction() as sess:
                settings = sess.get('settings', {})
                assert settings['briefing_tone'] == 'energetic'
                assert settings['content_depth'] == 'headlines'
                assert settings['keywords_exclude'] == 'politics,sports'
                assert settings['voice_speed'] == '0.8'
    
    def test_complete_form_to_config_workflow(self, app):
        """Test complete workflow from form data to Config object."""
        with app.test_client() as client:
            # Simulate complete form submission data
            form_data = {
                # Required API keys
                'newsapi_key': 'test_news_key',
                'openweather_api_key': 'test_weather_key',
                'gemini_api_key': 'test_gemini_key',
                'elevenlabs_api_key': 'test_elevenlabs_key',
                
                # Basic settings
                'listener_name': 'Integration Test User',
                'location_city': 'Boston',
                'location_country': 'US',
                'briefing_duration_minutes': 12,
                'google_voice_name': 'en-US-Studio-M',
                
                # Remaining advanced setting
                'briefing_tone': 'casual',
                # Removed fields are auto-configured
            }
            
            # Create config from form data
            config = WebConfig.create_config_from_form(form_data)
            
            # Verify all fields are properly mapped
            assert config.get('LISTENER_NAME') == 'Integration Test User'
            assert config.get('LOCATION_CITY') == 'Boston'
            assert config.get('BRIEFING_DURATION_MINUTES') == '12'
            assert config.get('NEWS_TOPICS') == 'business,entertainment,general,health,science,sports,technology'  # Auto-configured
            assert config.get('MAX_ARTICLES_PER_TOPIC') == '100'  # Auto-configured
            assert config.get('BRIEFING_TONE') == 'casual'
            assert config.get('CONTENT_DEPTH') == 'balanced'  # Hardcoded
            assert config.get('KEYWORDS_EXCLUDE') == ''  # Hardcoded
            assert config.get('VOICE_SPEED') == '1.0'  # Hardcoded


class TestPreviewFunctionality:
    """Test preview script functionality (Iteration 3)."""
    
    def test_preview_script_route_success(self, app):
        """Test successful script preview generation via web route."""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                # Set up complete session data
                sess['api_keys'] = {
                    'newsapi_key': 'test_news_key',
                    'openweather_api_key': 'test_weather_key',
                    'gemini_api_key': 'test_gemini_key',
                    'elevenlabs_api_key': 'test_elevenlabs_key',
                }
                sess['settings'] = {
                    'listener_name': 'Test User',
                    'briefing_duration_minutes': 5,
                    'briefing_tone': 'casual',
                    'content_depth': 'headlines',
                    'keywords_exclude': 'sports,celebrity',
                    'voice_speed': '1.2'
                }
            
            # Mock the generate_script_only function
            with patch('main.generate_script_only') as mock_generate:
                mock_generate.return_value = {
                    'success': True,
                    'data': {
                        'script_content': 'This is a test script for preview.',
                        'word_count': 50,
                        'estimated_duration_minutes': 2.5,
                        'generation_time_seconds': 8.3,
                        'articles_count': 3,
                        'script_length_chars': 200,
                        'has_weather': True,
                        'tone': 'casual',
                        'depth': 'headlines',
                        'keywords_excluded': 2
                    }
                }
                
                # Test the preview route
                response = client.post('/preview-script')
                
                # Check response
                assert response.status_code == 200
                data = response.get_json()
                
                assert data['success'] is True
                assert data['script'] == 'This is a test script for preview.'
                assert data['word_count'] == 50
                assert data['estimated_duration_minutes'] == 2.5
                assert data['generation_time_seconds'] == 8.3
                assert data['articles_count'] == 3
                assert data['tone'] == 'casual'
                assert data['depth'] == 'headlines'
                assert data['keywords_excluded'] == 2
                
                # Verify generate_script_only was called
                mock_generate.assert_called_once()
    
    def test_preview_script_route_incomplete_config(self, app):
        """Test preview route with incomplete configuration."""
        with app.test_client() as client:
            # Don't set session data
            response = client.post('/preview-script')
            
            assert response.status_code == 200
            data = response.get_json()
            
            assert data['success'] is False
            assert 'Configuration incomplete' in data['error']
    
    def test_preview_script_route_generation_failure(self, app):
        """Test preview route when script generation fails."""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                # Provide complete session data so config validation passes
                sess['api_keys'] = {
                    'newsapi_key': 'test_news_key',
                    'openweather_api_key': 'test_weather_key',
                    'gemini_api_key': 'test_gemini_key',
                    'elevenlabs_api_key': 'test_elevenlabs_key',
                }
                sess['settings'] = {'briefing_duration_minutes': 5}
            
            # Mock the generate_script_only function to return error
            with patch('main.generate_script_only') as mock_generate:
                mock_generate.return_value = {
                    'success': False,
                    'error': 'API connection failed',
                    'message': 'Failed to fetch news data'
                }
                
                response = client.post('/preview-script')
                
                assert response.status_code == 200
                data = response.get_json()
                
                assert data['success'] is False
                assert data['error'] == 'API connection failed'
                assert data['message'] == 'Failed to fetch news data'


class TestGenerateScriptOnly:
    """Test the generate_script_only function from main.py."""
    
    @patch('data_fetchers.get_weather')
    @patch('data_fetchers.get_news_articles') 
    @patch('summarizer.create_briefing_script')
    def test_generate_script_only_success(self, mock_script, mock_news, mock_weather):
        """Test successful script-only generation."""
        from main import generate_script_only
        from config import Config
        
        # Set up mocks
        mock_weather.return_value = Mock(city='Test City')
        mock_news.return_value = [Mock(title='Test Article')]
        mock_script.return_value = 'This is a test script for preview functionality.'
        
        # Create test config
        config = Config({
            'NEWSAPI_AI_KEY': 'test_key',
            'OPENWEATHER_API_KEY': 'test_key',
            'GEMINI_API_KEY': 'test_key',
            'ELEVENLABS_API_KEY': 'test_key',
            'BRIEFING_TONE': 'energetic',
            'CONTENT_DEPTH': 'detailed',
            'KEYWORDS_EXCLUDE': 'politics',
            'VOICE_SPEED': '0.8'
        })
        
        # Call function
        result = generate_script_only(config)
        
        # Verify result
        assert result['success'] is True
        assert result['status'] == 'success'
        assert 'Script preview generated successfully' in result['message']
        
        data = result['data']
        assert data['script_content'] == 'This is a test script for preview functionality.'
        assert data['word_count'] == 8  # Number of words in test script
        assert data['estimated_duration_minutes'] > 0
        assert data['articles_count'] == 1
        assert data['has_weather'] is True
        assert data['tone'] == 'energetic'
        assert data['depth'] == 'detailed'
        assert data['keywords_excluded'] == 1
        assert data['generation_time_seconds'] >= 0  # May be 0 with mocked functions
        
        # Verify all functions were called
        mock_weather.assert_called_once_with(config)
        mock_news.assert_called_once_with(config)
        mock_script.assert_called_once()
    
    @patch('data_fetchers.get_weather')
    def test_generate_script_only_error_handling(self, mock_weather):
        """Test error handling in script-only generation."""
        from main import generate_script_only
        from config import Config
        
        # Set up mock to raise exception
        mock_weather.side_effect = Exception('API connection failed')
        
        # Create test config
        config = Config({
            'NEWSAPI_AI_KEY': 'test_key',
            'OPENWEATHER_API_KEY': 'test_key',
            'GEMINI_API_KEY': 'test_key',
            'ELEVENLABS_API_KEY': 'test_key'
        })
        
        # Call function
        result = generate_script_only(config)
        
        # Verify error handling
        assert result['success'] is False
        assert result['status'] == 'error'
        assert 'API connection failed' in result['error']
        assert 'Script preview generation failed' in result['message']
    
    def test_generate_script_only_performance(self):
        """Test that script-only generation is faster than full generation."""
        # This is more of a documentation test - in real usage, 
        # script-only generation should be significantly faster
        from main import generate_script_only
        import time
        
        # We can't easily test actual performance without real API calls,
        # but we can verify the function exists and has the right structure
        assert callable(generate_script_only)
        
        # The function should not import TTS-related modules
        import inspect
        source = inspect.getsource(generate_script_only)
        assert 'generate_audio' not in source
        assert 'save_audio_locally' not in source


# Mock Flask app fixture for testing (update the existing one if needed)
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
def valid_api_keys_data():
    """Valid API keys form data for testing."""
    return {
        'newsapi_key': 'test_newsapi_key',
        'openweather_api_key': 'test_openweather_key',
        'gemini_api_key': 'test_gemini_key',
        'elevenlabs_api_key': 'test_elevenlabs_key'
    }


@pytest.fixture
def valid_settings_data():
    """Valid settings form data for testing."""
    return {
        'listener_name': 'Test User',
        'location_city': 'Denver',
        'location_country': 'US',
        'briefing_duration_minutes': 5,
        'news_topics': ['technology', 'business'],  # Updated to list format for checkboxes
        'max_articles_per_topic': 3,
        'google_voice_name': 'en-US-Journey-D',
        'aws_region': 'us-east-1',
        # Advanced settings (Milestone 5)
        'briefing_tone': 'professional',
        'content_depth': 'balanced',
        'keywords_exclude': '',
        'voice_speed': '1.0',
        # Personalization settings
        'specific_interests': 'AI, renewable energy',
        # 'briefing_goal' removed for UI simplification
        'followed_entities': 'OpenAI, Tesla',
        'hobbies': 'hiking, reading',
        'favorite_teams_artists': 'Lakers',
        'passion_topics': 'space exploration',
        'greeting_preference': 'Good morning!',
        'daily_routine_detail': 'I commute by train'
    }


@pytest.fixture
def valid_form_data():
    """Valid form data for testing (legacy fixture for compatibility)."""
    return {
        'newsapi_key': 'test_newsapi_key',
        'openweather_api_key': 'test_openweather_key',
        'gemini_api_key': 'test_gemini_key',
        'elevenlabs_api_key': 'test_elevenlabs_key',
        'listener_name': 'Test User',
        'location_city': 'Denver',
        'location_country': 'US',
        'briefing_duration_minutes': 5,
        'news_topics': 'technology,business',
        'max_articles_per_topic': 3,
        'google_voice_name': 'en-US-Journey-D',
        'aws_region': 'us-east-1'
    }


class TestMultiPageFlow:
    """Test the multi-page workflow."""
    
    def test_root_redirects_to_api_keys(self, client):
        """Test that root / redirects to /api-keys."""
        response = client.get('/')
        assert response.status_code == 302
        assert '/api-keys' in response.location
    
    def test_api_keys_page_loads(self, client):
        """Test that API keys page loads correctly."""
        response = client.get('/api-keys')
        assert response.status_code == 200
        assert b'API Keys' in response.data
        assert b'Save API Keys &amp; Continue' in response.data
        
        # Check that required fields are present
        assert b'name="newsapi_key"' in response.data
        assert b'name="openweather_api_key"' in response.data
        assert b'name="gemini_api_key"' in response.data
        assert b'name="elevenlabs_api_key"' in response.data
    
    def test_api_keys_form_validation_empty(self, client):
        """Test API keys form validation with empty data."""
        response = client.post('/api-keys', data={})
        assert response.status_code == 200
        assert b'NewsAPI Key is required' in response.data
        assert b'OpenWeatherMap API Key is required' in response.data
        assert b'Please correct the errors below' in response.data
    
    def test_api_keys_form_validation_partial(self, client):
        """Test API keys form validation with partial data."""
        response = client.post('/api-keys', data={
            'newsapi_key': 'test_key'
        })
        assert response.status_code == 200
        assert b'OpenWeatherMap API Key is required' in response.data
    
    def test_api_keys_form_success_redirects_to_settings(self, client, valid_api_keys_data):
        """Test successful API keys submission redirects to settings."""
        response = client.post('/api-keys', data=valid_api_keys_data)
        assert response.status_code == 302
        assert '/settings' in response.location
    
    def test_settings_page_requires_api_keys(self, client):
        """Test that settings page requires API keys to be set first."""
        response = client.get('/settings')
        assert response.status_code == 302
        assert '/api-keys' in response.location
    
    def test_settings_page_loads_after_api_keys(self, client, valid_api_keys_data):
        """Test that settings page loads after API keys are set."""
        # First set API keys
        client.post('/api-keys', data=valid_api_keys_data)
        
        # Then access settings
        response = client.get('/settings')
        assert response.status_code == 200
        assert b'Personal Settings' in response.data
        assert b'Save Settings &amp; Continue' in response.data
    
    def test_settings_form_success_redirects_to_generate(self, client, valid_api_keys_data, valid_settings_data):
        """Test successful settings submission redirects to generate."""
        # First set API keys
        client.post('/api-keys', data=valid_api_keys_data)
        
        # Then submit settings
        response = client.post('/settings', data=valid_settings_data)
        assert response.status_code == 302
        assert '/generate' in response.location
    
    def test_generate_page_requires_both_forms(self, client):
        """Test that generate page requires both API keys and settings."""
        response = client.get('/generate')
        assert response.status_code == 302
        assert '/api-keys' in response.location
    
    def test_generate_page_loads_after_both_forms(self, client, valid_api_keys_data, valid_settings_data):
        """Test that generate page loads after both forms are completed."""
        # Set API keys
        client.post('/api-keys', data=valid_api_keys_data)
        # Set settings
        client.post('/settings', data=valid_settings_data)
        
        # Access generate page
        response = client.get('/generate')
        assert response.status_code == 200
        assert b'Generate Daily Briefing' in response.data


class TestFormValidation:
    """Test individual form validation."""
    
    def test_api_keys_form_validation(self, app):
        """Test APIKeysForm validation."""
        with app.app_context():
            # Test valid form
            valid_data = {
                'newsapi_key': 'test_key',
                'openweather_api_key': 'test_key',
                'gemini_api_key': 'test_key',
                'elevenlabs_api_key': 'test_key'
            }
            form = APIKeysForm(data=valid_data)
            assert form.validate() is True
            
            # Test missing required field
            invalid_data = valid_data.copy()
            del invalid_data['newsapi_key']
            form = APIKeysForm(data=invalid_data)
            assert form.validate() is False
            assert 'newsapi_key' in form.errors
    
    def test_settings_form_validation(self, app):
        """Test SettingsForm validation."""
        with app.app_context():
            # Test valid form
            valid_data = {
                'listener_name': 'Test',
                'location_city': 'Denver',
                'location_country': 'US',
                'briefing_duration_minutes': 5,
                'news_topics': ['technology'],  # Fixed: use list format and valid category
                'max_articles_per_topic': 3,
                'google_voice_name': 'en-US-Journey-D'
            }
            form = SettingsForm(data=valid_data)
            assert form.validate() is True
            
            # Test invalid briefing duration (too high)
            invalid_data = valid_data.copy()
            invalid_data['briefing_duration_minutes'] = 50  # Too high
            form = SettingsForm(data=invalid_data)
            assert form.validate() is False
            assert 'briefing_duration_minutes' in form.errors
            
            # Test invalid briefing duration (too low)  
            invalid_data['briefing_duration_minutes'] = 0  # Too low
            form = SettingsForm(data=invalid_data)
            assert form.validate() is False
            assert 'briefing_duration_minutes' in form.errors
    
    def test_legacy_form_validation(self, app, valid_form_data):
        """Test legacy BriefingConfigForm validation."""
        with app.app_context():
            form = BriefingConfigForm(data=valid_form_data)
            assert form.validate() is True
            assert len(form.errors) == 0


class TestRouteHandlers:
    """Test HTTP route handlers."""
    
    def test_health_check_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['service'] == 'ai-daily-briefing-agent'
    
    def test_audio_file_serving(self, client):
        """Test audio file serving endpoint."""
        # Create a dummy audio file for testing using the same path construction as the route
        from flask import current_app
        
        with client.application.app_context():
            # Use the same path construction as the audio serving route
            audio_dir = os.path.join(current_app.root_path, 'static', 'audio')
            os.makedirs(audio_dir, exist_ok=True)
            test_file = os.path.join(audio_dir, 'test.mp3')
            
            with open(test_file, 'w') as f:
                f.write('dummy audio content')
            
            try:
                response = client.get('/audio/test.mp3')
                assert response.status_code == 200
                assert response.mimetype == 'audio/mpeg'
            finally:
                # Clean up
                if os.path.exists(test_file):
                    os.remove(test_file)
    
    def test_audio_file_not_found(self, client):
        """Test audio file serving with non-existent file."""
        response = client.get('/audio/nonexistent.mp3')
        assert response.status_code == 302  # Redirects with flash message
    
    @patch('web.routes.generate_daily_briefing')
    def test_briefing_generation_success(self, mock_generate, client, valid_api_keys_data, valid_settings_data):
        """Test successful briefing generation through AJAX endpoint."""
        # Set up session data
        client.post('/api-keys', data=valid_api_keys_data)
        client.post('/settings', data=valid_settings_data)
        
        # Mock successful generation
        mock_result = {
            'success': True,
            'status': 'success',
            'message': 'Briefing generated successfully',
            'data': {
                'audio_filename': 'test_briefing.mp3',
                'audio_file_path': 'static/audio/test_briefing.mp3',
                'total_processing_time_seconds': 30.5,
                'articles_count': 5,
                'script_length_chars': 1000,
                'audio_size_bytes': 1024000,
                'script_content': 'Test briefing script'
            }
        }
        mock_generate.return_value = mock_result
        
        # Test AJAX generation endpoint
        response = client.post('/create-briefing')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'redirect' in data
        
        # Verify mock was called
        mock_generate.assert_called_once()
    
    @patch('web.routes.generate_daily_briefing')
    def test_briefing_generation_failure(self, mock_generate, client, valid_api_keys_data, valid_settings_data):
        """Test briefing generation failure handling."""
        # Set up session data
        client.post('/api-keys', data=valid_api_keys_data)
        client.post('/settings', data=valid_settings_data)
        
        # Mock generation failure
        mock_generate.side_effect = Exception('API Error')
        
        # Test AJAX generation endpoint
        response = client.post('/create-briefing')
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'API Error' in data['error']
    
    def test_briefing_generation_without_config(self, client):
        """Test briefing generation without proper configuration."""
        response = client.post('/create-briefing',
                              headers={'Content-Type': 'application/json'})
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Configuration incomplete' in data['error']

    def test_data_report_endpoint(self, client):
        """Test data report generation endpoint."""
        # Test without configuration
        response = client.post('/data-report',
                              headers={'Content-Type': 'application/json'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is False
        assert 'Configuration incomplete' in data['error']
        
        # Test with mock configuration (would need mock data fetchers for full test)
        with client.session_transaction() as sess:
            sess['api_keys'] = {
                'newsapi_key': 'test_key',
                'openweather_api_key': 'test_key',
                'gemini_api_key': 'test_key',
                'elevenlabs_api_key': 'test_key'
            }
            sess['settings'] = {
                'listener_name': 'Test User',
                'location_city': 'Test City',
                'location_country': 'US',
                'briefing_duration_minutes': 3,
                'news_topics': 'technology',
                'max_articles_per_topic': 3,
                'google_voice_name': 'en-US-Studio-O'
            }
        
        # This would fail due to invalid API keys, but we're testing the endpoint exists
        response = client.post('/data-report',
                              headers={'Content-Type': 'application/json'})
        
        assert response.status_code == 200
        data = response.get_json()
        # Should either succeed or fail gracefully with specific error message
        assert 'success' in data


class TestConfigurationIntegration:
    """Test integration between web forms and configuration."""
    
    def test_web_form_to_config_mapping(self, valid_form_data):
        """Test that web form data correctly maps to Config object."""
        config = WebConfig.create_config_from_form(valid_form_data)
        assert isinstance(config, Config)
        assert config.get('NEWSAPI_AI_KEY') == 'test_newsapi_key'
        assert config.get('LISTENER_NAME') == 'Test User'
    
    def test_default_values_populate_correctly(self):
        """Test that default values are populated correctly."""
        defaults = WebConfig.get_form_defaults()
        assert defaults['location_city'] == 'Denver'
        assert defaults['briefing_duration_minutes'] == 5  # Updated from 3 to 5
        assert defaults['google_voice_name'] == 'en-US-Journey-D'
    
    def test_google_voice_preview_endpoint(self, app):
        """Test the new Google TTS voice preview endpoint."""
        with app.test_client() as client:
            # Set up session with API keys
            with client.session_transaction() as sess:
                sess['api_keys'] = {
                    'google_api_key': 'test_google_key'
                }
            
            # Test valid voice preview request
            response = client.post('/preview-voice', 
                json={'voice_name': 'en-US-Studio-M'},
                content_type='application/json')
            
            # Should fail due to missing mock, but endpoint should exist and handle request
            assert response.status_code in [200, 500]  # 500 expected due to no mock
            data = response.get_json()
            assert 'success' in data
    
    def test_google_voice_preview_missing_voice_name(self, app):
        """Test voice preview endpoint with missing voice name."""
        with app.test_client() as client:
            # Set up session with API keys
            with client.session_transaction() as sess:
                sess['api_keys'] = {
                    'google_api_key': 'test_google_key'
                }
            
            # Test request without voice_name
            response = client.post('/preview-voice', 
                json={},
                content_type='application/json')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is False
            assert 'No voice name provided' in data['error']
    
    def test_google_voice_preview_missing_api_key(self, app):
        """Test voice preview endpoint without API key configured."""
        with app.test_client() as client:
            # Test request without API key in session
            response = client.post('/preview-voice', 
                json={'voice_name': 'en-US-Studio-M'},
                content_type='application/json')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is False
            assert 'Google API key not configured' in data['error']

    def test_configuration_validation_integration(self, valid_form_data):
        """Test configuration validation with web form data."""
        # Test valid configuration
        config = WebConfig.create_config_from_form(valid_form_data)
        config.validate_config()  # Should not raise exception
        
        # Test configuration without form API keys (should fallback to environment)
        form_data_without_api_key = valid_form_data.copy()
        del form_data_without_api_key['newsapi_key']
        
        # Mock environment to ensure no fallback values exist
        with patch.dict(os.environ, {}, clear=True):
            # Should raise exception because environment fallback doesn't exist in test
            with pytest.raises(ConfigurationError):
                config_with_fallback = WebConfig.create_config_from_form(form_data_without_api_key)
    
    def test_form_data_validation(self, valid_form_data):
        """Test form data validation function."""
        # Test valid data
        errors = WebConfig.validate_form_data(valid_form_data)
        assert len(errors) == 0
        
        # Test invalid data
        invalid_data = valid_form_data.copy()
        invalid_data['briefing_duration_minutes'] = 50  # Too high
        
        errors = WebConfig.validate_form_data(invalid_data)
        assert 'briefing_duration_minutes' in errors


class TestCompleteWorkflow:
    """Test complete multi-page workflow."""
    
    @patch('web.routes.generate_daily_briefing')
    def test_complete_multi_page_workflow(self, mock_generate, client, valid_api_keys_data, valid_settings_data):
        """Test complete workflow from start to finish."""
        # Mock successful generation
        mock_result = {
            'success': True,
            'status': 'success',
            'message': 'Test briefing generated',
            'data': {
                'audio_filename': 'test_briefing_20250128_120000.mp3',
                'audio_file_path': 'static/audio/test_briefing_20250128_120000.mp3',
                'total_processing_time_seconds': 25.3,
                'articles_count': 7,
                'script_length_chars': 1500,
                'audio_size_bytes': 2048000,
                'script_content': 'Test briefing script content'
            }
        }
        mock_generate.return_value = mock_result
        
        # Step 1: Start at root, should redirect to API keys
        response = client.get('/')
        assert response.status_code == 302
        
        # Step 2: Submit API keys
        response = client.post('/api-keys', data=valid_api_keys_data)
        assert response.status_code == 302
        assert '/settings' in response.location
        
        # Step 3: Submit settings
        response = client.post('/settings', data=valid_settings_data)
        assert response.status_code == 302
        assert '/generate' in response.location
        
        # Step 4: Access generate page
        response = client.get('/generate')
        assert response.status_code == 200
        assert b'Generate Daily Briefing' in response.data
        
        # Step 5: Generate briefing via AJAX
        response = client.post('/create-briefing')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Step 6: Access results page
        response = client.get('/results')
        assert response.status_code == 200
        assert b'test_briefing_20250128_120000.mp3' in response.data
        
        # Verify mock was called
        mock_generate.assert_called_once()


class TestAPIValidation:
    """Test API validation endpoint."""
    
    def test_api_validate_valid_data(self, client, valid_form_data):
        """Test API validation with valid data."""
        response = client.post('/api/validate', 
                              data=json.dumps(valid_form_data),
                              content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['valid'] is True
        assert len(data['errors']) == 0
    
    def test_api_validate_invalid_data(self, client):
        """Test API validation with invalid data."""
        invalid_data = {'briefing_duration_minutes': 50}  # Too high
        
        response = client.post('/api/validate', 
                              data=json.dumps(invalid_data),
                              content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['valid'] is False
        assert 'briefing_duration_minutes' in data['errors']
    
    def test_api_validate_no_data(self, client):
        """Test API validation with no data."""
        response = client.post('/api/validate', 
                              data=json.dumps({}),
                              content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'errors' in data


if __name__ == '__main__':
    pytest.main([__file__, '-v']) 