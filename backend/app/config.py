import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App Information
    APP_NAME: str = "ProofLink API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Biometric Face Matching Parameters
    FACE_DISTANCE_THRESHOLD: float = Field(default=0.60, description="Max Euclidean distance for face match (lower = stricter)")
    FACE_SIMILARITY_THRESHOLD: float = Field(default=0.70, description="Min Cosine similarity for face match (higher = stricter)")
    FACE_MIN_CONFIDENCE: float = Field(default=70.0, description="Min percentage confidence score required for blockchain notarization")
    FACE_DETECTION_MODEL: str = "ProofLink-SFace-128D"
    
    # Blockchain Settings (Polygon Amoy Testnet default, Ethereum Sepolia or Local RPC)
    CHAIN_ID: int = Field(default=80002, description="Polygon Amoy: 80002, Sepolia: 11155111, Hardhat: 31337")
    CHAIN_NAME: str = Field(default="Polygon Amoy Testnet", description="Network name")
    BLOCKCHAIN_RPC_URL: str = Field(default="https://rpc-amoy.polygon.technology", description="EVM RPC Node URL")
    BLOCKCHAIN_EXPLORER_URL: str = Field(default="https://amoy.polygonscan.com", description="Block Explorer URL")
    BLOCKCHAIN_PRIVATE_KEY: Optional[str] = Field(default=None, description="Backend testnet signer private key")
    PRIVATE_KEY: str = Field(default="", description="Fallback private key")
    CONTRACT_ADDRESS: str = Field(default="", description="Deployed ProofRegistry contract address")
    PROOF_REGISTRY_ADDRESS: str = Field(default="", description="Alias for ProofRegistry contract address")
    
    # Upload & Security Guardrails
    FRONTEND_ORIGIN: Optional[str] = Field(default=None, description="Frontend origin URL")
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000,*"
    MAX_UPLOAD_SIZE_MB: int = 10
    MIN_IMAGE_DIMENSION: int = 50
    MAX_IMAGE_DIMENSION: int = 8000
    ALLOWED_IMAGE_EXTENSIONS: str = "jpg,jpeg,png,webp"
    TEMP_UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_uploads")
    
    # URL Fetching limits & security
    URL_FETCH_TIMEOUT_SECONDS: int = 15
    MAX_URL_PAYLOAD_SIZE_MB: int = 15
    USER_AGENT: str = "ProofLink-Identity-Verification/1.0 (+https://prooflink.verification)"

    @property
    def active_private_key(self) -> str:
        if self.BLOCKCHAIN_PRIVATE_KEY is not None and self.BLOCKCHAIN_PRIVATE_KEY.strip():
            return self.BLOCKCHAIN_PRIVATE_KEY.strip()
        return self.PRIVATE_KEY.strip()

    @property
    def active_contract_address(self) -> str:
        if self.PROOF_REGISTRY_ADDRESS and self.PROOF_REGISTRY_ADDRESS.strip():
            return self.PROOF_REGISTRY_ADDRESS.strip()
        return self.CONTRACT_ADDRESS.strip()

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
