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
        # Use explicit TTS provider choice, with fallback to auto-detection
        tts_provider = form_data.get('tts_provider', '').lower()
        if not tts_provider:
            # Only auto-detect if no explicit choice was made
            if form_data.get('google_api_key', '').strip():
                tts_provider = 'google'  # Default to Google TTS (user preference)
            elif form_data.get('elevenlabs_api_key', '').strip():
                tts_provider = 'elevenlabs'
            else:
                # Default to google for new installations
                tts_provider = 'google'
        
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
        # Auto-configure news topics for comprehensive coverage (no user selection needed)
        news_topics_str = 'business,entertainment,general,health,science,sports,technology'  # All NewsAPI categories
        
        config_dict = {
            # API Keys
            'NEWSAPI_AI_KEY': form_data['newsapi_key'],
            'OPENWEATHER_API_KEY': form_data['openweather_api_key'],
            'GEMINI_API_KEY': form_data['gemini_api_key'],
            'ELEVENLABS_API_KEY': form_data['elevenlabs_api_key'],
            'GOOGLE_API_KEY': form_data['google_api_key'],
            
            # Personal Settings
            'LISTENER_NAME': form_data.get('listener_name', ''),
            'LOCATION_CITY': form_data.get('location_city', 'Denver'),
            'LOCATION_COUNTRY': form_data.get('location_country', 'US'),
            
            # Content Settings - Simplified for fast iteration
            'BRIEFING_DURATION_MINUTES': str(form_data.get('briefing_duration_minutes', 5)),
            'NEWS_TOPICS': news_topics_str,  # Auto-configured to all categories
            'MAX_ARTICLES_PER_TOPIC': '100',  # Auto-configured for comprehensive news gathering
            
            # Audio Settings
            'TTS_PROVIDER': tts_provider,
            'ELEVENLABS_VOICE_ID': form_data.get('elevenlabs_voice_id', 'default'),
            'GOOGLE_TTS_VOICE_NAME': form_data.get('google_tts_voice_name', 'en-US-Neural2-C'),
            'GOOGLE_TTS_LANGUAGE_CODE': form_data.get('google_tts_language_code', 'en-US'),
            
            # AWS Settings
            'AWS_REGION': form_data.get('aws_region', 'us-east-1'),
            'S3_BUCKET_NAME': form_data.get('s3_bucket_name', ''),
            
            # Customization settings - Simplified UI (some hardcoded for fast iteration)
            'BRIEFING_TONE': form_data.get('briefing_tone', 'professional'),
            'CONTENT_DEPTH': 'balanced',  # Hardcoded - removed from UI
            'KEYWORDS_EXCLUDE': '',  # Hardcoded - removed from UI (let AI handle filtering)
            'VOICE_SPEED': '1.0',  # Hardcoded - removed from UI (users can adjust in player)
            
            # Personalization settings - News & Information Preferences
            'SPECIFIC_INTERESTS': form_data.get('specific_interests', ''),
            # BRIEFING_GOAL removed for UI simplification
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
            # Removed news_topics, max_articles_per_topic - these are now auto-configured
            'google_tts_voice_name': 'en-US-Neural2-C',
            'briefing_duration_minutes': 5,  # Updated from 3 to 5 minutes
            'listener_name': '',
            
            # Simplified settings - removed complex options
            'briefing_tone': 'professional',
            # Removed: content_depth, keywords_exclude, voice_speed - now hardcoded for simplicity
            
            # Smart personalization defaults with environment variable support
            'specific_interests': os.environ.get('DEFAULT_INTERESTS', 'artificial intelligence, machine learning, startup news'),
            # Removed: briefing_goal (hardcoded to 'work' for simplicity)
            'followed_entities': os.environ.get('DEFAULT_ENTITIES', 'tech industry, major tech companies'),
            'hobbies': os.environ.get('DEFAULT_HOBBIES', 'reading tech blogs, podcasts'),
            'favorite_teams_artists': os.environ.get('DEFAULT_TEAMS_ARTISTS', ''),
            'passion_topics': os.environ.get('DEFAULT_PASSION_TOPICS', 'technology trends, innovation'),
            'greeting_preference': os.environ.get('DEFAULT_GREETING', 'Good morning! Here is your essential tech and business update.'),
            'daily_routine_detail': os.environ.get('DEFAULT_ROUTINE', 'I listen during my morning coffee'),
        }
        
        # Add API keys from environment variables for local development
        # These will be empty in production and filled by AWS Secrets Manager
        api_key_defaults = {
            'newsapi_key': os.environ.get('NEWSAPI_AI_KEY', ''),
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
            'newsapi_key': 'NewsAPI.ai Key is required',
            'openweather_api_key': 'OpenWeather API Key is required',
            'gemini_api_key': 'Google Gemini API Key is required'
        }
        
        # TTS provider specific validation
        # Use explicit TTS provider choice, with fallback to auto-detection (same logic as create_config_from_form)
        tts_provider = form_data.get('tts_provider', '').lower()
        if not tts_provider:
            # Only auto-detect if no explicit choice was made
            if form_data.get('google_api_key', '').strip():
                tts_provider = 'google'  # Default to Google TTS (user preference)
            elif form_data.get('elevenlabs_api_key', '').strip():
                tts_provider = 'elevenlabs'
            else:
                # Default to google for new installations
                tts_provider = 'google'
        
        tts_required_fields = {}
        if tts_provider == 'elevenlabs':
            tts_required_fields['elevenlabs_api_key'] = 'ElevenLabs API Key is required when using ElevenLabs TTS'
        elif tts_provider == 'google':
            tts_required_fields['google_api_key'] = 'Google API Key is required when using Google TTS'
        
        required_fields = {**always_required_fields, **tts_required_fields}
        
        for field, error_msg in required_fields.items():
            if not form_data.get(field, '').strip():
                errors[field] = error_msg
        
        # Numeric field validation - removed max_articles_per_topic (now hardcoded)
        
        try:
            duration = int(form_data.get('briefing_duration_minutes', 5))  # Updated default to 5
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