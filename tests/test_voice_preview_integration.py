"""
Integration test for voice preview endpoint.

Tests the actual Flask route with mocked TTS generation.
"""

import pytest
import json
from unittest.mock import patch


@patch('tts_generator.generate_audio')
def test_voice_preview_endpoint_integration(mock_generate_audio, client):
    """Test voice preview endpoint with Flask test client using Google TTS."""
    # Mock the audio generation
    mock_generate_audio.return_value = b'fake_audio_data'
    
    # Set up session with API keys (simulating user has completed step 1)
    with client.session_transaction() as sess:
        sess['api_keys'] = {
            'google_api_key': 'test_api_key_12345'
        }
    
    # Test voice preview request with Neural2 voice
    response = client.post('/preview-voice',
                          json={'voice_id': 'en-US-Neural2-C'},  # Neural2 Female
                          content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Verify successful response
    assert data['success'] is True
    assert 'audio_data' in data
    assert data['voice_id'] == 'en-US-Neural2-C'
    
    # Verify generate_audio was called with correct config
    mock_generate_audio.assert_called_once()
    args, kwargs = mock_generate_audio.call_args
    preview_text, config_obj = args
    
    assert "Neural2 voice" in preview_text
    assert config_obj.get('TTS_PROVIDER') == 'google'
    assert config_obj.get('GOOGLE_TTS_VOICE_NAME') == 'en-US-Neural2-C'


def test_voice_preview_endpoint_no_session(client):
    """Test voice preview fails without API keys in session."""
    response = client.post('/preview-voice',
                          json={'voice_id': 'EXAVITQu4vr4xnSDxMaL'},
                          content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['success'] is False
    assert 'API key not configured' in data['error']


def test_voice_preview_endpoint_missing_voice_id(client):
    """Test voice preview fails without voice_id."""
    with client.session_transaction() as sess:
        sess['api_keys'] = {'google_api_key': 'test_key'}
    
    response = client.post('/preview-voice',
                          json={},  # No voice_id
                          content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['success'] is False
    assert 'No voice name provided' in data['error']


@patch('tts_generator.generate_audio')
def test_voice_preview_with_default_voice(mock_generate_audio, client):
    """Test voice preview with Neural2 default voice selection."""
    mock_generate_audio.return_value = b'fake_audio_data'
    
    with client.session_transaction() as sess:
        sess['api_keys'] = {'google_api_key': 'test_api_key'}
    
    # Test with Neural2 default voice
    response = client.post('/preview-voice',
                          json={'voice_id': 'en-US-Neural2-C'},  # Default Neural2 voice
                          content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['success'] is True
    assert 'audio_data' in data
    assert data['voice_id'] == 'en-US-Neural2-C'
    
    # Verify the config was created correctly
    mock_generate_audio.assert_called_once()
    args, kwargs = mock_generate_audio.call_args
    preview_text, config_obj = args
    
    assert config_obj.get('TTS_PROVIDER') == 'google'
    assert config_obj.get('GOOGLE_TTS_VOICE_NAME') == 'en-US-Neural2-C'


@pytest.fixture
def client():
    """Create test client for voice preview tests."""
    from app import app
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        yield client 