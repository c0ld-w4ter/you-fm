"""
Google Cloud Text-to-Speech generator module for AI Daily Briefing Agent.

This module interfaces with the Google Cloud Text-to-Speech API to convert
the briefing script text into high-quality audio.
"""

import logging
import os
from typing import Optional, Dict, Any
from google.cloud import texttospeech
from google.oauth2 import service_account

logger = logging.getLogger(__name__)


class GoogleTTSClient:
    """Wrapper for Google Cloud Text-to-Speech client with configuration."""
    
    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize Google TTS client.
        
        Args:
            credentials_path: Path to service account JSON file. If None, uses default credentials.
        """
        if credentials_path and os.path.exists(credentials_path):
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            self.client = texttospeech.TextToSpeechClient(credentials=credentials)
        else:
            # Use default credentials (from environment or metadata service)
            self.client = texttospeech.TextToSpeechClient()
            
    def synthesize_speech(
        self,
        text: str,
        voice_name: str = "en-US-Journey-D",
        language_code: str = "en-US",
        speaking_rate: float = 1.0,
        pitch: float = 0.0,
        volume_gain_db: float = 0.0
    ) -> bytes:
        """
        Synthesize speech from text using Google TTS.
        
        Args:
            text: Text to convert to speech
            voice_name: Google TTS voice name
            language_code: Language code for the voice
            speaking_rate: Speaking rate (0.25 to 4.0, default 1.0)
            pitch: Voice pitch (-20.0 to 20.0, default 0.0)
            volume_gain_db: Volume gain in dB (-96.0 to 16.0, default 0.0)
            
        Returns:
            Audio content as bytes (MP3 format)
        """
        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        # Build the voice request
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=voice_name
        )
        
        # Select the type of audio file and configure audio parameters
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=speaking_rate,
            pitch=pitch,
            volume_gain_db=volume_gain_db
        )
        
        # Perform the text-to-speech request
        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        return response.audio_content


def generate_audio_google(script_text: str, config=None) -> bytes:
    """
    Convert text script to audio using Google Cloud Text-to-Speech API.
    
    Args:
        script_text: The complete briefing script text
        config: Optional Config object. If None, loads from environment.
        
    Returns:
        Audio data as bytes (MP3 format)
        
    Raises:
        Exception: If Google TTS API call fails
    """
    logger.info("Generating audio from script using Google TTS...")
    
    if not script_text or not script_text.strip():
        raise Exception("Cannot generate audio from empty script text")
    
    logger.info(f"Script length: {len(script_text)} characters")
    
    try:
        from config import get_config
        
        # Get configuration
        if config is None:
            config = get_config()
            
        # Get Google TTS configuration
        credentials_path = config.get('GOOGLE_CLOUD_CREDENTIALS_PATH', '')
        voice_name = config.get('GOOGLE_TTS_VOICE_NAME', 'en-US-Journey-D')
        language_code = config.get('GOOGLE_TTS_LANGUAGE_CODE', 'en-US')
        
        # Get voice speed from config (same as ElevenLabs for consistency)
        voice_speed = config.get_voice_speed()
        
        # Initialize Google TTS client
        client = GoogleTTSClient(credentials_path)
        
        logger.info(f"Using Google TTS voice: {voice_name}, language: {language_code}, speed: {voice_speed}")
        
        # Generate audio using Google TTS API
        audio_bytes = client.synthesize_speech(
            text=script_text,
            voice_name=voice_name,
            language_code=language_code,
            speaking_rate=voice_speed
        )
        
        logger.info(f"✓ Successfully generated {len(audio_bytes)} bytes of audio using Google TTS")
        return audio_bytes
        
    except ImportError as e:
        logger.error("Google Cloud Text-to-Speech library not available")
        raise Exception(f"Google Cloud Text-to-Speech library not installed: {e}")
        
    except Exception as e:
        logger.error(f"Failed to generate audio with Google TTS: {e}")
        
        # Enhanced error handling with specific messages
        error_message = str(e).lower()
        if "credentials" in error_message or "authentication" in error_message:
            raise Exception("Google Cloud authentication failed. Please check your credentials configuration.")
        elif "voice" in error_message:
            raise Exception(f"Voice '{voice_name}' not found. Please check your GOOGLE_TTS_VOICE_NAME setting.")
        elif "quota" in error_message or "limit" in error_message:
            raise Exception("Google Cloud quota exceeded. Please check your account limits.")
        elif "network" in error_message or "connection" in error_message:
            raise Exception("Network error connecting to Google TTS API. Please check your internet connection.")
        else:
            raise Exception(f"Google TTS API error: {e}")


def get_available_voices(language_code: str = "en-US", credentials_path: Optional[str] = None) -> list:
    """
    Get list of available voices for a given language.
    
    Args:
        language_code: Language code to filter voices
        credentials_path: Optional path to service account JSON
        
    Returns:
        List of voice names
    """
    try:
        client = GoogleTTSClient(credentials_path)
        
        # List available voices
        voices = client.client.list_voices(language_code=language_code)
        
        voice_list = []
        for voice in voices.voices:
            for language_code in voice.language_codes:
                if language_code.startswith("en"):
                    voice_list.append({
                        "name": voice.name,
                        "language": language_code,
                        "gender": voice.ssml_gender.name
                    })
                    
        return voice_list
        
    except Exception as e:
        logger.error(f"Failed to list Google TTS voices: {e}")
        return []