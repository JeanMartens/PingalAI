#!/bin/bash
# Civ6 RAG - Quick Setup Script

echo "🎮 Civilization VI RAG System - Setup 🎮"
echo "========================================"
echo ""


conda activate civ6_rag_env

echo "2. Installing dependencies..."
pip install -r requirements.txt

# Create data directories
echo "3. Creating data directories..."
mkdir -p data/raw
mkdir -p data/processed

echo ""
echo "✓ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run example workflow: python example_workflow.py"
echo "  3. Or start scraping: python civ6_wiki_scraper.py"
echo ""
echo "Happy coding! 🚀"