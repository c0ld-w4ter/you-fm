"""
Flask route handlers for AI Daily Briefing Agent web interface.

This module defines HTTP endpoints for the web application.
"""

import os
import logging
from datetime import datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file, jsonify, session, current_app
from werkzeug.utils import secure_filename

from web.forms import BriefingConfigForm, APIKeysForm, SettingsForm
from config_web import WebConfig
from config import ConfigurationError
from main import generate_daily_briefing

logger = logging.getLogger(__name__)

# Create blueprint for web routes
web_bp = Blueprint('web', __name__)


@web_bp.route('/', methods=['GET', 'POST'])
def index():
    """Landing page - redirect to API keys page."""
    return redirect(url_for('web.api_keys'))


@web_bp.route('/api-keys', methods=['GET', 'POST'])
def api_keys():
    """Page 1: API Keys configuration."""
    form = APIKeysForm()
    
    if request.method == 'POST':
        if form.validate_on_submit():
            # Store API keys in session
            session['api_keys'] = {
                'newsapi_key': form.newsapi_key.data,
                'openweather_api_key': form.openweather_api_key.data,
                'taddy_api_key': form.taddy_api_key.data,
                'taddy_user_id': form.taddy_user_id.data,
                'gemini_api_key': form.gemini_api_key.data,
                'elevenlabs_api_key': form.elevenlabs_api_key.data,
            }
            flash('API keys saved successfully!', 'success')
            return redirect(url_for('web.settings'))
        else:
            flash('Please correct the errors below.', 'error')
    
    # Pre-populate form with defaults for GET requests
    if request.method == 'GET':
        defaults = WebConfig.get_form_defaults()
        for field_name, default_value in defaults.items():
            if hasattr(form, field_name):
                getattr(form, field_name).data = default_value
    
    return render_template('api_keys.html', form=form)


@web_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    """Page 2: Personal and content settings."""
    # Check if API keys are set
    if 'api_keys' not in session:
        flash('Please configure your API keys first.', 'error')
        return redirect(url_for('web.api_keys'))
    
    form = SettingsForm()
    
    if request.method == 'POST':
        if form.validate_on_submit():
            # Convert checkbox lists to comma-separated strings for session storage
            news_topics = form.news_topics.data
            if isinstance(news_topics, list):
                news_topics_str = ','.join(news_topics)
            else:
                news_topics_str = news_topics or 'technology,business,science'
                
            podcast_categories = form.podcast_categories.data
            if isinstance(podcast_categories, list):
                podcast_categories_str = ','.join(podcast_categories)
            else:
                podcast_categories_str = podcast_categories or 'Technology,Business,Science'
            
            # Store settings in session
            session['settings'] = {
                'listener_name': form.listener_name.data,
                'location_city': form.location_city.data,
                'location_country': form.location_country.data,
                'briefing_duration_minutes': form.briefing_duration_minutes.data,
                'news_topics': news_topics_str,  # Store as comma-separated string
                'max_articles_per_topic': form.max_articles_per_topic.data,
                'podcast_categories': podcast_categories_str,  # Store as comma-separated string
                'elevenlabs_voice_id': form.elevenlabs_voice_id.data,
                'aws_region': form.aws_region.data,
                
                # Advanced settings (New for Milestone 5)
                'briefing_tone': form.briefing_tone.data,
                'content_depth': form.content_depth.data,
                'keywords_exclude': form.keywords_exclude.data,
                'voice_speed': form.voice_speed.data,
            }
            flash('Settings saved successfully!', 'success')
            return redirect(url_for('web.generate'))
        else:
            flash('Please correct the errors below.', 'error')
    
    # Pre-populate form with defaults for GET requests
    if request.method == 'GET':
        defaults = WebConfig.get_form_defaults()
        for field_name, default_value in defaults.items():
            if hasattr(form, field_name):
                getattr(form, field_name).data = default_value
    
    return render_template('settings.html', form=form)


@web_bp.route('/generate', methods=['GET'])
def generate():
    """Page 3: Generate briefing page."""
    # Check if settings are configured
    if 'api_keys' not in session or 'settings' not in session:
        flash('Please complete the configuration steps first.', 'error')
        return redirect(url_for('web.api_keys'))
    
    return render_template('generate.html')


