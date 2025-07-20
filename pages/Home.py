import streamlit as st
from utils import fetch_cartoons, get_thumbnail, group_by_season
from firebase_db import get_watch_history, get_my_list
from datetime import datetime
import platform

st.set_page_config(page_title="Cartoon Library", layout="wide")

st.title("🎬 Cartoon Library")

# 🔐 Require login
user = st.session_state.get("user")
uid = st.session_state.get("uid")
if not uid:
    st.warning("Please sign in to view your personalized feed.")
    st.stop()

# 🔍 Search and Filters
query = st.text_input("🔍 Search Cartoons")
years_filter = st.multiselect("📅 Filter by Year", options=[str(y) for y in range(1920, datetime.now().year + 1)])
sort_order = st.radio("Sort by", ["Popularity", "Recent"], horizontal=True)

if st.button("🔄 Refresh Library Cache"):
    st.cache_data.clear()
    st.experimental_rerun()

# 🎞️ Load Data
years_filter = st.multiselect("📅 Filter by Year", options=available_years, default=[])
years_filter = [str(y) for y in years_filter]  # ✅ convert to strings
cartoons = fetch_cartoons(query=query, year=','.join(years_filter) if years_filter else None)

# 📌 Sort
if sort_order == "Recent":
    cartoons.sort(key=lambda x: x.get("year", ""), reverse=True)
else:
    cartoons.sort(key=lambda x: x.get("downloads", 0), reverse=True)

# 📁 Resume Watching
st.subheader("⏯️ Continue Watching")
watch_history = get_watch_history(uid)
resumables = watch_history[:5] if watch_history else []
if resumables:
    cols = st.columns(len(resumables))
    for i, entry in enumerate(resumables):
        with cols[i]:
            st.image(f"https://archive.org/services/img/{entry['video_id']}", use_column_width=True)
            st.caption(entry['title'])
            if st.button("▶ Resume", key=f"resume_{entry['video_id']}"):
                st.session_state["selected_video"] = entry['video_id']
                st.switch_page("pages/watch.py")
else:
    st.info("No recently watched cartoons.")

# 💖 Favorites
st.subheader("❤️ My List")
favorites = get_my_list(uid)
if favorites:
    fav_cols = st.columns(min(4, len(favorites)))
    for i, fav in enumerate(favorites):
        with fav_cols[i % 4]:
            st.image(f"https://archive.org/services/img/{fav['video_id']}", use_column_width=True)
            st.caption(fav['title'])
            if st.button("▶ Watch", key=f"watch_fav_{fav['video_id']}"):
                st.session_state["selected_video"] = fav['video_id']
                st.switch_page("pages/watch.py")
else:
    st.info("No favorites yet.")

# 📺 All Cartoons
st.subheader("📺 All Cartoons")
grouped = group_by_season(cartoons)
for season, items in grouped.items():
    st.markdown(f"### {season}")
    cols = st.columns(4)
    for i, cartoon in enumerate(items):
        with cols[i % 4]:
            st.image(get_thumbnail(cartoon), use_column_width=True)
            st.markdown(f"**{cartoon['title']}**")
            st.markdown(f"`{cartoon.get('year', 'Unknown')}`")
            if st.button("▶ Watch", key=f"watch_{cartoon['identifier']}"):
                st.session_state["selected_video"] = cartoon['identifier']
                st.switch_page("pages/watch.py")

# Device info (optional analytics)
st.session_state["platform_info"] = {
    "device": platform.machine(),
    "system": platform.system(),
    "timestamp": datetime.utcnow().isoformat(),
}
