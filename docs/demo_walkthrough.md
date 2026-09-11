# Short Demonstration Walkthrough

Date: 2026-09-12
Duration target: 2 to 4 minutes

## Goal
Demonstrate all mandatory assignment behaviors:
- RAG destination guidance
- MCP weather tool
- MCP currency tool
- Combined RAG + MCP answer
- Multi-turn context retention

## Prerequisites

- `.env` is configured with `GOOGLE_API_KEY`, `GOOGLE_MODEL`, and `GOOGLE_EMBEDDING_MODEL`.
- The first run may build the vector store and can take longer than normal.

## Demo Steps

1. Open the app:
   - `streamlit run app.py`
2. Ask RAG-only question:
   - "What are the must-visit attractions in Singapore?"
3. Ask MCP weather question:
   - "What is the weather in Singapore for the next three days?"
4. Ask MCP currency question:
   - "Convert INR 50000 to SGD."
5. Ask combined question:
   - "Create a three-day Singapore itinerary for next week and adjust it according to the weather forecast."
6. Ask follow-up to verify context retention:
   - "Make day 2 more family friendly and reduce walking."

## What to Point Out While Demoing

- The response includes a `Live Data Used (MCP)` section when tools are used.
- The response includes a `Sources` section for knowledge-base grounding.
- Tool failure cases are surfaced as explicit limitations rather than fabricated facts.
- Follow-up answer preserves constraints from the previous turn.
- If `Sources` is empty for RAG prompts, explain that a one-time knowledge-base rebuild is required after quota reset.

## Validation Notes (already verified)

- Dependency check passed: `python -m pip check`
- MCP weather call passed
- MCP currency call passed
- UI formatter now appends MCP and source sections deterministically

## Evidence Files

- Questions: [docs/sample_questions.md](sample_questions.md)
- Responses: [docs/sample_responses.md](sample_responses.md)
- Requirements mapping: [docs/requirement_checklist.md](requirement_checklist.md)
