"""
Data fetchers module for AI Daily Briefing Agent.

This module contains functions for calling external data APIs:
- NewsAPI for news articles
- OpenWeatherMap for weather data
"""

import logging
import json
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, UTC
from pathlib import Path

from config import get_config, Config

logger = logging.getLogger(__name__)

# Cache configuration
CACHE_DIR = Path(".cache")
NEWS_CACHE_FILE = CACHE_DIR / "news_cache.json"
CACHE_DURATION_HOURS = 6  # Cache news for 6 hours


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


class NewsCache:
    """Simple file-based cache for news articles."""
    
    def __init__(self, cache_file: Path = NEWS_CACHE_FILE):
        self.cache_file = cache_file
        self.cache_file.parent.mkdir(exist_ok=True)
        
    def _load_cache(self) -> Dict[str, Any]:
        """Load cache from file."""
        if not self.cache_file.exists():
            return {}
        
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load cache: {e}")
            return {}
    
    def _save_cache(self, cache_data: Dict[str, Any]) -> None:
        """Save cache to file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except IOError as e:
            logger.error(f"Failed to save cache: {e}")
    
    def get(self, cache_key: str, max_age_hours: float = CACHE_DURATION_HOURS) -> Optional[List[Dict[str, Any]]]:
        """Get cached articles if they exist and are not expired."""
        cache_data = self._load_cache()
        
        if cache_key not in cache_data:
            return None
        
        entry = cache_data[cache_key]
        cached_time = datetime.fromisoformat(entry['timestamp'])
        
        # Ensure cached_time is timezone-aware
        if cached_time.tzinfo is None:
            cached_time = cached_time.replace(tzinfo=UTC)
        
        # Check if cache is expired
        if datetime.now(UTC) - cached_time > timedelta(hours=max_age_hours):
            logger.info(f"Cache expired for key: {cache_key}")
            return None
        
        logger.info(f"Using cached data for key: {cache_key}")
        return entry['articles']
    
    def set(self, cache_key: str, articles: List[Dict[str, Any]]) -> None:
        """Store articles in cache with current timestamp."""
        cache_data = self._load_cache()
        
        cache_data[cache_key] = {
            'timestamp': datetime.now(UTC).isoformat(),
            'articles': articles
        }
        
        self._save_cache(cache_data)
        logger.info(f"Cached data for key: {cache_key}")
    
    def clear(self) -> None:
        """Clear all cached data."""
        if self.cache_file.exists():
            self.cache_file.unlink()
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        cache_data = self._load_cache()
        stats = {
            'total_entries': len(cache_data),
            'entries': []
        }
        
        for key, entry in cache_data.items():
            cached_time = datetime.fromisoformat(entry['timestamp'])
            
            # Ensure cached_time is timezone-aware
            if cached_time.tzinfo is None:
                cached_time = cached_time.replace(tzinfo=UTC)
            
            age_hours = (datetime.now(UTC) - cached_time).total_seconds() / 3600
            stats['entries'].append({
                'key': key,
                'cached_at': entry['timestamp'],
                'age_hours': round(age_hours, 2),
                'article_count': len(entry['articles'])
            })
        
        return stats


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


def get_news_articles(config=None, use_cache: bool = True) -> List[Article]:
    """
    Fetch news articles from NewsAPI.ai for configured categories.
    Fetches articles from the past 24 hours using keyword-based searches.
    
    Args:
        config: Optional Config object. If None, loads from environment.
        use_cache: Whether to use caching (default: True)
    
    Returns:
        List of Article objects
        
    Raises:
        Exception: If API call fails
    """
    logger.info("Fetching news articles from NewsAPI.ai...")
    
    if config is None:
        config = get_config()
    api_key = config.get('NEWSAPI_AI_KEY')
    topics = config.get_news_topics()
    max_articles = config.get_max_articles_per_topic()
    
    # Calculate date for past 24 hours
    from_date = (datetime.now(UTC) - timedelta(days=1)).strftime('%Y-%m-%d')
    to_date = datetime.now(UTC).strftime('%Y-%m-%d')
    
    # Map NewsAPI categories to single effective keywords (Boolean OR doesn't work with date filters)
    category_keywords = {
        'business': 'business',
        'entertainment': 'entertainment', 
        'health': 'health',
        'science': 'science',
        'sports': 'sports',
        'technology': 'technology',
        # New categories for expanded coverage
        'politics': 'politics',
        'world': 'international',
        'environment': 'climate',
        'finance': 'finance',
        'crime': 'crime',
        'education': 'education',
        'weather': 'weather'
    }
    
    # Initialize cache
    cache = NewsCache() if use_cache else None
    
    all_articles = []
    api_calls_made = 0
    
    try:
        import requests
        
        for category in topics:
            # Create cache key based on category and date
            cache_key = f"{category}_{from_date}_{max_articles}"
            
            # Try to get from cache first
            if cache:
                cached_articles = cache.get(cache_key)
                if cached_articles is not None:
                    # Convert cached data back to Article objects
                    for article_data in cached_articles:
                        article = Article(
                            title=article_data['title'],
                            source=article_data['source'],
                            url=article_data['url'],
                            content=article_data['content'],
                            category=article_data['category'],
                            summary=article_data['summary']
                        )
                        all_articles.append(article)
                    continue
            
            # If not in cache or cache disabled, fetch from API
            keywords = category_keywords.get(category, category)
            logger.info(f"Fetching articles for category '{category}' using keywords: {keywords}")
            api_calls_made += 1
            
            # NewsAPI.ai article search endpoint
            url = "https://newsapi.ai/api/v1/article/getArticles"
            payload = {
                "query": {
                    "$query": {
                        "$and": [
                            {"lang": "eng"},
                            {"keyword": keywords},
                            {"dateStart": from_date},
                            {"dateEnd": to_date}
                        ]
                    }
                },
                "resultType": "articles",
                "articlesSortBy": "date",
                "articlesCount": max_articles,
                "apiKey": api_key
            }
            
            headers = {
                "Content-Type": "application/json",
                "accept": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Check if we have articles in the response
            articles_data = data.get('articles', {}).get('results', [])
            if not articles_data:
                logger.info(f"No articles found for category '{category}'")
                continue
            
            # Parse articles
            articles_for_category = []
            articles_count = 0
            for article_data in articles_data:
                # Skip articles with null/empty essential fields
                if not article_data.get('title') or not article_data.get('url'):
                    continue
                
                # Extract source name
                source_name = 'Unknown Source'
                if 'source' in article_data and article_data['source']:
                    source_name = article_data['source'].get('title', 'Unknown Source')
                
                # Use full body content if available, fallback to title
                content = article_data.get('body', '') or article_data.get('title', '')
                
                article = Article(
                    title=article_data['title'],
                    source=source_name,
                    url=article_data['url'],
                    content=content,
                    category=category,
                    summary=""  # Will be populated later
                )
                all_articles.append(article)
                articles_for_category.append(asdict(article))
                articles_count += 1
            
            # Cache the articles for this category
            if cache and articles_for_category:
                cache.set(cache_key, articles_for_category)
            
            logger.info(f"✓ Fetched {articles_count} articles for category '{category}'")
        
        logger.info(f"✓ Fetched {len(all_articles)} total news articles across {len(topics)} categories")
        logger.info(f"✓ Made {api_calls_made} API calls (saved {len(topics) - api_calls_made} calls using cache)")
        return all_articles
        
    except requests.exceptions.RequestException as e:
        logger.error(f"NewsAPI.ai request failed: {e}")
        # Try to get more details from the response if available
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_details = e.response.json()
                logger.error(f"API error details: {error_details}")
                if 'error' in error_details:
                    raise Exception(f"NewsAPI.ai error: {error_details['error']}")
                else:
                    raise Exception(f"NewsAPI.ai error: {error_details}")
            except:
                pass
        raise Exception(f"Failed to fetch news articles: {e}")
    except KeyError as e:
        logger.error(f"Unexpected NewsAPI.ai response format: {e}")
        raise Exception(f"Invalid NewsAPI.ai response: {e}")
    except Exception as e:
        logger.error(f"News articles fetch error: {e}")
        raise 