# pages/watch.py

import streamlit as st
from utils import get_metadata, get_stream_url, group_by_season
from firebase_db import update_viewing_progress, get_viewing_progress, add_to_watch_history
from datetime import datetime

st.set_page_config(page_title="Watch Cartoon", layout="wide")

# Check if video is selected
video_id = st.session_state.get("selected_video")
if not video_id:
    st.error("No video selected.")
    st.stop()

# Fetch metadata and streamable files
meta = get_metadata(video_id)
metadata = meta.get("metadata", {})
files = meta.get("files", [])

title = metadata.get("title", video_id)
description = metadata.get("description", "No description available.")

# Store user info if available
uid = st.session_state.get("uid")
email = st.session_state.get("user", {}).get("email")

# Add to watch history
if uid:
    add_to_watch_history(uid, video_id, title)

# List episodes (only .mp4 files)
episodes = [
    {
        "title": f.get("title", f["name"]),
        "url": f"https://archive.org/download/{video_id}/{f['name']}",
        "filename": f["name"]
    }
    for f in files if f["name"].endswith(".mp4")
]

grouped = group_by_season(episodes)

# Show header
st.title(title)
st.caption(description)

# Embedded player for first episode or selected one
selected_ep = st.session_state.get("selected_episode") or episodes[0]
stream_url = selected_ep["url"]

st.video(stream_url)

# Load previous progress
if uid:
    progress = get_viewing_progress(uid, video_id)
    if progress > 0:
        st.info(f"⏮ Resume from {progress} seconds")

# Allow manual save of progress
st.markdown("### 💾 Save Progress")
pos = st.slider("Progress (seconds)", 0, 3000, 0)

if st.button("✅ Save"):
    if uid:
        update_viewing_progress(uid, video_id, pos)
        st.success("Progress saved!")
    else:
        st.warning("Login required to save progress.")

# List grouped episodes
st.markdown("### 📺 Episodes")
for season, eps in grouped.items():
    st.subheader(season)
    for ep in eps:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**{ep['title']}**")
        with col2:
            if st.button("▶️ Play", key=ep["filename"]):
                st.session_state["selected_episode"] = ep
                st.experimental_rerun()
