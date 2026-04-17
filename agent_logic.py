import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
import time
from urllib.parse import quote
import re

import requests

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from tools import get_tools

load_dotenv()

DEFAULT_OPENROUTER_MODEL = "google/gemini-2.5-flash"

SYSTEM_PROMPT_TEMPLATE = """
You are an intelligent, highly personalized fashion recommendation agent.

Follow this workflow strictly for every user request:
1) Extract key context from the user request:
   - location/place
   - occasion/event
   - time/season/weather sensitivity
   - user demographics (gender, age) if provided
   - specific clothing items requested (e.g., "jean pant", "jacket")
   If no location is provided in the user query, you MUST instantly call the `get_current_location` tool to find the real-time location.
2) Use the weather tool for the detected (or real-time fetched) location.
3) Use the fashion trends tool to fetch current fashion trends for the relevant context (including age and gender).
4) Use the wardrobe retrieval tool to fetch matching outfits that the user owns. When calling this tool, explicitly include the user's gender and occasion in the query.
5) PREFERENCE INCORPORATION RULES (30% weight):
   - You must NOT solely depend on the utility scores from past feedback.
   - CRITICAL RULE FOR FORBIDDEN ITEMS (Bad Ratings): {forbidden_items}
     Under NO circumstances should you recommend the outfits or specific items listed in FORBIDDEN ITEMS. You MUST provide a completely different style of outfit than what is in this list. This rule overrides everything.
   - PREFERRED ITEMS (Good Ratings): {preferred_items}
     Consider these ONLY IF they perfectly match the CURRENT occasion and weather.
6) SITUATION AND CONTEXT RULES (70% weight):
   - The user's NEW situation, current occasion, and weather context MUST govern 70% of your decision-making.
   - E.g., if the user asks for an "office outfit", you must ONLY recommend office-appropriate attire, even if they previously highly rated a "riverside dinner outfit". The current occasion ALWAYS overrides past preferences if there is a conflict.
7) EXACT GENDER MATCH RULES (CRITICAL):
   - If the user is identified as MALE, you must STRICTLY AND EXCLUSIVELY recommend men's clothing (e.g., shirts, trousers, suits, men's jeans). YOU MUST NEVER recommend female clothing items like dresses, skirts, blouses, midi dresses, or A-line dresses to a male user under any circumstances.
   - If the user is identified as FEMALE, you must STRICTLY recommend women's clothing.
8) Produce a final recommendation that includes:
   - suggested colors
   - outfit pairing
   - footwear suggestion
   - short reasoning

CRITICAL OUTPUT CONSTRAINT:
Your final text output MUST be strictly 1 or 2 lines long (a very concise one or two sentences). 
Tailor your response explicitly to the user's age, gender, and CURRENT OCCASION. 
MANDATORY: If the user explicitly asked for a specific clothing item (like "jean pant" or "shoes"), you MUST include that specific item in your final recommendation.
CRITICAL: Do NOT change the user's stated occasion (e.g., if they ask for office, do not suggest a dinner outfit just because a retrieved wardrobe item says "dinner"). Ensure the suggested items are strictly appropriate for the user's gender.
DO NOT mention that you are an AI, and DO NOT state that you are insensitive or neutral to gender/age. Just directly provide the tailored outfit suggestion.
Always prioritize the user's current query context over their historical preferences.
Never include raw JSON, image_urls, IDs, distance scores, or technical artifacts. Do not explain your reasoning step-by-step; just give the final answer concisely.
"""


def _infer_user_gender(user_query: str) -> Optional[str]:
    """
    Infer the wearer's gender from common phrases in the user request.
    This avoids treating companion words like "girl" as the wearer's gender.
    """
    q = user_query.lower().strip()

    male_markers = [
        "i am a man",
        "i am male",
        "for a man",
        "for me, a man",
        "mens outfit",
        "men's outfit",
        "male outfit",
        "boy outfit",
        "guy outfit",
        "for him",
    ]
    female_markers = [
        "i am a woman",
        "i am female",
        "for a woman",
        "for me, a woman",
        "womens outfit",
        "women's outfit",
        "female outfit",
        "girl outfit",
        "lady outfit",
        "for her",
    ]

    if any(m in q for m in male_markers):
        return "male"
    if any(f in q for f in female_markers):
        return "female"

    # Companion phrases like "date with a girl" or "dinner with a girl"
    # should not flip the wearer to female; default these to male.
    companion_patterns = [
        r"\bwith a girl\b",
        r"\bwith my girlfriend\b",
        r"\bdate with a girl\b",
        r"\bdinner with a girl\b",
        r"\blunch with a girl\b",
    ]
    if any(re.search(p, q) for p in companion_patterns):
        return "male"

    return None


def _augment_user_query(user_query: str) -> str:
    """
    Add explicit wearer-gender clarification when we can infer it.
    """
    inferred_gender = _infer_user_gender(user_query)
    if not inferred_gender:
        return user_query
    return (
        f"{user_query}\n"
        f"Explicit wearer clarification: the outfit is for the user, who is {inferred_gender}. "
        f"Do not style the companion instead."
    )

