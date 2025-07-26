# firebase_db.py

import firebase_admin
from firebase_admin import credentials, firestore, db as rtdb
import streamlit as st
import uuid

# Use correct key from secrets.toml
firebase_config = st.secrets["firestore_service_account"]

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate(dict(firebase_config))
    firebase_admin.initialize_app(cred, {
        "databaseURL": f"https://{firebase_config['project_id']}.firebaseio.com"
    })

db = firestore.client()

# --- Firestore Functions ---

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
        history_doc_id = str(uuid.uuid4())
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

def clear_watch_history(uid):
    try:
        history_ref = db.collection("users").document(uid).collection("history")
        docs = list(history_ref.stream())
        for doc in docs:
            history_ref.document(doc.id).delete()
    except Exception as e:
        st.error("❌ Failed to clear history.")
        st.text(f"Error: {e}")

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

# --- Profile Info ---

def save_user_profile(uid, name, email, image_url=None):
    db.collection("users").document(uid).set({
        "name": name,
        "email": email,
        "image_url": image_url,
        "joined": firestore.SERVER_TIMESTAMP
    }, merge=True)

def get_user_profile(uid):
    try:
        doc = db.collection("users").document(uid).get()
        return doc.to_dict() if doc.exists else {}
    except Exception as e:
        st.error("❌ Failed to fetch profile.")
        st.text(f"Error: {e}")
        return {}

# --- Realtime DB Sync (optional) ---

def sync_to_realtime_db(uid, key, value):
    try:
        ref = rtdb.reference(f"users/{uid}/{key}")
        ref.set(value)
    except Exception as e:
        st.warning("⚠️ Failed to sync to Realtime DB.")
        st.text(f"Error: {e}")
