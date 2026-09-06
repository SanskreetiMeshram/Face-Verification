import os
import abc
import json
import logging
from datetime import datetime, timezone
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
            raise ValueError("Reverse-image search provider is not configured.")

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
                files = {"file": (filename, image_bytes, "image/jpeg")}
                data = {
                    "engine": self.engine,
                    "api_key": self.api_key
                }
                response = await client.post("https://serpapi.com/search.json", data=data, files=files)

            if response.status_code != 200:
                logger.error(f"SerpApi error ({response.status_code}): {response.text}")
                raise RuntimeError(f"SerpApi search request failed with status {response.status_code}: {response.text}")

            data = response.json()
            now_iso = datetime.now(timezone.utc).isoformat()
            
            # Parse Google Lens visual matches
            visual_matches = data.get("visual_matches", [])
            for item in visual_matches:
                url = item.get("link") or item.get("url") or ""
                if not url:
                    continue
                platform, domain = classify_social_platform(url)
                title = item.get("title") or item.get("source") or ""
                thumbnail = item.get("thumbnail") or item.get("thumbnail_url")
                source_name = item.get("source") or "Google Lens (SerpApi)"
                
                results.append(SearchResultItem(
                    title=title,
                    url=url,
                    domain=domain,
                    thumbnail=thumbnail,
                    source=source_name,
                    platform=platform,
                    is_social_media=bool(platform),
                    similarity="Potential Match (Google Lens)",
                    discovered_at=now_iso,
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
                source_name = item.get("source") or "Google Images (SerpApi)"
                
                results.append(SearchResultItem(
                    title=title,
                    url=url,
                    domain=domain,
                    thumbnail=thumbnail,
                    source=source_name,
                    platform=platform,
                    is_social_media=bool(platform),
                    similarity="Potential Match (Google Images)",
                    published_at=item.get("published_date"),
                    discovered_at=now_iso
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
            raise ValueError("Reverse-image search provider is not configured.")

        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        results: List[SearchResultItem] = []
        now_iso = datetime.now(timezone.utc).isoformat()

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
                                similarity="Potential Match (Bing)",
                                published_at=val.get("datePublished"),
                                discovered_at=now_iso
                            ))
        return results

class RapidApiProvider(ReverseImageSearchProvider):
    """
    RapidAPI Reverse Image Search provider.
    """
    def __init__(self, api_key: str, host: str):
        self.api_key = api_key
        self.host = host or "google-lens-reverse-image-search.p.rapidapi.com"

    @property
    def provider_name(self) -> str:
        return f"RapidAPI ({self.host})"

    async def search(self, image_bytes: bytes, filename: str, image_url: Optional[str] = None) -> List[SearchResultItem]:
        if not self.api_key:
            raise ValueError("Reverse-image search provider is not configured.")

        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.host
        }
        results: List[SearchResultItem] = []
        now_iso = datetime.now(timezone.utc).isoformat()

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
                    is_social_media=bool(platform),
                    similarity="Potential Match (RapidAPI)",
                    discovered_at=now_iso
                ))
        return results

