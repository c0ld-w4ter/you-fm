# Technical Specification: AI Daily Briefing Agent

**Version:** 2.0
**Date:** January 28, 2025
**Status:** In Development - Web UI Phase

---

### 1. Project Overview

This document provides a complete technical blueprint for building an AI-powered daily audio news briefing application with a modern web interface. The system has evolved from a serverless CLI application to a comprehensive web-based platform that generates personalized audio briefings through an intuitive user interface.

The application fetches content from multiple online sources, summarizes it using Large Language Models (LLM), converts the resulting script to speech, and delivers it as audio files through a web interface. The system supports multiple users, advanced customization, scheduled generation, and extensive data source integration.

The development plan follows iterative, testable milestones to facilitate rapid, test-driven development with clear validation at each stage.

---

### 2. Architecture & Technology Stack

#### **Core Architecture**
* **Language:** Python 3.11
* **Web Framework:** Flask (development) → ECS Fargate (production)
* **Database:** SQLite (development) → RDS PostgreSQL (production)
* **Frontend:** HTML5 + Vanilla JavaScript + Tailwind CSS
* **Task Processing:** Celery + Redis (for scheduling)
* **Testing Framework:** `pytest`

#### **Development vs Production Architecture**
**Development (Milestones 4-5):**
- Local Flask application
- SQLite database
- Local file system storage
- Environment variable configuration

**Production (Milestone 6+):**
- AWS ECS Fargate containerized deployment
- RDS PostgreSQL database
- S3 storage with CloudFront CDN
- AWS Secrets Manager for configuration
- Application Load Balancer

#### **Python Libraries**
* `flask`: Web application framework
* `flask-login`: User session management
* `flask-wtf`: Form handling and CSRF protection
* `sqlalchemy`: Database ORM
* `celery`: Background task processing
* `redis`: Message broker and caching
* `requests`: REST API calls and GraphQL queries
* `boto3`: AWS SDK for cloud services
* `google-generativeai`: Google Gemini API client
* `elevenlabs`: ElevenLabs TTS API client
* `werkzeug`: Security utilities

#### **External Services & APIs**
* **News Source:** NewsAPI
* **Weather Source:** OpenWeatherMap API
* **Podcast Source:** Taddy API (GraphQL)
* **AI Summarization:** Google Gemini API
* **Text-to-Speech (TTS):** ElevenLabs API
* **Extended Sources:** RSS feeds, Reddit API, Financial data APIs
* **Cloud Services:** AWS (ECS, RDS, S3, CloudFront, Secrets Manager)

---

### 3. Project Structure

The application follows a modular web architecture with clear separation between business logic and web interface components.

```text
ai-daily-briefing-agent/
├── app.py                      # Flask application entry point
├── web/                        # Web-specific modules
│   ├── __init__.py
│   ├── routes.py              # Flask route handlers
│   ├── forms.py               # Web form validation
│   └── utils.py               # Web utility functions
├── templates/                  # Jinja2 HTML templates
│   ├── base.html              # Base template
│   ├── index.html             # Configuration form
│   ├── generate.html          # Generation progress/results
│   ├── login.html             # User authentication
│   ├── dashboard.html         # User dashboard
│   └── admin/                 # Admin interface templates
├── static/                     # Static web assets
│   ├── css/
│   │   └── style.css          # Tailwind CSS styling
│   ├── js/
│   │   ├── app.js             # Main application JavaScript
│   │   └── audio-player.js    # Custom audio player
│   └── audio/                 # Generated briefing files
├── auth/                       # Authentication system
│   ├── __init__.py
│   ├── models.py              # User models
│   └── routes.py              # Auth routes
├── db/                         # Database components
│   ├── __init__.py
│   ├── models.py              # Database models
│   └── migrations/            # Database migration scripts
├── scheduler/                  # Background task system
│   ├── __init__.py
│   ├── tasks.py               # Celery tasks
│   └── scheduler.py           # Scheduling logic
├── data_sources/               # Extended data source framework
│   ├── __init__.py
│   ├── base.py                # Base data source interface
│   ├── rss.py                 # RSS feed integration
│   ├── reddit.py              # Reddit API integration
│   └── finance.py             # Financial data integration
├── infrastructure/             # AWS deployment code
│   ├── terraform/             # Infrastructure as Code
│   └── docker/                # Container configuration
├── config_web.py              # Web-specific configuration
├── main.py                    # Core business logic (unchanged)
├── config.py                  # Base configuration management
├── data_fetchers.py           # External API data fetching
├── summarizer.py              # AI summarization with Gemini
├── tts_generator.py           # Text-to-speech generation
├── uploader.py                # File upload handling
├── tests/                     # Comprehensive test suite
│   ├── test_web.py            # Web interface tests
│   ├── test_auth.py           # Authentication tests
│   ├── test_multi_user.py     # Multi-user functionality tests
│   ├── test_scheduling.py     # Scheduling system tests
│   ├── test_data_sources.py   # Extended data source tests
│   ├── test_security.py       # Security validation tests
│   └── [existing test files]
├── requirements.txt           # Python dependencies
├── docker-compose.yml         # Local development environment
└── README.md                  # Updated documentation
```

