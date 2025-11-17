#!/usr/bin/env python3
"""
Create Project Structure Script
Automatically sets up the recommended folder structure for the Civ6 RAG project
"""

import os
from pathlib import Path


def create_directory_structure():
    """Create the complete directory structure"""
    
    print("🎮 Creating Civ6 RAG Project Structure...")
    print("="*60)
    
    base_dir = Path("civ6-rag")
    
    # Define the directory structure
    directories = [
        # Data directories
        "data/raw/civ6_wiki",
        "data/raw/bbg_wiki",
        "data/raw/youtube",
        "data/processed",
        "data/vector_db",
        
        # Source code directories
        "scrapers",
        "processors",
        "rag",
        "app/components",
        "app/utils",
        
        # Scripts and utilities
        "scripts/examples",
        
        # Tests
        "tests/fixtures",
        
        # Configuration
        "config/prompts",
        
        # Documentation
        "docs",
        
        # Optional
        "notebooks",
    ]
    
    # Create directories
    print("\n📁 Creating directories...")
    for directory in directories:
        dir_path = base_dir / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {directory}")
    
    print("\n✓ All directories created!")


def create_init_files():
    """Create __init__.py files for Python packages"""
    
    print("\n🐍 Creating __init__.py files...")
    
    base_dir = Path("civ6-rag")
    
    packages = [
        "scrapers",
        "processors",
        "rag",
        "app",
        "app/components",
        "app/utils",
        "config",
        "tests",
    ]
    
    for package in packages:
        init_file = base_dir / package / "__init__.py"
        init_file.touch(exist_ok=True)
        print(f"  ✓ {package}/__init__.py")
    
    print("\n✓ All __init__.py files created!")


def create_gitignore():
    """Create .gitignore file"""
    
    print("\n📝 Creating .gitignore...")
    
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Data
data/
*.json
*.csv
*.xlsx

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Jupyter
.ipynb_checkpoints/
*.ipynb

# ChromaDB
chroma/
*.db
*.sqlite3

# Logs
*.log
logs/
"""
    
    gitignore_path = Path("civ6-rag") / ".gitignore"
    gitignore_path.write_text(gitignore_content, encoding='utf-8')
    print("  ✓ .gitignore created")


def create_env_example():
    """Create .env.example file"""
    
    print("\n🔐 Creating .env.example...")
    
    env_content = """# LLM API Keys
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Embedding Configuration
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_PROVIDER=openai

# LLM Configuration
LLM_MODEL=gpt-4
LLM_PROVIDER=openai
LLM_TEMPERATURE=0.7
MAX_TOKENS=2000

# Scraper Settings
SCRAPER_DELAY=1
MAX_RETRIES=3
TIMEOUT=30

# Vector Database Settings
CHROMA_PERSIST_DIR=./data/vector_db/chroma
COLLECTION_NAME=civ6_knowledge

# RAG Settings
CHUNK_SIZE=800
CHUNK_OVERLAP=100
TOP_K_RESULTS=5

