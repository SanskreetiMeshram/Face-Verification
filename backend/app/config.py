import os
from typing import List
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
    
    # Reverse Search Configuration
    REVERSE_IMAGE_PROVIDER: str = Field(default="serpapi", description="Provider: serpapi, bing, rapidapi, tineye, searxng, demo")
    REVERSE_IMAGE_API_KEY: str = Field(default="", description="API key for the reverse search provider")
    SERPAPI_ENGINE: str = "google_lens"
    BING_ENDPOINT: str = "https://api.bing.microsoft.com/v7.0/images/visualsearch"
    RAPIDAPI_HOST: str = "google-lens-reverse-image-search.p.rapidapi.com"
    SEARXNG_URL: str = "http://localhost:8080"
    ALLOW_DEMO_FALLBACK: bool = True
    
    # Blockchain Settings (Polygon Amoy Testnet default)
    CHAIN_ID: int = 80002
    CHAIN_NAME: str = "Polygon Amoy Testnet"
    BLOCKCHAIN_RPC_URL: str = "https://rpc-amoy.polygon.technology/"
    BLOCKCHAIN_EXPLORER_URL: str = "https://amoy.polygonscan.com"
    PRIVATE_KEY: str = Field(default="", description="Backend signer wallet private key")
    CONTRACT_ADDRESS: str = Field(default="", description="Deployed FaceMatchRegistry address")
    
    # Upload & Security
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000,*"
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_IMAGE_EXTENSIONS: str = "jpg,jpeg,png,webp"
    TEMP_UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_uploads")
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        
    @property
    def allowed_extensions_set(self) -> set:
        return {ext.strip().lower() for ext in self.ALLOWED_IMAGE_EXTENSIONS.split(",") if ext.strip()}

settings = Settings()
