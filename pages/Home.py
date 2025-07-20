# 📁 pages/home.py

import streamlit as st
from utils import fetch_cartoons, get_thumbnail
from firebase_db import get_my_list, get_watch_history, add_to_watch_history
from datetime import datetime
import platform

st.set_page_config(page_title="CartoonBox", layout="wide")

# ─── TOP NAVIGATION ──────────────────────────────────────────────────────
with st.container():
    col1, col2, col3 = st.columns([1, 7, 1])
    with col1:
        st.markdown("### 📺")
    with col2:
        query = st.text_input("Search Cartoons", placeholder="Search by title or genre", label_visibility="collapsed")
    with col3:
        if st.session_state.get("user"):
            st.markdown(f"""<a href='/pages/profile.py'><button style='float:right'>👤</button></a>""", unsafe_allow_html=True)
        else:
            st.warning("🔐 Sign in required", icon="🔐")
            st.stop()

uid = st.session_state.get("uid")

# ─── TOGGLE FILTER ───────────────────────────────────────────────────────
tab = st.radio("View", ["📚 All", "❤️ My List", "🕓 History"], horizontal=True, label_visibility="collapsed")

# ─── FILTERS AND CONTROLS ────────────────────────────────────────────────
sort_by = st.selectbox("Sort by", ["downloads", "year"], index=0, format_func=lambda x: "Most Viewed" if x == "downloads" else "Most Recent")
all_cartoons = fetch_cartoons(include_subjects=False, sort_by=sort_by)[0]

# Extract unique years
available_years = sorted({int(c["year"]) for c in all_cartoons if "year" in c and str(c["year"]).isdigit()}, reverse=True)
years_filter = st.multiselect("📅 Filter by Year", options=available_years, default=[])

# ─── PAGINATION SETUP ────────────────────────────────────────────────────
PER_PAGE = 8
page = st.session_state.get("page", 0)

def change_page(delta):
    st.session_state.page = max(0, st.session_state.get("page", 0) + delta)

# ─── FETCH AND FILTER DATA ───────────────────────────────────────────────
if tab == "📚 All":
    cartoons = fetch_cartoons(query=query, year=",".join(map(str, years_filter)) if years_filter else None, sort_by=sort_by)[0]
elif tab == "❤️ My List":
    cartoons = get_my_list(uid)
elif tab == "🕓 History":
    cartoons = get_watch_history(uid)
else:
    cartoons = []

# ─── PAGINATE RESULTS ─────────────────────────────────────────────────────
total = len(cartoons)
start = page * PER_PAGE
end = start + PER_PAGE
page_cartoons = cartoons[start:end]

if page_cartoons:
    for i in range(0, len(page_cartoons), 4):
        row = page_cartoons[i:i+4]
        cols = st.columns(4)
        for j, cartoon in enumerate(row):
            with cols[j]:
                thumbnail = get_thumbnail(cartoon)
                title = cartoon.get("title", "Untitled")
                year = cartoon.get("year", "N/A")
                identifier = cartoon["identifier"]

                st.image(thumbnail, use_column_width=True)
                st.markdown(f"**{title}**")
                st.caption(f"📅 {year}")
                if st.button("▶ Watch Now", key=f"watch_{identifier}"):
                    st.session_state["selected_video"] = identifier
                    add_to_watch_history(uid, identifier, title)
                    st.switch_page("pages/watch.py")
else:
    st.info("No results found.")

# ─── PAGINATION CONTROLS ────────────────────────────────────────────────
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if page > 0:
        st.button("⬅ Previous", on_click=change_page, args=[-1])
with col3:
    if end < total:
        st.button("Next ➡", on_click=change_page, args=[1])
with col2:
    st.markdown(f"<p style='text-align:center;'>Page {page + 1}</p>", unsafe_allow_html=True)

# ─── FOOTER DEBUG (Optional) ─────────────────────────────────────────────
st.session_state["platform_info"] = {
    "device": platform.machine(),
    "system": platform.system(),
    "timestamp": datetime.utcnow().isoformat(),
}
