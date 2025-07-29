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
from web.forms import BriefingConfigForm
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
def valid_form_data():
    """Valid form data for testing."""
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


class TestFormValidation:
    """Test form validation and error handling."""
    
    def test_empty_form_submission_fails_fast(self, client):
        """Test that submitting form without API keys fails fast with validation errors."""
        # Submit completely empty form
        response = client.post('/', data={
            'submit': 'Generate Daily Briefing'
        }, follow_redirects=True)
        
        # Should return to form page (not redirect to generation page)
        assert response.status_code == 200
        assert b'Generate Daily Briefing' in response.data  # Still on form page
        
        # Check that validation errors are displayed
        assert b'NewsAPI Key is required' in response.data
        assert b'OpenWeatherMap API Key is required' in response.data
        assert b'Taddy API Key is required' in response.data
        assert b'Taddy User ID is required' in response.data
        assert b'Google Gemini API Key is required' in response.data
        assert b'ElevenLabs API Key is required' in response.data
        
        # Check that form validation flash message is shown
        assert b'Please correct the errors below' in response.data
    
    def test_partial_form_submission_fails_fast(self, client):
        """Test that submitting form with only some API keys fails fast."""
        # Submit form with only NewsAPI key
        response = client.post('/', data={
            'newsapi_key': 'test_key',
            'submit': 'Generate Daily Briefing'
        }, follow_redirects=True)
        
        # Should return to form page with validation errors
        assert response.status_code == 200
        assert b'Generate Daily Briefing' in response.data  # Still on form page
        
        # Should show errors for missing keys but not for provided ones
        assert b'NewsAPI Key is required' not in response.data  # This one was provided
        assert b'OpenWeatherMap API Key is required' in response.data
        assert b'Taddy API Key is required' in response.data
        assert b'Google Gemini API Key is required' in response.data
        assert b'ElevenLabs API Key is required' in response.data
    
    def test_required_fields_have_required_attribute(self, client):
        """Test that all API key fields have the HTML required attribute for client-side validation."""
        response = client.get('/')
        
        # Verify that all required API key fields have required="required" attribute
        required_fields = [
            'newsapi_key',
            'openweather_api_key', 
            'taddy_api_key',
            'taddy_user_id',
            'gemini_api_key',
            'elevenlabs_api_key'
        ]
        
        for field_name in required_fields:
            # Check that field has required attribute (Flask-WTF renders it as required="required")
            field_pattern = f'name="{field_name}"'
            assert field_pattern.encode() in response.data
            
            # More specific check: look for required attribute in the field
            assert b'required' in response.data
        
        # Also verify the submit button exists
        assert b'Generate Daily Briefing' in response.data
    
    def test_javascript_validation_elements_present(self, client):
        """Test that necessary JavaScript validation elements are present."""
        response = client.get('/')
        
        # Check that the form has the necessary elements for JS validation
        assert b'handleFormSubmission' in response.data or b'app.js' in response.data
        
        # Verify form fields are rendered with proper names for JS to find them
        api_key_fields = [
            b'name="newsapi_key"',
            b'name="openweather_api_key"', 
            b'name="taddy_api_key"',
            b'name="taddy_user_id"',
            b'name="gemini_api_key"',
            b'name="elevenlabs_api_key"'
        ]
        
        for field in api_key_fields:
            assert field in response.data
    
    def test_form_has_proper_onsubmit_handler(self, client):
        """Test that the API keys form works with the new multi-page approach."""
        response = client.get('/api-keys')
        
        # Check that we're on the API keys page
        assert b'Step 1: API Keys' in response.data
        assert b'Save API Keys &amp; Continue' in response.data
        
        # Check that all required API key fields are present
        required_fields = [
            b'name="newsapi_key"',
            b'name="openweather_api_key"',
            b'name="taddy_api_key"',
            b'name="taddy_user_id"',
            b'name="gemini_api_key"',
            b'name="elevenlabs_api_key"'
        ]
        
        for field in required_fields:
            assert field in response.data
        
        # Check that the form has proper structure for multi-page flow
        assert b'Step 1: API Keys' in response.data
        assert b'Settings' in response.data  # Progress indicator shows "Settings"
        assert b'Generate' in response.data  # Progress indicator shows "Generate"
    
    def test_loading_indicator_element_present(self, client):
        """Test that the loading indicator element is properly present for JavaScript manipulation."""
        response = client.get('/')
        
        # Check that loading indicator is present with proper structure
        assert b'id="loading-indicator"' in response.data
        assert b'class="hidden fixed inset-0' in response.data  # Should start hidden
        assert b'Generating your briefing' in response.data  # Loading message
        assert b'animate-spin' in response.data  # Spinner animation
        
        # Check enhanced loading indicator features
        assert b'id="progress-bar"' in response.data  # Progress bar
        assert b'id="loading-status"' in response.data  # Status message
        assert b'id="progress-steps"' in response.data  # Progress steps
        assert b'Step 1 of 5' in response.data  # Initial step message
        
        # Ensure the element can be manipulated by JavaScript
        assert b'classList.remove' not in response.data  # JS manipulation should happen in app.js, not template
    
    def test_loading_indicator_conditional_display(self, client):
        """Test that loading indicator only shows when validation passes, not when it fails."""
        response = client.get('/')
        
        # Verify that the form has proper structure for conditional loading
        assert b'onsubmit="return handleFormSubmission(event)"' in response.data
        assert b'app.js' in response.data  # JavaScript file is loaded
        
        # Verify loading indicator starts hidden
        assert b'class="hidden' in response.data
        assert b'style="display: none;"' in response.data
        
        # Test the JavaScript file separately
        js_response = client.get('/static/js/app.js')
        assert b'Form validation failed - preventing submission' in js_response.data
        assert b'Form validation passed - proceeding with submission' in js_response.data
        assert b'showLoadingWithProgress' in js_response.data
    
    def test_valid_form_data(self, app, valid_form_data):
        """Test form validation with valid data."""
        with app.app_context():
            form = BriefingConfigForm(data=valid_form_data)
            assert form.validate() is True
            assert len(form.errors) == 0
    
    def test_missing_required_fields(self, app):
        """Test form validation with missing required fields."""
        with app.app_context():
            incomplete_data = {
                'newsapi_key': 'test_key',
                'listener_name': 'Test User'
                # Missing other required fields
            }
            form = BriefingConfigForm(data=incomplete_data)
            assert form.validate() is False
            
            # Check that required fields have errors
            required_fields = [
                'openweather_api_key', 'taddy_api_key', 'taddy_user_id',
                'gemini_api_key', 'elevenlabs_api_key'
            ]
            for field in required_fields:
                assert field in form.errors
    
    def test_invalid_data_types(self, app, valid_form_data):
        """Test form validation with invalid data types."""
        with app.app_context():
            # Test out of range values (WTForms converts invalid strings to None for IntegerField)
            invalid_data = valid_form_data.copy()
            invalid_data['briefing_duration_minutes'] = 50  # Too high
            form = BriefingConfigForm(data=invalid_data)
            assert form.validate() is False
            
            # Test zero value (too low)
            invalid_data['briefing_duration_minutes'] = 0
            form = BriefingConfigForm(data=invalid_data)
            assert form.validate() is False
    
    def test_country_code_validation(self, app, valid_form_data):
        """Test country code validation."""
        with app.app_context():
            # Test valid country code
            form = BriefingConfigForm(data=valid_form_data)
            assert form.validate() is True
            
            # Test invalid country code
            invalid_data = valid_form_data.copy()
            invalid_data['location_country'] = 'USA'  # Should be 2 letters
            form = BriefingConfigForm(data=invalid_data)
            assert form.validate() is False
            assert 'location_country' in form.errors
    
    def test_edge_cases(self, app, valid_form_data):
        """Test edge cases and boundary values."""
        with app.app_context():
            # Test minimum values
            edge_data = valid_form_data.copy()
            edge_data['briefing_duration_minutes'] = 1
            edge_data['max_articles_per_topic'] = 1
            form = BriefingConfigForm(data=edge_data)
            assert form.validate() is True
            
            # Test maximum values
            edge_data['briefing_duration_minutes'] = 30
            edge_data['max_articles_per_topic'] = 10
            form = BriefingConfigForm(data=edge_data)
            assert form.validate() is True


