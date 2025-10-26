import sqlite3
import json

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
    update user set requirements = ? where name = ?
    """, [requirements_json, profile.name])  # TODO: identify user by ID so we can change their name
    connection.commit()
    connection.close()


def get_profile(name: str) -> User:
    connection = sqlite3.connect('food.db')
    cursor = connection.cursor()

    # NOTE: assumes name is unique identifier. We don't allow multiple users with the
    # same name
    cursor.execute("select * from user where name = ?", [name])

    user_db = cursor.fetchone()

    requirements_json = user_db[2]

    requirements_tuple = json.loads(requirements_json)

    diet_requirements = Diet_Requirements(requirements_tuple)

    user = User(user_db[1], diet_requirements)

    return user


def get_all_profiles():
    connection = sqlite3.connect('food.db')
    cursor = connection.cursor()

    cursor.execute("select * from user")

    profiles = cursor.fetchall()

    connection.close()
    return profiles


def check_user_exists(name: str) -> bool:
    connection = sqlite3.connect('food.db')
    cursor = connection.cursor()

    name = name.lower()

    cursor.execute(
        "select count(*) from user where lower(name) = ?", (name,))

    return cursor.fetchone()[0] == 1