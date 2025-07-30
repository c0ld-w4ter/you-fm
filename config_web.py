"""
Web configuration module for AI Daily Briefing Agent.

This module handles mapping web form data to configuration objects,
replacing the environment variable dependency for web-based configuration.
"""

import os
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
        
        # Convert checkbox lists to comma-separated strings
        news_topics = form_data.get('news_topics', ['technology', 'business', 'science'])
        if isinstance(news_topics, list):
            news_topics_str = ','.join(news_topics)
        else:
            news_topics_str = news_topics or 'technology,business,science'
            
        podcast_categories = form_data.get('podcast_categories', ['Technology', 'Business', 'Science'])
        if isinstance(podcast_categories, list):
            podcast_categories_str = ','.join(podcast_categories)
        else:
            podcast_categories_str = podcast_categories or 'Technology,Business,Science'
        
        # Create configuration dictionary in the format expected by Config
        config_dict = {
            # Required API keys
            'NEWSAPI_KEY': form_data['newsapi_key'],
            'OPENWEATHER_API_KEY': form_data['openweather_api_key'],
            'TADDY_API_KEY': form_data['taddy_api_key'],
            'TADDY_USER_ID': form_data['taddy_user_id'],
            'GEMINI_API_KEY': form_data['gemini_api_key'],
            'ELEVENLABS_API_KEY': form_data['elevenlabs_api_key'],
            
            # Optional configuration
            'AWS_REGION': form_data.get('aws_region', 'us-east-1'),
            'LOCATION_CITY': form_data.get('location_city', 'Denver'),
            'LOCATION_COUNTRY': form_data.get('location_country', 'US'),
            'NEWS_TOPICS': news_topics_str,
            'MAX_ARTICLES_PER_TOPIC': str(form_data.get('max_articles_per_topic', 3)),
            'PODCAST_CATEGORIES': podcast_categories_str,
            'ELEVENLABS_VOICE_ID': form_data.get('elevenlabs_voice_id', 'default'),
            'BRIEFING_DURATION_MINUTES': str(form_data.get('briefing_duration_minutes', 8)),
            'LISTENER_NAME': form_data.get('listener_name', 'Seamus'),
            
            # Advanced customization options (New for Milestone 5)
            'BRIEFING_TONE': form_data.get('briefing_tone', 'professional'),
            'CONTENT_DEPTH': form_data.get('content_depth', 'balanced'),
            'KEYWORDS_EXCLUDE': form_data.get('keywords_exclude', ''),
            'VOICE_SPEED': form_data.get('voice_speed', '1.0'),
        }
        
        logger.info("Web form data mapped to configuration successfully")
        return Config(config_dict)
    
    @staticmethod
    def get_form_defaults() -> Dict[str, Any]:
        """
        Get default values for form fields.
        For local development, this includes API keys from environment variables.
        
        Returns:
            Dictionary of default form values
        """
        defaults = {
            'aws_region': 'us-east-1',
            'location_city': 'Denver',
            'location_country': 'US',
            'news_topics': ['technology', 'business', 'science'],  # Changed to list for checkboxes
            'max_articles_per_topic': 3,
            'podcast_categories': ['Technology', 'Business', 'Science'],  # Changed to list for checkboxes
            'elevenlabs_voice_id': 'default',
            'briefing_duration_minutes': 8,
            'listener_name': 'Seamus',
            
            # Advanced defaults (New for Milestone 5)
            'briefing_tone': 'professional',
            'content_depth': 'balanced',
            'keywords_exclude': '',
            'voice_speed': '1.0',
        }
        
        # Add API keys from environment variables for local development
        # These will be empty in production and filled by AWS Secrets Manager
        api_key_defaults = {
            'newsapi_key': os.environ.get('NEWSAPI_KEY', ''),
            'openweather_api_key': os.environ.get('OPENWEATHER_API_KEY', ''),
            'taddy_api_key': os.environ.get('TADDY_API_KEY', ''),
            'taddy_user_id': os.environ.get('TADDY_USER_ID', ''),
            'gemini_api_key': os.environ.get('GEMINI_API_KEY', ''),
            'elevenlabs_api_key': os.environ.get('ELEVENLABS_API_KEY', ''),
        }
        
        defaults.update(api_key_defaults)
        return defaults
    
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