@web_bp.route('/preview-script', methods=['POST'])
def preview_script():
    """AJAX endpoint to generate script preview without audio generation."""
    try:
        # Check if configuration is complete
        if 'api_keys' not in session or 'settings' not in session:
            return jsonify({
                'success': False, 
                'error': 'Configuration incomplete. Please complete API keys and settings first.'
            })
        
        # Combine session data into config
        session_data = {**session.get('api_keys', {}), **session.get('settings', {})}
        config = WebConfig.create_config_from_form(session_data)
        
        # Import the new script-only generation function
        from main import generate_script_only
        
        # Generate script preview (much faster than full generation)
        logger.info("Generating script preview via web interface...")
        result = generate_script_only(config)
        
        if result['success']:
            data = result['data']
            return jsonify({
                'success': True,
                'script': data['script_content'],
                'word_count': data['word_count'],
                'estimated_duration_minutes': data['estimated_duration_minutes'],
                'generation_time_seconds': data['generation_time_seconds'],
                'articles_count': data['articles_count'],
                'podcasts_count': data['podcasts_count'],
                'has_weather': data['has_weather'],
                'tone': data['tone'],
                'depth': data['depth'],
                'keywords_excluded': data['keywords_excluded'],
                'char_count': data['script_length_chars']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error'],
                'message': result['message']
            })
            
    except Exception as e:
        logger.error(f"Error during script preview: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate preview',
            'message': str(e)
        })


