# Assignment Summary

## Objective

Build an AI Travel Planning Assistant for one destination that combines:

- RAG for stable travel knowledge
- MCP tools for live weather and currency conversion
- a combined response that uses both sources when needed
- a simple UI and multi-turn conversation memory

## Scope chosen here

- Destination: Singapore
- UI: Streamlit
- RAG stack: LangChain + Google embeddings + Chroma
- MCP stack: Official Python MCP SDK over stdio
- MCP tools: weather and currency conversion

## Acceptance criteria mapping

- Knowledge base from at least three resources: covered with four public sources
- Embedding retrieval: covered with Chroma semantic search
- Grounded answers with citations: covered through source metadata in the prompt and response
- Weather through MCP: covered by local weather MCP server
- Currency through MCP: covered by local currency MCP server
- Combined response: covered by itinerary + forecast flow
- Multi-turn context: covered by Streamlit session history
- Tool selection: covered by intent routing in the assistant
- Tool failure handling: covered by structured fallback messages
- Usable interface: covered by chat UI and rebuild control

## Deep-thought design notes

1. Keep the destination fixed to Singapore because the assignment allows a single-destination implementation and that reduces prompt and retrieval ambiguity.
2. Keep MCP tools as local servers even though the underlying data comes from public APIs. This satisfies the assignment requirement to use MCP-compatible tools while keeping setup manageable.
3. Route queries conservatively. Destination facts come from retrieval. Live data comes from tools. Combined questions use both.
4. Preserve source URLs in metadata so the final answer can show evidence without exposing raw chunks.
5. Fail clearly. If retrieval is weak or a tool call fails, say so instead of filling gaps with guesses.

## Best-practice guidance for beginners

- Separate stable facts from live data. That is the key architectural idea in this assignment.
- Start with a narrow destination scope so you can prove the workflow end to end.
- Use metadata early. Source title and URL are not optional if you want trustworthy citations.
- Validate the MCP boundary independently before debugging prompts.
- Keep the UI simple. The assignment values AI workflow quality more than front-end complexity.
