import streamlit as st
import db_utils as db

def pantry_page():
    st.title("My Pantry")

    with st.form("add_item"):
        name = st.text_input("Ingredient name")
        quantity = st.number_input("Quantity", min_value=0.0)
        units = st.text_input("Units (e.g. g, ml, pieces)")
        expiry = st.date_input("Expiry date")

        if st.form_submit_button("Add to pantry"):
            db.add_pantry_item(name, quantity, units, str(expiry))
            st.success("Item added")
            st.rerun()

    st.subheader("Current Pantry")

    items = db.get_all_pantry_items()

    for item in items:
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.write(item[0])
        col2.write(item[1])
        col3.write(item[2])
        col4.write(item[3])
        if col5.button("Delete", key=item[0]):
            db.delete_pantry_item(item[0])
            st.rerun()
