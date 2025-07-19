# pages/home.py
import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from sqlalchemy import insert, select
from db import Session, my_list, watch_history

st.set_page_config(page_title="Cartoons", page_icon="📺", layout="wide")

# Ensure login
if "user" not in st.session_state or not st.session_state.user:
    st.warning("You're not logged in.")
    st.stop()

email = st.session_state.user["email"]
session = Session()

# Profile dropdown
with st.container():
    col1, col2 = st.columns([8, 2])
    with col2:
        with st.expander(f"👤 {st.session_state.user['name']}"):
            st.image(st.session_state.user["picture"], width=100)
            st.caption(f"{email}")
            if st.button("🚪 Logout"):
                st.session_state.clear()
                st.experimental_rerun()

# Filter/Search
st.subheader("🎞️ Cartoon Library")
query = st.text_input("🔍 Search", "")
year = st.selectbox("📅 Filter by Year", [""] + list(range(1920, 2000)))
page = st.number_input("Page", min_value=1, value=1)

@st.cache_data
def fetch_cartoons(query, page, year):
    q = f'collection:animationandcartoons'
    if query:
        q += f' AND title:("{query}")'
    if year:
        q += f" AND year:({year})"

    url = "https://archive.org/advancedsearch.php"
    params = {
        "q": q,
        "fl[]": "identifier,title,description",
        "sort[]": "downloads desc",
        "rows": 9,
        "page": page,
        "output": "json"
    }
    return requests.get(url, params=params).json()["response"]["docs"]

cartoons = fetch_cartoons(query, page, year)

# Helpers
def is_in(table, vid):
    stmt = select(table).where(table.c.email == email, table.c.video_id == vid)
    return session.execute(stmt).first() is not None

def save(table, vid, data={}):
    stmt = insert(table).values(email=email, video_id=vid, **data)
    session.execute(stmt)
    session.commit()

st.header("🎞️ Cartoon Library")
resumes = session.execute(select(progress).where(progress.c.email == email, progress.c.last_position > 0).order_by(progress.c.updated_at.desc()).limit(5)).fetchall()
if resumes:
    cols = st.columns(min(3, len(resumes)))
    for i, row in enumerate(resumes):
        vid = row.video_id
        thumb = f"https://archive.org/services/img/{vid}"
        pos = int(row.last_position)
        with cols[i % 3]:
            st.image(thumb, use_column_width=True)
            st.markdown(f"[{vid}](https://archive.org/details/{vid})")
            st.caption(f"Resume at {pos}s")
else:
    st.info("No videos in progress")

# Main grid
cols = st.columns(3)
for idx, cartoon in enumerate(cartoons):
    vid = cartoon["identifier"]
    title = cartoon.get("title", "Untitled")
    thumb = f"https://archive.org/services/img/{vid}"
    video_url = f"https://archive.org/download/{vid}/{vid}.mp4"

    with cols[idx % 3]:
        st.image(thumb, use_column_width=True)
        st.markdown(f"**{title}**")

        if st.button(f"▶️ Watch ({vid})", key=f"watch_{vid}"):
            st.session_state["current_video"] = video_url
            st.session_state["current_title"] = title
            save(watch_history, vid, {"watched_at": datetime.utcnow()})

        if not is_in(my_list, vid):
            if st.button(f"❤️ Add to My List", key=f"fav_{vid}"):
                save(my_list, vid)
        else:
            st.caption("✅ In My List")

# Playback + simulated progress save
if "current_video" in st.session_state:
    st.markdown("---")
    st.subheader(f"Now Playing: {st.session_state['current_title']}")
    st.video(st.session_state["current_video"])
    pos = st.slider("🕓 Resume Position", 0, 300, 0)
    if st.button("💾 Save Progress"):
        session.execute(
            insert(progress).values(email=email, video_id=vid, last_position=pos)
            .on_conflict_do_update(index_elements=["email", "video_id"],
                                   set_={"last_position": pos, "updated_at": datetime.utcnow()})
        )
        session.commit()
        st.success("Saved!")

# Download History
st.markdown("---")
st.subheader("📄 My List & Watch History")

tab1, tab2, tab3 = st.tabs(["❤️ My List", "🕒 History", "⬇️ Export"])

def render(table):
    rows = session.execute(select(table).where(table.c.email == email)).fetchall()
    for row in rows:
        st.markdown(f"[{row.video_id}](https://archive.org/details/{row.video_id})")

with tab1:
    render(my_list)

with tab2:
    render(watch_history)

with tab3:
    hist = session.execute(select(watch_history).where(watch_history.c.email == email)).fetchall()
    if hist:
        df = pd.DataFrame(hist, columns=["email", "video_id", "watched_at"])
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", data=csv, file_name="watch_history.csv", mime="text/csv")
    else:
        st.info("No history to export.")
