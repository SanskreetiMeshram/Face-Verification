import pytest
from app.utils.helpers import classify_social_platform
from app.services.reverse_search import reverse_search_service, DemoModeProvider

def test_classify_social_platforms():
    """Verify accurate extraction of known social media platforms from URLs."""
    test_cases = [
        ("https://www.instagram.com/p/C_abc123/", "Instagram"),
        ("https://instagr.am/p/xyz", "Instagram"),
        ("https://x.com/tech_innovator/status/123", "X (Twitter)"),
        ("https://twitter.com/user/status/456", "X (Twitter)"),
        ("https://tiktok.com/@creator/video/789", "TikTok"),
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "YouTube"),
        ("https://youtu.be/dQw4w9WgXcQ", "YouTube"),
        ("https://www.linkedin.com/in/john-doe", "LinkedIn"),
        ("https://reddit.com/r/technology/comments/abc", "Reddit"),
        ("https://facebook.com/photo.php?fbid=101", "Facebook"),
        ("https://example.com/unrelated/blog/post", None),
        ("https://news.ycombinator.com/item?id=123", None),
    ]

    for url, expected_platform in test_cases:
        platform, domain = classify_social_platform(url)
        assert platform == expected_platform, f"Failed for {url}: got {platform}, expected {expected_platform}"
        assert domain != "", f"Domain should not be empty for {url}"

@pytest.mark.asyncio
async def test_demo_provider_output():
    """Verify demo mode provider provides clearly labeled results with social media flags."""
    provider = DemoModeProvider()
    results = await provider.search(b"dummy", "dummy.jpg")
    
    assert len(results) > 0
    assert any(r.is_social_media for r in results)
    assert any(r.platform == "Instagram" for r in results)
    assert any("Demo Simulation" in r.source for r in results)
