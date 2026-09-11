from __future__ import annotations

import httpx
from mcp.server import MCPServer


mcp = MCPServer("travel-currency")


SUPPORTED_CURRENCIES = {"SGD", "INR", "USD"}


@mcp.tool(title="Convert travel budget between currencies")
def convert_currency(amount: float, from_currency: str, to_currency: str) -> dict:
    """Convert a currency amount using live exchange rates."""
    from_currency = from_currency.upper().strip()
    to_currency = to_currency.upper().strip()

    if from_currency not in SUPPORTED_CURRENCIES or to_currency not in SUPPORTED_CURRENCIES:
        return {
            "error": "This assignment implementation supports SGD, INR, and USD conversions only."
        }

    try:
        response = httpx.get(
            "https://api.frankfurter.app/latest",
            params={"amount": amount, "from": from_currency, "to": to_currency},
            follow_redirects=True,
            timeout=30.0,
        )
        response.raise_for_status()
    except Exception as exc:
        return {"error": f"Currency service unavailable: {exc}"}

    payload = response.json()
    converted_amount = payload.get("rates", {}).get(to_currency)
    if converted_amount is None:
        return {"error": "Conversion result was missing from the currency service response."}

    return {
        "amount": amount,
        "from_currency": from_currency,
        "to_currency": to_currency,
        "converted_amount": converted_amount,
        "rate_date": payload.get("date"),
        "source": "Frankfurter",
    }


if __name__ == "__main__":
    mcp.run()