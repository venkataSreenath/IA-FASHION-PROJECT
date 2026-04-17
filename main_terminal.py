from typing import List

from agent_logic import recommend_outfit_with_leonardo
from database_sqlite import (
    add_disliked_feature,
    get_recent_disliked_features,
    add_user_preference,
    get_recent_preferences,
    initialize_database,
)


def _capture_rated_features_from_user() -> List[str]:
    """
    Ask user to enter specific items/features that drove their rating as comma-separated values.
    Example: leather shoes, dark colors, heavy fabric
    """
    raw = input(
        "\nWhat specific items or features drove this rating? "
        "(comma-separated, leave blank to rate the whole outfit): "
    ).strip()
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def main() -> None:
    initialize_database()

    print("=== Intelligent Fashion Recommender (Terminal) ===")
    user_id = input("Enter your user id: ").strip()
    if not user_id:
        user_id = "default_user"

    print("\nType your fashion query. Type 'exit' to quit.")

    while True:
        user_query = input("\nYour query: ").strip()
        if user_query.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        if not user_query:
            print("Please enter a valid query.")
            continue

        user_preferences = get_recent_preferences(user_id=user_id, limit=20)
        print(f"\nLoaded {len(user_preferences)} utility-scored preferences from memory.")

        try:
            result = recommend_outfit_with_leonardo(
                user_query=user_query,
                user_preferences=user_preferences,
                verbose=True,
            )
        except Exception as exc:
            print(f"\nError while running agent: {exc}")
            continue

        text_output = result.get("text_output", "No recommendation returned.")
        image_urls = result.get("image_urls", [])
        local_paths = result.get("local_image_paths", [])
        leonardo_error = result.get("leonardo_error")

        print("\n=== Final Recommendation ===")
        print(text_output)

        print("\n=== Leonardo Generated Images ===")
        if leonardo_error:
            print(f"Leonardo error: {leonardo_error}")
        if image_urls:
            print("Image URLs:")
            for url in image_urls:
                print(f"- {url}")
        if local_paths:
            print("Local saved files:")
            for p in local_paths:
                print(f"- {p}")

        rating_map = {
            "bad": -2,
            "ok": -1,
            "average": 0,
            "good": 1,
            "very good": 2
        }
        
        feedback = input("\nRate this suggestion (bad, ok, average, good, very good): ").strip().lower()
        if feedback in rating_map:
            score = rating_map[feedback]
            features_to_store = _capture_rated_features_from_user()
            
            if not features_to_store:
                # Fallback: store a compact marker from the recommendation text.
                features_to_store = [text_output[:160]]

            for feature in features_to_store:
                add_user_preference(user_id=user_id, preference_text=feature, utility_score=score)

            print(f"Saved {len(features_to_store)} preference feature(s) with utility score {score} to memory.")
        else:
            print("Feedback not recognized as a valid rating. Skipping memory update.")


if __name__ == "__main__":
    main()
