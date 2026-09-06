import os
import abc
import json
import logging
import httpx
from typing import List, Optional, Dict, Any
from app.config import settings
from app.models.schemas import SearchResultItem, ReverseSearchResponse
from app.utils.helpers import classify_social_platform

logger = logging.getLogger("facechain.reverse_search")

class ReverseImageSearchProvider(abc.ABC):
    """
    Abstract Base Class for genuine reverse-image search integrations.
    """
    @property
    @abc.abstractmethod
    def provider_name(self) -> str:
        pass

    @abc.abstractmethod
    async def search(self, image_bytes: bytes, filename: str, image_url: Optional[str] = None) -> List[SearchResultItem]:
        """
        Execute reverse image search with provided image bytes or URL.
        Returns a list of normalized SearchResultItem objects.
        """
        pass

class SerpApiProvider(ReverseImageSearchProvider):
    """
    SerpApi Reverse Image Search / Google Lens Provider.
    Calls https://serpapi.com/search.json?engine=google_lens or google_reverse_image
    """
    def __init__(self, api_key: str, engine: str = "google_lens"):
        self.api_key = api_key
        self.engine = engine or "google_lens"

    @property
    def provider_name(self) -> str:
        return f"SerpApi ({self.engine})"

    async def search(self, image_bytes: bytes, filename: str, image_url: Optional[str] = None) -> List[SearchResultItem]:
        if not self.api_key:
            raise ValueError("SerpApi API key is not configured in REVERSE_IMAGE_API_KEY")

        results: List[SearchResultItem] = []
        async with httpx.AsyncClient(timeout=30.0) as client:
            if image_url:
                params = {
                    "engine": self.engine,
                    "url": image_url,
                    "api_key": self.api_key
                }
                response = await client.get("https://serpapi.com/search.json", params=params)
            else:
                # SerpApi Google Lens accepts image file uploads via POST or direct multipart
                files = {"file": (filename, image_bytes, "image/jpeg")}
                data = {
                    "engine": self.engine,
                    "api_key": self.api_key
                }
                # Direct upload to SerpApi endpoint or query
                response = await client.post("https://serpapi.com/search.json", data=data, files=files)

            if response.status_code != 200:
                logger.error(f"SerpApi error ({response.status_code}): {response.text}")
                raise RuntimeError(f"SerpApi request failed with status {response.status_code}: {response.text}")

            data = response.json()
            
            # Parse Google Lens visual matches
            visual_matches = data.get("visual_matches", [])
            for item in visual_matches:
                url = item.get("link") or item.get("url") or ""
                if not url:
                    continue
                platform, domain = classify_social_platform(url)
                title = item.get("title") or item.get("source") or ""
                thumbnail = item.get("thumbnail") or item.get("thumbnail_url")
                source_name = item.get("source") or "Google Lens / SerpApi"
                
                results.append(SearchResultItem(
                    title=title,
                    url=url,
                    domain=domain,
                    thumbnail=thumbnail,
                    source=source_name,
                    platform=platform,
                    is_social_media=bool(platform),
                    raw_metadata={"position": item.get("position"), "price": item.get("price")}
                ))
                
            # Also check image_results if using google_reverse_image engine
            image_results = data.get("image_results", [])
            for item in image_results:
                url = item.get("link") or ""
                if not url:
                    continue
                platform, domain = classify_social_platform(url)
                title = item.get("title") or item.get("snippet") or ""
                thumbnail = item.get("thumbnail")
                source_name = item.get("source") or "Google Images / SerpApi"
                
                results.append(SearchResultItem(
                    title=title,
                    url=url,
                    domain=domain,
                    thumbnail=thumbnail,
                    source=source_name,
                    platform=platform,
                    is_social_media=bool(platform),
                    published_at=item.get("published_date")
                ))

        return results

