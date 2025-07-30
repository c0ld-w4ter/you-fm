"""
Data fetchers module for AI Daily Briefing Agent.

This module contains functions for calling external data APIs:
- NewsAPI for news articles
- OpenWeatherMap for weather data
- Taddy API for podcast episodes
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
    Fetch news articles from NewsAPI for configured topics.
    
    Args:
        config: Optional Config object. If None, loads from environment.
    
    Returns:
        List of Article objects
        
    Raises:
        Exception: If API call fails
    """
    logger.info("Fetching news articles...")
    
    if config is None:
        config = get_config()
    api_key = config.get('NEWSAPI_KEY')
    topics = config.get_news_topics()
    max_articles = config.get_max_articles_per_topic()
    
    all_articles = []
    
    try:
        import requests
        
        for topic in topics:
            logger.info(f"Fetching articles for topic: {topic}")
            
            # NewsAPI Everything endpoint
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': topic,
                'apiKey': api_key,
                'sortBy': 'publishedAt',
                'pageSize': max_articles,
                'language': 'en'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] != 'ok':
                logger.warning(f"NewsAPI returned non-ok status for topic {topic}: {data.get('message', 'Unknown error')}")
                continue
            
            # Parse articles
            for article_data in data.get('articles', []):
                # Skip articles with null/empty essential fields
                if not article_data.get('title') or not article_data.get('url'):
                    continue
                
                article = Article(
                    title=article_data['title'],
                    source=article_data.get('source', {}).get('name', 'Unknown Source'),
                    url=article_data['url'],
                    content=article_data.get('content', '') or article_data.get('description', ''),
                    summary=""  # Will be populated in Milestone 2
                )
                all_articles.append(article)
        
        logger.info(f"✓ Fetched {len(all_articles)} news articles across {len(topics)} topics")
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


def get_news_from_gemini(config=None) -> List[Article]:
    """
    Fetch curated daily news using Gemini's web search capabilities.
    
    Uses Google Gemini 2.0 with web search to find and curate recent news articles
    across configured topics. This is a more intelligent alternative to NewsAPI
    that can provide better curation and real-time information.
    
    Args:
        config: Optional Config object. If None, loads from environment.
    
    Returns:
        List of Article objects
        
    Raises:
        Exception: If Gemini API call fails
    """
    logger.info("Fetching news articles using Gemini with web search...")
    
    if config is None:
        config = get_config()
    
    api_key = config.get('GEMINI_API_KEY')
    topics = config.get_news_topics()
    
    # Calculate target articles - aim for more raw material for better curation
    # Use 100 total articles distributed across topics for better selection
    target_articles = 100
    
    try:
        import google.generativeai as genai
        
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        
        # Use Gemini 2.5 Pro for high-quality news curation with web search capability
        # Note: Using simpler approach for now - may need model with search capability
        model = genai.GenerativeModel('gemini-2.5-pro')
        
        # Create specific, token-efficient prompt that requests web search
        prompt = f"""
        Please search the web and find exactly {target_articles} of today's most important news articles across these topics: {', '.join(topics)}
        
        REQUIREMENTS:
        - Use web search to find articles published in the last 24 hours only
        - Mix of breaking news and significant developments  
        - Credible sources (major news outlets, tech publications, business journals)
        - Distribute roughly evenly across topics: {', '.join(topics)}
        
        FORMAT each article as:
        TITLE: [exact headline]
        SOURCE: [publication name]
        URL: [if available, otherwise 'N/A']
        SUMMARY: [exactly 2 sentences describing key facts]
        ---
        
        IMPORTANT: Keep summaries brief - there will be further AI processing later.
        Focus on factual content, not opinions.
        Return exactly {target_articles} articles total.
        Please use your web search capabilities to find current, real-time news.
        """
        
        logger.info(f"Requesting {target_articles} articles from Gemini across topics: {', '.join(topics)}")
        
        # Make the API call - using basic model for now
        # The model should automatically use web search when needed
        response = model.generate_content(prompt)
        
        # Parse the response
        articles = _parse_gemini_news_response(response.text)
        
        logger.info(f"✓ Fetched {len(articles)} news articles from Gemini web search")
        return articles
        
    except Exception as e:
        logger.error(f"Gemini news fetch error: {e}")
        raise Exception(f"Failed to fetch news articles with Gemini: {e}")


