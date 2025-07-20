import streamlit as st
from utils import fetch_cartoons, get_thumbnail
from firebase_db import get_my_list, get_watch_history
from datetime import datetime

st.set_page_config(page_title="📺 CartoonBox", layout="wide")
st.markdown("<h1 style='display: inline;'>📺 CartoonBox</h1>", unsafe_allow_html=True)

# Top bar: Search + Profile
cols = st.columns([3, 1])
with cols[0]:
    query = st.text_input("🔍 Search for cartoons", placeholder="e.g. Tom and Jerry, Sonic...")
with cols[1]:
    if st.session_state.get("user"):
        st.markdown(f"[👤 {st.session_state.user.get('name', 'Profile')}](/pages/profile.py)")
    else:
        st.markdown("[🔐 Login](#)")

# Filters
st.markdown("---")
filter_cols = st.columns([2, 2, 2])
with filter_cols[0]:
    years_filter = st.multiselect("📅 Filter by Year", options=[str(y) for y in range(1940, 2025)], default=[])
with filter_cols[1]:
    sort_option = st.selectbox("Sort by", ["Downloads", "Latest"])
with filter_cols[2]:
    if st.button("🔄 Refresh"):
        st.cache_data.clear()

# Fetch and display cartoons
cartoons = fetch_cartoons(query=query, year=",".join(years_filter) if years_filter else None,
                          sort="date desc" if sort_option == "Latest" else "downloads desc")

PER_PAGE = 12
page = st.session_state.get("page", 1)
total_pages = (len(cartoons) + PER_PAGE - 1) // PER_PAGE
start = (page - 1) * PER_PAGE
end = start + PER_PAGE

paginated = cartoons[start:end]

st.markdown("---")
st.markdown("## 📰 Cartoon Feed")
grid_cols = st.columns(4)
for i, cartoon in enumerate(paginated):
    with grid_cols[i % 4]:
        st.image(get_thumbnail(cartoon), use_column_width=True)
        st.markdown(f"**{cartoon['title']}**")
        st.markdown(f"*{cartoon.get('year', '')}*")
        if st.button("▶ Watch Now", key=f"watch_{cartoon['identifier']}"):
            st.session_state["selected_video"] = cartoon["identifier"]
            st.switch_page("pages/watch.py")

# Pagination Controls
pag_col1, pag_col2, pag_col3 = st.columns(3)
with pag_col1:
    if st.button("⬅️ Prev") and page > 1:
        st.session_state.page = page - 1
        st.experimental_rerun()
with pag_col2:
    st.markdown(f"**Page {page} of {total_pages}**")
with pag_col3:
    if st.button("➡️ Next") and page < total_pages:
        st.session_state.page = page + 1
        st.experimental_rerun()

# Tabs for My List and History
st.markdown("---")
st.header("🗂️ Library")
tab1, tab2 = st.tabs(["❤️ My List", "🕓 History"])

uid = st.session_state.get("uid")
if uid:
    with tab1:
        my_list = get_my_list(uid)
        if not my_list:
            st.info("No saved cartoons.")
        for row in my_list:
            st.markdown(f"[{row['title']}](https://archive.org/details/{row['video_id']})")

    with tab2:
        history = get_watch_history(uid)
        if not history:
            st.info("No watch history yet.")
        for row in history:
            st.markdown(f"[{row['title']}](https://archive.org/details/{row['video_id']})")
else:
    with tab1:
        st.warning("Login to view your saved list.")
    with tab2:
        st.warning("Login to view your history.")
