# db.py
import streamlit as st
from sqlalchemy import create_engine, Table, Column, String, MetaData, DateTime, insert, select, and_, delete
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Load from Streamlit secrets
DATABASE_URL = st.secrets["db_url"]

# Setup DB engine and metadata
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Define tables
watch_history = Table(
    "watch_history", metadata,
    Column("email", String, primary_key=True),
    Column("video_id", String, primary_key=True),
    Column("title", String),
    Column("watched_at", DateTime, default=datetime.utcnow)
)

my_list = Table(
    "my_list", metadata,
    Column("email", String, primary_key=True),
    Column("video_id", String, primary_key=True),
    Column("title", String)
)

# Create tables if not exist
metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def add_to_watch_history(email, video_id, title):
    with engine.begin() as conn:
        conn.execute(
            insert(watch_history)
            .values(email=email, video_id=video_id, title=title, watched_at=datetime.utcnow())
            .on_conflict_do_nothing()
        )

def get_watch_history(email):
    with engine.begin() as conn:
        result = conn.execute(
            select(watch_history.c.video_id, watch_history.c.title)
            .where(watch_history.c.email == email)
            .order_by(watch_history.c.watched_at.desc())
        )
        return result.fetchall()

def add_to_my_list(email, video_id, title):
    with engine.begin() as conn:
        conn.execute(
            insert(my_list)
            .values(email=email, video_id=video_id, title=title)
            .on_conflict_do_nothing()
        )

def get_my_list(email):
    with engine.begin() as conn:
        result = conn.execute(
            select(my_list.c.video_id, my_list.c.title)
            .where(my_list.c.email == email)
        )
        return result.fetchall()

def remove_from_my_list(email, video_id):
    with engine.begin() as conn:
        conn.execute(
            delete(my_list).where(and_(my_list.c.email == email, my_list.c.video_id == video_id))
        )