class BingVisualSearchProvider(ReverseImageSearchProvider):
    """
    Microsoft Azure Bing Visual Search API Provider.
    """
    def __init__(self, api_key: str, endpoint: str):
        self.api_key = api_key
        self.endpoint = endpoint or "https://api.bing.microsoft.com/v7.0/images/visualsearch"

    @property
    def provider_name(self) -> str:
        return "Bing Visual Search API"

    async def search(self, image_bytes: bytes, filename: str, image_url: Optional[str] = None) -> List[SearchResultItem]:
        if not self.api_key:
            raise ValueError("Bing Visual Search API key is not configured")

        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        results: List[SearchResultItem] = []

        async with httpx.AsyncClient(timeout=30.0) as client:
            files = {'image': (filename, image_bytes, 'multipart/form-data')}
            response = await client.post(self.endpoint, headers=headers, files=files)

            if response.status_code != 200:
                raise RuntimeError(f"Bing Visual Search failed ({response.status_code}): {response.text}")

            data = response.json()
            tags = data.get("tags", [])
            for tag in tags:
                for action in tag.get("actions", []):
                    if action.get("actionType") in ["VisualSearch", "PagesIncluding", "WebResults"]:
                        for val in action.get("data", {}).get("value", []):
                            url = val.get("hostPageUrl") or val.get("webSearchUrl") or ""
                            if not url:
                                continue
                            platform, domain = classify_social_platform(url)
                            title = val.get("name") or val.get("snippet") or ""
                            thumbnail = val.get("thumbnailUrl") or val.get("contentUrl")
                            
                            results.append(SearchResultItem(
                                title=title,
                                url=url,
                                domain=domain,
                                thumbnail=thumbnail,
                                source="Bing Visual Search",
                                platform=platform,
                                is_social_media=bool(platform),
                                published_at=val.get("datePublished")
                            ))
        return results

class RapidApiProvider(ReverseImageSearchProvider):
    """
    RapidAPI Reverse Image Search provider (supports Lens/Visual search endpoints).
    """
    def __init__(self, api_key: str, host: str):
        self.api_key = api_key
        self.host = host or "google-lens-reverse-image-search.p.rapidapi.com"

    @property
    def provider_name(self) -> str:
        return f"RapidAPI ({self.host})"

    async def search(self, image_bytes: bytes, filename: str, image_url: Optional[str] = None) -> List[SearchResultItem]:
        if not self.api_key:
            raise ValueError("RapidAPI key is not configured")

        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.host
        }
        results: List[SearchResultItem] = []

        async with httpx.AsyncClient(timeout=30.0) as client:
            files = {"file": (filename, image_bytes, "image/jpeg")}
            url = f"https://{self.host}/search"
            response = await client.post(url, headers=headers, files=files)

            if response.status_code != 200:
                raise RuntimeError(f"RapidAPI request failed ({response.status_code}): {response.text}")

            data = response.json()
            items = data.get("results") or data.get("visual_matches") or data.get("matches") or []
            for item in items:
                link = item.get("link") or item.get("url") or ""
                if not link:
                    continue
                platform, domain = classify_social_platform(link)
                results.append(SearchResultItem(
                    title=item.get("title") or item.get("name") or "",
                    url=link,
                    domain=domain,
                    thumbnail=item.get("thumbnail"),
                    source="RapidAPI Lens",
                    platform=platform,
                    is_social_media=bool(platform)
                ))
        return results

class DemoModeProvider(ReverseImageSearchProvider):
    """
    Explicitly labeled offline demonstration provider.
    Used ONLY when ALLOW_DEMO_FALLBACK=True and no external API key is configured.
    Labels all output with clear [DEMO MODE - MOCK DATA] tags.
    """
    @property
    def provider_name(self) -> str:
        return "Demo Mode Provider [MOCK DATA]"

    async def search(self, image_bytes: bytes, filename: str, image_url: Optional[str] = None) -> List[SearchResultItem]:
        # Realistic sample results clearly marked as demonstration data
        demo_items = [
            SearchResultItem(
                title="Verified Photography Showcase — Public Instagram Archive",
                url="https://www.instagram.com/p/C_DemoPhotoRecord2026",
                domain="instagram.com",
                thumbnail="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80",
                source="Demo Simulation (Instagram Search Result)",
                platform="Instagram",
                is_social_media=True,
                similarity="94.8% Match",
                published_at="2026-08-14T10:22:00Z",
                raw_metadata={"note": "DEMO MODE — Sample social media result for offline test verification"}
            ),
            SearchResultItem(
                title="Speaker Profile & Portrait — Open Tech Conference (X/Twitter Post)",
                url="https://x.com/tech_innovator/status/1827394018274918273",
                domain="x.com",
                thumbnail="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=300&q=80",
                source="Demo Simulation (X/Twitter Search Result)",
                platform="X (Twitter)",
                is_social_media=True,
                similarity="89.2% Match",
                published_at="2026-07-29T18:40:12Z"
            ),
            SearchResultItem(
                title="Global Developer Community Spotlight on Reddit",
                url="https://www.reddit.com/r/technology/comments/1exdemo/ai_face_blockchain_evidence_showcase/",
                domain="reddit.com",
                thumbnail="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=300&q=80",
                source="Demo Simulation (Reddit Web Match)",
                platform="Reddit",
                is_social_media=True,
                similarity="83.5% Match",
                published_at="2026-08-01T04:15:30Z"
            )
        ]
        return demo_items

