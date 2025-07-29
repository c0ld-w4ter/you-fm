"""
Flask-WTF forms for AI Daily Briefing Agent web interface.

This module defines form classes for user input validation and processing.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Optional, NumberRange, Length, Regexp


class APIKeysForm(FlaskForm):
    """Form for API keys configuration (Page 1)."""
    
    # Required API Keys
    newsapi_key = StringField(
        'NewsAPI Key',
        validators=[DataRequired(message='NewsAPI Key is required')],
        render_kw={'placeholder': 'Enter your NewsAPI key'}
    )
    
    openweather_api_key = StringField(
        'OpenWeatherMap API Key',
        validators=[DataRequired(message='OpenWeatherMap API Key is required')],
        render_kw={'placeholder': 'Enter your OpenWeatherMap API key'}
    )
    
    taddy_api_key = StringField(
        'Taddy API Key',
        validators=[DataRequired(message='Taddy API Key is required')],
        render_kw={'placeholder': 'Enter your Taddy API key'}
    )
    
    taddy_user_id = StringField(
        'Taddy User ID',
        validators=[DataRequired(message='Taddy User ID is required')],
        render_kw={'placeholder': 'Enter your Taddy User ID'}
    )
    
    gemini_api_key = StringField(
        'Google Gemini API Key',
        validators=[DataRequired(message='Google Gemini API Key is required')],
        render_kw={'placeholder': 'Enter your Google Gemini API key'}
    )
    
    elevenlabs_api_key = StringField(
        'ElevenLabs API Key',
        validators=[DataRequired(message='ElevenLabs API Key is required')],
        render_kw={'placeholder': 'Enter your ElevenLabs API key'}
    )
    
    # Submit button
    submit = SubmitField('Save API Keys & Continue')


class SettingsForm(FlaskForm):
    """Form for personal and content settings (Page 2)."""
    
    # Personal Settings
    listener_name = StringField(
        'Listener Name',
        validators=[Optional(), Length(max=50)],
        render_kw={'placeholder': 'Enter your name (optional)'}
    )
    
    location_city = StringField(
        'City',
        validators=[Optional(), Length(max=50)],
        render_kw={'placeholder': 'e.g., Denver'}
    )
    
    location_country = StringField(
        'Country Code',
        validators=[Optional(), Regexp(r'^[A-Z]{2}$', message='Please enter a 2-letter country code (e.g., US)')],
        render_kw={'placeholder': 'e.g., US, CA, GB'}
    )
    
    # Content Settings
    briefing_duration_minutes = IntegerField(
        'Briefing Duration (minutes)',
        validators=[NumberRange(min=1, max=30, message='Duration must be between 1 and 30 minutes')],
        render_kw={'min': 1, 'max': 30}
    )
    
    news_topics = StringField(
        'News Topics',
        validators=[Optional(), Length(max=200)],
        render_kw={'placeholder': 'e.g., technology,business,science'}
    )
    
    max_articles_per_topic = IntegerField(
        'Max Articles per Topic',
        validators=[NumberRange(min=1, max=10, message='Must be between 1 and 10')],
        render_kw={'min': 1, 'max': 10}
    )
    
    podcast_categories = StringField(
        'Podcast Categories',
        validators=[Optional(), Length(max=200)],
        render_kw={'placeholder': 'e.g., Technology,Business,Science'}
    )
    
    # Audio Settings
    elevenlabs_voice_id = SelectField(
        'Voice Selection',
        choices=[
            ('default', 'Default Voice'),
            ('EXAVITQu4vr4xnSDxMaL', 'Bella'),
            ('VR6AewLTigWG4xSOukaG', 'Arnold'),
            ('pNInz6obpgDQGcFmaJgB', 'Adam'),
            ('yoZ06aMxZJJ28mfd3POQ', 'Sam'),
        ],
        default='default',
        validators=[Optional()]
    )
    
    aws_region = HiddenField(default='us-east-1')
    
    # Submit button
    submit = SubmitField('Save Settings & Continue')


class BriefingConfigForm(FlaskForm):
    """
    Form for configuring daily briefing generation parameters.
    
    NOTE: This is a legacy single-page form maintained for compatibility.
    For new development, use the multi-page forms: APIKeysForm + SettingsForm.
    """
    
    # Required API Keys
    newsapi_key = StringField(
        'NewsAPI Key',
        validators=[DataRequired(message='NewsAPI Key is required')],
        render_kw={'placeholder': 'Enter your NewsAPI key'}
    )
    
    openweather_api_key = StringField(
        'OpenWeatherMap API Key',
        validators=[DataRequired(message='OpenWeatherMap API Key is required')],
        render_kw={'placeholder': 'Enter your OpenWeatherMap API key'}
    )
    
    taddy_api_key = StringField(
        'Taddy API Key',
        validators=[DataRequired(message='Taddy API Key is required')],
        render_kw={'placeholder': 'Enter your Taddy API key'}
    )
    
    taddy_user_id = StringField(
        'Taddy User ID',
        validators=[DataRequired(message='Taddy User ID is required')],
        render_kw={'placeholder': 'Enter your Taddy User ID'}
    )
    
    gemini_api_key = StringField(
        'Google Gemini API Key',
        validators=[DataRequired(message='Google Gemini API Key is required')],
        render_kw={'placeholder': 'Enter your Google Gemini API key'}
    )
    
    elevenlabs_api_key = StringField(
        'ElevenLabs API Key',
        validators=[DataRequired(message='ElevenLabs API Key is required')],
        render_kw={'placeholder': 'Enter your ElevenLabs API key'}
    )
    
    # Personal Settings
    listener_name = StringField(
        'Listener Name',
        validators=[Optional(), Length(max=50)],
        render_kw={'placeholder': 'Enter your name (optional)'}
    )
    
    location_city = StringField(
        'City',
        validators=[Optional(), Length(max=50)],
        render_kw={'placeholder': 'e.g., Denver'}
    )
    
    location_country = StringField(
        'Country Code',
        validators=[Optional(), Regexp(r'^[A-Z]{2}$', message='Please enter a 2-letter country code (e.g., US)')],
        render_kw={'placeholder': 'e.g., US, CA, GB'}
    )
    
    # Content Settings
    briefing_duration_minutes = IntegerField(
        'Briefing Duration (minutes)',
        validators=[NumberRange(min=1, max=30, message='Duration must be between 1 and 30 minutes')],
        render_kw={'min': 1, 'max': 30}
    )
    
    news_topics = StringField(
        'News Topics',
        validators=[Optional(), Length(max=200)],
        render_kw={'placeholder': 'e.g., technology,business,science'}
    )
    
    max_articles_per_topic = IntegerField(
        'Max Articles per Topic',
        validators=[NumberRange(min=1, max=10, message='Must be between 1 and 10')],
        render_kw={'min': 1, 'max': 10}
    )
    
    podcast_categories = StringField(
        'Podcast Categories',
        validators=[Optional(), Length(max=200)],
        render_kw={'placeholder': 'e.g., Technology,Business,Science'}
    )
    
    # Audio Settings
    elevenlabs_voice_id = SelectField(
        'Voice Selection',
        choices=[
            ('default', 'Default Voice'),
            ('EXAVITQu4vr4xnSDxMaL', 'Bella'),
            ('VR6AewLTigWG4xSOukaG', 'Arnold'),
            ('pNInz6obpgDQGcFmaJgB', 'Adam'),
            ('yoZ06aMxZJJ28mfd3POQ', 'Sam'),
        ],
        default='default',
        validators=[Optional()]
    )
    
    aws_region = HiddenField(default='us-east-1')
    
    # Submit button
    submit = SubmitField('Generate Daily Briefing')
    
    def validate(self, extra_validators=None):
        """Custom validation for the form."""
        if not super().validate(extra_validators):
            return False
        
        # Additional custom validation can be added here
        # For example, validating news topics format
        if self.news_topics.data:
            topics = [topic.strip() for topic in self.news_topics.data.split(',')]
            if not all(topic for topic in topics):
                self.news_topics.errors.append('Topics cannot be empty')
                return False
        
        if self.podcast_categories.data:
            categories = [cat.strip() for cat in self.podcast_categories.data.split(',')]
            if not all(category for category in categories):
                self.podcast_categories.errors.append('Categories cannot be empty')
                return False
        
        return True 