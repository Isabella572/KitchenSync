#this is shoppinglist.py it does the shoppinglist page, generates shoppinglist from selected recipes

import streamlit as st
import db_utils
import json


#below are utility functions

#this returns a structured ingredient list
def extract_ingredients(recipe_row):

    ingredients_json = db_utils.parse_structured_column(recipe_row["ingredients"])
    extracted = []

    for item in ingredients_json:
        food = item.get("food", "").lower()
        quantity = item.get("quantity", 0)
        unit = item.get("measure", "")

        if food:
            extracted.append((food, quantity, unit))

    return extracted


def get_missing_ingredients(recipe_row):

    recipe_ingredients = extract_ingredients(recipe_row)
    pantry_items = db_utils.get_all_pantry_items()

    pantry_names = [item[1].lower() for item in pantry_items]
    missing = []

    for food, quantity, unit in recipe_ingredients:
        if food not in pantry_names:
            missing.append((food, quantity, unit))
    return missing


#shopping list page functuons

def shoppinglist_page():
    st.title("Shopping List")
    shopping_items = db_utils.get_shoppinglist()

    if not shopping_items:
        st.info("Your shopping list is empty.")
    else:
        for item in shopping_items:

            name = item[1]
            quantity = item[2]
            unit = item[3]
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"• {name.capitalize()} — {quantity} {unit}")
            with col2:
                if st.button("Remove", key=f"remove_shop_{item[0]}"):
                    db_utils.remove_shopping_item(item[0])
                    st.rerun()

        st.markdown("---")

        if st.button("Clear Entire List"):
            db_utils.clear_shoppinglist()
            st.rerun()
