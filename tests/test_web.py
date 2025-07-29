"""
Unit tests for AI Daily Briefing Agent web interface.

Tests the Flask web application functionality including form validation,
route handlers, and configuration integration.
"""

import pytest
import json
import os
from unittest.mock import Mock, patch, MagicMock

from app import create_app
from web.forms import BriefingConfigForm, APIKeysForm, SettingsForm
from config_web import WebConfig
from config import Config, ConfigurationError


@pytest.fixture
def app():
    """Create test Flask application."""
    app = create_app('testing')
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
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
        'taddy_api_key': 'test_taddy_key',
        'taddy_user_id': 'test_taddy_user',
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
        'news_topics': 'technology,business',
        'max_articles_per_topic': 3,
        'podcast_categories': 'Technology,Business',
        'elevenlabs_voice_id': 'default',
        'aws_region': 'us-east-1'
    }


@pytest.fixture
def valid_form_data():
    """Valid form data for testing (legacy fixture for compatibility)."""
    return {
        'newsapi_key': 'test_newsapi_key',
        'openweather_api_key': 'test_openweather_key',
        'taddy_api_key': 'test_taddy_key',
        'taddy_user_id': 'test_taddy_user',
        'gemini_api_key': 'test_gemini_key',
        'elevenlabs_api_key': 'test_elevenlabs_key',
        'listener_name': 'Test User',
        'location_city': 'Denver',
        'location_country': 'US',
        'briefing_duration_minutes': 5,
        'news_topics': 'technology,business',
        'max_articles_per_topic': 3,
        'podcast_categories': 'Technology,Business',
        'elevenlabs_voice_id': 'default',
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
        assert b'name="taddy_api_key"' in response.data
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
        assert b'Taddy API Key is required' in response.data
    
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
                'taddy_api_key': 'test_key',
                'taddy_user_id': 'test_user',
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
                'news_topics': 'tech',
                'max_articles_per_topic': 3,
                'podcast_categories': 'Tech',
                'elevenlabs_voice_id': 'default'
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
        # Create a dummy audio file for testing
        audio_dir = 'static/audio'
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
                'podcasts_count': 3,
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
        response = client.post('/create-briefing')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Configuration incomplete' in data['error']


class TestConfigurationIntegration:
    """Test integration between web forms and configuration."""
    
    def test_web_form_to_config_mapping(self, valid_form_data):
        """Test that web form data correctly maps to Config object."""
        config = WebConfig.create_config_from_form(valid_form_data)
        assert isinstance(config, Config)
        assert config.get('NEWSAPI_KEY') == 'test_newsapi_key'
        assert config.get('LISTENER_NAME') == 'Test User'
    
    def test_default_values_populate_correctly(self):
        """Test that default values are populated correctly."""
        defaults = WebConfig.get_form_defaults()
        assert defaults['location_city'] == 'Denver'
        assert defaults['briefing_duration_minutes'] == 8
        assert defaults['elevenlabs_voice_id'] == 'default'
    
    def test_configuration_validation_integration(self, valid_form_data):
        """Test configuration validation with web form data."""
        # Test valid configuration
        config = WebConfig.create_config_from_form(valid_form_data)
        config.validate_config()  # Should not raise exception
        
        # Test invalid configuration
        invalid_data = valid_form_data.copy()
        del invalid_data['newsapi_key']
        
        with pytest.raises(ConfigurationError):
            WebConfig.create_config_from_form(invalid_data)
    
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
                'podcasts_count': 2,
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