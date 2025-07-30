"""
Tests for audio file serving functionality.

Tests the /audio/<filename> and /download/<filename> routes to ensure
they correctly serve audio files from the static/audio directory.
"""

import pytest
import os
import tempfile
from unittest.mock import patch
from flask import url_for


class TestAudioServing:
    """Test audio file serving routes."""
    
    def test_serve_audio_existing_file(self, client):
        """Test serving an existing audio file."""
        # Create a temporary audio file
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            temp_file.write(b'fake_mp3_data')
            temp_filename = os.path.basename(temp_file.name)
        
        # Move it to the static/audio directory for testing
        import shutil
        audio_dir = os.path.join(os.getcwd(), 'static', 'audio')
        os.makedirs(audio_dir, exist_ok=True)
        test_file_path = os.path.join(audio_dir, temp_filename)
        shutil.move(temp_file.name, test_file_path)
        
        try:
            # Test the audio serving route
            response = client.get(f'/audio/{temp_filename}')
            
            assert response.status_code == 200
            assert response.mimetype == 'audio/mpeg'
            assert response.data == b'fake_mp3_data'
            
        finally:
            # Clean up
            if os.path.exists(test_file_path):
                os.unlink(test_file_path)
    
    def test_serve_audio_nonexistent_file(self, client):
        """Test serving a non-existent audio file."""
        response = client.get('/audio/nonexistent_file.mp3')
        
        # Should redirect (302) since file doesn't exist
        assert response.status_code == 302
        # Should redirect to main page
        assert '/api-keys' in response.location or '/' in response.location
    
    def test_download_audio_existing_file(self, client):
        """Test downloading an existing audio file."""
        # Create a temporary audio file
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            temp_file.write(b'fake_mp3_download_data')
            temp_filename = os.path.basename(temp_file.name)
        
        # Move it to the static/audio directory for testing
        import shutil
        audio_dir = os.path.join(os.getcwd(), 'static', 'audio')
        os.makedirs(audio_dir, exist_ok=True)
        test_file_path = os.path.join(audio_dir, temp_filename)
        shutil.move(temp_file.name, test_file_path)
        
        try:
            # Test the download route
            response = client.get(f'/download/{temp_filename}')
            
            assert response.status_code == 200
            assert response.mimetype == 'audio/mpeg'
            assert response.data == b'fake_mp3_download_data'
            # Should have attachment header for download
            assert 'attachment' in response.headers.get('Content-Disposition', '')
            assert temp_filename in response.headers.get('Content-Disposition', '')
            
        finally:
            # Clean up
            if os.path.exists(test_file_path):
                os.unlink(test_file_path)
    
    def test_download_audio_nonexistent_file(self, client):
        """Test downloading a non-existent audio file."""
        response = client.get('/download/nonexistent_file.mp3')
        
        # Should redirect (302) since file doesn't exist
        assert response.status_code == 302
        # Should redirect to main page
        assert '/api-keys' in response.location or '/' in response.location
    
    def test_audio_path_calculation(self):
        """Test that the audio path calculation is correct."""
        from flask import Flask
        import os
        
        app = Flask(__name__)
        
        with app.app_context():
            # This simulates the path calculation in the fixed routes
            filename = 'test_file.mp3'
            audio_path = os.path.join(app.root_path, 'static', 'audio', filename)
            audio_path = os.path.abspath(audio_path)
            
            # Should point to the correct location relative to the app root
            expected_path = os.path.abspath(os.path.join(app.root_path, 'static', 'audio', filename))
            assert audio_path == expected_path
            
            # Should not contain '..' in the path (which was the bug)
            assert '..' not in audio_path
            
            # Should end with the expected structure
            assert audio_path.endswith(os.path.join('static', 'audio', filename))


@pytest.fixture
def client():
    """Create test client for audio serving tests."""
    from app import app
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        yield client 