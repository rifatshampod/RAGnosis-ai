import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY: str = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct:free")

CHROMA_HOST: str = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT: int = int(os.getenv("CHROMA_PORT", "8000"))
COLLECTION_NAME: str = "ragnosis_v1"

TOP_K: int = int(os.getenv("TOP_K", "5"))
EMBED_MODEL: str = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")

PROCESSED_DIR: Path = Path(os.getenv("PROCESSED_DIR", "data/processed"))
CHUNKS_DIR: Path = Path(os.getenv("CHUNKS_DIR", "data/chunks"))

MAX_CHUNK_TOKENS: int = 600
OVERLAP_TOKENS: int = 50
RELEVANCE_THRESHOLD: float = 0.75
