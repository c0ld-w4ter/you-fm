"""
Summarizer module for AI Daily Briefing Agent.

This module interfaces with the Google Gemini API to generate
concise summaries of news articles and other content.
"""

import logging
from typing import List
from data_fetchers import Article

from config import get_config

logger = logging.getLogger(__name__)


def summarize_articles(articles: List[Article]) -> List[Article]:
    """
    Summarize a list of articles using Google Gemini API.
    
    Args:
        articles: List of Article objects to summarize
        
    Returns:
        List of Article objects with populated summary fields
        
    Raises:
        Exception: If Gemini API call fails
    """
    logger.info(f"Summarizing {len(articles)} articles...")
    
    if not articles:
        logger.info("No articles to summarize")
        return articles
    
    try:
        import google.generativeai as genai
        
        # Get configuration
        config = get_config()
        api_key = config.get('GEMINI_API_KEY')
        
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        
        # Use Gemini 2.5 Pro for high-quality summarization
        model = genai.GenerativeModel('gemini-2.5-pro')
        
        # Summarize each article
        for i, article in enumerate(articles, 1):
            logger.info(f"Summarizing article {i}/{len(articles)}: {article.title}")
            
            try:
                # Create a prompt for summarization
                prompt = f"""
Please provide a concise, informative summary of this news article in 2-3 sentences.
Focus on the key facts, main points, and any important implications.
Keep the summary objective and factual.

Article Title: {article.title}
Source: {article.source}
Content: {article.content}

Summary:"""

                # Call Gemini API
                response = model.generate_content(prompt)
                
                # Update the article with the summary
                article.summary = response.text.strip()
                logger.info(f"✓ Successfully summarized: {article.title}")
                
            except Exception as e:
                logger.error(f"Failed to summarize article '{article.title}': {e}")
                # Fallback to truncated content
                article.summary = f"[Auto-summary unavailable] {article.content[:200]}..." if len(article.content) > 200 else article.content
                
        logger.info("✓ Article summarization completed")
        return articles
        
    except Exception as e:
        logger.error(f"Gemini API setup failed: {e}")
        # Fallback: use truncated content as summary
        for article in articles:
            article.summary = f"[Summary unavailable] {article.content[:200]}..." if len(article.content) > 200 else article.content
        
        raise Exception(f"Failed to summarize articles with Gemini API: {e}")


def create_briefing_script(weather_data, summarized_articles: List[Article], podcast_episodes) -> str:
    """
    Create the final briefing script from all data sources using AI.
    
    Args:
        weather_data: WeatherData object
        summarized_articles: List of summarized Article objects
        podcast_episodes: List of PodcastEpisode objects
        
    Returns:
        Complete script text ready for text-to-speech
    """
    logger.info("Creating AI-generated briefing script...")
    
    try:
        import google.generativeai as genai
        from datetime import datetime
        
        # Get configuration
        config = get_config()
        api_key = config.get('GEMINI_API_KEY')
        
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        
        # Use Gemini 2.5 Pro for high-quality script generation
        model = genai.GenerativeModel('gemini-2.5-pro')
        
        # Prepare data for the prompt
        current_date = datetime.now().strftime("%A, %B %d, %Y")
        
        # Build weather information
        weather_info = "No weather data available"
        if weather_data:
            weather_info = f"""Weather in {weather_data.city}, {weather_data.country}:
- Temperature: {weather_data.temperature}°C
- Conditions: {weather_data.description}
- Humidity: {weather_data.humidity}%
- Wind Speed: {weather_data.wind_speed} m/s"""

        # Build news summaries
        news_info = "No news articles available"
        if summarized_articles:
            news_items = []
            for i, article in enumerate(summarized_articles[:5], 1):  # Limit to top 5
                summary = article.summary if hasattr(article, 'summary') and article.summary else article.content[:150] + "..."
                news_items.append(f"{i}. {article.title} (Source: {article.source})\n   Summary: {summary}")
            news_info = "\n".join(news_items)
        
        # Build podcast information
        podcast_info = "No new podcast episodes available"
        if podcast_episodes:
            podcast_items = []
            for i, episode in enumerate(podcast_episodes[:3], 1):  # Limit to top 3
                podcast_items.append(f"{i}. '{episode.episode_title}' from {episode.podcast_title}")
            podcast_info = "\n".join(podcast_items)
        
        # Create comprehensive prompt for script generation
        prompt = f"""You are an AI assistant creating a personalized daily news briefing script. Generate a natural, engaging, and conversational script that sounds like it's being read by a professional news anchor or podcast host.

Date: {current_date}

AVAILABLE DATA:

WEATHER:
{weather_info}

NEWS ARTICLES:
{news_info}

PODCAST EPISODES:
{podcast_info}

INSTRUCTIONS:
1. Create a warm, professional greeting that includes the date
2. Present the weather in a conversational way, mentioning notable conditions (high humidity, strong winds, etc.)
3. Introduce the news section naturally and present each story clearly
4. Include the podcast recommendations in an engaging way
5. End with a positive, encouraging closing
6. Use natural transitions between sections
7. Keep the tone informative but friendly
8. Make it sound natural when spoken aloud
9. If any data is missing, handle it gracefully without being repetitive
10. Total length should be appropriate for a 2-3 minute audio briefing

Generate only the script text, ready for text-to-speech conversion:"""

        # Generate the briefing script
        logger.info("Generating briefing script with Gemini 2.5 Pro...")
        response = model.generate_content(prompt)
        
        final_script = response.text.strip()
        logger.info("✓ AI-generated briefing script created")
        return final_script
        
    except Exception as e:
        logger.error(f"Failed to generate AI briefing script: {e}")
        logger.info("Falling back to simple script generation...")
        
        # Fallback to a basic script if AI generation fails
        from datetime import datetime
        current_time = datetime.now().strftime("%A, %B %d")
        
        fallback_parts = [f"Good morning! Here's your daily briefing for {current_time}."]
        
        if weather_data:
            fallback_parts.append(f"The weather in {weather_data.city} is {weather_data.temperature}°C with {weather_data.description.lower()}.")
        
        if summarized_articles:
            fallback_parts.append("Here are today's top news stories:")
            for i, article in enumerate(summarized_articles[:3], 1):
                summary = article.summary if hasattr(article, 'summary') and article.summary else article.content[:100] + "..."
                fallback_parts.append(f"{summary}")
        
        if podcast_episodes:
            fallback_parts.append("New podcast episodes are available from " + 
                                ", ".join([ep.podcast_title for ep in podcast_episodes[:2]]))
        
        fallback_parts.append("That's your briefing for today. Have a great day!")
        
        return " ".join(fallback_parts) 