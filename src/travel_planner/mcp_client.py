from __future__ import annotations

import json
from pathlib import Path
import sys

from mcp import Client, StdioServerParameters
from mcp.types import TextContent


class TravelMCPClient:
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.weather_server = project_root / "mcp_servers" / "weather_server.py"
        self.currency_server = project_root / "mcp_servers" / "currency_server.py"

    async def list_weather_tools(self) -> list[str]:
        return await self._list_tools(self.weather_server)

    async def list_currency_tools(self) -> list[str]:
        return await self._list_tools(self.currency_server)

    async def get_weather(self, destination: str = "Singapore", days: int = 3) -> dict:
        return await self._call_tool(
            self.weather_server,
            "get_weather_forecast",
            {"destination": destination, "days": days},
        )

    async def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> dict:
        return await self._call_tool(
            self.currency_server,
            "convert_currency",
            {
                "amount": amount,
                "from_currency": from_currency,
                "to_currency": to_currency,
            },
        )

    async def _list_tools(self, server_script: Path) -> list[str]:
        params = StdioServerParameters(command=sys.executable, args=[str(server_script)])
        async with Client(params) as client:
            result = await client.list_tools()
            return [tool.name for tool in result.tools]

    async def _call_tool(self, server_script: Path, tool_name: str, arguments: dict) -> dict:
        params = StdioServerParameters(command=sys.executable, args=[str(server_script)])
        async with Client(params) as client:
            result = await client.call_tool(tool_name, arguments)
            text_parts = [block.text for block in result.content if isinstance(block, TextContent)]
            text_output = "\n".join(text_parts).strip()
            structured = result.structured_content
            if structured is None and text_output:
                try:
                    structured = json.loads(text_output)
                except json.JSONDecodeError:
                    structured = None

            ok = not result.is_error
            if isinstance(structured, dict) and "error" in structured:
                ok = False

            return {
                "tool": tool_name,
                "ok": ok,
                "data": structured,
                "text": text_output,
            }
