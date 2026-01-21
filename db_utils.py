import sqlite3
import json
import pandas as pd

from entities.user import User
from entities.diet_requirements import Diet_Requirements

def add_profile(profile: User):
    connection = sqlite3.connect('food.db')
    cursor = connection.cursor()

    requirements_tuple = profile.requirements.requirements_vector
    requirements_json = json.dumps(requirements_tuple)

    cursor.execute("""
insert into user(name, requirements) values (?, ?)
""", [profile.name, requirements_json])
    connection.commit()
    connection.close()


def update_profile(profile: User):
    connection = sqlite3.connect('food.db')
    cursor = connection.cursor()

    requirements_tuple = profile.requirements.requirements_vector
    requirements_json = json.dumps(requirements_tuple)

    cursor.execute("""
    update user set requirements = ?, name = ? where userId = ?
    """, [requirements_json, profile.name, profile.id])
    connection.commit()
    connection.close()


def delete_profile(profile: User):
    connection = sqlite3.connect('food.db')
    cursor = connection.cursor()

    cursor.execute("""
                   delete from user where userId = ?
    """, [profile.id])
    connection.commit()
    connection.close()


def get_dietary_requirements_object(row):
    requirements_json = row[2]
    requirements_tuple = json.loads(requirements_json)

    diet_requirements = Diet_Requirements(requirements_tuple)
    return diet_requirements


def get_profile(name: str) -> User:
    connection = sqlite3.connect('food.db')
    cursor = connection.cursor()

    # NOTE: assumes name is unique identifier. We don't allow multiple users with the
    # same name
    cursor.execute("select * from user where name = ?", [name])

    user_db = cursor.fetchone()

    diet_requirements = get_dietary_requirements_object(user_db)

    user = User(user_db[0], user_db[1], diet_requirements)

    return user


def get_all_profiles() -> list[User]:
    connection = sqlite3.connect('food.db')
    cursor = connection.cursor()

    cursor.execute("select * from user")

    profiles = cursor.fetchall()
    connection.close()

    users: list[User] = []
    for profile in profiles:
        requirements_json = profile[2]
        requirements_tuple = json.loads(requirements_json)
        users.append(User(profile[0], profile[1], Diet_Requirements(*requirements_tuple[:11])))

    return users


def check_user_exists(id: int, name: str) -> bool:
    connection = sqlite3.connect('food.db')
    cursor = connection.cursor()

    name = name.lower()

    cursor.execute(
        "select count(*) from user where lower(name) = ? and userId <> ?", (name,id))

    return cursor.fetchone()[0] >= 1






def add_pantry_item(name: str, quantity: float, units: str, expiry_date: str):
    connection = sqlite3.connect('food.db')
    cursor = connection.cursor()

    cursor.execute("""
    INSERT INTO Fridge (item, quantity, units, expiryDate)
    VALUES (?, ?, ?, ?)
    """, (name, quantity, units, expiry_date))

    connection.commit()
    connection.close()


def get_all_pantry_items():
    connection = sqlite3.connect('food.db')
    cursor = connection.cursor()

    cursor.execute("SELECT item, quantity, units, expiryDate FROM Fridge")
    items = cursor.fetchall()

    connection.close()
    return items


def delete_pantry_item(item_name: str):
    connection = sqlite3.connect('food.db')
    cursor = connection.cursor()

    cursor.execute("DELETE FROM Fridge WHERE item = ?", (item_name,))
    connection.commit()
    connection.close()





def get_filtered_recipes(diet_labels: list[str]):
    connection = sqlite3.connect('food.db')
    cursor = connection.cursor()

    placeholders = ",".join("?" for _ in diet_labels)

    query = f"""
    SELECT "Recipe Name", Ingredients, Instructions, Diet
    FROM recipes
    WHERE Diet IN ({placeholders})
    """

    cursor.execute(query, diet_labels)
    results = cursor.fetchall()
    connection.close()
    return results




DB_PATH = "food.db"

def load_pantry():
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql("SELECT * FROM pantry", conn)
    except Exception:
        df = pd.DataFrame()
    conn.close()
    return df

def load_recipes():
    conn = sqlite3.connect("food.db")
    df = pd.read_sql_query("SELECT * FROM recipes", conn)
    conn.close()
    return df