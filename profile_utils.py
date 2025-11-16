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
        isKosher = st.checkbox(
            "Kosher", value=user.requirements.requirements_vector[lookup_table["isKosher"]],
            key=user.name+"kosher"+str(add_new_profile)
            )
        isHalal = st.checkbox(
            "Halal", value=user.requirements.requirements_vector[lookup_table["isHalal"]], key=user.name+"halal"+str(add_new_profile)
            )
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
        hasCelery = st.checkbox("Celery", value=user.requirements.requirements_vector[lookup_table["hasCelery"]], key=user_name+"celery"+str(add_new_profile))
        hasGluten = st.checkbox("Gluten", value=user.requirements.requirements_vector[lookup_table["hasGluten"]], key=user_name+"gluten"+str(add_new_profile))
        hasCrustaceans = st.checkbox("Crustaceans", value=user.requirements.requirements_vector[lookup_table["hasCrustaceans"]], key=user_name+"crust"+str(add_new_profile))
        hasEggs = st.checkbox("Eggs", value=user.requirements.requirements_vector[lookup_table["hasEggs"]], key=user_name+"eggs"+str(add_new_profile))
        hasFish = st.checkbox("Fish", value=user.requirements.requirements_vector[lookup_table["hasFish"]], key=user_name+"fish"+str(add_new_profile))
        hasLupin = st.checkbox("Lupin", value=user.requirements.requirements_vector[lookup_table["hasLupin"]], key=user_name+"lupin"+str(add_new_profile))
        hasMolluscs = st.checkbox("Molluscs", value=user.requirements.requirements_vector[lookup_table["hasMolluscs"]], key=user_name+"molluscs"+str(add_new_profile))
        hasMustard = st.checkbox("Mustard", value=user.requirements.requirements_vector[lookup_table["hasMustard"]], key=user_name+"mustard"+str(add_new_profile))
        hasNuts = st.checkbox("Nuts", value=user.requirements.requirements_vector[lookup_table["hasNuts"]], key=user_name+"nuts"+str(add_new_profile))
        hasSesame = st.checkbox("Sesame", value=user.requirements.requirements_vector[lookup_table["hasSesame"]], key=user_name+"sesame"+str(add_new_profile))
        hasPeanuts = st.checkbox("Peanuts", value=user.requirements.requirements_vector[lookup_table["hasPeanuts"]], key=user_name+"peanuts"+str(add_new_profile))
        hasSoybeans = st.checkbox("Soybeans", value=user.requirements.requirements_vector[lookup_table["hasSoybeans"]], key=user_name+"soy"+str(add_new_profile))
        hasSulfurDioxide = st.checkbox("SulfurDioxide", value=user.requirements.requirements_vector[lookup_table["hasSulfurDioxide"]], key=user_name+"so2"+str(add_new_profile))

        user.name = user_name
        user.requirements = Diet_Requirements(isKosher=isKosher,
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
                                     hasSulfurDioxide=hasSulfurDioxide)

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
