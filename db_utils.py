# this is db_utils.py it handles all database interaction like creating tables, panty / shoppinglist / favourites managment , ratings etc.

import sqlite3
import pandas as pd
from datetime import datetime
import streamlit as st
import ast

def parse_structured_column(value):
    try:
        if isinstance(value, list):
            return value
        return ast.literal_eval(value)
    except:
        return []

#cacheing the recipes to make code faster
@st.cache_data
def load_recipes():
    df = pd.read_csv(
        "recipes-with-nutrition.csv",
        engine="python",
        on_bad_lines="skip",
    )
    return df


DB_NAME = "food.db"

#this creates the tables i need if they do not already exist. it doesnt modify the recipes table
def initialise_database():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    #user profile table that stores dietary requirements
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_profile (
            id INTEGER PRIMARY KEY,
            isVegetarian INTEGER,
            isVegan INTEGER,
            isPescatarian INTEGER,
            hasDairy INTEGER,
            hasGluten INTEGER,
            hasEggs INTEGER,
            hasFish INTEGER,
            hasShellfish INTEGER,
            hasTreeNuts INTEGER,
            hasPeanuts INTEGER,
            hasSoy INTEGER
        )
    """)


    #pantry table
    cursor.execute("""CREATE TABLE IF NOT EXISTS pantry (id INTEGER PRIMARY KEY AUTOINCREMENT,
        item TEXT,
        quantity REAL,
        unit TEXT,
        expiry_date TEXT,
        category TEXT)""")


    #shopping list table
    cursor.execute("""CREATE TABLE IF NOT EXISTS shoppinglist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingredient_name TEXT,
    quantity REAL,
    unit TEXT,
    checked INTEGER DEFAULT 0)""")

    #favourites table
    cursor.execute("""CREATE TABLE IF NOT EXISTS favourites (id INTEGER PRIMARY KEY AUTOINCREMENT,
        recipe_name TEXT UNIQUE)""")

    #user history table for behaviour tracking
    cursor.execute("""CREATE TABLE IF NOT EXISTS user_history (id INTEGER PRIMARY KEY AUTOINCREMENT,
        recipe_name TEXT,
        action TEXT,
        rating INTEGER,
        timestamp TEXT)""")

    conn.commit()
    conn.close()


#below are all the pantry functions

def add_pantry_item(item, quantity, unit, expiry_date, category):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO pantry (item, quantity, unit, expiry_date, category)
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


#below are all the shoppinglist functions

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

    cursor.execute("""
        INSERT INTO shoppinglist (ingredient_name, quantity, unit)
        VALUES (?, ?, ?)
    """, (name, quantity, unit))

    conn.commit()
    conn.close()


def update_shopping_item(item_id, checked):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE shoppinglist
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


def clear_shoppinglist():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM shoppinglist")
    conn.commit()
    conn.close()


#below are all the favourite functions

def add_favourite(recipe_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO favourites (recipe_name)
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

    cursor.execute("""
        DELETE FROM favourites
        WHERE recipe_name = ?
    """, (recipe_name,))

    conn.commit()
    conn.close()

#below is the behaviour tracking (favourites, cooked and rated)

def add_user_action(recipe_name, action, rating=None):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO user_history (recipe_name, action, rating, timestamp)
        VALUES (?, ?, ?, ?)
    """, (recipe_name, action, rating, datetime.now().isoformat()))

    conn.commit()
    conn.close()


def get_user_history():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT * FROM user_history", conn)
    conn.close()
    return df

#below are all the profile funtions

def save_user_profile(requirements):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_profile")

    cursor.execute("""
        INSERT INTO user_profile (
            id,
            isVegetarian,
            isVegan,
            isPescatarian,
            hasDairy,
            hasGluten,
            hasEggs,
            hasFish,
            hasShellfish,
            hasTreeNuts,
            hasPeanuts,
            hasSoy
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        1,
        *requirements.requirements_vector
    ))

    conn.commit()
    conn.close()


def load_user_profile():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM user_profile WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    return row
