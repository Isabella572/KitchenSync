# this is main.py it is the main page where i set up everything eg the sidebar and how it looks and it is the file that I run when running my code

import streamlit as st

import home
import pantry
import profile
import favourites
import shoppinglist
import db_utils
db_utils.initialise_database()

# the page setup
st.set_page_config(page_title="KitchenSync", layout="wide")


# some basic styling/making it look aesthetic
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


# what appears in the sidebar
st.sidebar.title("KitchenSync")
page = st.sidebar.radio("Menu",["Home","Pantry","Profile","Favourites","Shopping List"])

# this is routing for each page
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
