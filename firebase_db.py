import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_credentials.json")  # Path to your key
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
    db.collection("users").document(uid).collection("history").add({
        "video_id": video_id,
        "title": title,
        "watched_at": firestore.SERVER_TIMESTAMP
    })

def get_watch_history(uid, limit=20):
    docs = db.collection("users").document(uid).collection("history")\
        .order_by("watched_at", direction=firestore.Query.DESCENDING)\
        .limit(limit).stream()
    return [doc.to_dict() for doc in docs]

def update_viewing_progress(uid, video_id, position_seconds):
    db.collection("users").document(uid).collection("progress").document(video_id).set({
        "position": position_seconds,
        "updated_at": firestore.SERVER_TIMESTAMP
    })

def get_viewing_progress(uid, video_id):
    doc = db.collection("users").document(uid).collection("progress").document(video_id).get()
    if doc.exists:
        return doc.to_dict().get("position", 0)
    return 0
