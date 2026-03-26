#this is home.py it is the mane homepage of the website and displays three layers of recipe suggestions:
#layer 1 = recommended for you (behaviour based personalisation)
#layer 2 = using your ingredients (pantry and expiry based)
# layer 3 = previously cooked (just history, no weighting/scoring)
#it also has a search bar, catagory filter and who is eating selector

import streamlit as st
import db_utils
import reccomender
import pandas as pd


def format_ingredients(ingredients_json):
    #this converts the ingredient data from the csv file to readable strings
    formatted = []
    data = db_utils.parse_structured_column(ingredients_json)

    for item in data:
        food = item.get("food", "")
        quantity = item.get("quantity", "")
        measure = item.get("measure", "")

        quantity = round(float(quantity), 2) if quantity else ""
        if measure == "<unit>" or measure is None:
            measure = ""
        text = f"{quantity} {measure} {food}".strip()
        formatted.append((food.lower(), text))

    return formatted


def display_recipe_card(recipe_row, section="", pantry_match=None, show_rating_controls=True):
    #this gives a each recipe an ingredient match colour coding, favourite, rating and shopping list button

    st.subheader(recipe_row["recipe_name"])

    #colour coded ingredient match indicator
    if pantry_match is not None:
        percentage = int(pantry_match * 100)
        if pantry_match == 1.0:
            colour = "green"
            label = f"You have all ingredients ({percentage}%)"
        elif pantry_match >= 0.1:
            colour = "orange"
            label = f"You have {percentage}% of ingredients"
        else:
            colour = "red"
            label = f"You have {percentage}% of ingredients"
        st.markdown(
            f"<span style='color:{colour}'>{label}</span>",
            unsafe_allow_html=True
        )

    st.write(f"Calories: {int(recipe_row['calories'])}")
    st.write(recipe_row["url"])

    ingredients = format_ingredients(recipe_row["ingredients"])
    with st.expander("Ingredients"):
        for _, text in ingredients:
            st.write(text)

    col1, col2, col3, col4 = st.columns(4)

    #favourites button and logs to user history so recommender can use it
    favourites = db_utils.get_favourites()
    if recipe_row["recipe_name"] in favourites:
        if col1.button("🔖 Remove Favourite", key=f"fav_{section}_{recipe_row['recipe_name']}"):
            db_utils.remove_favourite(recipe_row["recipe_name"])
            st.rerun()
    else:
        if col1.button("🔖 Favourite", key=f"fav_{section}_{recipe_row['recipe_name']}"):
            db_utils.add_favourite(recipe_row["recipe_name"])
            db_utils.add_user_action(recipe_row["recipe_name"], "favourite")
            st.rerun()

    if show_rating_controls:
        rating = col2.selectbox(
            "Rate",
            [1, 2, 3, 4, 5], key=f"rate_{section}_{recipe_row['recipe_name']}")

        if col2.button("Submit Rating", key=f"submit_{section}_{recipe_row['recipe_name']}"):
            db_utils.add_user_action(
                recipe_row["recipe_name"],
                "rated",
                rating)
            st.success("Rating saved")

        #marking a recipe as cooked needs a rating first so the recommender always has a rating to work with when it sees a cooked recipe
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

    #this adds only the ingredients the user doesnt already own in their pantry to the shopping list
    # it also has the recommender count this as intent to cook
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
            db_utils.add_user_action(recipe_row["recipe_name"], "shopping_list")
            st.success("Missing ingredients added")
        else:
            st.info("You already have all ingredients")

    st.divider()


def display_layer(df, section, initial_count=5):
    #each layer at first only shows five at a time to allow the user to scroll to the next layer quickly
    #there is load more / show less buttons to show or hide more recipes on a specific layer
    if df.empty:
        st.info("No recipes found.")
        return

    count_key = f"show_count_{section}"
    if count_key not in st.session_state:
        st.session_state[count_key] = initial_count

    recipes_to_show = df.head(st.session_state[count_key])

    for _, row in recipes_to_show.iterrows():
        display_recipe_card(row, section=section, pantry_match=row.get("pantry_match"))

    col1, col2 = st.columns(2)
    with col1:
        if st.session_state[count_key] < len(df):
            if st.button("Load More ▼", key=f"load_more_{section}"):
                st.session_state[count_key] += 5
                st.rerun()
    with col2:
        if st.session_state[count_key] > initial_count:
            if st.button("Show Less ▲", key=f"show_less_{section}"):
                st.session_state[count_key] = max(initial_count, st.session_state[count_key] - 5)
                st.rerun()


def filter_by_category(df, selected_category):
    # returns the full dataframe unchanged if all is selected otherwise it filters to the chosen catagory
    if selected_category == "All":
        return df
    return df[df["meal_type"].apply(
        lambda x: selected_category.lower() in [m.lower() for m in db_utils.parse_structured_column(x)])]

