# Civ6 RAG - Strategy Assistant

A RAG-based question-answering system for Civilization VI that combines data from the official wiki, Better Balanced Game mod, and YouTube strategy guides.

## 🚀 Quick Start

1. **Setup environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
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
