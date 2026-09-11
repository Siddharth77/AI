from __future__ import annotations

import httpx
from mcp.server import MCPServer


mcp = MCPServer("travel-weather")


WEATHER_CODE_DESCRIPTIONS = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snowfall",
    80: "Rain showers",
    95: "Thunderstorm",
}


@mcp.tool(title="Get Singapore weather forecast")
def get_weather_forecast(destination: str = "Singapore", days: int = 3) -> dict:
    """Return a short weather forecast for Singapore."""
    if destination.strip().lower() != "singapore":
        return {
            "error": "This assignment implementation only supports Singapore as the destination."
        }

    try:
        response = httpx.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": 1.3521,
                "longitude": 103.8198,
                "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
                "timezone": "Asia/Singapore",
                "forecast_days": max(1, min(days, 7)),
            },
            timeout=30.0,
        )
        response.raise_for_status()
    except Exception as exc:
        return {"error": f"Weather service unavailable: {exc}"}

    payload = response.json()
    daily = payload.get("daily", {})
    forecast = []
    for date, weather_code, temp_max, temp_min, rain_probability in zip(
        daily.get("time", []),
        daily.get("weather_code", []),
        daily.get("temperature_2m_max", []),
        daily.get("temperature_2m_min", []),
        daily.get("precipitation_probability_max", []),
    ):
        forecast.append(
            {
                "date": date,
                "condition": WEATHER_CODE_DESCRIPTIONS.get(weather_code, "Unknown"),
                "temperature_max_c": temp_max,
                "temperature_min_c": temp_min,
                "precipitation_probability_max": rain_probability,
            }
        )

    return {
        "destination": "Singapore",
        "source": "Open-Meteo",
        "forecast": forecast,
    }


if __name__ == "__main__":
    mcp.run()
