"""
Unit tests for the config module.

These tests verify the configuration loading functionality
as specified in Milestone 0 of the technical specification.
"""

import os
import pytest
from unittest.mock import patch, MagicMock

from config import Config, ConfigurationError, get_config


class TestConfig:
    """Test cases for the Config class."""
    
    def test_config_loads_all_required_vars(self):
        """Test that Config loads all required environment variables."""
        # Mock all required environment variables
        mock_env = {
            'NEWSAPI_AI_KEY': 'test-newsapi-key',
            'OPENWEATHER_API_KEY': 'test-weather-key',
            'GEMINI_API_KEY': 'test-gemini-key',
            'ELEVENLABS_API_KEY': 'test-elevenlabs-key',
            'GOOGLE_DRIVE_FOLDER_ID': 'test-folder-id',
        }
        
        with patch.dict(os.environ, mock_env, clear=True):
            config = Config()
            
                    # Verify all required variables are loaded
        for var in Config.REQUIRED_KEYS:
                assert config.get(var) == mock_env[var]
    
    def test_config_handles_missing_required_vars(self):
        """Test that Config raises error when required variables are missing."""
        # Mock environment with missing required variables
        mock_env = {
            'NEWSAPI_AI_KEY': 'test-key',
            # Missing other required vars
        }
        
        with patch.dict(os.environ, mock_env, clear=True):
            with pytest.raises(ConfigurationError) as exc_info:
                Config()
            
            # Should mention the missing variables
            error_msg = str(exc_info.value)
            assert 'Missing required environment variables' in error_msg
            assert 'OPENWEATHER_API_KEY' in error_msg
    
    def test_config_loads_defaults(self):
        """Test that Config loads default values for optional variables."""
        # Mock only required environment variables
        mock_env = {
            'NEWSAPI_AI_KEY': 'test-newsapi-key',
            'OPENWEATHER_API_KEY': 'test-weather-key',
            'GEMINI_API_KEY': 'test-gemini-key',
            'ELEVENLABS_API_KEY': 'test-elevenlabs-key',
            'GOOGLE_DRIVE_FOLDER_ID': 'test-folder-id',
        }
        
        with patch.dict(os.environ, mock_env, clear=True):
            config = Config()
            
            # Verify default values are loaded
            assert config.get('LOCATION_CITY') == 'Denver'
            assert config.get('NEWS_TOPICS') == 'business,entertainment,general,health,science,sports,technology,politics,world,environment,finance,crime,education,weather'  # Updated for expanded coverage
    
    def test_config_overrides_defaults(self):
        """Test that environment variables override default values."""
        mock_env = {
            'NEWSAPI_AI_KEY': 'test-newsapi-key',
            'OPENWEATHER_API_KEY': 'test-weather-key',
            'GEMINI_API_KEY': 'test-gemini-key',
            'ELEVENLABS_API_KEY': 'test-elevenlabs-key',
            'GOOGLE_DRIVE_FOLDER_ID': 'test-folder-id',
            'LOCATION_CITY': 'New York',  # Override default
            'NEWS_TOPICS': 'politics,sports',  # Override default
        }
        
        with patch.dict(os.environ, mock_env, clear=True):
            config = Config()
            
            assert config.get('LOCATION_CITY') == 'New York'
            assert config.get('NEWS_TOPICS') == 'politics,sports'
    
    def test_get_with_default(self):
        """Test the get method with default value."""
        mock_env = {
            'NEWSAPI_AI_KEY': 'test-newsapi-key',
            'OPENWEATHER_API_KEY': 'test-weather-key',
            'GEMINI_API_KEY': 'test-gemini-key',
            'ELEVENLABS_API_KEY': 'test-elevenlabs-key',
            'GOOGLE_DRIVE_FOLDER_ID': 'test-folder-id',
        }
        
        with patch.dict(os.environ, mock_env, clear=True):
            config = Config()
            
            # Test existing key
            assert config.get('NEWSAPI_AI_KEY') == 'test-newsapi-key'
            
            # Test non-existing key with default
            assert config.get('NON_EXISTING_KEY', 'default_value') == 'default_value'
            
            # Test non-existing key without default should raise error
            with pytest.raises(ConfigurationError):
                config.get('NON_EXISTING_KEY')
    
    def test_get_news_topics(self):
        """Test parsing news topics into a list."""
        mock_env = {
            'NEWSAPI_AI_KEY': 'test-newsapi-key',
            'OPENWEATHER_API_KEY': 'test-weather-key',
            'GEMINI_API_KEY': 'test-gemini-key',
            'ELEVENLABS_API_KEY': 'test-elevenlabs-key',
            'GOOGLE_DRIVE_FOLDER_ID': 'test-folder-id',
            'NEWS_TOPICS': 'tech, business , science',  # Test with spaces
        }
        
        with patch.dict(os.environ, mock_env, clear=True):
            config = Config()
            topics = config.get_news_topics()
            
            assert topics == ['tech', 'business', 'science']
    
    def test_get_max_articles_per_topic(self):
        """Test parsing max articles as integer."""
        mock_env = {
            'NEWSAPI_AI_KEY': 'test-newsapi-key',
            'OPENWEATHER_API_KEY': 'test-weather-key',
            'GEMINI_API_KEY': 'test-gemini-key',
            'ELEVENLABS_API_KEY': 'test-elevenlabs-key',
            'GOOGLE_DRIVE_FOLDER_ID': 'test-folder-id',
            'MAX_ARTICLES_PER_TOPIC': '5',
        }
        
        with patch.dict(os.environ, mock_env, clear=True):
            config = Config()
            max_articles = config.get_max_articles_per_topic()
            
            assert max_articles == 5
            assert isinstance(max_articles, int)
    
    def test_is_aws_environment(self):
        """Test AWS environment detection."""
        mock_env = {
            'NEWSAPI_AI_KEY': 'test-newsapi-key',
            'OPENWEATHER_API_KEY': 'test-weather-key',
            'GEMINI_API_KEY': 'test-gemini-key',
            'ELEVENLABS_API_KEY': 'test-elevenlabs-key',
            'GOOGLE_DRIVE_FOLDER_ID': 'test-folder-id',
        }
        
        # Test without AWS environment
        with patch.dict(os.environ, mock_env, clear=True):
            config = Config()
            assert config.is_aws_environment() is False
        
        # Test with AWS environment
        mock_env['AWS_EXECUTION_ENV'] = 'AWS_Lambda_python3.11'
        with patch.dict(os.environ, mock_env, clear=True):
            config = Config()
            assert config.is_aws_environment() is True
    
    def test_validate_config(self):
        """Test configuration validation."""
        mock_env = {
            'NEWSAPI_AI_KEY': 'test-newsapi-key',
            'OPENWEATHER_API_KEY': 'test-weather-key',
            'GEMINI_API_KEY': 'test-gemini-key',
            'ELEVENLABS_API_KEY': 'test-elevenlabs-key',
            'GOOGLE_DRIVE_FOLDER_ID': 'test-folder-id',
        }
        
        with patch.dict(os.environ, mock_env, clear=True):
            config = Config()
            
                    # Should validate successfully (no exception raised)
        config.validate_config()
        
        # Test with invalid integer value
        mock_env['MAX_ARTICLES_PER_TOPIC'] = 'not_a_number'
        with patch.dict(os.environ, mock_env, clear=True):
            config = Config()
            
            with pytest.raises(ConfigurationError):
                config.validate_config()

    def test_get_briefing_duration_minutes_default(self):
        """Test that briefing duration returns default value when not set."""
        # Mock required environment variables
        mock_env = {
            'NEWSAPI_AI_KEY': 'test_news_key',
            'OPENWEATHER_API_KEY': 'test_weather_key',
            'GEMINI_API_KEY': 'test_gemini_key',
            'ELEVENLABS_API_KEY': 'test_elevenlabs_key',
        }
        with patch.dict(os.environ, mock_env, clear=True):
            config = Config()
            # Set a custom value for testing
            config._config['BRIEFING_DURATION_MINUTES'] = '5'
            assert config.get_briefing_duration_minutes() == 5
    
    def test_get_briefing_duration_minutes_custom(self):
        """Test that briefing duration returns custom value when set."""
        # Mock required environment variables
        mock_env = {
            'NEWSAPI_AI_KEY': 'test_news_key',
            'OPENWEATHER_API_KEY': 'test_weather_key',
            'GEMINI_API_KEY': 'test_gemini_key',
            'ELEVENLABS_API_KEY': 'test_elevenlabs_key',
            'BRIEFING_DURATION_MINUTES': '7',
        }
        with patch.dict(os.environ, mock_env, clear=True):
            config = Config()
            assert config.get_briefing_duration_minutes() == 7
    
    def test_get_briefing_duration_minutes_invalid(self):
        """Test that briefing duration handles invalid values gracefully."""
        # Mock required environment variables
        mock_env = {
            'NEWSAPI_AI_KEY': 'test_news_key',
            'OPENWEATHER_API_KEY': 'test_weather_key',
            'GEMINI_API_KEY': 'test_gemini_key',
            'ELEVENLABS_API_KEY': 'test_elevenlabs_key',
            'BRIEFING_DURATION_MINUTES': 'invalid',
        }
        with patch.dict(os.environ, mock_env, clear=True):
            config = Config()
            with pytest.raises(ValueError):
                config.get_briefing_duration_minutes()
    
    def test_get_listener_name_default(self):
        """Test that listener name returns default value when not set."""
        # Mock required environment variables
        mock_env = {
            'NEWSAPI_AI_KEY': 'test_news_key',
            'OPENWEATHER_API_KEY': 'test_weather_key',
            'GEMINI_API_KEY': 'test_gemini_key',
            'ELEVENLABS_API_KEY': 'test_elevenlabs_key',
        }
        with patch.dict(os.environ, mock_env, clear=True):
            config = Config()
            assert config.get_listener_name() == ''  # Default value from config
    
    def test_get_listener_name_custom(self):
        """Test that listener name returns custom value when set."""
        # Mock required environment variables
        mock_env = {
            'NEWSAPI_AI_KEY': 'test_news_key',
            'OPENWEATHER_API_KEY': 'test_weather_key',
            'GEMINI_API_KEY': 'test_gemini_key',
            'ELEVENLABS_API_KEY': 'test_elevenlabs_key',
            'LISTENER_NAME': 'Alice',
        }
        with patch.dict(os.environ, mock_env, clear=True):
            config = Config()
            assert config.get_listener_name() == 'Alice'