def _parse_gemini_news_response(response_text: str) -> List[Article]:
    """
    Parse Gemini's response text into Article objects.
    
    Expects format:
    TITLE: [headline]
    SOURCE: [source]
    URL: [url]
    SUMMARY: [summary]
    ---
    
    Args:
        response_text: Raw text response from Gemini
        
    Returns:
        List of Article objects
    """
    articles = []
    
    # Split response by article separators
    article_blocks = response_text.split('---')
    
    for block in article_blocks:
        block = block.strip()
        if not block:
            continue
            
        try:
            # Parse each field
            lines = [line.strip() for line in block.split('\n') if line.strip()]
            
            title = ""
            source = ""
            url = ""
            summary = ""
            
            for line in lines:
                if line.startswith('TITLE:'):
                    title = line[6:].strip()
                elif line.startswith('SOURCE:'):
                    source = line[7:].strip()
                elif line.startswith('URL:'):
                    url_text = line[4:].strip()
                    url = url_text if url_text != 'N/A' else ""
                elif line.startswith('SUMMARY:'):
                    summary = line[8:].strip()
            
            # Only create article if we have essential fields
            if title and source:
                article = Article(
                    title=title,
                    source=source,
                    url=url,
                    content=summary,  # Use summary as content since we don't have full text
                    summary=""  # Leave empty, will be processed later in the pipeline
                )
                articles.append(article)
                
        except Exception as e:
            logger.warning(f"Failed to parse article block: {e}")
            continue
    
    return articles


def get_new_podcast_episodes(config=None) -> List[PodcastEpisode]:
    """
    Fetch new podcast episodes from Taddy GraphQL API.
    
    Args:
        config: Optional Config object. If None, loads from environment.
    
    Returns:
        List of PodcastEpisode objects
        
    Raises:
        Exception: If API call fails
    """
    logger.info("Fetching new podcast episodes...")
    
    if config is None:
        config = get_config()
    api_key = config.get('TADDY_API_KEY')
    user_id = config.get('TADDY_USER_ID')
    
    # Hardcoded popular podcasts for initial implementation
    # These can be made configurable in a future iteration
    POPULAR_PODCASTS = [
        {
            'uuid': 'dacd25f2-7433-497b-8759-93d6daa3ceea',
            'name': 'TechCrunch Startup News',
            'category': 'Technology'
        },
        {
            'uuid': 'f371face-6b5d-4733-831f-3d242026248c', 
            'name': 'Planet Money',
            'category': 'Business'
        },
        {
            'uuid': 'ac48632f-be29-457e-9349-c03ffc17f684',
            'name': 'Science Talk',
            'category': 'Science'
        },
        {
            'uuid': '0e6d82bb-0da1-447f-84bd-1ef6cd596c2c',
            'name': 'Recode Daily',
            'category': 'Technology'
        }
    ]
    
    all_episodes = []
    
    try:
        import requests
        import json
        import re
        
        for podcast in POPULAR_PODCASTS:
            logger.info(f"Fetching episodes for {podcast['name']} ({podcast['category']})")
            
            # GraphQL query to get recent episodes from this podcast
            graphql_query = {
                "query": f"""{{
                    getPodcastSeries(uuid: "{podcast['uuid']}") {{
                        uuid
                        name
                        episodes(limitPerPage: 3) {{
                            uuid
                            name
                            description
                            audioUrl
                            datePublished
                        }}
                    }}
                }}"""
            }
            
            headers = {
                'Content-Type': 'application/json',
                'X-USER-ID': user_id,
                'X-API-KEY': api_key
            }
            
            response = requests.post(
                'https://api.taddy.org/graphql',
                json=graphql_query,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Check for GraphQL errors
            if 'errors' in data:
                error_messages = [error.get('message', 'Unknown error') for error in data['errors']]
                logger.error(f"GraphQL errors for {podcast['name']}: {error_messages}")
                continue
            
            # Parse episodes
            podcast_data = data.get('data', {}).get('getPodcastSeries', {})
            if not podcast_data:
                logger.warning(f"No data returned for podcast {podcast['name']}")
                continue
                
            episodes = podcast_data.get('episodes', [])
            
            for episode_data in episodes:
                if not episode_data.get('name') or not episode_data.get('audioUrl'):
                    continue
                
                # Clean up HTML tags from description for better readability
                description = episode_data.get('description', '')
                if description:
                    # Remove HTML tags using regex
                    description = re.sub(r'<[^>]+>', '', description)
                    # Clean up extra whitespace
                    description = re.sub(r'\s+', ' ', description).strip()
                
                episode = PodcastEpisode(
                    podcast_title=podcast_data.get('name', 'Unknown Podcast'),
                    episode_title=episode_data.get('name', 'Unknown Episode'),
                    url=episode_data.get('audioUrl', '')
                )
                all_episodes.append(episode)
        
        logger.info(f"✓ Fetched {len(all_episodes)} podcast episodes across {len(POPULAR_PODCASTS)} podcasts")
        return all_episodes
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Podcast API request failed: {e}")
        # Try to get more details from the response if available
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_details = e.response.json()
                logger.error(f"API error details: {error_details}")
                if 'errors' in error_details:
                    error_messages = [error.get('message', 'Unknown error') for error in error_details['errors']]
                    raise Exception(f"Podcast API GraphQL errors: {'; '.join(error_messages)}")
                raise Exception(f"Podcast API error: {error_details}")
            except json.JSONDecodeError:
                pass
        raise Exception(f"Failed to fetch podcast episodes: {e}")
    except KeyError as e:
        logger.error(f"Unexpected podcast API response format: {e}")
        raise Exception(f"Invalid podcast API response: {e}")
    except Exception as e:
        logger.error(f"Podcast episodes fetch error: {e}")
        raise 