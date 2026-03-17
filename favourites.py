# this is favourites.py it does the favourites page. it displays them and can also remove them

import streamlit as st
import db_utils
import pandas as pd


def favourites_page():
    st.title("Your Favourite Recipes")

    favourites = db_utils.get_favourites()

    if not favourites:
        st.info("You haven't added any favourites yet.")
        return

    recipes_df = db_utils.load_recipes()

    favourite_recipes = recipes_df[
        recipes_df["recipe_name"].isin(favourites)]
    for _, row in favourite_recipes.iterrows():

        st.markdown("---")
        st.subheader(row["recipe_name"])
        col1, col2 = st.columns([3, 1])

        with col1:
            st.write(f"Cuisine: {row['cuisine_type']}")
            st.write(f"Calories: {row['calories']}")
        with col2:
            if st.button("Remove", key=f"remove_fav_{row['recipe_name']}"):
                db_utils.remove_favourite(row["recipe_name"])
                st.rerun()
