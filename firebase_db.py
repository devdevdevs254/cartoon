# firebase_db.py

import firebase_admin
from firebase_admin import credentials, firestore, db as realtime_db
import streamlit as st
import uuid

# ------------------ Initialization ------------------

if not firebase_admin._apps:
    cred = credentials.Certificate(st.secrets["FIREBASE"])
    firebase_admin.initialize_app(cred, {
        "databaseURL": st.secrets["DATABASE_URL"]  # Needed for Realtime DB
    })

firestore_db = firestore.client()

# ------------------ User Profile ------------------

def set_user_profile(uid, name=None, email=None, photo_url=None):
    data = {
        "name": name,
        "email": email,
        "photo_url": photo_url,
        "updated_at": firestore.SERVER_TIMESTAMP,
    }
    # Remove None values
    data = {k: v for k, v in data.items() if v is not None}
    firestore_db.collection("users").document(uid).set(data, merge=True)
    realtime_db.reference(f"/users/{uid}/profile").update(data)

def get_user_profile(uid):
    try:
        doc = firestore_db.collection("users").document(uid).get()
        return doc.to_dict() if doc.exists else {}
    except Exception as e:
        st.error("❌ Failed to load user profile.")
        st.text(f"Error: {e}")
        return {}

# ------------------ My List ------------------

def add_to_my_list(uid, video_id, title):
    data = {
        "title": title,
        "added_at": firestore.SERVER_TIMESTAMP,
    }
    firestore_db.collection("users").document(uid).collection("my_list").document(video_id).set(data)
    realtime_db.reference(f"/users/{uid}/my_list/{video_id}").update(data)

def get_my_list(uid):
    try:
        docs = firestore_db.collection("users").document(uid).collection("my_list").stream()
        return [{"video_id": doc.id, **doc.to_dict()} for doc in docs]
    except Exception as e:
        st.error("❌ Failed to fetch 'My List'.")
        st.text(f"Error: {e}")
        return []

def remove_from_my_list(uid, video_id):
    try:
        firestore_db.collection("users").document(uid).collection("my_list").document(video_id).delete()
        realtime_db.reference(f"/users/{uid}/my_list/{video_id}").delete()
    except Exception as e:
        st.error("❌ Failed to remove from 'My List'.")
        st.text(f"Error: {e}")

# ------------------ Watch History ------------------

def add_to_watch_history(uid, video_id, title):
    try:
        history_doc_id = str(uuid.uuid4())
        data = {
            "video_id": video_id,
            "title": title,
            "watched_at": firestore.SERVER_TIMESTAMP,
        }
        firestore_db.collection("users").document(uid).collection("history").document(history_doc_id).set(data)
        realtime_db.reference(f"/users/{uid}/history/{history_doc_id}").update(data)
    except Exception as e:
        st.error("❌ Failed to add to watch history.")
        st.text(f"Error: {e}")

def get_watch_history(uid, limit=20):
    try:
        docs = firestore_db.collection("users").document(uid).collection("history")\
            .order_by("watched_at", direction=firestore.Query.DESCENDING)\
            .limit(limit).stream()
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        st.error("❌ Failed to fetch watch history.")
        st.text(f"Error: {e}")
        return []

def clear_watch_history(uid):
    try:
        col_ref = firestore_db.collection("users").document(uid).collection("history")
        docs = col_ref.stream()
        for doc in docs:
            doc.reference.delete()
            realtime_db.reference(f"/users/{uid}/history/{doc.id}").delete()
    except Exception as e:
        st.error("❌ Failed to clear watch history.")
        st.text(f"Error: {e}")

# ------------------ Viewing Progress ------------------

def update_viewing_progress(uid, video_id, position_seconds):
    try:
        data = {
            "position": position_seconds,
            "updated_at": firestore.SERVER_TIMESTAMP,
        }
        firestore_db.collection("users").document(uid).collection("progress").document(video_id).set(data)
        realtime_db.reference(f"/users/{uid}/progress/{video_id}").update(data)
    except Exception as e:
        st.error("❌ Failed to save viewing progress.")
        st.text(f"Error: {e}")

def get_viewing_progress(uid, video_id):
    try:
        doc = firestore_db.collection("users").document(uid).collection("progress").document(video_id).get()
        if doc.exists:
            return doc.to_dict().get("position", 0)
    except Exception as e:
        st.error("❌ Failed to load viewing progress.")
        st.text(f"Error: {e}")
    return 0
