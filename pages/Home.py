# 📁 pages/home.py
import streamlit as st
from utils import fetch_cartoons, get_thumbnail, group_by_season

st.set_page_config(page_title="Cartoon Library", layout="wide")

st.title("🎬 Cartoon Library")

cartoons = fetch_cartoons()

grouped = group_by_season(cartoons)

for season, items in grouped.items():
    st.subheader(season)
    cols = st.columns(4)
    for i, cartoon in enumerate(items):
        with cols[i % 4]:
            st.image(get_thumbnail(cartoon), use_column_width=True)
            st.markdown(f"**{cartoon['title']}**")
            st.markdown(f"`{cartoon['year']}`")
            if st.button("▶ Watch", key=f"watch_{cartoon['identifier']}"):
                st.session_state["selected_video"] = cartoon['identifier']
                st.switch_page("pages/watch.py")
