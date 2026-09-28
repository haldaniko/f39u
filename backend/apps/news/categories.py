from __future__ import annotations

from django.utils.text import slugify


CANONICAL_CATEGORIES = [
    {
        "name": "Politics",
        "description": "Domestic and international politics, elections, laws and diplomacy.",
    },
    {
        "name": "World",
        "description": "Events in other countries, conflicts and international relations.",
    },
    {
        "name": "Finance",
        "description": "The economy, markets, banks, inflation, currencies and investing.",
    },
    {
        "name": "Business",
        "description": "Companies, deals, startups and industries.",
    },
    {
        "name": "Technology",
        "description": "IT, AI, the internet, gadgets, cybersecurity and space.",
    },
    {
        "name": "Science",
        "description": "Research, discoveries, medicine and climate.",
    },
    {
        "name": "Society",
        "description": "Social issues, education, migration and demographics.",
    },
    {
        "name": "Health",
        "description": "Medicine, diseases, pharmaceuticals and healthcare.",
    },
    {
        "name": "Culture",
        "description": "Film, music, literature and art.",
    },
    {
        "name": "Sport",
        "description": "Competitions, teams and athletes.",
    },
]

CANONICAL_CATEGORY_NAMES = [category["name"] for category in CANONICAL_CATEGORIES]
CANONICAL_CATEGORY_SLUGS = [slugify(name) for name in CANONICAL_CATEGORY_NAMES]
CANONICAL_CATEGORY_BY_SLUG = {
    slugify(category["name"]): category
    for category in CANONICAL_CATEGORIES
}

CATEGORY_ALIASES = {
    "agriculture": "Business",
    "agriculture & foodtech": "Business",
    "agriculture and foodtech": "Business",
    "ai": "Technology",
    "art": "Culture",
    "artificial intelligence": "Technology",
    "biotech & health": "Health",
    "biotech and health": "Health",
    "business": "Business",
    "culture": "Culture",
    "economics": "Finance",
    "economy": "Finance",
    "economy & finance": "Finance",
    "entertainment": "Culture",
    "environment": "Science",
    "feminism": "Society",
    "finance": "Finance",
    "general": "World",
    "health": "Health",
    "incidents": "World",
    "politics": "Politics",
    "rss": "World",
    "science": "Science",
    "sport": "Sport",
    "sports": "Sport",
    "startups": "Business",
    "technology": "Technology",
    "top": "World",
    "world": "World",
}


def normalize_category_name(name: str) -> str:
    value = str(name or "").strip()
    if not value:
        return "World"
    return CATEGORY_ALIASES.get(value.lower(), value if value in CANONICAL_CATEGORY_NAMES else "World")
