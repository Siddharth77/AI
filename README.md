# AI Travel Planning Assistant

A Python implementation of the AI Travel Planning Assistant assignment for Singapore. The application combines a Retrieval-Augmented Generation knowledge base with two custom MCP tools for weather and currency conversion.

## What this project does

- Answers destination questions about Singapore using RAG over public travel sources.
- Uses custom MCP tools for live weather and currency conversion.
- Produces combined answers when a prompt needs both stable destination facts and live data.
- Retains conversation context across turns inside the Streamlit session.
- Shows the source links used for knowledge-base facts and clearly labels MCP-derived data.

## Architecture

1. Knowledge base
   - Public Singapore travel sources are fetched from the web.
   - Content is cleaned, chunked, embedded, and stored in Chroma.
   - Relevant chunks are retrieved for each destination-aware query.
2. MCP tools
   - `mcp_servers/weather_server.py` calls Open-Meteo for a 3-day forecast.
   - `mcp_servers/currency_server.py` calls Frankfurter for exchange rates.
   - The app launches both servers over stdio using the official Python MCP client.
3. Response generation
   - LangChain prompt templates combine chat history, retrieved source excerpts, and MCP tool outputs.
   - The final answer separates destination facts, live data, and AI suggestions.
4. Interface
   - Streamlit provides a simple multi-turn chat UI with a rebuild button and starter prompts.

## Knowledge-base sources

- Wikivoyage Singapore Travel Guide
- Visit Singapore: Essential Travel Information
- Visit Singapore: Itineraries
- Visit Singapore: Top Things To Do

The app stores each source title and URL as metadata so citations remain visible in answers.

## Prompt strategy

The prompts instruct the model to:

- use retrieved context for destination facts only
- use MCP outputs for current weather and currency data only
- avoid unsupported claims
- state when information is missing or a tool is unavailable
- preserve relevant user preferences from the conversation
- output structured travel recommendations in markdown

## Setup

1. Create and activate a virtual environment.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Configure environment variables.

```bash
cp .env.example .env
```

Set the following in `.env`:

```env
GOOGLE_API_KEY=your_key_here
GOOGLE_MODEL=gemini-3.6-flash
GOOGLE_EMBEDDING_MODEL=models/gemini-embedding-001
```

Important: keep real credentials only in `.env`. The `.env.example` file must contain placeholders only.

4. Run the app.

```bash
streamlit run app.py
```

On first use, the application builds the vector store automatically.

## Quick verification for a new reviewer

Use this sequence if you are reviewing the assignment for the first time.

1. Start the app.

```bash
streamlit run app.py
```

2. Run these prompts in order:
   - Convert INR 50000 to SGD.
   - What are the must-visit attractions in Singapore?
   - Create a three-day Singapore itinerary for next week and adjust it according to the weather forecast.
   - Make day 2 more family friendly and reduce walking.

3. Confirm expected behavior:
   - MCP-only prompt shows a `Live Data Used (MCP)` section with currency tool output.
   - RAG prompt returns Singapore recommendations based on knowledge-base content.
   - Combined prompt uses weather tool output and gives a day-wise weather-aware plan.
   - Follow-up prompt reflects prior user constraints (family-friendly, less walking).

4. Confirm grounding and transparency:
   - Responses show sources when retrieval is available.
   - If quota or key issues occur, the app shows a clear user-facing setup/quota message instead of a crash.
   - If `Sources` is empty for RAG prompts, run one knowledge-base rebuild after quota reset and retry.

If quota is temporarily exhausted, retry after the quota window resets. Avoid pressing "Rebuild knowledge base" repeatedly during free-tier evaluation.

## Suggested demo flow

1. Ask a RAG-only question.
   - `What are the must-visit attractions in Singapore?`
2. Ask an MCP-only question.
   - `Convert INR 50000 to SGD.`
3. Ask a combined question.
   - `Create a three-day Singapore itinerary for next week and adjust it according to the weather forecast.`
4. Ask a follow-up.
   - `Make it more family friendly and keep the budget in SGD.`

## Sample questions

See `docs/sample_questions.md` for a set of prompts mapped to the assignment objectives.

## MCP configuration file

- `.vscode/mcp.json` is required in this project submission to expose the local MCP servers in a standard VS Code MCP setup.

## Project structure

```text
app.py
mcp_servers/
src/travel_planner/
docs/
.vscode/mcp.json
```

## Notes for evaluation

- The destination scope is intentionally limited to Singapore, which is allowed by the assignment.
- Weather uses Open-Meteo and currency uses Frankfurter, both accessed through local MCP servers.
- If `GOOGLE_API_KEY` is missing, the UI reports the setup problem instead of failing silently.
- If Google AI Studio quota is exhausted, MCP-only questions still work, while RAG/LLM generation will fail until quota is available.
