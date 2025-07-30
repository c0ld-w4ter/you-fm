"""
Data fetchers module for AI Daily Briefing Agent.

This module contains functions for calling external data APIs:
- NewsAPI for news articles
- OpenWeatherMap for weather data
"""

import logging
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

from config import get_config, Config

logger = logging.getLogger(__name__)


@dataclass
class Article:
    """Data structure for news articles."""
    title: str
    source: str
    url: str
    content: str
    category: str = ""  # NewsAPI category (technology, business, etc.)
    summary: str = ""


@dataclass
class WeatherData:
    """Data structure for weather information."""
    city: str
    country: str
    temperature: float
    description: str
    humidity: int
    wind_speed: float


def get_weather(config=None) -> WeatherData:
    """
    Fetch current weather data from OpenWeatherMap API.
    
    Args:
        config: Optional Config object. If None, loads from environment.
    
    Returns:
        WeatherData object with current conditions
        
    Raises:
        Exception: If API call fails
    """
    logger.info("Fetching weather data...")
    
    if config is None:
        config = get_config()
    api_key = config.get('OPENWEATHER_API_KEY')
    city = config.get('LOCATION_CITY')
    country = config.get('LOCATION_COUNTRY')
    
    # OpenWeatherMap Current Weather API
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': f"{city},{country}",
        'appid': api_key,
        'units': 'metric'  # Use Celsius
    }
    
    try:
        import requests
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        data = response.json()
        
        # Parse the response
        weather_data = WeatherData(
            city=data['name'],
            country=data['sys']['country'],
            temperature=data['main']['temp'],
            description=data['weather'][0]['description'],
            humidity=data['main']['humidity'],
            wind_speed=data['wind']['speed']
        )
        
        logger.info(f"✓ Weather data fetched for {weather_data.city}, {weather_data.country}")
        return weather_data
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Weather API request failed: {e}")
        # Try to get more details from the response if available
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_details = e.response.json()
                logger.error(f"API error details: {error_details}")
                raise Exception(f"Weather API error: {error_details.get('message', str(e))}")
            except:
                pass
        raise Exception(f"Failed to fetch weather data: {e}")
    except KeyError as e:
        logger.error(f"Unexpected weather API response format: {e}")
        raise Exception(f"Invalid weather API response: {e}")
    except Exception as e:
        logger.error(f"Weather data fetch error: {e}")
        raise


def get_news_articles(config=None) -> List[Article]:
    """
    Fetch news articles from NewsAPI top headlines for configured categories.
    Only fetches articles from the past 24 hours.
    
    Args:
        config: Optional Config object. If None, loads from environment.
    
    Returns:
        List of Article objects
        
    Raises:
        Exception: If API call fails
    """
    logger.info("Fetching news articles from top headlines...")
    
    if config is None:
        config = get_config()
    api_key = config.get('NEWSAPI_KEY')
    topics = config.get_news_topics()  # These are now real NewsAPI categories
    max_articles = config.get_max_articles_per_topic()
    
    # Calculate date for past 24 hours
    from_date = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    all_articles = []
    
    try:
        import requests
        
        for category in topics:
            logger.info(f"Fetching top headlines for category: {category}")
            
            # NewsAPI Top Headlines endpoint with date filtering
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                'category': category,      # Use category instead of query search
                'country': 'us',          # Focus on US news for now
                'from': from_date,        # Only articles from past 24 hours
                'apiKey': api_key,
                'sortBy': 'publishedAt',
                'pageSize': max_articles,
                'language': 'en'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] != 'ok':
                logger.warning(f"NewsAPI returned non-ok status for category {category}: {data.get('message', 'Unknown error')}")
                continue
            
            # Parse articles
            articles_count = 0
            for article_data in data.get('articles', []):
                # Skip articles with null/empty essential fields
                if not article_data.get('title') or not article_data.get('url'):
                    continue
                
                article = Article(
                    title=article_data['title'],
                    source=article_data.get('source', {}).get('name', 'Unknown Source'),
                    url=article_data['url'],
                    content=(article_data.get('content') or article_data.get('description') or ''),
                    category=category, # Assign the category
                    summary=""  # Will be populated in Milestone 2
                )
                all_articles.append(article)
                articles_count += 1
            
            logger.info(f"✓ Fetched {articles_count} articles for category '{category}'")
        
        logger.info(f"✓ Fetched {len(all_articles)} total news articles across {len(topics)} categories (past 24 hours)")
        return all_articles
        
    except requests.exceptions.RequestException as e:
        logger.error(f"News API request failed: {e}")
        # Try to get more details from the response if available
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_details = e.response.json()
                logger.error(f"API error details: {error_details}")
                raise Exception(f"News API error: {error_details.get('message', str(e))}")
            except:
                pass
        raise Exception(f"Failed to fetch news articles: {e}")
    except KeyError as e:
        logger.error(f"Unexpected news API response format: {e}")
        raise Exception(f"Invalid news API response: {e}")
    except Exception as e:
        logger.error(f"News articles fetch error: {e}")
        raise 