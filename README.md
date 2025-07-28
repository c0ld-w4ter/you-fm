# AI Daily Briefing Agent

A serverless application that generates personalized, AI-powered daily audio news briefings. The system automatically fetches content from multiple sources, summarizes it using AI, converts it to speech, and delivers it as an audio file.

## 🏗️ Project Status

**Current Status**: Milestone 1 ✅ Complete  
**Next**: Milestone 2 - AI Summarization

### Milestone Progress
- ✅ **Milestone 0**: Secure Setup & Configuration
- ✅ **Milestone 1**: Live Data Aggregation  
- 🔄 **Milestone 2**: AI Summarization
- ⏳ **Milestone 3**: Audio Generation & Delivery
- ⏳ **Milestone 4**: Cloud Migration & Deployment

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
   export GOOGLE_DRIVE_FOLDER_ID="your_google_drive_folder_id_here"
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
Current test coverage focuses on:
- ✅ Configuration loading and validation
- ✅ Environment variable handling  
- ✅ Error handling for missing configuration
- ✅ Live data fetching from external APIs
- ✅ API response parsing and validation
- ✅ Error handling for API failures

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
GOOGLE_DRIVE_FOLDER_ID=your_google_drive_folder_id_here
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
6. **Google Drive**: Set up service account and get folder ID

## 🏃 Running the Application

### Current Functionality (Milestone 1)
The application now fetches live data from external APIs and generates a text briefing:

```bash
# Activate virtual environment
source venv/bin/activate

# Run the main application (requires API keys to be set)
python main.py
```

**Expected Output**: 
- Console logs showing data fetching progress
- A `briefing.txt` file containing current weather, news articles, and podcast episodes
- Success message with data counts

**Note**: You need to set the required environment variables (API keys) for the application to work with real data. Without API keys, you'll see configuration errors.

### Future Functionality
After upcoming milestones, the application will:
- Generate AI summaries using Google Gemini (Milestone 2)  
- Convert text to speech using ElevenLabs (Milestone 3)
- Upload audio files to Google Drive (Milestone 3)
- Deploy to AWS Lambda for automated daily execution (Milestone 4)

## 📁 Project Structure

```
ai-daily-briefing-agent/
├── main.py                 # Main Lambda handler and orchestration (✅ Milestone 1)
├── config.py               # Configuration management (✅ Complete)
├── data_fetchers.py        # External API data fetching (✅ Complete)
├── summarizer.py           # AI summarization with Gemini API (🔄 Next)
├── tts_generator.py        # Text-to-speech with ElevenLabs
├── uploader.py             # Google Drive file upload
├── tests/                  # Unit tests
│   ├── test_config.py      # Configuration tests (✅ Complete)
│   └── test_data_fetchers.py # Data fetching tests (✅ Complete)
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

1. **Milestone 2**: Implement AI summarization
   - Integrate Google Gemini API for article summarization
   - Create cohesive briefing script generation
   - Update tests for summarization functionality

2. **Get API Keys**: Sign up for required services and configure environment variables

3. **Test Manual Workflow**: Run `python main.py` with API keys to generate live briefing

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