"""
Configuration Settings
Central configuration for the Civ6 RAG system
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
VECTOR_DB_DIR = DATA_DIR / "vector_db"

# LLM Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))

# Embedding Configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "openai")

# Scraper Configuration
SCRAPER_DELAY = int(os.getenv("SCRAPER_DELAY", "1"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
TIMEOUT = int(os.getenv("TIMEOUT", "30"))

# URLs
CIV6_WIKI_BASE = "https://civilization.fandom.com"
BBG_WIKI_BASE = "https://bbg.civfanatics.com"  # Update with actual URL

# RAG Configuration
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "5"))

# Vector DB Configuration
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", str(VECTOR_DB_DIR / "chroma"))
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "civ6_knowledge")

# App Configuration
APP_TITLE = os.getenv("APP_TITLE", "Civ6 Strategy Assistant")
APP_ICON = os.getenv("APP_ICON", "🎮")
MAX_HISTORY = int(os.getenv("MAX_HISTORY", "10"))
ENABLE_STREAMING = os.getenv("ENABLE_STREAMING", "true").lower() == "true"

# Data Sources
DATA_SOURCES = {
    "civ6_wiki": {
        "name": "Civilization VI Wiki",
        "base_url": CIV6_WIKI_BASE,
        "categories": [
            "civilizations",
            "leaders",
            "units",
            "buildings",
            "wonders",
            "districts",
            "improvements",
            "game_concepts",
        ]
    },
    "bbg_wiki": {
        "name": "Better Balanced Game Wiki",
        "base_url": BBG_WIKI_BASE,
        "enabled": False,  # Enable when implemented
    },
    "youtube": {
        "name": "YouTube Strategy Guides",
        "enabled": False,  # Enable when implemented
    }
}
