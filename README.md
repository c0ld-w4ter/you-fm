# AI Daily Briefing Agent

A serverless application that generates personalized, AI-powered daily audio news briefings. The system automatically fetches content from multiple sources, summarizes it using AI, converts it to speech, and delivers it as an audio file.

## 🏗️ Project Status

**Current Status**: Milestone 3 ✅ Complete  
**Next**: Milestone 4 - Cloud Migration & Deployment

### Milestone Progress
- ✅ **Milestone 0**: Secure Setup & Configuration
- ✅ **Milestone 1**: Live Data Aggregation  
- ✅ **Milestone 2**: AI Summarization with Google Gemini
- ✅ **Milestone 3**: Audio Generation & Delivery
- 🔄 **Milestone 4**: Cloud Migration & Deployment

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

4. **Set up environment variables** (required for full functionality):
   
   Set the following environment variables in your shell:
   ```bash
   export NEWSAPI_KEY="your_newsapi_key_here"
   export OPENWEATHER_API_KEY="your_openweather_key_here"
   export TADDY_API_KEY="your_taddy_api_key_here"
   export TADDY_USER_ID="your_taddy_user_id_here"
   export GEMINI_API_KEY="your_google_gemini_key_here"
   export ELEVENLABS_API_KEY="your_elevenlabs_key_here"
   # export S3_BUCKET_NAME="your_bucket_name"  # Optional: Currently saves audio locally
   ```

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
Current test coverage includes **60 comprehensive tests** covering:
- ✅ Configuration loading and validation (10 tests)
- ✅ Environment variable handling and error cases
- ✅ Live data fetching from external APIs (10 tests)
- ✅ API response parsing and validation
- ✅ Error handling for API failures
- ✅ **AI summarization with Google Gemini (10 tests)**
- ✅ **AI-generated briefing script creation**
- ✅ **Text-to-Speech generation with ElevenLabs (12 tests)**
- ✅ **Amazon S3 upload and authentication (18 tests)**
- ✅ **Complete audio pipeline integration**
- ✅ **Comprehensive error handling and fallbacks**

## 🔧 Configuration

The application requires several API keys to function fully:

### Required Environment Variables
```bash
NEWSAPI_KEY=your_newsapi_key_here
OPENWEATHER_API_KEY=your_openweather_key_here
TADDY_API_KEY=your_taddy_api_key_here
TADDY_USER_ID=your_taddy_user_id_here
GEMINI_API_KEY=your_google_gemini_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here
```

### Optional Configuration
```bash
# Briefing duration in minutes (default: 3)
BRIEFING_DURATION_MINUTES=3

# Listener name for personalized greetings (optional)
LISTENER_NAME=Alice

# Location settings (default: Denver, US)
LOCATION_CITY=Denver
LOCATION_COUNTRY=US

# News topics (default: technology,business,science)
NEWS_TOPICS=technology,business,science

# Maximum articles per topic (default: 3)
MAX_ARTICLES_PER_TOPIC=3

# Podcast categories (default: Technology,Business,Science)
PODCAST_CATEGORIES=Technology,Business,Science

# ElevenLabs voice ID (default: default)
ELEVENLABS_VOICE_ID=default
```
S3_BUCKET_NAME=your_s3_bucket_name_here
```

### Optional Configuration (with defaults)
```bash
LOCATION_CITY=San Francisco
LOCATION_COUNTRY=US
NEWS_TOPICS=technology,business,science
MAX_ARTICLES_PER_TOPIC=3
PODCAST_CATEGORIES=Technology,Business,Science
```

### Getting API Keys
1. **NewsAPI**: Register at [newsapi.org](https://newsapi.org/)
2. **OpenWeatherMap**: Sign up at [openweathermap.org](https://openweathermap.org/api)
3. **Taddy**: Get API key and User ID at [taddy.org](https://taddy.org/developers)
4. **Google Gemini**: Access via [Google AI Studio](https://makersuite.google.com/)
5. **ElevenLabs**: Sign up at [elevenlabs.io](https://elevenlabs.io/)
6. **Amazon S3**: Create S3 bucket and configure permissions

## 🏃 Running the Application

### Current Functionality (Milestone 3)
The application now provides a complete end-to-end audio briefing solution:

```bash
# Activate virtual environment
source venv/bin/activate

