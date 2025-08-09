# You.FM

An application to generate personalized podcast audio using AI. 

## 🚀 Quick Start

### Prerequisites
- Python 3.11+ (tested with Python 3.11.13)
- Virtual environment (recommended)

> **Note**: If Python 3.11 is not installed, you can install it via:
> - **macOS**: `brew install python@3.11`
> - **Ubuntu/Debian**: `sudo apt install python3.11`
> - **Other platforms**: Download from [python.org](https://www.python.org/downloads/)

### Setup

1. **Clone and navigate to the project**:
   ```bash
   cd you-fm
   ```

2. **Create and activate virtual environment**:
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the web application**:
   ```bash
   source venv/bin/activate  # If not already activated
   python app.py
   ```

5. **Access the web interface**:
   - Open your browser and navigate to: `http://localhost:8080`
   - Fill in your API keys through the web form (see Getting API Keys section below)
   - Configure your preferences and generate your first briefing!

## 🧪 Running Tests

### Unit Tests
Run the complete test suite:
```bash
# Activate virtual environment first
source venv/bin/activate

# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_config.py -v
```

## 🔧 Configuration

The application can be configured through the **web interface** or via environment variables. The web interface is the recommended approach for ease of use.

### Web Interface Configuration
1. Start the application with `python app.py`
2. Navigate to `http://localhost:8080`
3. Fill out the configuration form with your API keys and preferences
4. All settings are configured through the web form

### Required API Keys
The following API keys are required and can be entered through the web form:
- **NewsAPI.ai Key**: For fetching news articles
- **OpenWeatherMap API Key**: For weather data
- **Google Gemini API Key**: For AI summarization and script generation
- **ElevenLabs API Key**: For text-to-speech conversion


### Environment Variables Config Setup (Alternative)
For automated/CLI usage, you can still use environment variables:
```bash
# Required API Keys
NEWSAPI_AI_KEY=your_newsapi_ai_key_here
OPENWEATHER_API_KEY=your_openweather_key_here
GEMINI_API_KEY=your_google_gemini_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here

# Optional Personalization Defaults (New in UI Simplification)
DEFAULT_INTERESTS="artificial intelligence, machine learning, startup news"
# DEFAULT_BRIEFING_GOAL removed - hardcoded to 'work' for simplicity
DEFAULT_ENTITIES="tech industry, major tech companies"
DEFAULT_HOBBIES="reading tech blogs, podcasts"
DEFAULT_TEAMS_ARTISTS=""
DEFAULT_PASSION_TOPICS="technology trends, innovation"
DEFAULT_GREETING="Good morning! Here is your essential tech and business update."
DEFAULT_ROUTINE="I listen during my morning coffee"

# Other optional settings...
```

### Getting API Keys
1. **NewsAPI.ai**: Register at [newsapi.ai](https://newsapi.ai/) 
2. **OpenWeatherMap**: Sign up at [openweathermap.org](https://openweathermap.org/api)
3. **Google Gemini**: Access via [Google AI Studio](https://makersuite.google.com/) (make sure you have the gemini genrative language API enabled in Google Cloud)
4. **ElevenLabs**: Sign up at [elevenlabs.io](https://elevenlabs.io/)


## 🐛 Troubleshooting

### Common Issues

**"Port 5000 is in use by another program"**
- The application now uses port 8080 instead of 5000
- If port 8080 is also in use, modify the port in `app.py`
- Check what's using the port: `lsof -i :8080`

**"Missing required API keys" in web interface**
- Fill in all required API key fields on Page 1 (API Keys)
- API keys are validated when you submit each page
- The multi-page flow guides you through: API Keys → Settings → Generate → Results
- No need to set environment variables when using the web interface

**"ModuleNotFoundError"**
- Ensure virtual environment is activated: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`
- Check you're running Python 3.11+

**Web interface not loading**
- Verify the application started successfully: look for "Running on http://localhost:8080"
- Check browser console for JavaScript errors
- Try accessing `http://127.0.0.1:8080` instead of localhost
- The home page (/) redirects to /api-keys automatically

**Audio generation fails**
- Verify all API keys are entered correctly on the API Keys page
- Check browser network tab for API errors during generation
- The loading modal should show step-by-step progress during generation
- ElevenLabs API has usage limits - check your account status

**Tests failing**
- Check Python version (3.11+ required)
- Ensure pytest is installed: `pip install pytest`
- Run tests from project root directory: `python -m pytest tests/ -v`
- Note: Tests have been updated for the new multi-page architecture

**Performance issues**
- Audio generation can take 2-5 minutes depending on content length
- The loading modal shows real-time progress with 5 distinct steps
- Large news articles may increase processing time
- The multi-page flow prevents accidental navigation during generation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
