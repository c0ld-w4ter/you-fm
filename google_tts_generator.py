"""
Google Cloud Text-to-Speech generator module for AI Daily Briefing Agent.

This module interfaces with the Google Cloud Text-to-Speech API to convert
the briefing script text into high-quality audio.
"""

import logging
import os
import json
import base64
import requests
from typing import Optional, Dict, Any

# Import Google Cloud TTS modules at module level for testing
try:
    from google.cloud import texttospeech
    from google.oauth2 import service_account
except ImportError:
    # Handle case where Google Cloud libraries are not installed
    texttospeech = None
    service_account = None

logger = logging.getLogger(__name__)


class GoogleTTSClient:
    """Wrapper for Google Cloud Text-to-Speech with API key and credentials support."""
    
    def __init__(self, api_key: Optional[str] = None, credentials_path: Optional[str] = None):
        """
        Initialize Google TTS client.
        
        Args:
            api_key: Google API key for REST API authentication
            credentials_path: Path to service account JSON file. If None, uses default credentials.
        """
        self.api_key = api_key
        self.credentials_path = credentials_path
        self.client = None
        
        # Try to initialize client library if no API key provided
        if not api_key:
            try:
                if texttospeech is None or service_account is None:
                    raise ImportError("Google Cloud TTS libraries not available")
                
                if credentials_path and os.path.exists(credentials_path):
                    credentials = service_account.Credentials.from_service_account_file(credentials_path)
                    self.client = texttospeech.TextToSpeechClient(credentials=credentials)
                else:
                    # Use default credentials (from environment or metadata service)
                    self.client = texttospeech.TextToSpeechClient()
                    
                logger.info("Using Google Cloud client library authentication")
            except Exception as e:
                logger.warning(f"Could not initialize Google Cloud client: {e}")
        else:
            logger.info("Using Google API key authentication")
            
    def synthesize_speech(
        self,
        text: str,
        voice_name: str = "en-US-Neural2-C",
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
        if self.api_key:
            return self._synthesize_with_api_key(
                text, voice_name, language_code, speaking_rate, pitch, volume_gain_db
            )
        elif self.client:
            return self._synthesize_with_client(
                text, voice_name, language_code, speaking_rate, pitch, volume_gain_db
            )
        else:
            raise Exception("No valid authentication method available. Please provide either an API key or valid credentials.")
    
    def _synthesize_with_api_key(
        self,
        text: str,
        voice_name: str,
        language_code: str,
        speaking_rate: float,
        pitch: float,
        volume_gain_db: float
    ) -> bytes:
        """Synthesize speech using REST API with API key."""
        # Google TTS has performance limits around 2000-3000 characters
        # Split text into chunks if needed
        chunks = self._split_text_into_chunks(text, max_chars=2000)  # Safe limit based on testing
        
        if len(chunks) == 1:
            # Single chunk - direct synthesis
            return self._synthesize_chunk_with_api_key(
                chunks[0], voice_name, language_code, speaking_rate, pitch, volume_gain_db
            )
        else:
            # Multiple chunks - synthesize each and combine
            logger.info(f"Text too long ({len(text)} chars), splitting into {len(chunks)} chunks")
            audio_segments = []
            
            for i, chunk in enumerate(chunks):
                logger.info(f"Synthesizing chunk {i+1}/{len(chunks)} ({len(chunk)} chars)")
                chunk_audio = self._synthesize_chunk_with_api_key(
                    chunk, voice_name, language_code, speaking_rate, pitch, volume_gain_db
                )
                audio_segments.append(chunk_audio)
                
                # Add delay between chunks to avoid rate limiting (except for last chunk)
                if i < len(chunks) - 1:
                    import time
                    logger.info("Waiting 1 second before next chunk...")
                    time.sleep(1)
            
            # Combine all audio segments
            return self._combine_audio_segments(audio_segments)
    
    def _synthesize_chunk_with_api_key(
        self,
        text: str,
        voice_name: str,
        language_code: str,
        speaking_rate: float,
        pitch: float,
        volume_gain_db: float
    ) -> bytes:
        """Synthesize a single chunk using REST API with API key."""
        url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={self.api_key}"
        
        payload = {
            "input": {"text": text},
            "voice": {
                "languageCode": language_code,
                "name": voice_name
            },
            "audioConfig": {
                "audioEncoding": "MP3",
                "speakingRate": speaking_rate,
                "pitch": pitch,
                "volumeGainDb": volume_gain_db
            }
        }
        
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        audio_content = base64.b64decode(result["audioContent"])
        
        return audio_content
    
    def _split_text_into_chunks(self, text: str, max_chars: int = 2000) -> list[str]:
        """Split text into chunks that fit within Google TTS limits."""
        # First try to split by sentences to maintain natural breaks
        sentences = self._split_into_sentences(text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # Check if adding this sentence would exceed the limit
            test_chunk = current_chunk + (" " if current_chunk else "") + sentence
            if len(test_chunk) <= max_chars:
                current_chunk = test_chunk
            else:
                # If current chunk is not empty, save it and start new chunk
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = sentence
                else:
                    # Single sentence is too long, split it by words
                    word_chunks = self._split_long_sentence(sentence, max_chars)
                    chunks.extend(word_chunks)
                    current_chunk = ""
        
        # Add remaining chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        import re
        # Split on sentence endings, but keep the punctuation
        sentences = re.split(r'([.!?]+)', text)
        result = []
        
        for i in range(0, len(sentences) - 1, 2):
            sentence = sentences[i]
            punctuation = sentences[i + 1] if i + 1 < len(sentences) else ""
            if sentence.strip():
                result.append((sentence + punctuation).strip())
        
        # Handle any remaining text without punctuation
        if len(sentences) % 2 == 1 and sentences[-1].strip():
            result.append(sentences[-1].strip())
        
        return result
    
    def _split_long_sentence(self, sentence: str, max_chars: int) -> list[str]:
        """Split a sentence that's too long by words."""
        words = sentence.split()
        chunks = []
        current_chunk = ""
        
        for word in words:
            test_chunk = current_chunk + (" " if current_chunk else "") + word
            if len(test_chunk) <= max_chars:
                current_chunk = test_chunk
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = word
                else:
                    # Single word is too long, just add it (truncate if necessary)
                    chunks.append(word[:max_chars].strip())
                    current_chunk = ""
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
        
    def _combine_audio_segments(self, audio_segments: list[bytes]) -> bytes:
        """Combine multiple MP3 audio segments into one."""
        # For MP3 files, we can simply concatenate the bytes
        # This works because MP3 is a streaming format
        return b''.join(audio_segments)
    
    def _synthesize_with_client(
        self,
        text: str,
        voice_name: str,
        language_code: str,
        speaking_rate: float,
        pitch: float,
        volume_gain_db: float
    ) -> bytes:
        """Synthesize speech using Google Cloud client library."""
        
        # Google TTS has performance limits around 2000-3000 characters
        # Split text into chunks if needed
        chunks = self._split_text_into_chunks(text, max_chars=2000)  # Safe limit based on testing
        
        if len(chunks) == 1:
            # Single chunk - direct synthesis
            return self._synthesize_chunk_with_client(
                chunks[0], voice_name, language_code, speaking_rate, pitch, volume_gain_db
            )
        else:
            # Multiple chunks - synthesize each and combine
            logger.info(f"Text too long ({len(text)} chars), splitting into {len(chunks)} chunks")
            audio_segments = []
            
            for i, chunk in enumerate(chunks):
                logger.info(f"Synthesizing chunk {i+1}/{len(chunks)} ({len(chunk)} chars)")
                chunk_audio = self._synthesize_chunk_with_client(
                    chunk, voice_name, language_code, speaking_rate, pitch, volume_gain_db
                )
                audio_segments.append(chunk_audio)
                
                # Add delay between chunks to avoid rate limiting (except for last chunk)
                if i < len(chunks) - 1:
                    import time
                    logger.info("Waiting 1 second before next chunk...")
                    time.sleep(1)
            
            # Combine all audio segments
            return self._combine_audio_segments(audio_segments)
    
    def _synthesize_chunk_with_client(
        self,
        text: str,
        voice_name: str,
        language_code: str,
        speaking_rate: float,
        pitch: float,
        volume_gain_db: float
    ) -> bytes:
        """Synthesize a single chunk using Google Cloud client library."""
        
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
        api_key = config.get('GOOGLE_API_KEY', '')
        credentials_path = config.get('GOOGLE_CLOUD_CREDENTIALS_PATH', '')
        voice_name = config.get('GOOGLE_TTS_VOICE_NAME', 'en-US-Neural2-C')
        language_code = config.get('GOOGLE_TTS_LANGUAGE_CODE', 'en-US')
        
        # Get voice speed from config (same as ElevenLabs for consistency)
        voice_speed = config.get_voice_speed()
        
        # Initialize Google TTS client (prefer API key over credentials)
        client = GoogleTTSClient(api_key=api_key if api_key else None, credentials_path=credentials_path if credentials_path else None)
        
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


def get_available_voices(language_code: str = "en-US", api_key: Optional[str] = None, credentials_path: Optional[str] = None) -> list:
    """
    Get list of available voices for a given language.
    
    Args:
        language_code: Language code to filter voices
        api_key: Optional Google API key
        credentials_path: Optional path to service account JSON
        
    Returns:
        List of voice names
    """
    try:
        if api_key:
            # Use REST API to list voices
            url = f"https://texttospeech.googleapis.com/v1/voices?key={api_key}"
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            voice_list = []
            
            for voice in data.get("voices", []):
                for lang_code in voice.get("languageCodes", []):
                    if lang_code.startswith("en"):
                        voice_list.append({
                            "name": voice.get("name", ""),
                            "language": lang_code,
                            "gender": voice.get("ssmlGender", "NEUTRAL")
                        })
            
            return voice_list
        else:
            # Use client library
            client = GoogleTTSClient(api_key=None, credentials_path=credentials_path)
            
            if not client.client:
                logger.error("No valid authentication method for listing voices")
                return []
            
            # List available voices
            voices = client.client.list_voices(language_code=language_code)
            
            voice_list = []
            for voice in voices.voices:
                for lang_code in voice.language_codes:
                    if lang_code.startswith("en"):
                        voice_list.append({
                            "name": voice.name,
                            "language": lang_code,
                            "gender": voice.ssml_gender.name
                        })
                        
            return voice_list
        
    except Exception as e:
        logger.error(f"Failed to list Google TTS voices: {e}")
        return []