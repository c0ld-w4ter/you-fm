"""
Configuration module for AI Daily Briefing Agent.

This module handles loading configuration from environment variables during development
and will be extended to support AWS Secrets Manager in production (Milestone 4).
"""

import os
import logging
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when a required configuration value is missing or invalid."""
    pass


class Config:
    """Configuration manager for the AI Daily Briefing Agent."""
    
    # Required environment variables for all milestones
    REQUIRED_VARS = [
        'NEWSAPI_KEY',           # NewsAPI.org API key
        'OPENWEATHER_API_KEY',   # OpenWeatherMap API key
        'TADDY_API_KEY',         # Taddy Podcast API key
        'TADDY_USER_ID',         # Taddy User ID
        'GEMINI_API_KEY',        # Google Gemini API key
        'ELEVENLABS_API_KEY',    # ElevenLabs API key
        'GOOGLE_DRIVE_FOLDER_ID', # Target folder ID in Google Drive
    ]
    
    # Optional configuration with defaults
    DEFAULT_VALUES = {
        'AWS_REGION': 'us-east-1',
        'LOCATION_CITY': 'Denver',
        'LOCATION_COUNTRY': 'US',
        'NEWS_TOPICS': 'technology,business,science',
        'MAX_ARTICLES_PER_TOPIC': '3',
        'PODCAST_CATEGORIES': 'Technology,Business,Science',
        'ELEVENLABS_VOICE_ID': 'default',
    }
    
    def __init__(self):
        """Initialize configuration by loading from environment variables."""
        self._config: Dict[str, str] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from environment variables."""
        logger.info("Loading configuration from environment variables...")
        
        # Load required variables
        missing_vars = []
        for var in self.REQUIRED_VARS:
            value = os.environ.get(var)
            if value:
                self._config[var] = value
                logger.info(f"✓ Loaded {var}")
            else:
                missing_vars.append(var)
                logger.warning(f"✗ Missing required variable: {var}")
        
        # Load optional variables with defaults
        for var, default in self.DEFAULT_VALUES.items():
            value = os.environ.get(var, default)
            self._config[var] = value
            logger.info(f"✓ Loaded {var} = {value}")
        
        # Raise error if any required variables are missing
        if missing_vars:
            error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg)
        
        logger.info("✓ Configuration loaded successfully")
    
    def get(self, key: str, default: Optional[str] = None) -> str:
        """
        Get a configuration value.
        
        Args:
            key: The configuration key to retrieve
            default: Default value if key is not found
            
        Returns:
            The configuration value
            
        Raises:
            ConfigurationError: If key is not found and no default provided
        """
        if key in self._config:
            return self._config[key]
        
        if default is not None:
            return default
            
        raise ConfigurationError(f"Configuration key '{key}' not found")
    
    def get_news_topics(self) -> list[str]:
        """Get news topics as a list."""
        topics_str = self.get('NEWS_TOPICS')
        return [topic.strip() for topic in topics_str.split(',')]
    
    def get_podcast_categories(self) -> list[str]:
        """Get podcast categories as a list."""
        categories_str = self.get('PODCAST_CATEGORIES')
        return [category.strip() for category in categories_str.split(',')]
    
    def get_max_articles_per_topic(self) -> int:
        """Get maximum articles per topic as integer."""
        return int(self.get('MAX_ARTICLES_PER_TOPIC'))
    
    def is_aws_environment(self) -> bool:
        """
        Check if running in AWS environment.
        
        This will be used in Milestone 4 to determine whether to use
        AWS Secrets Manager instead of environment variables.
        """
        return os.environ.get('AWS_EXECUTION_ENV') is not None
    
    def validate_config(self) -> bool:
        """
        Validate that all required configuration is present and valid.
        
        Returns:
            True if configuration is valid
            
        Raises:
            ConfigurationError: If configuration is invalid
        """
        try:
            # Validate integer values
            self.get_max_articles_per_topic()
            
            # Check that lists are not empty
            if not self.get_news_topics():
                raise ConfigurationError("NEWS_TOPICS cannot be empty")
            
            if not self.get_podcast_categories():
                raise ConfigurationError("PODCAST_CATEGORIES cannot be empty")
            
            logger.info("✓ Configuration validation passed")
            return True
        
        except (ValueError, ConfigurationError) as e:
            logger.error(f"Configuration validation failed: {e}")
            raise ConfigurationError(f"Invalid configuration: {e}")


# Global configuration instance
# This will be initialized when the module is imported
try:
    config = Config()
except ConfigurationError as e:
    # In development, we might not have all environment variables set yet
    # Log the error but don't crash the module import
    logger.warning(f"Configuration not fully loaded: {e}")
    config = None


def get_config() -> Config:
    """
    Get the global configuration instance.
    
    Returns:
        The global Config instance
        
    Raises:
        ConfigurationError: If configuration is not properly initialized
    """
    global config
    if config is None:
        config = Config()
    return config 