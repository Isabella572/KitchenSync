import streamlit as st

from entities.diet_requirements import Diet_Requirements
from entities.user import User
from profile_utils import *

st.title("Active Profiles")

with st.expander("Add profile"):
    name = st.text_input("Name")
    isKosher = st.checkbox("Kosher")
    isHalal = st.checkbox("Halal")
    isVegetarian = st.checkbox("Vegetarian")
    isVegan = st.checkbox("Vegan")
    isPescatarian = st.checkbox("Pescatarian")
    hasDairy = st.checkbox("Dairy")
    hasCelery = st.checkbox("Celery")
    hasGluten = st.checkbox("Gluten")
    hasCrustaceans = st.checkbox("Crustaceans")
    hasEggs = st.checkbox("Eggs")
    hasFish = st.checkbox("Fish")
    hasLupin = st.checkbox("Lupin")
    hasMolluscs = st.checkbox("Molluscs")
    hasMustard = st.checkbox("Mustard")
    hasNuts = st.checkbox("Nuts")
    hasSesame =st.checkbox("Sesame")
    hasPeanuts = st.checkbox("Peanuts")
    hasSoybeans = st.checkbox("Soybeans")
    hasSulfurDioxide = st.checkbox("SulfurDioxide")

    st.button("Add profile", on_click=add_profile(User(name, Diet_Requirements(
        isKosher=isKosher,
        isHalal=isHalal,
        isVegetarian=isVegetarian,
        isVegan=isVegan,
        isPescatarian=isPescatarian,
        hasDairy=hasDairy,
        hasCelery=hasCelery,
        hasGluten=hasGluten,
        hasCrustaceans=hasCrustaceans,
        hasEggs=hasEggs,
        hasFish=hasFish,
        hasLupin=hasLupin,
        hasMolluscs=hasMolluscs,
        hasMustard=hasMustard,
        hasNuts=hasNuts,
        hasSesame =hasSesame,
        hasPeanuts=hasPeanuts,
        hasSoybeans=hasSoybeans,
        hasSulfurDioxide=hasSulfurDioxide

    ))))
