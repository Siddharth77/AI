from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TravelSource:
    title: str
    url: str
    category: str


SINGAPORE_SOURCES = [
    TravelSource(
        title="Wikivoyage Singapore Travel Guide",
        url="https://en.wikivoyage.org/wiki/Singapore",
        category="overview",
    ),
    TravelSource(
        title="Visit Singapore: Essential Travel Information",
        url="https://www.visitsingapore.com/travel-guide-tips/essential-travel-information/",
        category="practical",
    ),
    TravelSource(
        title="Visit Singapore: Itineraries",
        url="https://www.visitsingapore.com/travel-guide-tips/itineraries/",
        category="itinerary",
    ),
    TravelSource(
        title="Visit Singapore: Top Things To Do",
        url="https://www.visitsingapore.com/see-do-singapore/",
        category="activities",
    ),
]