@web_bp.route('/data-report', methods=['POST'])
def data_report():
    """AJAX endpoint to generate raw data input report for debugging and observability."""
    try:
        # Check if configuration is complete
        if 'api_keys' not in session or 'settings' not in session:
            return jsonify({
                'success': False, 
                'error': 'Configuration incomplete. Please complete API keys and settings first.'
            })
        
        # Combine session data into config
        session_data = {**session.get('api_keys', {}), **session.get('settings', {})}
        config = WebConfig.create_config_from_form(session_data)
        
        # Import data fetchers
        from data_fetchers import get_weather, get_news_articles, get_new_podcast_episodes
        from datetime import datetime
        import time
        
        logger.info("Generating data input report via web interface...")
        
        # Track timing
        start_time = time.perf_counter()
        report_lines = []
        
        # Header
        report_lines.append("=" * 60)
        report_lines.append("AI DAILY BRIEFING - DATA INPUT REPORT")
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Configuration: {config.get('LISTENER_NAME', 'Default')} | {config.get('LOCATION_CITY', 'Unknown')}, {config.get('LOCATION_COUNTRY', 'Unknown')}")
        report_lines.append("=" * 60)
        report_lines.append("")
        
        # Initialize counters
        weather_status = "N/A"
        news_count = 0
        podcast_count = 0
        
        # Fetch Weather Data
        try:
            logger.info("Fetching weather data for report...")
            weather_data = get_weather(config)
            weather_status = "✓"
            
            report_lines.append("WEATHER DATA")
            report_lines.append("-" * 12)
            report_lines.append(f"Location: {weather_data.city}, {weather_data.country}")
            report_lines.append(f"Temperature: {weather_data.temperature:.1f}°C")
            report_lines.append(f"Conditions: {weather_data.description.title()}")
            report_lines.append(f"Humidity: {weather_data.humidity}%")
            report_lines.append(f"Wind Speed: {weather_data.wind_speed} m/s")
            report_lines.append("")
            
        except Exception as e:
            weather_status = "✗"
            report_lines.append("WEATHER DATA")
            report_lines.append("-" * 12)
            report_lines.append(f"Error fetching weather data: {str(e)}")
            report_lines.append("")
        
        # Fetch News Articles
        try:
            logger.info("Fetching news articles for report...")
            news_articles = get_news_articles(config)
            news_count = len(news_articles)
            
            # Group articles by topic
            topics = config.get_news_topics()
            max_articles_per_topic = config.get_max_articles_per_topic()
            
            report_lines.append(f"NEWS ARTICLES ({news_count} articles)")
            report_lines.append("-" * 20)
            
            articles_by_topic = {}
            for article in news_articles:
                # Try to match article to topic (simplified approach)
                matched_topic = "General"
                for topic in topics:
                    if topic.lower() in article.title.lower() or topic.lower() in article.content.lower():
                        matched_topic = topic.title()
                        break
                
                if matched_topic not in articles_by_topic:
                    articles_by_topic[matched_topic] = []
                articles_by_topic[matched_topic].append(article)
            
            for topic, articles in articles_by_topic.items():
                report_lines.append(f"\nTopic: {topic} ({len(articles)} articles)")
                for i, article in enumerate(articles, 1):
                    report_lines.append(f"  {i}. {article.title}")
                    report_lines.append(f"     Source: {article.source}")
                    report_lines.append(f"     URL: {article.url}")
                    content_preview = article.content[:200] + "..." if len(article.content) > 200 else article.content
                    report_lines.append(f"     Content Preview: {content_preview}")
                    report_lines.append("")
            
        except Exception as e:
            report_lines.append(f"NEWS ARTICLES (Error)")
            report_lines.append("-" * 20)
            report_lines.append(f"Error fetching news articles: {str(e)}")
            report_lines.append("")
        
        # Fetch Podcast Episodes
        try:
            logger.info("Fetching podcast episodes for report...")
            podcast_episodes = get_new_podcast_episodes(config)
            podcast_count = len(podcast_episodes)
            
            report_lines.append(f"PODCAST EPISODES ({podcast_count} episodes)")
            report_lines.append("-" * 25)
            
            for i, episode in enumerate(podcast_episodes, 1):
                report_lines.append(f"  {i}. {episode.podcast_title} - {episode.episode_title}")
                report_lines.append(f"     URL: {episode.url}")
                report_lines.append("")
            
        except Exception as e:
            report_lines.append(f"PODCAST EPISODES (Error)")
            report_lines.append("-" * 25)
            report_lines.append(f"Error fetching podcast episodes: {str(e)}")
            report_lines.append("")
        
        # Footer
        end_time = time.perf_counter()
        fetch_time = round(end_time - start_time, 2)
        
        report_lines.append("=" * 60)
        report_lines.append(f"Total Data Points: Weather: {weather_status} | News: {news_count} | Podcasts: {podcast_count}")
        report_lines.append(f"Data Fetch Time: {fetch_time} seconds")
        report_lines.append(f"Next Step: AI Processing & Audio Generation")
        report_lines.append("=" * 60)
        
        # Join all lines into final report
        report_content = "\n".join(report_lines)
        
        return jsonify({
            'success': True,
            'report_content': report_content,
            'weather_status': weather_status,
            'news_count': news_count,
            'podcast_count': podcast_count,
            'fetch_time_seconds': fetch_time,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
            
    except Exception as e:
        logger.error(f"Error during data report generation: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate data report',
            'message': str(e)
        })


@web_bp.route('/preview-voice', methods=['POST'])
def preview_voice():
    """AJAX endpoint to generate voice preview audio."""
    try:
        # Get voice ID from request
        data = request.get_json()
        voice_id = data.get('voice_id')
        
        if not voice_id:
            return jsonify({
                'success': False,
                'error': 'No voice ID provided'
            })
        
        # Check if API keys are configured
        if 'api_keys' not in session:
            return jsonify({
                'success': False, 
                'error': 'ElevenLabs API key not configured. Please set up your API keys first.'
            })
        
        # Create a minimal config for preview
        api_keys = session.get('api_keys', {})
        elevenlabs_api_key = api_keys.get('elevenlabs_api_key')
        
        if not elevenlabs_api_key:
            return jsonify({
                'success': False,
                'error': 'ElevenLabs API key not found. Please configure your API keys.'
            })
        
        # Sample text for voice preview
        preview_text = "Hello! This is a preview of your selected voice for the AI Daily Briefing. I'll be delivering your personalized news, weather, and podcast summaries in this style."
        
        # Import TTS generator
        from tts_generator import generate_audio
        from config import Config
        
        # Create a minimal config object for the preview
        # We need to bypass the validation for preview, so we'll create a simple config object
        preview_config = type('PreviewConfig', (), {
            'get': lambda self, key, default=None: {
                'ELEVENLABS_API_KEY': elevenlabs_api_key,
                'ELEVENLABS_VOICE_ID': voice_id
            }.get(key, default),
            'get_voice_speed': lambda self: 1.0
        })()
        
        logger.info(f"Generating voice preview for voice ID: {voice_id}")
        
        # Generate preview audio
        audio_bytes = generate_audio(preview_text, preview_config)
        
        # Save preview to temporary file
        import tempfile
        import base64
        
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_filename = temp_file.name
        
        # Convert to base64 for easy transmission
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        # Clean up temp file
        os.unlink(temp_filename)
        
        return jsonify({
            'success': True,
            'audio_data': f"data:audio/mp3;base64,{audio_base64}",
            'voice_id': voice_id
        })
        
    except Exception as e:
        logger.error(f"Error during voice preview: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate voice preview',
            'message': str(e)
        })


