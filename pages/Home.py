# 📁 pages/home.py
import streamlit as st
from utils import fetch_cartoons, get_thumbnail
from datetime import datetime

st.set_page_config(page_title="📺 CartoonBox", layout="wide")

# --- Header Bar ---
cols = st.columns([1, 6, 1])
with cols[0]:
    st.markdown("## 📺")
with cols[1]:
    search = st.text_input("Search for cartoons...", label_visibility="collapsed", placeholder="Search...")
with cols[2]:
    if st.button("👤 Profile"):
        st.switch_page("pages/profile.py")

st.markdown("---")

# --- Fetch and Filter ---
cartoons = fetch_cartoons()
if search:
    cartoons = [c for c in cartoons if search.lower() in c["title"].lower()]

# --- Detail / My List Tabs ---
tabs = st.tabs(["📄 Detail", "📥 My List"])
with tabs[0]:
    st.subheader("🎬 Featured Cartoons")
    cols = st.columns(4)
    for i, cartoon in enumerate(cartoons[:12]):  # Limit to 12 for performance
        with cols[i % 4]:
            st.image(get_thumbnail(cartoon), use_column_width=True)
            st.markdown(f"**{cartoon['title']}**")
            year = cartoon.get("year", "Unknown")
            st.caption(f"Year: {year}")
            if st.button("▶️ Watch Now", key=f"watch_{cartoon['identifier']}"):
                st.session_state["selected_video"] = cartoon["identifier"]
                st.session_state["selected_title"] = cartoon["title"]
                st.switch_page("pages/watch.py")

with tabs[1]:
    st.info("✅ Your saved favorites will appear here.")

# --- Feed Section ---
st.markdown("---")
st.header("📡 Cartoon Feed")
feed_cols = st.columns(5)
for i, cartoon in enumerate(cartoons[12:27]):
    with feed_cols[i % 5]:
        thumb = get_thumbnail(cartoon)
        title = cartoon["title"]
        if st.button("", key=f"feed_{i}"):
            st.session_state["selected_video"] = cartoon["identifier"]
            st.session_state["selected_title"] = title
            st.switch_page("pages/watch.py")
        st.image(thumb, use_column_width=True)
        st.caption(title)

# --- Footer (Optional) ---
st.markdown("---")
st.caption(f"CartoonBox • {datetime.utcnow().year}")
