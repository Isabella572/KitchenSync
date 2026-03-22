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
    user_history = db_utils.get_user_history()

    # build ratings dictionary
    ratings_dict = {}
    if not user_history.empty:
        rated = user_history[user_history["action"] == "rated"]
        if not rated.empty:
            for _, r in rated.iterrows():
                name = r["recipe_name"]
                val = r["rating"]
                if name not in ratings_dict or val > ratings_dict[name]:
                    ratings_dict[name] = val

    favourite_recipes = recipes_df[recipes_df["recipe_name"].isin(favourites)]

    for _, row in favourite_recipes.iterrows():

        st.markdown("---")
        st.subheader(row["recipe_name"])
        col1, col2 = st.columns([3, 1])

        with col1:
            st.write(f"Cuisine: {row['cuisine_type']}")
            st.write(f"Calories: {row['calories']}")

            # show rating if it exists
            recipe_rating = ratings_dict.get(row["recipe_name"])
            if recipe_rating is not None:
                stars = "⭐" * int(recipe_rating)
                st.write(f"Your Rating: {stars}")
            else:
                st.write("Not rated yet")

        with col2:
            if st.button("Remove", key=f"remove_fav_{row['recipe_name']}"):
                db_utils.remove_favourite(row["recipe_name"])
                st.rerun()