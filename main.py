#this is main.py which is the file that is run to start the app, it sets up the page config, initialiases database and handels the navigation between pages

import streamlit as st
import home
import pantry
import profile
import favourites
import shoppinglist
import db_utils

#initialise the database on every startup
db_utils.initialise_database()

st.set_page_config(page_title="KitchenSync", layout="wide")

#global CSS applied across all pages
st.markdown("""
<style>
    .title {
        font-size: 32px;
        font-weight: bold;
    }
    .section {
        margin-top: 30px;
    }
</style>
""", unsafe_allow_html=True)

st.sidebar.title("KitchenSync")
page = st.sidebar.radio("Menu", ["Home", "Pantry", "Profile", "Favourites", "Shopping List"])

#this routes to the correct page based on sidebar which gets clicked in the sidebar
if page == "Home":
    home.home_page()
elif page == "Pantry":
    pantry.pantry_page()
elif page == "Profile":
    profile.profile_page()
elif page == "Favourites":
    favourites.favourites_page()
elif page == "Shopping List":
    shoppinglist.shoppinglist_page()