# App Settings
APP_TITLE=Civ6 Strategy Assistant
APP_ICON=🎮
MAX_HISTORY=10
ENABLE_STREAMING=true
"""
    
    env_path = Path("civ6-rag") / ".env.example"
    env_path.write_text(env_content, encoding='utf-8')
    print("  ✓ .env.example created")
    print("  ⚠️  Don't forget to copy .env.example to .env and add your API keys!")


def create_config_file():
    """Create main configuration file"""
    
    print("\n⚙️  Creating config/settings.py...")
    
    config_content = '''"""
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
'''
    
    config_path = Path("civ6-rag") / "config" / "settings.py"
    config_path.write_text(config_content, encoding='utf-8')
    print("  ✓ config/settings.py created")


def create_readme():
    """Create a basic README"""
    
    print("\n📖 Creating README.md...")
    
    readme_content = """# Civ6 RAG - Strategy Assistant

A RAG-based question-answering system for Civilization VI that combines data from the official wiki, Better Balanced Game mod, and YouTube strategy guides.

## 🚀 Quick Start

1. **Setup environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

3. **Collect data:**
   ```bash
   python scripts/scrape_all.py
   python scripts/process_all.py
   python scripts/build_vector_db.py
   ```

4. **Run the app:**
   ```bash
   streamlit run app/main.py
   ```

## 📂 Project Structure

See `docs/PROJECT_STRUCTURE.md` for detailed structure explanation.

## 📚 Documentation

- [Getting Started](docs/GETTING_STARTED.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Project Structure](docs/PROJECT_STRUCTURE.md)

## 🎮 Features

- Query Civ6 strategies across multiple sources
- Filter by mod (vanilla vs BBG)
- Filter by expansion (base game, Rise & Fall, Gathering Storm)
- Source attribution for all answers
- Chat-based interface

## 🛠️ Tech Stack

- **Scraping:** BeautifulSoup, Requests
- **RAG:** LangChain, ChromaDB
- **LLM:** OpenAI GPT-4 or Anthropic Claude
- **Frontend:** Streamlit

## 📝 License

Personal project for educational purposes.
"""
    
    readme_path = Path("civ6-rag") / "README.md"
    readme_path.write_text(readme_content, encoding='utf-8')
    print("  ✓ README.md created")


def move_existing_files():
    """Move existing files to appropriate locations"""
    
    print("\n📦 Moving existing files...")
    
    base_dir = Path("civ6-rag")
    
    file_mappings = {
        "civ6_wiki_scraper.py": "scrapers/civ6_wiki_scraper.py",
        "civ6_rag_processor.py": "processors/rag_processor.py",
        "example_workflow.py": "scripts/examples/example_workflow.py",
        "requirements.txt": "requirements.txt",
        "setup.sh": "scripts/setup.sh",
        "ARCHITECTURE.md": "docs/ARCHITECTURE.md",
        "GETTING_STARTED.md": "docs/GETTING_STARTED.md",
        "PROJECT_STRUCTURE.md": "docs/PROJECT_STRUCTURE.md",
    }
    
    current_dir = Path(".")
    
    for source, destination in file_mappings.items():
        source_path = current_dir / source
        dest_path = base_dir / destination
        
        if source_path.exists():
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Read and write (to handle cross-directory moves)
            content = source_path.read_text(encoding='utf-8')
            dest_path.write_text(content, encoding='utf-8')
            print(f"  ✓ Moved {source} → {destination}")
        else:
            print(f"  ⚠️  {source} not found, skipping")


def create_placeholder_files():
    """Create placeholder files for future implementation"""
    
    print("\n📄 Creating placeholder files...")
    
    base_dir = Path("civ6-rag")
    
    placeholders = {
        "scrapers/bbg_wiki_scraper.py": '''"""
BBG Wiki Scraper
TODO: Implement scraper for Better Balanced Game wiki
"""

from scrapers.civ6_wiki_scraper import Civ6WikiScraper


class BBGWikiScraper(Civ6WikiScraper):
    """Scraper for BBG wiki - to be implemented"""
    
    def __init__(self):
        # Update with actual BBG wiki URL
        super().__init__(base_url="https://bbg.civfanatics.com")
    
    # TODO: Implement BBG-specific scraping methods
''',
        
        "scrapers/youtube_scraper.py": '''"""
YouTube Transcript Scraper
TODO: Implement YouTube transcript scraper
"""

# Example: pip install youtube-transcript-api

class YouTubeScraper:
    """Scraper for YouTube video transcripts - to be implemented"""
    
    def __init__(self):
        pass
    
    # TODO: Implement transcript extraction
    # from youtube_transcript_api import YouTubeTranscriptApi
''',
        
        "rag/vector_store.py": '''"""
Vector Store Wrapper
TODO: Implement ChromaDB wrapper
"""

import chromadb


class VectorStore:
    """Wrapper for ChromaDB - to be implemented"""
    
    def __init__(self, persist_directory: str, collection_name: str):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
    
    # TODO: Implement vector store methods
''',
        
        "app/main.py": '''"""
Streamlit Main App
TODO: Implement Streamlit frontend
"""

import streamlit as st

def main():
    st.title("🎮 Civ6 Strategy Assistant")
    st.write("Coming soon!")

if __name__ == "__main__":
    main()
''',
    }
    
    for filepath, content in placeholders.items():
        file_path = base_dir / filepath
        file_path.write_text(content, encoding='utf-8')
        print(f"  ✓ {filepath}")


def print_next_steps():
    """Print next steps for the user"""
    
    print("\n" + "="*60)
    print("✅ Project structure created successfully!")
    print("="*60)
    
    print("\n📋 Next Steps:")
    print("\n1. Navigate to project directory:")
    print("   cd civ6-rag")
    
    print("\n2. Set up Python environment:")
    print("   python3 -m venv venv")
    print("   source venv/bin/activate")
    print("   pip install -r requirements.txt")
    
    print("\n3. Configure environment variables:")
    print("   cp .env.example .env")
    print("   # Edit .env and add your API keys")
    
    print("\n4. Start collecting data:")
    print("   python scripts/examples/example_workflow.py")
    
    print("\n📁 Project created at: ./civ6-rag/")
    print("\n🎮 Happy coding!")


def main():
    """Main function to create the project structure"""
    
    try:
        create_directory_structure()
        create_init_files()
        create_gitignore()
        create_env_example()
        create_config_file()
        create_readme()
        create_placeholder_files()
        move_existing_files()
        print_next_steps()
        
    except Exception as e:
        print(f"\n❌ Error creating project structure: {e}")
        raise


if __name__ == "__main__":
    main()