from typing import Dict, List, Optional

import chromadb
from chromadb.utils import embedding_functions

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "wardrobe_items"


def get_collection():
    """Initialize and return a local Chroma collection."""
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    default_embedder = embedding_functions.DefaultEmbeddingFunction()
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=default_embedder,
        metadata={"hnsw:space": "cosine"},
    )
    return collection


def seed_dummy_wardrobe_items() -> None:
    """Seed the collection with 45 dummy wardrobe items.

    If the Chroma DB already exists, this function only adds items that are missing.
    """
    collection = get_collection()

    existing = collection.get(include=["metadatas"])
    existing_ids = set(existing.get("ids", []))

    items = [
        {
            "id": "item_1",
            "description": "Navy blue slim-fit blazer for semi-formal evening events",
            "category": "blazer",
            "occasion": "semi-formal",
            "season": "all",
            "image_url": "https://example.com/images/navy_blazer.jpg",
        },
        {
            "id": "item_2",
            "description": "White cotton Oxford shirt suitable for office and brunch",
            "category": "shirt",
            "occasion": "formal-casual",
            "season": "all",
            "image_url": "https://example.com/images/white_oxford_shirt.jpg",
        },
        {
            "id": "item_3",
            "description": "Black tailored trousers with clean straight cut",
            "category": "pants",
            "occasion": "formal",
            "season": "all",
            "image_url": "https://example.com/images/black_trousers.jpg",
        },
        {
            "id": "item_4",
            "description": "Beige chinos for smart casual daytime outfit",
            "category": "pants",
            "occasion": "smart-casual",
            "season": "summer",
            "image_url": "https://example.com/images/beige_chinos.jpg",
        },
        {
            "id": "item_5",
            "description": "Dark brown leather loafers for business casual look",
            "category": "shoes",
            "occasion": "business-casual",
            "season": "all",
            "image_url": "https://example.com/images/brown_loafers.jpg",
        },
        {
            "id": "item_6",
            "description": "White minimal sneakers for travel and casual outings",
            "category": "shoes",
            "occasion": "casual",
            "season": "all",
            "image_url": "https://example.com/images/white_sneakers.jpg",
        },
        {
            "id": "item_7",
            "description": "Olive green bomber jacket for cool outdoor evenings",
            "category": "jacket",
            "occasion": "casual",
            "season": "winter",
            "image_url": "https://example.com/images/olive_bomber.jpg",
        },
        {
            "id": "item_8",
            "description": "Charcoal grey turtleneck sweater for winter layering",
            "category": "sweater",
            "occasion": "casual-formal",
            "season": "winter",
            "image_url": "https://example.com/images/charcoal_turtleneck.jpg",
        },
        {
            "id": "item_9",
            "description": "Maroon midi dress for festive dinner occasion",
            "category": "dress",
            "occasion": "festive",
            "season": "all",
            "image_url": "https://example.com/images/maroon_midi_dress.jpg",
        },
        {
            "id": "item_10",
            "description": "Light blue denim jacket for relaxed street style",
            "category": "jacket",
            "occasion": "casual",
            "season": "all",
            "image_url": "https://example.com/images/denim_jacket.jpg",
        },
        {
            "id": "item_11",
            "description": "Black wool overcoat for cold winter formal occasions",
            "category": "coat",
            "occasion": "formal",
            "season": "winter",
            "image_url": "https://example.com/images/black_overcoat.jpg",
        },
        {
            "id": "item_12",
            "description": "Camel wool coat for business meetings in cool weather",
            "category": "coat",
            "occasion": "business",
            "season": "winter",
            "image_url": "https://example.com/images/camel_coat.jpg",
        },
        {
            "id": "item_13",
            "description": "Trench coat in beige for rainy day smart styling",
            "category": "coat",
            "occasion": "smart-casual",
            "season": "rainy",
            "image_url": "https://example.com/images/beige_trench.jpg",
        },
        {
            "id": "item_14",
            "description": "Olive bomber jacket with a casual street look",
            "category": "jacket",
            "occasion": "casual",
            "season": "autumn",
            "image_url": "https://example.com/images/olive_bomber2.jpg",
        },
        {
            "id": "item_15",
            "description": "Lightweight grey hoodie for comfortable casual outings",
            "category": "hoodie",
            "occasion": "casual",
            "season": "all",
            "image_url": "https://example.com/images/grey_hoodie.jpg",
        },
        {
            "id": "item_16",
            "description": "Red plaid flannel shirt for cozy casual evenings",
            "category": "shirt",
            "occasion": "casual",
            "season": "autumn",
            "image_url": "https://example.com/images/red_flannel.jpg",
        },
        {
            "id": "item_17",
            "description": "Sky blue formal shirt for office and interviews",
            "category": "shirt",
            "occasion": "office",
            "season": "all",
            "image_url": "https://example.com/images/sky_blue_shirt.jpg",
        },
        {
            "id": "item_18",
            "description": "White linen shirt for summer brunch and vacations",
            "category": "shirt",
            "occasion": "casual",
            "season": "summer",
            "image_url": "https://example.com/images/linen_white_shirt.jpg",
        },
        {
            "id": "item_19",
            "description": "Black turtleneck sweater for sleek winter layering",
            "category": "sweater",
            "occasion": "formal-casual",
            "season": "winter",
            "image_url": "https://example.com/images/black_turtleneck.jpg",
        },
        {
            "id": "item_20",
            "description": "Cream knit sweater for warm smart casual looks",
            "category": "sweater",
            "occasion": "smart-casual",
            "season": "winter",
            "image_url": "https://example.com/images/cream_sweater.jpg",
        },
        {
            "id": "item_21",
            "description": "Striped knit polo for effortless everyday style",
            "category": "shirt",
            "occasion": "everyday",
            "season": "all",
            "image_url": "https://example.com/images/striped_polo.jpg",
        },
        {
            "id": "item_22",
            "description": "Dark navy chinos for smart casual weekday outfits",
            "category": "pants",
            "occasion": "smart-casual",
            "season": "all",
            "image_url": "https://example.com/images/navy_chinos.jpg",
        },
        {
            "id": "item_23",
            "description": "Light khaki chinos for warm weather daytime styling",
            "category": "pants",
            "occasion": "casual",
            "season": "summer",
            "image_url": "https://example.com/images/khaki_chinos.jpg",
        },
        {
            "id": "item_24",
            "description": "Tailored grey trousers with clean formal cut",
            "category": "pants",
            "occasion": "formal",
            "season": "all",
            "image_url": "https://example.com/images/grey_trousers.jpg",
        },
        {
            "id": "item_25",
            "description": "Black straight-leg jeans for casual everyday looks",
            "category": "pants",
            "occasion": "casual",
            "season": "all",
            "image_url": "https://example.com/images/black_jeans.jpg",
        },
        {
            "id": "item_26",
            "description": "Blue denim jeans for relaxed street style outfits",
            "category": "pants",
            "occasion": "casual",
            "season": "all",
            "image_url": "https://example.com/images/blue_jeans.jpg",
        },
        {
            "id": "item_27",
            "description": "Maroon midi dress for festive dinner and celebrations",
            "category": "dress",
            "occasion": "festive",
            "season": "all",
            "image_url": "https://example.com/images/maroon_dress2.jpg",
        },
        {
            "id": "item_28",
            "description": "Black wrap dress for parties and evening events",
            "category": "dress",
            "occasion": "party",
            "season": "all",
            "image_url": "https://example.com/images/black_wrap_dress.jpg",
        },
        {
            "id": "item_29",
            "description": "White A-line dress for daytime casual outings",
            "category": "dress",
            "occasion": "casual",
            "season": "summer",
            "image_url": "https://example.com/images/white_dress.jpg",
        },
        {
            "id": "item_30",
            "description": "Classic white sneaker for travel and everyday comfort",
            "category": "shoes",
            "occasion": "everyday",
            "season": "all",
            "image_url": "https://example.com/images/white_sneakers2.jpg",
        },
        {
            "id": "item_31",
            "description": "Brown leather loafers for business casual office wear",
            "category": "shoes",
            "occasion": "business-casual",
            "season": "all",
            "image_url": "https://example.com/images/brown_loafers2.jpg",
        },
        {
            "id": "item_32",
            "description": "Black leather dress shoes for formal events",
            "category": "shoes",
            "occasion": "formal",
            "season": "all",
            "image_url": "https://example.com/images/black_dress_shoes.jpg",
        },
        {
            "id": "item_33",
            "description": "Chelsea boots in dark brown for autumn evening style",
            "category": "shoes",
            "occasion": "outdoor",
            "season": "autumn",
            "image_url": "https://example.com/images/chelsea_boots.jpg",
        },
        {
            "id": "item_34",
            "description": "Suede desert boots in tan for smart casual outfits",
            "category": "shoes",
            "occasion": "smart-casual",
            "season": "all",
            "image_url": "https://example.com/images/desert_boots.jpg",
        },
        {
            "id": "item_35",
            "description": "Black ankle boots for winter nights and layering looks",
            "category": "shoes",
            "occasion": "winter-night",
            "season": "winter",
            "image_url": "https://example.com/images/ankle_boots.jpg",
        },
        {
            "id": "item_36",
            "description": "White minimal sneakers for casual travel and day wear",
            "category": "shoes",
            "occasion": "casual",
            "season": "all",
            "image_url": "https://example.com/images/white_sneakers3.jpg",
        },
        {
            "id": "item_37",
            "description": "Grey running shoes for sporty casual outfit pairing",
            "category": "shoes",
            "occasion": "sporty-casual",
            "season": "all",
            "image_url": "https://example.com/images/grey_sport_shoes.jpg",
        },
        {
            "id": "item_38",
            "description": "Leather belt in black for polished formal outfits",
            "category": "accessory",
            "occasion": "formal",
            "season": "all",
            "image_url": "https://example.com/images/black_leather_belt.jpg",
        },
        {
            "id": "item_39",
            "description": "Silver wristwatch for a clean modern accessory touch",
            "category": "accessory",
            "occasion": "office",
            "season": "all",
            "image_url": "https://example.com/images/silver_watch.jpg",
        },
        {
            "id": "item_40",
            "description": "Wool scarf in charcoal grey for cold winter styling",
            "category": "accessory",
            "occasion": "winter-outdoor",
            "season": "winter",
            "image_url": "https://example.com/images/charcoal_scarf.jpg",
        },
        {
            "id": "item_41",
            "description": "Lightweight cotton scarf in beige for spring smart casual",
            "category": "accessory",
            "occasion": "smart-casual",
            "season": "spring",
            "image_url": "https://example.com/images/beige_scarf.jpg",
        },
        {
            "id": "item_42",
            "description": "Navy blue slim-fit blazer for evening semi-formal events",
            "category": "blazer",
            "occasion": "semi-formal",
            "season": "all",
            "image_url": "https://example.com/images/navy_blazer2.jpg",
        },
        {
            "id": "item_43",
            "description": "Beige chinos in warm fabric for smart casual daytime looks",
            "category": "pants",
            "occasion": "smart-casual",
            "season": "summer",
            "image_url": "https://example.com/images/beige_chinos2.jpg",
        },
        {
            "id": "item_44",
            "description": "Black tailored trousers for formal office and conferences",
            "category": "pants",
            "occasion": "formal",
            "season": "all",
            "image_url": "https://example.com/images/black_trousers2.jpg",
        },
        {
            "id": "item_45",
            "description": "Blue denim jacket for relaxed street style and casual outings",
            "category": "jacket",
            "occasion": "casual",
            "season": "all",
            "image_url": "https://example.com/images/denim_jacket2.jpg",
        },
    ]

    missing_items = [item for item in items if item["id"] not in existing_ids]
    if not missing_items:
        return

    collection.add(
        ids=[item["id"] for item in missing_items],
        documents=[item["description"] for item in missing_items],
        metadatas=[
            {
                "category": item["category"],
                "occasion": item["occasion"],
                "season": item["season"],
                "image_url": item["image_url"],
            }
            for item in missing_items
        ],
    )


