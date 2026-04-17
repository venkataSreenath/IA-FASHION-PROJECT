# Intelligent Fashion Recommender (Backend)

This project is a backend-first implementation of an intelligent, context-aware fashion recommendation agent.

It uses:
- LangChain + **OpenRouter** (e.g. `Gemini 2.5 Flash`) for LLM reasoning
- WeatherAPI for real-time weather context
- Tavily API for current trend context
- ChromaDB for outfit retrieval (vector memory)
- SQLite for user dislike memory (learning loop)

## Project Structure

- `database_sqlite.py` - user dislike memory storage
- `database_chroma.py` - local outfit vector store + similarity search
- `tools.py` - LangChain tools (weather, trends, retrieval)
- `agent_logic.py` - OpenRouter-backed tool-calling agent and system prompt
- `main_terminal.py` - terminal execution pipeline with feedback loop
- `.env.example` - environment variable template

## 1) Setup

### Prerequisites

- Python 3.10+ recommended
- API keys (external tools):
  - OpenRouter API key
  - WeatherAPI key
  - Tavily API key

### Install dependencies

```bash
pip install -r requirements.txt
```

## 2) Configure Environment Variables

Copy `.env.example` values into `.env` and fill your real keys:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=google/gemini-2.5-flash
WEATHERAPI_KEY=your_weatherapi_key
TAVILY_API_KEY=your_tavily_key
```

## 3) Run the Backend Pipeline

```bash
python main_terminal.py
```

Then:
1. Enter `user_id`
2. Enter fashion query (occasion/place/time style prompt)
3. See final recommendation + reasoning/tool trace
4. Enter `Like` or `Dislike`
5. If `Dislike`, enter disliked features (comma-separated)

Type `exit` to stop.

## 4) Quick Example Query

Try:

`I have a dinner in Kochi tonight. Suggest a smart casual outfit.`

Dislike example features:

`dark colors, leather loafers, heavy fabrics`

## 5) How Learning Works

- Disliked features are saved in SQLite per user.
- On future queries, those disliked features are injected into the agent prompt.
- The retrieval/reasoning flow filters out matching outfit traits.

## 6) Troubleshooting

- **OpenRouter connection errors**
  - Verify your `OPENROUTER_API_KEY` and confirm billing status.
- **Missing API key error** (weather / Tavily)
  - Check `.env` values and restart terminal.
- **No trends/weather returned**
  - Verify internet connection and API quotas.
- **Chroma retrieval issues**
  - Delete `chroma_db` folder and rerun to reseed dummy items.

## 7) Next Suggested Phase

- Build Streamlit frontend (`main.py`) with:
  - text input
  - recommendation cards
  - Like/Dislike buttons
  - callback to SQLite update

