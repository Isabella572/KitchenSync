import time
import db_utils as db
import streamlit as st
import random

from entities.diet_requirements import Diet_Requirements
from entities.user import User


def add_profile(profile: User):
    db.add_profile(profile)


def update_profile(profile: User):
    db.update_profile(profile)


def get_all_profiles() -> list[User]:
    return db.get_all_profiles()


def check_user_exists(id: int, name: str) -> bool:
    return db.check_user_exists(id, name)


def add_or_update_profile(user, func) -> bool:
    if user.name is None or user.name == "":
        st.error("Please enter a name")
        return False
    elif check_user_exists(user.id, user.name):
        st.error("User already exists")
        return False
    else:
        func(user)
        return True
    

def delete_profile(user) -> bool:
    try:
        db.delete_profile(user)
        return True
    except:
        return False


def profile_expander(add_new_profile: bool, user_name=None):
    profile_string = "Add profile" if add_new_profile else "Update profile"

    user = User(-1, "", Diet_Requirements())

    if not add_new_profile:
        user = db.get_profile(user_name)  #NOTE: doesn't allow two users with the same name
        # TODO: use ID instead of name

    if user_name is None:
        user_name = ""
    lookup_table = user.requirements.lookup_table
    with st.expander(profile_string):
        user_name = st.text_input("Name", value=user.name)
        isVegetarian = st.checkbox(
            "Vegetarian", value=user.requirements.requirements_vector[lookup_table["isVegetarian"]], key=user.name+"veggie"+str(add_new_profile)
            )
        isVegan = st.checkbox(
            "Vegan", value=user.requirements.requirements_vector[lookup_table["isVegan"]], key=user.name+"vegan"+str(add_new_profile)
            )
        isPescatarian = st.checkbox(
            "Pescatarian", value=user.requirements.requirements_vector[lookup_table["isPescatarian"]], key=user_name+"pesc"+str(add_new_profile)
            )
        hasDairy = st.checkbox(
            "Dairy", value=user.requirements.requirements_vector[lookup_table["hasDairy"]], key=user_name+"dairy"+str(add_new_profile))
        hasGluten = st.checkbox("Gluten", value=user.requirements.requirements_vector[lookup_table["hasGluten"]], key=user_name+"gluten"+str(add_new_profile))
        hasEggs = st.checkbox("Eggs", value=user.requirements.requirements_vector[lookup_table["hasEggs"]], key=user_name+"eggs"+str(add_new_profile))
        hasFish = st.checkbox("Fish", value=user.requirements.requirements_vector[lookup_table["hasFish"]], key=user_name+"fish"+str(add_new_profile))
        hasShellfish = st.checkbox("Shellfish", value=user.requirements.requirements_vector[lookup_table["hasShellfish"]], key=user_name+"Shellfish"+str(add_new_profile))
        hasTreeNuts = st.checkbox("TreeNuts", value=user.requirements.requirements_vector[lookup_table["hasTreeNuts"]], key=user_name+"Treenuts"+str(add_new_profile))
        hasPeanuts = st.checkbox("Peanuts", value=user.requirements.requirements_vector[lookup_table["hasPeanuts"]], key=user_name+"peanuts"+str(add_new_profile))
        hasSoy = st.checkbox("Soy", value=user.requirements.requirements_vector[lookup_table["hasSoy"]], key=user_name+"soy"+str(add_new_profile))

        user.name = user_name
        user.requirements = Diet_Requirements(
                                     isVegetarian=isVegetarian,
                                     isVegan=isVegan,
                                     isPescatarian=isPescatarian,
                                     hasDairy=hasDairy,
                                     hasGluten=hasGluten,
                                     hasEggs=hasEggs,
                                     hasFish=hasFish,
                                     hasShellfish=hasShellfish,
                                     hasTreeNuts=hasTreeNuts,
                                     hasPeanuts=hasPeanuts,
                                     hasSoy=hasSoy)

        if st.button(
            profile_string, key=(user_name if user_name else 'new_user') + str(add_new_profile)
            ):
            if add_or_update_profile(user, add_profile if add_new_profile else update_profile):
                st.success("Profile Saved")
                time.sleep(1)
                st.rerun()
        if not add_new_profile:
            if st.button("Delete profile", key=user_name + 'delete'):
                if delete_profile(user):
                    st.success("Profile deleted")
                    time.sleep(1)
                    st.rerun()
