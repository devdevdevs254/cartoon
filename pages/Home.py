# pages/home.py

import streamlit as st
import pandas as pd
from datetime import datetime
import platform
from firebase_db import (
    add_to_watch_history,
    get_watch_history,
    add_to_my_list,
    get_my_list,
    remove_from_my_list,
    update_viewing_progress,
    get_viewing_progress,
)

st.set_page_config(page_title="CartoonBox", layout="wide")
st.title("🎞️ CartoonBox")
st.caption("Enjoy free retro animated series — hosted on Internet Archive")

query = st.text_input("🔍 Search Cartoons")

# Firebase Auth
email = st.session_state.get("email")
if not email:
    st.warning("🔐 Please sign in to access your library and save progress.")
    st.stop()

@st.cache_data(ttl=60)
def load_cartoon_data():
    import json
    with open("data/cartoon_index.json") as f:
        return json.load(f)

cartoons = load_cartoon_data()

# 🔎 Filter by search query
if query:
    cartoons = [d for d in cartoons if query.casefold() in d["title"].casefold()]

# 👁️ Viewing logic
for i, show in enumerate(cartoons):
    title = show["title"]
    vid = show["video_id"]
    desc = show.get("description", "")
    thumb = f"https://archive.org/services/img/{vid}"
    video_url = f"https://archive.org/embed/{vid}"

    with st.container():
        cols = st.columns([1, 3])
        with cols[0]:
            st.image(thumb, width=200)
        with cols[1]:
            st.subheader(title)
            st.write(desc)

            if st.button(f"▶️ Watch", key=f"watch_{i}"):
                st.session_state["current_video"] = video_url
                st.session_state["current_title"] = title
                add_to_watch_history(email, vid, title)

            is_fav = any(item["video_id"] == vid for item in get_my_list(email))
            if is_fav:
                if st.button("❌ Remove from My List", key=f"rm_{i}"):
                    remove_from_my_list(email, vid)
                    st.experimental_rerun()
                else:
                    st.caption("✅ In My List")
            else:
                if st.button("❤️ Add to My List", key=f"fav_{i}"):
                    add_to_my_list(email, vid, title)

# Resume Watching
st.markdown("---")
st.header("🎬 Resume Watching")

watch_history = get_watch_history(email)
progress_cache = {row["video_id"]: get_viewing_progress(email, row["video_id"])
                  for row in watch_history}
resumables = [r for r in watch_history if progress_cache.get(r["video_id"], 0) > 0]

if resumables:
    cols = st.columns(min(3, len(resumables)))
    for i, r in enumerate(resumables):
        vid = r["video_id"]
        title = r["title"]
        pos = progress_cache[vid]
        thumb = f"https://archive.org/services/img/{vid}"
        with cols[i % 3]:
            st.image(thumb, use_column_width=True)
            st.markdown(f"**{title}**")
            st.markdown(f"[Resume at {pos}s](https://archive.org/details/{vid})")
else:
    st.info("No viewing progress yet.")

# Manual Progress Save
st.markdown("---")
st.subheader("💾 Save Progress")

vid_input = st.text_input("Video ID")
pos = st.slider("Progress (seconds)", 0, 3000, 0)

if st.button("✅ Save Viewing Progress"):
    if vid_input:
        update_viewing_progress(email, vid_input, pos)
        st.success("Progress saved!")
    else:
        st.error("Enter a video ID")

# My Library Tabs
st.markdown("---")
st.subheader("📚 Library")

tab1, tab2, tab3 = st.tabs(["❤️ My List", "🕓 History", "📥 Export"])

with tab1:
    favorites = get_my_list(email)
    if not favorites:
        st.info("No shows in My List.")
    for row in favorites:
        st.markdown(f"[{row['title']}](https://archive.org/details/{row['video_id']})")

with tab2:
    history = get_watch_history(email)
    if not history:
        st.info("No viewing history yet.")
    for row in history:
        st.markdown(f"[{row['title']}](https://archive.org/details/{row['video_id']})")

with tab3:
    if history:
        df = pd.DataFrame(history)
        df["exported_at"] = datetime.utcnow()
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", data=csv, file_name="watch_history.csv", mime="text/csv")
    else:
        st.info("Nothing to export yet.")

# OPTIONAL: Log platform for analytics (extend as needed)
st.session_state["platform_info"] = {
    "device": platform.machine(),
    "system": platform.system(),
    "ip": st.experimental_get_query_params().get("ip", ["N/A"])[0],
    "timestamp": datetime.utcnow().isoformat(),
}