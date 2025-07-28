# Technical Specification: AI Daily Briefing Agent

**Version:** 1.0
**Date:** July 28, 2025
**Status:** Final

---

### 1. Project Overview

This document provides a complete technical blueprint for building a serverless application that generates a personalized, AI-powered daily audio news briefing. The system is designed to run automatically, fetching content from specified online sources, summarizing it using a Large Language Model (LLM), converting the resulting script to speech, and delivering it as a single audio file to a cloud-based folder for easy streaming.

The development plan is broken into iterative, testable milestones to facilitate a rapid, prototype-driven approach.

---

### 2. Architecture & Technology Stack

#### **Core Architecture**
* **Language:** Python 3.11
* **Orchestration:** AWS Lambda
* **Scheduling:** Amazon EventBridge (CloudWatch Events)
* **Secret Management:** Local Environment Variables (Development) & AWS Secrets Manager (Production)
* **Testing Framework:** `pytest`

#### **Python Libraries**
* `requests`: For REST API calls and GraphQL queries.
* `boto3`: AWS SDK for Python (for AWS Secrets Manager).
* `google-api-python-client` & `google-auth-httplib2`: For Google Drive integration.
* `google-generativeai`: Client for the Gemini API.
* `elevenlabs`: Client for the ElevenLabs API.

#### **External Services & APIs**
* **News Source:** NewsAPI
* **Weather Source:** OpenWeatherMap API
* **Podcast Source:** Taddy API (GraphQL)
* **AI Summarization:** Google Gemini API
* **Text-to-Speech (TTS):** ElevenLabs API
* **File Delivery:** Google Drive API v3

---

### 3. Project Structure

The application will be organized into a modular structure to ensure a clear separation of concerns and to facilitate unit testing.

```text
/ai-daily-briefing/
|
├── main.py                 # Main Lambda handler; orchestrates the workflow
├── config.py               # Handles loading of configuration and secrets
├── data_fetchers.py        # Contains all functions for calling external data APIs
├── summarizer.py           # Interfaces with the Gemini API for summarization
├── tts_generator.py        # Interfaces with the ElevenLabs API for audio generation
├── uploader.py             # Handles the file upload process to Google Drive
|
├── tests/                    # Contains all unit and integration tests
|
├── .gitignore
├── requirements.txt        # Project dependencies
└── iam_policy.json         # Required IAM policy for the Lambda execution role
```

### 4. Data Structures

To ensure data consistency between modules, the application will use simple, well-defined data structures, implemented as Python `dataclasses` or dictionaries.

* **`Article`**: Contains fields such as `title`, `source`, `url`, `content`, and `summary`.
* **`PodcastEpisode`**: Contains fields such as `podcast_title`, `episode_title`, and `url`.
* **`Briefing`**: A list of strings, where each string is a segment of the final script to be spoken.

---

### 5. Iterative Development Plan

The project will be built using a "text-first" approach, focusing on perfecting the content before introducing audio and delivery complexities.

### **Milestone 0: Secure Setup & Configuration**

* **Goal:** Establish a secure development environment where secrets are never hardcoded.
* **Tasks:**
    1.  Initialize the project structure and Git repository.
    2.  Set all required API keys as **environment variables** in the local shell.
    3.  Implement the `config.py` module to load variables from `os.environ`.
* **Test Plan:**
    * **Unit Tests:** Verify the `config` module correctly reads mocked environment variables and handles missing variables gracefully.
    * **Manual Test:** `export TEST_KEY="test-value"` and confirm a test script can print the value via the `config` module.

### **Milestone 1: Live Data Aggregation**

* **Goal:** Create a script that fetches all raw data and assembles a basic, non-summarized text briefing.
* **Tasks:**
    1.  Implement and test `data_fetchers.get_weather()`.
    2.  Implement and test `data_fetchers.get_news_articles()` for all topics.
    3.  Implement and test `data_fetchers.get_new_podcast_episodes()`.
    4.  Modify `main.py` to call these functions and save the assembled raw text to a local file (e.g., `briefing.txt`).
* **Test Plan:**
    * **Unit Tests:** Mock the `requests.get` method for REST APIs and `requests.post` for GraphQL APIs. Assert that sample responses are parsed into the correct data structures.
    * **Manual Test:** Run `python main.py` and verify that `briefing.txt` contains the current weather, news headlines, and podcast updates.

### **Milestone 2: AI Summarization**

* **Goal:** Enhance the text briefing by integrating the core AI summarization feature.
* **Tasks:**
    1.  Implement and test `summarizer.summarize_articles()`.
    2.  Integrate the summarizer into the `main.py` workflow, replacing raw article content with AI-generated summaries.
* **Test Plan:**
    * **Unit Tests:** Mock the Gemini API client. Pass a sample article to `summarize_articles()` and assert that the prompt sent to the client is correctly formatted.
    * **Manual Test:** Run `python main.py` and verify the news section in `briefing.txt` now contains coherent, concise summaries.

### **Milestone 3: Audio Generation & Delivery**

* **Goal:** Convert the final text script into an audio file and deliver it to Google Drive.
* **Tasks:**
    1.  Implement `tts_generator.generate_audio()`.
    2.  Implement `uploader.upload_to_drive()`.
    3.  Modify `main.py` to orchestrate the text-to-audio-to-upload pipeline, removing the local file save.
* **Test Plan:**
    * **Unit Tests:** Mock the API clients for ElevenLabs and Google Drive. Assert that the clients are called with the correct data (script text, API keys, audio data, folder ID).
    * **Manual Test:** Run `python main.py` and verify a new MP3 file appears in the target Google Drive folder and that its audio content is correct.

### **Milestone 4: Cloud Migration & Deployment**

* **Goal:** Harden the application and deploy for automated, serverless execution.
* **Tasks:**
    1.  Move local environment variables into AWS Secrets Manager.
    2.  Enhance `config.py` to fetch secrets from Secrets Manager when it detects an AWS environment.
    3.  Deploy the application to AWS Lambda with a daily EventBridge trigger.
* **Test Plan:**
    * **Unit Tests:** Mock `os.environ` to simulate a Lambda environment and mock `boto3`. Assert the config module attempts to call the Secrets Manager client.
    * **Manual Test:** Manually trigger the deployed Lambda. Verify file creation in Google Drive and check CloudWatch logs. Finally, confirm the scheduled trigger works correctly the next day.