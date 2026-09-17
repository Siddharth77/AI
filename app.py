from __future__ import annotations

from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from src.travel_planner.assistant import TravelAssistant


load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent


@st.cache_resource
def get_assistant() -> TravelAssistant:
    return TravelAssistant(PROJECT_ROOT)


def render_sidebar() -> None:
    st.sidebar.title("AI Travel Planning Assistant")
    st.sidebar.caption("Singapore travel guidance demo")
    st.sidebar.markdown("### Included features")
    st.sidebar.markdown("- RAG over Singapore travel content")
    st.sidebar.markdown("- Live weather via MCP")
    st.sidebar.markdown("- Live currency conversion via MCP")
    st.sidebar.markdown("- Multi-turn travel planning chat")
    st.sidebar.markdown("### Demo prompts")
    for prompt in [
        "What are the must-visit attractions in Singapore?",
        "Suggest indoor attractions for a rainy day in Singapore.",
        "Convert INR 60000 to SGD.",
        "Create a three-day itinerary for Singapore and adjust it based on the weather forecast.",
    ]:
        st.sidebar.write(f"- {prompt}")


def build_response_markdown(response: dict) -> str:
    answer = response.get("answer", "")
    sections: list[str] = [answer]

    tool_outputs = response.get("tool_outputs", []) or []
    if tool_outputs:
        lines = ["### Live Data Used (MCP)"]
        for output in tool_outputs:
            tool_name = output.get("tool", "unknown_tool")
            ok = output.get("ok", False)
            readable = (output.get("text") or "").strip()
            status = "success" if ok else "failed"
            if readable:
                lines.append(f"- **{tool_name}** ({status}): {readable}")
            else:
                lines.append(f"- **{tool_name}** ({status})")
        sections.append("\n".join(lines))

    sources = response.get("sources", []) or []
    if sources:
        source_lines = ["### Sources"]
        for source in sources:
            title = source.get("title", "Source")
            url = source.get("url", "")
            if url:
                source_lines.append(f"- [{title}]({url})")
            else:
                source_lines.append(f"- {title}")
        sections.append("\n".join(source_lines))

    return "\n\n".join(section for section in sections if section.strip())


def format_runtime_error(exc: Exception) -> str:
    message = str(exc)
    lowered = message.lower()

    if "google_api_key" in lowered or "api key not valid" in lowered or "missing credentials" in lowered:
        return (
            "The app could not find a valid Google AI Studio API key. "
            "Please set `GOOGLE_API_KEY` in `.env`, then rerun the request."
        )

    if (
        "insufficient_quota" in lowered
        or "credit_balance_exhausted" in lowered
        or "no credits remaining" in lowered
        or "resource_exhausted" in lowered
        or "quota" in lowered
    ):
        return (
            "Google AI Studio quota is currently exhausted for this API key. "
            "Check quota/billing (or use a key with available quota) and try again. "
            "MCP weather and currency tools can still run, but final LLM-generated answers require available model quota."
        )

    if "rate limit" in lowered or "ratelimit" in lowered:
        return (
            "The language model request hit a rate limit. "
            "Please wait briefly and retry."
        )

    return f"The application could not complete the request. Details: {message}"


def main() -> None:
    st.set_page_config(page_title="AI Travel Planning Assistant", page_icon="🧭", layout="wide")
    render_sidebar()

    st.title("AI Travel Planning Assistant")
    st.caption("A simple demo for a Singapore travel planner using LangChain + MCP + RAG")

    assistant = get_assistant()

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Ask about attractions, budget conversion, weather-aware planning, or a Singapore itinerary. "
                    "Try one of the quick demo prompts below."
                ),
            }
        ]

    demo_prompts = [
        "What are the must-visit attractions in Singapore?",
        "Suggest indoor attractions for a rainy day in Singapore.",
        "Convert INR 60000 to SGD.",
        "Create a three-day itinerary for Singapore and adjust it based on the weather forecast.",
    ]

    st.markdown("### Quick demo prompts")
    demo_cols = st.columns(len(demo_prompts))
    for col, prompt in zip(demo_cols, demo_prompts):
        if col.button(prompt, use_container_width=True):
            st.session_state.pending_prompt = prompt

    if "pending_prompt" in st.session_state and st.session_state.pending_prompt:
        user_prompt = st.session_state.pending_prompt
        del st.session_state.pending_prompt
    else:
        user_prompt = st.chat_input("Ask a Singapore travel planning question")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if not user_prompt:
        if st.button("Rebuild knowledge base", use_container_width=False):
            with st.spinner("Rebuilding Singapore knowledge base..."):
                stats = assistant.ensure_knowledge_base(force_rebuild=True)
            st.success(f"Knowledge base ready with {stats['chunk_count']} chunks from {stats['source_count']} sources.")
        return

    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        with st.spinner("Planning your trip..."):
            try:
                response = assistant.answer_sync(user_prompt, st.session_state.messages[:-1])
            except Exception as exc:
                response_text = format_runtime_error(exc)
            else:
                response_text = build_response_markdown(response)

            st.markdown(response_text)

    st.session_state.messages.append({"role": "assistant", "content": response_text})


if __name__ == "__main__":
    main()
