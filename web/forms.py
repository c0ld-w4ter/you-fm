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
    
    # TTS Provider Selection - ElevenLabs Recommended
    tts_provider = SelectField(
        'Text-to-Speech Provider',
        choices=[
            ('elevenlabs', 'ElevenLabs (Recommended - High Quality Voices)'),
            ('google', 'Google Cloud Text-to-Speech (Fallback)')
        ],
        default='elevenlabs',
        validators=[DataRequired()]
    )
    
    elevenlabs_api_key = StringField(
        'ElevenLabs API Key (Required for high-quality TTS)',
        validators=[DataRequired(message='ElevenLabs API Key is required')],
        render_kw={'placeholder': 'Enter your ElevenLabs API key'}
    )
    
    google_api_key = StringField(
        'Google API Key (Optional - only needed if using Google TTS fallback)',
        validators=[Optional()],
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
    
    # Audio Settings - ElevenLabs Voice Selection
    elevenlabs_voice_id = SelectField(
        'Voice Selection (ElevenLabs - Premium Quality)',
        choices=[
            ('default', 'Rachel - Professional Female (Default)'),
            ('21m00Tcm4TlvDq8ikWAM', 'Rachel - Professional Female'),
            ('EXAVITQu4vr4xnSDxMaL', 'Bella - Conversational Female'),
            ('VR6AewLTigWG4xSOukaG', 'Arnold - Authoritative Male'),
            ('pNInz6obpgDQGcFmaJgB', 'Adam - Deep Male'),
            ('Xb7hH8MSUJpSbSDYk0k2', 'Alice - Warm Female'),
            ('onwK4e9ZLuTAKqWW03F9', 'Daniel - Professional Male'),
        ],
        default='default',
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
        'Google API Key (for TTS)',
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
    
    # Audio Settings - ElevenLabs Voice Selection
    elevenlabs_voice_id = SelectField(
        'Voice Selection (ElevenLabs - Premium Quality)',
        choices=[
            ('default', 'Rachel - Professional Female (Default)'),
            ('21m00Tcm4TlvDq8ikWAM', 'Rachel - Professional Female'),
            ('EXAVITQu4vr4xnSDxMaL', 'Bella - Conversational Female'),
            ('VR6AewLTigWG4xSOukaG', 'Arnold - Authoritative Male'),
            ('pNInz6obpgDQGcFmaJgB', 'Adam - Deep Male'),
            ('Xb7hH8MSUJpSbSDYk0k2', 'Alice - Warm Female'),
            ('onwK4e9ZLuTAKqWW03F9', 'Daniel - Professional Male'),
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
        
        return True 