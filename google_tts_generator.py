"""
Google Text-to-Speech generator module for AI Daily Briefing Agent.

This module interfaces with the Google Cloud Text-to-Speech API to convert
the briefing script text into high-quality audio.
"""

import logging
import json
import base64
from typing import Dict, Any, Optional

from config import get_config, Config

logger = logging.getLogger(__name__)

# Mapping of ElevenLabs voice IDs to Google TTS voices
# This mapping tries to match voice characteristics as closely as possible
VOICE_MAPPING = {
    'default': {
        'name': 'en-US-Journey-F',  # Neural2 professional female voice
        'language_code': 'en-US',
        'description': 'Professional Female (Journey)'
    },
    'EXAVITQu4vr4xnSDxMaL': {  # Bella - Warm Female
        'name': 'en-US-Neural2-H',
        'language_code': 'en-US',
        'description': 'Warm Female (Neural2-H)'
    },
    'VR6AewLTigWG4xSOukaG': {  # Arnold - Deep Male
        'name': 'en-US-Neural2-D',
        'language_code': 'en-US',
        'description': 'Deep Male (Neural2-D)'
    },
    'pNInz6obpgDQGcFmaJgB': {  # Adam - Clear Male
        'name': 'en-US-Neural2-A',
        'language_code': 'en-US',
        'description': 'Clear Male (Neural2-A)'
    },
    'yoZ06aMxZJJ28mfd3POQ': {  # Sam - Young Male
        'name': 'en-US-Neural2-J',
        'language_code': 'en-US',
        'description': 'Young Male (Neural2-J)'
    },
    'kdmDKE6EkgrWrrykO9Qt': {  # Alexandra - Realistic Young Female
        'name': 'en-US-Neural2-C',
        'language_code': 'en-US',
        'description': 'Young Female (Neural2-C)'
    },
    'L0Dsvb3SLTyegXwtm47J': {  # Archer - Friendly British Male
        'name': 'en-GB-Neural2-B',
        'language_code': 'en-GB',
        'description': 'British Male (Neural2-B)'
    },
    'g6xIsTj2HwM6VR4iXFCw': {  # Jessica - Empathetic Female
        'name': 'en-US-Neural2-E',
        'language_code': 'en-US',
        'description': 'Empathetic Female (Neural2-E)'
    },
    'OYTbf65OHHFELVut7v2H': {  # Hope - Bright & Uplifting Female
        'name': 'en-US-Neural2-F',
        'language_code': 'en-US',
        'description': 'Bright Female (Neural2-F)'
    },
    'dj3G1R1ilKoFKhBnWOzG': {  # Eryn - Friendly & Relatable Female
        'name': 'en-US-Neural2-G',
        'language_code': 'en-US',
        'description': 'Friendly Female (Neural2-G)'
    },
    'HDA9tsk27wYi3uq0fPcK': {  # Stuart - Professional Australian Male
        'name': 'en-AU-Neural2-B',
        'language_code': 'en-AU',
        'description': 'Australian Male (Neural2-B)'
    },
    '1SM7GgM6IMuvQlz2BwM3': {  # Mark - Relaxed & Laid Back Male
        'name': 'en-US-Neural2-I',
        'language_code': 'en-US',
        'description': 'Relaxed Male (Neural2-I)'
    },
    'PT4nqlKZfc06VW1BuClj': {  # Angela - Down to Earth Female
        'name': 'en-US-Studio-O',
        'language_code': 'en-US',
        'description': 'Down to Earth Female (Studio-O)'
    },
    'vBKc2FfBKJfcZNyEt1n6': {  # Finn - Podcast Friendly Male
        'name': 'en-US-Studio-Q',
        'language_code': 'en-US',
        'description': 'Podcast Male (Studio-Q)'
    },
    '56AoDkrOh6qfVPDXZ7Pt': {  # Cassidy - Energetic Female
        'name': 'en-US-Casual-K',
        'language_code': 'en-US',
        'description': 'Energetic Female (Casual-K)'
    }
}


def generate_audio_google(script_text: str, config: Optional[Config] = None) -> bytes:
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
        from google.cloud import texttospeech
        from google.oauth2 import service_account
        
        # Get configuration
        if config is None:
            config = get_config()
        
        # Get Google Cloud credentials
        google_credentials_json = config.get('GOOGLE_CLOUD_CREDENTIALS_JSON', '')
        if not google_credentials_json:
            raise Exception("GOOGLE_CLOUD_CREDENTIALS_JSON not configured")
        
        # Parse credentials
        try:
            credentials_dict = json.loads(google_credentials_json)
            credentials = service_account.Credentials.from_service_account_info(
                credentials_dict
            )
        except json.JSONDecodeError:
            raise Exception("Invalid GOOGLE_CLOUD_CREDENTIALS_JSON format")
        
        # Initialize Google TTS client
        client = texttospeech.TextToSpeechClient(credentials=credentials)
        
        # Get voice configuration
        elevenlabs_voice_id = config.get('ELEVENLABS_VOICE_ID', 'default')
        voice_config = VOICE_MAPPING.get(elevenlabs_voice_id, VOICE_MAPPING['default'])
        
        logger.info(f"Using Google TTS voice: {voice_config['description']} ({voice_config['name']})")
        
        # Get voice speed setting
        voice_speed = config.get_voice_speed()
        
        # Set up the voice parameters
        voice = texttospeech.VoiceSelectionParams(
            language_code=voice_config['language_code'],
            name=voice_config['name']
        )
        
        # Set up audio configuration
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=voice_speed,  # Google TTS directly supports speaking rate
            pitch=0.0,  # Neutral pitch
            volume_gain_db=0.0  # Normal volume
        )
        
        # Prepare the synthesis input
        synthesis_input = texttospeech.SynthesisInput(text=script_text)
        
        # Perform the text-to-speech request
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        # The response's audio_content is binary
        audio_bytes = response.audio_content
        
        logger.info(f"✓ Successfully generated {len(audio_bytes)} bytes of audio with Google TTS")
        return audio_bytes
        
    except ImportError as e:
        logger.error("Google Cloud Text-to-Speech library not available")
        raise Exception(f"Google Cloud Text-to-Speech library not installed: {e}")
        
    except Exception as e:
        logger.error(f"Failed to generate audio with Google TTS: {e}")
        
        # Enhanced error handling with specific messages
        error_message = str(e).lower()
        if "credentials" in error_message or "authentication" in error_message:
            raise Exception("Google Cloud authentication failed. Please check your GOOGLE_CLOUD_CREDENTIALS_JSON.")
        elif "quota" in error_message or "limit" in error_message:
            raise Exception("Google Cloud quota exceeded. Please check your account limits.")
        elif "network" in error_message or "connection" in error_message:
            raise Exception("Network error connecting to Google Cloud Text-to-Speech API. Please check your internet connection.")
        elif "invalid" in error_message and "voice" in error_message:
            raise Exception(f"Voice '{voice_config['name']}' not available. Please check Google TTS voice availability.")
        else:
            raise Exception(f"Google Cloud Text-to-Speech API error: {e}")


def get_available_voices() -> Dict[str, Dict[str, Any]]:
    """
    Get available Google TTS voices mapped from ElevenLabs voice IDs.
    
    Returns:
        Dictionary mapping ElevenLabs voice IDs to Google TTS voice configurations
    """
    return VOICE_MAPPING.copy()