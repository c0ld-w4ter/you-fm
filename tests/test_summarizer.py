"""
Unit tests for summarizer module.

Tests the Google Gemini API integration for article summarization
and briefing script creation.
"""

import pytest
from unittest.mock import MagicMock, patch
from data_fetchers import Article, WeatherData, PodcastEpisode
from summarizer import summarize_articles, create_briefing_script


class TestSummarizeArticles:
    """Test cases for summarize_articles function."""
    
    @patch('google.generativeai.GenerativeModel')
    @patch('google.generativeai.configure')
    @patch('summarizer.get_config')
    def test_summarize_articles_success(self, mock_config, mock_configure, mock_model_class):
        """Test successful article summarization."""
        # Mock configuration
        mock_config_instance = MagicMock()
        mock_config_instance.get.return_value = 'test-gemini-key'
        mock_config.return_value = mock_config_instance
        
        # Mock Gemini model and response
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "This is a test summary from Gemini API."
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        # Create test articles
        articles = [
            Article(
                title="Tech News Article",
                source="TechCrunch",
                url="https://example.com/tech",
                content="This is a technology article about AI developments..."
            ),
            Article(
                title="Business News Article", 
                source="BusinessInsider",
                url="https://example.com/business",
                content="This is a business article about market trends..."
            )
        ]
        
        # Call function
        result = summarize_articles(articles)
        
        # Verify results
        assert len(result) == 2
        assert result[0].summary == "This is a test summary from Gemini API."
        assert result[1].summary == "This is a test summary from Gemini API."
        
        # Verify API calls
        mock_configure.assert_called_once_with(api_key='test-gemini-key')
        mock_model_class.assert_called_once_with('gemini-2.5-pro')
        assert mock_model.generate_content.call_count == 2
        
    @patch('google.generativeai.GenerativeModel')
    @patch('google.generativeai.configure')
    @patch('summarizer.get_config')
    def test_summarize_articles_empty_list(self, mock_config, mock_configure, mock_model_class):
        """Test summarizing empty article list."""
        # Mock configuration
        mock_config_instance = MagicMock()
        mock_config_instance.get.return_value = 'test-gemini-key'
        mock_config.return_value = mock_config_instance
        
        # Call function with empty list
        result = summarize_articles([])
        
        # Verify results
        assert len(result) == 0
        
        # Verify no API calls were made
        mock_configure.assert_not_called()
        mock_model_class.assert_not_called()
        
    @patch('google.generativeai.GenerativeModel')
    @patch('google.generativeai.configure')
    @patch('summarizer.get_config')
    def test_summarize_articles_individual_failure(self, mock_config, mock_configure, mock_model_class):
        """Test when individual article summarization fails."""
        # Mock configuration
        mock_config_instance = MagicMock()
        mock_config_instance.get.return_value = 'test-gemini-key'
        mock_config.return_value = mock_config_instance
        
        # Mock Gemini model - first call succeeds, second fails
        mock_model = MagicMock()
        mock_success_response = MagicMock()
        mock_success_response.text = "Successful summary"
        
        def mock_generate_content(prompt):
            if "Tech News" in prompt:
                return mock_success_response
            else:
                raise Exception("API connection failed")
                
        mock_model.generate_content.side_effect = mock_generate_content
        mock_model_class.return_value = mock_model
        
        # Create test articles
        articles = [
            Article(
                title="Tech News Article",
                source="TechCrunch",
                url="https://example.com/tech",
                content="This is a technology article..."
            ),
            Article(
                title="Business News Article",
                source="BusinessInsider", 
                url="https://example.com/business",
                content="This is a business article with very long content that definitely exceeds two hundred characters and should be truncated for fallback summary when the API fails to generate a proper summary for this news article."
            )
        ]
        
        # Call function
        result = summarize_articles(articles)
        
        # Verify results
        assert len(result) == 2
        assert result[0].summary == "Successful summary"
        assert result[1].summary.startswith("[Auto-summary unavailable]")
        
    @patch('summarizer.get_config')
    def test_summarize_articles_api_setup_failure(self, mock_config):
        """Test when Gemini API setup fails."""
        # Mock configuration failure
        mock_config.side_effect = Exception("Configuration error")
        
        # Create test articles
        articles = [
            Article(
                title="Test Article",
                source="TestSource",
                url="https://example.com/test",
                content="Test content for fallback"
            )
        ]
        
        # Verify exception is raised
        with pytest.raises(Exception) as exc_info:
            summarize_articles(articles)
            
        assert "Failed to summarize articles with Gemini API" in str(exc_info.value)
        
    @patch('google.generativeai.GenerativeModel')
    @patch('google.generativeai.configure')
    @patch('summarizer.get_config')
    def test_summarize_articles_prompt_format(self, mock_config, mock_configure, mock_model_class):
        """Test that the prompt is correctly formatted."""
        # Mock configuration
        mock_config_instance = MagicMock()
        mock_config_instance.get.return_value = 'test-gemini-key'
        mock_config.return_value = mock_config_instance
        
        # Mock Gemini model
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Test summary"
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        # Create test article
        articles = [
            Article(
                title="Test Title",
                source="Test Source",
                url="https://example.com/test",
                content="Test content"
            )
        ]
        
        # Call function
        summarize_articles(articles)
        
        # Verify prompt contains required elements
        call_args = mock_model.generate_content.call_args[0][0]
        assert "Test Title" in call_args
        assert "Test Source" in call_args
        assert "Test content" in call_args
        assert "Summary:" in call_args
        assert "concise, informative summary" in call_args


