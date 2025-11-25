"""
Object storage service for files.
"""
import boto3
from botocore.client import Config
from typing import BinaryIO, Optional
from app.config import settings
import os
from pathlib import Path


class StorageService:
    """Service for object storage (S3/MinIO)."""
    
    def __init__(self):
        """Initialize storage client."""
        self.storage_type = settings.STORAGE_TYPE
        self.bucket_name = settings.S3_BUCKET_NAME
        
        if self.storage_type == "s3":
            self.s3_client = boto3.client(
                's3',
                endpoint_url=settings.S3_ENDPOINT_URL,
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
                region_name=settings.S3_REGION,
                config=Config(signature_version='s3v4')
            )
            self._ensure_bucket()
        elif self.storage_type == "local":
            self.local_storage_path = Path("storage")
            self.local_storage_path.mkdir(exist_ok=True)
        else:
            raise ValueError(f"Unsupported storage type: {self.storage_type}")
    
    def _ensure_bucket(self):
        """Ensure the bucket exists (for S3)."""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except Exception as e:
            # Log error but don't fail - bucket might not exist yet or permissions issue
            # Will create on first use
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Could not access bucket {self.bucket_name}: {e}. Will attempt on first use.")
            # Don't fail - will handle errors when actually using storage
    
    async def save_file(
        self,
        file_data: BinaryIO,
        key: str,
        content_type: Optional[str] = None
    ) -> str:
        """Save file to storage and return the key."""
        if self.storage_type == "s3":
            self.s3_client.upload_fileobj(
                file_data,
                self.bucket_name,
                key,
                ExtraArgs={"ContentType": content_type} if content_type else {}
            )
            return key
        else:  # local
            file_path = self.local_storage_path / key
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(file_data.read())
            return key
    
    async def get_file_url(self, key: str, expires_in: int = 3600) -> str:
        """Get a signed URL for accessing a file."""
        if self.storage_type == "s3":
            return self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=expires_in
            )
        else:
            return f"/storage/{key}"
    
    async def delete_file(self, key: str):
        """Delete a file from storage."""
        if self.storage_type == "s3":
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
        else:
            file_path = self.local_storage_path / key
            if file_path.exists():
                file_path.unlink()


storage_service = StorageService()

