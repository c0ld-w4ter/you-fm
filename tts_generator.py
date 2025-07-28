"""
Text-to-Speech generator module for AI Daily Briefing Agent.

This module interfaces with the ElevenLabs API to convert
the briefing script text into high-quality audio.
"""

import logging

from config import get_config

logger = logging.getLogger(__name__)


def generate_audio(script_text: str) -> bytes:
    """
    Convert text script to audio using ElevenLabs API.
    
    Args:
        script_text: The complete briefing script text
        
    Returns:
        Audio data as bytes (MP3 format)
        
    Raises:
        Exception: If ElevenLabs API call fails
    """
    logger.info("Generating audio from script...")
    
    if not script_text or not script_text.strip():
        raise Exception("Cannot generate audio from empty script text")
    
    logger.info(f"Script length: {len(script_text)} characters")
    
    try:
        from elevenlabs.client import ElevenLabs
        
        # Get configuration
        config = get_config()
        api_key = config.get('ELEVENLABS_API_KEY')
        voice_id = config.get('ELEVENLABS_VOICE_ID', 'default')
        
        # Initialize ElevenLabs client
        client = ElevenLabs(api_key=api_key)
        
        logger.info(f"Using ElevenLabs voice: {voice_id}")
        
        # Generate audio using ElevenLabs API
        # Use recommended settings for news/briefing content
        audio = client.text_to_speech.convert(
            text=script_text,
            voice_id=voice_id if voice_id != 'default' else "JBFqnCBsd6RMkjVDRZzb",  # Rachel voice as default
            model_id="eleven_multilingual_v2",  # High quality multilingual model
            output_format="mp3_44100_128",  # Standard MP3 quality
        )
        
        # Convert generator to bytes if needed
        if hasattr(audio, '__iter__') and not isinstance(audio, (bytes, str)):
            # Handle streaming response
            audio_bytes = b''.join(audio)
        else:
            audio_bytes = audio
            
        logger.info(f"✓ Successfully generated {len(audio_bytes)} bytes of audio")
        return audio_bytes
        
    except ImportError as e:
        logger.error("ElevenLabs library not available")
        raise Exception(f"ElevenLabs library not installed: {e}")
        
    except Exception as e:
        logger.error(f"Failed to generate audio with ElevenLabs: {e}")
        
        # Enhanced error handling with specific messages
        error_message = str(e).lower()
        if "api key" in error_message or "unauthorized" in error_message:
            raise Exception("ElevenLabs API authentication failed. Please check your ELEVENLABS_API_KEY.")
        elif "voice" in error_message:
            raise Exception(f"Voice ID '{voice_id}' not found. Please check your ELEVENLABS_VOICE_ID setting.")
        elif "quota" in error_message or "limit" in error_message:
            raise Exception("ElevenLabs API quota exceeded. Please check your account limits.")
        elif "network" in error_message or "connection" in error_message:
            raise Exception("Network error connecting to ElevenLabs API. Please check your internet connection.")
        else:
            raise Exception(f"ElevenLabs API error: {e}")


def save_audio_locally(audio_data: bytes, filename: str = "briefing.mp3") -> str:
    """
    Save audio data to local file for testing.
    
    Args:
        audio_data: Audio bytes to save
        filename: Output filename
        
    Returns:
        Path to saved file
    """
    logger.info(f"Saving audio to local file: {filename}")
    
    with open(filename, "wb") as f:
        f.write(audio_data)
    
    logger.info(f"✓ Audio saved to {filename}")
    return filename 