def _build_agent(forbidden_text: str, preferred_text: str):
    """Create and return a LangGraph tool-calling agent (OpenRouter API)."""
    model = os.getenv("OPENROUTER_MODEL", DEFAULT_OPENROUTER_MODEL)
    api_key = os.getenv("OPENROUTER_API_KEY")

    llm = ChatOpenAI(
        model=model,
        openai_api_key=api_key,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.4,
        max_tokens=2000,
    )

    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        forbidden_items=forbidden_text,
        preferred_items=preferred_text
    )

    # Some versions of LangGraph ignore `prompt=`, so we rely on explicit injection inside `run_agent_with_trace` 
    return create_react_agent(
        model=llm,
        tools=get_tools(),
    )


def _pollinations_api_base_url() -> str:
    return os.getenv("POLLINATIONS_API_BASE_URL", "https://image.pollinations.ai/prompt").rstrip("/")


def _pollinations_model() -> str:
    return os.getenv("POLLINATIONS_MODEL", "flux").strip() or "flux"


def _make_image_prompt(text_output: str, user_query: str) -> Tuple[str, str]:
    """
    Convert the agent's text suggestion into a clean image prompt.
    """
    gender = _infer_user_gender(user_query)
    gender_clause = ""
    if gender == "male":
        gender_clause = "Show one adult man wearing the outfit. Do not show a woman, dress, skirt, blouse, heels, or feminine styling. "
    elif gender == "female":
        gender_clause = "Show one adult woman wearing the outfit. Do not show masculine tailoring unless the text explicitly requests it. "

    prompt = (
        "High-quality realistic fashion product photo. "
        f"{gender_clause}"
        f"Full-body outfit based on this suggestion: {text_output}. "
        "Single person only. Neutral studio background, studio lighting, sharp fabric details, no text, no watermark, no logos."
    )

    # Add a negative prompt to reduce artifacts.
    negative_prompt = (
        "blurry, low-resolution, watermark, text, logo, signature, extra limbs, bad anatomy, deformed hands, "
        "out-of-frame, cropped, duplicate subjects"
    )
    if gender == "male":
        negative_prompt += ", woman, female model, dress, skirt, blouse, gown, heels, feminine styling"
    elif gender == "female":
        negative_prompt += ", male model, mens suit, beard"
    return prompt, negative_prompt


def _build_pollinations_image_url(
    prompt: str,
    negative_prompt: str,
    width: int,
    height: int,
    seed: int,
) -> str:
    encoded_prompt = quote(prompt, safe="")
    encoded_negative = quote(negative_prompt, safe="")
    model = quote(_pollinations_model(), safe="")
    base = _pollinations_api_base_url()
    return (
        f"{base}/{encoded_prompt}"
        f"?width={int(width)}"
        f"&height={int(height)}"
        f"&seed={int(seed)}"
        f"&model={model}"
        f"&nologo=true"
        f"&private=true"
        f"&enhance=true"
        f"&negative={encoded_negative}"
    )


def generate_images_with_pollinations(
    text_output: str,
    user_query: str,
    num_images: int = 3,
    width: int = 768,
    height: int = 768,
    stop_check: Optional[Callable[[], bool]] = None,
) -> Dict[str, Any]:
    """
    Generate images on Pollinations AI using the outfit text as the prompt.
    Returns image URLs and (best-effort) downloaded local file paths.
    """
    if stop_check and stop_check():
        return {
            "image_urls": [],
            "local_image_paths": [],
            "generation_id": None,
            "image_error": "Stopped by user.",
            "stopped_by_user": True,
        }

    prompt, negative_prompt = _make_image_prompt(text_output=text_output, user_query=user_query)
    generation_id = f"pollinations-{abs(hash((user_query, text_output))) % 10**10}"
    image_urls = [
        _build_pollinations_image_url(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            seed=1000 + i,
        )
        for i in range(int(max(1, min(num_images, 4))))
    ]

    # Best-effort download so you can open locally if desired.
    out_dir = Path("pollinations_outputs")
    out_dir.mkdir(parents=True, exist_ok=True)
    local_paths: List[str] = []
    valid_image_urls: List[str] = []
    for i, url in enumerate(image_urls[:num_images]):
        if stop_check and stop_check():
            return {
                "image_urls": image_urls[:i],
                "local_image_paths": local_paths,
                "generation_id": generation_id,
                "image_error": "Stopped by user.",
                "stopped_by_user": True,
            }
        try:
            img_resp = requests.get(url, stream=True, timeout=60)
            img_resp.raise_for_status()
            file_path = out_dir / f"{generation_id}_{i+1}.png"
            with open(file_path, "wb") as f:
                for chunk in img_resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            local_paths.append(str(file_path))
            valid_image_urls.append(url)
            if i < num_images - 1:
                time.sleep(2.0)
        except Exception as e:
            # Skip broken image responses instead of rendering broken cards.
            print(f"Image generation failed for {url}: {e}")
            continue

    return {
        "image_urls": valid_image_urls,
        "local_image_paths": local_paths,
        "generation_id": generation_id,
        "image_error": None if valid_image_urls else "No valid images were returned.",
        "stopped_by_user": False,
    }

