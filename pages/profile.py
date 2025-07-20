# 📁 pages/profile.py
import streamlit as st
from firebase_db import get_my_list, get_watch_history

st.set_page_config(page_title="Profile", layout="wide")

st.title("👤 My Profile")

user = st.session_state.get("user")
if not user:
    st.warning("Please sign in to view your profile.")
    st.stop()

uid = user["sub"]

st.subheader("📺 Watch History")
history = get_watch_history(uid)
for entry in history:
    st.markdown(f"- {entry['title']} at `{entry['watched_at']}`")

st.subheader("⭐ My List")
my_list = get_my_list(uid)
for entry in my_list:
    st.markdown(f"- {entry['title']}")
