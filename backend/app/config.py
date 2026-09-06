import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App Information
    APP_NAME: str = "FaceChain Verify API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Reverse Search Configuration (Supports standard and aliased env keys)
    REVERSE_SEARCH_PROVIDER: Optional[str] = Field(default=None, description="Provider: serpapi, bing, rapidapi, tineye, searxng, demo")
    REVERSE_IMAGE_PROVIDER: str = Field(default="serpapi", description="Provider fallback")
    REVERSE_SEARCH_API_KEY: Optional[str] = Field(default=None, description="API key for the reverse search provider")
    REVERSE_IMAGE_API_KEY: str = Field(default="", description="API key fallback")
    SERPAPI_ENGINE: str = "google_lens"
    BING_ENDPOINT: str = "https://api.bing.microsoft.com/v7.0/images/visualsearch"
    RAPIDAPI_HOST: str = "google-lens-reverse-image-search.p.rapidapi.com"
    SEARXNG_URL: str = "http://localhost:8080"
    ALLOW_DEMO_FALLBACK: bool = True
    
    # Blockchain Settings (Supports local Hardhat/Anvil or Polygon Amoy)
    CHAIN_ID: int = 31337
    CHAIN_NAME: str = "Local Hardhat Network"
    BLOCKCHAIN_RPC_URL: str = "http://127.0.0.1:8545"
    BLOCKCHAIN_EXPLORER_URL: str = "https://amoy.polygonscan.com"
    BLOCKCHAIN_PRIVATE_KEY: Optional[str] = Field(default=None, description="Backend signer wallet private key")
    PRIVATE_KEY: str = Field(default="", description="Backend signer wallet private key fallback")
    CONTRACT_ADDRESS: str = Field(default="", description="Deployed ContentFingerprintRegistry address")
    
    # Upload & Security
    FRONTEND_ORIGIN: Optional[str] = Field(default=None, description="Frontend origin URL")
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000,*"
    MAX_UPLOAD_SIZE_MB: int = 10
    MIN_IMAGE_DIMENSION: int = 50
    MAX_IMAGE_DIMENSION: int = 8000
    ALLOWED_IMAGE_EXTENSIONS: str = "jpg,jpeg,png,webp"
    TEMP_UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_uploads")
    
    @property
    def active_search_provider(self) -> str:
        if self.REVERSE_SEARCH_PROVIDER is not None and self.REVERSE_SEARCH_PROVIDER.strip():
            return self.REVERSE_SEARCH_PROVIDER.strip().lower()
        return self.REVERSE_IMAGE_PROVIDER.strip().lower()

    @property
    def active_search_api_key(self) -> str:
        if self.REVERSE_SEARCH_API_KEY is not None and self.REVERSE_SEARCH_API_KEY.strip():
            return self.REVERSE_SEARCH_API_KEY.strip()
        return self.REVERSE_IMAGE_API_KEY.strip()

    @property
    def active_private_key(self) -> str:
        if self.BLOCKCHAIN_PRIVATE_KEY is not None and self.BLOCKCHAIN_PRIVATE_KEY.strip():
            return self.BLOCKCHAIN_PRIVATE_KEY.strip()
        return self.PRIVATE_KEY.strip()

    @property
    def cors_origins_list(self) -> List[str]:
        origins = [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        if self.FRONTEND_ORIGIN and self.FRONTEND_ORIGIN.strip():
            origins.append(self.FRONTEND_ORIGIN.strip())
        return list(set(origins))
        
    @property
    def allowed_extensions_set(self) -> set:
        return {ext.strip().lower() for ext in self.ALLOWED_IMAGE_EXTENSIONS.split(",") if ext.strip()}

settings = Settings()