class TestGetConfig:
    """Test cases for the get_config function."""
    
    def test_get_config_returns_instance(self):
        """Test that get_config returns a Config instance."""
        mock_env = {
            'NEWSAPI_AI_KEY': 'test-newsapi-key',
            'OPENWEATHER_API_KEY': 'test-weather-key',
            'GEMINI_API_KEY': 'test-gemini-key',
            'ELEVENLABS_API_KEY': 'test-elevenlabs-key',
            'GOOGLE_DRIVE_FOLDER_ID': 'test-folder-id',
        }
        
        with patch.dict(os.environ, mock_env, clear=True):
            # Reset global config to None to test fresh initialization
            import config
            config.config = None
            
            instance = get_config()
            assert isinstance(instance, Config)
            assert instance.get('NEWSAPI_AI_KEY') == 'test-newsapi-key' 


class TestAdvancedConfigurationGetters:
    """Test new advanced configuration getter methods."""
    
    def test_get_briefing_tone(self):
        """Test briefing tone getter method."""
        config_dict = {
            'NEWSAPI_AI_KEY': 'test_key',
            'OPENWEATHER_API_KEY': 'test_key',
            'GEMINI_API_KEY': 'test_key',
            'ELEVENLABS_API_KEY': 'test_key',
            'BRIEFING_TONE': 'casual'
        }
        
        config = Config(config_dict)
        assert config.get_briefing_tone() == 'casual'
    
    def test_get_content_depth(self):
        """Test content depth getter method."""
        config_dict = {
            'NEWSAPI_AI_KEY': 'test_key',
            'OPENWEATHER_API_KEY': 'test_key',
            'GEMINI_API_KEY': 'test_key',
            'ELEVENLABS_API_KEY': 'test_key',
            'CONTENT_DEPTH': 'detailed'
        }
        
        config = Config(config_dict)
        assert config.get_content_depth() == 'detailed'
    
    def test_get_keywords_exclude_with_values(self):
        """Test keywords exclude getter with actual keywords."""
        config_dict = {
            'NEWSAPI_AI_KEY': 'test_key',
            'OPENWEATHER_API_KEY': 'test_key',
            'GEMINI_API_KEY': 'test_key',
            'ELEVENLABS_API_KEY': 'test_key',
            'KEYWORDS_EXCLUDE': 'sports,Celebrity,POLITICS'
        }
        
        config = Config(config_dict)
        keywords = config.get_keywords_exclude()
        
        # Should return lowercase, trimmed keywords
        assert keywords == ['sports', 'celebrity', 'politics']
    
    def test_get_keywords_exclude_empty(self):
        """Test keywords exclude getter with empty string."""
        config_dict = {
            'NEWSAPI_AI_KEY': 'test_key',
            'OPENWEATHER_API_KEY': 'test_key',
            'GEMINI_API_KEY': 'test_key',
            'ELEVENLABS_API_KEY': 'test_key',
            'KEYWORDS_EXCLUDE': ''
        }
        
        config = Config(config_dict)
        keywords = config.get_keywords_exclude()
        
        # Should return empty list for empty string
        assert keywords == []
    
    def test_get_voice_speed(self):
        """Test voice speed getter method."""
        config_dict = {
            'NEWSAPI_AI_KEY': 'test_key',
            'OPENWEATHER_API_KEY': 'test_key',
            'GEMINI_API_KEY': 'test_key',
            'ELEVENLABS_API_KEY': 'test_key',
            'VOICE_SPEED': '1.2'
        }
        
        config = Config(config_dict)
        speed = config.get_voice_speed()
        
        # Should return float value
        assert speed == 1.2
        assert isinstance(speed, float)
    
    def test_advanced_config_defaults_in_class(self):
        """Test that advanced config defaults are properly set in Config class."""
        # Test that defaults exist in the class
        assert 'BRIEFING_TONE' in Config.DEFAULT_CONFIG
        assert 'CONTENT_DEPTH' in Config.DEFAULT_CONFIG
        assert 'KEYWORDS_EXCLUDE' in Config.DEFAULT_CONFIG
        assert 'VOICE_SPEED' in Config.DEFAULT_CONFIG
        
        # Test default values
        assert Config.DEFAULT_CONFIG['BRIEFING_TONE'] == 'professional'
        assert Config.DEFAULT_CONFIG['CONTENT_DEPTH'] == 'balanced'
        assert Config.DEFAULT_CONFIG['KEYWORDS_EXCLUDE'] == ''
        assert Config.DEFAULT_CONFIG['VOICE_SPEED'] == '1.0'
    
    def test_personalization_getters(self):
        """Test all personalization getter methods."""
        config_dict = {
            'NEWSAPI_AI_KEY': 'test_key',
            'OPENWEATHER_API_KEY': 'test_key',
            'GEMINI_API_KEY': 'test_key',
            'ELEVENLABS_API_KEY': 'test_key',
            'SPECIFIC_INTERESTS': 'AI, quantum computing',
            # 'BRIEFING_GOAL' removed for UI simplification
            'FOLLOWED_ENTITIES': 'OpenAI, Elon Musk',
            'HOBBIES': 'hiking, gaming',
            'FAVORITE_TEAMS_ARTISTS': 'Lakers, Taylor Swift',
            'PASSION_TOPICS': 'space exploration',
            'GREETING_PREFERENCE': 'Good morning, friend!',
            'DAILY_ROUTINE_DETAIL': 'I walk my dog every morning'
        }
        
        config = Config(config_dict)
        
        # Test News & Information Preferences
        assert config.get_specific_interests() == 'AI, quantum computing'
        # briefing_goal method removed for UI simplification
        assert config.get_followed_entities() == 'OpenAI, Elon Musk'
        
        # Test Hobbies & Personal Interests
        assert config.get_hobbies() == 'hiking, gaming'
        assert config.get_favorite_teams_artists() == 'Lakers, Taylor Swift'
        assert config.get_passion_topics() == 'space exploration'
        
        # Test Personal Quirks & Style
        assert config.get_greeting_preference() == 'Good morning, friend!'
        assert config.get_daily_routine_detail() == 'I walk my dog every morning'
    
    def test_personalization_defaults(self):
        """Test personalization fields have proper defaults."""
        config_dict = {
            'NEWSAPI_AI_KEY': 'test_key',
            'OPENWEATHER_API_KEY': 'test_key',
            'GEMINI_API_KEY': 'test_key',
            'ELEVENLABS_API_KEY': 'test_key'
        }
        
        config = Config(config_dict)
        
        # Now have smart defaults instead of empty strings
        assert config.get_specific_interests() == 'artificial intelligence, machine learning, startup news'
        # briefing_goal method removed for UI simplification
        assert config.get_followed_entities() == 'tech industry, major tech companies'
        assert config.get_hobbies() == 'reading tech blogs, podcasts'
        assert config.get_passion_topics() == 'technology trends, innovation'
        assert config.get_greeting_preference() == 'Good morning! Here is your essential tech and business update.'
        assert config.get_daily_routine_detail() == 'I listen during my morning coffee' 