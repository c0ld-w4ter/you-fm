# AI Daily Briefing Agent

A modern web application that generates personalized, AI-powered daily audio news briefings. The system features an intuitive web interface where users can configure their preferences and generate custom audio briefings from multiple data sources including news and weather.

## 🏗️ Project Status

**Current Status**: UI Simplified ✅ Complete - Streamlined for Fast Iteration  
**Previous**: Milestone 5 ✅ Complete - Enhanced Customization  
**Next**: Milestone 6 - Production Deployment

### 🚀 Recent UI Simplification
The interface has been significantly streamlined to enable **rapid testing and development**:
- ⚡ **Pre-populated Defaults**: All personalization fields now have smart defaults
- 📰 **Comprehensive News**: Automatically fetches all news categories (no user selection needed)
- 🎯 **Simplified Settings**: Removed complex options (content depth, voice speed, keyword exclusion)
- 🕐 **5-minute Default**: Extended default briefing length for more content
- 🤖 **AI Curation**: Let AI handle content filtering instead of manual keyword exclusion

### Milestone Progress
- ✅ **Milestone 0**: Secure Setup & Configuration
- ✅ **Milestone 1**: Live Data Aggregation  
- ✅ **Milestone 2**: AI Summarization with Google Gemini
- ✅ **Milestone 3**: Audio Generation & Delivery
- ✅ **Milestone 4**: Web UI MVP
- ✅ **Milestone 5**: Enhanced Customization

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
   cd ai-daily-briefing-agent
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

### Test Coverage
Current test coverage includes **110+ comprehensive tests** covering:
- ✅ Configuration loading and validation (21 tests)
- ✅ Environment variable handling and error cases
- ✅ Live data fetching from external APIs (10 tests)
- ✅ API response parsing and validation
- ✅ Error handling for API failures
- ✅ **AI summarization with Google Gemini (17 tests)**
- ✅ **Style-aware AI script generation with filtering**
- ✅ **Text-to-Speech generation with ElevenLabs (12 tests)**
- ✅ **Amazon S3 upload and authentication (18 tests)**
- ✅ **Web interface and form validation (37 tests)**
- ✅ **Advanced customization features and preview functionality**
- ✅ **Route handlers and configuration integration**
- ✅ **Complete audio pipeline integration**
- ✅ **Comprehensive error handling and fallbacks**

## 🔧 Configuration

The application can be configured through the **web interface** or via environment variables. The web interface is the recommended approach for ease of use.

### Web Interface Configuration
1. Start the application with `python app.py`
2. Navigate to `http://localhost:8080`
3. Fill out the configuration form with your API keys and preferences
4. All settings are configured through the intuitive web form

### Required API Keys
The following API keys are required and can be entered through the web form:
- **NewsAPI.ai Key**: For fetching news articles (replacement for NewsAPI.org)
- **OpenWeatherMap API Key**: For weather data
- **Google Gemini API Key**: For AI summarization and script generation
- **ElevenLabs API Key**: For high-quality text-to-speech conversion

### Optional Configuration (via Web Interface)
**Simplified UI for Fast Iteration** - Configuration made streamlined for rapid development:

**Basic Settings** (User Configurable):
- **Listener Name**: For personalized greetings (pre-populated)
- **Location**: City and country code (default: Denver, US)
- **Briefing Duration**: Target length in minutes (default: 5 minutes)
- **Voice Selection**: Choose from multiple ElevenLabs/Google TTS voices
- **Briefing Tone**: Professional, Casual, or Energetic

**Auto-Configured Settings** (Optimized for Speed):
- **News Topics**: All categories (business, entertainment, general, health, science, sports, technology)
- **Max Articles**: 100 per topic for comprehensive coverage
- **Content Depth**: Balanced (hardcoded for optimal results)
- **Voice Speed**: Normal (users can adjust in audio player)
- **Content Filtering**: AI-powered (removed keyword exclusion for better curation)

