"""
Configuration module for AI Daily Briefing Agent.

This module handles loading configuration from environment variables during development
and will be extended to support AWS Secrets Manager in production (Milestone 4).
"""

import os
import logging
from typing import Optional, Dict, Any

# Load .env file for local development
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file if it exists
except ImportError:
    pass  # dotenv not required in production

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when a required configuration value is missing or invalid."""
    pass


class Config:
    """Configuration manager for the AI Daily Briefing Agent."""
    
    # Required configuration keys
    REQUIRED_KEYS = [
        'NEWSAPI_KEY',               # NewsAPI API key
        'OPENWEATHER_API_KEY',       # OpenWeatherMap API key
        'GEMINI_API_KEY',            # Google Gemini API key
        'ELEVENLABS_API_KEY',        # ElevenLabs API key
    ]
    
    # Optional configuration with defaults
    DEFAULT_CONFIG = {
        # Personal settings
        'LISTENER_NAME': '',  # Empty string for no personalization
        'LOCATION_CITY': 'Denver',
        'LOCATION_COUNTRY': 'US',
        
        # Content settings
        'BRIEFING_DURATION_MINUTES': '3',
        'NEWS_TOPICS': 'technology,business,science',  # Default NewsAPI categories
        'MAX_ARTICLES_PER_TOPIC': '3',
        
        # Audio settings
        'ELEVENLABS_VOICE_ID': 'default',  # Use default voice
        
        # AWS settings (optional for S3 upload)
        'AWS_REGION': 'us-east-1',
        'S3_BUCKET_NAME': '',
        
        # Advanced customization settings (Milestone 5)
        'BRIEFING_TONE': 'professional',  # professional, casual, energetic
        'CONTENT_DEPTH': 'balanced',       # headlines, balanced, detailed
        'KEYWORDS_EXCLUDE': '',            # Comma-separated keywords to filter out
        'VOICE_SPEED': '1.0',              # 0.8 (slow), 1.0 (normal), 1.2 (fast)
    }
    
    def __init__(self, config_dict: Optional[Dict[str, str]] = None):
        """
        Initialize configuration from environment variables or provided dictionary.
        
        Args:
            config_dict: Optional dictionary of configuration values.
                        If None, loads from environment variables.
        """
        self._config: Dict[str, str] = {}
        if config_dict is not None:
            self._load_from_dict(config_dict)
        else:
            self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from environment variables."""
        logger.info("Loading configuration from environment variables...")
        
        # Load required variables
        missing_vars = []
        for var in self.REQUIRED_KEYS:
            value = os.environ.get(var)
            if value:
                self._config[var] = value
                logger.info(f"✓ Loaded {var}")
            else:
                missing_vars.append(var)
                logger.warning(f"✗ Missing required variable: {var}")
        
        # Load optional variables with defaults
        for var, default in self.DEFAULT_CONFIG.items():
            value = os.environ.get(var, default)
            self._config[var] = value
            logger.info(f"✓ Loaded {var} = {value}")
        
        # Raise error if any required variables are missing
        if missing_vars:
            error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg)
        
        logger.info("✓ Configuration loaded successfully")
    
    def _load_from_dict(self, config_dict: Dict[str, str]) -> None:
        """
        Load configuration from provided dictionary.
        
        Args:
            config_dict: Dictionary containing configuration values
        """
        logger.info("Loading configuration from provided dictionary...")
        
        # Validate required variables
        missing_vars = []
        for var in self.REQUIRED_KEYS:
            if var in config_dict and config_dict[var]:
                self._config[var] = config_dict[var]
                logger.info(f"✓ Loaded {var}")
            else:
                missing_vars.append(var)
                logger.warning(f"✗ Missing required variable: {var}")
        
        # Load optional variables with defaults
        for var, default in self.DEFAULT_CONFIG.items():
            value = config_dict.get(var, default)
            self._config[var] = value
            logger.info(f"✓ Loaded {var} = {value}")
        
        # Raise error if any required variables are missing
        if missing_vars:
            error_msg = f"Missing required configuration values: {', '.join(missing_vars)}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg)
        
        logger.info("✓ Configuration loaded successfully from dictionary")
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, str]) -> 'Config':
        """
        Create a Config instance from a dictionary.
        
        Args:
            config_dict: Dictionary containing configuration values
            
        Returns:
            New Config instance
        """
        return cls(config_dict=config_dict)
    
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
        # Return empty list since podcasts are removed
        return []
    
    def get_max_articles_per_topic(self) -> int:
        """Get maximum articles per topic as integer."""
        return int(self.get('MAX_ARTICLES_PER_TOPIC'))
    
    def get_briefing_duration_minutes(self) -> int:
        """Get briefing duration in minutes as integer."""
        return int(self.get('BRIEFING_DURATION_MINUTES'))
    
    def get_listener_name(self) -> str:
        """Get listener name for personalized greetings."""
        return self.get('LISTENER_NAME')
    
    # Advanced configuration getters (New for Milestone 5)
    def get_briefing_tone(self) -> str:
        """Get briefing tone setting."""
        return self.get('BRIEFING_TONE')
    
    def get_content_depth(self) -> str:
        """Get content depth setting."""
        return self.get('CONTENT_DEPTH')
    
    def get_keywords_exclude(self) -> list[str]:
        """Get keywords to exclude as a list."""
        keywords_str = self.get('KEYWORDS_EXCLUDE')
        if not keywords_str.strip():
            return []
        return [keyword.strip().lower() for keyword in keywords_str.split(',')]
    
    def get_voice_speed(self) -> float:
        """Get voice speed as float."""
        return float(self.get('VOICE_SPEED'))
    
    def is_aws_environment(self) -> bool:
        """
        Check if running in AWS environment.
        
        This will be used in Milestone 4 to determine whether to use
        AWS Secrets Manager instead of environment variables.
        """
        return os.environ.get('AWS_EXECUTION_ENV') is not None
    
    def validate_config(self):
        """
        Validate the configuration has all required fields.
        
        Raises:
            ConfigurationError: If required fields are missing or invalid
        """
        missing_keys = []
        
        for key in self.REQUIRED_KEYS:
            if not self.get(key):
                missing_keys.append(key)
        
        if missing_keys:
            raise ConfigurationError(
                f"Missing required configuration: {', '.join(missing_keys)}"
            )
        
        # Validate location settings
        if not self.get('LOCATION_CITY'):
            raise ConfigurationError("LOCATION_CITY cannot be empty")
        
        if not self.get('LOCATION_COUNTRY'):
            raise ConfigurationError("LOCATION_COUNTRY cannot be empty")
        
        # Validate content settings
        if not self.get_news_topics():
            raise ConfigurationError("NEWS_TOPICS cannot be empty")
        
        # Validate numeric fields
        try:
            self.get_max_articles_per_topic()
        except ValueError:
            raise ConfigurationError("MAX_ARTICLES_PER_TOPIC must be a valid integer")
        
        try:
            self.get_briefing_duration_minutes()
        except ValueError:
            raise ConfigurationError("BRIEFING_DURATION_MINUTES must be a valid integer")
        
        # Validate advanced settings
        if self.get_briefing_tone() not in ['professional', 'casual', 'energetic']:
            raise ConfigurationError("BRIEFING_TONE must be one of: professional, casual, energetic")
        
        if self.get_content_depth() not in ['headlines', 'balanced', 'detailed']:
            raise ConfigurationError("CONTENT_DEPTH must be one of: headlines, balanced, detailed")
        
        try:
            voice_speed = float(self.get('VOICE_SPEED'))
            if voice_speed not in [0.8, 1.0, 1.2]:
                raise ConfigurationError("VOICE_SPEED must be one of: 0.8, 1.0, 1.2")
        except ValueError:
            raise ConfigurationError("VOICE_SPEED must be a valid float")


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