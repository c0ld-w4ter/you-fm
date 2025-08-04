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


def summarize_articles_with_flash(articles: List[Article], config, api_key: str) -> List[dict]:
    """
    Use Gemini 2.5 Flash to analyze articles for both importance and relevance,
    providing variable detail based on combined scores.
    
    Args:
        articles: List of Article objects to analyze
        config: Configuration object
        api_key: Pre-configured API key
        
    Returns:
        List of dictionaries with scored and filtered articles
    """
    if not articles:
        return []
    
    logger.info(f"Starting Flash analysis for article filtering and scoring...")
    
    try:
        import google.generativeai as genai
        import json
        
        # Get user preferences for relevance scoring
        specific_interests = config.get_specific_interests() if hasattr(config, 'get_specific_interests') else config.get('SPECIFIC_INTERESTS', '')
        followed_entities = config.get_followed_entities() if hasattr(config, 'get_followed_entities') else config.get('FOLLOWED_ENTITIES', '')
        passion_topics = config.get_passion_topics() if hasattr(config, 'get_passion_topics') else config.get('PASSION_TOPICS', '')
        hobbies = config.get_hobbies() if hasattr(config, 'get_hobbies') else config.get('HOBBIES', '')
        
        # Use the pre-configured API (don't configure again)
        flash_model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Build user context for relevance scoring
        user_context_parts = []
        if specific_interests:
            user_context_parts.append(f"Specific interests: {specific_interests}")
        if followed_entities:
            user_context_parts.append(f"Followed entities: {followed_entities}")
        if passion_topics:
            user_context_parts.append(f"Passion topics: {passion_topics}")
        if hobbies:
            user_context_parts.append(f"Hobbies: {hobbies}")
        
        user_context_str = "\n".join(user_context_parts) if user_context_parts else "General news interests"
        
        # Build articles for analysis (process all available articles)
        # Let's test if Flash can handle the full dataset with improved error handling
        articles_to_analyze = articles  # Process ALL articles, not just first 50
        
        logger.info(f"Processing {len(articles_to_analyze)} articles (full dataset) with Flash analysis")
        
        articles_text = []
        for i, article in enumerate(articles_to_analyze, 1):
            content = article.content if article.content else "No content available"
            # Ensure content is a string to avoid formatting issues with mocks
            content = str(content)
            # Truncate very long articles to prevent token overflow
            if len(content) > 1000:
                content = content[:1000] + "... [truncated]"
            articles_text.append(f"""
Article {i}:
Title: {article.title}
Source: {article.source}
Content: {content}
""")
        
        prompt = f"""You are a news analysis assistant. Review these articles and create a comprehensive summary focusing on the most important and newsworthy stories.

USER INTERESTS (prioritize articles matching these):
{user_context_str}

ARTICLES TO REVIEW:
{"".join(articles_text)}

INSTRUCTIONS:
1. Focus on articles with high importance (breaking news, major events, widespread impact)
2. Give extra attention to articles matching the user's interests and topics they follow
3. For each significant article, provide:
   - Brief summary of the key points
   - Why it's important or relevant
   - Key entities/people involved

4. Organize by importance - most significant stories first
5. Aim for a comprehensive but concise overview that captures the day's most important news
6. Write in a natural, readable format - no special formatting required

Create a thorough summary of today's most important news stories."""

        response = flash_model.generate_content(prompt)
        
        # Log metrics for Flash API call
        if hasattr(response, 'usage_metadata'):
            usage = response.usage_metadata
            try:
                # Gemini 2.5 Flash pricing (as of 2025-08-01)
                # Input: $0.30 for text/image/video, $1.00 for audio
                # Output: $2.50 for all content types
                # Note: Using text/image/video rates (most common use case)
                input_cost = (usage.prompt_token_count / 1_000_000) * 0.30  # Flash input cost (text/image/video)
                output_cost = (usage.candidates_token_count / 1_000_000) * 2.50  # Flash output cost
                total_cost = input_cost + output_cost
                
                logger.info(f"Flash Analysis - Tokens: {usage.prompt_token_count} in, {usage.candidates_token_count} out, {usage.total_token_count} total")
                logger.info(f"Flash Analysis - Cost: ${input_cost:.4f} in, ${output_cost:.4f} out, ${total_cost:.4f} total")
            except (TypeError, AttributeError):
                # Handle mocked objects in tests
                logger.info("Flash Analysis - Metrics logging skipped (mocked response)")
        
        # Return the Flash summary as a simple text string
        if hasattr(response, 'text') and response.text:
            flash_summary = response.text.strip()
            logger.info(f"✓ Flash analysis completed: {len(flash_summary)} characters of summary generated")
            return flash_summary
        else:
            logger.warning("Flash response is empty")
            return None
            
    except Exception as e:
        logger.error(f"Flash analysis failed: {e}")
        return None


