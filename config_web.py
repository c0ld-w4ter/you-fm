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
        logger.debug(f"Form data keys available: {list(form_data.keys())}")
        
        # Validate required fields with environment variable fallback
        always_required_fields = [
            'newsapi_key',
            'openweather_api_key',
            'gemini_api_key'
        ]
        
        # TTS provider specific requirements
        # Auto-detect TTS provider if not explicitly set
        tts_provider = form_data.get('tts_provider', '').lower()
        if not tts_provider:
            # Auto-detect based on which API key is provided
            if form_data.get('elevenlabs_api_key', '').strip():
                tts_provider = 'elevenlabs'
            elif form_data.get('google_api_key', '').strip():
                tts_provider = 'google'
            else:
                # Default to elevenlabs for backward compatibility
                tts_provider = 'elevenlabs'
        
        tts_required_fields = []
        if tts_provider == 'elevenlabs':
            tts_required_fields = ['elevenlabs_api_key']
        elif tts_provider == 'google':
            tts_required_fields = ['google_api_key']
        
        required_fields = always_required_fields + tts_required_fields
        
        missing_fields = []
        for field in required_fields:
            form_value = form_data.get(field, '').strip()
            env_key = field.upper().replace('_KEY', '_KEY')
            env_value = os.environ.get(env_key, '').strip()
            
            if not form_value and not env_value:
                missing_fields.append(field)
            elif not form_value and env_value:
                # Use environment variable as fallback
                form_data[field] = env_value
                logger.info(f"Using environment variable fallback for {field}")
        
        # Always ensure we have values for both TTS providers (even if empty) for config creation
        for tts_field in ['elevenlabs_api_key', 'google_api_key']:
            if tts_field not in form_data:
                form_data[tts_field] = os.environ.get(tts_field.upper().replace('_KEY', '_KEY'), '')
        
        if missing_fields:
            error_msg = f"Missing required fields: {', '.join(missing_fields)}"
            logger.error(error_msg)
            logger.error(f"Available form data: {[k for k, v in form_data.items() if v]}")
            raise ConfigurationError(error_msg)
        
        # Convert form data to config dictionary
        # Handle news topics (convert list to comma-separated string)
        news_topics = form_data.get('news_topics', ['technology', 'business', 'science'])
        if isinstance(news_topics, list):
            news_topics_str = ','.join(news_topics)
        else:
            news_topics_str = news_topics or 'technology,business,science'
        
        config_dict = {
            # API Keys
            'NEWSAPI_KEY': form_data['newsapi_key'],
            'OPENWEATHER_API_KEY': form_data['openweather_api_key'],
            'GEMINI_API_KEY': form_data['gemini_api_key'],
            'ELEVENLABS_API_KEY': form_data['elevenlabs_api_key'],
            'GOOGLE_API_KEY': form_data['google_api_key'],
            
            # Personal Settings
            'LISTENER_NAME': form_data.get('listener_name', ''),
            'LOCATION_CITY': form_data.get('location_city', 'Denver'),
            'LOCATION_COUNTRY': form_data.get('location_country', 'US'),
            
            # Content Settings
            'BRIEFING_DURATION_MINUTES': str(form_data.get('briefing_duration_minutes', 3)),
            'NEWS_TOPICS': news_topics_str,
            'MAX_ARTICLES_PER_TOPIC': str(form_data.get('max_articles_per_topic', 3)),
            
            # Audio Settings
            'TTS_PROVIDER': tts_provider,
            'ELEVENLABS_VOICE_ID': form_data.get('elevenlabs_voice_id', 'default'),
            'GOOGLE_TTS_VOICE_NAME': form_data.get('google_tts_voice_name', 'en-US-Journey-D'),
            'GOOGLE_TTS_LANGUAGE_CODE': form_data.get('google_tts_language_code', 'en-US'),
            
            # AWS Settings
            'AWS_REGION': form_data.get('aws_region', 'us-east-1'),
            'S3_BUCKET_NAME': form_data.get('s3_bucket_name', ''),
            
            # Advanced customization settings (Milestone 5)
            'BRIEFING_TONE': form_data.get('briefing_tone', 'professional'),
            'CONTENT_DEPTH': form_data.get('content_depth', 'balanced'),
            'KEYWORDS_EXCLUDE': form_data.get('keywords_exclude', ''),
            'VOICE_SPEED': str(form_data.get('voice_speed', '1.0')),
            
            # Personalization settings - News & Information Preferences
            'SPECIFIC_INTERESTS': form_data.get('specific_interests', ''),
            'BRIEFING_GOAL': form_data.get('briefing_goal', ''),
            'FOLLOWED_ENTITIES': form_data.get('followed_entities', ''),
            
            # Personalization settings - Hobbies & Personal Interests
            'HOBBIES': form_data.get('hobbies', ''),
            'FAVORITE_TEAMS_ARTISTS': form_data.get('favorite_teams_artists', ''),
            'PASSION_TOPICS': form_data.get('passion_topics', ''),
            
            # Personalization settings - Personal Quirks & Style
            'GREETING_PREFERENCE': form_data.get('greeting_preference', ''),
            'DAILY_ROUTINE_DETAIL': form_data.get('daily_routine_detail', ''),
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
            'news_topics': ['technology', 'business', 'science'],  # Real NewsAPI categories only
            'max_articles_per_topic': 3,  # Reasonable default
            'elevenlabs_voice_id': 'default',
            'briefing_duration_minutes': 3,
            'listener_name': '',
            
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
            'gemini_api_key': os.environ.get('GEMINI_API_KEY', ''),
            'elevenlabs_api_key': os.environ.get('ELEVENLABS_API_KEY', ''),
            'google_api_key': os.environ.get('GOOGLE_API_KEY', ''),
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
        always_required_fields = {
            'newsapi_key': 'NewsAPI Key is required',
            'openweather_api_key': 'OpenWeather API Key is required',
            'gemini_api_key': 'Google Gemini API Key is required'
        }
        
        # TTS provider specific validation
        # Auto-detect TTS provider if not explicitly set (same logic as create_config_from_form)
        tts_provider = form_data.get('tts_provider', '').lower()
        if not tts_provider:
            # Auto-detect based on which API key is provided
            if form_data.get('elevenlabs_api_key', '').strip():
                tts_provider = 'elevenlabs'
            elif form_data.get('google_api_key', '').strip():
                tts_provider = 'google'
            else:
                # Default to elevenlabs for backward compatibility
                tts_provider = 'elevenlabs'
        
        tts_required_fields = {}
        if tts_provider == 'elevenlabs':
            tts_required_fields['elevenlabs_api_key'] = 'ElevenLabs API Key is required when using ElevenLabs TTS'
        elif tts_provider == 'google':
            tts_required_fields['google_api_key'] = 'Google API Key is required when using Google TTS'
        
        required_fields = {**always_required_fields, **tts_required_fields}
        
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