class TestCreateBriefingScript:
    """Test cases for create_briefing_script function."""
    
    @patch('google.generativeai.GenerativeModel')
    @patch('google.generativeai.configure')
    @patch('summarizer.get_config')
    def test_create_briefing_script_ai_generation_success(self, mock_config, mock_configure, mock_model_class):
        """Test successful AI-generated briefing script creation."""
        # Mock configuration
        mock_config_instance = MagicMock()
        mock_config_instance.get.return_value = 'test-gemini-key'
        mock_config.return_value = mock_config_instance
        
        # Mock Gemini model and response
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = """Good morning! Here's your AI-powered daily briefing for Monday, January 29, 2024.

Let's start with the weather in San Francisco. It's currently 22°C with clear skies - a beautiful day ahead with comfortable humidity at 65%.

Now for today's top news stories. AI technology is advancing rapidly with new breakthroughs in machine learning, showing promising developments in the tech sector.

Here are some interesting podcast episodes you might enjoy. 'Future of AI' from Tech Talk explores cutting-edge developments, and 'Market Analysis' from Business Hour provides valuable insights into current trends.

That's your briefing for today. Stay informed and have a wonderful day!"""
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        # Create test data
        weather_data = WeatherData(
            city="San Francisco",
            country="US",
            temperature=22,
            description="Clear sky",
            humidity=65,
            wind_speed=3
        )
        
        articles = [
            Article(
                title="AI News",
                source="TechNews",
                url="https://example.com/ai",
                content="AI content"
            )
        ]
        articles[0].summary = "AI technology is advancing rapidly with new breakthroughs in machine learning."
        
        podcast_episodes = [
            PodcastEpisode(
                podcast_title="Tech Talk",
                episode_title="Future of AI",
                url="https://example.com/podcast1"
            ),
            PodcastEpisode(
                podcast_title="Business Hour",
                episode_title="Market Analysis", 
                url="https://example.com/podcast2"
            )
        ]
        
        # Call function
        result = create_briefing_script(weather_data, articles, podcast_episodes)
        
        # Verify AI-generated content is returned
        assert "Good morning!" in result
        assert "San Francisco" in result
        assert "AI technology is advancing rapidly" in result
        assert "Tech Talk" in result
        assert "wonderful day" in result
        
        # Verify API calls
        mock_configure.assert_called_once_with(api_key='test-gemini-key')
        mock_model_class.assert_called_once_with('gemini-2.5-pro')
        mock_model.generate_content.assert_called_once()
        
        # Verify prompt contains expected data
        call_args = mock_model.generate_content.call_args[0][0]
        assert "San Francisco" in call_args
        assert "22°C" in call_args
        assert "AI News" in call_args
        assert "Tech Talk" in call_args
        assert "Future of AI" in call_args
        
    @patch('summarizer.get_config')
    def test_create_briefing_script_fallback_on_api_failure(self, mock_config):
        """Test fallback script generation when AI API fails."""
        # Mock configuration failure to trigger fallback
        mock_config.side_effect = Exception("API connection failed")
        
        # Create test data
        weather_data = WeatherData(
            city="Denver",
            country="US",
            temperature=15,
            description="Cloudy",
            humidity=80,
            wind_speed=2
        )
        
        articles = [
            Article(
                title="Test Article",
                source="TestSource",
                url="https://example.com/test",
                content="Test content"
            )
        ]
        articles[0].summary = "Test summary"
        
        podcast_episodes = [
            PodcastEpisode(
                podcast_title="Daily News",
                episode_title="Today's Update",
                url="https://example.com/daily"
            )
        ]
        
        # Call function
        result = create_briefing_script(weather_data, articles, podcast_episodes)
        
        # Verify fallback script content
        assert "Good morning!" in result
        assert "Denver" in result
        assert "15°C" in result
        assert "Test summary" in result
        assert "Daily News" in result
        assert "Have a great day!" in result
        
    @patch('google.generativeai.GenerativeModel')
    @patch('google.generativeai.configure')
    @patch('summarizer.get_config')  
    def test_create_briefing_script_missing_data_handling(self, mock_config, mock_configure, mock_model_class):
        """Test that the prompt correctly handles missing data."""
        # Mock configuration
        mock_config_instance = MagicMock()
        mock_config_instance.get.return_value = 'test-gemini-key'
        mock_config.return_value = mock_config_instance
        
        # Mock Gemini model
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Good morning! Here's your briefing with limited data available today."
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        # Call function with no data
        result = create_briefing_script(None, [], [])
        
        # Verify function runs without error
        assert "Good morning!" in result
        
        # Verify prompt handles missing data correctly
        call_args = mock_model.generate_content.call_args[0][0]
        assert "No weather data available" in call_args
        assert "No news articles available" in call_args
        assert "No new podcast episodes available" in call_args
        
    @patch('google.generativeai.GenerativeModel')
    @patch('google.generativeai.configure')
    @patch('summarizer.get_config')
    def test_create_briefing_script_content_limits(self, mock_config, mock_configure, mock_model_class):
        """Test that the prompt correctly limits articles and podcasts."""
        # Mock configuration
        mock_config_instance = MagicMock()
        mock_config_instance.get.return_value = 'test-gemini-key'
        mock_config.return_value = mock_config_instance
        
        # Mock Gemini model
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Generated briefing with limited content"
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        # Create more content than should be included
        articles = []
        for i in range(10):
            article = Article(
                title=f"Article {i}",
                source="TestSource",
                url=f"https://example.com/article{i}",
                content=f"Content {i}"
            )
            article.summary = f"Summary {i}"
            articles.append(article)
            
        podcasts = []
        for i in range(10):
            podcasts.append(PodcastEpisode(
                podcast_title=f"Podcast {i}",
                episode_title=f"Episode {i}",
                url=f"https://example.com/podcast{i}"
            ))
        
        # Call function
        result = create_briefing_script(None, articles, podcasts)
        
        # Verify limits are applied in the prompt
        call_args = mock_model.generate_content.call_args[0][0]
        
        # Should only include first 5 articles
        assert "1. Article 0" in call_args
        assert "5. Article 4" in call_args
        assert "6. Article 5" not in call_args
        
        # Should only include first 3 podcasts
        assert "1. 'Episode 0'" in call_args
        assert "3. 'Episode 2'" in call_args
        assert "4. 'Episode 3'" not in call_args
        
    @patch('summarizer.get_config')
    def test_create_briefing_script_fallback_minimal_data(self, mock_config):
        """Test fallback script generation with minimal data."""
        # Mock configuration failure to trigger fallback
        mock_config.side_effect = Exception("API connection failed")
        
        # Call function with minimal data
        result = create_briefing_script(None, [], [])
        
        # Verify fallback script content
        assert "Good morning!" in result
        assert "daily briefing" in result
        assert "Have a great day!" in result 