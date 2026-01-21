import streamlit as st
import home
import pantry
import profile
import settings

st.set_page_config(page_title="KitchenSync", layout="wide")

st.sidebar.title("KitchenSync")
page = st.sidebar.radio("Go to", ["Home", "Pantry", "Profile", "Settings"])

if page == "Home":
    home.home()
elif page == "Pantry":
    pantry.pantry_page()
elif page == "Profile":
    profile.profile_page()
elif page == "Settings":
    settings.settings_page()

