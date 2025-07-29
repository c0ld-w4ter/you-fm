"""
Web configuration module for AI Daily Briefing Agent.

This module handles mapping web form data to configuration objects,
replacing the environment variable dependency for web-based configuration.
"""

import logging
from typing import Dict, Any, Optional
from config import Config, ConfigurationError

logger = logging.getLogger(__name__)


class WebConfig:
    """
    Configuration manager that creates Config objects from web form data.
    
    This class serves as the bridge between web forms and the core Config class.
    For Milestone 5: This will be extended to support advanced customization options
    including content filtering, briefing style preferences, and enhanced audio settings.
    """
    
    @staticmethod
    def create_config_from_form(form_data: Dict[str, Any]) -> Config:
        """
        Create a Config object from web form data.
        
        Args:
            form_data: Dictionary containing form field values
            
        Returns:
            Initialized Config object
            
        Raises:
            ConfigurationError: If required fields are missing or invalid
        """
        logger.info("Creating configuration from web form data...")
        
        # Validate required fields
        required_fields = [
            'newsapi_key',
            'openweather_api_key', 
            'taddy_api_key',
            'taddy_user_id',
            'gemini_api_key',
            'elevenlabs_api_key'
        ]
        
        missing_fields = []
        for field in required_fields:
            if not form_data.get(field, '').strip():
                missing_fields.append(field)
        
        if missing_fields:
            error_msg = f"Missing required fields: {', '.join(missing_fields)}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg)
        
        # Create configuration dictionary in the format expected by Config
        config_dict = {
            # Required API keys
            'NEWSAPI_KEY': form_data['newsapi_key'].strip(),
            'OPENWEATHER_API_KEY': form_data['openweather_api_key'].strip(),
            'TADDY_API_KEY': form_data['taddy_api_key'].strip(),
            'TADDY_USER_ID': form_data['taddy_user_id'].strip(),
            'GEMINI_API_KEY': form_data['gemini_api_key'].strip(),
            'ELEVENLABS_API_KEY': form_data['elevenlabs_api_key'].strip(),
            
            # Optional settings with defaults
            'AWS_REGION': form_data.get('aws_region', 'us-east-1').strip(),
            'LOCATION_CITY': form_data.get('location_city', 'Denver').strip(),
            'LOCATION_COUNTRY': form_data.get('location_country', 'US').strip(),
            'NEWS_TOPICS': form_data.get('news_topics', 'technology,business,science').strip(),
            'MAX_ARTICLES_PER_TOPIC': str(form_data.get('max_articles_per_topic', 3)),
            'PODCAST_CATEGORIES': form_data.get('podcast_categories', 'Technology,Business,Science').strip(),
            'ELEVENLABS_VOICE_ID': form_data.get('elevenlabs_voice_id', 'default').strip(),
            'BRIEFING_DURATION_MINUTES': str(form_data.get('briefing_duration_minutes', 8)),
            'LISTENER_NAME': form_data.get('listener_name', 'Seamus').strip(),
        }
        
        # Create Config object with custom data
        config = Config.from_dict(config_dict)
        
        logger.info("✓ Configuration created successfully from web form")
        return config
    
    @staticmethod
    def get_form_defaults() -> Dict[str, Any]:
        """
        Get default values for web form fields.
        
        Returns:
            Dictionary of default form values
        """
        return {
            'aws_region': 'us-east-1',
            'location_city': 'Denver',
            'location_country': 'US',
            'news_topics': 'technology,business,science',
            'max_articles_per_topic': 3,
            'podcast_categories': 'Technology,Business,Science',
            'elevenlabs_voice_id': 'default',
            'briefing_duration_minutes': 8,
            'listener_name': 'Seamus',
        }
    
    @staticmethod
    def validate_form_data(form_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Validate form data and return any validation errors.
        
        Args:
            form_data: Dictionary containing form field values
            
        Returns:
            Dictionary of field names to error messages (empty if valid)
        """
        errors = {}
        
        # Required field validation
        required_fields = {
            'newsapi_key': 'NewsAPI Key is required',
            'openweather_api_key': 'OpenWeather API Key is required',
            'taddy_api_key': 'Taddy API Key is required',
            'taddy_user_id': 'Taddy User ID is required',
            'gemini_api_key': 'Google Gemini API Key is required',
            'elevenlabs_api_key': 'ElevenLabs API Key is required'
        }
        
        for field, error_msg in required_fields.items():
            if not form_data.get(field, '').strip():
                errors[field] = error_msg
        
        # Numeric field validation
        try:
            max_articles = int(form_data.get('max_articles_per_topic', 3))
            if max_articles < 1 or max_articles > 10:
                errors['max_articles_per_topic'] = 'Must be between 1 and 10'
        except (ValueError, TypeError):
            errors['max_articles_per_topic'] = 'Must be a valid number'
        
        try:
            duration = int(form_data.get('briefing_duration_minutes', 8))
            if duration < 1 or duration > 30:
                errors['briefing_duration_minutes'] = 'Must be between 1 and 30 minutes'
        except (ValueError, TypeError):
            errors['briefing_duration_minutes'] = 'Must be a valid number'
        
        # String length validation
        if len(form_data.get('listener_name', '')) > 50:
            errors['listener_name'] = 'Name too long (maximum 50 characters)'
        
        if len(form_data.get('location_city', '')) > 100:
            errors['location_city'] = 'City name too long (maximum 100 characters)'
        
        return errors 