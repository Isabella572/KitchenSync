# this is profile.py - handles multiple profiles, each with their own dietary requirements

import streamlit as st
import db_utils
from diet_requirements import Diet_Requirements


def profile_row_to_requirements(row):
    return Diet_Requirements(
        isVegetarian=bool(row[2]),
        isVegan=bool(row[3]),
        isPescatarian=bool(row[4]),
        hasDairy=bool(row[5]),
        hasGluten=bool(row[6]),
        hasEggs=bool(row[7]),
        hasFish=bool(row[8]),
        hasShellfish=bool(row[9]),
        hasTreeNuts=bool(row[10]),
        hasPeanuts=bool(row[11]),
        hasSoy=bool(row[12])
    )


def get_current_user_requirements():
    # get selected profile ids from session state
    selected_ids = st.session_state.get("selected_profile_ids", [])
    profiles = db_utils.get_all_profiles()

    if not profiles:
        return Diet_Requirements()

    # if none selected use all profiles
    if not selected_ids:
        return Diet_Requirements()
    else:
        selected_profiles = [p for p in profiles if p[0] in selected_ids]

    if not selected_profiles:
        return Diet_Requirements()

    # combine requirements across all selected profiles
    # if ANY profile has a requirement, it applies to everyone
    combined = {
        "isVegetarian": False,
        "isVegan": False,
        "isPescatarian": False,
        "hasDairy": False,
        "hasGluten": False,
        "hasEggs": False,
        "hasFish": False,
        "hasShellfish": False,
        "hasTreeNuts": False,
        "hasPeanuts": False,
        "hasSoy": False,
    }

    keys = list(combined.keys())
    for profile in selected_profiles:
        for i, key in enumerate(keys):
            if bool(profile[i + 2]):
                combined[key] = True

    return Diet_Requirements(**combined)


def profile_page():
    st.title("Profiles")

    profiles = db_utils.get_all_profiles()

    # add new profile
    st.subheader("Add New Profile")
    with st.form("add_profile_form"):
        new_name = st.text_input("Profile Name (e.g. Mum, Dad, Guest)")
        if st.form_submit_button("Add Profile"):
            if new_name.strip() == "":
                st.warning("Please enter a name.")
            else:
                success = db_utils.add_profile(new_name.strip())
                if success:
                    st.success(f"Profile '{new_name}' added!")
                    st.rerun()
                else:
                    st.warning("A profile with that name already exists.")

    st.markdown("---")

    # show existing profiles
    if not profiles:
        st.info("No profiles yet. Add one above.")
        return

    st.subheader("Existing Profiles")

    for profile in profiles:
        profile_id = profile[0]
        profile_name = profile[1]

        with st.expander(f"👤 {profile_name}"):
            current = profile_row_to_requirements(profile)
            vec = current.requirements_vector
            lookup = current.lookup_table

            st.write("**Diet Type**")
            isVegetarian = st.checkbox("Vegetarian", value=vec[lookup["isVegetarian"]], key=f"veg_{profile_id}")
            isVegan = st.checkbox("Vegan", value=vec[lookup["isVegan"]], key=f"vegan_{profile_id}")
            isPescatarian = st.checkbox("Pescatarian", value=vec[lookup["isPescatarian"]], key=f"pesc_{profile_id}")

            st.write("**Allergies / Intolerances**")
            hasDairy = st.checkbox("Dairy", value=vec[lookup["hasDairy"]], key=f"dairy_{profile_id}")
            hasGluten = st.checkbox("Gluten", value=vec[lookup["hasGluten"]], key=f"gluten_{profile_id}")
            hasEggs = st.checkbox("Eggs", value=vec[lookup["hasEggs"]], key=f"eggs_{profile_id}")
            hasFish = st.checkbox("Fish", value=vec[lookup["hasFish"]], key=f"fish_{profile_id}")
            hasShellfish = st.checkbox("Shellfish", value=vec[lookup["hasShellfish"]], key=f"shell_{profile_id}")
            hasTreeNuts = st.checkbox("Tree Nuts", value=vec[lookup["hasTreeNuts"]], key=f"nuts_{profile_id}")
            hasPeanuts = st.checkbox("Peanuts", value=vec[lookup["hasPeanuts"]], key=f"peanuts_{profile_id}")
            hasSoy = st.checkbox("Soy", value=vec[lookup["hasSoy"]], key=f"soy_{profile_id}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save", key=f"save_{profile_id}"):
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
                        hasSoy=hasSoy
                    )
                    db_utils.update_profile(profile_id, new_requirements)
                    st.session_state.pop("layer1_df", None)
                    st.session_state.pop("layer2_df", None)
                    st.success("Saved!")
                    st.rerun()
            with col2:
                if st.button("Delete Profile", key=f"delete_{profile_id}"):
                    db_utils.delete_profile(profile_id)
                    st.session_state.pop("layer1_df", None)
                    st.session_state.pop("layer2_df", None)
                    st.rerun()