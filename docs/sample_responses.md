# Sample Questions and Responses

Date captured: 2026-09-12

This file contains assignment-aligned sample responses gathered from the implemented flow.

## Scenario 1: MCP Weather Only

### Question
What is the weather in Singapore for the next day?

### Tool used
- `get_weather_forecast` from weather MCP server

### Captured result summary
- Tool status: success
- Source: Open-Meteo
- Forecast includes condition, max/min temperature, and precipitation probability

### Example response (application format)
## Answer
Singapore's near-term forecast is available and can be used to plan indoor or outdoor activities.

### Live Data Used (MCP)
- get_weather_forecast (success): structured forecast returned from Open-Meteo for Singapore.

### Suggested Plan
If precipitation probability is high, prioritize indoor attractions for that day and shift outdoor activities to clearer windows.

### Sources
- MCP Weather Tool (Open-Meteo)

## Scenario 2: MCP Currency Only

### Question
Convert INR 50000 to SGD.

### Tool used
- `convert_currency` from currency MCP server

### Captured result
- Tool status: success
- Validated tool output example:
  - amount: 1000 INR
  - converted_amount: 13.2683 SGD
  - rate_date: 2026-09-11
  - source: Frankfurter
- Approximation for this question amount (50000 INR) using the same sampled rate:
  - about 663.415 SGD

### Example response (application format)
## Answer
Currency conversion completed successfully.

### Live Data Used (MCP)
- convert_currency (success): sampled run returned 1000.0 INR to SGD = 13.2683 (rate date: 2026-09-11). For 50000 INR, the approximate value is 663.415 SGD at that sampled rate.

### Suggested Plan
Use this conversion rate to set your SGD budget bands for transport, attractions, and food.

### Sources
- MCP Currency Tool (Frankfurter)

## Scenario 3: RAG Only

### Question
What are the must-visit attractions in Singapore?

### Knowledge source path
- RAG retrieval from the Singapore knowledge base built from:
  - Wikivoyage Singapore Travel Guide
  - Visit Singapore Essential Travel Information
  - Visit Singapore Itineraries
  - Visit Singapore Top Things To Do

### Example response (application format)
## Answer
Top attractions in Singapore generally include Marina Bay, Gardens by the Bay, Sentosa, Chinatown, Little India, and key cultural districts, with options for both family and solo travel.

### Suggested Plan
Start with central attractions on day 1, culture-focused neighborhoods on day 2, and Sentosa or indoor attractions on day 3.

### Sources
- Wikivoyage Singapore Travel Guide
- Visit Singapore resources listed above

## Scenario 4: Combined RAG + MCP

### Question
Create a three-day Singapore itinerary for next week and adjust it according to the weather forecast.

### Expected orchestration
- RAG retrieves attraction, transport, indoor/outdoor ideas, and itinerary structure.
- MCP weather provides current forecast.
- Final response presents day-wise plan with rain-aware substitutions.

### Example response (application format)
## Answer
Here is a weather-aware three-day Singapore itinerary.

### Live Data Used (MCP)
- get_weather_forecast (success): next-day/next-days forecast data for Singapore.

### Suggested Plan
- Day 1: Marina Bay + Gardens by the Bay (shift to museums if rain probability is high).
- Day 2: Cultural districts with MRT-based routing and reduced walking.
- Day 3: Sentosa or indoor family alternatives depending on forecast.

### Sources
- Singapore RAG source set (Wikivoyage + Visit Singapore pages)
- MCP Weather Tool (Open-Meteo)

## Notes
- Full model-generated transcripts for RAG-heavy answers require `GOOGLE_API_KEY` in `.env`.
- MCP integrations and tool outputs were validated successfully in this environment.
