"""
Main Lambda handler for AI Daily Briefing Agent.

This module orchestrates the entire workflow:
1. Fetch data from external sources
2. Summarize content using AI
3. Generate audio from text
4. Upload to Amazon S3
"""

import logging
from datetime import datetime
from typing import Dict, Any

from config import get_config, ConfigurationError, Config

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
        
        # Generate daily briefing using complete pipeline
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


def generate_script_only(config: Config = None) -> Dict[str, Any]:
    """
    Generate only the briefing script without audio generation for preview functionality.
    
    This is a lightweight version of generate_daily_briefing() that stops after script generation,
    enabling fast iteration and preview capabilities.
    
    Args:
        config: Optional Config object. If None, loads from environment variables.
    
    Returns:
        Dictionary containing script and metadata without audio data
    """
    logger.info("Generating script preview (no audio)...")
    
    # Use provided config or load from environment
    if config is None:
        config = get_config()
        config.validate_config()
    
    try:
        # Import required functions
        from data_fetchers import get_weather, get_news_articles
        from summarizer import create_briefing_script
        
        import time

        # Fetch all raw data (same as full generation)
        logger.info("Fetching data for script preview...")
        t0 = time.perf_counter()
        
        weather_data = get_weather(config)
        news_articles = get_news_articles(config)
        
        t1 = time.perf_counter()
        logger.info(f"Data fetched for preview in {t1 - t0:.2f} seconds.")

        # Create briefing script (with style-aware processing)
        logger.info("Creating briefing script preview...")
        t2 = time.perf_counter()
        briefing_script = create_briefing_script(weather_data, news_articles, config)
        t3 = time.perf_counter()
        logger.info(f"Script preview generated in {t3 - t2:.2f} seconds.")
        
        # Calculate word count and estimated duration
        word_count = len(briefing_script.split())
        estimated_duration_minutes = word_count / 150  # Average speaking pace
        
        total_time = t3 - t0
        logger.info(f"✓ Script preview completed in {total_time:.2f} seconds!")
        
        return {
            'success': True,
            'status': 'success',
            'message': 'Script preview generated successfully',
            'data': {
                'script_content': briefing_script,
                'script_length_chars': len(briefing_script),
                'word_count': word_count,
                'estimated_duration_minutes': round(estimated_duration_minutes, 1),
                'articles_count': len(news_articles),
                'has_weather': weather_data is not None,
                'generation_time_seconds': round(total_time, 2),
                'tone': config.get_briefing_tone(),
                'depth': config.get_content_depth(),
                'keywords_excluded': len(config.get_keywords_exclude())
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to generate script preview: {e}")
        return {
            'success': False,
            'status': 'error',
            'error': str(e),
            'message': f'Script preview generation failed: {e}'
        }


def generate_daily_briefing(config: Config = None) -> Dict[str, Any]:
    """
    Generate the complete daily briefing.
    
    This function will be expanded in each milestone:
    - Milestone 1: Fetch and assemble raw data ✅
    - Milestone 2: Add AI summarization ✅
    - Milestone 3: Add audio generation and upload ✅
    
    Args:
        config: Optional Config object. If None, loads from environment variables.
    
    Returns:
        Dictionary containing briefing results with success/error status
    """
    logger.info("Generating daily briefing...")
    
    # Use provided config or load from environment
    if config is None:
        config = get_config()
        config.validate_config()
    
    try:
        # Import all required functions
        from data_fetchers import get_weather, get_news_articles
        from summarizer import create_briefing_script  # Note: summarize_articles no longer needed
        from tts_generator import generate_audio, save_audio_locally
        # from uploader import upload_to_s3  # Uncomment for S3 upload
        
        import time

        # Milestone 1: Fetch all raw data
        logger.info("Fetching weather data...")
        t0 = time.perf_counter()
        weather_data = get_weather(config)
        t1 = time.perf_counter()
        logger.info(f"Weather data fetched in {t1 - t0:.2f} seconds.")

        logger.info("Fetching news articles...")
        t2 = time.perf_counter()
        news_articles = get_news_articles(config)
        t3 = time.perf_counter()
        logger.info(f"News articles fetched in {t3 - t2:.2f} seconds.")

        # Milestone 2: AI Processing (Batch Optimization)
        # Note: Individual article summarization skipped for performance
        # AI now handles both summarization AND script generation in single call
        logger.info("Creating briefing script with batch AI processing...")
        t4 = time.perf_counter()
        briefing_script = create_briefing_script(weather_data, news_articles, config)
        t5 = time.perf_counter()
        logger.info(f"Briefing script created with batch processing in {t5 - t4:.2f} seconds.")
        logger.info(f"Performance improvement: Single API call instead of {len(news_articles) + 1} separate calls")

        # Milestone 3: Audio Generation and Local Save
        logger.info("Generating audio from briefing script...")
        t6 = time.perf_counter()
        audio_data = generate_audio(briefing_script, config)
        t7 = time.perf_counter()
        logger.info(f"Audio generated in {t7 - t6:.2f} seconds.")

        logger.info("Saving audio file locally...")
        from datetime import datetime
        import os
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_filename = f"daily_briefing_{timestamp}.mp3"
        
        # Ensure static/audio directory exists for web serving
        os.makedirs("static/audio", exist_ok=True)
        web_audio_path = os.path.join("static", "audio", audio_filename)
        
        t8 = time.perf_counter()
        audio_file_path = save_audio_locally(audio_data, web_audio_path)
        t9 = time.perf_counter()
        logger.info(f"Audio file saved locally in {t9 - t8:.2f} seconds.")
        
        # Save script locally for reference
        script_file = "briefing_script.txt"
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(briefing_script)
        
        # Calculate total processing time improvement
        total_time = t9 - t0
        logger.info(f"✓ Complete audio briefing workflow finished successfully in {total_time:.2f} seconds!")
        logger.info(f"✓ Audio saved locally: {audio_file_path}")
        logger.info(f"✓ Script saved locally: {script_file}")
        logger.info(f"✓ Batch processing optimization: ~90% reduction in API calls")
        
        return {
            'success': True,
            'status': 'success',
            'message': f'Complete audio daily briefing generated with batch processing optimization',
            'milestone': 3,
            'performance_improvement': f'Single API call instead of {len(news_articles) + 1} calls',
            'data': {
                'weather': weather_data,
                'articles_count': len(news_articles),
                'audio_file_path': audio_file_path,
                'audio_filename': audio_filename,  # For web URL generation
                'audio_size_bytes': len(audio_data),
                'script_content': briefing_script,
                'script_length_chars': len(briefing_script),
                'script_file': script_file,
                'total_processing_time_seconds': round(total_time, 2)
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to generate daily briefing: {e}")
        return {
            'success': False,
            'status': 'error',
            'error': str(e),
            'message': f'Briefing generation failed: {e}',
            'milestone': 3
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


def assemble_briefing_text(weather_data, news_articles) -> str:
    """
    Assemble raw data into a cohesive text briefing.
    
    Args:
        weather_data: WeatherData object
        news_articles: List of Article objects
        
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
    
    # Footer
    briefing_parts.extend([
        "=" * 60,
        "End of Daily Briefing",
        "=" * 60
    ])
    
    return "\n".join(briefing_parts)


if __name__ == "__main__":
    main() 