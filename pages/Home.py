# 📁 pages/home.py

import streamlit as st
from utils import fetch_cartoons, get_thumbnail, group_by_season
from firebase_db import get_my_list, get_watch_history
from datetime import datetime

st.set_page_config(page_title="Dr. Cartoon", layout="wide")

# ─── TOP NAVIGATION BAR ────────────────────────────────────────
with st.container():
    col1, col2, col3 = st.columns([1, 4, 4])  # 3-part top bar layout

    # LEFT: App Logo
    with col1:
        st.markdown("<h3 style='margin-top: 0;'>📺 Dr. Cartoon</h3>", unsafe_allow_html=True)

    # MIDDLE: Profile Info (Avatar + Name)
    with col2:
        user = st.session_state.get("user")
        if user:
            name = user.get("name", "User")
            pic = user.get("picture", "")
            st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 10px;">
                    <img src="{pic}" alt="avatar" width="36" height="36" style="border-radius: 50%;">
                    <strong>{name}</strong>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("🔐 Sign in required", icon="🔐")
            st.stop()

    # RIGHT: Search Bar + Sort
    with col3:
        query = st.text_input("Search", placeholder="Search by title or genre", label_visibility="collapsed")
        sort_by = st.selectbox("Sort by", ["downloads", "year"], index=0, format_func=lambda x: "Most Viewed" if x == "downloads" else "Most Recent")

uid = st.session_state.get("uid")

# ─── TOGGLE FILTER ────────────────────────────────
st.markdown("---")
tab = st.radio("View", ["📚 All", "❤️ My List", "🕓 History"], horizontal=True, label_visibility="collapsed")

# ─── FETCH CARTOONS ──────────────────────────────
all_cartoons = fetch_cartoons(query=query, sort_by=sort_by, include_subjects=False)[0]

# ─── DYNAMIC YEAR FILTER ───────────────────────────
available_years = sorted({int(c["year"]) for c in all_cartoons if "year" in c and str(c["year"]).isdigit()}, reverse=True)
years_filter = st.multiselect("📅 Filter by Year", options=available_years, default=[])

if years_filter:
    all_cartoons = [c for c in all_cartoons if int(c.get("year", 0)) in years_filter]

# ─── FILTER BY TAB ───────────────────────────────
if tab == "❤️ My List":
    ids = {item["video_id"] for item in get_my_list(uid)}
    all_cartoons = [c for c in all_cartoons if c["identifier"] in ids]
elif tab == "🕓 History":
    ids = {item["video_id"] for item in get_watch_history(uid)}
    all_cartoons = [c for c in all_cartoons if c["identifier"] in ids]

# ─── PAGINATION SETUP ────────────────────────────
PER_PAGE = 8
if "page" not in st.session_state:
    st.session_state.page = 0

page = st.session_state.page
start = page * PER_PAGE
end = start + PER_PAGE
total_pages = (len(all_cartoons) - 1) // PER_PAGE + 1
current_page_items = all_cartoons[start:end]

# ─── DISPLAY THUMBNAILS IN GRID ───────────────────────────
st.markdown("---")
cols = st.columns(2 if st.session_state.get("is_mobile") else 4)

for i, cartoon in enumerate(current_page_items):
    with cols[i % len(cols)]:
        st.image(get_thumbnail(cartoon), use_container_width=True)
        st.markdown(f"**{cartoon['title']}**")
        st.caption(cartoon.get("year", "Unknown Year"))
        if st.button("▶ Watch Now", key=f"watch_{cartoon['identifier']}_{page}"):  # ADD page to key
            st.session_state["selected_video"] = cartoon['identifier']
            st.switch_page("pages/watch.py")

# ─── PAGINATION CONTROLS ───────────────────────────
st.markdown("---")
col_prev, col_page, col_next = st.columns([1, 2, 1])

with col_prev:
    if st.button("⬅ Previous") and page > 0:
        st.session_state.page -= 1
        st.experimental_rerun()

with col_page:
    st.markdown(f"**Page {page + 1} of {total_pages}**")

with col_next:
    if st.button("Next ➡") and end < len(all_cartoons):
        st.session_state.page += 1
        st.experimental_rerun()

# ─── FOOTER OR TIMESTAMP ───────────────────────────
st.caption(f"Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
