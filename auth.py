# auth.py

import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
from urllib.parse import urlencode
from google.cloud import firestore
from google.oauth2 import service_account

# Load secrets from Streamlit secrets manager
client_id = st.secrets["client_id"]
client_secret = st.secrets["client_secret"]
redirect_uri = st.secrets["redirect_uri"]
firestore_credentials = st.secrets["firestore_service_account"]  # JSON as dict

# OAuth2 Endpoints
authorization_endpoint = "https://accounts.google.com/o/oauth2/v2/auth"
token_endpoint = "https://oauth2.googleapis.com/token"
userinfo_endpoint = "https://openidconnect.googleapis.com/v1/userinfo"

# Initialize Firestore (cached)
@st.cache_resource
def get_firestore_db():
    credentials = service_account.Credentials.from_service_account_info(firestore_credentials)
    return firestore.Client(credentials=credentials, project=credentials.project_id)

db = get_firestore_db()

# Save or update user profile in Firestore
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

# Handle Google OAuth2 callback
def handle_callback():
    params = st.query_params
    if "code" in params:
        client = OAuth2Session(client_id, client_secret, redirect_uri=redirect_uri)
        try:
            token = client.fetch_token(token_endpoint, code=params["code"])
            client.token = token
            userinfo = client.get(userinfo_endpoint).json()

            if not userinfo.get("email") or not userinfo.get("sub"):
                st.error("Login failed: Missing required user info.")
                st.stop()

            uid = save_user_to_firestore(userinfo)
            st.session_state.user = userinfo
            st.session_state.uid = uid
            st.session_state.token = token

            st.query_params.clear()
            st.switch_page("pages/Home.py")

        except Exception as e:
            st.error(f"OAuth Error: {e}")
            st.stop()

# Login button with styling
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
        <a href="{auth_url}" target="_self">
            <button style="padding: 0.5rem 1rem; font-size: 1rem;">🔐 Login with Google</button>
        </a>
    """, unsafe_allow_html=True)

# Require login or redirect user
def require_login():
    if "user" not in st.session_state:
        st.session_state.user = None
        st.session_state.uid = None

    if not st.session_state.user:
        handle_callback()
        login_button()
        st.stop()

# Optional logout button
def logout_button(label="Logout 🔒"):
    if st.button(label):
        st.session_state.clear()
        st.success("You have been logged out.")
        st.experimental_rerun()
