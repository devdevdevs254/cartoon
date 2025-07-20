# firebase_db.py
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import streamlit as st

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_credentials.json")  # Keep this JSON secret!
    firebase_admin.initialize_app(cred)

db = firestore.client()

def save_user_profile(userinfo):
    uid = userinfo["sub"]
    profile = {
        "email": userinfo.get("email"),
        "name": userinfo.get("name"),
        "picture": userinfo.get("picture"),
        "last_login": firestore.SERVER_TIMESTAMP,
        "ip": st.session_state.get("ip", ""),
        "platform": st.session_state.get("platform", ""),
    }
    db.collection("users").document(uid).set(profile, merge=True)

def add_to_my_list(uid, show_id):
    db.collection("users").document(uid).collection("my_list").document(show_id).set({
        "added_at": firestore.SERVER_TIMESTAMP
    })

def get_my_list(uid):
    docs = db.collection("users").document(uid).collection("my_list").stream()
    return [doc.id for doc in docs]

def save_watch_progress(uid, show_id, episode_id, progress_percent, timestamp=None):
    data = {
        "progress": progress_percent,
        "last_watched": timestamp or firestore.SERVER_TIMESTAMP,
    }
    db.collection("users").document(uid).collection("progress")\
        .document(f"{show_id}_{episode_id}").set(data, merge=True)

def get_watch_progress(uid, show_id, episode_id):
    doc = db.collection("users").document(uid).collection("progress")\
        .document(f"{show_id}_{episode_id}").get()
    return doc.to_dict() if doc.exists else None

def save_watch_history(uid, show_id, episode_id):
    entry = {
        "show_id": show_id,
        "episode_id": episode_id,
        "watched_at": firestore.SERVER_TIMESTAMP,
    }
    db.collection("users").document(uid).collection("history").add(entry)

def get_watch_history(uid, limit=20):
    docs = db.collection("users").document(uid).collection("history")\
        .order_by("watched_at", direction=firestore.Query.DESCENDING)\
        .limit(limit).stream()
    return [doc.to_dict() for doc in docs]
