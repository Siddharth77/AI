from __future__ import annotations

import asyncio
import os
import re
from pathlib import Path

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from .knowledge_base import TravelKnowledgeBase, collect_source_references, format_retrieved_documents
from .mcp_client import TravelMCPClient
from .prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE


CURRENCY_ALIASES = {
    "sgd": "SGD",
    "singapore dollar": "SGD",
    "singapore dollars": "SGD",
    "inr": "INR",
    "rupee": "INR",
    "rupees": "INR",
    "indian rupee": "INR",
    "indian rupees": "INR",
    "usd": "USD",
    "us dollar": "USD",
    "us dollars": "USD",
    "dollar": "USD",
    "dollars": "USD",
}


class TravelAssistant:
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.knowledge_base = TravelKnowledgeBase(project_root)
        self.mcp_client = TravelMCPClient(project_root)
        self.model_name = os.getenv("GOOGLE_MODEL", "gemini-3.6-flash")

    def ensure_knowledge_base(self, force_rebuild: bool = False) -> dict[str, int]:
        self._require_api_key()
        return self.knowledge_base.ensure_ready(force_rebuild=force_rebuild)

    def answer_sync(self, question: str, history: list[dict[str, str]]) -> dict:
        return asyncio.run(self.answer(question, history))

    async def answer(self, question: str, history: list[dict[str, str]]) -> dict:
        self._require_api_key()
        self.knowledge_base.ensure_ready()

        needs_weather = self._needs_weather(question)
        needs_currency = self._needs_currency(question)
        needs_destination_knowledge = self._needs_destination_knowledge(question) or not (needs_weather or needs_currency)

        documents = self.knowledge_base.retrieve(question) if needs_destination_knowledge else []
        knowledge_context = format_retrieved_documents(documents)
        source_references = collect_source_references(documents)

        tool_outputs: list[dict] = []
        if needs_weather:
            tool_outputs.append(await self.mcp_client.get_weather())

        if needs_currency:
            parsed_budget = self._extract_currency_request(question)
            if parsed_budget is None:
                tool_outputs.append(
                    {
                        "tool": "convert_currency",
                        "ok": False,
                        "data": None,
                        "text": "Could not determine the amount and currency pair from the user's question.",
                    }
                )
            else:
                tool_outputs.append(
                    await self.mcp_client.convert_currency(
                        parsed_budget["amount"],
                        parsed_budget["from_currency"],
                        parsed_budget["to_currency"],
                    )
                )

        tool_context = self._format_tool_outputs(tool_outputs)
        answer = self._generate_answer(question, history, knowledge_context, tool_context)

        return {
            "answer": answer,
            "sources": source_references,
            "tool_outputs": tool_outputs,
        }

    def _generate_answer(
        self,
        question: str,
        history: list[dict[str, str]],
        knowledge_context: str,
        tool_context: str,
    ) -> str:
        llm = ChatGoogleGenerativeAI(model=self.model_name, temperature=0.2)
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                ("human", USER_PROMPT_TEMPLATE),
            ]
        )
        chain = prompt | llm | StrOutputParser()
        history_text = self._format_history(history)
        return chain.invoke(
            {
                "history": history_text,
                "question": question,
                "knowledge_context": knowledge_context,
                "tool_context": tool_context,
            }
        )

    @staticmethod
    def _format_history(history: list[dict[str, str]]) -> str:
        if not history:
            return "No previous conversation."
        relevant_turns = history[-6:]
        return "\n".join(f"{item['role']}: {item['content']}" for item in relevant_turns)

    @staticmethod
    def _format_tool_outputs(tool_outputs: list[dict]) -> str:
        if not tool_outputs:
            return "No MCP tool output used."
        formatted = []
        for tool_output in tool_outputs:
            formatted.append(
                f"Tool: {tool_output['tool']}\n"
                f"Success: {tool_output['ok']}\n"
                f"Structured data: {tool_output['data']}\n"
                f"Readable output: {tool_output['text']}"
            )
        return "\n\n".join(formatted)

    @staticmethod
    def _needs_weather(question: str) -> bool:
        keywords = ["weather", "forecast", "rain", "temperature", "tomorrow", "next week"]
        lowered = question.lower()
        return any(keyword in lowered for keyword in keywords)

    @staticmethod
    def _needs_currency(question: str) -> bool:
        keywords = ["convert", "currency", "budget", "sgd", "inr", "usd"]
        lowered = question.lower()
        return any(keyword in lowered for keyword in keywords)

    @staticmethod
    def _needs_destination_knowledge(question: str) -> bool:
        keywords = [
            "itinerary",
            "attractions",
            "neighbourhood",
            "neighborhood",
            "transport",
            "food",
            "family",
            "indoor",
            "outdoor",
            "singapore",
            "trip",
            "plan",
        ]
        lowered = question.lower()
        return any(keyword in lowered for keyword in keywords)

    @classmethod
    def _extract_currency_request(cls, question: str) -> dict[str, str | float] | None:
        compact = question.lower().replace(",", "")
        match = re.search(r"(\d+(?:\.\d+)?)\s*([a-zA-Z ]+?)\s+(?:to|in)\s+([a-zA-Z ]+)", compact)
        if not match:
            match = re.search(r"([a-zA-Z ]+)\s*(\d+(?:\.\d+)?)\s+(?:to|in)\s+([a-zA-Z ]+)", compact)
            if not match:
                return None
            left_currency = cls._normalize_currency(match.group(1))
            amount = float(match.group(2))
            right_currency = cls._normalize_currency(match.group(3))
        else:
            amount = float(match.group(1))
            left_currency = cls._normalize_currency(match.group(2))
            right_currency = cls._normalize_currency(match.group(3))

        if left_currency is None or right_currency is None:
            currency_mentions = [
                cls._normalize_currency(token)
                for token in re.findall(r"[a-zA-Z]{3}|singapore dollars?|indian rupees?|us dollars?", compact)
            ]
            currency_mentions = [token for token in currency_mentions if token is not None]
            if len(currency_mentions) >= 2:
                left_currency = currency_mentions[0]
                right_currency = currency_mentions[1]

        if left_currency is None or right_currency is None:
            return None

        return {
            "amount": amount,
            "from_currency": left_currency,
            "to_currency": right_currency,
        }

    @staticmethod
    def _normalize_currency(raw_value: str) -> str | None:
        value = raw_value.strip().lower()
        value = re.sub(r"\bmy travel budget from\b", "", value).strip()
        value = re.sub(r"\bhow much is\b", "", value).strip()
        if value in CURRENCY_ALIASES:
            return CURRENCY_ALIASES[value]
        if len(value) == 3 and value.upper() in {"SGD", "INR", "USD"}:
            return value.upper()
        return None

    @staticmethod
    def _require_api_key() -> None:
        if not os.getenv("GOOGLE_API_KEY"):
            raise RuntimeError("GOOGLE_API_KEY is not set. Update .env before running the app.")
