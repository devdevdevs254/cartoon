# app.py
import streamlit as st
import auth  # your custom Firebase auth module

st.set_page_config(
    page_title="Dr Cartoon",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Require login before proceeding
auth.require_login()

# Redirect to home (by page title, not filename)
st.switch_page("Home")
