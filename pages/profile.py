# 📁 pages/profile.py
import streamlit as st
from firebase_db import get_watch_history, get_my_list
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="My Profile | CartoonBox")
st.title("👤 My Profile")

uid = st.session_state.get("uid")
if not uid:
    st.warning("Please log in to view your profile.")
    st.stop()

st.subheader("📥 Watch History")
history = get_watch_history(uid)

if not history:
    st.info("No viewing history found.")
else:
    for row in history:
        st.markdown(f"[{row['title']}](https://archive.org/details/{row['video_id']}) — _{row['watched_at'].strftime('%Y-%m-%d %H:%M:%S') if 'watched_at' in row else 'Unknown'}_")

    with st.expander("⬇ Export history as CSV"):
        df = pd.DataFrame(history)
        df["exported_at"] = datetime.utcnow()
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", data=csv, file_name="watch_history.csv", mime="text/csv")

st.markdown("---")
st.subheader("❤️ My List")
favorites = get_my_list(uid)

if not favorites:
    st.info("Your list is empty.")
else:
    for row in favorites:
        st.markdown(f"[{row['title']}](https://archive.org/details/{row['video_id']})")
