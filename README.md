# AI Daily Briefing Agent

A serverless application that generates personalized, AI-powered daily audio news briefings. The system automatically fetches content from multiple sources, summarizes it using AI, converts it to speech, and delivers it as an audio file.

## 🏗️ Project Status

**Current Status**: Milestone 2 ✅ Complete  
**Next**: Milestone 3 - Audio Generation & Delivery

### Milestone Progress
- ✅ **Milestone 0**: Secure Setup & Configuration
- ✅ **Milestone 1**: Live Data Aggregation  
- ✅ **Milestone 2**: AI Summarization with Google Gemini
- 🔄 **Milestone 3**: Audio Generation & Delivery
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
Current test coverage includes **30 comprehensive tests** covering:
- ✅ Configuration loading and validation (10 tests)
- ✅ Environment variable handling  
- ✅ Error handling for missing configuration
- ✅ Live data fetching from external APIs (10 tests)
- ✅ API response parsing and validation
- ✅ Error handling for API failures
- ✅ **AI summarization with Google Gemini (10 tests)**
- ✅ **AI-generated briefing script creation**
- ✅ **Fallback handling for AI failures**

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

### Current Functionality (Milestone 2)
The application fetches live data from external APIs, summarizes articles with AI, and generates an enhanced briefing:

```bash
# Activate virtual environment
source venv/bin/activate

# Run the main application (requires API keys to be set)
python main.py
```

**Expected Output**: 
- Console logs showing data fetching and AI summarization progress
- A `briefing.txt` file containing the AI-enhanced briefing script
- A `briefing_raw.txt` file containing the raw data for comparison
- Success message with data counts and file paths

**New Features**:
- ✅ AI-powered article summarization using Google Gemini 2.5 Pro
- ✅ **AI-generated briefing scripts** - Natural, professional scripts created entirely by AI
- ✅ Intelligent content selection (top 5 articles, top 3 podcasts)
- ✅ Dynamic script formatting based on available data
- ✅ Robust fallback handling for API failures

**Note**: You need to set all required environment variables (including `GEMINI_API_KEY`) for the application to work with real data.

### Future Functionality
After upcoming milestones, the application will:  
- Convert text to speech using ElevenLabs (Milestone 3)
- Upload audio files to Google Drive (Milestone 3)
- Deploy to AWS Lambda for automated daily execution (Milestone 4)

## 📁 Project Structure

```
ai-daily-briefing-agent/
├── main.py                 # Main Lambda handler and orchestration (✅ Milestone 2)
├── config.py               # Configuration management (✅ Complete)
├── data_fetchers.py        # External API data fetching (✅ Complete)
├── summarizer.py           # AI summarization with Gemini API (✅ Complete)
├── tts_generator.py        # Text-to-speech with ElevenLabs (🔄 Next)
├── uploader.py             # Google Drive file upload
├── tests/                  # Unit tests
│   ├── test_config.py      # Configuration tests (✅ Complete)
│   ├── test_data_fetchers.py # Data fetching tests (✅ Complete)
│   └── test_summarizer.py  # AI summarization tests (✅ Complete)
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

1. **Milestone 3**: Implement audio generation and delivery
   - Integrate ElevenLabs API for text-to-speech conversion
   - Implement Google Drive API for file upload
   - Create end-to-end audio briefing workflow

2. **Get Additional API Keys**: If you haven't already, sign up for ElevenLabs and configure Google Drive credentials

3. **Test Complete Workflow**: Run `python main.py` with all API keys to generate AI-enhanced briefing

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