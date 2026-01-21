import streamlit as st
import reccomender
import db_utils

def home():
    st.title("Home")
    st.subheader("For you")

    profiles = db_utils.get_all_profiles()

    if profiles:
        user = profiles[0]
        recs = reccomender.recommend_recipes(user.requirements)

        if recs.empty:
            st.info("No recipes matched your dietary preferences and pantry.")
            return

        for _, r in recs.iterrows():
            st.markdown(f"### {r['recipe_name']}")
            st.write(f"**Calories:** {int(r['calories'])}")
            st.write(", ".join(r["ingredient_lines"]) if isinstance(r["ingredient_lines"], list) else r["ingredient_lines"])
            st.write(r["url"])
            st.divider()

    else:
        st.info("No profiles found. Please create one in Settings.")

