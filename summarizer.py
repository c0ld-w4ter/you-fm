"""
Summarizer module for AI Daily Briefing Agent.

This module interfaces with the Google Gemini API to generate
concise summaries of news articles and other content.
"""

import logging
from typing import List
from data_fetchers import Article

from config import get_config, Config

logger = logging.getLogger(__name__)


def filter_articles_by_keywords(articles: List[Article], excluded_keywords: List[str]) -> List[Article]:
    """
    Filter articles to exclude those containing specified keywords.
    
    Args:
        articles: List of Article objects to filter
        excluded_keywords: List of keywords to avoid (case-insensitive)
        
    Returns:
        Filtered list of Article objects
    """
    if not excluded_keywords:
        return articles
    
    filtered_articles = []
    excluded_count = 0
    
    for article in articles:
        # Check title and content for excluded keywords (case-insensitive)
        article_text = f"{article.title} {article.content}".lower()
        
        contains_excluded = False
        for keyword in excluded_keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in article_text:
                contains_excluded = True
                logger.info(f"Filtering out article '{article.title}' due to keyword: {keyword}")
                break
        
        if not contains_excluded:
            filtered_articles.append(article)
        else:
            excluded_count += 1
    
    logger.info(f"Keyword filtering: {len(articles)} → {len(filtered_articles)} articles ({excluded_count} filtered out)")
    return filtered_articles


def generate_style_instructions(tone: str, depth: str, listener_name: str = "") -> dict:
    """
    Generate AI prompt instructions based on user style preferences.
    
    Args:
        tone: User's preferred briefing tone
        depth: User's preferred content depth
        listener_name: Name for personalization
        
    Returns:
        Dictionary with tone and depth instruction strings
    """
    tone_instructions = {
        'professional': "Maintain a professional, authoritative tone suitable for business news. Use formal language and clear, direct statements.",
        'casual': "Use a friendly, conversational tone like talking to a friend. Keep it relaxed but informative, with natural transitions.", 
        'energetic': "Use an upbeat, engaging tone with enthusiasm. Keep the energy high while remaining informative and clear."
    }
    
    depth_instructions = {
        'headlines': "Focus on headlines and key facts only. Keep each story to 1-2 sentences maximum. Prioritize breadth over depth.",
        'balanced': "Provide balanced coverage with key details and context. Give each important story 2-3 sentences with essential background.",
        'detailed': "Include detailed analysis, background context, and implications. Provide comprehensive coverage with 3-4 sentences per major story."
    }
    
    tone_instruction = tone_instructions.get(tone, tone_instructions['professional'])
    depth_instruction = depth_instructions.get(depth, depth_instructions['balanced'])
    
    # Add personalization for non-professional tones
    if tone in ['casual', 'energetic'] and listener_name:
        tone_instruction += f" Address {listener_name} directly when appropriate to make it feel personal."
    
    return {
        'tone': tone_instruction,
        'depth': depth_instruction
    }


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


