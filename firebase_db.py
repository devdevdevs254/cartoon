# firebase_db.py

import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
import uuid

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate(st.secrets["FIREBASE"])  # Path to your service account JSON
    firebase_admin.initialize_app(cred)

db = firestore.client()

def add_to_my_list(uid, video_id, title):
    db.collection("users").document(uid).collection("my_list").document(video_id).set({
        "title": title,
        "added_at": firestore.SERVER_TIMESTAMP
    })

def get_my_list(uid):
    docs = db.collection("users").document(uid).collection("my_list").stream()
    return [{"video_id": doc.id, **doc.to_dict()} for doc in docs]

def remove_from_my_list(uid, video_id):
    db.collection("users").document(uid).collection("my_list").document(video_id).delete()

def add_to_watch_history(uid, video_id, title):
    try:
        history_doc_id = str(uuid.uuid4())  # Unique document ID
        db.collection("users").document(uid).collection("history").document(history_doc_id).set({
            "video_id": video_id,
            "title": title,
            "watched_at": firestore.SERVER_TIMESTAMP
        })
    except Exception as e:
        st.error("❌ Failed to add to watch history.")
        st.text(f"Error: {e}")

def get_watch_history(uid, limit=20):
    try:
        docs = db.collection("users").document(uid).collection("history")\
            .order_by("watched_at", direction=firestore.Query.DESCENDING)\
            .limit(limit).stream()
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        st.error("❌ Failed to fetch watch history.")
        st.text(f"Error: {e}")
        return []

def update_viewing_progress(uid, video_id, position_seconds):
    try:
        db.collection("users").document(uid).collection("progress").document(video_id).set({
            "position": position_seconds,
            "updated_at": firestore.SERVER_TIMESTAMP
        })
    except Exception as e:
        st.error("❌ Failed to save progress.")
        st.text(f"Error: {e}")

def get_viewing_progress(uid, video_id):
    try:
        doc = db.collection("users").document(uid).collection("progress").document(video_id).get()
        if doc.exists:
            return doc.to_dict().get("position", 0)
    except Exception as e:
        st.error("❌ Failed to load progress.")
        st.text(f"Error: {e}")
    return 0
