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
    
    # TTS Provider Selection
    tts_provider = SelectField(
        'Text-to-Speech Provider',
        choices=[
            ('google', 'Google Cloud Text-to-Speech'),
            ('elevenlabs', 'ElevenLabs')
        ],
        default='google',
        validators=[DataRequired()]
    )
    
    elevenlabs_api_key = StringField(
        'ElevenLabs API Key (Optional - only needed if using ElevenLabs)',
        validators=[Optional()],
        render_kw={'placeholder': 'Enter your ElevenLabs API key'}
    )
    
    google_api_key = StringField(
        'Google API Key (Optional - only needed if using Google TTS)',
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
    
    # Google TTS Voice Selection (replaces ElevenLabs, Studio voices excluded due to cost)
    google_voice_name = SelectField(
        'Voice Selection',
        choices=[
            ('en-US-News-K', 'News-K - News Anchor Male'),
            ('en-US-News-L', 'News-L - News Anchor Female'),
            ('en-US-News-N', 'News-N - News Anchor Neutral'),
            ('en-US-Polyglot-1', 'Polyglot-1 - Multilingual Male'),
            ('en-US-Wavenet-A', 'Wavenet-A - Male'),
            ('en-US-Wavenet-B', 'Wavenet-B - Male'),
            ('en-US-Wavenet-C', 'Wavenet-C - Female'),
            ('en-US-Wavenet-D', 'Wavenet-D - Male'),
            ('en-US-Wavenet-E', 'Wavenet-E - Female'),
            ('en-US-Wavenet-F', 'Wavenet-F - Female'),
            ('en-US-Standard-A', 'Standard-A - Male'),
            ('en-US-Standard-B', 'Standard-B - Male'),
            ('en-US-Standard-C', 'Standard-C - Female'),
            ('en-US-Standard-D', 'Standard-D - Male'),
            ('en-US-Standard-E', 'Standard-E - Female'),
        ],
        default='en-US-News-K',
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
    
    # Audio Settings
    elevenlabs_voice_id = SelectField(
        'Voice Selection',
        choices=[
            ('default', 'Rachel (Default) - Professional Female'),
            ('EXAVITQu4vr4xnSDxMaL', 'Bella - Warm Female'),
            ('VR6AewLTigWG4xSOukaG', 'Arnold - Deep Male'),
            ('pNInz6obpgDQGcFmaJgB', 'Adam - Clear Male'),
            ('yoZ06aMxZJJ28mfd3POQ', 'Sam - Young Male'),
            ('kdmDKE6EkgrWrrykO9Qt', 'Alexandra - Realistic Young Female'),
            ('L0Dsvb3SLTyegXwtm47J', 'Archer - Friendly British Male'),
            ('g6xIsTj2HwM6VR4iXFCw', 'Jessica - Empathetic Female'),
            ('OYTbf65OHHFELVut7v2H', 'Hope - Bright & Uplifting Female'),
            ('dj3G1R1ilKoFKhBnWOzG', 'Eryn - Friendly & Relatable Female'),
            ('HDA9tsk27wYi3uq0fPcK', 'Stuart - Professional Australian Male'),
            ('1SM7GgM6IMuvQlz2BwM3', 'Mark - Relaxed & Laid Back Male'),
            ('PT4nqlKZfc06VW1BuClj', 'Angela - Down to Earth Female'),
            ('vBKc2FfBKJfcZNyEt1n6', 'Finn - Podcast Friendly Male'),
            ('56AoDkrOh6qfVPDXZ7Pt', 'Cassidy - Energetic Female'),
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