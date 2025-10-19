import db_utils as db
import streamlit as st

from entities.diet_requirements import Diet_Requirements
from entities.user import User


def add_profile(profile: User):
    db.add_profile(profile)


def update_profile(profile: User):
    db.update_profile(profile)


def get_all_profiles():
    return db.get_all_profiles()


def check_user_exists(name: str) -> bool:
    return db.check_user_exists(name)


def add_or_update_profile(name, func, *args, **kwargs) -> bool:
    if name is None or name is "":
        st.error("Please enter a name")
        return False
    elif check_user_exists(name):
        st.error("User already exists")
        return False
    else:
        func(User(name, Diet_Requirements(*args, **kwargs)))
        return True


def profile_expander(add_new_profile: bool, name=None):
    profile_string = "Add profile" if add_new_profile else "Update profile"

    user = User("", Diet_Requirements())

    if not add_new_profile:
        user = db.get_profile

    with st.expander(profile_string):
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
        hasSesame = st.checkbox("Sesame")
        hasPeanuts = st.checkbox("Peanuts")
        hasSoybeans = st.checkbox("Soybeans")
        hasSulfurDioxide = st.checkbox("SulfurDioxide")

        if st.button(profile_string):
            if add_or_update_profile(name, add_profile if add_new_profile else update_profile,
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
                                     hasSesame=hasSesame,
                                     hasPeanuts=hasPeanuts,
                                     hasSoybeans=hasSoybeans,
                                     hasSulfurDioxide=hasSulfurDioxide
                                     ):
                st.success("Profile added")