def home_page():

    st.title("KitchenSync")
    search_query = st.text_input("🔍 Search recipes by name", "").strip().lower()

    all_categories = ["All", "Breakfast", "Lunch/Dinner", "Snack", "Brunch"]
    selected_category = st.selectbox("Filter by category", all_categories)

    #who is eating selects profile ids so that the diet filter can be customise
    profiles = db_utils.get_all_profiles()
    if profiles:
        profile_names = [p[1] for p in profiles]
        profile_ids = [p[0] for p in profiles]
        selected_names = st.multiselect("Who is eating?",
            profile_names,
            default=[])
        st.session_state["selected_profile_ids"] = [profile_ids[profile_names.index(name)] for name in selected_names]

        #wipes cached recommendations whenever the profile selection changes
        if st.session_state.get("last_selected_profiles") != selected_names:
            st.session_state.pop("layer1_df", None)
            st.session_state.pop("layer2_df", None)
            st.session_state["last_selected_profiles"] = selected_names
    else:
        st.info("No profiles set up yet. Go to the Profile page to add one.")

    from profile import get_current_user_requirements
    user_requirements = get_current_user_requirements()

    #recommendations are cached so the scoring algorithem doesnr run again on every interaction
    if "layer1_df" not in st.session_state or "layer2_df" not in st.session_state:
        layer1_df, layer2_df = reccomender.recommend_recipes(user_requirements)
        st.session_state["layer1_df"] = layer1_df
        st.session_state["layer2_df"] = layer2_df
    else:
        layer1_df = st.session_state["layer1_df"]
        layer2_df = st.session_state["layer2_df"]

    user_history = db_utils.get_user_history()

    #layer one
    st.header("Recommended For You")

    if layer1_df.empty:
        st.info("No recipes match your preferences yet.")
    else:
        layer1_filtered = filter_by_category(layer1_df, selected_category)
        if search_query:
            layer1_filtered = layer1_filtered[
                layer1_filtered["recipe_name"].str.lower().str.contains(search_query, na=False)
            ]
        if layer1_filtered.empty:
            st.info("No recipes found matching your search or category.")
        else:
            display_layer(layer1_filtered, section="layer1")

    #layer 2
    st.header("Using Your Ingredients")

    if layer2_df.empty:
        st.info("No recipes match your preferences yet.")
    else:
        high_pantry = filter_by_category(layer2_df, selected_category)
        if search_query:
            high_pantry = high_pantry[
                high_pantry["recipe_name"].str.lower().str.contains(search_query, na=False)
            ]
        if high_pantry.empty:
            st.info("No recipes found matching your search or category.")
        else:
            display_layer(high_pantry, section="layer2")

    #layer 3
    st.header("Previously Cooked")

    if not user_history.empty:
        cooked = user_history[user_history["action"] == "cooked"]
        ratings = user_history[user_history["action"] == "rated"]

        if not cooked.empty:
            #thi is so that each recipe only appears once even if cooked multiple times
            cooked_unique = cooked.drop_duplicates(subset="recipe_name", keep="first").copy()

            #builds rating lookup separately instead of merging dataframes
            ratings_dict = {}
            if not ratings.empty:
                for _, r in ratings.iterrows():
                    name = r["recipe_name"]
                    val = r["rating"]
                    if name not in ratings_dict or val > ratings_dict[name]:
                        ratings_dict[name] = val

            cooked_unique["rating"] = cooked_unique["recipe_name"].map(ratings_dict)

            sort_option = st.selectbox("Sort by", ["Most Recent", "Highest Rating"])

            if sort_option == "Most Recent":
                cooked_unique = cooked_unique.sort_values(by="timestamp", ascending=False)
            else:
                cooked_unique["rating"] = pd.to_numeric(cooked_unique["rating"], errors="coerce")
                cooked_unique = cooked_unique.sort_values(by="rating", ascending=False, na_position="last")

            cooked_unique = cooked_unique.reset_index(drop=True)
            recipes_df = db_utils.load_recipes()

            for _, row in cooked_unique.iterrows():
                recipe_name = row["recipe_name"]
                rating = row["rating"] if pd.notna(row["rating"]) else None
                match = recipes_df[recipes_df["recipe_name"] == recipe_name]

                if not match.empty:
                    display_recipe_card(match.iloc[0], section="history", show_rating_controls=False)

                    if rating is not None:
                        col_stars, col_edit = st.columns([3, 1])
                        with col_stars:
                            stars = "⭐" * int(rating)
                            st.write(f"Your Rating: {stars}")
                        with col_edit:
                            if st.button("Edit", key=f"toggle_edit_{recipe_name}"):
                                st.session_state[f"editing_{recipe_name}"] = not st.session_state.get(f"editing_{recipe_name}", False)
                        if st.session_state.get(f"editing_{recipe_name}", False):
                            new_rating = st.selectbox("New Rating",
                                [1, 2, 3, 4, 5],
                                index=int(rating) - 1,
                                key=f"edit_rate_{recipe_name}")
                            if st.button("Save", key=f"update_rate_{recipe_name}"):
                                db_utils.add_user_action(recipe_name, "rated", new_rating)
                                st.session_state[f"editing_{recipe_name}"] = False
                                st.success("Rating updated!")
                                st.rerun()
                    else:
                        st.write("Not rated yet")
        else:
            st.info("You haven't cooked anything yet.")
    else:
        st.info("No history yet.")