### 4. Data Structures

The application uses well-defined data structures for consistency across all modules.

#### **Core Data Models**
* **`Article`**: Contains `title`, `source`, `url`, `content`, `summary`, and metadata
* **`PodcastEpisode`**: Contains `podcast_title`, `episode_title`, `url`, `date_published`
* **`WeatherData`**: Contains `city`, `country`, `temperature`, `description`, `humidity`, `wind_speed`
* **`User`**: Contains `id`, `username`, `password_hash`, `created_at`, `is_admin`
* **`UserConfiguration`**: Contains `user_id`, `config_name`, `config_data` (JSONB), `is_default`
* **`BriefingHistory`**: Contains `user_id`, `config_id`, `filename`, `s3_key`, `generation_duration`

#### **Configuration Schema**
```python
CONFIGURATION_SCHEMA = {
    'basic': {
        'api_keys': {...},           # Required API keys
        'location': {...},           # City, country settings
        'briefing_preferences': {...} # Duration, listener name
    },
    'advanced': {
        'news_filtering': {...},     # Keywords, source filtering
        'briefing_style': {...},     # Tone, depth, personality
        'content_sections': {...},   # Enable/disable sections
        'audio_options': {...}       # Voice, speed, stability
    },
    'scheduling': {
        'enabled': False,
        'frequency': 'daily',        # daily, weekdays, custom
        'time': '07:00',            # Local time
        'timezone': 'UTC'
    }
}
```

---

### 5. Iterative Development Plan

The project follows a test-driven development approach with comprehensive validation at each milestone.

### **Milestones 0-3: Foundation (Completed)**

The first four milestones established the core functionality:
- ✅ **Milestone 0**: Secure configuration management
- ✅ **Milestone 1**: Live data aggregation from external APIs
- ✅ **Milestone 2**: AI summarization with Google Gemini
- ✅ **Milestone 3**: Audio generation and local file delivery

### **Milestone 4: Web UI MVP**

**Goal**: Create a simple local web interface that replaces command-line execution

**Technical Implementation**:
- Flask web application wrapping existing business logic
- HTML forms replace environment variable configuration
- Local file system storage for generated audio
- Synchronous request handling with progress indicators

**Key Components**:
1. **Flask Application (`app.py`)**: Main web server entry point
2. **Route Handlers (`web/routes.py`)**: HTTP endpoint implementations
3. **Form Validation (`web/forms.py`)**: Input sanitization and validation
4. **Configuration Handler (`config_web.py`)**: Web form to config object mapping
5. **Templates**: Jinja2 HTML templates with Tailwind CSS styling
6. **Static Assets**: JavaScript for form handling and audio playback

**Test Plan**:

**Unit Tests** (`tests/test_web.py`):
1. **Form Validation Tests**:
   - Test valid configuration submission
   - Test missing required fields (API keys)
   - Test invalid data types (non-numeric duration)
   - Test edge cases (empty strings, very long values)

2. **Route Handler Tests**:
   - Test GET `/` returns configuration form
   - Test POST `/generate` with valid data calls existing generation logic
   - Test POST `/generate` with invalid data returns error
   - Test audio file serving endpoint

3. **Configuration Integration Tests**:
   - Test web form data correctly maps to existing `Config` object
   - Test default values populate correctly
   - Test configuration validation integration

4. **Mock Integration Tests**:
   - Mock existing `generate_daily_briefing()` function
   - Test complete web workflow without external API calls
   - Test error handling for generation failures

