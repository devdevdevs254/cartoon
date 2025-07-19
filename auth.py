# auth.py
import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
from urllib.parse import urlencode

# Load secrets
client_id = st.secrets["client_id"]
client_secret = st.secrets["client_secret"]
redirect_uri = st.secrets["redirect_uri"]

authorization_endpoint = "https://accounts.google.com/o/oauth2/v2/auth"
token_endpoint = "https://oauth2.googleapis.com/token"
userinfo_endpoint = "https://openidconnect.googleapis.com/v1/userinfo"

def handle_callback():
    params = st.query_params
    if "code" in params:
        client = OAuth2Session(client_id, client_secret, redirect_uri=redirect_uri)
        try:
            token = client.fetch_token(token_endpoint, code=params["code"])
            client.token = token
            userinfo = client.get(userinfo_endpoint).json()
            st.session_state.user = userinfo

            # ✅ Clear query params and switch to main content
            st.query_params.clear()
            st.switch_page("pages/Home.py")

        except Exception as e:
            st.error(f"OAuth error: {e}")
            st.stop()

def login_button():
    auth_url = authorization_endpoint + "?" + urlencode({
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    })
    st.markdown(f"[Login with Google]({auth_url})")

def require_login():
    if "user" not in st.session_state:
        st.session_state.user = None

    if not st.session_state.user:
        handle_callback()
        login_button()
        st.stop()
