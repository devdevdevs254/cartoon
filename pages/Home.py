# 📁 pages/home.py
import streamlit as st
from utils import fetch_cartoons, get_thumbnail, group_by_season
from firebase_db import get_watch_history, get_my_list, get_viewing_progress
from datetime import datetime
import platform
import math

st.set_page_config(page_title="Cartoon Library", layout="wide")
st.title("📺 Cartoon Library")

# Optional Refresh
if st.button("🔄 Refresh Library"):
    st.cache_data.clear()
    st.success("Cartoon list refreshed!")

# Fetch all cartoons (no filters) for year options
initial_cartoons = fetch_cartoons()
available_years = sorted({c.get("year") for c in initial_cartoons if c.get("year")}, reverse=True)

# Search + Filter UI
query = st.text_input("🔍 Search Cartoons")
years_filter = st.multiselect("📅 Filter by Year", options=available_years)
years_filter = [str(y) for y in years_filter]  # Ensure string format

# Sort option
sort_by = st.radio("📊 Sort By", ["Popularity", "Recent"], horizontal=True)
sort = "downloads desc" if sort_by == "Popularity" else "date desc"

# Pagination setup
page_size = 12
page_num = st.number_input("Page", min_value=1, value=1, step=1)

# Fetch filtered cartoons
cartoons = fetch_cartoons(query=query, year=",".join(years_filter) if years_filter else None, sort=sort)
total_pages = math.ceil(len(cartoons) / page_size)
page_num = min(page_num, total_pages) if total_pages else 1
cartoons_paginated = cartoons[(page_num - 1) * page_size: page_num * page_size]

# Continue Watching (if logged in)
email = st.session_state.get("email")
if email:
    st.markdown("### 🎮 Continue Watching")
    watch_history = get_watch_history(email)
    progress_cache = {
        row["video_id"]: get_viewing_progress(email, row["video_id"]) for row in watch_history
    }
    resumables = [r for r in watch_history if progress_cache.get(r["video_id"], 0) > 0]

    if resumables:
        cols = st.columns(min(3, len(resumables)))
        for i, r in enumerate(resumables):
            with cols[i % 3]:
                st.image(f"https://archive.org/services/img/{r['video_id']}", use_column_width=True)
                st.markdown(f"**{r['title']}**")
                st.markdown(f"[Resume at {progress_cache[r['video_id']]}s](https://archive.org/details/{r['video_id']})")
    else:
        st.info("No resume data found.")
else:
    st.info("🔐 Sign in to see your progress.")

# Display paginated Cartoons by Group
grouped = group_by_season(cartoons_paginated)

for season, items in grouped.items():
    st.subheader(season)
    cols = st.columns(4)
    for i, cartoon in enumerate(items):
        with cols[i % 4]:
            st.image(get_thumbnail(cartoon), use_column_width=True)
            st.markdown(f"**{cartoon['title']}**")
            st.caption(f"{cartoon.get('year', 'Unknown')}")
            if st.button("▶ Watch", key=f"watch_{cartoon['identifier']}"):
                st.session_state["selected_video"] = cartoon["identifier"]
                st.switch_page("pages/watch.py")

# Pagination control
if total_pages > 1:
    st.markdown(f"Page {page_num} of {total_pages}")

# Tabs for Library
st.markdown("---")
st.subheader("📚 Library")

tab1, tab2 = st.tabs(["❤️ My List", "🕓 History"])

with tab1:
    if not email:
        st.info("Login to see your favorites")
    else:
        favorites = get_my_list(email)
        if not favorites:
            st.info("No shows in My List.")
        for row in favorites:
            st.markdown(f"[{row['title']}](https://archive.org/details/{row['video_id']})")

with tab2:
    if not email:
        st.info("Login to see your watch history")
    else:
        history = get_watch_history(email)
        if not history:
            st.info("No viewing history yet.")
        for row in history:
            st.markdown(f"[{row['title']}](https://archive.org/details/{row['video_id']})")

# Track session device
st.session_state["platform_info"] = {
    "device": platform.machine(),
    "system": platform.system(),
    "ip": st.experimental_get_query_params().get("ip", ["N/A"])[0],
    "timestamp": datetime.utcnow().isoformat(),
}
