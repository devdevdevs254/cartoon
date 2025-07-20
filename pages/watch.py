# 📁 pages/watch.py
import streamlit as st
from firebase_db import add_to_watch_history, update_viewing_progress, get_viewing_progress

video_id = st.session_state.get("selected_video")

if not video_id:
    st.error("No video selected.")
    st.stop()

video_url = f"https://archive.org/download/{video_id}/{video_id}.mp4"
st.video(video_url)

st.markdown(f"**Now Watching:** `{video_id}`")

if st.session_state.get("user"):
    uid = st.session_state["user"]["sub"]
    add_to_watch_history(uid, video_id, video_id)