# Run the main application (requires API keys to be set)
python main.py
```

**Expected Output**: 
- Console logs showing the complete audio generation pipeline
- AI script generated from live data (weather, news, podcasts)
- High-quality audio file generated using ElevenLabs TTS
- Audio file saved locally (e.g., `daily_briefing_20250128_140000.mp3`)
- Text script saved locally (`briefing_script.txt`)
- Success message with local file paths and audio details

**Complete Features**:
- ✅ **Live Data Aggregation**: Weather, News, and Podcast data fetching
- ✅ **AI Summarization**: Google Gemini 2.5 Pro for article summaries
- ✅ **AI Script Generation**: Natural, professional briefing scripts
- ✅ **Text-to-Speech**: High-quality audio generation via ElevenLabs
- ✅ **Local File Output**: Audio and script files saved with timestamps
- ✅ **Intelligent Selection**: Top 5 articles, top 3 podcasts
- ✅ **Robust Error Handling**: Fallbacks for all external API failures
- ✅ **Configurable Duration**: Customize briefing length via `BRIEFING_DURATION_MINUTES`
- ✅ **Personal Touch**: Personalized greetings using `LISTENER_NAME`

**Note**: You need to set all required environment variables (including `GEMINI_API_KEY` and `ELEVENLABS_API_KEY`) for the complete audio briefing functionality. Google Drive setup is optional - audio files are currently saved locally.

> **💡 TTS Testing Mode**: The application currently saves audio files locally for easy testing. To re-enable S3 upload, uncomment the `S3_BUCKET_NAME` line in `config.py` and update the `main.py` import to use `upload_to_s3` instead of `save_audio_locally`.

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

### Future Functionality
After upcoming milestones, the application will:  
- Convert text to speech using ElevenLabs (Milestone 3)
- Upload audio files to Google Drive (Milestone 3)
- Deploy to AWS Lambda for automated daily execution (Milestone 4)

## 🏗️ Technical Design

For a comprehensive understanding of the system architecture, data flow, and implementation details, see our detailed technical documentation:

**📖 [Technical Design Document](TECHNICAL_DESIGN.md)**

This document covers:
- **System Architecture**: Modular serverless design with visual diagrams
- **Data Flow**: Four-phase pipeline from data aggregation to audio delivery
- **Module Design**: Detailed breakdown of each component's responsibilities
- **API Integrations**: External service integrations with error handling strategies
- **Testing Architecture**: 60 comprehensive tests with mocking strategies
- **Performance Considerations**: Optimization and scalability approaches

Perfect for new developers joining the project or understanding the technical implementation details.

## 📁 Project Structure

```
ai-daily-briefing-agent/
├── main.py                 # Main Lambda handler and orchestration (✅ Milestone 3)
├── config.py               # Configuration management (✅ Complete)
├── data_fetchers.py        # External API data fetching (✅ Complete)
├── summarizer.py           # AI summarization with Gemini API (✅ Complete)
├── tts_generator.py        # Text-to-speech with ElevenLabs (✅ Complete)
├── uploader.py             # Amazon S3 file upload (✅ Complete)
├── tests/                  # Unit tests (60 tests)
│   ├── test_config.py      # Configuration tests (✅ Complete)
│   ├── test_data_fetchers.py # Data fetching tests (✅ Complete)
│   ├── test_summarizer.py  # AI summarization tests (✅ Complete)
│   ├── test_tts_generator.py # Text-to-speech tests (✅ Complete)
│   └── test_uploader.py    # Amazon S3 upload tests (✅ Complete)
├── requirements.txt        # Python dependencies
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

## 📋 Next Steps

1. **Milestone 4**: Cloud Migration & Deployment
   - Migrate environment variables to AWS Secrets Manager
   - Deploy application to AWS Lambda with EventBridge scheduling
   - Set up automated daily execution in the cloud

2. **Production Setup**: Configure AWS infrastructure
   - Create AWS Lambda function
   - Set up EventBridge daily trigger
   - Configure IAM roles and permissions

3. **Monitor Deployment**: Verify scheduled execution and CloudWatch logs

## 🐛 Troubleshooting

### Common Issues

**"Missing required environment variables"**
- Ensure all required API keys are set in your environment
- Check `.env` file exists and is properly formatted
- Verify virtual environment is activated

**"ModuleNotFoundError"**
- Ensure virtual environment is activated: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

**Tests failing**
- Check Python version (3.11+ required)
- Ensure pytest is installed: `pip install pytest`
- Run tests from project root directory

**"Configuration error" when running application**
- This is expected without API keys set
- The application will work when you provide the required API keys
- You can still run unit tests without API keys

## 📄 License

This project is part of a technical specification implementation for an AI Daily Briefing Agent system.

---

*Last updated: Milestone 1 completion* 
