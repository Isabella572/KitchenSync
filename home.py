# this is home.py it is the home page (what you see first). it has the header, recommended for you, recipes using owned ingredients, and prev cooked recipes

import streamlit as st
import db_utils
import reccomender
import pandas as pd

#this formats the ingredients

def format_ingredients(ingredients_json):
    formatted = []

    data = db_utils.parse_structured_column(ingredients_json)

    for item in data:
        food = item.get("food", "")
        quantity = item.get("quantity", "")
        measure = item.get("measure", "")

        text = f"{quantity} {measure} {food}".strip()
        formatted.append((food.lower(), text))

    return formatted


#displays a single recipe 

def display_recipe_card(recipe_row, section=""):

    st.subheader(recipe_row["recipe_name"])
    st.write(f"Calories: {int(recipe_row['calories'])}")
    st.write(recipe_row["url"])

    ingredients = format_ingredients(recipe_row["ingredients"])

    with st.expander("Ingredients"):
        for _, text in ingredients:
            st.write(text)

    col1, col2, col3, col4 = st.columns(4)

    #favourites
    favourites = db_utils.get_favourites()
    if recipe_row["recipe_name"] in favourites:
        if col1.button("⭐ Remove Favourite", key=f"fav_{section}_{recipe_row['recipe_name']}"):
            db_utils.remove_favourite(recipe_row["recipe_name"])
            st.rerun()
    else:
        if col1.button("⭐ Favourite", key=f"fav_{section}_{recipe_row['recipe_name']}"):
            db_utils.add_favourite(recipe_row["recipe_name"])
            db_utils.add_user_action(recipe_row["recipe_name"], "favourite")
            st.rerun()


    #rating
    rating = col2.selectbox(
        "Rate",
        [1, 2, 3, 4, 5], key=f"rate_{section}_{recipe_row['recipe_name']}")

    if col2.button("Submit Rating", key=f"submit_{section}_{recipe_row['recipe_name']}"):
        db_utils.add_user_action(
            recipe_row["recipe_name"],
            "rated",
            rating)
        st.success("Rating saved")

    #marking it as cooked
    if col2.button("Mark as Cooked", key=f"cook_{section}_{recipe_row['recipe_name']}"):

        user_history = db_utils.get_user_history()

        rating_exists = user_history[
            (user_history["recipe_name"] == recipe_row["recipe_name"]) &
            (user_history["action"] == "rated")
        ]

        if rating_exists.empty:
            st.warning("You must rate this recipe before marking it as cooked.")
        else:
            db_utils.add_user_action(
                recipe_row["recipe_name"],
                "cooked",
                None
            )
            st.success("Recipe marked as cooked!")
            st.rerun()



    #genetates the shopping list of missing items
    if col4.button("Add Missing to Shopping List", key=f"shop_{section}_{recipe_row['recipe_name']}"):

        pantry_items = db_utils.get_all_pantry_items()
        pantry_names = [item[1].lower() for item in pantry_items]

        missing = []

        for ingredient in db_utils.parse_structured_column(recipe_row["ingredients"]):
            food = ingredient.get("food", "").lower()
            quantity = ingredient.get("quantity", 0)
            unit = ingredient.get("measure", "")

            if food and food not in pantry_names:
                missing.append((food, quantity, unit))

        for name, quantity, unit in missing:
            db_utils.add_to_shoppinglist(name, quantity, unit)

        if missing:
            st.success("Missing ingredients added")
        else:
            st.info("You already have all ingredients")

    st.divider()


#the home page

def home_page():

    st.title("KitchenSync")

    #load user requirements properly later
    from profile import get_current_user_requirements
    user_requirements = get_current_user_requirements()

    if "layer1_df" not in st.session_state or "layer2_df" not in st.session_state:
        layer1_df, layer2_df = reccomender.recommend_recipes(user_requirements)
        st.session_state["layer1_df"] = layer1_df
        st.session_state["layer2_df"] = layer2_df
    else:
        layer1_df = st.session_state["layer1_df"]
        layer2_df = st.session_state["layer2_df"]
    user_history = db_utils.get_user_history()


# 1st layer - recommended for you

    st.header("Recommended For You")

    if layer1_df.empty:
        st.info("No recipes match your preferences yet.")
    else:
        for _, row in layer1_df.head(5).iterrows():
            display_recipe_card(row)

#layer 2 - using ingredients already owned

    st.header("Using Your Ingredients")

    if not layer2_df.empty:
        high_pantry = layer2_df[
            layer2_df["layer2_score"] > 0.3
        ]

        for _, row in high_pantry.head(5).iterrows():
            display_recipe_card(row)

#layer three prev cookeed recipes

    st.header("Previously Cooked")

    if not user_history.empty:

        cooked = user_history[user_history["action"] == "cooked"]
        ratings = user_history[user_history["action"] == "rated"]

        if not cooked.empty:

            cooked_with_ratings = cooked.merge(
                ratings[["recipe_name", "rating"]],
                on="recipe_name",
                how="left"
            )

            #sort option
            sort_option = st.selectbox(
                "Sort by",
                ["Most Recent", "Highest Rating"]
            )

            if sort_option == "Most Recent":
                cooked_with_ratings = cooked_with_ratings.sort_values(
                    by="timestamp",
                    ascending=False
                )
            else:
                cooked_with_ratings = cooked_with_ratings.sort_values(
                    by="rating",
                    ascending=False
                )

            recipes_df = db_utils.load_recipes()

            for _, row in cooked_with_ratings.iterrows():

                recipe_name = row["recipe_name"]
                rating = row["rating"]

                match = recipes_df[
                    recipes_df["recipe_name"] == recipe_name
                ]

                if not match.empty:

                    display_recipe_card(match.iloc[0], section = "history")

                    #ratings
                    if pd.notna(rating):
                        stars = "⭐" * int(rating)
                        st.write(f"Your Rating: {stars}")

        else:
            st.info("You haven't cooked anything yet.")

    else:
        st.info("No history yet.")