**Manual Tests**:
1. **Basic Functionality**:
   - Start Flask app locally (`python app.py`)
   - Navigate to `http://localhost:8080`
   - Fill configuration form with valid API keys
   - Click "Generate Briefing" button
   - Verify briefing generation completes successfully
   - Verify audio file plays correctly

2. **Form Validation**:
   - Submit form with missing required fields
   - Submit form with invalid data types
   - Verify appropriate error messages display

3. **Error Handling**:
   - Submit form with invalid API keys
   - Verify graceful error handling and user feedback

### **Milestone 5: Enhanced Customization**

**Goal**: Add advanced customization features for personal testing and refinement

**Technical Implementation**:
- Extended configuration schema with advanced options
- Enhanced AI prompt generation based on user preferences
- Voice selection and audio customization
- Preview mode for faster iteration
- Tabbed interface for configuration complexity management

**New Components**:
1. **Advanced Configuration Schema**: Extended options for filtering, style, audio
2. **Enhanced Summarizer**: Style-aware prompt generation and content filtering
3. **Voice Options Integration**: ElevenLabs voice selection and parameter control
4. **Preview Functionality**: Script-only generation for rapid testing
5. **Advanced Web Interface**: Multi-tab configuration with real-time validation

**Test Plan**:

**Unit Tests** (`tests/test_advanced_config.py`):
1. **Advanced Configuration Tests**:
   - Test advanced config schema validation
   - Test config merging (basic + advanced options)
   - Test default advanced options handling

2. **Content Filtering Tests**:
   - Test keyword-based article filtering
   - Test source exclusion functionality
   - Test topic weighting application

3. **Style Customization Tests**:
   - Test different tone settings affect prompt generation
   - Test summary depth variations
   - Test personality setting integration

4. **Audio Customization Tests**:
   - Test voice selection integration
   - Test speed and stability parameter passing
   - Test preview mode functionality

**Manual Tests**:
1. **Advanced Configuration**:
   - Configure custom keywords and verify article filtering
   - Test different briefing tones and verify script changes
   - Test audio customization options

2. **Preview Functionality**:
   - Generate script-only preview
   - Verify faster generation time
   - Test iteration workflow (preview → adjust → preview)

3. **Voice Options**:
   - Test different ElevenLabs voices
   - Test speech speed variations
   - Verify audio quality with different settings

### **Milestone 6: AWS Deployment & Database Migration**

**Goal**: Deploy to AWS with proper database architecture

**Technical Implementation**:
- Migration from local Flask app to containerized ECS Fargate deployment
- Database migration from SQLite to RDS PostgreSQL
- S3 integration for audio file storage with CloudFront CDN
- Infrastructure as Code with Terraform
- Proper secret management with AWS Secrets Manager

**Architecture Components**:
1. **ECS Fargate**: Containerized Flask application deployment
2. **RDS PostgreSQL**: Persistent database for user data and configurations
3. **S3 + CloudFront**: Audio file storage and content delivery
4. **Application Load Balancer**: Traffic distribution and SSL termination
5. **Terraform Infrastructure**: Automated AWS resource provisioning

