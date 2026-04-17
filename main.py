import streamlit as st

from agent_logic import recommend_outfit_with_pollinations
from database_sqlite import (
    add_user_preference,
    get_recent_preferences,
    initialize_database,
)


st.set_page_config(page_title="Fashion AI", layout="wide", page_icon="✦")

with open("style.css", "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)



def _render_images(image_sources, max_images: int = 3) -> None:
    if not image_sources:
        st.info("No generated images returned.")
        return
    cols = st.columns(min(len(image_sources), max_images))
    for idx, src in enumerate(image_sources[:max_images]):
        with cols[idx]:
            st.image(src, width=350)


def _parse_features(raw: str) -> list[str]:
    raw = raw.strip()
    if not raw:
        return []
    return [x.strip() for x in raw.split(",") if x.strip()]


def main() -> None:
    initialize_database()

    # ── Hero ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="page-hero">
        <div class="hero-badge">✦ &nbsp; AI Stylist</div>
        <h1>Fashion AI</h1>
        <p>Describe your occasion and get a personalised, curated outfit with AI-generated visuals.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Session state ────────────────────────────────────────────────────────
    for key, default in [
        ("stop_requested",   False),
        ("generation_result", None),
        ("selected_rating",   None),
        ("last_saved_rating", None),
        ("feedback_submitted", False),
        ("trigger_generate",  False),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    def _request_stop() -> None:
        st.session_state.stop_requested = True

    # ── Input columns ────────────────────────────────────────────────────────
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown('<span class="md-label-large">Your request</span>', unsafe_allow_html=True)
        user_id = st.text_input("User ID", value="default_user")
        user_query = st.text_input(
            "What are you dressing for?",
            placeholder="e.g. Smart casual dinner in Kochi tonight",
        )

        btn_col1, btn_col2 = st.columns([2, 1])
        with btn_col1:
            generate_btn = st.button(
                "✦  Generate outfit", type="primary", use_container_width=True
            )
        with btn_col2:
            st.button(
                "Exit", type="secondary", on_click=_request_stop, use_container_width=True
            )

    with col_right:
        st.markdown('<span class="md-label-large">Recommendation</span>', unsafe_allow_html=True)
        status_placeholder = st.empty()
        status_placeholder.markdown(
            '<div class="status-idle">'
            '<div class="status-dot"></div>'
            'Waiting for your request…'
            '</div>',
            unsafe_allow_html=True,
        )

    # ── Generate ─────────────────────────────────────────────────────────────
    if generate_btn or st.session_state.trigger_generate:
        st.session_state.trigger_generate    = False
        st.session_state.stop_requested      = False
        st.session_state.selected_rating     = None
        st.session_state.generation_result   = None
        st.session_state.last_saved_rating   = None
        st.session_state.feedback_submitted  = False

        if not user_query.strip():
            st.warning("Please enter a fashion request.")
            return

        status_placeholder.info("Generating your outfit recommendation…")

        user_preferences = get_recent_preferences(user_id=user_id, limit=20)
        result = recommend_outfit_with_pollinations(
            user_query=user_query,
            user_preferences=user_preferences,
            verbose=False,
            num_images=1,
            stop_check=lambda: st.session_state.stop_requested,
        )

        st.session_state.generation_result = result
        status_placeholder.success("Your outfit is ready!")

    # ── Display result ────────────────────────────────────────────────────────
    result = st.session_state.generation_result or None
    if not result:
        return

    text_output        = result.get("text_output", "")
    image_urls         = result.get("image_urls", []) or []
    local_image_paths  = result.get("local_image_paths", []) or []
    image_error        = result.get("image_error")
    stopped_by_user    = bool(result.get("stopped_by_user", False))

    st.markdown("---")

    # Outfit recommendation card with gradient accent stripe
    st.markdown("""
    <div class="recommendation-card">
        <div class="recommendation-card-accent"></div>
        <div class="recommendation-card-body">
            <span class="md-label-large">Outfit recommendation</span>
    """, unsafe_allow_html=True)
    st.write(text_output or "No recommendation returned.")
    st.markdown("</div></div>", unsafe_allow_html=True)

    if image_error and not stopped_by_user:
        st.error(f"Image generation error: {image_error}")
    if stopped_by_user:
        st.warning("Generation was stopped.")

    image_sources = local_image_paths if local_image_paths else image_urls
    _render_images(image_sources=image_sources)

    if stopped_by_user:
        return

    st.markdown("---")

    # ── Feedback section ──────────────────────────────────────────────────────
    if st.session_state.feedback_submitted:
        st.markdown("""
        <div class="success-banner">
            <span class="success-icon">✦</span>
            <h3>Feedback saved!</h3>
            <p>The AI will personalise future suggestions based on your taste.</p>
        </div>
        """, unsafe_allow_html=True)

        btn_c1, btn_c2 = st.columns(2)
        with btn_c1:
            if st.button(
                "✦  Refine with new feedback", type="primary", use_container_width=True
            ):
                st.session_state.feedback_submitted = False
                st.session_state.trigger_generate   = True
                st.rerun()
        with btn_c2:
            if st.button("I'm satisfied — finish", type="secondary", use_container_width=True):
                for key in ["generation_result", "selected_rating", "last_saved_rating"]:
                    st.session_state[key] = None
                st.session_state.feedback_submitted = False
                st.rerun()
        return

    st.markdown('<span class="md-label-large">Rate this outfit</span>', unsafe_allow_html=True)
    st.markdown(
        '<p style="color:var(--on-sv); font-size:0.9375rem; margin-bottom:1rem; font-weight:500;">'
        'How well did this match your needs?'
        '</p>',
        unsafe_allow_html=True,
    )

    rating_to_liked_utility    = {1: 1,  2: 1, 3: 2, 4: 2, 5: 3}
    rating_to_disliked_utility = {1: -2, 2: -1, 3: -2, 4: -2, 5: -3}
    rating_to_overall_utility  = {1: -2, 2: -1, 3: 1,  4: 2,  5: 2}

    rating_labels = {
        1: "😞  Not for me",
        2: "😐  It's okay",
        3: "🙂  Pretty good",
        4: "😊  Love it",
        5: "🤩  Perfect!",
    }

    rcols = st.columns(5)
    for r in range(1, 6):
        with rcols[r - 1]:
            st.markdown(f'<div class="rating-btn-{r}"></div>', unsafe_allow_html=True)
            if st.button(rating_labels[r], key=f"rate_{r}", use_container_width=True):
                st.session_state.selected_rating = r

    selected_rating = st.session_state.selected_rating
    if selected_rating is None:
        st.markdown(
            '<p style="color:var(--on-sv); font-size:0.875rem; margin-top:0.75rem; font-weight:500;">'
            'Tap a rating above to continue.'
            '</p>',
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        f'<span class="rating-chip">Selected &nbsp;{rating_labels[selected_rating]}</span>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # Save overall rating signal immediately
    if st.session_state.last_saved_rating != selected_rating:
        overall_utility = rating_to_overall_utility[int(selected_rating)]
        marker = (text_output or "")[:160].strip()
        if marker:
            add_user_preference(
                user_id=user_id, preference_text=marker, utility_score=int(overall_utility)
            )
            st.session_state.last_saved_rating = selected_rating
            st.info("Overall rating saved to your style profile.")

    # Feature feedback card
    st.markdown('<div class="md-card">', unsafe_allow_html=True)
    st.markdown(
        '<span class="md-label-large">Style feedback &nbsp;<span style="opacity:.5;font-size:.7em;">optional</span></span>',
        unsafe_allow_html=True,
    )

    liked_skip    = st.checkbox("Skip liked features",    value=False)
    disliked_skip = st.checkbox("Skip disliked features", value=False)

    liked_features_raw    = ""
    disliked_features_raw = ""

    if not liked_skip:
        liked_features_raw = st.text_area(
            "What did you like?",
            placeholder="e.g. navy colour, leather loafers, the blazer",
            height=88,
        )

    if not disliked_skip:
        disliked_features_raw = st.text_area(
            "What didn't work for you?",
            placeholder="e.g. too dark, heavy fabric, uncomfortable shoes",
            height=88,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    submit = st.button("Submit feedback  →", type="primary")
    if not submit:
        return

    liked_features    = _parse_features(liked_features_raw)
    disliked_features = _parse_features(disliked_features_raw)

    liked_utility    = rating_to_liked_utility[int(selected_rating)]
    disliked_utility = rating_to_disliked_utility[int(selected_rating)]

    stored = 0
    if not liked_skip and liked_features:
        for feat in liked_features:
            add_user_preference(
                user_id=user_id, preference_text=feat, utility_score=int(liked_utility)
            )
            stored += 1

    if not disliked_skip and disliked_features:
        for feat in disliked_features:
            add_user_preference(
                user_id=user_id, preference_text=feat, utility_score=int(disliked_utility)
            )
            stored += 1

    if stored == 0:
        if st.session_state.last_saved_rating is not None:
            st.info("Overall rating was saved. No feature preferences provided.")
        else:
            st.warning("No feedback stored (recommendation text was empty).")

    st.session_state.feedback_submitted = True
    st.rerun()


if __name__ == "__main__":
    main()