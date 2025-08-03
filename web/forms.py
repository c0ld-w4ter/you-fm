"""
Flask-WTF forms for AI Daily Briefing Agent web interface.

This module defines form classes for user input validation and processing.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SelectMultipleField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Optional, NumberRange, Length, Regexp, ValidationError


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
    
    gemini_api_key = StringField(
        'Google Gemini API Key',
        validators=[DataRequired(message='Google Gemini API Key is required')],
        render_kw={'placeholder': 'Enter your Google Gemini API key'}
    )
    
    # TTS Provider Selection (Google TTS only)
    tts_provider = SelectField(
        'Text-to-Speech Provider',
        choices=[
            ('google', 'Google Cloud Text-to-Speech (Standard & Neural2 voices)')
        ],
        default='google',
        validators=[DataRequired()]
    )
    
    google_api_key = StringField(
        'Google API Key (Required for Google TTS)',
        validators=[DataRequired(message='Google API Key is required for Text-to-Speech')],
        render_kw={'placeholder': 'Enter your Google API key'}
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
    
    # Enhanced: Country as dropdown with US as default
    location_country = SelectField(
        'Country',
        choices=[
            ('US', 'United States'),
            ('CA', 'Canada'),
            ('GB', 'United Kingdom'),
            ('AU', 'Australia'),
            ('DE', 'Germany'),
            ('FR', 'France'),
            ('IT', 'Italy'),
            ('ES', 'Spain'),
            ('NL', 'Netherlands'),
            ('BE', 'Belgium'),
            ('CH', 'Switzerland'),
            ('AT', 'Austria'),
            ('SE', 'Sweden'),
            ('NO', 'Norway'),
            ('DK', 'Denmark'),
            ('FI', 'Finland'),
            ('IE', 'Ireland'),
            ('PT', 'Portugal'),
            ('PL', 'Poland'),
            ('CZ', 'Czech Republic'),
            ('HU', 'Hungary'),
            ('GR', 'Greece'),
            ('TR', 'Turkey'),
            ('RU', 'Russia'),
            ('JP', 'Japan'),
            ('KR', 'South Korea'),
            ('CN', 'China'),
            ('IN', 'India'),
            ('SG', 'Singapore'),
            ('HK', 'Hong Kong'),
            ('TW', 'Taiwan'),
            ('TH', 'Thailand'),
            ('MY', 'Malaysia'),
            ('ID', 'Indonesia'),
            ('PH', 'Philippines'),
            ('VN', 'Vietnam'),
            ('BR', 'Brazil'),
            ('MX', 'Mexico'),
            ('AR', 'Argentina'),
            ('CL', 'Chile'),
            ('CO', 'Colombia'),
            ('ZA', 'South Africa'),
            ('EG', 'Egypt'),
            ('IL', 'Israel'),
            ('AE', 'United Arab Emirates'),
            ('SA', 'Saudi Arabia'),
            ('NZ', 'New Zealand'),
        ],
        default='US',
        validators=[Optional()]
    )
    
    # Content Settings - Simplified for fast iteration
    briefing_duration_minutes = IntegerField(
        'Briefing Duration (minutes)',
        validators=[NumberRange(min=1, max=30, message='Duration must be between 1 and 30 minutes')],
        render_kw={'min': 1, 'max': 30}
    )
    
    # Removed: news_topics, max_articles_per_topic - now auto-configured for comprehensive coverage
    
    # Content Settings - Simplified (removed complex options for fast iteration)
    briefing_tone = SelectField(
        'Briefing Tone',
        choices=[
            ('professional', 'Professional'),
            ('casual', 'Casual'),
            ('energetic', 'Energetic')
        ],
        default='professional',
        validators=[Optional()]
    )
    
    # Removed: content_depth (hardcoded to 'balanced'), keywords_exclude (let AI handle filtering)
    
    # Audio Settings
    google_tts_voice_name = SelectField(
        'Google TTS Voice Selection',
        choices=[
            # Standard voices (most cost-effective - $4 per 1M characters)
            ('en-US-Standard-A', 'Standard-A - Male (Cost-effective)'),
            ('en-US-Standard-B', 'Standard-B - Male (Cost-effective)'),
            ('en-US-Standard-C', 'Standard-C - Female (Cost-effective)'),
            ('en-US-Standard-D', 'Standard-D - Male (Cost-effective)'),
            ('en-US-Standard-E', 'Standard-E - Female (Cost-effective)'),
            ('en-US-Standard-F', 'Standard-F - Female (Cost-effective)'),
            ('en-US-Standard-G', 'Standard-G - Female (Cost-effective)'),
            ('en-US-Standard-H', 'Standard-H - Female (Cost-effective)'),
            ('en-US-Standard-I', 'Standard-I - Male (Cost-effective)'),
            ('en-US-Standard-J', 'Standard-J - Male (Cost-effective)'),
            
            # Neural2 voices (higher quality - $16 per 1M characters)
            ('en-US-Neural2-A', 'Neural2-A - Male (High Quality)'),
            ('en-US-Neural2-C', 'Neural2-C - Female (High Quality)'),
            ('en-US-Neural2-D', 'Neural2-D - Male (High Quality)'),
            ('en-US-Neural2-E', 'Neural2-E - Female (High Quality)'),
            ('en-US-Neural2-F', 'Neural2-F - Female (High Quality)'),
            ('en-US-Neural2-G', 'Neural2-G - Female (High Quality)'),
            ('en-US-Neural2-H', 'Neural2-H - Female (High Quality)'),
            ('en-US-Neural2-I', 'Neural2-I - Male (High Quality)'),
            ('en-US-Neural2-J', 'Neural2-J - Male (High Quality)'),
            
            # Additional Standard voices for variety
            ('en-GB-Standard-A', 'Standard-A - British Female (Cost-effective)'),
            ('en-GB-Standard-B', 'Standard-B - British Male (Cost-effective)'),
            ('en-GB-Standard-C', 'Standard-C - British Female (Cost-effective)'),
            ('en-GB-Standard-D', 'Standard-D - British Male (Cost-effective)'),
            ('en-AU-Standard-A', 'Standard-A - Australian Female (Cost-effective)'),
            ('en-AU-Standard-B', 'Standard-B - Australian Male (Cost-effective)'),
            ('en-AU-Standard-C', 'Standard-C - Australian Female (Cost-effective)'),
            ('en-AU-Standard-D', 'Standard-D - Australian Male (Cost-effective)'),
            
            # Additional Neural2 voices for variety
            ('en-GB-Neural2-A', 'Neural2-A - British Female (High Quality)'),
            ('en-GB-Neural2-B', 'Neural2-B - British Male (High Quality)'),
            ('en-GB-Neural2-C', 'Neural2-C - British Female (High Quality)'),
            ('en-GB-Neural2-D', 'Neural2-D - British Male (High Quality)'),
            ('en-AU-Neural2-A', 'Neural2-A - Australian Female (High Quality)'),
            ('en-AU-Neural2-B', 'Neural2-B - Australian Male (High Quality)'),
            ('en-AU-Neural2-C', 'Neural2-C - Australian Female (High Quality)'),
            ('en-AU-Neural2-D', 'Neural2-D - Australian Male (High Quality)'),
        ],
        default='en-US-Standard-C',  # Default to cost-effective female voice
        validators=[Optional()]
    )
    
    # Removed: voice_speed (users can adjust in audio player if needed)
    
    # Personalization fields - News & Information Preferences
    specific_interests = StringField(
        'Specific Interests',
        validators=[Optional(), Length(max=500)],
        render_kw={
            'placeholder': "e.g., 'advancements in generative AI', 'Formula 1 results', 'Nintendo', 'quantum computing'",
            'title': 'What are 1-3 specific sub-topics, companies, or technologies you are most interested in right now?'
        }
    )
    
    # Removed: briefing_goal (hardcoded to 'work' for UI simplification)
    
    followed_entities = StringField(
        'Followed Entities',
        validators=[Optional(), Length(max=500)],
        render_kw={
            'placeholder': "e.g., 'tech industry', 'Elon Musk', 'OpenAI', 'renewable energy sector'",
            'title': 'Are there any specific industries or public figures you actively follow?'
        }
    )
    
    # Personalization fields - Hobbies & Personal Interests
    hobbies = StringField(
        'Hobbies & Free Time',
        validators=[Optional(), Length(max=500)],
        render_kw={
            'placeholder': "e.g., 'Hiking', 'Playing video games', 'Cooking', 'Reading fiction'",
            'title': 'How do you like to spend your free time? What are your main hobbies?'
        }
    )
    
    favorite_teams_artists = StringField(
        'Favorite Teams/Artists',
        validators=[Optional(), Length(max=500)],
        render_kw={
            'placeholder': "e.g., 'Lakers', 'Taylor Swift', 'Marvel movies', 'Real Madrid'",
            'title': 'Are you a fan of any particular sports teams, artists, or movie franchises?'
        }
    )
    
    passion_topics = StringField(
        'Passion Topics',
        validators=[Optional(), Length(max=500)],
        render_kw={
            'placeholder': "e.g., 'History', 'Space exploration', 'Personal finance', 'Cooking techniques'",
            'title': "What's a topic you could talk about for hours?"
        }
    )
    
    # Personalization fields - Personal Quirks & Style
    greeting_preference = StringField(
        'Greeting Preference',
        validators=[Optional(), Length(max=200)],
        render_kw={
            'placeholder': "e.g., 'Good morning, [Name]!', 'Alright, let's get to it.', 'Here is your essential update.'",
            'title': 'How would you like the anchor to greet you in the morning?'
        }
    )
    
    daily_routine_detail = StringField(
        'Daily Routine Detail',
        validators=[Optional(), Length(max=500)],
        render_kw={
            'placeholder': "e.g., 'I listen while walking my dog, Sparky', 'I'm not a morning person', 'I'm training for a marathon'",
            'title': 'Is there a unique detail about your daily routine the briefing should know?'
        }
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
    
    gemini_api_key = StringField(
        'Google Gemini API Key',
        validators=[DataRequired(message='Google Gemini API Key is required')],
        render_kw={'placeholder': 'Enter your Google Gemini API key'}
    )
    
    google_api_key = StringField(
        'Google API Key',
        validators=[DataRequired(message='Google API Key is required')],
        render_kw={'placeholder': 'Enter your Google API key'}
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
    
    # Audio Settings
    google_tts_voice_name = SelectField(
        'Google TTS Voice Selection',
        choices=[
            # Standard voices (most cost-effective - $4 per 1M characters)
            ('en-US-Standard-A', 'Standard-A - Male (Cost-effective)'),
            ('en-US-Standard-B', 'Standard-B - Male (Cost-effective)'),
            ('en-US-Standard-C', 'Standard-C - Female (Cost-effective)'),
            ('en-US-Standard-D', 'Standard-D - Male (Cost-effective)'),
            ('en-US-Standard-E', 'Standard-E - Female (Cost-effective)'),
            ('en-US-Standard-F', 'Standard-F - Female (Cost-effective)'),
            ('en-US-Standard-G', 'Standard-G - Female (Cost-effective)'),
            ('en-US-Standard-H', 'Standard-H - Female (Cost-effective)'),
            ('en-US-Standard-I', 'Standard-I - Male (Cost-effective)'),
            ('en-US-Standard-J', 'Standard-J - Male (Cost-effective)'),
            
            # Neural2 voices (higher quality - $16 per 1M characters)
            ('en-US-Neural2-A', 'Neural2-A - Male (High Quality)'),
            ('en-US-Neural2-C', 'Neural2-C - Female (High Quality)'),
            ('en-US-Neural2-D', 'Neural2-D - Male (High Quality)'),
            ('en-US-Neural2-E', 'Neural2-E - Female (High Quality)'),
            ('en-US-Neural2-F', 'Neural2-F - Female (High Quality)'),
            ('en-US-Neural2-G', 'Neural2-G - Female (High Quality)'),
            ('en-US-Neural2-H', 'Neural2-H - Female (High Quality)'),
            ('en-US-Neural2-I', 'Neural2-I - Male (High Quality)'),
            ('en-US-Neural2-J', 'Neural2-J - Male (High Quality)'),
            
            # Additional Standard voices for variety
            ('en-GB-Standard-A', 'Standard-A - British Female (Cost-effective)'),
            ('en-GB-Standard-B', 'Standard-B - British Male (Cost-effective)'),
            ('en-GB-Standard-C', 'Standard-C - British Female (Cost-effective)'),
            ('en-GB-Standard-D', 'Standard-D - British Male (Cost-effective)'),
            ('en-AU-Standard-A', 'Standard-A - Australian Female (Cost-effective)'),
            ('en-AU-Standard-B', 'Standard-B - Australian Male (Cost-effective)'),
            ('en-AU-Standard-C', 'Standard-C - Australian Female (Cost-effective)'),
            ('en-AU-Standard-D', 'Standard-D - Australian Male (Cost-effective)'),
            
            # Additional Neural2 voices for variety
            ('en-GB-Neural2-A', 'Neural2-A - British Female (High Quality)'),
            ('en-GB-Neural2-B', 'Neural2-B - British Male (High Quality)'),
            ('en-GB-Neural2-C', 'Neural2-C - British Female (High Quality)'),
            ('en-GB-Neural2-D', 'Neural2-D - British Male (High Quality)'),
            ('en-AU-Neural2-A', 'Neural2-A - Australian Female (High Quality)'),
            ('en-AU-Neural2-B', 'Neural2-B - Australian Male (High Quality)'),
            ('en-AU-Neural2-C', 'Neural2-C - Australian Female (High Quality)'),
            ('en-AU-Neural2-D', 'Neural2-D - Australian Male (High Quality)'),
        ],
        default='en-US-Standard-C',  # Default to cost-effective female voice
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
        
        return True 