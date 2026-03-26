# this profile.py it handels the profile page and diet requirements logic

import streamlit as st
import db_utils
from diet_requirements import Diet_Requirements


def profile_row_to_requirements(row):
    #converts a raw database row into a diet_requirements object. the column indices match the order they were defined in initialise database
    return Diet_Requirements(isVegetarian=bool(row[2]),
        isVegan=bool(row[3]),
        isPescatarian=bool(row[4]),
        hasDairy=bool(row[5]),
        hasGluten=bool(row[6]),
        hasEggs=bool(row[7]),
        hasFish=bool(row[8]),
        hasShellfish=bool(row[9]),
        hasTreeNuts=bool(row[10]),
        hasPeanuts=bool(row[11]),
        hasSoy=bool(row[12]))


def get_current_user_requirements():

    selected_ids = st.session_state.get("selected_profile_ids", [])
    profiles = db_utils.get_all_profiles()

    #if no profiles exist or none are selected it returns empty requirements so no dietary filtering is applied and all recipes are shown
    if not profiles or not selected_ids:
        return Diet_Requirements()

    selected_profiles = [p for p in profiles if p[0] in selected_ids]

    if not selected_profiles:
        return Diet_Requirements()

    #a requirement is active if any selected profile has it. this is a strict safty approach
    combined = {"isVegetarian": False,"isVegan": False,
        "isPescatarian": False,
        "hasDairy": False,
        "hasGluten": False,
        "hasEggs": False,
        "hasFish": False,
        "hasShellfish": False,
        "hasTreeNuts": False,
        "hasPeanuts": False,
        "hasSoy": False,}

    keys = list(combined.keys())
    for profile in selected_profiles:
        for i, key in enumerate(keys):
            if bool(profile[i + 2]):
                combined[key] = True

    return Diet_Requirements(**combined)


def profile_page():
    st.title("Profiles")

    profiles = db_utils.get_all_profiles()

    #adds new profiles
    st.subheader("Add New Profile")
    with st.form("add_profile_form"):
        new_name = st.text_input("Profile Name (e.g. Mum, Dad)")
        is_guest = st.checkbox("Guest profile (temporary, can be cleared all at once)")
        if st.form_submit_button("Add Profile"):
            if new_name.strip() == "":
                st.warning("Please enter a name.")
            else:
                success = db_utils.add_profile(new_name.strip(), is_guest=is_guest)
                if success:
                    profile_type = "Guest profile" if is_guest else "Profile"
                    st.success(f"{profile_type} '{new_name}' added!")
                    st.rerun()
                else:
                    st.warning("A profile with that name already exists.")

    #only shows the clear guests button if at least one guest profile exists
    if any(p[-1] == 1 for p in db_utils.get_all_profiles()):
        st.markdown("---")
        if st.button("Remove all guest profiles"):
            db_utils.delete_guest_profiles()
            st.session_state.pop("layer1_df", None)
            st.session_state.pop("layer2_df", None)
            st.rerun()

    st.markdown("---")

    if not profiles:
        st.info("No profiles yet. Add one above.")
        return

    #existing profiles
    st.subheader("Existing Profiles")

    for profile in profiles:
        profile_id = profile[0]
        profile_name = profile[1]

        guest_label = " 👥 Guest" if profile[-1] == 1 else ""
        with st.expander(f"👤 {profile_name}{guest_label}"):

            #loads current values from the database row so checkboxes reflect what is already saved rather than defaulting to False
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
                    new_requirements = Diet_Requirements(isVegetarian=isVegetarian,
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
                    db_utils.update_profile(profile_id, new_requirements)
                    # clear cached recommendations so dietary filtering is recalculated with the updated profile the next time the user goes to the home page
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