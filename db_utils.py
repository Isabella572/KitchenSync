# this is db_utils.py it handels all the database intereaction for my website like table creation and all other files import from here so no other file touches the database directly

import sqlite3
import pandas as pd
from datetime import datetime
import streamlit as st
import ast


#the CSV with the recipes stores lists as stings eg ['vegan','glutenfree'...] so this converts them back into actual python lists so that they can be iterated
def parse_structured_column(value):
    try:
        if isinstance(value, list):
            return value
        return ast.literal_eval(value)
    except:
        return []


#this was added because without it every page interaction reloaded tens of thousands of rows which slowed down the website significantly
@st.cache_data
def load_recipes():
    df = pd.read_csv("recipes-with-nutrition.csv", engine="python", on_bad_lines="skip",)
    return df


DB_NAME = "food.db"


#this function creates all tables on the first run if they dont exist yet
def initialise_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS profiles (id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            isVegetarian INTEGER DEFAULT 0,
            isVegan INTEGER DEFAULT 0,
            isPescatarian INTEGER DEFAULT 0,
            hasDairy INTEGER DEFAULT 0,
            hasGluten INTEGER DEFAULT 0,
            hasEggs INTEGER DEFAULT 0,
            hasFish INTEGER DEFAULT 0,
            hasShellfish INTEGER DEFAULT 0,
            hasTreeNuts INTEGER DEFAULT 0,
            hasPeanuts INTEGER DEFAULT 0,
            hasSoy INTEGER DEFAULT 0,
            isGuest INTEGER DEFAULT 0)""")

    #I used alter table here instead of recreating it so that any existing user data is preserved when the app is updated
    try:
        cursor.execute("ALTER TABLE profiles ADD COLUMN isGuest INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass  

    cursor.execute("""CREATE TABLE IF NOT EXISTS pantry (id INTEGER PRIMARY KEY AUTOINCREMENT,
        item TEXT,
        quantity REAL,
        unit TEXT,
        expiry_date TEXT,
        category TEXT)""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS shoppinglist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ingredient_name TEXT,
        quantity REAL,
        unit TEXT,
        checked INTEGER DEFAULT 0)""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS favourites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recipe_name TEXT UNIQUE)""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS user_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recipe_name TEXT,
        action TEXT,
        rating INTEGER,
        timestamp TEXT)""")

    conn.commit()
    conn.close()


#pantry functions

def add_pantry_item(item, quantity, unit, expiry_date, category):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO pantry (item, quantity, unit, expiry_date, category)
        VALUES (?, ?, ?, ?, ?)
    """, (item, quantity, unit, expiry_date, category))
    conn.commit()
    conn.close()

def get_all_pantry_items():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pantry")
    items = cursor.fetchall()
    conn.close()
    return items

def delete_pantry_item(item_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pantry WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()


#shopping list functions

def get_shoppinglist():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM shoppinglist")
    items = cursor.fetchall()
    conn.close()
    return items

def add_to_shoppinglist(name, quantity, unit):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO shoppinglist (ingredient_name, quantity, unit)
        VALUES (?, ?, ?)
    """, (name, quantity, unit))
    conn.commit()
    conn.close()

def update_shopping_item(item_id, checked):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""UPDATE shoppinglist
        SET checked = ?
        WHERE id = ?
    """, (checked, item_id))
    conn.commit()
    conn.close()

def remove_shopping_item(item_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM shoppinglist WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

def edit_shopping_item(item_id, name, quantity, unit):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""UPDATE shoppinglist
        SET ingredient_name = ?, quantity = ?, unit = ?
        WHERE id = ?
    """, (name, quantity, unit, item_id))
    conn.commit()
    conn.close()

def clear_shoppinglist():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM shoppinglist")
    conn.commit()
    conn.close()


#favourites functions

def add_favourite(recipe_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""INSERT OR IGNORE INTO favourites (recipe_name)
        VALUES (?)
    """, (recipe_name,))
    conn.commit()
    conn.close()

def get_favourites():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT recipe_name FROM favourites")
    favs = [row[0] for row in cursor.fetchall()]
    conn.close()
    return favs

def remove_favourite(recipe_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""DELETE FROM favourites
        WHERE recipe_name = ?
    """, (recipe_name,))
    conn.commit()
    conn.close()


#user history/behaviour tracking functions

def add_user_action(recipe_name, action, rating=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    #the ratings are updated in place insteaf of adding a new row each time so only the most recent rating is used
    if action == "rated":
        cursor.execute("""SELECT id FROM user_history
            WHERE recipe_name = ? AND action = 'rated'
        """, (recipe_name,))
        existing = cursor.fetchone()

        if existing:
            cursor.execute("""UPDATE user_history
                SET rating = ?, timestamp = ?
                WHERE id = ?
            """, (rating, datetime.now().isoformat(), existing[0]))
            conn.commit()
            conn.close()
            return

    cursor.execute("""INSERT INTO user_history (recipe_name, action, rating, timestamp)
        VALUES (?, ?, ?, ?)
    """, (recipe_name, action, rating, datetime.now().isoformat()))

    conn.commit()
    conn.close()

def get_user_history():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT * FROM user_history", conn)
    conn.close()
    return df


#profile functions

def add_profile(name, is_guest=False):
    #this returns false if a profile with the same name already exists
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO profiles (name, isGuest) VALUES (?, ?)",
            (name, int(is_guest))
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_all_profiles():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profiles")
    profiles = cursor.fetchall()
    conn.close()
    return profiles

def update_profile(profile_id, requirements):
    #the values are pulled by name, not position, from lookup table so adding or re ordering feilds in diet requirements wont secretly write the wrong value to the wrong column
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    vec = requirements.requirements_vector
    lookup = requirements.lookup_table
    cursor.execute("""UPDATE profiles SET
            isVegetarian = ?,
            isVegan = ?,
            isPescatarian = ?,
            hasDairy = ?,
            hasGluten = ?,
            hasEggs = ?,
            hasFish = ?,
            hasShellfish = ?,
            hasTreeNuts = ?,
            hasPeanuts = ?,
            hasSoy = ?
        WHERE id = ?
    """, (int(vec[lookup["isVegetarian"]]),
        int(vec[lookup["isVegan"]]),
        int(vec[lookup["isPescatarian"]]),
        int(vec[lookup["hasDairy"]]),
        int(vec[lookup["hasGluten"]]),
        int(vec[lookup["hasEggs"]]),
        int(vec[lookup["hasFish"]]),
        int(vec[lookup["hasShellfish"]]),
        int(vec[lookup["hasTreeNuts"]]),
        int(vec[lookup["hasPeanuts"]]),
        int(vec[lookup["hasSoy"]]),
        profile_id))
    conn.commit()
    conn.close()

def delete_profile(profile_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
    conn.commit()
    conn.close()

def delete_guest_profiles():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM profiles WHERE isGuest = 1")
    conn.commit()
    conn.close()

def get_profile_by_id(profile_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profiles WHERE id = ?", (profile_id,))
    row = cursor.fetchone()
    conn.close()
    return row