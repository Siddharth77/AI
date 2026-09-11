# Assignment Requirement Checklist

Date checked: 2026-09-12

## Core Features and Acceptance Criteria

- [x] Knowledge base from at least three travel resources
  - Implemented in [src/travel_planner/source_catalog.py](../src/travel_planner/source_catalog.py) with 4 Singapore sources.
- [x] Embedding-based semantic retrieval
  - Implemented in [src/travel_planner/knowledge_base.py](../src/travel_planner/knowledge_base.py) using Google embeddings + Chroma.
- [x] Grounded answers with source references
  - Retrieval metadata includes title and URL.
  - UI now renders explicit source links from assistant output.
- [x] Weather information through an MCP tool
  - Implemented in [mcp_servers/weather_server.py](../mcp_servers/weather_server.py).
- [x] Currency conversion through an MCP tool
  - Implemented in [mcp_servers/currency_server.py](../mcp_servers/currency_server.py).
- [x] Combined response using RAG + MCP
  - Routing and composition implemented in [src/travel_planner/assistant.py](../src/travel_planner/assistant.py).
- [x] Multi-turn conversation with retained context
  - Implemented in Streamlit session state in [app.py](../app.py).
- [x] Appropriate tool selection based on user intent
  - Keyword-based routing implemented in [src/travel_planner/assistant.py](../src/travel_planner/assistant.py).
- [x] Clear handling of missing knowledge and tool failures
  - Prompt policy and tool-error fallback behavior implemented.
- [x] Simple, usable interface
  - Streamlit UI in [app.py](../app.py).

## Deliverables Status

- [x] Source code in repository
- [x] Working application (smoke-tested)
- [x] Knowledge base source instructions
  - Documented in [README.md](../README.md).
- [x] README with architecture, RAG, MCP, prompt and setup
  - Present in [README.md](../README.md).
- [x] Sample questions and application responses
  - Questions are present in [docs/sample_questions.md](./sample_questions.md).
  - Response artifact added in [docs/sample_responses.md](./sample_responses.md).
- [x] Short demonstration artifact
  - Walkthrough script/transcript added in [docs/demo_walkthrough.md](./demo_walkthrough.md).

## Recommended Final Steps Before Submission

1. For final grading, optionally replace the example RAG-heavy responses with live model outputs after setting `GOOGLE_API_KEY` in `.env`.
2. If your evaluator explicitly requires video format (instead of transcript), record the same sequence from [docs/demo_walkthrough.md](./demo_walkthrough.md).
3. Verify `.env` is excluded from commits and `.env.example` contains placeholders only (no real keys).

## Reviewer Understanding Guide

For a new reviewer, use this quick mapping:

1. Assignment requirement to evidence file
  - Requirements coverage: [docs/assignment_summary.md](./assignment_summary.md)
  - Acceptance checklist: [docs/requirement_checklist.md](./requirement_checklist.md)
  - Demo script: [docs/demo_walkthrough.md](./demo_walkthrough.md)
  - Sample prompts: [docs/sample_questions.md](./sample_questions.md)
  - Sample outputs: [docs/sample_responses.md](./sample_responses.md)

2. Runtime components
  - App entry point: [app.py](../app.py)
  - RAG and orchestration: [src/travel_planner/assistant.py](../src/travel_planner/assistant.py)
  - Knowledge base ingestion and retrieval: [src/travel_planner/knowledge_base.py](../src/travel_planner/knowledge_base.py)
  - MCP tool client: [src/travel_planner/mcp_client.py](../src/travel_planner/mcp_client.py)
  - Weather MCP server: [mcp_servers/weather_server.py](../mcp_servers/weather_server.py)
  - Currency MCP server: [mcp_servers/currency_server.py](../mcp_servers/currency_server.py)

3. What to verify in responses
  - `Live Data Used (MCP)` appears when weather/currency tools are invoked.
  - `Sources` appear for retrieval-grounded destination answers.
  - Missing key/quota errors are shown as clear user messages.

Interpretation note for reviewers:
- If `Sources` is empty for RAG prompts, the likely cause is an incomplete knowledge-base build due quota limits. Rebuild once after quota reset and re-check.
