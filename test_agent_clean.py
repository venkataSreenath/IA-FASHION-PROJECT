import traceback
import sys
from agent_logic import recommend_outfit_with_leonardo

try:
    print("Testing recommendation...")
    out = recommend_outfit_with_leonardo(
        "Suggest me an outfit for a date with a girl.",
        None,
        False,
        num_images=2,
    )
    print("Success. Text:", out.get("text_output"))
    print("Image URLs:", out.get("image_urls"))
    if out.get("local_image_paths"):
        print("Local files:", out.get("local_image_paths"))
except Exception as e:
    print("Failed")
    with open("err3.log", "w") as f:
        f.write(traceback.format_exc())
