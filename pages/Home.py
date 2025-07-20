# 📁 pages/home.py

import streamlit as st
from utils import fetch_cartoons, get_thumbnail
from firebase_db import (
    get_my_list,
    get_watch_history,
    add_to_watch_history,
)
from datetime import datetime
import platform

st.set_page_config(page_title="📺 CartoonBox", layout="wide")

# ─── TOP NAVBAR ─────────────────────────────────────────────
with st.container():
    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        st.markdown("### 📺")
    with col2:
        query = st.text_input("Search Cartoons", placeholder="e.g. Sonic, Bugs Bunny", label_visibility="collapsed")
    with col3:
        if "user" in st.session_state:
            st.markdown(f"""<a href='/pages/profile.py'><button style='float:right'>👤</button></a>""", unsafe_allow_html=True)
        else:
            st.warning("🔐 Sign in required")

# ─── FILTER TOGGLE ──────────────────────────────────────────
tab = st.radio("View", ["📚 All", "❤️ My List", "🕓 History"], horizontal=True, label_visibility="collapsed")

# ─── FETCH + FILTER CARTOONS ────────────────────────────────
if tab == "📚 All":
    cartoons = fetch_cartoons(query=query)
elif tab == "❤️ My List":
    cartoons = get_my_list(st.session_state.uid)
elif tab == "🕓 History":
    cartoons = get_watch_history(st.session_state.uid)
else:
    cartoons = []

# ─── DISPLAY RESULTS ─────────────────────────────────────────
if cartoons:
    st.markdown("### Recommended For You")
    for i in range(0, len(cartoons), 4):
        row = cartoons[i:i+4]
        cols = st.columns(4)
        for j, cartoon in enumerate(row):
            with cols[j]:
                st.image(get_thumbnail(cartoon), use_column_width=True)
                st.markdown(f"**{cartoon.get('title', 'Untitled')}**")
                year = cartoon.get("year", "N/A")
                st.caption(f"📅 {year}")
                if st.button("▶ Watch Now", key=f"watch_{cartoon['identifier']}"):
                    st.session_state["selected_video"] = cartoon["identifier"]
                    add_to_watch_history(st.session_state.uid, cartoon["identifier"], cartoon.get("title", ""))
                    st.switch_page("pages/watch.py")
else:
    st.info("No cartoons found.")

# ─── PLATFORM INFO (Analytics / Debug) ───────────────────────
st.session_state["platform_info"] = {
    "device": platform.machine(),
    "system": platform.system(),
    "timestamp": datetime.utcnow().isoformat(),
}
