"""
Uploader module for AI Daily Briefing Agent.

This module handles uploading the generated audio file
to Amazon S3 for easy streaming and access.
"""

import logging
from datetime import datetime

from config import get_config

logger = logging.getLogger(__name__)


def upload_to_s3(audio_data: bytes, filename: str = None) -> str:
    """
    Upload audio file to Amazon S3.
    
    Args:
        audio_data: Audio bytes to upload
        filename: Optional filename (auto-generated if not provided)
        
    Returns:
        S3 object URL of uploaded file
        
    Raises:
        Exception: If S3 upload fails
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"daily_briefing_{timestamp}.mp3"
        
    logger.info(f"Uploading audio to S3: {filename}")
    
    if not audio_data:
        raise Exception("Cannot upload empty audio data to S3")
    
    logger.info(f"Audio size: {len(audio_data)} bytes")
    
    try:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError
        
        # Get configuration
        config = get_config()
        bucket_name = config.get('S3_BUCKET_NAME')
        
        # Verify bucket access
        if not verify_bucket_access(bucket_name):
            raise Exception(f"Cannot access S3 bucket: {bucket_name}")
        
        # Create S3 client
        s3_client = boto3.client('s3')
        
        logger.info("Uploading file to S3...")
        
        # Upload the file
        s3_client.put_object(
            Bucket=bucket_name,
            Key=filename,
            Body=audio_data,
            ContentType='audio/mpeg',
            Metadata={
                'Content-Type': 'audio/mpeg',
                'Generated-By': 'AI-Daily-Briefing-Agent',
                'Generated-Date': datetime.now().isoformat()
            }
        )
        
        # Generate the S3 URL
        s3_url = f"https://{bucket_name}.s3.amazonaws.com/{filename}"
        
        logger.info(f"✓ Successfully uploaded to S3")
        logger.info(f"  Bucket: {bucket_name}")
        logger.info(f"  Key: {filename}")
        logger.info(f"  URL: {s3_url}")
        
        return s3_url
        
    except ImportError as e:
        logger.error("boto3 library not available")
        raise Exception(f"boto3 library not installed: {e}")
        
    except Exception as e:
        # Handle specific S3 errors first
        error_message = str(e)
        
        if "NoSuchBucket" in error_message:
            raise Exception(f"S3 bucket '{bucket_name}' does not exist.")
        elif "AccessDenied" in error_message:
            raise Exception(f"Access denied to S3 bucket '{bucket_name}'. Please check IAM permissions.")
        elif "InvalidAccessKeyId" in error_message:
            raise Exception("Invalid AWS access key. Please check your AWS credentials.")
        elif "SignatureDoesNotMatch" in error_message:
            raise Exception("AWS signature mismatch. Please check your AWS credentials.")
        elif "NoCredentialsError" in error_message or "Unable to locate credentials" in error_message:
            raise Exception("AWS credentials not found. Please configure AWS credentials.")
        else:
            raise Exception(f"S3 upload failed: {e}")


def verify_bucket_access(bucket_name: str) -> bool:
    """
    Verify that we have write access to the target S3 bucket.
    
    Args:
        bucket_name: S3 bucket name to check
        
    Returns:
        True if bucket is accessible and writable
        
    Raises:
        Exception: If bucket access check fails
    """
    logger.info(f"Verifying access to S3 bucket: {bucket_name}")
    
    if not bucket_name:
        logger.warning("No bucket name provided")
        return False
    
    try:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError
        
        # Create S3 client
        s3_client = boto3.client('s3')
        
        # Try to get bucket location to verify it exists and we have access
        response = s3_client.get_bucket_location(Bucket=bucket_name)
        
        region = response.get('LocationConstraint')
        if region is None:
            region = 'us-east-1'  # Default region for buckets without location constraint
            
        logger.info(f"✓ Successfully verified access to bucket '{bucket_name}' in region '{region}'")
        return True
        
    except Exception as e:
        # Handle specific S3 errors first
        error_message = str(e)
        
        if "NoSuchBucket" in error_message:
            logger.error(f"Bucket {bucket_name} does not exist")
            raise Exception(f"S3 bucket '{bucket_name}' does not exist")
        elif "AccessDenied" in error_message:
            logger.error(f"No permission to access bucket {bucket_name}")
            raise Exception(f"No permission to access S3 bucket '{bucket_name}'")
        elif "NoCredentialsError" in error_message or "Unable to locate credentials" in error_message:
            logger.error("AWS credentials not found")
            raise Exception("AWS credentials not found. Please configure AWS credentials.")
        else:
            logger.error(f"Failed to verify bucket access: {error_message}")
            raise Exception(f"Failed to verify S3 bucket access: {error_message}")


def setup_s3_credentials():
    """
    Set up AWS S3 credentials.
    
    Returns:
        Authenticated boto3 S3 client
        
    Raises:
        Exception: If credential setup fails
    """
    logger.info("Setting up AWS S3 credentials...")
    
    try:
        import boto3
        from botocore.exceptions import NoCredentialsError
        
        # boto3 will automatically use credentials from:
        # 1. Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
        # 2. AWS credentials file (~/.aws/credentials)
        # 3. IAM role (when running on AWS)
        
        s3_client = boto3.client('s3')
        
        # Test credentials by making a simple API call
        s3_client.list_buckets()
        
        logger.info("✓ AWS S3 credentials setup successful")
        return s3_client
        
    except ImportError as e:
        logger.error("boto3 library not available")
        raise Exception(f"Required boto3 library not installed: {e}")
        
    except NoCredentialsError:
        logger.error("AWS credentials not found")
        raise Exception(
            "AWS credentials not found. Please configure credentials using:\n"
            "1. Environment variables: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY\n"
            "2. AWS credentials file: ~/.aws/credentials\n"
            "3. IAM role (when running on AWS Lambda)"
        )
        
    except Exception as e:
        logger.error(f"Failed to setup AWS S3 credentials: {e}")
        raise Exception(f"AWS S3 authentication failed: {e}") 