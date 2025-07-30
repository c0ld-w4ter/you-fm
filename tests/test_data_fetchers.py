"""
Unit tests for the data_fetchers module.

These tests verify the data fetching functionality from external APIs
as specified in Milestone 1 of the technical specification.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from data_fetchers import (
    get_weather, get_news_articles,
    WeatherData, Article
)


class TestGetWeather:
    """Test cases for the get_weather function."""
    
    @patch('requests.get')
    @patch('data_fetchers.get_config')
    def test_get_weather_success(self, mock_config, mock_requests):
        """Test successful weather data fetching."""
        # Mock configuration
        mock_config_instance = MagicMock()
        mock_config_instance.get.side_effect = lambda key: {
            'OPENWEATHER_API_KEY': 'test-weather-key',
            'LOCATION_CITY': 'San Francisco',
            'LOCATION_COUNTRY': 'US'
        }[key]
        mock_config.return_value = mock_config_instance
        
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'name': 'San Francisco',
            'sys': {'country': 'US'},
            'main': {
                'temp': 22.5,
                'humidity': 65
            },
            'weather': [{'description': 'partly cloudy'}],
            'wind': {'speed': 3.2}
        }
        mock_response.raise_for_status.return_value = None
        mock_requests.return_value = mock_response
        
        # Call function
        result = get_weather()
        
        # Verify API call
        mock_requests.assert_called_once()
        call_args = mock_requests.call_args
        assert call_args[1]['params']['q'] == 'San Francisco,US'
        assert call_args[1]['params']['appid'] == 'test-weather-key'
        assert call_args[1]['params']['units'] == 'metric'
        assert call_args[1]['timeout'] == 10
        
        # Verify result
        assert isinstance(result, WeatherData)
        assert result.city == 'San Francisco'
        assert result.country == 'US'
        assert result.temperature == 22.5
        assert result.description == 'partly cloudy'
        assert result.humidity == 65
        assert result.wind_speed == 3.2

    @patch('requests.get')
    @patch('data_fetchers.get_config')
    def test_get_weather_invalid_response(self, mock_config, mock_requests):
        """Test weather API handling of invalid response."""
        # Mock configuration
        mock_config_instance = MagicMock()
        mock_config_instance.get.side_effect = lambda key: {
            'OPENWEATHER_API_KEY': 'test-weather-key',
            'LOCATION_CITY': 'Denver',
            'LOCATION_COUNTRY': 'US'
        }[key]
        mock_config.return_value = mock_config_instance
        
        # Mock invalid API response (missing required fields)
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'invalid': 'response'  # Missing required fields
        }
        mock_response.raise_for_status.return_value = None
        mock_requests.return_value = mock_response
        
        # Verify exception is raised
        with pytest.raises(Exception) as exc_info:
            get_weather()

        
        assert "Invalid weather API response" in str(exc_info.value)


class TestGetNewsArticles:
    """Test cases for the get_news_articles function."""
    
    @patch('data_fetchers.datetime')
    @patch('requests.get')
    @patch('data_fetchers.get_config')
    def test_get_news_articles_success(self, mock_config, mock_requests, mock_datetime):
        """Test successful news articles fetching from top headlines."""
        # Mock datetime for deterministic date filtering
        mock_now = datetime(2025, 7, 30, 12, 0, 0)
        mock_yesterday = mock_now - timedelta(days=1)
        mock_datetime.utcnow.return_value = mock_now
        mock_datetime.timedelta = timedelta  # Keep real timedelta
        
        # Mock configuration
        mock_config_instance = MagicMock()
        mock_config_instance.get.side_effect = lambda key: {
            'NEWSAPI_KEY': 'test-news-key'
        }[key]
        mock_config_instance.get_news_topics.return_value = ['technology', 'business']
        mock_config_instance.get_max_articles_per_topic.return_value = 2
        mock_config.return_value = mock_config_instance
        
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'status': 'ok',
            'articles': [
                {
                    'title': 'Test Tech Article',
                    'source': {'name': 'TechCrunch'},
                    'url': 'https://example.com/tech1',
                    'content': 'Tech article content...',
                    'description': 'Tech article description'
                },
                {
                    'title': 'Test Business Article',
                    'source': {'name': 'Bloomberg'},
                    'url': 'https://example.com/business1',
                    'content': 'Business article content...',
                    'description': 'Business article description'
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_requests.return_value = mock_response
        
        # Call function
        result = get_news_articles()
        
        # Verify API calls (should be called twice for two categories)
        assert mock_requests.call_count == 2
        
        # Verify API endpoint
        first_call = mock_requests.call_args_list[0]
        assert 'top-headlines' in first_call[0][0]  # Check URL contains top-headlines
        
        # Verify API call parameters for first category
        first_params = first_call[1]['params']
        assert first_params['category'] == 'technology'  # Changed from 'q' to 'category'
        assert first_params['country'] == 'us'           # New parameter
        assert first_params['from'] == '2025-07-29'      # New date filtering
        assert first_params['apiKey'] == 'test-news-key'
        assert first_params['pageSize'] == 2
        assert first_params['sortBy'] == 'publishedAt'
        assert first_params['language'] == 'en'
        
        # Verify second category call
        second_call = mock_requests.call_args_list[1]
        second_params = second_call[1]['params']
        assert second_params['category'] == 'business'
        
        # Verify result
        assert len(result) == 4  # 2 articles × 2 categories
        assert all(isinstance(article, Article) for article in result)
        
        # Check first article
        first_article = result[0]
        assert first_article.title == 'Test Tech Article'
        assert first_article.source == 'TechCrunch'
        assert first_article.url == 'https://example.com/tech1'
        assert first_article.content == 'Tech article content...'
        assert first_article.summary == ""  # Not populated yet
    
    @patch('data_fetchers.datetime')
    @patch('requests.get')
    @patch('data_fetchers.get_config')
    def test_get_news_articles_skip_invalid(self, mock_config, mock_requests, mock_datetime):
        """Test news articles fetching skips invalid articles."""
        # Mock datetime
        mock_now = datetime(2025, 7, 30, 12, 0, 0)
        mock_datetime.utcnow.return_value = mock_now
        mock_datetime.timedelta = timedelta
        
        # Mock configuration
        mock_config_instance = MagicMock()
        mock_config_instance.get.side_effect = lambda key: {
            'NEWSAPI_KEY': 'test-news-key'
        }[key]
        mock_config_instance.get_news_topics.return_value = ['technology']
        mock_config_instance.get_max_articles_per_topic.return_value = 3
        mock_config.return_value = mock_config_instance
        
        # Mock API response with some invalid articles
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'status': 'ok',
            'articles': [
                {
                    'title': 'Valid Article',
                    'source': {'name': 'TechCrunch'},
                    'url': 'https://example.com/valid',
                    'content': 'Valid content...'
                },
                {
                    'title': None,  # Invalid - no title
                    'source': {'name': 'Source'},
                    'url': 'https://example.com/invalid1',
                    'content': 'Invalid content...'
                },
                {
                    'title': 'No URL Article',
                    'source': {'name': 'Source'},
                    'url': None,  # Invalid - no URL
                    'content': 'Invalid content...'
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_requests.return_value = mock_response
        
        # Call function
        result = get_news_articles()
        
        # Verify only valid article is returned
        assert len(result) == 1
        assert result[0].title == 'Valid Article'
    
    @patch('data_fetchers.datetime')
    @patch('requests.get')
    @patch('data_fetchers.get_config')
    def test_get_news_articles_api_error(self, mock_config, mock_requests, mock_datetime):
        """Test news API error handling."""
        # Mock datetime
        mock_datetime.utcnow.return_value = datetime(2025, 7, 30, 12, 0, 0)
        mock_datetime.timedelta = timedelta
        
        # Mock configuration
        mock_config_instance = MagicMock()
        mock_config_instance.get.side_effect = lambda key: {
            'NEWSAPI_KEY': 'test-news-key'
        }[key]
        mock_config_instance.get_news_topics.return_value = ['technology']
        mock_config_instance.get_max_articles_per_topic.return_value = 2
        mock_config.return_value = mock_config_instance
        
        # Mock API error
        mock_requests.side_effect = Exception("NewsAPI connection failed")
        
        # Verify exception is raised
        with pytest.raises(Exception) as exc_info:
            get_news_articles()
        
        assert "NewsAPI connection failed" in str(exc_info.value) 