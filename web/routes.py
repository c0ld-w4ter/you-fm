"""
Flask route handlers for AI Daily Briefing Agent web interface.

This module defines HTTP endpoints for the web application.
"""

import os
import logging
from datetime import datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file, jsonify, session
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
            # Store settings in session
            session['settings'] = {
                'listener_name': form.listener_name.data,
                'location_city': form.location_city.data,
                'location_country': form.location_country.data,
                'briefing_duration_minutes': form.briefing_duration_minutes.data,
                'news_topics': form.news_topics.data,
                'max_articles_per_topic': form.max_articles_per_topic.data,
                'podcast_categories': form.podcast_categories.data,
                'elevenlabs_voice_id': form.elevenlabs_voice_id.data,
                'aws_region': form.aws_region.data,
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
    """Page 3: Generate briefing page with big button."""
    # Check if both API keys and settings are set
    if 'api_keys' not in session:
        flash('Please configure your API keys first.', 'error')
        return redirect(url_for('web.api_keys'))
    
    if 'settings' not in session:
        flash('Please configure your settings first.', 'error')
        return redirect(url_for('web.settings'))
    
    return render_template('generate.html')


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
        audio_path = os.path.join('static', 'audio', filename)
        if os.path.exists(audio_path):
            return send_file(audio_path, mimetype='audio/mpeg')
        else:
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
        audio_path = os.path.join('static', 'audio', filename)
        if os.path.exists(audio_path):
            return send_file(audio_path, 
                           mimetype='audio/mpeg',
                           as_attachment=True,
                           download_name=filename)
        else:
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