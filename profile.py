# this is profile.py it is whetre the profiles get created, displays diet requirements and returns requirements to recommender

import streamlit as st
import db_utils
from diet_requirements import Diet_Requirements

#loads currennt requirements

def get_current_user_requirements():
    row = db_utils.load_user_profile()
    if row is None:
        return Diet_Requirements()

    return Diet_Requirements(
        isVegetarian=bool(row[1]),
        isVegan=bool(row[2]),
        isPescatarian=bool(row[3]),
        hasDairy=bool(row[4]),
        hasGluten=bool(row[5]),
        hasEggs=bool(row[6]),
        hasFish=bool(row[7]),
        hasShellfish=bool(row[8]),
        hasTreeNuts=bool(row[9]),
        hasPeanuts=bool(row[10]),
        hasSoy=bool(row[11]))


#profile page user interface

def profile_page():
    st.title("Your Dietary Profile")
    current = get_current_user_requirements()
    vec = current.requirements_vector
    lookup = current.lookup_table

    #prefrences
    st.subheader("Diet Type")
    isVegetarian = st.checkbox("Vegetarian", value=vec[lookup["isVegetarian"]])
    isVegan = st.checkbox("Vegan", value=vec[lookup["isVegan"]])
    isPescatarian = st.checkbox("Pescatarian", value=vec[lookup["isPescatarian"]])

    #allergic
    st.subheader("Allergies / Intolerances")
    hasDairy = st.checkbox("Dairy", value=vec[lookup["hasDairy"]])
    hasGluten = st.checkbox("Gluten", value=vec[lookup["hasGluten"]])
    hasEggs = st.checkbox("Eggs", value=vec[lookup["hasEggs"]])
    hasFish = st.checkbox("Fish", value=vec[lookup["hasFish"]])
    hasShellfish = st.checkbox("Shellfish", value=vec[lookup["hasShellfish"]])
    hasTreeNuts = st.checkbox("Tree Nuts", value=vec[lookup["hasTreeNuts"]])
    hasPeanuts = st.checkbox("Peanuts", value=vec[lookup["hasPeanuts"]])
    hasSoy = st.checkbox("Soy", value=vec[lookup["hasSoy"]])

    if st.button("Save Preferences"):

        new_requirements = Diet_Requirements(
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

        db_utils.save_user_profile(new_requirements)

        st.session_state.pop("layer1_df", None)
        st.session_state.pop("layer2_df", None)
        
        st.success("Preferences saved successfully.")