class ReverseSearchService:
    """
    High-level reverse image search service factory and coordinator.
    """
    def __init__(self):
        self._provider = self._create_provider()

    def _create_provider(self) -> ReverseImageSearchProvider:
        prov_name = settings.REVERSE_IMAGE_PROVIDER.lower().strip()
        api_key = settings.REVERSE_IMAGE_API_KEY.strip()

        if prov_name == "serpapi":
            if api_key:
                return SerpApiProvider(api_key=api_key, engine=settings.SERPAPI_ENGINE)
            elif settings.ALLOW_DEMO_FALLBACK:
                logger.warning("No SerpApi key supplied; falling back to labeled DemoModeProvider.")
                return DemoModeProvider()
            else:
                return SerpApiProvider(api_key="", engine=settings.SERPAPI_ENGINE)

        elif prov_name == "bing":
            if api_key:
                return BingVisualSearchProvider(api_key=api_key, endpoint=settings.BING_ENDPOINT)
            elif settings.ALLOW_DEMO_FALLBACK:
                return DemoModeProvider()
            else:
                return BingVisualSearchProvider(api_key="", endpoint=settings.BING_ENDPOINT)

        elif prov_name == "rapidapi":
            if api_key:
                return RapidApiProvider(api_key=api_key, host=settings.RAPIDAPI_HOST)
            elif settings.ALLOW_DEMO_FALLBACK:
                return DemoModeProvider()
            else:
                return RapidApiProvider(api_key="", host=settings.RAPIDAPI_HOST)

        elif prov_name == "demo":
            return DemoModeProvider()

        else:
            if settings.ALLOW_DEMO_FALLBACK:
                return DemoModeProvider()
            return SerpApiProvider(api_key="", engine="google_lens")

    async def execute_search(self, image_bytes: bytes, filename: str, image_url: Optional[str] = None) -> ReverseSearchResponse:
        """
        Execute reverse image search, filter results for social media platforms,
        and return a structured response.
        """
        provider = self._create_provider()
        is_demo = isinstance(provider, DemoModeProvider)
        demo_badge = "DEMO MODE — MOCK DATA (Configure REVERSE_IMAGE_API_KEY for live search)" if is_demo else None

        try:
            results = await provider.search(image_bytes=image_bytes, filename=filename, image_url=image_url)
            
            # Find primary social media match
            social_matches = [r for r in results if r.is_social_media]
            primary_match = social_matches[0] if social_matches else (results[0] if results else None)
            
            return ReverseSearchResponse(
                success=True,
                provider=provider.provider_name,
                results_count=len(results),
                social_match_found=bool(social_matches),
                primary_match=primary_match,
                all_results=results,
                is_demo_mode=is_demo,
                demo_badge_message=demo_badge
            )
        except Exception as e:
            logger.error(f"Reverse image search failed: {e}")
            # If demo fallback is allowed, provide demo results with clear warning
            if settings.ALLOW_DEMO_FALLBACK and not is_demo:
                logger.info("Falling back to labeled DemoModeProvider due to provider failure.")
                demo_prov = DemoModeProvider()
                demo_res = await demo_prov.search(image_bytes, filename, image_url)
                return ReverseSearchResponse(
                    success=True,
                    provider="Demo Mode Fallback (Live Provider Error)",
                    results_count=len(demo_res),
                    social_match_found=True,
                    primary_match=demo_res[0],
                    all_results=demo_res,
                    is_demo_mode=True,
                    demo_badge_message=f"DEMO MODE — Live search failed ({str(e)}). Displaying test mock results.",
                    error_message=str(e)
                )

            return ReverseSearchResponse(
                success=False,
                provider=provider.provider_name,
                results_count=0,
                social_match_found=False,
                primary_match=None,
                all_results=[],
                is_demo_mode=is_demo,
                error_message=str(e)
            )

# Global singleton instance
reverse_search_service = ReverseSearchService()