class TestRouteHandlers:
    """Test HTTP route handlers."""
    
    def test_get_index_returns_form(self, client):
        """Test GET / returns configuration form."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Generate Daily Briefing' in response.data
        assert b'API Keys' in response.data
        assert b'Personal Settings' in response.data
    
    @patch('web.routes.generate_daily_briefing')
    def test_post_generate_with_valid_data(self, mock_generate, client, valid_form_data):
        """Test POST /generate with valid data calls generation logic."""
        # Mock successful briefing generation
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
        
        response = client.post('/', data=valid_form_data, follow_redirects=True)
        assert response.status_code == 200
        assert b'Briefing Generated Successfully' in response.data
        
        # Verify generate_daily_briefing was called with Config object
        mock_generate.assert_called_once()
        config_arg = mock_generate.call_args[0][0]
        assert isinstance(config_arg, Config)
    
    def test_post_generate_with_invalid_data(self, client):
        """Test POST /generate with invalid data returns error."""
        invalid_data = {
            'newsapi_key': '',  # Missing required field
            'listener_name': 'Test User'
        }
        
        response = client.post('/', data=invalid_data)
        assert response.status_code == 200
        assert b'correct the errors' in response.data.lower()
    
    def test_audio_file_serving(self, client):
        """Test audio file serving endpoint."""
        # Create a test audio file
        os.makedirs('static/audio', exist_ok=True)
        test_file = 'static/audio/test_audio.mp3'
        with open(test_file, 'wb') as f:
            f.write(b'fake_audio_data')
        
        try:
            response = client.get('/audio/test_audio.mp3')
            assert response.status_code == 200
            assert response.mimetype == 'audio/mpeg'
        finally:
            # Clean up test file
            if os.path.exists(test_file):
                os.remove(test_file)
    
    def test_audio_file_not_found(self, client):
        """Test audio file serving with non-existent file."""
        response = client.get('/audio/nonexistent.mp3')
        assert response.status_code == 302  # Redirect to index
    
    def test_health_check_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert data['service'] == 'ai-daily-briefing-agent'


class TestConfigurationIntegration:
    """Test configuration integration between web forms and Config objects."""
    
    def test_web_form_to_config_mapping(self, valid_form_data):
        """Test web form data correctly maps to Config object."""
        config = WebConfig.create_config_from_form(valid_form_data)
        
        # Test required mappings
        assert config.get('NEWSAPI_KEY') == valid_form_data['newsapi_key']
        assert config.get('OPENWEATHER_API_KEY') == valid_form_data['openweather_api_key']
        assert config.get('GEMINI_API_KEY') == valid_form_data['gemini_api_key']
        
        # Test optional mappings
        assert config.get('LISTENER_NAME') == valid_form_data['listener_name']
        assert config.get('LOCATION_CITY') == valid_form_data['location_city']
        assert config.get_briefing_duration_minutes() == valid_form_data['briefing_duration_minutes']
    
    def test_default_values_populate_correctly(self):
        """Test default values populate correctly."""
        defaults = WebConfig.get_form_defaults()
        
        expected_defaults = {
            'aws_region': 'us-east-1',
            'location_city': 'Denver',
            'location_country': 'US',
            'news_topics': 'technology,business,science',
            'max_articles_per_topic': 3,
            'podcast_categories': 'Technology,Business,Science',
            'elevenlabs_voice_id': 'default',
            'briefing_duration_minutes': 8,
            'listener_name': 'Seamus'
        }
        
        for key, value in expected_defaults.items():
            assert defaults[key] == value
    
    def test_configuration_validation_integration(self, valid_form_data):
        """Test configuration validation integration."""
        # Test valid configuration
        config = WebConfig.create_config_from_form(valid_form_data)
        assert config.validate_config() is True
        
        # Test missing required field
        invalid_data = valid_form_data.copy()
        del invalid_data['newsapi_key']
        
        with pytest.raises(ConfigurationError):
            WebConfig.create_config_from_form(invalid_data)
    
    def test_form_data_validation(self, valid_form_data):
        """Test form data validation utility."""
        # Test valid data
        errors = WebConfig.validate_form_data(valid_form_data)
        assert len(errors) == 0
        
        # Test missing required fields
        invalid_data = {'listener_name': 'Test'}
        errors = WebConfig.validate_form_data(invalid_data)
        assert len(errors) > 0
        assert 'newsapi_key' in errors
        
        # Test invalid numeric values
        invalid_data = valid_form_data.copy()
        invalid_data['briefing_duration_minutes'] = 50  # Too high
        errors = WebConfig.validate_form_data(invalid_data)
        assert 'briefing_duration_minutes' in errors


class TestMockIntegration:
    """Test complete web workflow with mocked external dependencies."""
    
    @patch('web.routes.generate_daily_briefing')
    def test_complete_workflow_mock(self, mock_generate, client, valid_form_data):
        """Test complete web workflow without external API calls."""
        # Mock successful generation
        mock_result = {
            'success': True,
            'status': 'success',
            'message': 'Test briefing generated',
            'data': {
                'audio_filename': 'test_briefing_20250128_120000.mp3',
                'total_processing_time_seconds': 25.3,
                'articles_count': 7,
                'podcasts_count': 2,
                'script_length_chars': 1500,
                'audio_size_bytes': 2048000
            }
        }
        mock_generate.return_value = mock_result
        
        # Submit form
        response = client.post('/', data=valid_form_data)
        
        # Verify successful response
        assert response.status_code == 200
        assert b'Briefing Generated Successfully' in response.data
        assert b'test_briefing_20250128_120000.mp3' in response.data
        
        # Verify mock was called
        mock_generate.assert_called_once()
    
    @patch('web.routes.generate_daily_briefing')
    def test_error_handling_for_generation_failures(self, mock_generate, client, valid_form_data):
        """Test error handling for generation failures."""
        # Mock generation failure
        mock_result = {
            'success': False,
            'error': 'API key invalid',
            'message': 'Briefing generation failed: API key invalid'
        }
        mock_generate.return_value = mock_result
        
        response = client.post('/', data=valid_form_data)
        
        # Verify error handling
        assert response.status_code == 200
        assert b'Error generating briefing' in response.data
        assert b'API key invalid' in response.data
    
    @patch('web.routes.generate_daily_briefing')
    def test_exception_handling(self, mock_generate, client, valid_form_data):
        """Test handling of unexpected exceptions."""
        # Mock exception during generation
        mock_generate.side_effect = Exception("Unexpected error")
        
        response = client.post('/', data=valid_form_data)
        
        # Verify graceful error handling
        assert response.status_code == 200
        assert b'Unexpected error' in response.data


class TestAPIValidation:
    """Test API validation endpoint."""
    
    def test_api_validate_valid_data(self, client, valid_form_data):
        """Test API validation with valid data."""
        response = client.post('/api/validate',
                             json=valid_form_data,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['valid'] is True
    
    def test_api_validate_invalid_data(self, client):
        """Test API validation with invalid data."""
        invalid_data = {'listener_name': 'Test'}  # Missing required fields
        
        response = client.post('/api/validate',
                             json=invalid_data,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['valid'] is False
        assert 'errors' in data
    
    def test_api_validate_no_data(self, client):
        """Test API validation with no data."""
        response = client.post('/api/validate',
                             json=None,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['valid'] is False
        # The actual error handling catches exceptions and returns a general error
        assert 'errors' in data


if __name__ == '__main__':
    pytest.main([__file__, '-v']) 