import streamlit as st
import auth

st.set_page_config(page_title="CartoonFlix", page_icon="📺", layout="wide")
auth.require_login()
st.switch_page("pages/Home.py")  # Must exist as 'Home.py' inside pages/

#app.py
import streamlit as st
import auth

st.set_page_config(page_title="Dr Cartoon", page_icon="📺")

# Force login
auth.require_login()

# Once logged in, redirect to home
st.switch_page("home.py")

