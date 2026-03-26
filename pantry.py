#this is pantry.py which is where the user manages the ingredients they own. the pantry data feeds diectily to the pantry match and expiry scores for the recommender

import streamlit as st
import db_utils
from datetime import datetime

def pantry_page():

    st.title("Your Pantry")
    st.markdown("Add ingredients you currently own.")

    #to add ingredients
    with st.form("add_ingredient_form"):

        col1, col2, col3 = st.columns(3)
        with col1:
            ingredient_name = st.text_input("Ingredient Name")
        with col2:
            quantity = st.number_input("Quantity", min_value=0.0, step=0.1)
        with col3:
            unit = st.text_input("Unit (e.g. g, ml, cups)")

        col4, col5 = st.columns(2)
        with col4:
            expiry_date = st.date_input("Expiry Date")
        with col5:
            category = st.selectbox("Category",["Vegetable", "Fruit", "Dairy", "Protein", "Grain", "Other"])

        submitted = st.form_submit_button("Add to Pantry")

        if submitted:
            if ingredient_name.strip() == "":
                st.warning("Please enter an ingredient name.")
            else:
                db_utils.add_pantry_item(ingredient_name.strip().lower(),quantity,
                    unit.strip().lower(),
                    expiry_date.isoformat(),
                    category)
                #clears cached recommendations so scores recalculate with the updates pantry everytime you go back to home
                st.session_state.pop("layer1_df", None)
                st.session_state.pop("layer2_df", None)
                st.success(f"{ingredient_name} added to pantry.")

    #displays the current pantry
    st.markdown("---")
    st.subheader("Current Pantry Items")
    pantry_items = db_utils.get_all_pantry_items()

    if not pantry_items:
        st.info("Your pantry is currently empty.")
        return

    for item in pantry_items:

        item_id = item[0]
        name = item[1]
        quantity = item[2]
        unit = item[3]

        col1, col2 = st.columns([4, 1])
        with col1:
            if item[4]:
                #calculate days remaining and apply colour coding
                days_left = (datetime.fromisoformat(item[4]) - datetime.now()).days
                days_left += 1

                if days_left <= 0:
                    colour = "red"
                    expiry_text = "Expires TODAY" if days_left == 0 else "EXPIRED"
                elif days_left <= 2:
                    colour = "orange"
                    expiry_text = f"Expires in {days_left} day(s)"
                else:
                    colour = "green"
                    expiry_text = f"Expires in {days_left} day(s)"

                st.markdown(f"<span style='color:{colour}'>"
                    f"{name.capitalize()} — {quantity} {unit} "
                    f"({expiry_text})"
                    f"</span>",
                    unsafe_allow_html=True)
            else:
                st.write(f"{name.capitalize()} — {quantity} {unit}")

        with col2:
            if st.button("Remove", key=f"remove_{item_id}"):
                db_utils.delete_pantry_item(item_id)
                #clears cached recommendations for the same reason as on add
                st.session_state.pop("layer1_df", None)
                st.session_state.pop("layer2_df", None)
                st.rerun()