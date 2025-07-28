"""
Data fetchers module for AI Daily Briefing Agent.

This module contains functions for calling external data APIs:
- NewsAPI for news articles
- OpenWeatherMap for weather data
- Listen Notes for podcast episodes
"""

import logging
from typing import List, Dict, Any
from dataclasses import dataclass

from config import get_config

logger = logging.getLogger(__name__)


@dataclass
class Article:
    """Data structure for news articles."""
    title: str
    source: str
    url: str
    content: str
    summary: str = ""


@dataclass
class PodcastEpisode:
    """Data structure for podcast episodes."""
    podcast_title: str
    episode_title: str
    url: str


@dataclass
class WeatherData:
    """Data structure for weather information."""
    city: str
    country: str
    temperature: float
    description: str
    humidity: int
    wind_speed: float


def get_weather() -> WeatherData:
    """
    Fetch current weather data from OpenWeatherMap API.
    
    Returns:
        WeatherData object with current conditions
        
    Raises:
        Exception: If API call fails
    """
    logger.info("Fetching weather data...")
    
    # TODO: Implement in Milestone 1
    # config = get_config()
    # api_key = config.get('OPENWEATHER_API_KEY')
    # city = config.get('LOCATION_CITY')
    # country = config.get('LOCATION_COUNTRY')
    
    # Placeholder return
    return WeatherData(
        city="San Francisco",
        country="US",
        temperature=22.5,
        description="partly cloudy",
        humidity=65,
        wind_speed=3.2
    )


def get_news_articles() -> List[Article]:
    """
    Fetch news articles from NewsAPI for configured topics.
    
    Returns:
        List of Article objects
        
    Raises:
        Exception: If API call fails
    """
    logger.info("Fetching news articles...")
    
    # TODO: Implement in Milestone 1
    # config = get_config()
    # api_key = config.get('NEWSAPI_KEY')
    # topics = config.get_news_topics()
    # max_articles = config.get_max_articles_per_topic()
    
    # Placeholder return
    return [
        Article(
            title="Sample Tech News Article",
            source="TechCrunch",
            url="https://example.com/article1",
            content="This is sample content for a technology article..."
        ),
        Article(
            title="Sample Business News Article", 
            source="Bloomberg",
            url="https://example.com/article2",
            content="This is sample content for a business article..."
        )
    ]


def get_new_podcast_episodes() -> List[PodcastEpisode]:
    """
    Fetch new podcast episodes from Listen Notes API.
    
    Returns:
        List of PodcastEpisode objects
        
    Raises:
        Exception: If API call fails
    """
    logger.info("Fetching new podcast episodes...")
    
    # TODO: Implement in Milestone 1
    # config = get_config()
    # api_key = config.get('LISTEN_NOTES_API_KEY')
    # categories = config.get_podcast_categories()
    
    # Placeholder return
    return [
        PodcastEpisode(
            podcast_title="Tech Talk Daily",
            episode_title="The Future of AI in 2025",
            url="https://example.com/podcast1"
        ),
        PodcastEpisode(
            podcast_title="Business Insights",
            episode_title="Market Trends This Week",
            url="https://example.com/podcast2"
        )
    ] 