**Database Schema**:
```sql
-- Core user management
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User configuration management
CREATE TABLE user_configurations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    config_name VARCHAR(100) NOT NULL,
    config_data JSONB NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Briefing generation history
CREATE TABLE briefing_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    config_id INTEGER REFERENCES user_configurations(id),
    filename VARCHAR(255) NOT NULL,
    s3_key VARCHAR(500) NOT NULL,
    script_content TEXT,
    generation_duration_seconds INTEGER,
    file_size_bytes BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Test Plan**:

**Unit Tests** (`tests/test_aws_integration.py`):
1. **Database Tests**:
   - Test database connection and disconnection
   - Test user CRUD operations
   - Test configuration storage and retrieval
   - Test briefing history tracking

2. **S3 Integration Tests**:
   - Test audio file upload to S3 (mocked)
   - Test signed URL generation
   - Test file cleanup functionality

3. **Container Tests**:
   - Test application startup in container
   - Test health check endpoints
   - Test environment variable loading

**Integration Tests** (`tests/test_deployment.py`):
1. **Infrastructure Tests**:
   - Test Terraform plan validation
   - Test database migration scripts
   - Test ECS task definition

2. **End-to-End Tests**:
   - Test complete workflow in AWS environment
   - Test database persistence across container restarts
   - Test S3 file access through web interface

**Manual Tests**:
1. **Local Container Testing**:
   - Build Docker image locally
   - Test with docker-compose setup
   - Verify PostgreSQL connection

2. **AWS Deployment Testing**:
   - Deploy to AWS staging environment
   - Test complete briefing generation workflow
   - Verify S3 file access and persistence
   - Test application scaling and health checks

### **Milestone 7: Multi-User Foundation**

**Goal**: Support multiple users with individual preferences and secure authentication

**Technical Implementation**:
- User authentication system with Flask-Login
- Session management with Redis for scalability
- Per-user configuration management and isolation
- Basic admin interface for user management
- CSRF protection and security hardening

**Authentication System**:
1. **User Models**: SQLAlchemy ORM models for users and sessions
2. **Session Management**: Redis-backed session storage for horizontal scaling
3. **Password Security**: Werkzeug password hashing with salt
4. **Authorization**: Role-based access control (admin vs regular users)
5. **Admin Interface**: User management and system monitoring

**Test Plan**:

**Unit Tests** (`tests/test_multi_user.py`):
1. **Authentication Tests**:
   - Test user registration with valid data
   - Test login with correct credentials
   - Test login with incorrect credentials
   - Test session management and expiration

2. **User Configuration Tests**:
   - Test configuration creation and storage per user
   - Test configuration retrieval and updates
   - Test default configuration assignment
   - Test configuration isolation between users

3. **Authorization Tests**:
   - Test user can only access own configurations
   - Test user can only access own briefing history
   - Test admin access controls and privileges

4. **Admin Interface Tests**:
   - Test admin user creation and management
   - Test system monitoring data access
   - Test user activity tracking

**Manual Tests**:
1. **Multi-User Workflow**:
   - Register multiple test users
   - Configure different preferences per user
   - Generate briefings for each user
   - Verify complete isolation between users

2. **Admin Functionality**:
   - Test admin user management interface
   - Test system monitoring and statistics
   - Test user support tools

### **Milestone 8: Scheduling & Automation**

**Goal**: Automated briefing generation with user-controlled scheduling

**Technical Implementation**:
- Celery background task processing system
- Redis message broker for task distribution
- Celery Beat for cron-like scheduling
- User-configurable scheduling interface
- Email notification system for delivery

**Scheduler Architecture**:
1. **Celery Tasks**: Background briefing generation tasks
2. **Celery Beat**: Periodic task scheduling engine
3. **Schedule Management**: User interface for schedule configuration
4. **Notification System**: Email delivery with template system
5. **Task Monitoring**: Task status tracking and error handling

**Test Plan**:

**Unit Tests** (`tests/test_scheduling.py`):
1. **Task System Tests**:
   - Test briefing generation task execution
   - Test task failure handling and retry logic
   - Test task result storage and retrieval

2. **Schedule Management Tests**:
   - Test schedule creation and validation
   - Test timezone handling and conversion
   - Test schedule conflict detection
   - Test schedule modification and deletion

3. **Notification Tests**:
   - Test email notification sending (mocked)
   - Test notification template rendering
   - Test notification preference handling
   - Test notification delivery tracking

**Integration Tests** (`tests/test_automation.py`):
1. **End-to-End Automation Tests**:
   - Test complete scheduled generation workflow
   - Test multiple user schedules running concurrently
   - Test error handling in automated context
   - Test system recovery from failures

**Manual Tests**:
1. **Scheduling Interface**:
   - Create various schedule types (daily, weekdays, custom)
   - Test schedule editing and deletion
   - Verify scheduled execution accuracy
   - Test timezone handling

2. **Notification Testing**:
   - Test email delivery and formatting
   - Test notification preferences
   - Test notification history and tracking

### **Milestone 9: Extended Data Sources**

**Goal**: Expand content variety through additional data source integrations

**Technical Implementation**:
- Extensible data source framework with plugin architecture
- Integration with RSS feeds, Reddit API, financial data APIs
- Content intelligence for duplicate detection and relevance scoring
- User preference learning system
- Calendar integration for schedule-aware content

**Data Source Framework**:
1. **Base Data Source Interface**: Abstract base class for all data sources
2. **RSS Integration**: Configurable RSS feed parsing and aggregation
3. **Reddit Integration**: Subreddit monitoring and content extraction
4. **Financial Data**: Stock prices, crypto data, market news integration
5. **Calendar Integration**: Personal schedule awareness for content timing

**Test Plan**:

**Unit Tests** (`tests/test_data_sources.py`):
1. **Data Source Framework Tests**:
   - Test base data source interface compliance
   - Test data source registration and discovery
   - Test configuration validation framework

2. **Individual Source Tests**:
   - Test RSS feed parsing with various formats
   - Test Reddit API integration (mocked)
   - Test financial data fetching (mocked)
   - Test calendar integration (mocked)

3. **Content Intelligence Tests**:
   - Test duplicate detection algorithms
   - Test content relevance scoring
   - Test content filtering and ranking
   - Test user preference learning

**Manual Tests**:
1. **Data Source Configuration**:
   - Configure various RSS feeds and verify content quality
   - Test Reddit subreddit integration and filtering
   - Test financial data sources and relevance
   - Test calendar integration and schedule awareness

2. **Content Quality Validation**:
   - Verify content relevance and diversity
   - Test duplicate handling across sources
   - Test content variety in final briefings
   - Validate user preference application

### **Milestone 10: Advanced Features & Security**

**Goal**: Power-user features, security hardening, and system maturity

**Technical Implementation**:
- Multi-Factor Authentication (MFA) with TOTP
- Advanced script editor with real-time preview
- A/B testing framework for briefing optimization
- RESTful API for programmatic access
- Comprehensive analytics and monitoring system

**Security Enhancements**:
1. **Multi-Factor Authentication**: TOTP-based MFA with QR code setup
2. **Rate Limiting**: API and web interface rate limiting with Redis
3. **API Key Encryption**: Encryption at rest for sensitive user data
4. **Audit Logging**: Comprehensive logging for security events
5. **Content Security Policy**: XSS protection and secure headers

**Advanced Features**:
1. **Script Editor**: Monaco Editor integration with syntax highlighting
2. **Analytics System**: User behavior tracking and performance monitoring
3. **A/B Testing**: Framework for testing different briefing formats
4. **RESTful API**: Full API access for power users and integrations
5. **Export/Import**: Configuration backup and sharing capabilities

**Test Plan**:

**Security Tests** (`tests/test_security.py`):
1. **Authentication Security Tests**:
   - Test MFA setup and validation flow
   - Test brute force protection mechanisms
   - Test session security and timeout handling
   - Test password policy enforcement

2. **API Security Tests**:
   - Test API key validation and rotation
   - Test rate limiting effectiveness
   - Test input sanitization and validation
   - Test authorization for all endpoints

3. **Data Security Tests**:
   - Test encryption of sensitive data at rest
   - Test secure data transmission (HTTPS)
   - Test audit logging functionality
   - Test data retention and cleanup policies

**Performance Tests** (`tests/test_performance.py`):
1. **Load Testing**:
   - Test concurrent user handling capacity
   - Test database performance under load
   - Test API response times under stress
   - Test caching effectiveness

2. **Stress Testing**:
   - Test system behavior at capacity limits
   - Test graceful degradation mechanisms
   - Test recovery from various failure scenarios
   - Test resource cleanup and memory management

**Manual Tests**:
1. **Security Validation**:
   - Test complete MFA setup process
   - Verify security headers and CSP policies
   - Test audit log generation and accuracy
   - Validate data encryption implementation

2. **Advanced Features**:
   - Test script editor functionality and performance
   - Validate analytics dashboard accuracy
   - Test A/B testing framework
   - Verify API access and documentation

---

### 6. Quality Assurance & Deployment

**Testing Strategy**:
- **Unit Tests**: Comprehensive coverage for all modules (target: >90%)
- **Integration Tests**: API integration and workflow testing
- **Security Tests**: Penetration testing and vulnerability scanning
- **Performance Tests**: Load testing and optimization validation
- **User Acceptance Tests**: End-to-end user journey validation

**Deployment Pipeline**:
1. **Development**: Local Flask application with SQLite
2. **Staging**: Containerized deployment with PostgreSQL
3. **Production**: Full AWS deployment with monitoring and logging
4. **Monitoring**: CloudWatch, application logs, and user analytics

This comprehensive specification provides a clear roadmap for transforming the AI Daily Briefing Agent from a CLI tool into a robust, scalable web application with enterprise-grade features and security.