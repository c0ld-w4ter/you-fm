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


def create_briefing_script(weather_data, articles: List[Article], podcast_episodes) -> str:
    """
    Create the final briefing script from all data sources using AI.
    Performs both article summarization and script generation in a single API call for optimal performance.
    
    Args:
        weather_data: WeatherData object
        articles: List of raw Article objects (not pre-summarized)
        podcast_episodes: List of PodcastEpisode objects
        
    Returns:
        Complete script text ready for text-to-speech
    """
    logger.info("Creating AI-generated briefing script with batch article processing...")
    
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

        # Build raw news articles information
        news_info = "No news articles available"
        if articles:
            news_items = []
            for i, article in enumerate(articles[:8], 1):  # Limit to top 8 for context management
                content = article.content if article.content else "No content available"
                news_items.append(f"""
Article {i}:
Title: {article.title}
Source: {article.source}
Content: {content}
""")
            news_info = "\n".join(news_items)
        
        # Build podcast information
        podcast_info = "No new podcast episodes available"
        if podcast_episodes:
            podcast_items = []
            
            # Better selection: get episodes from different podcasts for variety
            podcast_counts = {}
            selected_episodes = []
            
            for episode in podcast_episodes:
                podcast_title = episode.podcast_title
                if podcast_title not in podcast_counts:
                    podcast_counts[podcast_title] = 0
                
                # Only add if we haven't reached the limit for this podcast and overall limit
                if podcast_counts[podcast_title] < 1 and len(selected_episodes) < 3:
                    selected_episodes.append(episode)
                    podcast_counts[podcast_title] += 1
            
            # If we still have room and want more variety, add more episodes
            if len(selected_episodes) < 3:
                for episode in podcast_episodes:
                    if episode not in selected_episodes and len(selected_episodes) < 3:
                        selected_episodes.append(episode)
            
            for i, episode in enumerate(selected_episodes, 1):
                podcast_items.append(f"{i}. '{episode.episode_title}' from {episode.podcast_title}")
            podcast_info = "\n".join(podcast_items)
        
        # Get briefing duration and listener name from configuration
        briefing_duration = config.get_briefing_duration_minutes()
        listener_name = config.get_listener_name()
        
        # Create enhanced prompt for combined summarization and script generation
        listener_greeting = f" for {listener_name}" if listener_name else ""
        prompt = f"""You are an AI assistant creating a personalized daily news briefing script{listener_greeting}. You need to:

1. ANALYZE and SUMMARIZE the provided news articles
2. SELECT the most important and newsworthy stories that fit within the target duration
3. GENERATE a natural, engaging, conversational script for a professional news anchor

Date: {current_date}
Listener: {listener_name if listener_name else "General audience"}
Target Duration: {briefing_duration} minutes

AVAILABLE DATA:

WEATHER:
{weather_info}

NEWS ARTICLES (analyze and select the most newsworthy):
{news_info}

PODCAST EPISODES:
{podcast_info}

SCRIPT GENERATION INSTRUCTIONS:
1. Create a warm, professional greeting that includes the date{f" and addresses {listener_name} by name" if listener_name else ""}
2. Present the weather information conversationally, mentioning notable conditions
3. INTELLIGENTLY SELECT and SUMMARIZE the most important/interesting news stories from the articles above
4. Use your editorial judgment to determine how many stories to include and how much detail to provide based on the {briefing_duration}-minute target duration
5. For each selected story, provide an appropriate summary length that balances comprehensiveness with time constraints
6. Present stories in order of importance/interest
7. Include podcast recommendations naturally
8. End with a positive, encouraging closing{f" that includes {listener_name}'s name" if listener_name else ""}
9. Use natural transitions between sections
10. Keep the tone informative but friendly{f" and personal to {listener_name}" if listener_name else ""}
11. Make it sound natural when spoken aloud - avoid written language patterns
12. Handle missing data gracefully without being repetitive
13. Target the script length to fit comfortably within a {briefing_duration}-minute audio briefing
14. Convert all numbers, symbols, and units to word equivalents (e.g. "35.78°C" as "thirty five point seven eight degrees Celsius", "50%" as "fifty percent")

EDITORIAL GUIDELINES:
- Prioritize stories with the most significant impact or widespread interest
- Choose recent, breaking news over older stories when possible
- Ensure variety across different topics when multiple quality options exist
- Skip duplicate or very similar stories
- Focus on stories with clear, factual content
- Balance depth vs breadth based on available time and story importance
- Quality over quantity - better to cover fewer stories well than many stories superficially

Generate only the final script text, ready for text-to-speech conversion:"""

        # Generate the briefing script with integrated summarization
        logger.info("Generating briefing script with integrated article summarization...")
        response = model.generate_content(prompt)
        
        final_script = response.text.strip()
        logger.info(f"✓ AI-generated briefing script created with batch processing ({len(articles)} articles processed)")
        return final_script
        
    except Exception as e:
        logger.error(f"Failed to generate AI briefing script with batch processing: {e}")
        logger.info("Falling back to simple script generation...")
        
        # Fallback to a basic script if AI generation fails
        from datetime import datetime
        current_time = datetime.now().strftime("%A, %B %d")
        
        # Get briefing duration and listener name for fallback script (with safe fallback)
        try:
            config = get_config()
            briefing_duration = config.get_briefing_duration_minutes()
            listener_name = config.get_listener_name()
        except Exception:
            briefing_duration = 3  # Default fallback duration
            listener_name = ""  # Default to no name
        
        # Create personalized greeting
        greeting = f"Good morning{f', {listener_name}' if listener_name else ''}! Here's your daily briefing for {current_time}."
        fallback_parts = [greeting]
        
        if weather_data:
            fallback_parts.append(f"The weather in {weather_data.city} is {weather_data.temperature}°C with {weather_data.description.lower()}.")
        
        if articles:
            fallback_parts.append("Here are today's top news stories:")
            for i, article in enumerate(articles[:3], 1):
                # Use truncated content as fallback summary
                content = article.content[:150] + "..." if len(article.content) > 150 else article.content
                fallback_parts.append(f"{article.title}: {content}")
        
        if podcast_episodes:
            fallback_parts.append("New podcast episodes are available from " + 
                                ", ".join([ep.podcast_title for ep in podcast_episodes[:2]]))
        
        # Create personalized closing
        closing = f"That's your briefing for today{f', {listener_name}' if listener_name else ''}. Have a great day!"
        fallback_parts.append(closing)
        
        return " ".join(fallback_parts) 