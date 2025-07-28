"""
Uploader module for AI Daily Briefing Agent.

This module handles uploading the generated audio file
to Google Drive for easy streaming and access.
"""

import logging
from datetime import datetime

from config import get_config

logger = logging.getLogger(__name__)


def upload_to_drive(audio_data: bytes, filename: str = None) -> str:
    """
    Upload audio file to Google Drive.
    
    Args:
        audio_data: Audio bytes to upload
        filename: Optional filename (auto-generated if not provided)
        
    Returns:
        Google Drive file ID of uploaded file
        
    Raises:
        Exception: If Google Drive API call fails
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"daily_briefing_{timestamp}.mp3"
        
    logger.info(f"Uploading audio to Google Drive: {filename}")
    
    if not audio_data:
        raise Exception("Cannot upload empty audio data to Google Drive")
    
    logger.info(f"Audio size: {len(audio_data)} bytes")
    
    try:
        import io
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaIoBaseUpload
        from google.oauth2 import service_account
        
        # Get configuration
        config = get_config()
        folder_id = config.get('GOOGLE_DRIVE_FOLDER_ID')
        
        # Set up credentials using service account
        service = setup_drive_credentials()
        
        # Verify folder access
        if not verify_folder_access(folder_id):
            raise Exception(f"Cannot access Google Drive folder: {folder_id}")
        
        # Create file metadata
        file_metadata = {
            'name': filename,
            'parents': [folder_id] if folder_id else []
        }
        
        # Create media upload from audio bytes
        audio_io = io.BytesIO(audio_data)
        media = MediaIoBaseUpload(
            audio_io,
            mimetype='audio/mpeg',
            resumable=True
        )
        
        logger.info("Uploading file to Google Drive...")
        
        # Upload the file
        request = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id,name,size,webViewLink'
        )
        
        response = request.execute()
        
        file_id = response.get('id')
        file_size = response.get('size', 'unknown')
        web_link = response.get('webViewLink', 'unavailable')
        
        logger.info(f"✓ Successfully uploaded to Google Drive")
        logger.info(f"  File ID: {file_id}")
        logger.info(f"  File size: {file_size} bytes")
        logger.info(f"  Web link: {web_link}")
        
        return file_id
        
    except ImportError as e:
        logger.error("Google API libraries not available")
        raise Exception(f"Google API libraries not installed: {e}")
        
    except Exception as e:
        logger.error(f"Failed to upload to Google Drive: {e}")
        
        # Enhanced error handling
        error_message = str(e).lower()
        if "credentials" in error_message or "authentication" in error_message:
            raise Exception("Google Drive authentication failed. Please check your service account credentials.")
        elif "folder" in error_message or "parent" in error_message:
            raise Exception(f"Cannot access Google Drive folder '{folder_id}'. Please check folder ID and permissions.")
        elif "quota" in error_message or "storage" in error_message:
            raise Exception("Google Drive storage quota exceeded. Please free up space or upgrade your account.")
        elif "permission" in error_message:
            raise Exception("Insufficient permissions for Google Drive upload. Please check service account access.")
        else:
            raise Exception(f"Google Drive API error: {e}")


def setup_drive_credentials():
    """
    Set up Google Drive API credentials using service account.
    
    Returns:
        Authenticated Google Drive service object
        
    Raises:
        Exception: If credential setup fails
    """
    logger.info("Setting up Google Drive credentials...")
    
    try:
        from googleapiclient.discovery import build
        from google.oauth2 import service_account
        import json
        import os
        
        config = get_config()
        
        # Try to get service account credentials from environment
        # This supports both file path and direct JSON content
        service_account_info = None
        
        # Method 1: Check for GOOGLE_SERVICE_ACCOUNT_JSON environment variable (JSON content)
        service_account_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
        if service_account_json:
            try:
                service_account_info = json.loads(service_account_json)
                logger.info("Using service account from GOOGLE_SERVICE_ACCOUNT_JSON environment variable")
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in GOOGLE_SERVICE_ACCOUNT_JSON: {e}")
        
        # Method 2: Check for GOOGLE_SERVICE_ACCOUNT_FILE environment variable (file path)
        if not service_account_info:
            service_account_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
            if service_account_file and os.path.exists(service_account_file):
                with open(service_account_file, 'r') as f:
                    service_account_info = json.load(f)
                logger.info(f"Using service account from file: {service_account_file}")
        
        # Method 3: Look for credentials.json in current directory (fallback)
        if not service_account_info:
            credentials_file = 'service_account.json'
            if os.path.exists(credentials_file):
                with open(credentials_file, 'r') as f:
                    service_account_info = json.load(f)
                logger.info(f"Using service account from local file: {credentials_file}")
        
        if not service_account_info:
            raise Exception(
                "Google service account credentials not found. Please set either:\n"
                "1. GOOGLE_SERVICE_ACCOUNT_JSON environment variable with JSON content, or\n"
                "2. GOOGLE_SERVICE_ACCOUNT_FILE environment variable with file path, or\n"
                "3. Place service_account.json file in the project directory"
            )
        
        # Define the scopes needed for Google Drive
        scopes = ['https://www.googleapis.com/auth/drive.file']
        
        # Create credentials from service account info
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=scopes
        )
        
        # Build the Drive service
        service = build('drive', 'v3', credentials=credentials)
        
        logger.info("✓ Google Drive credentials setup successful")
        return service
        
    except ImportError as e:
        logger.error("Google API libraries not available")
        raise Exception(f"Required Google API libraries not installed: {e}")
        
    except Exception as e:
        logger.error(f"Failed to setup Google Drive credentials: {e}")
        raise Exception(f"Google Drive authentication failed: {e}")


def verify_folder_access(folder_id: str) -> bool:
    """
    Verify that we have write access to the target Google Drive folder.
    
    Args:
        folder_id: Google Drive folder ID to check
        
    Returns:
        True if folder is accessible and writable
        
    Raises:
        Exception: If folder access check fails
    """
    logger.info(f"Verifying access to Google Drive folder: {folder_id}")
    
    if not folder_id:
        logger.warning("No folder ID provided - files will be uploaded to root directory")
        return True
    
    try:
        # Set up credentials and service
        service = setup_drive_credentials()
        
        # Try to get folder metadata to verify it exists and we have access
        folder = service.files().get(
            fileId=folder_id,
            fields='id,name,parents,capabilities'
        ).execute()
        
        folder_name = folder.get('name', 'Unknown')
        capabilities = folder.get('capabilities', {})
        
        # Check if we can add children (upload files) to this folder
        can_add_children = capabilities.get('canAddChildren', False)
        
        if not can_add_children:
            logger.error(f"No write permission for folder '{folder_name}' ({folder_id})")
            return False
        
        logger.info(f"✓ Successfully verified access to folder '{folder_name}' ({folder_id})")
        return True
        
    except Exception as e:
        error_message = str(e).lower()
        
        if "not found" in error_message or "404" in error_message:
            logger.error(f"Folder {folder_id} not found or not accessible")
            raise Exception(f"Google Drive folder '{folder_id}' not found or not accessible")
        elif "permission" in error_message or "forbidden" in error_message:
            logger.error(f"No permission to access folder {folder_id}")
            raise Exception(f"No permission to access Google Drive folder '{folder_id}'")
        else:
            logger.error(f"Failed to verify folder access: {e}")
            raise Exception(f"Failed to verify Google Drive folder access: {e}")
        
        return False 