def recommend_outfit(
    user_query: str, user_preferences: Optional[List[Dict[str, Any]]] = None, verbose: bool = False
) -> str:
    """
    Run the fashion agent and return final recommendation text.
    user_preferences is passed into the prompt as utility-based filter memory.
    """
    run_result = run_agent_with_trace(
        user_query=user_query, user_preferences=user_preferences, verbose=verbose
    )
    return run_result.get("output", "")


def recommend_outfit_with_pollinations(
    user_query: str,
    user_preferences: Optional[List[Dict[str, Any]]] = None,
    verbose: bool = False,
    num_images: int = 3,
    stop_check: Optional[Callable[[], bool]] = None,
) -> Dict[str, Any]:
    """
    1) Get short fashion text output from the agent.
    2) Send that text to Pollinations AI to generate outfit images.
    3) Return both the text and the generated image URLs (+ local downloads when possible).
    """
    text_output = recommend_outfit(
        user_query=_augment_user_query(user_query), user_preferences=user_preferences, verbose=verbose
    )
    images = generate_images_with_pollinations(
        text_output=text_output,
        user_query=user_query,
        num_images=num_images,
        stop_check=stop_check,
    )
    return {
        "text_output": text_output,
        "image_urls": images.get("image_urls", []),
        "local_image_paths": images.get("local_image_paths", []),
        "generation_id": images.get("generation_id"),
        "image_error": images.get("image_error"),
        "stopped_by_user": images.get("stopped_by_user", False),
    }


def recommend_outfit_with_leonardo(
    user_query: str,
    user_preferences: Optional[List[Dict[str, Any]]] = None,
    verbose: bool = False,
    num_images: int = 3,
    stop_check: Optional[Callable[[], bool]] = None,
) -> Dict[str, Any]:
    """
    Backward-compatible alias for older callers.
    """
    return recommend_outfit_with_pollinations(
        user_query=user_query,
        user_preferences=user_preferences,
        verbose=verbose,
        num_images=num_images,
        stop_check=stop_check,
    )

def run_agent_with_trace(
    user_query: str, user_preferences: Optional[List[Dict[str, Any]]] = None, verbose: bool = False
) -> dict:
    """Run the agent and return output with a simple tool reasoning trace."""
    user_preferences = user_preferences or []
    
    neg_prefs = [p.get('text', '') for p in user_preferences if p.get('score', 0) < 0]
    pos_prefs = [p.get('text', '') for p in user_preferences if p.get('score', 0) > 0]
    
    forbidden_text = ", ".join(neg_prefs) if neg_prefs else "None"
    preferred_text = ", ".join(pos_prefs) if pos_prefs else "None"
    
    agent = _build_agent(forbidden_text=forbidden_text, preferred_text=preferred_text)
    
    # Render the system prompt to explicitly pass it
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        forbidden_items=forbidden_text,
        preferred_items=preferred_text
    )

    response = agent.invoke(
        {
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": (
                        f"User request: {user_query}\n"
                        f"Forbidden Items: {forbidden_text}\n"
                        f"Preferred Items: {preferred_text}\n"
                        "CRITICAL: Be extremely concise, strictly follow FORBIDDEN ITEMS rules, and ignore any urge to repeat identical suggestions!"
                    ),
                }
            ]
        }
    )

    messages = response.get("messages", [])
    final_output = ""
    trace = []

    for msg in messages:
        msg_type = getattr(msg, "type", "")
        msg_name = getattr(msg, "name", "")
        # For AIMessage, the content might be a list of tool calls in some versions, or text
        msg_content = getattr(msg, "content", "")

        if msg_type == "tool":
            trace.append(
                {
                    "tool": msg_name or "tool",
                    "output": str(msg_content),
                }
            )

        if msg_type == "ai" and msg_content:
            # Avoid storing internal tool call JSON as the final output
            if isinstance(msg_content, str):
                final_output = msg_content
            elif isinstance(msg_content, list):
                # If there's text in the content block, use it.
                texts = [b.get("text") for b in msg_content if isinstance(b, dict) and b.get("type") == "text"]
                if texts:
                    final_output = "\n".join(texts)

    return {
        "output": final_output,
        "trace": trace,
        "messages": messages,
    }

if __name__ == "__main__":
    sample_query = "I am going to a dinner in Kochi tonight. Suggest a smart casual outfit."
    sample_prefs = [{"text": "leather loafers", "score": -2}, {"text": "navy blue suit", "score": 2}]
    output = recommend_outfit(sample_query, user_preferences=sample_prefs, verbose=False)
    print(output)
