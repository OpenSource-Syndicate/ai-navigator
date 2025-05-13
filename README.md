# Ultimate AI

Ultimate AI is a modular, extensible API platform that leverages LLMs (Large Language Models) and web automation to analyze, summarize, and store information from web pages. It is built with FastAPI, SQLAlchemy, and integrates with Ollama for LLM-powered text generation.

## Features
- **Analyze Webpages:** Extracts and summarizes content from any URL using Selenium and LLMs.
- **Flexible LLM Integration:** Supports multiple model types (general, coding, reasoning, embedding) via Ollama.
- **Persistent Storage:** Saves learned information (topic, content, source) in a local SQLite database.
- **Modular Plugin System:** Easily extendable for new APIs or automation tasks.

## Project Structure
```
Ultimate-AI/
├── main.py                  # FastAPI app entry point
├── init_db.py               # Script to initialize the database
├── requirements.txt         # Python dependencies
├── pyproject.toml           # Project metadata
├── core/
│   ├── database/
│   │   ├── database.py      # SQLAlchemy setup
│   │   └── models.py        # ORM models
│   └── plugins/
│       ├── selenium_manager.py   # Web automation & scraping
│       └── apis/
│           └── ollama_client.py  # LLM API client
├── ultimate_ai.db           # SQLite database (auto-created)
└── .env                     # Model and API configuration
```

## Requirements
- Python 3.13+
- Chrome browser (for Selenium)
- [Ollama](https://ollama.com/) running locally (default: http://localhost:11434)

## Installation
1. **Clone the repository:**
   ```sh
   git clone <repo-url>
   cd Ultimate-AI
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Configure environment:**
   - Edit `.env` to set your LLM model names and API keys as needed.

4. **Initialize the database:**
   ```sh
   python init_db.py
   ```

5. **Run the API server:**
   ```sh
   uvicorn main:app --reload
   ```

## Usage
### Analyze a Webpage
Send a POST request to `/analyze-webpage` with a JSON body:
```json
{
  "url": "https://example.com",
  "context": "Summarize the main points."
}
```
**Response:**
```json
{
  "content": "...summary...",
  "source": "https://example.com"
}
```

### Generate Text with a Specific Model
POST `/generate/{model_type}` with query parameter `prompt`:
- `model_type`: one of `general`, `coding`, `embedding`, `reasoning`

Example:
```
POST /generate/reasoning?prompt=Explain+quantum+computing
```

## Extending
- Add new plugins in `core/plugins/` for additional automation or API integrations.
- Update `.env` to add or change LLM models.

## License
MIT License
