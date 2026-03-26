#this is shoppinglist.py it handles the shopping list page where items are added automatically from recipes in home
#users can also add items manually, edit them and remove them and mark them as bought so they go to the pantry

import streamlit as st
import db_utils


def extract_ingredients(recipe_row):
    #parses structured ingredient json from a recipe row and returns a flat list of food, quantity, unit tuples for easy comparison
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
    #this compares a recipes ingredients against the pantry and returns only the ones the user doesn't already own
    recipe_ingredients = extract_ingredients(recipe_row)
    pantry_items = db_utils.get_all_pantry_items()
    pantry_names = [item[1].lower() for item in pantry_items]
    missing = []
    for food, quantity, unit in recipe_ingredients:
        if food not in pantry_names:
            missing.append((food, quantity, unit))
    return missing


def shoppinglist_page():
    st.title("Shopping List")

    #manual add
    st.subheader("Add an Item Manually")
    with st.form("manual_add_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            new_name = st.text_input("Ingredient Name")
        with col2:
            new_quantity = st.number_input("Quantity", min_value=0.0, step=0.1)
        with col3:
            new_unit = st.text_input("Unit (e.g. g, ml, cups)")
        if st.form_submit_button("Add to List"):
            if new_name.strip() == "":
                st.warning("Please enter an ingredient name.")
            else:
                db_utils.add_to_shoppinglist(
                    new_name.strip().lower(),
                    new_quantity,
                    new_unit.strip().lower()
                )
                st.rerun()

    st.markdown("---")

    #shoping list items
    shopping_items = db_utils.get_shoppinglist()

    if not shopping_items:
        st.info("Your shopping list is empty.")
    else:
        for item in shopping_items:
            item_id = item[0]
            name = item[1]
            quantity = item[2]
            unit = item[3]

            with st.expander(f" {name.capitalize()} — {round(quantity, 2)} {unit}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    edited_name = st.text_input("Name", value=name, key=f"edit_name_{item_id}")
                with col2:
                    edited_quantity = st.number_input("Quantity", value=float(quantity),
                        min_value=0.0, step=0.1,
                        key=f"edit_qty_{item_id}")
                with col3:
                    edited_unit = st.text_input("Unit", value=unit, key=f"edit_unit_{item_id}")

                col4, col5 = st.columns(2)
                with col4:
                    if st.button("Save Changes", key=f"save_{item_id}"):
                        db_utils.edit_shopping_item(item_id,
                            edited_name.strip().lower(),
                            edited_quantity,
                            edited_unit.strip().lower())
                        st.rerun()
                with col5:
                    if st.button("Remove", key=f"remove_shop_{item_id}"):
                        db_utils.remove_shopping_item(item_id)
                        st.rerun()

            # ticking the bought checkbox makes you confirm quantity and set expiry before moving the item into the pantry
            bought = st.checkbox(f"Bought {name.capitalize()}", key=f"bought_{item_id}")

            if bought:
                col1, col2 = st.columns(2)
                with col1:
                    bought_quantity = st.number_input("Quantity bought",
                        min_value=0.0,
                        step=0.1,
                        value=float(quantity),
                        key=f"bought_qty_{item_id}")
                with col2:
                    bought_unit = st.text_input("Unit",
                        value=unit,
                        key=f"bought_unit_{item_id}")

                col3, col4 = st.columns(2)
                with col3:
                    bought_expiry = st.date_input("Expiry Date",
                        key=f"bought_expiry_{item_id}")
                with col4:
                    bought_category = st.selectbox("Category",
                        ["Vegetable", "Fruit", "Dairy", "Protein", "Grain", "Other"],
                        key=f"bought_cat_{item_id}")

                #confirming moves the item from shopping list to pantry and removes it from the list so it doesnt appear twice
                if st.button(f"Add {name.capitalize()} to Pantry", key=f"confirm_bought_{item_id}"):
                    db_utils.add_pantry_item(name,
                        bought_quantity,
                        bought_unit,
                        bought_expiry.isoformat(),
                        bought_category)
                    db_utils.remove_shopping_item(item_id)
                    st.success(f"{name.capitalize()} added to pantry!")
                    st.rerun()

        st.markdown("---")
        if st.button("Clear Entire List"):
            db_utils.clear_shoppinglist()
            st.rerun()