def create_briefing_script(weather_data, articles: List[Article], config=None) -> str:
    """
    Create the final briefing script from all data sources using AI.
    Performs both article summarization and script generation in a single API call for optimal performance.
    
    Args:
        weather_data: WeatherData object
        articles: List of raw Article objects (not pre-summarized)
        config: Optional Config object. If None, loads from environment.
        
    Returns:
        Complete script text ready for text-to-speech
    """
    logger.info("Creating AI-generated briefing script with batch article processing...")
    
    try:
        import google.generativeai as genai
        from datetime import datetime
        
        # Get configuration
        if config is None:
            config = get_config()
        api_key = config.get('GEMINI_API_KEY')
        
        # Get advanced settings
        briefing_tone = config.get_briefing_tone()
        content_depth = config.get_content_depth()
        excluded_keywords = config.get_keywords_exclude()
        listener_name = config.get_listener_name()
        briefing_duration = config.get_briefing_duration_minutes()
        
        # Get personalization settings
        specific_interests = config.get_specific_interests()
        # briefing_goal removed for UI simplification
        followed_entities = config.get_followed_entities()
        hobbies = config.get_hobbies()
        favorite_teams_artists = config.get_favorite_teams_artists()
        passion_topics = config.get_passion_topics()
        greeting_preference = config.get_greeting_preference()
        daily_routine_detail = config.get_daily_routine_detail()
        
        # Filter articles by excluded keywords
        if articles and excluded_keywords:
            articles = filter_articles_by_keywords(articles, excluded_keywords)
            if not articles:
                logger.warning("All articles were filtered out by keyword exclusion!")
        
        # Generate style-specific instructions
        style_instructions = generate_style_instructions(briefing_tone, content_depth, listener_name)
        
        # Build user profile from personalization data
        user_profile_parts = []
        
        if listener_name:
            user_profile_parts.append(f"Name: {listener_name}")
        
        # News & Information Preferences
        if specific_interests:
            user_profile_parts.append(f"Specific Interests: {specific_interests}")
        # briefing_goal section removed for UI simplification
        if followed_entities:
            user_profile_parts.append(f"Followed Entities: {followed_entities}")
        
        # Hobbies & Personal Interests
        if hobbies:
            user_profile_parts.append(f"Hobbies: {hobbies}")
        if favorite_teams_artists:
            user_profile_parts.append(f"Favorite Teams/Artists: {favorite_teams_artists}")
        if passion_topics:
            user_profile_parts.append(f"Passion Topics: {passion_topics}")
        
        # Personal Quirks & Style
        if greeting_preference:
            user_profile_parts.append(f"Preferred Greeting: {greeting_preference}")
        if daily_routine_detail:
            user_profile_parts.append(f"Daily Routine: {daily_routine_detail}")
        
        user_profile = "\n".join(user_profile_parts) if user_profile_parts else "No personalization data provided"
        
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


        
        # Create enhanced prompt for combined summarization and script generation with style awareness
        listener_greeting = f" for {listener_name}" if listener_name else ""
        prompt = f"""You are an AI assistant creating a personalized daily news briefing script{listener_greeting}. You need to:

1. ANALYZE and SUMMARIZE the provided news articles
2. SELECT the most important and newsworthy stories that fit within the target duration
3. GENERATE a natural, engaging, conversational script for a professional news anchor

Date: {current_date}
Listener: {listener_name if listener_name else "General audience"}
Target Duration: {briefing_duration} minutes

CRITICAL REQUIREMENTS:
- The script MUST be long enough to fill {briefing_duration} minutes when read aloud at a normal pace
- Assume a speaking rate of approximately 150-160 words per minute
- This means the script should be approximately {briefing_duration * 150} to {briefing_duration * 160} words long
{"- You MUST start the briefing with EXACTLY this greeting: '" + greeting_preference + "'" if greeting_preference else "- Start with a warm, professional greeting"}

USER PROFILE:
{user_profile}

PERSONALIZATION REQUIREMENTS:
- Actively incorporate the user's interests, followed entities, hobbies, and passion topics throughout the briefing
- When selecting news stories, give strong preference to topics that match the user profile
- Make explicit connections between news stories and the user's stated interests
- Reference the user's hobbies or passion topics when relevant to make the briefing feel personal

STYLE PREFERENCES:
TONE: {style_instructions['tone']}
DEPTH: {style_instructions['depth']}

AVAILABLE DATA:

WEATHER:
{weather_info}

NEWS ARTICLES (analyze and select the most newsworthy):
{news_info}

SCRIPT GENERATION INSTRUCTIONS:
1. {"START WITH EXACTLY THIS GREETING: '" + greeting_preference + "' then mention the date" if greeting_preference else "Create a warm greeting that matches the specified TONE and includes the date"}{f" and addresses {listener_name} by name" if listener_name and not greeting_preference else ""}
2. Present the weather information conversationally, mentioning notable conditions using the specified TONE
3. INTELLIGENTLY SELECT and SUMMARIZE news stories, giving priority to:
   - Breaking news of high importance
   - Stories directly related to the user's specific interests
   - News about their followed entities
   - Topics connected to their hobbies or passion topics
4. For a {briefing_duration}-minute briefing, include approximately {3 if briefing_duration <= 3 else 4 if briefing_duration <= 5 else 5 if briefing_duration <= 7 else 6} news stories, prioritizing quality and relevance over quantity
5. Adjust the detail level of each story based on the target duration and DEPTH preference
6. EXPLICITLY mention when a story relates to the user's interests (e.g., "Since you follow Tesla..." or "Given your interest in quantum computing...")
7. Present stories in order of general importance, then by relevance to the user
8. Include podcast recommendations naturally in the specified TONE
9. End with a positive, encouraging closing that matches the TONE{f" and includes {listener_name}'s name" if listener_name else ""}
10. Use natural transitions between sections that match the TONE
11. Follow the TONE guidelines throughout the entire script
12. Make it sound natural when spoken aloud - avoid written language patterns
13. Handle missing data gracefully without being repetitive
14. ENSURE the script is {briefing_duration * 150} to {briefing_duration * 160} words long to fill the requested {briefing_duration} minutes
15. Convert all numbers, symbols, and units to word equivalents (e.g. "35.78°C" as "thirty five point seven eight degrees Celsius", "50%" as "fifty percent")
{"16. If the user mentioned details about their daily routine, acknowledge or reference it appropriately" if daily_routine_detail else ""}

EDITORIAL GUIDELINES:
- Prioritize stories with the most significant impact or widespread interest
- Give extra weight to stories related to the user's specific interests and followed entities
- Choose recent, breaking news over older stories when possible
- Ensure variety across different topics when multiple quality options exist
- Skip duplicate or very similar stories
- Focus on stories with clear, factual content
- Balance depth vs breadth based on available time, story importance, and DEPTH preference
- Quality over quantity - better to cover fewer stories well than many stories superficially
- Consider the user's briefing goal when selecting and presenting stories

Generate only the final script text, ready for text-to-speech conversion:"""

        # Generate the briefing script with integrated summarization
        logger.info(f"Generating briefing script with style preferences: tone={briefing_tone}, depth={content_depth}")
        response = model.generate_content(prompt)
        
        final_script = response.text.strip()
        logger.info(f"✓ AI-generated briefing script created with style awareness ({len(articles)} articles processed)")
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
        
        # Create personalized closing
        closing = f"That's your briefing for today{f', {listener_name}' if listener_name else ''}. Have a great day!"
        fallback_parts.append(closing)
        
        return " ".join(fallback_parts) 