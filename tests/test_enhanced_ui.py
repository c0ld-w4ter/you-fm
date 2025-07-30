"""
Unit tests for enhanced UI improvements.
Tests checkbox functionality for news topics and podcast categories.
"""

import pytest
from web.forms import SettingsForm
from config_web import WebConfig


class TestEnhancedUI:
    """Test enhanced UI features with checkboxes and dropdown."""
    
    def test_country_dropdown_defaults_to_us(self):
        """Test that country dropdown defaults to US."""
        form = SettingsForm()
        defaults = WebConfig.get_form_defaults()
        form.location_country.data = defaults['location_country']
        assert form.location_country.data == 'US'
    
    def test_country_dropdown_has_choices(self):
        """Test that country dropdown has proper choices."""
        form = SettingsForm()
        choices = form.location_country.choices
        
        # Check that US is first and default
        assert choices[0] == ('US', 'United States')
        
        # Check some other major countries
        country_codes = [choice[0] for choice in choices]
        assert 'CA' in country_codes  # Canada
        assert 'GB' in country_codes  # United Kingdom
        assert 'AU' in country_codes  # Australia
        assert 'DE' in country_codes  # Germany
    
    def test_news_topics_checkbox_defaults(self):
        """Test that news topics checkboxes have correct defaults."""
        defaults = WebConfig.get_form_defaults()
        expected_topics = ['technology', 'business', 'science']
        assert defaults['news_topics'] == expected_topics
    
    def test_news_topics_has_choices(self):
        """Test that news topics field has proper choices."""
        form = SettingsForm()
        choices = form.news_topics.choices
        
        # Check that default topics are included
        topic_values = [choice[0] for choice in choices]
        assert 'technology' in topic_values
        assert 'business' in topic_values
        assert 'science' in topic_values
        
        # Check some additional topics
        assert 'health' in topic_values
        assert 'politics' in topic_values
        assert 'entertainment' in topic_values
    
    def test_podcast_categories_checkbox_defaults(self):
        """Test that podcast categories checkboxes have correct defaults."""
        defaults = WebConfig.get_form_defaults()
        expected_categories = ['Technology', 'Business', 'Science']
        assert defaults['podcast_categories'] == expected_categories
    
    def test_podcast_categories_has_choices(self):
        """Test that podcast categories field has proper choices."""
        form = SettingsForm()
        choices = form.podcast_categories.choices
        
        # Check that default categories are included
        category_values = [choice[0] for choice in choices]
        assert 'Technology' in category_values
        assert 'Business' in category_values
        assert 'Science' in category_values
        
        # Check some additional categories
        assert 'Health & Fitness' in category_values
        assert 'True Crime' in category_values
        assert 'Comedy' in category_values
    
    def test_checkbox_list_to_string_conversion(self):
        """Test conversion of checkbox lists to comma-separated strings."""
        form_data = {
            'newsapi_key': 'test_key',
            'openweather_api_key': 'test_key',
            'taddy_api_key': 'test_key',
            'taddy_user_id': 'test_user',
            'gemini_api_key': 'test_key',
            'elevenlabs_api_key': 'test_key',
            'news_topics': ['technology', 'health', 'sports'],
            'podcast_categories': ['Technology', 'Health & Fitness'],
        }
        
        config = WebConfig.create_config_from_form(form_data)
        
        # Verify lists were converted to comma-separated strings
        assert config.get('NEWS_TOPICS') == 'technology,health,sports'
        assert config.get('PODCAST_CATEGORIES') == 'Technology,Health & Fitness'
    
    def test_string_input_still_works(self):
        """Test that string inputs still work for backwards compatibility."""
        form_data = {
            'newsapi_key': 'test_key',
            'openweather_api_key': 'test_key',
            'taddy_api_key': 'test_key',
            'taddy_user_id': 'test_user',
            'gemini_api_key': 'test_key',
            'elevenlabs_api_key': 'test_key',
            'news_topics': 'technology,health,sports',  # String format
            'podcast_categories': 'Technology,Health & Fitness',  # String format
        }
        
        config = WebConfig.create_config_from_form(form_data)
        
        # Verify strings are preserved
        assert config.get('NEWS_TOPICS') == 'technology,health,sports'
        assert config.get('PODCAST_CATEGORIES') == 'Technology,Health & Fitness'
    
    def test_empty_checkbox_selection(self):
        """Test handling of empty checkbox selections."""
        form_data = {
            'newsapi_key': 'test_key',
            'openweather_api_key': 'test_key',
            'taddy_api_key': 'test_key',
            'taddy_user_id': 'test_user',
            'gemini_api_key': 'test_key',
            'elevenlabs_api_key': 'test_key',
            'news_topics': [],  # Empty list
            'podcast_categories': [],  # Empty list
        }
        
        config = WebConfig.create_config_from_form(form_data)
        
        # Verify empty lists become empty strings
        assert config.get('NEWS_TOPICS') == ''
        assert config.get('PODCAST_CATEGORIES') == ''


# Manual Testing Guide
def manual_test_guide():
    """
    Manual testing guide for enhanced UI features:
    
    1. Start the application: `python app.py`
    2. Navigate to http://localhost:8080
    3. Go through API Keys page (Page 1)
    4. On Settings page (Page 2), verify:
       - Country dropdown shows "United States" as selected by default
       - News Topics shows checkboxes with Technology, Business, Science pre-selected
       - Podcast Categories shows checkboxes with Technology, Business, Science pre-selected
       - Keywords to Avoid has improved placeholder text and tooltip
    5. Try different selections:
       - Change country to Canada
       - Select different news topics like Health, Sports, Politics
       - Select different podcast categories like Comedy, True Crime
       - Add some keywords to avoid like "celebrity, sports"
    6. Submit the form and verify settings are saved correctly
    7. Generate a briefing to ensure the new settings work end-to-end
    8. Verify the UI is responsive and checkboxes display properly on mobile
    """
    pass 