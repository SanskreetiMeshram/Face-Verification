import re
import socket
import ipaddress
import urllib.parse
from datetime import datetime, timezone
import logging
from typing import Tuple, Optional
import httpx
from app.config import settings
from app.models.schemas import UrlMetadata

logger = logging.getLogger("prooflink.url_service")

# Regex patterns for HTML OpenGraph / Twitter Card image metadata
OG_IMAGE_REGEX = re.compile(r'<meta[^>]+(?:property|name)=["\'](?:og:image|og:image:secure_url|twitter:image|twitter:image:src)["\'][^>]+content=["\']([^"\']+)["\']', re.IGNORECASE)
OG_IMAGE_ALT_REGEX = re.compile(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\'](?:og:image|og:image:secure_url|twitter:image|twitter:image:src)["\']', re.IGNORECASE)
LINK_IMAGE_REGEX = re.compile(r'<link[^>]+rel=["\'](?:image_src|icon|apple-touch-icon)["\'][^>]+href=["\']([^"\']+)["\']', re.IGNORECASE)

class UrlService:
    def __init__(self):
        self.timeout = settings.URL_FETCH_TIMEOUT_SECONDS
        self.max_size_bytes = settings.MAX_URL_PAYLOAD_SIZE_MB * 1024 * 1024
        self.user_agent = settings.USER_AGENT

    def detect_platform(self, url: str) -> str:
        """Identify public social or web platform from URL hostname."""
        try:
            parsed = urllib.parse.urlparse(url)
            host = parsed.netloc.lower()
            if "twitter.com" in host or "x.com" in host or "t.co" in host:
                return "X (Twitter)"
            elif "instagram.com" in host or "cdninstagram.com" in host:
                return "Instagram"
            elif "linkedin.com" in host or "licdn.com" in host:
                return "LinkedIn"
            elif "github.com" in host or "githubusercontent.com" in host:
                return "GitHub"
            elif "gravatar.com" in host:
                return "Gravatar"
            elif "facebook.com" in host or "fbcdn.net" in host:
                return "Facebook"
            elif "youtube.com" in host or "ytimg.com" in host:
                return "YouTube"
            elif "unsplash.com" in host:
                return "Unsplash"
            elif "wikimedia.org" in host or "wikipedia.org" in host:
                return "Wikimedia"
            elif "threads.net" in host:
                return "Threads"
            elif "bluesky" in host or "bsky.app" in host:
                return "Bluesky"
            elif "medium.com" in host:
                return "Medium"
            elif "substack.com" in host:
                return "Substack"
            return "Public Web Profile"
        except Exception:
            return "Public Web Profile"

    def is_safe_url(self, url: str) -> Tuple[bool, Optional[str]]:
        """
        Anti-SSRF security verification.
        Disallows local, loopback, private RFC1918, or non-HTTP/HTTPS URLs.
        """
        try:
            parsed = urllib.parse.urlparse(url)
            if parsed.scheme.lower() not in ("http", "https"):
                return False, f"Invalid URL scheme '{parsed.scheme}'. Only HTTP and HTTPS are permitted."

            hostname = parsed.hostname
            if not hostname:
                return False, "Invalid URL: missing hostname."

            # Block localhost & standard loopback names
            if hostname.lower() in ("localhost", "127.0.0.1", "0.0.0.0", "::1", "local"):
                return False, "Access to localhost and internal loopback addresses is restricted."

            # Resolve IP to check for private / internal network subnets
            try:
                ip_str = socket.gethostbyname(hostname)
                ip_obj = ipaddress.ip_address(ip_str)
                if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_reserved or ip_obj.is_link_local:
                    return False, "Access to private or internal subnet IP addresses is restricted."
            except socket.gaierror:
                return False, f"Could not resolve domain name '{hostname}'."

            return True, None
        except Exception as e:
            return False, f"URL security check failed: {str(e)}"

    async def fetch_profile_image(self, input_url: str) -> Tuple[Optional[bytes], UrlMetadata, Optional[str]]:
        """
        Fetch image from a user-supplied URL.
        Accepts direct image URLs or public web/social URLs with OpenGraph preview metadata.
        Only fetches this single specific URL — never searches or crawls.
        """
        fetch_time_iso = datetime.now(timezone.utc).isoformat()
        platform = self.detect_platform(input_url)

        # 1. Security Check
        is_safe, error_msg = self.is_safe_url(input_url)
        if not is_safe:
            meta = UrlMetadata(
                input_url=input_url,
                resolved_url=input_url,
                content_type="none",
                http_status=400,
                platform_detected=platform,
                fetch_timestamp=fetch_time_iso,
                image_size_bytes=0,
                error=error_msg
            )
            return None, meta, error_msg

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 ProofLink/1.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,image/png,image/jpeg,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, headers=headers) as client:
                response = await client.get(input_url)
                
                final_url = str(response.url)
                status_code = response.status_code
                content_type = response.headers.get("content-type", "").lower()

                if status_code != 200:
                    err = f"URL returned HTTP {status_code} ({response.reason_phrase})."
                    meta = UrlMetadata(
                        input_url=input_url,
                        resolved_url=final_url,
                        content_type=content_type,
                        http_status=status_code,
                        platform_detected=platform,
                        fetch_timestamp=fetch_time_iso,
                        image_size_bytes=0,
                        error=err
                    )
                    return None, meta, err

                # Case A: Response is directly an image
                if content_type.startswith("image/"):
                    image_bytes = response.content
                    if len(image_bytes) > self.max_size_bytes:
                        err = f"Image size ({len(image_bytes) / 1024 / 1024:.1f} MB) exceeds maximum allowed limit."
                        meta = UrlMetadata(
                            input_url=input_url,
                            resolved_url=final_url,
                            content_type=content_type,
                            http_status=status_code,
                            platform_detected=platform,
                            fetch_timestamp=fetch_time_iso,
                            image_size_bytes=len(image_bytes),
                            is_direct_image=True,
                            error=err
                        )
                        return None, meta, err

                    meta = UrlMetadata(
                        input_url=input_url,
                        resolved_url=final_url,
                        content_type=content_type,
                        http_status=status_code,
                        platform_detected=platform,
                        fetch_timestamp=fetch_time_iso,
                        image_size_bytes=len(image_bytes),
                        is_direct_image=True
                    )
                    return image_bytes, meta, None

                # Case B: Response is HTML — extract image preview tag
                html_text = response.text
                extracted_image_url = None

                # Check OpenGraph & Twitter tags
                og_match = OG_IMAGE_REGEX.search(html_text) or OG_IMAGE_ALT_REGEX.search(html_text)
                if og_match:
                    extracted_image_url = og_match.group(1).strip()
                else:
                    link_match = LINK_IMAGE_REGEX.search(html_text)
                    if link_match:
                        extracted_image_url = link_match.group(1).strip()

                if not extracted_image_url:
                    err = "The provided URL is a web page, but no public preview image or OpenGraph face image was found in the page header."
                    meta = UrlMetadata(
                        input_url=input_url,
                        resolved_url=final_url,
                        content_type=content_type,
                        http_status=status_code,
                        platform_detected=platform,
                        fetch_timestamp=fetch_time_iso,
                        image_size_bytes=0,
                        error=err
                    )
                    return None, meta, err

                # Resolve relative URL if needed
                full_img_url = urllib.parse.urljoin(final_url, extracted_image_url)
                
                # Fetch the extracted image
                is_img_safe, img_sec_err = self.is_safe_url(full_img_url)
                if not is_img_safe:
                    err = f"Extracted preview image URL failed security check: {img_sec_err}"
                    meta = UrlMetadata(
                        input_url=input_url,
                        resolved_url=full_img_url,
                        content_type="none",
                        http_status=400,
                        platform_detected=platform,
                        fetch_timestamp=fetch_time_iso,
                        image_size_bytes=0,
                        error=err
                    )
                    return None, meta, err

                img_res = await client.get(full_img_url)
                if img_res.status_code != 200:
                    err = f"Extracted image URL returned HTTP {img_res.status_code}."
                    meta = UrlMetadata(
                        input_url=input_url,
                        resolved_url=str(img_res.url),
                        content_type=img_res.headers.get("content-type", ""),
                        http_status=img_res.status_code,
                        platform_detected=platform,
                        fetch_timestamp=fetch_time_iso,
                        image_size_bytes=0,
                        error=err
                    )
                    return None, meta, err

                img_bytes = img_res.content
                img_content_type = img_res.headers.get("content-type", "image/jpeg")

                meta = UrlMetadata(
                    input_url=input_url,
                    resolved_url=str(img_res.url),
                    content_type=img_content_type,
                    http_status=img_res.status_code,
                    platform_detected=platform,
                    fetch_timestamp=fetch_time_iso,
                    image_size_bytes=len(img_bytes),
                    is_direct_image=False
                )
                return img_bytes, meta, None

        except httpx.TimeoutException:
            err = f"Request timed out while connecting to {input_url} (exceeded {self.timeout}s)."
            meta = UrlMetadata(
                input_url=input_url,
                resolved_url=input_url,
                content_type="none",
                http_status=504,
                platform_detected=platform,
                fetch_timestamp=fetch_time_iso,
                image_size_bytes=0,
                error=err
            )
            return None, meta, err
        except Exception as e:
            err = f"Failed to fetch profile image: {str(e)}"
            meta = UrlMetadata(
                input_url=input_url,
                resolved_url=input_url,
                content_type="none",
                http_status=500,
                platform_detected=platform,
                fetch_timestamp=fetch_time_iso,
                image_size_bytes=0,
                error=err
            )
            return None, meta, err

url_service = UrlService()