def create_briefing_script(weather_data, articles: List[Article], config=None) -> str:
    """
    Create the final briefing script using two-stage approach:
    1. Gemini 2.5 Flash for article analysis and filtering by importance/relevance
    2. Gemini 2.5 Pro for final personalized script generation
    
    Args:
        weather_data: WeatherData object
        articles: List of raw Article objects
        config: Optional Config object. If None, loads from environment.
        
    Returns:
        Complete script text ready for text-to-speech
    """
    logger.info("Creating AI-generated briefing script with two-stage processing...")
    
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
        
        # Filter articles by excluded keywords first
        if articles and excluded_keywords:
            articles = filter_articles_by_keywords(articles, excluded_keywords)
            if not articles:
                logger.warning("All articles were filtered out by keyword exclusion!")
        
        # Stage 1: Use Gemini 2.5 Flash for initial article analysis and filtering
        analyzed_articles = summarize_articles_with_flash(articles, config, api_key)
        
        # Check if Flash analysis succeeded
        if analyzed_articles is None:
            logger.warning("Flash analysis failed, falling back to original approach")
            # Use filtered articles directly with Pro model
            news_info = ""
            for i, article in enumerate(articles[:20], 1):  # Limit to top 20 for Pro
                news_info += f"""
Article {i}: {article.title} (Source: {article.source})
Content: {article.content[:500]}{'...' if len(article.content) > 500 else ''}
"""
        else:
            # Use Flash summary as input to Pro model
            news_info = f"""
FLASH ANALYSIS SUMMARY:
{analyzed_articles}

The above summary was generated by analyzing {len(articles)} articles and identifying the most important and relevant news stories for today's briefing.
"""
            logger.info(f"Using Flash summary ({len(analyzed_articles)} chars) as Pro model input")

        # Generate style-specific instructions
        style_instructions = generate_style_instructions(briefing_tone, content_depth, listener_name)
        
        # Build user profile from personalization data
        user_profile_parts = []
        
        if listener_name:
            user_profile_parts.append(f"Name: {listener_name}")
        
        # News & Information Preferences
        if specific_interests:
            user_profile_parts.append(f"Specific Interests: {specific_interests}")
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
        
        # Configure the Gemini API (may already be configured by Flash stage)
        genai.configure(api_key=api_key)
        
        # Stage 2: Use Gemini 2.5 Pro for high-quality script generation
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

        # Create enhanced prompt for script generation using Flash summary or fallback
        listener_greeting = f" for {listener_name}" if listener_name else ""
        
        # Determine if we're using Flash summary or fallback
        using_flash_summary = (analyzed_articles is not None)
        
        # Build greeting instruction safely to avoid formatting issues with mocks
        if greeting_preference:
            greeting_instruction = f"Start with the user's preferred greeting: '{greeting_preference}' then mention the date"
        else:
            greeting_instruction = "Create a warm greeting that matches the specified TONE and includes the date"
        
        if listener_name and not greeting_preference:
            greeting_instruction += f" and addresses {listener_name} by name"
        
        # Build closing instruction safely
        closing_instruction = "End with a positive, encouraging closing that matches the TONE"
        if listener_name:
            closing_instruction += f" and includes {listener_name}'s name"
        
        prompt = f"""You are an AI assistant creating a personalized daily news briefing script{listener_greeting}. 

{'The articles have been pre-analyzed with importance and relevance scores.' if using_flash_summary else 'You need to analyze and select the most important articles.'}

Date: {current_date}
Listener: {listener_name if listener_name else "General audience"}
Target Duration: {briefing_duration} minutes

CRITICAL REQUIREMENTS:
- The script MUST be long enough to fill {briefing_duration} minutes when read aloud at a normal pace
- Assume a speaking rate of approximately 150-160 words per minute
- This means the script should be approximately {briefing_duration * 150} to {briefing_duration * 160} words long
{f"- START WITH EXACTLY THIS GREETING: '{greeting_preference}'" if greeting_preference else "- Start with a warm, professional greeting"}

USER PROFILE:
{user_profile}

PERSONALIZATION REQUIREMENTS:
- Actively incorporate the user's interests, followed entities, hobbies, and passion topics throughout the briefing
- Make explicit connections between news stories and the user's stated interests
- Reference the user's hobbies or passion topics when relevant to make the briefing feel personal
- When selecting news stories, give strong preference to topics that match the user profile

STYLE PREFERENCES:
TONE: {style_instructions['tone']}
DEPTH: {style_instructions['depth']}

AVAILABLE DATA:

WEATHER:
{weather_info}

{'PRE-ANALYZED NEWS ARTICLES (sorted by combined importance + relevance score):' if using_flash_summary else 'NEWS ARTICLES (analyze and select the most newsworthy):'}
{news_info}

SCRIPT GENERATION INSTRUCTIONS:
1. {greeting_instruction}
2. Present the weather information conversationally, mentioning notable conditions using the specified TONE
3. {'SELECT from the pre-analyzed articles based on their scores and content detail level' if using_flash_summary else 'INTELLIGENTLY SELECT and SUMMARIZE news stories, giving priority to breaking news and user interests'}
4. For a {briefing_duration}-minute briefing, include approximately {3 if briefing_duration <= 3 else 4 if briefing_duration <= 5 else 5 if briefing_duration <= 7 else 6} news stories, prioritizing quality and relevance over quantity
5. {'Use the provided content detail (summary/detailed/full) as appropriate for each article' if using_flash_summary else 'Adjust the detail level of each story based on the target duration and DEPTH preference'}
6. EXPLICITLY mention when a story relates to the user's interests (e.g., "Since you follow Tesla..." or "Given your interest in quantum computing...")
7. {'Present stories in the order provided (already sorted by score)' if using_flash_summary else 'Present stories in order of general importance, then by relevance to the user'}
8. Include podcast recommendations naturally in the specified TONE
9. {closing_instruction}
10. Use natural transitions between sections that match the TONE
11. Follow the TONE guidelines throughout the entire script
12. Make it sound natural when spoken aloud - avoid written language patterns
13. Handle missing data gracefully without being repetitive
14. ENSURE the script is {briefing_duration * 150} to {briefing_duration * 160} words long to fill the requested {briefing_duration} minutes
15. Convert all numbers, symbols, and units to word equivalents (e.g. "35.78°C" as "thirty five point seven eight degrees Celsius", "50%" as "fifty percent")
{"16. If the user mentioned details about their daily routine, acknowledge or reference it appropriately" if daily_routine_detail else ""}

EDITORIAL GUIDELINES:
{'- Articles are pre-scored for importance and relevance - use higher-scored articles first' if using_flash_summary else '- Prioritize stories with the most significant impact or widespread interest'}
- Give extra weight to stories related to the user's specific interests and followed entities
- Ensure variety across different topics when multiple quality options exist
- Skip duplicate or very similar stories
- Focus on stories with clear, factual content
- Balance depth vs breadth based on available time, story importance, and DEPTH preference
- Quality over quantity - better to cover fewer stories well than many stories superficially

Generate only the final script text, ready for text-to-speech conversion:"""

        # Generate the final briefing script
        logger.info(f"Generating final script with Gemini 2.5 Pro (tone={briefing_tone}, depth={content_depth})")
        response = model.generate_content(prompt)
        
        # Log metrics for Pro API call
        if hasattr(response, 'usage_metadata'):
            usage = response.usage_metadata
            try:
                # Gemini 2.5 Pro tiered pricing (as of 2025-08-01)
                prompt_tokens = usage.prompt_token_count
                
                # Input pricing: $1.25 for ≤200k tokens, $2.50 for >200k tokens
                if prompt_tokens <= 200_000:
                    input_cost = (prompt_tokens / 1_000_000) * 1.25
                else:
                    input_cost = (prompt_tokens / 1_000_000) * 2.50
                
                # Output pricing: $10.00 for ≤200k tokens, $15.00 for >200k tokens  
                if prompt_tokens <= 200_000:
                    output_cost = (usage.candidates_token_count / 1_000_000) * 10.00
                else:
                    output_cost = (usage.candidates_token_count / 1_000_000) * 15.00
                
                total_cost = input_cost + output_cost
                
                logger.info(f"Pro Script Generation - Tokens: {usage.prompt_token_count} in, {usage.candidates_token_count} out, {usage.total_token_count} total")
                logger.info(f"Pro Script Generation - Cost: ${input_cost:.4f} in, ${output_cost:.4f} out, ${total_cost:.4f} total")
            except (TypeError, AttributeError):
                # Handle mocked objects in tests
                logger.info("Pro Script Generation - Metrics logging skipped (mocked response)")
        
        final_script = response.text.strip()
        if using_flash_summary:
            logger.info(f"✓ Two-stage briefing script created: Flash summary → Pro script generation")
        else:
            logger.info(f"✓ Single-stage briefing script created: Pro model processed raw articles")
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