class DemoModeProvider(ReverseImageSearchProvider):
    """
    Explicitly labeled deterministic offline demonstration provider.
    Used ONLY for demonstrating UI, canonical hashing, and blockchain workflows when no live API key is configured.
    Labels all output with prominent 'DEMO DATA — NOT A LIVE SEARCH RESULT' warnings.
    """
    @property
    def provider_name(self) -> str:
        return "Demo Provider [DEMO DATA — NOT A LIVE SEARCH RESULT]"

    async def search(self, image_bytes: bytes, filename: str, image_url: Optional[str] = None) -> List[SearchResultItem]:
        demo_items = [
            SearchResultItem(
                title="Public Web Photography Showcase (Instagram Archive)",
                url="https://www.instagram.com/p/C_DemoPhotoRecord2026",
                domain="instagram.com",
                thumbnail="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80",
                source="Demo Simulation (Public Instagram Post)",
                platform="Instagram",
                is_social_media=True,
                similarity="Potential Match (Demo Sample)",
                published_at="2026-08-14T10:22:00Z",
                discovered_at="2026-09-06T12:00:00Z",
                raw_metadata={"note": "DEMO DATA — NOT A LIVE SEARCH RESULT"}
            ),
            SearchResultItem(
                title="Keynote Speaker Portrait — Open Tech Summit (X/Twitter Post)",
                url="https://x.com/tech_innovator/status/1827394018274918273",
                domain="x.com",
                thumbnail="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=300&q=80",
                source="Demo Simulation (Public X/Twitter Post)",
                platform="X (Twitter)",
                is_social_media=True,
                similarity="Potential Match (Demo Sample)",
                published_at="2026-07-29T18:40:12Z",
                discovered_at="2026-09-06T12:00:00Z"
            ),
            SearchResultItem(
                title="Global Developer Community Portrait on Reddit",
                url="https://www.reddit.com/r/technology/comments/1exdemo/ai_face_blockchain_evidence_showcase/",
                domain="reddit.com",
                thumbnail="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=300&q=80",
                source="Demo Simulation (Public Reddit Post)",
                platform="Reddit",
                is_social_media=True,
                similarity="Potential Match (Demo Sample)",
                published_at="2026-08-01T04:15:30Z",
                discovered_at="2026-09-06T12:00:00Z"
            )
        ]
        return demo_items

class ReverseSearchService:
    """
    Reverse image search service factory and coordinator.
    """
    def __init__(self):
        pass

    def _create_provider(self) -> ReverseImageSearchProvider:
        prov_name = settings.active_search_provider
        api_key = settings.active_search_api_key

        if prov_name == "serpapi":
            if api_key:
                return SerpApiProvider(api_key=api_key, engine=settings.SERPAPI_ENGINE)
            elif settings.ALLOW_DEMO_FALLBACK:
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
        Execute reverse image search across configured provider.
        """
        provider = self._create_provider()
        is_demo = isinstance(provider, DemoModeProvider)
        demo_badge = "DEMO DATA — NOT A LIVE SEARCH RESULT (Set REVERSE_SEARCH_API_KEY in .env for live discovery)" if is_demo else None

        try:
            results = await provider.search(image_bytes=image_bytes, filename=filename, image_url=image_url)
            
            if not results:
                return ReverseSearchResponse(
                    success=True,
                    provider=provider.provider_name,
                    results_count=0,
                    match_status="NOT_FOUND",
                    social_match_found=False,
                    primary_match=None,
                    all_results=[],
                    is_demo_mode=is_demo,
                    demo_badge_message=demo_badge
                )

            social_matches = [r for r in results if r.is_social_media]
            primary_match = social_matches[0] if social_matches else results[0]
            
            return ReverseSearchResponse(
                success=True,
                provider=provider.provider_name,
                results_count=len(results),
                match_status="FOUND" if not is_demo else "POSSIBLE_MATCH",
                social_match_found=bool(social_matches),
                primary_match=primary_match,
                all_results=results,
                is_demo_mode=is_demo,
                demo_badge_message=demo_badge
            )
        except Exception as e:
            logger.warning(f"Reverse image search query failed: {e}")
            if settings.ALLOW_DEMO_FALLBACK and not is_demo:
                demo_prov = DemoModeProvider()
                demo_res = await demo_prov.search(image_bytes, filename, image_url)
                return ReverseSearchResponse(
                    success=True,
                    provider="Demo Provider [DEMO DATA — NOT A LIVE SEARCH RESULT]",
                    results_count=len(demo_res),
                    match_status="POSSIBLE_MATCH",
                    social_match_found=True,
                    primary_match=demo_res[0],
                    all_results=demo_res,
                    is_demo_mode=True,
                    demo_badge_message=f"DEMO DATA — Live search notice ({str(e)}). Showing demo sample data.",
                    error_message=None
                )

            return ReverseSearchResponse(
                success=False,
                provider=provider.provider_name,
                results_count=0,
                match_status="ERROR",
                social_match_found=False,
                primary_match=None,
                all_results=[],
                is_demo_mode=is_demo,
                error_message=str(e)
            )

# Global singleton instance
reverse_search_service = ReverseSearchService()
