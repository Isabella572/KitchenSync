import db_utils as db
import streamlit as st
import random

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
    elif check_user_exists(name) and func == add_profile:
        st.error("User already exists")
        return False
    else:
        func(User(name, Diet_Requirements(*args, **kwargs)))
        return True


def profile_expander(add_new_profile: bool, user_name=None):
    profile_string = "Add profile" if add_new_profile else "Update profile"

    user = User("", Diet_Requirements())

    if not add_new_profile:
        user = db.get_profile(user_name)  #NOTE: doesn't allow two users with the same name
        # TODO: use ID instead of name

    lookup_table = user.requirements.lookup_table
    with st.expander(profile_string):
        user_name = st.text_input("Name", value=user.name)
        isKosher = st.checkbox(
            "Kosher", value=user.requirements.requirements_vector[lookup_table["isKosher"]],
            key=user_name+"kosher"
            )
        isHalal = st.checkbox(
            "Halal", value=user.requirements.requirements_vector[lookup_table["isHalal"]], key=user_name+"halal"
            )
        isVegetarian = st.checkbox(
            "Vegetarian", value=user.requirements.requirements_vector[lookup_table["isVegetarian"]], key=user_name+"veggie"
            )
        isVegan = st.checkbox(
            "Vegan", value=user.requirements.requirements_vector[lookup_table["isVegan"]], key=user_name+"vegan"
            )
        isPescatarian = st.checkbox(
            "Pescatarian", value=user.requirements.requirements_vector[lookup_table["isPescatarian"]], key=user_name+"pesc"
            )
        hasDairy = st.checkbox(
            "Dairy", value=user.requirements.requirements_vector[lookup_table["hasDairy"]], key=user_name+"dairy")
        hasCelery = st.checkbox("Celery", value=user.requirements.requirements_vector[lookup_table["hasCelery"]], key=user_name+"celery")
        hasGluten = st.checkbox("Gluten", value=user.requirements.requirements_vector[lookup_table["hasGluten"]], key=user_name+"gluten")
        hasCrustaceans = st.checkbox("Crustaceans", value=user.requirements.requirements_vector[lookup_table["hasCrustaceans"]], key=user_name+"crust")
        hasEggs = st.checkbox("Eggs", value=user.requirements.requirements_vector[lookup_table["hasEggs"]], key=user_name+"eggs")
        hasFish = st.checkbox("Fish", value=user.requirements.requirements_vector[lookup_table["hasFish"]], key=user_name+"fish")
        hasLupin = st.checkbox("Lupin", value=user.requirements.requirements_vector[lookup_table["hasLupin"]], key=user_name+"lupin")
        hasMolluscs = st.checkbox("Molluscs", value=user.requirements.requirements_vector[lookup_table["hasMolluscs"]], key=user_name+"molluscs")
        hasMustard = st.checkbox("Mustard", value=user.requirements.requirements_vector[lookup_table["hasMustard"]], key=user_name+"mustard")
        hasNuts = st.checkbox("Nuts", value=user.requirements.requirements_vector[lookup_table["hasNuts"]], key=user_name+"nuts")
        hasSesame = st.checkbox("Sesame", value=user.requirements.requirements_vector[lookup_table["hasSesame"]], key=user_name+"sesame")
        hasPeanuts = st.checkbox("Peanuts", value=user.requirements.requirements_vector[lookup_table["hasPeanuts"]], key=user_name+"peanuts")
        hasSoybeans = st.checkbox("Soybeans", value=user.requirements.requirements_vector[lookup_table["hasSoybeans"]], key=user_name+"soy")
        hasSulfurDioxide = st.checkbox("SulfurDioxide", value=user.requirements.requirements_vector[lookup_table["hasSulfurDioxide"]], key=user_name+"so2")

        if st.button(
            profile_string, key=(user_name if user_name else 'new_user') + str(add_new_profile)
            ):
            if add_or_update_profile(user_name, add_profile if add_new_profile else update_profile,
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
                st.rerun()