@web_bp.route('/loading', methods=['GET'])
def loading():
    """Page 4: Loading screen."""
    # Check if both API keys and settings are set
    if 'api_keys' not in session or 'settings' not in session:
        flash('Please complete the configuration first.', 'error')
        return redirect(url_for('web.api_keys'))
    
    return render_template('loading.html')


@web_bp.route('/create-briefing', methods=['POST'])
def create_briefing():
    """API endpoint to start briefing generation."""
    # Check if both API keys and settings are set
    if 'api_keys' not in session or 'settings' not in session:
        return jsonify({'error': 'Configuration incomplete'}), 400
    
    try:
        # Combine API keys and settings
        form_data = {**session['api_keys'], **session['settings']}
        
        # Create configuration from form data
        config = WebConfig.create_config_from_form(form_data)
        
        # Generate the briefing
        logger.info("Starting briefing generation from web interface...")
        result = generate_daily_briefing(config)
        
        # Store result in session for results page
        session['briefing_result'] = result
        
        return jsonify({'success': True, 'redirect': url_for('web.results')})
        
    except ConfigurationError as e:
        return jsonify({'error': f'Configuration error: {str(e)}'}), 400
    except Exception as e:
        logger.error(f"Unexpected error during briefing generation: {e}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500


@web_bp.route('/results', methods=['GET'])
def results():
    """Page 5: Final briefing results."""
    if 'briefing_result' not in session:
        flash('No briefing result found. Please generate a briefing first.', 'error')
        return redirect(url_for('web.generate'))
    
    result = session['briefing_result']
    config = {**session.get('api_keys', {}), **session.get('settings', {})}
    
    return render_template('results.html', result=result, config=config)


@web_bp.route('/audio/<filename>')
def serve_audio(filename):
    """Serve audio files from the static/audio directory."""
    try:
        # Use correct path - static/audio is relative to the app root directory
        audio_path = os.path.join(current_app.root_path, 'static', 'audio', filename)
        audio_path = os.path.abspath(audio_path)  # Resolve the absolute path
        
        logger.info(f"Attempting to serve audio file: {audio_path}")
        
        if os.path.exists(audio_path):
            logger.info(f"✓ Audio file found, serving: {filename}")
            return send_file(audio_path, mimetype='audio/mpeg')
        else:
            logger.error(f"✗ Audio file not found at: {audio_path}")
            flash('Audio file not found.', 'error')
            return redirect(url_for('web.index'))
    except Exception as e:
        logger.error(f"Error serving audio file {filename}: {e}")
        flash('Error serving audio file.', 'error')
        return redirect(url_for('web.index'))


@web_bp.route('/download/<filename>')
def download_audio(filename):
    """Download audio files."""
    try:
        # Use correct path - static/audio is relative to the app root directory
        audio_path = os.path.join(current_app.root_path, 'static', 'audio', filename)
        audio_path = os.path.abspath(audio_path)  # Resolve the absolute path
        
        logger.info(f"Attempting to download audio file: {audio_path}")
        
        if os.path.exists(audio_path):
            logger.info(f"✓ Audio file found, downloading: {filename}")
            return send_file(audio_path, 
                           mimetype='audio/mpeg',
                           as_attachment=True,
                           download_name=filename)
        else:
            logger.error(f"✗ Audio file not found at: {audio_path}")
            flash('Audio file not found.', 'error')
            return redirect(url_for('web.index'))
    except Exception as e:
        logger.error(f"Error downloading audio file {filename}: {e}")
        flash('Error downloading audio file.', 'error')
        return redirect(url_for('web.index'))


@web_bp.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'ai-daily-briefing-agent',
        'timestamp': datetime.utcnow().isoformat()
    })


@web_bp.route('/api/validate', methods=['POST'])
def api_validate():
    """API endpoint for form validation."""
    try:
        data = request.get_json() or {}
        errors = WebConfig.validate_form_data(data)
        
        return jsonify({
            'valid': len(errors) == 0,
            'errors': errors
        })
    except Exception as e:
        return jsonify({
            'valid': False,
            'errors': {'general': str(e)}
        })


# Error handlers
@web_bp.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    return render_template('404.html'), 404


@web_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return render_template('500.html'), 500 