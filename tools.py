import json
import os
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv
from langchain.tools import tool
from tavily import TavilyClient

from database_chroma import search_similar_outfits, seed_dummy_wardrobe_items

load_dotenv()


def _safe_json(data: Dict[str, Any]) -> str:
    """Return compact, valid JSON text for tool outputs."""
    return json.dumps(data, ensure_ascii=True)


@tool
def get_current_location() -> str:
    """
    Fetch the user's current city based on IP location using ip-api.com.
    Returns a JSON string with the city, region, and country.
    """
    try:
        response = requests.get("http://ip-api.com/json/", timeout=5)
        response.raise_for_status()
        payload = response.json()
        result = {
            "city": payload.get("city", "Unknown"),
            "region": payload.get("regionName", "Unknown"),
            "country": payload.get("country", "Unknown")
        }
        return _safe_json(result)
    except Exception as exc:
        return _safe_json({"error": f"IP location request failed: {str(exc)}"})


@tool
def get_current_weather(location: str) -> str:
    """
    Fetch current weather from WeatherAPI for a given location.
    Returns JSON string with temperature, humidity, and precipitation.
    """
    api_key = os.getenv("WEATHERAPI_KEY")
    if not api_key:
        return _safe_json({"error": "WEATHERAPI_KEY is not set."})

    try:
        response = requests.get(
            "https://api.weatherapi.com/v1/current.json",
            params={"key": api_key, "q": location},
            timeout=15,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        return _safe_json({"error": f"Weather API request failed: {str(exc)}"})

    current = payload.get("current", {})
    location_data = payload.get("location", {})
    temperature = current.get("temp_c")
    humidity = current.get("humidity")
    precipitation = current.get("precip_mm", 0.0)
    condition = current.get("condition", {})

    result = {
        "location": location_data.get("name", location),
        "temperature_celsius": temperature,
        "humidity_percent": humidity,
        "precipitation_mm_last_1h": precipitation,
        "weather_main": condition.get("text"),
        "weather_description": condition.get("text"),
    }
    return _safe_json(result)


@tool
def get_fashion_trends(fashion_query: str, weather_context: str = "") -> str:
    """
    Search latest fashion trends with Tavily, considering the weather context.
    Example query: 'dinner outfit trends'. weather_context: 'sunny, 25C'.
    Returns a concise JSON string with the top 3 results.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return _safe_json({"error": "TAVILY_API_KEY is not set."})

    search_q = f"Fashion trends for {fashion_query}"
    if weather_context:
        search_q += f" given weather: {weather_context}"

    try:
        client = TavilyClient(api_key=api_key)
        # Using basic depth and fewer results to keep it concise
        result = client.search(
            query=search_q,
            search_depth="basic",
            max_results=3,
            include_raw_content=False,
        )
    except Exception as exc:
        return _safe_json({"error": f"Tavily search failed: {str(exc)}"})

    cleaned_results: List[Dict[str, Any]] = []
    for item in result.get("results", []):
        content = item.get("content", "")
        # truncate content for conciseness
        short_content = content[:250] + "..." if len(content) > 250 else content
        cleaned_results.append(
            {
                "title": item.get("title"),
                "summary": short_content,
            }
        )

    return _safe_json(
        {
            "search_used": search_q,
            "trends": cleaned_results,
        }
    )


@tool
def search_wardrobe_outfits(query: str, gender: str = "unknown") -> str:
    """
    Search local ChromaDB wardrobe collection for relevant outfits.
    Provide the user's gender ('male' or 'female') to strictly filter out wrong-gender items.
    """
    try:
        seed_dummy_wardrobe_items()
        
        disliked = []
        g = gender.lower()
        if g == 'male' or 'male' in query.lower() or 'men' in query.lower():
            disliked = ['dress', 'skirt', 'blouse', 'midi', 'a-line', 'a line', 'gown', 'heels']
        elif g == 'female' or 'female' in query.lower() or 'women' in query.lower():
            # If strictly needed, could add male-only terms here, but usually less strict.
            pass

        matches = search_similar_outfits(query_text=query, top_k=3, disliked_keywords=disliked)
        return _safe_json({"query": query, "gender_filter": gender, "matches": matches})
    except Exception as exc:
        return _safe_json({"error": f"Chroma search failed: {str(exc)}"})


def get_tools():
    """Convenience helper for agent wiring."""
    return [get_current_location, get_current_weather, get_fashion_trends, search_wardrobe_outfits]

