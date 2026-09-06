import os
import re
import uuid
import hashlib
import logging
from typing import Tuple, Optional
from urllib.parse import urlparse
from app.config import settings

logger = logging.getLogger("facechain.helpers")

SOCIAL_DOMAINS = {
    "instagram.com": "Instagram",
    "instagr.am": "Instagram",
    "facebook.com": "Facebook",
    "fb.com": "Facebook",
    "fb.watch": "Facebook",
    "twitter.com": "X (Twitter)",
    "x.com": "X (Twitter)",
    "t.co": "X (Twitter)",
    "tiktok.com": "TikTok",
    "youtube.com": "YouTube",
    "youtu.be": "YouTube",
    "linkedin.com": "LinkedIn",
    "reddit.com": "Reddit",
    "redd.it": "Reddit",
    "pinterest.com": "Pinterest",
    "pin.it": "Pinterest",
    "threads.net": "Threads",
    "vk.com": "VKontakte",
    "weibo.com": "Weibo"
}

def ensure_temp_dir() -> str:
    """Ensure the temporary upload directory exists and return its path."""
    os.makedirs(settings.TEMP_UPLOAD_DIR, exist_ok=True)
    return settings.TEMP_UPLOAD_DIR

def compute_sha256(data: bytes) -> str:
    """Compute standard hex SHA-256 hash of bytes."""
    return hashlib.sha256(data).hexdigest()

def classify_social_platform(url: str) -> Tuple[Optional[str], str]:
    """
    Classify whether a URL belongs to a known social media platform.
    Returns: (platform_name or None, clean_domain)
    """
    if not url:
        return None, ""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        if domain.startswith("m."):
            domain = domain[3:]
        if domain.startswith("mobile."):
            domain = domain[7:]
            
        # Match against known domain patterns
        for key_domain, platform_name in SOCIAL_DOMAINS.items():
            if domain == key_domain or domain.endswith("." + key_domain):
                return platform_name, domain
                
        return None, domain
    except Exception as e:
        logger.warning(f"Error parsing URL {url}: {e}")
        return None, ""

def generate_safe_filename(original_filename: str) -> Tuple[str, str]:
    """
    Generate a secure, unique filename for temporary storage.
    Returns: (new_filename, absolute_filepath)
    """
    ext = os.path.splitext(original_filename)[1].lower()
    if not ext or ext[1:] not in settings.allowed_extensions_set:
        ext = ".jpg"
    safe_name = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(ensure_temp_dir(), safe_name)
    return safe_name, filepath

def safe_delete_file(filepath: Optional[str]) -> bool:
    """Safely delete a temporary file if it exists."""
    if not filepath:
        return False
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.debug(f"Temporary file deleted: {filepath}")
            return True
    except Exception as e:
        logger.warning(f"Failed to delete temp file {filepath}: {e}")
    return False

def validate_image_bytes(image_bytes: bytes, filename: str) -> Tuple[bool, Optional[str]]:
    """Validate uploaded image size and header magic bytes."""
    if not image_bytes or len(image_bytes) == 0:
        return False, "Empty image file provided."

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(image_bytes) > max_bytes:
        return False, f"File size exceeds maximum allowed {settings.MAX_UPLOAD_SIZE_MB}MB"
        
    ext = os.path.splitext(filename)[1].lower().lstrip(".")
    # If extension is present, check against common supported formats
    valid_exts = settings.allowed_extensions_set.union({
        "jpg", "jpeg", "png", "webp", "bmp", "gif", "tiff", "jfif", "heic", "heif", "svg", "blob", ""
    })
    
    if ext and ext not in valid_exts:
        # Check if bytes are still decodable image bytes
        if not (image_bytes.startswith(b'\xff\xd8\xff') or 
                image_bytes.startswith(b'\x89PNG\r\n\x1a\n') or 
                (image_bytes.startswith(b'RIFF') and b'WEBP' in image_bytes[:16])):
            return False, f"Unsupported file extension '.{ext}'. Allowed: {', '.join(settings.allowed_extensions_set)}"
        
    # Magic bytes check for JPEG, PNG, WebP, BMP, GIF
    if image_bytes.startswith(b'\xff\xd8\xff'):
        return True, None
    elif image_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
        return True, None
    elif image_bytes.startswith(b'RIFF') and b'WEBP' in image_bytes[:16]:
        return True, None
    elif image_bytes.startswith(b'BM'):
        return True, None
    elif image_bytes.startswith(b'GIF87a') or image_bytes.startswith(b'GIF89a'):
        return True, None
    elif len(image_bytes) > 16:
        # Permissive check for any binary image data
        return True, None
        
    return False, "Invalid or empty image file format"
