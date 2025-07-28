"""
Main Lambda handler for AI Daily Briefing Agent.

This module orchestrates the entire workflow:
1. Fetch data from external sources
2. Summarize content using AI
3. Generate audio from text
4. Upload to Google Drive
"""

import logging
from datetime import datetime
from typing import Dict, Any

from config import get_config, ConfigurationError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler function.
    
    Args:
        event: AWS Lambda event data
        context: AWS Lambda context object
        
    Returns:
        Response dictionary with status and message
    """
    try:
        logger.info("Starting AI Daily Briefing Agent...")
        
        # Load configuration
        config = get_config()
        config.validate_config()
        
        # TODO: Implement workflow for each milestone
        # Milestone 1: Data aggregation
        # Milestone 2: AI summarization  
        # Milestone 3: Audio generation & delivery
        
        result = generate_daily_briefing()
        
        return {
            'statusCode': 200,
            'body': {
                'message': 'Daily briefing generated successfully',
                'timestamp': datetime.utcnow().isoformat(),
                'result': result
            }
        }
        
    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        return {
            'statusCode': 500,
            'body': {
                'error': 'Configuration error',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
        }
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': {
                'error': 'Internal server error',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
        }


def generate_daily_briefing() -> Dict[str, Any]:
    """
    Generate the complete daily briefing.
    
    This function will be expanded in each milestone:
    - Milestone 1: Fetch and assemble raw data ✅
    - Milestone 2: Add AI summarization ✅
    - Milestone 3: Add audio generation and upload
    
    Returns:
        Dictionary containing briefing results
    """
    logger.info("Generating daily briefing...")
    
    try:
        # Import data fetching and summarization functions
        from data_fetchers import get_weather, get_news_articles, get_new_podcast_episodes
        from summarizer import summarize_articles, create_briefing_script
        
        # Milestone 1: Fetch all raw data
        logger.info("Fetching weather data...")
        weather_data = get_weather()
        
        logger.info("Fetching news articles...")
        news_articles = get_news_articles()
        
        logger.info("Fetching podcast episodes...")
        podcast_episodes = get_new_podcast_episodes()
        
        # Milestone 2: AI Summarization
        logger.info("Summarizing articles with AI...")
        summarized_articles = summarize_articles(news_articles)
        
        logger.info("Creating final briefing script...")
        briefing_script = create_briefing_script(weather_data, summarized_articles, podcast_episodes)
        
        # Save both versions to local files
        raw_briefing_file = "briefing_raw.txt"
        final_briefing_file = "briefing.txt"
        
        # Save raw version for comparison
        raw_briefing_text = assemble_briefing_text(weather_data, news_articles, podcast_episodes)
        with open(raw_briefing_file, 'w', encoding='utf-8') as f:
            f.write(raw_briefing_text)
        
        # Save AI-enhanced version
        with open(final_briefing_file, 'w', encoding='utf-8') as f:
            f.write(briefing_script)
        
        logger.info(f"✓ AI-enhanced daily briefing saved to {final_briefing_file}")
        logger.info(f"✓ Raw briefing saved to {raw_briefing_file} for comparison")
        
        return {
            'status': 'success',
            'message': f'AI-enhanced daily briefing generated and saved to {final_briefing_file}',
            'milestone': 2,
            'data': {
                'weather': weather_data,
                'articles_count': len(news_articles),
                'summarized_articles': len(summarized_articles),
                'podcasts_count': len(podcast_episodes),
                'final_script_file': final_briefing_file,
                'raw_file': raw_briefing_file
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to generate daily briefing: {e}")
        return {
            'status': 'error',
            'message': f'Briefing generation failed: {e}',
            'milestone': 2
        }


def main():
    """
    Main function for local testing.
    
    This allows running the briefing generator locally during development.
    """
    print("AI Daily Briefing Agent - Local Test Mode")
    print("=" * 50)
    
    try:
        result = generate_daily_briefing()
        print(f"Result: {result}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def assemble_briefing_text(weather_data, news_articles, podcast_episodes) -> str:
    """
    Assemble raw data into a cohesive text briefing.
    
    Args:
        weather_data: WeatherData object
        news_articles: List of Article objects
        podcast_episodes: List of PodcastEpisode objects
        
    Returns:
        Complete briefing text
    """
    from datetime import datetime
    
    # Start with header
    current_time = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
    briefing_parts = [
        "=" * 60,
        "AI DAILY BRIEFING",
        f"Generated on {current_time}",
        "=" * 60,
        ""
    ]
    
    # Weather section
    briefing_parts.extend([
        "🌤️  WEATHER UPDATE",
        "-" * 30,
        f"Location: {weather_data.city}, {weather_data.country}",
        f"Temperature: {weather_data.temperature}°C",
        f"Conditions: {weather_data.description.title()}",
        f"Humidity: {weather_data.humidity}%",
        f"Wind Speed: {weather_data.wind_speed} m/s",
        ""
    ])
    
    # News section
    briefing_parts.extend([
        "📰 NEWS HEADLINES",
        "-" * 30
    ])
    
    if news_articles:
        for i, article in enumerate(news_articles, 1):
            briefing_parts.extend([
                f"{i}. {article.title}",
                f"   Source: {article.source}",
                f"   URL: {article.url}",
                f"   Content: {article.content[:200]}..." if len(article.content) > 200 else f"   Content: {article.content}",
                ""
            ])
    else:
        briefing_parts.extend(["No news articles available.", ""])
    
    # Podcast section
    briefing_parts.extend([
        "🎧 NEW PODCAST EPISODES",
        "-" * 30
    ])
    
    if podcast_episodes:
        for i, episode in enumerate(podcast_episodes, 1):
            briefing_parts.extend([
                f"{i}. {episode.episode_title}",
                f"   Podcast: {episode.podcast_title}",
                f"   URL: {episode.url}",
                ""
            ])
    else:
        briefing_parts.extend(["No new podcast episodes available.", ""])
    
    # Footer
    briefing_parts.extend([
        "=" * 60,
        "End of Daily Briefing",
        "=" * 60
    ])
    
    return "\n".join(briefing_parts)


if __name__ == "__main__":
    main() 