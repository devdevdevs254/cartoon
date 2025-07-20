# auth.py

import streamlit as st
import json
from authlib.integrations.requests_client import OAuth2Session
from urllib.parse import urlencode
from google.cloud import firestore
from google.oauth2 import service_account

# Load secrets from .streamlit/secrets.toml
client_id = st.secrets["oauth"]["client_id"]
client_secret = st.secrets["oauth"]["client_secret"]
redirect_uri = st.secrets["oauth"]["redirect_uri"]
firestore_credentials = st.secrets["firestore_service_account"]

# OAuth2 endpoints
authorization_endpoint = "https://accounts.google.com/o/oauth2/v2/auth"
token_endpoint = "https://oauth2.googleapis.com/token"
userinfo_endpoint = "https://openidconnect.googleapis.com/v1/userinfo"

# Initialize Firestore
@st.cache_resource
def get_firestore_db():
    credentials = service_account.Credentials.from_service_account_info(firestore_credentials)
    return firestore.Client(credentials=credentials, project=credentials.project_id)

db = get_firestore_db()

# Save or update user in Firestore
def save_user_to_firestore(userinfo):
    uid = userinfo["sub"]
    user_ref = db.collection("users").document(uid)
    user_ref.set({
        "email": userinfo.get("email"),
        "name": userinfo.get("name", "Anonymous"),
        "picture": userinfo.get("picture", ""),
        "last_login": firestore.SERVER_TIMESTAMP,
        "platform": st.runtime.scriptrunner.get_script_run_ctx().session_id if st.runtime.exists() else "unknown"
    }, merge=True)
    return uid

# Handle OAuth2 code exchange
def handle_callback():
    if "code" in st.query_params:
        try:
            client = OAuth2Session(client_id, client_secret, redirect_uri=redirect_uri)
            token = client.fetch_token(token_endpoint, code=st.query_params["code"])
            client.token = token
            userinfo = client.get(userinfo_endpoint).json()

            if not userinfo.get("email") or not userinfo.get("sub"):
                st.error("Login failed: Missing email or ID.")
                st.stop()

            # Save user info
            uid = save_user_to_firestore(userinfo)
            st.session_state.user = userinfo
            st.session_state.uid = uid
            st.session_state.email = userinfo["email"]
            st.session_state.name = userinfo.get("name", "Anonymous")
            st.session_state.picture = userinfo.get("picture", "")
            st.session_state.token = token

            st.query_params.clear()
            st.switch_page("pages/Home.py")

        except Exception as e:
            st.error(f"OAuth Error: {e}")
            st.stop()

# Login button
def login_button():
    auth_url = authorization_endpoint + "?" + urlencode({
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    })
    st.markdown(f"""
        <a href="{auth_url}">
            <button style="padding:0.5rem 1rem; font-size:1rem">🔐 Login with Google</button>
        </a>
    """, unsafe_allow_html=True)

# Require login or redirect to auth
def require_login():
    if "user" not in st.session_state or not st.session_state.user:
        handle_callback()  # Try to process OAuth2 callback
        login_button()
        st.stop()

# Optional logout
def logout_button(label="Logout 🔒"):
    if st.button(label):
        st.session_state.clear()
        st.success("Logged out successfully.")
        st.experimental_rerun()