**Personalization Fields** (Pre-populated with Smart Defaults):
- **Specific Interests**: What topics you care about most
- **Briefing Goal**: Your primary listening objective  
- **Followed Entities**: Industries or figures you follow
- **Hobbies & Interests**: Personal activities and passions
- **Greeting & Routine**: How you prefer to be addressed

### Environment Variables (Alternative)
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
1. **NewsAPI.ai**: Register at [newsapi.ai](https://newsapi.ai/) (replacement for NewsAPI.org with better pricing and features)
2. **OpenWeatherMap**: Sign up at [openweathermap.org](https://openweathermap.org/api)
3. **Google Gemini**: Access via [Google AI Studio](https://makersuite.google.com/) (make sure you have the gemini genrative language API enabled in Google Cloud)
4. **ElevenLabs**: Sign up at [elevenlabs.io](https://elevenlabs.io/) for cost-effective voice generation (using Flash v2.5 model)


## 🏃 Running the Application

### Current Functionality (Milestone 5 - Enhanced Customization)
The application now provides a modern multi-page web interface for generating personalized audio briefings:

```bash
# Activate virtual environment
source venv/bin/activate

# Start the web application
python app.py
```

**Then open your browser and go to: `http://localhost:8080`**

### Web Interface Features:
- 🎯 **Multi-Page Flow**: Clean step-by-step process (API Keys → Settings → Generate → Results)
- 🔄 **Progress Indicators**: Visual progress tracking across all steps
- 🔑 **Secure API Key Entry**: Dedicated page for API key configuration
- 👤 **Personal Customization**: Separate settings page with organized sections
- 📰 **Content Control**: Configurable news topics and article limits
- 🎧 **Audio Options**: Voice selection, speed control, and duration management
- 📊 **Real-time Feedback**: Immediate loading modal with step-by-step progress
- 🎵 **Built-in Player**: Listen to your briefing directly in the browser
- 📥 **Download Option**: Save audio files for offline listening
- 📈 **Generation Statistics**: Performance metrics and configuration display
- 🔒 **Session Management**: Settings persist between pages during configuration
- **🎛️ Advanced Customization (New in Milestone 5)**:
  - **📝 Script Preview**: Fast script generation (10-20s) before audio creation
  - **🎨 Style Control**: Professional, casual, or energetic briefing tones  
  - **📊 Content Depth**: Headlines-only, balanced, or detailed analysis
  - **🚫 Keyword Filtering**: Exclude unwanted topics with smart filtering
  - **🎯 Organized UI**: Collapsible sections with logical field grouping

### Complete Pipeline Features:
- ✅ **Live Data Aggregation**: Weather and News data fetching
- ✅ **AI Summarization**: Google Gemini 2.5 Pro for article summaries
- ✅ **AI Script Generation**: Natural, professional briefing scripts
- ✅ **Text-to-Speech**: Cost-optimized audio generation via ElevenLabs Flash v2.5 (50% cost savings)
- ✅ **Multi-Page Interface**: Intuitive step-by-step configuration process
- ✅ **Local File Storage**: Audio files saved in `static/audio/` directory
- ✅ **Intelligent Selection**: AI-powered story prioritization
- ✅ **Robust Error Handling**: Fallbacks for all external API failures
- ✅ **Personal Touch**: Fully customizable personalization options

### Usage Workflow:
1. **Start the application**: `python app.py`
2. **Open browser**: Navigate to `http://localhost:8080`
3. **Page 1 - API Keys**: Enter all required API keys → "Save API Keys & Continue"
4. **Page 2 - Settings**: Configure personal preferences → "Save Settings & Continue"  
5. **Page 3 - Generate**: Review configuration → Click "🎧 Generate Daily Briefing"
6. **Loading Screen**: Real-time progress bar with step-by-step updates
7. **Page 4 - Results**: Listen with built-in player or download the MP3

## ⏱️ Configurable Duration & Personalization

### Duration
Set `BRIEFING_DURATION_MINUTES` to customize briefing length (default: 3 minutes):

```bash
export BRIEFING_DURATION_MINUTES=1  # Quick updates
export BRIEFING_DURATION_MINUTES=5  # Detailed coverage
```

### Personal Touch
Set `LISTENER_NAME` to personalize greetings and closings:

```bash
export LISTENER_NAME="Alice"  # "Good morning, Alice!"
export LISTENER_NAME="John"   # "Good morning, John!"
# Leave unset for generic greetings
```

## 🏗️ Technical Documentation

We maintain comprehensive technical documentation in two focused documents:

### **📖 Current Implementation**
**[TECHNICAL_DESIGN_CURRENT.md](TECHNICAL_DESIGN_CURRENT.md)** - Details of what's built (Milestone 4)
- **System Architecture**: Current Flask web application design with visual diagrams
- **Data Flow**: Four-phase pipeline from user request to audio delivery
- **Module Design**: Detailed breakdown of each implemented component
- **API Integrations**: Current external service integrations with error handling
- **Testing Architecture**: 81+ comprehensive tests with mocking strategies

## 📁 Project Structure

```
ai-daily-briefing-agent/
├── app.py                  # Flask application entry point (✅ Milestone 4)
├── config_web.py           # Web form to config mapping (✅ Milestone 4)
├── web/                    # Web interface modules (✅ Milestone 4)
│   ├── __init__.py         # Web module initialization
│   ├── routes.py           # Flask route handlers with multi-page flow
│   ├── forms.py            # Web form validation (APIKeysForm, SettingsForm)
│   └── utils.py            # Web utility functions
├── templates/              # Jinja2 HTML templates (✅ Milestone 4)
│   ├── base.html           # Base template with Tailwind CSS
│   ├── api_keys.html       # Page 1: API Keys configuration
│   ├── settings.html       # Page 2: Personal settings
│   ├── generate.html       # Page 3: Generate briefing with big button
│   └── results.html        # Page 4: Results and audio player
├── static/                 # Static web assets (✅ Milestone 4)
│   ├── css/style.css       # Custom styling
│   ├── js/app.js           # JavaScript enhancements
│   └── audio/              # Generated audio files
├── main.py                 # Core business logic (✅ Milestone 3)
├── config.py               # Configuration management (✅ Complete)
├── data_fetchers.py        # External API data fetching (✅ Complete)
├── summarizer.py           # AI summarization with Gemini API (✅ Complete)
├── tts_generator.py        # Text-to-speech with ElevenLabs (✅ Complete)
├── uploader.py             # Amazon S3 file upload (✅ Complete)
├── tests/                  # Unit tests (81+ tests)
│   ├── test_config.py      # Configuration tests (✅ Complete)
│   ├── test_data_fetchers.py # Data fetching tests (✅ Complete)
│   ├── test_summarizer.py  # AI summarization tests (✅ Complete)
│   ├── test_tts_generator.py # Text-to-speech tests (✅ Complete)
│   ├── test_uploader.py    # Amazon S3 upload tests (✅ Complete)
│   └── test_web.py         # Web interface tests (✅ Milestone 4)
├── requirements.txt        # Python dependencies (updated for Flask)
├── iam_policy.json         # AWS Lambda execution policy
└── .gitignore             # Git ignore rules
```

## 🔒 Security

- **No hardcoded secrets**: All API keys loaded from environment variables
- **Graceful error handling**: Missing configuration handled safely
- **AWS IAM policy**: Minimal permissions for Lambda execution
- **Environment isolation**: Virtual environment for dependencies

## 🛠️ Development

### Adding New Tests
```bash
# Create test file in tests/ directory
# Follow the naming convention: test_<module>.py
# Run tests to verify
python -m pytest tests/test_<module>.py -v
```

### Code Style
- Type hints for function parameters and return values
- Comprehensive docstrings for all functions
- Modular design with clear separation of concerns
- Error handling with custom exceptions


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
- Audio generation can take 60-90 seconds depending on content length
- The loading modal shows real-time progress with 5 distinct steps
- Large news articles may increase processing time
- The multi-page flow prevents accidental navigation during generation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