def search_similar_outfits(
    query_text: str, top_k: int = 3, disliked_keywords: Optional[List[str]] = None
) -> List[Dict]:
    """
    Run cosine similarity search and return top matching outfits.
    If disliked_keywords are provided, filter out obvious disliked matches.
    """
    collection = get_collection()
    results = collection.query(query_texts=[query_text], n_results=max(top_k * 3, top_k))

    response = []
    disliked_keywords = [k.lower().strip() for k in (disliked_keywords or []) if k.strip()]

    for item_id, doc, meta, distance in zip(
        results.get("ids", [[]])[0],
        results.get("documents", [[]])[0],
        results.get("metadatas", [[]])[0],
        results.get("distances", [[]])[0],
    ):
        doc_lower = doc.lower()
        meta_values = " ".join(str(v).lower() for v in meta.values())
        combined_text = f"{doc_lower} {meta_values}"

        if disliked_keywords and any(keyword in combined_text for keyword in disliked_keywords):
            continue

        response.append(
            {
                "id": item_id,
                "description": doc,
                "category": meta.get("category"),
                "occasion": meta.get("occasion"),
                "season": meta.get("season"),
                "image_url": meta.get("image_url"),
                "distance": distance,
            }
        )
        if len(response) == top_k:
            break
    return response


if __name__ == "__main__":
    seed_dummy_wardrobe_items()
    sample_results = search_similar_outfits("smart casual evening outfit with loafers")
    print(sample_results)
